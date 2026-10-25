"""Tests for the 2026-10-11 decision pass (D2, D6, D10, D4, Arm C A1-A6). Synthetic data only; no
repository data file is read; every solver interface is mocked to fail (conftest.no_solver)."""
import copy

import numpy as np
import pandas as pd
import pytest

import calibrate_arm_c as cal
import gates_three_arm as gates
import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf

ARMS = ("PC-Control", "A", "A_FIX", "B", "C")


@pytest.fixture(scope="module")
def stat():
    return r.load_frozen().stat


def telemetry(n_origins=30, unmet=None, fuel=None, seed=0):
    """Synthetic hourly telemetry for all arms. unmet/fuel: {arm: per-hour value or callable(o, h)}."""
    rng = np.random.default_rng(seed)
    rows = []
    for arm in ARMS:
        for o in range(1, n_origins + 1):
            for h in range(24):
                u = (unmet or {}).get(arm, 0.0)
                f = (fuel or {}).get(arm, 1.0)
                rows.append({"arm": arm, "origin_id": o, "hour": h,
                             "forecast_start": (pd.Timestamp("2024-05-01") + pd.Timedelta(days=o - 1)).strftime("%Y-%m-%d %H:%M:%S"),
                             "unmet_load": float(u(o, h) if callable(u) else u),
                             "diesel_fuel": float(f(o, h) if callable(f) else f) + 0.001 * rng.random(),
                             "critical_demand": 11600.0, "critical_served_first": 11600.0,
                             "critical_served_prop": 11600.0, "soc_after": 60.0, "curtailment": 0.0,
                             "diesel_power": 0.0, "held_cloud_hours": h, "solver_status": "OPTIMAL",
                             "e_after_wh": 140000.0})
    return pd.DataFrame(rows)


def gcfg(**over):
    c = sf.approve_everything(sf.load_real_cfg())
    c["gates"].update(over)
    return c


# ---------------------------------------------------------------- D2: S4 point estimate
def test_s4_tie_passes():
    df = telemetry(unmet={a: 5.0 for a in ARMS})
    res = gates.s4_point(df, "C")
    assert res["PASS"] and res["delta_Wh"] == 0.0 and res["U_arm_Wh"] == res["U_ref_Wh"] == 5.0 * 24 * 30
    assert res["origins_equal"] == 30


def test_s4_regression_fails_by_one_hundredth_watt():
    df = telemetry(unmet={a: 5.0 for a in ARMS})
    df.loc[(df.arm == "C") & (df.origin_id == 7) & (df.hour == 13), "unmet_load"] = 5.01
    res = gates.s4_point(df, "C")
    assert not res["PASS"] and res["delta_Wh"] == pytest.approx(0.01) and res["origins_worse"] == 1
    assert list(res["worst_5_origins"])[0] == 7


def test_s4_improvement_passes():
    df = telemetry(unmet={"PC-Control": 10.0, "C": 2.0})
    assert gates.s4_point(df, "C")["PASS"]


@pytest.mark.parametrize("mut,msg", [
    (lambda d: d.drop(d[(d.arm == "C") & (d.origin_id == 3) & (d.hour == 5)].index), "unpaired"),
    (lambda d: d.drop(d[(d.arm == "PC-Control") & (d.origin_id == 3) & (d.hour == 5)].index), "unpaired"),
    (lambda d: pd.concat([d, d[(d.arm == "C") & (d.origin_id == 1) & (d.hour == 0)]]), "duplicate"),
    (lambda d: d.assign(unmet_load=np.where((d.arm == "C") & (d.hour == 2), np.nan, d.unmet_load)), "non-finite"),
    (lambda d: d.assign(solver_status=np.where((d.arm == "C") & (d.hour == 2), "INFEASIBLE", d.solver_status)), "non-optimal"),
    (lambda d: d[d.arm != "C"], "no rows"),
    (lambda d: d[~((d.origin_id == 4) & (d.hour == 23))], "hours 0..23"),
])
def test_s4_missing_failed_or_unpaired_is_not_evaluable(mut, msg):
    """Removing a cell where the candidate is worse must not produce a pass."""
    df = mut(telemetry(unmet={a: 0.0 for a in ARMS}))
    res = gates.s4_point(df, "C")
    assert res["status"] == "NOT EVALUABLE" and res["PASS"] is False
    assert any(msg in p for p in res["problems"]), res["problems"]


def test_s4_failed_arm_makes_verdict_not_an_improvement(stat):
    df = telemetry(fuel={"PC-Control": 2.0, "A": 1.0, "A_FIX": 1.0, "B": 1.0, "C": 1.0})
    df = df.drop(df[(df.arm == "C") & (df.origin_id == 2) & (df.hour == 9)].index)
    out = gates.evaluate(df, gcfg(), r.ARM_CONFIGS, stat)
    assert out["arms"]["C"]["S4_point"]["status"] == "NOT EVALUABLE"
    assert out["arms"]["C"]["verdict"].startswith("NOT AN IMPROVEMENT")
    assert out["arms"]["C"]["E1"]["PASS"] is False


# ---------------------------------------------------------------- D6: strict S4
def _manual_stationary(x, block, B, seed):
    rng = np.random.default_rng(seed)
    n = len(x)
    starts = rng.integers(n, size=(B, n))
    u = rng.random((B, n))
    out = np.empty(B)
    for b in range(B):
        idx = np.empty(n, dtype=int)
        for t in range(n):
            idx[t] = starts[b, t] if (t == 0 or u[b, t] < 1.0 / block) else (idx[t - 1] + 1) % n
        out[b] = x[idx].mean()
    return out


def test_stationary_bootstrap_matches_documented_algorithm():
    x = np.sin(np.arange(40) * 0.7) * 3.0
    assert np.allclose(gates.stationary_bootstrap_means(x, 10, 500, 42), _manual_stationary(x, 10, 500, 42))


def test_stationary_bootstrap_is_seeded_and_reproducible():
    x = np.arange(30.0)
    a = gates.stationary_bootstrap_means(x, 10, 1000, 42)
    assert np.array_equal(a, gates.stationary_bootstrap_means(x, 10, 1000, 42))
    assert not np.array_equal(a, gates.stationary_bootstrap_means(x, 10, 1000, 43))


def test_strict_s4_uses_config_seed_block_and_interval():
    df = telemetry(unmet={"PC-Control": 5.0, "C": lambda o, h: 5.0 + (0.5 if o % 3 == 0 else -0.4)})
    g = gcfg()["gates"]
    res = gates.s4_strict(df, "C", g)
    du = gates.per_origin_delta_unmet(df, "C").to_numpy()
    exp = np.percentile(gates.stationary_bootstrap_means(du, 10, 10000, 42), 97.5)
    assert res["upper_bound_Wh_per_origin"] == pytest.approx(exp)
    assert res["bootstrap"]["seed"] == 42 and res["bootstrap"]["mean_block_days"] == 10 and res["bootstrap"]["resamples"] == 10000
    assert res["percentile"] == 97.5
    g2 = copy.deepcopy(g)
    g2["S4_strict_interval"] = "one_sided_95_upper"
    assert gates.s4_strict(df, "C", g2)["percentile"] == 95.0


def test_point_and_strict_s4_reported_separately(stat):
    """A candidate can pass the point criterion yet fail the strict one; both are visible."""
    def u(o, h):
        return 10.0 if (o <= 10 and h == 12) else 0.0
    def uc(o, h):
        return 400.0 if (o == 30 and h == 12) else 0.0
    df = telemetry(unmet={"PC-Control": uc, "C": u})
    out = gates.evaluate(df, gcfg(), r.ARM_CONFIGS, stat)
    c = out["arms"]["C"]
    assert c["S4_point"]["PASS"] is True and c["S4_strict"]["PASS"] is False
    assert c["reliability_gates_PASS"] is False


def test_strict_s4_not_evaluable_on_missing_pair():
    df = telemetry()
    df = df.drop(df[(df.arm == "C") & (df.origin_id == 1) & (df.hour == 0)].index)
    res = gates.s4_strict(df, "C", gcfg()["gates"])
    assert res["status"] == "NOT EVALUABLE" and res["PASS"] is False


# ---------------------------------------------------------------- D10: E1 family
@pytest.mark.parametrize("family", [["A", "C"], ["A", "A_FIX", "C"]])
def test_e1_family_is_exactly_the_configured_one(stat, family):
    df = telemetry(fuel={"PC-Control": 2.0, "A": 1.5, "A_FIX": 1.4, "B": 0.5, "C": 1.2})
    out = gates.evaluate(df, gcfg(E1_holm_family=family), r.ARM_CONFIGS, stat)
    assert [a for a in gates.REPORTED_ARMS if "E1" in out["arms"][a]] == family
    assert out["E1_family_size"] == len(family)
    for a in family:
        e = out["arms"][a]["E1"]
        assert e["holm_family_size"] == len(family)
        for k in ("wilcoxon_statistic", "wilcoxon_p", "holm_adj_p", "mean_saving_L_per_origin", "bca95_low", "bca95_high"):
            assert k in e
    assert "E1" not in out["arms"]["B"]
    assert out["winner"] is None


def test_holm_family_not_shrunk_when_an_arm_fails_safety(stat):
    df = telemetry(fuel={"PC-Control": 2.0, "A": 1.5, "A_FIX": 1.4, "B": 0.5, "C": 1.2})
    df.loc[(df.arm == "A") & (df.hour == 3), "soc_after"] = 10.0     # S3 fails for A
    out = gates.evaluate(df, gcfg(E1_holm_family=["A", "A_FIX", "C"]), r.ARM_CONFIGS, stat)
    ps = [out["arms"][a]["E1"]["wilcoxon_p"] for a in ("A", "A_FIX", "C")]
    assert [out["arms"][a]["E1"]["holm_adj_p"] for a in ("A", "A_FIX", "C")] == stat.holm_adjust(ps)
    assert out["arms"]["A"]["E1"]["PASS"] is False


@pytest.mark.parametrize("family", [["B"], ["A", "B"], ["PC-Control"], ["C", "C"], None, []])
def test_arm_b_and_invalid_families_cannot_enter_e1(stat, family):
    df = telemetry()
    with pytest.raises(gates.GateConfigError):
        gates.evaluate(df, gcfg(E1_holm_family=family), r.ARM_CONFIGS, stat)
    if family and "B" in family:
        assert any("'B'" in f for f in pf.check_gates(gcfg(E1_holm_family=family)))


def test_arm_b_verdict_never_eligible(stat):
    df = telemetry(fuel={"PC-Control": 2.0, "B": 0.1})
    out = gates.evaluate(df, gcfg(), r.ARM_CONFIGS, stat)
    assert out["arms"]["B"]["verdict"] == "NONCAUSAL DIAGNOSTIC — NOT DEPLOYABLE — NEVER ELIGIBLE"
    assert out["arms"]["B"]["in_E1_family"] is False and out["arms"]["B"]["promotion_eligible"] is False


# ---------------------------------------------------------------- D4: primary vs secondary
def test_primary_fuel_is_unadjusted_and_secondary_is_separate(stat):
    df = telemetry(fuel={"PC-Control": 2.0, "A": 1.5, "A_FIX": 1.5, "B": 1.0, "C": 1.5})
    df.loc[(df.arm == "C") & (df.hour == 23), "e_after_wh"] = 120000.0   # C ends 20 kWh lower each origin
    out = gates.evaluate(df, gcfg(), r.ARM_CONFIGS, stat)
    c = out["arms"]["C"]
    delta = (stat.origin_fuel(df, "PC-Control") - stat.origin_fuel(df, "C")).to_numpy()
    assert c["E1"]["mean_saving_L_per_origin"] == pytest.approx(delta.mean())      # primary: unadjusted
    sec = c["secondary_soc_parity_fuel"]
    assert sec["status"].startswith("REPORTED (secondary")
    for f in ("0.30", "0.75"):
        exp = float(stat.origin_fuel(df, "C").sum()) + 30 * 20.0 / 0.92 * float(f)
        assert sec["by_f"][f]["adjusted_fuel_L"] == pytest.approx(exp)
    assert c["E1"]["mean_saving_L_per_origin"] == pytest.approx(delta.mean())       # unchanged by secondary


def test_secondary_blocked_unless_approved(stat):
    df = telemetry()
    cfg = gcfg()
    cfg["gates"]["soc_parity_secondary"]["status"] = "BLOCKED"
    out = gates.evaluate(df, cfg, r.ARM_CONFIGS, stat)
    assert out["arms"]["C"]["secondary_soc_parity_fuel"]["status"].startswith("BLOCKED")


def test_primary_metric_cannot_be_switched(stat):
    with pytest.raises(gates.GateConfigError):
        gates.evaluate(telemetry(), gcfg(primary_fuel_metric="soc_parity_adjusted"), r.ARM_CONFIGS, stat)


# ---------------------------------------------------------------- Arm C A1-A6
def test_a1_split_conformal_rule():
    r_ = np.arange(1.0, 101.0)            # n=100, alpha=0.1 -> k=floor(10.1)=10 -> 10th smallest
    assert cal.alpha_quantile(r_, 0.1, "split_conformal_lower") == 10.0
    assert cal.alpha_quantile(r_, 0.1, "split_conformal_lower") <= cal.alpha_quantile(r_, 0.1, "inverted_cdf")


def test_a2_protocol_literal_bins():
    el = np.array([0.5, 5.0, 5.01, 15.0, 15.01, 30.0, 30.01, 90.0])
    assert cal.assign_bin(el, [0, 5, 15, 30, 90], "right_closed").tolist() == [0, 0, 1, 1, 2, 2, 3, 3]
    cf = np.array([0.0, 0.19, 0.2, 0.5, 0.8, 0.81, 1.0])
    assert cal.assign_bin(cf, [0, 0.2, 0.8, 1.0], "closed_middle").tolist() == [0, 0, 1, 1, 1, 2, 2]
    with pytest.raises(cal.CalibrationError):
        cal.assign_bin(el, [0, 5, 15, 30, 90], "closed_middle")
    assert cal.dim_rule({"elevation": "right_closed", "cloud": "closed_middle"}, "cloud") == "closed_middle"
    assert cal.dim_rule("left_closed", "elevation") == "left_closed"
    with pytest.raises(cal.CalibrationError):
        cal.assign_bin(cf, [0, 0.2, 0.8, 1.0], cal.dim_rule({"elevation": "right_closed"}, "cloud"))


def _rows_with_counts(counts):
    """counts: {(eb, cb): n_origins}. One daylight hour per origin per cell, synthetic residuals."""
    centers_el, centers_cf = [2.5, 10.0, 20.0, 40.0], [0.1, 0.5, 0.9]
    rows = []
    for (e, c), n in counts.items():
        for o in range(n):
            rows.append({"forecast_start": f"2024-01-{o % 28 + 1:02d} 00:00:00" if o < 28 else f"2024-02-{o - 27:02d} 00:00:00",
                         "elevation_deg": centers_el[e], "cloud_frac": centers_cf[c], "clear_sky_ghi": 500.0,
                         "actual_SW_IN": 300.0 + 10 * (o % 7) + e, "daylight": True})
    return pd.DataFrame(rows)


def _method(**over):
    m = {"alpha": 0.1, "elevation_bin_edges_deg": [0, 5, 15, 30, 90], "cloud_bin_edges_fraction": [0, 0.2, 0.8, 1.0],
         "bin_boundary_rule": {"elevation": "right_closed", "cloud": "closed_middle"},
         "quantile_method": "split_conformal_lower", "min_origin_days_per_bin": 20,
         "insufficient_bin_policy": "merge_single_neighbour_else_lower", "residual_space": "ghi_w_m2"}
    m.update(over)
    return m


def _full(n=25):
    return {(e, c): n for e in range(4) for c in range(3)}


def test_a3_top_bin_merges_into_its_only_neighbour():
    counts = _full()
    counts[(3, 1)] = 5
    qt = cal.quantile_table(_rows_with_counts(counts), 0.5, _method(), lambda x: x)
    assert qt["merges"] == [{"from": [3, 1], "into": [2, 1], "origin_days_before_merge": 5}]


def test_a3_bottom_bin_merges_upward_and_interior_merges_lower():
    counts = _full()
    counts[(0, 0)] = 3
    counts[(2, 2)] = 4
    qt = cal.quantile_table(_rows_with_counts(counts), 0.5, _method(), lambda x: x)
    m = {tuple(x["from"]): tuple(x["into"]) for x in qt["merges"]}
    assert m[(0, 0)] == (1, 0) and m[(2, 2)] == (1, 2)
    assert len(qt["table"]) == 12


def test_a3_no_neighbour_left_fails_closed():
    counts = {(e, 0): 2 for e in range(4)}
    counts.update({(e, c): 25 for e in range(4) for c in (1, 2)})
    with pytest.raises(cal.InsufficientBinError, match="no neighbour"):
        cal.quantile_table(_rows_with_counts(counts), 0.5, _method(), lambda x: x)


def test_a4_origin_day_counts_distinct_origins_and_requires_midnight_origins():
    counts = _full()
    rows = _rows_with_counts(counts)
    dup = rows.iloc[:5].copy()                      # same origins again in the same cell: not new origin-days
    qt = cal.quantile_table(pd.concat([rows, dup]), 0.5, _method(), lambda x: x)
    cell = [t for t in qt["table"] if (t["elevation_bin"], t["cloud_bin"]) == (0, 0)][0]
    assert cell["origin_days"] == 25 and cell["n_hours"] == 30
    w = sf.synthetic_weather(["2024-02-01"])
    w["forecast_start"] = "2024-02-01 06:00:00"
    w["timestamp"] = [(pd.Timestamp("2024-02-01 06:00") + pd.Timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S") for h in range(24)]
    with pytest.raises(cal.CalibrationError, match="00:00"):
        cal.validate_calibration_rows(w)


def test_a5_ghi_residual_space_equals_pv_space_below_clip():
    pv = lambda g: max(0.0, min(g * 51.0, 60000.0))
    pt, q = np.array([100.0, 400.0, 800.0]), -50.0
    lb_ghi = np.maximum(0.0, np.minimum(pt, pt + q))
    assert [pv(x) for x in lb_ghi] == pytest.approx([max(0.0, min(pv(p), pv(p) + 51.0 * q)) for p in pt])


def test_a6_tie_rule_largest_gamma():
    rows = pd.DataFrame({"daylight": [True] * 3, "clear_sky_ghi": [500.0] * 3, "cloud_frac": [0.0] * 3,
                         "actual_SW_IN": [400.0, 450.0, 500.0]})
    assert cal.fit_gamma(rows, cal.gamma_grid({"start": 0.1, "stop": 1.0, "step": 0.01}), "largest_gamma")["gamma_hat"] == pytest.approx(1.0)


def test_recommended_values_are_valid_and_now_delegated():
    m = sf.load_real_cfg()["arm_c_method"]
    assert m["quantile_method"]["value"] in cal.QUANTILE_METHODS
    assert m["bin_boundary_rule"]["value"] == {"elevation": "right_closed", "cloud": "closed_middle"}
    assert m["insufficient_bin_policy"]["value"] in cal.INSUFFICIENT_POLICIES
    assert m["residual_space"]["value"] in cal.RESIDUAL_SPACES
    assert m["gamma_tie_rule"]["value"] in cal.TIE_RULES
    for k in ("quantile_method", "bin_boundary_rule", "insufficient_bin_policy", "origin_day_definition",
              "residual_space", "gamma_tie_rule"):
        # M6-M8: RECOMMENDED; M9: resolved by delegated technical authority, value unchanged, authority named
        assert m[k]["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY" and "M9" in m[k]["authority"]


# ---------------------------------------------------------------- input restriction before processing
def test_two_pass_reader_never_parses_excluded_values(tmp_path):
    days = ["2024-04-28", "2024-04-29", "2024-04-30", "2024-05-01", "2024-08-31", "2024-09-01", "2024-09-02"]
    w = sf.synthetic_weather(days).astype({"actual_SW_IN": object})
    bad = ~pd.to_datetime(w.forecast_start).isin(pd.to_datetime(["2024-04-28", "2024-04-29", "2024-09-02"]))
    w.loc[bad, "actual_SW_IN"] = "POISON-EXCLUDED-VALUE"
    p = tmp_path / "w.csv"
    w.to_csv(p, index=False)
    cfg = sf.load_real_cfg()
    rows = cal.read_calibration_input(p, cfg["evaluation"], cfg["calibration_window"])
    assert sorted(rows.forecast_start.unique()) == ["2024-04-28 00:00:00", "2024-04-29 00:00:00", "2024-09-02 00:00:00"]
    assert rows["actual_SW_IN"].dtype.kind == "f"


def test_two_pass_reader_rejects_2025_before_values(tmp_path):
    w = sf.synthetic_weather(["2024-02-01", "2024-02-02"]).astype({"actual_SW_IN": object})
    w.loc[30, "timestamp"] = "2025-06-01 05:00:00"
    w["actual_SW_IN"] = "POISON"
    p = tmp_path / "w.csv"
    w.to_csv(p, index=False)
    cfg = sf.load_real_cfg()
    with pytest.raises(PermissionError):
        cal.read_calibration_input(p, cfg["evaluation"], cfg["calibration_window"])


def test_calibration_main_reads_nothing_before_authorization(tmp_path, monkeypatch):
    repo = sf.build_fake_repo(tmp_path)
    monkeypatch.setattr(cal, "read_calibration_input", lambda *a, **k: (_ for _ in ()).throw(AssertionError("read")))
    assert cal.main(["--repo", str(repo)]) == 2
