"""
POLARIS — Factor-Isolated Replay Harness (Configuration & Validation Only)
=============================================================================
N6 Operational Readiness Remediation, Section 6.

GOVERNANCE STATUS: NON-PRODUCTION / NOT EXECUTED
- This module builds the MINIMUM reusable structure needed for a future
  fair, paired evaluation of frozen N6 against the authorized established
  forecast baseline. It intentionally does NOT run any dispatch, call
  GAP19, call N6 inference, or execute a historical campaign.
- `FactorIsolatedReplayHarness.execute_experiment_a()` and
  `.execute_experiment_b()` both raise `CampaignExecutionNotAuthorizedError`
  unconditionally -- there is currently no authorization path that allows
  this remediation pass to run a campaign. This is deliberate: the
  protocol this module implements explicitly says "Do not execute either
  experiment now."
- Experiment B (reserve-policy comparison) additionally requires a
  constructor-level authorization token for even its CONFIGURATION to be
  accepted, because Section 6 states "the second experiment must not be
  enabled until the candidate reserve policy and safety thresholds have
  explicit authorization." No valid token exists anywhere in this
  repository or remediation pass; `ExperimentBConfig` will always raise
  `AuthorizationRequiredError` unless a caller explicitly fabricates one,
  which no production or test code in this remediation does.

WHAT THIS MODULE DOES BUILD (validate-only, safe to exercise with tests):
- `MatchedControllerSettings`: a frozen bundle of controller-identity
  fields (battery params, diesel/fuel curves, GAP19 solver settings,
  objective priorities, termination criteria, demand-criticality config,
  scenario inclusion rules) that both arms of a comparison must share
  bit-for-bit.
- `ScenarioSpec`: one matched scenario (key, forecast origin, initial SOC,
  controller settings, and the set of decision-time-only valid times).
- `validate_matched_scenario_pair`: asserts two scenarios used for a
  forecast-value comparison are identical in every dimension EXCEPT the
  forecast provider itself.
- Oracle-provider rejection, delegated to `forecast_lineage.reject_if_oracle`.
- `ExperimentAConfig` / `ExperimentBConfig`: the two independently
  configured comparisons required by Section 6, with Experiment B gated
  behind an authorization token that is never actually supplied.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional

from system.evaluation.forecast_lineage import reject_if_oracle

__all__ = [
    "CampaignExecutionNotAuthorizedError",
    "ScenarioMismatchError",
    "AuthorizationRequiredError",
    "SecurityIntegrityViolationError",
    "DiagnosticExecutionAuthorization",
    "EXECUTION_STAGE_BLOCKED_AWAITING_POST_TEST_SIGN_OFF",
    "EXECUTION_STAGE_AUTHORIZED_BY_OWNER",
    "IMPLEMENTATION_STAGE_AUTHORIZED",
    "APPROVED_CLASSIFICATION",
    "APPROVED_PROTOCOL",
    "APPROVED_ORIGINS",
    "REGISTERED_PROTECTED_FILE_HASHES",
    "validate_diagnostic_execution_authorization",
    "MatchedControllerSettings",
    "ScenarioSpec",
    "validate_matched_scenario_pair",
    "validate_matched_scenario_set",
    "ExperimentAConfig",
    "ExperimentBConfig",
    "FactorIsolatedReplayHarness",
]

import hashlib
from pathlib import Path


class SecurityIntegrityViolationError(Exception):
    """Raised when protected file hashes or security boundaries are violated."""


# Two-stage authorization lifecycle constants (Section 40 governance)
EXECUTION_STAGE_BLOCKED_AWAITING_POST_TEST_SIGN_OFF = "BLOCKED_AWAITING_POST_TEST_SIGN_OFF"
EXECUTION_STAGE_AUTHORIZED_BY_OWNER = "EXECUTION_AUTHORIZED_BY_OWNER"
IMPLEMENTATION_STAGE_AUTHORIZED = "INSTRUMENTATION_AUTHORIZED"

# Registered diagnostic configuration boundaries
APPROVED_CLASSIFICATION = "OFFLINE_ENGINEERING_DIAGNOSTIC_IN_SAMPLE_CONTAMINATED"
APPROVED_PROTOCOL = "OPTION_A_INDEPENDENT_24H_DAILY_RUNS"
APPROVED_ORIGINS: Tuple[str, ...] = (
    "2024-06-01",
    "2024-06-02",
    "2024-06-03",
    "2024-06-04",
    "2024-06-05",
    "2024-06-06",
    "2024-06-07",
)
APPROVED_INITIAL_SOC_PCT = 80.0
APPROVED_INITIAL_ENERGY_WH = 160000.0
APPROVED_INITIAL_FUEL_L = 100.0
APPROVED_INITIAL_GEN_RUNNING = False

# Bit-for-bit registered SHA-256 hashes of all 7 PROTECTED_FILES (Decision Register v1.9.13)
REGISTERED_PROTECTED_FILE_HASHES: Dict[str, str] = {
    "system/control/router.py": "b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3",
    "system/control/ecd.py": "091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db",
    "system/optimization/implementations/option_d.py": "688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3",
    "system/optimization/implementations/gap19_highs_native.py": "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
    "system/simulation/simulator.py": "8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f",
    "system/runtime/runner.py": "6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10",
    "system/orchestration/manifest.py": "7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35",
}


@dataclass(frozen=True)
class DiagnosticExecutionAuthorization:
    """
    Immutable authorization context for the offline engineering diagnostic.
    Enforces strict binding to registered protocol, exact origins, initial
    conditions, classification, winner: null, and protected-file hashes.
    """

    execution_stage_status: str
    classification: str
    protocol: str
    origins: Tuple[str, ...]
    initial_soc_pct: float
    initial_battery_energy_wh: float
    initial_fuel_liters: float
    initial_generator_running: bool
    winner_declared: Optional[str]
    protected_file_hashes: Dict[str, str]


def validate_diagnostic_execution_authorization(
    auth: DiagnosticExecutionAuthorization,
    repo_root: Optional[Path] = None,
) -> None:
    """
    Validates execution authorization against registered boundaries and live file hashes.
    Fails closed if any parameter deviates or if execution status is not owner-authorized.
    """
    if auth.execution_stage_status != EXECUTION_STAGE_AUTHORIZED_BY_OWNER:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: execution_stage_status is '{auth.execution_stage_status}'. "
            f"Expected '{EXECUTION_STAGE_AUTHORIZED_BY_OWNER}'. "
            "Implementation is authorized, but execution remains strictly blocked pending separate owner approval."
        )
    if auth.classification != APPROVED_CLASSIFICATION:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: classification '{auth.classification}' does not match "
            f"approved '{APPROVED_CLASSIFICATION}'."
        )
    if auth.protocol != APPROVED_PROTOCOL:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: protocol '{auth.protocol}' does not match approved '{APPROVED_PROTOCOL}'."
        )
    if tuple(auth.origins) != APPROVED_ORIGINS:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: origins {auth.origins} do not match approved {APPROVED_ORIGINS}."
        )
    if auth.initial_soc_pct != APPROVED_INITIAL_SOC_PCT:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: initial SOC {auth.initial_soc_pct} != {APPROVED_INITIAL_SOC_PCT}%."
        )
    if auth.initial_battery_energy_wh != APPROVED_INITIAL_ENERGY_WH:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: initial energy {auth.initial_battery_energy_wh} != {APPROVED_INITIAL_ENERGY_WH} Wh."
        )
    if auth.initial_fuel_liters != APPROVED_INITIAL_FUEL_L:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: initial fuel {auth.initial_fuel_liters} != {APPROVED_INITIAL_FUEL_L} L."
        )
    if auth.initial_generator_running != APPROVED_INITIAL_GEN_RUNNING:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: initial generator running {auth.initial_generator_running} != {APPROVED_INITIAL_GEN_RUNNING}."
        )
    if auth.winner_declared is not None:
        raise CampaignExecutionNotAuthorizedError(
            f"Campaign execution is DENIED: winner_declared must be None, got '{auth.winner_declared}'."
        )

    # Validate protected file hashes against registered baselines
    for rel_path, expected_hash in REGISTERED_PROTECTED_FILE_HASHES.items():
        if auth.protected_file_hashes.get(rel_path) != expected_hash:
            raise SecurityIntegrityViolationError(
                f"Security violation: protected file '{rel_path}' hash in authorization "
                f"('{auth.protected_file_hashes.get(rel_path)}') does not match registered baseline ('{expected_hash}')."
            )

    # Verify live on-disk file hashes if repo_root is available
    if repo_root is not None:
        for rel_path, expected_hash in REGISTERED_PROTECTED_FILE_HASHES.items():
            file_path = repo_root / rel_path
            if not file_path.exists():
                raise SecurityIntegrityViolationError(f"Security violation: protected file '{rel_path}' not found on disk.")
            live_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if live_hash != expected_hash:
                raise SecurityIntegrityViolationError(
                    f"Security violation: live protected file '{rel_path}' hash ('{live_hash}') "
                    f"does not match registered baseline ('{expected_hash}')."
                )


class CampaignExecutionNotAuthorizedError(Exception):
    """Raised unconditionally by execute_experiment_a/b -- campaign execution is out of scope here."""


class ScenarioMismatchError(Exception):
    """Raised when two scenarios intended for a factor-isolated comparison are not actually matched."""


class AuthorizationRequiredError(Exception):
    """Raised when Experiment B (candidate reserve policy) is configured without explicit authorization."""


@dataclass(frozen=True)
class MatchedControllerSettings:
    """
    Every field here must be IDENTICAL across the two arms of a single
    factor-isolated comparison. Equality is structural (dataclass __eq__),
    so any drift -- including an accidental change to solver tolerances or
    objective priorities between "the baseline run" and "the candidate
    run" -- is caught by `validate_matched_scenario_pair`.
    """

    battery_params: Dict[str, float]
    diesel_generator_constraints: Dict[str, float]
    fuel_curve_params: Dict[str, float]
    gap19_solver_settings: Dict[str, Any]
    objective_priorities: Dict[str, int]
    termination_criteria: Dict[str, Any]
    demand_criticality_config: Dict[str, Any]
    scenario_inclusion_rules: Dict[str, Any]


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_key: str
    forecast_origin: str
    initial_battery_soc_wh: float
    controller_settings: MatchedControllerSettings
    forecast_provider: str
    reserve_policy_name: str
    decision_time_valid_times: List[str] = field(default_factory=list)

    def __post_init__(self):
        reject_if_oracle(self.forecast_provider, context=f"scenario={self.scenario_key} (dispatch)")


def validate_matched_scenario_pair(baseline: ScenarioSpec, candidate: ScenarioSpec) -> None:
    """
    Validates that `baseline` and `candidate` differ ONLY in forecast
    provider (Experiment A) or ONLY in reserve policy (Experiment B) --
    never both, and never in scenario key, origin, initial state, or any
    controller setting. Fails closed with `ScenarioMismatchError`
    otherwise.
    """
    if baseline.scenario_key != candidate.scenario_key:
        raise ScenarioMismatchError(
            f"Fail-closed: scenario_key mismatch: '{baseline.scenario_key}' vs '{candidate.scenario_key}'"
        )
    if baseline.forecast_origin != candidate.forecast_origin:
        raise ScenarioMismatchError(
            f"Fail-closed: forecast_origin mismatch for scenario '{baseline.scenario_key}': "
            f"'{baseline.forecast_origin}' vs '{candidate.forecast_origin}'"
        )
    if abs(baseline.initial_battery_soc_wh - candidate.initial_battery_soc_wh) > 1e-6:
        raise ScenarioMismatchError(
            f"Fail-closed: initial_battery_soc_wh mismatch for scenario '{baseline.scenario_key}': "
            f"{baseline.initial_battery_soc_wh} vs {candidate.initial_battery_soc_wh}"
        )
    if baseline.controller_settings != candidate.controller_settings:
        raise ScenarioMismatchError(
            f"Fail-closed: controller_settings differ for scenario '{baseline.scenario_key}'. "
            f"Factor isolation requires every controller setting to be identical except the "
            f"single factor under test (forecast provider for Experiment A, reserve policy for "
            f"Experiment B)."
        )

    provider_differs = baseline.forecast_provider != candidate.forecast_provider
    reserve_policy_differs = baseline.reserve_policy_name != candidate.reserve_policy_name
    if provider_differs and reserve_policy_differs:
        raise ScenarioMismatchError(
            f"Fail-closed: scenario '{baseline.scenario_key}' varies BOTH forecast provider AND "
            f"reserve policy simultaneously -- this is not a factor-isolated comparison."
        )
    if not provider_differs and not reserve_policy_differs:
        raise ScenarioMismatchError(
            f"Fail-closed: scenario '{baseline.scenario_key}' varies NEITHER forecast provider NOR "
            f"reserve policy -- baseline and candidate are identical, nothing is being compared."
        )


def validate_matched_scenario_set(baseline_scenarios: List[ScenarioSpec], candidate_scenarios: List[ScenarioSpec]) -> None:
    """Validates an entire matched-pair list: same scenario keys (as a set) and pairwise isolation."""
    baseline_keys = {s.scenario_key for s in baseline_scenarios}
    candidate_keys = {s.scenario_key for s in candidate_scenarios}
    if baseline_keys != candidate_keys:
        raise ScenarioMismatchError(
            f"Fail-closed: scenario key sets differ. Only in baseline: "
            f"{baseline_keys - candidate_keys}; only in candidate: {candidate_keys - baseline_keys}"
        )
    by_key_candidate = {s.scenario_key: s for s in candidate_scenarios}
    for b in baseline_scenarios:
        validate_matched_scenario_pair(b, by_key_candidate[b.scenario_key])


@dataclass
class ExperimentAConfig:
    """
    Experiment A -- Isolate forecast value: compare the authorized
    established forecast baseline against frozen N6 while holding the
    governed reserve policy and all other controller settings constant.
    """

    baseline_scenarios: List[ScenarioSpec]
    candidate_scenarios: List[ScenarioSpec]
    governed_reserve_policy_name: str

    def __post_init__(self):
        for s in self.baseline_scenarios + self.candidate_scenarios:
            if s.reserve_policy_name != self.governed_reserve_policy_name:
                raise ScenarioMismatchError(
                    f"Fail-closed: Experiment A requires the governed reserve policy "
                    f"('{self.governed_reserve_policy_name}') held constant across ALL scenarios; "
                    f"scenario '{s.scenario_key}' uses '{s.reserve_policy_name}' instead."
                )
        validate_matched_scenario_set(self.baseline_scenarios, self.candidate_scenarios)


@dataclass
class ExperimentBConfig:
    """
    Experiment B -- Isolate reserve-policy value: with forecast held fixed
    at N6, compare the existing governed reserve policy against a
    separately authorized candidate reserve policy.

    Per Section 6, this must NOT be enabled until the candidate reserve
    policy and safety thresholds have explicit authorization. This
    constructor therefore REQUIRES `authorization_token` to equal the
    module-level `_EXPERIMENT_B_AUTHORIZATION_TOKEN` sentinel, which is
    intentionally never set to a real value anywhere in this repository.
    """

    fixed_forecast_provider: str
    baseline_reserve_scenarios: List[ScenarioSpec]
    candidate_reserve_scenarios: List[ScenarioSpec]
    authorization_token: Optional[str] = None

    def __post_init__(self):
        if self.authorization_token != _EXPERIMENT_B_AUTHORIZATION_TOKEN:
            raise AuthorizationRequiredError(
                "Fail-closed: Experiment B (candidate reserve-policy comparison) requires explicit, "
                "separately granted authorization that does not exist in this remediation pass. "
                "AUTHORIZATION REQUIRED before this configuration may be constructed."
            )
        for s in self.baseline_reserve_scenarios + self.candidate_reserve_scenarios:
            if s.forecast_provider != self.fixed_forecast_provider:
                raise ScenarioMismatchError(
                    f"Fail-closed: Experiment B requires the forecast provider "
                    f"('{self.fixed_forecast_provider}') held fixed across ALL scenarios; "
                    f"scenario '{s.scenario_key}' uses '{s.forecast_provider}' instead."
                )
        validate_matched_scenario_set(self.baseline_reserve_scenarios, self.candidate_reserve_scenarios)


# Deliberately never set to any real/guessable value by this remediation. Its
# only purpose is to make the fail-closed gate in ExperimentBConfig testable
# (a test may construct this exact sentinel object to prove the gate logic
# and its own negative cases work), while guaranteeing no ordinary caller --
# including any other module in this repository -- can satisfy it by accident.
_EXPERIMENT_B_AUTHORIZATION_TOKEN = object()


class FactorIsolatedReplayHarness:
    """
    Minimum reusable structure for a future fair, paired evaluation.
    `validate_experiment_a_config` / `validate_experiment_b_config` perform
    ALL configuration/matching/oracle-rejection checks without running any
    dispatch. `execute_experiment_a` / `execute_experiment_b` are present
    only to make unambiguous, in code, that no campaign execution is
    authorized by this remediation pass.
    """

    def __init__(
        self,
        execution_stage_status: str = EXECUTION_STAGE_BLOCKED_AWAITING_POST_TEST_SIGN_OFF,
        repo_root: Optional[Path] = None,
    ):
        self._validated_a: Optional[ExperimentAConfig] = None
        self.execution_stage_status = execution_stage_status
        self.repo_root = repo_root

    def validate_experiment_a_config(self, config: ExperimentAConfig) -> ExperimentAConfig:
        """Re-validates an already-constructed config (construction itself already validates)."""
        validate_matched_scenario_set(config.baseline_scenarios, config.candidate_scenarios)
        self._validated_a = config
        return config

    def execute_experiment_a(
        self,
        config: ExperimentAConfig,
        auth: Optional[DiagnosticExecutionAuthorization] = None,
    ) -> None:
        if self.execution_stage_status != EXECUTION_STAGE_AUTHORIZED_BY_OWNER:
            raise CampaignExecutionNotAuthorizedError(
                f"Fail-closed: execution is DENIED: execution_stage_status is '{self.execution_stage_status}'. "
                f"Expected '{EXECUTION_STAGE_AUTHORIZED_BY_OWNER}'. "
                "Phase 2 authorizes instrumentation and unit tests only. Execution remains hard-blocked "
                "awaiting explicit post-test owner sign-off."
            )
        if auth is None:
            raise CampaignExecutionNotAuthorizedError(
                "Fail-closed: execution is DENIED: missing DiagnosticExecutionAuthorization context."
            )
        validate_diagnostic_execution_authorization(auth, repo_root=self.repo_root)
        raise CampaignExecutionNotAuthorizedError(
            "Fail-closed: diagnostic campaign execution dispatch runner is NOT enabled in Phase 2. "
            "Execution against real June 1–7 data remains hard-blocked."
        )

    def execute_experiment_b(self, config: ExperimentBConfig) -> None:
        raise CampaignExecutionNotAuthorizedError(
            "Fail-closed: Experiment B execution is unconditionally disabled. Even its configuration "
            "requires authorization that does not exist in this repository; execution requires a "
            "further, separate authorization beyond that."
        )
