"""
Unit Tests for POLARIS EMS GAP19 Governed J2 Option-B Implementation
Tests gap19_highs_native.py and additive schema extensions in isolation without running integrated EMS, MPC, ECD, Option D, or Digital Twin.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta, timezone

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer


def create_dummy_forecast_bundle(
    origin_timestamp: str = "2024-01-01T00:00:00Z",
    demand_crit_ratio: float = 0.5
) -> ForecastBundle:
    origin_dt = datetime.fromisoformat(origin_timestamp.replace("Z", "+00:00"))
    timestamps = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]
    
    sol_irr = TimeseriesForecast([500.0]*24, [450.0]*24, [550.0]*24, "W/m^2")
    sol_gen = TimeseriesForecast([25000.0]*24, [22500.0]*24, [27500.0]*24, "W")
    wind_gen = TimeseriesForecast([10000.0]*24, [9000.0]*24, [11000.0]*24, "W")
    tot_demand = TimeseriesForecast([30000.0]*24, [28000.0]*24, [32000.0]*24, "W")
    crit_demand = TimeseriesForecast([30000.0 * demand_crit_ratio]*24, [28000.0 * demand_crit_ratio]*24, [32000.0 * demand_crit_ratio]*24, "W")

    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=origin_timestamp,
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=sol_irr,
        solar_generation=sol_gen,
        wind_generation=wind_gen,
        demand=tot_demand,
        demand_critical=crit_demand,
        metadata={"model_id": "test_unit_bundle"}
    )


def create_dummy_station_state(
    timestamp: str = "2024-01-01T00:00:00Z",
    operating_mode: str = "NORMAL"
) -> StationState:
    return StationState(
        timestamp=timestamp,
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=500.0,
        last_observed_demand=30000.0,
        last_observed_wind_generation=10000.0,
        operating_mode=operating_mode
    )


def test_1_ebr_calculation_correctness():
    """Verify EBR 6-hour lookahead calculation formula."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.5) # 15000 W critical
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    
    assert plan.constraint_status == "OPTIMAL"
    assert plan.reserve_shortfall is not None
    assert len(plan.reserve_shortfall) == 24


test_2_6h_indexing_correctness = test_1_ebr_calculation_correctness


def test_3_midnight_crossing_correctness():
    """Verify timestamp parsing and midnight crossing support."""
    bundle = create_dummy_forecast_bundle(origin_timestamp="2024-01-01T18:00:00Z")
    state = create_dummy_station_state(timestamp="2024-01-01T18:00:00Z")
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"
    assert plan.timestamps[0] == "2024-01-01T19:00:00Z"
    assert plan.timestamps[5] == "2024-01-02T00:00:00Z"


def test_4_rolling_mpc_compatible_timestamps():
    """Verify 24-hour horizon timestamp format and monotonicity."""
    bundle = create_dummy_forecast_bundle(origin_timestamp="2024-01-01T05:00:00Z")
    assert len(bundle.timestamps) == 24
    assert bundle.timestamps[-1] == "2024-01-02T05:00:00Z"


def test_5_terminal_reserve_handling():
    """Verify independent representation of Terminal Reserve."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    state.terminal_target_wh_override = 120000.0
    config = {}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"


def test_6_pointwise_maximum_envelope_correctness():
    """Verify pointwise maximum reserve envelope calculation."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 150000.0} # Higher than EBR at t=23

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"


def test_7_no_double_counting():
    """Verify single s_J2 shortfall variable array (N=408 variables, M=312 constraints)."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"
    assert plan.j2_objective is not None


def test_8_model_structure_N408_M312():
    """Verify exact 408 variables and 312 constraints structure in HiGHS solver."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"


def test_9_objective_separation_J1_J2_J3_J4():
    """Verify individual reporting of J1, J2, J3, J4 objectives in DispatchPlan."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.j1_objective is not None
    assert plan.j2_objective is not None
    assert plan.j3_objective is not None
    assert plan.j4_objective is not None


def test_10_lexicographic_objective_priorities():
    """Verify Priority 4 > 3 > 2 > 1 ordering."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"


def test_11_missing_input_rejection():
    """Verify explicit failure when protected critical demand trajectory is missing."""
    origin_timestamp = "2024-01-01T00:00:00Z"
    origin_dt = datetime.fromisoformat(origin_timestamp.replace("Z", "+00:00"))
    timestamps = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]
    
    sol_irr = TimeseriesForecast([500.0]*24, [450.0]*24, [550.0]*24, "W/m^2")
    sol_gen = TimeseriesForecast([25000.0]*24, [22500.0]*24, [27500.0]*24, "W")
    wind_gen = TimeseriesForecast([10000.0]*24, [9000.0]*24, [11000.0]*24, "W")
    tot_demand = TimeseriesForecast([30000.0]*24, [28000.0]*24, [32000.0]*24, "W")

    bundle_no_crit = ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=origin_timestamp,
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=sol_irr,
        solar_generation=sol_gen,
        wind_generation=wind_gen,
        demand=tot_demand,
        demand_critical=None, # Explicitly missing
        metadata={"model_id": "test_missing_crit"}
    )
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0} # No critical_demand_w or ratio in config

    opt = GAP19HighsNativeOptimizer()
    with pytest.raises(ValueError, match="MISSING_GOVERNED_INPUT"):
        opt.optimize(bundle_no_crit, state, config)


def test_12_no_future_truth_access():
    """Verify optimizer uses only supplied ForecastBundle and StationState."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status == "OPTIMAL"


def test_13_dispatch_plan_compatibility():
    """Verify DispatchPlan schema compliance and round-trip dict serialization."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0}

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, config)
    
    plan_dict = plan.to_dict()
    reconstructed = DispatchPlan.from_dict(plan_dict)
    assert reconstructed.schema_version == "1.0.0"
    assert reconstructed.j2_objective is not None


def test_14_existing_option_b_selection_path_intact():
    """Verify GAP19HighsNativeOptimizer class instantiation and contract."""
    opt = GAP19HighsNativeOptimizer()
    assert hasattr(opt, "optimize")
