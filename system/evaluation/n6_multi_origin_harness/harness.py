"""
POLARIS -- N6 Multi-Origin Campaign Harness (Structure, Matching, Aggregation Only)
=====================================================================================
Resolves `ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Table row 2
(`ENGINEERING_WORK_REQUIRED`): as of that plan, no N6-integrated multi-origin
dispatch-campaign harness existed anywhere in the repository -- only two
single-origin integrations existed (`run_n6_closed_loop_simulation.py`,
`n6_operational_pipeline.py`, both in
`forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/`),
confirmed by FOR-02's targeted audit (register Section 19.4). This module
builds the smallest maintainable structure that generalizes that single-origin
pattern to N origins, WITHOUT executing it.

GOVERNANCE STATUS: NON-PRODUCTION / NOT EXECUTED / NO NEW EXECUTION PATH
-------------------------------------------------------------------------
- This module reuses, and does not duplicate or reimplement,
  `system/evaluation/replay_harness.py`'s existing `FactorIsolatedReplayHarness`,
  `ExperimentAConfig`, `ScenarioSpec`, `MatchedControllerSettings`, and
  `validate_matched_scenario_set` -- all unmodified, imported as-is.
- `MultiOriginCampaignHarness.execute_campaign()` delegates DIRECTLY to
  `FactorIsolatedReplayHarness.execute_experiment_a()`, which raises
  `CampaignExecutionNotAuthorizedError` UNCONDITIONALLY (no flag, config
  value, or environment variable disables it -- see `replay_harness.py`'s own
  module docstring). This module adds NO new authorization mechanism, NO new
  gate, and NO bypass of that gate. Calling `execute_campaign` with ANY
  config, including a fully valid one, always raises.
- This module does NOT import, call, mock, or stub `N6SolarForecastEngine`,
  `GAP19HighsNativeOptimizer`, `DigitalTwinSimulator`, or `EMSControlRouter`
  anywhere, and it still does not do so after this pass's implementation of
  `execute_origin_dispatch_cell`. **UPDATED THIS PASS (consolidated
  readiness-remediation, 2026-10-17):** `execute_origin_dispatch_cell` (bottom
  of this file) is no longer a bare `NotImplementedError` stub -- it is now
  a real, dependency-injected per-origin, per-arm dispatch-cell LOOP, typed
  against the four `*Protocol` classes defined below. It is exercised ONLY
  against small Fake/Mock test doubles in
  `system/tests/test_n6_multi_origin_harness.py`; this module never supplies
  it a real production object. It is NOT called by `execute_campaign` or by
  `MultiOriginCampaignHarness` anywhere -- the campaign-level gate above is
  completely independent of, and does not route through, this function.
  Wiring a REAL `N6SolarForecastEngine`/`GAP19HighsNativeOptimizer`/
  `DigitalTwinSimulator`/`EMSControlRouter` instance into this function and
  actually calling it that way would itself constitute a dispatch
  evaluation / replay-equivalent simulation, and requires the SAME
  campaign-execution authorization `execute_campaign` is gated behind; this
  function's existence grants, implies, or bypasses none of that.
- Every dataclass and function in this module operates on PLAIN, CALLER-SUPPLIED
  data (dicts, floats, strings) or on `replay_harness.py`'s own existing
  types. None of it reads a sealed file, a frozen model artifact, or any
  non-synthetic historical dataset. All of it is exercised in
  `system/tests/test_n6_multi_origin_harness.py` using small synthetic
  fixtures only.

WHAT THIS MODULE BUILDS
------------------------
- `build_origin_scenario_pair` / `build_multi_origin_campaign_config`:
  constructs N matched baseline/candidate `ScenarioSpec` pairs (one per
  origin) and wraps them in an `ExperimentAConfig`, so N6-vs-baseline matching
  and oracle-rejection are validated across an arbitrary origin set using the
  EXACT same checks `replay_harness.py` already provides for a single pair --
  this is the concrete "N6-integrated multi-origin candidate harness"
  structure the prerequisite plan identified as missing.
- `OriginRunStatus` / `OriginRunResult` / `record_origin_outcome`: the
  recording schema and logic for one arm's outcome at one origin -- diesel
  litres consumed, critical/total unmet load, safety evidence (explicitly
  `UNKNOWN_NOT_VERIFIED` when not supplied, NEVER defaulted to a pass),
  optimizer/run status, and provenance. Built from an already-produced
  dispatch-outcome dict and an already-computed (or absent)
  `SafetyEvaluationResult` -- never by running dispatch itself.
- `CampaignAggregateResult` / `aggregate_origin_results`: pure, per-arm
  aggregation across origins -- status counts, safety-evidence-unknown
  counts, diesel/unmet-load totals and means that EXCLUDE (never zero-fill)
  missing metrics.
- `MultiOriginCampaignHarness`: the multi-origin analogue of
  `FactorIsolatedReplayHarness`. `validate_campaign_config` performs
  configuration/matching/leakage checks only. `execute_campaign` always
  raises `CampaignExecutionNotAuthorizedError`.
- `ForecastProviderProtocol` / `DispatchOptimizerProtocol` /
  `SimulationStepperProtocol` / `SafetyEvaluatorProtocol`: structural
  (`typing.Protocol`) interface contracts describing the call SHAPE a real
  per-origin integration would need -- one `.predict`/`.optimize`/`.step`/
  `.evaluate_dispatch_safety` method each, mirroring
  `run_n6_closed_loop_simulation.py`'s existing single-origin call sequence
  (`N6SolarForecastEngine.predict` -> `EMSControlRouter`/
  `GAP19HighsNativeOptimizer.optimize` -> `DigitalTwinSimulator` step ->
  `reserve_policy_guard.evaluate_dispatch_safety`). These are typing
  contracts only -- this module does not import, subclass, or register any
  real implementation against them.
- `execute_origin_dispatch_cell`: the per-origin, per-arm dispatch-cell
  LOOP STRUCTURE, generalized via dependency injection against the four
  Protocols above and tested EXCLUSIVELY against small Fake/Mock test
  doubles (`system/tests/test_n6_multi_origin_harness.py`). It still never
  imports, constructs, or calls a real `N6SolarForecastEngine`,
  `GAP19HighsNativeOptimizer`, `DigitalTwinSimulator`, or
  `EMSControlRouter` -- see the function's own docstring for the governance
  statement on why wiring REAL objects through it requires a separate
  campaign-execution authorization this module does not grant, and is not
  done anywhere in this repository.
- `CrossArmReproducibilityManifest` / `build_cross_arm_reproducibility_manifest`
  (in the sibling `reproducibility_manifest.py` module): the schema and a
  fail-closed builder for the combined cross-arm reproducibility manifest
  (Table row 12 of `ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md`) -- it never
  fabricates a missing hash; every field must be supplied by the caller from
  an already-computed, cited source.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from system.evaluation.replay_harness import (
    ExperimentAConfig,
    FactorIsolatedReplayHarness,
    MatchedControllerSettings,
    ScenarioSpec,
)
from system.safety.reserve_policy_guard import SafetyEvaluationResult

__all__ = [
    "SAFETY_EVIDENCE_UNKNOWN",
    "SAFETY_EVIDENCE_VERIFIED",
    "VALID_ROUTES",
    "OriginRunStatus",
    "OriginRunResult",
    "CampaignAggregateResult",
    "MultiOriginCampaignConfig",
    "build_origin_scenario_pair",
    "build_multi_origin_campaign_config",
    "record_origin_outcome",
    "aggregate_origin_results",
    "summarize_step_safety_evaluations",
    "MultiOriginCampaignHarness",
    "ForecastProviderProtocol",
    "DispatchOptimizerProtocol",
    "SimulationStepperProtocol",
    "SafetyEvaluatorProtocol",
    "RouterProtocol",
    "execute_origin_dispatch_cell",
    "compute_canonical_realized_trajectory_hash",
    "compute_canonical_non_solar_forecast_hash",
    "PairedOriginComparisonResult",
    "evaluate_paired_origin_comparison",
]


# Matches SAF-02's existing literal (register Section 4 item 7 / Policy B) --
# reused here, not reinvented, for the same "missing evidence is unknown, not
# a pass" semantics applied to a per-origin safety evaluation.
SAFETY_EVIDENCE_UNKNOWN = "UNKNOWN_NOT_VERIFIED"
SAFETY_EVIDENCE_VERIFIED = "VERIFIED"

# IA-2 (owner decision, forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 2): the exact
# three-value route vocabulary `EMSControlRouter.evaluate_and_route` returns
# (`system/control/router.py` lines 100-106, a PROTECTED_FILE, read-only --
# reused verbatim here, never redefined or widened).
VALID_ROUTES = frozenset({"NORMAL", "EMERGENCY", "UNKNOWN_INVALID"})


class OriginRunStatus:
    """
    Run-outcome vocabulary for one arm at one origin. `OPTIMAL`,
    `FAILED_OPTIMIZATION_EXCEPTION`, and `FAILED_WORKER_EXIT` are the EXACT
    strings already used by `system/orchestration/worker.py:475` and
    `system/orchestration/master.py:121` (SAF-10) -- reused here rather than
    inventing parallel terminology. `INCOMPLETE_RUN` is introduced by this
    harness for the "fewer than the expected number of steps completed, no
    exception raised" case the directive separately calls out ("incomplete
    runs"), which worker.py/master.py's existing two-value vocabulary does
    not itself distinguish from a clean completion. `FAILED_UNKNOWN_INVALID`
    is the EXACT string `system/orchestration/worker.py`'s Cell B path uses
    (`status = "FAILED_UNKNOWN_INVALID"`, confirmed by direct read this
    pass) for the fail-closed case where the router returns
    `UNKNOWN_INVALID` -- reused here (IA-2 pass) for the same reason, now
    that `execute_origin_dispatch_cell` can observe a router's route
    decision at all.
    """

    OPTIMAL = "OPTIMAL"
    FAILED_OPTIMIZATION_EXCEPTION = "FAILED_OPTIMIZATION_EXCEPTION"
    FAILED_WORKER_EXIT = "FAILED_WORKER_EXIT"
    INCOMPLETE_RUN = "INCOMPLETE_RUN"
    FAILED_UNKNOWN_INVALID = "FAILED_UNKNOWN_INVALID"
    ALL = frozenset(
        {OPTIMAL, FAILED_OPTIMIZATION_EXCEPTION, FAILED_WORKER_EXIT, INCOMPLETE_RUN, FAILED_UNKNOWN_INVALID}
    )


@dataclass(frozen=True)
class OriginRunResult:
    """One arm's recorded outcome for one origin. Immutable, fully explicit."""

    origin: str
    arm: str  # "baseline" | "candidate"
    scenario_key: str
    forecast_provider: str
    run_status: str
    completed_steps: int
    expected_steps: int
    diesel_consumed_liters: Optional[float]
    critical_unmet_load_wh: Optional[float]
    total_unmet_load_wh: Optional[float]
    safety_evidence_status: str  # SAFETY_EVIDENCE_UNKNOWN | SAFETY_EVIDENCE_VERIFIED
    safety_passed: Optional[bool]  # None iff safety_evidence_status == SAFETY_EVIDENCE_UNKNOWN
    optimizer_constraint_status: Optional[str]
    failure_reasons: Tuple[str, ...]
    provenance: Dict[str, Any]
    # IA-2 (owner decision, Section 2 of forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md):
    # the ACTUAL router decision for this origin, recorded explicitly rather
    # than inferred after the fact from which optimizer ran. `route` is the
    # LAST route observed in this run (the only route, for a single-shot
    # wiring); `route_history` is the FULL per-step sequence of route
    # decisions, needed to reconstruct a receding-horizon run where the
    # route can legitimately differ step to step. `None` / `()` mean no
    # `RouterProtocol` was supplied to `execute_origin_dispatch_cell` for
    # this run (the pre-existing, router-less call shape remains valid and
    # unchanged) -- NEVER a silent default standing in for an unrecorded
    # real decision.
    route: Optional[str] = None
    route_history: Tuple[str, ...] = ()
    # OWNER-AUTHORIZED BLOCKER RESOLUTION PASS (2026-10-17), Section 3A /
    # forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md blocker F ("safety is evaluated once
    # per run, not once per step"): the FULL per-step sequence of safety
    # evaluations this run actually produced, one entry per completed step,
    # in step order. `None` at a given index means either no
    # `SafetyEvaluatorProtocol` was supplied for this run at all, or that
    # step produced no dispatch outcome to evaluate -- NEVER a silent pass.
    # Stays `()` whenever no safety evaluator was supplied (identical to the
    # pre-existing, unchanged `safety_evidence_status`/`safety_passed`
    # single-verdict fields below, which this field does not replace --
    # those two still carry the LAST step's verdict for backward
    # compatibility with every pre-existing caller/test). This is purely
    # additive bookkeeping inside this isolated, fakes-only harness; it does
    # not call, wrap, or change `reserve_policy_guard.evaluate_dispatch_safety`
    # itself, and it changes no production call site, control flow, or
    # execution/run/worker status field anywhere in the repository.
    step_safety_evaluations: Tuple[Optional[SafetyEvaluationResult], ...] = ()
    # BLOCKER-LATCH-1 & BLOCKER-FUEL-1: All-step latching and comprehensive metrics
    has_solver_failure: bool = False
    has_unmet_essential: bool = False
    has_fuel_failure: bool = False
    fuel_failure_reason: Optional[str] = None
    all_step_solver_statuses: Tuple[str, ...] = ()
    all_step_unmet_essential_wh: Tuple[float, ...] = ()
    generator_starts: Optional[int] = None
    initial_battery_soc_pct: Optional[float] = None
    terminal_battery_soc_pct: Optional[float] = None
    initial_battery_energy_wh: Optional[float] = None
    terminal_battery_energy_wh: Optional[float] = None
    delta_e_term_wh: Optional[float] = None
    startup_surcharge_liters: Optional[float] = None
    diesel_fuel_tracking_gap: bool = False
    fold_label: Optional[str] = None
    realized_trajectory_hash: Optional[str] = None
    non_solar_forecast_hash: Optional[str] = None
    resolved_terminal_target_wh: Optional[float] = None
    resolved_ebr_target_wh: Optional[Tuple[float, ...]] = None

    def __post_init__(self) -> None:
        if self.run_status not in OriginRunStatus.ALL:
            raise ValueError(
                f"Fail-closed: unknown run_status '{self.run_status}' for origin '{self.origin}' ({self.arm})."
            )
        if self.arm not in ("baseline", "candidate"):
            raise ValueError(f"Fail-closed: arm must be 'baseline' or 'candidate', got '{self.arm}'.")
        if self.has_solver_failure and self.run_status == OriginRunStatus.OPTIMAL:
            raise ValueError(
                f"Fail-closed: run_status cannot be OPTIMAL when has_solver_failure is True for origin '{self.origin}' ({self.arm})."
            )
        if (self.has_fuel_failure or self.diesel_fuel_tracking_gap) and self.diesel_consumed_liters is not None:
            raise ValueError(
                f"Fail-closed: diesel_consumed_liters must be None when fuel failure or tracking gap is latched for origin '{self.origin}' ({self.arm})."
            )
        if self.safety_evidence_status == SAFETY_EVIDENCE_UNKNOWN and self.safety_passed is not None:
            raise ValueError(
                "Fail-closed: safety_evidence_status is UNKNOWN_NOT_VERIFIED but safety_passed is not "
                "None -- missing safety evidence must never be paired with an inferred pass/fail value."
            )
        if self.safety_evidence_status == SAFETY_EVIDENCE_VERIFIED and self.safety_passed is None:
            raise ValueError(
                "Fail-closed: safety_evidence_status is VERIFIED but safety_passed is None -- a verified "
                "evaluation must carry an explicit boolean outcome."
            )
        if self.completed_steps < 0 or self.expected_steps <= 0 or self.completed_steps > self.expected_steps:
            raise ValueError(
                f"Fail-closed: invalid step counts for origin '{self.origin}' ({self.arm}): "
                f"completed={self.completed_steps}, expected={self.expected_steps}."
            )
        if self.route is not None and self.route not in VALID_ROUTES:
            raise ValueError(
                f"Fail-closed: unrecognized route '{self.route}' for origin '{self.origin}' ({self.arm}) -- "
                f"must be one of {sorted(VALID_ROUTES)} or None."
            )
        bad_history = [r for r in self.route_history if r not in VALID_ROUTES]
        if bad_history:
            raise ValueError(
                f"Fail-closed: route_history for origin '{self.origin}' ({self.arm}) contains unrecognized "
                f"route(s) {bad_history} -- must each be one of {sorted(VALID_ROUTES)}."
            )
        if self.route_history and self.route != self.route_history[-1]:
            raise ValueError(
                f"Fail-closed: route ('{self.route}') must equal route_history[-1] "
                f"('{self.route_history[-1]}') for origin '{self.origin}' ({self.arm}) -- route provenance "
                "must never silently diverge from, or be replaced by a default relative to, the recorded "
                "per-step history."
            )
        if self.route is None and self.route_history:
            raise ValueError(
                f"Fail-closed: route_history is non-empty for origin '{self.origin}' ({self.arm}) but "
                "route is None -- a recorded per-step route history must always carry an explicit final "
                "route, never leave it defaulted away."
            )
        if len(self.step_safety_evaluations) > self.completed_steps:
            raise ValueError(
                f"Fail-closed: step_safety_evaluations has {len(self.step_safety_evaluations)} entries "
                f"but only {self.completed_steps} step(s) completed for origin '{self.origin}' "
                f"({self.arm}) -- cannot record more per-step safety evaluations than steps actually ran."
            )
        if self.step_safety_evaluations and self.safety_evidence_status == SAFETY_EVIDENCE_VERIFIED:
            if self.step_safety_evaluations[-1] is None:
                raise ValueError(
                    f"Fail-closed: safety_evidence_status is VERIFIED for origin '{self.origin}' "
                    f"({self.arm}) but the last recorded per-step safety evaluation is None -- the "
                    "overall verdict must be derived from, and consistent with, the last step's own "
                    "evaluation, never a value the per-step record does not support."
                )


def record_origin_outcome(
    origin: str,
    arm: str,
    scenario_key: str,
    forecast_provider: str,
    completed_steps: int,
    expected_steps: int,
    dispatch_outcome: Optional[Dict[str, Any]],
    safety_evaluation: Optional[SafetyEvaluationResult],
    provenance: Dict[str, Any],
    exception_message: Optional[str] = None,
    route: Optional[str] = None,
    route_history: Tuple[str, ...] = (),
    step_safety_evaluations: Tuple[Optional[SafetyEvaluationResult], ...] = (),
    has_solver_failure: Optional[bool] = None,
    has_unmet_essential: Optional[bool] = None,
    has_fuel_failure: Optional[bool] = None,
    fuel_failure_reason: Optional[str] = None,
    all_step_solver_statuses: Tuple[str, ...] = (),
    all_step_unmet_essential_wh: Tuple[float, ...] = (),
    generator_starts: Optional[int] = None,
    initial_battery_soc_pct: Optional[float] = None,
    terminal_battery_soc_pct: Optional[float] = None,
    initial_battery_energy_wh: Optional[float] = None,
    terminal_battery_energy_wh: Optional[float] = None,
    delta_e_term_wh: Optional[float] = None,
    startup_surcharge_liters: Optional[float] = None,
    diesel_fuel_tracking_gap: Optional[bool] = None,
    fold_label: Optional[str] = None,
    realized_trajectory_hash: Optional[str] = None,
    non_solar_forecast_hash: Optional[str] = None,
    resolved_terminal_target_wh: Optional[float] = None,
    resolved_ebr_target_wh: Optional[Tuple[float, ...]] = None,
) -> OriginRunResult:
    """
    Builds one `OriginRunResult` from ALREADY-COMPUTED outcomes. This
    function does not call N6, GAP19, the router, or the simulator -- it only
    packages outputs a future, separately authorized execution path would
    produce, which is why it can be exercised in tests against small plain
    dicts with no real dispatch involved.

    `dispatch_outcome`, if supplied, is expected to carry (any subset of)
    `diesel_consumed_liters`, `critical_unmet_load_wh`, `total_unmet_load_wh`,
    `constraint_status` -- the same field names used by `DispatchPlan`-derived
    reporting elsewhere in the repository (`evaluator.py`/`worker.py`). A
    missing key is recorded as `None` and excluded from later aggregation,
    never coerced to `0.0` (the SAF-09 zero-default bug this repository has
    already fixed once, for a different field, is not reintroduced here).

    `safety_evaluation=None` means safety evidence genuinely was not produced
    for this origin -- per the directive, this is UNKNOWN, never a pass.
    """
    failure_reasons: List[str] = []

    # Blocker LATCH-1: Resolve solver failure latch
    if has_solver_failure is None:
        if all_step_solver_statuses:
            has_solver_failure = any(s != "OPTIMAL" for s in all_step_solver_statuses)
        elif dispatch_outcome is not None and dispatch_outcome.get("constraint_status") != "OPTIMAL":
            has_solver_failure = True
        elif exception_message is not None:
            has_solver_failure = True
        else:
            has_solver_failure = False

    raw_crit = dispatch_outcome.get("critical_unmet_load_wh") if dispatch_outcome else None
    is_crit_valid = True
    if raw_crit is not None:
        is_crit_valid = (
            not isinstance(raw_crit, bool)
            and isinstance(raw_crit, (int, float))
            and not math.isnan(raw_crit)
            and not math.isinf(raw_crit)
            and raw_crit >= 0.0
        )
        if not is_crit_valid:
            has_unmet_essential = True
            critical_unmet = None
        else:
            critical_unmet = float(raw_crit)
    else:
        critical_unmet = None
        if completed_steps == expected_steps:
            has_unmet_essential = True
            is_crit_valid = False

    raw_total = dispatch_outcome.get("total_unmet_load_wh") if dispatch_outcome else None
    is_total_valid = True
    if raw_total is not None:
        is_total_valid = (
            not isinstance(raw_total, bool)
            and isinstance(raw_total, (int, float))
            and not math.isnan(raw_total)
            and not math.isinf(raw_total)
            and raw_total >= 0.0
        )
        if not is_total_valid:
            total_unmet = None
        else:
            total_unmet = float(raw_total)
    else:
        total_unmet = None
        if completed_steps == expected_steps:
            is_total_valid = False

    # Blocker LATCH-1: Resolve unmet essential load latch
    if has_unmet_essential is None:
        if all_step_unmet_essential_wh:
            has_unmet_essential = any(w > 1e-6 for w in all_step_unmet_essential_wh)
        elif critical_unmet is not None:
            has_unmet_essential = critical_unmet > 1e-6
        else:
            has_unmet_essential = False

    # Blocker FUEL-1: Resolve fuel failure latch
    if has_fuel_failure is None:
        if dispatch_outcome is not None and dispatch_outcome.get("has_fuel_failure"):
            has_fuel_failure = True
            fuel_failure_reason = fuel_failure_reason or dispatch_outcome.get("fuel_failure_reason")
        else:
            has_fuel_failure = False

    # Blocker FUEL-1: Detect fuel tracking gap
    if diesel_fuel_tracking_gap is None:
        if (
            dispatch_outcome is not None
            and "diesel_consumed_liters" in dispatch_outcome
            and dispatch_outcome.get("diesel_consumed_liters") is None
            and completed_steps == expected_steps
            and not has_fuel_failure
            and exception_message is None
        ):
            diesel_fuel_tracking_gap = True
        else:
            diesel_fuel_tracking_gap = False

    if safety_evaluation is None:
        safety_evidence_status = SAFETY_EVIDENCE_UNKNOWN
        safety_passed: Optional[bool] = None
    else:
        safety_evidence_status = SAFETY_EVIDENCE_VERIFIED
        safety_passed = bool(safety_evaluation.passed)
        failure_reasons.extend(safety_evaluation.failure_reasons)

    if exception_message is not None:
        run_status = OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION
        failure_reasons.append(exception_message)
    elif route == "UNKNOWN_INVALID" and completed_steps < expected_steps:
        run_status = OriginRunStatus.FAILED_UNKNOWN_INVALID
        failure_reasons.append(
            f"Router returned UNKNOWN_INVALID for origin '{origin}' ({arm}) at step {completed_steps}; "
            "halted fail-closed before invoking the optimizer, matching worker.py's Cell B behavior."
        )
    elif (dispatch_outcome is not None and dispatch_outcome.get("constraint_status") != "OPTIMAL") or has_solver_failure:
        run_status = OriginRunStatus.FAILED_WORKER_EXIT
        c_status = dispatch_outcome.get("constraint_status") if dispatch_outcome else "NON_OPTIMAL"
        failure_reasons.append(
            f"Optimizer constraint_status='{c_status}' or solver failure latched for origin "
            f"'{origin}' ({arm})."
        )
    elif completed_steps < expected_steps:
        run_status = OriginRunStatus.INCOMPLETE_RUN
        failure_reasons.append(
            f"Only {completed_steps}/{expected_steps} steps completed for origin '{origin}' ({arm})."
        )
    elif has_fuel_failure or diesel_fuel_tracking_gap:
        run_status = OriginRunStatus.FAILED_WORKER_EXIT
        reason = fuel_failure_reason or f"Fuel failure or tracking gap latched for origin '{origin}' ({arm})."
        failure_reasons.append(reason)
    elif has_unmet_essential or not is_crit_valid or (completed_steps == expected_steps and raw_crit is None):
        run_status = OriginRunStatus.FAILED_WORKER_EXIT
        failure_reasons.append(
            f"Unmet essential load or invalid/missing critical_unmet_load_wh telemetry for origin '{origin}' ({arm})."
        )
    elif not is_total_valid or (completed_steps == expected_steps and raw_total is None):
        run_status = OriginRunStatus.FAILED_WORKER_EXIT
        failure_reasons.append(
            f"Invalid or missing total_unmet_load_wh telemetry for origin '{origin}' ({arm})."
        )
    elif safety_passed is False:
        run_status = OriginRunStatus.FAILED_WORKER_EXIT
        failure_reasons.append(
            f"Safety evaluation failed for origin '{origin}' ({arm})."
        )
    else:
        run_status = OriginRunStatus.OPTIMAL

    diesel = dispatch_outcome.get("diesel_consumed_liters") if dispatch_outcome else None
    constraint_status = dispatch_outcome.get("constraint_status") if dispatch_outcome else None

    # Fail closed on fuel: zero or negative remaining fuel / clamping / tracking gap sets diesel to None
    if has_fuel_failure or diesel_fuel_tracking_gap:
        diesel = None

    if has_fuel_failure and fuel_failure_reason:
        if fuel_failure_reason not in failure_reasons:
            failure_reasons.append(fuel_failure_reason)

    # Populate optional metrics from dispatch_outcome if available
    if generator_starts is None and dispatch_outcome:
        generator_starts = dispatch_outcome.get("generator_starts")
    if initial_battery_soc_pct is None and dispatch_outcome:
        initial_battery_soc_pct = dispatch_outcome.get("initial_battery_soc_pct")
    if terminal_battery_soc_pct is None and dispatch_outcome:
        terminal_battery_soc_pct = dispatch_outcome.get("terminal_battery_soc_pct")
    if initial_battery_energy_wh is None and dispatch_outcome:
        initial_battery_energy_wh = dispatch_outcome.get("initial_battery_energy_wh")
    if terminal_battery_energy_wh is None and dispatch_outcome:
        terminal_battery_energy_wh = dispatch_outcome.get("terminal_battery_energy_wh")
    if delta_e_term_wh is None and dispatch_outcome:
        delta_e_term_wh = dispatch_outcome.get("delta_e_term_wh")
    if startup_surcharge_liters is None and dispatch_outcome:
        startup_surcharge_liters = dispatch_outcome.get("startup_surcharge_liters")

    # On an aborted trajectory or invalid run, do not fabricate terminal energy/SOC deltas,
    # generator starts, or startup surcharges. Mark unavailable metrics as None and quarantine the run.
    is_aborted = (
        completed_steps < expected_steps
        or run_status != OriginRunStatus.OPTIMAL
        or has_solver_failure
        or has_unmet_essential
        or has_fuel_failure
        or diesel_fuel_tracking_gap
        or safety_passed is False
        or not is_total_valid
        or not is_crit_valid
    )
    if is_aborted:
        diesel = None
        generator_starts = None
        startup_surcharge_liters = None
        terminal_battery_soc_pct = None
        terminal_battery_energy_wh = None
        delta_e_term_wh = None
        if not is_crit_valid or (completed_steps == expected_steps and raw_crit is None):
            critical_unmet = None
        if not is_total_valid or (completed_steps == expected_steps and raw_total is None):
            total_unmet = None

    if not all_step_solver_statuses and constraint_status is not None:
        all_step_solver_statuses = (str(constraint_status),)
    if not all_step_unmet_essential_wh and critical_unmet is not None and is_crit_valid:
        all_step_unmet_essential_wh = (float(critical_unmet),)

    return OriginRunResult(
        origin=origin,
        arm=arm,
        scenario_key=scenario_key,
        forecast_provider=forecast_provider,
        run_status=run_status,
        completed_steps=completed_steps,
        expected_steps=expected_steps,
        diesel_consumed_liters=diesel,
        critical_unmet_load_wh=critical_unmet,
        total_unmet_load_wh=total_unmet,
        safety_evidence_status=safety_evidence_status,
        safety_passed=safety_passed,
        optimizer_constraint_status=constraint_status,
        failure_reasons=tuple(failure_reasons),
        provenance=dict(provenance),
        route=route,
        route_history=tuple(route_history),
        step_safety_evaluations=tuple(step_safety_evaluations),
        has_solver_failure=has_solver_failure,
        has_unmet_essential=has_unmet_essential,
        has_fuel_failure=has_fuel_failure,
        fuel_failure_reason=fuel_failure_reason,
        all_step_solver_statuses=tuple(all_step_solver_statuses),
        all_step_unmet_essential_wh=tuple(all_step_unmet_essential_wh),
        generator_starts=generator_starts,
        initial_battery_soc_pct=initial_battery_soc_pct,
        terminal_battery_soc_pct=terminal_battery_soc_pct,
        initial_battery_energy_wh=initial_battery_energy_wh,
        terminal_battery_energy_wh=terminal_battery_energy_wh,
        delta_e_term_wh=delta_e_term_wh,
        startup_surcharge_liters=startup_surcharge_liters,
        diesel_fuel_tracking_gap=diesel_fuel_tracking_gap,
        fold_label=fold_label,
        realized_trajectory_hash=realized_trajectory_hash,
        non_solar_forecast_hash=non_solar_forecast_hash,
        resolved_terminal_target_wh=resolved_terminal_target_wh,
        resolved_ebr_target_wh=resolved_ebr_target_wh,
    )


def summarize_step_safety_evaluations(
    step_safety_evaluations: Tuple[Optional[SafetyEvaluationResult], ...],
) -> Dict[str, int]:
    """
    Pure, read-only summary of ONE origin run's PER-STEP safety-evaluation
    sequence (OWNER-AUTHORIZED BLOCKER RESOLUTION PASS, 2026-10-17; Section
    3A of the governing directive; resolves blocker F of
    `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md` Section 6 -- "safety is evaluated
    once per run, not once per step" -- WITHIN this isolated, fakes-only
    harness only). Never calls a real `reserve_policy_guard.evaluate_dispatch_safety`,
    never invents a missing step's evaluation, and never folds an unknown
    step into a pass or a fail -- a `None` entry (no safety evaluator
    supplied, or that step produced no dispatch outcome) is excluded from
    every count below.

    Mirrors, in vocabulary only (not in any shared code path), the kind of
    cumulative per-step integrity counters `worker.py`'s real Cell B loop
    accumulates (reserve-shortfall totals, hard-SOC-violation counts) --
    this function does not read, call, or depend on `worker.py` in any way.
    """
    evaluated = [e for e in step_safety_evaluations if e is not None]
    return {
        "n_steps_total": len(step_safety_evaluations),
        "n_steps_evaluated": len(evaluated),
        "n_steps_unknown": len(step_safety_evaluations) - len(evaluated),
        "n_steps_passed": sum(1 for e in evaluated if e.passed),
        "n_steps_failed": sum(1 for e in evaluated if not e.passed),
        "n_steps_hard_soc_violation": sum(1 for e in evaluated if e.hard_soc_violation),
        "n_steps_reserve_violation": sum(1 for e in evaluated if e.reserve_violation),
        "n_steps_solver_infeasible": sum(1 for e in evaluated if e.solver_infeasible),
    }


@dataclass(frozen=True)
class CampaignAggregateResult:
    """Pure, per-arm aggregation across origins. See `aggregate_origin_results`."""

    arm: str
    n_origins: int
    status_counts: Dict[str, int]
    n_safety_unknown: int
    n_safety_verified_pass: int
    n_safety_verified_fail: int
    total_diesel_consumed_liters: Optional[float]
    mean_diesel_consumed_liters: Optional[float]
    total_critical_unmet_load_wh: Optional[float]
    total_total_unmet_load_wh: Optional[float]
    n_missing_diesel_metric: int
    n_missing_critical_unmet_metric: int
    per_origin: Tuple[OriginRunResult, ...]
    # IA-2: route provenance survives aggregation two ways -- (a) every
    # individual OriginRunResult in `per_origin` still carries its own
    # `route`/`route_history` untouched (aggregation never strips it), and
    # (b) this summary-level count, so a report can state "N origins routed
    # EMERGENCY this arm" without re-walking `per_origin` itself. Origins
    # with `route is None` (no RouterProtocol supplied for that run) are
    # excluded from this count, never folded into a route bucket they were
    # never actually assigned.
    route_counts: Dict[str, int]
    total_generator_starts: Optional[int] = None
    total_startup_surcharge_liters: Optional[float] = None
    net_delta_e_term_wh: Optional[float] = None
    n_solver_failures: int = 0
    n_unmet_essential_failures: int = 0
    n_fuel_failures: int = 0
    by_fold: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    n_eligible_origins: int = 0


def aggregate_origin_results(results: List[OriginRunResult], arm: str) -> CampaignAggregateResult:
    """
    Pure aggregation across one arm's per-origin `OriginRunResult`s. A
    missing diesel/unmet-load metric is EXCLUDED from the sum/mean and
    counted separately as missing -- never silently folded in as `0.0`.
    Safety evidence is tallied into exactly three buckets (unknown / verified
    pass / verified fail); "unknown" is never added to "verified pass".

    Operational performance metrics (diesel, generator starts, surcharges,
    terminal energy delta, unmet load) are calculated ONLY from eligible runs
    that completed all expected steps, have OPTIMAL status, and have no solver,
    essential-load, fuel, or fuel-tracking failure.
    """
    arm_results = [r for r in results if r.arm == arm]
    if not arm_results:
        raise ValueError(f"Fail-closed: no OriginRunResult entries found for arm '{arm}'.")

    status_counts: Dict[str, int] = {}
    for r in arm_results:
        status_counts[r.run_status] = status_counts.get(r.run_status, 0) + 1

    n_safety_unknown = sum(1 for r in arm_results if r.safety_evidence_status == SAFETY_EVIDENCE_UNKNOWN)
    n_safety_verified_pass = sum(
        1 for r in arm_results if r.safety_evidence_status == SAFETY_EVIDENCE_VERIFIED and r.safety_passed
    )
    n_safety_verified_fail = sum(
        1 for r in arm_results if r.safety_evidence_status == SAFETY_EVIDENCE_VERIFIED and r.safety_passed is False
    )

    # Operational performance metrics are calculated ONLY from eligible runs:
    # 1. completed all expected steps
    # 2. run_status == OPTIMAL
    # 3. no solver failure
    # 4. no unmet essential load failure
    # 5. no fuel failure
    # 6. no fuel tracking gap
    eligible_results = [
        r for r in arm_results
        if r.completed_steps == r.expected_steps
        and r.run_status == OriginRunStatus.OPTIMAL
        and not r.has_solver_failure
        and not r.has_unmet_essential
        and not r.has_fuel_failure
        and not r.diesel_fuel_tracking_gap
        and r.safety_passed is not False
        and r.critical_unmet_load_wh is not None
        and r.total_unmet_load_wh is not None
    ]

    diesel_values = [r.diesel_consumed_liters for r in eligible_results if r.diesel_consumed_liters is not None]
    critical_values = [r.critical_unmet_load_wh for r in eligible_results if r.critical_unmet_load_wh is not None]
    total_values = [r.total_unmet_load_wh for r in eligible_results if r.total_unmet_load_wh is not None]

    route_counts: Dict[str, int] = {}
    for r in arm_results:
        if r.route is not None:
            route_counts[r.route] = route_counts.get(r.route, 0) + 1

    starts = [r.generator_starts for r in eligible_results if r.generator_starts is not None]
    surcharges = [r.startup_surcharge_liters for r in eligible_results if r.startup_surcharge_liters is not None]
    deltas = [r.delta_e_term_wh for r in eligible_results if r.delta_e_term_wh is not None]
    n_solver_failures = sum(1 for r in arm_results if r.has_solver_failure)
    n_unmet_essential_failures = sum(1 for r in arm_results if r.has_unmet_essential)
    n_fuel_failures = sum(1 for r in arm_results if r.has_fuel_failure or r.diesel_fuel_tracking_gap)

    by_fold: Dict[str, Dict[str, Any]] = {}
    folds = {r.fold_label for r in arm_results if r.fold_label is not None}
    for f in sorted(folds):
        f_results = [r for r in arm_results if r.fold_label == f]
        f_eligible = [
            r for r in f_results
            if r.completed_steps == r.expected_steps
            and r.run_status == OriginRunStatus.OPTIMAL
            and not r.has_solver_failure
            and not r.has_unmet_essential
            and not r.has_fuel_failure
            and not r.diesel_fuel_tracking_gap
            and r.safety_passed is not False
            and r.critical_unmet_load_wh is not None
            and r.total_unmet_load_wh is not None
        ]
        f_diesel = [r.diesel_consumed_liters for r in f_eligible if r.diesel_consumed_liters is not None]
        by_fold[f] = {
            "n_origins": len(f_results),
            "n_eligible_origins": len(f_eligible),
            "total_diesel_consumed_liters": sum(f_diesel) if f_diesel else None,
            "mean_diesel_consumed_liters": (sum(f_diesel) / len(f_diesel)) if f_diesel else None,
            "n_solver_failures": sum(1 for r in f_results if r.has_solver_failure),
            "n_fuel_failures": sum(1 for r in f_results if r.has_fuel_failure or r.diesel_fuel_tracking_gap),
        }

    return CampaignAggregateResult(
        arm=arm,
        n_origins=len(arm_results),
        status_counts=status_counts,
        n_safety_unknown=n_safety_unknown,
        n_safety_verified_pass=n_safety_verified_pass,
        route_counts=route_counts,
        n_safety_verified_fail=n_safety_verified_fail,
        total_diesel_consumed_liters=sum(diesel_values) if diesel_values else None,
        mean_diesel_consumed_liters=(sum(diesel_values) / len(diesel_values)) if diesel_values else None,
        total_critical_unmet_load_wh=sum(critical_values) if critical_values else None,
        total_total_unmet_load_wh=sum(total_values) if total_values else None,
        n_missing_diesel_metric=len(arm_results) - len(diesel_values),
        n_missing_critical_unmet_metric=len(arm_results) - len(critical_values),
        per_origin=tuple(arm_results),
        total_generator_starts=sum(starts) if starts else None,
        total_startup_surcharge_liters=sum(surcharges) if surcharges else None,
        net_delta_e_term_wh=sum(deltas) if deltas else None,
        n_solver_failures=n_solver_failures,
        n_unmet_essential_failures=n_unmet_essential_failures,
        n_fuel_failures=n_fuel_failures,
        by_fold=by_fold,
        n_eligible_origins=len(eligible_results),
    )


def build_origin_scenario_pair(
    origin: str,
    baseline_provider: str,
    candidate_provider: str,
    controller_settings: MatchedControllerSettings,
    initial_battery_soc_wh: float,
    governed_reserve_policy_name: str,
) -> Tuple[ScenarioSpec, ScenarioSpec]:
    """
    Builds one matched baseline/candidate `ScenarioSpec` pair for a single
    origin. Both specs go through `ScenarioSpec.__post_init__`'s existing
    `reject_if_oracle` call automatically -- this function adds no separate
    leakage check of its own, by design, to avoid two independently-maintained
    copies of the same rule drifting apart.
    """
    baseline = ScenarioSpec(
        scenario_key=origin,
        forecast_origin=origin,
        initial_battery_soc_wh=initial_battery_soc_wh,
        controller_settings=controller_settings,
        forecast_provider=baseline_provider,
        reserve_policy_name=governed_reserve_policy_name,
    )
    candidate = ScenarioSpec(
        scenario_key=origin,
        forecast_origin=origin,
        initial_battery_soc_wh=initial_battery_soc_wh,
        controller_settings=controller_settings,
        forecast_provider=candidate_provider,
        reserve_policy_name=governed_reserve_policy_name,
    )
    return baseline, candidate


@dataclass
class MultiOriginCampaignConfig:
    """
    Multi-origin analogue of `ExperimentAConfig`: N matched baseline/candidate
    `ScenarioSpec` pairs (one per origin) instead of a single pair. Wraps an
    `ExperimentAConfig` rather than reimplementing its matching/oracle-rejection
    logic -- `experiment_a_config`'s own `__post_init__` has already run
    `validate_matched_scenario_set` and every `ScenarioSpec`'s oracle check by
    the time this object exists.
    """

    origins: List[str]
    experiment_a_config: ExperimentAConfig

    @property
    def n_origins(self) -> int:
        return len(self.origins)


def build_multi_origin_campaign_config(
    origins: List[str],
    baseline_provider: str,
    candidate_provider: str,
    controller_settings: MatchedControllerSettings,
    initial_battery_soc_wh_by_origin: Dict[str, float],
    governed_reserve_policy_name: str,
) -> MultiOriginCampaignConfig:
    """
    Builds and validates a `MultiOriginCampaignConfig` for N origins. Fails
    closed on: an empty origin list, a duplicate origin, or any origin
    missing its required initial battery SOC (this function never invents an
    initial condition -- see ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md Table
    row 5 -- the caller must supply one per origin from a real, cited source).
    """
    if not origins:
        raise ValueError("Fail-closed: at least one origin is required.")
    if len(set(origins)) != len(origins):
        dupes = sorted({o for o in origins if origins.count(o) > 1})
        raise ValueError(f"Fail-closed: duplicate origins supplied: {dupes}")
    missing_soc = [o for o in origins if o not in initial_battery_soc_wh_by_origin]
    if missing_soc:
        raise ValueError(
            f"Fail-closed: no initial_battery_soc_wh supplied for origins {missing_soc}. This harness "
            "does not invent an initial condition; the caller must supply one per origin from an "
            "existing, cited source."
        )

    baseline_scenarios: List[ScenarioSpec] = []
    candidate_scenarios: List[ScenarioSpec] = []
    for origin in origins:
        b, c = build_origin_scenario_pair(
            origin=origin,
            baseline_provider=baseline_provider,
            candidate_provider=candidate_provider,
            controller_settings=controller_settings,
            initial_battery_soc_wh=initial_battery_soc_wh_by_origin[origin],
            governed_reserve_policy_name=governed_reserve_policy_name,
        )
        baseline_scenarios.append(b)
        candidate_scenarios.append(c)

    experiment_a_config = ExperimentAConfig(
        baseline_scenarios=baseline_scenarios,
        candidate_scenarios=candidate_scenarios,
        governed_reserve_policy_name=governed_reserve_policy_name,
    )
    return MultiOriginCampaignConfig(origins=list(origins), experiment_a_config=experiment_a_config)


class MultiOriginCampaignHarness:
    """
    Multi-origin analogue of `FactorIsolatedReplayHarness`. Owns one instance
    of the existing, unmodified harness and delegates every authorization
    decision to it -- this class defines no execution-authorization logic of
    its own.
    """

    def __init__(self) -> None:
        self._replay_harness = FactorIsolatedReplayHarness()

    def validate_campaign_config(self, config: MultiOriginCampaignConfig) -> MultiOriginCampaignConfig:
        """Re-validates an already-constructed config. Runs no dispatch."""
        self._replay_harness.validate_experiment_a_config(config.experiment_a_config)
        return config

    def execute_campaign(
        self,
        config: MultiOriginCampaignConfig,
        auth: Any = None,
    ) -> None:
        """
        Always raises `CampaignExecutionNotAuthorizedError` (or `SecurityIntegrityViolationError`). This call does
        nothing but forward to `FactorIsolatedReplayHarness.execute_experiment_a`,
        which raises unconditionally. No multi-origin dispatch loop exists in
        this module for this method to reach even if that upstream guard were
        ever lifted elsewhere -- see `execute_origin_dispatch_cell` below.
        """
        self._replay_harness.execute_experiment_a(config.experiment_a_config, auth=auth)


@runtime_checkable
class ForecastProviderProtocol(Protocol):
    """
    Structural contract for the arm's forecast provider at one step.
    Mirrors `N6SolarForecastEngine.predict` (candidate arm) / the existing
    baseline provider (baseline arm) in shape only -- this module never
    imports or references either real class.
    """

    def predict(self, origin: str, step_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        ...


@runtime_checkable
class DispatchOptimizerProtocol(Protocol):
    """
    Structural contract for one step's optimization call. Mirrors
    `GAP19HighsNativeOptimizer.optimize` (route `NORMAL`) /
    `OptionDFallbackSolver.solve` (route `EMERGENCY`) in shape only -- this
    module never imports or references either real class. IA-2 (owner
    decision, this pass): the router's decision is now supplied via the
    fifth `RouterProtocol` slot below rather than folded silently into this
    call; an implementation that needs to branch NORMAL/EMERGENCY reads the
    route an upstream `RouterProtocol` call recorded (e.g. via a `"route"`
    key the caller's own wiring adds to `forecast` before this call --
    `execute_origin_dispatch_cell` does exactly this when a `router` is
    supplied), rather than recomputing or re-inferring it here.
    """

    def optimize(
        self, state: Dict[str, Any], forecast: Dict[str, Any], controller_settings: MatchedControllerSettings
    ) -> Dict[str, Any]:
        ...


@runtime_checkable
class RouterProtocol(Protocol):
    """
    IA-2 (owner decision, forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 2): the
    fifth structural contract, added this pass, for the routing step real
    production call sites (`worker.py`, `runner.py`,
    `run_n6_closed_loop_simulation.py`) all perform immediately before
    optimize/solve. Mirrors `EMSControlRouter.evaluate_and_route(state,
    bundle, configs) -> (assessment, route)` in shape only -- this module
    never imports or references the real class.

    Returns a plain dict (consistent with every other Protocol in this
    module) carrying AT LEAST a `"route"` key whose value is one of
    `VALID_ROUTES` (`"NORMAL"`, `"EMERGENCY"`, `"UNKNOWN_INVALID"`) --
    the EXACT decision the real router produced, never inferred
    after the fact from which optimizer subsequently ran. Implementations
    may carry additional keys (e.g. a reference to the real
    `EmergencyAssessment` object, for an `EMERGENCY`-route optimizer
    implementation that needs it) -- `execute_origin_dispatch_cell` passes
    this dict's contents through to the optimizer call untouched.
    """

    def evaluate_and_route(
        self, state: Dict[str, Any], forecast: Dict[str, Any], controller_settings: MatchedControllerSettings
    ) -> Dict[str, Any]:
        ...


@runtime_checkable
class SimulationStepperProtocol(Protocol):
    """
    Structural contract for advancing one simulated step given a dispatch
    plan. Mirrors `DigitalTwinSimulator`'s per-step stepping in shape only --
    this module never imports or references the real class.
    """

    def step(self, state: Dict[str, Any], dispatch_plan: Dict[str, Any]) -> Dict[str, Any]:
        ...


@runtime_checkable
class SafetyEvaluatorProtocol(Protocol):
    """
    Structural contract for a post-hoc safety evaluation of the final
    dispatch outcome. Mirrors `reserve_policy_guard.evaluate_dispatch_safety`
    in shape only -- this module never imports or calls the real function
    through this protocol; a caller who wants the real check must call it
    themselves and pass the already-computed `SafetyEvaluationResult` to
    `record_origin_outcome` directly (as this function already does).
    """

    def evaluate_dispatch_safety(self, dispatch_outcome: Dict[str, Any]) -> Optional[SafetyEvaluationResult]:
        ...


def execute_origin_dispatch_cell(
    origin: str,
    arm: str,
    scenario: ScenarioSpec,
    expected_steps: int,
    initial_state: Dict[str, Any],
    forecast_provider: ForecastProviderProtocol,
    optimizer: DispatchOptimizerProtocol,
    simulator: SimulationStepperProtocol,
    safety_evaluator: Optional[SafetyEvaluatorProtocol],
    provenance: Dict[str, Any],
    router: Optional[RouterProtocol] = None,
) -> OriginRunResult:
    """
    Generalized, DEPENDENCY-INJECTED per-origin, per-arm dispatch-cell loop.

    Generalizes `run_n6_closed_loop_simulation.py`'s existing single-origin
    call sequence (forecast -> optimize -> simulate -> safety-evaluate) across
    an arbitrary `origin` and `arm in {"baseline", "candidate"}`, exactly as
    `ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Table row 2 and
    `forecasting/n6/reports/N6_MULTI_ORIGIN_HARNESS_REPORT.md` Section 7 identified as the remaining
    engineering gap. It does this WITHOUT importing, constructing, or
    referencing any real `N6SolarForecastEngine`, `GAP19HighsNativeOptimizer`,
    `DigitalTwinSimulator`, or `EMSControlRouter` -- the caller supplies
    `forecast_provider`/`optimizer`/`simulator`/`safety_evaluator`/`router` as
    already-constructed objects satisfying the five `*Protocol` contracts
    above.

    GOVERNANCE, READ BEFORE CALLING WITH ANYTHING OTHER THAN A TEST DOUBLE:
    this function is exercised in `system/tests/test_n6_multi_origin_harness.py`
    EXCLUSIVELY against small Fake/Mock objects returning synthetic, hand
    -built values. It is not called by `MultiOriginCampaignHarness` or by
    `execute_campaign` anywhere in this module -- the campaign-level
    `CampaignExecutionNotAuthorizedError` gate is untouched by this function's
    existence. Supplying a REAL production forecast engine / optimizer /
    simulator / router here and invoking this function would itself be a
    dispatch evaluation / replay-equivalent simulation, and requires the same
    separate, explicit campaign-execution authorization `execute_campaign`
    is gated behind (see `forecasting/n6/reports/N6_MULTI_ORIGIN_HARNESS_REPORT.md` Section 6 and
    `forecasting/n6/reports/N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md` Workstream 2). This
    function's existence does not grant, imply, or create that authorization,
    and no code in this repository calls it with a real production object.

    IA-2 (owner decision, this pass): `router` is OPTIONAL and defaults to
    `None`, so every pre-existing caller that does not pass it keeps running
    exactly as before (unchanged four-component call shape, `OriginRunResult.
    route` stays `None`) -- this is an additive, backward-compatible change,
    not a breaking one. When `router` IS supplied, it is called once per
    step, immediately before `optimizer.optimize`, exactly where
    `worker.py`/`runner.py`/`run_n6_closed_loop_simulation.py` call
    `EMSControlRouter.evaluate_and_route` (see module docstring's IA-1/IA-2
    citations) -- its returned `"route"` is (a) validated against
    `VALID_ROUTES`, fail-closed on anything else; (b) threaded into the
    `forecast` dict passed to `optimizer.optimize` under the same `"route"`
    key (and any other key the router returned, e.g. a real
    `EmergencyAssessment` reference under `"_real_assessment_ref"`) so a
    route-branching optimizer adapter can act on it without this function
    needing to know what `EMERGENCY` handling looks like; and (c) appended to
    `route_history`, the per-step record `record_origin_outcome` attaches to
    the resulting `OriginRunResult` -- this is what lets route provenance be
    reconstructed per step for a receding-horizon run where the route can
    legitimately differ step to step, not just once per origin. A route of
    `"UNKNOWN_INVALID"` halts the loop immediately, BEFORE `optimizer.optimize`
    is called for that step -- mirroring `worker.py`'s Cell B
    `else: status = "FAILED_UNKNOWN_INVALID"; break` branch exactly -- and is
    recorded as `OriginRunStatus.FAILED_UNKNOWN_INVALID`, never as a generic
    `INCOMPLETE_RUN` or silently coerced into `NORMAL`.

    StationState handoff (Section 5 of `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md`):
    the `context` dict passed to `forecast_provider.predict` now includes a
    `"state"` key holding THIS function's own already-tracked `state` dict
    (the same dict `simulator.step`'s return value updates every iteration)
    -- the documented, authoritative-for-THIS-LOOP source, since it is
    exactly the simulated state `initial_state` seeded and every subsequent
    `simulator.step` call advanced. This closes the previously-documented
    mechanical interface gap (`N6ForecastProviderAdapter.predict` could not
    previously read `context.get("state")` because the key did not exist at
    all). It does NOT, by itself, close the deeper evidence gap: `initial_state`
    itself must still come from an authoritative, cited per-origin source --
    this function still invents nothing and still has no opinion on where
    `initial_state` came from; the caller-side translation layer's
    `resolve_authoritative_initial_state` / `AuthoritativeInitialStateUnavailableError`
    is where that fail-closed boundary remains, deliberately kept outside
    this module (this file is never imported by, and never imports, that
    translation layer).

    Fail-closed behavior (reusing `record_origin_outcome`'s existing rules,
    not duplicating them):
    - Any exception raised by `forecast_provider.predict`, `router.evaluate_and_route`,
      `optimizer.optimize`, or `simulator.step` is caught, recorded as
      `OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION`, and stops the loop
      immediately (`completed_steps` reflects exactly how many full steps
      finished before the exception).
    - If `simulator.step`'s returned dict sets `"stop_early": True` before
      `expected_steps` is reached (e.g. representing a worker/solver exit),
      the loop stops there with no exception synthesized; `record_origin_outcome`
      classifies the resulting `completed_steps < expected_steps` as
      `INCOMPLETE_RUN` (or `FAILED_WORKER_EXIT` if the last dispatch outcome's
      `constraint_status` is non-`OPTIMAL`), exactly as it already does for
      any other caller.
    - `safety_evaluator`, if supplied, is now consulted after EVERY
      completed step (immediately after that step's `simulator.step` call
      produces a dispatch outcome), not only once after the loop ends.
      **OWNER-AUTHORIZED BLOCKER RESOLUTION PASS (2026-10-17):** this
      resolves `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md` Section 6 blocker F
      ("safety is evaluated once per run, not once per step") WITHIN this
      isolated, fakes-only harness, mirroring `worker.py`'s real per-step
      Cell B cadence in STRUCTURE only (evaluate after every step, not just
      the last) -- it does not call, wrap, read, or modify
      `worker.py`/`runner.py`/`reserve_policy_guard.evaluate_dispatch_safety`
      itself, does not add any new safety threshold, and does not change any
      production control flow. Every per-step result (or `None`, if that
      step produced no dispatch outcome) is appended, in order, to
      `OriginRunResult.step_safety_evaluations` -- see
      `summarize_step_safety_evaluations` for a pure aggregate view. If
      `safety_evaluator` is `None`, `step_safety_evaluations` stays `()` and
      the resulting `OriginRunResult.safety_evidence_status` is
      `SAFETY_EVIDENCE_UNKNOWN`, never a pass -- this function does not
      change that rule. The pre-existing single-verdict
      `safety_evidence_status`/`safety_passed` fields are UNCHANGED in
      meaning and in value for every pre-existing caller: they still carry
      exactly the LAST completed step's evaluation (now taken from
      `step_safety_evaluations[-1]`, which equals what the single
      end-of-loop call used to compute from the same evaluator and the same
      final dispatch outcome -- not a second, independently-derived value),
      and still collapse to `SAFETY_EVIDENCE_UNKNOWN`/`None` whenever the
      loop ended in an exception, exactly as before. A matching call
      sequence for forecast/route/optimize was already in place; this
      change additionally makes the per-step safety-evaluation CADENCE
      match it, for the subset of information (`step_safety_evaluations`)
      this harness newly exposes.
    - A missing `diesel_consumed_liters`/`critical_unmet_load_wh`/
      `total_unmet_load_wh` key in the final dispatch outcome is recorded as
      `None` by `record_origin_outcome`, never coerced to `0.0`.
    """
    completed_steps = 0
    exception_message: Optional[str] = None
    last_dispatch_outcome: Optional[Dict[str, Any]] = None
    state: Dict[str, Any] = dict(initial_state)
    # Only ever appended to AFTER a route is validated against VALID_ROUTES
    # (below) -- so route_history[-1], if non-empty, is always a value
    # OriginRunResult.__post_init__ will accept, and the final `route`
    # recorded is simply its last entry (never a separately-tracked value
    # that could silently drift from, or survive past, an invalid/aborted
    # step). Stays `[]` for the entire run when `router is None`.
    route_history: List[str] = []
    # Per-step safety-evaluation sequence (blocker F fix, see function
    # docstring). Appended to ONLY when `safety_evaluator is not None`, so
    # it stays `[]` (never padded with Nones) for a router-less/evaluator-
    # less caller -- identical "no evidence at all" semantics as before.
    step_safety_evaluations: List[Optional[SafetyEvaluationResult]] = []

    all_step_solver_statuses: List[str] = []
    all_step_unmet_essential_wh: List[float] = []
    has_solver_failure: bool = False
    has_unmet_essential: bool = False
    has_fuel_failure: bool = False
    fuel_failure_reason: Optional[str] = None

    # Check for pre-existing latched failure in state
    if state.get("_has_fuel_failure", False) or state.get("_diesel_fuel_tracking_gap", False):
        has_fuel_failure = True
        fuel_failure_reason = state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"

    try:
        for step_index in range(expected_steps):
            # After any latched safety or execution failure, prevent subsequent optimizer and simulator calls
            if has_solver_failure or has_fuel_failure or has_unmet_essential:
                break
            if step_safety_evaluations and step_safety_evaluations[-1] is not None and not step_safety_evaluations[-1].passed:
                break
            if state.get("_has_fuel_failure", False) or state.get("_diesel_fuel_tracking_gap", False):
                has_fuel_failure = True
                fuel_failure_reason = state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"
                break

            forecast = forecast_provider.predict(
                origin,
                step_index,
                {"scenario_key": scenario.scenario_key, "arm": arm, "state": state},
            )

            if router is not None:
                route_result = router.evaluate_and_route(
                    state=state, forecast=forecast, controller_settings=scenario.controller_settings
                )
                step_route = route_result.get("route")
                if step_route not in VALID_ROUTES:
                    raise ValueError(
                        f"Fail-closed: router returned unrecognized route '{step_route}' for origin "
                        f"'{origin}' at step {step_index} -- must be one of {sorted(VALID_ROUTES)}."
                    )
                route_history.append(step_route)
                if step_route == "UNKNOWN_INVALID":
                    # Mirrors worker.py's Cell B fail-closed branch: halt
                    # BEFORE optimizer.optimize is ever called this step.
                    # completed_steps correctly does NOT increment for this
                    # step -- no plan was computed or applied.
                    break
                forecast = dict(forecast)
                for key, value in route_result.items():
                    if key != "route":
                        forecast[key] = value
                forecast["route"] = step_route

            plan = optimizer.optimize(
                state=state, forecast=forecast, controller_settings=scenario.controller_settings
            )

            # Inspect optimizer solver status BEFORE calling simulator.step()
            step_solver_status = getattr(plan, "constraint_status", None)
            if step_solver_status is None and isinstance(plan, dict):
                step_solver_status = plan.get("constraint_status")
                if step_solver_status is None and "_real_plan_ref" in plan:
                    step_solver_status = getattr(plan["_real_plan_ref"], "constraint_status", None)

            step_solver_status_str = (
                str(step_solver_status) if (step_solver_status is not None and step_solver_status != "") else "None"
            )
            all_step_solver_statuses.append(step_solver_status_str)

            # If the status is missing, empty, or anything other than OPTIMAL, latch failure and abort
            # the origin's dispatch loop without executing that plan.
            if step_solver_status is None or step_solver_status == "" or step_solver_status_str != "OPTIMAL":
                has_solver_failure = True
                break

            step_result = simulator.step(state=state, dispatch_plan=plan)
            state = step_result.get("state", state)
            last_dispatch_outcome = step_result.get("dispatch_outcome")
            completed_steps += 1

            if last_dispatch_outcome is not None:
                crit_raw = last_dispatch_outcome.get("critical_unmet_load_wh")
                if crit_raw is not None:
                    is_crit_valid = (
                        not isinstance(crit_raw, bool)
                        and isinstance(crit_raw, (int, float))
                        and not math.isnan(crit_raw)
                        and not math.isinf(crit_raw)
                        and crit_raw >= 0.0
                    )
                    if is_crit_valid:
                        crit_val = float(crit_raw)
                        all_step_unmet_essential_wh.append(crit_val)
                        if crit_val > 1e-6:
                            has_unmet_essential = True
                    else:
                        # Non-None but invalid measurement (Boolean, non-numeric, non-finite, or negative)
                        # Never replace with 0.0, latch essential failure.
                        has_unmet_essential = True

                if last_dispatch_outcome.get("has_fuel_failure"):
                    has_fuel_failure = True
                    fuel_failure_reason = last_dispatch_outcome.get("fuel_failure_reason")

                tot_raw = last_dispatch_outcome.get("total_unmet_load_wh")
                if tot_raw is not None:
                    is_tot_valid = (
                        not isinstance(tot_raw, bool)
                        and isinstance(tot_raw, (int, float))
                        and not math.isnan(tot_raw)
                        and not math.isinf(tot_raw)
                        and tot_raw >= 0.0
                    )
                    if not is_tot_valid:
                        has_unmet_essential = True

            if state.get("_has_fuel_failure", False) or state.get("_diesel_fuel_tracking_gap", False):
                has_fuel_failure = True
                fuel_failure_reason = fuel_failure_reason or state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"

            # Blocker-F fix: evaluate safety for THIS step now, not only
            # once after the whole loop ends -- mirrors worker.py's
            # per-step Cell B cadence in structure only (see docstring).
            if safety_evaluator is not None:
                if last_dispatch_outcome is not None:
                    step_safety_evaluations.append(
                        safety_evaluator.evaluate_dispatch_safety(last_dispatch_outcome)
                    )
                else:
                    step_safety_evaluations.append(None)

            has_safety_fail = (
                step_safety_evaluations
                and step_safety_evaluations[-1] is not None
                and not step_safety_evaluations[-1].passed
            )
            # After any latched safety or execution failure, prevent subsequent optimizer and simulator calls
            if (
                has_solver_failure
                or has_fuel_failure
                or has_safety_fail
                or step_result.get("stop_early", False)
            ):
                break
    except Exception as exc:  # fail closed: never swallow silently, always record
        exception_message = f"{type(exc).__name__}: {exc}"

    # The pre-existing single-verdict field: UNKNOWN whenever the loop
    # raised (unchanged rule), else the LAST step's own evaluation --
    # already computed above, in-loop, as step_safety_evaluations[-1]; this
    # is the SAME value the prior single end-of-loop call would have
    # computed (same evaluator, same final dispatch outcome), not a second,
    # independently-derived one.
    safety_evaluation: Optional[SafetyEvaluationResult] = None
    if exception_message is None and step_safety_evaluations:
        safety_evaluation = step_safety_evaluations[-1]

    return record_origin_outcome(
        origin=origin,
        arm=arm,
        scenario_key=scenario.scenario_key,
        forecast_provider=scenario.forecast_provider,
        completed_steps=completed_steps,
        expected_steps=expected_steps,
        dispatch_outcome=last_dispatch_outcome,
        safety_evaluation=safety_evaluation,
        provenance=provenance,
        exception_message=exception_message,
        route=(route_history[-1] if route_history else None),
        route_history=tuple(route_history),
        step_safety_evaluations=tuple(step_safety_evaluations),
        has_solver_failure=has_solver_failure,
        has_unmet_essential=has_unmet_essential,
        has_fuel_failure=has_fuel_failure,
        fuel_failure_reason=fuel_failure_reason,
        all_step_solver_statuses=tuple(all_step_solver_statuses),
        all_step_unmet_essential_wh=tuple(all_step_unmet_essential_wh),
    )


def _canonicalize_data(obj: Any) -> Any:
    """Helper to convert nested data structures, lists, dicts, numpy/pandas types to a canonical serializable form."""
    if hasattr(obj, "to_dict"):
        return _canonicalize_data(obj.to_dict())
    if isinstance(obj, dict):
        return {str(k): _canonicalize_data(v) for k, v in sorted(obj.items(), key=lambda item: str(item[0]))}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_data(x) for x in obj]
    if isinstance(obj, float):
        if math.isnan(obj):
            return "NaN"
        if math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
        return round(obj, 8)
    if hasattr(obj, "item"):
        return _canonicalize_data(obj.item())
    return obj


def compute_canonical_realized_trajectory_hash(data: Any) -> str:
    """
    Computes a deterministic SHA-256 hash of realized trajectory data across an origin's dispatch steps.
    Used for parity enforcement between baseline and candidate arms (BLOCKER-PARITY-1).
    """
    canon = _canonicalize_data(data)
    encoded = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_canonical_non_solar_forecast_hash(data: Any) -> str:
    """
    Computes a deterministic SHA-256 hash of non-solar forecast data (demand, wind, etc.) across an origin.
    Used for parity enforcement between baseline and candidate arms (BLOCKER-PARITY-1).
    """
    canon = _canonicalize_data(data)
    encoded = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class PairedOriginComparisonResult:
    """
    Result of comparing matched baseline and candidate OriginRunResults for a single origin (BLOCKER-PARITY-1).
    Fails closed on any parity violation, solver failure, unmet load, or fuel tracking gap.
    """

    origin: str
    is_valid_comparison: bool
    status: str
    baseline_run_status: str
    candidate_run_status: str
    net_diesel_savings_liters: Optional[float]
    net_delta_e_term_wh: Optional[float]
    net_generator_starts: Optional[int]
    net_startup_surcharge_liters: Optional[float]
    winner: Optional[str] = None  # HARD GOVERNANCE: Always None. Execution is blocked.
    invalidation_reasons: Tuple[str, ...] = ()
    baseline_result: Optional[OriginRunResult] = None
    candidate_result: Optional[OriginRunResult] = None


def evaluate_paired_origin_comparison(
    baseline: OriginRunResult, candidate: OriginRunResult
) -> PairedOriginComparisonResult:
    """
    Evaluates a paired origin comparison between baseline and candidate arms under BLOCKER-PARITY-1.
    Enforces identical realized trajectories, non-solar forecasts, and resolved terminal targets.
    Latches all solver, unmet load, and fuel failures.
    Unconditionally sets winner to None (execution remains blocked).
    """
    invalidation_reasons: List[str] = []

    if baseline.origin != candidate.origin:
        invalidation_reasons.append(
            f"INVALID_PAIR_ORIGIN_MISMATCH: baseline origin '{baseline.origin}' != candidate origin '{candidate.origin}'"
        )
    if baseline.arm != "baseline" or candidate.arm != "candidate":
        invalidation_reasons.append(
            f"INVALID_PAIR_ARM_MISMATCH: expected baseline/candidate, got '{baseline.arm}'/'{candidate.arm}'"
        )

    # Parity checks
    if baseline.realized_trajectory_hash is None or candidate.realized_trajectory_hash is None:
        invalidation_reasons.append("INVALID_PAIR_MISSING_TRAJECTORY_HASH")
    elif baseline.realized_trajectory_hash != candidate.realized_trajectory_hash:
        invalidation_reasons.append(
            f"INVALID_PAIR_TRAJECTORY_MISMATCH: baseline={baseline.realized_trajectory_hash} != candidate={candidate.realized_trajectory_hash}"
        )

    if baseline.non_solar_forecast_hash is None or candidate.non_solar_forecast_hash is None:
        invalidation_reasons.append("INVALID_PAIR_MISSING_NON_SOLAR_FORECAST_HASH")
    elif baseline.non_solar_forecast_hash != candidate.non_solar_forecast_hash:
        invalidation_reasons.append(
            f"INVALID_PAIR_FORECAST_MISMATCH: baseline={baseline.non_solar_forecast_hash} != candidate={candidate.non_solar_forecast_hash}"
        )

    if baseline.resolved_terminal_target_wh is not None or candidate.resolved_terminal_target_wh is not None:
        if (
            baseline.resolved_terminal_target_wh is None
            or candidate.resolved_terminal_target_wh is None
            or abs(baseline.resolved_terminal_target_wh - candidate.resolved_terminal_target_wh) > 1e-4
        ):
            invalidation_reasons.append(
                f"INVALID_PAIR_TERMINAL_TARGET_MISMATCH: baseline={baseline.resolved_terminal_target_wh} != candidate={candidate.resolved_terminal_target_wh}"
            )

    if baseline.resolved_ebr_target_wh is not None or candidate.resolved_ebr_target_wh is not None:
        if (
            baseline.resolved_ebr_target_wh is None
            or candidate.resolved_ebr_target_wh is None
            or len(baseline.resolved_ebr_target_wh) != len(candidate.resolved_ebr_target_wh)
            or any(abs(b - c) > 1e-4 for b, c in zip(baseline.resolved_ebr_target_wh, candidate.resolved_ebr_target_wh))
        ):
            invalidation_reasons.append("INVALID_PAIR_EBR_TARGET_MISMATCH")

    # Run status & completion checks
    if baseline.completed_steps < baseline.expected_steps or candidate.completed_steps < candidate.expected_steps:
        invalidation_reasons.append(
            f"INVALID_PAIR_INCOMPLETE_RUN: baseline={baseline.completed_steps}/{baseline.expected_steps}, candidate={candidate.completed_steps}/{candidate.expected_steps}"
        )

    if baseline.run_status != OriginRunStatus.OPTIMAL or candidate.run_status != OriginRunStatus.OPTIMAL:
        invalidation_reasons.append(
            f"INVALID_PAIR_NON_OPTIMAL_STATUS: baseline={baseline.run_status}, candidate={candidate.run_status}"
        )

    # Solver failures
    if baseline.has_solver_failure or candidate.has_solver_failure:
        invalidation_reasons.append("INVALID_PAIR_SOLVER_FAILURE")

    # Unmet essential load & total unmet load
    if baseline.has_unmet_essential or candidate.has_unmet_essential:
        invalidation_reasons.append("INVALID_PAIR_UNMET_ESSENTIAL_LOAD")
    if (
        (baseline.critical_unmet_load_wh is not None and baseline.critical_unmet_load_wh > 1e-6)
        or (candidate.critical_unmet_load_wh is not None and candidate.critical_unmet_load_wh > 1e-6)
    ):
        invalidation_reasons.append("INVALID_PAIR_CRITICAL_UNMET_LOAD_POSITIVE")
    if (
        (baseline.total_unmet_load_wh is not None and baseline.total_unmet_load_wh > 1e-6)
        or (candidate.total_unmet_load_wh is not None and candidate.total_unmet_load_wh > 1e-6)
    ):
        invalidation_reasons.append("INVALID_PAIR_TOTAL_UNMET_LOAD_POSITIVE")

    # Safety failures
    if baseline.safety_passed is False or candidate.safety_passed is False:
        invalidation_reasons.append("INVALID_PAIR_SAFETY_FAILURE")

    # Fuel failures
    if baseline.has_fuel_failure or candidate.has_fuel_failure:
        invalidation_reasons.append(
            f"INVALID_PAIR_FUEL_FAILURE: baseline_reason={baseline.fuel_failure_reason}, candidate_reason={candidate.fuel_failure_reason}"
        )
    if baseline.diesel_fuel_tracking_gap or candidate.diesel_fuel_tracking_gap:
        invalidation_reasons.append("INVALID_PAIR_DIESEL_FUEL_TRACKING_GAP")
    if baseline.diesel_consumed_liters is None or candidate.diesel_consumed_liters is None:
        invalidation_reasons.append("INVALID_PAIR_MISSING_DIESEL_CONSUMED")

    # Strict validation of all 8 required metrics on both arms
    for arm_name, arm_result in [("baseline", baseline), ("candidate", candidate)]:
        for metric_name, non_neg, check_soc, check_int in [
            ("diesel_consumed_liters", True, False, False),
            ("delta_e_term_wh", False, False, False),
            ("initial_battery_energy_wh", True, False, False),
            ("terminal_battery_energy_wh", True, False, False),
            ("initial_battery_soc_pct", True, True, False),
            ("terminal_battery_soc_pct", True, True, False),
            ("generator_starts", True, False, True),
            ("startup_surcharge_liters", True, False, False),
        ]:
            val = getattr(arm_result, metric_name, None)
            if val is None:
                invalidation_reasons.append(
                    f"INVALID_PAIR_MISSING_TERMINAL_METRIC: {arm_name}.{metric_name} is None"
                )
            elif isinstance(val, bool) or not isinstance(val, (int, float)):
                invalidation_reasons.append(
                    f"INVALID_PAIR_MALFORMED_TERMINAL_METRIC: {arm_name}.{metric_name} must be numeric, got {type(val).__name__} ({val!r})"
                )
            elif math.isnan(val) or math.isinf(val):
                invalidation_reasons.append(
                    f"INVALID_PAIR_MALFORMED_TERMINAL_METRIC: {arm_name}.{metric_name} cannot be NaN or Inf, got {val}"
                )
            elif non_neg and val < 0.0:
                invalidation_reasons.append(
                    f"INVALID_PAIR_MALFORMED_TERMINAL_METRIC: {arm_name}.{metric_name} cannot be negative, got {val}"
                )
            elif check_soc and val > 100.0:
                invalidation_reasons.append(
                    f"INVALID_PAIR_MALFORMED_TERMINAL_METRIC: {arm_name}.{metric_name} cannot exceed 100.0%, got {val}"
                )
            elif check_int and (isinstance(val, float) and not val.is_integer()):
                invalidation_reasons.append(
                    f"INVALID_PAIR_MALFORMED_TERMINAL_METRIC: {arm_name}.{metric_name} must be an integer count, got {val}"
                )

    # Safety evaluation
    if (
        baseline.safety_evidence_status != SAFETY_EVIDENCE_VERIFIED
        or candidate.safety_evidence_status != SAFETY_EVIDENCE_VERIFIED
        or not baseline.safety_passed
        or not candidate.safety_passed
    ):
        invalidation_reasons.append("INVALID_PAIR_SAFETY_FAILURE")

    is_valid = len(invalidation_reasons) == 0

    if not is_valid:
        return PairedOriginComparisonResult(
            origin=baseline.origin,
            is_valid_comparison=False,
            status=invalidation_reasons[0].split(":")[0],
            baseline_run_status=baseline.run_status,
            candidate_run_status=candidate.run_status,
            net_diesel_savings_liters=None,
            net_delta_e_term_wh=None,
            net_generator_starts=None,
            net_startup_surcharge_liters=None,
            winner=None,
            invalidation_reasons=tuple(invalidation_reasons),
            baseline_result=baseline,
            candidate_result=candidate,
        )

    # Valid comparison (no fallback to 0.0 or 0 -- all metrics guaranteed present and valid above)
    net_diesel = baseline.diesel_consumed_liters - candidate.diesel_consumed_liters
    net_delta_e = candidate.delta_e_term_wh - baseline.delta_e_term_wh
    net_starts = candidate.generator_starts - baseline.generator_starts
    net_surcharge = baseline.startup_surcharge_liters - candidate.startup_surcharge_liters

    return PairedOriginComparisonResult(
        origin=baseline.origin,
        is_valid_comparison=True,
        status="VALID_MATCHED_PAIR",
        baseline_run_status=baseline.run_status,
        candidate_run_status=candidate.run_status,
        net_diesel_savings_liters=net_diesel,
        net_delta_e_term_wh=net_delta_e,
        net_generator_starts=net_starts,
        net_startup_surcharge_liters=net_surcharge,
        winner=None,  # HARD CONSTRAINT: winner is always None
        invalidation_reasons=(),
        baseline_result=baseline,
        candidate_result=candidate,
    )
