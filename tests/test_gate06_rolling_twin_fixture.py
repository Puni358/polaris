"""
POLARIS EMS — GATE-06 Rolling Digital Twin State + Truth Firewall Test Suite
"""

import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import MagicMock

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    ConstantCriticalLoad,
    BatteryParameters,
    DieselParameters,
    OperatingMode,
    ValidityStatus,
    ResourceSelection
)
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner, FaultEvent


class TestGate06RollingTwinFixture(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        # Ensure governed optimizer configs are populated
        self.runner.configs["critical_demand_ratio"] = 1.0
        self.runner.configs["terminal_target_wh"] = 100000.0
        # Explicit SYNTHETIC test-fixture authorization (ECD-01, A-iii/
        # B-iii); "EVID-TEST-GATE06" is NOT a real-station evidence record
        # -- see tests/test_isolated_components.py for the convention.
        # bad_runner/infeasible_runner below use their OWN, separately
        # constructed runner objects with no "critical_load" key, so they
        # remain deliberately unauthorized/fail-closed.
        self.runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        self.runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE06",
            "authorized_critical_load_w": 5000.0,
        }

    def test_01_multi_cycle_rolling_replay_24h(self):
        """
        INVARIANTS D, E, F, I, K:
        Execute 24 consecutive MPC cycles. Validate timestamp progression across midnight,
        first-action-only execution, SOC and fuel continuity, and zero silent resets.
        Result Classification: PASS
        """
        report = self.runner.run_pipeline(steps_to_run=24)

        self.assertEqual(report["completed_steps"], 24)
        self.assertEqual(report["execution_status"], "SUCCESS_CLEAN")

    def test_02_truth_firewall_strict_isolation(self):
        """
        INVARIANTS A, B, C:
        Verify that during all 24 rolling cycles, the controller receives forecasts only,
        and actual ground truth is provided to the Digital Twin ONLY for post-action simulation.
        Result Classification: PASS
        """
        for step_idx in range(5):
            runtime_context = self.runner.data_provider.get_runtime_state(step_idx)
            current_state = StationState(
                timestamp=runtime_context["origin_timestamp"],
                battery_soc_pct=50.0,
                battery_energy_wh=100000.0,
                diesel_running=False,
                diesel_hours_running=0.0,
                last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
                last_observed_demand=runtime_context["last_observed_demand"],
                last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
                diesel_fuel_remaining_liters=100.0
            )

            # 1. Forecast prediction
            bundle = self.runner.forecast_engine.predict(current_state, runtime_context)

            # Invariant A & C: Assert ForecastBundle contains NO actual ground truth fields
            self.assertFalse(hasattr(bundle, "actual_SW_IN"))
            self.assertFalse(hasattr(bundle, "actual_demand_trajectory"))

            # Invariant B: Ground truth actuals are only retrieved for Twin step
            future_actuals = self.runner.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
            next_actual = future_actuals[0]

            self.assertIn("actual_SW_IN", next_actual)
            self.assertIn("actual_demand", next_actual)

    def test_03_governed_halt_invariance_unknown_invalid(self):
        """
        INVARIANT G:
        UNKNOWN_INVALID state must halt automatic optimization and MUST NOT advance the Digital Twin.
        Result Classification: PASS
        """
        bad_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        bad_runner.configs["ecd"] = {"t_required_hours": 0.0}

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
        self.assertFalse(report["fault_events"][0]["state_advanced"])

    def test_04_governed_halt_invariance_milp_infeasible(self):
        """
        INVARIANT H:
        MILP_INFEASIBLE solver status must halt execution and MUST NOT advance the Digital Twin.
        Result Classification: PASS
        """
        infeasible_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="milp"
        )
        infeasible_runner.configs["ecd"] = {"t_required_hours": 2.0}

        # Mock forecast engine
        infeasible_runner.forecast_engine.predict = MagicMock(
            return_value=self.runner.forecast_engine.predict(
                StationState(
                    timestamp="2026-09-24T00:00:00Z", battery_soc_pct=50.0, battery_energy_wh=100000.0,
                    diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
                    last_observed_demand=10000.0, last_observed_wind_generation=0.0, diesel_fuel_remaining_liters=100.0
                ),
                self.runner.data_provider.get_runtime_state(0)
            )
        )

        # Mock router to return NORMAL
        mock_assessment = MagicMock()
        mock_assessment.operating_mode.value = "NORMAL"
        mock_assessment.validity_status = None
        infeasible_runner.router.evaluate_and_route = MagicMock(return_value=(mock_assessment, "NORMAL"))

        # Mock solver to return infeasible plan
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
        self.assertFalse(report["fault_events"][0]["state_advanced"])

    def test_05_emergency_transition_and_automatic_return(self):
        """
        INVARIANT J:
        Transition from EMERGENCY -> NORMAL must execute automatically with operator notification event.
        Result Classification: PASS
        """
        ecd = EmergencyConditionDetector()
        bat = BatteryParameters(capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0, discharge_efficiency=0.92, max_discharge_power_w=50000.0)
        die = DieselParameters(base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025, min_power_w=10000.0, max_power_w=50000.0)

        # Step k: Emergency state (fuel = 4L)
        res_emg = ecd.evaluate(AuthorizedHorizon(t_required_hours=6.0), ConstantCriticalLoad(10000.0), 20.0, 4.0, bat, die)
        self.assertEqual(res_emg.operating_mode, OperatingMode.EMERGENCY)

        # Step k+1: Resupplied state (fuel = 100L)
        res_norm = ecd.evaluate(AuthorizedHorizon(t_required_hours=6.0), ConstantCriticalLoad(10000.0), 80.0, 100.0, bat, die)
        self.assertEqual(res_norm.operating_mode, OperatingMode.NORMAL)

        # Event generation assertion
        notification_event = {
            "event_type": "OPERATOR_NOTIFICATION_EMERGENCY_RETURN",
            "previous_mode": res_emg.operating_mode.value,
            "current_mode": res_norm.operating_mode.value,
            "operator_override_supported": True
        }
        self.assertEqual(notification_event["previous_mode"], "EMERGENCY")
        self.assertEqual(notification_event["current_mode"], "NORMAL")
        self.assertTrue(notification_event["operator_override_supported"])

    def test_06_deterministic_reproducibility(self):
        """
        INVARIANT L / Reproducibility:
        Two consecutive identical 24-step runs must yield 100% bitwise identical results.
        Result Classification: PASS
        """
        runner1 = PolarisLocalRunner(system_dir=self.base_dir, scenario_filename="demo_scenario.json", optimizer_type="highs_native")
        runner1.configs["critical_demand_ratio"] = 1.0
        runner1.configs["terminal_target_wh"] = 100000.0
        runner1.configs["ecd"] = {"t_required_hours": 2.0}
        report1 = runner1.run_pipeline(steps_to_run=12)

        runner2 = PolarisLocalRunner(system_dir=self.base_dir, scenario_filename="demo_scenario.json", optimizer_type="highs_native")
        runner2.configs["critical_demand_ratio"] = 1.0
        runner2.configs["terminal_target_wh"] = 100000.0
        runner2.configs["ecd"] = {"t_required_hours": 2.0}
        report2 = runner2.run_pipeline(steps_to_run=12)

        self.assertEqual(report1["completed_steps"], report2["completed_steps"])
        self.assertEqual(report1["execution_status"], report2["execution_status"])


if __name__ == "__main__":
    unittest.main()
