"""Runner tests: refusal before any solve, budget accounting, loop structure, alignment, lookahead,
arm parity, Arm B/C handling, and no overwrite / no partial success.

Synthetic data only. Every optimize() goes to FakeOptimizer (no solver); the real solver entry points
are replaced by mocks that fail if called (conftest.no_solver)."""
import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf
from conftest import SolverCalled

RUNNER = Path(r.__file__)
REPO = sf.PKG.parents[1]


# ---------------------------------------------------------------- the solver mock itself
def test_solver_mock_fails_if_called():
    with pytest.raises(SolverCalled):
        r.load_planner_class()(reserve_enabled=True)
    import highspy
    with pytest.raises(SolverCalled):
        highspy.Highs()


def test_real_planner_optimize_is_blocked():
    Planner = r._load("research_numerical_extractor_planner_cf_v1",
                      "experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py").PlannerCFV1Optimizer
    p = Planner(reserve_enabled=True)  # construction builds no model
    fc = r.ArmForecaster("A")
    st = r.make_initial_state("2024-06-30T23:00:00Z")
    b, _, _ = fc.predict(st, [40.0] * 24)
    with pytest.raises(SolverCalled):
        p.optimize(b, st, {"critical_demand_w": [11600.0] * 24, "ebr_target_wh": [0.0] * 24,
                           "terminal_target_wh": 100000.0, **r.load_canonical_configs(REPO)})


# ---------------------------------------------------------------- refusal before any solve
def test_execute_refused_on_real_package_config(tmp_path, monkeypatch, capsys):
    """--execute on the package as it stands (unsigned, decisions open) exits 2 before any optimizer,
    forecaster, frozen-module load or output directory exists."""
    repo = sf.build_fake_repo(tmp_path)

    def boom(*a, **k):
        raise AssertionError("execution machinery reached despite failed preflight")
    for name in ("load_frozen", "ArmForecaster", "run_origin", "evaluation_origins"):
        monkeypatch.setattr(r, name, boom)
    monkeypatch.setattr(r.pd, "read_csv", boom)
    before = sorted(p.name for p in (repo / sf.PKG_REL / "results").iterdir())
    assert r.main(["--repo", str(repo), "--execute"]) == 2
    err = capsys.readouterr().err
    assert "execution refused" in err
    assert "[decisions]" not in err                      # all decisions pass and the config is frozen (M9)
    for frag in ("unsigned", "calibration artifact missing",
                 "input-content guards skipped"):
        assert frag in err, frag
    assert sorted(p.name for p in (repo / sf.PKG_REL / "results").iterdir()) == before


def test_no_bypass_option_exists():
    tree = ast.parse(RUNNER.read_text())
    flags = [a.value for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument"
             for a in n.args if isinstance(a, ast.Constant)]
    assert sorted(flags) == ["--audit-budget", "--execute", "--preflight", "--repo"]
    src = RUNNER.read_text().lower()
    for w in ("--force", "--skip", "--override", "--no-check", "--unsafe", "--dry-run-ok"):
        assert w not in src


def test_execute_rechecks_preflight_itself(tmp_path, monkeypatch):
    repo = sf.build_fake_repo(tmp_path)
    monkeypatch.setattr(r, "load_frozen", lambda: (_ for _ in ()).throw(AssertionError("reached")))
    assert r.execute(repo, pf.load_config(repo)) == 2


@pytest.mark.parametrize("missing", ["authorization", "decision", "hash"])
def test_single_missing_item_blocks_otherwise_complete_package(tmp_path, monkeypatch, missing):
    """TEST-ONLY fully approved synthetic package with a valid synthetic artifact; removing one item refuses."""
    import calibrate_arm_c as cal
    repo = sf.build_fake_repo(tmp_path)
    cfg = sf.approve_everything(pf.load_config(repo))
    sf.write_cfg(repo, cfg)
    sf.write_manifest(repo)
    sf.freeze_prereg(repo)
    monkeypatch.setattr(cal, "load_artifact",
                        lambda p, c: ({"synthetic": True, "created_at_utc": "2026-10-11T00:00:01Z"}, "a" * 64))
    sf.sign(repo, "calibration")
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=14760)
    rep, _, _ = r.full_preflight(repo, cfg, "execute")
    # Everything governance-related passes; only the synthetic (dummy) inputs fail the content guards.
    assert all(f.startswith("[inputs]") for f in rep.failures), rep.failures
    if missing == "authorization":
        (repo / sf.PKG_REL / "AUTHORIZATION_RECORD.json").unlink()
    elif missing == "decision":
        cfg["decisions"]["D6"]["status"] = "PARTIALLY APPROVED"
    else:
        (repo / "system/control/router.py").write_text("tampered\n")
    rep, _, _ = r.full_preflight(repo, cfg, "execute")
    assert any(not f.startswith("[inputs]") for f in rep.failures)
    assert "[inputs] input-content guards skipped because earlier checks failed" in rep.failures


def test_missing_calibration_artifact_blocks_execution_and_arm_c(tmp_path):
    repo = sf.build_fake_repo(tmp_path)
    rep, art, sha = r.full_preflight(repo, pf.load_config(repo), "preflight")
    assert art is None and sha is None
    assert any("[calibration] calibration artifact missing" in f for f in rep.failures)
    with pytest.raises(r.ArmInvalid, match="calibration artifact"):
        r.ArmForecaster("C", calibration=None)


# ---------------------------------------------------------------- budget
def test_budget_audit_reconciles_with_ceiling():
    a = r.budget_audit(123, sf.load_real_cfg())
    assert a["optimize_calls_per_arm"] == 2952 and a["optimize_calls_total"] == 14760
    assert a["highs_run_calls_total"] == 14760
    assert a["max_internal_lexicographic_subsolves_total"] == 14760 * 5
    assert a["n_arms"] == 5 and a["reconciles"] is True
    for k in ("repeat_check_calls", "retry_calls", "calibration_solver_calls", "rule_d_subarm_calls", "test_solver_calls"):
        assert a[k] == 0
    assert pf.check_budget(sf.load_real_cfg(), 2952, 14760) == []


def test_budget_mismatch_is_a_preflight_failure():
    cfg = sf.load_real_cfg()
    cfg["budget"]["total_ceiling"] = 14784
    assert r.budget_audit(123, cfg)["reconciles"] is False
    assert pf.check_budget(cfg, 2952, 14760) != []


def test_audit_budget_cli_needs_no_solver(tmp_path, monkeypatch, capsys):
    repo = sf.build_fake_repo(tmp_path)
    monkeypatch.setattr(r, "full_preflight", lambda *a: (_ for _ in ()).throw(AssertionError("preflight")))
    assert r.main(["--repo", str(repo), "--audit-budget"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["optimize_calls_total"] == 14760 and out["reconciles"] is True


def test_orchestration_has_exactly_one_optimize_call_site():
    """The derived count assumes one optimize() per step and nothing else. Check that statically."""
    tree = ast.parse(RUNNER.read_text())
    sites = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "optimize"]
    owners = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for s in sites:
            if fn.lineno <= s.lineno <= fn.end_lineno:
                owners.append(fn.name)
    assert sorted(owners) == ["optimize", "run_origin"]  # BudgetedOptimizer.optimize delegates; run_origin calls once
    ro = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "run_origin"][0]
    loops = [n for n in ast.walk(ro) if isinstance(n, ast.For)]
    assert len(loops) == 1 and ast.unparse(loops[0].iter) == "range(STEPS_PER_ORIGIN)"
    assert r.STEPS_PER_ORIGIN == 24 and r.OPTIMIZE_CALLS_PER_STEP == 1


def test_budget_is_charged_before_the_inner_optimizer():
    class Inner:
        n = 0

        def optimize(self, *a):
            Inner.n += 1
            return "plan"
    b = r.SolveBudget(per_arm=2, total=3)
    opt = r.BudgetedOptimizer(Inner(), b, "A")
    opt.optimize(None, None, None)
    opt.optimize(None, None, None)
    with pytest.raises(r.BudgetExceeded):
        opt.optimize(None, None, None)
    assert Inner.n == 2
    r.BudgetedOptimizer(Inner(), b, "C").optimize(None, None, None)
    with pytest.raises(r.BudgetExceeded):
        r.BudgetedOptimizer(Inner(), b, "B").optimize(None, None, None)
    assert Inner.n == 3 and b.used == 3


# ---------------------------------------------------------------- arms
def test_rule_d_off_everywhere():
    assert all(spec["rule_d"] is False for spec in r.ARM_CONFIGS.values())
    assert all(a["rule_d"] is False for a in sf.load_real_cfg()["arms"].values())
    code = RUNNER.read_text()
    assert "rule_d_true_curtailment" not in code and "RuleD" not in code
    bad = {k: dict(v) for k, v in r.ARM_CONFIGS.items()}
    bad["C"]["rule_d"] = True
    assert any("Rule D is not OFF" in f for f in pf.check_arms(sf.load_real_cfg(), bad))


def test_nothing_is_promotion_eligible_and_b_is_noncausal():
    assert all(spec["promotion_eligible"] is False for spec in r.ARM_CONFIGS.values())
    b = r.ARM_CONFIGS["B"]
    assert b["causal"] is False and "NONCAUSAL" in b["result_label"] and "NOT DEPLOYABLE" in b["result_label"]
    assert pf.check_arms(sf.load_real_cfg(), r.ARM_CONFIGS) == []
    bad = {k: dict(v) for k, v in r.ARM_CONFIGS.items()}
    bad["B"]["causal"] = True
    assert pf.check_arms(sf.load_real_cfg(), bad) != []


def test_a_and_a_fix_differ_only_in_correction():
    bad = {k: dict(v) for k, v in r.ARM_CONFIGS.items()}
    bad["A_FIX"]["ebr_solar"] = "calibrated_lower_bound"
    assert any("A and A_FIX differ" in f for f in pf.check_arms(sf.load_real_cfg(), bad))


def _two_origin_weather():
    return sf.synthetic_weather(["2024-06-10", "2024-06-11"], cloud={"2024-06-11": 99.0})


def _sites_lookup(w):
    return {pd.Timestamp(t): float(v) for t, v in zip(w["timestamp"], w["actual_SW_IN"])}


def test_forecasters_parity_a_vs_a_fix():
    st = r.make_initial_state("2024-06-09T23:00:00Z")
    cloud = [35.0] * 24
    ba, sa, _ = r.ArmForecaster("A").predict(st, cloud)
    bf, sf_, _ = r.ArmForecaster("A_FIX").predict(st, cloud)
    assert ba.timestamps == bf.timestamps
    assert ba.wind_generation.point == bf.wind_generation.point
    assert ba.demand.point == bf.demand.point
    assert sa == list(ba.solar_generation.point) and sf_ == list(bf.solar_generation.point)
    assert ba.solar_generation.point != bf.solar_generation.point  # only the solar channel moves


def test_arm_b_uses_realized_solar_and_is_tagged():
    w = _two_origin_weather()
    st = r.make_initial_state("2024-06-09T23:00:00Z")
    fb = r.ArmForecaster("B", sites_hourly=_sites_lookup(w))
    b, s, _ = fb.predict(st, [35.0] * 24)
    exp = w[w.forecast_start == "2024-06-10 00:00:00"].actual_SW_IN.tolist()
    assert b.solar_irradiance.point == exp
    assert b.metadata["status"] == "NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY"
    base, _, _ = r.ArmForecaster("A").predict(st, [35.0] * 24)
    assert b.wind_generation.point == base.wind_generation.point and b.demand.point == base.demand.point
    with pytest.raises(r.ArmInvalid):
        r.ArmForecaster("B", sites_hourly=None)
    with pytest.raises(r.ArmInvalid, match="missing"):
        r.ArmForecaster("B", sites_hourly={pd.Timestamp("2024-01-01"): 1.0}).predict(st, [35.0] * 24)


def _synthetic_calibration():
    qt = {"residual_space": "ghi_w_m2", "elevation_bin_edges_deg": [0.0, 5.0, 15.0, 30.0, 90.0],
          "cloud_bin_edges_fraction": [0.0, 0.2, 0.8, 1.0], "bin_boundary_rule": "left_closed",
          "table": [{"elevation_bin": e, "cloud_bin": c, "q_alpha": -40.0 - 10 * e} for e in range(4) for c in range(3)]}
    return {"gamma_fit": {"gamma_hat": 0.5}, "quantiles": qt}


def test_arm_c_point_to_planner_lower_bound_to_reserve():
    st = r.make_initial_state("2024-06-09T23:00:00Z")
    cloud = [30.0] * 24
    fc = r.ArmForecaster("C", calibration=_synthetic_calibration())
    b, ebr_solar, _ = fc.predict(st, cloud)
    ref, _, _ = r.ArmForecaster("A_FIX").predict(st, [0.0] * 24)  # corrected clear sky
    cs = np.array(ref.solar_irradiance.point)
    elev = fc.wrapper.get_solarposition(pd.to_datetime(b.timestamps, utc=True))["elevation"].to_numpy()
    day = (elev > 0) & (cs > 0)
    exp = np.where(day, cs * 0.7 ** 0.5, 0.0)
    assert np.allclose(b.solar_irradiance.point, exp)
    pt_pv = np.array(b.solar_generation.point)
    assert np.all(np.array(ebr_solar) <= pt_pv + 1e-9) and np.all(np.array(ebr_solar) >= 0)
    assert np.array(ebr_solar).sum() < pt_pv.sum()
    assert b.metadata["arm"] == "C"


# ---------------------------------------------------------------- one origin through the loop
def _run(arm, optimizer=None, calibration=None, weather=None):
    w = weather if weather is not None else _two_origin_weather()
    frozen = r.load_frozen()
    configs = r.load_canonical_configs(REPO)
    from system.control.router import EMSControlRouter
    from system.simulation.research_realization_executor import ResearchRealizationExecutor
    opt = optimizer or sf.FakeOptimizer()
    fc = r.ArmForecaster(arm, sites_hourly=_sites_lookup(w), calibration=calibration)
    seen = []
    orig = fc.predict

    def spy(state, cloud):
        seen.append(list(cloud))
        return orig(state, cloud)
    fc.predict = spy
    hourly, execd = r.run_origin(arm=arm, origin_index=1, forecast_start="2024-06-10 00:00:00", weather_df=w,
                                 forecaster=fc, optimizer=opt, executor=ResearchRealizationExecutor(configs),
                                 router=EMSControlRouter(), elevation_provider=frozen.s4a.SolarElevationProvider(None),
                                 frozen=frozen, configs=configs)
    return hourly, execd, opt, seen, w


def test_run_origin_calls_optimize_exactly_24_times():
    hourly, execd, opt, _, _ = _run("A")
    assert len(opt.calls) == 24 and len(hourly) == 24 and len(execd) == 24
    assert [h["hour"] for h in hourly] == list(range(24))


def test_timestamp_and_origin_alignment():
    hourly, _, opt, _, w = _run("A_FIX")
    labels = w[w.forecast_start == "2024-06-10 00:00:00"].timestamp.tolist()
    exp = [t.replace(" ", "T") + "Z" for t in labels]
    assert [h["timestamp"] for h in hourly] == exp
    assert [c["bundle_t1"] for c in opt.calls] == exp      # plan hour 0 == the realized hour
    assert opt.calls[0]["state_ts"] == "2024-06-09T23:00:00Z"   # t0 = forecast_start - 1 h
    assert all(c["terminal"] == r.TERMINAL_TARGET_WH for c in opt.calls)
    from system.simulation.research_realization_executor import ResearchRealizationExecutor
    ex = ResearchRealizationExecutor(r.load_canonical_configs(REPO))
    sw = w[w.forecast_start == "2024-06-10 00:00:00"].actual_SW_IN.tolist()   # same origin, same hour
    # the executor reports realized powers rounded to 0.01 W
    assert [h["actual_solar"] for h in hourly] == pytest.approx([ex.pv_from_sw_in(x) for x in sw], abs=0.005)


def test_no_horizon_tail_lookahead():
    hourly, _, _, seen, _ = _run("A")
    assert all(v < 99.0 for traj in seen for v in traj)      # next origin's sentinel cloud never used
    assert [h["held_cloud_hours"] for h in hourly] == list(range(24))


def test_reserve_elevation_identical_in_a_and_a_fix():
    ha, _, oa, _, _ = _run("A")
    hf, _, of, _, _ = _run("A_FIX")
    assert [h["solar_elevation_t1_deg"] for h in ha] == [h["solar_elevation_t1_deg"] for h in hf]
    import stage4_low_sun_adapter as s4a
    p = s4a.SolarElevationProvider(None)
    assert hf[12]["solar_elevation_t1_deg"] == pytest.approx(p.get_elevation_vector([hf[12]["timestamp"]])[0])
    assert [c["solar_w"] for c in oa.calls] != [c["solar_w"] for c in of.calls]


def test_arm_c_runs_through_loop_with_lower_bound_reserve():
    hc, _, oc, _, _ = _run("C", calibration=_synthetic_calibration())
    assert len(oc.calls) == 24 and len(hc) == 24
    assert all(h["result_label"] == r.LABEL_C for h in hc)


def test_non_optimal_status_invalidates_the_arm():
    with pytest.raises(r.ArmInvalid, match="INFEASIBLE"):
        _run("A", optimizer=sf.FakeOptimizer(status="INFEASIBLE"))


class _NativeStatusOptimizer(sf.FakeOptimizer):
    """Like FakeOptimizer, but lets the plan's constraint_status and the diagnostics dict's
    solver_status differ, mirroring the real Planner (research_numerical_extractor_planner_cf_v1.py),
    where constraint_status is a hardcoded literal ("OPTIMAL") while diagnostics["solver_status"] is
    str(model_status), the native HiGHS enum representation (e.g. "HighsModelStatus.kOptimal")."""

    def __init__(self, constraint_status="OPTIMAL", diagnostics_status="OPTIMAL"):
        super().__init__(status=constraint_status)
        self._diagnostics_status = diagnostics_status

    def optimize(self, bundle, state, cfg):
        plan = super().optimize(bundle, state, cfg)
        self.last_diagnostics[0]["solver_status"] = self._diagnostics_status
        return plan


def test_native_highs_status_string_is_normalized_in_telemetry():
    """Regression test for the run_20261011T075716Z validation failure: every real solve returned
    HighsModelStatus.kOptimal (diagnostics) while constraint_status was the literal "OPTIMAL" (the
    gated value). Telemetry must record the gated literal, not the native enum string, so validate_run
    accepts a run where every solve was genuinely optimal."""
    hourly, _, _, _, _ = _run("A", optimizer=_NativeStatusOptimizer(
        constraint_status="OPTIMAL", diagnostics_status="HighsModelStatus.kOptimal"))
    assert all(h["solver_status"] == "OPTIMAL" for h in hourly)
    df = pd.DataFrame(hourly)
    assert r.validate_run(df, ["2024-06-10 00:00:00"], arms=("A",)) == []


def test_native_solver_status_is_preserved_alongside_the_canonical_one():
    """The canonical `solver_status` (the gated literal, checked by validate_run) and the native
    `solver_status_native` (the diagnostics dict's raw string, e.g. the HiGHS enum repr) are both
    recorded, so normalizing the validated field does not discard the underlying solver detail."""
    hourly, _, _, _, _ = _run("A", optimizer=_NativeStatusOptimizer(
        constraint_status="OPTIMAL", diagnostics_status="HighsModelStatus.kOptimal"))
    assert all(h["solver_status"] == "OPTIMAL" for h in hourly)
    assert all(h["solver_status_native"] == "HighsModelStatus.kOptimal" for h in hourly)
    df = pd.DataFrame(hourly)
    assert r.validate_run(df, ["2024-06-10 00:00:00"], arms=("A",)) == []


def test_native_solver_status_defaults_to_canonical_when_diagnostics_missing():
    """When the optimizer's diagnostics dict carries no 'solver_status' key at all (not merely a
    differing one), the native column falls back to the gated literal rather than being blank or
    raising -- matching the frozen runner's original str(diag0.get(..., plan.constraint_status))
    fallback, now applied to the native column instead of the validated one."""
    class _NoDiagnosticsStatus(_NativeStatusOptimizer):
        def optimize(self, bundle, state, cfg):
            plan = sf.FakeOptimizer.optimize(self, bundle, state, cfg)
            self.last_diagnostics[0].pop("solver_status", None)
            return plan
    hourly, _, _, _, _ = _run("A", optimizer=_NoDiagnosticsStatus(constraint_status="OPTIMAL"))
    assert all(h["solver_status"] == "OPTIMAL" for h in hourly)
    assert all(h["solver_status_native"] == "OPTIMAL" for h in hourly)


def test_feasible_status_is_accepted_end_to_end():
    """Confirms the runner's own contract (gate at run_origin + validate_run) accepts "FEASIBLE" when
    both the gate and the diagnostics agree on it. This does not claim the real frozen Planner ever
    emits "FEASIBLE" -- source inspection (research_numerical_extractor_planner_cf_v1.py) shows its
    success path only ever sets constraint_status="OPTIMAL"; "FEASIBLE" is not currently reachable
    from the real solver integration, only from this runner's declared, broader contract."""
    hourly, _, _, _, _ = _run("A", optimizer=_NativeStatusOptimizer(
        constraint_status="FEASIBLE", diagnostics_status="FEASIBLE"))
    assert all(h["solver_status"] == "FEASIBLE" for h in hourly)
    df = pd.DataFrame(hourly)
    assert r.validate_run(df, ["2024-06-10 00:00:00"], arms=("A",)) == []


def test_invalid_status_still_raises_despite_telemetry_fix():
    """The telemetry fix (recording plan.constraint_status instead of the diagnostics dict's solver_status)
    must not weaken the in-loop fail-closed gate: an unexpected/error status still raises ArmInvalid,
    regardless of what the diagnostics dict separately reports."""
    with pytest.raises(r.ArmInvalid, match="TIMEOUT"):
        _run("A", optimizer=_NativeStatusOptimizer(
            constraint_status="TIMEOUT", diagnostics_status="HighsModelStatus.kTimeLimit"))


def test_control_uses_governed_ebr():
    import stage4_low_sun_adapter as s4a
    crit = [11600.0] * 24
    assert r.arm_ebr("PC-Control", s4a, crit, [0.0] * 24, [0.0] * 24) == s4a.compute_governed_ebr(crit)
    sol = [20000.0] * 24
    assert r.arm_ebr("A", s4a, crit, sol, [0.0] * 24) == s4a.compute_variant_sw_ebr(crit, sol, [0.0] * 24)


# ---------------------------------------------------------------- execute(): no overwrite, no partial success
def _fake_execute_env(tmp_path, monkeypatch, run_origin_impl):
    repo = sf.build_fake_repo(tmp_path)
    cfg = pf.load_config(repo)
    w = sf.synthetic_weather(["2024-06-10", "2024-06-11"])
    w.to_csv(repo / cfg["paths"]["weather"], index=False)
    pd.DataFrame({"TIMESTAMP": w["timestamp"], "SW_IN": w["actual_SW_IN"]}).to_csv(repo / cfg["paths"]["sites_hourly"], index=False)
    ok = pf.PreflightReport("execute")

    def fake_preflight(repo_, cfg_, mode_):
        assert mode_ == "execute"
        return ok, {"synthetic": True}, "a" * 64
    monkeypatch.setattr(r, "full_preflight", fake_preflight)
    # execute() re-checks the execute-scoped authorization itself, so this synthetic run needs a TEST-ONLY one.
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=cfg["budget"]["total_ceiling"])
    monkeypatch.setattr(r, "evaluation_origins", lambda wdf, c: ["2024-06-10 00:00:00", "2024-06-11 00:00:00"])
    monkeypatch.setattr(r, "load_canonical_configs", lambda repo_: {})
    monkeypatch.setattr(r, "ArmForecaster", lambda *a, **k: object())
    monkeypatch.setattr(r, "load_planner_class", lambda: (lambda **k: sf.FakeOptimizer()))
    monkeypatch.setattr(r, "run_origin", run_origin_impl)

    class FixedDT:
        @staticmethod
        def now(tz=None):
            from datetime import datetime, timezone
            return datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(r, "datetime", FixedDT)
    import system.simulation.research_realization_executor as rre
    monkeypatch.setattr(rre, "ResearchRealizationExecutor", lambda configs: object())
    return repo, cfg


def _rows(arm, oi, fs, n=24):
    return [{"origin_id": oi, "forecast_start": fs, "hour": h, "arm": arm, "solver_status": "OPTIMAL",
             **{k: 1.0 for k in r.REQUIRED_NUMERIC}} for h in range(n)], []


def test_failure_marks_arm_invalid_and_run_failed(tmp_path, monkeypatch):
    def impl(*, arm, origin_index, forecast_start, **k):
        if arm == "A" and origin_index == 2:
            raise r.ArmInvalid("synthetic failure")
        return _rows(arm, origin_index, forecast_start)
    repo, cfg = _fake_execute_env(tmp_path, monkeypatch, impl)
    assert r.execute(repo, cfg) == 3
    run_dir = repo / cfg["paths"]["results_root"] / "run_20260101T000000Z"
    st = json.loads((run_dir / "RUN_STATUS.json").read_text())
    assert st["status"] == "FAILED" and st["failed_arm"] == "A"
    assert st["arms"] == {"PC-Control": "COMPLETE", "A": "INVALID", "A_FIX": "PENDING", "B": "PENDING", "C": "PENDING"}
    assert not (run_dir / "RESULTS.json").exists() and not (run_dir / "HOURLY_TELEMETRY.csv").exists()
    assert (run_dir / "PARTIAL_HOURLY_TELEMETRY_INVALID.csv").exists()


def test_incomplete_output_is_not_a_result(tmp_path, monkeypatch):
    def impl(*, arm, origin_index, forecast_start, **k):
        return _rows(arm, origin_index, forecast_start, n=23 if arm == "C" else 24)
    repo, cfg = _fake_execute_env(tmp_path, monkeypatch, impl)
    import gates_three_arm as g
    monkeypatch.setattr(g, "evaluate", lambda *a, **k: (_ for _ in ()).throw(AssertionError("gates on invalid run")))
    assert r.execute(repo, cfg) == 4
    run_dir = repo / cfg["paths"]["results_root"] / "run_20260101T000000Z"
    st = json.loads((run_dir / "RUN_STATUS.json").read_text())
    assert st["status"] == "FAILED" and any("C: 46 hourly rows" in p for p in st["validity_problems"])
    assert not (run_dir / "RESULTS.json").exists()


def test_existing_run_directory_is_never_reused(tmp_path, monkeypatch):
    """Isolates the output-directory exclusivity guard from the single-use authorization guard
    (preflight._consumed_execute_refs): the first execute() call consumes its execute_instruction_ref
    by writing RUN_STATUS.json, so a second call with the SAME ref is now refused earlier, at the
    authorization layer (check_execution_authorization), before any directory is touched -- it no
    longer reaches the FileExistsError path at all. Re-signing with a fresh, distinct ref before the
    second call lets this test exercise the directory guard on its own, as it did before that
    authorization check existed, without weakening either guard."""
    def impl(*, arm, origin_index, forecast_start, **k):
        raise r.ArmInvalid("stop early")
    repo, cfg = _fake_execute_env(tmp_path, monkeypatch, impl)
    assert r.execute(repo, cfg) == 3
    run_dir = repo / cfg["paths"]["results_root"] / "run_20260101T000000Z"
    before = {p.name: p.read_bytes() for p in run_dir.iterdir()}
    sf.sign(repo, "execution", calibration_sha="a" * 64, solve_ceiling=cfg["budget"]["total_ceiling"],
            execute_instruction_ref="a second, distinct instruction -- not yet consumed by any run")
    with pytest.raises(FileExistsError):
        r.execute(repo, cfg)
    assert {p.name: p.read_bytes() for p in run_dir.iterdir()} == before


def test_consumed_authorization_blocks_execute_before_any_directory_is_touched(tmp_path, monkeypatch):
    """Companion to test_existing_run_directory_is_never_reused: reusing the SAME
    execute_instruction_ref for a second execute() call is refused at the authorization layer (exit
    code 2, matching a preflight failure), and nothing new is written to the existing run directory."""
    def impl(*, arm, origin_index, forecast_start, **k):
        raise r.ArmInvalid("stop early")
    repo, cfg = _fake_execute_env(tmp_path, monkeypatch, impl)
    assert r.execute(repo, cfg) == 3
    run_dir = repo / cfg["paths"]["results_root"] / "run_20260101T000000Z"
    before = {p.name: p.read_bytes() for p in run_dir.iterdir()}
    assert r.execute(repo, cfg) == 2
    assert {p.name: p.read_bytes() for p in run_dir.iterdir()} == before


def test_results_json_written_exclusively(tmp_path):
    p = tmp_path / "RESULTS.json"
    r._write_json_exclusive(p, {"a": 1})
    with pytest.raises(FileExistsError):
        r._write_json_exclusive(p, {"a": 2})
    assert json.loads(p.read_text()) == {"a": 1}


@pytest.mark.parametrize("mut,msg", [
    (lambda d: d.iloc[:-1], "hourly rows"),
    (lambda d: pd.concat([d.iloc[:-1], d.iloc[[0]]]), "duplicate"),
    (lambda d: d.assign(solver_status=["OPTIMAL"] * (len(d) - 1) + ["TIME_LIMIT"]), "non-optimal"),
    (lambda d: d.assign(unmet_load=[1.0] * (len(d) - 1) + [np.nan]), "non-finite"),
    (lambda d: d.assign(forecast_start="2024-06-12 00:00:00"), "origin set"),
])
def test_validate_run_rejects_partial_or_bad_output(mut, msg):
    origins = ["2024-06-10 00:00:00"]
    df = pd.DataFrame(_rows("A", 1, origins[0])[0])
    assert r.validate_run(df, origins, arms=("A",)) == []
    probs = r.validate_run(mut(df), origins, arms=("A",))
    assert probs and any(msg in p for p in probs), probs
    assert r.validate_run(df, origins, arms=("A", "B"))  # a missing arm is a problem


# ---------------------------------------------------------------- frozen reference parity (static)
def _fn(path, name):
    tree = ast.parse(Path(path).read_text())
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name][0]


def _station_kwargs(fn):
    call = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "StationState"][0]
    return {k.arg: ast.literal_eval(k.value) for k in call.keywords if k.arg != "timestamp"}


def test_initial_state_and_configs_match_frozen_reference():
    ref = REPO / "experiments" / "run_diesel_reduction_campaign.py"  # parsed, never imported
    assert pf.sha256_file(ref) == sf.load_real_cfg()["expected_sha256"]["configuration"]["experiments/run_diesel_reduction_campaign.py"]
    assert _station_kwargs(_fn(ref, "make_initial_state")) == _station_kwargs(_fn(RUNNER, "make_initial_state"))
    src = ast.unparse(_fn(ref, "load_canonical_configs"))
    for frag in ("'critical_demand_baseline_w': 11600.0", "'terminal_target_wh': 100000.0", "battery.yaml",
                 "diesel.yaml", "solar_pv.yaml", "loads.yaml"):
        assert frag in src
    c = r.load_canonical_configs(REPO)
    assert c["critical_demand_baseline_w"] == 11600.0 and c["terminal_target_wh"] == 100000.0
    assert set(c) == {"battery", "diesel", "solar_pv", "loads", "critical_demand_baseline_w", "terminal_target_wh"}


def test_all_pinned_sources_byte_identical():
    cfg = sf.load_real_cfg()
    assert pf.check_hashes(REPO, cfg) == []
