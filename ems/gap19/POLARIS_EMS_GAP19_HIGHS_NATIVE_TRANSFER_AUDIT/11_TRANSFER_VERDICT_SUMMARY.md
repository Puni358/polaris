# POLARIS EMS GAP19 — HIGHS NATIVE TRANSFER AUDIT
# Document 11: TRANSFER VERDICT SUMMARY
# Audit Phase: GAP19_HIGHS_NATIVE_TRANSFER_AUDIT
# Generation Mode: READ-ONLY SYNTHESIS
# Execution Performed: FALSE
# Audit Date: 2026-09-22

---

## GOVERNING QUESTION

> *Can the actual POLARIS MILP formulation be transferred from
> `scipy.optimize.milp()` to a lexicographic multi-stage objective
> (Option A: sequential MILP, or Option B: native HiGHS multi-objective)
> without changing the mathematical optimization problem?*

---

## VERDICT

### Mathematical Transferability of the MILP Problem

**VERDICT: YES — The MILP optimization problem (variables + constraints) is
fully mathematically transferable to either option.**

The 360-variable structure, all 12 constraint types, and all variable bounds
(physical limits, binary commitment, battery SOC) transfer without modification
to any standard MILP solver API, including both the existing scipy interface and
the highspy interface.

---

### Option A: Sequential MILP Objective Locking (scipy-compatible)

**VERDICT: FEASIBLE within the current SciPy API.**

| Component | Status |
|---|---|
| Decision variables | Transfer directly — no change |
| Constraints (C1–C12) | Transfer directly — no change |
| Stage 1 objective (p_unmet) | Direct extraction from current c vector |
| Stage 2 objective (terminal reserve) | **NEW FORMULATION REQUIRED** — not currently in objective |
| Stage 3 objective (diesel/fuel/startup) | Direct extraction from current c vector |
| Stage 4 objective (renewable curtailment) | Direct extraction from current c vector |
| Lexicographic enforcement mechanism | Epsilon-constraint: add c_k^T x ≤ z_k* after each stage solve |
| Solver library | scipy.optimize.milp — no change |
| Blocking items | OI-1 OI-2 (Stage 2 formulation + E_EBR_target) OI-3 (epsilon values) OI-6 (temporal weighting) OI-7 (DispatchPlan reporting) |

**Option A does NOT require HiGHS multi-objective capability.**
**Option A does NOT require changing the solver library.**
**Option A is the lower-risk path from an implementation standpoint.**

---

### Option B: Native HiGHS Multi-Objective (highspy required)

**VERDICT: CONDITIONALLY FEASIBLE — subject to dependency resolution.**

| Component | Status |
|---|---|
| Decision variables | Transfer directly — same structure |
| Constraints (C1–C12) | Transfer directly — same structure |
| Stage 2 objective | **NEW FORMULATION REQUIRED** — same as Option A |
| Lexicographic enforcement mechanism | HiGHS native IF confirmed stable for MILP |
| Solver library | **Requires highspy** — not currently installed |
| HiGHS MILP multi-objective (stable) | **NOT CONFIRMED** — HiGHS multi-obj LP exists experimentally; MILP multi-obj stable status is unconfirmed |
| Blocking items | OI-1 OI-2 (same as Option A) + OI-4 (highspy install) + OI-5 (HiGHS version confirmation) |

**Option B mathematical equivalence to Option A is conditionally established:**
Equivalent when: same objective order, same epsilon tolerance (0), same feasibility
region, same underlying HiGHS solver engine. NOT equivalent if Option B uses
Pareto-front enumeration instead of strict lexicographic priority.

---

## KEY DISTINCTIONS

| Distinction | Finding |
|---|---|
| scipy API capability vs HiGHS native capability | **CLEARLY DISTINGUISHED** — scipy.optimize.milp exposes ONLY single-objective MILP. HiGHS native (via highspy) may expose more. These are different access paths. |
| Engineering effort vs mathematical incompatibility | **CONFIRMED SEPARATE** — All mathematical components are transferable. Engineering effort (highspy, Stage 2 formulation, sequential solve logic) is not a mathematical barrier. |
| Option A vs Option B mathematical equivalence | **CONDITIONAL** — Analytically equivalent under matched conditions (see doc 06). Not yet empirically verified. |
| Current formulation vs governed objective | **STRUCTURAL GAP EXISTS** — Current formulation is weighted-sum; governed objective is lexicographic. This gap is present regardless of Option A vs B choice. The gap is NOT introduced by either option — it pre-exists. |

---

## WHAT THE AUDIT CONFIRMS

1. The MILP feasibility region (variables + constraints + bounds) is **fully transferable** to either option without mathematical change.
2. Stage 1 (unmet load), Stage 3 (diesel/fuel), and Stage 4 (curtailment) objective terms **exist in the current code** and can be extracted by decomposing the current c vector.
3. Stage 2 (terminal battery reserve) **does not exist** in the current objective and requires formulation work for BOTH options.
4. `scipy.optimize.milp` **cannot access** HiGHS native multi-objective features — confirmed by API inspection.
5. `highspy` is **not currently installed** in POLARIS — confirmed by prior session investigation.
6. **Battery degradation penalties** (p_chg, p_dis) have **no explicit governed stage assignment** — this is an open governance item.

---

## WHAT THE AUDIT DOES NOT CONFIRM

- Empirical equivalence of Option A vs Option B outputs (requires execution — outside read-only scope).
- Exact HiGHS version bundled in current scipy install (requires execution).
- Whether HiGHS stable MILP multi-objective is production-ready (requires version-specific documentation or execution evidence).
- Numerical behavior under edge cases (INFEASIBLE stages, degenerate optima).

---

## AUDIT INTEGRITY STATEMENT

This audit was conducted entirely from:
- Static source code inspection of `system/optimization/implementations/milp.py`
- Static inspection of `system/config/optimizer.yaml`
- API documentation review (scipy.optimize.milp, HiGHS)
- Synthesis of prior governance documents

No MILP was executed. No EMS was executed. No code was modified. No
dependencies were installed. No solvers were run.

The audit is a read-only mathematical equivalence investigation.
