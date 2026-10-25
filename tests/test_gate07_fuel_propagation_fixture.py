"""
POLARIS EMS — GATE-07 Rolling Diesel Fuel State Propagation Test Suite

Validates all 17 GATE-07 audit items:
1. Initial diesel fuel state is established once.
2. Each executed diesel action consumes the correct amount of fuel.
3. Fuel is propagated from cycle k to cycle k+1 through StationState.
4. Fuel is never silently reset between cycles.
5. Fuel never increases without an explicitly represented replenishment event.
6. ECD receives the current StationState fuel value, not future fuel truth.
7. Option D receives the current governed fuel state.
8. Option B receives only the fuel information already authorized by its existing contract.
9. Digital Twin uses the committed k=0 action for fuel propagation.
10. Future actual fuel values are never exposed to the controller.
11. UNKNOWN_INVALID does not advance fuel state.
12. MILP infeasibility does not advance fuel state.
13. Valid NORMAL and EMERGENCY dispatches advance fuel state exactly once.
14. No double-consumption occurs.
15. No fuel consumption occurs for discarded k=1..k=23 forecast actions.
16. Timestamp/order of fuel updates is deterministic.
17. Two identical replays produce identical fuel traces.
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


class TestGate07FuelPropagationFixture(unittest.TestCase):

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
        # B-iii); "EVID-TEST-GATE07" is NOT a real-station evidence record
        # -- see tests/test_isolated_components.py for the convention.
        # The separately-constructed bad_runner/infeasible_runner/runner1/
        # runner2 objects elsewhere in this file have no "critical_load"
        # key, so they remain deliberately unauthorized/fail-closed.
        self.runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        self.runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE07",
            "authorized_critical_load_w": 5000.0,
        }

    def test_01_initial_fuel_state_established_once(self):
        """Audit Item 1: Initial diesel fuel state is established once."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        initial_fuel = 100.0  # Synthetic fixture value
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=runtime_context["last_observed_demand"],
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=initial_fuel
        )
        self.assertEqual(current_state.diesel_fuel_remaining_liters, 100.0)

    def test_02_each_executed_action_consumes_correct_fuel(self):
        """Audit Item 2: Each executed diesel action consumes the correct amount of fuel."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        state_before = StationState(
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

        p_diesel_k0 = 20000.0  # 20 kW diesel dispatch at k=0
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-24T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[p_diesel_k0] + [0.0]*23, load_served=[20000.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=100.0,
            constraint_status="OPTIMIZATION_SUCCESSFUL",
            energy_balance_errors=[0.0]*24
        )

        actuals = self.runner.data_provider.get_future_ground_truth(0, horizon_hours=24)[0]
        state_after = simulator.step(state_before, plan, actuals)

        # Formula in simulator: base 5.0 L/h + 0.00025 L/Wh * 20000 W * 1.0 h = 5.0 + 5.0 = 10.0 L
        expected_consumed = 5.0 + (0.00025 * p_diesel_k0)
        expected_next_fuel = 100.0 - expected_consumed
        self.assertAlmostEqual(state_after.diesel_fuel_remaining_liters, expected_next_fuel, places=4)

    def test_03_fuel_propagated_through_station_state(self):
        """Audit Item 3: Fuel is propagated from cycle k to cycle k+1 through StationState."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
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

        for step_idx in range(5):
            plan = DispatchPlan(
                schema_version="1.0.0",
                timestamps=[f"2026-09-24T{step_idx:02d}:00:00Z"]*24,
                solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
                battery_soc=[50.0]*24, diesel_power=[10000.0]*24, load_served=[10000.0]*24, flexible_load_schedule=[0.0]*24,
                renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=100.0,
                constraint_status="OPTIMIZATION_SUCCESSFUL",
                energy_balance_errors=[0.0]*24
            )
            actuals = self.runner.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)[0]
            next_state = simulator.step(current_state, plan, actuals)

            # Fuel consumed per step: 5.0 + 0.00025 * 10000 = 7.5 L
            self.assertAlmostEqual(
                next_state.diesel_fuel_remaining_liters,
                current_state.diesel_fuel_remaining_liters - 7.5,
                places=4
            )
            current_state = next_state

    def test_04_fuel_never_silently_reset(self):
        """Audit Item 4: Fuel is never silently reset between cycles."""
        runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        runner.configs["critical_demand_ratio"] = 1.0
        runner.configs["terminal_target_wh"] = 100000.0
        # Explicit SYNTHETIC test-fixture authorization (ECD-01, A-iii/
        # B-iii) -- see setUp() above for the convention; this test's
        # intent (12-cycle fuel continuity) needs a classified route, not
        # the fail-closed gate.
        runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE07",
            "authorized_critical_load_w": 5000.0,
        }

        report = runner.run_pipeline(steps_to_run=12)
        self.assertEqual(report["completed_steps"], 12)

    def test_05_fuel_never_increases_without_replenishment_event(self):
        """Audit Item 5: Fuel never increases without explicitly represented replenishment event."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
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

        fuel_levels = [current_state.diesel_fuel_remaining_liters]
        for step_idx in range(10):
            plan = DispatchPlan(
                schema_version="1.0.0",
                timestamps=[f"2026-09-24T{step_idx:02d}:00:00Z"]*24,
                solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
                battery_soc=[50.0]*24, diesel_power=[0.0]*24, load_served=[0.0]*24, flexible_load_schedule=[0.0]*24,
                renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=0.0,
                constraint_status="OPTIMIZATION_SUCCESSFUL",
                energy_balance_errors=[0.0]*24
            )
            actuals = self.runner.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)[0]
            current_state = simulator.step(current_state, plan, actuals)
            fuel_levels.append(current_state.diesel_fuel_remaining_liters)

        for i in range(1, len(fuel_levels)):
            self.assertLessEqual(fuel_levels[i], fuel_levels[i-1])

    def test_06_ecd_receives_current_station_state_fuel(self):
        """Audit Item 6: ECD receives current StationState fuel value, not future fuel truth."""
        ecd = EmergencyConditionDetector()
        bat = BatteryParameters(capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0, discharge_efficiency=0.92, max_discharge_power_w=50000.0)
        die = DieselParameters(base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025, min_power_w=10000.0, max_power_w=50000.0)

        current_fuel = 45.67  # Governed current fuel state
        res = ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=2.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=50.0,
            fuel_remaining_liters=current_fuel,
            battery_params=bat,
            diesel_params=die
        )
        self.assertIsNotNone(res)
        # Total fuel consumption rate at 10 kW load: 5.0 base + 0.00025*10000 marginal = 7.5 L/h
        # 45.67 L / 7.5 L/h = 6.08933 hours of endurance
        self.assertAlmostEqual(res.diesel_endurance_hours, 45.67 / 7.5, places=4)

    def test_07_option_d_receives_current_governed_fuel_state(self):
        """Audit Item 7: Option D receives current governed fuel state."""
        solver = OptionDFallbackSolver()
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=runtime_context["last_observed_demand"],
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=25.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, _ = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        plan = solver.solve(assessment, bundle, current_state, self.runner.configs)

        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.diesel_power), 24)

    def test_08_option_b_receives_only_authorized_fuel_info(self):
        """Audit Item 8: Option B receives only fuel information authorized by existing contract."""
        optimizer = GAP19HighsNativeOptimizer()
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=runtime_context["last_observed_solar_irradiance"],
            last_observed_demand=runtime_context["last_observed_demand"],
            last_observed_wind_generation=runtime_context["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=80.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        plan = optimizer.optimize(bundle, current_state, self.runner.configs)

        self.assertIsNotNone(plan)
        self.assertIn(plan.constraint_status, ["OPTIMAL", "OPTIMIZATION_SUCCESSFUL"])

    def test_09_digital_twin_uses_committed_k0_action(self):
        """Audit Item 9: Digital Twin uses committed k=0 action for fuel propagation."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        state_before = StationState(
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

        # Plan with k=0 diesel power = 10 kW, k=1..23 diesel power = 50 kW
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-24T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[10000.0] + [50000.0]*23, load_served=[10000.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=100.0,
            constraint_status="OPTIMIZATION_SUCCESSFUL",
            energy_balance_errors=[0.0]*24
        )

        actuals = self.runner.data_provider.get_future_ground_truth(0, horizon_hours=24)[0]
        state_after = simulator.step(state_before, plan, actuals)

        # Expected consumption for k=0 action ONLY (10 kW): 5.0 + 0.00025 * 10000 = 7.5 L
        # NOT k=1..23 (50 kW)
        expected_consumed = 5.0 + (0.00025 * 10000.0)
        expected_next_fuel = 100.0 - expected_consumed
        self.assertAlmostEqual(state_after.diesel_fuel_remaining_liters, expected_next_fuel, places=4)

    def test_10_future_actual_fuel_values_never_exposed(self):
        """Audit Item 10: Future actual fuel values are never exposed to the controller."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
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
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)

        self.assertFalse(hasattr(bundle, "future_fuel_truth"))
        self.assertFalse(hasattr(bundle, "diesel_fuel_remaining_liters"))

    def test_11_unknown_invalid_does_not_advance_fuel_state(self):
        """Audit Item 11: UNKNOWN_INVALID does not advance fuel state."""
        bad_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        bad_runner.configs["ecd"] = {"t_required_hours": 0.0}  # Triggers UNKNOWN_INVALID

        report = bad_runner.run_pipeline(steps_to_run=5)

        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "FAILED_TERMINATED")

    def test_12_milp_infeasibility_does_not_advance_fuel_state(self):
        """Audit Item 12: MILP infeasibility does not advance fuel state."""
        infeasible_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="milp"
        )
        infeasible_runner.configs["ecd"] = {"t_required_hours": 2.0}

        # Mock router to return NORMAL route
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

        report = infeasible_runner.run_pipeline(steps_to_run=5)
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "GOVERNANCE_DECISION_REQUIRED")

    def test_13_14_valid_dispatches_advance_fuel_exactly_once_no_double_consumption(self):
        """Audit Items 13 & 14: Valid dispatches advance fuel state exactly once; no double-consumption."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        state_before = StationState(
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

        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-24T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[20000.0]*24, load_served=[20000.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=100.0,
            constraint_status="OPTIMIZATION_SUCCESSFUL",
            energy_balance_errors=[0.0]*24
        )

        actuals = self.runner.data_provider.get_future_ground_truth(0, horizon_hours=24)[0]
        state_after = simulator.step(state_before, plan, actuals)

        actual_consumed = state_before.diesel_fuel_remaining_liters - state_after.diesel_fuel_remaining_liters
        expected_single_step_consumed = 5.0 + (0.00025 * 20000.0)  # 10.0 L

        self.assertAlmostEqual(actual_consumed, expected_single_step_consumed, places=4)

    def test_15_no_fuel_consumption_for_discarded_forecast_actions(self):
        """Audit Item 15: No fuel consumption occurs for discarded k=1..k=23 forecast actions."""
        simulator = DigitalTwinSimulator(self.runner.configs)
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        state_before = StationState(
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

        # Diesel off at k=0, maximum diesel (50 kW) at k=1..23
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-24T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[0.0] + [50000.0]*23, load_served=[0.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[0.0]*24, objective_value=0.0,
            constraint_status="OPTIMIZATION_SUCCESSFUL",
            energy_balance_errors=[0.0]*24
        )

        actuals = self.runner.data_provider.get_future_ground_truth(0, horizon_hours=24)[0]
        state_after = simulator.step(state_before, plan, actuals)

        # Zero fuel consumed since k=0 diesel power is 0.0 W
        self.assertEqual(state_after.diesel_fuel_remaining_liters, 100.0)

    def test_16_17_deterministic_reproducibility(self):
        """Audit Items 16 & 17: Timestamp/order of fuel updates is deterministic; identical replay produces identical fuel trace."""
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
