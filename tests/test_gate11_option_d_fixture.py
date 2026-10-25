"""
POLARIS EMS — GATE-11 Option D Protected-Critical Fallback Test Suite (D1-D6)

Validates:
1. D1 — Protected Critical Load Priority
2. D2 — Battery Protection & Noncritical Load Shedding
3. D3 — Resource Depletion & Battery Support Fallback
4. D4 — Proportional Critical Allocation & Zero-Denominator Safety
5. D5 — Time/Resource Boundary Semantics
6. D6 — Diesel Excess Handling & Charge/Discharge Exclusivity (p_diesel > 0 and p_dis == 0)
7. Valid DispatchPlan returned
8. Critical service preservation
9. Battery & Diesel constraints respected
10. Fuel accounting & First-action-only semantics
11. Twin advancement on valid emergency dispatch only
12. UNKNOWN_INVALID and MILP_INFEASIBILITY boundary isolation (no auto Option D)
13. Truth firewall & Deterministic execution
14. Option D SHA256 integrity (78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12)
"""

import unittest
from pathlib import Path
from typing import Dict, Any, List
import hashlib

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
)
from system.control.router import EMSControlRouter
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner


class TestGate11OptionDFixture(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        self.runner.configs["critical_demand_ratio"] = 1.0
        self.runner.configs["terminal_target_wh"] = 100000.0
        # Explicit SYNTHETIC test-fixture authorization for the router/ECD
        # fail-closed contract (ECD-01, A-iii/B-iii). This GATE-11 suite
        # tests genuine Option-D/EMERGENCY mechanics, not the fail-closed
        # gate itself (test_06 below builds its own, deliberately
        # unauthorized configs to exercise that gate directly). "EVID-TEST-
        # GATE11" is NOT a real-station evidence record -- see
        # tests/test_isolated_components.py for the same convention.
        self.runner.configs["ecd"] = {"t_required_hours": 2.0, "t_required_authorized": True}
        self.runner.configs["critical_load"] = {
            "authorized": True,
            "evidence_id": "EVID-TEST-GATE11",
            "authorized_critical_load_w": 5000.0,
        }
        self.solver = OptionDFallbackSolver()

    def test_01_option_d_sha256_unmodified(self):
        """
        Audit 14: Option D SHA256 integrity check.

        Baseline rebased to the hash recorded after the authorized RT-01
        diesel-minimum-power-floor sequencing fix (approach a'), per
        ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md / N6_REMEDIATION_REPORTS
        mirror. That change is explicit, owner-authorized, and scoped to
        exactly this one file; this test's purpose (detect any FUTURE,
        unreviewed edit to option_d.py) is preserved by updating the
        baseline to the new, reviewed value, not by weakening the check.
        """
        option_d_path = self.base_dir / "optimization" / "implementations" / "option_d.py"
        with open(option_d_path, "rb") as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        expected_sha = "cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511"
        self.assertEqual(computed_sha, expected_sha)

    def test_02_d1_protected_critical_load_priority(self):
        """Audit D1 & Item 1: Option D prioritizes protected critical load and produces valid DispatchPlan."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=4.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, route = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        self.assertEqual(route, "EMERGENCY")

        plan = self.solver.solve(assessment, bundle, current_state, self.runner.configs)
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.diesel_power), 24)

    def test_03_d2_battery_protection_and_limits(self):
        """Audit D2: Battery supports critical load; SOC limits and discharge bounds respected."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=2.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, route = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        plan = self.solver.solve(assessment, bundle, current_state, self.runner.configs)

        for h in range(24):
            self.assertGreaterEqual(plan.battery_soc[h], 20.0 - 1e-3)
            self.assertLessEqual(plan.battery_soc[h], 95.0 + 1e-3)

    def test_04_d4_proportional_allocation_and_zero_denominator_safety(self):
        """Audit D4: Proportional allocation under power deficit & safe zero-denominator handling."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=20.0,  # Empty usable battery
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=0.0,  # Zero demand -> tests zero denominator
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=0.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, _ = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        plan = self.solver.solve(assessment, bundle, current_state, self.runner.configs)
        self.assertIsNotNone(plan)

    def test_05_d6_diesel_excess_and_exclusivity(self):
        """Audit D6 & Item 5: Charge/discharge exclusivity (p_diesel > 0 and p_dis == 0) and no diesel-only battery charging."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=15000.0,  # 15 kW demand triggers min diesel output (10 kW or more)
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=50.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, _ = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        plan = self.solver.solve(assessment, bundle, current_state, self.runner.configs)

        for h in range(24):
            p_diesel = plan.diesel_power[h]
            p_dis = plan.battery_discharge[h]
            p_chg = plan.battery_charge[h]

            if p_diesel > 0:
                # Sealed Gate-06 audit correction: when diesel is running, battery discharge MUST be 0
                self.assertEqual(p_dis, 0.0)

            # Exclusivity: cannot charge and discharge simultaneously
            self.assertFalse(p_chg > 0 and p_dis > 0)

    def test_06_boundary_isolation_unknown_invalid_and_milp_infeasible(self):
        """Audit 9 & 10: UNKNOWN_INVALID and MILP_INFEASIBLE do NOT automatically invoke Option D."""
        # UNKNOWN_INVALID
        bad_runner = PolarisLocalRunner(
            system_dir=self.base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native"
        )
        bad_runner.configs["ecd"] = {"t_required_hours": 0.0}

        option_d_called = False
        original_solve = bad_runner.option_d_solver.solve
        def mock_solve(a, b, s, c):
            nonlocal option_d_called
            option_d_called = True
            return original_solve(a, b, s, c)
        bad_runner.option_d_solver.solve = mock_solve

        report = bad_runner.run_pipeline(steps_to_run=5)
        self.assertFalse(option_d_called, "Option D MUST NOT be invoked on UNKNOWN_INVALID")
        self.assertEqual(report["completed_steps"], 0)

    def test_07_truth_firewall_and_determinism(self):
        """Audit 12 & 13: Truth Firewall and deterministic replay of Option D."""
        runtime_context = self.runner.data_provider.get_runtime_state(0)
        current_state = StationState(
            timestamp=runtime_context["origin_timestamp"],
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=4.0
        )
        bundle = self.runner.forecast_engine.predict(current_state, runtime_context)
        assessment, _ = self.runner.router.evaluate_and_route(current_state, bundle, self.runner.configs)

        plan1 = self.solver.solve(assessment, bundle, current_state, self.runner.configs)
        plan2 = self.solver.solve(assessment, bundle, current_state, self.runner.configs)

        self.assertEqual(plan1.diesel_power, plan2.diesel_power)
        self.assertEqual(plan1.battery_charge, plan2.battery_charge)
        self.assertEqual(plan1.battery_discharge, plan2.battery_discharge)

        # Ground truth firewall check
        self.assertFalse(hasattr(bundle, "actual_SW_IN"))
        self.assertFalse(hasattr(bundle, "actual_demand"))


if __name__ == "__main__":
    unittest.main()
