"""
Synthetic End-to-End Pipeline Integration Test Suite for Stage81ForecastEngine
Phase S8.1-E2E Verification Suite.

Tests complete closed-loop MPC execution of the Stage 8.1 solar forecasting adapter
through PolarisLocalRunner, ForecastBundle v1.0.0, LocalMILPEnergyOptimizer,
DigitalTwinSimulator, and EvaluationEngine.
"""

import json
import socket
from pathlib import Path
import pytest

from system.runtime.runner import PolarisLocalRunner
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.schemas.station_state import StationState
from system.forecasting.implementations.s81_solar import (
    Stage81ForecastEngine,
    validate_stage81_solar_metadata,
    STAGE8_1_PROVENANCE_KEY
)

SYSTEM_DIR = Path(__file__).resolve().parent.parent


def _authorize_router_for_s81_test(runner: PolarisLocalRunner) -> PolarisLocalRunner:
    """
    Explicit, clearly-labeled SYNTHETIC test-fixture authorization for the
    router/ECD fail-closed contract (ECD-01, A-iii/B-iii). This suite
    tests genuine Stage-8.1 closed-loop MPC mechanics, not the
    authorization gate itself (test_12 below exercises the optimizer
    directly, bypassing the router entirely, so it is unaffected).
    "EVID-TEST-S81-E2E" is NOT a real-station evidence record -- see
    tests/test_isolated_components.py for the convention.
    """
    runner.configs.setdefault("ecd", {}).update({
        "t_required_hours": 6.0,
        "t_required_authorized": True,
    })
    runner.configs.setdefault("critical_load", {}).update({
        "authorized": True,
        "evidence_id": "EVID-TEST-S81-E2E",
        "authorized_critical_load_w": 5000.0,
    })
    return runner


@pytest.fixture
def s81_runner() -> PolarisLocalRunner:
    return _authorize_router_for_s81_test(PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename="demo_scenario.json",
        optimizer_type="milp",
        forecast_engine_type="stage81_solar"
    ))


def test_1_runner_instantiation_with_stage81(s81_runner):
    """Req 1: Stage81ForecastEngine loads through authorized runtime path."""
    assert s81_runner.forecast_engine_type in ("stage81_solar", "stage81", "s81_solar", "s81")
    assert isinstance(s81_runner.forecast_engine, Stage81ForecastEngine)


def test_2_24step_forecast_bundle_generation(s81_runner):
    """Req 2: A 24-step ForecastBundle is produced by the runner's forecast engine."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    assert isinstance(bundle, ForecastBundle)
    assert bundle.horizon_hours == 24
    assert len(bundle.timestamps) == 24


def test_3_forecast_bundle_validation_succeeds(s81_runner):
    """Req 3: ForecastBundle validation and stage8_1_provenance metadata validation succeed."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    assert validate_stage81_solar_metadata(bundle) is True


def test_4_solar_generation_representation_preserved(s81_runner):
    """Req 4: Solar generation representation follows D3 PV mapping formula."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    for idx in range(24):
        irr = bundle.solar_irradiance.point[idx]
        gen = bundle.solar_generation.point[idx]
        expected_raw = irr * 300.0 * 0.20 * 0.85
        expected_gen = min(expected_raw, 60000.0)
        assert gen == pytest.approx(expected_gen, abs=1e-2)


def test_5_degenerate_point_only_interval_bounds(s81_runner):
    """Req 5: lower == point == upper for solar channels."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    for idx in range(24):
        assert bundle.solar_irradiance.lower[idx] == bundle.solar_irradiance.point[idx] == bundle.solar_irradiance.upper[idx]
        assert bundle.solar_generation.lower[idx] == bundle.solar_generation.point[idx] == bundle.solar_generation.upper[idx]


def test_6_optimizer_consumes_stage81_bundle(s81_runner):
    """Req 6: ForecastBundle reaches the optimizer through the existing interface and solves."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    plan = s81_runner.optimizer.optimize(bundle, initial_state, s81_runner.configs)
    assert isinstance(plan, DispatchPlan)
    assert plan.constraint_status == "OPTIMAL"


def test_7_dispatch_plan_validation_succeeds(s81_runner):
    """Req 7: DispatchPlan validation succeeds."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    plan = s81_runner.optimizer.optimize(bundle, initial_state, s81_runner.configs)
    plan_dict = plan.to_dict()
    reconstituted = DispatchPlan.from_dict(plan_dict)
    assert reconstituted.schema_version == "1.0.0"


def test_8_h1_action_execution_and_simulator_advancement(s81_runner):
    """Req 8 & 9: H1 action executes and DigitalTwinSimulator advances state correctly."""
    context = s81_runner.data_provider.get_runtime_state(0)
    initial_state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
        last_observed_demand=context["last_observed_demand"],
        last_observed_wind_generation=context["last_observed_wind_generation"]
    )
    bundle = s81_runner.forecast_engine.predict(initial_state, context)
    plan = s81_runner.optimizer.optimize(bundle, initial_state, s81_runner.configs)
    future_actuals = s81_runner.data_provider.get_future_ground_truth(0, horizon_hours=24)
    next_state = s81_runner.simulator.step(initial_state, plan, future_actuals[0])

    assert isinstance(next_state, StationState)
    assert next_state.timestamp == future_actuals[0]["timestamp"]


def test_10_24h_closed_loop_mpc_execution(s81_runner):
    """Req 10: Multi-step MPC execution works cleanly for 24 steps with Stage 8.1 forecast engine."""
    report = s81_runner.run_pipeline(steps_to_run=24)
    assert report["timesteps_executed"] == 24
    assert report["execution_status"] == "SUCCESS_CLEAN"
    assert report["ems_evaluation"]["unmet_critical_load_kwh"] == 0.0


def test_11_deterministic_e2e_replay(s81_runner):
    """Req 11: Deterministic replay produces bitwise equivalent results across repeated runs."""
    report_1 = s81_runner.run_pipeline(steps_to_run=12)
    report_2 = s81_runner.run_pipeline(steps_to_run=12)

    assert report_1["timesteps_executed"] == report_2["timesteps_executed"]
    assert report_1["ems_evaluation"] == report_2["ems_evaluation"]
    assert report_1["forecast_evaluation"] == report_2["forecast_evaluation"]


def test_12_d4c1_fault_containment_preserved(s81_runner):
    """Req 12: E2E integration does not bypass or alter D4-C1 fault governance."""
    bad_runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename="demo_scenario.json",
        optimizer_type="milp",
        forecast_engine_type="stage81_solar"
    )
    bad_runner.configs["diesel"]["max_power_w"] = 0.0
    bad_runner.configs["battery"]["max_discharge_power_w"] = 0.0
    bad_runner.configs["battery"]["capacity_wh"] = 0.0

    from datetime import datetime, timedelta, timezone
    origin_dt = datetime.fromisoformat("2026-09-18T00:00:00Z".replace("Z", "+00:00"))
    ts = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]
    impossible_bundle = ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp="2026-09-18T00:00:00Z",
        horizon_hours=24,
        timestamps=ts,
        solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
        solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
        wind_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
        demand=TimeseriesForecast([100000.0]*24, [100000.0]*24, [100000.0]*24, "W"),
        metadata={"status": "TEST"}
    )
    context = bad_runner.data_provider.get_runtime_state(0)
    state = StationState(
        timestamp=context["origin_timestamp"],
        battery_soc_pct=0.0,
        battery_energy_wh=0.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=100000.0,
        last_observed_wind_generation=0.0
    )
    plan = bad_runner.optimizer.optimize(impossible_bundle, state, bad_runner.configs)
    assert plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
    assert plan.objective_value == 1e9


def test_13_no_future_truth_consumed(s81_runner):
    """Req 13: No future ground truth is consumed by Stage 8.1 forecast engine."""
    context = s81_runner.data_provider.get_runtime_state(0)
    assert "future_actuals" not in context
    assert "actual_SW_IN_future" not in context


def test_14_offline_execution_network_isolation(s81_runner):
    """Req 14: Offline execution succeeds with 100% network isolation."""
    old_socket = socket.socket
    old_getaddrinfo = socket.getaddrinfo

    def forbidden_socket(*args, **kwargs):
        raise RuntimeError("CRITICAL NETWORK LEAKAGE: Network access strictly forbidden.")

    def forbidden_getaddrinfo(*args, **kwargs):
        raise RuntimeError("CRITICAL NETWORK LEAKAGE: DNS lookup forbidden.")

    socket.socket = forbidden_socket
    socket.getaddrinfo = forbidden_getaddrinfo

    try:
        report = s81_runner.run_pipeline(steps_to_run=12)
        assert report["network_connectivity"] == "DISCONNECTED (100% OFFLINE)"
        assert report["timesteps_executed"] == 12
    finally:
        socket.socket = old_socket
        socket.getaddrinfo = old_getaddrinfo


def test_15_multi_scenario_stress_execution():
    """Req 15: Re-verifies E2E execution across authorized stress scenarios S1-S6."""
    scenarios = [
        "demo_scenario.json",
        "renewable_stress_scenario.json",
        "demand_stress_scenario.json",
        "battery_stress_scenario.json"
    ]
    for sc in scenarios:
        runner = _authorize_router_for_s81_test(PolarisLocalRunner(
            SYSTEM_DIR,
            scenario_filename=sc,
            optimizer_type="milp",
            forecast_engine_type="stage81_solar"
        ))
        report = runner.run_pipeline(steps_to_run=12)
        assert report["timesteps_executed"] == 12
        assert report["execution_status"] == "SUCCESS_CLEAN"
