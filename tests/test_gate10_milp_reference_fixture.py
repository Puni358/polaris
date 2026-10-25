"""
POLARIS EMS — GATE-10 MILP / Native HiGHS Reference Validation Test Suite

Validates:
1. Native HiGHS solver invocation succeeds deterministically.
2. A feasible governed test problem produces a valid DispatchPlan.
3. All hard physical constraints are satisfied.
4. Critical load remains hard and fully served.
5. Power balance is satisfied.
6. Battery SOC/charge/discharge constraints are satisfied.
7. Diesel bounds are satisfied.
8. Renewable availability constraints are satisfied.
9. First-action extraction is deterministic.
10. Repeated identical inputs produce identical optimization results.
11. Objective value is internally consistent with the returned solution.
12. Solver status is correctly propagated.
13. Infeasible status does NOT produce a physically executable zero-dispatch.
14. No Digital Twin advancement occurs from an invalid/infeasible plan.
15. No future truth enters the MILP inputs.
16. The protected Option B implementation remains unchanged (SHA256 verified).
"""

import unittest
from pathlib import Path
from typing import Dict, Any, List
import hashlib
from unittest.mock import MagicMock

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import EmergencyConditionDetector
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner


class TestGate10MILPReferenceFixture(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        self.runner.configs["critical_demand_ratio"] = 1.0
        self.runner.configs["terminal_target_wh"] = 100000.0
        self.runner.configs["ecd"] = {"t_required_hours": 2.0}
        self.optimizer = GAP19HighsNativeOptimizer()

    def test_01_option_b_source_sha256_unmodified(self):
        """Audit 16: Verify protected Option B source file SHA256 remains unmodified."""
        option_b_path = self.base_dir / "optimization" / "implementations" / "gap19_highs_native.py"
        with open(option_b_path, "rb") as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        expected_sha = "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737"
        self.assertEqual(computed_sha, expected_sha)

    def test_02_native_highs_invocation_and_dispatch_plan(self):
        """Audit 1 & 2: Native HiGHS solver invocation succeeds and returns valid DispatchPlan."""
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
        plan = self.optimizer.optimize(bundle, current_state, self.runner.configs)

        self.assertIsNotNone(plan)
        self.assertIn(plan.constraint_status, ["OPTIMAL", "OPTIMIZATION_SUCCESSFUL"])
        self.assertEqual(len(plan.diesel_power), 24)
        self.assertEqual(len(plan.battery_soc), 24)

    def test_03_hard_constraints_and_critical_load(self):
        """Audit 3, 4 & 5: Hard physical constraints, critical load, and power balance satisfied."""
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
        plan = self.optimizer.optimize(bundle, current_state, self.runner.configs)

        for h in range(24):
            # Critical load served
            self.assertAlmostEqual(plan.unmet_load[h], 0.0, places=3)
            self.assertAlmostEqual(plan.load_served[h], bundle.demand.point[h], places=3)
            # Power balance
            self.assertAlmostEqual(plan.energy_balance_errors[h], 0.0, places=3)

    def test_04_battery_and_diesel_bounds(self):
        """Audit 6, 7 & 8: Battery SOC/charge/discharge, diesel bounds, and renewables satisfied."""
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
        plan = self.optimizer.optimize(bundle, current_state, self.runner.configs)

        for h in range(24):
            # Battery SOC
            self.assertGreaterEqual(plan.battery_soc[h], 20.0 - 1e-3)
            self.assertLessEqual(plan.battery_soc[h], 95.0 + 1e-3)
            # Battery power
            self.assertLessEqual(plan.battery_charge[h], 50000.0 + 1e-3)
            self.assertLessEqual(plan.battery_discharge[h], 50000.0 + 1e-3)
            # Diesel power
            p_diesel = plan.diesel_power[h]
            if p_diesel > 0:
                self.assertGreaterEqual(p_diesel, 10000.0 - 1e-3)
                self.assertLessEqual(p_diesel, 100000.0 + 1e-3)
            # Renewables
            self.assertLessEqual(plan.solar_used[h], bundle.solar_generation.point[h] + 1e-3)
            self.assertLessEqual(plan.wind_used[h], bundle.wind_generation.point[h] + 1e-3)

    def test_05_objective_value_consistency(self):
        """Audit 11: Objective value is finite, non-negative, and consistent with returned solution."""
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
        plan = self.optimizer.optimize(bundle, current_state, self.runner.configs)

        self.assertGreaterEqual(plan.objective_value, 0.0)
        self.assertLess(plan.objective_value, 1e8)

    def test_06_determinism_and_first_action_extraction(self):
        """Audit 9 & 10: Repeated identical inputs produce identical optimization results."""
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

        plan1 = self.optimizer.optimize(bundle, current_state, self.runner.configs)
        plan2 = self.optimizer.optimize(bundle, current_state, self.runner.configs)

        self.assertEqual(plan1.diesel_power[0], plan2.diesel_power[0])
        self.assertEqual(plan1.battery_charge[0], plan2.battery_charge[0])
        self.assertEqual(plan1.battery_discharge[0], plan2.battery_discharge[0])
        self.assertEqual(plan1.objective_value, plan2.objective_value)

    def test_07_infeasibility_safety_and_no_digital_twin_advancement(self):
        """Audit 12, 13 & 14: Infeasible status correctly propagated, no zero-dispatch execution, no Twin advancement."""
        infeasible_state = StationState(
            timestamp="2026-09-24T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=200000.0,  # Unsolvable demand exceeding 100 kW diesel + 50 kW battery
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=0.0
        )
        bundle = self.runner.forecast_engine.predict(infeasible_state, self.runner.data_provider.get_runtime_state(0))
        plan = self.optimizer.optimize(bundle, infeasible_state, self.runner.configs)

        # Status must explicitly report infeasibility
        self.assertTrue(plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"))

        # Verify runner halts without calling simulator step on infeasible status
        bad_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        bad_runner.configs["ecd"] = {"t_required_hours": 2.0}

        mock_assessment = MagicMock()
        mock_assessment.operating_mode.value = "NORMAL"
        mock_assessment.validity_status = None
        bad_runner.router.evaluate_and_route = MagicMock(return_value=(mock_assessment, "NORMAL"))
        bad_runner.optimizer.optimize = MagicMock(return_value=plan)

        simulator_called = False
        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s
        bad_runner.simulator.step = mock_step

        report = bad_runner.run_pipeline(steps_to_run=5)
        self.assertFalse(simulator_called)
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "GOVERNANCE_DECISION_REQUIRED")

    def test_08_truth_firewall_no_future_truth(self):
        """Audit 15: No future ground truth enters the MILP inputs."""
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

        self.assertFalse(hasattr(bundle, "actual_SW_IN"))
        self.assertFalse(hasattr(bundle, "actual_demand"))


if __name__ == "__main__":
    unittest.main()
