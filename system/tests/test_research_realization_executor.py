"""
Unit and Integration Tests for ResearchRealizationExecutor
Covers Requirements A through N:
- Test A: Exact energy balance/accounting (P_in == P_out, zero residual)
- Test B: Solar shortfall produces unmet load when supply is insufficient
- Test C: Excess solar produces curtailment when storage/load cannot absorb it
- Test D: Battery charge efficiency (delta_E = p_chg * eta_chg)
- Test E: Battery discharge efficiency (delta_E = p_dis / eta_dis)
- Test F: SOC floor protection (cannot discharge below 20% SOC)
- Test G: SOC ceiling protection (cannot charge above 95% SOC)
- Test H: Diesel fuel consumption & state transition
- Test I: Zero-solar case (night / polar night)
- Test J: Zero-wind case (calm weather)
- Test K: Causal firewall separation (actual observations on realization side only)
- Test L: Deterministic repeatability
- Test M: Next StationState validity & contract adherence
- Test N: Production simulator unmodified
- Smoke Test: Causal NWP forecaster -> GAP19 -> ResearchRealizationExecutor -> next StationState
"""

import math
import subprocess
from pathlib import Path
import pytest
import pandas as pd

from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.simulation.research_realization_executor import (
    ResearchRealizationExecutor,
    RealizationResult
)
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer


@pytest.fixture
def default_configs():
    return {
        "battery": {
            "capacity_wh": 200000.0,
            "min_soc_pct": 20.0,
            "max_soc_pct": 95.0,
            "charge_efficiency": 0.92,
            "discharge_efficiency": 0.92,
            "max_charge_power_w": 50000.0,
            "max_discharge_power_w": 50000.0,
            "initial_soc_pct": 50.0
        },
        "diesel": {
            "min_power_w": 10000.0,
            "max_power_w": 100000.0,
            "base_fuel_consumption_l_per_h": 5.0,
            "marginal_fuel_consumption_l_per_wh": 0.00025,
            "initial_fuel_l": 100.0
        },
        "solar_pv": {
            "array_area_m2": 300.0,
            "panel_efficiency": 0.20,
            "performance_ratio": 0.85,
            "max_inverter_power_w": 60000.0
        }
    }


def make_plan(battery_charge=0.0, battery_discharge=0.0, diesel_power=0.0):
    timestamps = [f"2024-06-22T{h:02d}:00:00Z" for h in range(24)]
    return DispatchPlan(
        schema_version="1.0.0",
        timestamps=timestamps,
        solar_used=[0.0] * 24,
        wind_used=[0.0] * 24,
        battery_charge=[battery_charge] * 24,
        battery_discharge=[battery_discharge] * 24,
        battery_soc=[50.0] * 24,
        diesel_power=[diesel_power] * 24,
        load_served=[15000.0] * 24,
        flexible_load_schedule=[0.0] * 24,
        renewable_curtailment=[0.0] * 24,
        unmet_load=[0.0] * 24,
        objective_value=0.0,
        constraint_status="OPTIMAL",
        energy_balance_errors=[0.0] * 24
    )


def test_a_exact_energy_balance_accounting(default_configs):
    """Test A: Exact busbar energy balance (P_in == P_out, demand == served + unmet)."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=5000.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan(battery_charge=5000.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 400.0,  # 400 * 51 = 20,400 W
        "actual_wind_generation": 4000.0,
        "actual_demand": 15000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Busbar balance: P_in == P_out
    assert result.busbar_energy_balance_error_w == pytest.approx(0.0, abs=1e-5)
    assert result.solar_realized_w == pytest.approx(20400.0, abs=1e-2)
    assert result.wind_realized_w == 4000.0
    assert result.served_load_w == 15000.0
    assert result.unmet_load_w == 0.0

    # Total supply = 20,400 + 4,000 = 24,400 W. Demand = 15,000 W. Surplus = 9,400 W.
    # Battery charges up to planned 5,000 W or available room.
    assert result.battery_charge_realized_w == pytest.approx(9400.0, abs=1e-2)
    assert result.curtailment_w == pytest.approx(0.0, abs=1e-2)


def test_b_solar_shortfall_produces_unmet_load(default_configs):
    """Test B: Solar shortfall when total supply is insufficient produces unmet load."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=20.0,  # Battery at minimum SOC floor, cannot discharge
        battery_energy_wh=40000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=20000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=0.0  # No diesel
    )
    plan = make_plan(battery_charge=0.0, battery_discharge=10000.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 100.0,  # Realized solar: 100 * 51 = 5,100 W (shortfall vs 20 kW demand)
        "actual_wind_generation": 0.0,
        "actual_demand": 20000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Battery cannot discharge because it is at 20% SOC floor
    assert result.battery_discharge_realized_w == 0.0
    assert result.solar_realized_w == pytest.approx(5100.0, abs=1e-2)
    assert result.served_load_w == pytest.approx(5100.0, abs=1e-2)
    assert result.unmet_load_w == pytest.approx(14900.0, abs=1e-2)
    assert result.curtailment_w == 0.0


def test_c_excess_solar_produces_curtailment(default_configs):
    """Test C: Excess solar produces curtailment when storage cannot absorb it."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=95.0,  # Battery fully charged at max SOC ceiling (95%)
        battery_energy_wh=190000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=5000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan(battery_charge=10000.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 600.0,  # 600 * 51 = 30,600 W solar
        "actual_wind_generation": 0.0,
        "actual_demand": 5000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Battery cannot charge because it is at 95% ceiling (0 room)
    assert result.battery_charge_realized_w == 0.0
    assert result.served_load_w == 5000.0
    assert result.unmet_load_w == 0.0
    assert result.curtailment_w == pytest.approx(25600.0, abs=1e-2)


def test_d_battery_charge_efficiency(default_configs):
    """Test D: Battery charging adds p_chg * eta_chg to battery energy."""
    executor = ResearchRealizationExecutor(default_configs)
    initial_e = 100000.0
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=initial_e,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Solar: 20 kW. Demand: 10 kW. Surplus: 10 kW.
    plan = make_plan(battery_charge=10000.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 20000.0 / 51.0,  # Exactly 20,000 W solar
        "actual_wind_generation": 0.0,
        "actual_demand": 10000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Charge is 10,000 W AC. Added DC energy = 10,000 * 0.92 = 9,200 Wh.
    expected_e = initial_e + 10000.0 * 0.92
    assert result.battery_charge_realized_w == pytest.approx(10000.0, abs=1e-2)
    assert result.realized_battery_energy_wh == pytest.approx(expected_e, abs=1e-2)
    assert result.next_state.battery_energy_wh == pytest.approx(expected_e, abs=1e-2)


def test_e_battery_discharge_efficiency(default_configs):
    """Test E: Battery discharging removes p_dis / eta_dis from battery energy."""
    executor = ResearchRealizationExecutor(default_configs)
    initial_e = 100000.0
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=initial_e,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Zero renewable generation; discharge 10,000 W AC
    plan = make_plan(battery_charge=0.0, battery_discharge=10000.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 0.0,
        "actual_wind_generation": 0.0,
        "actual_demand": 10000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Removed DC energy = 10,000 / 0.92 = 10,869.57 Wh
    expected_e = initial_e - (10000.0 / 0.92)
    assert result.battery_discharge_realized_w == pytest.approx(10000.0, abs=1e-2)
    assert result.realized_battery_energy_wh == pytest.approx(expected_e, abs=1e-2)
    assert result.next_state.battery_energy_wh == pytest.approx(expected_e, abs=1e-2)


def test_f_soc_floor_protection(default_configs):
    """Test F: Battery cannot discharge below min_soc_pct (20% = 40,000 Wh)."""
    executor = ResearchRealizationExecutor(default_configs)
    initial_e = 45000.0  # Only 5,000 Wh DC available above 40,000 Wh floor
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=22.5,
        battery_energy_wh=initial_e,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=20000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Plan requests 20,000 W discharge
    plan = make_plan(battery_charge=0.0, battery_discharge=20000.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 0.0,
        "actual_wind_generation": 0.0,
        "actual_demand": 20000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Max AC discharge allowed: 5,000 Wh * 0.92 = 4,600 W
    assert result.battery_discharge_realized_w == pytest.approx(4600.0, abs=1e-2)
    assert result.realized_battery_energy_wh == pytest.approx(40000.0, abs=1e-2)
    assert result.realized_soc_pct == pytest.approx(20.0, abs=1e-2)
    assert result.unmet_load_w == pytest.approx(20000.0 - 4600.0, abs=1e-2)


def test_g_soc_ceiling_protection(default_configs):
    """Test G: Battery cannot charge above max_soc_pct (95% = 190,000 Wh)."""
    executor = ResearchRealizationExecutor(default_configs)
    initial_e = 185000.0  # Only 5,000 Wh DC room below 190,000 Wh ceiling
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=92.5,
        battery_energy_wh=initial_e,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=5000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Plan requests 20,000 W charge from solar surplus
    plan = make_plan(battery_charge=20000.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 500.0,  # 25,500 W solar - 5,000 W demand = 20,500 W surplus
        "actual_wind_generation": 0.0,
        "actual_demand": 5000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Max AC charge room: 5,000 / 0.92 = 5,434.78 W
    assert result.battery_charge_realized_w == pytest.approx(5000.0 / 0.92, abs=1e-2)
    assert result.realized_battery_energy_wh == pytest.approx(190000.0, abs=1e-2)
    assert result.realized_soc_pct == pytest.approx(95.0, abs=1e-2)
    # Remainder is curtailed
    expected_curtail = 20500.0 - (5000.0 / 0.92)
    assert result.curtailment_w == pytest.approx(expected_curtail, abs=1e-2)


def test_h_diesel_fuel_and_state_transition(default_configs):
    """Test H: Diesel generator consumes fuel (base + marginal * P) and transitions hours."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=20000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Dispatch 20,000 W diesel
    plan = make_plan(battery_charge=0.0, battery_discharge=0.0, diesel_power=20000.0)
    realized = {
        "actual_SW_IN": 0.0,
        "actual_wind_generation": 0.0,
        "actual_demand": 20000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    # Fuel consumption: 5.0 L/h base + 0.00025 L/Wh * 20,000 W = 5.0 + 5.0 = 10.0 L
    assert result.diesel_realized_w == 20000.0
    assert result.diesel_fuel_consumed_l == pytest.approx(10.0, abs=1e-4)
    assert result.diesel_fuel_remaining_l == pytest.approx(90.0, abs=1e-4)
    assert result.diesel_running is True
    assert result.diesel_hours_running == 1.0
    assert result.next_state.diesel_running is True
    assert result.next_state.diesel_hours_running == 1.0


def test_i_zero_solar_case(default_configs):
    """Test I: Zero solar irradiance executes cleanly."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=10000.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan(battery_charge=0.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 0.0,
        "actual_wind_generation": 10000.0,
        "actual_demand": 10000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    assert result.solar_realized_w == 0.0
    assert result.served_load_w == 10000.0
    assert result.unmet_load_w == 0.0
    assert result.busbar_energy_balance_error_w == pytest.approx(0.0, abs=1e-5)


def test_j_zero_wind_case(default_configs):
    """Test J: Zero wind generation executes cleanly."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan(battery_charge=0.0, battery_discharge=0.0, diesel_power=0.0)
    realized = {
        "actual_SW_IN": 10000.0 / 51.0,
        "actual_wind_generation": 0.0,
        "actual_demand": 10000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    result = executor.execute_step(state, plan, realized)

    assert result.wind_realized_w == 0.0
    assert result.served_load_w == pytest.approx(10000.0, abs=1e-2)
    assert result.unmet_load_w == 0.0
    assert result.busbar_energy_balance_error_w == pytest.approx(0.0, abs=1e-5)


def test_k_actual_observations_remain_on_realization_side_only(default_configs):
    """Test K: Forecast engine strictly rejects actual observations; executor processes them."""
    forecast_engine = CausalNwpPhysicsForecastEngine()
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=5000.0,
        diesel_fuel_remaining_liters=100.0
    )
    # Passing actuals to forecast engine fails closed
    with pytest.raises(PermissionError, match="Causal firewall violation"):
        forecast_engine.predict(state, {"fc_cloud_cover": [50.0]*24, "actual_SW_IN": [100.0]*24})

    # But passing actuals to the realization executor succeeds
    plan = make_plan()
    result = executor.execute_step(state, plan, {
        "actual_SW_IN": 100.0,
        "actual_wind_generation": 5000.0,
        "actual_demand": 10000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    })
    assert isinstance(result, RealizationResult)


def test_l_deterministic_repeatability(default_configs):
    """Test L: Repeated executions return bitwise identical results."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=60.0,
        battery_energy_wh=120000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=12000.0,
        last_observed_wind_generation=4000.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan(battery_charge=3000.0, battery_discharge=0.0, diesel_power=5000.0)
    realized = {
        "actual_SW_IN": 250.0,
        "actual_wind_generation": 3500.0,
        "actual_demand": 14000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    }
    res1 = executor.execute_step(state, plan, realized)
    res2 = executor.execute_step(state, plan, realized)

    assert res1.to_dict() == res2.to_dict()


def test_m_next_station_state_is_valid(default_configs):
    """Test M: Next StationState instance is fully formed and schema-compliant."""
    executor = ResearchRealizationExecutor(default_configs)
    state = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=5000.0,
        diesel_fuel_remaining_liters=100.0
    )
    plan = make_plan()
    result = executor.execute_step(state, plan, {
        "actual_SW_IN": 300.0,
        "actual_wind_generation": 4000.0,
        "actual_demand": 12000.0,
        "timestamp": "2024-06-22T00:00:00Z"
    })
    next_s = result.next_state
    assert isinstance(next_s, StationState)
    assert next_s.timestamp == "2024-06-22T00:00:00Z"
    assert 20.0 <= next_s.battery_soc_pct <= 95.0
    assert 40000.0 <= next_s.battery_energy_wh <= 190000.0
    assert next_s.last_observed_solar_irradiance == 300.0
    assert next_s.last_observed_demand == 12000.0
    assert next_s.last_observed_wind_generation == 4000.0


def test_n_production_simulator_unmodified():
    """Test N: system/simulation/simulator.py is not modified."""
    sim_path = Path("system/simulation/simulator.py")
    assert sim_path.exists()
    diff = subprocess.check_output(["git", "diff", "--", str(sim_path)]).decode("utf-8")
    assert diff.strip() == "", "system/simulation/simulator.py was modified!"


def test_smoke_forecast_to_gap19_to_realization(default_configs):
    """Smoke test: Causal NWP forecaster -> GAP19 -> ResearchRealizationExecutor -> next StationState."""
    df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    sub = df[df["forecast_start"] == "2024-06-22 00:00:00"].copy()
    assert len(sub) == 24

    cloud_trajectory = sub["fc_cloud_cover"].tolist()
    realized_sw_in = float(sub["actual_SW_IN"].iloc[0])

    state_t0 = StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0,
        operating_mode="NORMAL"
    )

    # 1. Forecast side (strictly firewalled, MEPS only)
    engine = CausalNwpPhysicsForecastEngine()
    bundle = engine.predict(state_t0, {"fc_cloud_cover": cloud_trajectory})
    assert len(bundle.solar_generation.point) == 24

    # 2. Optimization side (GAP19 HiGHS)
    gap19_config = dict(default_configs)
    gap19_config["critical_demand_ratio"] = 0.5
    gap19_config["terminal_target_wh"] = 100000.0
    optimizer = GAP19HighsNativeOptimizer()
    plan = optimizer.optimize(bundle, state_t0, gap19_config)
    assert plan.constraint_status == "OPTIMAL"

    # 3. Realization side (actual solar, wind, demand)
    executor = ResearchRealizationExecutor(default_configs)
    realized_inputs = {
        "timestamp": "2024-06-22T00:00:00Z",
        "actual_SW_IN": realized_sw_in,
        "actual_wind_generation": 4500.0,
        "actual_demand": 15000.0
    }
    result = executor.execute_step(state_t0, plan, realized_inputs)

    assert result.busbar_energy_balance_error_w == pytest.approx(0.0, abs=1e-5)
    assert result.solar_realized_w == pytest.approx(realized_sw_in * 51.0, abs=1e-2)
    assert result.next_state.timestamp == "2024-06-22T00:00:00Z"
    assert 20.0 <= result.realized_soc_pct <= 95.0
    assert result.next_state.last_observed_solar_irradiance == pytest.approx(realized_sw_in, abs=1e-4)
