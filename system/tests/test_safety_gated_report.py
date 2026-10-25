"""
POLARIS — Safety-Gated Outcome Report Test Suite
===================================================
N6 Operational Readiness Remediation, Section 7.

Covers: no-silent-drop enforcement, proposed-vs-authorized gate
separation (all gates currently unauthorized), and gate evaluation
against the Arm A_FIX-shaped fixture (fuel saved, reliability worse).
"""

from __future__ import annotations

import unittest

from system.evaluation.safety_gated_report import (
    DroppedOriginError,
    OriginResult,
    build_report,
)


def _origin(oid, diesel_l, unmet_kwh, demand_kwh=1000.0, reserve_violations=0, feasible=True):
    return OriginResult(
        origin_id=oid,
        diesel_liters=diesel_l,
        critical_unmet_kwh=unmet_kwh,
        total_demand_kwh=demand_kwh,
        reserve_violations=reserve_violations,
        reserve_slack_wh=0.0,
        min_battery_soc_wh=15000.0,
        solver_feasible=feasible,
    )


class TestNoSilentDrop(unittest.TestCase):
    def test_01_dropped_baseline_origin_fails_closed(self):
        baseline = [_origin("o1", 100.0, 0.0)]
        candidate = [_origin("o1", 90.0, 0.0), _origin("o2", 90.0, 0.0)]
        with self.assertRaises(DroppedOriginError):
            build_report("control", "candidate", baseline, candidate, n_origins_attempted=2)

    def test_02_complete_results_pass(self):
        baseline = [_origin("o1", 100.0, 0.0), _origin("o2", 100.0, 0.0)]
        candidate = [_origin("o1", 90.0, 0.0), _origin("o2", 90.0, 0.0)]
        report = build_report("control", "candidate", baseline, candidate, n_origins_attempted=2)
        self.assertEqual(report.total_diesel_baseline_l, 200.0)
        self.assertEqual(report.total_diesel_candidate_l, 180.0)


class TestGateSeparation(unittest.TestCase):
    def test_03_all_authorized_gates_not_evaluated(self):
        baseline = [_origin("o1", 100.0, 0.0)]
        candidate = [_origin("o1", 90.0, 0.0)]
        report = build_report("control", "candidate", baseline, candidate, n_origins_attempted=1)
        self.assertTrue(len(report.authorized_gate_results) >= 4)
        for msg in report.authorized_gate_results.values():
            self.assertIn("NOT_EVALUATED", msg)

    def test_04_arm_a_fix_shaped_fixture_proposed_gate_would_fail(self):
        """Reproduces the Arm A_FIX pattern at report level: diesel improves, unmet load worsens."""
        baseline = [
            _origin("o1", 10368.85 / 2, 329.35 / 2),
            _origin("o2", 10368.85 / 2, 329.35 / 2),
        ]
        candidate = [
            _origin("o1", 9204.24 / 2, 484.81 / 2),
            _origin("o2", 9204.24 / 2, 484.81 / 2),
        ]
        report = build_report("Control", "Arm_A_FIX", baseline, candidate, n_origins_attempted=2)
        report.evaluate_gates()

        self.assertGreater(report.diesel_diff_pct, 0)  # diesel improved
        self.assertIn("WOULD_FAIL", report.proposed_gate_results["critical_unmet_not_worse_than_baseline"])
        self.assertEqual(report.pct_origins_with_increased_unmet, 100.0)
        self.assertIn("WOULD_FAIL", report.proposed_gate_results["unserved_energy_origin_failure_rate"])

    def test_05_clean_improvement_fixture_proposed_gates_would_pass(self):
        baseline = [_origin("o1", 1000.0, 50.0, demand_kwh=500.0)]
        candidate = [_origin("o1", 950.0, 20.0, demand_kwh=500.0)]
        report = build_report("Control", "Candidate", baseline, candidate, n_origins_attempted=1)
        report.evaluate_gates()
        self.assertIn("WOULD_PASS", report.proposed_gate_results["critical_unmet_not_worse_than_baseline"])


if __name__ == "__main__":
    unittest.main()
