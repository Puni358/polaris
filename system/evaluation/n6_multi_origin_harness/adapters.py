"""
POLARIS -- N6 Multi-Origin Harness: Production-Adapter Interface Mapping
=============================================================================
Resolves `forecasting/n6/reports/N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md` blocker 2 /
`forecasting/n6/reports/N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` Workstream 2: documents, and
provides translation-only adapter classes for, the EXACT interface gap
between `harness.py`'s four structural `typing.Protocol` contracts
(`ForecastProviderProtocol` / `DispatchOptimizerProtocol` /
`SimulationStepperProtocol` / `SafetyEvaluatorProtocol`) and the real
production classes those Protocols are modeled on, as confirmed by direct
read of the one existing real single-origin integration,
`forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/
run_n6_closed_loop_simulation.py`, this pass.

GOVERNANCE STATUS: NON-PRODUCTION / NOT EXECUTED / NO NEW EXECUTION PATH
-------------------------------------------------------------------------
- This module imports NOTHING from `system.forecasting.implementations.n6_solar`,
  `system.control.router`, `system.optimization.implementations.gap19_highs_native`,
  `system.simulation.simulator`, or `system.safety.reserve_policy_guard` AT RUNTIME.
  Real-class names appear ONLY inside a `typing.TYPE_CHECKING` guard, purely for
  static type-checker hints, and are never evaluated when this module is imported
  or executed. This is a deliberate choice, not an oversight: it keeps this module
  importable, and its adapters constructible, without ever loading a frozen model
  artifact or constructing a real optimizer/simulator/router, so that nothing in
  this module can accidentally become a dispatch evaluation.
- Every adapter class below is a pure TRANSLATION layer: it takes an
  already-constructed object (injected by the caller, typed `Any` at runtime)
  that is assumed to expose the real class's method signature, and re-shapes
  calls/returns to satisfy `harness.py`'s Protocol method signature, or vice
  versa. No adapter here constructs, imports, or calls a real production
  object anywhere in this module or in its tests
  (`system/tests/test_n6_multi_origin_harness_adapters.py`) -- every test in
  that file injects a hand-built Fake whose shape mirrors the REAL class's
  documented call signature (confirmed against `run_n6_closed_loop_simulation.py`
  by direct read this pass), never a real engine/optimizer/simulator/evaluator.
- NONE of these adapters is imported by, registered with, or reachable from
  `MultiOriginCampaignHarness`, `execute_campaign`, or `execute_origin_dispatch_cell`
  anywhere in this repository. Wiring one of these adapters around a REAL
  production object and passing it into `execute_origin_dispatch_cell` would
  itself constitute a dispatch evaluation / replay-equivalent simulation and
  requires the same campaign-execution authorization `execute_campaign` is
  gated behind (`system/evaluation/replay_harness.py`'s unconditional
  `CampaignExecutionNotAuthorizedError`) -- this module's existence grants,
  implies, or bypasses none of that.

WHY THIS MODULE EXISTS (what it resolves, and what it deliberately does NOT)
-------------------------------------------------------------------------------
`forecasting/n6/reports/N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md` blocker 2 asked: "what are
the exact interfaces and compatibility requirements for real N6, GAP19/router,
simulator and safety-evaluator adapters?" Direct re-read of
`run_n6_closed_loop_simulation.py` this pass (the ONLY existing real
single-origin integration; FOR-02 confirmed no other integration beyond
`n6_operational_pipeline.py`, not re-read line-by-line this pass since FOR-02
already audited it) surfaces the real call shapes:

    n6_bundle   = N6SolarForecastEngine().predict(station_state, context_dict)
                  -> ForecastBundle (24-hour, schema_version "1.0.0")
    assessment, route = EMSControlRouter().evaluate_and_route(station_state, bundle, configs)
                  -> (assessment_obj, route: "NORMAL"|other)
    plan        = GAP19HighsNativeOptimizer().optimize(bundle, station_state, configs)
                  -> DispatchPlan (one call, ALL 24 hours at once)
    next_state  = DigitalTwinSimulator(configs).step(station_state, one_hour_slice_of(plan), actual_t)
                  -> StationState (one call PER HOUR, slicing the single 24h plan)
    safety      = reserve_policy_guard.evaluate_dispatch_safety(plan_dict, min_e_wh, reserve_shortfall_authorization_wh)
                  -> SafetyEvaluationResult

Compare this to `harness.py`'s `execute_origin_dispatch_cell` loop, which
calls `optimizer.optimize(...)` ONCE PER STEP, inside the same `for step_index
in range(expected_steps)` loop that also calls `simulator.step(...)`:

    for step_index in range(expected_steps):
        forecast = forecast_provider.predict(origin, step_index, context)
        plan     = optimizer.optimize(state=state, forecast=forecast, controller_settings=...)
        step_result = simulator.step(state=state, dispatch_plan=plan)
        ...

**THE SINGLE MOST IMPORTANT INTEGRATION-ASSUMPTION GAP THIS MODULE SURFACES**
(not resolved by this module -- see `IntegrationAssumption` list below):
`execute_origin_dispatch_cell`'s loop structure assumes a RECEDING-HORIZON
control strategy (re-optimize from scratch every single simulated step).
The only real integration that exists today (`run_n6_closed_loop_simulation.py`)
instead optimizes ONCE for the full 24-hour horizon and then only STEPS the
simulator 24 times across 1-hour slices of that one plan -- it never calls
the optimizer a second time within the same horizon. These are two
substantively different control strategies with different computational
cost, different GAP19 solve counts, and (most importantly) NEVER-VALIDATED
behavior for the receding-horizon variant -- no document, test, or script in
this repository has ever run GAP19 in a per-step replanning loop. Resolving
this is a design decision (fold the real single-shot-plan-then-slice pattern
into the `DispatchOptimizerProtocol`/`SimulationStepperProtocol` adapters
below so the FIRST call to `optimizer.optimize` produces and caches a full
plan while subsequent calls return cached per-step slices; OR revise
`harness.py`'s loop structure itself to call `optimize` once per scenario
instead of once per step), and this module does NOT make that decision --
it documents it as the first entry in `INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW`
below and implements ONLY the "cache a single plan, slice it per step" variant,
because that is the ONLY pattern this repository has ever actually exercised
(even then, only in a single real smoke run, never a campaign). A caller who
wants the untested receding-horizon variant must build a different adapter;
this module does not provide one, to avoid silently presenting an
unvalidated control strategy as equivalent to the real integration.

Four more concrete, smaller gaps the adapters below must translate across
(each independently confirmed by direct read of `run_n6_closed_loop_simulation.py`
and the Protocol definitions in `harness.py`, this pass):

1. **State representation.** Real: `StationState` (typed object,
   `.to_dict()`/`.from_dict()`). Harness Protocol: plain `Dict[str, Any]`.
   `StationStateCodec` below translates both directions, using ONLY
   `StationState`'s own already-existing `to_dict`/`from_dict` methods --
   it does not reimplement StationState's field validation.
2. **Forecast representation.** Real: `ForecastBundle` (typed object with
   `.solar_irradiance`/`.demand`/`.metadata` sub-objects, each a
   `TimeseriesForecast` with `.point`/`.lower`/`.upper` per-hour lists).
   Harness Protocol: plain `Dict[str, Any]` returned once per step (a single
   step's forecast, not a 24-hour bundle). `ForecastBundleStepView` below
   extracts one step's values from an already-produced `ForecastBundle`
   without re-deriving or forecasting anything itself.
3. **Router step is unrepresented.** The real sequence has FIVE real
   components (forecast engine, router, optimizer, simulator, safety
   evaluator); `harness.py`'s Protocols have FOUR slots (no
   `RouterProtocol`). `RoutedOptimizerAdapter` below folds
   `EMSControlRouter.evaluate_and_route` into the SAME adapter object that
   implements `DispatchOptimizerProtocol.optimize`, calling the router
   first and recording its `route` decision into the returned plan dict's
   `"route"` key (never silently dropped) -- this is a design choice this
   module makes explicitly and documents, not an upstream harness.py change
   (which this pass's boundaries do not authorize making unilaterally,
   since `harness.py`'s own Protocol shape is part of what a prior pass
   already built and tested; changing it is a separate, reviewable
   decision, listed below, not made here).
4. **DispatchPlan is a validated, fixed-24-length object.** Real:
   `DispatchPlan.__init__` RAISES if any field list is not exactly length 24
   or contains a non-finite/negative value (see `system/schemas/dispatch_plan.py`
   lines ~36-52, read this pass). A per-step slice (as
   `run_n6_closed_loop_simulation.py` builds it, lines ~201-217: every field
   repeated as `[plan.field[t]] * 24`) is itself a full, valid 24-entry
   `DispatchPlan` whose 24 entries all equal the single hour's value --
   this is the REAL script's own undocumented convention, confirmed by
   direct read, not invented by this module. `DispatchOutcomeView` below
   extracts the single scalar value any given hour actually needs
   (`diesel_power[t]`, `unmet_load[t]`, `constraint_status`, etc.) from
   either a full plan or a single-hour-repeated slice, since both shapes
   are structurally identical 24-tuples under this convention.

Everything below is pure, dependency-free translation code: no file I/O, no
network access, no sealed-path access, no hashing, no randomness. It is
exercised exclusively against hand-built Fakes in
`system/tests/test_n6_multi_origin_harness_adapters.py`.
"""
from __future__ import annotations

import copy
import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, TYPE_CHECKING, runtime_checkable

import pandas as pd

from system.evaluation.n6_multi_origin_harness.harness import (
    VALID_ROUTES,
    DispatchOptimizerProtocol,
    ForecastProviderProtocol,
    SafetyEvaluatorProtocol,
    SimulationStepperProtocol,
)
from system.evaluation.n6_multi_origin_harness.realized_loader import (
    CANONICAL_FIXTURE_RELATIVE_PATH,
    load_authoritative_actuals_by_origin,
)

if TYPE_CHECKING:
    # Type-checking-only references to the real production classes. These
    # names are NEVER evaluated at runtime (no module-level import of any
    # of these modules exists in this file) -- see the module docstring's
    # GOVERNANCE STATUS section for why. Adapters below type their injected
    # collaborators as `Any` at runtime for exactly this reason.
    from system.control.router import EMSControlRouter  # noqa: F401
    from system.forecasting.implementations.n6_solar import N6SolarForecastEngine  # noqa: F401
    from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer  # noqa: F401
    from system.safety import reserve_policy_guard as _reserve_policy_guard_module  # noqa: F401
    from system.schemas.dispatch_plan import DispatchPlan  # noqa: F401
    from system.schemas.forecast_bundle import ForecastBundle  # noqa: F401
    from system.schemas.station_state import StationState  # noqa: F401
    from system.simulation.simulator import DigitalTwinSimulator  # noqa: F401

__all__ = [
    "IntegrationAssumption",
    "INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW",
    "AuthoritativeInitialStateUnavailableError",
    "MalformedInitialStateRecordError",
    "REQUIRED_STATION_STATE_FIELDS",
    "PROVENANCE_FIELD",
    "resolve_authoritative_initial_state",
    "resolve_and_validate_authoritative_initial_state",
    "StationStateCodec",
    "ForecastBundleStepView",
    "DispatchOutcomeView",
    "N6ForecastProviderAdapter",
    "RoutedOptimizerAdapter",
    "SingleShotPlanSlicingSimulatorAdapter",
    "ReservePolicyGuardSafetyEvaluatorAdapter",
    "N6RecedingHorizonForecastAdapter",
    "N6RecedingHorizonRouterAdapter",
    "N6RecedingHorizonOptimizerAdapter",
    "RecedingHorizonPlanSlicingSimulatorAdapter",
    "_prepare_gap19_terminal_target_config",
    "_prepare_gap19_policy_b_config",
    "_compute_gap19_six_hour_critical_reserve",
    "_extract_and_validate_demands",
    "_validate_conformal_ebr",
    "_align_timeseries_od02",
    "_align_n6_bundle_od02",
    "_compute_boundary_clearsky_ratio",
]


@dataclass(frozen=True)
class IntegrationAssumption:
    """
    One documented, NOT-YET-RESOLVED assumption this adapter layer makes or
    exposes, which `forecasting/n6/reports/N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` Workstream 2
    requires be explicitly identified as "still requiring an authorized
    smoke test" before any real object is ever wired through these adapters.
    """

    id: str
    assumption: str
    why_unresolved: str
    required_before_real_use: str


INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW: List[IntegrationAssumption] = [
    IntegrationAssumption(
        id="IA-1",
        assumption=(
            "DECIDED AND IMPLEMENTED THIS PASS (forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 1): the "
            "owner decided the production-representative N6-vs-baseline comparison must use "
            "RECEDING-HORIZON control (re-forecast/re-route/re-optimize fresh every simulated "
            "step), matching `worker.py`'s Cell B loop and `runner.py`'s live runtime structurally, "
            "NOT the single-shot-plan-then-slice pattern `run_n6_closed_loop_simulation.py` "
            "happens to use. `N6RecedingHorizonForecastAdapter` / `N6RecedingHorizonRouterAdapter` / "
            "`N6RecedingHorizonOptimizerAdapter` / `RecedingHorizonPlanSlicingSimulatorAdapter` "
            "below implement this variant -- each calls its real collaborator fresh every step, "
            "with NO caching across steps (the opposite of `N6ForecastProviderAdapter`/"
            "`RoutedOptimizerAdapter`/`SingleShotPlanSlicingSimulatorAdapter` above, which remain "
            "unmodified and still implement single-shot-then-slice for whichever caller still "
            "wants that variant)."
        ),
        why_unresolved=(
            "RESOLVED AS A DESIGN/ENGINEERING MATTER this pass -- fakes-only tests in "
            "`system/tests/test_n6_receding_horizon_adapters.py` lock in the call-sequence/cadence "
            "this decision implies. STILL UNRESOLVED: no real GAP19/router/N6 object has ever been "
            "run this way (receding-horizon, hourly N6 re-forecast) even once -- this pass builds "
            "and fake-tests the adapter layer ONLY; it never constructs or calls a real production "
            "object, per this pass's explicit boundaries. GAP19 convergence/latency/"
            "`constraint_status` stability under hourly N6 re-forecasting with REAL objects remains "
            "completely unvalidated."
        ),
        required_before_real_use=(
            "A separately authorized real-object smoke test (one real origin, receding-horizon, "
            "real N6/router/GAP19/simulator) is required before any multi-origin run -- this pass "
            "grants no such authorization and performs no such test. The campaign-execution "
            "authorization gate (blocker A) is a SEPARATE, also-still-missing prerequisite."
        ),
    ),
    IntegrationAssumption(
        id="IA-2",
        assumption=(
            "DECIDED AND IMPLEMENTED THIS PASS (forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 2): the "
            "owner decided to extend `harness.py` with a fifth `RouterProtocol` and an explicit "
            "`route` (+ `route_history`) field on `OriginRunResult`, rather than keep "
            "`EMSControlRouter.evaluate_and_route`'s decision folded silently into "
            "`DispatchOptimizerProtocol.optimize` (the ORIGINAL interim shape `RoutedOptimizerAdapter` "
            "above still implements, kept unmodified for callers still using the single-shot wiring)."
        ),
        why_unresolved=(
            "RESOLVED. `harness.py`'s `RouterProtocol`, `VALID_ROUTES`, `OriginRunStatus."
            "FAILED_UNKNOWN_INVALID`, and `OriginRunResult.route`/`route_history` are implemented "
            "and fake-tested this pass (42 pre-existing `harness.py` tests pass unchanged -- the "
            "new `router` parameter on `execute_origin_dispatch_cell` is optional/additive). The "
            "route is now recorded explicitly, never inferred after the fact, and is validated to "
            "never silently default or diverge from the per-step history it was computed from."
        ),
        required_before_real_use=(
            "No further design decision required. The remaining gap is the same one IA-1 names: "
            "no real router/optimizer pair has been run through this new slot with real objects; "
            "that still requires a separately authorized real-object smoke test."
        ),
    ),
    IntegrationAssumption(
        id="IA-3",
        assumption=(
            "Each origin's `initial_state` (battery SOC, diesel state, fuel remaining) would be "
            "supplied by the caller from an already-cited source per origin, exactly as "
            "`build_multi_origin_campaign_config`'s existing `initial_battery_soc_wh_by_origin` "
            "parameter already requires (ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md Table row 5) -- "
            "this adapter layer invents no initial condition for any origin."
        ),
        why_unresolved=(
            "No per-origin initial-state table for a multi-origin N6 comparison (123 origins or "
            "any other finite set) has been assembled anywhere in this repository; "
            "`run_n6_closed_loop_simulation.py` hand-constructs exactly one origin's initial "
            "state (lines ~101-112 of that script)."
        ),
        required_before_real_use=(
            "A concrete, cited, per-origin initial-state table must be assembled as part of the "
            "comparison specification (Workstream 3) before any real adapter use; this module "
            "does not and will not synthesize one."
        ),
    ),
    IntegrationAssumption(
        id="IA-4",
        assumption=(
            "`reserve_shortfall_authorization_wh` passed to "
            "`reserve_policy_guard.evaluate_dispatch_safety` stays `None` (the current production "
            "default at both existing call sites in `evaluator.py`/`worker.py`), so every "
            "reserve shortfall continues to report `AUTHORIZATION_REQUIRED`, never a silent pass."
        ),
        why_unresolved=(
            "SAF-03 (numeric reserve-shortfall ceiling) remains an explicit, deliberate owner "
            "deferral (register SAF-03, 'keep unset, pending further evidence') -- not a gap "
            "this module can or should close."
        ),
        required_before_real_use=(
            "No action required to proceed with `None` (the safe default); a non-`None` value "
            "would require the same owner decision SAF-03 is already waiting on, which this "
            "module does not invent, select, or imply."
        ),
    ),
]


class AuthoritativeInitialStateUnavailableError(Exception):
    """
    Raised by `resolve_authoritative_initial_state` when no authoritative,
    cited initial `StationState` evidence exists for an origin. This
    repository contains NO per-origin initial-state table anywhere (IA-3;
    confirmed absent again this pass by repository-wide search -- the only
    hand-built example, `run_n6_closed_loop_simulation.py` lines ~101-112,
    hardcodes literal constants -- `battery_soc_pct=80.0`,
    `battery_energy_wh=160000.0`, `diesel_fuel_remaining_liters=500.0` -- for
    ONE smoke-test origin, not a cited, generalizable source for any other
    origin). This function and this module NEVER invent, zero-fill, or
    impute a substitute when this error is the correct outcome.
    """


def resolve_authoritative_initial_state(
    origin: str, authoritative_initial_states_by_origin: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Looks up ORIGIN's initial `StationState`-shaped plain dict from a
    caller-supplied registry of ALREADY-CITED, authoritative per-origin
    initial states. This function builds, sources, or default-fills
    NOTHING itself -- it is a fail-closed lookup, not a state constructor.
    Raises `AuthoritativeInitialStateUnavailableError` (never returns a
    zero-filled/guessed dict) when `origin` is not present, naming the
    missing artifact in the message so a caller/operator knows exactly what
    evidence is missing (see `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md` Section 5 /
    Blocker B for the current, still-open status of this gap: as of this
    pass, NO caller anywhere in this repository supplies a non-empty
    `authoritative_initial_states_by_origin` for any real origin -- this
    function exists so that, if/when such a registry is ever assembled and
    cited, the adapters above can consume it without inventing anything in
    the interim).
    """
    if origin not in authoritative_initial_states_by_origin:
        raise AuthoritativeInitialStateUnavailableError(
            f"Fail-closed: no authoritative initial StationState evidence exists for origin "
            f"'{origin}'. This repository contains no per-origin initial-state artifact (IA-3) -- "
            "see forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md Section 5 / Blocker B. Supplying a zero-filled, "
            "guessed, or default StationState here would violate the directive's fail-closed "
            "requirement; the caller must supply a real, cited initial StationState record for "
            f"origin '{origin}' (battery SOC, diesel fuel remaining, demand/irradiance/wind "
            "observations at t0) from an authoritative source before this adapter chain can be "
            "used for anything beyond a fakes-only test."
        )
    return dict(authoritative_initial_states_by_origin[origin])


# OWNER-AUTHORIZED BLOCKER RESOLUTION PASS (2026-10-17), Section 3A: "Improve
# the initial-state interface so future verified station-state records can
# be supplied through a documented, validated input contract. Do not
# manufacture initial-state records or treat hardcoded smoke-test constants
# as authoritative evidence." The two names below are the EXACT required
# positional-argument names of the real `system.schemas.station_state.
# StationState.__init__`/`.from_dict` contract (confirmed by direct read of
# `system/schemas/station_state.py` this pass -- `StationState.from_dict`
# reads each of these 8 via `data["key"]`, with NO `.get(...)` default, so a
# real construction from an incomplete dict already raises `KeyError`;
# `PROVENANCE_FIELD` is new, added by this pass, so a record's SOURCE is
# machine-checkable, not merely assumed). Reused verbatim, never redefined
# or widened.
REQUIRED_STATION_STATE_FIELDS: Tuple[str, ...] = (
    "timestamp",
    "battery_soc_pct",
    "battery_energy_wh",
    "diesel_running",
    "diesel_hours_running",
    "last_observed_solar_irradiance",
    "last_observed_demand",
    "last_observed_wind_generation",
)

# A caller-supplied citation of WHERE this origin's initial state came from
# (e.g. "SITES telemetry log 2024-06-01T00:00:00Z, ingested 2024-06-01
# 00:04:12Z" or "owner-authorized per-origin initial-state table v1, row
# 42") -- required by `resolve_and_validate_authoritative_initial_state`
# below so a hardcoded smoke-test constant (which has no such citation,
# confirmed by direct read of `run_n6_closed_loop_simulation.py` lines
# ~101-112 -- `battery_soc_pct=80.0`, `battery_energy_wh=160000.0`, etc.,
# with no cited source anywhere in that script) can never be mistaken for,
# or silently promoted to, authoritative per-origin evidence.
PROVENANCE_FIELD = "_provenance"


class MalformedInitialStateRecordError(Exception):
    """
    Raised by `resolve_and_validate_authoritative_initial_state` when an
    origin's record EXISTS in the caller-supplied registry (so
    `AuthoritativeInitialStateUnavailableError` does not apply) but is
    missing one or more of `REQUIRED_STATION_STATE_FIELDS` or the
    `PROVENANCE_FIELD` citation. Distinguished deliberately from
    `AuthoritativeInitialStateUnavailableError` because the fail-closed
    reason differs: that error means "no evidence at all for this origin";
    this one means "evidence is present but incomplete or uncited, so it is
    not trustworthy enough to treat as authoritative."
    """


def resolve_and_validate_authoritative_initial_state(
    origin: str, authoritative_initial_states_by_origin: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    The NEW, STRICTER, DOCUMENTED entry point for supplying a future,
    genuinely verified per-origin `StationState` record (Section 3A of the
    2026-10-17 owner-authorized blocker-resolution pass). Delegates the
    missing-origin check to `resolve_authoritative_initial_state` above
    UNCHANGED (never duplicates that fail-closed rule), then additionally
    validates the returned record against `REQUIRED_STATION_STATE_FIELDS`
    (the real `StationState` contract, reused verbatim) and
    `PROVENANCE_FIELD` (new) before returning it.

    This function does NOT replace `resolve_authoritative_initial_state`,
    which remains available, unmodified, and still exercised by its own
    pre-existing tests (`system/tests/test_n6_receding_horizon_adapters.py`
    `TestAuthoritativeInitialStateLookup`) for callers who only need the
    bare fail-closed lookup. This function is the stricter contract a
    FUTURE caller assembling a real, citable per-origin initial-state table
    (IA-3, still otherwise unresolved -- see `INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW`
    above) should use instead, so that an incomplete or uncited record fails
    closed at the SAME lookup step, rather than surfacing later as a
    confusing `KeyError` inside a real `StationState.from_dict` call, or
    (worse) being silently accepted as "good enough."

    Raises `AuthoritativeInitialStateUnavailableError` (unchanged, from the
    delegated call) if `origin` is entirely absent, or
    `MalformedInitialStateRecordError` if the record exists but is missing
    required fields and/or a provenance citation. Never zero-fills, guesses,
    or otherwise invents a replacement value for any missing field --
    exactly like the function it wraps.
    """
    record = resolve_authoritative_initial_state(origin, authoritative_initial_states_by_origin)

    missing_fields = [f for f in REQUIRED_STATION_STATE_FIELDS if record.get(f) is None]
    if missing_fields:
        raise MalformedInitialStateRecordError(
            f"Fail-closed: initial-state record for origin '{origin}' is missing required "
            f"StationState field(s) {missing_fields} (or they are explicitly None). The real "
            "StationState.from_dict contract requires all of "
            f"{list(REQUIRED_STATION_STATE_FIELDS)} -- see system/schemas/station_state.py. This "
            "function does not fill in a default or guessed value for a missing field."
        )

    provenance = record.get(PROVENANCE_FIELD)
    if not isinstance(provenance, str) or not provenance.strip():
        raise MalformedInitialStateRecordError(
            f"Fail-closed: initial-state record for origin '{origin}' has no non-empty "
            f"'{PROVENANCE_FIELD}' citation. A hardcoded smoke-test constant (e.g. "
            "run_n6_closed_loop_simulation.py's own battery_soc_pct=80.0/battery_energy_wh=160000.0 "
            "example, which cites no source) must NOT be treated as authoritative per-origin "
            "evidence; this function requires an explicit, non-empty string naming where this "
            "record's values actually came from before it will be returned as 'validated'."
        )

    return record


class StationStateCodec:
    """
    Pure translation between a real `StationState` instance and the plain
    `Dict[str, Any]` shape `harness.py`'s Protocols use for `state`. Uses
    ONLY `StationState.to_dict()` / `StationState.from_dict()` -- confirmed
    present on the real class by direct read of `system/schemas/station_state.py`
    this pass -- and performs no field validation of its own (that remains
    `StationState`'s own responsibility).
    """

    @staticmethod
    def to_plain_dict(real_station_state: Any) -> Dict[str, Any]:
        """`real_station_state` is assumed to expose `.to_dict()` (the real `StationState` contract)."""
        return dict(real_station_state.to_dict())

    @staticmethod
    def from_plain_dict(state_dict: Dict[str, Any], station_state_cls: Any) -> Any:
        """
        `station_state_cls` is the real `StationState` class, INJECTED by the
        caller (never imported here) so this module never constructs a real
        object itself -- it only calls the classmethod the caller supplies.
        """
        return station_state_cls.from_dict(state_dict)


class ForecastBundleStepView:
    """
    Extracts one step's plain-dict forecast view from an already-produced
    real `ForecastBundle` instance, WITHOUT calling any forecast engine
    itself. Mirrors the field names `run_n6_closed_loop_simulation.py`
    actually reads per step (`solar_irradiance.point/lower/upper`,
    `demand.point`, `metadata["ebr_target_wh"]`) -- confirmed by direct read
    of that script, this pass.
    """

    @staticmethod
    def step_view(real_forecast_bundle: Any, step_index: int) -> Dict[str, Any]:
        return {
            "solar_irradiance_point": real_forecast_bundle.solar_irradiance.point[step_index],
            "solar_irradiance_lower": real_forecast_bundle.solar_irradiance.lower[step_index],
            "solar_irradiance_upper": real_forecast_bundle.solar_irradiance.upper[step_index],
            "demand_point": real_forecast_bundle.demand.point[step_index],
            "ebr_target_wh": real_forecast_bundle.metadata.get("ebr_target_wh"),
            "step_index": step_index,
        }


_UNSET = object()


# Exhaustion threshold for physical diesel fuel in evaluation layer (Blocker FUEL-1)
# Rationale: Baseline idle consumption is 5.0 L/h. If remaining fuel drops to or below 0.0001 L (0.1 mL)
# while diesel is commanded, or if required fuel exceeds available fuel, the physical simulator clamps
# to 0.0 without raising an exception, masking true consumption. Any run reaching this threshold
# with diesel running is latched as invalid.
FUEL_EXHAUSTION_THRESHOLD_L = 1e-4


class DispatchOutcomeView:
    """
    Extracts the single-hour scalar values `record_origin_outcome` expects
    (`diesel_consumed_liters`, `critical_unmet_load_wh`, `total_unmet_load_wh`,
    `constraint_status`) from a real `DispatchPlan`-shaped object at one hour
    index. Works identically whether `real_dispatch_plan` is a genuine
    24-distinct-hour plan or a single-hour-repeated 24-entry slice (see
    module docstring, gap 4) -- both are valid 24-length `DispatchPlan`
    instances under the real script's own existing convention.
    """

    @staticmethod
    def at_hour(
        real_dispatch_plan: Any,
        hour_index: int,
        fuel_consumed_liters_this_hour: Optional[float] = None,
        cumulative_diesel_consumed_liters: Any = _UNSET,
        generator_starts: Optional[int] = None,
        initial_battery_soc_pct: Optional[float] = None,
        terminal_battery_soc_pct: Optional[float] = None,
        initial_battery_energy_wh: Optional[float] = None,
        terminal_battery_energy_wh: Optional[float] = None,
        delta_e_term_wh: Optional[float] = None,
        startup_surcharge_liters: Optional[float] = None,
        has_fuel_failure: bool = False,
        fuel_failure_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        unmet_essential = getattr(real_dispatch_plan, "unmet_essential", None)
        critical_unmet_w = unmet_essential[hour_index] if unmet_essential is not None else None
        if cumulative_diesel_consumed_liters is not _UNSET:
            diesel = cumulative_diesel_consumed_liters
        else:
            diesel = fuel_consumed_liters_this_hour
        res = {
            "diesel_consumed_liters": diesel,
            "critical_unmet_load_wh": critical_unmet_w,
            "total_unmet_load_wh": real_dispatch_plan.unmet_load[hour_index],
            "constraint_status": real_dispatch_plan.constraint_status,
        }
        if generator_starts is not None:
            res["generator_starts"] = generator_starts
        if initial_battery_soc_pct is not None:
            res["initial_battery_soc_pct"] = initial_battery_soc_pct
        if terminal_battery_soc_pct is not None:
            res["terminal_battery_soc_pct"] = terminal_battery_soc_pct
        if initial_battery_energy_wh is not None:
            res["initial_battery_energy_wh"] = initial_battery_energy_wh
        if terminal_battery_energy_wh is not None:
            res["terminal_battery_energy_wh"] = terminal_battery_energy_wh
        if delta_e_term_wh is not None:
            res["delta_e_term_wh"] = delta_e_term_wh
        if startup_surcharge_liters is not None:
            res["startup_surcharge_liters"] = startup_surcharge_liters
        if has_fuel_failure:
            res["has_fuel_failure"] = True
            res["fuel_failure_reason"] = fuel_failure_reason
        return res


_CLEARSKY_CACHE = None


def _get_clearsky_df():
    global _CLEARSKY_CACHE
    if _CLEARSKY_CACHE is None:
        csv_path = Path("data/POLARIS_v0_1_clearsky_decomposition.csv")
        if not csv_path.exists():
            csv_path = Path(__file__).resolve().parents[4] / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
        df = pd.read_csv(csv_path)
        df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], utc=True)
        _CLEARSKY_CACHE = df.set_index("TIMESTAMP")
    return _CLEARSKY_CACHE


def _compute_boundary_clearsky_ratio(forecast_t23: float, clearsky_t23: float, clearsky_t24: float) -> float:
    MIN_CLEARSKY_WM2 = 5.0
    if clearsky_t23 < MIN_CLEARSKY_WM2:
        return max(0.0, 1.0 * clearsky_t24)
    k_t = min(forecast_t23 / clearsky_t23, 1.2)
    return max(0.0, k_t * clearsky_t24)


def _align_timeseries_od02(
    ts: Any,
    origin_timestamp_str: Optional[str] = None,
    is_generation: bool = False,
) -> Any:
    """
    Aligns a 24-step forecast timeseries with simulator dispatch steps under
    approved Decision OD-02-C (Candidate C.2 Clear-Sky Ratio fallback):
      - Shifts horizons 1..23 (indices 1..23) to dispatch steps 0..22.
      - Calculates dispatch step 23 using Candidate C.2 (Clear-Sky Ratio)
        derived from astronomical clear-sky curve; fails safe to 0.0.
    Preserves lower/upper bounds and unit if present.
    """
    if ts is None:
        return None
    pts = list(ts.point)
    if len(pts) != 24:
        raise ValueError(
            f"Fail-closed: OD-02 alignment requires 24-step forecast, got {len(pts)}."
        )

    terminal_val = 0.0
    if origin_timestamp_str is not None:
        try:
            origin_dt = pd.to_datetime(origin_timestamp_str, utc=True)
            time_t23 = origin_dt + timedelta(hours=23)
            time_t24 = origin_dt + timedelta(hours=24)

            cs_df = _get_clearsky_df()
            try:
                cs_t23 = float(cs_df.loc[time_t23, "clearsky_ghi"])
                cs_t24 = float(cs_df.loc[time_t24, "clearsky_ghi"])
                if is_generation or getattr(ts, "unit", "") == "W":
                    # Engineering PV transformation (K_pv = 51.0, max 60kW) for power channel
                    cs_t23_eff = cs_t23 * 51.0
                    cs_t24_eff = cs_t24 * 51.0
                    min_cs = 5.0 * 51.0
                    if cs_t23_eff < min_cs:
                        terminal_val = max(0.0, 1.0 * cs_t24_eff)
                    else:
                        k_t = min(float(pts[23]) / cs_t23_eff, 1.2)
                        terminal_val = max(0.0, k_t * cs_t24_eff)
                    terminal_val = min(terminal_val, 60000.0)
                else:
                    terminal_val = _compute_boundary_clearsky_ratio(float(pts[23]), cs_t23, cs_t24)
            except KeyError:
                terminal_val = 0.0  # Fail-safe if offline CSV lacks the timestamp
        except Exception:
            terminal_val = 0.0

    aligned_ts = copy.copy(ts)
    aligned_ts.point = pts[1:] + [terminal_val]

    if hasattr(ts, "lower") and ts.lower is not None:
        low = list(ts.lower)
        if len(low) == 24:
            aligned_ts.lower = low[1:] + [terminal_val]
        else:
            aligned_ts.lower = aligned_ts.point

    if hasattr(ts, "upper") and ts.upper is not None:
        upp = list(ts.upper)
        if len(upp) == 24:
            aligned_ts.upper = upp[1:] + [terminal_val]
        else:
            aligned_ts.upper = aligned_ts.point

    return aligned_ts


def _align_n6_bundle_od02(bundle: Any, origin_timestamp_str: Optional[str] = None) -> Any:
    """
    Aligns a 24-horizon N6 ForecastBundle (or duck-typed equivalent) with
    simulator dispatch steps 0-23 per approved Decision OD-02-C (POLARIS Master
    Decision Register Pass 24):

      1. Shifts solar forecast horizons 1..23 (indices 1..23) to dispatch steps 0..22.
      2. Injects Candidate C.2 (Clear-Sky Ratio) solar prediction for dispatch step 23
         (horizon h=25 / t0 + 24h), with fail-safe to 0.0.
      3. Advances bundle timestamps (if present) from [t0, t0+23h] to [t0+1h, t0+24h].
      4. Preserves demand, demand_critical, wind_generation, and ebr_target_wh
         unshifted, maintaining exact Policy B and OD-01 parity.

    Safe and idempotent: returns unmodified if already marked aligned.
    """
    if bundle is None:
        return None

    meta = getattr(bundle, "metadata", None)
    if isinstance(meta, dict) and meta.get("od02_time_aligned"):
        return bundle

    aligned_bundle = copy.copy(bundle)

    # Determine origin_timestamp_str if not explicitly passed
    if origin_timestamp_str is None:
        if hasattr(bundle, "origin_timestamp") and bundle.origin_timestamp:
            origin_timestamp_str = str(bundle.origin_timestamp)
        elif hasattr(bundle, "timestamps") and bundle.timestamps and len(bundle.timestamps) > 0:
            origin_timestamp_str = str(bundle.timestamps[0])
        elif isinstance(meta, dict):
            origin_timestamp_str = meta.get("origin_timestamp") or meta.get("forecast_origin")

    # 1. Align solar_irradiance (indices 1..23 -> 0..22, step 23 -> clearsky ratio / fallback)
    if hasattr(bundle, "solar_irradiance") and bundle.solar_irradiance is not None:
        aligned_bundle.solar_irradiance = _align_timeseries_od02(
            bundle.solar_irradiance, origin_timestamp_str=origin_timestamp_str, is_generation=False
        )

    # 2. Align solar_generation (if present: indices 1..23 -> 0..22, step 23 -> clearsky ratio / fallback)
    if hasattr(bundle, "solar_generation") and bundle.solar_generation is not None:
        aligned_bundle.solar_generation = _align_timeseries_od02(
            bundle.solar_generation, origin_timestamp_str=origin_timestamp_str, is_generation=True
        )

    # 3. Align timestamps (if present and len == 24)
    if hasattr(bundle, "timestamps") and bundle.timestamps is not None and len(bundle.timestamps) == 24:
        try:
            last_ts_str = str(bundle.timestamps[-1])
            dt_last = datetime.fromisoformat(last_ts_str.replace("Z", "+00:00"))
            dt_24 = dt_last + timedelta(hours=1)
            if last_ts_str.endswith("Z"):
                t_24 = dt_24.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                t_24 = dt_24.isoformat()
            aligned_bundle.timestamps = list(bundle.timestamps[1:]) + [t_24]
        except Exception:
            aligned_bundle.timestamps = list(bundle.timestamps[1:]) + [f"{bundle.timestamps[-1]}+1h"]

    # 4. Provenance in metadata
    if isinstance(meta, dict):
        new_meta = dict(meta)
        new_meta["od02_time_aligned"] = True
        new_meta["step23_method"] = "candidate_c2_clearsky_ratio"
        aligned_bundle.metadata = new_meta
    elif hasattr(bundle, "metadata"):
        aligned_bundle.metadata = {"od02_time_aligned": True, "step23_method": "candidate_c2_clearsky_ratio"}

    return aligned_bundle


class N6ForecastProviderAdapter:
    """
    Implements `ForecastProviderProtocol` (`.predict(origin, step_index, context)
    -> Dict[str, Any]`) around an injected object assumed to already expose
    the real `N6SolarForecastEngine.predict(station_state, context) ->
    ForecastBundle` signature (confirmed by direct read of
    `run_n6_closed_loop_simulation.py` line ~142, this pass).

    The real engine forecasts the FULL 24-hour bundle in one call; this
    adapter therefore calls it exactly ONCE per origin (on `step_index == 0`)
    and caches the resulting bundle, returning per-step views via
    `ForecastBundleStepView` on every call -- never re-forecasting per step,
    since the real engine's contract does not support that and nothing in
    this repository has ever exercised it that way.

    Under approved Decision OD-02-C, the bundle is aligned to simulator dispatch
    steps (N6 rows 1..23 -> dispatch steps 0..22, with Candidate C.2 Clear-Sky
    Ratio fallback at step 23).

    NEVER constructed with a real `N6SolarForecastEngine` instance anywhere
    in this module or its tests -- see module docstring.
    """

    def __init__(self, real_forecast_engine: Any, station_state_cls: Any, feature_matrix_by_origin: Dict[str, Any]) -> None:
        self._engine = real_forecast_engine
        self._station_state_cls = station_state_cls
        self._feature_matrix_by_origin = feature_matrix_by_origin
        self._cached_bundle_by_origin: Dict[str, Any] = {}

    def predict(self, origin: str, step_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        if origin not in self._cached_bundle_by_origin:
            if origin not in self._feature_matrix_by_origin:
                raise ValueError(
                    f"Fail-closed: no N6 feature matrix supplied for origin '{origin}' -- this "
                    "adapter never synthesizes a feature matrix."
                )
            real_station_state = StationStateCodec.from_plain_dict(context.get("state", {}), self._station_state_cls)
            raw_bundle = self._engine.predict(
                real_station_state, {"n6_feature_matrix": self._feature_matrix_by_origin[origin]}
            )
            self._cached_bundle_by_origin[origin] = _align_n6_bundle_od02(raw_bundle, origin_timestamp_str=origin)
        bundle = self._cached_bundle_by_origin[origin]
        view = ForecastBundleStepView.step_view(bundle, step_index)
        view["origin"] = origin
        view["_real_bundle_ref"] = bundle  # passed through for RoutedOptimizerAdapter's single-shot optimize call
        return view


def _prepare_gap19_terminal_target_config(
    station_state: Any,
    configs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Prepares a shallow-copied configuration for GAP19 optimization, dynamically
    deriving and injecting the cycle-neutral terminal lower-bound target per
    approved Decision OD-01 (POLARIS Master Decision Register v1.9.12 Section 38):

        terminal_target_wh = initial_e_wh - min_e_wh

    where:
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)
        initial_e_wh = max(min_e_wh, min(max_e_wh, station_state.battery_energy_wh))

    Precedence rules preserved:
      1. station_state.terminal_target_wh_override (highest tier, handled by GAP19)
      2. configs['terminal_target_wh'] (explicit caller numeric override)
      3. Dynamic OD-01 target derivation (injected only if overrides are absent)

    Downstream GAP19 call path is demonstrably read-only, so a shallow copy
    (dict(configs)) guarantees the shared caller configs_by_origin state remains
    immutable.
    """
    if not isinstance(configs, dict):
        raise ValueError(f"Fail-closed: configs must be a dictionary, got {type(configs).__name__}")

    # Shallow copy guarantees shared configs_by_origin state remains immutable
    opt_configs = dict(configs)

    # 1. Check explicit targets BEFORE validating dynamic-derivation inputs.
    # If either explicit target applies, bypass dynamic derivation and preserve existing GAP19 precedence.
    has_state_override = (
        station_state is not None
        and getattr(station_state, "terminal_target_wh_override", None) is not None
    )
    has_config_target = (
        "terminal_target_wh" in opt_configs and opt_configs["terminal_target_wh"] is not None
    )

    if has_state_override or has_config_target:
        return opt_configs

    # 2. Dynamic derivation required: fail-closed validation of state and battery parameters
    if station_state is None:
        raise ValueError("Fail-closed: station_state is None; cannot derive terminal target.")

    raw_energy = getattr(station_state, "battery_energy_wh", None)
    if raw_energy is None:
        raise ValueError("Fail-closed: station_state.battery_energy_wh is None; cannot derive terminal target.")

    if isinstance(raw_energy, bool):
        raise ValueError(f"Fail-closed: station_state.battery_energy_wh is boolean ({raw_energy!r}), expected numeric.")
    try:
        battery_energy_wh = float(raw_energy)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: station_state.battery_energy_wh is non-numeric ({raw_energy!r}): {err}")

    if not math.isfinite(battery_energy_wh):
        raise ValueError(f"Fail-closed: station_state.battery_energy_wh is not finite ({battery_energy_wh}).")

    # Extract and validate battery capacity and SOC bounds (applying GAP19 defaults if missing)
    bat_cfg = opt_configs.get("battery")
    if bat_cfg is None:
        bat_cfg = {}
    elif not isinstance(bat_cfg, dict):
        raise ValueError(f"Fail-closed: configs['battery'] must be a dictionary, got {type(bat_cfg).__name__}")

    raw_cap = bat_cfg.get("capacity_wh", 200000.0)
    raw_min_soc = bat_cfg.get("min_soc_pct", 20.0)
    raw_max_soc = bat_cfg.get("max_soc_pct", 95.0)

    if isinstance(raw_cap, bool):
        raise ValueError(f"Fail-closed: battery capacity_wh is boolean ({raw_cap!r}), expected numeric.")
    try:
        capacity_wh = float(raw_cap)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: battery capacity_wh is non-numeric ({raw_cap!r}): {err}")

    if not math.isfinite(capacity_wh) or capacity_wh <= 0.0:
        raise ValueError(f"Fail-closed: battery capacity_wh must be finite and > 0, got {capacity_wh}")

    if isinstance(raw_min_soc, bool):
        raise ValueError(f"Fail-closed: battery min_soc_pct is boolean ({raw_min_soc!r}), expected numeric.")
    try:
        min_soc_pct = float(raw_min_soc)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: battery min_soc_pct is non-numeric ({raw_min_soc!r}): {err}")

    if not math.isfinite(min_soc_pct):
        raise ValueError(f"Fail-closed: battery min_soc_pct is not finite ({min_soc_pct})")

    if isinstance(raw_max_soc, bool):
        raise ValueError(f"Fail-closed: battery max_soc_pct is boolean ({raw_max_soc!r}), expected numeric.")
    try:
        max_soc_pct = float(raw_max_soc)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: battery max_soc_pct is non-numeric ({raw_max_soc!r}): {err}")

    if not math.isfinite(max_soc_pct):
        raise ValueError(f"Fail-closed: battery max_soc_pct is not finite ({max_soc_pct})")

    if not (0.0 <= min_soc_pct <= max_soc_pct <= 100.0):
        raise ValueError(
            f"Fail-closed: invalid battery SOC bounds [0 <= {min_soc_pct} <= {max_soc_pct} <= 100.0]"
        )

    # 3. Calculate energy boundaries and clamped initial energy
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)
    initial_e_wh = max(min_e_wh, min(max_e_wh, battery_energy_wh))

    # 4. Inject cycle-neutral OD-01 terminal target
    opt_configs["terminal_target_wh"] = initial_e_wh - min_e_wh

    return opt_configs


def _validate_conformal_ebr(ebr_raw: Any) -> List[float]:
    """
    Validates conformal EBR vector strictly fail-closed.
    Must be a sequence (list or tuple) of exactly 24 elements, all convertible
    to finite, non-negative floats (boolean values rejected).
    """
    if not isinstance(ebr_raw, (list, tuple)):
        raise ValueError(
            f"Fail-closed: conformal EBR must be a list or tuple, got {type(ebr_raw).__name__}."
        )
    if len(ebr_raw) != 24:
        raise ValueError(
            f"Fail-closed: conformal EBR must contain exactly 24 values, got {len(ebr_raw)}."
        )
    validated: List[float] = []
    for idx, val in enumerate(ebr_raw):
        if isinstance(val, bool):
            raise ValueError(
                f"Fail-closed: conformal EBR at index {idx} is boolean ({val!r}); expected finite numeric."
            )
        try:
            fval = float(val)
        except (TypeError, ValueError) as err:
            raise ValueError(
                f"Fail-closed: conformal EBR at index {idx} is non-numeric ({val!r}): {err}"
            )
        if math.isnan(fval) or math.isinf(fval):
            raise ValueError(
                f"Fail-closed: conformal EBR at index {idx} is non-finite ({fval})."
            )
        if fval < -1e-4:
            raise ValueError(
                f"Fail-closed: conformal EBR at index {idx} is negative ({fval})."
            )
        validated.append(max(0.0, fval))
    return validated


def _extract_and_validate_demands(
    bundle: Any,
    configs: Dict[str, Any],
) -> Tuple[List[float], List[float]]:
    """
    Ingests and validates total load demand and critical load demand following
    GAP19's exact contract and 4-tier precedence:
      1. bundle.demand_critical
      2. configs['critical_demand_w']
      3. configs['critical_demand_ratio']
      4. Fail-closed MISSING_GOVERNED_INPUT error
    """
    if bundle is None:
        raise ValueError("Fail-closed: bundle is None; cannot determine load demand.")
    demand_obj = getattr(bundle, "demand", None)
    if demand_obj is None or not hasattr(demand_obj, "point"):
        raise ValueError("Fail-closed: bundle missing 'demand' or 'demand.point'.")
    raw_demand = demand_obj.point
    if not isinstance(raw_demand, (list, tuple)) or len(raw_demand) != 24:
        raise ValueError(
            f"Fail-closed: total demand must be a 24-element sequence, got "
            f"{len(raw_demand) if isinstance(raw_demand, (list, tuple)) else type(raw_demand).__name__}."
        )
    demand: List[float] = []
    for idx, v in enumerate(raw_demand):
        if isinstance(v, bool):
            raise ValueError(f"Fail-closed: total demand at index {idx} is boolean ({v!r}).")
        try:
            fv = float(v)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Fail-closed: total demand at index {idx} is non-numeric ({v!r}): {err}")
        if math.isnan(fv) or math.isinf(fv) or fv < -1e-4:
            raise ValueError(f"Fail-closed: total demand at index {idx} is invalid ({fv}).")
        demand.append(max(0.0, fv))

    # Precedence tier 1: bundle.demand_critical
    demand_crit_obj = getattr(bundle, "demand_critical", None)
    if demand_crit_obj is not None:
        if not hasattr(demand_crit_obj, "point"):
            raise ValueError("Fail-closed: bundle.demand_critical missing 'point' attribute.")
        raw_cd = demand_crit_obj.point
        if not isinstance(raw_cd, (list, tuple)) or len(raw_cd) != 24:
            raise ValueError(
                f"Invalid critical_demand_w configuration array length ({len(raw_cd) if isinstance(raw_cd, (list, tuple)) else type(raw_cd)}); expected 24."
            )
        critical_demand = [float(v) for v in raw_cd]
    # Precedence tier 2: config["critical_demand_w"]
    elif "critical_demand_w" in configs and configs["critical_demand_w"] is not None:
        cd_cfg = configs["critical_demand_w"]
        if not isinstance(cd_cfg, (list, tuple)) or len(cd_cfg) != 24:
            raise ValueError(
                f"Invalid critical_demand_w configuration array length ({len(cd_cfg) if isinstance(cd_cfg, (list, tuple)) else type(cd_cfg)}); expected 24."
            )
        critical_demand = [float(v) for v in cd_cfg]
    # Precedence tier 3: config["critical_demand_ratio"]
    elif "critical_demand_ratio" in configs and configs["critical_demand_ratio"] is not None:
        raw_ratio = configs["critical_demand_ratio"]
        if isinstance(raw_ratio, bool):
            raise ValueError(f"Invalid critical_demand_ratio ({raw_ratio!r}); expected ratio in [0.0, 1.0].")
        try:
            ratio = float(raw_ratio)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid critical_demand_ratio ({raw_ratio!r}): {err}")
        if not (0.0 <= ratio <= 1.0) or math.isnan(ratio) or math.isinf(ratio):
            raise ValueError(f"Invalid critical_demand_ratio ({ratio}); expected ratio in [0.0, 1.0].")
        critical_demand = [p * ratio for p in demand]
    # Precedence tier 4: missing input
    else:
        raise ValueError("MISSING_GOVERNED_INPUT: Protected critical load trajectory (demand_critical) is missing or unspecified.")

    # Validation matching GAP19 lines 103-108
    for idx, (cp, dp) in enumerate(zip(critical_demand, demand)):
        if isinstance(cp, bool):
            raise ValueError(f"Invalid protected critical load value at index {idx}: {cp!r}.")
        if math.isnan(cp) or math.isinf(cp) or cp < 0.0:
            raise ValueError(f"Invalid protected critical load value at index {idx}: {cp}.")
        if cp > dp + 1e-4:
            raise ValueError(f"Protected critical load ({cp}W) exceeds total demand ({dp}W) at index {idx}.")

    return critical_demand, demand


def _compute_gap19_six_hour_critical_reserve(
    critical_demand: List[float],
    configs: Dict[str, Any],
) -> List[float]:
    """
    Computes the governed 6-hour critical reserve trajectory matching
    GAP19HighsNativeOptimizer lines 109, 126-132 identically:
        W(t) = [t, min(t+5, 23)]
        w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, min(t+6, 24)))
        ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
    """
    bat_cfg = configs.get("battery")
    if bat_cfg is None:
        bat_cfg = {}
    elif not isinstance(bat_cfg, dict):
        raise ValueError(f"Fail-closed: configs['battery'] must be a dictionary, got {type(bat_cfg).__name__}")

    raw_eta = bat_cfg.get("discharge_efficiency", 0.92)
    if isinstance(raw_eta, bool):
        raise ValueError(f"Fail-closed: discharge_efficiency is boolean ({raw_eta!r}), expected numeric.")
    try:
        eta_dis = float(raw_eta)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: discharge_efficiency is non-numeric ({raw_eta!r}): {err}")
    if not math.isfinite(eta_dis) or eta_dis <= 0.0:
        raise ValueError(f"Fail-closed: discharge_efficiency must be finite and > 0, got {eta_dis}")

    opt_cfg = configs.get("optimizer")
    if opt_cfg is None:
        opt_cfg = {}
    elif not isinstance(opt_cfg, dict):
        raise ValueError(f"Fail-closed: configs['optimizer'] must be a dictionary, got {type(opt_cfg).__name__}")

    raw_dt = opt_cfg.get("timestep_hours", 1.0)
    if isinstance(raw_dt, bool):
        raise ValueError(f"Fail-closed: timestep_hours is boolean ({raw_dt!r}), expected numeric.")
    try:
        dt = float(raw_dt)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Fail-closed: timestep_hours is non-numeric ({raw_dt!r}): {err}")
    if not math.isfinite(dt) or dt <= 0.0:
        raise ValueError(f"Fail-closed: timestep_hours must be finite and > 0, got {dt}")

    crit_reserve_wh: List[float] = []
    for t in range(24):
        end_k = min(t + 6, 24)
        w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
        ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
        crit_reserve_wh.append(ebr_req_wh)

    return crit_reserve_wh


def _prepare_gap19_policy_b_config(
    bundle: Any,
    configs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Prepares a shallow-copied configuration for GAP19 optimization, enforcing
    Policy B (register Section 4 item 7):

        combined_reserve_wh[t] = max(existing_GAP19_critical_reserve_wh[t], conformal_ebr_wh[t])

    Precedence and signal detection:
      1. Policy B is active if:
         - configs['reserve_policy'] or configs['policy'] is 'POLICY_B' / 'B', OR
         - configs['policy_b'] is True, OR
         - bundle.metadata explicitly identifies N6 (SOLAR_FORECAST_SOURCE, engine_class,
           or model_id matching CANDIDATE_N6_25ADD_15KT_SPECIALIST / N6SolarForecastEngine), OR
         - bundle.metadata['reserve_policy'] is 'POLICY_B' / 'B'.
      2. When Policy B is active:
         - Attempting to pass 'ebr_target_wh_override' in configs fails closed immediately
           (cannot bypass Policy B).
         - Conformal EBR is extracted from bundle.metadata['ebr_target_wh'] (or
           configs['conformal_ebr_wh'] / configs['ebr_target_wh']).
         - If missing or malformed, fails closed immediately.
         - Critical demand and total demand are validated per GAP19's exact 4-tier contract.
         - 6-hour critical reserve is computed matching GAP19's exact arithmetic.
         - Pointwise maximum is computed and injected into opt_configs['ebr_target_wh'].
      3. When Policy B is NOT active (non-N6 / baseline runs):
         - Existing config['ebr_target_wh'] is preserved if present; otherwise left unset.
         - GAP19 native critical reserve calculation is preserved without alteration.

    Immutability:
      Uses dict(configs) to guarantee caller-supplied configuration is never mutated.
    """
    if not isinstance(configs, dict):
        raise ValueError(f"Fail-closed: configs must be a dictionary, got {type(configs).__name__}")

    opt_configs = dict(configs)

    # 1. Check for Policy B activation signals
    metadata = getattr(bundle, "metadata", None)
    is_n6_bundle = False
    metadata_policy_b = False
    has_metadata_ebr = False

    if isinstance(metadata, dict):
        source = (
            metadata.get("SOLAR_FORECAST_SOURCE")
            or metadata.get("engine_class")
            or metadata.get("model_id")
        )
        if source in (
            "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
            "N6SolarForecastEngine",
        ):
            is_n6_bundle = True

        b_pol = str(metadata.get("reserve_policy", metadata.get("policy", ""))).upper()
        if b_pol in ("POLICY_B", "B", "POLICYB"):
            metadata_policy_b = True

        if "ebr_target_wh" in metadata and metadata["ebr_target_wh"] is not None:
            has_metadata_ebr = True

    cfg_policy = str(opt_configs.get("reserve_policy", opt_configs.get("policy", ""))).upper()
    cfg_policy_b = cfg_policy in ("POLICY_B", "B", "POLICYB") or bool(opt_configs.get("policy_b", False))

    policy_b_active = is_n6_bundle or metadata_policy_b or cfg_policy_b

    # 2. If Policy B is NOT active, preserve existing non-N6 behavior
    if not policy_b_active:
        return opt_configs

    # 3. Policy B is active: forbid bypassing Policy B via config override
    if "ebr_target_wh_override" in opt_configs and opt_configs["ebr_target_wh_override"] is not None:
        raise ValueError(
            "Fail-closed: 'ebr_target_wh_override' in configs cannot be used to bypass Policy B. "
            "Policy B strictly requires combined_reserve = max(critical_reserve, conformal_ebr)."
        )

    # 4. Policy B is active: resolve conformal EBR
    raw_conformal_ebr = None
    if has_metadata_ebr:
        raw_conformal_ebr = metadata["ebr_target_wh"]
    elif "conformal_ebr_wh" in opt_configs and opt_configs["conformal_ebr_wh"] is not None:
        raw_conformal_ebr = opt_configs["conformal_ebr_wh"]
    elif "ebr_target_wh" in opt_configs and opt_configs["ebr_target_wh"] is not None:
        raw_conformal_ebr = opt_configs["ebr_target_wh"]

    if raw_conformal_ebr is None:
        raise ValueError(
            "Fail-closed: N6 Policy B evaluation requires conformal 'ebr_target_wh' in bundle metadata or config, none provided."
        )

    # Validate conformal EBR fail-closed
    conformal_ebr = _validate_conformal_ebr(raw_conformal_ebr)

    # Ingest and validate demands matching GAP19
    critical_demand, demand = _extract_and_validate_demands(bundle, opt_configs)

    # Compute authoritative 6-hour critical reserve matching GAP19
    crit_reserve_wh = _compute_gap19_six_hour_critical_reserve(critical_demand, opt_configs)

    # Compute pointwise maximum: max(critical_reserve[t], conformal_ebr[t])
    combined_reserve = [
        max(float(c_wh), float(e_wh))
        for c_wh, e_wh in zip(crit_reserve_wh, conformal_ebr)
    ]

    opt_configs["ebr_target_wh"] = combined_reserve
    return opt_configs


class RoutedOptimizerAdapter:
    """
    Implements `DispatchOptimizerProtocol` (`.optimize(state, forecast,
    controller_settings) -> Dict[str, Any]`) around injected objects assumed
    to expose the real `EMSControlRouter.evaluate_and_route(station_state,
    bundle, configs) -> (assessment, route)` and
    `GAP19HighsNativeOptimizer.optimize(bundle, station_state, configs) ->
    DispatchPlan` signatures (both confirmed by direct read of
    `run_n6_closed_loop_simulation.py` lines ~154-163, this pass).

    Resolves integration-assumption gap 3 (router step unrepresented in
    `harness.py`'s four Protocols, IA-2 above) by calling the router FIRST
    and recording its `route` decision into the returned dict's `"route"`
    key -- never silently dropped. Resolves gap/IA-1 (single-shot-vs-receding
    -horizon) by optimizing ONCE per origin (on `step_index == 0`, read from
    `forecast["step_index"]`) and caching the resulting `DispatchPlan`;
    subsequent calls within the same origin return the SAME cached plan
    object (not a re-optimization), to be sliced per hour by
    `SingleShotPlanSlicingSimulatorAdapter`.

    NEVER constructed with a real `EMSControlRouter`/`GAP19HighsNativeOptimizer`
    instance anywhere in this module or its tests -- see module docstring.
    """

    def __init__(self, real_router: Any, real_optimizer: Any, configs_by_origin: Dict[str, Dict[str, Any]]) -> None:
        self._router = real_router
        self._optimizer = real_optimizer
        self._configs_by_origin = configs_by_origin
        self._cached_plan_by_origin: Dict[str, Any] = {}
        self._cached_route_by_origin: Dict[str, str] = {}

    def optimize(self, state: Dict[str, Any], forecast: Dict[str, Any], controller_settings: Any) -> Dict[str, Any]:
        origin = forecast.get("origin")
        if origin is None:
            raise ValueError("Fail-closed: forecast dict carries no 'origin' key; cannot route/optimize.")
        if state.get("_has_fuel_failure", False) or state.get("_diesel_fuel_tracking_gap", False):
            raise RuntimeError(
                f"Fail-closed: cannot optimize origin '{origin}' when fuel failure or tracking gap is latched."
            )
        if origin not in self._cached_plan_by_origin:
            if origin not in self._configs_by_origin:
                raise ValueError(
                    f"Fail-closed: no microgrid subsystem config supplied for origin '{origin}' -- "
                    "this adapter never synthesizes a configuration."
                )
            bundle = forecast.get("_real_bundle_ref")
            if bundle is None:
                raise ValueError(
                    "Fail-closed: forecast dict carries no '_real_bundle_ref' -- "
                    "RoutedOptimizerAdapter must be paired with N6ForecastProviderAdapter "
                    "(or an equivalent that supplies the real ForecastBundle reference)."
                )
            real_station_state = state.get("_real_station_state_ref")
            if real_station_state is None:
                raise ValueError(
                    "Fail-closed: state dict carries no '_real_station_state_ref' -- the caller "
                    "must supply the real StationState object alongside its plain-dict view."
                )
            configs = self._configs_by_origin[origin]
            assessment, route = self._router.evaluate_and_route(real_station_state, bundle, configs)
            solver_configs = _prepare_gap19_terminal_target_config(real_station_state, configs)
            solver_configs = _prepare_gap19_policy_b_config(bundle, solver_configs)
            plan = self._optimizer.optimize(bundle, real_station_state, solver_configs)
            self._cached_plan_by_origin[origin] = plan
            self._cached_route_by_origin[origin] = route
        return {
            "origin": origin,
            "route": self._cached_route_by_origin[origin],
            "_real_plan_ref": self._cached_plan_by_origin[origin],
        }


class SingleShotPlanSlicingSimulatorAdapter:
    """
    Implements `SimulationStepperProtocol` (`.step(state, dispatch_plan) ->
    Dict[str, Any]`) around an injected object assumed to expose the real
    `DigitalTwinSimulator.step(station_state, one_hour_dispatch_plan_slice,
    actual_t) -> StationState` signature (confirmed by direct read of
    `run_n6_closed_loop_simulation.py` lines ~200-221, this pass -- including
    that script's own convention of repeating each scalar 24 times to build
    a valid single-hour `DispatchPlan` slice, gap 4 above).

    Requires the caller to supply `actuals_by_origin_and_step` (already
    -known ground-truth values per origin/step) -- this adapter NEVER
    fabricates a ground-truth actual; a missing value for the requested
    origin/step raises, it is not defaulted to the forecast or to zero.

    NEVER constructed with a real `DigitalTwinSimulator` instance anywhere
    in this module or its tests -- see module docstring.
    """

    @classmethod
    def from_authoritative_fixture(
        cls,
        real_simulator: Any,
        dispatch_plan_cls: Any,
        station_state_cls: Any,
        fixture_path: Path | str = CANONICAL_FIXTURE_RELATIVE_PATH,
        origins: Sequence[str] = (),
        steps_per_origin: int = 24,
        verify_sha256: bool = True,
    ) -> SingleShotPlanSlicingSimulatorAdapter:
        actuals = load_authoritative_actuals_by_origin(
            fixture_path=fixture_path,
            origins=origins,
            steps_per_origin=steps_per_origin,
            verify_sha256=verify_sha256,
        )
        return cls(
            real_simulator=real_simulator,
            dispatch_plan_cls=dispatch_plan_cls,
            actuals_by_origin_and_step=actuals,
            station_state_cls=station_state_cls,
            _allow_synthetic_actuals_for_testing=True,
        )

    def __init__(
        self,
        real_simulator: Any,
        dispatch_plan_cls: Any,
        actuals_by_origin_and_step: Dict[str, List[Dict[str, Any]]],
        station_state_cls: Any,
        _allow_synthetic_actuals_for_testing: bool = False,
    ) -> None:
        if not _allow_synthetic_actuals_for_testing and not getattr(actuals_by_origin_and_step, "_is_authoritative_actuals", False):
            raise ValueError(
                "Fail-closed: direct construction of SingleShotPlanSlicingSimulatorAdapter with "
                "unverified actuals is prohibited. Use SingleShotPlanSlicingSimulatorAdapter.from_authoritative_fixture() "
                "or pass _allow_synthetic_actuals_for_testing=True for synthetic tests."
            )
        self._simulator = real_simulator
        self._dispatch_plan_cls = dispatch_plan_cls
        self._actuals_by_origin_and_step = actuals_by_origin_and_step
        self._station_state_cls = station_state_cls

    def step(self, state: Dict[str, Any], dispatch_plan: Dict[str, Any]) -> Dict[str, Any]:
        origin = dispatch_plan.get("origin")
        real_plan = dispatch_plan.get("_real_plan_ref")
        if origin is None or real_plan is None:
            raise ValueError(
                "Fail-closed: dispatch_plan dict carries no 'origin'/'_real_plan_ref' -- "
                "SingleShotPlanSlicingSimulatorAdapter must be paired with RoutedOptimizerAdapter."
            )
        step_index = state.get("_step_index")
        if step_index is None:
            raise ValueError("Fail-closed: state dict carries no '_step_index'; caller must track it explicitly.")
        real_station_state = state.get("_real_station_state_ref")
        if real_station_state is None:
            raise ValueError("Fail-closed: state dict carries no '_real_station_state_ref'.")
        if origin not in self._actuals_by_origin_and_step or step_index >= len(self._actuals_by_origin_and_step[origin]):
            raise ValueError(
                f"Fail-closed: no ground-truth actual supplied for origin '{origin}' step {step_index} -- "
                "this adapter never fabricates a ground-truth value."
            )
        actual_t = self._actuals_by_origin_and_step[origin][step_index]

        one_hour_slice = self._dispatch_plan_cls(
            schema_version=real_plan.schema_version,
            timestamps=[real_plan.timestamps[step_index]] * 24,
            solar_used=[real_plan.solar_used[step_index]] * 24,
            wind_used=[real_plan.wind_used[step_index]] * 24,
            battery_charge=[real_plan.battery_charge[step_index]] * 24,
            battery_discharge=[real_plan.battery_discharge[step_index]] * 24,
            battery_soc=[real_plan.battery_soc[step_index]] * 24,
            diesel_power=[real_plan.diesel_power[step_index]] * 24,
            load_served=[real_plan.load_served[step_index]] * 24,
            flexible_load_schedule=[real_plan.flexible_load_schedule[step_index]] * 24,
            renewable_curtailment=[real_plan.renewable_curtailment[step_index]] * 24,
            unmet_load=[real_plan.unmet_load[step_index]] * 24,
            objective_value=real_plan.objective_value,
            constraint_status=real_plan.constraint_status,
            energy_balance_errors=[0.0] * 24,
        )

        # 1. Authoritative Diesel Power Validation Before Step (BLOCKER-FUEL-1)
        p_diesel_raw = real_plan.diesel_power[step_index]
        p_diesel_valid = (
            p_diesel_raw is not None
            and not isinstance(p_diesel_raw, bool)
            and isinstance(p_diesel_raw, (int, float))
            and not math.isnan(p_diesel_raw)
            and not math.isinf(p_diesel_raw)
            and p_diesel_raw >= 0.0
        )
        p_diesel_val = float(p_diesel_raw) if p_diesel_valid else 0.0
        is_diesel_dispatched = (p_diesel_val > 0.0)

        # 2. Authoritative Fuel State Validation Before Step (BLOCKER-FUEL-1)
        fuel_before = getattr(real_station_state, "diesel_fuel_remaining_liters", None)
        fuel_before_valid = (
            fuel_before is not None
            and not isinstance(fuel_before, bool)
            and isinstance(fuel_before, (int, float))
            and not math.isnan(fuel_before)
            and not math.isinf(fuel_before)
            and fuel_before >= 0.0
        )

        # Simulator physical fuel curve: base_fuel_lph = 5.0, marginal_fuel_lpwh = 0.00025
        required_fuel = ((5.0 if is_diesel_dispatched else 0.0) + (0.00025 * p_diesel_val)) * 1.0
        fuel_after_est = round(fuel_before - required_fuel, 4) if (fuel_before_valid and p_diesel_valid) else None

        # Pre-call fuel guards (CRIT-01): reject and latch BEFORE calling self._simulator.step()
        pre_fuel_failure_reason = None
        has_pre_fuel_failure = False

        if state.get("_diesel_fuel_tracking_gap", False) or state.get("_has_fuel_failure", False):
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"
        elif not p_diesel_valid:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"INVALID_DIESEL_POWER: diesel power must be a non-negative finite number (got {p_diesel_raw})"
            )
        elif not fuel_before_valid:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_ACCOUNTING_INVALID: missing, non-numeric, non-finite, or negative fuel observation "
                f"(before={fuel_before})"
            )
        elif fuel_before <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: fuel ({fuel_before:.6f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )
        elif required_fuel > fuel_before:  # Zero-slack check
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTION_CLAMPED: required fuel {required_fuel:.4f} L exceeds available fuel {fuel_before:.4f} L"
            )
        elif fuel_after_est is not None and fuel_after_est <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: fuel after consumption ({fuel_after_est:.6f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )

        if has_pre_fuel_failure:
            # Under pre-call failure, self._simulator.step() is NEVER invoked.
            # On an aborted trajectory, do not fabricate terminal energy/SOC deltas,
            # generator starts, or startup surcharges as zero. Mark unavailable metrics as None
            # and invalidate the run.
            if step_index == 0:
                init_soc = float(getattr(real_station_state, "battery_soc_pct", 0.0))
                init_energy = float(getattr(real_station_state, "battery_energy_wh", 0.0))
            else:
                init_soc = state.get("_initial_battery_soc_pct")
                init_energy = state.get("_initial_battery_energy_wh")

            next_state_dict = StationStateCodec.to_plain_dict(real_station_state)
            next_state_dict["_real_station_state_ref"] = real_station_state
            next_state_dict["_step_index"] = step_index
            next_state_dict["_cumulative_generator_starts"] = None
            next_state_dict["_startup_surcharge_liters"] = None
            next_state_dict["_initial_battery_soc_pct"] = init_soc
            next_state_dict["_initial_battery_energy_wh"] = init_energy
            next_state_dict["_terminal_battery_soc_pct"] = None
            next_state_dict["_terminal_battery_energy_wh"] = None
            next_state_dict["_delta_e_term_wh"] = None
            next_state_dict["_diesel_fuel_tracking_gap"] = True
            next_state_dict["_has_fuel_failure"] = True
            next_state_dict["_fuel_failure_reason"] = pre_fuel_failure_reason
            next_state_dict["_cumulative_diesel_consumed_liters"] = None

            return {
                "state": next_state_dict,
                "dispatch_outcome": DispatchOutcomeView.at_hour(
                    real_plan,
                    step_index,
                    fuel_consumed_liters_this_hour=None,
                    cumulative_diesel_consumed_liters=None,
                    generator_starts=None,
                    initial_battery_soc_pct=init_soc,
                    terminal_battery_soc_pct=None,
                    initial_battery_energy_wh=init_energy,
                    terminal_battery_energy_wh=None,
                    delta_e_term_wh=None,
                    startup_surcharge_liters=None,
                    has_fuel_failure=True,
                    fuel_failure_reason=pre_fuel_failure_reason,
                ),
                "stop_early": True,
            }

        # Step simulator ONLY after pre-call validation passes
        next_real_state = self._simulator.step(real_station_state, one_hour_slice, actual_t)

        # 3. Authoritative Fuel State Validation After Step (BLOCKER-FUEL-1 defense-in-depth)
        fuel_after = getattr(next_real_state, "diesel_fuel_remaining_liters", None)
        fuel_after_valid = (
            fuel_after is not None
            and not isinstance(fuel_after, bool)
            and isinstance(fuel_after, (int, float))
            and not math.isnan(fuel_after)
            and not math.isinf(fuel_after)
            and fuel_after >= 0.0
        )

        fuel_failure_reason = None
        has_fuel_failure = False

        if not fuel_after_valid:
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_ACCOUNTING_INVALID: missing or non-finite fuel observation after step "
                f"(after={fuel_after})"
            )
        elif fuel_after > fuel_before:  # Zero-slack monotonicity check
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_MONOTONICITY_VIOLATED: fuel increased from {fuel_before:.4f} L to {fuel_after:.4f} L"
            )
        elif fuel_after <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: remaining fuel ({fuel_after:.4f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )

        # Check for pre-existing latched failure from prior steps
        had_fuel_gap = state.get("_diesel_fuel_tracking_gap", False) or state.get("_has_fuel_failure", False)
        if had_fuel_gap or has_fuel_failure:
            fuel_gap_active = True
            cumulative_fuel = None
            step_consumed = None
            latched_reason = fuel_failure_reason or state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"
        else:
            fuel_gap_active = False
            latched_reason = None
            step_consumed = (
                max(0.0, fuel_before - fuel_after) if (fuel_before is not None and fuel_after is not None) else None
            )
            prev_cumulative = state.get("_cumulative_diesel_consumed_liters")
            cumulative_fuel = round((0.0 if prev_cumulative is None else prev_cumulative) + (step_consumed or 0.0), 6)

        # 4. Generator Start Counting via diesel_running boolean transition
        was_running = bool(getattr(real_station_state, "diesel_running", False))
        is_running_now = bool(getattr(next_real_state, "diesel_running", False))
        is_start = (is_running_now and not was_running)
        prev_starts = state.get("_cumulative_generator_starts", 0)
        cumulative_starts = prev_starts + (1 if is_start else 0)
        startup_surcharge_liters = float(cumulative_starts) * 6.0

        # 5. Authoritative Battery State Tracking (SOC and Energy)
        if step_index == 0:
            init_soc = float(getattr(real_station_state, "battery_soc_pct", 0.0))
            init_energy = float(getattr(real_station_state, "battery_energy_wh", 0.0))
        else:
            init_soc = state.get("_initial_battery_soc_pct")
            init_energy = state.get("_initial_battery_energy_wh")

        term_soc = float(getattr(next_real_state, "battery_soc_pct", 0.0))
        term_energy = float(getattr(next_real_state, "battery_energy_wh", 0.0))
        delta_e = round(term_energy - init_energy, 4) if init_energy is not None else None

        if fuel_gap_active:
            cumulative_starts = None
            startup_surcharge_liters = None
            term_soc = None
            term_energy = None
            delta_e = None

        next_state_dict = StationStateCodec.to_plain_dict(next_real_state)
        next_state_dict["_real_station_state_ref"] = next_real_state
        next_state_dict["_step_index"] = step_index + 1
        next_state_dict["_cumulative_generator_starts"] = cumulative_starts
        next_state_dict["_startup_surcharge_liters"] = startup_surcharge_liters
        next_state_dict["_initial_battery_soc_pct"] = init_soc
        next_state_dict["_initial_battery_energy_wh"] = init_energy
        next_state_dict["_terminal_battery_soc_pct"] = term_soc
        next_state_dict["_terminal_battery_energy_wh"] = term_energy
        next_state_dict["_delta_e_term_wh"] = delta_e

        if fuel_gap_active:
            next_state_dict["_diesel_fuel_tracking_gap"] = True
            next_state_dict["_has_fuel_failure"] = True
            next_state_dict["_fuel_failure_reason"] = latched_reason
            next_state_dict["_cumulative_diesel_consumed_liters"] = None
        else:
            next_state_dict["_cumulative_diesel_consumed_liters"] = cumulative_fuel

        return {
            "state": next_state_dict,
            "dispatch_outcome": DispatchOutcomeView.at_hour(
                real_plan,
                step_index,
                fuel_consumed_liters_this_hour=step_consumed,
                cumulative_diesel_consumed_liters=cumulative_fuel,
                generator_starts=cumulative_starts,
                initial_battery_soc_pct=init_soc,
                terminal_battery_soc_pct=term_soc,
                initial_battery_energy_wh=init_energy,
                terminal_battery_energy_wh=term_energy,
                delta_e_term_wh=delta_e,
                startup_surcharge_liters=startup_surcharge_liters,
                has_fuel_failure=fuel_gap_active,
                fuel_failure_reason=latched_reason,
            ),
            "stop_early": fuel_gap_active,
        }


class ReservePolicyGuardSafetyEvaluatorAdapter:
    """
    Implements `SafetyEvaluatorProtocol` (`.evaluate_dispatch_safety(dispatch_outcome)
    -> Optional[SafetyEvaluationResult]`) around the injected real
    `reserve_policy_guard.evaluate_dispatch_safety(plan: Dict, min_e_wh,
    reserve_shortfall_authorization_wh) -> SafetyEvaluationResult` function
    (confirmed by direct read of `system/safety/reserve_policy_guard.py`
    lines ~238-253, this pass).

    `reserve_shortfall_authorization_wh` defaults to `None` -- IA-4 above --
    matching the current production default at both existing call sites
    (`evaluator.py`/`worker.py`); this adapter does not invent a numeric
    ceiling SAF-03 has not authorized.

    NEVER constructed with the real `evaluate_dispatch_safety` function
    anywhere in this module or its tests -- see module docstring.
    """

    def __init__(
        self,
        real_evaluate_dispatch_safety_fn: Any,
        min_e_wh: Optional[float] = None,
        reserve_shortfall_authorization_wh: Optional[float] = None,
    ) -> None:
        self._evaluate_dispatch_safety_fn = real_evaluate_dispatch_safety_fn
        self._min_e_wh = min_e_wh
        self._reserve_shortfall_authorization_wh = reserve_shortfall_authorization_wh

    def evaluate_dispatch_safety(self, dispatch_outcome: Dict[str, Any]) -> Optional[Any]:
        real_plan_dict = dispatch_outcome.get("_real_plan_dict")
        if real_plan_dict is None:
            # No real DispatchPlan-shaped dict was supplied for this outcome --
            # per SAF-02/record_origin_outcome's existing rule, missing safety
            # evidence is UNKNOWN, never a pass. This adapter returns None
            # (not a fabricated result) so the harness's existing rule applies.
            return None
        return self._evaluate_dispatch_safety_fn(
            real_plan_dict, self._min_e_wh, self._reserve_shortfall_authorization_wh
        )


# ---------------------------------------------------------------------------
# IA-1 (owner decision, this pass): receding-horizon adapter variant.
# ---------------------------------------------------------------------------
# Everything below mirrors the ABOVE adapters' translation-only role and the
# SAME governance boundary (no real production object imported or
# constructed anywhere in this module; every injected collaborator is typed
# `Any` at runtime and assumed by the CALLER to already satisfy the real
# class's documented signature). The difference is purely architectural:
# the single-shot adapters above call their real collaborator ONCE per
# origin and cache the result; the adapters below call theirs FRESH, EVERY
# STEP, with NO cross-step cache of any kind -- mirroring
# `system/orchestration/worker.py`'s Cell B loop
# (`bundle = self.forecast_engine.predict(st_k, runtime_ctx)` /
# `assessment, route = self.router.evaluate_and_route(st_k, bundle, configs)` /
# `plan = self.optimizer.optimize(bundle, st_k, configs)` each called fresh
# inside `for k in range(current_step, self.end_step)`) and
# `system/runtime/runner.py`'s equivalent live-runtime loop, confirmed by
# direct read both this pass and the prior IA-1/IA-2 design-resolution pass.
#
# These adapters are exercised EXCLUSIVELY against hand-built Fakes in
# `system/tests/test_n6_receding_horizon_adapters.py` -- never against a
# real `N6SolarForecastEngine`/`EMSControlRouter`/
# `GAP19HighsNativeOptimizer`/`OptionDFallbackSolver`/`DigitalTwinSimulator`.
# Wiring one of these around a REAL production object and actually invoking
# it would itself constitute a dispatch evaluation requiring the same
# campaign-execution authorization `execute_campaign` is gated behind (see
# this module's own module-docstring GOVERNANCE STATUS section) -- nothing
# below grants, implies, or bypasses that.


class N6RecedingHorizonForecastAdapter:
    """
    Receding-horizon implementation of `ForecastProviderProtocol`
    (`.predict(origin, step_index, context) -> Dict[str, Any]`). Unlike
    `N6ForecastProviderAdapter` above (which calls the real engine ONCE per
    origin and caches), this adapter calls the injected real forecast
    engine's `.predict(station_state, context)` FRESH every single call --
    no bundle is ever cached or reused across steps -- mirroring
    `worker.py`/`runner.py`'s per-step `forecast_engine.predict(...)` call.

    Requires `context["state"]` (the CURRENT simulated station state for
    this step) to be present -- `harness.py`'s `execute_origin_dispatch_cell`
    now supplies this automatically every iteration (IA-2's StationState
    -handoff fix, Section 5). Raises (fails closed) if it is absent, rather
    than reusing a stale prior-step state or fabricating one.

    Requires the caller to supply a PER-STEP feature matrix
    (`feature_matrix_by_origin_and_step: Dict[str, List[Any]]`), indexed
    strictly by the CURRENT `step_index` -- this adapter never looks ahead
    to a later step's entry and never reuses an earlier step's entry for a
    later one, so it cannot leak future information across steps merely by
    construction; it is the caller's responsibility (never this adapter's)
    to ensure each per-step entry itself was built from only
    information available at that step.
    """

    def __init__(
        self,
        real_forecast_engine: Any,
        station_state_cls: Any,
        feature_matrix_by_origin_and_step: Dict[str, List[Any]],
    ) -> None:
        self._engine = real_forecast_engine
        self._station_state_cls = station_state_cls
        self._feature_matrix_by_origin_and_step = feature_matrix_by_origin_and_step

    def predict(self, origin: str, step_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        if origin not in self._feature_matrix_by_origin_and_step:
            raise ValueError(
                f"Fail-closed: no N6 per-step feature matrix supplied for origin '{origin}' -- "
                "this adapter never synthesizes one."
            )
        steps = self._feature_matrix_by_origin_and_step[origin]
        if step_index >= len(steps):
            raise ValueError(
                f"Fail-closed: no N6 feature matrix supplied for origin '{origin}' at step "
                f"{step_index} (only {len(steps)} step(s) supplied)."
            )
        if "state" not in context:
            raise ValueError(
                f"Fail-closed: no 'state' key in context at step {step_index} for origin '{origin}' -- "
                "N6RecedingHorizonForecastAdapter requires the CURRENT simulated StationState every step."
            )
        real_station_state = StationStateCodec.from_plain_dict(context["state"], self._station_state_cls)
        raw_bundle = self._engine.predict(real_station_state, {"n6_feature_matrix": steps[step_index]})
        aligned_bundle = _align_n6_bundle_od02(raw_bundle, origin_timestamp_str=origin)
        # Under approved Decision OD-02-C, the bundle is aligned to simulator dispatch
        # steps (N6 rows 1..23 -> dispatch steps 0..22, with Candidate C.2 Clear-Sky
        # Ratio fallback at step 23). The freshly-aligned bundle's own hour 0 is raw row 1 (the
        # immediate next step's decision-relevant value).
        view = ForecastBundleStepView.step_view(aligned_bundle, 0)
        view["origin"] = origin
        view["step_index"] = step_index
        view["_real_bundle_ref"] = aligned_bundle
        view["_real_station_state_ref"] = real_station_state
        return view


class N6RecedingHorizonRouterAdapter:
    """
    Receding-horizon implementation of `RouterProtocol`
    (`.evaluate_and_route(state, forecast, controller_settings) -> Dict[str, Any]`).
    Calls the injected real router's `.evaluate_and_route(station_state, bundle,
    configs)` FRESH every step -- no caching -- mirroring `worker.py`/
    `runner.py`'s per-step `router.evaluate_and_route(...)` call, confirmed
    by direct read this pass.

    Returns `{"route": ..., "origin": ..., "_real_assessment_ref": ...}` --
    the route is validated against `VALID_ROUTES` (fail-closed on anything
    else) before being returned, so `execute_origin_dispatch_cell` never has
    to special-case an adapter-level invalid value separately from a
    genuinely-invalid real router response.
    """

    def __init__(self, real_router: Any, configs_by_origin: Dict[str, Dict[str, Any]]) -> None:
        self._router = real_router
        self._configs_by_origin = configs_by_origin

    def evaluate_and_route(
        self, state: Dict[str, Any], forecast: Dict[str, Any], controller_settings: Any
    ) -> Dict[str, Any]:
        origin = forecast.get("origin")
        if origin is None:
            raise ValueError("Fail-closed: forecast dict carries no 'origin' key; cannot route.")
        if origin not in self._configs_by_origin:
            raise ValueError(
                f"Fail-closed: no microgrid subsystem config supplied for origin '{origin}' -- "
                "this adapter never synthesizes a configuration."
            )
        bundle = forecast.get("_real_bundle_ref")
        if bundle is None:
            raise ValueError(
                "Fail-closed: forecast dict carries no '_real_bundle_ref' -- "
                "N6RecedingHorizonRouterAdapter must be paired with N6RecedingHorizonForecastAdapter "
                "(or an equivalent that supplies the real ForecastBundle reference)."
            )
        real_station_state = forecast.get("_real_station_state_ref") or state.get("_real_station_state_ref")
        if real_station_state is None:
            raise ValueError(
                "Fail-closed: neither forecast nor state dict carries '_real_station_state_ref'."
            )
        configs = self._configs_by_origin[origin]
        assessment, route = self._router.evaluate_and_route(real_station_state, bundle, configs)
        if route not in VALID_ROUTES:
            raise ValueError(
                f"Fail-closed: real router returned unrecognized route '{route}' for origin '{origin}' -- "
                f"must be one of {sorted(VALID_ROUTES)}."
            )
        return {"route": route, "origin": origin, "_real_assessment_ref": assessment}


class N6RecedingHorizonOptimizerAdapter:
    """
    Receding-horizon implementation of `DispatchOptimizerProtocol`
    (`.optimize(state, forecast, controller_settings) -> Dict[str, Any]`).
    Branches on `forecast["route"]` (set by `execute_origin_dispatch_cell`
    from the paired `N6RecedingHorizonRouterAdapter`'s decision, per IA-2):
    `"NORMAL"` calls the injected real GAP19 optimizer's
    `.optimize(bundle, station_state, configs)`; `"EMERGENCY"` calls the
    injected real Option D solver's `.solve(assessment, bundle, station_state,
    configs)`, reading the real `EmergencyAssessment` from
    `forecast["_real_assessment_ref"]` (fails closed if absent). Calls its
    collaborator FRESH every step -- no caching -- mirroring `worker.py`'s
    Cell B `if route == "NORMAL": plan = self.optimizer.optimize(...) elif
    route == "EMERGENCY": plan = self.option_d_solver.solve(...)` branch,
    confirmed by direct read this pass. `"UNKNOWN_INVALID"` is never passed
    to this adapter in practice -- `execute_origin_dispatch_cell` halts the
    loop before calling `optimizer.optimize` for that route -- but this
    adapter still fails closed (raises) if it ever is, rather than silently
    defaulting to either solver.
    """

    def __init__(self, real_gap19_optimizer: Any, real_option_d_solver: Any, configs_by_origin: Dict[str, Dict[str, Any]]) -> None:
        self._gap19_optimizer = real_gap19_optimizer
        self._option_d_solver = real_option_d_solver
        self._configs_by_origin = configs_by_origin

    def optimize(self, state: Dict[str, Any], forecast: Dict[str, Any], controller_settings: Any) -> Dict[str, Any]:
        origin = forecast.get("origin")
        route = forecast.get("route")
        if origin is None or route is None:
            raise ValueError("Fail-closed: forecast dict carries no 'origin'/'route' key; cannot optimize.")
        if state.get("_has_fuel_failure", False) or state.get("_diesel_fuel_tracking_gap", False):
            raise RuntimeError(
                f"Fail-closed: cannot optimize origin '{origin}' when fuel failure or tracking gap is latched."
            )
        if origin not in self._configs_by_origin:
            raise ValueError(
                f"Fail-closed: no microgrid subsystem config supplied for origin '{origin}'."
            )
        bundle = forecast.get("_real_bundle_ref")
        real_station_state = forecast.get("_real_station_state_ref") or state.get("_real_station_state_ref")
        if bundle is None or real_station_state is None:
            raise ValueError(
                "Fail-closed: forecast dict missing '_real_bundle_ref'/'_real_station_state_ref'."
            )
        configs = self._configs_by_origin[origin]
        if route == "NORMAL":
            solver_configs = _prepare_gap19_terminal_target_config(real_station_state, configs)
            solver_configs = _prepare_gap19_policy_b_config(bundle, solver_configs)
            plan = self._gap19_optimizer.optimize(bundle, real_station_state, solver_configs)
        elif route == "EMERGENCY":
            assessment = forecast.get("_real_assessment_ref")
            if assessment is None:
                raise ValueError(
                    "Fail-closed: EMERGENCY route requires the real EmergencyAssessment "
                    "('_real_assessment_ref') from the paired router adapter; none was supplied."
                )
            plan = self._option_d_solver.solve(assessment, bundle, real_station_state, configs)
        else:
            raise ValueError(
                f"Fail-closed: N6RecedingHorizonOptimizerAdapter cannot optimize for route '{route}' "
                f"(origin '{origin}') -- only 'NORMAL'/'EMERGENCY' are ever expected to reach this adapter."
            )
        return {"origin": origin, "route": route, "_real_plan_ref": plan}


class RecedingHorizonPlanSlicingSimulatorAdapter:
    """
    Receding-horizon implementation of `SimulationStepperProtocol`
    (`.step(state, dispatch_plan) -> Dict[str, Any]`). Unlike
    `SingleShotPlanSlicingSimulatorAdapter` above (which slices a SINGLE
    cached 24h plan at an ever-increasing hour index), this adapter ALWAYS
    applies HOUR INDEX 0 of whichever plan it is given, because a
    receding-horizon optimizer re-solves a brand-new plan every step whose
    hour 0 IS the decision for the CURRENT step -- mirrors `worker.py`/
    `runner.py` applying only `plan.diesel_power[0]` /
    `plan.battery_charge[0]` / `plan.battery_discharge[0]` from each freshly
    -solved plan before stepping the simulator and moving to the next
    iteration's fresh forecast/route/optimize call, confirmed by direct read
    this pass.

    Requires the caller to supply `actuals_by_origin_and_step` (already
    -known ground-truth values per origin/step) -- never fabricates a
    ground-truth actual, identical fail-closed rule to
    `SingleShotPlanSlicingSimulatorAdapter`.
    """

    @classmethod
    def from_authoritative_fixture(
        cls,
        real_simulator: Any,
        dispatch_plan_cls: Any,
        fixture_path: Path | str = CANONICAL_FIXTURE_RELATIVE_PATH,
        origins: Sequence[str] = (),
        steps_per_origin: int = 24,
        verify_sha256: bool = True,
    ) -> RecedingHorizonPlanSlicingSimulatorAdapter:
        actuals = load_authoritative_actuals_by_origin(
            fixture_path=fixture_path,
            origins=origins,
            steps_per_origin=steps_per_origin,
            verify_sha256=verify_sha256,
        )
        return cls(
            real_simulator=real_simulator,
            dispatch_plan_cls=dispatch_plan_cls,
            actuals_by_origin_and_step=actuals,
            _allow_synthetic_actuals_for_testing=True,
        )

    def __init__(
        self,
        real_simulator: Any,
        dispatch_plan_cls: Any,
        actuals_by_origin_and_step: Dict[str, List[Dict[str, Any]]],
        _allow_synthetic_actuals_for_testing: bool = False,
    ) -> None:
        if not _allow_synthetic_actuals_for_testing and not getattr(actuals_by_origin_and_step, "_is_authoritative_actuals", False):
            raise ValueError(
                "Fail-closed: direct construction of RecedingHorizonPlanSlicingSimulatorAdapter with "
                "unverified actuals is prohibited. Use RecedingHorizonPlanSlicingSimulatorAdapter.from_authoritative_fixture() "
                "or pass _allow_synthetic_actuals_for_testing=True for synthetic tests."
            )
        self._simulator = real_simulator
        self._dispatch_plan_cls = dispatch_plan_cls
        self._actuals_by_origin_and_step = actuals_by_origin_and_step

    def step(self, state: Dict[str, Any], dispatch_plan: Dict[str, Any]) -> Dict[str, Any]:
        origin = dispatch_plan.get("origin")
        real_plan = dispatch_plan.get("_real_plan_ref")
        if origin is None or real_plan is None:
            raise ValueError(
                "Fail-closed: dispatch_plan dict carries no 'origin'/'_real_plan_ref' -- "
                "RecedingHorizonPlanSlicingSimulatorAdapter must be paired with "
                "N6RecedingHorizonOptimizerAdapter."
            )
        step_index = state.get("_step_index")
        if step_index is None:
            raise ValueError("Fail-closed: state dict carries no '_step_index'; caller must track it explicitly.")
        real_station_state = state.get("_real_station_state_ref")
        if real_station_state is None:
            raise ValueError("Fail-closed: state dict carries no '_real_station_state_ref'.")
        if origin not in self._actuals_by_origin_and_step or step_index >= len(self._actuals_by_origin_and_step[origin]):
            raise ValueError(
                f"Fail-closed: no ground-truth actual supplied for origin '{origin}' step {step_index} -- "
                "this adapter never fabricates a ground-truth value."
            )
        actual_t = self._actuals_by_origin_and_step[origin][step_index]

        # Hour index 0 ALWAYS -- this plan was solved fresh THIS step, so
        # its own hour 0 is the current step's decision (never `step_index`,
        # which would misread a receding-horizon plan as if it were the one
        # single-shot cached plan the sibling adapter slices).
        one_hour_slice = self._dispatch_plan_cls(
            schema_version=real_plan.schema_version,
            timestamps=[real_plan.timestamps[0]] * 24,
            solar_used=[real_plan.solar_used[0]] * 24,
            wind_used=[real_plan.wind_used[0]] * 24,
            battery_charge=[real_plan.battery_charge[0]] * 24,
            battery_discharge=[real_plan.battery_discharge[0]] * 24,
            battery_soc=[real_plan.battery_soc[0]] * 24,
            diesel_power=[real_plan.diesel_power[0]] * 24,
            load_served=[real_plan.load_served[0]] * 24,
            flexible_load_schedule=[real_plan.flexible_load_schedule[0]] * 24,
            renewable_curtailment=[real_plan.renewable_curtailment[0]] * 24,
            unmet_load=[real_plan.unmet_load[0]] * 24,
            objective_value=real_plan.objective_value,
            constraint_status=real_plan.constraint_status,
            energy_balance_errors=[0.0] * 24,
        )

        # 1. Authoritative Diesel Power Validation Before Step (BLOCKER-FUEL-1)
        p_diesel_raw = real_plan.diesel_power[0]
        p_diesel_valid = (
            p_diesel_raw is not None
            and not isinstance(p_diesel_raw, bool)
            and isinstance(p_diesel_raw, (int, float))
            and not math.isnan(p_diesel_raw)
            and not math.isinf(p_diesel_raw)
            and p_diesel_raw >= 0.0
        )
        p_diesel_val = float(p_diesel_raw) if p_diesel_valid else 0.0
        is_diesel_dispatched = (p_diesel_val > 0.0)

        # 2. Authoritative Fuel State Validation Before Step (BLOCKER-FUEL-1)
        fuel_before = getattr(real_station_state, "diesel_fuel_remaining_liters", None)
        fuel_before_valid = (
            fuel_before is not None
            and not isinstance(fuel_before, bool)
            and isinstance(fuel_before, (int, float))
            and not math.isnan(fuel_before)
            and not math.isinf(fuel_before)
            and fuel_before >= 0.0
        )

        # Simulator physical fuel curve: base_fuel_lph = 5.0, marginal_fuel_lpwh = 0.00025
        required_fuel = ((5.0 if is_diesel_dispatched else 0.0) + (0.00025 * p_diesel_val)) * 1.0
        fuel_after_est = round(fuel_before - required_fuel, 4) if (fuel_before_valid and p_diesel_valid) else None

        # Pre-call fuel guards (CRIT-01): reject and latch BEFORE calling self._simulator.step()
        pre_fuel_failure_reason = None
        has_pre_fuel_failure = False

        if state.get("_diesel_fuel_tracking_gap", False) or state.get("_has_fuel_failure", False):
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"
        elif not p_diesel_valid:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"INVALID_DIESEL_POWER: diesel power must be a non-negative finite number (got {p_diesel_raw})"
            )
        elif not fuel_before_valid:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_ACCOUNTING_INVALID: missing, non-numeric, non-finite, or negative fuel observation "
                f"(before={fuel_before})"
            )
        elif fuel_before <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: fuel ({fuel_before:.6f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )
        elif required_fuel > fuel_before:  # Zero-slack check
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTION_CLAMPED: required fuel {required_fuel:.4f} L exceeds available fuel {fuel_before:.4f} L"
            )
        elif fuel_after_est is not None and fuel_after_est <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_pre_fuel_failure = True
            pre_fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: fuel after consumption ({fuel_after_est:.6f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )

        if has_pre_fuel_failure:
            # Under pre-call failure, self._simulator.step() is NEVER invoked.
            # On an aborted trajectory, do not fabricate terminal energy/SOC deltas,
            # generator starts, or startup surcharges as zero. Mark unavailable metrics as None
            # and invalidate the run.
            if step_index == 0:
                init_soc = float(getattr(real_station_state, "battery_soc_pct", 0.0))
                init_energy = float(getattr(real_station_state, "battery_energy_wh", 0.0))
            else:
                init_soc = state.get("_initial_battery_soc_pct")
                init_energy = state.get("_initial_battery_energy_wh")

            next_state_dict = StationStateCodec.to_plain_dict(real_station_state)
            next_state_dict["_real_station_state_ref"] = real_station_state
            next_state_dict["_step_index"] = step_index
            next_state_dict["_cumulative_generator_starts"] = None
            next_state_dict["_startup_surcharge_liters"] = None
            next_state_dict["_initial_battery_soc_pct"] = init_soc
            next_state_dict["_initial_battery_energy_wh"] = init_energy
            next_state_dict["_terminal_battery_soc_pct"] = None
            next_state_dict["_terminal_battery_energy_wh"] = None
            next_state_dict["_delta_e_term_wh"] = None
            next_state_dict["_diesel_fuel_tracking_gap"] = True
            next_state_dict["_has_fuel_failure"] = True
            next_state_dict["_fuel_failure_reason"] = pre_fuel_failure_reason
            next_state_dict["_cumulative_diesel_consumed_liters"] = None

            return {
                "state": next_state_dict,
                "dispatch_outcome": DispatchOutcomeView.at_hour(
                    real_plan,
                    0,
                    fuel_consumed_liters_this_hour=None,
                    cumulative_diesel_consumed_liters=None,
                    generator_starts=None,
                    initial_battery_soc_pct=init_soc,
                    terminal_battery_soc_pct=None,
                    initial_battery_energy_wh=init_energy,
                    terminal_battery_energy_wh=None,
                    delta_e_term_wh=None,
                    startup_surcharge_liters=None,
                    has_fuel_failure=True,
                    fuel_failure_reason=pre_fuel_failure_reason,
                ),
                "stop_early": True,
            }

        # Step simulator ONLY after pre-call validation passes
        next_real_state = self._simulator.step(real_station_state, one_hour_slice, actual_t)

        # 3. Authoritative Fuel State Validation After Step (BLOCKER-FUEL-1 defense-in-depth)
        fuel_after = getattr(next_real_state, "diesel_fuel_remaining_liters", None)
        fuel_after_valid = (
            fuel_after is not None
            and not isinstance(fuel_after, bool)
            and isinstance(fuel_after, (int, float))
            and not math.isnan(fuel_after)
            and not math.isinf(fuel_after)
            and fuel_after >= 0.0
        )

        fuel_failure_reason = None
        has_fuel_failure = False

        if not fuel_after_valid:
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_ACCOUNTING_INVALID: missing or non-finite fuel observation after step "
                f"(after={fuel_after})"
            )
        elif fuel_after > fuel_before:  # Zero-slack monotonicity check
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_MONOTONICITY_VIOLATED: fuel increased from {fuel_before:.4f} L to {fuel_after:.4f} L"
            )
        elif fuel_after <= FUEL_EXHAUSTION_THRESHOLD_L:
            has_fuel_failure = True
            fuel_failure_reason = (
                f"FUEL_EXHAUSTED_AT_STEP: remaining fuel ({fuel_after:.4f} L) <= threshold ({FUEL_EXHAUSTION_THRESHOLD_L} L)"
            )

        # Check for pre-existing latched failure from prior steps
        had_fuel_gap = state.get("_diesel_fuel_tracking_gap", False) or state.get("_has_fuel_failure", False)
        if had_fuel_gap or has_fuel_failure:
            fuel_gap_active = True
            cumulative_fuel = None
            step_consumed = None
            latched_reason = fuel_failure_reason or state.get("_fuel_failure_reason") or "FUEL_TRACKING_GAP_LATCHED"
        else:
            fuel_gap_active = False
            latched_reason = None
            step_consumed = (
                max(0.0, fuel_before - fuel_after) if (fuel_before is not None and fuel_after is not None) else None
            )
            prev_cumulative = state.get("_cumulative_diesel_consumed_liters")
            cumulative_fuel = round((0.0 if prev_cumulative is None else prev_cumulative) + (step_consumed or 0.0), 6)

        # 4. Generator Start Counting via diesel_running boolean transition
        was_running = bool(getattr(real_station_state, "diesel_running", False))
        is_running_now = bool(getattr(next_real_state, "diesel_running", False))
        is_start = (is_running_now and not was_running)
        prev_starts = state.get("_cumulative_generator_starts", 0)
        cumulative_starts = prev_starts + (1 if is_start else 0)
        startup_surcharge_liters = float(cumulative_starts) * 6.0

        # 5. Authoritative Battery State Tracking (SOC and Energy)
        if step_index == 0:
            init_soc = float(getattr(real_station_state, "battery_soc_pct", 0.0))
            init_energy = float(getattr(real_station_state, "battery_energy_wh", 0.0))
        else:
            init_soc = state.get("_initial_battery_soc_pct")
            init_energy = state.get("_initial_battery_energy_wh")

        term_soc = float(getattr(next_real_state, "battery_soc_pct", 0.0))
        term_energy = float(getattr(next_real_state, "battery_energy_wh", 0.0))
        delta_e = round(term_energy - init_energy, 4) if init_energy is not None else None

        if fuel_gap_active:
            cumulative_starts = None
            startup_surcharge_liters = None
            term_soc = None
            term_energy = None
            delta_e = None

        next_state_dict = StationStateCodec.to_plain_dict(next_real_state)
        next_state_dict["_real_station_state_ref"] = next_real_state
        next_state_dict["_step_index"] = step_index + 1
        next_state_dict["_cumulative_generator_starts"] = cumulative_starts
        next_state_dict["_startup_surcharge_liters"] = startup_surcharge_liters
        next_state_dict["_initial_battery_soc_pct"] = init_soc
        next_state_dict["_initial_battery_energy_wh"] = init_energy
        next_state_dict["_terminal_battery_soc_pct"] = term_soc
        next_state_dict["_terminal_battery_energy_wh"] = term_energy
        next_state_dict["_delta_e_term_wh"] = delta_e

        if fuel_gap_active:
            next_state_dict["_diesel_fuel_tracking_gap"] = True
            next_state_dict["_has_fuel_failure"] = True
            next_state_dict["_fuel_failure_reason"] = latched_reason
            next_state_dict["_cumulative_diesel_consumed_liters"] = None
        else:
            next_state_dict["_cumulative_diesel_consumed_liters"] = cumulative_fuel

        return {
            "state": next_state_dict,
            "dispatch_outcome": DispatchOutcomeView.at_hour(
                real_plan,
                0,
                fuel_consumed_liters_this_hour=step_consumed,
                cumulative_diesel_consumed_liters=cumulative_fuel,
                generator_starts=cumulative_starts,
                initial_battery_soc_pct=init_soc,
                terminal_battery_soc_pct=term_soc,
                initial_battery_energy_wh=init_energy,
                terminal_battery_energy_wh=term_energy,
                delta_e_term_wh=delta_e,
                startup_surcharge_liters=startup_surcharge_liters,
                has_fuel_failure=fuel_gap_active,
                fuel_failure_reason=latched_reason,
            ),
            "stop_early": fuel_gap_active,
        }
