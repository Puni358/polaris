"""
POLARIS — Reserve/EBR Safety-Policy Validation & Enforcement
================================================================
N6 Operational Readiness Remediation, Section 4.

GOVERNANCE STATUS: NON-PRODUCTION VALIDATION LAYER
- Does NOT modify `system/optimization/implementations/gap19_highs_native.py`
  (a PROTECTED_FILES entry per `system/orchestration/manifest.py`), nor any
  other protected/frozen file. This module is a separate, additive,
  post-hoc validation layer that inspects a DispatchPlan-shaped result
  (or an equivalent dict) and the governed reserve configuration already
  computed by GAP19, WITHOUT altering how GAP19 solves.
- Does NOT invent a new reserve multiplier, does NOT claim the existing
  15 kWh EBR floor alone guarantees safety, and does NOT change the
  production reserve policy. Several thresholds below are explicitly
  marked `AUTHORIZATION_REQUIRED` because this repository does not
  currently contain a formally authorized numerical policy for them (see
  the research findings in `forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md`
  Section 5/7): calling the corresponding check without supplying an
  explicit, caller-provided authorization raises `AuthorizationRequiredError`
  rather than silently assuming a default is safe.

WHY THIS MODULE EXISTS (root cause this addresses):
Per-run evaluation code (`system/evaluation/evaluator.py`,
`system/orchestration/worker.py`) was found during remediation research to
NOT surface per-step critical-unmet-load or reserve-shortfall at all: a
dispatch can report `constraint_status == "OPTIMAL"` while critical load was
actually unmet and/or the governed EBR/terminal reserve was violated via the
slack variable `s_J2`, because nothing downstream reads `j1_objective`,
`j2_objective`, `reserve_shortfall`, or `unmet_essential`. This is exactly the
failure mode documented for historical Arm A_FIX: an 11.23% diesel reduction
that was accompanied by a ~47.2% INCREASE in critical unmet energy -- a
serious reserve-policy failure that a diesel-liters-only report would hide.
This module gives any caller (evaluator, worker, future replay harness) an
explicit, fail-closed way to detect that failure mode BEFORE it is reported
as a win.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

__all__ = [
    "ReservePolicyViolation",
    "AuthorizationRequiredError",
    "SafetyEvaluationResult",
    "SAFETY_GATE_REGISTRY",
    "validate_hard_soc_floor",
    "validate_reserve_units_consistent",
    "assert_no_double_netting",
    "compute_bounded_solar_credit",
    "evaluate_dispatch_safety",
    "detect_reserve_regression_vs_baseline",
]


class ReservePolicyViolation(Exception):
    """Raised when a dispatch result violates an enforced (authorized) reserve/safety rule."""


class AuthorizationRequiredError(Exception):
    """
    Raised when a check depends on a numerical threshold or policy decision
    that has not been formally authorized in this repository. Fail-closed:
    the caller must obtain explicit authorization and pass it in, rather
    than this module silently assuming a "reasonable" default.
    """


@dataclass(frozen=True)
class SafetyGateDefinition:
    name: str
    description: str
    authorized: bool
    proposed_threshold_note: str


# Registry of safety gates discussed in prior POLARIS audits. Per Section 7
# of the remediation protocol, these are PROPOSED thresholds, not existing
# governance requirements, until the repository's governance owner formally
# authorizes them. This registry exists so reporting code can clearly
# distinguish "proposed" from "authorized" -- none of these are flipped to
# authorized=True by this remediation pass.
SAFETY_GATE_REGISTRY: Dict[str, SafetyGateDefinition] = {
    "critical_unmet_not_worse_than_baseline": SafetyGateDefinition(
        name="critical_unmet_not_worse_than_baseline",
        description="Candidate critical unmet load must not exceed baseline (Control).",
        authorized=False,
        proposed_threshold_note="AUTHORIZATION_REQUIRED: proposed in prior audit, not formally authorized.",
    ),
    "unserved_energy_origin_failure_rate": SafetyGateDefinition(
        name="unserved_energy_origin_failure_rate",
        description="Candidate must not increase unserved energy in more than 5% of origins.",
        authorized=False,
        proposed_threshold_note="AUTHORIZATION_REQUIRED: proposed 5% ceiling, not formally authorized.",
    ),
    "diesel_savings_significance": SafetyGateDefinition(
        name="diesel_savings_significance",
        description="Diesel savings must exceed 2% with p < 0.01.",
        authorized=False,
        proposed_threshold_note="AUTHORIZATION_REQUIRED: proposed statistical gate, not formally authorized.",
    ),
    "critical_service_ratio_floor": SafetyGateDefinition(
        name="critical_service_ratio_floor",
        description="Critical service ratio must exceed 99.95%.",
        authorized=False,
        proposed_threshold_note="AUTHORIZATION_REQUIRED: proposed floor, not formally authorized; no "
        "'critical_service_ratio' metric currently exists in production evaluator code.",
    ),
}


@dataclass
class SafetyEvaluationResult:
    passed: bool
    hard_soc_violation: bool
    reserve_shortfall_total_wh: Optional[float]
    reserve_violation: bool
    critical_unmet_total_wh: Optional[float]
    solver_infeasible: bool
    failure_reasons: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def validate_hard_soc_floor(
    battery_soc_wh: Sequence[float], min_e_wh: float, tolerance_wh: float = 1e-3
) -> None:
    """
    Validates that the battery energy trajectory never drops below the
    governed hard minimum SOC floor. This mirrors the GAP19 variable-bound
    enforcement (`lb[base+6] = min_e_wh`) as an independent, out-of-band
    check -- useful when validating a plan produced by ANY optimizer/path,
    not just the protected GAP19 implementation itself.
    """
    violations = [
        (i, v) for i, v in enumerate(battery_soc_wh) if v < (min_e_wh - tolerance_wh)
    ]
    if violations:
        raise ReservePolicyViolation(
            f"Fail-closed: battery energy dropped below governed hard minimum SOC floor "
            f"({min_e_wh} Wh) at timesteps {[i for i, _ in violations]}: values {[v for _, v in violations]}"
        )


def validate_reserve_units_consistent(
    quantity_name: str, value: float, unit: str, expected_unit: str = "Wh"
) -> None:
    """
    Fails closed if a reserve-related quantity is tagged with a unit other
    than the expected one. Guards against the Wh/kWh/W/energy-over-interval
    mixing risk identified in `gap19_highs_native.py` (J1 uses power*dt,
    J2 uses a raw energy slack with no dt) by requiring every caller of
    this guard to explicitly state units rather than assume them.
    """
    if unit != expected_unit:
        raise ReservePolicyViolation(
            f"Fail-closed: reserve quantity '{quantity_name}' declared unit '{unit}', "
            f"expected '{expected_unit}'. Refusing to proceed with an ambiguous/mixed-unit "
            f"reserve calculation (value={value})."
        )


def assert_no_double_netting(
    lower_bound_applied_to_reserve_target: bool,
    lower_bound_applied_to_dispatch_objective: bool,
    lower_bound_applied_to_solar_credit: bool,
) -> None:
    """
    Fails closed if the SAME forecast lower-bound/uncertainty value appears
    to be netted into more than one of: the reserve target, the dispatch
    objective, and a solar-credit reduction. Each of these is a legitimate
    standalone use; applying the same uncertainty-derived quantity in more
    than one of them simultaneously, without an explicit reconciliation,
    risks double-counting (making the dispatch look safer, or less safe,
    than it actually is).
    """
    applied_count = sum(
        [
            bool(lower_bound_applied_to_reserve_target),
            bool(lower_bound_applied_to_dispatch_objective),
            bool(lower_bound_applied_to_solar_credit),
        ]
    )
    if applied_count > 1:
        raise ReservePolicyViolation(
            "Fail-closed: forecast lower-bound/uncertainty value appears applied in more than one "
            "of {reserve_target, dispatch_objective, solar_credit} simultaneously "
            f"(applied_count={applied_count}). This risks inconsistent double-netting of uncertainty."
        )


def compute_bounded_solar_credit(
    forecast_lower_wh: float,
    uncertainty_is_valid: bool,
    forecast_is_fresh: bool,
    authorized_max_credit_fraction: Optional[float],
    governed_reserve_target_wh: float,
) -> float:
    """
    Computes a reserve credit derived from a solar forecast lower bound,
    BOUNDED by an explicitly authorized maximum fraction of the governed
    reserve target, and validated against uncertainty validity/freshness.

    Fail-closed behavior (Section 4.5-4.6 of the remediation protocol):
    - If `authorized_max_credit_fraction` is None, this function refuses to
      guess a safe default and raises `AuthorizationRequiredError`. No solar
      credit may be authorized implicitly.
    - If the uncertainty estimate is invalid or the forecast is stale
      (not fresh), the credit is forced to 0.0 -- an invalid/missing
      uncertainty estimate can NEVER silently produce a reserve reduction.
    - The returned credit is always clamped to
      `[0, authorized_max_credit_fraction * governed_reserve_target_wh]`,
      so even a valid, fresh forecast cannot authorize an unbounded credit.
    """
    if authorized_max_credit_fraction is None:
        raise AuthorizationRequiredError(
            "Fail-closed: no authorized_max_credit_fraction supplied. Any solar credit to the "
            "reserve requirement must be explicitly bounded by a separately authorized policy "
            "before this function will compute a non-zero credit. Mark as AUTHORIZATION REQUIRED."
        )
    if authorized_max_credit_fraction < 0.0 or authorized_max_credit_fraction > 1.0:
        raise ReservePolicyViolation(
            f"Fail-closed: authorized_max_credit_fraction must be in [0, 1], got "
            f"{authorized_max_credit_fraction}."
        )
    if not uncertainty_is_valid or not forecast_is_fresh:
        return 0.0
    if forecast_lower_wh < 0.0:
        raise ReservePolicyViolation(
            f"Fail-closed: forecast_lower_wh must be non-negative, got {forecast_lower_wh}."
        )

    max_credit_wh = authorized_max_credit_fraction * governed_reserve_target_wh
    return float(max(0.0, min(forecast_lower_wh, max_credit_wh)))


def evaluate_dispatch_safety(
    plan: Dict[str, object],
    min_e_wh: Optional[float] = None,
    reserve_shortfall_authorization_wh: Optional[float] = None,
) -> SafetyEvaluationResult:
    """
    Evaluates a DispatchPlan-shaped dict (accepts either a `DispatchPlan`
    instance via `.to_dict()`-like access, or a plain dict with the same
    keys) for the safety properties required by Section 4 of the
    remediation protocol:
      1. Hard battery SOC floor is respected (if `battery_soc` and
         `min_e_wh` are supplied).
      2. Solver infeasibility is explicitly surfaced, never hidden.
      3. Critical unmet load (`unmet_essential` if present, else a
         conservative fallback onto `unmet_load` with a note that the
         critical-specific signal was unavailable) is surfaced as a
         number, not silently dropped.
      4. Reserve shortfall (`reserve_shortfall`) is surfaced; if a
         `reserve_shortfall_authorization_wh` ceiling is supplied, values
         exceeding it are flagged as a violation. If no ceiling is
         supplied, the shortfall is still reported, but `reserve_violation`
         is left False with a note that no ceiling is authorized yet
         (fail-closed on the GATE, not on the computation) -- the caller is
         responsible for treating "no ceiling authorized" as "do not
         promote," per Section 4's closing guidance, not as "pass."

    This function never raises on an unsafe VALUE -- it reports the
    violation structurally in the returned `SafetyEvaluationResult` so that
    the caller (which may be an evaluator, a report generator, or a human)
    can decide how to act. It DOES raise (`ReservePolicyViolation`) only if
    the hard SOC floor is violated, because that is an unconditionally
    enforced physical constraint, never a policy judgment call.
    """
    failure_reasons: List[str] = []
    notes: List[str] = []

    constraint_status = str(plan.get("constraint_status", ""))
    solver_infeasible = constraint_status.startswith("OPTIMIZATION_INFEASIBLE")
    if solver_infeasible:
        failure_reasons.append(f"solver_infeasible: {constraint_status}")

    hard_soc_violation = False
    battery_soc = plan.get("battery_soc")
    if battery_soc is not None and min_e_wh is not None:
        try:
            validate_hard_soc_floor(battery_soc, min_e_wh)
        except ReservePolicyViolation:
            hard_soc_violation = True
            raise
    else:
        notes.append("hard_soc_floor_check_skipped: battery_soc or min_e_wh not supplied")

    unmet_essential = plan.get("unmet_essential")
    if unmet_essential is not None:
        critical_unmet_total_wh = float(sum(unmet_essential))
    else:
        unmet_load = plan.get("unmet_load")
        if unmet_load is not None:
            critical_unmet_total_wh = float(sum(unmet_load))
            notes.append(
                "critical_unmet_total_wh falls back to TOTAL unmet_load because 'unmet_essential' "
                "was not present on this plan -- this OVER-COUNTS non-critical shortfalls and is a "
                "known evaluator gap (see forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md Section 4)."
            )
        else:
            critical_unmet_total_wh = None
            notes.append("critical_unmet_total_wh unavailable: neither 'unmet_essential' nor 'unmet_load' present")
    if critical_unmet_total_wh and critical_unmet_total_wh > 0.0:
        failure_reasons.append(f"nonzero_critical_unmet_energy_wh: {critical_unmet_total_wh}")

    reserve_shortfall = plan.get("reserve_shortfall")
    reserve_shortfall_total_wh = (
        float(sum(reserve_shortfall)) if reserve_shortfall is not None else None
    )
    reserve_violation = False
    if reserve_shortfall is not None:
        if reserve_shortfall_authorization_wh is not None:
            reserve_violation = reserve_shortfall_total_wh > reserve_shortfall_authorization_wh
            if reserve_violation:
                failure_reasons.append(
                    f"reserve_shortfall_total_wh {reserve_shortfall_total_wh} exceeds authorized "
                    f"ceiling {reserve_shortfall_authorization_wh}"
                )
        else:
            notes.append(
                "reserve_shortfall_authorization_wh not supplied: AUTHORIZATION_REQUIRED before this "
                "gate can be formally evaluated; shortfall is reported for visibility only."
            )
    else:
        notes.append("reserve_shortfall not present on plan; cannot evaluate governed-reserve-policy gate.")

    passed = not failure_reasons

    return SafetyEvaluationResult(
        passed=passed,
        hard_soc_violation=hard_soc_violation,
        reserve_shortfall_total_wh=reserve_shortfall_total_wh,
        reserve_violation=reserve_violation,
        critical_unmet_total_wh=critical_unmet_total_wh,
        solver_infeasible=solver_infeasible,
        failure_reasons=failure_reasons,
        notes=notes,
    )


def detect_reserve_regression_vs_baseline(
    baseline_critical_unmet_wh: float,
    candidate_critical_unmet_wh: float,
    baseline_diesel_l: float,
    candidate_diesel_l: float,
) -> Dict[str, object]:
    """
    Implements, as a PROPOSED (not authorized) gate, the exact failure mode
    documented for historical Arm A_FIX: a diesel reduction accompanied by
    an increase in critical unmet load. Returns a structured result; never
    silently hides a regression behind an attractive fuel number.

    This directly operationalizes
    `SAFETY_GATE_REGISTRY["critical_unmet_not_worse_than_baseline"]`
    (authorized=False) so a caller can see both the computed outcome and
    the fact that the gate itself is not yet formally authorized.
    """
    diesel_saved_l = baseline_diesel_l - candidate_diesel_l
    diesel_saved_pct = (diesel_saved_l / baseline_diesel_l * 100.0) if baseline_diesel_l else 0.0
    unmet_increase_wh = candidate_critical_unmet_wh - baseline_critical_unmet_wh
    unmet_increase_pct = (
        (unmet_increase_wh / baseline_critical_unmet_wh * 100.0) if baseline_critical_unmet_wh else float("inf")
    )
    is_arm_a_fix_pattern = diesel_saved_l > 0 and unmet_increase_wh > 0

    return {
        "gate": SAFETY_GATE_REGISTRY["critical_unmet_not_worse_than_baseline"],
        "diesel_saved_l": diesel_saved_l,
        "diesel_saved_pct": diesel_saved_pct,
        "unmet_increase_wh": unmet_increase_wh,
        "unmet_increase_pct": unmet_increase_pct,
        "is_fuel_savings_masking_reliability_regression": is_arm_a_fix_pattern,
        "would_pass_proposed_gate": unmet_increase_wh <= 0,
        "gate_formally_authorized": False,
    }
