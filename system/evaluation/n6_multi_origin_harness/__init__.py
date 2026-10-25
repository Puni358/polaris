"""
POLARIS -- N6 Multi-Origin Campaign Harness package.

See `harness.py`'s module docstring for governance status, scope, and the
unconditional execution gate. This package does NOT execute any dispatch,
campaign, or replay-equivalent simulation on import or at any other point.
"""
from __future__ import annotations

from system.evaluation.n6_multi_origin_harness.harness import (
    CampaignAggregateResult,
    DispatchOptimizerProtocol,
    ForecastProviderProtocol,
    MultiOriginCampaignConfig,
    MultiOriginCampaignHarness,
    OriginRunResult,
    OriginRunStatus,
    SafetyEvaluatorProtocol,
    SimulationStepperProtocol,
    aggregate_origin_results,
    build_origin_scenario_pair,
    execute_origin_dispatch_cell,
    record_origin_outcome,
)
from system.evaluation.n6_multi_origin_harness.reproducibility_manifest import (
    CrossArmReproducibilityManifest,
    build_cross_arm_reproducibility_manifest,
    load_known_existing_hash_sources,
)

__all__ = [
    "CampaignAggregateResult",
    "MultiOriginCampaignConfig",
    "MultiOriginCampaignHarness",
    "OriginRunResult",
    "OriginRunStatus",
    "ForecastProviderProtocol",
    "DispatchOptimizerProtocol",
    "SimulationStepperProtocol",
    "SafetyEvaluatorProtocol",
    "aggregate_origin_results",
    "build_origin_scenario_pair",
    "execute_origin_dispatch_cell",
    "record_origin_outcome",
    "CrossArmReproducibilityManifest",
    "build_cross_arm_reproducibility_manifest",
    "load_known_existing_hash_sources",
]
