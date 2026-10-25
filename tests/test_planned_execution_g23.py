"""
Focused tests for executed-hour planned telemetry and the G2/G3 evaluator
(EXP-PLANNER-CF-CONSISTENCY-2025, §7). Synthetic instances only; no origin, oracle or campaign run.
"""

import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import planned_execution_telemetry as pet  # noqa: E402
import oracle_runner as oracle  # noqa: E402
import research_numerical_extractor_planner_cf_v1 as planner  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402

E_MIN = 40000.0
ETA_DIS = 0.92


def _rows(base):
    """24 lookahead rows; row t has values distinct from row 0 so collapse errors are visible."""
    return [{
        "t": t, "served_c": base + 1000.0 * t, "served_nc": 2000.0 + t, "unmet_crit": 3000.0 + t,
        "unmet_nc": 4000.0 + t, "charge": 5000.0 + t, "discharge": 0.0, "diesel": 6000.0 + t,
        "E_next": 9e9, "s_j2": 0.0, "u_diesel": 0.0, "v_start": 0.0,
        "residue_corrected": False, "zeroed_magnitude_w": 0.0,
    } for t in range(24)]


def _record(rec, origin, step, rows, e_start=100000.0, pv=0.0, wind=4500.0, dc=11600.0):
    return rec.record_resolve(origin_id=origin, arm="PC-Control", step=step, planned_rows=rows,
                              e_start_wh=e_start, pv_real_w=pv, wind_real_w=wind, d_c_real_w=dc,
                              e_min_wh=E_MIN, eta_dis=ETA_DIS)


# ---------------------------------------------------------------------------
# 24 lookahead rows collapse to exactly 1 executed-hour record per re-solve
# ---------------------------------------------------------------------------

def test_24_lookahead_rows_collapse_to_one_executed_record_per_resolve():
    rec = pet.ExecutedHourRecorder()
    for step in range(24):
        _record(rec, origin=1, step=step, rows=_rows(base=10000.0 * step))
    assert len(rec.records) == 24
    assert [r.step for r in rec.records] == list(range(24))
    assert all(r.plan_hour == 0 for r in rec.records)


def test_executed_record_uses_plan_hour_0_values_not_lookahead():
    rec = pet.ExecutedHourRecorder()
    rows = _rows(base=7000.0)
    r = _record(rec, origin=1, step=3, rows=rows)
    assert r.planned_served_c_w == rows[0]["served_c"] == 7000.0
    assert r.planned_unmet_crit_w == rows[0]["unmet_crit"] == 3000.0
    assert r.planned_charge_w == rows[0]["charge"] == 5000.0
    assert r.planned_diesel_w == rows[0]["diesel"] == 6000.0


def test_executed_record_rejects_non_24_or_misordered_plans():
    rec = pet.ExecutedHourRecorder()
    with pytest.raises(ValueError):
        _record(rec, origin=1, step=0, rows=_rows(0.0)[:23])
    bad = _rows(0.0)
    bad[0], bad[1] = bad[1], bad[0]
    with pytest.raises(ValueError):
        _record(rec, origin=1, step=0, rows=bad)


def test_max_discharge_uses_preregistered_formula_and_cap():
    rec = pet.ExecutedHourRecorder()
    r = _record(rec, origin=1, step=0, rows=_rows(0.0), e_start=100000.0)
    assert r.max_discharge_w == pytest.approx(min(50000.0, (100000.0 - 40000.0) * 0.92))
    r2 = _record(rec, origin=1, step=1, rows=_rows(0.0), e_start=200000.0)
    assert r2.max_discharge_w == 50000.0
    r3 = _record(rec, origin=1, step=2, rows=_rows(0.0), e_start=30000.0)
    assert r3.max_discharge_w == 0.0


# ---------------------------------------------------------------------------
# E_t is the start-of-hour state
# ---------------------------------------------------------------------------

def test_recorded_E_t_is_the_input_start_of_hour_energy():
    rec = pet.ExecutedHourRecorder()
    r = _record(rec, origin=1, step=0, rows=_rows(0.0), e_start=123456.0)
    assert r.E_t_wh == 123456.0
    # Planned E_next of hour 0 is a different quantity and must not be used as E_t.
    assert r.E_t_wh != _rows(0.0)[0]["E_next"]


def test_oracle_runner_captures_E_t_before_execution_and_advances_state_after():
    src = inspect.getsource(oracle.run_oracle_origin)
    i_cap = src.index("e_start_wh = state.battery_energy_wh")
    i_exec = src.index("res = executor.execute_step(state, plan, realized, step_index=0)")
    i_rec = src.index("exec_recorder.record_resolve(")
    i_adv = src.index("state = res.next_state")
    assert i_cap < i_exec < i_rec < i_adv
    assert "e_start_wh=e_start_wh" in src


# ---------------------------------------------------------------------------
# G2 / G3 evaluator: deterministic on synthetic data
# ---------------------------------------------------------------------------

def _rec_dict(**kw):
    base = dict(origin_id=1, arm="PC-Control", step=0, plan_hour=0, E_t_wh=100000.0,
                pv_real_w=0.0, wind_real_w=0.0, planned_diesel_w=0.0, d_c_w=11600.0,
                max_discharge_w=0.0, planned_served_c_w=11600.0, planned_served_nc_w=0.0,
                planned_unmet_crit_w=0.0, planned_unmet_nc_w=0.0, planned_charge_w=0.0)
    base.update(kw)
    return base


def test_g2_flags_nc_unmet_with_planned_charge():
    res = pet.evaluate_g2_g3([_rec_dict(planned_unmet_nc_w=500.0, planned_charge_w=100.0)])
    assert res["G2_PASS"] is False and res["g2_violations"] == [("PC-Control", 1, 0)]


def test_g2_passes_when_no_charge_or_no_nc_unmet():
    recs = [_rec_dict(step=0, planned_unmet_nc_w=500.0, planned_charge_w=0.0),
            _rec_dict(step=1, planned_unmet_nc_w=0.0, planned_charge_w=900.0)]
    assert pet.evaluate_g2_g3(recs)["G2_PASS"] is True


def test_g3_boundary_strict_inequality():
    # S_avail + max_dis == D_c is NOT < D_c, so unmet_crit > 0 there is a violation.
    on_bound = _rec_dict(planned_unmet_crit_w=10.0, pv_real_w=1000.0, wind_real_w=1000.0,
                         planned_diesel_w=1000.0, max_discharge_w=8600.0, d_c_w=11600.0)
    assert pet.evaluate_g2_g3([on_bound])["G3_PASS"] is False
    just_below = dict(on_bound, max_discharge_w=8599.0)
    assert pet.evaluate_g2_g3([just_below])["G3_PASS"] is True


def test_g3_excludes_planned_discharge_from_supply():
    # Planned discharge is not in the record at all; S_avail uses realized PV+W and planned diesel only.
    # 4000 W supply + 0 W discharge < 11600 W critical demand: shedding is feasible -> G3 passes.
    short = _rec_dict(planned_unmet_crit_w=10.0, pv_real_w=2000.0, wind_real_w=2000.0,
                      planned_diesel_w=0.0, max_discharge_w=0.0, d_c_w=11600.0)
    assert pet.evaluate_g2_g3([short])["G3_PASS"] is True
    # 12000 W supply (realized PV+W) >= 11600 W critical demand: shedding is infeasible -> G3 violation.
    enough = _rec_dict(planned_unmet_crit_w=10.0, pv_real_w=6000.0, wind_real_w=6000.0,
                       planned_diesel_w=0.0, max_discharge_w=0.0, d_c_w=11600.0)
    res = pet.evaluate_g2_g3([enough])
    assert res["G3_PASS"] is False
    assert res["g3_violations"] == [("PC-Control", 1, 0)]


def test_evaluator_is_deterministic_and_order_independent():
    recs = [_rec_dict(origin_id=2, step=5, planned_unmet_nc_w=1.0, planned_charge_w=1.0),
            _rec_dict(origin_id=1, step=3, planned_unmet_crit_w=10.0, pv_real_w=6000.0, wind_real_w=6000.0,
                      max_discharge_w=0.0, d_c_w=11600.0),
            _rec_dict(origin_id=1, step=0, planned_unmet_nc_w=1.0, planned_charge_w=1.0)]
    a = pet.evaluate_g2_g3(recs)
    b = pet.evaluate_g2_g3(list(reversed(recs)))
    assert a == b
    assert a["g2_violations"] == [("PC-Control", 1, 0), ("PC-Control", 2, 5)]
    assert a["g3_violations"] == [("PC-Control", 1, 3)]


def test_evaluator_on_real_optimizer_synthetic_is_deterministic():
    night = [0.0] * 24
    wind = [4500.0] * 24
    dem = [12000.0] * 24
    crit = [min(11600.0, d) for d in dem]

    class _S:
        def __init__(self, p):
            self.point = list(p)

    class _B:
        timestamps = [f"2025-05-01T{h:02d}:00:00Z" for h in range(24)]
        solar_generation = _S(night)
        wind_generation = _S(wind)
        demand = _S(dem)
        demand_critical = None

    cfg = oracle.canonical_configs()
    cfg["critical_demand_w"] = crit
    state = StationState(timestamp="2025-04-30T23:00:00Z", battery_soc_pct=50.0,
                         battery_energy_wh=100000.0, diesel_running=False, diesel_hours_running=0.0,
                         last_observed_solar_irradiance=0.0, last_observed_demand=15000.0,
                         last_observed_wind_generation=4500.0, diesel_fuel_remaining_liters=100.0,
                         operating_mode="NORMAL")

    def run():
        opt = planner.PlannerCFV1Optimizer()
        opt.optimize(_B(), state, cfg)
        rec = pet.ExecutedHourRecorder()
        rec.record_resolve(origin_id=0, arm="PC-Control", step=0, planned_rows=opt.last_planned,
                           e_start_wh=100000.0, pv_real_w=0.0, wind_real_w=4500.0,
                           d_c_real_w=crit[0], e_min_wh=E_MIN, eta_dis=ETA_DIS)
        return pet.evaluate_g2_g3(rec.records)

    first, second = run(), run()
    assert first == second
    assert first["G2_PASS"] is True and first["G3_PASS"] is True
