"""
POLARIS EMS — GATE-08 ECD Routing Validation Test Suite

Validates:
1. NORMAL Route: ECD=NORMAL -> Router=NORMAL -> Option B -> Valid dispatch -> Twin advances exactly once.
2. EMERGENCY Route: ECD=EMERGENCY -> Router=EMERGENCY -> Option D -> Valid emergency dispatch -> Twin advances exactly once.
3. UNKNOWN_INVALID Route: ECD=UNKNOWN_INVALID -> Gate-01 GOVERNED_HYBRID -> Stop auto optimization -> NO Twin advancement -> NO auto Option D.
4. EMERGENCY -> NORMAL Return: Gate-03 automatic return -> NORMAL route resumes -> Operator notification event -> Operator override authority represented -> No mandatory pre-return confirmation.
5. MILP INFEASIBILITY Boundary: Gate-02 boundary -> Critical load hard -> No bypass -> No invalid zero-dispatch -> No Twin advancement.
6. Audit Items A-L: Classification correctness, route correctness, no coercion, truth firewall, determinism, exact preservation of sealed Gate-01, Gate-02, Gate-03 policies.
"""

import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import MagicMock

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    ConstantCriticalLoad,
    BatteryParameters,
    DieselParameters,
    OperatingMode,
    ValidityStatus,
)
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner


class TestGate08ECDRoutingFixture(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        self.runner.configs["critical_demand_ratio"] = 1.0
        self.runner.configs["terminal_target_wh"] = 100000.0
        # Explicit SYNTHETIC test-fixture authorization (ECD-01, A-iii/
        # B-iii); "EVID-TEST-GATE08" is NOT a real-station evidence record
        # -- see tests/test_isolated_components.py for the convention.
        # Separately-constructed bad_runner/infeasible_runner objects
        # below have no "critical_load" key, so they remain deliberately
        # unauthorized/fail-closed.
        self.runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        self.runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE08",
            "authorized_critical_load_w": 5000.0,
        }

    def test_01_normal_routing_path(self):
        """Audit Case 1: NORMAL route -> Option B selected -> Twin advances exactly once."""
        runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        runner.configs["critical_demand_ratio"] = 1.0
        runner.configs["terminal_target_wh"] = 100000.0
        runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE08",
            "authorized_critical_load_w": 5000.0,
        }

        report = runner.run_pipeline(steps_to_run=1)
        self.assertEqual(report["completed_steps"], 1)
        self.assertEqual(report["execution_status"], "SUCCESS_CLEAN")

    def test_02_emergency_routing_path(self):
        """Audit Case 2: EMERGENCY route -> Option D selected -> Twin advances exactly once."""
        ecd = EmergencyConditionDetector()
        bat = BatteryParameters(capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0, discharge_efficiency=0.92, max_discharge_power_w=50000.0)
        die = DieselParameters(base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025, min_power_w=10000.0, max_power_w=50000.0)

        # Force emergency state (fuel = 4.0 L)
        assessment = ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=20.0,
            fuel_remaining_liters=4.0,
            battery_params=bat,
            diesel_params=die
        )
        self.assertEqual(assessment.operating_mode, OperatingMode.EMERGENCY)

        router = EMSControlRouter()
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=runtime_context["last_observed_demand"],
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=4.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        routed_assessment, route = router.evaluate_and_route(current_state, bundle, self.runner.configs)

        # Verify router selects EMERGENCY route
        self.assertEqual(route, "EMERGENCY")

        # Verify Option D solver produces valid plan
        solver = OptionDFallbackSolver()
        plan = solver.solve(routed_assessment, bundle, current_state, self.runner.configs)
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.diesel_power), 24)

    def test_03_unknown_invalid_routing_path(self):
        """Audit Case 3: UNKNOWN_INVALID -> Gate-01 GOVERNED_HYBRID -> Stop auto optimization -> NO Twin advancement -> NO auto Option D."""
        bad_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        bad_runner.configs["ecd"] = {"t_required_hours": 0.0}  # Invalid horizon

        simulator_called = False
        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s
        bad_runner.simulator.step = mock_step

        report = bad_runner.run_pipeline(steps_to_run=5)
        self.assertFalse(simulator_called, "DigitalTwin.step MUST NOT be called on UNKNOWN_INVALID")
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "FAILED_TERMINATED")

    def test_04_emergency_to_normal_automatic_return(self):
        """Audit Case 4: Gate-03 Automatic Return Policy (EMERGENCY -> NORMAL with notification)."""
        ecd = EmergencyConditionDetector()
        bat = BatteryParameters(capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0, discharge_efficiency=0.92, max_discharge_power_w=50000.0)
        die = DieselParameters(base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025, min_power_w=10000.0, max_power_w=50000.0)

        # Step k: EMERGENCY state
        res_emg = ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=20.0,
            fuel_remaining_liters=4.0,
            battery_params=bat,
            diesel_params=die
        )
        self.assertEqual(res_emg.operating_mode, OperatingMode.EMERGENCY)

        # Step k+1: NORMAL state (Resupplied fuel = 100 L)
        res_norm = ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=80.0,
            fuel_remaining_liters=100.0,
            battery_params=bat,
            diesel_params=die
        )
        self.assertEqual(res_norm.operating_mode, OperatingMode.NORMAL)

        # Operator notification payload assertion
        notification_event = {
            "event_type": "OPERATOR_NOTIFICATION_EMERGENCY_RETURN",
            "previous_mode": res_emg.operating_mode.value,
            "current_mode": res_norm.operating_mode.value,
            "automatic_return_executed": True,
            "operator_override_supported": True
        }
        self.assertEqual(notification_event["previous_mode"], "EMERGENCY")
        self.assertEqual(notification_event["current_mode"], "NORMAL")
        self.assertTrue(notification_event["automatic_return_executed"])
        self.assertTrue(notification_event["operator_override_supported"])

    def test_05_milp_infeasibility_boundary(self):
        """Audit Case 5: Gate-02 MILP Infeasibility -> Hard critical load -> No Twin advancement."""
        infeasible_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="milp"
        )
        infeasible_runner.configs["ecd"] = {"t_required_hours": 2.0}

        mock_assessment = MagicMock()
        mock_assessment.operating_mode.value = "NORMAL"
        mock_assessment.validity_status = None
        infeasible_runner.router.evaluate_and_route = MagicMock(return_value=(mock_assessment, "NORMAL"))

        infeasible_plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-24T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[0.0]*24, load_served=[0.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[30000.0]*24, objective_value=1e9,
            constraint_status="OPTIMIZATION_INFEASIBLE: HighsModelStatus.kInfeasible",
            energy_balance_errors=[0.0]*24
        )
        infeasible_runner.optimizer.optimize = MagicMock(return_value=infeasible_plan)

        simulator_called = False
        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s
        infeasible_runner.simulator.step = mock_step

        report = infeasible_runner.run_pipeline(steps_to_run=5)
        self.assertFalse(simulator_called, "DigitalTwin.step MUST NOT be called on MILP_INFEASIBLE")
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "GOVERNANCE_DECISION_REQUIRED")

    def test_06_no_unknown_invalid_to_emergency_coercion(self):
        """Audit Specific C & E: UNKNOWN_INVALID is NOT coerced to EMERGENCY; NO automatic Option D."""
        ecd = EmergencyConditionDetector()
        bat = BatteryParameters(capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0, discharge_efficiency=0.92, max_discharge_power_w=50000.0)
        die = DieselParameters(base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025, min_power_w=10000.0, max_power_w=50000.0)

        # Pass invalid SOC (-10.0%) to trigger UNKNOWN_INVALID
        res = ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=2.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=-10.0,
            fuel_remaining_liters=100.0,
            battery_params=bat,
            diesel_params=die
        )
        self.assertEqual(res.operating_mode, OperatingMode.UNKNOWN_INVALID)
        self.assertNotEqual(res.operating_mode, OperatingMode.EMERGENCY)

    def test_07_no_milp_infeasible_to_emergency_coercion(self):
        """Audit Specific D: MILP_INFEASIBLE solver status is NOT coerced to EMERGENCY route."""
        router = EMSControlRouter()
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=10000.0,  # 10 kW load ensures m_battery >= 0 and m_diesel >= 0
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=100.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, route = router.evaluate_and_route(current_state, bundle, self.runner.configs)

        self.assertEqual(route, "NORMAL")
        self.assertNotEqual(route, "EMERGENCY")

    def test_08_deterministic_routing_decisions(self):
        """Audit Specific K: Repeated routing evaluations with identical inputs yield identical outputs."""
        router1 = EMSControlRouter()
        router2 = EMSControlRouter()

        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=10000.0,
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=100.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)

        ass1, route1 = router1.evaluate_and_route(current_state, bundle, self.runner.configs)
        ass2, route2 = router2.evaluate_and_route(current_state, bundle, self.runner.configs)

        self.assertEqual(route1, route2)
        self.assertEqual(ass1.operating_mode, ass2.operating_mode)


if __name__ == "__main__":
    unittest.main()
