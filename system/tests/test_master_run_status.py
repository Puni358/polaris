"""
Focused regression tests for the campaign-status fix in
system/orchestration/master.py (CampaignMaster.compute_run_status).

Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 3):
ems/reports/rt01_runtime_fixes/SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md Section 1/5 found that a worker
subprocess exiting nonzero (recorded in workers_info as
status == "FAILED_EXIT_{code}") did not change the persisted
CAMPAIGN_STATUS.json's run-level "status" field, which was computed only from
self.interrupted -- so a campaign with a crashed worker cell still reported
"COMPLETED".

compute_run_status is a pure, side-effect-free staticmethod extracted from
CampaignMaster.execute_campaign specifically so this fix can be verified here
without starting any real worker subprocess, dispatch campaign, or solver --
no CampaignMaster instance, system_dir, or run_dir is needed for these tests.
"""
import unittest

from system.orchestration.master import CampaignMaster


class TestComputeRunStatus(unittest.TestCase):
    def test_all_workers_completed_and_not_interrupted_is_completed(self):
        workers_info = [
            {"cell_id": "cell_a2", "status": "COMPLETED"},
            {"cell_id": "cell_b", "status": "COMPLETED"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(False, workers_info)
        self.assertEqual(run_status, "COMPLETED")
        self.assertEqual(failed, [])

    def test_crashed_worker_is_not_reported_as_completed(self):
        """This is the exact defect the audit found: a crashed worker (nonzero
        subprocess exit) must not leave the campaign status COMPLETED."""
        workers_info = [
            {"cell_id": "cell_a2", "status": "COMPLETED"},
            {"cell_id": "cell_b", "status": "FAILED_EXIT_1"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(False, workers_info)
        self.assertNotEqual(run_status, "COMPLETED")
        self.assertEqual(run_status, "FAILED_WORKER_EXIT")
        self.assertEqual(failed, ["cell_b"])

    def test_interruption_takes_precedence_over_a_completed_worker_set(self):
        workers_info = [
            {"cell_id": "cell_a2", "status": "COMPLETED"},
            {"cell_id": "cell_b", "status": "COMPLETED"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(True, workers_info)
        self.assertEqual(run_status, "INTERRUPTED")
        self.assertEqual(failed, [])

    def test_interruption_and_worker_failure_both_present_reports_interrupted(self):
        """Distinctness requirement: when both occurred, the master's own
        deliberate interruption is the reported cause, but the failed-worker
        list is still surfaced for diagnosis, never silently dropped."""
        workers_info = [
            {"cell_id": "cell_a2", "status": "FAILED_EXIT_137"},
            {"cell_id": "cell_b", "status": "COMPLETED"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(True, workers_info)
        self.assertEqual(run_status, "INTERRUPTED")
        self.assertEqual(failed, ["cell_a2"])

    def test_multiple_failed_workers_are_all_listed(self):
        workers_info = [
            {"cell_id": "cell_a2", "status": "FAILED_EXIT_1"},
            {"cell_id": "cell_b", "status": "FAILED_EXIT_2"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(False, workers_info)
        self.assertEqual(run_status, "FAILED_WORKER_EXIT")
        self.assertEqual(failed, ["cell_a2", "cell_b"])

    def test_still_running_worker_status_is_not_treated_as_failed(self):
        """A worker still polling as RUNNING (no exit code yet) must not be
        mistaken for a failure."""
        workers_info = [
            {"cell_id": "cell_a2", "status": "RUNNING"},
            {"cell_id": "cell_b", "status": "COMPLETED"},
        ]
        run_status, failed = CampaignMaster.compute_run_status(False, workers_info)
        self.assertEqual(run_status, "COMPLETED")
        self.assertEqual(failed, [])

    def test_empty_workers_info_is_completed_when_not_interrupted(self):
        run_status, failed = CampaignMaster.compute_run_status(False, [])
        self.assertEqual(run_status, "COMPLETED")
        self.assertEqual(failed, [])


if __name__ == "__main__":
    unittest.main()
