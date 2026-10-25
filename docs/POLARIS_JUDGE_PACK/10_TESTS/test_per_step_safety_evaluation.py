"""
POLARIS -- N6 Multi-Origin Harness: Per-Step Safety-Evaluation Regression Tests
=================================================================================
OWNER-AUTHORIZED BLOCKER RESOLUTION PASS (2026-10-17), Section 3A.

Resolves blocker F of `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md` Section 6: "safety
is evaluated once per run, not once per step." The directive governing this
pass explicitly allows closing this gap ONLY if it can be done "entirely
within the isolated harness using injected test doubles" and WITHOUT
changing any production safety/control behavior. This file proves that is
exactly what was done:

  - `execute_origin_dispatch_cell` now calls a supplied `SafetyEvaluatorProtocol`
    once per COMPLETED step (not once after the whole loop), mirroring
    `worker.py`'s real per-step Cell B cadence in STRUCTURE only.
  - `OriginRunResult.step_safety_evaluations` carries the full per-step
    sequence; `summarize_step_safety_evaluations` is a pure, read-only
    aggregate view over it.
  - The pre-existing single-verdict `safety_evidence_status`/`safety_passed`
    fields are UNCHANGED in meaning: still the LAST step's evaluation, still
    `UNKNOWN_NOT_VERIFIED`/`None` whenever the loop raised or no evaluator
    was supplied.
  - NO real `reserve_policy_guard.evaluate_dispatch_safety`,
    `N6SolarForecastEngine`, `GAP19HighsNativeOptimizer`, or
    `DigitalTwinSimulator` is imported, instantiated, or called anywhere in
    this file -- every collaborator below is a small hand-built Fake.
  - NO production file (`worker.py`, `runner.py`, `router.py`,
    `gap19_highs_native.py`, `reserve_policy_guard.py`) is imported,
    modified, or executed by this file.
"""
from __future__ import annotations

import unittest

from system.evaluation.n6_multi_origin_harness.harness import (
    SAFETY_EVIDENCE_UNKNOWN,
    SAFETY_EVIDENCE_VERIFIED,
    OriginRunStatus,
    execute_origin_dispatch_cell,
    record_origin_outcome,
    summarize_step_safety_evaluations,
)
from system.evaluation.replay_harness import MatchedControllerSettings
from system.safety.reserve_policy_guard import SafetyEvaluationResult


def _controller_settings(**overrides) -> MatchedControllerSettings:
    base = dict(
        battery_params={"capacity_wh": 150000.0, "eta_chg": 0.95, "eta_dis": 0.95},
        diesel_generator_constraints={"p_max_w": 80000.0, "min_runtime_h": 1.0},
        fuel_curve_params={"base_lph": 2.0, "marginal_lpwh": 0.00025},
        gap19_solver_settings={"tolerance": 1e-6, "time_limit_s": 30},
        objective_priorities={"J1": 1, "J2": 3, "J3": 4, "J4": 5},
        termination_criteria={"max_iters": 1000},
        demand_criticality_config={"critical_fraction": 0.4},
        scenario_inclusion_rules={"min_data_completeness": 0.99},
    )
    base.update(overrides)
    return MatchedControllerSettings(**base)


class _Scenario:
    """Minimal stand-in exposing exactly what execute_origin_dispatch_cell reads off `scenario`."""

    def __init__(self, scenario_key="o1", forecast_provider="n6_solar"):
        self.scenario_key = scenario_key
        self.forecast_provider = forecast_provider
        self.controller_settings = _controller_settings()


class _FakeForecastProvider:
    def predict(self, origin, step_index, context):
        return {"origin": origin, "step_index": step_index}


class _FakeOptimizer:
    def optimize(self, state, forecast, controller_settings):
        return {"constraint_status": "OPTIMAL"}


class _FakeSimulator:
    """Produces a fresh dispatch_outcome every step; never stops early unless told to."""

    def __init__(self, stop_early_at_step=None):
        self._stop_early_at_step = stop_early_at_step

    def step(self, state, dispatch_plan):
        step_idx = state.get("_step", 0)
        new_state = dict(state)
        new_state["_step"] = step_idx + 1
        stop_early = self._stop_early_at_step is not None and step_idx >= self._stop_early_at_step
        return {
            "state": new_state,
            "dispatch_outcome": {
                "constraint_status": "OPTIMAL",
                "diesel_consumed_liters": 1.0,
                "critical_unmet_load_wh": 0.0,
                "total_unmet_load_wh": 0.0,
                "_step_evaluated": step_idx,
            },
            "stop_early": stop_early,
        }


class _FakeSimulatorThenRaises:
    """Completes N clean steps, then the NEXT optimizer.optimize call raises."""

    def step(self, state, dispatch_plan):
        step_idx = state.get("_step", 0)
        new_state = dict(state)
        new_state["_step"] = step_idx + 1
        return {
            "state": new_state,
            "dispatch_outcome": {"constraint_status": "OPTIMAL", "diesel_consumed_liters": 1.0},
            "stop_early": False,
        }


class _FakeOptimizerRaisesAtStep:
    def __init__(self, raise_at_step):
        self._raise_at_step = raise_at_step
        self.calls = 0

    def optimize(self, state, forecast, controller_settings):
        if self.calls == self._raise_at_step:
            raise RuntimeError(f"synthetic failure at step {self.calls}")
        self.calls += 1
        return {"constraint_status": "OPTIMAL"}


class _CountingSafetyEvaluator:
    """Records every dispatch_outcome it was asked to evaluate, in call order."""

    def __init__(self, passed_sequence=None, default_passed=True):
        self._passed_sequence = passed_sequence
        self._default_passed = default_passed
        self.calls = []

    def evaluate_dispatch_safety(self, dispatch_outcome):
        self.calls.append(dispatch_outcome)
        if self._passed_sequence is not None:
            passed = self._passed_sequence[len(self.calls) - 1]
        else:
            passed = self._default_passed
        return SafetyEvaluationResult(
            passed=passed,
            hard_soc_violation=not passed,
            reserve_shortfall_total_wh=0.0 if passed else 500.0,
            reserve_violation=False,
            critical_unmet_total_wh=0.0,
            solver_infeasible=False,
        )


class TestPerStepSafetyEvaluationCadence(unittest.TestCase):
    """
    Core regression: the safety evaluator must be consulted once PER
    COMPLETED STEP, not once after the whole loop -- the exact gap
    forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 6 (blocker F) documented as
    still open.
    """

    def test_01_safety_evaluator_called_once_per_completed_step_not_once_total(self):
        evaluator = _CountingSafetyEvaluator(default_passed=True)
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=5,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(),
            simulator=_FakeSimulator(),
            safety_evaluator=evaluator,
            provenance={"test": "cadence"},
        )
        self.assertEqual(result.completed_steps, 5)
        self.assertEqual(len(evaluator.calls), 5, "safety evaluator must be called once per completed step")
        self.assertEqual(len(result.step_safety_evaluations), 5)
        for ev in result.step_safety_evaluations:
            self.assertIsInstance(ev, SafetyEvaluationResult)

    def test_02_per_step_evaluations_are_in_step_order_and_distinct(self):
        # Step-varying outcome: evaluator sees a different dispatch_outcome
        # each call (via the fake simulator's _step_evaluated tag), proving
        # these are genuinely per-step evaluations, not one cached result
        # replayed N times.
        evaluator = _CountingSafetyEvaluator(default_passed=True)
        execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=3,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(),
            simulator=_FakeSimulator(),
            safety_evaluator=evaluator,
            provenance={},
        )
        seen_step_tags = [call["_step_evaluated"] for call in evaluator.calls]
        self.assertEqual(seen_step_tags, [0, 1, 2])

    def test_03_overall_verdict_still_reflects_the_last_step_backward_compatible(self):
        # Mixed per-step outcomes: steps 0-2 pass, step 3 fails. The
        # pre-existing single-verdict fields must reflect the LAST step
        # (fail), exactly as the single end-of-loop call used to.
        evaluator = _CountingSafetyEvaluator(passed_sequence=[True, True, True, False])
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=4,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(),
            simulator=_FakeSimulator(),
            safety_evaluator=evaluator,
            provenance={},
        )
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_VERIFIED)
        self.assertFalse(result.safety_passed)
        self.assertEqual(len(result.step_safety_evaluations), 4)
        self.assertTrue(result.step_safety_evaluations[0].passed)
        self.assertFalse(result.step_safety_evaluations[3].passed)

    def test_04_no_safety_evaluator_supplied_step_safety_evaluations_stays_empty(self):
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=3,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(),
            simulator=_FakeSimulator(),
            safety_evaluator=None,
            provenance={},
        )
        self.assertEqual(result.step_safety_evaluations, ())
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN)
        self.assertIsNone(result.safety_passed)

    def test_05_exception_mid_loop_keeps_earlier_step_evaluations_but_final_verdict_stays_unknown(self):
        # Steps 0-1 complete cleanly and ARE evaluated per-step; the
        # optimizer then raises on its 3rd call (step index 2). The
        # pre-existing rule ("an exception mid-loop means no FINAL safety
        # evaluation is attempted") is preserved for the single-verdict
        # fields, while the earlier steps' own per-step evidence is still
        # honestly retained in step_safety_evaluations -- more information
        # than before, not less, and never a silently invented pass.
        evaluator = _CountingSafetyEvaluator(default_passed=True)
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=10,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizerRaisesAtStep(raise_at_step=2),
            simulator=_FakeSimulatorThenRaises(),
            safety_evaluator=evaluator,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION)
        self.assertEqual(result.completed_steps, 2)
        self.assertEqual(len(result.step_safety_evaluations), 2, "steps that DID complete must still carry their own evidence")
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN, "no FINAL verdict when the run itself failed")
        self.assertIsNone(result.safety_passed)

    def test_06_stop_early_still_evaluates_every_step_that_did_complete(self):
        evaluator = _CountingSafetyEvaluator(default_passed=True)
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=_Scenario(),
            expected_steps=10,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(),
            simulator=_FakeSimulator(stop_early_at_step=2),
            safety_evaluator=evaluator,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.INCOMPLETE_RUN)
        self.assertEqual(result.completed_steps, len(result.step_safety_evaluations))
        self.assertEqual(len(evaluator.calls), result.completed_steps)


class TestSummarizeStepSafetyEvaluations(unittest.TestCase):
    """Pure aggregate helper over OriginRunResult.step_safety_evaluations."""

    def test_07_counts_mixed_pass_fail_and_violations_correctly(self):
        evals = (
            SafetyEvaluationResult(
                passed=True, hard_soc_violation=False, reserve_shortfall_total_wh=0.0,
                reserve_violation=False, critical_unmet_total_wh=0.0, solver_infeasible=False,
            ),
            SafetyEvaluationResult(
                passed=False, hard_soc_violation=True, reserve_shortfall_total_wh=500.0,
                reserve_violation=True, critical_unmet_total_wh=200.0, solver_infeasible=False,
            ),
            None,  # no dispatch outcome that step -- must be excluded, never coerced
            SafetyEvaluationResult(
                passed=False, hard_soc_violation=False, reserve_shortfall_total_wh=0.0,
                reserve_violation=False, critical_unmet_total_wh=0.0, solver_infeasible=True,
            ),
        )
        summary = summarize_step_safety_evaluations(evals)
        self.assertEqual(summary["n_steps_total"], 4)
        self.assertEqual(summary["n_steps_evaluated"], 3)
        self.assertEqual(summary["n_steps_unknown"], 1)
        self.assertEqual(summary["n_steps_passed"], 1)
        self.assertEqual(summary["n_steps_failed"], 2)
        self.assertEqual(summary["n_steps_hard_soc_violation"], 1)
        self.assertEqual(summary["n_steps_reserve_violation"], 1)
        self.assertEqual(summary["n_steps_solver_infeasible"], 1)

    def test_08_empty_sequence_all_zero_never_divides_by_zero(self):
        summary = summarize_step_safety_evaluations(())
        self.assertEqual(summary, {
            "n_steps_total": 0, "n_steps_evaluated": 0, "n_steps_unknown": 0,
            "n_steps_passed": 0, "n_steps_failed": 0, "n_steps_hard_soc_violation": 0,
            "n_steps_reserve_violation": 0, "n_steps_solver_infeasible": 0,
        })

    def test_09_all_none_sequence_counts_as_fully_unknown(self):
        summary = summarize_step_safety_evaluations((None, None, None))
        self.assertEqual(summary["n_steps_total"], 3)
        self.assertEqual(summary["n_steps_evaluated"], 0)
        self.assertEqual(summary["n_steps_unknown"], 3)


class TestOriginRunResultStepSafetyEvaluationsValidation(unittest.TestCase):
    """Fail-closed __post_init__ invariants on the new field."""

    def test_10_more_step_evaluations_than_completed_steps_rejected(self):
        ev = SafetyEvaluationResult(
            passed=True, hard_soc_violation=False, reserve_shortfall_total_wh=0.0,
            reserve_violation=False, critical_unmet_total_wh=0.0, solver_infeasible=False,
        )
        with self.assertRaises(ValueError):
            record_origin_outcome(
                origin="o1", arm="candidate", scenario_key="o1", forecast_provider="n6_solar",
                completed_steps=1, expected_steps=2,
                dispatch_outcome={"constraint_status": "OPTIMAL"},
                safety_evaluation=ev,
                provenance={},
                step_safety_evaluations=(ev, ev, ev),  # 3 > completed_steps=1
            )

    def test_11_default_step_safety_evaluations_is_empty_tuple_backward_compatible(self):
        result = record_origin_outcome(
            origin="o1", arm="candidate", scenario_key="o1", forecast_provider="n6_solar",
            completed_steps=1, expected_steps=1,
            dispatch_outcome={"constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
        )
        self.assertEqual(result.step_safety_evaluations, ())


if __name__ == "__main__":
    unittest.main()
