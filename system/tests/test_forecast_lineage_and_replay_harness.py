"""
POLARIS — Forecast Lineage & Factor-Isolated Replay Harness Test Suite
=========================================================================
N6 Operational Readiness Remediation, Section 5 & 6.

Validates: oracle-provider classification/rejection against the verified
Arm A/A_FIX/B/C lineage facts, matched-scenario/controller-settings
isolation, forecast-provider-identity checks, Experiment A construction,
Experiment B's unconditional authorization gate, and that NEITHER
experiment can be executed (campaign execution stays disabled).
"""

from __future__ import annotations

import unittest

from system.evaluation.forecast_lineage import (
    OracleProviderRejectedError,
    build_lineage_record,
    is_oracle_provider,
    reject_if_oracle,
)
from system.evaluation.replay_harness import (
    AuthorizationRequiredError,
    CampaignExecutionNotAuthorizedError,
    ExperimentAConfig,
    ExperimentBConfig,
    FactorIsolatedReplayHarness,
    MatchedControllerSettings,
    ScenarioMismatchError,
    ScenarioSpec,
    validate_matched_scenario_pair,
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


def _scenario(key, provider, reserve_policy="governed", soc=100000.0, settings=None) -> ScenarioSpec:
    return ScenarioSpec(
        scenario_key=key,
        forecast_origin="2024-06-01T00:00:00Z",
        initial_battery_soc_wh=soc,
        controller_settings=settings or _controller_settings(),
        forecast_provider=provider,
        reserve_policy_name=reserve_policy,
    )


class TestOracleProviderClassification(unittest.TestCase):
    def test_01_realized_sw_in_is_oracle(self):
        self.assertTrue(is_oracle_provider("realized_sw_in"))

    def test_02_causal_nwp_gamma1_is_not_oracle(self):
        self.assertFalse(is_oracle_provider("causal_nwp_gamma1"))

    def test_03_lineage_record_arm_a_fix_verified_causal(self):
        rec = build_lineage_record(
            "A_FIX",
            provider_configured="causal_nwp_gamma1",
            model_artifact_loaded="CausalNwpPhysicsForecastEngine",
            forecast_consumed_by_dispatch="forecast_point",
            forecast_used_for_reserve="forecast_point",
        )
        self.assertEqual(rec.lineage_status, "VERIFIED_CAUSAL")
        self.assertFalse(rec.leakage_detected)

    def test_04_lineage_record_arm_b_confirmed_oracle(self):
        rec = build_lineage_record(
            "B",
            provider_configured="realized_sw_in",
            model_artifact_loaded="SITES_measured_SW_IN",
            forecast_consumed_by_dispatch="realized_sw_in_power",
            forecast_used_for_reserve="realized_sw_in_power",
        )
        self.assertEqual(rec.lineage_status, "CONFIRMED_ORACLE")
        self.assertTrue(rec.leakage_detected)

    def test_05_lineage_record_arm_c_verified_causal(self):
        rec = build_lineage_record(
            "C",
            provider_configured="calibrated_gamma_hat_point",
            forecast_used_for_reserve="calibrated_lower_bound",
        )
        self.assertEqual(rec.lineage_status, "VERIFIED_CAUSAL")

    def test_06_unknown_provider_marked_unverified_not_assumed_safe(self):
        rec = build_lineage_record("X", provider_configured="some_new_untested_provider")
        self.assertEqual(rec.lineage_status, "UNKNOWN_UNVERIFIED")
        self.assertFalse(rec.leakage_detected)  # not flagged as leakage, but also not certified safe

    def test_07_reject_if_oracle_raises_for_known_oracle(self):
        with self.assertRaises(OracleProviderRejectedError):
            reject_if_oracle("realized_sw_in")

    def test_08_reject_if_oracle_passes_for_causal_provider(self):
        reject_if_oracle("causal_nwp_gamma1")  # no raise


class TestScenarioSpecOracleRejection(unittest.TestCase):
    def test_09_scenario_construction_rejects_oracle_provider(self):
        with self.assertRaises(OracleProviderRejectedError):
            _scenario("origin_001", provider="realized_sw_in")

    def test_10_scenario_construction_accepts_causal_provider(self):
        s = _scenario("origin_001", provider="causal_nwp_gamma1")
        self.assertEqual(s.forecast_provider, "causal_nwp_gamma1")


class TestMatchedScenarioValidation(unittest.TestCase):
    def test_11_matched_pair_differing_only_in_forecast_provider_passes(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1")
        candidate = _scenario("origin_001", provider="n6_solar")
        validate_matched_scenario_pair(baseline, candidate)  # no raise

    def test_12_mismatched_scenario_key_fails_closed(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1")
        candidate = _scenario("origin_002", provider="n6_solar")
        with self.assertRaises(ScenarioMismatchError):
            validate_matched_scenario_pair(baseline, candidate)

    def test_13_mismatched_initial_soc_fails_closed(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1", soc=100000.0)
        candidate = _scenario("origin_001", provider="n6_solar", soc=120000.0)
        with self.assertRaises(ScenarioMismatchError):
            validate_matched_scenario_pair(baseline, candidate)

    def test_14_mismatched_controller_settings_fails_closed(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1")
        drifted_settings = _controller_settings(gap19_solver_settings={"tolerance": 1e-3, "time_limit_s": 30})
        candidate = _scenario("origin_001", provider="n6_solar", settings=drifted_settings)
        with self.assertRaises(ScenarioMismatchError):
            validate_matched_scenario_pair(baseline, candidate)

    def test_15_varying_both_provider_and_reserve_policy_fails_closed(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1", reserve_policy="governed")
        candidate = _scenario("origin_001", provider="n6_solar", reserve_policy="candidate_policy_x")
        with self.assertRaises(ScenarioMismatchError):
            validate_matched_scenario_pair(baseline, candidate)

    def test_16_identical_scenarios_with_no_isolated_factor_fails_closed(self):
        baseline = _scenario("origin_001", provider="causal_nwp_gamma1")
        candidate = _scenario("origin_001", provider="causal_nwp_gamma1")
        with self.assertRaises(ScenarioMismatchError):
            validate_matched_scenario_pair(baseline, candidate)


class TestExperimentAConfig(unittest.TestCase):
    def test_17_experiment_a_valid_config_constructs(self):
        baseline = [_scenario("o1", provider="causal_nwp_gamma1"), _scenario("o2", provider="causal_nwp_gamma1")]
        candidate = [_scenario("o1", provider="n6_solar"), _scenario("o2", provider="n6_solar")]
        cfg = ExperimentAConfig(
            baseline_scenarios=baseline, candidate_scenarios=candidate, governed_reserve_policy_name="governed"
        )
        self.assertEqual(len(cfg.baseline_scenarios), 2)

    def test_18_experiment_a_rejects_reserve_policy_drift(self):
        baseline = [_scenario("o1", provider="causal_nwp_gamma1", reserve_policy="governed")]
        candidate = [_scenario("o1", provider="n6_solar", reserve_policy="governed")]
        candidate[0] = _scenario("o1", provider="n6_solar", reserve_policy="NOT_GOVERNED")
        with self.assertRaises(ScenarioMismatchError):
            ExperimentAConfig(
                baseline_scenarios=baseline, candidate_scenarios=candidate, governed_reserve_policy_name="governed"
            )

    def test_19_experiment_a_rejects_oracle_candidate(self):
        baseline = [_scenario("o1", provider="causal_nwp_gamma1")]
        with self.assertRaises(OracleProviderRejectedError):
            ExperimentAConfig(
                baseline_scenarios=baseline,
                candidate_scenarios=[_scenario("o1", provider="realized_sw_in")],
                governed_reserve_policy_name="governed",
            )


class TestExperimentBConfigGated(unittest.TestCase):
    def test_20_experiment_b_without_token_raises_authorization_required(self):
        baseline = [_scenario("o1", provider="n6_solar", reserve_policy="governed")]
        candidate = [_scenario("o1", provider="n6_solar", reserve_policy="candidate_policy_x")]
        with self.assertRaises(AuthorizationRequiredError):
            ExperimentBConfig(
                fixed_forecast_provider="n6_solar",
                baseline_reserve_scenarios=baseline,
                candidate_reserve_scenarios=candidate,
            )

    def test_21_experiment_b_with_wrong_token_still_raises(self):
        baseline = [_scenario("o1", provider="n6_solar", reserve_policy="governed")]
        candidate = [_scenario("o1", provider="n6_solar", reserve_policy="candidate_policy_x")]
        with self.assertRaises(AuthorizationRequiredError):
            ExperimentBConfig(
                fixed_forecast_provider="n6_solar",
                baseline_reserve_scenarios=baseline,
                candidate_reserve_scenarios=candidate,
                authorization_token="some_guessed_string",
            )


class TestHarnessExecutionDisabled(unittest.TestCase):
    def test_22_execute_experiment_a_always_raises(self):
        baseline = [_scenario("o1", provider="causal_nwp_gamma1")]
        candidate = [_scenario("o1", provider="n6_solar")]
        cfg = ExperimentAConfig(
            baseline_scenarios=baseline, candidate_scenarios=candidate, governed_reserve_policy_name="governed"
        )
        harness = FactorIsolatedReplayHarness()
        harness.validate_experiment_a_config(cfg)
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_experiment_a(cfg)

    def test_23_execute_experiment_b_always_raises_even_if_config_existed(self):
        # Experiment B configs cannot even be constructed without the (never-issued) token,
        # so execute_experiment_b is exercised with None to prove the method itself is
        # unconditionally disabled regardless of what might be passed to it.
        harness = FactorIsolatedReplayHarness()
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_experiment_b(None)


if __name__ == "__main__":
    unittest.main()
