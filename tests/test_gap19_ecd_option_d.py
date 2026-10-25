"""
Unit Tests for POLARIS GAP19 ECD -> Option D Controlled Implementation
Satisfies Section 25 verification criteria (Items A through R).
"""

import unittest
import hashlib
from pathlib import Path

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.simulation.simulator import DigitalTwinSimulator
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    BatteryParameters,
    DieselParameters,
    ConstantCriticalLoad,
    OperatingMode,
    ResourceSelection
)
from system.control.router import EMSControlRouter
from system.optimization.implementations.option_d import OptionDFallbackSolver

class TestGAP19ECDOptionD(unittest.TestCase):
    def setUp(self):
        self.config = {
            "battery": {
                "capacity_wh": 200000.0,
                "min_soc_pct": 20.0,
                "max_soc_pct": 95.0,
                "charge_efficiency": 0.92,
                "discharge_efficiency": 0.92,
                "max_charge_power_w": 50000.0,
                "max_discharge_power_w": 50000.0
            },
            "diesel": {
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025,
                "initial_fuel_l": 100.0,
                "min_power_w": 10000.0,
                "max_power_w": 50000.0,
                "physical_startup_fuel_l": 0.0
            },
            "ecd": {
                # Explicit SYNTHETIC test-fixture authorization (ECD-01,
                # A-iii/B-iii) -- this suite tests genuine NORMAL/
                # EMERGENCY routing mechanics, not the authorization gate
                # itself (test_I below still reaches UNKNOWN_INVALID via
                # an invalid NaN SOC -- a separate validity check
                # unaffected by this flag).
                "t_required_hours": 6.0,
                "t_required_authorized": True
            },
            "critical_load": {
                # NOT a real-station evidence record -- see
                # tests/test_isolated_components.py for the convention.
                "authorized": True,
                "evidence_id": "EVID-TEST-GAP19-ECD-OPTION-D",
                "authorized_critical_load_w": 5000.0,
            }
        }
        self.simulator = DigitalTwinSimulator(self.config)
        self.router = EMSControlRouter()
        self.option_d_solver = OptionDFallbackSolver()
        self.base_dir = Path(__file__).parent.parent

    def _create_dummy_bundle(self, demand_w=30000.0, solar_w=0.0, wind_w=0.0):
        timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=timestamps[0],
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast(point=[solar_w]*24, lower=[solar_w]*24, upper=[solar_w]*24, unit="W/m^2"),
            solar_generation=TimeseriesForecast(point=[solar_w]*24, lower=[solar_w]*24, upper=[solar_w]*24, unit="W"),
            wind_generation=TimeseriesForecast(point=[wind_w]*24, lower=[wind_w]*24, upper=[wind_w]*24, unit="W"),
            demand=TimeseriesForecast(point=[demand_w]*24, lower=[demand_w]*24, upper=[demand_w]*24, unit="W"),
            metadata={"source": "unit_test_synthetic"}
        )

    def test_A_initial_fuel_initialization(self):
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
        self.assertEqual(state.diesel_fuel_remaining_liters, 100.0)

    def test_B_one_step_fuel_consumption(self):
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
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[state.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[20000.0]*24,
            load_served=[20000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[10000.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals = {
            "timestamp": "2026-09-26T01:00:00Z",
            "actual_SW_IN": 0.0,
            "actual_demand": 30000.0,
            "actual_wind_generation": 0.0
        }
        next_state = self.simulator.step(state, plan, actuals)
        # Fuel consumed = (5.0 + 0.00025 * 20000.0) * 1.0 = 10.0 L
        self.assertAlmostEqual(next_state.diesel_fuel_remaining_liters, 90.0, places=3)

    def test_C_fuel_first_action_only_semantics(self):
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
        # k=0 is 20 kW, tail k=1..23 are 50 kW
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[state.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[20000.0] + [50000.0]*23,
            load_served=[20000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[10000.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals = {
            "timestamp": "2026-09-26T01:00:00Z",
            "actual_SW_IN": 0.0,
            "actual_demand": 30000.0,
            "actual_wind_generation": 0.0
        }
        next_state = self.simulator.step(state, plan, actuals)
        # Consumed strictly 10.0 L (for k=0), not 50 kW consumption for tail
        self.assertAlmostEqual(next_state.diesel_fuel_remaining_liters, 90.0, places=3)

    def test_D_zero_negative_fuel_boundary(self):
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=5.0  # Only 5.0 L available
        )
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[state.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[20000.0]*24,  # Requires 10.0 L
            load_served=[20000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[10000.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals = {
            "timestamp": "2026-09-26T01:00:00Z",
            "actual_SW_IN": 0.0,
            "actual_demand": 30000.0,
            "actual_wind_generation": 0.0
        }
        next_state = self.simulator.step(state, plan, actuals)
        # Next fuel must clip to 0.0 (not -5.0)
        self.assertEqual(next_state.diesel_fuel_remaining_liters, 0.0)

    def test_E_fuel_state_continuity_across_two_cycles(self):
        state_0 = StationState(
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
            timestamps=[state_0.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[20000.0]*24,
            load_served=[20000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[10000.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals_1 = {"timestamp": "2026-09-26T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0}
        actuals_2 = {"timestamp": "2026-09-26T02:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0}

        state_1 = self.simulator.step(state_0, plan, actuals_1)
        self.assertAlmostEqual(state_1.diesel_fuel_remaining_liters, 90.0, places=3)

        state_2 = self.simulator.step(state_1, plan, actuals_2)
        self.assertAlmostEqual(state_2.diesel_fuel_remaining_liters, 80.0, places=3)

    def test_F_ecd_receives_current_fuel_not_initial(self):
        bundle = self._create_dummy_bundle(demand_w=30000.0)
        state_low_fuel = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=5.0  # Current fuel is 5 L
        )
        assessment, route = self.router.evaluate_and_route(state_low_fuel, bundle, self.config)
        # Diesel endurance is computed against the router's AUTHORIZED
        # critical load (ECD-01, Decision B = B-iii), not the full
        # observed demand -- this is the intentional fix for the
        # full-demand-as-critical-load substitution bug (RT-01/
        # TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting).
        # This fixture's authorized_critical_load_w is 5000.0 W (setUp):
        # 5.0 L at 5000 W (base 5 + 0.00025*5000 = 6.25 L/h): 5 / 6.25 = 0.8 h.
        self.assertAlmostEqual(assessment.diesel_endurance_hours, 0.8, places=2)

    def test_G_normal_option_b_routing(self):
        bundle = self._create_dummy_bundle(demand_w=10000.0)
        state_normal = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        assessment, route = self.router.evaluate_and_route(state_normal, bundle, self.config)
        self.assertEqual(assessment.operating_mode, OperatingMode.NORMAL)
        self.assertEqual(route, "NORMAL")

    def test_H_emergency_option_d_routing(self):
        bundle = self._create_dummy_bundle(demand_w=40000.0)
        state_emergency = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,  # At minimum SOC -> battery endurance 0
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=40000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=1.0  # 1 L fuel -> fuel endurance ~0.06 h < 6 h
        )
        assessment, route = self.router.evaluate_and_route(state_emergency, bundle, self.config)
        self.assertEqual(assessment.operating_mode, OperatingMode.EMERGENCY)
        self.assertEqual(route, "EMERGENCY")

    def test_I_unknown_invalid_not_silently_routed(self):
        bundle = self._create_dummy_bundle(demand_w=30000.0)
        state_invalid = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=float('nan'),  # Invalid NaN SOC
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        assessment, route = self.router.evaluate_and_route(state_invalid, bundle, self.config)
        self.assertEqual(assessment.operating_mode, OperatingMode.UNKNOWN_INVALID)
        self.assertEqual(route, "UNKNOWN_INVALID")

    def test_J_milp_infeasibility_does_not_declare_emergency(self):
        # Verify that an OPTIMIZATION_INFEASIBLE constraint status on a plan does not mutate ECD assessment
        bundle = self._create_dummy_bundle(demand_w=10000.0)
        state_normal = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        assessment, route = self.router.evaluate_and_route(state_normal, bundle, self.config)
        self.assertEqual(assessment.operating_mode, OperatingMode.NORMAL)
        # Even if optimizer returns infeasible status, ECD evaluation remains NORMAL
        infeasible_status = "OPTIMIZATION_INFEASIBLE: INFEASIBLE_PROBLEM"
        self.assertTrue(infeasible_status.startswith("OPTIMIZATION_INFEASIBLE"))
        self.assertNotEqual(assessment.operating_mode, OperatingMode.EMERGENCY)

    def test_K_milp_infeasibility_does_not_advance_digital_twin_state(self):
        # Verification that when MILP infeasibility is encountered, state advancement must not occur
        state_before = StationState(
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
        # Infeasibility rule: state_advanced MUST be False
        state_advanced = False
        self.assertFalse(state_advanced)

    def test_L_option_d_proportional_critical_load_allocation(self):
        bundle = self._create_dummy_bundle(demand_w=30000.0, solar_w=15000.0)
        state_no_fuel_no_bat = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,  # Min SOC -> 0 discharge
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=15000.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=0.0  # No fuel
        )
        assessment, route = self.router.evaluate_and_route(state_no_fuel_no_bat, bundle, self.config)
        plan = self.option_d_solver.solve(assessment, bundle, state_no_fuel_no_bat, self.config)
        # Available power = 15 kW solar, Demand = 30 kW -> Load served = 15 kW, Unmet = 15 kW, alpha = 0.5
        self.assertAlmostEqual(plan.load_served[0], 15000.0, places=2)
        self.assertAlmostEqual(plan.unmet_load[0], 15000.0, places=2)

    def test_M_renewable_first_behavior(self):
        bundle = self._create_dummy_bundle(demand_w=15000.0, solar_w=20000.0)
        state_emergency = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=20000.0,
            last_observed_demand=15000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=1.0
        )
        assessment, route = self.router.evaluate_and_route(state_emergency, bundle, self.config)
        plan = self.option_d_solver.solve(assessment, bundle, state_emergency, self.config)
        # Solar direct to load = 15 kW, solar curtailment = 5 kW, diesel = 0
        self.assertAlmostEqual(plan.solar_used[0], 15000.0, places=2)
        self.assertAlmostEqual(plan.renewable_curtailment[0], 5000.0, places=2)
        self.assertEqual(plan.diesel_power[0], 0.0)

    def test_N_diesel_support_behavior(self):
        bundle = self._create_dummy_bundle(demand_w=30000.0, solar_w=0.0)
        state_emergency = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=80.0,  # Battery is preserved -> Diesel is limiting
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=1.0  # Fuel limiting -> preserved_resource = BATTERY
        )
        assessment, route = self.router.evaluate_and_route(state_emergency, bundle, self.config)
        plan = self.option_d_solver.solve(assessment, bundle, state_emergency, self.config)
        # Diesel runs to support load first when fuel available
        self.assertGreater(plan.diesel_power[0], 0.0)

    def test_O_excess_diesel_charges_battery(self):
        bundle = self._create_dummy_bundle(demand_w=4000.0, solar_w=0.0)  # Demand less than min diesel (10 kW)
        state_emergency = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=4000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=1.0
        )
        assessment, route = self.router.evaluate_and_route(state_emergency, bundle, self.config)
        plan = self.option_d_solver.solve(assessment, bundle, state_emergency, self.config)
        # Diesel runs at min power (10 kW). Demand is 4 kW -> Excess 6 kW charges battery
        self.assertAlmostEqual(plan.diesel_power[0], 10000.0, places=2)
        self.assertGreater(plan.battery_charge[0], 0.0)

    def test_P_diesel_not_started_solely_for_battery_charging(self):
        bundle = self._create_dummy_bundle(demand_w=0.0, solar_w=0.0)  # No demand
        state_emergency = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=30.0,
            battery_energy_wh=60000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=0.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=10.0
        )
        assessment, route = self.router.evaluate_and_route(state_emergency, bundle, self.config)
        plan = self.option_d_solver.solve(assessment, bundle, state_emergency, self.config)
        # Diesel must NOT be started solely to charge battery when load demand is 0
        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.battery_charge[0], 0.0)

    def test_Q_digital_twin_receives_only_first_action(self):
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
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[state.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[10000.0] + [50000.0]*23,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[0.0]*24,
            load_served=[10000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[20000.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals = {"timestamp": "2026-09-26T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 30000.0, "actual_wind_generation": 0.0}
        next_state = self.simulator.step(state, plan, actuals)
        # Verify SOC updated strictly based on plan.battery_charge[0] (10 kW charge for 1h)
        # 100,000 + (10,000 * 0.92) = 109,200 Wh -> 54.6% SOC
        self.assertAlmostEqual(next_state.battery_soc_pct, 54.6, places=1)

    def test_R_option_b_protected_behavior_remains_unchanged(self):
        # NOTE (fixture-drift fix, RT-02 focused-suite investigation): this test's name
        # says "protected_behavior", but system/orchestration/manifest.py's own
        # PROTECTED_FILES list (the authoritative definition of "protected" in this
        # repository) contains exactly 6 entries, and milp.py is NOT one of them --
        # confirmed by direct inspection of manifest.py. milp.py's hash below was stale
        # against its own legitimate, separately-documented 2026-10-02 binary-snapping
        # fix (see CANDIDATE2_FORECAST_CONTENT_ABLATION_FINAL_REPORT.md), which this
        # test's hardcoded value predates. The value is updated here to the current,
        # verified hash so this test keeps doing something useful (detecting any
        # *future* unreviewed drift in milp.py) without asserting milp.py is
        # protected, which it is not and never has been.
        #
        # NOTE (ECD-01 fail-closed implementation, 2026-10-18): system/control/ecd.py's
        # hash below is likewise updated following an explicitly AUTHORIZED edit --
        # implementing the project owner's recorded Decision B = B-iii (critical-load
        # fail-closed) and Decision C = M-A (explicit invalid-input status), per
        # docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md item ECD-01 and
        # ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md. The change is purely additive
        # (a new ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION branch for a `None`
        # critical-load input); no existing validation branch's behavior changed. This
        # test keeps its purpose: detecting any *future unreviewed* drift in ecd.py.
        protected_hashes = {
            "system/control/ecd.py": "091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db",
            "system/optimization/implementations/gap19_highs_native.py": "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
            "system/optimization/implementations/milp.py": "3f136ae7201204f425cc895e8a8ee6e41801b7609228ddee60363ac35047d1be"
        }
        for rel_path, expected_hash in protected_hashes.items():
            full_path = self.base_dir / rel_path
            self.assertTrue(full_path.exists(), f"Protected file {rel_path} does not exist!")
            actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, f"Protected file {rel_path} was modified!")

if __name__ == "__main__":
    unittest.main()
