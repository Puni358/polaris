"""
Focused regression tests for the dispatch-safety guard wiring into
system/orchestration/worker.py (CampaignWorker).

These tests construct a REAL CampaignWorker (fast: only loads yaml configs and the
canonical POLARIS_HYBRID_FIXTURE_H1_0 fixture already present in this repository; no
MILP solve happens during construction). To keep every test fast, deterministic, and
free of any live dispatch campaign, GAP19 solve, or network access, the single
per-step dependency that would otherwise invoke the HiGHS solver
(`self.optimizer.optimize`) and the router (`self.router.evaluate_and_route`) are
monkeypatched on the instance to return a hand-built, synthetic DispatchPlan /
fixed "NORMAL" route. This exercises the REAL worker.py wiring code added in this
remediation pass (unit conversion, counters, step-record persistence, final-result
propagation) without starting a dispatch campaign or touching restricted data.

`system.simulation.simulator.DigitalTwinSimulator.step` is NOT patched: it runs for
real, which is why every synthetic plan below uses battery_charge=battery_discharge=0
(a physically no-op battery action), so the real simulator's own hard-SOC-bound check
never trips for reasons unrelated to what is under test here.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from system.orchestration.worker import CampaignWorker
from system.schemas.dispatch_plan import DispatchPlan

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = REPO_ROOT / "system"


def _make_plan(**overrides):
    ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
    kwargs = dict(
        schema_version="1.0.0",
        timestamps=ts,
        solar_used=[0.0] * 24,
        wind_used=[0.0] * 24,
        battery_charge=[0.0] * 24,
        battery_discharge=[0.0] * 24,
        battery_soc=[60.0] * 24,
        diesel_power=[20000.0] * 24,
        load_served=[20000.0] * 24,
        flexible_load_schedule=[0.0] * 24,
        renewable_curtailment=[0.0] * 24,
        unmet_load=[0.0] * 24,
        objective_value=1.0,
        constraint_status="OPTIMAL",
        energy_balance_errors=[0.0] * 24,
    )
    kwargs.update(overrides)
    return DispatchPlan(**kwargs)


class _WorkerTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="polaris_worker_safety_test_"))
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)

    def _make_worker(self, end_step=1, cell_id="cell_b_safety_test"):
        worker = CampaignWorker(
            run_id="safety_wiring_test_run",
            cell_id=cell_id,
            worker_id="worker_01",
            system_dir=SYSTEM_DIR,
            run_dir=self.tmp_dir,
            start_step=0,
            end_step=end_step,
            checkpoint_interval=500,
        )
        # Deterministic, solver-free routing for this isolated wiring test.
        worker.router.evaluate_and_route = lambda *a, **k: (None, "NORMAL")
        return worker


class TestWorkerPropagatesSafetyFindings(_WorkerTestBase):
    """Protocol item 8: safety findings must be visible in the final result AND the
    persisted trajectory record, never suppressed or reset."""

    def test_optimal_but_unsafe_step_is_propagated_to_final_result(self):
        plan = _make_plan(
            unmet_load=[300.0] * 24,
            unmet_essential=[300.0] * 24,
            reserve_shortfall=[150.0] * 24,
        )
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()

        self.assertEqual(result["status"], "COMPLETED")
        summary = result["safety_summary"]
        self.assertAlmostEqual(summary["unmet_critical_load_wh"], 300.0, places=2)
        self.assertAlmostEqual(summary["reserve_shortfall_total_wh"], 150.0, places=2)
        self.assertEqual(summary["optimal_but_unsafe_step_count"], 1)
        self.assertTrue(summary["any_safety_finding"])
        self.assertIn("AUTHORIZATION_REQUIRED", summary["reserve_shortfall_authorization_status"])

        # Also persisted to the on-disk trajectory record, not just the return value.
        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        self.assertEqual(persisted["safety_summary"]["optimal_but_unsafe_step_count"], 1)
        self.assertAlmostEqual(
            persisted["integrity_counters"]["unmet_critical_load_wh"], 300.0, places=2
        )
        self.assertEqual(persisted["records"][0]["safety"]["critical_unmet_source"], "unmet_essential")
        self.assertTrue(persisted["records"][0]["safety"]["optimal_but_unsafe"])

    def test_hard_soc_violation_is_propagated_to_final_result(self):
        # 10% of 200,000 Wh = 20,000 Wh < governed 20% floor (40,000 Wh).
        plan = _make_plan(battery_soc=[10.0] * 24)
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()
        summary = result["safety_summary"]
        self.assertEqual(summary["hard_soc_violation_count"], 1)
        self.assertTrue(summary["any_safety_finding"])

    def test_safe_plan_reports_no_findings(self):
        plan = _make_plan()  # all-zero unmet/reserve, safe SOC
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()
        summary = result["safety_summary"]
        self.assertEqual(summary["hard_soc_violation_count"], 0)
        self.assertEqual(summary["optimal_but_unsafe_step_count"], 0)
        self.assertEqual(summary["unmet_critical_load_wh"], 0.0)
        self.assertFalse(summary["any_safety_finding"])


class TestWorkerCriticalUnmetSourceFallback(_WorkerTestBase):
    """Protocol item 3: a plan without 'unmet_essential' must be tagged as a fallback,
    not silently treated as a genuine critical-specific measurement."""

    def test_missing_unmet_essential_is_counted_as_fallback(self):
        plan = _make_plan(unmet_load=[50.0] * 24)  # no unmet_essential
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()
        summary = result["safety_summary"]
        self.assertEqual(summary["unmet_critical_load_source_fallback_count"], 1)
        self.assertAlmostEqual(summary["unmet_critical_load_wh"], 50.0, places=2)


class TestWorkerMissingReserveShortfallStaysUnknown(_WorkerTestBase):
    """Protocol item 4: an absent reserve_shortfall field must not be silently
    treated as a verified zero shortfall."""

    def test_missing_reserve_shortfall_field_does_not_add_to_total(self):
        plan = _make_plan()  # DispatchPlan.reserve_shortfall defaults to None if omitted
        self.assertIsNone(plan.reserve_shortfall)
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()
        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        self.assertEqual(persisted["records"][0]["safety"]["reserve_shortfall_wh"], "UNKNOWN_NOT_VERIFIED")
        # The running total must not have been silently incremented by an unverified zero.
        self.assertEqual(result["safety_summary"]["reserve_shortfall_total_wh"], 0.0)


class TestWorkerSolverInfeasibleGate02Path(_WorkerTestBase):
    """Solver infeasibility / fallback: the Gate-02 relaxation re-solve path must still
    evaluate the FINAL adopted plan's safety, and a persistently infeasible step must
    halt (BLOCKED_INFEASIBLE) without ever reporting a safe/successful step record."""

    def test_initial_infeasible_then_relaxed_optimal_plan_is_evaluated(self):
        infeasible_plan = _make_plan(constraint_status="OPTIMIZATION_INFEASIBLE: kInfeasible")
        relaxed_plan = _make_plan(constraint_status="OPTIMAL", unmet_essential=[0.0] * 24)

        calls = {"n": 0}

        def fake_optimize(*a, **k):
            calls["n"] += 1
            return infeasible_plan if calls["n"] == 1 else relaxed_plan

        worker = self._make_worker()
        worker.optimizer.optimize = fake_optimize

        result = worker.execute()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["safety_summary"]["solver_infeasible_safety_flagged_count"], 0)

        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        # The step record reflects the FINAL (relaxed, OPTIMAL) plan, not the discarded
        # initial infeasible solve.
        self.assertEqual(persisted["records"][0]["safety"]["constraint_status"], "OPTIMAL")

    def test_persistently_infeasible_plan_halts_without_fabricating_a_safe_step(self):
        infeasible_plan = _make_plan(constraint_status="OPTIMIZATION_INFEASIBLE: kInfeasible")
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: infeasible_plan

        result = worker.execute()
        self.assertEqual(result["status"], "BLOCKED_INFEASIBLE")
        self.assertEqual(result["completed_cycles"], 0)
        # No fabricated "safe" step record was ever appended for this halted step.
        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        self.assertEqual(persisted["records"], [])


class _FakePlanDict:
    """
    Minimal stand-in for a DispatchPlan used ONLY to drive
    CampaignWorker._evaluate_step_dispatch_safety directly with a plan dict that
    has neither 'unmet_essential' nor 'unmet_load' -- a shape that cannot occur
    via a real, schema-valid DispatchPlan (unmet_load is a required constructor
    argument there), but which worker.py's own "unavailable" branch must still
    handle without silently reporting a verified zero (Policy D / bounded
    correctness fix item 2a).
    """

    def __init__(self, data):
        self._data = data

    def to_dict(self):
        return dict(self._data)


class TestWorkerCriticalUnmetUnavailableStaysUnknown(_WorkerTestBase):
    """Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 2a): when
    neither 'unmet_essential' nor 'unmet_load' is present on the plan dict reaching
    the worker's safety helper, critical_unmet_wh must be reported as unknown, not
    silently defaulted to a verified-looking 0.0."""

    def test_missing_both_fields_reports_unknown_not_zero(self):
        worker = self._make_worker()
        fake_plan = _FakePlanDict({
            "constraint_status": "OPTIMAL",
            "battery_soc": [60.0] * 24,
            # Deliberately omit both 'unmet_essential' and 'unmet_load'.
        })
        step_safety = worker._evaluate_step_dispatch_safety(fake_plan)
        self.assertEqual(step_safety["critical_unmet_source"], "unavailable")
        self.assertEqual(step_safety["critical_unmet_wh"], "UNKNOWN_NOT_VERIFIED")
        # An unknown critical-unmet measurement must not itself assert "unsafe".
        self.assertFalse(step_safety["optimal_but_unsafe"])


class TestWorkerOptimizerExceptionHandling(_WorkerTestBase):
    """Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 2b): an
    exception raised by the optimizer in the Cell B path must produce a structured,
    persisted, non-success worker result -- not an uncaught subprocess crash, and
    not mislabeled as OPTIMIZATION_INFEASIBLE."""

    def test_optimizer_exception_produces_structured_failure_result(self):
        worker = self._make_worker(end_step=5)

        def raising_optimize(*a, **k):
            raise ValueError("MISSING_GOVERNED_INPUT: terminal_target_wh is missing or unspecified.")

        worker.optimizer.optimize = raising_optimize

        result = worker.execute()  # must not raise

        self.assertEqual(result["status"], "FAILED_OPTIMIZATION_EXCEPTION")
        self.assertNotIn("INFEASIBLE", result["status"])
        diag = result["failure_diagnostics"]
        self.assertIsNotNone(diag)
        self.assertEqual(diag["exception_type"], "ValueError")
        self.assertIn("MISSING_GOVERNED_INPUT", diag["exception_message"])
        self.assertIn("Traceback", diag["traceback"])

        # Persisted reliably to disk as well, not just the in-memory return value.
        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        self.assertEqual(persisted["status"], "FAILED_OPTIMIZATION_EXCEPTION")
        self.assertEqual(persisted["failure_diagnostics"]["exception_type"], "ValueError")
        # No fabricated "safe" step record was appended for the failed step.
        self.assertEqual(persisted["records"], [])

    def test_optimizer_exception_does_not_crash_the_campaign_worker_process(self):
        """The worker's execute() call itself must never raise out to its caller
        (worker_cli.py makes a bare, unwrapped call to execute())."""
        worker = self._make_worker(end_step=3)
        worker.optimizer.optimize = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))

        try:
            result = worker.execute()
        except Exception as exc:  # pragma: no cover - this is exactly what must NOT happen
            self.fail(f"worker.execute() raised {type(exc).__name__}: {exc} instead of returning a structured result")

        self.assertEqual(result["status"], "FAILED_OPTIMIZATION_EXCEPTION")
        self.assertEqual(result["failure_diagnostics"]["exception_type"], "RuntimeError")

    def test_non_exception_statuses_have_no_failure_diagnostics(self):
        """Interruption and genuine success must retain their own distinct status
        and must not be contaminated with failure diagnostics from this new path."""
        plan = _make_plan()
        worker = self._make_worker()
        worker.optimizer.optimize = lambda *a, **k: plan

        result = worker.execute()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertIsNone(result["failure_diagnostics"])


class TestWorkerBaselineCellHasNoApplicableSafetyCheck(_WorkerTestBase):
    """Cell A (SIMPLE_DIESEL_ONLY_BASELINE) produces no MILP DispatchPlan; the safety
    wiring must mark the check as not-applicable rather than fabricating a pass."""

    def test_baseline_cell_step_marks_safety_not_applicable(self):
        worker = self._make_worker(cell_id="cell_a")
        result = worker.execute()
        self.assertEqual(result["status"], "COMPLETED")
        records_file = worker.cell_dir / "trajectory_records.json"
        with open(records_file) as f:
            persisted = json.load(f)
        self.assertFalse(persisted["records"][0]["safety"]["applicable"])
        self.assertFalse(persisted["safety_summary"]["any_safety_finding"])


if __name__ == "__main__":
    unittest.main()
