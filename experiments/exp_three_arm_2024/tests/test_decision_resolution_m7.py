"""Tests for the second 2026-10-11 decision pass (M7: D10, D6 sign and interval, D4 application, Arm C
A1-A6/A8 and D5). Synthetic data only; no repository data file is read; every solver interface is mocked
to fail (conftest.no_solver)."""
import copy

import numpy as np
import pandas as pd
import pytest

import calibrate_arm_c as cal
import gates_three_arm as gates
import preflight as pf
import run_three_arm_2024 as r
import synthetic_fixtures as sf
from test_decision_resolution import ARMS, gcfg, telemetry


@pytest.fixture(scope="module")
def stat():
    return r.load_frozen().stat


# ---------------------------------------------------------------- D10: protocol family {A, C}
def test_d10_real_config_is_the_protocol_family():
    cfg = sf.load_real_cfg()
    assert cfg["gates"]["E1_holm_family"] == ["A", "C"]
    assert cfg["decisions"]["D10"]["status"] == "APPROVED"
    assert "M7" in cfg["decisions"]["D10"]["evidence"] and "PROTOCOL.md §7" in cfg["decisions"]["D10"]["evidence"]
    assert not any("E1_holm_family" in f for f in pf.check_gates(cfg))


def test_d10_a_fix_is_diagnostic_only(stat):
    df = telemetry(fuel={"PC-Control": 2.0, "A": 1.5, "A_FIX": 1.0, "B": 0.5, "C": 1.2})
    out = gates.evaluate(df, gcfg(E1_holm_family=sf.load_real_cfg()["gates"]["E1_holm_family"]), r.ARM_CONFIGS, stat)
    assert out["E1_family_size"] == 2
    assert "E1" not in out["arms"]["A_FIX"] and out["arms"]["A_FIX"]["in_E1_family"] is False
    assert out["arms"]["A"]["E1"]["holm_family_size"] == 2 and out["arms"]["C"]["E1"]["holm_family_size"] == 2
    assert {"A_vs_A_FIX", "A_FIX_vs_C"} <= set(out["diagnostic_comparisons"])
    assert out["winner"] is None


# ---------------------------------------------------------------- D6: sign convention and interval
def test_d6_delta_is_arm_minus_control():
    df = telemetry(unmet={"PC-Control": 2.0, "C": 5.0})
    du = gates.per_origin_delta_unmet(df, "C")
    assert np.allclose(du.to_numpy(), 24 * (5.0 - 2.0))      # positive = arm has more unmet energy = worse


@pytest.mark.parametrize("arm_unmet,expect_pass,sign", [
    (5.0, False, 1),     # arm worse on every origin -> upper bound > 0 -> FAIL
    (1.0, True, -1),     # arm better on every origin -> upper bound < 0 -> PASS
    (2.0, True, 0),      # identical -> upper bound == 0 -> PASS (ties pass, as S4)
])
def test_d6_upper_bound_le_zero_is_the_non_regression_direction(arm_unmet, expect_pass, sign):
    df = telemetry(unmet={"PC-Control": 2.0, "C": lambda o, h: arm_unmet + (0.01 * (o % 5) if arm_unmet != 2.0 else 0.0)})
    res = gates.s4_strict(df, "C", gcfg()["gates"])
    assert res["PASS"] is expect_pass
    assert np.sign(res["upper_bound_Wh_per_origin"]) == sign
    assert gates.s4_point(df, "C")["PASS"] is expect_pass


def test_d6_two_sided_upper_endpoint_is_the_97_5th_percentile():
    df = telemetry(unmet={"PC-Control": 5.0, "C": lambda o, h: 5.0 + (0.5 if o % 3 == 0 else -0.4)})
    g = gcfg(S4_strict_interval="two_sided_95_upper")["gates"]
    res = gates.s4_strict(df, "C", g)
    means = gates.stationary_bootstrap_means(gates.per_origin_delta_unmet(df, "C").to_numpy(), 10, 10000, 42)
    lo, hi = np.percentile(means, [2.5, 97.5])
    assert res["upper_bound_Wh_per_origin"] == pytest.approx(hi) and lo <= res["mean_delta_U_Wh_per_origin"] <= hi


def test_d6_interval_seed_block_resamples_approved_and_used():
    """M8: the project lead approved the two-sided 95% interval (97.5th percentile), seed 42, 10-day blocks,
    10,000 resamples. The real config must carry exactly these, and s4_strict must use them."""
    cfg = sf.load_real_cfg()
    g = cfg["gates"]
    assert cfg["decisions"]["D6"]["status"] == "APPROVED" and "M8" in cfg["decisions"]["D6"]["evidence"]
    assert g["S4_strict_interval"] == "two_sided_95_upper" and g["S4_strict_interval_record"]["percentile"] == 97.5
    assert g["S4_strict_bootstrap_seed"] == 42
    assert g["S4_strict_mean_block_days"] == {**g["S4_strict_mean_block_days"], "value": 10, "status": "APPROVED"}
    assert g["S4_strict_resamples"] == {**g["S4_strict_resamples"], "value": 10000, "status": "APPROVED"}
    assert not any("S4_strict" in f for f in pf.check_gates(cfg))
    df = telemetry(unmet={"PC-Control": 5.0, "C": lambda o, h: 5.0 + (0.5 if o % 3 == 0 else -0.4)})
    res = gates.s4_strict(df, "C", g)
    assert res["percentile"] == 97.5 and res["bootstrap"]["seed"] == 42
    assert res["bootstrap"]["mean_block_days"] == 10 and res["bootstrap"]["resamples"] == 10000


# ---------------------------------------------------------------- D4: per-origin application
def _gap_telemetry():
    """Control ends every origin at 140 kWh; the arm ends 10 kWh lower on odd origins and 10 kWh higher on
    even ones, so the aggregate gap is zero but per-origin deficits exist. Fuel is identical."""
    df = telemetry(fuel={a: 1.0 for a in ARMS})
    odd = (df.arm == "C") & (df.hour == 23) & (df.origin_id % 2 == 1)
    even = (df.arm == "C") & (df.hour == 23) & (df.origin_id % 2 == 0)
    df.loc[odd, "e_after_wh"] = 130000.0
    df.loc[even, "e_after_wh"] = 150000.0
    return df


def test_d4_per_origin_does_not_net_surplus_against_deficit(stat):
    df = _gap_telemetry()
    res = gates.secondary_soc_parity(df, "C", gcfg()["gates"], stat)
    assert res["origins_arm_ends_lower"] == 15 and res["mean_end_energy_gap_kwh"] == pytest.approx(5.0)
    fuel_c = float(stat.origin_fuel(df, "C").sum())
    for f in (0.30, 0.75):
        per_origin = fuel_c + 15 * 10.0 * (1 / 0.92) * f
        assert res["by_f"][f"{f:.2f}"]["adjusted_fuel_L"] == pytest.approx(per_origin)
    # the aggregate reading would add max(0, sum of gaps) = 0 here; it is not implemented and is refused
    g = gcfg()["gates"]
    g["soc_parity_secondary"]["application"] = "aggregate"
    with pytest.raises(gates.GateConfigError):
        gates.secondary_soc_parity(df, "C", g, stat)


def test_d4_secondary_per_origin_delegated_and_formula_unchanged(stat):
    """M8: application blocked. M9: per-origin application of the unchanged formula, delegated, secondary only."""
    g = sf.load_real_cfg()["gates"]["soc_parity_secondary"]
    assert g["application"] == "per_origin" and g["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY"
    assert "Not part of the original preregistered text" in g["application_record"]
    assert "never decision-bearing" in g["limitations"] and g["role"].startswith("secondary")
    assert g["protocol_text_verbatim"].startswith(
        "SoC-parity-adjusted fuel = fuel + max(0, E_end,ctrl − E_end,arm)·(1/0.92)·f, with f ∈ {0.30, 0.75} L/kWh")
    assert g["protocol_aggregation_semantics"].startswith("NOT STATED")
    assert "formula" not in g      # the per-origin form is recorded separately, never as the protocol text
    assert g["f_values_l_per_kwh"] == [0.3, 0.75]
    res = gates.secondary_soc_parity(_gap_telemetry(), "C", sf.load_real_cfg()["gates"], stat)
    assert res["status"] == "REPORTED (secondary, not decision-bearing)"
    assert res["applied_form"] == g["per_origin_form"] and set(res["by_f"]) == {"0.30", "0.75"}


# ---------------------------------------------------------------- D5 values come from PROTOCOL §4 only
def test_d5_values_are_the_protocol_values_unchanged_by_m9():
    m = sf.load_real_cfg()["arm_c_method"]
    assert m["alpha"]["value"] == 0.10
    assert m["elevation_bin_edges_deg"]["value"] == [0.0, 5.0, 15.0, 30.0, 90.0]
    assert m["cloud_bin_edges_fraction"]["value"] == [0.0, 0.2, 0.8, 1.0]
    assert m["min_origin_days_per_bin"]["value"] == 20
    assert (m["gamma_grid"]["start"], m["gamma_grid"]["stop"], m["gamma_grid"]["step"]) == (0.1, 1.0, 0.01)
    assert len(cal.gamma_grid(m["gamma_grid"])) == 91
    for k in ("alpha", "elevation_bin_edges_deg", "cloud_bin_edges_fraction", "min_origin_days_per_bin",
              "gamma_grid", "gamma_objective"):
        assert m[k]["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY", k   # M8: PROPOSED
        assert m[k]["basis"].startswith("PROTOCOL.md §4"), k
    assert sf.load_real_cfg()["decisions"]["D5"]["status"] == "RESOLVED BY DELEGATED TECHNICAL AUTHORITY"
    assert m["gamma_objective"]["citation_status"].startswith("UNVERIFIED")      # provenance stays unverified
    assert m["min_origin_days_per_bin"]["citation_status"].startswith("UNVERIFIED")


def test_a2_integer_percent_edges_fall_in_the_middle_cloud_bin():
    idx = cal.assign_bin(np.array([19, 20, 80, 81]) / 100.0, [0.0, 0.2, 0.8, 1.0], "closed_middle")
    assert idx.tolist() == [0, 1, 1, 2]


# ---------------------------------------------------------------- A5 calibration-time diagnostic

def _diag_rows(actuals):
    n = len(actuals)
    return pd.DataFrame({"daylight": [True] * n, "clear_sky_ghi": [600.0] * n, "cloud_frac": [0.1] * n,
                         "actual_SW_IN": actuals})


def test_a5_diagnostic_zero_below_clip_and_counts_clipped_hours():
    pv = lambda g: max(0.0, min(g * 51.0, 60000.0))
    d0 = cal.residual_space_diagnostic(_diag_rows([100.0, 500.0, 900.0]), 0.5, pv)
    assert d0["n_hours_pv_map_nonlinear"] == 0 and d0["pv_slope_w_per_w_m2"] == 51.0
    d1 = cal.residual_space_diagnostic(_diag_rows([100.0, 1300.0]), 0.5, pv)
    assert d1["n_hours_pv_map_nonlinear"] == 1
    assert d1["max_point_ghi_w_m2"] < 60000.0 / 51.0


def test_a5_diagnostic_is_in_the_artifact(monkeypatch):
    cfg = sf.approve_everything(sf.load_real_cfg())
    days = [str(d.date()) for d in pd.date_range("2024-01-01", periods=40)]
    w = sf.synthetic_weather(days)
    rows = cal.attach_geometry(w, lambda fs: ([0.0] * 6 + [300.0] * 12 + [0.0] * 6,
                                              [-5.0] * 6 + [10.0] * 12 + [-5.0] * 6))
    monkeypatch.setattr(cal, "quantile_table", lambda *a, **k: {"stub": True})  # bins are tested elsewhere
    art = cal.build_artifact(rows, cfg, {}, "synthetic", lambda g: max(0.0, min(g * 51.0, 60000.0)))
    assert "residual_space_diagnostic" in art and art["residual_space_diagnostic"]["n_daylight_hours"] == 40 * 12


# ---------------------------------------------------------------- A8 daylight rule consistency
def test_a8_daylight_rule_is_the_same_in_calibration_and_at_run_time():
    w = sf.synthetic_weather(["2024-01-05"])
    cs = [0.0, 50.0, 0.0] + [100.0] * 21
    el = [2.0, -1.0, 0.0] + [10.0] * 21
    rows = cal.attach_geometry(w, lambda fs: (cs, el))
    assert rows["daylight"].tolist()[:3] == [False, False, False]
    qt = {"residual_space": "ghi_w_m2", "elevation_bin_edges_deg": [0.0, 5.0, 15.0, 30.0, 90.0],
          "cloud_bin_edges_fraction": [0.0, 0.2, 0.8, 1.0],
          "bin_boundary_rule": {"elevation": "right_closed", "cloud": "closed_middle"},
          "table": [{"elevation_bin": e, "cloud_bin": c, "q_alpha": -10.0} for e in range(4) for c in range(3)]}
    lb = cal.lower_bound([40.0, 40.0, 40.0, 40.0], el[:4], [0.5] * 4, cs[:4], qt)
    assert lb == [0.0, 0.0, 0.0, 30.0]


def test_a8_recorded_as_recommendation_not_protocol():
    o = sf.load_real_cfg()["arm_c_method"]["gamma_objective"]
    assert o["daylight_rule"] == "elevation>0 and clearsky_ghi>0" and o["daylight_rule_ref"] == "A8"
    assert "without a definition" in o["daylight_rule_note"] and "A8 clarification" in o["daylight_rule_note"]
    assert "A8 clarification" in o["basis"]


# ---------------------------------------------------------------- M8: protocol text verbatim
def test_m8_protocol_soc_text_is_copied_verbatim_from_protocol():
    import pathlib
    proto = (pathlib.Path(sf.__file__).resolve().parents[1] / "reports/source_prep/PROTOCOL.md").read_text()
    text = sf.load_real_cfg()["gates"]["soc_parity_secondary"]["protocol_text_verbatim"]
    assert text.split("  [PROTOCOL.md")[0] in proto


# ---------------------------------------------------------------- M8: D10a classification conflict blocks execution
def test_m8_d10a_is_an_execution_decision_and_d10_unchanged():
    cfg = sf.load_real_cfg()
    fails = pf.check_decisions(cfg, pf.EXECUTION_DECISIONS)
    assert "D10a" in pf.EXECUTION_DECISIONS and "D10a" not in pf.CALIBRATION_DECISIONS
    assert not any("decision D10a " in f for f in fails)            # M9: resolved (amendment 1)
    assert not any("decision D10 " in f for f in fails)
    assert cfg["decisions"]["D10"]["status"] == "APPROVED"


def test_m8_d7a_c_label_follows_amendment_1():
    # M8: DIAGNOSTIC (D7a §1 as written). M9: PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md (D10a resolved)
    assert r.LABEL_C.startswith("RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE")
    assert r.LABEL_A_FIX == "DIAGNOSTIC — NOT PROMOTION-ELIGIBLE"


# ---------------------------------------------------------------- M8: A3 sparse top bin at calibration and run time
def test_a3_sparse_top_bin_pools_with_15_30_and_is_used_for_high_sun_hours():
    """19 origin-days above 30° (as in the calibration geometry) and 40 in 15-30°, one cloud class.
    The >30° cell merges into 15-30°; its quantile is the pooled one; a 40° hour at run time uses it."""
    rows = []
    for o in range(40):
        fs = (pd.Timestamp("2024-01-01") + pd.Timedelta(days=o)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append({"forecast_start": fs, "daylight": True, "elevation_deg": 20.0, "cloud_frac": 0.5,
                     "clear_sky_ghi": 400.0, "actual_SW_IN": 300.0 - o})
        if o < 19:
            rows.append({"forecast_start": fs, "daylight": True, "elevation_deg": 35.0, "cloud_frac": 0.5,
                         "clear_sky_ghi": 600.0, "actual_SW_IN": 200.0 - 5 * o})
    rows = pd.DataFrame(rows)
    m = {k: (v["value"] if isinstance(v, dict) and "value" in v else v)
         for k, v in sf.load_real_cfg()["arm_c_method"].items() if not k.startswith("_")}
    m["min_origin_days_per_bin"] = 20
    # only the two upper elevation bins and one cloud class, so empty cells cannot trigger unrelated merges
    m.update(elevation_bin_edges_deg=[15.0, 30.0, 90.0], cloud_bin_edges_fraction=[0.0, 1.0],
             bin_boundary_rule={"elevation": "right_closed", "cloud": "right_closed"})
    qt = cal.quantile_table(rows, 1.0, m, lambda x: x)
    top = [t for t in qt["table"] if (t["elevation_bin"], t["cloud_bin"]) == (1, 0)][0]
    mid = [t for t in qt["table"] if (t["elevation_bin"], t["cloud_bin"]) == (0, 0)][0]
    assert top["pooled_group"] == [0, 0] and top["q_alpha"] == mid["q_alpha"] and top["n_hours"] == 59
    assert qt["merges"] == [{"from": [1, 0], "into": [0, 0], "origin_days_before_merge": 19}]
    # the pooled quantile differs from what the 19 high-sun origin-days alone would give
    alone = cal.alpha_quantile(rows[rows.elevation_deg > 30].eval("actual_SW_IN - 0.5 * clear_sky_ghi").to_numpy(), 0.10, "split_conformal_lower")
    assert alone != top["q_alpha"]
    lb = cal.lower_bound([500.0], [40.0], [0.5], [600.0], qt)
    assert lb == [max(0.0, min(500.0, 500.0 + top["q_alpha"]))]
