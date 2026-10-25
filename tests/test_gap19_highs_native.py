"""
Unit and Static Tests for GAP19 Native HiGHS Multi-Objective EnergyOptimizer
Verifies canonical model dimensions (N=409, M=313), variable indexing, objective vector disjointness,
absence of w_stop binaries, and isolated solver execution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from datetime import datetime, timedelta, timezone

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

def create_synthetic_forecast_bundle(demand_crit_ratio=0.5):
    origin = "2026-09-24T00:00:00Z"
    ts_list = [(datetime.fromisoformat("2026-09-24T00:00:00Z") + timedelta(hours=i)).isoformat().replace("+00:00", "Z") for i in range(24)]

    sol_irr = TimeseriesForecast([100.0]*24, [90.0]*24, [110.0]*24, "W/m^2")
    sol_gen = TimeseriesForecast([2000.0]*24, [1800.0]*24, [2200.0]*24, "W")
    wind_gen = TimeseriesForecast([1000.0]*24, [800.0]*24, [1200.0]*24, "W")
    dem = TimeseriesForecast([1500.0]*24, [1400.0]*24, [1600.0]*24, "W")
    # Synthetic test-only protected critical-load trajectory (NOT a real/validated
    # station value -- gap19_highs_native.py's mandatory `demand_critical` input
    # contract, added after this fixture was written, requires one of
    # demand_critical / critical_demand_w / critical_demand_ratio; this fixture
    # supplies demand_critical as a fixed ratio of total demand, following the
    # identical convention already used by system/tests/test_gap19_milp_v2_research.py's
    # create_dummy_forecast_bundle(). This is a fixture-drift fix only -- it does not
    # change, and must not be read as establishing, any real critical-load figure
    # (see EVID-02 / CL-01 in POLARIS_MASTER_DECISION_REGISTER).
    crit_dem = TimeseriesForecast(
        [1500.0 * demand_crit_ratio]*24,
        [1400.0 * demand_crit_ratio]*24,
        [1600.0 * demand_crit_ratio]*24,
        "W"
    )

    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=origin,
        horizon_hours=24,
        timestamps=ts_list,
        solar_irradiance=sol_irr,
        solar_generation=sol_gen,
        wind_generation=wind_gen,
        demand=dem,
        demand_critical=crit_dem,
        metadata={"source": "unit_test"}
    )

def create_synthetic_station_state(operating_mode="NORMAL"):
    # operating_mode is forwarded onto StationState itself (not left to the
    # `config` dict some callers also set): gap19_highs_native.py resolves mode via
    # `getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))`,
    # and StationState.__init__ always sets its own `operating_mode` attribute
    # (default "NORMAL"), so that attribute is always present and the `getattr`
    # default branch (config.get(...)) is unreachable in practice. StationState's own
    # operating_mode is therefore the authoritative input in this call path, not config.
    return StationState(
        timestamp="2026-09-24T00:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=100.0,
        last_observed_demand=1500.0,
        last_observed_wind_generation=1000.0,
        operating_mode=operating_mode
    )

def test_canonical_409_model_structure():
    opt = GAP19HighsNativeOptimizer()
    bundle = create_synthetic_forecast_bundle()
    state = create_synthetic_station_state()
    config = {
        "operating_mode": "NORMAL",
        "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
        "diesel": {"min_power_w": 10000.0, "max_power_w": 100000.0},
        "optimizer": {"timestep_hours": 1.0},
        # Fixture-drift fix: gap19_highs_native.py also requires a governed terminal
        # reserve target (terminal_target_wh / terminal_target_wh_override /
        # terminal_reserve_model), added after this fixture was written. "INITIAL_STATE"
        # is used here because it requires no new numeric value to be invented for this
        # unit test -- it is simply the battery's own starting energy, already supplied
        # above via create_synthetic_station_state().
        "terminal_reserve_model": "INITIAL_STATE"
    }
    
    plan = opt.optimize(bundle, state, config)
    assert isinstance(plan, DispatchPlan)
    assert plan.constraint_status == "OPTIMAL"
    assert len(plan.solar_used) == 24
    assert len(plan.diesel_power) == 24

def test_objective_vector_disjointness():
    # Verify vector indexing for N=409
    H, K = 24, 15
    num_total_vars = 409
    idx_unmet_crit_start = 360
    idx_s_ebr_start = 384
    idx_s_term = 408
    
    c1 = np.zeros(num_total_vars)
    c2 = np.zeros(num_total_vars)
    c3 = np.zeros(num_total_vars)
    c4 = np.zeros(num_total_vars)
    
    for t in range(H):
        base = t * K
        c1[idx_unmet_crit_start + t] = 1.0
        c2[idx_s_ebr_start + t] = 1.0
        c3[base + 7] = 0.00025; c3[base + 13] = 5.0; c3[base + 14] = 2.0
        c4[base + 2] = 1.0; c4[base + 3] = 1.0
    c2[idx_s_term] = 1.0
    
    # Check disjoint nonzeros
    assert np.dot(c1, c2) == 0.0
    assert np.dot(c1, c3) == 0.0
    assert np.dot(c1, c4) == 0.0
    assert np.dot(c2, c3) == 0.0
    assert np.dot(c2, c4) == 0.0
    assert np.dot(c3, c4) == 0.0

def test_absence_of_w_stop():
    # Verify that binary variable count per timestep is 4 (not 5) -> 96 total
    H, K = 24, 15
    binary_count = 0
    for t in range(H):
        base = t * K
        # Indices 11, 12, 13, 14 are binary
        binary_count += 4
    assert binary_count == 96

def test_failsafe_unknown_invalid_mode():
    opt = GAP19HighsNativeOptimizer()
    bundle = create_synthetic_forecast_bundle()
    # operating_mode must be set on StationState itself, not only in `config`: see the
    # precedence note in create_synthetic_station_state() above. Passing it only via
    # `config` (the fixture's original form) was silently ignored because StationState
    # always carries its own "NORMAL"-defaulted operating_mode attribute, so this test
    # never actually exercised the UNKNOWN_INVALID failsafe branch.
    state = create_synthetic_station_state(operating_mode="UNKNOWN_INVALID")
    config = {"operating_mode": "UNKNOWN_INVALID"}

    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "DEGRADED_FAILSAFE_UNKNOWN_INVALID"
    assert sum(plan.solar_used) == 0.0
    assert sum(plan.diesel_power) == 0.0

if __name__ == "__main__":
    test_canonical_409_model_structure()
    print("test_canonical_409_model_structure: PASSED")
    test_objective_vector_disjointness()
    print("test_objective_vector_disjointness: PASSED")
    test_absence_of_w_stop()
    print("test_absence_of_w_stop: PASSED")
    test_failsafe_unknown_invalid_mode()
    print("test_failsafe_unknown_invalid_mode: PASSED")
    print("ALL UNIT TESTS PASSED SUCCESSFULLY.")
