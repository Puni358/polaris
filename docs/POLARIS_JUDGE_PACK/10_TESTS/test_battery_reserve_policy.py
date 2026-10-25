"""
POLARIS — Reserve/EBR Safety-Policy Validation Test Suite
============================================================
N6 Operational Readiness Remediation, Section 4.

Covers: Arm A_FIX known failure mode (diesel saved, critical unmet load
increased ~47.2%), hard SOC-floor enforcement, missing/invalid uncertainty
forcing zero solar credit, unauthorized-credit fail-closed behavior,
reserve-unit mismatch detection, double-netting detection, solver
infeasibility surfacing, and low-solar/high-shortfall synthetic scenarios.

All fixtures are deterministic/synthetic. No production code, frozen
model, or governed reserve policy is modified or executed by this suite.
"""

from __future__ import annotations

import unittest

from system.safety.reserve_policy_guard import (
    AuthorizationRequiredError,
    ReservePolicyViolation,
    SAFETY_GATE_REGISTRY,
    assert_no_double_netting,
    compute_bounded_solar_credit,
    detect_reserve_regression_vs_baseline,
    evaluate_dispatch_safety,
    validate_hard_soc_floor,
    validate_reserve_units_consistent,
)


class TestArmAFixRegressionDetection(unittest.TestCase):
    def test_01_arm_a_fix_reported_numbers_flagged_as_masking_pattern(self):
        """
        Reproduces the historical Arm A_FIX finding using the EXACT reported
        numbers (Control 10,368.85 L / 329.35 kWh unmet; Arm A_FIX 9,204.24 L /
        484.81 kWh unmet) and asserts the guard detects the
        fuel-savings-masking-a-reliability-regression pattern, and that the
        proposed gate ("critical unmet must not exceed baseline") would fail.
        """
        result = detect_reserve_regression_vs_baseline(
            baseline_critical_unmet_wh=329.35 * 1000.0,
            candidate_critical_unmet_wh=484.81 * 1000.0,
            baseline_diesel_l=10368.85,
            candidate_diesel_l=9204.24,
        )
        self.assertTrue(result["is_fuel_savings_masking_reliability_regression"])
        self.assertFalse(result["would_pass_proposed_gate"])
        self.assertFalse(result["gate_formally_authorized"])
        self.assertAlmostEqual(result["diesel_saved_pct"], 11.233, places=1)
        self.assertAlmostEqual(result["unmet_increase_pct"], 47.2, delta=0.5)

    def test_02_candidate_that_improves_both_fuel_and_reliability_passes(self):
        result = detect_reserve_regression_vs_baseline(
            baseline_critical_unmet_wh=329.35 * 1000.0,
            candidate_critical_unmet_wh=300.0 * 1000.0,
            baseline_diesel_l=10368.85,
            candidate_diesel_l=9204.24,
        )
        self.assertFalse(result["is_fuel_savings_masking_reliability_regression"])
        self.assertTrue(result["would_pass_proposed_gate"])

    def test_03_registry_marks_gate_unauthorized(self):
        gate = SAFETY_GATE_REGISTRY["critical_unmet_not_worse_than_baseline"]
        self.assertFalse(gate.authorized)
        self.assertIn("AUTHORIZATION_REQUIRED", gate.proposed_threshold_note)


class TestHardSocFloor(unittest.TestCase):
    def test_04_soc_within_floor_passes(self):
        validate_hard_soc_floor([20000, 18000, 16000, 15500], min_e_wh=15000.0)  # no raise

    def test_05_soc_below_floor_raises(self):
        with self.assertRaises(ReservePolicyViolation) as cm:
            validate_hard_soc_floor([20000, 14999.0, 16000], min_e_wh=15000.0)
        self.assertIn("timesteps [1]", str(cm.exception))


class TestUnitConsistency(unittest.TestCase):
    def test_06_matching_unit_passes(self):
        validate_reserve_units_consistent("ebr_target", 15000.0, "Wh")  # no raise

    def test_07_mismatched_unit_fails_closed(self):
        with self.assertRaises(ReservePolicyViolation):
            validate_reserve_units_consistent("ebr_target", 15.0, "kWh")

    def test_08_power_unit_mistakenly_used_for_energy_fails_closed(self):
        with self.assertRaises(ReservePolicyViolation):
            validate_reserve_units_consistent("s_J2_slack", 5000.0, "W")


class TestDoubleNetting(unittest.TestCase):
    def test_09_single_application_passes(self):
        assert_no_double_netting(True, False, False)  # no raise

    def test_10_double_application_fails_closed(self):
        with self.assertRaises(ReservePolicyViolation):
            assert_no_double_netting(True, True, False)

    def test_11_triple_application_fails_closed(self):
        with self.assertRaises(ReservePolicyViolation):
            assert_no_double_netting(True, True, True)


class TestBoundedSolarCredit(unittest.TestCase):
    def test_12_no_authorization_fails_closed(self):
        with self.assertRaises(AuthorizationRequiredError):
            compute_bounded_solar_credit(
                forecast_lower_wh=5000.0,
                uncertainty_is_valid=True,
                forecast_is_fresh=True,
                authorized_max_credit_fraction=None,
                governed_reserve_target_wh=15000.0,
            )

    def test_13_invalid_uncertainty_forces_zero_credit_even_if_authorized(self):
        credit = compute_bounded_solar_credit(
            forecast_lower_wh=5000.0,
            uncertainty_is_valid=False,
            forecast_is_fresh=True,
            authorized_max_credit_fraction=0.5,
            governed_reserve_target_wh=15000.0,
        )
        self.assertEqual(credit, 0.0)

    def test_14_stale_forecast_forces_zero_credit(self):
        credit = compute_bounded_solar_credit(
            forecast_lower_wh=5000.0,
            uncertainty_is_valid=True,
            forecast_is_fresh=False,
            authorized_max_credit_fraction=0.5,
            governed_reserve_target_wh=15000.0,
        )
        self.assertEqual(credit, 0.0)

    def test_15_valid_fresh_credit_is_bounded_by_authorized_fraction(self):
        # forecast_lower_wh exceeds the authorized cap -> credit clamps to the cap.
        credit = compute_bounded_solar_credit(
            forecast_lower_wh=20000.0,
            uncertainty_is_valid=True,
            forecast_is_fresh=True,
            authorized_max_credit_fraction=0.2,
            governed_reserve_target_wh=15000.0,
        )
        self.assertEqual(credit, 3000.0)  # 0.2 * 15000

    def test_16_out_of_range_fraction_fails_closed(self):
        with self.assertRaises(ReservePolicyViolation):
            compute_bounded_solar_credit(
                forecast_lower_wh=1000.0,
                uncertainty_is_valid=True,
                forecast_is_fresh=True,
                authorized_max_credit_fraction=1.5,
                governed_reserve_target_wh=15000.0,
            )


class TestEvaluateDispatchSafety(unittest.TestCase):
    def _base_plan(self, **overrides):
        plan = {
            "constraint_status": "OPTIMAL",
            "battery_soc": [20000.0] * 24,
            "unmet_essential": [0.0] * 24,
            "reserve_shortfall": [0.0] * 24,
        }
        plan.update(overrides)
        return plan

    def test_17_clean_plan_passes(self):
        result = evaluate_dispatch_safety(self._base_plan(), min_e_wh=15000.0)
        self.assertTrue(result.passed)
        self.assertFalse(result.hard_soc_violation)
        self.assertFalse(result.solver_infeasible)

    def test_18_solver_infeasible_surfaced_never_hidden(self):
        plan = self._base_plan(constraint_status="OPTIMIZATION_INFEASIBLE: INFEASIBLE")
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertFalse(result.passed)
        self.assertTrue(result.solver_infeasible)
        self.assertTrue(any("solver_infeasible" in r for r in result.failure_reasons))

    def test_19_hard_soc_violation_raises(self):
        plan = self._base_plan(battery_soc=[20000.0, 10000.0] + [20000.0] * 22)
        with self.assertRaises(ReservePolicyViolation):
            evaluate_dispatch_safety(plan, min_e_wh=15000.0)

    def test_20_nonzero_critical_unmet_flagged(self):
        plan = self._base_plan(unmet_essential=[0.0] * 20 + [500.0, 0.0, 0.0, 0.0])
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertFalse(result.passed)
        self.assertEqual(result.critical_unmet_total_wh, 500.0)

    def test_21_missing_unmet_essential_falls_back_with_note(self):
        plan = self._base_plan()
        del plan["unmet_essential"]
        plan["unmet_load"] = [0.0] * 23 + [100.0]
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertEqual(result.critical_unmet_total_wh, 100.0)
        self.assertTrue(any("falls back to TOTAL unmet_load" in n for n in result.notes))

    def test_22_reserve_shortfall_without_authorization_reported_not_failed(self):
        plan = self._base_plan(reserve_shortfall=[1000.0] + [0.0] * 23)
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertEqual(result.reserve_shortfall_total_wh, 1000.0)
        self.assertFalse(result.reserve_violation)
        self.assertTrue(any("AUTHORIZATION_REQUIRED" in n for n in result.notes))

    def test_23_reserve_shortfall_exceeding_authorized_ceiling_violates(self):
        plan = self._base_plan(reserve_shortfall=[1000.0] + [0.0] * 23)
        result = evaluate_dispatch_safety(
            plan, min_e_wh=15000.0, reserve_shortfall_authorization_wh=500.0
        )
        self.assertTrue(result.reserve_violation)
        self.assertFalse(result.passed)

    def test_24_low_solar_high_ramp_synthetic_scenario_flags_both_unmet_and_reserve(self):
        """Synthetic low-solar/ramp-condition fixture: nonzero critical unmet AND reserve shortfall."""
        plan = self._base_plan(
            unmet_essential=[0.0] * 18 + [250.0, 400.0, 150.0, 0.0, 0.0, 0.0],
            reserve_shortfall=[0.0] * 18 + [2000.0, 3500.0, 1200.0, 0.0, 0.0, 0.0],
        )
        result = evaluate_dispatch_safety(
            plan, min_e_wh=15000.0, reserve_shortfall_authorization_wh=1000.0
        )
        self.assertFalse(result.passed)
        self.assertTrue(result.reserve_violation)
        self.assertEqual(result.critical_unmet_total_wh, 800.0)


class TestReserveShortfallTotalStaysUnknownWhenAbsent(unittest.TestCase):
    """
    Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 1):
    SafetyEvaluationResult.reserve_shortfall_total_wh must represent "unknown"
    (None) when the plan does not contain 'reserve_shortfall' at all -- mirroring
    critical_unmet_total_wh's existing Optional[float]/None handling -- instead of
    the previous numeric 0.0 default, which could be misread by any future caller
    as a verified "no shortfall" finding for a plan that simply never populated
    the field.
    """

    def _base_plan(self, **overrides):
        plan = {
            "constraint_status": "OPTIMAL",
            "battery_soc": [20000.0] * 24,
            "unmet_essential": [0.0] * 24,
            "reserve_shortfall": [0.0] * 24,
        }
        plan.update(overrides)
        return plan

    def test_25_missing_reserve_shortfall_is_none_not_zero(self):
        plan = self._base_plan()
        del plan["reserve_shortfall"]
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertIsNone(result.reserve_shortfall_total_wh)
        self.assertFalse(result.reserve_violation)
        self.assertTrue(
            any("reserve_shortfall not present on plan" in n for n in result.notes)
        )

    def test_26_present_reserve_shortfall_values_remain_numerically_unchanged(self):
        """A present reserve_shortfall field must still produce the exact same
        numeric total as before this fix -- only the MISSING case changed."""
        plan = self._base_plan(reserve_shortfall=[1000.0, 250.5] + [0.0] * 22)
        result = evaluate_dispatch_safety(plan, min_e_wh=15000.0)
        self.assertEqual(result.reserve_shortfall_total_wh, 1250.5)

        plan_all_zero = self._base_plan(reserve_shortfall=[0.0] * 24)
        result_zero = evaluate_dispatch_safety(plan_all_zero, min_e_wh=15000.0)
        # An explicitly-present all-zero shortfall is a VERIFIED zero, distinct
        # from the None/"unknown" case above, and must stay a numeric 0.0.
        self.assertEqual(result_zero.reserve_shortfall_total_wh, 0.0)
        self.assertIsNotNone(result_zero.reserve_shortfall_total_wh)

    def test_27_missing_reserve_shortfall_does_not_cause_crash_or_false_violation(self):
        """A missing reserve_shortfall must not raise, and must not be reported as
        a reserve_violation (there is nothing to compare a ceiling against)."""
        plan = self._base_plan()
        del plan["reserve_shortfall"]
        result = evaluate_dispatch_safety(
            plan, min_e_wh=15000.0, reserve_shortfall_authorization_wh=500.0
        )
        self.assertIsNone(result.reserve_shortfall_total_wh)
        self.assertFalse(result.reserve_violation)
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
