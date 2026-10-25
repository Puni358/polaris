"""
POLARIS -- N6 Multi-Origin Campaign Harness Test Suite
==========================================================
Validates: multi-origin matched-scenario construction (interface wiring onto
`replay_harness.py`'s existing types), oracle/leakage rejection across
multiple origins, per-origin outcome recording and its "missing safety
evidence is unknown, not a pass" rule, failure-mode classification
(optimizer exception / non-optimal solver status / incomplete run), per-arm
aggregation correctness, output-integrity validation on `OriginRunResult`,
and that NEITHER `MultiOriginCampaignHarness.execute_campaign` NOR the
documented-gap `execute_origin_dispatch_cell` can ever run a campaign.

Every fixture in this file is a small, hand-constructed synthetic value.
Nothing here reads a real historical dataset, calls N6SolarForecastEngine,
GAP19HighsNativeOptimizer, DigitalTwinSimulator, or touches the sealed 2025
blind partition.
"""
from __future__ import annotations

import unittest

from system.evaluation.forecast_lineage import OracleProviderRejectedError
from system.evaluation.n6_multi_origin_harness.harness import (
    SAFETY_EVIDENCE_UNKNOWN,
    SAFETY_EVIDENCE_VERIFIED,
    CampaignAggregateResult,
    MultiOriginCampaignConfig,
    MultiOriginCampaignHarness,
    OriginRunResult,
    OriginRunStatus,
    aggregate_origin_results,
    build_multi_origin_campaign_config,
    build_origin_scenario_pair,
    execute_origin_dispatch_cell,
    record_origin_outcome,
)
from system.evaluation.n6_multi_origin_harness.reproducibility_manifest import (
    CrossArmReproducibilityManifest,
    build_cross_arm_reproducibility_manifest,
)
from system.evaluation.replay_harness import (
    CampaignExecutionNotAuthorizedError,
    MatchedControllerSettings,
    ScenarioMismatchError,
)
from system.safety.reserve_policy_guard import SafetyEvaluationResult


class _FakeForecastProvider:
    """Test double only -- never a real N6SolarForecastEngine."""

    def __init__(self, sw_in_by_step=None):
        self._sw_in_by_step = sw_in_by_step or {}

    def predict(self, origin, step_index, context):
        return {"sw_in": self._sw_in_by_step.get(step_index, 100.0), "origin": origin, **context}


class _FakeOptimizer:
    """Test double only -- never a real GAP19HighsNativeOptimizer."""

    def __init__(self, constraint_status="OPTIMAL", raise_at_step=None, diesel_per_step=1.0):
        self._constraint_status = constraint_status
        self._raise_at_step = raise_at_step
        self._diesel_per_step = diesel_per_step
        self._calls = 0

    def optimize(self, state, forecast, controller_settings):
        if self._raise_at_step is not None and self._calls == self._raise_at_step:
            raise RuntimeError(f"synthetic solver crash at call {self._calls}")
        self._calls += 1
        return {"constraint_status": self._constraint_status, "diesel_liters": self._diesel_per_step}


class _FakeSimulator:
    """Test double only -- never a real DigitalTwinSimulator."""

    def __init__(self, stop_early_at_step=None, missing_diesel_metric=False):
        self._stop_early_at_step = stop_early_at_step
        self._missing_diesel_metric = missing_diesel_metric

    def step(self, state, dispatch_plan):
        dispatch_outcome = {"constraint_status": dispatch_plan.get("constraint_status")}
        if not self._missing_diesel_metric:
            dispatch_outcome["diesel_consumed_liters"] = dispatch_plan.get("diesel_liters", 0.0)
        dispatch_outcome["critical_unmet_load_wh"] = 0.0
        dispatch_outcome["total_unmet_load_wh"] = 0.0
        stop_early = self._stop_early_at_step is not None and state.get("_step", 0) >= self._stop_early_at_step
        new_state = dict(state)
        new_state["_step"] = state.get("_step", 0) + 1
        return {"state": new_state, "dispatch_outcome": dispatch_outcome, "stop_early": stop_early}


class _FakeSafetyEvaluator:
    """Test double only -- never the real evaluate_dispatch_safety."""

    def __init__(self, passed=True):
        self._passed = passed

    def evaluate_dispatch_safety(self, dispatch_outcome):
        return SafetyEvaluationResult(
            passed=self._passed,
            hard_soc_violation=False,
            reserve_shortfall_total_wh=0.0,
            reserve_violation=False,
            critical_unmet_total_wh=0.0,
            solver_infeasible=False,
        )


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


_ORIGINS = ["2024-01-01T00:00:00Z", "2024-02-01T00:00:00Z", "2024-03-01T00:00:00Z"]


def _soc_by_origin(value: float = 100000.0):
    return {o: value for o in _ORIGINS}


class TestOriginScenarioPairConstruction(unittest.TestCase):
    def test_01_builds_matched_pair_for_one_origin(self):
        settings = _controller_settings()
        baseline, candidate = build_origin_scenario_pair(
            origin="2024-06-01T00:00:00Z",
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=settings,
            initial_battery_soc_wh=100000.0,
            governed_reserve_policy_name="governed",
        )
        self.assertEqual(baseline.scenario_key, candidate.scenario_key)
        self.assertEqual(baseline.forecast_provider, "causal_nwp_gamma1")
        self.assertEqual(candidate.forecast_provider, "n6_solar")

    def test_02_oracle_candidate_provider_rejected_at_construction(self):
        settings = _controller_settings()
        with self.assertRaises(OracleProviderRejectedError):
            build_origin_scenario_pair(
                origin="o1",
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="realized_sw_in",
                controller_settings=settings,
                initial_battery_soc_wh=100000.0,
                governed_reserve_policy_name="governed",
            )


class TestMultiOriginCampaignConfigConstruction(unittest.TestCase):
    def test_03_builds_config_across_multiple_origins(self):
        cfg = build_multi_origin_campaign_config(
            origins=list(_ORIGINS),
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh_by_origin=_soc_by_origin(),
            governed_reserve_policy_name="governed",
        )
        self.assertEqual(cfg.n_origins, 3)
        self.assertEqual(len(cfg.experiment_a_config.baseline_scenarios), 3)
        self.assertEqual(len(cfg.experiment_a_config.candidate_scenarios), 3)

    def test_04_empty_origin_list_fails_closed(self):
        with self.assertRaises(ValueError):
            build_multi_origin_campaign_config(
                origins=[],
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh_by_origin={},
                governed_reserve_policy_name="governed",
            )

    def test_05_duplicate_origin_fails_closed(self):
        with self.assertRaises(ValueError):
            build_multi_origin_campaign_config(
                origins=["o1", "o1"],
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh_by_origin={"o1": 100000.0},
                governed_reserve_policy_name="governed",
            )

    def test_06_missing_initial_soc_fails_closed_not_invented(self):
        with self.assertRaises(ValueError):
            build_multi_origin_campaign_config(
                origins=["o1", "o2"],
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh_by_origin={"o1": 100000.0},  # o2 missing
                governed_reserve_policy_name="governed",
            )

    def test_07_oracle_provider_rejected_across_multi_origin_set(self):
        with self.assertRaises(OracleProviderRejectedError):
            build_multi_origin_campaign_config(
                origins=list(_ORIGINS),
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="actual_sw_in",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh_by_origin=_soc_by_origin(),
                governed_reserve_policy_name="governed",
            )

    def test_08_reserve_policy_drift_fails_closed_across_multi_origin_set(self):
        # Build manually with one origin's candidate scenario on a different
        # reserve policy than the rest, to exercise ExperimentAConfig's own
        # governed-reserve-policy check at multi-origin scale.
        settings = _controller_settings()
        baseline_scenarios = []
        candidate_scenarios = []
        for i, origin in enumerate(_ORIGINS):
            b, c = build_origin_scenario_pair(
                origin=origin,
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=settings,
                initial_battery_soc_wh=100000.0,
                governed_reserve_policy_name="governed",
            )
            baseline_scenarios.append(b)
            if i == 1:
                from system.evaluation.replay_harness import ScenarioSpec

                c = ScenarioSpec(
                    scenario_key=origin,
                    forecast_origin=origin,
                    initial_battery_soc_wh=100000.0,
                    controller_settings=settings,
                    forecast_provider="n6_solar",
                    reserve_policy_name="DRIFTED_POLICY",
                )
            candidate_scenarios.append(c)

        from system.evaluation.replay_harness import ExperimentAConfig

        with self.assertRaises(ScenarioMismatchError):
            ExperimentAConfig(
                baseline_scenarios=baseline_scenarios,
                candidate_scenarios=candidate_scenarios,
                governed_reserve_policy_name="governed",
            )


class TestRecordOriginOutcome(unittest.TestCase):
    def test_09_optimal_run_recorded_with_verified_safety_pass(self):
        safety = SafetyEvaluationResult(
            passed=True,
            hard_soc_violation=False,
            reserve_shortfall_total_wh=0.0,
            reserve_violation=False,
            critical_unmet_total_wh=0.0,
            solver_infeasible=False,
        )
        result = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={
                "diesel_consumed_liters": 12.5,
                "critical_unmet_load_wh": 0.0,
                "total_unmet_load_wh": 0.0,
                "constraint_status": "OPTIMAL",
            },
            safety_evaluation=safety,
            provenance={"config_hash": "deadbeef"},
        )
        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_VERIFIED)
        self.assertTrue(result.safety_passed)
        self.assertEqual(result.diesel_consumed_liters, 12.5)

    def test_10_missing_safety_evaluation_recorded_as_unknown_never_pass(self):
        result = record_origin_outcome(
            origin="o1",
            arm="baseline",
            scenario_key="o1",
            forecast_provider="causal_nwp_gamma1",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={
                "diesel_consumed_liters": 15.0,
                "constraint_status": "OPTIMAL",
            },
            safety_evaluation=None,
            provenance={},
        )
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN)
        self.assertIsNone(result.safety_passed)

    def test_11_exception_recorded_as_failed_optimization_exception(self):
        result = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=5,
            expected_steps=24,
            dispatch_outcome=None,
            safety_evaluation=None,
            provenance={},
            exception_message="RuntimeError: solver crashed at step 5",
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION)
        self.assertIn("solver crashed", result.failure_reasons[0])

    def test_12_non_optimal_constraint_status_recorded_as_failed_worker_exit(self):
        result = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "INFEASIBLE"},
            safety_evaluation=None,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_13_fewer_completed_than_expected_steps_recorded_as_incomplete(self):
        result = record_origin_outcome(
            origin="o1",
            arm="baseline",
            scenario_key="o1",
            forecast_provider="causal_nwp_gamma1",
            completed_steps=10,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.INCOMPLETE_RUN)

    def test_14_missing_diesel_metric_recorded_as_none_not_zero(self):
        result = record_origin_outcome(
            origin="o1",
            arm="baseline",
            scenario_key="o1",
            forecast_provider="causal_nwp_gamma1",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL"},  # no diesel key at all
            safety_evaluation=None,
            provenance={},
        )
        self.assertIsNone(result.diesel_consumed_liters)


class TestOriginRunResultIntegrity(unittest.TestCase):
    def test_15_unknown_safety_status_paired_with_nonnull_passed_fails_closed(self):
        with self.assertRaises(ValueError):
            OriginRunResult(
                origin="o1",
                arm="baseline",
                scenario_key="o1",
                forecast_provider="causal_nwp_gamma1",
                run_status=OriginRunStatus.OPTIMAL,
                completed_steps=24,
                expected_steps=24,
                diesel_consumed_liters=1.0,
                critical_unmet_load_wh=0.0,
                total_unmet_load_wh=0.0,
                safety_evidence_status=SAFETY_EVIDENCE_UNKNOWN,
                safety_passed=True,  # inconsistent: unknown evidence cannot carry a pass value
                optimizer_constraint_status="OPTIMAL",
                failure_reasons=(),
                provenance={},
            )

    def test_16_invalid_step_counts_fail_closed(self):
        with self.assertRaises(ValueError):
            OriginRunResult(
                origin="o1",
                arm="baseline",
                scenario_key="o1",
                forecast_provider="causal_nwp_gamma1",
                run_status=OriginRunStatus.OPTIMAL,
                completed_steps=30,
                expected_steps=24,  # completed > expected
                diesel_consumed_liters=1.0,
                critical_unmet_load_wh=0.0,
                total_unmet_load_wh=0.0,
                safety_evidence_status=SAFETY_EVIDENCE_UNKNOWN,
                safety_passed=None,
                optimizer_constraint_status="OPTIMAL",
                failure_reasons=(),
                provenance={},
            )

    def test_17_unknown_run_status_fails_closed(self):
        with self.assertRaises(ValueError):
            OriginRunResult(
                origin="o1",
                arm="baseline",
                scenario_key="o1",
                forecast_provider="causal_nwp_gamma1",
                run_status="NOT_A_REAL_STATUS",
                completed_steps=24,
                expected_steps=24,
                diesel_consumed_liters=1.0,
                critical_unmet_load_wh=0.0,
                total_unmet_load_wh=0.0,
                safety_evidence_status=SAFETY_EVIDENCE_UNKNOWN,
                safety_passed=None,
                optimizer_constraint_status="OPTIMAL",
                failure_reasons=(),
                provenance={},
            )


class TestAggregation(unittest.TestCase):
    def _three_origin_results(self, arm="candidate"):
        return [
            record_origin_outcome(
                origin="o1", arm=arm, scenario_key="o1", forecast_provider="n6_solar",
                completed_steps=24, expected_steps=24,
                dispatch_outcome={"diesel_consumed_liters": 10.0, "critical_unmet_load_wh": 0.0,
                                   "total_unmet_load_wh": 0.0, "constraint_status": "OPTIMAL"},
                safety_evaluation=SafetyEvaluationResult(True, False, 0.0, False, 0.0, False),
                provenance={},
            ),
            record_origin_outcome(
                origin="o2", arm=arm, scenario_key="o2", forecast_provider="n6_solar",
                completed_steps=24, expected_steps=24,
                dispatch_outcome={"diesel_consumed_liters": 20.0, "constraint_status": "OPTIMAL",
                                  "critical_unmet_load_wh": 0.0, "total_unmet_load_wh": 0.0},
                safety_evaluation=None,  # unknown safety evidence
                provenance={},
            ),
            record_origin_outcome(
                origin="o3", arm=arm, scenario_key="o3", forecast_provider="n6_solar",
                completed_steps=5, expected_steps=24,
                dispatch_outcome=None,
                safety_evaluation=None,
                provenance={},
                exception_message="optimizer crashed",
            ),
        ]

    def test_18_aggregates_status_counts_correctly(self):
        results = self._three_origin_results()
        agg = aggregate_origin_results(results, arm="candidate")
        self.assertEqual(agg.n_origins, 3)
        self.assertEqual(agg.status_counts[OriginRunStatus.OPTIMAL], 2)
        self.assertEqual(agg.status_counts[OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION], 1)

    def test_19_diesel_total_and_mean_exclude_missing_not_zero_fill(self):
        results = self._three_origin_results()
        agg = aggregate_origin_results(results, arm="candidate")
        # o3 has no diesel metric (exception before any outcome); o1=10.0, o2=20.0
        self.assertEqual(agg.total_diesel_consumed_liters, 30.0)
        self.assertEqual(agg.mean_diesel_consumed_liters, 15.0)
        self.assertEqual(agg.n_missing_diesel_metric, 1)

    def test_20_safety_unknown_count_never_folded_into_verified_pass(self):
        results = self._three_origin_results()
        agg = aggregate_origin_results(results, arm="candidate")
        self.assertEqual(agg.n_safety_verified_pass, 1)  # only o1
        self.assertEqual(agg.n_safety_unknown, 2)  # o2 and o3

    def test_21_aggregation_filters_by_arm(self):
        candidate_results = self._three_origin_results(arm="candidate")
        baseline_results = self._three_origin_results(arm="baseline")
        combined = candidate_results + baseline_results
        agg_candidate = aggregate_origin_results(combined, arm="candidate")
        agg_baseline = aggregate_origin_results(combined, arm="baseline")
        self.assertEqual(agg_candidate.n_origins, 3)
        self.assertEqual(agg_baseline.n_origins, 3)

    def test_22_aggregation_on_empty_arm_fails_closed(self):
        with self.assertRaises(ValueError):
            aggregate_origin_results([], arm="candidate")


class TestExecutionRemainsUnauthorized(unittest.TestCase):
    def test_23_validate_campaign_config_does_not_raise(self):
        cfg = build_multi_origin_campaign_config(
            origins=list(_ORIGINS),
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh_by_origin=_soc_by_origin(),
            governed_reserve_policy_name="governed",
        )
        harness = MultiOriginCampaignHarness()
        validated = harness.validate_campaign_config(cfg)
        self.assertIs(validated, cfg)

    def test_24_execute_campaign_always_raises_campaign_not_authorized(self):
        cfg = build_multi_origin_campaign_config(
            origins=list(_ORIGINS),
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh_by_origin=_soc_by_origin(),
            governed_reserve_policy_name="governed",
        )
        harness = MultiOriginCampaignHarness()
        harness.validate_campaign_config(cfg)
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_campaign(cfg)

    def test_25_execute_origin_dispatch_cell_requires_explicit_collaborators_fails_closed(self):
        # No silent defaults: calling without the required DI collaborators
        # fails closed with a TypeError rather than running anything.
        with self.assertRaises(TypeError):
            execute_origin_dispatch_cell()

    def test_26_execute_campaign_raises_even_for_single_origin_config(self):
        cfg = build_multi_origin_campaign_config(
            origins=["o1"],
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh_by_origin={"o1": 100000.0},
            governed_reserve_policy_name="governed",
        )
        harness = MultiOriginCampaignHarness()
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_campaign(cfg)


class TestExecuteOriginDispatchCellDependencyInjected(unittest.TestCase):
    """
    All fixtures below are hand-built Fake* test doubles (`_FakeForecastProvider`,
    `_FakeOptimizer`, `_FakeSimulator`, `_FakeSafetyEvaluator`), never real
    `N6SolarForecastEngine`/`GAP19HighsNativeOptimizer`/`DigitalTwinSimulator`
    objects. Exercises the directive's required categories for the newly
    implemented per-origin integration: matched scenarios, solver failures,
    incomplete runs, missing metrics, and unknown safety evidence.
    """

    def _scenario(self, origin="o1", provider="n6_solar"):
        return build_origin_scenario_pair(
            origin=origin,
            baseline_provider="causal_nwp_gamma1",
            candidate_provider=provider,
            controller_settings=_controller_settings(),
            initial_battery_soc_wh=100000.0,
            governed_reserve_policy_name="governed",
        )[1]  # candidate scenario

    def test_27_clean_run_across_matched_scenario_records_optimal(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=4,
            initial_state={"_step": 0, "soc_wh": 100000.0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(constraint_status="OPTIMAL"),
            simulator=_FakeSimulator(),
            safety_evaluator=_FakeSafetyEvaluator(passed=True),
            provenance={"test": "27"},
        )
        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, 4)
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_VERIFIED)
        self.assertTrue(result.safety_passed)

    def test_28_optimizer_exception_mid_loop_recorded_as_failed_optimization_exception(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=10,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(raise_at_step=3),
            simulator=_FakeSimulator(),
            safety_evaluator=None,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION)
        self.assertEqual(result.completed_steps, 3)
        self.assertIn("synthetic solver crash", result.failure_reasons[0])
        # An exception mid-loop means no safety evaluation is ever attempted.
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN)

    def test_29_simulator_stop_early_before_expected_steps_recorded_as_incomplete(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=10,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(constraint_status="OPTIMAL"),
            simulator=_FakeSimulator(stop_early_at_step=2),
            safety_evaluator=None,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.INCOMPLETE_RUN)
        self.assertLess(result.completed_steps, 10)

    def test_30_non_optimal_constraint_status_recorded_as_failed_worker_exit(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=3,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(constraint_status="INFEASIBLE"),
            simulator=_FakeSimulator(),
            safety_evaluator=None,
            provenance={},
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_31_missing_diesel_metric_recorded_as_none_not_zero(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=2,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(constraint_status="OPTIMAL"),
            simulator=_FakeSimulator(missing_diesel_metric=True),
            safety_evaluator=None,
            provenance={},
        )
        self.assertIsNone(result.diesel_consumed_liters)

    def test_32_no_safety_evaluator_supplied_recorded_as_unknown_never_pass(self):
        scenario = self._scenario()
        result = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=2,
            initial_state={"_step": 0},
            forecast_provider=_FakeForecastProvider(),
            optimizer=_FakeOptimizer(constraint_status="OPTIMAL"),
            simulator=_FakeSimulator(),
            safety_evaluator=None,
            provenance={},
        )
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN)
        self.assertIsNone(result.safety_passed)

    def test_33_oracle_candidate_still_rejected_before_any_cell_executes(self):
        # The DI loop never gets a chance to run at all if the scenario
        # itself is leakage/oracle-tainted -- construction-time rejection,
        # reused unmodified from forecast_lineage.reject_if_oracle.
        with self.assertRaises(OracleProviderRejectedError):
            self._scenario(provider="realized_sw_in")

    def test_34_multi_origin_di_loop_feeds_aggregation_end_to_end(self):
        # Full, small, synthetic multi-origin flow: build matched scenarios
        # for 3 origins -> run each through the DI'd dispatch cell (one
        # origin configured to fail) -> aggregate. No real dispatch anywhere.
        origins = ["o1", "o2", "o3"]
        results = []
        for i, origin in enumerate(origins):
            scenario = self._scenario(origin=origin)
            optimizer = _FakeOptimizer(raise_at_step=0) if origin == "o3" else _FakeOptimizer()
            results.append(
                execute_origin_dispatch_cell(
                    origin=origin,
                    arm="candidate",
                    scenario=scenario,
                    expected_steps=4,
                    initial_state={"_step": 0},
                    forecast_provider=_FakeForecastProvider(),
                    optimizer=optimizer,
                    simulator=_FakeSimulator(),
                    safety_evaluator=_FakeSafetyEvaluator(passed=True) if origin != "o3" else None,
                    provenance={"origin_index": i},
                )
            )
        agg = aggregate_origin_results(results, arm="candidate")
        self.assertEqual(agg.n_origins, 3)
        self.assertEqual(agg.status_counts[OriginRunStatus.OPTIMAL], 2)
        self.assertEqual(agg.status_counts[OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION], 1)
        self.assertEqual(agg.n_safety_verified_pass, 2)
        self.assertEqual(agg.n_safety_unknown, 1)

    def test_35_harness_source_never_imports_production_dispatch_classes(self):
        # Static proof (mirrors forecasting/n6/reports/N6_MULTI_ORIGIN_HARNESS_REPORT.md Section 3's
        # own `grep -n "^from\|^import"`) that implementing the DI-based cell
        # did not introduce a real production IMPORT anywhere in harness.py.
        # The class names themselves appear in docstrings/comments (by
        # design, to document the Protocol shape they mirror) -- what must
        # never appear is an actual `from ... import <RealClass>` line, so
        # this test inspects only lines starting with `from`/`import`.
        import inspect

        from system.evaluation.n6_multi_origin_harness import harness as harness_module

        import_lines = "\n".join(
            line for line in inspect.getsource(harness_module).splitlines()
            if line.strip().startswith(("from ", "import "))
        )
        for forbidden in (
            "N6SolarForecastEngine",
            "GAP19HighsNativeOptimizer",
            "DigitalTwinSimulator",
            "EMSControlRouter",
            "gap19_highs_native",
            "n6_solar",
            "system.simulation.simulator",
            "system.control.router",
        ):
            self.assertNotIn(
                forbidden, import_lines, f"harness.py must never IMPORT the real '{forbidden}'."
            )

    def test_36_execute_campaign_still_gated_even_though_dispatch_cell_now_works(self):
        # Regression guard: implementing execute_origin_dispatch_cell for
        # real must not have loosened execute_campaign's own gate.
        cfg = build_multi_origin_campaign_config(
            origins=list(_ORIGINS),
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh_by_origin=_soc_by_origin(),
            governed_reserve_policy_name="governed",
        )
        harness = MultiOriginCampaignHarness()
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_campaign(cfg)


class TestCrossArmReproducibilityManifest(unittest.TestCase):
    """
    Synthetic hash strings only below -- none of these is a real artifact
    hash; they exercise the schema's fail-closed validation, not real
    provenance. `forecasting/n6/reports/N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md` Workstream 4
    demonstrates assembly against the repository's actual, already-existing
    hash manifests separately (read-only, outside this hermetic test file).
    """

    def _valid_kwargs(self, **overrides):
        base = dict(
            n6_model_sha256="a" * 64,
            n6_model_manifest_source="synthetic/manifest.json",
            baseline_code_sha256={"system/control/router.py": "b" * 64},
            baseline_configuration_sha256={"system/config/battery.yaml": "c" * 64},
            baseline_inputs_sha256={"data/synthetic.csv": "d" * 64},
            baseline_manifest_source="synthetic/manifests/",
            origins=("o1", "o2"),
            experiment_configuration_sha256="e" * 64,
            runtime_dependency_versions={"python": "3.12.3"},
            authorization_reference="NOT_YET_AUTHORIZED",
        )
        base.update(overrides)
        return base

    def test_37_builds_manifest_with_all_required_fields(self):
        manifest = build_cross_arm_reproducibility_manifest(**self._valid_kwargs())
        self.assertIsInstance(manifest, CrossArmReproducibilityManifest)
        self.assertEqual(manifest.output_hashes, {})

    def test_38_missing_n6_model_hash_fails_closed(self):
        with self.assertRaises(ValueError):
            build_cross_arm_reproducibility_manifest(**self._valid_kwargs(n6_model_sha256=""))

    def test_39_missing_authorization_reference_fails_closed_not_defaulted(self):
        with self.assertRaises(ValueError):
            build_cross_arm_reproducibility_manifest(**self._valid_kwargs(authorization_reference=None))

    def test_40_empty_baseline_hash_dict_fails_closed(self):
        with self.assertRaises(ValueError):
            build_cross_arm_reproducibility_manifest(**self._valid_kwargs(baseline_code_sha256={}))

    def test_41_empty_origins_fails_closed(self):
        with self.assertRaises(ValueError):
            build_cross_arm_reproducibility_manifest(**self._valid_kwargs(origins=()))

    def test_42_output_hashes_never_fabricated_defaults_empty(self):
        # No campaign has run; output_hashes must default to empty, never a
        # placeholder that could be mistaken for a real output hash.
        manifest = build_cross_arm_reproducibility_manifest(**self._valid_kwargs())
        self.assertEqual(manifest.output_hashes, {})
        self.assertEqual(manifest.notes, ())


if __name__ == "__main__":
    unittest.main()
