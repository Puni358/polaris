"""
Integration tests: ORACLE-PHYS audit path routed through the Amendment A2 (§17.3) G1 evaluator.
Synthetic records only. No oracle run, no campaign.
"""
import dataclasses
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import planner_cf_audit_gates as gates  # noqa: E402
import oracle_audit_adapter as oaa  # noqa: E402
import oracle_runner as oracle  # noqa: E402

O46_SOLAR = [35795.2, 35392.3, 33426.3, 30435.9, 26539.5, 13381.9, 2857.4, 2452.3, 2047.6, 1716.6, 1301.4, 1008.9,
             1167.2, 1624.9, 2557.4, 4531.3, 7520.8, 11543.9, 16189.1, 20987.4, 25426.9, 28758.9, 26242.9, 29599.5]
O46_WIND = [4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0,
            4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0]
O46_DEMAND = [12000.0, 12102.2, 12401.9, 12878.7, 13500.0, 14223.5, 15000.0, 15776.5, 16500.0, 17121.3, 17598.1,
              17897.8, 18000.0, 17897.8, 17598.1, 17121.3, 16500.0, 15776.5, 15000.0, 14223.5, 13500.0, 12878.7,
              12401.9, 12102.2]
O46_DIS = [0.0] * 6 + [7642.6, 11324.1, 14282.5, 15404.8, 16126.9, 14888.9, 12332.8, 9272.8, 6210.6, 3090.0,
                       149.1] + [0.0] * 7
O46_PCURT = [7175.3] + [0.0] * 23


def _horizon(**kw):
    h = {"forecast_solar": list(O46_SOLAR), "forecast_wind": list(O46_WIND), "P_discharge": list(O46_DIS),
         "P_diesel": [0.0] * 24, "P_served": list(O46_DEMAND), "P_unmet": [0.0] * 24, "P_curt": list(O46_PCURT)}
    h.update(kw)
    return h


def classb_row(**kw):
    """Known Class-B row: origin 46, step 11 (planned charge 21,119.94 W; realized 28,295.20 W)."""
    r = {"origin_id": 46, "step": 11,
         "P_charge_w": 21119.94, "R_charge_w": 28295.2, "P_curt_w": 7175.26,
         "P_discharge_w": 0.0, "R_discharge_w": 0.0, "P_diesel_w": 0.0, "R_diesel_w": 0.0,
         "P_served_w": 12000.0, "R_served_w": 12000.0, "P_unmet_w": 0.0, "R_unmet_w": 0.0,
         "P_solar_used_w": 28619.94, "P_wind_used_w": 4500.0,
         "solar_w": 35795.2, "wind_w": 4500.0, "forecast_solar_w": 35795.2, "forecast_wind_w": 4500.0,
         "demand_w": 12000.0, "E_before_wh": 64558.2, "fuel_before_l": 100.0, "horizon": _horizon()}
    r.update(kw)
    return r


def classc_row(**kw):
    """Known Class-C row: origin 97, step 23 (fuel starvation, remaining 8.7123 L)."""
    r = {"origin_id": 97, "step": 23,
         "P_charge_w": 2806.23, "R_charge_w": 1349.56, "P_curt_w": 0.0,
         "P_discharge_w": 0.0, "R_discharge_w": 0.0, "P_diesel_w": 16305.87, "R_diesel_w": 14849.2,
         "P_served_w": 18000.0, "R_served_w": 18000.0, "P_unmet_w": 0.0, "R_unmet_w": 0.0,
         "P_solar_used_w": 0.36, "P_wind_used_w": 4500.0,
         "solar_w": 0.36, "wind_w": 4500.0, "forecast_solar_w": 0.36, "forecast_wind_w": 4500.0,
         "demand_w": 18000.0, "E_before_wh": 143672.18, "fuel_before_l": 8.7123,
         "horizon": _horizon(P_diesel=[16305.87] + [0.0] * 23, P_served=[18000.0] + O46_DEMAND[1:],
                             P_curt=[0.0] * 24, P_discharge=[0.0] * 24)}
    r.update(kw)
    return r


def _pairs(rows, variant="ORACLE-PHYS", origin_index=46):
    res = oracle.OracleOriginResult(origin="2025-05-01", variant=variant)
    res.audit = list(rows)
    return [(origin_index, res)]


def _v12(rows):
    return oaa.g1_v12_for_oracle(_pairs(rows), expected_rows=len(rows))


# --- known rows ------------------------------------------------------------

def test_I1_known_classb_row_is_admitted_through_oracle_path():
    out = _v12([classb_row()])
    assert out["PASS"] is True and out["admitted_ties"] == 1 and out["exact"] == 0


def test_I2_known_classc_row_is_rejected_through_oracle_path():
    out = _v12([classc_row()])
    assert out["PASS"] is False and len(out["failures"]) == 1
    assert out["failures"][0]["starvation_row"] is True


def test_I3_ordinary_exact_row_passes():
    row = classb_row(P_charge_w=28295.2, P_curt_w=0.0, P_solar_used_w=35795.2, P_wind_used_w=4500.0,
                     horizon=_horizon(P_curt=[0.0] * 24))
    out = _v12([row])
    assert out["PASS"] is True and out["exact"] == 1


# --- each failed A2 condition -----------------------------------------------

@pytest.mark.parametrize("name,change", [
    ("c1_served_unmet_equal", {"P_served_w": 12010.0}),
    ("c2_discharge_diesel_equal", {"R_discharge_w": 500.0}),
    ("c4_J4_tie_within_1Wh", {"horizon": _horizon(P_curt=[7175.26 + 5.0] + [0.0] * 23)}),
    ("c5_planned_identity_forecast_equals_realized", {"forecast_wind_w": 4000.0}),
    ("c6_realized_rule", {"R_charge_w": 20000.0}),
])
def test_I4_each_failed_condition_fails_the_row(name, change):
    out = _v12([classb_row(**change)])
    assert out["PASS"] is False
    assert name in out["failures"][0]["failed_conditions"]


def test_I5_hour0_fuel_condition_fails_the_row():
    row = classb_row(P_diesel_w=16000.0, R_diesel_w=16000.0, fuel_before_l=4.0,
                     horizon=_horizon(P_diesel=[16000.0] + [0.0] * 23))
    out = _v12([row])
    assert out["PASS"] is False
    assert "c7_hour0_fuel_feasible" in out["failures"][0]["failed_conditions"]


# --- fail-closed behaviour ---------------------------------------------------

@pytest.mark.parametrize("missing", ["horizon", "E_before_wh", "fuel_before_l", "P_served_w"])
def test_I6_missing_required_field_fails_closed(missing):
    row = classb_row()
    row.pop(missing)
    out = _v12([row])
    assert out["PASS"] is False
    assert out["per_row"][0]["result"] == "FAIL"


def test_I7_missing_horizon_subfield_fails_closed():
    row = classb_row(horizon=_horizon())
    row["horizon"].pop("P_unmet")
    out = _v12([row])
    assert out["PASS"] is False


def test_I8_forecast_not_equal_realized_fails_closed():
    out = _v12([classb_row(forecast_solar_w=35000.0)])
    assert out["PASS"] is False
    assert "c5_planned_identity_forecast_equals_realized" in out["failures"][0]["failed_conditions"]


def test_I9_wrong_row_count_fails_closed():
    out = oaa.g1_v12_for_oracle(_pairs([classb_row()]), expected_rows=2952)
    assert out["row_count_ok"] is False and out["PASS"] is False


def test_I10_no_audit_records_fails_closed():
    res = oracle.OracleOriginResult(origin="x", variant="ORACLE-PHYS")
    out = oaa.g1_v12_for_oracle([(1, res)], expected_rows=2952)
    assert out["PASS"] is False


# --- determinism, exact path availability, no decision change ----------------

def test_I11_audit_result_is_deterministic():
    rows = [classb_row(), classc_row()]
    assert _v12(rows) == _v12(rows)


def test_I12_old_exact_g1_remains_available():
    res = oracle.OracleOriginResult(origin="x", variant="ORACLE-PHYS")
    res.hourly = [{"step": 0, "charge_w": 28295.2}]
    res.executed = [{"origin_id": 46, "arm": "ORACLE-PHYS", "step": 0, "plan_hour": 0, "planned_charge_w": 21119.94}]
    exact = oaa.g1_for_oracle([(46, res)], "ORACLE-PHYS")
    assert exact["PASS"] is False  # exact G1 still fails a mismatch
    rl = [{"origin_id": 1, "hour": 0, "battery_charge": 500.0}]
    ex = [{"origin_id": 1, "step": 0, "planned_charge_w": 500.0}]
    assert gates.g1_realizability(__import__("pandas").DataFrame(rl), __import__("pandas").DataFrame(ex))["PASS"] is True


def test_I13_evaluator_is_audit_only_and_does_not_mutate_inputs():
    row = classb_row()
    snapshot = repr(row)
    gates.g1_v12([row])
    assert repr(row) == snapshot


# --- data path: oracle record construction and result schema -----------------

class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_I14_audit_row_contains_every_required_field_from_oracle_objects():
    bundle = _Obj(solar_generation=_Obj(point=O46_SOLAR), wind_generation=_Obj(point=O46_WIND))
    plan = _Obj(battery_discharge=O46_DIS, diesel_power=[0.0] * 24, load_served=O46_DEMAND,
                unmet_load=[0.0] * 24, renewable_curtailment=O46_PCURT,
                solar_used=[28619.94] + [0.0] * 23, wind_used=[4500.0] + [0.0] * 23)
    optimizer = _Obj(last_planned=[{"charge": 21119.94}])
    state = _Obj(battery_energy_wh=64558.2, diesel_fuel_remaining_liters=100.0)
    res = _Obj(battery_charge_realized_w=28295.2, battery_discharge_realized_w=0.0, diesel_realized_w=0.0,
               served_load_w=12000.0, unmet_load_w=0.0, solar_realized_w=35795.2, wind_realized_w=4500.0,
               demand_realized_w=12000.0)
    row = oracle.audit_row(46, 11, bundle, plan, optimizer, state, res)
    assert gates.v12_missing_fields(row) == []
    out = gates.g1_v12([row])
    assert out["PASS"] is True and out["admitted_ties"] == 1


def test_I15_v11_result_schema_is_preserved_and_audit_field_is_additive():
    names = [f.name for f in dataclasses.fields(oracle.OracleOriginResult)]
    for legacy in ("origin", "variant", "hourly", "planned", "executed", "route_by_step", "optimizer_status"):
        assert legacy in names
    assert "audit" in names and names.index("audit") >= names.index("executed")
