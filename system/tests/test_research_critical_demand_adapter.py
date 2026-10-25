"""
Unit and Integration Tests for Research Critical Demand Adapter
Module: system.tests.test_research_critical_demand_adapter
"""

import math
from pathlib import Path
import pytest
import pandas as pd
import yaml

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.research.research_critical_demand_adapter import (
    adapt_critical_demand_vector,
    AdaptedClosedLoopRunner
)


@pytest.fixture
def default_configs():
    with open("system/config/battery.yaml") as f: bat = yaml.safe_load(f)
    with open("system/config/diesel.yaml") as f: die = yaml.safe_load(f)
    with open("system/config/solar_pv.yaml") as f: sol = yaml.safe_load(f)
    with open("system/config/loads.yaml") as f: loads = yaml.safe_load(f)
    return {
        "battery": bat,
        "diesel": die,
        "solar_pv": sol,
        "loads": loads,
        "critical_demand_baseline_w": 11600.0,
        "terminal_target_wh": 100000.0,
        # Explicit SYNTHETIC test-fixture authorization for the router/ECD
        # fail-closed contract (ECD-01, A-iii/B-iii); NOT a real-station
        # evidence record -- see tests/test_isolated_components.py for
        # the convention.
        "ecd": {"t_required_hours": 6.0, "t_required_authorized": True},
        "critical_load": {
            "authorized": True,
            "evidence_id": "EVID-TEST-CRITICAL-DEMAND-ADAPTER",
            "authorized_critical_load_w": 5000.0,
        },
    }


def test_micro_cases_critical_demand_clipping():
    """Micro-test: verifies clipping formula across required benchmark levels."""
    ceiling = 11600.0
    
    # Case A: 15,000 W -> 11,600 W
    res_a = adapt_critical_demand_vector(ceiling, [15000.0] * 24)
    assert res_a == [11600.0] * 24
    
    # Case B: 11,325.76 W -> 11,325.76 W
    res_b = adapt_critical_demand_vector(ceiling, [11325.76] * 24)
    assert res_b == [11325.76] * 24
    
    # Case C: 10,000 W -> 10,000 W
    res_c = adapt_critical_demand_vector(ceiling, [10000.0] * 24)
    assert res_c == [10000.0] * 24
    
    # Case D: 20,000 W -> 11,600 W
    res_d = adapt_critical_demand_vector(ceiling, [20000.0] * 24)
    assert res_d == [11600.0] * 24


def test_gap19_accepts_all_four_micro_cases(default_configs):
    """Verifies that unmodified GAP19 accepts all four micro-test cases."""
    opt = GAP19HighsNativeOptimizer()
    cases = [
        ("A", 15000.0, 11600.0),
        ("B", 11325.76, 11325.76),
        ("C", 10000.0, 10000.0),
        ("D", 20000.0, 11600.0)
    ]
    
    state = StationState(
        timestamp="2024-04-30T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4000.0,
        diesel_fuel_remaining_liters=100.0
    )
    
    for name, total_d, expected_crit in cases:
        d_points = [total_d] * 24
        crit_w = adapt_critical_demand_vector(11600.0, d_points)
        assert crit_w == [expected_crit] * 24
        
        ts = [f"2024-05-01T{h:02d}:00:00Z" for h in range(24)]
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp="2024-04-30T23:00:00Z",
            horizon_hours=24,
            timestamps=ts,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            wind_generation=TimeseriesForecast([4000.0]*24, [4000.0]*24, [4000.0]*24, "W"),
            demand=TimeseriesForecast(d_points, d_points, d_points, "W"),
            metadata={"test": f"case_{name}"}
        )
        
        cfg = dict(default_configs)
        cfg["critical_demand_w"] = crit_w
        plan = opt.optimize(bundle, state, cfg)
        assert plan.constraint_status in ("OPTIMAL", "FEASIBLE")


def test_cross_arm_adaptation_invariance(default_configs):
    """Verifies that the critical demand vector is 100% identical across Arms A, B, and C."""
    state = StationState(
        timestamp="2024-04-30T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0
    )
    
    # Arm A
    engine_a = LocalBaselineForecastEngine(Path("system/config/solar_pv.yaml"))
    bundle_a = engine_a.predict(state, {})
    
    # Arm B
    engine_b = CausalNwpPhysicsForecastEngine()
    bundle_b = engine_b.predict(state, {"fc_cloud_cover": [30.0]*24})
    
    crit_a = adapt_critical_demand_vector(11600.0, bundle_a.demand.point)
    crit_b = adapt_critical_demand_vector(11600.0, bundle_b.demand.point)
    
    assert crit_a == crit_b
    assert all(c <= 11600.0 for c in crit_a)
    assert all(c <= d for c, d in zip(crit_a, bundle_a.demand.point))


def test_adapted_runner_executes_origin_1(default_configs):
    """Verifies AdaptedClosedLoopRunner completes 24h of Origin 1 without error."""
    df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    sub = df[df["forecast_start"] == "2024-05-01 00:00:00"]
    realized_solar = sub["actual_SW_IN"].tolist()
    realized_ts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    realized_wind = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    realized_demand = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    state0 = StationState(
        timestamp="2024-04-30T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0
    )

    runner = AdaptedClosedLoopRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=state0,
        hours_to_run=24,
        weather_dataset=df,
        realized_solar=realized_solar,
        realized_wind=realized_wind,
        realized_demand=realized_demand,
        realized_timestamps=realized_ts
    )

    assert report.execution_status == "SUCCESS"
    assert report.total_hours_executed == 24
    assert report.reoptimizations_count == 24
    assert len(report.step_records) == 24
    assert report.cumulative_diesel_fuel_l > 0.0
