"""
POLARIS -- Phase 2 Instrumentation Authorization & Blocker Guards Test Suite
=============================================================================
Validates:
1. [BLOCKER-AUTH-2]: Two-stage authorization gate (default denial, parameter validation,
   protected file hash validation, execution stage status BLOCKED_AWAITING_POST_TEST_SIGN_OFF).
2. [BLOCKER-FUEL-1]: Per-step fuel exhaustion, clamping detection, monotonicity check,
   and tracking gap latching across single-shot and receding-horizon simulation adapters.
3. [BLOCKER-PARITY-1]: Canonical realized trajectory hashing, non-solar forecast hashing,
   resolved terminal target parity, and paired origin comparison fail-closed rules.
4. [BLOCKER-LATCH-1]: All-step solver-status and unmet-essential-load latching, generator
   start counting, startup surcharge separation, and battery delta E_term tracking.

All tests operate strictly on synthetic in-memory fixtures. No real historical or 2025 blind
data is accessed; no optimizers or simulations on real data are executed.
"""
from __future__ import annotations

import copy
import hashlib
import math
from pathlib import Path
from unittest.mock import MagicMock
import unittest
from typing import Any, Dict, List

from system.evaluation.replay_harness import (
    CampaignExecutionNotAuthorizedError,
    DiagnosticExecutionAuthorization,
    ExperimentAConfig,
    FactorIsolatedReplayHarness,
    MatchedControllerSettings,
    ScenarioSpec,
    SecurityIntegrityViolationError,
    APPROVED_CLASSIFICATION,
    APPROVED_PROTOCOL,
    APPROVED_ORIGINS,
    APPROVED_INITIAL_SOC_PCT,
    APPROVED_INITIAL_ENERGY_WH,
    APPROVED_INITIAL_FUEL_L,
    APPROVED_INITIAL_GEN_RUNNING,
    EXECUTION_STAGE_BLOCKED_AWAITING_POST_TEST_SIGN_OFF,
    EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
    REGISTERED_PROTECTED_FILE_HASHES,
    validate_diagnostic_execution_authorization,
)
from system.evaluation.n6_multi_origin_harness.harness import (
    SAFETY_EVIDENCE_UNKNOWN,
    SAFETY_EVIDENCE_VERIFIED,
    CampaignAggregateResult,
    MultiOriginCampaignConfig,
    MultiOriginCampaignHarness,
    OriginRunResult,
    OriginRunStatus,
    PairedOriginComparisonResult,
    aggregate_origin_results,
    build_multi_origin_campaign_config,
    build_origin_scenario_pair,
    compute_canonical_non_solar_forecast_hash,
    compute_canonical_realized_trajectory_hash,
    evaluate_paired_origin_comparison,
    execute_origin_dispatch_cell,
    record_origin_outcome,
)
from system.evaluation.n6_multi_origin_harness.adapters import (
    FUEL_EXHAUSTION_THRESHOLD_L,
    DispatchOutcomeView,
    RecedingHorizonPlanSlicingSimulatorAdapter,
    SingleShotPlanSlicingSimulatorAdapter,
    _prepare_gap19_terminal_target_config,
)
from system.safety.reserve_policy_guard import SafetyEvaluationResult
from system.evaluation.n6_multi_origin_harness.realized_loader import (
    load_authoritative_actuals_by_origin,
    CANONICAL_FIXTURE_SHA256,
    CANONICAL_FIXTURE_RELATIVE_PATH,
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


def _build_test_origin_run_result(
    origin: str = "2024-06-01",
    arm: str = "candidate",
    run_status: str = OriginRunStatus.OPTIMAL,
    completed_steps: int = 24,
    expected_steps: int = 24,
    diesel_consumed_liters: float = 25.0,
    critical_unmet_load_wh: float = 0.0,
    total_unmet_load_wh: float = 0.0,
    safety_evidence_status: str = SAFETY_EVIDENCE_VERIFIED,
    safety_passed: bool = True,
    has_solver_failure: bool = False,
    has_unmet_essential: bool = False,
    has_fuel_failure: bool = False,
    fuel_failure_reason: str = None,
    generator_starts: int = 2,
    initial_battery_soc_pct: float = 80.0,
    terminal_battery_soc_pct: float = 80.0,
    initial_battery_energy_wh: float = 160000.0,
    terminal_battery_energy_wh: float = 160000.0,
    delta_e_term_wh: float = 0.0,
    startup_surcharge_liters: float = 12.0,
    realized_trajectory_hash: str = "traj_hash_123",
    non_solar_forecast_hash: str = "forecast_hash_123",
    resolved_terminal_target_wh: float = 120000.0,
    resolved_ebr_target_wh: tuple = (15000.0,) * 24,
    fold_label: str = "test_fold",
    **kwargs,
) -> OriginRunResult:
    return OriginRunResult(
        origin=origin,
        arm=arm,
        scenario_key=origin,
        forecast_provider="n6_solar" if arm == "candidate" else "causal_nwp_gamma1",
        run_status=run_status,
        completed_steps=completed_steps,
        expected_steps=expected_steps,
        diesel_consumed_liters=diesel_consumed_liters,
        critical_unmet_load_wh=critical_unmet_load_wh,
        total_unmet_load_wh=total_unmet_load_wh,
        safety_evidence_status=safety_evidence_status,
        safety_passed=safety_passed,
        optimizer_constraint_status="OPTIMAL" if run_status == OriginRunStatus.OPTIMAL else "INFEASIBLE",
        failure_reasons=(),
        provenance={"test": "provenance"},
        has_solver_failure=has_solver_failure,
        has_unmet_essential=has_unmet_essential,
        has_fuel_failure=has_fuel_failure,
        fuel_failure_reason=fuel_failure_reason,
        generator_starts=generator_starts,
        initial_battery_soc_pct=initial_battery_soc_pct,
        terminal_battery_soc_pct=terminal_battery_soc_pct,
        initial_battery_energy_wh=initial_battery_energy_wh,
        terminal_battery_energy_wh=terminal_battery_energy_wh,
        delta_e_term_wh=delta_e_term_wh,
        startup_surcharge_liters=startup_surcharge_liters,
        realized_trajectory_hash=realized_trajectory_hash,
        non_solar_forecast_hash=non_solar_forecast_hash,
        resolved_terminal_target_wh=resolved_terminal_target_wh,
        resolved_ebr_target_wh=resolved_ebr_target_wh,
        fold_label=fold_label,
        **kwargs,
    )


class TestBlockerAuth2TwoStageAuthorization(unittest.TestCase):
    """
    Validates [BLOCKER-AUTH-2]: Two-stage authorization enforcement.
    Campaign execution must be fail-closed, default-denied, strictly parameterized,
    and unconditionally blocked at post-test sign-off stage.
    """

    def setUp(self):
        self.settings = _controller_settings()
        self.origins = list(APPROVED_ORIGINS)
        self.soc_by_origin = {o: 160000.0 for o in self.origins}
        self.config = build_multi_origin_campaign_config(
            origins=self.origins,
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=self.settings,
            initial_battery_soc_wh_by_origin=self.soc_by_origin,
            governed_reserve_policy_name="governed",
        )
        self.harness = MultiOriginCampaignHarness()
        self.replay = FactorIsolatedReplayHarness()

    def test_01_default_denial_without_auth_raises_campaign_not_authorized(self):
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            self.harness.execute_campaign(self.config)
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            self.replay.execute_experiment_a(self.config.experiment_a_config)

    def test_02_valid_auth_token_still_blocked_awaiting_post_test_sign_off(self):
        # Even a fully valid DiagnosticExecutionAuthorization token must raise
        # CampaignExecutionNotAuthorizedError because execution_stage_status is BLOCKED_AWAITING_POST_TEST_SIGN_OFF
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_BLOCKED_AWAITING_POST_TEST_SIGN_OFF,
            classification=APPROVED_CLASSIFICATION,
            protocol=APPROVED_PROTOCOL,
            origins=APPROVED_ORIGINS,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared=None,
            protected_file_hashes=dict(REGISTERED_PROTECTED_FILE_HASHES),
        )
        with self.assertRaises(CampaignExecutionNotAuthorizedError) as ctx:
            self.harness.execute_campaign(self.config, auth=auth)
        self.assertIn("BLOCKED_AWAITING_POST_TEST_SIGN_OFF", str(ctx.exception))

    def test_03_tampered_study_classification_raises_campaign_not_authorized(self):
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
            classification="PRODUCTION_REPLAY_SAVINGS_CLAIM",
            protocol=APPROVED_PROTOCOL,
            origins=APPROVED_ORIGINS,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared=None,
            protected_file_hashes=dict(REGISTERED_PROTECTED_FILE_HASHES),
        )
        with self.assertRaises(CampaignExecutionNotAuthorizedError) as ctx:
            validate_diagnostic_execution_authorization(auth)
        self.assertIn("classification", str(ctx.exception))

    def test_04_tampered_origins_list_raises_campaign_not_authorized(self):
        tampered_origins = ("2024-06-01", "2024-06-02")
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
            classification=APPROVED_CLASSIFICATION,
            protocol=APPROVED_PROTOCOL,
            origins=tampered_origins,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared=None,
            protected_file_hashes=dict(REGISTERED_PROTECTED_FILE_HASHES),
        )
        with self.assertRaises(CampaignExecutionNotAuthorizedError) as ctx:
            validate_diagnostic_execution_authorization(auth)
        self.assertIn("origins", str(ctx.exception))

    def test_05_declared_winner_non_none_rejected_fail_closed(self):
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
            classification=APPROVED_CLASSIFICATION,
            protocol=APPROVED_PROTOCOL,
            origins=APPROVED_ORIGINS,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared="candidate_n6",
            protected_file_hashes=dict(REGISTERED_PROTECTED_FILE_HASHES),
        )
        with self.assertRaises(CampaignExecutionNotAuthorizedError) as ctx:
            validate_diagnostic_execution_authorization(auth)
        self.assertIn("winner_declared must be None", str(ctx.exception))

    def test_06_protected_files_sha256_verification(self):
        # Verify that all 7 protected files exist and match their registered SHA-256 hashes
        repo_root = Path("/home/punith-bs/01polaris (Copy)")
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
            classification=APPROVED_CLASSIFICATION,
            protocol=APPROVED_PROTOCOL,
            origins=APPROVED_ORIGINS,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared=None,
            protected_file_hashes=dict(REGISTERED_PROTECTED_FILE_HASHES),
        )
        # Should validate without raising SecurityIntegrityViolationError on disk
        validate_diagnostic_execution_authorization(auth, repo_root=repo_root)

    def test_07_tampered_file_hash_raises_security_integrity_violation(self):
        tampered_hashes = dict(REGISTERED_PROTECTED_FILE_HASHES)
        tampered_hashes["system/control/router.py"] = "0000000000000000000000000000000000000000000000000000000000000000"
        auth = DiagnosticExecutionAuthorization(
            execution_stage_status=EXECUTION_STAGE_AUTHORIZED_BY_OWNER,
            classification=APPROVED_CLASSIFICATION,
            protocol=APPROVED_PROTOCOL,
            origins=APPROVED_ORIGINS,
            initial_soc_pct=APPROVED_INITIAL_SOC_PCT,
            initial_battery_energy_wh=APPROVED_INITIAL_ENERGY_WH,
            initial_fuel_liters=APPROVED_INITIAL_FUEL_L,
            initial_generator_running=APPROVED_INITIAL_GEN_RUNNING,
            winner_declared=None,
            protected_file_hashes=tampered_hashes,
        )
        with self.assertRaises(SecurityIntegrityViolationError) as ctx:
            validate_diagnostic_execution_authorization(auth)
        self.assertIn("router.py", str(ctx.exception))


class TestBlockerFuel1FuelGuardsAndLatching(unittest.TestCase):
    """
    Validates [BLOCKER-FUEL-1]: Per-step fuel exhaustion, clamping detection,
    monotonicity violation, and tracking gap latching.
    """

    def test_01_fuel_exhaustion_at_or_below_threshold_latches_failure(self):
        # Remaining fuel <= 1e-4 L while generator is commanded latches fuel failure
        outcome = DispatchOutcomeView.at_hour(
            real_dispatch_plan=type(
                "FakePlan", (), {"unmet_load": [0.0] * 24, "constraint_status": "OPTIMAL", "unmet_essential": [0.0] * 24}
            )(),
            hour_index=0,
            cumulative_diesel_consumed_liters=None,
            has_fuel_failure=True,
            fuel_failure_reason="FUEL_EXHAUSTED_AT_STEP: generator dispatched with fuel <= threshold",
        )
        self.assertTrue(outcome["has_fuel_failure"])
        self.assertIn("FUEL_EXHAUSTED_AT_STEP", outcome["fuel_failure_reason"])

        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome=outcome,
            safety_evaluation=None,
            provenance={},
        )
        self.assertTrue(res.has_fuel_failure)
        self.assertIsNone(res.diesel_consumed_liters)
        self.assertIn("FUEL_EXHAUSTED_AT_STEP", res.failure_reasons[0])

    def test_02_simulator_clamping_detection_latches_fuel_failure(self):
        # When required_fuel > available_fuel + 1e-6, the simulator clamps to 0.0.
        # The adapter detects this clamping and latches failure.
        outcome = DispatchOutcomeView.at_hour(
            real_dispatch_plan=type(
                "FakePlan", (), {"unmet_load": [0.0] * 24, "constraint_status": "OPTIMAL", "unmet_essential": [0.0] * 24}
            )(),
            hour_index=0,
            has_fuel_failure=True,
            fuel_failure_reason="FUEL_EXHAUSTION_CLAMPED: required fuel 5.0 L exceeds available fuel 2.0 L",
        )
        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome=outcome,
            safety_evaluation=None,
            provenance={},
        )
        self.assertTrue(res.has_fuel_failure)
        self.assertIsNone(res.diesel_consumed_liters)
        self.assertIn("FUEL_EXHAUSTION_CLAMPED", res.fuel_failure_reason)

    def test_03_monotonicity_violation_fuel_increase_latches_failure(self):
        # Physical fuel must never increase: fuel_after > fuel_before + 1e-6 latches failure
        outcome = DispatchOutcomeView.at_hour(
            real_dispatch_plan=type(
                "FakePlan", (), {"unmet_load": [0.0] * 24, "constraint_status": "OPTIMAL", "unmet_essential": [0.0] * 24}
            )(),
            hour_index=0,
            has_fuel_failure=True,
            fuel_failure_reason="FUEL_MONOTONICITY_VIOLATED: fuel increased from 10.0 L to 15.0 L",
        )
        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome=outcome,
            safety_evaluation=None,
            provenance={},
        )
        self.assertTrue(res.has_fuel_failure)
        self.assertIsNone(res.diesel_consumed_liters)
        self.assertIn("FUEL_MONOTONICITY_VIOLATED", res.fuel_failure_reason)

    def test_04_fuel_tracking_gap_sets_diesel_to_none_and_records_gap(self):
        # If diesel consumed is missing (None) in completed run, diesel_fuel_tracking_gap is latched
        res = record_origin_outcome(
            origin="o1",
            arm="baseline",
            scenario_key="o1",
            forecast_provider="causal_nwp_gamma1",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"diesel_consumed_liters": None, "constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
        )
        self.assertTrue(res.diesel_fuel_tracking_gap)
        self.assertIsNone(res.diesel_consumed_liters)

    def _build_test_adapter_fixture(self, is_receding: bool = False):
        class _TestState:
            def __init__(
                self,
                timestamp="t0",
                battery_soc_pct=80.0,
                diesel_fuel_remaining_liters=500.0,
                battery_energy_wh=160000.0,
            ):
                self.timestamp = timestamp
                self.battery_soc_pct = battery_soc_pct
                self.diesel_fuel_remaining_liters = diesel_fuel_remaining_liters
                self.battery_energy_wh = battery_energy_wh
                self.diesel_running = False
                self.diesel_hours_running = 0.0

            def to_dict(self):
                return {
                    "timestamp": self.timestamp,
                    "battery_soc_pct": self.battery_soc_pct,
                    "diesel_fuel_remaining_liters": self.diesel_fuel_remaining_liters,
                    "battery_energy_wh": self.battery_energy_wh,
                    "diesel_running": self.diesel_running,
                    "diesel_hours_running": self.diesel_hours_running,
                }

            @classmethod
            def from_dict(cls, data):
                return cls(**data)

        class _TestPlan:
            def __init__(self, diesel_power_val=1000.0, **kwargs):
                self.schema_version = kwargs.get("schema_version", "1.0.0")
                self.timestamps = kwargs.get("timestamps", [f"T{i}" for i in range(24)])
                self.solar_used = kwargs.get("solar_used", [0.0] * 24)
                self.wind_used = kwargs.get("wind_used", [0.0] * 24)
                self.battery_charge = kwargs.get("battery_charge", [0.0] * 24)
                self.battery_discharge = kwargs.get("battery_discharge", [0.0] * 24)
                self.battery_soc = kwargs.get("battery_soc", [160000.0] * 24)
                self.diesel_power = kwargs.get("diesel_power", [diesel_power_val] * 24)
                self.load_served = kwargs.get("load_served", [5000.0] * 24)
                self.flexible_load_schedule = kwargs.get("flexible_load_schedule", [0.0] * 24)
                self.renewable_curtailment = kwargs.get("renewable_curtailment", [0.0] * 24)
                self.unmet_load = kwargs.get("unmet_load", [0.0] * 24)
                self.objective_value = kwargs.get("objective_value", 0.0)
                self.constraint_status = kwargs.get("constraint_status", "OPTIMAL")
                self.energy_balance_errors = kwargs.get("energy_balance_errors", [0.0] * 24)

        class _RealSim:
            def step(self, station_state, one_hour_slice, actual_t):
                p_dis = one_hour_slice.diesel_power[0]
                p_val = float(p_dis) if p_dis is not None else 0.0
                req = ((5.0 if p_val > 0.0 else 0.0) + (0.00025 * p_val)) * 1.0
                return _TestState(
                    timestamp=one_hour_slice.timestamps[0],
                    battery_soc_pct=station_state.battery_soc_pct,
                    diesel_fuel_remaining_liters=round(station_state.diesel_fuel_remaining_liters - req, 4),
                    battery_energy_wh=station_state.battery_energy_wh,
                )

        spy_sim = MagicMock(wraps=_RealSim())
        if is_receding:
            adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
                real_simulator=spy_sim,
                dispatch_plan_cls=_TestPlan,
                actuals_by_origin_and_step={"o1": [{"actual_SW_IN": 0.0, "actual_demand": 5000.0, "actual_wind_generation": 0.0, "timestamp": "t0"}] * 24},
                _allow_synthetic_actuals_for_testing=True,
            )
        else:
            adapter = SingleShotPlanSlicingSimulatorAdapter(
                real_simulator=spy_sim,
                dispatch_plan_cls=_TestPlan,
                actuals_by_origin_and_step={"o1": [{"actual_SW_IN": 0.0, "actual_demand": 5000.0, "actual_wind_generation": 0.0, "timestamp": "t0"}] * 24},
                station_state_cls=_TestState,
                _allow_synthetic_actuals_for_testing=True,
            )
        return adapter, spy_sim, _TestState, _TestPlan

    def test_05_pre_call_fuel_rejection_spy_mock_single_shot(self):
        # 1. Reject invalid fuel values: None, "100.0", True, NaN, +inf, -inf, -0.01, 0.0, 1e-4
        invalid_fuels = [None, "100.0", True, float("nan"), float("inf"), float("-inf"), -0.01, 0.0, 1e-4]
        for bad_fuel in invalid_fuels:
            adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
            state_obj = _TestState(diesel_fuel_remaining_liters=bad_fuel)
            state_dict = state_obj.to_dict()
            state_dict["_real_station_state_ref"] = state_obj
            state_dict["_step_index"] = 0
            plan_obj = _TestPlan(diesel_power_val=1000.0)
            dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

            res = adapter.step(state_dict, dispatch_dict)
            spy_sim.step.assert_not_called()
            self.assertTrue(res["stop_early"], f"Expected stop_early=True for fuel={bad_fuel}")
            self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
            self.assertIsNone(res["dispatch_outcome"]["diesel_consumed_liters"])
            self.assertTrue(res["state"]["_has_fuel_failure"])

        # 2. Reject negative and non-finite diesel power
        invalid_powers = [-100.0, float("nan"), float("inf"), "invalid_power"]
        for bad_p in invalid_powers:
            adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
            state_obj = _TestState(diesel_fuel_remaining_liters=500.0)
            state_dict = state_obj.to_dict()
            state_dict["_real_station_state_ref"] = state_obj
            state_dict["_step_index"] = 0
            plan_obj = _TestPlan(diesel_power_val=bad_p)
            dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

            res = adapter.step(state_dict, dispatch_dict)
            spy_sim.step.assert_not_called()
            self.assertTrue(res["stop_early"])
            self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
            self.assertIsNone(res["dispatch_outcome"]["diesel_consumed_liters"])

        # 3. Reject insufficient fuel with zero slack: required_fuel > fuel_before
        # Case 3a: fuel_before = 5.0, required = 5.0001 (p_diesel = 0.4 W)
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj = _TestState(diesel_fuel_remaining_liters=5.0)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=0.4)  # req = 5.0 + 0.00025 * 0.4 = 5.0001 L
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_not_called()
        self.assertTrue(res["stop_early"])
        self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
        self.assertIn("FUEL_EXHAUSTION_CLAMPED", res["dispatch_outcome"]["fuel_failure_reason"])

        # Case 3b: fuel_before = 5.0, required = 5.0 + 5e-7 (p_diesel = 0.002 W)
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj = _TestState(diesel_fuel_remaining_liters=5.0)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=0.002)  # req = 5.0 + 0.00025 * 0.002 = 5.0000005 L
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_not_called()
        self.assertTrue(res["stop_early"])
        self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
        self.assertIn("FUEL_EXHAUSTION_CLAMPED", res["dispatch_outcome"]["fuel_failure_reason"])

        # 4. Positive test: valid fuel and valid power -> simulator.step.assert_called_once()
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj = _TestState(diesel_fuel_remaining_liters=500.0)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=1000.0)  # req = 5.0 + 0.25 = 5.25 L <= 500.0 L
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_called_once()
        self.assertFalse(res["stop_early"])
        self.assertFalse(res["dispatch_outcome"].get("has_fuel_failure", False))
        self.assertEqual(res["dispatch_outcome"]["diesel_consumed_liters"], 5.25)

    def test_06_pre_call_fuel_rejection_spy_mock_receding_horizon(self):
        # Repeat exact verification for RecedingHorizonPlanSlicingSimulatorAdapter
        invalid_fuels = [None, "100.0", True, float("nan"), float("inf"), float("-inf"), -0.01, 0.0, 1e-4]
        for bad_fuel in invalid_fuels:
            adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=True)
            state_obj = _TestState(diesel_fuel_remaining_liters=bad_fuel)
            state_dict = state_obj.to_dict()
            state_dict["_real_station_state_ref"] = state_obj
            state_dict["_step_index"] = 0
            plan_obj = _TestPlan(diesel_power_val=1000.0)
            dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

            res = adapter.step(state_dict, dispatch_dict)
            spy_sim.step.assert_not_called()
            self.assertTrue(res["stop_early"], f"Expected stop_early=True for fuel={bad_fuel}")
            self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
            self.assertIsNone(res["dispatch_outcome"]["diesel_consumed_liters"])
            self.assertTrue(res["state"]["_has_fuel_failure"])

        # Positive test: valid fuel and valid power
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=True)
        state_obj = _TestState(diesel_fuel_remaining_liters=500.0)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=1000.0)
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_called_once()
        self.assertFalse(res["stop_early"])
        self.assertFalse(res["dispatch_outcome"].get("has_fuel_failure", False))
        self.assertEqual(res["dispatch_outcome"]["diesel_consumed_liters"], 5.25)

    def test_07_residual_gap_fuel_exhaustion_pre_call_guard_spy_single_shot(self):
        # [BLOCKER-FUEL-1 Residual Gap]:
        # fuel_before = 5.00005 L, required_fuel = 5.0 L (e.g. p_diesel = 1e-12 W).
        # fuel_before > 1e-4 L (passes check 2).
        # required_fuel <= fuel_before (passes check 3).
        # BUT fuel_after = 5.00005 - 5.0 = 0.00005 L <= 1e-4 L (FUEL_EXHAUSTION_THRESHOLD_L).
        # Adapter MUST reject and latch failure BEFORE calling simulator.step()!
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj = _TestState(diesel_fuel_remaining_liters=5.00005)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=1e-12)  # required_fuel = 5.0 + 2.5e-16 ≈ 5.0 L
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_not_called()
        self.assertTrue(res["stop_early"])
        self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
        self.assertIsNone(res["dispatch_outcome"]["diesel_consumed_liters"])
        self.assertTrue(res["state"]["_has_fuel_failure"])
        self.assertIn("FUEL_EXHAUSTED_AT_STEP", res["dispatch_outcome"]["fuel_failure_reason"])

    def test_08_residual_gap_fuel_exhaustion_pre_call_guard_spy_receding_horizon(self):
        # Same residual gap verification for RecedingHorizonPlanSlicingSimulatorAdapter
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=True)
        state_obj = _TestState(diesel_fuel_remaining_liters=5.00005)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_not_called()
        self.assertTrue(res["stop_early"])
        self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
        self.assertIsNone(res["dispatch_outcome"]["diesel_consumed_liters"])
        self.assertTrue(res["state"]["_has_fuel_failure"])
        self.assertIn("FUEL_EXHAUSTED_AT_STEP", res["dispatch_outcome"]["fuel_failure_reason"])

    def test_09_residual_gap_boundary_values(self):
        # Precise boundary values around 1e-4 threshold:
        # Case 1: fuel_before = 5.0001000, required = 5.0 -> fuel_after = 0.0001000 <= 1e-4 -> REJECTED
        adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj = _TestState(diesel_fuel_remaining_liters=5.0001000)
        state_dict = state_obj.to_dict()
        state_dict["_real_station_state_ref"] = state_obj
        state_dict["_step_index"] = 0
        plan_obj = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

        res = adapter.step(state_dict, dispatch_dict)
        spy_sim.step.assert_not_called()
        self.assertTrue(res["stop_early"])
        self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])

        # Case 2: fuel_before = 5.0001001, required = 5.0 -> round(0.0001001, 4) = 0.0001 <= 1e-4 -> PRE-CALL REJECTED
        # Note: 4-decimal pre-call rounding matches DigitalTwinSimulator.step()'s round(next_fuel, 4).
        # This prevents simulator state mutation!
        adapter2, spy_sim2, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj2 = _TestState(diesel_fuel_remaining_liters=5.0001001)
        state_dict2 = state_obj2.to_dict()
        state_dict2["_real_station_state_ref"] = state_obj2
        state_dict2["_step_index"] = 0
        plan_obj2 = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict2 = {"_real_plan_ref": plan_obj2, "origin": "o1"}

        res2 = adapter2.step(state_dict2, dispatch_dict2)
        spy_sim2.step.assert_not_called()
        self.assertTrue(res2["stop_early"])
        self.assertTrue(res2["dispatch_outcome"]["has_fuel_failure"])

        # Case 2b: fuel_before = 5.0001499, required = 5.0 -> round(0.0001499, 4) = 0.0001 <= 1e-4 -> PRE-CALL REJECTED
        adapter2b, spy_sim2b, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj2b = _TestState(diesel_fuel_remaining_liters=5.0001499)
        state_dict2b = state_obj2b.to_dict()
        state_dict2b["_real_station_state_ref"] = state_obj2b
        state_dict2b["_step_index"] = 0
        plan_obj2b = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict2b = {"_real_plan_ref": plan_obj2b, "origin": "o1"}

        res2b = adapter2b.step(state_dict2b, dispatch_dict2b)
        spy_sim2b.step.assert_not_called()
        self.assertTrue(res2b["stop_early"])
        self.assertTrue(res2b["dispatch_outcome"]["has_fuel_failure"])

        # Case 2c: fuel_before = 5.0001501, required = 5.0 -> round(0.0001501, 4) = 0.0002 > 1e-4 -> PRE-CALL PASSES (calls simulator)
        adapter2c, spy_sim2c, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj2c = _TestState(diesel_fuel_remaining_liters=5.0001501)
        state_dict2c = state_obj2c.to_dict()
        state_dict2c["_real_station_state_ref"] = state_obj2c
        state_dict2c["_step_index"] = 0
        plan_obj2c = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict2c = {"_real_plan_ref": plan_obj2c, "origin": "o1"}

        res2c = adapter2c.step(state_dict2c, dispatch_dict2c)
        spy_sim2c.step.assert_called_once()
        self.assertFalse(res2c["stop_early"])
        self.assertFalse(res2c["dispatch_outcome"].get("has_fuel_failure", False))

        # Case 3: fuel_before = 5.0002000, required = 5.0 -> round(0.0002000, 4) = 0.0002 > 1e-4 -> FULLY PASSES
        adapter3, spy_sim3, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=False)
        state_obj3 = _TestState(diesel_fuel_remaining_liters=5.0002000)
        state_dict3 = state_obj3.to_dict()
        state_dict3["_real_station_state_ref"] = state_obj3
        state_dict3["_step_index"] = 0
        plan_obj3 = _TestPlan(diesel_power_val=1e-12)
        dispatch_dict3 = {"_real_plan_ref": plan_obj3, "origin": "o1"}

        res3 = adapter3.step(state_dict3, dispatch_dict3)
        spy_sim3.step.assert_called_once()
        self.assertFalse(res3["stop_early"])
        self.assertFalse(res3["dispatch_outcome"].get("has_fuel_failure", False))

    def test_08_fail_closed_zero_fuel_zero_power_both_adapters_spy(self):
        # Reject zero fuel before calling simulator, even when p_diesel == 0
        for is_receding in [False, True]:
            adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=is_receding)
            state_obj = _TestState(diesel_fuel_remaining_liters=0.0)
            state_dict = state_obj.to_dict()
            state_dict["_real_station_state_ref"] = state_obj
            state_dict["_step_index"] = 0
            plan_obj = _TestPlan(diesel_power_val=0.0)
            dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

            res = adapter.step(state_dict, dispatch_dict)
            spy_sim.step.assert_not_called()
            self.assertTrue(res["stop_early"])
            self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
            self.assertIsNone(res["dispatch_outcome"].get("diesel_consumed_liters"))
            self.assertIsNone(res["dispatch_outcome"].get("cumulative_diesel_consumed_liters"))
            self.assertIsNone(res["dispatch_outcome"].get("generator_starts"))
            self.assertIsNone(res["dispatch_outcome"].get("terminal_battery_soc_pct"))
            self.assertIsNone(res["dispatch_outcome"].get("terminal_battery_energy_wh"))
            self.assertIsNone(res["dispatch_outcome"].get("delta_e_term_wh"))
            self.assertIsNone(res["dispatch_outcome"].get("startup_surcharge_liters"))
            self.assertIsNone(res["state"].get("_cumulative_generator_starts"))
            self.assertIsNone(res["state"].get("_terminal_battery_soc_pct"))
            self.assertIsNone(res["state"].get("_delta_e_term_wh"))

    def test_09_threshold_edge_fuel_exhaustion_both_adapters_spy(self):
        # Reject threshold-edge fuel (1e-4 L) before calling simulator for both p_diesel=0 and p_diesel>0
        for is_receding in [False, True]:
            for p_diesel in [0.0, 50.0]:
                adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=is_receding)
                state_obj = _TestState(diesel_fuel_remaining_liters=FUEL_EXHAUSTION_THRESHOLD_L)
                state_dict = state_obj.to_dict()
                state_dict["_real_station_state_ref"] = state_obj
                state_dict["_step_index"] = 0
                plan_obj = _TestPlan(diesel_power_val=p_diesel)
                dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

                res = adapter.step(state_dict, dispatch_dict)
                spy_sim.step.assert_not_called()
                self.assertTrue(res["stop_early"])
                self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
                self.assertIsNone(res["dispatch_outcome"].get("diesel_consumed_liters"))
                self.assertIsNone(res["dispatch_outcome"].get("generator_starts"))
                self.assertIsNone(res["dispatch_outcome"].get("terminal_battery_soc_pct"))
                self.assertIsNone(res["dispatch_outcome"].get("delta_e_term_wh"))
                self.assertIsNone(res["state"].get("_cumulative_generator_starts"))
                self.assertIsNone(res["state"].get("_terminal_battery_soc_pct"))

    def test_10_excess_fuel_demand_zero_slack_both_adapters_spy(self):
        # Reject required fuel exceeding available fuel without slack (+1e-6)
        for is_receding in [False, True]:
            adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=is_receding)
            p_val = (5.0000001) / 0.00025  # required = 5.0 + 5.0000001 = 10.0000001 L > 10.0 L
            state_obj = _TestState(diesel_fuel_remaining_liters=10.0)
            state_dict = state_obj.to_dict()
            state_dict["_real_station_state_ref"] = state_obj
            state_dict["_step_index"] = 0
            plan_obj = _TestPlan(diesel_power_val=p_val)
            dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

            res = adapter.step(state_dict, dispatch_dict)
            spy_sim.step.assert_not_called()
            self.assertTrue(res["stop_early"])
            self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
            self.assertIn("FUEL_EXHAUSTION_CLAMPED", res["dispatch_outcome"]["fuel_failure_reason"])

    def test_11_previously_latched_failure_and_gap_rejects_pre_call_both_adapters_spy(self):
        # Reject calls when _diesel_fuel_tracking_gap or _has_fuel_failure was already latched
        for is_receding in [False, True]:
            for latch_key in ["_diesel_fuel_tracking_gap", "_has_fuel_failure"]:
                adapter, spy_sim, _TestState, _TestPlan = self._build_test_adapter_fixture(is_receding=is_receding)
                state_obj = _TestState(diesel_fuel_remaining_liters=500.0)
                state_dict = state_obj.to_dict()
                state_dict["_real_station_state_ref"] = state_obj
                state_dict["_step_index"] = 1
                state_dict[latch_key] = True
                plan_obj = _TestPlan(diesel_power_val=100.0)
                dispatch_dict = {"_real_plan_ref": plan_obj, "origin": "o1"}

                res = adapter.step(state_dict, dispatch_dict)
                spy_sim.step.assert_not_called()
                self.assertTrue(res["stop_early"])
                self.assertTrue(res["dispatch_outcome"]["has_fuel_failure"])
                self.assertIsNone(res["dispatch_outcome"].get("generator_starts"))
                self.assertIsNone(res["dispatch_outcome"].get("terminal_battery_soc_pct"))
                self.assertIsNone(res["dispatch_outcome"].get("delta_e_term_wh"))
                self.assertIsNone(res["dispatch_outcome"].get("startup_surcharge_liters"))
                self.assertIsNone(res["state"].get("_cumulative_generator_starts"))
                self.assertIsNone(res["state"].get("_terminal_battery_soc_pct"))


class TestAuthoritativeRealizedDataLoader(unittest.TestCase):
    """
    Validates Workstream C: Authoritative Realized Environmental Actuals Loader.
    Authoritative source: ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv (8,784 rows, SHA-256 pinned).
    """

    def test_01_load_approved_origins_june_1_to_7_matches_shape_and_range(self):
        origins = list(APPROVED_ORIGINS)
        actuals = load_authoritative_actuals_by_origin(
            fixture_path=CANONICAL_FIXTURE_RELATIVE_PATH,
            origins=origins,
            steps_per_origin=24,
            verify_sha256=True,
        )
        self.assertEqual(len(actuals), len(origins))
        for origin in origins:
            self.assertIn(origin, actuals)
            steps = actuals[origin]
            self.assertEqual(len(steps), 24)
            # Step 0 transition consumes t0 + 1h; step 23 consumes t0 + 24h
            self.assertEqual(steps[0]["timestamp"], f"{origin}T01:00:00Z")
            for s in steps:
                self.assertIn("actual_SW_IN", s)
                self.assertIn("actual_demand", s)
                self.assertIn("actual_wind_generation", s)
                self.assertGreaterEqual(s["actual_SW_IN"], 0.0)
                self.assertGreaterEqual(s["actual_demand"], 0.0)
                self.assertGreaterEqual(s["actual_wind_generation"], 0.0)

        # June 7 boundary check: step 0 is 2024-06-07T01:00:00Z, step 23 is 2024-06-08T00:00:00Z
        june7_steps = actuals["2024-06-07"]
        self.assertEqual(june7_steps[0]["timestamp"], "2024-06-07T01:00:00Z")
        self.assertEqual(june7_steps[-1]["timestamp"], "2024-06-08T00:00:00Z")

    def test_02_load_fails_closed_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_authoritative_actuals_by_origin(
                fixture_path="data/real_weather_2024.csv",
                origins=["2024-06-01"],
            )

    def test_03_load_fails_closed_on_corrupt_sha256(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
            tf.write("2024-06-01T00:00:00Z,10.0,5000.0,1000.0\n")
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=True,
                )
            self.assertIn("SHA-256 mismatch", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_04_load_fails_closed_on_missing_origin(self):
        with self.assertRaises(KeyError) as ctx:
            load_authoritative_actuals_by_origin(
                fixture_path=CANONICAL_FIXTURE_RELATIVE_PATH,
                origins=["2023-01-01"],
                steps_per_origin=24,
                verify_sha256=True,
            )
        self.assertIn("Missing actual observation", str(ctx.exception))

    def test_05_load_fails_closed_on_missing_required_column(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            # Missing synthetic_load_W
            tf.write("timestamp,solar_SW_IN_W_m2,wind_power_generic_W\n")
            tf.write("2024-06-01T01:00:00Z,10.0,1000.0\n")
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=False,
                )
            self.assertIn("Missing required column", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_06_load_fails_closed_on_non_monotonic_timestamps(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
            tf.write("2024-06-01T02:00:00Z,10.0,5000.0,1000.0\n")
            tf.write("2024-06-01T01:00:00Z,10.0,5000.0,1000.0\n")
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=False,
                )
            self.assertIn("Non-monotonic or duplicate timestamp", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_07_load_fails_closed_on_duplicate_timestamps(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
            tf.write("2024-06-01T01:00:00Z,10.0,5000.0,1000.0\n")
            tf.write("2024-06-01T01:00:00Z,10.0,5000.0,1000.0\n")
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=False,
                )
            self.assertIn("Non-monotonic or duplicate timestamp", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_08_load_fails_closed_on_irregular_interval(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
            tf.write("2024-06-01T01:00:00Z,10.0,5000.0,1000.0\n")
            tf.write("2024-06-01T03:00:00Z,10.0,5000.0,1000.0\n")  # 2h jump
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=False,
                )
            self.assertIn("Irregular time interval", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_09_load_fails_closed_on_non_utc_timezone(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
            tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
            tf.write("2024-06-01T01:00:00+05:30,10.0,5000.0,1000.0\n")
            temp_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_authoritative_actuals_by_origin(
                    fixture_path=temp_path,
                    origins=["2024-06-01"],
                    verify_sha256=False,
                )
            self.assertIn("Non-UTC timestamp", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_10_load_fails_closed_on_nan_and_inf_values(self):
        import tempfile
        for bad_val in ["nan", "inf", "-inf"]:
            with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
                tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
                tf.write(f"2024-06-01T01:00:00Z,{bad_val},5000.0,1000.0\n")
                temp_path = tf.name

            try:
                with self.assertRaises(ValueError):
                    load_authoritative_actuals_by_origin(
                        fixture_path=temp_path,
                        origins=["2024-06-01"],
                        verify_sha256=False,
                    )
            finally:
                Path(temp_path).unlink(missing_ok=True)

    def test_11_load_fails_closed_on_negative_values(self):
        import tempfile
        for row in [
            "2024-06-01T01:00:00Z,-1.0,5000.0,1000.0\n",
            "2024-06-01T01:00:00Z,10.0,-5.0,1000.0\n",
            "2024-06-01T01:00:00Z,10.0,5000.0,-10.0\n",
        ]:
            with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as tf:
                tf.write("timestamp,solar_SW_IN_W_m2,synthetic_load_W,wind_power_generic_W\n")
                tf.write(row)
                temp_path = tf.name

            try:
                with self.assertRaises(ValueError) as ctx:
                    load_authoritative_actuals_by_origin(
                        fixture_path=temp_path,
                        origins=["2024-06-01"],
                        verify_sha256=False,
                    )
                self.assertIn("Negative", str(ctx.exception))
            finally:
                Path(temp_path).unlink(missing_ok=True)

    def test_12_load_fails_closed_on_empty_origins(self):
        with self.assertRaises(ValueError) as ctx:
            load_authoritative_actuals_by_origin(
                origins=[],
                verify_sha256=False,
            )
        self.assertIn("origins", str(ctx.exception).lower())

    def test_13_load_fails_closed_on_unaligned_origin_minute(self):
        with self.assertRaises(ValueError) as ctx:
            load_authoritative_actuals_by_origin(
                origins=["2024-06-01T00:30:00Z"],
                verify_sha256=False,
            )
        self.assertIn("aligned to an hourly boundary", str(ctx.exception).lower())

    def test_14_load_fails_closed_on_non_utc_origin_string(self):
        with self.assertRaises(ValueError) as ctx:
            load_authoritative_actuals_by_origin(
                origins=["2024-06-01T00:00:00+05:30"],
                verify_sha256=False,
            )
        self.assertIn("utc", str(ctx.exception).lower())

    def test_15_direct_construction_with_arbitrary_dict_fails_closed_by_default(self):
        # (a) Direct construction with arbitrary dicts fails closed by default
        arbitrary_dict = {"o1": [{"actual_SW_IN": 0.0, "actual_demand": 1000.0, "actual_wind_generation": 0.0, "timestamp": "t0"}] * 24}
        with self.assertRaises(ValueError) as ctx:
            SingleShotPlanSlicingSimulatorAdapter(
                real_simulator=MagicMock(),
                dispatch_plan_cls=MagicMock(),
                actuals_by_origin_and_step=arbitrary_dict,
                station_state_cls=MagicMock(),
            )
        self.assertIn("unverified actuals is prohibited", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            RecedingHorizonPlanSlicingSimulatorAdapter(
                real_simulator=MagicMock(),
                dispatch_plan_cls=MagicMock(),
                actuals_by_origin_and_step=arbitrary_dict,
            )
        self.assertIn("unverified actuals is prohibited", str(ctx.exception))

    def test_16_construction_via_from_authoritative_fixture_succeeds_with_verification(self):
        # (b) Construction via from_authoritative_fixture() succeeds against canonical H1.0 fixture with verify_sha256=True
        origins = ["2024-06-01"]
        adapter_ss = SingleShotPlanSlicingSimulatorAdapter.from_authoritative_fixture(
            real_simulator=MagicMock(),
            dispatch_plan_cls=MagicMock(),
            station_state_cls=MagicMock(),
            fixture_path=CANONICAL_FIXTURE_RELATIVE_PATH,
            origins=origins,
            steps_per_origin=24,
            verify_sha256=True,
        )
        self.assertIn("2024-06-01", adapter_ss._actuals_by_origin_and_step)
        self.assertEqual(len(adapter_ss._actuals_by_origin_and_step["2024-06-01"]), 24)

        adapter_rh = RecedingHorizonPlanSlicingSimulatorAdapter.from_authoritative_fixture(
            real_simulator=MagicMock(),
            dispatch_plan_cls=MagicMock(),
            fixture_path=CANONICAL_FIXTURE_RELATIVE_PATH,
            origins=origins,
            steps_per_origin=24,
            verify_sha256=True,
        )
        self.assertIn("2024-06-01", adapter_rh._actuals_by_origin_and_step)
        self.assertEqual(len(adapter_rh._actuals_by_origin_and_step["2024-06-01"]), 24)

    def test_17_synthetic_construction_works_via_explicit_testing_flag(self):
        # (c) Synthetic tests work via the explicit test-only flag
        synthetic_dict = {"o1": [{"actual_SW_IN": 0.0, "actual_demand": 1000.0, "actual_wind_generation": 0.0, "timestamp": "t0"}] * 24}
        adapter_ss = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=MagicMock(),
            dispatch_plan_cls=MagicMock(),
            actuals_by_origin_and_step=synthetic_dict,
            station_state_cls=MagicMock(),
            _allow_synthetic_actuals_for_testing=True,
        )
        self.assertIs(adapter_ss._actuals_by_origin_and_step, synthetic_dict)

        adapter_rh = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=MagicMock(),
            dispatch_plan_cls=MagicMock(),
            actuals_by_origin_and_step=synthetic_dict,
            _allow_synthetic_actuals_for_testing=True,
        )
        self.assertIs(adapter_rh._actuals_by_origin_and_step, synthetic_dict)


class TestBlockerParity1DeterministicHashingAndComparison(unittest.TestCase):
    """
    Validates [BLOCKER-PARITY-1]: Deterministic canonical hashing, resolved terminal target
    parity, and fail-closed paired origin comparison.
    """

    def test_01_canonical_realized_trajectory_hash_determinism(self):
        data1 = {"step": 1, "ghi": 500.25, "temp": 20.0, "demand": 4500.0}
        data2 = {"demand": 4500.0, "temp": 20.0, "ghi": 500.25, "step": 1}
        hash1 = compute_canonical_realized_trajectory_hash(data1)
        hash2 = compute_canonical_realized_trajectory_hash(data2)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_02_canonical_non_solar_forecast_hash_determinism(self):
        f1 = {"demand_point": [100.0, 200.0], "wind_point": [50.0, 60.0]}
        f2 = {"wind_point": [50.0, 60.0], "demand_point": [100.0, 200.0]}
        h1 = compute_canonical_non_solar_forecast_hash(f1)
        h2 = compute_canonical_non_solar_forecast_hash(f2)
        self.assertEqual(h1, h2)

    def test_03_paired_comparison_valid_matches_produce_correct_metrics_and_winner_none(self):
        base = _build_test_origin_run_result(
            origin="o1",
            arm="baseline",
            diesel_consumed_liters=30.0,
            generator_starts=3,
            startup_surcharge_liters=18.0,
            delta_e_term_wh=-5000.0,
            realized_trajectory_hash="hash_same",
            non_solar_forecast_hash="non_solar_same",
            resolved_terminal_target_wh=120000.0,
            resolved_ebr_target_wh=(10000.0,) * 24,
        )
        cand = _build_test_origin_run_result(
            origin="o1",
            arm="candidate",
            diesel_consumed_liters=24.0,
            generator_starts=2,
            startup_surcharge_liters=12.0,
            delta_e_term_wh=-1000.0,
            realized_trajectory_hash="hash_same",
            non_solar_forecast_hash="non_solar_same",
            resolved_terminal_target_wh=120000.0,
            resolved_ebr_target_wh=(10000.0,) * 24,
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertTrue(cmp_res.is_valid_comparison)
        self.assertEqual(cmp_res.status, "VALID_MATCHED_PAIR")
        # Net savings = baseline - candidate = 30.0 - 24.0 = 6.0 L
        self.assertAlmostEqual(cmp_res.net_diesel_savings_liters, 6.0)
        # Net delta E = candidate - baseline = -1000.0 - (-5000.0) = +4000.0 Wh
        self.assertAlmostEqual(cmp_res.net_delta_e_term_wh, 4000.0)
        # Net starts = candidate - baseline = 2 - 3 = -1 start
        self.assertEqual(cmp_res.net_generator_starts, -1)
        # Net startup surcharge = baseline - candidate = 18.0 - 12.0 = 6.0 L
        self.assertAlmostEqual(cmp_res.net_startup_surcharge_liters, 6.0)
        # Winner must unconditionally remain None
        self.assertIsNone(cmp_res.winner)

    def test_04_paired_comparison_fails_closed_on_realized_trajectory_hash_mismatch(self):
        base = _build_test_origin_run_result(arm="baseline", realized_trajectory_hash="hash_A")
        cand = _build_test_origin_run_result(arm="candidate", realized_trajectory_hash="hash_B")
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertEqual(cmp_res.status, "INVALID_PAIR_TRAJECTORY_MISMATCH")
        self.assertIsNone(cmp_res.net_diesel_savings_liters)
        self.assertIsNone(cmp_res.winner)

    def test_05_paired_comparison_fails_closed_on_non_solar_forecast_hash_mismatch(self):
        base = _build_test_origin_run_result(
            arm="baseline", realized_trajectory_hash="h1", non_solar_forecast_hash="f_base"
        )
        cand = _build_test_origin_run_result(
            arm="candidate", realized_trajectory_hash="h1", non_solar_forecast_hash="f_cand"
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertEqual(cmp_res.status, "INVALID_PAIR_FORECAST_MISMATCH")
        self.assertIsNone(cmp_res.winner)

    def test_06_paired_comparison_fails_closed_on_terminal_target_mismatch(self):
        base = _build_test_origin_run_result(
            arm="baseline",
            realized_trajectory_hash="h1",
            non_solar_forecast_hash="f1",
            resolved_terminal_target_wh=120000.0,
        )
        cand = _build_test_origin_run_result(
            arm="candidate",
            realized_trajectory_hash="h1",
            non_solar_forecast_hash="f1",
            resolved_terminal_target_wh=130000.0,
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertEqual(cmp_res.status, "INVALID_PAIR_TERMINAL_TARGET_MISMATCH")
        self.assertIsNone(cmp_res.winner)

    def test_07_paired_comparison_fails_closed_on_solver_failure(self):
        base = _build_test_origin_run_result(
            arm="baseline",
            realized_trajectory_hash="h1",
            non_solar_forecast_hash="f1",
            run_status=OriginRunStatus.FAILED_WORKER_EXIT,
            has_solver_failure=True,
        )
        cand = _build_test_origin_run_result(
            arm="candidate", realized_trajectory_hash="h1", non_solar_forecast_hash="f1"
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertIn("INVALID_PAIR", cmp_res.status)
        self.assertIsNone(cmp_res.winner)

    def test_08_paired_comparison_fails_closed_on_unmet_essential_load(self):
        base = _build_test_origin_run_result(
            arm="baseline", realized_trajectory_hash="h1", non_solar_forecast_hash="f1"
        )
        cand = _build_test_origin_run_result(
            arm="candidate",
            realized_trajectory_hash="h1",
            non_solar_forecast_hash="f1",
            has_unmet_essential=True,
            critical_unmet_load_wh=50.0,
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertIn("INVALID_PAIR", cmp_res.status)
        self.assertIsNone(cmp_res.winner)

    def test_09_paired_comparison_fails_closed_on_fuel_failure(self):
        base = _build_test_origin_run_result(
            arm="baseline",
            realized_trajectory_hash="h1",
            non_solar_forecast_hash="f1",
            has_fuel_failure=True,
            fuel_failure_reason="FUEL_EXHAUSTION_CLAMPED",
            diesel_consumed_liters=None,
        )
        cand = _build_test_origin_run_result(
            arm="candidate", realized_trajectory_hash="h1", non_solar_forecast_hash="f1"
        )
        cmp_res = evaluate_paired_origin_comparison(base, cand)
        self.assertFalse(cmp_res.is_valid_comparison)
        self.assertIn("INVALID_PAIR_FUEL_FAILURE", cmp_res.invalidation_reasons[0])
        self.assertIsNone(cmp_res.winner)

    def test_10_paired_comparison_fails_closed_on_missing_terminal_metrics(self):
        # Every one of the 8 required metrics must be present on both arms.
        metrics = [
            "diesel_consumed_liters",
            "delta_e_term_wh",
            "initial_battery_energy_wh",
            "terminal_battery_energy_wh",
            "initial_battery_soc_pct",
            "terminal_battery_soc_pct",
            "generator_starts",
            "startup_surcharge_liters",
        ]
        for metric in metrics:
            for bad_arm in ["baseline", "candidate"]:
                base_kwargs = {"arm": "baseline", "realized_trajectory_hash": "h1", "non_solar_forecast_hash": "f1"}
                cand_kwargs = {"arm": "candidate", "realized_trajectory_hash": "h1", "non_solar_forecast_hash": "f1"}
                if bad_arm == "baseline":
                    base_kwargs[metric] = None
                else:
                    cand_kwargs[metric] = None

                base = _build_test_origin_run_result(**base_kwargs)
                cand = _build_test_origin_run_result(**cand_kwargs)
                cmp_res = evaluate_paired_origin_comparison(base, cand)
                self.assertFalse(cmp_res.is_valid_comparison)
                self.assertTrue(
                    any(
                        f"INVALID_PAIR_MISSING_TERMINAL_METRIC: {bad_arm}.{metric} is None" in r
                        or "INVALID_PAIR_MISSING_DIESEL_CONSUMED" in r
                        for r in cmp_res.invalidation_reasons
                    )
                )
                self.assertIsNone(cmp_res.net_diesel_savings_liters)
                self.assertIsNone(cmp_res.net_delta_e_term_wh)
                self.assertIsNone(cmp_res.net_generator_starts)
                self.assertIsNone(cmp_res.net_startup_surcharge_liters)
                self.assertIsNone(cmp_res.winner)

    def test_11_paired_comparison_fails_closed_on_malformed_terminal_metrics(self):
        # Tests NaN, Inf, boolean, negative where disallowed, SoC > 100%, non-integer starts
        malformed_cases = [
            ("diesel_consumed_liters", float("nan")),
            ("diesel_consumed_liters", float("inf")),
            ("diesel_consumed_liters", True),
            ("diesel_consumed_liters", -1.0),
            ("delta_e_term_wh", float("nan")),
            ("delta_e_term_wh", float("inf")),
            ("delta_e_term_wh", False),
            ("initial_battery_energy_wh", -10.0),
            ("terminal_battery_energy_wh", -5.0),
            ("initial_battery_soc_pct", 105.0),
            ("terminal_battery_soc_pct", -2.0),
            ("generator_starts", 2.5),
            ("generator_starts", True),
            ("generator_starts", -1),
            ("startup_surcharge_liters", -0.5),
        ]
        for metric, bad_val in malformed_cases:
            base = _build_test_origin_run_result(
                arm="baseline", realized_trajectory_hash="h1", non_solar_forecast_hash="f1"
            )
            cand_kwargs = {
                "arm": "candidate",
                "realized_trajectory_hash": "h1",
                "non_solar_forecast_hash": "f1",
                metric: bad_val,
            }
            cand = _build_test_origin_run_result(**cand_kwargs)
            cmp_res = evaluate_paired_origin_comparison(base, cand)
            self.assertFalse(cmp_res.is_valid_comparison)
            self.assertTrue(any("INVALID_PAIR_MALFORMED_TERMINAL_METRIC" in r for r in cmp_res.invalidation_reasons))
            self.assertIsNone(cmp_res.net_diesel_savings_liters)
            self.assertIsNone(cmp_res.net_delta_e_term_wh)
            self.assertIsNone(cmp_res.net_generator_starts)
            self.assertIsNone(cmp_res.net_startup_surcharge_liters)
            self.assertIsNone(cmp_res.winner)


class TestBlockerLatch1LatchingAndMetricCompleteness(unittest.TestCase):
    """
    Validates [BLOCKER-LATCH-1]: All-step solver status and unmet essential load latching,
    generator starts, startup surcharges, and battery energy tracking.
    """

    def test_01_solver_failure_at_step_0_intermediate_or_terminal_remains_latched(self):
        # Step 0 failure
        res0 = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
            all_step_solver_statuses=("INFEASIBLE",) + ("OPTIMAL",) * 23,
        )
        self.assertTrue(res0.has_solver_failure)
        self.assertEqual(res0.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

        # Intermediate step (step 10) failure
        statuses = ["OPTIMAL"] * 24
        statuses[10] = "TIME_LIMIT"
        res10 = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
            all_step_solver_statuses=tuple(statuses),
        )
        self.assertTrue(res10.has_solver_failure)
        self.assertEqual(res10.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

        # Terminal step (step 23) failure
        statuses_term = ["OPTIMAL"] * 23 + ["INFEASIBLE"]
        res23 = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL"},
            safety_evaluation=None,
            provenance={},
            all_step_solver_statuses=tuple(statuses_term),
        )
        self.assertTrue(res23.has_solver_failure)
        self.assertEqual(res23.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_02_unmet_essential_load_at_any_step_latches_failure(self):
        unmet_seq = [0.0] * 24
        unmet_seq[5] = 12.5  # 12.5 Wh unmet essential at step 5
        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL", "critical_unmet_load_wh": 0.0},
            safety_evaluation=None,
            provenance={},
            all_step_unmet_essential_wh=tuple(unmet_seq),
        )
        self.assertTrue(res.has_unmet_essential)

    def test_03_generator_starts_and_startup_surcharge_calculation(self):
        # 3 generator starts -> 3 * 6.0 L/start = 18.0 L surcharge
        res = record_origin_outcome(
            origin="o1",
            arm="baseline",
            scenario_key="o1",
            forecast_provider="causal_nwp_gamma1",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL", "critical_unmet_load_wh": 0.0, "total_unmet_load_wh": 0.0},
            safety_evaluation=None,
            provenance={},
            generator_starts=3,
            startup_surcharge_liters=18.0,
        )
        self.assertEqual(res.generator_starts, 3)
        self.assertEqual(res.startup_surcharge_liters, 18.0)

    def test_04_initial_terminal_soc_energy_and_signed_delta_e_term(self):
        # Initial: 80% (160 kWh), Terminal: 75% (150 kWh) -> delta E = -10,000 Wh
        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={"constraint_status": "OPTIMAL", "critical_unmet_load_wh": 0.0, "total_unmet_load_wh": 0.0},
            safety_evaluation=None,
            provenance={},
            initial_battery_soc_pct=80.0,
            terminal_battery_soc_pct=75.0,
            initial_battery_energy_wh=160000.0,
            terminal_battery_energy_wh=150000.0,
            delta_e_term_wh=-10000.0,
        )
        self.assertEqual(res.initial_battery_soc_pct, 80.0)
        self.assertEqual(res.terminal_battery_soc_pct, 75.0)
        self.assertEqual(res.initial_battery_energy_wh, 160000.0)
        self.assertEqual(res.terminal_battery_energy_wh, 150000.0)
        self.assertEqual(res.delta_e_term_wh, -10000.0)

    def test_05_campaign_aggregation_aggregates_new_metrics_and_fold_stratification(self):
        r1 = _build_test_origin_run_result(
            origin="o1",
            arm="candidate",
            diesel_consumed_liters=20.0,
            generator_starts=2,
            startup_surcharge_liters=12.0,
            delta_e_term_wh=-2000.0,
            fold_label="fold_A",
        )
        r2 = _build_test_origin_run_result(
            origin="o2",
            arm="candidate",
            diesel_consumed_liters=30.0,
            generator_starts=3,
            startup_surcharge_liters=18.0,
            delta_e_term_wh=+1000.0,
            fold_label="fold_B",
        )
        agg = aggregate_origin_results([r1, r2], arm="candidate")
        self.assertEqual(agg.total_diesel_consumed_liters, 50.0)
        self.assertEqual(agg.mean_diesel_consumed_liters, 25.0)
        self.assertEqual(agg.total_generator_starts, 5)
        self.assertEqual(agg.total_startup_surcharge_liters, 30.0)
        self.assertEqual(agg.net_delta_e_term_wh, -1000.0)
        self.assertEqual(agg.n_solver_failures, 0)
        self.assertEqual(agg.n_unmet_essential_failures, 0)
        self.assertEqual(agg.n_fuel_failures, 0)
        self.assertIn("fold_A", agg.by_fold)
        self.assertIn("fold_B", agg.by_fold)
        self.assertEqual(agg.by_fold["fold_A"]["total_diesel_consumed_liters"], 20.0)
        self.assertEqual(agg.by_fold["fold_B"]["total_diesel_consumed_liters"], 30.0)

    def test_06_solver_status_none_or_empty_latches_failure_in_execute_cell(self):
        # When plan or outcome has constraint_status=None or "", execute_origin_dispatch_cell latches failure
        for bad_status in [None, "", "INFEASIBLE"]:
            scenario = build_origin_scenario_pair(
                origin="o1",
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh=100000.0,
                governed_reserve_policy_name="governed",
            )[1]
            fake_opt = type("FakeOpt", (), {
                "optimize": lambda self, state, forecast, controller_settings: {"constraint_status": bad_status, "diesel_liters": 1.0}
            })()
            fake_sim = type("FakeSim", (), {
                "step": lambda self, state, dispatch_plan: {
                    "dispatch_outcome": {"constraint_status": bad_status, "diesel_consumed_liters": 1.0, "critical_unmet_load_wh": 0.0, "total_unmet_load_wh": 0.0},
                    "state": state,
                }
            })()
            fake_fc = type("FakeFc", (), {
                "predict": lambda self, origin, step, ctx: {"sw_in": 100.0, "origin": origin}
            })()

            res = execute_origin_dispatch_cell(
                origin="o1",
                arm="candidate",
                scenario=scenario,
                expected_steps=2,
                initial_state={"_step": 0},
                forecast_provider=fake_fc,
                optimizer=fake_opt,
                simulator=fake_sim,
                safety_evaluator=None,
                provenance={},
            )
            self.assertTrue(res.has_solver_failure)
            self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_07_record_origin_outcome_missing_or_non_optimal_constraint_status_latches_failure(self):
        # Missing (None), empty (""), or non-OPTIMAL constraint_status in dispatch_outcome latches solver failure
        for bad_status in [None, "", "INFEASIBLE", "TIME_LIMIT"]:
            res = record_origin_outcome(
                origin="o1",
                arm="candidate",
                scenario_key="o1",
                forecast_provider="n6_solar",
                completed_steps=24,
                expected_steps=24,
                dispatch_outcome={"constraint_status": bad_status, "diesel_consumed_liters": 10.0},
                safety_evaluation=None,
                provenance={},
            )
            self.assertTrue(res.has_solver_failure)
            self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_08_section_a_spy_no_simulator_call_on_non_optimal_plan(self):
        # Spy-based test proving that no simulator call occurs for a non-optimal plan
        for bad_status in [None, "", "INFEASIBLE", "TIME_LIMIT"]:
            scenario = build_origin_scenario_pair(
                origin="o1",
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh=100000.0,
                governed_reserve_policy_name="governed",
            )[1]

            mock_optimizer = MagicMock()
            mock_optimizer.optimize.return_value = {
                "constraint_status": bad_status,
                "diesel_power": [100.0] * 24,
            }

            mock_simulator = MagicMock()
            fake_fc = type("FakeFc", (), {
                "predict": lambda self, origin, step, ctx: {"origin": origin}
            })()

            res = execute_origin_dispatch_cell(
                origin="o1",
                arm="candidate",
                scenario=scenario,
                expected_steps=4,
                initial_state={"_step": 0},
                forecast_provider=fake_fc,
                optimizer=mock_optimizer,
                simulator=mock_simulator,
                safety_evaluator=None,
                provenance={},
            )

            # 1. Optimizer was called for step 0
            mock_optimizer.optimize.assert_called_once()
            # 2. Simulator was NEVER called for non-optimal plan
            mock_simulator.step.assert_not_called()
            # 3. Solver failure is latched and loop aborted with 0 completed steps
            self.assertTrue(res.has_solver_failure)
            self.assertEqual(res.completed_steps, 0)
            self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_09_section_a_spy_no_later_optimization_or_simulation_after_failure(self):
        # Spy-based test proving no later optimization or simulation steps occur after failure
        scenario = build_origin_scenario_pair(
            origin="o1",
            baseline_provider="causal_nwp_gamma1",
            candidate_provider="n6_solar",
            controller_settings=_controller_settings(),
            initial_battery_soc_wh=100000.0,
            governed_reserve_policy_name="governed",
        )[1]

        # Call sequence: step 0 returns OPTIMAL; step 1 returns INFEASIBLE
        mock_optimizer = MagicMock()
        mock_optimizer.optimize.side_effect = [
            {"constraint_status": "OPTIMAL", "diesel_power": [0.0] * 24},
            {"constraint_status": "INFEASIBLE", "diesel_power": [0.0] * 24},
            {"constraint_status": "OPTIMAL", "diesel_power": [0.0] * 24},
        ]

        mock_simulator = MagicMock()
        mock_simulator.step.side_effect = [
            {
                "dispatch_outcome": {
                    "constraint_status": "OPTIMAL",
                    "diesel_consumed_liters": 0.0,
                    "critical_unmet_load_wh": 0.0,
                    "total_unmet_load_wh": 0.0,
                },
                "state": {"_step": 1},
                "stop_early": False,
            },
        ]

        fake_fc = type("FakeFc", (), {
            "predict": lambda self, origin, step, ctx: {"origin": origin}
        })()

        res = execute_origin_dispatch_cell(
            origin="o1",
            arm="candidate",
            scenario=scenario,
            expected_steps=4,
            initial_state={"_step": 0},
            forecast_provider=fake_fc,
            optimizer=mock_optimizer,
            simulator=mock_simulator,
            safety_evaluator=None,
            provenance={},
        )

        # Proves step 0 executed both opt & sim
        self.assertEqual(mock_simulator.step.call_count, 1)
        # Proves step 1 executed opt, discovered non-OPTIMAL, aborted immediately without calling simulator
        self.assertEqual(mock_optimizer.optimize.call_count, 2)
        # Proves steps 2 and 3 NEVER ran (neither optimizer nor simulator called)
        self.assertEqual(res.completed_steps, 1)
        self.assertTrue(res.has_solver_failure)
        self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)

    def test_10_invalid_critical_unmet_load_measurements_never_coerced_to_zero(self):
        # Treating missing, Boolean, non-numeric, non-finite, or negative critical_unmet_load_wh as invalid measurement
        invalid_values = [True, False, "invalid_str", float("nan"), float("inf"), -5.0]
        for bad_val in invalid_values:
            scenario = build_origin_scenario_pair(
                origin="o1",
                baseline_provider="causal_nwp_gamma1",
                candidate_provider="n6_solar",
                controller_settings=_controller_settings(),
                initial_battery_soc_wh=100000.0,
                governed_reserve_policy_name="governed",
            )[1]

            mock_optimizer = MagicMock()
            mock_optimizer.optimize.return_value = {
                "constraint_status": "OPTIMAL",
                "diesel_power": [0.0] * 24,
            }

            mock_simulator = MagicMock()
            mock_simulator.step.return_value = {
                "dispatch_outcome": {
                    "constraint_status": "OPTIMAL",
                    "diesel_consumed_liters": 0.0,
                    "critical_unmet_load_wh": bad_val,
                    "total_unmet_load_wh": 0.0,
                },
                "state": {"_step": 1},
                "stop_early": False,
            }

            fake_fc = type("FakeFc", (), {
                "predict": lambda self, origin, step, ctx: {"origin": origin}
            })()

            res = execute_origin_dispatch_cell(
                origin="o1",
                arm="candidate",
                scenario=scenario,
                expected_steps=1,
                initial_state={"_step": 0},
                forecast_provider=fake_fc,
                optimizer=mock_optimizer,
                simulator=mock_simulator,
                safety_evaluator=None,
                provenance={},
            )

            # Invalid measurements must latch essential failure and never be replaced with 0.0
            self.assertTrue(res.has_unmet_essential, f"Expected has_unmet_essential for bad_val={bad_val}")
            self.assertIsNone(res.critical_unmet_load_wh, f"Expected critical_unmet_load_wh is None for bad_val={bad_val}")

    def test_11_aggregate_origin_results_quarantines_all_failed_and_incomplete_runs(self):
        # Add tests proving failed and incomplete runs cannot affect decision-grade diesel, generator-start, surcharge, or terminal-energy aggregates
        clean_eligible = _build_test_origin_run_result(
            origin="clean_1",
            arm="candidate",
            run_status=OriginRunStatus.OPTIMAL,
            completed_steps=24,
            expected_steps=24,
            diesel_consumed_liters=25.0,
            generator_starts=2,
            startup_surcharge_liters=12.0,
            delta_e_term_wh=-1500.0,
            critical_unmet_load_wh=0.0,
            total_unmet_load_wh=0.0,
            has_solver_failure=False,
            has_unmet_essential=False,
            has_fuel_failure=False,
            diesel_fuel_tracking_gap=False,
        )

        incomplete_run = _build_test_origin_run_result(
            origin="incomplete_2",
            arm="candidate",
            run_status=OriginRunStatus.INCOMPLETE_RUN,
            completed_steps=20,
            expected_steps=24,
            diesel_consumed_liters=100.0,
            generator_starts=10,
            startup_surcharge_liters=60.0,
            delta_e_term_wh=5000.0,
            critical_unmet_load_wh=0.0,
        )

        solver_failed_run = _build_test_origin_run_result(
            origin="solver_fail_3",
            arm="candidate",
            run_status=OriginRunStatus.FAILED_WORKER_EXIT,
            completed_steps=24,
            expected_steps=24,
            has_solver_failure=True,
            diesel_consumed_liters=200.0,
            generator_starts=20,
            startup_surcharge_liters=120.0,
            delta_e_term_wh=8000.0,
        )

        essential_failed_run = _build_test_origin_run_result(
            origin="essential_fail_4",
            arm="candidate",
            run_status=OriginRunStatus.OPTIMAL,
            completed_steps=24,
            expected_steps=24,
            has_unmet_essential=True,
            critical_unmet_load_wh=500.0,
            diesel_consumed_liters=300.0,
            generator_starts=30,
            startup_surcharge_liters=180.0,
            delta_e_term_wh=9000.0,
        )

        fuel_failed_run = _build_test_origin_run_result(
            origin="fuel_fail_5",
            arm="candidate",
            run_status=OriginRunStatus.FAILED_WORKER_EXIT,
            completed_steps=24,
            expected_steps=24,
            has_fuel_failure=True,
            diesel_consumed_liters=None,
            generator_starts=40,
            startup_surcharge_liters=240.0,
            delta_e_term_wh=10000.0,
        )

        tracking_gap_run = _build_test_origin_run_result(
            origin="tracking_gap_6",
            arm="candidate",
            run_status=OriginRunStatus.FAILED_WORKER_EXIT,
            completed_steps=24,
            expected_steps=24,
            diesel_fuel_tracking_gap=True,
            diesel_consumed_liters=None,
            generator_starts=50,
            startup_surcharge_liters=300.0,
            delta_e_term_wh=12000.0,
        )

        all_runs = [
            clean_eligible,
            incomplete_run,
            solver_failed_run,
            essential_failed_run,
            fuel_failed_run,
            tracking_gap_run,
        ]

        agg = aggregate_origin_results(all_runs, arm="candidate")

        # 1. Total attempted origins vs eligible runs clearly distinguished
        self.assertEqual(agg.n_origins, 6, "Must report all 6 attempted origins")
        self.assertEqual(agg.n_eligible_origins, 1, "Must report exactly 1 eligible origin")

        # 2. Operational metrics computed STRICTLY from eligible run (completely isolated from runs 2-6)
        self.assertEqual(agg.total_diesel_consumed_liters, 25.0)
        self.assertEqual(agg.mean_diesel_consumed_liters, 25.0)
        self.assertEqual(agg.total_generator_starts, 2)
        self.assertEqual(agg.total_startup_surcharge_liters, 12.0)
        self.assertEqual(agg.net_delta_e_term_wh, -1500.0)
        self.assertEqual(agg.total_critical_unmet_load_wh, 0.0)

        # 3. Failure counts tracked across all attempted origins
        self.assertEqual(agg.n_solver_failures, 1)
        self.assertEqual(agg.n_unmet_essential_failures, 1)
        self.assertEqual(agg.n_fuel_failures, 2)  # 1 fuel failure + 1 tracking gap

    def test_12_missing_or_malformed_critical_unmet_load_quarantines_completed_run(self):
        # Missing or malformed critical_unmet_load_wh on completed run must latch failure,
        # set run_status=FAILED_WORKER_EXIT, and quarantine decision-grade terminal metrics to None
        for bad_crit in [None, True, False, "invalid_str", float("nan"), float("inf"), -1.0]:
            outcome = {
                "constraint_status": "OPTIMAL",
                "diesel_consumed_liters": 25.0,
                "generator_starts": 2,
                "startup_surcharge_liters": 12.0,
                "terminal_battery_soc_pct": 75.0,
                "terminal_battery_energy_wh": 150000.0,
                "delta_e_term_wh": -5000.0,
                "total_unmet_load_wh": 0.0,
            }
            if bad_crit is not None:
                outcome["critical_unmet_load_wh"] = bad_crit

            res = record_origin_outcome(
                origin="o1",
                arm="candidate",
                scenario_key="o1",
                forecast_provider="n6_solar",
                completed_steps=24,
                expected_steps=24,
                dispatch_outcome=outcome,
                safety_evaluation=None,
                provenance={},
            )

            self.assertTrue(res.has_unmet_essential, f"Expected has_unmet_essential=True for bad_crit={bad_crit}")
            self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)
            self.assertIsNone(res.critical_unmet_load_wh)
            self.assertIsNone(res.diesel_consumed_liters)
            self.assertIsNone(res.generator_starts)
            self.assertIsNone(res.startup_surcharge_liters)
            self.assertIsNone(res.terminal_battery_soc_pct)
            self.assertIsNone(res.terminal_battery_energy_wh)
            self.assertIsNone(res.delta_e_term_wh)

    def test_13_invalid_total_unmet_load_quarantines_run(self):
        # Invalid total_unmet_load_wh must set total_unmet_load_wh=None, latch failure,
        # set run_status=FAILED_WORKER_EXIT, and null out decision-grade metrics
        for bad_total in [True, False, "invalid_str", float("nan"), float("inf"), -10.0]:
            outcome = {
                "constraint_status": "OPTIMAL",
                "diesel_consumed_liters": 25.0,
                "generator_starts": 2,
                "startup_surcharge_liters": 12.0,
                "terminal_battery_soc_pct": 75.0,
                "delta_e_term_wh": -5000.0,
                "critical_unmet_load_wh": 0.0,
                "total_unmet_load_wh": bad_total,
            }

            res = record_origin_outcome(
                origin="o1",
                arm="candidate",
                scenario_key="o1",
                forecast_provider="n6_solar",
                completed_steps=24,
                expected_steps=24,
                dispatch_outcome=outcome,
                safety_evaluation=None,
                provenance={},
            )

            self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)
            self.assertIsNone(res.total_unmet_load_wh)
            self.assertIsNone(res.diesel_consumed_liters)
            self.assertIsNone(res.generator_starts)
            self.assertIsNone(res.startup_surcharge_liters)
            self.assertIsNone(res.terminal_battery_soc_pct)
            self.assertIsNone(res.delta_e_term_wh)

    def test_14_has_unmet_essential_latched_quarantines_run_and_nulls_metrics(self):
        # A run with latched has_unmet_essential=True must not preserve decision-grade metrics
        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={
                "constraint_status": "OPTIMAL",
                "diesel_consumed_liters": 25.0,
                "generator_starts": 2,
                "startup_surcharge_liters": 12.0,
                "critical_unmet_load_wh": 50.0,
                "total_unmet_load_wh": 50.0,
            },
            safety_evaluation=None,
            provenance={},
            has_unmet_essential=True,
        )

        self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)
        self.assertIsNone(res.diesel_consumed_liters)
        self.assertIsNone(res.generator_starts)
        self.assertIsNone(res.startup_surcharge_liters)
        self.assertIsNone(res.terminal_battery_soc_pct)
        self.assertIsNone(res.delta_e_term_wh)

    def test_15_safety_passed_false_quarantines_run_and_nulls_metrics(self):
        # A run with safety_passed=False must force FAILED_WORKER_EXIT and quarantine all metrics to None
        safety_fail = SafetyEvaluationResult(
            passed=False,
            hard_soc_violation=True,
            reserve_shortfall_total_wh=500.0,
            reserve_violation=False,
            critical_unmet_total_wh=0.0,
            solver_infeasible=False,
            failure_reasons=["HARD_SOC_VIOLATION"],
        )

        res = record_origin_outcome(
            origin="o1",
            arm="candidate",
            scenario_key="o1",
            forecast_provider="n6_solar",
            completed_steps=24,
            expected_steps=24,
            dispatch_outcome={
                "constraint_status": "OPTIMAL",
                "diesel_consumed_liters": 25.0,
                "generator_starts": 2,
                "startup_surcharge_liters": 12.0,
                "terminal_battery_soc_pct": 75.0,
                "delta_e_term_wh": -5000.0,
                "critical_unmet_load_wh": 0.0,
                "total_unmet_load_wh": 0.0,
            },
            safety_evaluation=safety_fail,
            provenance={},
        )

        self.assertFalse(res.safety_passed)
        self.assertEqual(res.run_status, OriginRunStatus.FAILED_WORKER_EXIT)
        self.assertIsNone(res.diesel_consumed_liters)
        self.assertIsNone(res.generator_starts)
        self.assertIsNone(res.startup_surcharge_liters)
        self.assertIsNone(res.terminal_battery_soc_pct)
        self.assertIsNone(res.delta_e_term_wh)


if __name__ == "__main__":
    unittest.main()


