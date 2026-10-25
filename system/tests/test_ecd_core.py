"""
POLARIS Energy Management System (EMS)
Emergency Condition Detector (ECD) Isolated Core Unit Test Suite

Verifies:
1. 100% Independent reproduction of 5 Canonical Synthetic Fixture cases.
2. E3 resource preservation semantics & tie handling.
3. Fail-closed safety boundary (UNKNOWN_INVALID for missing/invalid inputs).
4. Time-varying critical load integration (BLK-010).
5. 100% Deterministic execution across repeated runs.
"""

import json
import os
import math
import pytest
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    BatteryParameters,
    DieselParameters,
    ECDConfig,
    OperatingMode,
    ResourceSelection,
    ValidityStatus,
    ConstantCriticalLoad,
    TimeSeriesCriticalLoad
)

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../ems/ecd/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json"
)


@pytest.fixture
def canonical_fixture():
    with open(FIXTURE_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def ecd_evaluator():
    return EmergencyConditionDetector(ECDConfig())


def test_canonical_fixture_reproduction(ecd_evaluator, canonical_fixture):
    """Verify exact reproduction of the 5 canonical synthetic fixture cases."""
    component_params = canonical_fixture["component_parameters"]

    bat_params = BatteryParameters(
        capacity_wh=component_params["battery"]["capacity_wh"],
        min_soc_pct=component_params["battery"]["min_soc_pct"],
        max_soc_pct=component_params["battery"]["max_soc_pct"],
        discharge_efficiency=component_params["battery"]["discharge_efficiency"],
        max_discharge_power_w=component_params["battery"]["max_discharge_power_w"]
    )

    dsl_params = DieselParameters(
        base_fuel_consumption_l_per_h=component_params["diesel"]["base_fuel_consumption_l_per_h"],
        marginal_fuel_consumption_l_per_wh=component_params["diesel"]["marginal_fuel_consumption_l_per_wh"],
        min_power_w=component_params["diesel"]["min_power_w"],
        max_power_w=component_params["diesel"]["max_power_w"],
        physical_startup_fuel_l=component_params["diesel"].get("physical_startup_fuel_l", 0.0)
    )

    test_cases = canonical_fixture["test_cases"]
    assert len(test_cases) == 5

    for case in test_cases:
        inputs = case["predeclared_inputs"]
        expected = case["analytical_outputs"]

        auth_horizon = AuthorizedHorizon(t_required_hours=inputs["T_test_hours"])

        assessment = ecd_evaluator.evaluate(
            horizon_input=auth_horizon,
            critical_load=inputs["critical_load_w"],
            soc_pct=inputs["soc_pct"],
            fuel_remaining_liters=inputs["fuel_remaining_liters"],
            battery_params=bat_params,
            diesel_params=dsl_params
        )

        # Assert validity
        assert assessment.validity_status == ValidityStatus.VALID, f"Case {case['case_id']} failed validity check"

        # Assert Operating Mode
        assert assessment.operating_mode.value == expected["expected_mode"], (
            f"Case {case['case_id']} mode mismatch: expected {expected['expected_mode']}, got {assessment.operating_mode.value}"
        )

        # Assert Endurances within float tolerance (1e-5 hours)
        assert math.isclose(assessment.battery_endurance_hours, expected["T_battery_hours"], abs_tol=1e-5), (
            f"Case {case['case_id']} T_battery mismatch: expected {expected['T_battery_hours']}, got {assessment.battery_endurance_hours}"
        )
        assert math.isclose(assessment.diesel_endurance_hours, expected["T_diesel_hours"], abs_tol=1e-5), (
            f"Case {case['case_id']} T_diesel mismatch: expected {expected['T_diesel_hours']}, got {assessment.diesel_endurance_hours}"
        )

        # Assert Margins
        assert math.isclose(assessment.battery_margin_hours, expected["M_battery_hours"], abs_tol=1e-5)
        assert math.isclose(assessment.diesel_margin_hours, expected["M_diesel_hours"], abs_tol=1e-5)

        # Assert Resource Preservation
        assert assessment.preserved_resource.value == expected["preserved_resource"], (
            f"Case {case['case_id']} preserved_resource mismatch: expected {expected['preserved_resource']}, got {assessment.preserved_resource.value}"
        )
        assert assessment.limiting_resource.value == expected["limiting_resource"], (
            f"Case {case['case_id']} limiting_resource mismatch: expected {expected['limiting_resource']}, got {assessment.limiting_resource.value}"
        )


def test_missing_and_invalid_t_required(ecd_evaluator, canonical_fixture):
    """Verify fail-closed behavior for missing, invalid, expired, or unauthorized T_required."""
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)

    # Missing T_required
    auth_missing = AuthorizedHorizon(t_required_hours=None)
    assessment = ecd_evaluator.evaluate(auth_missing, 30000.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID
    assert assessment.validity_status == ValidityStatus.MISSING_T_REQUIRED

    # Invalid T_required <= 0
    auth_zero = AuthorizedHorizon(t_required_hours=0.0)
    assessment = ecd_evaluator.evaluate(auth_zero, 30000.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID

    # NaN T_required
    auth_nan = AuthorizedHorizon(t_required_hours=float('nan'))
    assessment = ecd_evaluator.evaluate(auth_nan, 30000.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID

    # Expired T_required
    auth_expired = AuthorizedHorizon(t_required_hours=2.0, expires_at=100.0, current_time=105.0)
    assessment = ecd_evaluator.evaluate(auth_expired, 30000.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID
    assert assessment.validity_status == ValidityStatus.EXPIRED_T_REQUIRED

    # Unauthorized T_required
    auth_unauth = AuthorizedHorizon(t_required_hours=2.0, is_authorized=False)
    assessment = ecd_evaluator.evaluate(auth_unauth, 30000.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID
    assert assessment.validity_status == ValidityStatus.UNAUTHORIZED_T_REQUIRED


def test_invalid_telemetry_and_critical_load(ecd_evaluator):
    """Verify fail-closed behavior for invalid SOC, fuel, or critical load values."""
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)
    auth = AuthorizedHorizon(2.0)

    # Invalid SOC (> 100%)
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 105.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID
    assert assessment.validity_status == ValidityStatus.INVALID_TELEMETRY

    # Negative fuel
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 80.0, -10.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID

    # Invalid critical load <= 0
    assessment = ecd_evaluator.evaluate(auth, 0.0, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.operating_mode == OperatingMode.UNKNOWN_INVALID
    assert assessment.validity_status == ValidityStatus.INVALID_CRITICAL_LOAD


def test_boundary_state_conditions(ecd_evaluator):
    """Verify physical boundary state behavior (SOC at min, zero fuel, SOC at 100%)."""
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)
    auth = AuthorizedHorizon(2.0)

    # SOC at min (20%) -> Usable battery energy = 0
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 20.0, 50.0, bat_params, dsl_params)
    assert assessment.validity_status == ValidityStatus.VALID
    assert assessment.battery_endurance_hours == 0.0
    assert assessment.operating_mode == OperatingMode.EMERGENCY
    assert assessment.limiting_resource == ResourceSelection.BATTERY

    # Fuel = 0 -> Diesel endurance = 0
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 80.0, 0.0, bat_params, dsl_params)
    assert assessment.validity_status == ValidityStatus.VALID
    assert assessment.diesel_endurance_hours == 0.0
    assert assessment.operating_mode == OperatingMode.EMERGENCY
    assert assessment.limiting_resource == ResourceSelection.DIESEL

    # Maximum SOC (100%) -> Usable battery energy = (100 - 20)/100 * 200000 * 0.92 = 147200 Wh -> 4.906667 h
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 100.0, 50.0, bat_params, dsl_params)
    assert assessment.validity_status == ValidityStatus.VALID
    assert math.isclose(assessment.battery_endurance_hours, 147200.0 / 30000.0, abs_tol=1e-5)


def test_tie_epsilon_behavior(ecd_evaluator):
    """Verify floating-point tie detection under BLK-009 epsilon boundary."""
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)
    auth = AuthorizedHorizon(2.0)

    # Case 5: Fuel = 46.0 L -> T_diesel = 46 / 12.5 = 3.68 h; T_battery = 3.68 h
    assessment = ecd_evaluator.evaluate(auth, 30000.0, 80.0, 46.0, bat_params, dsl_params)
    assert assessment.tie_status is True
    assert assessment.preserved_resource == ResourceSelection.BOTH

    # Slightly perturb fuel by 0.1 L -> T_diesel = 46.1 / 12.5 = 3.688 h != 3.68 h -> Not a tie
    assessment_no_tie = ecd_evaluator.evaluate(auth, 30000.0, 80.0, 46.1, bat_params, dsl_params)
    assert assessment_no_tie.tie_status is False


def test_time_varying_critical_load_trajectory(ecd_evaluator):
    """Verify BLK-010 time-varying critical load trajectory integration."""
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)
    auth = AuthorizedHorizon(2.0)

    # Time-varying load vector: [20000, 40000, 30000] W over 1-hour steps
    time_varying_traj = TimeSeriesCriticalLoad([20000.0, 40000.0, 30000.0], step_hours=1.0)

    # Usable AC energy for 80% SOC = 110,400 Wh
    # Hour 1 (20kW): 20,000 Wh (accumulated = 20,000 Wh)
    # Hour 2 (40kW): 40,000 Wh (accumulated = 60,000 Wh)
    # Hour 3 (30kW): 30,000 Wh (accumulated = 90,000 Wh)
    # Remaining needed: 110,400 - 90,000 = 20,400 Wh at 30kW -> 20.4 / 30 = 0.68 h
    # Expected T_battery = 3 + 0.68 = 3.68 h
    assessment = ecd_evaluator.evaluate(auth, time_varying_traj, 80.0, 50.0, bat_params, dsl_params)
    assert assessment.validity_status == ValidityStatus.VALID
    assert math.isclose(assessment.battery_endurance_hours, 3.68, abs_tol=1e-5)


def test_deterministic_reproducibility(ecd_evaluator, canonical_fixture):
    """Verify 100% deterministic, side-effect-free repeated execution over 100 iterations."""
    component_params = canonical_fixture["component_parameters"]
    bat_params = BatteryParameters(200000.0, 20.0, 95.0, 0.92, 50000.0)
    dsl_params = DieselParameters(5.0, 0.00025, 10000.0, 100000.0)
    auth = AuthorizedHorizon(2.0)

    initial_assessment = ecd_evaluator.evaluate(auth, 30000.0, 80.0, 50.0, bat_params, dsl_params)

    for _ in range(100):
        repeat_assessment = ecd_evaluator.evaluate(auth, 30000.0, 80.0, 50.0, bat_params, dsl_params)
        assert repeat_assessment == initial_assessment
