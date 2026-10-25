"""
Unit / static / invariant tests for Planner-CF v1 (EXP-PLANNER-CF-CONSISTENCY-2025).

These tests verify the implementation only. They do NOT evaluate any origin, run any
campaign, or produce any outcome.
"""

import hashlib
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
import planned_telemetry_harness as harness  # noqa: E402
import oracle_runner as oracle  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402
from system.schemas.dispatch_plan import DispatchPlan  # noqa: E402

GAP19_SHA = "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737"
DISPATCH_SHA = "21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b"
EXTRACTOR_SHA = "95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e"
SOLAR_SHA = "d457facdbeb57b9c582b623c524c0f50717306ca083ab93028f1bd700d1e7a2e"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class _Series:
    def __init__(self, point):
        self.point = list(point)


class _Bundle:
    def __init__(self, solar, wind, demand, critical):
        self.timestamps = [f"2025-05-01T{h:02d}:00:00Z" for h in range(24)]
        self.solar_generation = _Series(solar)
        self.wind_generation = _Series(wind)
        self.demand = _Series(demand)
        self.demand_critical = None
        self._critical = list(critical)


def _config(critical):
    cfg = oracle.canonical_configs()
    cfg["critical_demand_w"] = list(critical)
    return cfg


def _state(mode="NORMAL"):
    return StationState(
        timestamp="2025-04-30T23:00:00Z", battery_soc_pct=50.0, battery_energy_wh=100000.0,
        diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0, last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0, operating_mode=mode,
    )


def _synthetic():
    # Night-like: no solar; wind 4.5 kW; demand 12 kW of which 11.6 kW is critical.
    solar = [0.0] * 24
    wind = [4500.0] * 24
    demand = [12000.0] * 24
    critical = [min(11600.0, d) for d in demand]
    return _Bundle(solar, wind, demand, critical), critical


# ---------------------------------------------------------------------------
# C1–C4: static layout, priorities, flex, EMERGENCY reference
# ---------------------------------------------------------------------------

def test_layout_is_408_columns_and_has_no_flex_column():
    assert planner.NUM_VARS == 408
    offsets = [planner.OFF_P_SOL_USED, planner.OFF_P_WIND_USED, planner.OFF_CURT_SOL, planner.OFF_CURT_WIND,
               planner.OFF_P_CHG, planner.OFF_P_DIS, planner.OFF_E_NEXT, planner.OFF_P_DIESEL,
               planner.OFF_SERVED_C, planner.OFF_SERVED_NC, planner.OFF_UNMET_NC,
               planner.OFF_U_CHG, planner.OFF_U_DIS, planner.OFF_U_DIESEL, planner.OFF_V_START]
    assert len(set(offsets)) == 15 and max(offsets) == 14
    src = inspect.getsource(planner)
    assert "OFF_FLEX" not in src and "OFF_P_FLEX" not in src and "p_flx =" not in src


def test_flex_is_fixed_zero_and_not_a_variable():
    assert planner.FLEX_FIXED_W == 0.0


def test_priority_order_is_J1_gt_Jnc_gt_J2_gt_J3_gt_J4():
    p = planner.PRIORITY
    assert p["J1"] > p["J_NC"] > p["J2"] > p["J3"] > p["J4"]
    assert (p["J1"], p["J_NC"], p["J2"], p["J3"], p["J4"]) == (5, 4, 3, 2, 1)


def test_objectives_are_assigned_in_declared_priority_order():
    src = inspect.getsource(planner.PlannerCFV1Optimizer.optimize)
    i1 = src.index('("J1", c_j1)')
    i2 = src.index('("J_NC", c_jnc)')
    i3 = src.index('("J2", c_j2)')
    i4 = src.index('("J3", c_j3)')
    i5 = src.index('("J4", c_j4)')
    assert i1 < i2 < i3 < i4 < i5
    assert "obj.priority = PRIORITY[name]" in src


def test_emergency_row_uses_total_served_C4():
    src = inspect.getsource(planner.PlannerCFV1Optimizer.optimize)
    assert "[base + OFF_P_DIS, base + OFF_SERVED_C, base + OFF_SERVED_NC]" in src
    assert "[1.0, -1.0, -1.0]" in src


# ---------------------------------------------------------------------------
# Model invariants on a synthetic instance (unit level; no origin, no outcome)
# ---------------------------------------------------------------------------

def _rows_recorded(monkeypatch, optimizer, bundle, cfg, state):
    import highspy
    recorded = []

    class Spy(highspy.Highs):
        def addRow(self, lhs, rhs, n, idx, coef):
            recorded.append((float(lhs), float(rhs), list(idx), list(coef)))
            return super().addRow(lhs, rhs, n, idx, coef)

    monkeypatch.setattr(highspy, "Highs", Spy)
    plan = optimizer.optimize(bundle, state, cfg)
    return plan, recorded


def test_normal_reserve_row_count_312(monkeypatch):
    b, crit = _synthetic()
    plan, rows = _rows_recorded(monkeypatch, planner.PlannerCFV1Optimizer(), b, _config(crit), _state("NORMAL"))
    assert plan.constraint_status == "OPTIMAL"
    # v1.2 (A2 §17.2): one hour-0 fuel row is added. v1.1 (fuel_inventory=False) keeps 312 rows.
    assert len(rows) == 11 * 24 + 24 + 24 + 1
    assert planner.PlannerCFV1Optimizer().reserve_enabled is True


def test_emergency_adds_24_rows_and_reference_is_total_served(monkeypatch):
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    plan, rows = _rows_recorded(monkeypatch, opt, b, _config(crit), _state("EMERGENCY"))
    assert plan.constraint_status == "OPTIMAL"
    assert opt.last_em_rows_built == 24
    assert len(rows) == 11 * 24 + 24 + 24 + 24 + 1  # v1.2 hour-0 fuel row included
    em = [r for r in rows if len(r[2]) == 3 and r[1] == 0.0 and r[0] == -np.inf]
    assert len(em) == 24
    for lhs, rhs, idx, coef in em:
        assert coef == [1.0, -1.0, -1.0]
        dis, sc, snc = idx
        assert (sc - dis) % 15 == 3 and (snc - dis) % 15 == 4  # served_c, served_nc of same hour


def test_reserve_disabled_removes_layer_C(monkeypatch):
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer(reserve_enabled=False)
    plan, rows = _rows_recorded(monkeypatch, opt, b, _config(crit), _state("NORMAL"))
    assert plan.constraint_status == "OPTIMAL"
    assert len(rows) == 11 * 24 + 24 + 1  # no Layer C rows; v1.2 hour-0 fuel row included
    assert all(v == 0.0 for v in [opt.last_objectives["J2"]])


def test_customer_first_serves_noncritical_when_supply_allows():
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    plan = opt.optimize(b, _state("NORMAL"), _config(crit))
    assert plan.constraint_status == "OPTIMAL"
    for row in opt.last_planned:
        assert row["unmet_nc"] <= 1e-3, f"hour {row['t']}: non-critical shed while servable"


def test_planned_identities_hold():
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    opt.optimize(b, _state("NORMAL"), _config(crit))
    msgs = harness.check_planned_identities(opt.last_planned, b.demand.point, crit,
                                            b.solar_generation.point, b.wind_generation.point)
    assert msgs == []


def test_g2_no_planned_charge_with_nc_unmet_on_synthetic():
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    opt.optimize(b, _state("NORMAL"), _config(crit))
    for row in opt.last_planned:
        assert not (row["unmet_nc"] > 1e-3 and row["charge"] > 1e-3), f"hour {row['t']}: G2 inversion"


def test_bus_balance_on_returned_plan():
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    plan = opt.optimize(b, _state("NORMAL"), _config(crit))
    for t in range(24):
        lhs = plan.solar_used[t] + plan.wind_used[t] + plan.battery_discharge[t] + plan.diesel_power[t]
        rhs = plan.load_served[t] + plan.battery_charge[t] + plan.flexible_load_schedule[t]
        assert abs(lhs - rhs) < 1e-2, f"hour {t}: bus balance {lhs} vs {rhs}"
        assert plan.flexible_load_schedule[t] == 0.0


def test_emergency_plan_discharge_not_above_total_served():
    b, crit = _synthetic()
    opt = planner.PlannerCFV1Optimizer()
    plan = opt.optimize(b, _state("EMERGENCY"), _config(crit))
    assert plan.constraint_status == "OPTIMAL"
    for t in range(24):
        assert plan.battery_discharge[t] <= plan.load_served[t] + 1e-3


# ---------------------------------------------------------------------------
# Harness-only telemetry; production DispatchPlan untouched
# ---------------------------------------------------------------------------

def test_dispatch_plan_signature_unchanged():
    params = list(inspect.signature(DispatchPlan.__init__).parameters)
    assert "served_c" not in params and "planned" not in params
    assert _sha(REPO / "system/schemas/dispatch_plan.py") == DISPATCH_SHA


def test_planned_telemetry_wrapper_collects_24_records(monkeypatch):
    b, crit = _synthetic()
    h = harness.PlannedTelemetryHarness(planner.PlannerCFV1Optimizer())
    h.optimize(b, _state("NORMAL"), _config(crit), origin_id=7, arm="PC-Control", step=0)
    recs = h.as_dicts()
    assert len(recs) == 24
    assert all(set(harness.PLANNED_FIELDS) <= set(r) for r in recs)
    assert {r["origin_id"] for r in recs} == {7}


# ---------------------------------------------------------------------------
# Oracle inputs: definitions, calendar, coverage (no oracle run)
# ---------------------------------------------------------------------------

def test_oracle_solar_source_hash_pinned():
    assert oracle.verify_solar_source() == SOLAR_SHA


def test_oracle_population_is_123_origins_in_window():
    origins = oracle.origins_2025_may_aug()
    assert len(origins) == 123
    assert origins[0] == pd.Timestamp("2025-05-01")
    assert origins[-1] == pd.Timestamp("2025-08-31")


def test_wind_and_demand_formulas_reproduce_recorded_realized_values():
    tel = pd.read_csv(REPO / "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv")
    rows = tel[(tel.origin_id == 1) & (tel.arm == "Control_Frozen_B")].sort_values("hour")
    for k, r in enumerate(rows.itertuples()):
        assert oracle.wind_w(k) == pytest.approx(r.actual_wind, abs=1e-6)
        assert oracle.demand_w(k) == pytest.approx(r.actual_demand, abs=1e-6)


def test_solar_conversion_reproduces_recorded_realized_solar_for_origin_1():
    tel = pd.read_csv(REPO / "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv")
    rows = tel[(tel.origin_id == 1) & (tel.arm == "Control_Frozen_B")].sort_values("hour")
    lookup = oracle.load_sw_in_lookup()
    origin = pd.Timestamp("2025-05-01")
    for k, r in enumerate(rows.itertuples()):
        assert oracle.solar_w(lookup, origin, k) == pytest.approx(r.actual_solar, abs=0.01)


def test_calendar_horizon_offsets_and_timestamps():
    lookup = oracle.load_sw_in_lookup()
    origin = pd.Timestamp("2025-05-01")
    bundle = oracle.build_horizon(origin, 23, lookup)
    assert bundle.timestamps[0] == "2025-05-01T23:00:00Z"
    assert bundle.timestamps[-1] == "2025-05-02T22:00:00Z"
    assert bundle.wind_generation.point[0] == oracle.wind_w(23)
    assert bundle.demand.point[-1] == oracle.demand_w(46)


def test_coverage_g12_last_origin_window_available():
    lookup = oracle.load_sw_in_lookup()
    last = pd.Timestamp("2025-08-31")
    for step in range(24):
        oracle.solar_w(lookup, last, step + 23)  # highest offset used by re-solve at step 23
    assert "2025-09-01 22:00:00" in lookup


def test_oracle_rejects_unknown_variant():
    with pytest.raises(ValueError):
        oracle.run_oracle_origin(pd.Timestamp("2025-05-01"), "ORACLE-BOGUS", 0)


# ---------------------------------------------------------------------------
# Production / frozen protection
# ---------------------------------------------------------------------------

def test_production_and_frozen_hashes_unchanged():
    assert _sha(REPO / "system/optimization/implementations/gap19_highs_native.py") == GAP19_SHA
    assert _sha(REPO / "experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py") == EXTRACTOR_SHA


def test_v11_reproduction_flag_restores_312_rows(monkeypatch):
    # fuel_inventory=False is the v1.1 formulation. It reproduces the v1.1 row count exactly.
    b, crit = _synthetic()
    plan, rows = _rows_recorded(monkeypatch, planner.PlannerCFV1Optimizer(fuel_inventory=False), b,
                                _config(crit), _state("NORMAL"))
    assert plan.constraint_status == "OPTIMAL"
    assert len(rows) == 11 * 24 + 24 + 24
