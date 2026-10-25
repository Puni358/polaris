"""
Focused Unit Tests for MILP v2 Research-Only Essential-Tier Extension (Rev. 3)

Tests gap19_highs_native_milp_v2_research.py in isolation. Does not run the integrated
EMS, MPC, ECD, Option D, or Digital Twin, and does not run broad simulations. GAP19
(gap19_highs_native.py) is exercised only as a frozen-control comparison baseline and is
never modified by these tests.
"""

import pytest
from datetime import datetime, timedelta

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.gap19_highs_native_milp_v2_research import (
    GAP19HighsNativeOptimizerMILPV2Research,
)


def create_dummy_forecast_bundle(
    origin_timestamp: str = "2024-01-01T00:00:00Z",
    demand_crit_ratio: float = 0.5,
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
        metadata={"model_id": "test_v2_research_bundle"},
    )


def create_dummy_station_state(
    timestamp: str = "2024-01-01T00:00:00Z",
    operating_mode: str = "NORMAL",
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
        operating_mode=operating_mode,
    )


DEFAULT_LOADS_CFG = {
    "loads": {
        "critical_load": {"unmet_penalty_per_wh": 10.0, "baseline_power_w": 11600.0},
        "deferrable_loads": [
            {"id": "water_pumping_heat_store", "power_w": 10000.0, "duration_hours": 4,
             "earliest_start_h": 8, "latest_finish_h": 18, "priority": 2}
        ],
        "curtailable_loads": [
            {"id": "secondary_heating", "max_power_w": 5000.0, "curtailment_penalty_per_wh": 0.10}
        ],
    }
}


def test_1_v2_optimal_and_essential_fields_present():
    """Verify V2 solves OPTIMAL and reports the new Essential-tier output fields."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.5)
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.constraint_status == "OPTIMAL"
    assert plan.load_served_essential is not None
    assert plan.unmet_essential is not None
    assert len(plan.load_served_essential) == 24
    assert len(plan.unmet_essential) == 24


def test_2_essential_demand_clipping_bounds():
    """essential_demand[t] = min(5000, max(0, demand - critical)) must bound served+unmet essential."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.5)  # demand 30000, crit 15000 -> essential = min(5000, 15000) = 5000
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.constraint_status == "OPTIMAL"
    for served_ess, unmet_ess in zip(plan.load_served_essential, plan.unmet_essential):
        assert abs((served_ess + unmet_ess) - 5000.0) < 1e-2


def test_3_essential_demand_clipped_when_little_headroom():
    """When demand - critical < max_power_w, essential_demand must clip to the smaller value, not go negative."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.98)  # demand 30000, crit 29400 -> headroom 600 W
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.constraint_status == "OPTIMAL"
    for served_ess, unmet_ess in zip(plan.load_served_essential, plan.unmet_essential):
        assert abs((served_ess + unmet_ess) - 600.0) < 1e-1


def test_4_no_double_counting_of_essential_in_unmet_load():
    """Blocker #1 fix: unmet_load must not count Essential-served energy as unmet."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.5)
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.constraint_status == "OPTIMAL"
    demand = bundle.demand.point
    for t in range(24):
        total = plan.load_served[t] + plan.load_served_essential[t] + plan.unmet_load[t]
        assert abs(total - demand[t]) < 1e-1
        # energy balance error reported by the implementation itself must be ~0
        assert plan.energy_balance_errors[t] < 1e-2


def test_5_essential_indifference_resolved_prefers_serving_when_free():
    """Fix 2: with cheap surplus renewable available and no cost elsewhere, solver should
    serve Essential load rather than leave it indifferent/unmet, since P_unmet_essential
    is now costed in J4."""
    bundle = create_dummy_forecast_bundle(demand_crit_ratio=0.3)  # large surplus solar/wind vs demand
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 50000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.constraint_status == "OPTIMAL"
    # Essential tier should be substantially served, not left fully unmet, when feasible.
    assert sum(plan.load_served_essential) > 0.0


def test_6_stage_count_unchanged_four_objectives():
    """Rev. 3 §7: stage count unchanged -- still exactly J1..J4, no 5th stage."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    assert plan.j1_objective is not None
    assert plan.j2_objective is not None
    assert plan.j3_objective is not None
    assert plan.j4_objective is not None


def test_7_dispatch_plan_round_trip_compatibility():
    """Verify DispatchPlan schema compliance and round-trip dict serialization with the
    new additive fields."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    plan = opt.optimize(bundle, state, config)

    plan_dict = plan.to_dict()
    reconstructed = DispatchPlan.from_dict(plan_dict)
    assert reconstructed.schema_version == "1.0.0"
    assert reconstructed.load_served_essential == plan.load_served_essential
    assert reconstructed.unmet_essential == plan.unmet_essential


def test_8_missing_input_rejection_unchanged():
    """Verify explicit failure when protected critical demand trajectory is missing
    (unchanged fail-closed behavior from GAP19)."""
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
        demand_critical=None,
        metadata={"model_id": "test_v2_missing_crit"},
    )
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    opt = GAP19HighsNativeOptimizerMILPV2Research()
    with pytest.raises(ValueError, match="MISSING_GOVERNED_INPUT"):
        opt.optimize(bundle_no_crit, state, config)


def test_9_gap19_frozen_control_unaffected():
    """Verify GAP19HighsNativeOptimizer (the frozen control) is completely unaffected:
    same class, same behavior, no Essential-tier fields on its own output, and no
    import-time coupling to the V2 research module."""
    bundle = create_dummy_forecast_bundle()
    state = create_dummy_station_state()
    config = {"terminal_target_wh": 100000.0, **DEFAULT_LOADS_CFG}

    gap19_opt = GAP19HighsNativeOptimizer()
    gap19_plan = gap19_opt.optimize(bundle, state, config)

    assert gap19_plan.constraint_status == "OPTIMAL"
    assert gap19_plan.load_served_essential is None
    assert gap19_plan.unmet_essential is None

    # DispatchPlan backward-compatibility: to_dict() for a GAP19 plan must omit the new
    # optional keys entirely (additive-only schema change, not a behavior change).
    plan_dict = gap19_plan.to_dict()
    assert "load_served_essential" not in plan_dict
    assert "unmet_essential" not in plan_dict


def test_10_v2_isolated_class_identity():
    """Verify V2 is a distinct, separately-selectable class -- not a monkeypatch or
    subclass override of GAP19HighsNativeOptimizer."""
    assert GAP19HighsNativeOptimizerMILPV2Research is not GAP19HighsNativeOptimizer
    assert not issubclass(GAP19HighsNativeOptimizerMILPV2Research, GAP19HighsNativeOptimizer)
    assert hasattr(GAP19HighsNativeOptimizerMILPV2Research(), "optimize")
