import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.control.ecd import EmergencyAssessment, OperatingMode, ResourceSelection, ValidityStatus

_BATTERY_CFG = {
    "capacity_wh": 200000.0,
    "min_soc_pct": 20.0,
    "max_soc_pct": 95.0,
    "max_discharge_power_w": 50000.0,
    "max_charge_power_w": 50000.0,
    "charge_efficiency": 0.92,
    "discharge_efficiency": 0.92,
}

_DIESEL_CFG = {
    "min_power_w": 10000.0,
    "max_power_w": 100000.0,
    "initial_fuel_l": 100.0,
    "base_fuel_consumption_l_per_h": 5.0,
    "marginal_fuel_consumption_l_per_wh": 0.00025,
}

_CONFIGS = {
    "battery": _BATTERY_CFG,
    "diesel": _DIESEL_CFG,
}

def _make_test_bundle(solar_w: float, wind_w: float, demand_w: float) -> ForecastBundle:
    ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=ts[0],
        horizon_hours=24,
        timestamps=ts,
        solar_irradiance=TimeseriesForecast([500.0] * 24, [500.0] * 24, [500.0] * 24, "W/m^2"),
        solar_generation=TimeseriesForecast([solar_w] * 24, [solar_w] * 24, [solar_w] * 24, "W"),
        wind_generation=TimeseriesForecast([wind_w] * 24, [wind_w] * 24, [wind_w] * 24, "W"),
        demand=TimeseriesForecast([demand_w] * 24, [demand_w] * 24, [demand_w] * 24, "W"),
        metadata={},
    )

def _make_test_assessment(preserved: ResourceSelection = ResourceSelection.BOTH) -> EmergencyAssessment:
    return EmergencyAssessment(
        operating_mode=OperatingMode.EMERGENCY,
        battery_endurance_hours=10.0,
        diesel_endurance_hours=10.0,
        battery_margin_hours=1.0,
        diesel_margin_hours=1.0,
        preserved_resource=preserved,
        limiting_resource=preserved,
        tie_status=False,
        validity_status=ValidityStatus.VALID,
    )

def _make_test_state(battery_energy_wh: float, demand0: float, fuel_l: float = 100.0) -> StationState:
    return StationState(
        timestamp="2024-06-01T00:00:00Z",
        battery_soc_pct=(battery_energy_wh / _BATTERY_CFG["capacity_wh"]) * 100.0,
        battery_energy_wh=battery_energy_wh,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=500.0,
        last_observed_demand=demand0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=fuel_l,
    )

@pytest.mark.parametrize("scenario_name, preserved, solar_w, wind_w, demand_w, soc_pct, expected_diesel_w, expected_dis_w, expected_chg_w", [
    (
        "Boundary 1: Low Residual Demand, Full Battery, Guard Triggers (BOTH)",
        ResourceSelection.BOTH, 0.0, 0.0, 4000.0, 95.0,
        0.0, 4000.0, 0.0
    ),
    (
        "Boundary 2: Low Residual Demand, Half Battery (Charges Surplus)",
        ResourceSelection.BOTH, 0.0, 0.0, 4000.0, 50.0,
        10000.0, 0.0, 6000.0
    ),
    (
        "Boundary 3: Residual Demand Matches Diesel Min (10 kW)",
        ResourceSelection.BOTH, 0.0, 0.0, 10000.0, 95.0,
        10000.0, 0.0, 0.0
    ),
    (
        "Boundary 4: Residual Demand Exceeds Diesel Min (14 kW Co-dispatch)",
        ResourceSelection.BOTH, 0.0, 0.0, 14000.0, 80.0,
        10000.0, 4000.0, 0.0
    ),
    (
        "Boundary 5: Renewable Generation Exceeds Demand (P_rem = 0)",
        ResourceSelection.BOTH, 5000.0, 0.0, 4000.0, 50.0,
        0.0, 0.0, 1000.0
    ),
    (
        "Boundary 6: Preserved Resource BATTERY (Always Routes to Battery First)",
        ResourceSelection.BATTERY, 0.0, 0.0, 4000.0, 95.0,
        0.0, 4000.0, 0.0
    ),
])
def test_patched_option_d_boundary_power_balance(
    scenario_name, preserved, solar_w, wind_w, demand_w, soc_pct,
    expected_diesel_w, expected_dis_w, expected_chg_w
):
    """Verifies that OptionDFallbackSolver satisfies bus-bar balance (< 1e-3 W)
    and executes the expected physical dispatch across all boundary combinations.
    """
    solver = OptionDFallbackSolver()
    assessment = _make_test_assessment(preserved=preserved)
    bundle = _make_test_bundle(solar_w=solar_w, wind_w=wind_w, demand_w=demand_w)
    state = _make_test_state(battery_energy_wh=200000.0 * (soc_pct / 100.0), demand0=demand_w)

    plan = solver.solve(assessment, bundle, state, _CONFIGS)

    gen = plan.solar_used[0] + plan.wind_used[0] + plan.diesel_power[0] + plan.battery_discharge[0]
    load = plan.load_served[0] + plan.flexible_load_schedule[0] + plan.battery_charge[0]
    bus_err = abs(gen - load)

    assert bus_err < 1e-3, (
        f"{scenario_name}: Bus-bar imbalance of {bus_err:.4f} W exceeded tolerance (1e-3 W). "
        f"Gen={gen} W, Load={load} W"
    )
    assert abs(plan.diesel_power[0] - expected_diesel_w) < 1e-3, (
        f"{scenario_name}: Diesel power {plan.diesel_power[0]} != expected {expected_diesel_w}"
    )
    assert abs(plan.battery_discharge[0] - expected_dis_w) < 1e-3, (
        f"{scenario_name}: Battery discharge {plan.battery_discharge[0]} != expected {expected_dis_w}"
    )
    assert abs(plan.battery_charge[0] - expected_chg_w) < 1e-3, (
        f"{scenario_name}: Battery charge {plan.battery_charge[0]} != expected {expected_chg_w}"
    )
