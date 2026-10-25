# GAP19 DEPENDENCY REGISTER

## GAP19 Deferral Principle

This document explicitly identifies all EMS solver features, multi-objective formulations, and lexicographic orchestration mechanisms that are **DEFERRED TO GAP19**. 

> [!WARNING]
> **PRE-GAP19 FIREWALL**:
> Pre-GAP19 Option D implementation must **NOT** attempt to implement, simulate, or approximate any GAP19 multi-objective solver features. In particular, pre-GAP19 code must **NOT** introduce giant penalty weights into the scalar objective to emulate lexicographic priority order.

---

## Deferred Component Register

| Deferred Feature | GAP19 Responsibility | Pre-GAP19 Compatibility Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Stage 1 Objective: Critical Reliability** | Reformulate $D4$ proportional critical load allocation as Stage 1 primary objective in HiGHS lexicographic solver. | Enforce D4 via hard linear constraints ($P_{i,\text{served}} = \alpha P_{i,\text{min}}$) in scalar MILP. | `DEFERRED_TO_GAP19` |
| **Stage 2 Objective: EBR / Reserve Optimization** | Formulate Energy Buffer Ratio (EBR) and terminal state-of-charge reserve optimization. | Maintain static minimum battery SOC ($\text{SOC}_{\text{min}} = 20\%$) as hard bound. | `DEFERRED_TO_GAP19` |
| **Stage 3 Objective: Governed Fuel Optimization** | Formulate multi-period diesel fuel conservation and generator start minimization. | Enforce D6 generator rules via linear bounds; use scalar fuel cost coefficient. | `DEFERRED_TO_GAP19` |
| **Stage 4 Objective: Renewable / Curtailment** | Formulate Pareto-optimal renewable capture and curtailment minimization. | Use scalar renewable cost coefficients without altering balance equations. | `DEFERRED_TO_GAP19` |
| **Native HiGHS Lexicographic Orchestration** | C++ multi-stage sequential solve with tolerance passing between stages. | Single-pass scalar MILP solve using SciPy HiGHS wrapper interface. | `DEFERRED_TO_GAP19` |
| **Exact Pareto Stage Reporting** | Detailed per-stage objective value logging and trade-off frontier metrics. | Single scalar objective value reporting in `DispatchPlan`. | `DEFERRED_TO_GAP19` |

---

## Unopened Architecture Options

In prior architectural reviews, Option A (Integrated Multi-Objective Solver) and Option B (Separate Emergency Dispatch Heuristic) were evaluated. 

- **Option D Selection**: Strategy 2 (Option D Policy Layer + Solver-Neutral `ModeConstraintSet` + Linear Constraints) was chosen as the pre-GAP19 bridge.
- **No Reopening**: Option A and Option B selection decisions are sealed and will **NOT** be reopened during GAP19 solver development.
