"""
POLARIS — OD-02 Boundary Diagnostic & EBR Alignment Harness (In-Memory Draft)
Tracking ID: PROP-2026-OD02-DIAG-01 (Revision 2.1)
Specification: SPEC-2026-OD02-DIAG-01
MDR Canonical Governance Version: v1.9.13 (Pass 23, 2026-10-19)

STATUS: GATE B.2 AUTHORIZED — DIAGNOSTIC SCRIPT REMEDIATION ONLY
GATE C STATUS: STRICTLY NOT AUTHORIZED (Zero optimizer/HiGHS execution permitted)

GOVERNANCE CONTRACT:
- Decision OD-02 and baseline contracts remain FROZEN.
- winner: null is preserved.
- 2025 blind evaluation data remains quarantined.
- Production code, tests, configs, and MDR are UNTOUCHED.
- Continuous-action tolerance tau_cont remains UNSET.
- Candidate solar estimators and EBR shift are EXPLICITLY EXPERIMENTAL AND DISABLED.
- Solver feasibility, action differences, objective differences, and degeneracy
  are recorded as four separate orthogonal dimensions.
"""

from dataclasses import dataclass, field
from enum import Enum
import copy
from datetime import datetime, timedelta
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import sys
from pathlib import Path

# Ensure repository root is on sys.path for importing production system schemas/adapters
REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


# ==============================================================================
# 1. GOVERNANCE CONSTANTS & GATE FIREWALLS
# ==============================================================================

MDR_CANONICAL_VERSION = "1.9.13"
MDR_PASS_DATE = "2026-10-19"
PROPOSAL_TRACKING_ID = "PROP-2026-OD02-DIAG-01-REV-2.1"
SPECIFICATION_ID = "SPEC-2026-OD02-DIAG-01"

# Gate Authorization Flags
GATE_A_APPROVED = True          # Design agreement in principle approved
GATE_B_AUTHORIZED = True        # Script authoring authorized
GATE_C_AUTHORIZED = False       # Execution strictly NOT AUTHORIZED
GATE_D_AUTHORIZED = False       # MDR decision amendment NOT AUTHORIZED

WINNER_SELECTION = None         # winner: null preserved; neither Path A nor Path B selected


class GateExecutionBlockedError(PermissionError):
    """Raised when an execution or optimizer call is attempted without explicit authorization."""
    pass


class QuarantineViolationError(ValueError):
    """Raised when an artifact or metadata violates the 2025 blind evaluation quarantine."""
    pass


class ExperimentalFeatureDisabledError(RuntimeError):
    """Raised when an unverified experimental feature is invoked without authorization."""
    pass


def assert_gate_c_authorized() -> None:
    """Fail-closed check preventing optimizer or simulation execution under Gate B."""
    if not GATE_C_AUTHORIZED:
        raise GateExecutionBlockedError(
            "FAIL-CLOSED: Gate C (Bounded HiGHS Execution) is STRICTLY NOT AUTHORIZED "
            "by the Project Owner. Optimizer invocation, solver runs, and simulation "
            "are prohibited under Gate B authoring clearance."
        )


def check_quarantine_compliance(path_or_identifier: str) -> None:
    """
    Supplementary defense-in-depth token check against 2025 quarantined evaluation data.
    NOTE: Token filtering alone does not constitute physical isolation; it serves
    strictly as an early static fail-closed guard against accidental references.
    """
    p_lower = str(path_or_identifier).lower()
    if "2025" in p_lower or "blind" in p_lower:
        raise QuarantineViolationError(
            f"FAIL-CLOSED QUARANTINE BREACH: Reference '{path_or_identifier}' "
            "contains quarantined 2025/blind token."
        )


# ==============================================================================
# 2. FIRST-ACTION DECISION VECTOR SCHEMAS (u_0)
# ==============================================================================

@dataclass(frozen=True)
class ContinuousActionVector:
    """
    Continuous decision variables at dispatch step t=0.
    Physical units: Watts (W) or Watt-hours (Wh) where applicable.

    SCHEMA FIDELITY:
    - p_sol_used, p_wind_used: Mapped directly from verified DispatchPlan fields (solar_used[0], wind_used[0]).
    - p_curt_total: Verified aggregate renewable curtailment (plan.renewable_curtailment[0]).
    - p_curt_sol, p_curt_wind: Unavailable in production DispatchPlan schema; marked None.
    """
    p_sol_used: float                   # Solar power dispatched to bus at t=0 (W) - plan.solar_used[0]
    p_wind_used: float                  # Wind power dispatched to bus at t=0 (W) - plan.wind_used[0]
    p_diesel: float                     # Diesel generator electrical power dispatch (W) - plan.diesel_power[0]
    p_chg: float                        # Battery charging power from microgrid bus (W) - plan.battery_charge[0]
    p_dis: float                        # Battery discharging power to microgrid bus (W) - plan.battery_discharge[0]
    p_curt_total: float                 # Aggregate renewable curtailment power (W) - plan.renewable_curtailment[0]
    p_served: float                     # Microgrid electrical load served (W) - plan.load_served[0]
    p_unmet: float                      # Unmet electrical load (W) - plan.unmet_load[0]
    p_flex: float                       # Flexible load scheduled (W) - plan.flexible_load_schedule[0]
    p_curt_sol: Optional[float] = None  # Component solar curtailment (None = unavailable in schema)
    p_curt_wind: Optional[float] = None # Component wind curtailment (None = unavailable in schema)

    def to_dict(self) -> Dict[str, float]:
        """Returns active continuous variables available for comparison."""
        d = {
            "p_sol_used": self.p_sol_used,
            "p_wind_used": self.p_wind_used,
            "p_diesel": self.p_diesel,
            "p_chg": self.p_chg,
            "p_dis": self.p_dis,
            "p_curt_total": self.p_curt_total,
            "p_served": self.p_served,
            "p_unmet": self.p_unmet,
            "p_flex": self.p_flex,
        }
        if self.p_curt_sol is not None:
            d["p_curt_sol"] = self.p_curt_sol
        if self.p_curt_wind is not None:
            d["p_curt_wind"] = self.p_curt_wind
        return d


@dataclass(frozen=True)
class BinaryActionVector:
    """
    Discrete commitment and operational state variables at dispatch step t=0.
    Domain: {0, 1} when exposed by schema, or None when unavailable.

    SCHEMA FIDELITY & LIMITATION:
    The verified public DispatchPlan schema (system/schemas/dispatch_plan.py)
    does NOT expose solver-internal binary decision variables (u_diesel, v_start,
    u_chg, u_dis). Per Gate B.1/B.2 instructions, internal binary states are NOT derived
    from continuous power flows, and remain None (unavailable) unless exposed by
    an authorized public result schema.
    """
    u_diesel: Optional[int] = None      # Diesel on/off commitment state in {0, 1}
    v_start: Optional[int] = None       # Diesel startup event indicator in {0, 1}
    u_chg: Optional[int] = None         # Battery charging binary indicator in {0, 1}
    u_dis: Optional[int] = None         # Battery discharging binary indicator in {0, 1}

    def __post_init__(self):
        for name, val in [
            ("u_diesel", self.u_diesel),
            ("v_start", self.v_start),
            ("u_chg", self.u_chg),
            ("u_dis", self.u_dis),
        ]:
            if val is not None and val not in (0, 1):
                raise ValueError(f"Binary decision variable '{name}' must be 0, 1, or None; got {val}.")

    def to_dict(self) -> Dict[str, int]:
        return {
            k: v for k, v in {
                "u_diesel": self.u_diesel,
                "v_start": self.v_start,
                "u_chg": self.u_chg,
                "u_dis": self.u_dis,
            }.items() if v is not None
        }


@dataclass(frozen=True)
class FirstActionVector:
    """Complete first-step dispatch action u_0 partitioned into continuous and discrete states."""
    continuous: ContinuousActionVector
    binary: BinaryActionVector


# ==============================================================================
# 3. OBJECTIVE COMPONENTS & FOUR-DIMENSIONAL CLASSIFICATION
# ==============================================================================

@dataclass(frozen=True)
class ObjectiveComponents:
    """
    Verified four-tier lexicographic objective components from GAP19 DispatchPlan:
    - j1_critical_deficit: Layer B critical unmet load penalty (priority 4)
    - j2_reserve_shortfall: Layer C governed reserve shortfall penalty (priority 3)
    - j3_diesel_fuel_cost: Layer D physical/economic diesel fuel cost (priority 2)
    - j4_curtailment_penalty: Layer E renewable curtailment penalty (priority 1)
    """
    j1_critical_deficit: Optional[float] = None
    j2_reserve_shortfall: Optional[float] = None
    j3_diesel_fuel_cost: Optional[float] = None
    j4_curtailment_penalty: Optional[float] = None

    def is_complete(self) -> bool:
        """Returns True only if all four lexicographic components are available."""
        return (
            self.j1_critical_deficit is not None
            and self.j2_reserve_shortfall is not None
            and self.j3_diesel_fuel_cost is not None
            and self.j4_curtailment_penalty is not None
        )

    def to_dict(self) -> Dict[str, Optional[float]]:
        return {
            "j1_critical_deficit": self.j1_critical_deficit,
            "j2_reserve_shortfall": self.j2_reserve_shortfall,
            "j3_diesel_fuel_cost": self.j3_diesel_fuel_cost,
            "j4_curtailment_penalty": self.j4_curtailment_penalty,
        }


class SolverTerminationStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    INFEASIBLE = "INFEASIBLE"
    UNBOUNDED = "UNBOUNDED"
    TIME_LIMIT = "TIME_LIMIT"
    NUMERICAL_ERROR = "NUMERICAL_ERROR"
    INCONCLUSIVE = "INCONCLUSIVE"


class ObjectiveComparisonStatus(str, Enum):
    IDENTICAL = "IDENTICAL"
    DISTINCT = "DISTINCT"
    INCOMPLETE = "INCOMPLETE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DegeneracyStatus(str, Enum):
    UNIQUE_OPTIMUM_UNVERIFIED = "UNIQUE_OPTIMUM_UNVERIFIED"
    POTENTIAL_DEGENERACY_FLAGGED = "POTENTIAL_DEGENERACY_FLAGGED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class ActionComparisonResult:
    """
    Detailed comparison between baseline first-action u_0 and variant first-action u_0.
    NOTE: tau_cont is UNSET by default; 1.0 W is NOT an approved threshold.
    """
    # Dimension 2: Action Differences
    binary_difference_detected: Optional[bool]  # None if binary variables unavailable in schema
    binary_deltas: Dict[str, int]
    
    continuous_deltas_w: Dict[str, float]
    max_continuous_delta_w: float  # L-infinity norm ||Delta u_0,cont||_inf
    
    # Continuous difference status relative to tau_cont:
    # If tau_cont is None, continuous_difference_detected is None (UNSET).
    tau_cont_applied_w: Optional[float]
    continuous_difference_detected: Optional[bool]

    # Schema fidelity metadata
    curtailment_mode: str = "AGGREGATE_RENEWABLE_CURTAILMENT"
    binary_availability: str = "UNAVAILABLE_IN_PUBLIC_SCHEMA"


@dataclass
class ObjectiveComparisonResult:
    """Detailed comparison across all four lexicographic objective tiers."""
    is_complete: bool
    status: ObjectiveComparisonStatus
    deltas: Dict[str, Optional[float]]
    baseline_components: ObjectiveComponents
    variant_components: ObjectiveComponents


@dataclass
class DiagnosticOutcome:
    """
    Four-dimensional decoupled outcome classification record.
    Preserves strict separation across orthogonal dimensions.
    """
    variant_id: int
    variant_name: str
    
    # Dimension 1: Solver Termination & Feasibility
    solver_status: SolverTerminationStatus
    solver_raw_status: str
    
    # Dimension 2: First-Action Comparison (u_0)
    action_comparison: Optional[ActionComparisonResult]
    
    # Dimension 3: Objective-Value Variation (full lexicographic components)
    objective_comparison: Optional[ObjectiveComparisonResult]
    
    # Dimension 4: Degeneracy & Solution Uniqueness
    degeneracy_status: DegeneracyStatus
    degeneracy_caveat: str = (
        "CAVEAT: In MILP optimization, multiple distinct action vectors u_0 may yield "
        "identical objective values (alternative optima). Raw action differences "
        "(Delta u_0 != 0) accompanying identical or near-identical objective values "
        "(|Delta J| ~ 0) DO NOT prove that the first-action change was physically forced "
        "by the boundary condition. The shift may arise from solver simplex pivot selection "
        "or branch-and-bound tie-breaking across degenerate vertices. Raw action or "
        "objective differences must NOT be presented as proof of causal attribution."
    )


def compare_first_actions(
    base: FirstActionVector,
    var: FirstActionVector,
    tau_cont: Optional[float] = None
) -> ActionComparisonResult:
    """
    Compares two first-action vectors across binary and continuous components.
    
    SAFEGUARD: tau_cont is None by default. It must not be assumed or set to 1.0 W
    without explicit owner authorization.
    """
    # 1. Binary comparison (only over exposed binary variables)
    b_deltas: Dict[str, int] = {}
    has_bin_diff: Optional[bool] = None
    bin_avail = "UNAVAILABLE_IN_PUBLIC_SCHEMA"
    if base.binary is not None and var.binary is not None:
        base_b = base.binary.to_dict()
        var_b = var.binary.to_dict()
        common_b_keys = set(base_b.keys()) & set(var_b.keys())
        if common_b_keys:
            b_deltas = {k: var_b[k] - base_b[k] for k in common_b_keys}
            has_bin_diff = any(d != 0 for d in b_deltas.values())
            bin_avail = "AVAILABLE"

    # 2. Continuous comparison
    base_c = base.continuous.to_dict()
    var_c = var.continuous.to_dict()
    common_c_keys = set(base_c.keys()) & set(var_c.keys())
    c_deltas = {k: var_c[k] - base_c[k] for k in common_c_keys}
    max_c_delta = max(abs(d) for d in c_deltas.values()) if c_deltas else 0.0

    # 3. Continuous thresholding: only if tau_cont is explicitly provided
    cont_diff_detected: Optional[bool] = None
    if tau_cont is not None:
        cont_diff_detected = max_c_delta > tau_cont

    curt_mode = (
        "COMPONENT_SEPARATED"
        if (base.continuous.p_curt_sol is not None and var.continuous.p_curt_sol is not None)
        else "AGGREGATE_RENEWABLE_CURTAILMENT"
    )

    return ActionComparisonResult(
        binary_difference_detected=has_bin_diff,
        binary_deltas=b_deltas,
        continuous_deltas_w=c_deltas,
        max_continuous_delta_w=max_c_delta,
        tau_cont_applied_w=tau_cont,
        continuous_difference_detected=cont_diff_detected,
        curtailment_mode=curt_mode,
        binary_availability=bin_avail,
    )


def compare_objectives(
    base: ObjectiveComponents,
    var: ObjectiveComponents,
    tau_obj: float = 1e-4
) -> ObjectiveComparisonResult:
    """Compares all four lexicographic objective tiers without scalar collapse."""
    deltas = {
        "delta_j1": (var.j1_critical_deficit - base.j1_critical_deficit)
        if (var.j1_critical_deficit is not None and base.j1_critical_deficit is not None) else None,
        "delta_j2": (var.j2_reserve_shortfall - base.j2_reserve_shortfall)
        if (var.j2_reserve_shortfall is not None and base.j2_reserve_shortfall is not None) else None,
        "delta_j3": (var.j3_diesel_fuel_cost - base.j3_diesel_fuel_cost)
        if (var.j3_diesel_fuel_cost is not None and base.j3_diesel_fuel_cost is not None) else None,
        "delta_j4": (var.j4_curtailment_penalty - base.j4_curtailment_penalty)
        if (var.j4_curtailment_penalty is not None and base.j4_curtailment_penalty is not None) else None,
    }

    is_complete = base.is_complete() and var.is_complete()
    if not is_complete:
        status = ObjectiveComparisonStatus.INCOMPLETE
    else:
        all_identical = all(abs(d) <= tau_obj for d in deltas.values() if d is not None)
        status = ObjectiveComparisonStatus.IDENTICAL if all_identical else ObjectiveComparisonStatus.DISTINCT

    return ObjectiveComparisonResult(
        is_complete=is_complete,
        status=status,
        deltas=deltas,
        baseline_components=base,
        variant_components=var,
    )


# ==============================================================================
# 4. FOUR-VARIANT GENERATOR & ADAPTER MAPPINGS
# ==============================================================================

class VariantType(int, Enum):
    VARIANT_0_FROZEN_BASELINE = 0
    VARIANT_1_EBR_SHIFT_ONLY = 1
    VARIANT_2_SOLAR_EST_ONLY = 2
    VARIANT_3_COMBINED_INTERACTION = 3


@dataclass
class DiagnosticVariantConfig:
    """Configuration and guard flags for a diagnostic factor variant."""
    variant_id: VariantType
    name: str
    description: str
    is_experimental: bool
    is_enabled: bool


VARIANT_CONFIGS: Dict[VariantType, DiagnosticVariantConfig] = {
    VariantType.VARIANT_0_FROZEN_BASELINE: DiagnosticVariantConfig(
        variant_id=VariantType.VARIANT_0_FROZEN_BASELINE,
        name="Variant 0 (Control Reference)",
        description="Frozen OD-02 baseline: solar shifted 1..23 -> 0..22 with 0.0 W/m^2 fallback; EBR unshifted.",
        is_experimental=False,
        is_enabled=True,
    ),
    VariantType.VARIANT_1_EBR_SHIFT_ONLY: DiagnosticVariantConfig(
        variant_id=VariantType.VARIANT_1_EBR_SHIFT_ONLY,
        name="Variant 1 (EBR Alignment Perturbation Only)",
        description="Hypothetical experimental perturbation: EBR shifted +1h with persistence tail; solar unchanged from OD-02.",
        is_experimental=True,
        is_enabled=False,  # DISABLED pending authorized check
    ),
    VariantType.VARIANT_2_SOLAR_EST_ONLY: DiagnosticVariantConfig(
        variant_id=VariantType.VARIANT_2_SOLAR_EST_ONLY,
        name="Variant 2 (Terminal Solar Estimator Perturbation Only)",
        description="Experimental hypothesis: slot 23 solar replaced by candidate estimator; EBR unchanged (unshifted).",
        is_experimental=True,
        is_enabled=False,  # DISABLED pending authorized check
    ),
    VariantType.VARIANT_3_COMBINED_INTERACTION: DiagnosticVariantConfig(
        variant_id=VariantType.VARIANT_3_COMBINED_INTERACTION,
        name="Variant 3 (Combined Factor Interaction)",
        description="Simultaneous perturbation of both EBR alignment and terminal solar estimator.",
        is_experimental=True,
        is_enabled=False,  # DISABLED pending authorized check
    ),
}


def align_bundle_variant_0(bundle: Any) -> Any:
    """
    Strict replication of frozen OD-02 baseline behavior (adapters.py lines 641-695).
    - Idempotent: returns unmodified if already marked od02_time_aligned.
    - Solar generation/irradiance: raw horizons 1..23 -> dispatch steps 0..22; step 23 -> 0.0.
    - Timestamps: advanced by +1h.
    - EBR trajectory: preserved UNSHIFTED.
    - Wind, load, critical demand: preserved UNSHIFTED.
    """
    if bundle is None:
        raise ValueError("Cannot align None bundle.")

    # Idempotency check matching production adapters.py line 660
    meta = getattr(bundle, "metadata", None)
    if isinstance(meta, dict) and meta.get("od02_time_aligned"):
        return bundle

    # Fail-closed 24-step forecast validation matching adapters.py lines 618-620
    if not hasattr(bundle, "solar_generation") or bundle.solar_generation is None:
        raise ValueError("Fail-closed: bundle missing solar_generation.")
    pts_sol = list(bundle.solar_generation.point)
    if len(pts_sol) != 24:
        raise ValueError(f"Fail-closed: OD-02 requires 24-step forecast, got {len(pts_sol)}.")

    aligned = copy.copy(bundle)

    # Solar generation shift
    sol_gen = copy.copy(bundle.solar_generation)
    sol_gen.point = pts_sol[1:] + [0.0]
    if hasattr(bundle.solar_generation, "lower") and bundle.solar_generation.lower is not None:
        low = list(bundle.solar_generation.lower)
        sol_gen.lower = low[1:] + [0.0] if len(low) == 24 else sol_gen.point
    if hasattr(bundle.solar_generation, "upper") and bundle.solar_generation.upper is not None:
        upp = list(bundle.solar_generation.upper)
        sol_gen.upper = upp[1:] + [0.0] if len(upp) == 24 else sol_gen.point
    aligned.solar_generation = sol_gen

    # Solar irradiance shift if present (fail-closed if length != 24)
    if hasattr(bundle, "solar_irradiance") and bundle.solar_irradiance is not None:
        pts_irr = list(bundle.solar_irradiance.point)
        if len(pts_irr) != 24:
            raise ValueError(f"Fail-closed: solar_irradiance requires 24-step forecast, got {len(pts_irr)}.")
        sol_irr = copy.copy(bundle.solar_irradiance)
        sol_irr.point = pts_irr[1:] + [0.0]
        if hasattr(bundle.solar_irradiance, "lower") and bundle.solar_irradiance.lower is not None:
            low_i = list(bundle.solar_irradiance.lower)
            sol_irr.lower = low_i[1:] + [0.0] if len(low_i) == 24 else sol_irr.point
        if hasattr(bundle.solar_irradiance, "upper") and bundle.solar_irradiance.upper is not None:
            upp_i = list(bundle.solar_irradiance.upper)
            sol_irr.upper = upp_i[1:] + [0.0] if len(upp_i) == 24 else sol_irr.point
        aligned.solar_irradiance = sol_irr

    # Timestamp advance (+1h)
    if hasattr(bundle, "timestamps") and bundle.timestamps is not None and len(bundle.timestamps) == 24:
        try:
            last_ts = str(bundle.timestamps[-1])
            dt_last = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            dt_24 = dt_last + timedelta(hours=1)
            t_24 = dt_24.strftime("%Y-%m-%dT%H:%M:%SZ") if last_ts.endswith("Z") else dt_24.isoformat()
            aligned.timestamps = list(bundle.timestamps[1:]) + [t_24]
        except Exception:
            aligned.timestamps = list(bundle.timestamps[1:]) + [f"{bundle.timestamps[-1]}+1h"]

    # Metadata provenance
    new_meta = dict(meta or {})
    new_meta["od02_time_aligned"] = True
    new_meta["diagnostic_variant"] = VariantType.VARIANT_0_FROZEN_BASELINE.value
    aligned.metadata = new_meta

    # Conformal EBR remains strictly unshifted
    return aligned


def align_bundle_variant_1(bundle: Any, allow_experimental: bool = False) -> Any:
    """
    Variant 1: Hypothetical EBR alignment perturbation (+1h shift).
    E_ebr_aligned[0..22] = E_ebr_raw[1..23], E_ebr_aligned[23] = E_ebr_raw[23] (persistence tail).
    FAIL-CLOSED: Disabled by default. Requires explicit allow_experimental=True.
    """
    if not allow_experimental or not VARIANT_CONFIGS[VariantType.VARIANT_1_EBR_SHIFT_ONLY].is_enabled:
        raise ExperimentalFeatureDisabledError(
            "FAIL-CLOSED: Variant 1 (EBR Shift) is an unverified experimental hypothesis "
            "and is DISABLED. Cannot be evaluated without authorized verification."
        )

    # Start from Variant 0 baseline (solar shifted per OD-02)
    aligned = align_bundle_variant_0(bundle)
    
    meta = dict(aligned.metadata)
    raw_ebr = meta.get("ebr_target_wh")
    if not isinstance(raw_ebr, (list, tuple)) or len(raw_ebr) != 24:
        raise ValueError(f"Variant 1 requires valid 24-step 'ebr_target_wh' in metadata, got {type(raw_ebr)}.")

    # Shift EBR by +1h with persistence tail
    shifted_ebr = list(raw_ebr[1:]) + [float(raw_ebr[-1])]
    meta["ebr_target_wh"] = shifted_ebr
    meta["diagnostic_variant"] = VariantType.VARIANT_1_EBR_SHIFT_ONLY.value
    meta["ebr_alignment_perturbed"] = True
    aligned.metadata = meta

    return aligned


def align_bundle_variant_2(
    bundle: Any,
    candidate_slot23_solar_w: Optional[float] = None,
    allow_experimental: bool = False
) -> Any:
    """
    Variant 2: Terminal solar estimator perturbation at slot 23.
    Replaces 0.0 W fallback with candidate estimate while maintaining bounds consistency.
    FAIL-CLOSED: Disabled by default. Requires explicit allow_experimental=True and verified candidate input.
    """
    if not allow_experimental or not VARIANT_CONFIGS[VariantType.VARIANT_2_SOLAR_EST_ONLY].is_enabled:
        raise ExperimentalFeatureDisabledError(
            "FAIL-CLOSED: Variant 2 (Terminal Solar Estimator) is an unverified experimental "
            "hypothesis and is DISABLED. Runtime dependencies are unverified."
        )

    if candidate_slot23_solar_w is None or math.isnan(candidate_slot23_solar_w) or candidate_slot23_solar_w < 0.0:
        raise ValueError(
            f"Fail-closed: Variant 2 requires non-negative candidate solar estimate; got {candidate_slot23_solar_w}."
        )

    aligned = align_bundle_variant_0(bundle)
    sol_gen = copy.copy(aligned.solar_generation)
    pts = list(sol_gen.point)
    pts[-1] = float(candidate_slot23_solar_w)
    sol_gen.point = pts
    
    # Maintain bounds consistency (lower <= point <= upper) per ForecastBundle schema
    if hasattr(sol_gen, "upper") and sol_gen.upper is not None:
        upp = list(sol_gen.upper)
        upp[-1] = max(float(upp[-1]), float(candidate_slot23_solar_w))
        sol_gen.upper = upp
    if hasattr(sol_gen, "lower") and sol_gen.lower is not None:
        low = list(sol_gen.lower)
        low[-1] = min(float(low[-1]), float(candidate_slot23_solar_w))
        sol_gen.lower = low
    aligned.solar_generation = sol_gen

    meta = dict(aligned.metadata)
    meta["diagnostic_variant"] = VariantType.VARIANT_2_SOLAR_EST_ONLY.value
    meta["candidate_slot23_solar_w"] = float(candidate_slot23_solar_w)
    aligned.metadata = meta

    return aligned


def align_bundle_variant_3(
    bundle: Any,
    candidate_slot23_solar_w: Optional[float] = None,
    allow_experimental: bool = False
) -> Any:
    """
    Variant 3: Combined interaction of Variant 1 (EBR shift) and Variant 2 (Terminal solar).
    REMEDIATED: Directly mutates Variant 1 bundle without nested re-alignment, preventing
    the double-shift bug and metadata overwrite.
    FAIL-CLOSED: Disabled by default.
    """
    if not allow_experimental or not VARIANT_CONFIGS[VariantType.VARIANT_3_COMBINED_INTERACTION].is_enabled:
        raise ExperimentalFeatureDisabledError(
            "FAIL-CLOSED: Variant 3 (Combined Interaction) is DISABLED."
        )

    if candidate_slot23_solar_w is None or math.isnan(candidate_slot23_solar_w) or candidate_slot23_solar_w < 0.0:
        raise ValueError(
            f"Fail-closed: Variant 3 requires non-negative candidate solar estimate; got {candidate_slot23_solar_w}."
        )

    # 1. Start from Variant 1 (EBR shifted, solar and timestamps shifted once per OD-02)
    v3_bundle = align_bundle_variant_1(bundle, allow_experimental=True)

    # 2. Directly inject candidate solar into slot 23 (NO second call to align_bundle_variant_0)
    sol_gen = copy.copy(v3_bundle.solar_generation)
    pts = list(sol_gen.point)
    pts[-1] = float(candidate_slot23_solar_w)
    sol_gen.point = pts
    if hasattr(sol_gen, "upper") and sol_gen.upper is not None:
        upp = list(sol_gen.upper)
        upp[-1] = max(float(upp[-1]), float(candidate_slot23_solar_w))
        sol_gen.upper = upp
    if hasattr(sol_gen, "lower") and sol_gen.lower is not None:
        low = list(sol_gen.lower)
        low[-1] = min(float(low[-1]), float(candidate_slot23_solar_w))
        sol_gen.lower = low
    v3_bundle.solar_generation = sol_gen

    # 3. Provenance metadata for Variant 3
    meta = dict(v3_bundle.metadata)
    meta["diagnostic_variant"] = VariantType.VARIANT_3_COMBINED_INTERACTION.value
    meta["candidate_slot23_solar_w"] = float(candidate_slot23_solar_w)
    meta["interaction_perturbed"] = True
    v3_bundle.metadata = meta

    return v3_bundle


# ==============================================================================
# 5. INPUT MANIFEST & FAIL-CLOSED QUARANTINE FIREWALL
# ==============================================================================

@dataclass
class InputManifestItem:
    """Metadata for an approved 2024 historical input file."""
    file_path: str
    expected_sha256: str
    description: str
    is_verified: bool = False


class DatasetIngestionFirewall:
    """
    Strict fail-closed ingestion firewall enforcing an approved-input allow-list policy.
    
    ISOLATION & GOVERNANCE BOUNDARY:
    1. Primary Isolation Boundary: Ingestion is strictly restricted to an explicitly
       registered, verified allow-list of approved 2024 historical artifacts.
    2. Fail-Closed Policy: If the allow-list is empty, unverified, or None, ALL file
       ingestion is immediately rejected with PermissionError.
    3. No Broad Path Fallback: String/token checks serve solely as a defense-in-depth
       pre-filter; they are NOT presented as proof of physical isolation. Physical
       quarantine of 2025 blind data is enforced by process isolation.
    """
    def __init__(self, allow_list: Optional[List[InputManifestItem]] = None):
        self.allow_list = allow_list or []

    def validate_file(self, path: str) -> None:
        """Enforces fail-closed allow-list membership."""
        # 1. Fail closed if allow-list is empty or unverified
        if not self.allow_list:
            raise PermissionError(
                "FAIL-CLOSED: Approved input allow-list is empty or unverified. "
                "Dataset access is blocked until explicit approved 2024 artifacts are registered."
            )

        # 2. Defense-in-depth token check (rejects any 2025 reference)
        check_quarantine_compliance(path)

        # 3. Exact allow-list membership
        matching = [item for item in self.allow_list if item.file_path == path]
        if not matching:
            raise PermissionError(
                f"FAIL-CLOSED: Path '{path}' is not present in the approved input allow-list."
            )
        
        # 4. Require item to be verified
        if not matching[0].is_verified:
            raise PermissionError(
                f"FAIL-CLOSED: Allow-list entry for '{path}' is marked unverified."
            )


# ==============================================================================
# 6. SOLVER INTERFACE & CONFIGURATION WIRING
# ==============================================================================

def prepare_gap19_solver_config(
    bundle: Any,
    station_state: Any,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Wires production configuration helpers to prepare GAP19 optimizer config:
    1. Decision OD-01: Derives cycle-neutral terminal target:
       E_term = initial_e_wh - min_e_wh via _prepare_gap19_terminal_target_config.
    2. Policy B: Ingests conformal EBR from bundle.metadata['ebr_target_wh'] (or config),
       computes pointwise maximum envelope max(critical_reserve[t], conformal_ebr[t]),
       and injects it into config['ebr_target_wh'] via _prepare_gap19_policy_b_config.
    """
    try:
        from system.evaluation.n6_multi_origin_harness.adapters import (
            _prepare_gap19_terminal_target_config,
            _prepare_gap19_policy_b_config,
        )
    except ImportError as err:
        raise RuntimeError(f"Fail-closed: cannot import production configuration helpers: {err}")

    # 1. Dynamic terminal target per OD-01
    cfg_with_target = _prepare_gap19_terminal_target_config(station_state, config)

    # 2. Policy B pointwise maximum envelope
    cfg_policy = dict(cfg_with_target)
    if "policy_b" not in cfg_policy and "reserve_policy" not in cfg_policy:
        cfg_policy["policy_b"] = True

    final_cfg = _prepare_gap19_policy_b_config(bundle, cfg_policy)
    return final_cfg


def extract_first_action_from_dispatch_plan(plan: Any) -> FirstActionVector:
    """
    Extracts u_0 continuous and binary decision components from a DispatchPlan
    strictly conforming to the verified production DispatchPlan schema.
    """
    # Continuous components at t=0
    p_sol_used = float(plan.solar_used[0])
    p_wind_used = float(plan.wind_used[0])
    p_diesel = float(plan.diesel_power[0])
    p_chg = float(plan.battery_charge[0])
    p_dis = float(plan.battery_discharge[0])
    p_curt_total = float(plan.renewable_curtailment[0])
    p_served = float(plan.load_served[0])
    p_unmet = float(plan.unmet_load[0])
    p_flex = float(plan.flexible_load_schedule[0])

    cont = ContinuousActionVector(
        p_sol_used=p_sol_used,
        p_wind_used=p_wind_used,
        p_diesel=p_diesel,
        p_chg=p_chg,
        p_dis=p_dis,
        p_curt_total=p_curt_total,
        p_served=p_served,
        p_unmet=p_unmet,
        p_flex=p_flex,
        p_curt_sol=None,   # Explicitly unavailable in production DispatchPlan schema
        p_curt_wind=None,  # Explicitly unavailable in production DispatchPlan schema
    )

    # Binaries: Only populated if public schema explicitly provides binary attributes.
    # Otherwise remain None per Gate B.1/B.2 mandate (no derivation from power flows).
    binary = BinaryActionVector(
        u_diesel=int(getattr(plan, "u_diesel")[0]) if hasattr(plan, "u_diesel") and getattr(plan, "u_diesel") is not None else None,
        v_start=int(getattr(plan, "v_start")[0]) if hasattr(plan, "v_start") and getattr(plan, "v_start") is not None else None,
        u_chg=int(getattr(plan, "u_chg")[0]) if hasattr(plan, "u_chg") and getattr(plan, "u_chg") is not None else None,
        u_dis=int(getattr(plan, "u_dis")[0]) if hasattr(plan, "u_dis") and getattr(plan, "u_dis") is not None else None,
    )

    return FirstActionVector(continuous=cont, binary=binary)


def extract_objectives_from_dispatch_plan(plan: Any) -> ObjectiveComponents:
    """
    Extracts all four verified lexicographic objective components from DispatchPlan.
    Does not collapse into a single scalar. If any component is missing, it remains None.
    """
    j1 = getattr(plan, "j1_objective", None)
    j2 = getattr(plan, "j2_objective", None)
    j3 = getattr(plan, "j3_objective", getattr(plan, "objective_value", None))
    j4 = getattr(plan, "j4_objective", None)

    return ObjectiveComponents(
        j1_critical_deficit=float(j1) if j1 is not None else None,
        j2_reserve_shortfall=float(j2) if j2 is not None else None,
        j3_diesel_fuel_cost=float(j3) if j3 is not None else None,
        j4_curtailment_penalty=float(j4) if j4 is not None else None,
    )


def execute_diagnostic_solve(
    variant_bundle: Any,
    station_state: Any,
    config: Dict[str, Any],
    mock_optimizer: Optional[Any] = None
) -> Tuple[SolverTerminationStatus, Optional[FirstActionVector], Optional[ObjectiveComponents]]:
    """
    Executes or mocks solver invocation.
    
    FIREWALL: Calls assert_gate_c_authorized() before any optimizer construction
    or invocation. FAILS CLOSED unless Gate C has been explicitly authorized by Project Owner.
    """
    # 1. Wire governed solver configuration (Policy B + OD-01 dynamic terminal target)
    solver_cfg = prepare_gap19_solver_config(variant_bundle, station_state, config)

    # 2. Enforce Gate C firewall BEFORE constructing or invoking any optimizer
    assert_gate_c_authorized()

    # 3. Instantiate production solver or use injected test mock
    if mock_optimizer is None:
        from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
        optimizer = GAP19HighsNativeOptimizer()
    else:
        optimizer = mock_optimizer

    # 4. Execute solver conforming to EnergyOptimizer protocol
    plan = optimizer.optimize(variant_bundle, station_state, solver_cfg)
    status_str = str(getattr(plan, "constraint_status", "UNKNOWN")).upper()

    if "OPTIMAL" in status_str:
        status = SolverTerminationStatus.OPTIMAL
        u0 = extract_first_action_from_dispatch_plan(plan)
        objs = extract_objectives_from_dispatch_plan(plan)
        return status, u0, objs
    elif "INFEASIBLE" in status_str:
        return SolverTerminationStatus.INFEASIBLE, None, None
    elif "TIME_LIMIT" in status_str:
        return SolverTerminationStatus.TIME_LIMIT, None, None
    else:
        return SolverTerminationStatus.NUMERICAL_ERROR, None, None


# ==============================================================================
# 7. STATIC ORCHESTRATION & RUN MANIFEST SCHEMA
# ==============================================================================

VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD: List[Dict[str, Any]] = [
    # Regime A: Polar Day / Midnight Sun (4 origins, min elevation > 0.0°)
    {
        "timestamp": "2024-06-01T00:00:00Z",
        "origin_id": 67,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 0.50,
        "max_solar_elevation_deg": 43.71,
    },
    {
        "timestamp": "2024-06-11T00:00:00Z",
        "origin_id": 72,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.50,
        "max_solar_elevation_deg": 44.71,
    },
    {
        "timestamp": "2024-06-19T00:00:00Z",
        "origin_id": 76,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.82,
        "max_solar_elevation_deg": 45.02,
    },
    {
        "timestamp": "2024-06-21T00:00:00Z",
        "origin_id": 77,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.83,
        "max_solar_elevation_deg": 45.03,
    },
    # Regime B: Dynamic Shoulder / Autumn Equinox (3 origins, transition with daylight and night)
    {
        "timestamp": "2024-09-15T00:00:00Z",
        "origin_id": 120,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -18.74,
        "max_solar_elevation_deg": 24.29,
    },
    {
        "timestamp": "2024-09-21T00:00:00Z",
        "origin_id": 123,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -21.09,
        "max_solar_elevation_deg": 21.95,
    },
    {
        "timestamp": "2024-09-23T00:00:00Z",
        "origin_id": 124,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -21.88,
        "max_solar_elevation_deg": 21.16,
    },
    # Regime C: Polar Night (3 origins, max elevation <= 0.0°)
    {
        "timestamp": "2024-11-30T00:00:00Z",
        "origin_id": 158,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -43.17,
        "max_solar_elevation_deg": -0.25,
    },
    {
        "timestamp": "2024-12-08T00:00:00Z",
        "origin_id": 162,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -44.24,
        "max_solar_elevation_deg": -1.25,
    },
    {
        "timestamp": "2024-12-22T00:00:00Z",
        "origin_id": 169,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -45.01,
        "max_solar_elevation_deg": -1.85,
    },
]


VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN: List[Dict[str, Any]] = [
    # Regime A: Polar Day / Midnight Sun (4 origins, min elevation > 0.0°)
    {
        "forecast_origin": 134,
        "timestamp": "2024-06-02T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 2,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 0.63,
        "max_solar_elevation_deg": 43.84,
        "mid_solar_elevation_deg": 0.63,
    },
    {
        "forecast_origin": 144,
        "timestamp": "2024-06-12T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 2,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.57,
        "max_solar_elevation_deg": 44.77,
        "mid_solar_elevation_deg": 1.57,
    },
    {
        "forecast_origin": 152,
        "timestamp": "2024-06-20T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 3,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.83,
        "max_solar_elevation_deg": 45.03,
        "mid_solar_elevation_deg": 1.83,
    },
    {
        "forecast_origin": 154,
        "timestamp": "2024-06-22T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 2,
        "stratum": "REGIME_A_POLAR_DAY",
        "min_solar_elevation_deg": 1.82,
        "max_solar_elevation_deg": 45.02,
        "mid_solar_elevation_deg": 1.82,
    },
    # Regime B: Dynamic Shoulder / Autumn Equinox (3 origins, midnight darkness <= -6° and daylight max > 20°)
    {
        "forecast_origin": 240,
        "timestamp": "2024-09-16T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 4,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -19.13,
        "max_solar_elevation_deg": 23.90,
        "mid_solar_elevation_deg": -19.01,
    },
    {
        "forecast_origin": 246,
        "timestamp": "2024-09-22T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 1,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -21.49,
        "max_solar_elevation_deg": 21.56,
        "mid_solar_elevation_deg": -21.31,
    },
    {
        "forecast_origin": 248,
        "timestamp": "2024-09-24T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 5,
        "stratum": "REGIME_B_DYNAMIC_SHOULDER",
        "min_solar_elevation_deg": -22.28,
        "max_solar_elevation_deg": 20.77,
        "mid_solar_elevation_deg": -22.08,
    },
    # Regime C: Polar Night / Winter Minimum (3 origins, max elevation <= 0.0°)
    {
        "forecast_origin": 316,
        "timestamp": "2024-12-01T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 1,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -43.32,
        "max_solar_elevation_deg": -0.40,
        "mid_solar_elevation_deg": -43.30,
    },
    {
        "forecast_origin": 324,
        "timestamp": "2024-12-09T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 2,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -44.34,
        "max_solar_elevation_deg": -1.34,
        "mid_solar_elevation_deg": -44.34,
    },
    {
        "forecast_origin": 336,
        "timestamp": "2024-12-21T00:00:00Z",
        "parity": "EVEN",
        "canonical_fold": 1,
        "stratum": "REGIME_C_POLAR_NIGHT",
        "min_solar_elevation_deg": -45.00,
        "max_solar_elevation_deg": -1.85,
        "mid_solar_elevation_deg": -45.00,
    },
]



@dataclass
class DiagnosticRunManifest:
    """
    Immutable pre-execution run specification manifest.
    Establishes the planned run structure without executing anything.
    """
    tracking_id: str
    mdr_version: str
    git_commit_hash: str
    gate_c_authorized: bool
    tau_cont_applied_w: Optional[float]
    origin_timestamps: List[str]
    allow_list_entries: List[Dict[str, Any]]
    variant_status: Dict[str, bool]
    execution_status: str


def plan_diagnostic_run(
    origin_timestamps: List[str],
    allow_list: List[InputManifestItem]
) -> DiagnosticRunManifest:
    """
    Static pre-execution orchestration planner.
    Enforces fail-closed rules and pre-registers run structure.
    DOES NOT INVOKE THE SOLVER OR ACCESS DATASETS.
    """
    # 1. Validate Gate C authorization state
    if not GATE_C_AUTHORIZED:
        exec_status = "BLOCKED_GATE_C_NOT_AUTHORIZED"
    else:
        exec_status = "READY_FOR_EXECUTION"

    # 2. Validate origin timestamps
    if not origin_timestamps:
        raise ValueError("Fail-closed: origin_timestamps list is empty; explicit owner approval required.")

    # 3. Validate allow-list fail-closed
    if not allow_list:
        raise PermissionError("Fail-closed: input allow-list is empty or unverified.")

    for item in allow_list:
        if not item.is_verified:
            raise PermissionError(f"Fail-closed: allow-list entry '{item.file_path}' is not verified.")

    return DiagnosticRunManifest(
        tracking_id=PROPOSAL_TRACKING_ID,
        mdr_version=MDR_CANONICAL_VERSION,
        git_commit_hash="uncommitted_scratch_development",
        gate_c_authorized=GATE_C_AUTHORIZED,
        tau_cont_applied_w=None,
        origin_timestamps=list(origin_timestamps),
        allow_list_entries=[
            {"path": it.file_path, "sha256": it.expected_sha256, "verified": it.is_verified}
            for it in allow_list
        ],
        variant_status={cfg.name: cfg.is_enabled for cfg in VARIANT_CONFIGS.values()},
        execution_status=exec_status,
    )
