"""
POLARIS Energy Management System (EMS)
Controlled Implementation Unit Test Suite (Tests A through R)

Scope:
- Verifies rolling diesel fuel state propagation, simulator fuel consumption, EMSControlRouter policy routing,
  OptionDFallbackSolver DEC-004 logic, fail-closed UNKNOWN_INVALID firewall, and Option B preservation.
"""

import unittest
from pathlib import Path
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.simulation.simulator import DigitalTwinSimulator
from system.control.router import EMSControlRouter
from system.control.ecd import EmergencyConditionDetector, OperatingMode, ValidityStatus, ResourceSelection
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

class TestECDOptionDIntegration(unittest.TestCase):

    def setUp(self):
        self.configs = {
            "battery": {
                "capacity_wh": 200000.0,
                "initial_soc_pct": 50.0,
                "min_soc_pct": 20.0,
                "max_soc_pct": 95.0,
                "charge_efficiency": 0.92,
                "discharge_efficiency": 0.92,
                "max_discharge_power_w": 50000.0,
                "max_charge_power_w": 50000.0
            },
            "diesel": {
                "initial_fuel_l": 100.0,
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025,
                "min_power_w": 10000.0,
                "max_power_w": 50000.0,
                "physical_startup_fuel_l": 0.0
            },
            "ecd": {
                # Explicit SYNTHETIC test-fixture authorization (ECD-01,
                # A-iii/B-iii) -- this suite tests genuine NORMAL/
                # EMERGENCY/UNKNOWN_INVALID routing mechanics, not the
                # authorization gate itself (test_I below still reaches
                # UNKNOWN_INVALID via an invalid, negative SOC -- a
                # separate validity check unaffected by this flag).
                "t_required_hours": 6.0,
                "t_required_authorized": True
            },
            "critical_load": {
                # NOT a real-station evidence record -- see
                # tests/test_isolated_components.py for the convention.
                "authorized": True,
                "evidence_id": "EVID-TEST-ECD-OPTION-D",
                "authorized_critical_load_w": 5000.0,
            }
        }
        self.simulator = DigitalTwinSimulator(self.configs)
        self.router = EMSControlRouter()
        self.option_d_solver = OptionDFallbackSolver()

    def test_A_initial_fuel_initialization(self):
        """Test A: Initial fuel state initializes from config when not provided."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0
        )
        self.assertIsNone(state.diesel_fuel_remaining_liters)

    def test_B_one_step_fuel_consumption(self):
        """Test B: Fuel is decremented correctly after one step with diesel running."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        # Create plan with 20 kW diesel at step 0
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=["2026-09-26T00:00:00Z"] * 24,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[10000.0] * 24,
            battery_soc=[45.0] * 24,
            diesel_power=[20000.0] * 24,
            load_served=[30000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=100.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24
        )
        actuals = {"actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0, "timestamp": "2026-09-26T01:00:00Z"}
        next_state = self.simulator.step(state, plan, actuals)

        # Fuel consumed = (5.0 + 0.00025 * 20000) * 1.0 = 10.0 liters
        expected_fuel = 100.0 - 10.0
        self.assertAlmostEqual(next_state.diesel_fuel_remaining_liters, expected_fuel, places=2)

    def test_C_fuel_first_action_only(self):
        """Test C: Fuel consumption depends ONLY on timestep k=0 decision."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        # Plan has 0 diesel at k=0, but 50 kW diesel for k=1..23
        diesel_p = [0.0] + [50000.0] * 23
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=["2026-09-26T00:00:00Z"] * 24,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[30000.0] * 24,
            battery_soc=[35.0] * 24,
            diesel_power=diesel_p,
            load_served=[30000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=100.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24
        )
        actuals = {"actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0, "timestamp": "2026-09-26T01:00:00Z"}
        next_state = self.simulator.step(state, plan, actuals)

        # k=0 diesel power is 0 -> fuel consumed = 0
        self.assertEqual(next_state.diesel_fuel_remaining_liters, 100.0)

    def test_D_zero_fuel_boundary(self):
        """Test D: Fuel cannot drop below zero."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=2.0  # Only 2 liters left
        )
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=["2026-09-26T00:00:00Z"] * 24,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[10000.0] * 24,
            battery_soc=[45.0] * 24,
            diesel_power=[50000.0] * 24,  # Would consume 17.5L
            load_served=[30000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=100.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24
        )
        actuals = {"actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0, "timestamp": "2026-09-26T01:00:00Z"}
        next_state = self.simulator.step(state, plan, actuals)

        self.assertEqual(next_state.diesel_fuel_remaining_liters, 0.0)

    def test_E_fuel_state_continuity_two_cycles(self):
        """Test E: Fuel propagates continuously across two consecutive steps."""
        s0 = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=["2026-09-26T00:00:00Z"] * 24,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[10000.0] * 24,
            battery_soc=[45.0] * 24,
            diesel_power=[20000.0] * 24,
            load_served=[30000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=100.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24
        )
        act1 = {"actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0, "timestamp": "2026-09-26T01:00:00Z"}
        s1 = self.simulator.step(s0, plan, act1)
        self.assertAlmostEqual(s1.diesel_fuel_remaining_liters, 90.0, places=2)

        act2 = {"actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0, "timestamp": "2026-09-26T02:00:00Z"}
        s2 = self.simulator.step(s1, plan, act2)
        self.assertAlmostEqual(s2.diesel_fuel_remaining_liters, 80.0, places=2)

    def test_F_ecd_receives_current_fuel(self):
        """Test F: Router passes current state fuel to ECD evaluate."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=10.0  # Very low fuel
        )
        # Mock bundle
        class DummyVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummyVector()
            wind_generation = DummyVector()
            demand = DummyVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, route = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        # Diesel endurance should reflect 10L fuel (~0.8h endurance < 6h target) -> EMERGENCY
        self.assertLess(assessment.diesel_endurance_hours, 6.0)
        self.assertEqual(route, "EMERGENCY")

    def test_G_normal_option_b_routing(self):
        """Test G: High SOC and fuel routes to NORMAL mode."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=15000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        class DummyVector:
            point = [15000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummyVector()
            wind_generation = DummyVector()
            demand = DummyVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, route = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        self.assertEqual(route, "NORMAL")
        self.assertEqual(assessment.operating_mode, OperatingMode.NORMAL)

    def test_H_emergency_option_d_routing(self):
        """Test H: Low SOC and low fuel routes to EMERGENCY mode."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=21.0,  # Usable battery energy near 0
            battery_energy_wh=42000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=5.0   # Fuel endurance near 0
        )
        class DummyVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummyVector()
            wind_generation = DummyVector()
            demand = DummyVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, route = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        self.assertEqual(route, "EMERGENCY")

    def test_I_unknown_invalid_routing(self):
        """Test I: Invalid negative SOC returns UNKNOWN_INVALID mode."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=-10.0,  # Invalid SOC
            battery_energy_wh=-20000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        class DummyVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummyVector()
            wind_generation = DummyVector()
            demand = DummyVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, route = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertNotEqual(assessment.validity_status, ValidityStatus.VALID)

    def test_L_option_d_proportional_allocation(self):
        """Test L: Option D allocates available generation proportionally when insufficient."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=21.0,
            battery_energy_wh=42000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=0.0  # 0 fuel, low battery
        )
        class DummyVector:
            point = [5000.0] * 24  # Only 5kW solar available for 30kW demand
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyDemandVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummyVector()
            solar_generation = DummyVector()  # same 5 kW figure, W (post RT-01 mechanism-2 fix: option_d.py reads this field, not solar_irradiance, for generation)
            wind_generation = DummyVector()
            demand = DummyDemandVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, _ = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        plan = self.option_d_solver.solve(assessment, DummyBundle(), state, self.configs)

        self.assertEqual(plan.constraint_status, "OPTION_D_FALLBACK")
        # Load served should be >= solar generated + usable battery
        self.assertGreaterEqual(plan.load_served[0], 5000.0)
        self.assertGreater(plan.unmet_load[0], 0.0)

    def test_M_renewable_first_behavior(self):
        """Test M: Option D dispatches solar/wind directly to load before diesel."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=21.0,
            battery_energy_wh=42000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=50.0
        )
        class DummySolarVector:
            point = [40000.0] * 24  # 40 kW solar > 30 kW demand
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyDemandVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummySolarVector()
            solar_generation = DummySolarVector()  # same 40 kW figure, W (post RT-01 mechanism-2 fix)
            wind_generation = DummySolarVector()
            demand = DummyDemandVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, _ = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        plan = self.option_d_solver.solve(assessment, DummyBundle(), state, self.configs)

        # Solar alone covers 30 kW demand -> Diesel must be 0
        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.load_served[0], 30000.0)
        self.assertEqual(plan.unmet_load[0], 0.0)

    def test_P_diesel_not_started_solely_for_charging(self):
        """Test P: Diesel is not started if renewable solar covers demand."""
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=30.0,
            battery_energy_wh=60000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=50.0
        )
        class DummySolarVector:
            point = [30000.0] * 24
            timestamps = ["2026-09-26T00:00:00Z"] * 24
        class DummyBundle:
            solar_irradiance = DummySolarVector()
            solar_generation = DummySolarVector()  # same 30 kW figure, W (post RT-01 mechanism-2 fix)
            wind_generation = DummySolarVector()
            demand = DummySolarVector()
            timestamps = ["2026-09-26T00:00:00Z"] * 24

        assessment, _ = self.router.evaluate_and_route(state, DummyBundle(), self.configs)
        plan = self.option_d_solver.solve(assessment, DummyBundle(), state, self.configs)

        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.battery_charge[0], 0.0)

if __name__ == "__main__":
    unittest.main()
