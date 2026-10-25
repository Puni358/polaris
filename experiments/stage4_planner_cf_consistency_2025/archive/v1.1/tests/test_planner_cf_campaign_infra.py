"""
Synthetic / unit / invariant tests for the Planner-CF v1 campaign infrastructure
(EXP-PLANNER-CF-CONSISTENCY-2025). No real origin, oracle or campaign is executed.

The validation tests read the FROZEN corrected telemetry (read-only) to check definitions.
The closed-loop test uses a fake future origin (2099-01-01), not a population origin.
"""

import inspect
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import research_numerical_extractor_planner_cf_v1 as planner  # noqa: E402
import planner_cf_campaign_runner as runner  # noqa: E402
import planner_cf_statistics as stat  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402
import planner_cf_hash_guards as hg  # noqa: E402
import stage4_low_sun_adapter as s4a  # noqa: E402

FROZEN_TEL = REPO / "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv"
FROZEN_RES = REPO / "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv"


# ---------------------------------------------------------------------------
# C1 literal bound
# ---------------------------------------------------------------------------

def test_C1_served_c_upper_bound_is_critical_demand_literal():
    src = inspect.getsource(planner.PlannerCFV1Optimizer.optimize)
    assert "ub[base + OFF_SERVED_C] = 0.0, p_crit" in src
    assert "ub[base + OFF_SERVED_C] = 0.0, p_dem" not in src


def test_C1_served_c_never_exceeds_critical_demand_on_solution():
    n = 24
    solar = [0.0] * n
    wind = [4500.0] * n
    dem = [12000.0] * n
    crit = [min(11600.0, d) for d in dem]

    class _S:
        def __init__(self, p):
            self.point = list(p)

    class _B:
        timestamps = [f"2025-05-01T{h:02d}:00:00Z" for h in range(n)]
        solar_generation = _S(solar)
        wind_generation = _S(wind)
        demand = _S(dem)
        demand_critical = None

    from system.schemas.station_state import StationState
    import oracle_runner as oracle
    cfg = oracle.canonical_configs()
    cfg["critical_demand_w"] = crit
    st = StationState(timestamp="2025-04-30T23:00:00Z", battery_soc_pct=50.0, battery_energy_wh=100000.0,
                      diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
                      last_observed_demand=15000.0, last_observed_wind_generation=4500.0,
                      diesel_fuel_remaining_liters=100.0, operating_mode="NORMAL")
    opt = planner.PlannerCFV1Optimizer()
    opt.optimize(_B(), st, cfg)
    for row, c in zip(opt.last_planned, crit):
        assert row["served_c"] <= c + 1e-6


# ---------------------------------------------------------------------------
# Arms, campaign gating, hash guards
# ---------------------------------------------------------------------------

def test_five_arms_with_preregistered_specs():
    assert runner.ARMS == ("PC-Control", "PC-S", "PC-SW", "PC-S-L", "PC-SW-L")
    assert runner.ARM_SPEC["PC-S-L"] == ("solar", True)
    assert runner.ARM_SPEC["PC-SW"] == ("solar+wind", False)


def test_arm_ebr_matches_frozen_adapter_equations():
    crit = [11600.0] * 24
    sol = [3000.0] * 12 + [0.0] * 12
    wnd = [1000.0] * 24
    elev = [10.0] * 6 + [30.0] * 18
    assert runner.arm_ebr("PC-Control", crit, sol, wnd, elev) == s4a.compute_governed_ebr(crit)
    assert runner.arm_ebr("PC-S", crit, sol, wnd, elev) == s4a.compute_variant_s_ebr(crit, sol)
    assert runner.arm_ebr("PC-SW", crit, sol, wnd, elev) == s4a.compute_variant_sw_ebr(crit, sol, wnd)
    assert runner.arm_ebr("PC-S-L", crit, sol, wnd, elev) == s4a.compute_variant_sl_ebr(
        crit, sol, elev, threshold_deg=15.0, protection_enabled=True)
    assert runner.arm_ebr("PC-SW-L", crit, sol, wnd, elev) == s4a.compute_variant_swl_ebr(
        crit, sol, wnd, elev, threshold_deg=15.0, protection_enabled=True)
    with pytest.raises(ValueError):
        runner.arm_ebr("PC-X", crit, sol, wnd, elev)


def test_campaign_refuses_without_authorization():
    with pytest.raises(PermissionError):
        runner.run_campaign(authorized=False)


def test_hash_guards_detect_mismatch_and_pass_on_current_files():
    assert hg.verify_protected_hashes(REPO) == []
    bad = dict(hg.PROTECTED_PINS)
    first = next(iter(bad))
    bad[first] = "0" * 64
    assert any("hash mismatch" in m for m in hg.verify_protected_hashes(REPO, bad))


# ---------------------------------------------------------------------------
# Holm and BCa
# ---------------------------------------------------------------------------

def test_holm_adjust_matches_hand_computation():
    adj = stat.holm_adjust([0.01, 0.04, 0.03, 0.005])
    assert adj == pytest.approx([0.03, 0.06, 0.06, 0.02])


def test_holm_caps_at_one():
    assert max(stat.holm_adjust([0.9, 0.8, 0.7, 0.6])) <= 1.0


def test_bca_is_deterministic_and_brackets_mean():
    rng = np.random.default_rng(1)
    x = rng.normal(5.0, 1.0, 123)
    a = stat.bca_lower_mean(x)
    b = stat.bca_lower_mean(x)
    assert a == b
    assert a[0] <= x.mean() <= a[1]


# ---------------------------------------------------------------------------
# Synthetic 5-arm telemetry for S1-S3, E1, T40, winner, D1-D3
# ---------------------------------------------------------------------------

def _synthetic_frame(scales, crit_first_drop_arm=None, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for o in range(1, 124):
        base_fuel = 40.0 + rng.normal(0, 1.0, 24).clip(-0.5, 0.5)
        for arm in stat.CONTROL, *stat.CANDIDATES:
            scale = scales[arm]
            for h in range(24):
                crit = 11600.0
                served_first = crit
                if arm == crit_first_drop_arm and h == 3:
                    served_first = crit - 1000.0
                fuel = base_fuel[h] * scale
                rows.append({
                    "origin_id": o, "hour": h, "arm": arm, "route": "NORMAL",
                    "optimizer_received_mode": "NORMAL", "solver_status": gates.OPTIMAL_STATUS,
                    "em_rows_built": 0, "critical_demand": crit, "critical_served_first": served_first,
                    "critical_served_prop": crit, "diesel_power": 1000.0,
                    "diesel_fuel": fuel,
                    "battery_charge": 0.0, "soc_after": 50.0, "busbar_balance_error_w": 0.0,
                })
    return pd.DataFrame(rows)


SCALES = {"PC-Control": 1.0, "PC-S": 0.85, "PC-SW": 0.95, "PC-S-L": 0.90, "PC-SW-L": 0.60}


def test_evaluate_passes_all_safety_and_picks_largest_saving_as_winner():
    df = _synthetic_frame(SCALES)
    res = stat.evaluate(df)
    for cand in stat.CANDIDATES:
        c = res["candidates"][cand]
        assert c["S1_PASS"] and c["S2_PASS"] and c["S3_PASS"]
        assert c["E1_EVALUATED"] is True
    assert res["winner"] == "PC-SW-L"


def test_s1_failure_blocks_E1_evaluation_and_eligibility():
    df = _synthetic_frame(SCALES, crit_first_drop_arm="PC-SW-L")
    res = stat.evaluate(df)
    c = res["candidates"]["PC-SW-L"]
    assert c["S1_PASS"] is False
    assert c["E1_EVALUATED"] is False and c["E1_PASS"] is False
    assert res["winner"] != "PC-SW-L"


def test_soc_floor_violation_fails_S3():
    df = _synthetic_frame(SCALES)
    df.loc[(df.arm == "PC-S") & (df.hour == 5), "soc_after"] = 19.5
    s3 = stat.safety_gates(df, "PC-S")
    assert s3["S3_PASS"] is False and s3["soc_violations_below_20"] == 123


def test_T40_report_flag():
    res = stat.evaluate(_synthetic_frame(SCALES))
    assert res["candidates"]["PC-SW-L"]["T40_REPORT"] is True   # 40% saving
    assert res["candidates"]["PC-S"]["T40_REPORT"] is False


def test_d_comparisons_zero_difference_when_corrected_matches_frame():
    df = _synthetic_frame(SCALES)
    ctrl_fuel = stat.origin_fuel(df, "PC-Control")
    rel = stat.origin_reliability(df, "PC-Control")
    corr = pd.DataFrame({
        "origin_id": ctrl_fuel.index, "control_b_fuel_l": ctrl_fuel.values,
        "control_b_r_cf": rel["r_cf"].values, "control_b_r_p": rel["r_p"].values,
        "candidate_s_fuel_l": stat.origin_fuel(df, "PC-S").values,
        "candidate_s_r_cf": stat.origin_reliability(df, "PC-S")["r_cf"].values,
        "candidate_s_r_p": stat.origin_reliability(df, "PC-S")["r_p"].values,
    })
    d = stat.d_comparisons(df, corr)
    assert d["D1_PC-Control_minus_old_Control"]["fuel_L"]["mean_diff"] == pytest.approx(0.0)
    assert d["D2_PC-S_minus_old_S"]["R_P_pct"]["mean_diff"] == pytest.approx(0.0)
    # D3 is candidate minus control: a diesel saving is a negative fuel difference.
    assert d["D3_PC-SW-L_minus_PC-Control"]["fuel_L"]["mean_diff"] < 0


def test_report_writer_writes_table(tmp_path):
    res = stat.evaluate(_synthetic_frame(SCALES))
    out = tmp_path / "r.md"
    stat.write_summary_markdown(res, out)
    text = out.read_text()
    assert "PC-SW-L" in text and "Winner: PC-SW-L" in text


# ---------------------------------------------------------------------------
# Audit gates on synthetic data
# ---------------------------------------------------------------------------

def test_g4_flags_non_optimal_status():
    df = _synthetic_frame(SCALES)
    assert gates.g4_optimizer_status(df)["PASS"] is True
    df.loc[0, "solver_status"] = "HighsModelStatus.kInfeasible"
    assert gates.g4_optimizer_status(df)["PASS"] is False


def test_g6_lists_starvation_rows_and_fails_unlisted_mismatch():
    base ={"origin_id": 1, "hour": 0, "arm": "PC-S", "busbar_balance_error_w": 0.0, "soc_after": 50.0,
            "diesel_power": 0.0, "diesel_fuel": 0.0}
    ok = pd.DataFrame([base])
    assert gates.g6_busbar_soc_fuel(ok)["PASS"] is True
    starve = pd.DataFrame([dict(base, diesel_fuel=3.0)])
    r = gates.g6_busbar_soc_fuel(starve)
    assert r["PASS"] is True and len(r["starvation_rows_listed"]) == 1
    unlisted = pd.DataFrame([dict(base, diesel_power=20000.0, diesel_fuel=99.0)])
    assert gates.g6_busbar_soc_fuel(unlisted)["PASS"] is False


def test_g7_determinism_identical_passes_and_perturbed_fails():
    df = _synthetic_frame(SCALES)
    assert gates.g7_determinism(df, df.copy())["PASS"] is True
    pert = df.copy()
    pert.loc[10, "diesel_fuel"] += 1e-3
    assert gates.g7_determinism(df, pert)["PASS"] is False


def test_g9_counts_and_duplicates():
    df = _synthetic_frame(SCALES)
    r = gates.g9_accounting(df, runner.ARMS)
    assert r["PASS"] is True
    dup = pd.concat([df, df.iloc[:1]])
    assert gates.g9_accounting(dup, runner.ARMS)["PASS"] is False


def test_g10_route_and_em_rows():
    df = pd.DataFrame([{"route": "EMERGENCY", "optimizer_received_mode": "EMERGENCY", "em_rows_built": 24},
                       {"route": "NORMAL", "optimizer_received_mode": "NORMAL", "em_rows_built": 0}])
    assert gates.g10_route_propagation(df)["PASS"] is True
    bad = df.copy()
    bad.loc[0, "em_rows_built"] = 0
    assert gates.g10_route_propagation(bad)["PASS"] is False


def test_g1_realizability_within_1W():
    ex = pd.DataFrame([{"origin_id": 1, "step": 0, "planned_charge_w": 500.0}])
    rl = pd.DataFrame([{"origin_id": 1, "hour": 0, "battery_charge": 500.4}])
    assert gates.g1_realizability(rl, ex)["PASS"] is True
    rl.loc[0, "battery_charge"] = 503.0
    assert gates.g1_realizability(rl, ex)["PASS"] is False


def test_g12_blocks_origin_missing_window():
    origins = [pd.Timestamp("2025-05-01")] * 123
    keys = [(pd.Timestamp("2025-05-01") + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S") for j in range(47)]
    ok = gates.g12_oracle_coverage(origins, keys)
    assert ok["blocked_origins"] == [] and ok["PASS"] is True
    missing = gates.g12_oracle_coverage(origins, keys[:-1])
    assert missing["PASS"] is False and len(missing["blocked_origins"]) == 123


def test_g2_g3_wrappers_on_executed_records():
    ex = pd.DataFrame([{"origin_id": 1, "arm": "PC-S", "step": 0, "planned_unmet_nc_w": 500.0,
                        "planned_charge_w": 100.0, "planned_unmet_crit_w": 0.0, "pv_real_w": 0.0,
                        "wind_real_w": 0.0, "planned_diesel_w": 0.0, "d_c_w": 11600.0, "max_discharge_w": 0.0}])
    assert gates.g2_priority_inversion(ex)["PASS"] is False
    assert gates.g3_critical_infeasibility(ex)["PASS"] is True


def test_every_gate_has_executable_implementation():
    for name, fn in gates.GATE_IMPLEMENTATIONS.items():
        assert callable(fn), name
    assert set(gates.GATE_IMPLEMENTATIONS) == {"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G9", "G10", "G11", "G12"}


# ---------------------------------------------------------------------------
# Validation against FROZEN corrected telemetry (read-only; definitions only)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def frozen():
    tel = pd.read_csv(FROZEN_TEL)
    tel["arm"] = tel["arm"].map({"Control_Frozen_B": "PC-Control", "Candidate_S": "PC-S",
                                 "Candidate_SW": "PC-SW", "Candidate_SL": "PC-S-L",
                                 "Candidate_SWL": "PC-SW-L"})
    tel = tel.rename(columns={"hour": "hour", "origin_id": "origin_id"})
    return tel, pd.read_csv(FROZEN_RES)


def test_frozen_definitions_reproduce_corrected_results(frozen):
    tel, res = frozen
    fuel = stat.origin_fuel(tel, "PC-Control").to_numpy()
    assert fuel == pytest.approx(res["control_b_fuel_l"].to_numpy(), abs=1e-3)
    rel = stat.origin_reliability(tel, "PC-Control")
    assert rel["r_cf"].to_numpy() == pytest.approx(res["control_b_r_cf"].to_numpy(), abs=1e-4)
    assert rel["r_p"].to_numpy() == pytest.approx(res["control_b_r_p"].to_numpy(), abs=1e-4)


def test_frozen_G4_G6_pass_with_listed_starvation_row(frozen):
    tel, _ = frozen
    assert gates.g4_optimizer_status(tel)["PASS"] is True
    g6 = gates.g6_busbar_soc_fuel(tel)
    assert g6["unlisted_fuel_mismatches"] == 0
    assert len(g6["starvation_rows_listed"]) == 1
    assert g6["starvation_rows_listed"][0]["origin_id"] == 39


# ---------------------------------------------------------------------------
# Campaign post-run wiring (G2, G3, G4, G6, G7, G9, G10, G11 and statistics) on synthetic frames
# ---------------------------------------------------------------------------

def test_post_run_report_wires_gates_and_statistics():
    df = _synthetic_frame(SCALES)
    df["em_rows_built"] = 0
    df["route"] = "NORMAL"
    df["optimizer_received_mode"] = "NORMAL"
    ex = pd.DataFrame([{"origin_id": o, "arm": a, "step": h, "plan_hour": 0,
                        "planned_unmet_nc_w": 0.0, "planned_charge_w": 0.0, "planned_unmet_crit_w": 0.0,
                        "pv_real_w": 0.0, "wind_real_w": 0.0, "planned_diesel_w": 0.0, "d_c_w": 11600.0,
                        "max_discharge_w": 0.0}
                       for o in range(1, 124) for a in runner.ARMS for h in range(24)])
    repeat = df[(df.arm == "PC-Control") & (df.origin_id == 1)].copy()
    corr = pd.DataFrame({"origin_id": range(1, 124), "control_b_fuel_l": 1.0, "control_b_r_cf": 1.0,
                         "control_b_r_p": 1.0, "candidate_s_fuel_l": 1.0, "candidate_s_r_cf": 1.0,
                         "candidate_s_r_p": 1.0})
    rep = runner.build_post_run_report(df, ex, repeat, corr, REPO)
    for g in ("G2", "G3", "G4", "G6", "G7", "G9", "G10", "G11"):
        assert g in rep["gates"]
    assert rep["gates"]["G7"]["PASS"] is True
    assert rep["statistics"]["winner"] == "PC-SW-L"
    assert "D3_PC-SW-L_minus_PC-Control" in rep["d_comparisons"]


def test_g5_shortfall_residual_recorded_and_matched():
    hourly = pd.DataFrame([{"origin_id": 1, "hour": 0, "arm": "PC-S", "actual_solar": 0.0, "actual_wind": 0.0,
                            "diesel_power": 0.0, "battery_discharge": 0.0, "actual_demand": 15000.0,
                            "critical_served_first": 11000.0, "served_load": 11000.0}])
    executed = pd.DataFrame([{"origin_id": 1, "arm": "PC-S", "step": 0,
                              "planned_served_c_w": 11600.0, "planned_served_nc_w": 0.0}])
    r = gates.g5_shortfall_residual(hourly, executed)
    assert r["PASS"] is True and r["shortfall_hours"] == 1
    assert r["max_critical_residual_w"] == pytest.approx(600.0)
    assert gates.g5_shortfall_residual(hourly, executed.assign(step=5))["PASS"] is False
    assert "G5" in gates.GATE_IMPLEMENTATIONS


# ---------------------------------------------------------------------------
# Oracle output -> G1 / G12 wiring (synthetic OracleOriginResult objects; no oracle run)
# ---------------------------------------------------------------------------

import oracle_audit_adapter as oaa  # noqa: E402
from oracle_runner import OracleOriginResult  # noqa: E402


def _oracle_result(variant, charge_realized, charge_planned, origin_index=1):
    res = OracleOriginResult(origin="2025-05-01", variant=variant)
    res.hourly = [{"step": h, "charge_w": charge_realized} for h in range(24)]
    res.executed = [{"origin_id": origin_index, "arm": variant, "step": h, "plan_hour": 0,
                     "planned_charge_w": charge_planned} for h in range(24)]
    return res


def test_G1_wired_to_oracle_phys_passes_when_planned_equals_realized():
    pairs = [(1, _oracle_result("ORACLE-PHYS", 500.0, 500.4))]
    r = oaa.g1_for_oracle(pairs, "ORACLE-PHYS")
    assert r["PASS"] is True and r["rows"] == 24 and r["origins"] == 1


def test_G1_wired_to_oracle_phys_fails_on_charge_mismatch():
    pairs = [(1, _oracle_result("ORACLE-PHYS", 500.0, 510.0))]
    assert oaa.g1_for_oracle(pairs, "ORACLE-PHYS")["PASS"] is False


def test_G1_ignores_other_variant_pairs():
    pairs = [(1, _oracle_result("ORACLE-CTRL", 500.0, 900.0)),
             (1, _oracle_result("ORACLE-PHYS", 500.0, 500.0))]
    assert oaa.g1_for_oracle(pairs, "ORACLE-PHYS")["PASS"] is True


def test_G1_unmatched_rows_fail():
    res = _oracle_result("ORACLE-PHYS", 500.0, 500.0)
    res.executed = res.executed[:23]  # executed hour 23 missing -> realized row 23 is unmatched
    r1 = oaa.g1_for_oracle([(1, res)], "ORACLE-PHYS")
    assert r1["PASS"] is False and r1["unmatched"] >= 1
    full = _oracle_result("ORACLE-PHYS", 500.0, 500.0)
    full.hourly = full.hourly[:23]  # realized hour 23 missing -> executed row 23 is unmatched
    r2 = oaa.g1_for_oracle([(1, full)], "ORACLE-PHYS")
    assert r2["PASS"] is False and r2["unmatched"] >= 1


def test_G12_wired_to_sites_keys_blocks_missing_window():
    origins = [pd.Timestamp("2025-05-01")] * 123
    keys = [(pd.Timestamp("2025-05-01") + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S") for j in range(47)]
    assert oaa.g12_for_oracle(origins, keys)["PASS"] is True
    assert oaa.g12_for_oracle(origins, keys[:-1])["PASS"] is False


def test_G7_repeat_origin_rule_is_earliest_origin_index_one():
    origins = [pd.Timestamp("2025-05-02"), pd.Timestamp("2025-05-01")] + [pd.Timestamp("2025-06-01")] * 121
    assert oaa.g7_repeat_origin(origins) == 1
    src = inspect.getsource(runner.run_campaign)
    assert "fs1 = origins[0]" in src and "1, make_initial_state(t0_1)" in src


# ---------------------------------------------------------------------------
# G6 starvation mechanism (VERIFIED against frozen telemetry and executor code)
# ---------------------------------------------------------------------------

def test_starvation_row_mechanism_verified_on_frozen_telemetry(frozen):
    tel, _ = frozen
    sw = tel[(tel.arm == "PC-SW") & (tel.origin_id == 39)].sort_values("hour")
    cum_before = float(sw[sw.hour < 22]["diesel_fuel"].sum())
    row = sw[sw.hour == 22].iloc[0]
    # Fuel budget is 100 L per origin. Residual before hour 22 equals 100 - cumulative fuel.
    assert cum_before == pytest.approx(96.3707, abs=1e-4)
    assert float(row["diesel_fuel"]) == pytest.approx(100.0 - cum_before, abs=1e-3)
    # Realized diesel power is zero but the plan had diesel on (u=1, p>0) and fuel is consumed.
    assert float(row["diesel_power"]) == 0.0
    assert float(row["p_diesel"]) > 0.0 and float(row["u_diesel"]) == 1.0


def test_starvation_branch_present_in_frozen_executor_source():
    src = (REPO / "system/simulation/research_realization_executor.py").read_text()
    assert "max_p = max(0.0, (avail_fuel - self.base_fuel_lph) / self.marginal_fuel_lpwh)" in src
    assert "fuel_consumed = avail_fuel" in src
