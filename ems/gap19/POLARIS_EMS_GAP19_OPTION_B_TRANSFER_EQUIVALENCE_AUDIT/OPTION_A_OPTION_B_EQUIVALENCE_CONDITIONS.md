# OPTION A OPTION B EQUIVALENCE CONDITIONS

## Complete 14-Point Equivalence Conditions Register

This document establishes the 14 mandatory mathematical and solver conditions under which Option A and Option B are mathematically equivalent.

---

## The 14 Equivalence Conditions

1. **Identical Feasible Region**: Matrix $A$, vector $b$, bounds $lb, ub$ match 100%.
2. **Identical Decision Variables**: Exact same variable ordering and index offsets.
3. **Identical Physical Constraints**: All 12 physical constraint equations match.
4. **Identical $J_1$ Coefficients**: Exact same Stage 1 cost vector $c_1$.
5. **Identical $J_2$ Coefficients**: Exact same Stage 2 cost vector $c_2$.
6. **Identical $J_3$ Coefficients**: Exact same Stage 3 cost vector $c_3$.
7. **Identical $J_4$ Coefficients**: Exact same Stage 4 cost vector $c_4$.
8. **Identical Objective Direction**: Minimization sense across all 4 stages.
9. **Identical Priority Order**: Hierarchy order $1 \rightarrow 2 \rightarrow 3 \rightarrow 4$.
10. **Equivalent Tolerance Semantics**: Option A lock tolerances $\varepsilon_k$ match Option B native tolerances `abs_tolerance`.
11. **Strict Lexicographic Mode**: Option B sets `blend_multi_objectives = False`.
12. **Identical Tie-Breaking Rule**: Equal-objective primal optima resolved deterministically.
13. **Identical MIP Feasibility Tolerance**: `mip_rel_tolerance = 1e-4` across both solvers.
14. **Identical Infeasibility Handling**: Infeasible problems return clean degraded status.

---

## Technical Audit Status

```text
A_B_EQUIVALENCE_CONDITIONS = DEFINED
```
All 14 conditions are defined and recorded.
