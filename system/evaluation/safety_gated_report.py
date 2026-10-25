"""
POLARIS — Safety-Gated Outcome Evaluation Reporting
======================================================
N6 Operational Readiness Remediation, Section 7.

GOVERNANCE STATUS: NON-PRODUCTION REPORTING LAYER
- Does not execute a dispatch campaign. Consumes already-computed
  per-origin results (e.g. from a future authorized Experiment A run) and
  assembles the required outcome report structure.
- Explicitly separates AUTHORIZED safety gates (none currently exist in
  this repository's production code -- see
  `system/safety/reserve_policy_guard.SAFETY_GATE_REGISTRY`, all entries
  `authorized=False`) from PROPOSED thresholds carried over from prior
  audits. A candidate is only ever reported as "FAILED_SAFETY_GATE" against
  an AUTHORIZED gate; proposed-gate outcomes are reported for visibility
  under a separate, clearly labeled section and never presented as a
  governance failure.
- Never silently drops a failed or adverse origin: `build_report` raises
  if the number of included per-origin results does not match the
  declared total number of origins attempted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from system.safety.reserve_policy_guard import SAFETY_GATE_REGISTRY

__all__ = [
    "OriginResult",
    "DroppedOriginError",
    "SafetyGatedOutcomeReport",
    "build_report",
    "REQUIRED_OUTCOME_FIELDS",
]

# The minimum set of fields Section 7 requires the evaluation code to report,
# per origin, at minimum.
REQUIRED_OUTCOME_FIELDS = (
    "diesel_liters",
    "critical_unmet_kwh",
    "critical_service_ratio",
    "reserve_violations",
    "reserve_slack_wh",
    "min_battery_soc_wh",
    "battery_throughput_kwh",
    "diesel_runtime_h",
    "diesel_starts",
    "solver_feasible",
    "solver_timed_out",
    "fallback_action",
)


class DroppedOriginError(Exception):
    """Raised when a report would silently exclude a failed/adverse origin."""


@dataclass
class OriginResult:
    origin_id: str
    diesel_liters: float
    critical_unmet_kwh: float
    total_demand_kwh: float
    reserve_violations: int
    reserve_slack_wh: float
    min_battery_soc_wh: float
    battery_throughput_kwh: Optional[float] = None
    equivalent_full_cycles: Optional[float] = None
    diesel_runtime_h: Optional[float] = None
    diesel_starts: Optional[int] = None
    solver_feasible: bool = True
    solver_timed_out: bool = False
    fallback_action: Optional[str] = None

    @property
    def critical_service_ratio(self) -> Optional[float]:
        if self.total_demand_kwh <= 0:
            return None
        return (self.total_demand_kwh - self.critical_unmet_kwh) / self.total_demand_kwh

    @property
    def is_adverse(self) -> bool:
        return (
            not self.solver_feasible
            or self.solver_timed_out
            or self.critical_unmet_kwh > 0
            or self.reserve_violations > 0
            or self.fallback_action is not None
        )


@dataclass
class SafetyGatedOutcomeReport:
    baseline_label: str
    candidate_label: str
    origin_results_baseline: List[OriginResult]
    origin_results_candidate: List[OriginResult]
    n_origins_attempted: int
    authorized_gate_results: Dict[str, str] = field(default_factory=dict)
    proposed_gate_results: Dict[str, str] = field(default_factory=dict)

    @property
    def total_diesel_baseline_l(self) -> float:
        return sum(o.diesel_liters for o in self.origin_results_baseline)

    @property
    def total_diesel_candidate_l(self) -> float:
        return sum(o.diesel_liters for o in self.origin_results_candidate)

    @property
    def diesel_diff_l(self) -> float:
        return self.total_diesel_baseline_l - self.total_diesel_candidate_l

    @property
    def diesel_diff_pct(self) -> Optional[float]:
        base = self.total_diesel_baseline_l
        return (self.diesel_diff_l / base * 100.0) if base else None

    @property
    def total_critical_unmet_baseline_kwh(self) -> float:
        return sum(o.critical_unmet_kwh for o in self.origin_results_baseline)

    @property
    def total_critical_unmet_candidate_kwh(self) -> float:
        return sum(o.critical_unmet_kwh for o in self.origin_results_candidate)

    @property
    def n_adverse_origins_candidate(self) -> int:
        return sum(1 for o in self.origin_results_candidate if o.is_adverse)

    @property
    def pct_origins_with_increased_unmet(self) -> Optional[float]:
        by_id_baseline = {o.origin_id: o for o in self.origin_results_baseline}
        n = len(self.origin_results_candidate)
        if n == 0:
            return None
        n_worse = 0
        for c in self.origin_results_candidate:
            b = by_id_baseline.get(c.origin_id)
            if b is not None and c.critical_unmet_kwh > b.critical_unmet_kwh:
                n_worse += 1
        return n_worse / n * 100.0

    def evaluate_gates(self) -> None:
        """
        Populates authorized_gate_results (always empty/'NOT_EVALUATED:
        no authorized gates exist in this repository') and
        proposed_gate_results (computed for visibility, never treated as
        a pass/fail governance decision).
        """
        self.authorized_gate_results = {
            name: "NOT_EVALUATED: gate not formally authorized in this repository"
            for name, gate in SAFETY_GATE_REGISTRY.items()
            if not gate.authorized
        }

        results: Dict[str, str] = {}

        unmet_gate = SAFETY_GATE_REGISTRY["critical_unmet_not_worse_than_baseline"]
        would_pass = self.total_critical_unmet_candidate_kwh <= self.total_critical_unmet_baseline_kwh
        results[unmet_gate.name] = (
            f"PROPOSED_GATE_{'WOULD_PASS' if would_pass else 'WOULD_FAIL'} "
            f"(candidate={self.total_critical_unmet_candidate_kwh:.2f} kWh, "
            f"baseline={self.total_critical_unmet_baseline_kwh:.2f} kWh)"
        )

        origin_fail_gate = SAFETY_GATE_REGISTRY["unserved_energy_origin_failure_rate"]
        pct_worse = self.pct_origins_with_increased_unmet
        if pct_worse is None:
            results[origin_fail_gate.name] = "PROPOSED_GATE_NOT_EVALUABLE: no origins"
        else:
            would_pass = pct_worse <= 5.0
            results[origin_fail_gate.name] = (
                f"PROPOSED_GATE_{'WOULD_PASS' if would_pass else 'WOULD_FAIL'} "
                f"({pct_worse:.1f}% of origins worse than baseline, proposed ceiling 5%)"
            )

        savings_gate = SAFETY_GATE_REGISTRY["diesel_savings_significance"]
        pct = self.diesel_diff_pct
        if pct is None:
            results[savings_gate.name] = "PROPOSED_GATE_NOT_EVALUABLE: no baseline diesel"
        else:
            would_pass = pct > 2.0
            results[savings_gate.name] = (
                f"PROPOSED_GATE_{'WOULD_PASS' if would_pass else 'WOULD_FAIL'}_ON_MAGNITUDE_ONLY "
                f"({pct:.2f}% savings; significance/p-value not computed here -- requires a real "
                f"paired statistical test over executed origins, not a single aggregate)"
            )

        csr_gate = SAFETY_GATE_REGISTRY["critical_service_ratio_floor"]
        ratios = [o.critical_service_ratio for o in self.origin_results_candidate if o.critical_service_ratio is not None]
        if not ratios:
            results[csr_gate.name] = "PROPOSED_GATE_NOT_EVALUABLE: no critical_service_ratio data"
        else:
            min_ratio = min(ratios)
            would_pass = min_ratio > 0.9995
            results[csr_gate.name] = (
                f"PROPOSED_GATE_{'WOULD_PASS' if would_pass else 'WOULD_FAIL'} "
                f"(min critical_service_ratio={min_ratio:.5f}, proposed floor 0.9995)"
            )

        self.proposed_gate_results = results


def build_report(
    baseline_label: str,
    candidate_label: str,
    origin_results_baseline: List[OriginResult],
    origin_results_candidate: List[OriginResult],
    n_origins_attempted: int,
) -> SafetyGatedOutcomeReport:
    """
    Builds a `SafetyGatedOutcomeReport`. Fails closed (`DroppedOriginError`)
    if either results list is shorter than `n_origins_attempted` -- i.e. if
    any origin (including a failed/adverse one) was silently excluded
    rather than included with its failure recorded.
    """
    if len(origin_results_baseline) != n_origins_attempted:
        raise DroppedOriginError(
            f"Fail-closed: baseline origin results ({len(origin_results_baseline)}) do not match "
            f"n_origins_attempted ({n_origins_attempted}). Failed/adverse origins must never be "
            f"silently dropped from the report."
        )
    if len(origin_results_candidate) != n_origins_attempted:
        raise DroppedOriginError(
            f"Fail-closed: candidate origin results ({len(origin_results_candidate)}) do not match "
            f"n_origins_attempted ({n_origins_attempted}). Failed/adverse origins must never be "
            f"silently dropped from the report."
        )
    report = SafetyGatedOutcomeReport(
        baseline_label=baseline_label,
        candidate_label=candidate_label,
        origin_results_baseline=origin_results_baseline,
        origin_results_candidate=origin_results_candidate,
        n_origins_attempted=n_origins_attempted,
    )
    report.evaluate_gates()
    return report
