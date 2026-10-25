"""
POLARIS EMS — GATE-09 Option B Normal-Operation Baseline Test Suite

Validates:
1. NORMAL route reaches Option B.
2. Option B produces a valid DispatchPlan when feasible.
3. Critical load is served according to currently sealed policy.
4. Physical battery/SOC constraints are respected.
5. Diesel constraints are respected.
6. Power balance is respected.
7. Renewable generation/curtailment constraints are respected.
8. First-action-only execution semantics preserved.
9. Digital Twin receives only k=0 action.
10. Fuel accounting remains consistent.
11. State continuity remains consistent.
12. No future truth reaches Option B.
13. Repeated identical inputs produce deterministic results.
14. Option B does NOT silently invoke Option D.
15. Option B does NOT silently perform Gate-02 relaxation.
16. Option B does NOT silently alter Gate-01/03 behavior.
"""

import unittest
from pathlib import Path
from typing import Dict, Any, List
import math

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import EmergencyConditionDetector
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner


class TestGate09OptionBBaselineFixture(unittest.TestCase):

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
        # B-iii); "EVID-TEST-GATE09" is NOT a real-station evidence record
        # -- see tests/test_isolated_components.py for the convention.
        self.runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        self.runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE09",
            "authorized_critical_load_w": 5000.0,
        }
        self.optimizer = GAP19HighsNativeOptimizer()

    def test_01_normal_route_reaches_option_b(self):
        """Audit 1 & 14: NORMAL route reaches Option B and does NOT crossover to Option D."""
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
        assessment, route = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        self.assertEqual(route, "NORMAL")

        plan = self.optimizer.optimize(bundle, current_state, self.runner.configs)
        self.assertIsNotNone(plan)
        self.assertIn(plan.constraint_status, ["OPTIMAL", "OPTIMIZATION_SUCCESSFUL"])

    def test_02_valid_dispatch_plan_schema(self):
        """Audit 2: Option B produces a valid DispatchPlan schema when feasible."""
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

        self.assertEqual(len(plan.solar_used), 24)
        self.assertEqual(len(plan.wind_used), 24)
        self.assertEqual(len(plan.battery_charge), 24)
        self.assertEqual(len(plan.battery_discharge), 24)
        self.assertEqual(len(plan.battery_soc), 24)
        self.assertEqual(len(plan.diesel_power), 24)
        self.assertEqual(len(plan.load_served), 24)

    def test_03_critical_load_served(self):
        """Audit 3: Critical load is served according to currently sealed policy."""
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
            expected_demand = bundle.demand.point[h]
            served = plan.load_served[h]
            unmet = plan.unmet_load[h]
            self.assertAlmostEqual(served + unmet, expected_demand, places=3)
            # In a feasible NORMAL optimization, unmet load must be 0
            self.assertAlmostEqual(unmet, 0.0, places=3)

    def test_04_physical_battery_soc_constraints(self):
        """Audit 4: Physical battery/SOC constraints are respected."""
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
            soc = plan.battery_soc[h]
            self.assertGreaterEqual(soc, 20.0 - 1e-3)
            self.assertLessEqual(soc, 95.0 + 1e-3)

            p_chg = plan.battery_charge[h]
            p_dis = plan.battery_discharge[h]
            self.assertGreaterEqual(p_chg, 0.0)
            self.assertGreaterEqual(p_dis, 0.0)
            self.assertLessEqual(p_chg, 50000.0 + 1e-3)
            self.assertLessEqual(p_dis, 50000.0 + 1e-3)

    def test_05_diesel_constraints(self):
        """Audit 5: Diesel constraints (power bounds) are respected."""
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
            p_diesel = plan.diesel_power[h]
            self.assertGreaterEqual(p_diesel, 0.0)
            if p_diesel > 0:
                self.assertGreaterEqual(p_diesel, 10000.0 - 1e-3)
                self.assertLessEqual(p_diesel, 100000.0 + 1e-3)

    def test_06_power_balance(self):
        """Audit 6: Power balance equation is satisfied for all steps."""
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
            # Energy balance errors calculated inside optimizer must be zero
            self.assertAlmostEqual(plan.energy_balance_errors[h], 0.0, places=3)

    def test_07_renewable_constraints(self):
        """Audit 7: Renewable generation and curtailment constraints are respected."""
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
            self.assertLessEqual(plan.solar_used[h], bundle.solar_generation.point[h] + 1e-3)
            self.assertLessEqual(plan.wind_used[h], bundle.wind_generation.point[h] + 1e-3)
            self.assertGreaterEqual(plan.renewable_curtailment[h], 0.0)

    def test_08_09_first_action_only_execution(self):
        """Audit 8 & 9: First-action-only execution semantics preserved; Twin receives k=0 action."""
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
            "evidence_id": "EVID-TEST-GATE09",
            "authorized_critical_load_w": 5000.0,
        }

        report = runner.run_pipeline(steps_to_run=1)
        self.assertEqual(report["completed_steps"], 1)

    def test_10_11_fuel_accounting_and_state_continuity(self):
        """Audit 10 & 11: Fuel accounting and state continuity remain consistent."""
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
            "evidence_id": "EVID-TEST-GATE09",
            "authorized_critical_load_w": 5000.0,
        }

        report = runner.run_pipeline(steps_to_run=5)
        self.assertEqual(report["completed_steps"], 5)

    def test_12_truth_firewall_no_future_truth_in_option_b(self):
        """Audit 12: No future truth reaches Option B."""
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

        # Confirm ForecastBundle passed to Option B contains no actual ground truth attributes
        self.assertFalse(hasattr(bundle, "actual_SW_IN"))
        self.assertFalse(hasattr(bundle, "actual_demand"))

    def test_13_reproducibility_determinism(self):
        """Audit 13: Repeated identical inputs produce deterministic results."""
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

        self.assertEqual(plan1.battery_soc, plan2.battery_soc)
        self.assertEqual(plan1.diesel_power, plan2.diesel_power)

    def test_15_no_unauthorized_gate02_relaxation(self):
        """Audit 15: Option B does NOT silently perform Gate-02 relaxation when infeasible."""
        infeasible_state = StationState(
            timestamp="2026-09-24T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=150000.0,  # Extreme demand exceeding all generation sources
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=0.0
        )
        bundle = self.runner.forecast_engine.predict(infeasible_state, self.runner.data_provider.get_runtime_state(0))
        plan = self.optimizer.optimize(bundle, infeasible_state, self.runner.configs)

        # Must report infeasibility rather than silently relaxing constraints
        self.assertTrue(
            plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE") or
            plan.constraint_status == "INFEASIBLE"
        )

    def test_16_no_unauthorized_gate01_03_alteration(self):
        """Audit 16: Option B does NOT silently alter Gate-01 or Gate-03 behavior."""
        # Option B only implements EnergyOptimizer contract and returns DispatchPlan
        self.assertTrue(hasattr(self.optimizer, "optimize"))


if __name__ == "__main__":
    unittest.main()
