"""
Focused regression tests for the dispatch-safety guard wiring into
system/evaluation/evaluator.py::EvaluationEngine.evaluate_ems_performance.

Scope: system/safety/reserve_policy_guard.py was implemented in a prior remediation
pass (see forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md) but was not yet wired into
the evaluation/result path. This file tests ONLY the wiring added in this pass
(ems/reports/rt01_runtime_fixes/SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md) -- it does not re-test
reserve_policy_guard's own internals (see system/tests/test_reserve_policy_guard.py
for that), and it never starts a dispatch campaign, touches live services, or
accesses sealed/restricted data: every plan here is a synthetic, hand-built dict.
"""
import unittest

from system.evaluation.evaluator import EvaluationEngine


def _base_plan(**overrides):
    ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
    plan = {
        "constraint_status": "OPTIMAL",
        "timestamps": ts,
        "solar_used": [0.0] * 24,
        "wind_used": [0.0] * 24,
        "diesel_power": [0.0] * 24,
        "renewable_curtailment": [0.0] * 24,
        "unmet_load": [0.0] * 24,
        "load_served": [0.0] * 24,
        "flexible_load_schedule": [0.0] * 24,
        "battery_discharge": [0.0] * 24,
        "battery_soc": [60.0] * 24,
    }
    plan.update(overrides)
    return plan


_CONFIGS = {
    "diesel": {
        "base_fuel_consumption_l_per_h": 5.0,
        "marginal_fuel_consumption_l_per_wh": 0.00025,
        "fuel_cost_per_l": 2.50,
        "startup_cost": 15.0,
    },
    "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0},
}


class TestOptimalWithCriticalUnmetEnergy(unittest.TestCase):
    """Protocol item 6: OPTIMAL must not be presented as safe when critical load is unmet."""

    def test_optimal_with_nonzero_unmet_essential_is_flagged(self):
        plan = _base_plan(
            unmet_load=[500.0] * 24,       # total unmet (includes noncritical)
            unmet_essential=[120.0] * 24,  # critical-specific portion
        )
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]

        self.assertIn("unmet_essential", ds["critical_unmet_source"])
        self.assertAlmostEqual(ds["critical_unmet_total_wh"], 120.0 * 24, places=2)
        self.assertGreaterEqual(ds["optimal_but_unsafe_step_count"], 1)
        self.assertTrue(any("nonzero_critical_unmet_energy_wh" in r for r in ds["failure_reasons"]))
        self.assertFalse(ds["proposed_safety_gate_would_pass"])
        # Backward-compat field unchanged (still total unmet, mislabeled, documented)
        self.assertEqual(result["unmet_critical_load_kwh"], round(500.0 * 24 / 1000.0, 2))
        self.assertEqual(result["total_unmet_load_kwh"], result["unmet_critical_load_kwh"])
        self.assertIn("mislabeled", result["unmet_critical_load_kwh_label_warning"].lower())


class TestOptimalWithReserveShortfall(unittest.TestCase):
    """Protocol item 7: report measured reserve shortfall + AUTHORIZATION_REQUIRED, never invent a threshold."""

    def test_reserve_shortfall_is_surfaced_not_hidden(self):
        plan = _base_plan(reserve_shortfall=[250.0] * 24)
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]

        self.assertEqual(ds["reserve_shortfall_total_wh"], round(250.0 * 24, 2))
        self.assertIsNone(ds["reserve_shortfall_authorization_wh"])
        self.assertIn("AUTHORIZATION_REQUIRED", ds["reserve_shortfall_authorization_status"])
        # No ceiling authorized -> guard does not invent a pass/fail verdict on its own,
        # but the shortfall value itself must never be hidden or zeroed.
        self.assertNotEqual(ds["reserve_shortfall_total_wh"], 0.0)


class TestHardSocFloorViolation(unittest.TestCase):
    """Hard battery SOC floor violation must be detected, not hidden by a solver OPTIMAL status."""

    def test_soc_below_floor_is_flagged(self):
        # min_soc_pct=20%% of 200,000 Wh = 40,000 Wh floor. 10%% SOC => 20,000 Wh < floor.
        plan = _base_plan(battery_soc=[10.0] * 24)
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]

        self.assertTrue(ds["hard_soc_violation"])
        self.assertTrue(len(ds["hard_soc_violation_details"]) >= 1)
        self.assertTrue(any("hard minimum SOC floor" in d for d in ds["hard_soc_violation_details"]))

    def test_soc_above_floor_is_not_flagged(self):
        plan = _base_plan(battery_soc=[60.0] * 24)
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertFalse(ds["hard_soc_violation"])
        self.assertEqual(ds["hard_soc_violation_details"], [])


class TestMissingSafetyFieldsStayUnknown(unittest.TestCase):
    """Protocol item 4: a missing field must be reported UNKNOWN/NOT_VERIFIED, never silently zero."""

    def test_missing_reserve_shortfall_is_unknown_not_zero(self):
        plan = _base_plan()  # no 'reserve_shortfall' key at all
        self.assertNotIn("reserve_shortfall", plan)
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertEqual(ds["reserve_shortfall_total_wh"], "UNKNOWN_NOT_VERIFIED")

    def test_missing_battery_soc_skips_hard_soc_check_without_false_pass(self):
        plan = dict(_base_plan())
        del plan["battery_soc"]
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertFalse(ds["hard_soc_violation"])
        self.assertTrue(any("hard_soc_floor_check_skipped" in n for n in ds["notes"]))


class TestTotalVsCriticalUnmetReportedCorrectly(unittest.TestCase):
    """Protocol item 3: never label total unmet energy as critical-only without flagging the fallback."""

    def test_fallback_to_total_unmet_is_explicitly_labeled(self):
        plan = _base_plan(unmet_load=[300.0] * 24)  # no unmet_essential field
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]

        self.assertEqual(ds["critical_unmet_total_wh"], round(300.0 * 24, 2))
        self.assertIn("FALLBACK_TO_TOTAL_UNMET_LOAD", ds["critical_unmet_source"])
        self.assertIn("OVER-COUNTS", ds["critical_unmet_source"])

    def test_genuine_critical_specific_source_is_labeled_as_verified(self):
        plan = _base_plan(unmet_load=[300.0] * 24, unmet_essential=[50.0] * 24)
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]

        self.assertEqual(ds["critical_unmet_total_wh"], round(50.0 * 24, 2))
        self.assertIn("verified", ds["critical_unmet_source"])
        self.assertNotIn("FALLBACK", ds["critical_unmet_source"])
        # The legacy (mislabeled) field must still reflect TOTAL unmet, not critical-only.
        self.assertEqual(result["unmet_critical_load_kwh"], round(300.0 * 24 / 1000.0, 2))


class TestSolverInfeasibilityTimeoutFallback(unittest.TestCase):
    def test_infeasible_status_is_counted_as_solver_infeasible(self):
        plan = _base_plan(constraint_status="OPTIMIZATION_INFEASIBLE: kInfeasible")
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertEqual(ds["solver_infeasible_step_count"], 1)
        self.assertEqual(result["constraint_violations_count"], 1)  # existing behavior unchanged
        self.assertTrue(any("solver_infeasible" in r for r in ds["failure_reasons"]))

    def test_timeout_status_is_also_treated_as_infeasible(self):
        plan = _base_plan(constraint_status="OPTIMIZATION_INFEASIBLE: solver_timeout")
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertEqual(ds["solver_infeasible_step_count"], 1)


class TestSafeSyntheticPlanClassifiedCorrectly(unittest.TestCase):
    def test_fully_safe_plan_has_no_failure_reasons(self):
        plan = _base_plan(
            unmet_load=[0.0] * 24,
            unmet_essential=[0.0] * 24,
            reserve_shortfall=[0.0] * 24,
            battery_soc=[55.0] * 24,
        )
        result = EvaluationEngine.evaluate_ems_performance([plan], _CONFIGS)
        ds = result["dispatch_safety"]
        self.assertFalse(ds["hard_soc_violation"])
        self.assertEqual(ds["optimal_but_unsafe_step_count"], 0)
        self.assertEqual(ds["failure_reasons"], [])
        self.assertTrue(ds["proposed_safety_gate_would_pass"])


class TestArmAFixShapedRegression(unittest.TestCase):
    """
    Reproduces the documented Arm A_FIX failure mode at the evaluator layer: an
    OPTIMAL-status plan with lower diesel power but nonzero critical unmet energy
    must be flagged as unsafe, not reported as a clean win, purely because its
    diesel usage looks better than a baseline plan.
    """

    def test_lower_diesel_with_nonzero_critical_unmet_is_flagged_unsafe(self):
        control_plan = _base_plan(
            diesel_power=[40000.0] * 24,
            unmet_load=[0.0] * 24,
            unmet_essential=[0.0] * 24,
        )
        arm_a_fix_plan = _base_plan(
            diesel_power=[30000.0] * 24,   # LOWER diesel (looks like a fuel saving)
            unmet_load=[200.0] * 24,
            unmet_essential=[200.0] * 24,  # but genuinely higher critical unmet energy
        )

        control_result = EvaluationEngine.evaluate_ems_performance([control_plan], _CONFIGS)
        candidate_result = EvaluationEngine.evaluate_ems_performance([arm_a_fix_plan], _CONFIGS)

        self.assertLess(
            candidate_result["total_diesel_energy_kwh"], control_result["total_diesel_energy_kwh"]
        )
        ds = candidate_result["dispatch_safety"]
        self.assertGreater(ds["critical_unmet_total_wh"], 0.0)
        self.assertGreaterEqual(ds["optimal_but_unsafe_step_count"], 1)
        self.assertFalse(ds["proposed_safety_gate_would_pass"])

        # Directly cross-check with the guard's own Arm A_FIX regression detector,
        # using the exact historical numbers from the remediation report, to confirm
        # the two layers agree this pattern is a masked reliability regression.
        from system.safety import reserve_policy_guard
        regression = reserve_policy_guard.detect_reserve_regression_vs_baseline(
            baseline_critical_unmet_wh=329.35 * 1000.0,
            candidate_critical_unmet_wh=484.81 * 1000.0,
            baseline_diesel_l=10368.85,
            candidate_diesel_l=9204.24,
        )
        self.assertTrue(regression["is_fuel_savings_masking_reliability_regression"])
        self.assertFalse(regression["would_pass_proposed_gate"])


if __name__ == "__main__":
    unittest.main()
