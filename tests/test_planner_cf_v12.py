"""
Focused tests for Planner-CF v1.2 (EXP-PLANNER-CF-CONSISTENCY-2025, Amendment A2 §17).

Synthetic instances only. No oracle, no campaign, no real data.
"""

import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import research_numerical_extractor_planner_cf_v1 as planner  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402
import oracle_runner as oracle  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402

FUEL_ROW = (5.0, 0.00025)


class _S:
    def __init__(self, p):
        self.point = list(p)


class _B:
    def __init__(self, S, W, D):
        self.timestamps = [f"2025-05-01T{h:02d}:00:00Z" for h in range(24)]
        self.solar_generation = _S(S)
        self.wind_generation = _S(W)
        self.demand = _S(D)
        self.demand_critical = None


def _cfg(D):
    cfg = oracle.canonical_configs()
    cfg["critical_demand_w"] = [min(11600.0, d) for d in D]
    return cfg


def _state(fuel, e0=100000.0):
    return StationState(timestamp="2025-04-30T23:00:00Z", battery_soc_pct=e0 / 2000.0, battery_energy_wh=e0,
                        diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
                        last_observed_demand=15000.0, last_observed_wind_generation=4500.0,
                        diesel_fuel_remaining_liters=fuel, operating_mode="NORMAL")


def _solve(S, W, D, fuel, e0=100000.0, fuel_inventory=True):
    opt = planner.PlannerCFV1Optimizer(fuel_inventory=fuel_inventory)
    plan = opt.optimize(_B(S, W, D), _state(fuel, e0), _cfg(D))
    return opt, plan


ZERO = [0.0] * 24
DIESEL16 = [16000.0] * 24          # 16 kW request, no renewables, battery at the SOC floor
NIGHT_S, NIGHT_W, NIGHT_D = [0.0] * 24, [4500.0] * 24, [12000.0] * 24   # v1.1 needs no diesel


# ---------------------------------------------------------------------------
# Fuel constraint (A2 §17.2)
# ---------------------------------------------------------------------------

def test_F1_insufficient_fuel_forces_zero_diesel_at_hour0():
    # 5 + 0.00025*16000 = 9.0 L is needed. Only 4.4193 L remain, so diesel must be off at hour 0.
    opt, plan = _solve(ZERO, ZERO, DIESEL16, fuel=4.4193, e0=40000.0)
    assert plan.constraint_status == "OPTIMAL"
    assert opt.last_planned[0]["diesel"] == pytest.approx(0.0, abs=1e-6)


def test_F2_v12_reproduces_v11_hour0_when_v11_fuel_fits():
    # Case 1: no diesel needed by v1.1 (fuel requirement 0 <= F_rem).
    opt12, _ = _solve(NIGHT_S, NIGHT_W, NIGHT_D, fuel=100.0)
    opt11, _ = _solve(NIGHT_S, NIGHT_W, NIGHT_D, fuel=100.0, fuel_inventory=False)
    h12, h11 = opt12.last_planned[0], opt11.last_planned[0]
    for k in ("served_c", "served_nc", "unmet_crit", "unmet_nc", "charge", "discharge", "diesel"):
        assert h12[k] == pytest.approx(h11[k], abs=1e-4), k
    assert opt12.last_objectives["J4"] == pytest.approx(opt11.last_objectives["J4"], abs=1e-4)
    # Case 2: v1.1 uses diesel at hour 0 and its requirement fits within F_rem = 100 L.
    opt12b, _ = _solve(ZERO, ZERO, DIESEL16, fuel=100.0, e0=40000.0)
    opt11b, _ = _solve(ZERO, ZERO, DIESEL16, fuel=100.0, e0=40000.0, fuel_inventory=False)
    assert opt11b.last_planned[0]["diesel"] > 0.0
    for k in ("served_c", "served_nc", "unmet_crit", "unmet_nc", "charge", "discharge", "diesel"):
        assert opt12b.last_planned[0][k] == pytest.approx(opt11b.last_planned[0][k], abs=1e-4), k


def test_F3_exact_fuel_boundary_constraint_is_tight():
    # F_rem = 9.0 L is exactly 5 + 0.00025 * 16000. v1.2 must allow 16 kW and make the row tight.
    opt, plan = _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    assert plan.constraint_status == "OPTIMAL"
    p0 = opt.last_planned[0]["diesel"]
    assert p0 == pytest.approx(16000.0, abs=1e-3)
    lhs = 5.0 * (1.0 if p0 > 1e-3 else 0.0) + 0.00025 * p0
    assert lhs == pytest.approx(9.0, abs=1e-6)


def test_F4_zero_fuel_remains_feasible_with_diesel_off():
    opt, plan = _solve(ZERO, ZERO, DIESEL16, fuel=0.0, e0=40000.0)
    assert plan.constraint_status == "OPTIMAL"
    assert opt.last_planned[0]["diesel"] == pytest.approx(0.0, abs=1e-6)


def test_F5_repeated_solves_are_deterministic():
    a, _ = _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    b, _ = _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    assert a.last_planned[0] == b.last_planned[0]
    assert a.last_objectives == b.last_objectives


def test_F6_exactly_one_fuel_row_is_added_and_only_at_hour0(monkeypatch):
    import highspy
    recorded = []

    class Spy(highspy.Highs):
        def addRow(self, lhs, rhs, n, idx, coef):
            recorded.append((float(lhs), float(rhs), list(idx), list(coef)))
            return super().addRow(lhs, rhs, n, idx, coef)

    monkeypatch.setattr(highspy, "Highs", Spy)
    _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    fuel_rows = [r for r in recorded if r[3] == [FUEL_ROW[0], FUEL_ROW[1]]]
    assert len(fuel_rows) == 1
    lhs, rhs, idx, coef = fuel_rows[0]
    assert lhs == -float("inf") and rhs == pytest.approx(9.0)
    assert idx == [planner.OFF_U_DIESEL, planner.OFF_P_DIESEL]  # hour 0 only (base index 0)


def test_F7_no_hidden_tie_break_or_new_objective():
    src = inspect.getsource(planner.PlannerCFV1Optimizer.optimize)
    assert src.count("h.addLinearObjective(obj)") == 1
    assert '("J1", c_j1), ("J_NC", c_jnc), ("J2", c_j2), ("J3", c_j3), ("J4", c_j4)' in src
    assert planner.PRIORITY == {"J1": 5, "J_NC": 4, "J2": 3, "J3": 2, "J4": 1}
    assert "J5" not in src and "tie" not in src.lower()


# ---------------------------------------------------------------------------
# G1 Class-B admission (A2 §17.3): positive case and each condition
# ---------------------------------------------------------------------------

O46_SOLAR = [35795.2, 35392.3, 33426.3, 30435.9, 26539.5, 13381.9, 2857.4, 2452.3, 2047.6, 1716.6, 1301.4, 1008.9,
             1167.2, 1624.9, 2557.4, 4531.3, 7520.8, 11543.9, 16189.1, 20987.4, 25426.9, 28758.9, 26242.9, 29599.5]
O46_WIND = [4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0,
            4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0]
O46_DEMAND = [12000.0, 12102.2, 12401.9, 12878.7, 13500.0, 14223.5, 15000.0, 15776.5, 16500.0, 17121.3, 17598.1,
              17897.8, 18000.0, 17897.8, 17598.1, 17121.3, 16500.0, 15776.5, 15000.0, 14223.5, 13500.0, 12878.7,
              12401.9, 12102.2]
O46_PCHG = [21119.9, 30290.1, 29854.5, 27057.3, 21869.7, 6158.4] + [0.0] * 11 + [2767.4, 5689.1, 8763.8, 12096.8,
            15880.2, 14010.9, 19497.3]
O46_PCURT = [7175.3] + [0.0] * 23
O46_DIS = [0.0] * 6 + [7642.6, 11324.1, 14282.5, 15404.8, 16126.9, 14888.9, 12332.8, 9272.8, 6210.6, 3090.0,
                       149.1] + [0.0] * 7


def _horizon(**kw):
    h = {"forecast_solar": list(O46_SOLAR), "forecast_wind": list(O46_WIND), "P_discharge": list(O46_DIS),
         "P_diesel": [0.0] * 24, "P_served": list(O46_DEMAND), "P_unmet": [0.0] * 24, "P_curt": list(O46_PCURT),
         "demand": list(O46_DEMAND)}
    h.update(kw)
    return h


def _tie_row(**kw):
    row = {"origin_id": 46, "step": 11,
           "P_charge_w": 21119.94, "R_charge_w": 28295.2, "P_curt_w": 7175.26,
           "P_discharge_w": 0.0, "R_discharge_w": 0.0, "P_diesel_w": 0.0, "R_diesel_w": 0.0,
           "P_served_w": 12000.0, "R_served_w": 12000.0, "P_unmet_w": 0.0, "R_unmet_w": 0.0,
           "P_solar_used_w": 28619.94, "P_wind_used_w": 4500.0,
           "solar_w": 35795.2, "wind_w": 4500.0, "forecast_solar_w": 35795.2, "forecast_wind_w": 4500.0,
           "demand_w": 12000.0, "E_before_wh": 64558.2, "fuel_before_l": 100.0,
           "horizon": _horizon()}
    row.update(kw)
    return row


def test_T1_positive_tie_admitted_with_all_seven_conditions_true():
    ev = gates.g1_v12_admission(_tie_row())
    assert all(ev["conditions"].values()), ev["conditions"]
    assert len(ev["conditions"]) == 7
    assert ev["admitted"] is True and ev["starvation_row"] is False


@pytest.mark.parametrize("name,change", [
    ("c1_served_unmet_equal", {"P_served_w": 12010.0}),
    ("c2_discharge_diesel_equal", {"R_discharge_w": 500.0}),
    ("c4_J4_tie_within_1Wh", {"horizon": _horizon(P_curt=[7175.26 + 5.0] + [0.0] * 23)}),
    ("c5_planned_identity_forecast_equals_realized", {"forecast_wind_w": 4000.0}),
    ("c6_realized_rule", {"R_charge_w": 20000.0}),
])
def test_T2_each_failed_condition_rejects_the_row(name, change):
    ev = gates.g1_v12_admission(_tie_row(**change))
    assert ev["admitted"] is False
    assert name in ev["failed_conditions"]


def test_T3_hour0_fuel_condition_rejects_row_with_insufficient_fuel():
    row = _tie_row(P_diesel_w=16000.0, R_diesel_w=16000.0, fuel_before_l=4.0, P_charge_w=2000.0,
                   R_charge_w=2000.0, P_curt_w=0.0, P_solar_used_w=0.0, R_served_w=18000.0, P_served_w=18000.0,
                   demand_w=18000.0, solar_w=0.0, wind_w=4500.0, forecast_wind_w=4500.0, forecast_solar_w=0.0,
                   E_before_wh=140000.0, horizon=_horizon(P_diesel=[16000.0] + [0.0] * 23, P_served=[18000.0] + list(O46_DEMAND[1:]), P_curt=[0.0] * 24))
    ev = gates.g1_v12_admission(row)
    assert "c7_hour0_fuel_feasible" in ev["failed_conditions"]
    assert ev["admitted"] is False


def test_T4_class_c_starvation_row_is_never_admitted():
    # Origin 97, step 23: remaining fuel 8.7123 L, plan 16,305.87 W, realized 14,849.2 W.
    row = _tie_row(P_diesel_w=16305.87, R_diesel_w=14849.2, fuel_before_l=8.7123,
                   P_charge_w=2806.23, R_charge_w=1349.56, P_curt_w=0.0, P_solar_used_w=0.36,
                   R_served_w=18000.0, P_served_w=18000.0, demand_w=18000.0, solar_w=0.36, wind_w=4500.0,
                   forecast_solar_w=0.36, forecast_wind_w=4500.0, E_before_wh=143672.18,
                   P_wind_used_w=4500.0, horizon=_horizon(P_diesel=[16305.87] + [0.0] * 23,
                                                          P_served=[18000.0] + list(O46_DEMAND[1:]),
                                                          P_curt=[0.0] * 24))
    ev = gates.g1_v12_admission(row)
    assert ev["starvation_row"] is True
    assert ev["admitted"] is False
    assert "c2_discharge_diesel_equal" in ev["failed_conditions"]


def test_T5_forecast_must_equal_realized_for_admission():
    ev = gates.g1_v12_admission(_tie_row(forecast_solar_w=35000.0))
    assert "c5_planned_identity_forecast_equals_realized" in ev["failed_conditions"]


def test_T6_g1_v12_passes_only_when_every_row_is_exact_or_admitted():
    exact = _tie_row(P_charge_w=28295.2, P_curt_w=0.0, P_solar_used_w=35795.2 + 4500.0 - 0.0,
                     horizon=_horizon(P_curt=[0.0] * 24))
    exact["P_solar_used_w"] = 35795.2
    exact["P_wind_used_w"] = 4500.0
    admitted = _tie_row()
    ok = gates.g1_v12([exact, admitted])
    assert ok["PASS"] is True and ok["exact"] == 1 and ok["admitted_ties"] == 1
    bad = gates.g1_v12([exact, _tie_row(R_charge_w=20000.0)])
    assert bad["PASS"] is False and len(bad["failures"]) == 1
    assert "c6_realized_rule" in bad["failures"][0]["failed_conditions"]


def test_T7_admission_evaluator_does_not_modify_planner_solution():
    before, _ = _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    gates.g1_v12([_tie_row()])
    after, _ = _solve(ZERO, ZERO, DIESEL16, fuel=9.0, e0=40000.0)
    assert before.last_planned[0] == after.last_planned[0]
