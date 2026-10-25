"""
POLARIS — Forecast Lineage / Oracle-Provider Inspection Utility
==================================================================
N6 Operational Readiness Remediation, Section 5 & 6.

GOVERNANCE STATUS: READ-ONLY INSPECTION / NON-PRODUCTION
- Does not alter any historical experiment result, config, or runner script.
- Does not rerun, reproduce, or reinterpret the sealed 2025 blind evaluation.
- Provides a reusable, generic utility to classify a named forecast provider
  as causal or an oracle/leakage provider, and to construct a structured
  lineage record distinguishing: the forecast provider CONFIGURED, the
  model artifact ACTUALLY loaded, the forecast ACTUALLY consumed by
  dispatch, the forecast used for reserve/EBR calculation, and any
  detected future-information/target leakage.
- Reused by `system/evaluation/replay_harness.py` (Section 6) to reject
  known oracle providers from ever being used as a decision-time forecast
  in a future factor-isolated evaluation.

VERIFIED LINEAGE (recorded here as documentation of independently-verified
findings from reading `experiments/exp_three_arm_2024/scripts/run_three_arm_2024.py`
during this remediation; this module does not re-derive these at import time
-- it only encodes the oracle-provider blocklist and a reusable classifier):
  - Arm A / Arm A_FIX: configured provider "causal_nwp_gamma1" ->
    `CausalNwpPhysicsForecastEngine`. Causal. A_FIX differs only by a
    `LabelCorrectedLocation` geometry wrapper; neither uses Stage 8.1 or N6.
  - Arm B: configured provider "realized_sw_in" -> reads measured/realized
    SITES SW_IN for the full future 24h horizon into both the dispatch
    bundle and the EBR reserve calculation. CONFIRMED ORACLE / LEAKAGE.
    The code itself tags this "NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY".
  - Arm C: configured provider "calibrated_gamma_hat_point" (dispatch) /
    "calibrated_lower_bound" (reserve), via `calibrate_arm_c.py`. Causal
    (derived from the causal clear-sky/cloud physics engine), but not
    Stage 8.1 or N6 either.
  - No arm in this experiment uses Stage 8.1 or Candidate N6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = [
    "ORACLE_PROVIDER_NAMES",
    "CAUSAL_PROVIDER_NAMES",
    "LineageRecord",
    "is_oracle_provider",
    "build_lineage_record",
    "OracleProviderRejectedError",
]


class OracleProviderRejectedError(Exception):
    """Raised when a known oracle/leakage provider is used as a decision-time forecast."""


# Forecast-provider identifiers known, from direct source-code verification in
# this repository, to leak future-realized/target information into a
# decision-time forecast. Any provider name in this set must never be used
# as a forecast input for an operational-performance claim.
ORACLE_PROVIDER_NAMES = frozenset(
    {
        "realized_sw_in",
        "actual_sw_in",
        "actual_SW_IN",
        "actual_ghi",
        "realized_generation",
        "residual_target",
        "target",
    }
)

# Forecast-provider identifiers confirmed causal (decision-time-only inputs)
# by direct source-code verification during this remediation.
CAUSAL_PROVIDER_NAMES = frozenset(
    {
        "causal_nwp_gamma1",
        "calibrated_gamma_hat_point",
        "calibrated_lower_bound",
        "n6_solar",
        "stage81_corrected",
    }
)


@dataclass(frozen=True)
class LineageRecord:
    arm_or_scenario_name: str
    provider_configured: str
    model_artifact_loaded: Optional[str]
    forecast_consumed_by_dispatch: Optional[str]
    forecast_used_for_reserve: Optional[str]
    leakage_detected: bool
    leakage_reason: Optional[str]
    lineage_status: str  # "VERIFIED_CAUSAL" | "CONFIRMED_ORACLE" | "UNKNOWN_UNVERIFIED"


def is_oracle_provider(provider_name: str) -> bool:
    return provider_name in ORACLE_PROVIDER_NAMES


def build_lineage_record(
    arm_or_scenario_name: str,
    provider_configured: str,
    model_artifact_loaded: Optional[str] = None,
    forecast_consumed_by_dispatch: Optional[str] = None,
    forecast_used_for_reserve: Optional[str] = None,
) -> LineageRecord:
    """
    Builds a structured lineage record for one arm/scenario. Does NOT trust
    the `provider_configured` label blindly for the oracle classification --
    it classifies strictly from the `ORACLE_PROVIDER_NAMES` /
    `CAUSAL_PROVIDER_NAMES` registries built from direct code verification.
    A provider absent from both sets is marked `UNKNOWN_UNVERIFIED` rather
    than assumed safe.
    """
    if provider_configured in ORACLE_PROVIDER_NAMES:
        leakage_detected = True
        leakage_reason = (
            f"Provider '{provider_configured}' is a known oracle/leakage provider "
            f"(reads future-realized data at decision time)."
        )
        status = "CONFIRMED_ORACLE"
    elif provider_configured in CAUSAL_PROVIDER_NAMES:
        leakage_detected = False
        leakage_reason = None
        status = "VERIFIED_CAUSAL"
    else:
        leakage_detected = False
        leakage_reason = None
        status = "UNKNOWN_UNVERIFIED"

    return LineageRecord(
        arm_or_scenario_name=arm_or_scenario_name,
        provider_configured=provider_configured,
        model_artifact_loaded=model_artifact_loaded,
        forecast_consumed_by_dispatch=forecast_consumed_by_dispatch,
        forecast_used_for_reserve=forecast_used_for_reserve,
        leakage_detected=leakage_detected,
        leakage_reason=leakage_reason,
        lineage_status=status,
    )


def reject_if_oracle(provider_name: str, context: str = "") -> None:
    """
    Fail-closed guard: raises `OracleProviderRejectedError` if `provider_name`
    is a known oracle/leakage provider. Intended for use at the point where a
    forecast provider is about to be wired into a decision-time dispatch or
    reserve calculation (see `replay_harness.py`).
    """
    if is_oracle_provider(provider_name):
        raise OracleProviderRejectedError(
            f"Fail-closed: '{provider_name}' is a known oracle/leakage forecast provider and "
            f"cannot be used as a decision-time forecast{(' (' + context + ')') if context else ''}."
        )
