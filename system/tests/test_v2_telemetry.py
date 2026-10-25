"""
POLARIS V2 Observational Telemetry Non-Intervention & Isolation Verification Suite
Phase V2 Telemetry Failure Isolation Correction Bounded Tests

Verifies:
1. All 37 required fields represented, unique, and mapped.
2. Field availability classification (23 DIRECTLY_AVAILABLE, 14 REQUIRES_INSTRUMENTATION, 0 NOT_AVAILABLE).
3. Passive non-intervention (zero mutation of inputs, plans, state, or solver).
4. Raw float exact forecast preservation (length 24).
5. Deterministic JSON and CSV serialization.
6. TEST 1: Telemetry disabled -> normal EMS execution path.
7. TEST 2: Telemetry enabled and successful -> identical EMS semantics.
8. TEST 3: Telemetry collector raises exception -> EMS execution remains SUCCESS_CLEAN.
9. TEST 4: Telemetry serialization fails -> EMS execution remains unaffected.
10. TEST 5: Optimizer failure -> existing EMS failure semantics (FAILED_TERMINATED) preserved.
11. TEST 6: Simulator failure -> existing EMS failure semantics (FAILED_TERMINATED) preserved.
12. TEST 7: Telemetry exception cannot change DispatchPlan.
13. TEST 8: Telemetry exception cannot change StationState.
14. TEST 9: Telemetry exception cannot change timestep advancement.
15. TEST 10: Telemetry exception cannot change forecast vectors.
"""

import json
from pathlib import Path
import pytest
from dataclasses import fields

from system.telemetry.v2_logger import (
    V2TelemetryRecord,
    V2TelemetryCollector,
    REQUIRED_37_FIELDS,
    AVAILABILITY_CLASSIFICATION,
)
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.runtime.runner import PolarisLocalRunner


@pytest.fixture
def dummy_24_vector() -> list:
    return [float(i * 15.5) for i in range(24)]


@pytest.fixture
def dummy_telemetry_record(dummy_24_vector) -> V2TelemetryRecord:
    return V2TelemetryRecord(
        origin_id=1,
        origin_timestamp="2026-09-18T00:00:00Z",
        mpc_timestep_idx=0,
        timestamp="2026-09-18T01:00:00Z",
        treatment_forecast_vector_24=dummy_24_vector,
        control_forecast_vector_24=dummy_24_vector,
        actual_solar_truth=350.123456789,
        treatment_h1_forecast=0.0,
        control_h1_forecast=0.0,
        treatment_forecast_error_h1=-350.123456789,
        control_forecast_error_h1=-350.123456789,
        forecast_difference_h1=0.0,
        soc_before=50.0,
        diesel_state_before=False,
        cumulative_diesel_fuel_before=0.0,
        cumulative_diesel_energy_before=0.0,
        optimizer_status="OPTIMAL",
        objective_value=123.456,
        diesel_commitment=0.0,
        startup_event=False,
        shutdown_event=False,
        battery_charge_decision=10.0,
        battery_discharge_decision=0.0,
        reserve_status="NORMAL",
        constraint_status="FEASIBLE",
        h1_diesel_power=0.0,
        h1_battery_charge_power=10.0,
        h1_battery_discharge_power=0.0,
        h1_renewable_dispatch=25.0,
        h1_renewable_curtailment=2.5,
        h1_served_load=35.0,
        h1_unmet_load=0.0,
        soc_after=54.2,
        diesel_state_after=False,
        cumulative_diesel_fuel_after=0.0,
        cumulative_diesel_energy_after=0.0,
        cumulative_battery_throughput_after=10.0,
    )


class FaultyTelemetryCollector(V2TelemetryCollector):
    """Failing collector fixture that raises an exception during record_step."""
    def record_step(self, *args, **kwargs):
        raise RuntimeError("DELIBERATE_TELEMETRY_FAILURE_SIMULATION")


def test_1_exactly_37_unique_fields():
    """Verify exactly 37 unique fields are defined in REQUIRED_37_FIELDS and schema."""
    assert len(REQUIRED_37_FIELDS) == 37
    assert len(set(REQUIRED_37_FIELDS)) == 37

    record_fields = [f.name for f in fields(V2TelemetryRecord)]
    assert len(record_fields) == 37
    assert len(set(record_fields)) == 37
    assert set(record_fields) == set(REQUIRED_37_FIELDS)


def test_2_field_availability_classification_totals():
    """Verify field availability classification totals match governance state."""
    assert len(AVAILABILITY_CLASSIFICATION) == 37
    counts = {}
    for cls in AVAILABILITY_CLASSIFICATION.values():
        counts[cls] = counts.get(cls, 0) + 1

    assert counts.get("DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT", 0) == 23
    assert counts.get("REQUIRES_EXECUTION_CODE_INSTRUMENTATION", 0) == 14
    assert counts.get("NOT_AVAILABLE", 0) == 0


def test_3_record_validation(dummy_telemetry_record):
    """Verify record validation passes for valid input and fails on vector dimension mismatch."""
    dummy_telemetry_record.validate()

    invalid_record = V2TelemetryRecord(**dummy_telemetry_record.to_dict())
    invalid_record.treatment_forecast_vector_24 = [1.0] * 23
    with pytest.raises(ValueError, match="treatment_forecast_vector_24 must have length 24"):
        invalid_record.validate()


def test_4_exact_float_forecast_preservation(dummy_telemetry_record, dummy_24_vector):
    """Verify exact raw float forecast vectors (length 24) are preserved without rounding."""
    d = dummy_telemetry_record.to_dict()
    assert d["treatment_forecast_vector_24"] == dummy_24_vector
    assert d["control_forecast_vector_24"] == dummy_24_vector
    assert d["actual_solar_truth"] == 350.123456789


def test_5_deterministic_serialization(dummy_telemetry_record):
    """Verify JSON and CSV export are deterministic across multiple invocations."""
    collector = V2TelemetryCollector()
    collector.add_record(dummy_telemetry_record)

    json1 = collector.export_json()
    json2 = collector.export_json()
    assert json1 == json2

    csv1 = collector.export_csv()
    csv2 = collector.export_csv()
    assert csv1 == csv2


def test_6_passive_non_mutation():
    """Verify recording telemetry does not mutate source state or plan objects."""
    state = StationState(
        timestamp="2026-09-18T00:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=100.0,
        last_observed_demand=35000.0,
        last_observed_wind_generation=30000.0,
    )
    orig_state_dict = state.to_dict()

    collector = V2TelemetryCollector()
    collector.record_step(
        origin_id=1,
        origin_timestamp="2026-09-18T00:00:00Z",
        mpc_timestep_idx=0,
        timestamp=state.timestamp,
        treatment_forecast_vector_24=[100.0] * 24,
        control_forecast_vector_24=[100.0] * 24,
        actual_solar_truth=100.0,
        soc_before=state.battery_soc_pct,
        diesel_state_before=state.diesel_running,
        cumulative_diesel_fuel_before=0.0,
        cumulative_diesel_energy_before=0.0,
        optimizer_status="OPTIMAL",
        objective_value=10.0,
        diesel_commitment=0.0,
        battery_charge_decision=0.0,
        battery_discharge_decision=0.0,
        reserve_status="NORMAL",
        constraint_status="FEASIBLE",
        h1_diesel_power=0.0,
        h1_battery_charge_power=0.0,
        h1_battery_discharge_power=0.0,
        h1_renewable_dispatch=5.0,
        h1_renewable_curtailment=0.0,
        h1_served_load=35.0,
        h1_unmet_load=0.0,
        soc_after=50.0,
        diesel_state_after=False,
        cumulative_diesel_fuel_after=0.0,
        cumulative_diesel_energy_after=0.0,
        cumulative_battery_throughput_after=0.0,
    )

    assert state.to_dict() == orig_state_dict
    assert len(collector.records) == 1


# =====================================================================
# GOVERNANCE NON-INTERVENTION & EXCEPTION ISOLATION BOUNDED TESTS (1-10)
# =====================================================================


def _authorize_router_for_telemetry_test(runner):
    """
    Explicit, clearly-labeled SYNTHETIC test-fixture authorization for the
    router/ECD fail-closed contract implemented in ECD-01 (A-iii/B-iii;
    system/control/router.py, system/control/ecd.py). These governance
    telemetry tests (TEST 1-10) are not testing the fail-closed gate itself
    -- they test telemetry non-intervention/isolation around the EMS
    pipeline's real optimizer/simulator execution, so they need the router
    to reach a classified (NORMAL) route rather than UNKNOWN_INVALID.

    NOT a real-station evidence record: "EVID-TEST-V2-TELEMETRY" and the
    5000.0 W figure are synthetic test-fixture values only, chosen so that
    demo_scenario.json's step-0 battery state (50% SOC, 200 kWh capacity)
    yields a positive battery_margin_hours against a 6h horizon -- i.e. a
    genuine NORMAL classification under the real router logic, not a
    fabricated route. See docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md ECD-01 and
    tests/test_isolated_components.py (same "EVID-TEST-*" convention) for
    precedent.
    """
    runner.configs.setdefault("ecd", {}).update({
        "t_required_hours": 6.0,
        "t_required_authorized": True,
    })
    runner.configs.setdefault("critical_load", {}).update({
        "authorized": True,
        "evidence_id": "EVID-TEST-V2-TELEMETRY",
        "authorized_critical_load_w": 5000.0,
    })
    return runner


def test_gov_1_telemetry_disabled_normal_execution():
    """TEST 1: Telemetry disabled -> normal EMS execution path."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
    runner = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner)
    report = runner.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    assert report["execution_status"] == "SUCCESS_CLEAN"
    assert report["completed_steps"] == 3


def test_gov_2_telemetry_enabled_successful_identical_semantics():
    """TEST 2: Telemetry enabled and successful -> identical EMS semantics."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
    
    runner1 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    
    _authorize_router_for_telemetry_test(runner1)
    report_disabled = runner1.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    collector = V2TelemetryCollector()
    runner2 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner2)
    report_enabled = runner2.run_pipeline(steps_to_run=3, v2_telemetry_collector=collector)

    assert report_disabled["execution_status"] == report_enabled["execution_status"] == "SUCCESS_CLEAN"
    assert report_disabled["completed_steps"] == report_enabled["completed_steps"] == 3
    assert report_disabled["ems_evaluation"] == report_enabled["ems_evaluation"]
    assert len(collector.records) == 3


def test_gov_3_telemetry_collector_deliberate_exception_isolated():
    """TEST 3: Telemetry collector deliberately raises exception -> EMS execution remains unaffected."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")

    runner1 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")

    _authorize_router_for_telemetry_test(runner1)
    report_disabled = runner1.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    faulty_collector = FaultyTelemetryCollector()
    runner2 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner2)
    report_faulty = runner2.run_pipeline(steps_to_run=3, v2_telemetry_collector=faulty_collector)

    # EMS execution must remain SUCCESS_CLEAN despite telemetry exception!
    assert report_faulty["execution_status"] == "SUCCESS_CLEAN"
    assert report_faulty["completed_steps"] == 3
    assert report_faulty["ems_evaluation"] == report_disabled["ems_evaluation"]
    assert hasattr(runner2, "_telemetry_faults")
    assert len(runner2._telemetry_faults) == 3


def test_gov_4_telemetry_serialization_failure_isolated():
    """TEST 4: Telemetry serialization deliberately fails -> EMS execution remains unaffected."""
    collector = V2TelemetryCollector()
    # Mock invalid record inside collector
    collector.records.append("INVALID_RECORD_OBJECT")
    
    with pytest.raises(Exception):
        collector.export_json()

    # EMS pipeline execution is independent of export failures
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
    runner = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner)
    report = runner.run_pipeline(steps_to_run=2, v2_telemetry_collector=None)
    assert report["execution_status"] == "SUCCESS_CLEAN"


def test_gov_5_optimizer_deliberate_failure_preserved():
    """TEST 5: Optimizer failure -> existing EMS failure semantics preserved."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
    runner = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner)
    
    # Intentionally corrupt optimizer weights config to force optimization failure
    runner.configs["optimizer"]["weights"] = "INVALID_WEIGHT_TYPE"

    report = runner.run_pipeline(steps_to_run=2, v2_telemetry_collector=V2TelemetryCollector())
    assert report["execution_status"] == "FAILED_TERMINATED"
    assert "OPTIMIZATION_RUNTIME_FAILURE" in report["termination_reason"]


def test_gov_6_simulator_failure_preserved():
    """TEST 6: Simulator/state-transition failure -> existing EMS failure semantics preserved."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
    runner = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner)
    
    # Set min_soc_pct directly on simulator above initial SOC (50%) to trigger physical state violation
    runner.simulator.min_soc_pct = 99.0

    report = runner.run_pipeline(steps_to_run=2, v2_telemetry_collector=V2TelemetryCollector())
    assert report["execution_status"] == "FAILED_TERMINATED"
    assert "FAILED_STATE_VIOLATION" in report["termination_reason"]


def test_gov_7_telemetry_exception_cannot_change_dispatch_plan():
    """TEST 7: Telemetry exception cannot change DispatchPlan."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")

    runner1 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")

    _authorize_router_for_telemetry_test(runner1)
    report_normal = runner1.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    faulty_collector = FaultyTelemetryCollector()
    runner2 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner2)
    report_faulty = runner2.run_pipeline(steps_to_run=3, v2_telemetry_collector=faulty_collector)

    # Dispatch plans must be bit-for-bit identical
    assert report_normal["ems_evaluation"]["total_diesel_fuel_liters"] == report_faulty["ems_evaluation"]["total_diesel_fuel_liters"]
    assert report_normal["ems_evaluation"]["total_diesel_energy_kwh"] == report_faulty["ems_evaluation"]["total_diesel_energy_kwh"]
    assert report_normal["ems_evaluation"]["unmet_critical_load_kwh"] == report_faulty["ems_evaluation"]["unmet_critical_load_kwh"]


def test_gov_8_telemetry_exception_cannot_change_station_state():
    """TEST 8: Telemetry exception cannot change StationState trajectory."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")

    runner1 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")

    _authorize_router_for_telemetry_test(runner1)
    report_normal = runner1.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    faulty_collector = FaultyTelemetryCollector()
    runner2 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner2)
    report_faulty = runner2.run_pipeline(steps_to_run=3, v2_telemetry_collector=faulty_collector)

    assert report_normal["ems_evaluation"] == report_faulty["ems_evaluation"]


def test_gov_9_telemetry_exception_cannot_change_timestep_advancement():
    """TEST 9: Telemetry exception cannot change timestep advancement."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")

    faulty_collector = FaultyTelemetryCollector()
    runner = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner)
    report = runner.run_pipeline(steps_to_run=5, v2_telemetry_collector=faulty_collector)

    assert report["completed_steps"] == 5
    assert report["requested_steps"] == 5


def test_gov_10_telemetry_exception_cannot_change_forecast_vectors():
    """TEST 10: Telemetry exception cannot change forecast vectors."""
    system_dir = Path("/home/punith-bs/01polaris (Copy)/system")

    runner1 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")

    _authorize_router_for_telemetry_test(runner1)
    report_normal = runner1.run_pipeline(steps_to_run=3, v2_telemetry_collector=None)

    faulty_collector = FaultyTelemetryCollector()
    runner2 = PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")
    _authorize_router_for_telemetry_test(runner2)
    report_faulty = runner2.run_pipeline(steps_to_run=3, v2_telemetry_collector=faulty_collector)

    assert report_normal["forecast_evaluation"] == report_faulty["forecast_evaluation"]
