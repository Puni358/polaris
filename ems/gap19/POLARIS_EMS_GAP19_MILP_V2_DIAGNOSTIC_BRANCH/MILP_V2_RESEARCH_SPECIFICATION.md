# MILP v2 — Research-Only Design Specification

**Status**: Design document only. **No code, config, or model is modified or implemented.
No MILP is run.** GAP19 (`gap19_highs_native.py`) remains frozen, unmodified, as the
control. Everything here is built on `SIMULATED_POLICY_PACKAGE_MILP_V2.md`'s
`SIMULATED_RESEARCH_ASSUMPTION` decisions, which carry **no real governance authority**.
Per instruction, this design does **not** optimize for lower diesel use — the earlier
counterfactual isolation (`COUNTERFACTUAL_CAUSAL_ISOLATION_REPORT.md`) already showed
Stage 8.1's higher diesel is ~101.5% explained by genuine solar scarcity, so no change below
touches the energy-balance mechanics that produce it.

---

## 1. Load-tier formulation

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| **Critical** | `p_served ≤ critical_demand[t]` (hard cap, equality), `P_unmet_crit` costed at top priority `J1` | **Unchanged** | Already policy-aligned (D03/D04/D05 hard-constraint requirement) | `CURRENT_IMPLEMENTATION_FACT`, confirmed matching D03-05 | Existing evidence |
| **Essential / managed-shedding (Tier 2)** | Does not exist; collapsed into the same uncosted `p_unmet` as everything non-critical | New variable `p_served_essential[t] ∈ [0, essential_demand[t]]`, where `essential_demand[t]` is drawn from `loads.yaml`'s existing `deferrable_loads` entries (already present in config, never read by GAP19). Shortfall `P_unmet_essential[t]` given a small, nonzero cost at the **lowest existing priority tier (J4)**, alongside curtailment — not a new 5th lexicographic stage. | D01/D02 require a distinct managed-shedding tier; D02's exact mechanics are unspecified, so this sketches structure only, at minimal priority-system disruption | Tier's *existence* = D01 (real); exact cost/placement = simulated | **SIMULATED_RESEARCH_ASSUMPTION** |
| **Flexible / Interruptible-Noncritical (Tier 3)** | Same as Essential — fully uncosted, unconditionally unmet | Remains fully uncosted / shed first, by design — this tier is the one D02 explicitly authorizes to be deprioritized most heavily ("shed first") | D02 | Existing evidence (policy), simulated only in that no real circuit mapping exists | Existing evidence for intent; simulated for lack of real load data |

**Why J4, not a new priority level**: D15 authorizes exactly four stages (Critical
reliability → Resilience → Fuel → Renewables). Inserting a fifth stage for Essential-tier
service is not supported by any document. Folding a small Essential-shedding cost into the
existing lowest tier (J4) preserves D15's stage count exactly while giving Tier 2 *some*
accounting instead of none.

## 2. Critical-load hard constraint and infeasibility handling

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| Hard constraint mechanism | `p_served ≤ critical_demand`, `P_unmet_crit` at `J1` | **Unchanged** | Already matches D03/D04/D05's "hard constraint, not soft penalty" instruction | Confirmed in prior formulation audit | Existing evidence |
| Infeasibility response | If `model_status != kOptimal`, returns a degenerate zero-dispatch `DispatchPlan` (`constraint_status = "OPTIMIZATION_INFEASIBLE: ..."`) — already exists in code, previously unflagged | On that same infeasibility signal, route explicitly to the existing `OptionDFallbackSolver` instead of the degenerate plan, and log the event (timestamp, duration, magnitude) | D04 requires emergency unmet-critical events to be logged; D06 authorizes a lexicographic fallback, not a soft-penalty trade-off; the current degenerate-plan fallback does neither | Decision 1 of `SIMULATED_POLICY_PACKAGE_MILP_V2.md` (grade B) | **SIMULATED_RESEARCH_ASSUMPTION** |

## 3. Emergency Mode entry/mapping using the simulated 6h assumption

| | Current GAP19/router | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| Trigger logic | `EMSControlRouter.evaluate_and_route` already uses `t_required_hours = 6.0` (ECD survivability assessment) — unchanged, already running in R1/R2 | **No code change.** v2 formally *designates* this existing, unmodified router logic as satisfying the governed Emergency Mode mapping requirement | `T_REQUIRED = 6h` is the one value in this entire governance space marked `ESTABLISHED`; the router code implementing it already exists and is already exercised | Decision 2 of simulated package (grade A — reuses only already-real facts) | Existing evidence (the designation itself is simulated; the underlying facts are real) |

**This is a documentation/labeling step, not a formulation change.**

## 4. Terminal reserve

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| Unit | Wh (`config["terminal_target_wh"]`, `StationState.terminal_target_wh_override`) | **Unchanged** | Only unit the existing, unmodified ingestion code accepts | Code fact | Existing evidence |
| Formula/value | No governed source; R1/R2 supplied it externally via a research script | v2 proposes the **same, unchanged** R1/R2 formula (`40,000 Wh floor + 6h trailing deficit × 1.10`) as the value supplied — and proposes, as a *design* note only, that this injection logic would live in `worker.py`'s Cell B/A2 config-assembly step, mirroring the existing `critical_demand_w` injection pattern there (`worker.py:233-244`) | Reuses the only existing, documented injection precedent in the codebase; introduces no new formula | Decision 5 of simulated package (grade C) | **SIMULATED_RESEARCH_ASSUMPTION** |
| How it enters optimization | `e_stage2_target[23] = max(ebr_target[23], terminal_target_wh)`, strict `J2` priority (above `J3` fuel), no weighting | **Unchanged — deliberately.** v2 does not alter this mechanism, its priority, or its interaction with `J3` | The counterfactual isolation already showed this mechanism contributes ~0% (−1.5%) of the Stage 8.1 diesel increase — there is no diesel-reduction case for touching it, and doing so would be exactly the "optimize for lower diesel" move this specification is instructed to avoid | `COUNTERFACTUAL_CAUSAL_ISOLATION_REPORT.md` | Existing evidence (the finding); the non-change is a deliberate design choice |

## 5. Diesel

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| Minimum output (10,000 W when on) | Hard floor, unconditional | **Unchanged** | No evidence supports a different value; this is a `CURRENT_IMPLEMENTATION_FACT` (`diesel.yaml`), not a policy question | `diesel.yaml` | Existing evidence |
| Base fuel cost (5 L/h flat whenever running) | Unchanged mechanism | **Unchanged** | Same as above; already matches D07's "liters as primary fuel metric" | `diesel.yaml` | Existing evidence |
| **Minimum-up-time** | `diesel.yaml` declares `min_up_time_hours: 2`; **confirmed never read or enforced anywhere in `gap19_highs_native.py`** | Add the standard unit-commitment minimum-up-time constraint (`u_diesel[t]` must remain 1 for at least 2 consecutive hours after a start) | This closes a **confirmed, code-vs-config inconsistency** found in the earlier forensic audit — the value already exists in governed config and is simply unenforced. **Explicitly not proposed to reduce fuel use** — minimum-up-time constraints can *increase* total fuel in some scenarios (forcing diesel to run past the point of strict need); direction is not predicted or claimed here, consistent with the instruction not to chase lower diesel. | `diesel.yaml`'s own value (2h), confirmed unused in code | Existing evidence for the value; the *enforcement mechanism itself* is a design proposal, not yet validated |
| Startup fuel (2 L/start), marginal fuel (0.00025 L/Wh) | Unchanged | **Unchanged** | No evidence to revise | `diesel.yaml` defaults | Existing evidence |

## 6. Battery

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| SOC limits (20–95%) | Unchanged | **Unchanged** | `CURRENT_IMPLEMENTATION_FACT`, no evidence to revise | `battery.yaml` | Existing evidence |
| Charge/discharge (efficiency, max power, exclusivity) | Unchanged | **Unchanged** | No evidence to revise | `battery.yaml` | Existing evidence |
| Reserve interaction | `E_next[t] + s_J2[t] ≥ e_stage2_target[t] + min_e_wh`, unchanged mechanism | **Unchanged** | Same rationale as §4 — not implicated in the diesel increase; no case for touching it | `COUNTERFACTUAL_CAUSAL_ISOLATION_REPORT.md` | Existing evidence |
| Degradation | `battery.yaml`'s `deg_penalty_per_wh` exists but is **never read by GAP19** (confirmed) | **Intentionally left unmodeled** — v2 does not add a degradation term | SD-08 (degradation curves) remains `NOT_ESTABLISHED`; adding a degradation cost now would be a scope expansion with zero real evidence basis, and v2 is not a regression relative to the frozen control since the control doesn't model it either | Decision 6 of simulated package (grade C) | **SIMULATED_RESEARCH_ASSUMPTION** (the decision to defer, not a modeling choice) |

## 7. Objective / lexicographic priority order

| | Current GAP19 | Proposed v2 | Reason | Evidence/assumption | Type |
|---|---|---|---|---|---|
| Priority structure | Strict `J1 (critical) > J2 (reserve) > J3 (fuel) > J4 (curtailment)`, `blend_multi_objectives = False`, no weighting anywhere | **Unchanged stage count and ordering.** The only addition is folding Essential-tier shedding cost into the existing `J4` vector (§1) — no 5th stage, no weighting introduced between any existing tiers. | Matches D15 exactly (4 stages: Critical → Resilience → Fuel → Renewables); introducing a weighted trade-off or a new stage would both exceed what D15 authorizes and risk being read as tuning the model to favor less diesel use, which this specification is explicitly told not to do | D15 | Existing evidence for the 4-stage structure; the J4-folding placement is simulated (§1) |

---

## What v2 fixes

- The confirmed **minimum-up-time enforcement gap** (`diesel.yaml`'s governed 2h value,
  currently inert in code) — a genuine implementation-vs-config inconsistency, not a policy
  invention.
- The confirmed **absence of any Essential/managed-shedding tier** — gives Tier 2 at least
  minimal, nonzero accounting instead of being indistinguishable from Tier 3.
- The confirmed **degenerate infeasibility-fallback plan** — replaces it with an explicit,
  logged route to the existing OptionD path, addressing D04's logging requirement.
- Partially improves `unmet_load`'s interpretability (Essential-tier shortfall becomes a
  tracked, costed quantity) — but does **not** fully resolve the metric, since Tier 3
  remains deliberately uncosted (by design, per D02) and real circuit-level tier mapping
  still does not exist.

## What v2 intentionally leaves unchanged

- The critical-load hard-cap mechanism and its top priority (`J1`) — already policy-aligned.
- The terminal-reserve mathematical mechanism, its formula, and its strict `J2` priority
  over `J3` — explicitly preserved because the counterfactual showed it is not the diesel
  driver; touching it here would have no basis and would risk appearing diesel-motivated.
- Diesel minimum-output floor and all fuel-cost coefficients.
- Battery SOC limits, efficiency, and reserve-interaction mechanics.
- The 4-stage lexicographic structure itself (no 5th stage, no weighting).
- Degradation modeling — deferred, not attempted.

## What remains uncertain

- Whether the simulated Essential-tier cost placement (folded into `J4`) is the governance
  structure a real stakeholder would actually choose, versus a dedicated new tier.
- Whether minimum-up-time enforcement would raise or lower total fuel use in practice — not
  determinable without a counterfactual re-solve, not performed here.
- Whether the simulated terminal-reserve formula/margin would survive real stakeholder
  review (unchanged question from R1/R2).
- Whether a real circuit-level load inventory would even support the Essential tier as
  sketched here, given `loads.yaml`'s `deferrable_loads` entries are themselves synthetic.

## What cannot be validated without real station data

- SD-07/SD-08 (battery vendor minimum SOC, degradation curves) — blocks any real
  terminal-reserve numeric value and any future degradation modeling.
- SD-01/SD-02/SD-03 (circuit-level load inventory, ATS switching gap, UPS hold-up time) —
  blocks turning the Essential/Flexible tier from a synthetic placeholder into something
  grounded in real station equipment.
- SD-13 (named approvers) — blocks any of this moving from "research design" to anything
  with real governance standing.

## STOP

Design specification only. No code was written, no config changed, no model modified, no
experiment run. GAP19 remains the frozen, unmodified control.
