"""
Synthetic tests for the global lower-bound infrastructure (EXP-PLANNER-CF-CONSISTENCY-2025, Study 1).
No real data is read. Loader tests use fixtures written to a temporary directory with the same schema.
"""

import copy
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.optimize import linprog

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(REPO))

import global_lower_bound as g  # noqa: E402
import global_lower_bound_loader as L  # noqa: E402
import global_lower_bound_manifest as M  # noqa: E402
import oracle_runner as oracle  # noqa: E402


# ---------------------------------------------------------------------------
# Synthetic weather/SITES fixture (123 daily origins, 24 hours each, same schema)
# ---------------------------------------------------------------------------

def make_fixture(tmp: Path, n_origins=123, sw=300.0, drop_row=None, nan_row=None, bad_sw_row=None,
                 bad_ts_row=None, bad_horizon_row=None, extra_out_of_window=False):
    starts = pd.date_range("2025-05-01", periods=n_origins, freq="D")
    w_rows, s_rows = [], []
    for fs in starts:
        for t in range(24):
            ts = fs + pd.Timedelta(hours=t)
            w_rows.append({"forecast_start": fs.strftime("%Y-%m-%d %H:%M:%S"), "horizon_hour": t + 1,
                           "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "actual_SW_IN": sw,
                           "fc_cloud_cover": 20.0})
            s_rows.append({"TIMESTAMP": ts.strftime("%Y-%m-%d %H:%M:%S"), "SW_IN": sw})
    if extra_out_of_window:
        fs = pd.Timestamp("2025-09-01")
        for t in range(24):
            ts = fs + pd.Timedelta(hours=t)
            w_rows.append({"forecast_start": fs.strftime("%Y-%m-%d %H:%M:%S"), "horizon_hour": t + 1,
                           "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"), "actual_SW_IN": sw,
                           "fc_cloud_cover": 20.0})
    if drop_row is not None:
        del w_rows[drop_row]
    if nan_row is not None:
        w_rows[nan_row]["actual_SW_IN"] = np.nan
    if bad_sw_row is not None:
        w_rows[bad_sw_row]["actual_SW_IN"] = sw + 5.0
    if bad_ts_row is not None:
        w_rows[bad_ts_row]["timestamp"] = "2030-01-01 00:00:00"
    if bad_horizon_row is not None:
        w_rows[bad_horizon_row]["horizon_hour"] = w_rows[bad_horizon_row]["horizon_hour"] + 24
    wp = tmp / "weather.csv"
    sp = tmp / "sites.csv"
    pd.DataFrame(w_rows).to_csv(wp, index=False)
    pd.DataFrame(s_rows).to_csv(sp, index=False)
    return wp, sp


def test_L01_valid_fixture_yields_123_origins_of_24_hours(tmp_path):
    wp, sp = make_fixture(tmp_path)
    recs = L.load_population(wp, sp)
    assert len(recs) == 123
    assert all(len(r.solar_w) == 24 and len(r.wind_w) == 24 and len(r.demand_w) == 24 for r in recs)
    assert [r.origin_index for r in recs] == list(range(1, 124))
    assert recs[0].forecast_start == "2025-05-01 00:00:00"
    assert recs[-1].forecast_start == "2025-08-31 00:00:00"


def test_L02_derivations_match_oracle_formulas(tmp_path):
    wp, sp = make_fixture(tmp_path, sw=400.0)
    r = L.load_population(wp, sp)[0]
    for t in range(24):
        assert r.solar_w[t] == pytest.approx(oracle.pv_from_sw_in(400.0))
        assert r.wind_w[t] == pytest.approx(oracle.wind_w(t))
        assert r.demand_w[t] == pytest.approx(oracle.demand_w(t))
        assert r.critical_w[t] == pytest.approx(min(11600.0, r.demand_w[t]))
        assert r.noncritical_w[t] == pytest.approx(r.demand_w[t] - r.critical_w[t])
    assert r.initial_state == {"E0_wh": 100000.0, "soc_pct": 50.0, "diesel_on": False, "fuel_l": 100.0}


def test_L03_out_of_window_origin_is_ignored(tmp_path):
    wp, sp = make_fixture(tmp_path, extra_out_of_window=True)
    assert len(L.load_population(wp, sp)) == 123


def test_L04_wrong_population_count_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, n_origins=122)
    with pytest.raises(L.LoaderError, match="population count"):
        L.load_population(wp, sp)


def test_L05_missing_hour_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, drop_row=5)
    with pytest.raises(L.LoaderError):
        L.load_population(wp, sp)


def test_L06_nan_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, nan_row=10)
    with pytest.raises(L.LoaderError, match="NaN"):
        L.load_population(wp, sp)


def test_L07_wrong_horizon_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, bad_horizon_row=3)
    with pytest.raises(L.LoaderError):
        L.load_population(wp, sp)


def test_L08_sw_in_mismatch_against_sites_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, bad_sw_row=7)
    with pytest.raises(L.LoaderError, match="SW_IN mismatch"):
        L.load_population(wp, sp)


def test_L09_timestamp_misalignment_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path, bad_ts_row=9)
    with pytest.raises(L.LoaderError):
        L.load_population(wp, sp)


def test_L10_duplicate_origin_hour_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path)
    df = pd.read_csv(wp)
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    df.to_csv(wp, index=False)
    with pytest.raises(L.LoaderError):
        L.load_population(wp, sp)


def test_L11_hash_pin_mismatch_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path)
    with pytest.raises(L.LoaderError, match="hash mismatch"):
        L.load_population(wp, sp, expected_weather_sha256="0" * 64)


def test_L12_missing_column_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path)
    df = pd.read_csv(wp).drop(columns=["actual_SW_IN"])
    df.to_csv(wp, index=False)
    with pytest.raises(L.LoaderError, match="missing columns"):
        L.load_population(wp, sp)


def test_L13_wind_and_demand_formulas_equal_oracle_for_all_hours():
    for t in range(24):
        assert L.wind_w(t) == oracle.wind_w(t)
        assert L.demand_w(t) == oracle.demand_w(t)


def test_L14_pv_conversion_equals_oracle_and_caps_at_60kw():
    for sw in (0.0, 100.0, 800.0, 2000.0):
        assert L.pv_from_sw_in(sw) == oracle.pv_from_sw_in(sw)
    assert L.pv_from_sw_in(1e6) == 60000.0


def test_L15_zero_based_horizon_fails_closed(tmp_path):
    wp, sp = make_fixture(tmp_path)
    df = pd.read_csv(wp)
    df["horizon_hour"] = df["horizon_hour"] - 1  # shift 1..24 to 0..23
    df.to_csv(wp, index=False)
    with pytest.raises(L.LoaderError, match="canonical horizon_hour must be 1..24"):
        L.load_population(wp, sp)


def test_L16_origin_record_payload_excludes_horizon_hour(tmp_path):
    wp, sp = make_fixture(tmp_path)
    recs = L.load_population(wp, sp)
    rec = recs[0]
    assert not hasattr(rec, "horizon_hour")
    schema_row = M.input_schema(recs)[0]
    assert "horizon_hour" not in schema_row


# ---------------------------------------------------------------------------
# Dual validity, governance separation, and status classification (synthetic)
# ---------------------------------------------------------------------------

def brute_lp(D, e0):
    act = [t for t in range(len(D)) if D[t] > 0.0]
    n = len(act)
    emin = g.E_MIN_WH - g.SOC_MARGIN_WH
    emax = g.E_MAX_WH + g.SOC_MARGIN_WH
    best = np.inf
    for ys in itertools.product([0, 1], repeat=n):
        for modes in itertools.product([0, 1, 2], repeat=n):
            nv = 3 * n
            c = np.zeros(nv)
            fixed = 0.0
            bounds = []
            for k, t in enumerate(act):
                dmax = min(g.DIESEL_MAX_W, D[t] + g.BATTERY_POWER_W) if ys[k] else 0.0
                bounds += [(0.0, dmax), (0.0, g.BATTERY_POWER_W if modes[k] == 1 else 0.0),
                           (0.0, g.BATTERY_POWER_W if modes[k] == 2 else 0.0)]
                c[3 * k] = g.MARGINAL_FUEL_L_PER_WH
                fixed += g.BASE_FUEL_L_PER_H * ys[k]
            A_eq = np.zeros((n, nv))
            b_eq = np.zeros(n)
            for k, t in enumerate(act):
                A_eq[k, 3 * k], A_eq[k, 3 * k + 1], A_eq[k, 3 * k + 2] = 1.0, -1.0, 1.0
                b_eq[k] = D[t]
            A_ub, b_ub = [], []
            for j in range(1, n + 1):
                row = np.zeros(nv)
                for i in range(j):
                    row[3 * i + 1] = g.ETA_CHG
                    row[3 * i + 2] = -1.0 / g.ETA_DIS
                A_ub += [row, -row]
                b_ub += [emax - e0, e0 - emin]
            res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method="highs")
            if res.status == 0:
                best = min(best, res.fun + fixed)
    return best


TINY_D = [30000.0] * 3 + [0.0] * 21
TINY_E0 = 100000.0


def test_V01_tight_solve_dual_below_and_primal_above_true_optimum():
    opt = brute_lp(TINY_D, TINY_E0)
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    r = g.solve_origin(i)
    c = g.certify_origin(r, i)
    assert c["L_o"] <= opt + 1e-6
    assert c["U_o"] >= opt - 1e-6
    assert c["status_code"] == g.CERTIFIED_TIGHT


def test_V02_dual_remains_valid_when_gap_exceeds_limit_and_primal_is_not_substituted():
    opt = brute_lp(TINY_D, TINY_E0)
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    r = g.solve_origin(i, mip_rel_gap=0.5)  # deterministic loose stop, gap > 0.01 L
    c = g.certify_origin(r, i)
    gap = c["U_o"] - c["L_o"]
    assert gap > g.GAP_LIMIT_L
    assert c["L_o"] <= opt + 1e-6, "dual must remain a valid lower bound above the gap limit"
    assert c["U_o"] >= opt - 1e-6
    assert c["L_o"] != c["U_o"], "primal objective must never be substituted for the dual"
    assert c["status_code"] == g.LOWER_BOUND_AVAILABLE
    assert c["certification"] == "BLOCKED"


def test_V03_no_incumbent_gives_blocked_no_feasible_incumbent_and_no_lower_bound():
    D = one_hour_fixture(200000.0)  # infeasible: 200 kW exceeds diesel + battery
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, D, 100000.0)
    r = g.solve_origin(i)
    c = g.certify_origin(r, i)
    assert c["status_code"] == g.BLOCKED_NO_FEASIBLE_INCUMBENT
    assert c["U_o"] is None and c["L_o"] is None


def one_hour_fixture(v):
    return [v] + [0.0] * 23


def test_V04_no_dual_with_incumbent_is_blocked_no_dual_and_never_uses_primal():
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    r = dict(g.solve_origin(i))
    r["dual"] = None
    c = g.certify_origin(r, i)
    assert c["status_code"] == g.BLOCKED_NO_DUAL
    assert c["L_o"] is None
    assert c["U_o"] is not None


def test_V05_classification_path_for_valid_dual_without_incumbent():
    # Classification test only. HiGHS did not expose a finite dual without an incumbent in the
    # tested time-limit case (raw mip_dual_bound = -inf), so the solver is not retaining such duals.
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    synthetic = {"status": "synthetic", "x": None, "primal": None, "dual": 5.0, "has_terminal_row": False}
    c = g.certify_origin(synthetic, i)
    assert c["status_code"] == g.LOWER_BOUND_AVAILABLE
    assert c["L_o"] == 5.0 and c["U_o"] is None
    assert c["certification"] == "BLOCKED"


def test_V06_dual_above_primal_is_rejected():
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    r = dict(g.solve_origin(i))
    r["dual"] = r["primal"] + 1.0
    c = g.certify_origin(r, i)
    assert c["L_o"] is None and c["status_code"] == g.BLOCKED_NO_DUAL


def test_V07_aggregate_separates_valid_bounds_tight_and_blocked():
    i = g.OriginInputs(1, [0.0] * 24, [0.0] * 24, TINY_D, TINY_E0)
    tight = g.certify_origin(g.solve_origin(i), i)
    loose = g.certify_origin(dict(g.solve_origin(i, mip_rel_gap=0.5)), i)
    nodual = g.certify_origin(dict(g.solve_origin(i), dual=None), i)
    agg = g.aggregate_certificate([tight, loose, nodual])
    assert agg["count_valid_dual"] == 2
    assert agg["count_meeting_gap_limit"] == 1
    assert agg["count_blocked_no_dual"] == 1
    assert agg["sum_L_valid"] == pytest.approx(tight["L_o"] + loose["L_o"])
    assert agg["sum_L_tight"] == pytest.approx(tight["L_o"])
    assert agg["recommended_conservative_L_not_adopted"] == pytest.approx(agg["sum_L_valid"])
    assert agg["ng7"].startswith("NOT_EVALUATED")


# ---------------------------------------------------------------------------
# SOC clamp: the executor's own limits keep the unclamped energy inside bounds (synthetic states)
# ---------------------------------------------------------------------------

def test_S01_unclamped_soc_stays_within_physical_bounds_for_executor_limits():
    from system.schemas.station_state import StationState
    from system.schemas.dispatch_plan import DispatchPlan
    from system.simulation.research_realization_executor import ResearchRealizationExecutor

    cfg = oracle.canonical_configs()
    ex = ResearchRealizationExecutor(cfg)
    rng = np.random.default_rng(12345)
    # Wh: executor rounds the stored energy and flows to 2 dp; worst case ~0.005 Wh each, combined < 0.02 Wh
    tol = 0.02
    lo, hi = ex.min_e_wh, ex.max_e_wh
    checked = 0
    for _ in range(60):
        e0 = float(rng.uniform(lo, hi))
        state = StationState(timestamp="2025-05-01T00:00:00Z", battery_soc_pct=e0 / ex.capacity_wh * 100,
                             battery_energy_wh=e0, diesel_running=False, diesel_hours_running=0.0,
                             last_observed_solar_irradiance=0.0, last_observed_demand=15000.0,
                             last_observed_wind_generation=4500.0, diesel_fuel_remaining_liters=100.0,
                             operating_mode="NORMAL")
        solar = float(rng.uniform(0, 60000))
        wind = float(rng.uniform(0, 9000))
        demand = float(rng.uniform(10000, 18000))
        p_chg = float(rng.uniform(0, 50000)) if rng.uniform() < 0.5 else 0.0
        p_dis = 0.0 if p_chg > 0 else float(rng.uniform(0, 50000))
        plan = DispatchPlan(
            schema_version="1.0.0", timestamps=[f"2025-05-01T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0] * 24, wind_used=[0.0] * 24, battery_charge=[p_chg] * 24,
            battery_discharge=[p_dis] * 24, battery_soc=[0.0] * 24, diesel_power=[0.0] * 24,
            load_served=[0.0] * 24, flexible_load_schedule=[0.0] * 24, renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24, objective_value=0.0, constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24)
        realized = {"timestamp": "2025-05-01T00:00:00Z", "actual_SW_IN": 0.0,
                    "actual_wind_generation": wind, "actual_demand": demand}
        try:
            res = ex.execute_step(state, plan, realized, step_index=0)
        except Exception:
            continue
        chg, dis = res.battery_charge_realized_w, res.battery_discharge_realized_w
        e_unclamped = e0 + ex.eta_chg * chg - dis / ex.eta_dis
        assert lo - tol <= e_unclamped <= hi + tol, "unclamped SOC left physical bounds"
        assert abs(res.next_state.battery_energy_wh - min(hi, max(lo, e_unclamped))) <= tol
        checked += 1
    assert checked >= 20


# ---------------------------------------------------------------------------
# Manifests (in-memory only)
# ---------------------------------------------------------------------------

def test_M01_population_manifest_requires_123_origins(tmp_path):
    wp, sp = make_fixture(tmp_path)
    recs = L.load_population(wp, sp)
    m = M.population_manifest(recs)
    assert m["n_origins"] == 123 and m["hours_per_origin"] == 24
    with pytest.raises(ValueError):
        M.population_manifest(recs[:122])


def test_M02_input_hash_deterministic_and_sensitive(tmp_path):
    wp, sp = make_fixture(tmp_path)
    recs = L.load_population(wp, sp)
    h1 = M.input_hash(recs)
    assert h1 == M.input_hash(recs)
    changed = copy.deepcopy(recs)
    changed[0].solar_w[0] += 1.0
    assert M.input_hash(changed) != h1


def test_M03_configuration_and_solver_hashes_are_stable():
    assert M.configuration_hash() == g.config_hash()
    assert M.solver_settings_hash() == M.solver_settings_hash()
    assert M.SOLVER_SETTINGS["threads"] == 1
    assert M.SOLVER_SETTINGS["time_limit_s"] == 60.0  # K7


def test_M04_build_manifest_is_in_memory_and_unfrozen(tmp_path):
    wp, sp = make_fixture(tmp_path)
    recs = L.load_population(wp, sp)
    man = M.build_manifest(recs, {"global_lower_bound.py": "x"})
    assert man["frozen"] is False
    assert man["population"]["n_origins"] == 123
    assert not any(p.name.endswith(".json") for p in tmp_path.iterdir())
