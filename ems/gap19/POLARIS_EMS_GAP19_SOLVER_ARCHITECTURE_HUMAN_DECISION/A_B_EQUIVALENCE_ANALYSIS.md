# A B EQUIVALENCE ANALYSIS

## Mathematical & Algorithmic Equivalence Conditions

This document evaluates the conditions under which Option A and Option B yield identical mathematical optimization results.

---

## Equivalence Conditions Matrix

Option A and Option B are **mathematically equivalent** if and only if all of the following 6 conditions are satisfied:

| Condition # | Equivalence Domain | Exact Requirement |
| :--- | :--- | :--- |
| **1** | **Feasible Region** | Exact same constraint matrix $A$, lower bounds $lb$, upper bounds $ub$, and variable integrality definitions. |
| **2** | **Objective Functions** | Identical linear cost vectors $c_1, c_2, c_3, c_4$ passed in identical priority order. |
| **3** | **Mode Selection** | Option B must run in strict lexicographic mode (`blend_multi_objectives = False`). |
| **4** | **Tolerance Semantics** | Option A lock tolerances $\varepsilon_k$ match Option B native solver tolerances `abs_tolerance` and `rel_tolerance`. |
| **5** | **Solver Precision** | Identical MIP feasibility tolerance (`mip_feasibility_tolerance`), primal/dual tolerances, and presolve levels. |
| **6** | **Zero Degeneracy Bias** | In the presence of multiple primal optima at intermediate stages, both options must use deterministic tie-breaking. |

---

## Technical Summary

```text
A_B_MATHEMATICAL_EQUIVALENCE = EQUIVALENT_UNDER_SPECIFIED_CONDITIONS
TOY_PROBLEM_EQUIVALENCE = CONDITIONAL_ON_ENVIRONMENT
```
Under exact matching tolerances and strict lexicographic settings, Option A and Option B solve identical mathematical sub-problems.
