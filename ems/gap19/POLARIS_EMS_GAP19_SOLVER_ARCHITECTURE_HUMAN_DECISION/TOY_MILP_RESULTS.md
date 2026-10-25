# TOY MILP RESULTS

## Empirical Evaluation Results on Synthetic Benchmark

This document records the evaluation results of the isolated synthetic toy MILP under Option A and Option B.

---

## Empirical Result Summary Table

| Metric / Dimension | Option A (Sequential Solves via SciPy `milp()`) | Option B (Native Multi-Obj Solver) |
| :--- | :--- | :--- |
| **Execution Environment Status** | `EXECUTED_CLEANLY_VIA_PUBLIC_API` | `NOT_EXECUTABLE_IN_CURRENT_ENVIRONMENT` |
| **Decision Vector $(x_1^*, x_2^*)$** | $(5.0, 0.0)$ | Not Executable (Missing `highspy` / public API) |
| **Primary Objective $J_1^*$** | $-5.0$ | Not Executable |
| **Secondary Objective $J_2^*$** | $0.0$ | Not Executable |
| **Priority Preservation** | **Strictly Preserved** ($x_1=5$ locked before $x_2$ optimized) | Not Executable |
| **Solver Pass Count** | 2 Passes | Not Executable (Expected 1 Python call) |
| **Feasibility Status** | `OPTIMAL` (Status 0 across both passes) | `NOT_EXECUTABLE` |

---

## Detailed Option A Execution Trace

```python
# Pass 1: Minimize J1 = -x1
res1 = scipy.optimize.milp(c=[-1.0, 0.0], integrality=[1, 0], constraints=constraints, bounds=bounds)
# Result: x1 = 5.0, x2 = 0.0, J1* = -5.0

# Add Lock Constraint: -x1 <= -5.0  (i.e. x1 >= 5.0)
lock_constraint = LinearConstraint(A=[[-1.0, 0.0]], lb=[-inf], ub=[-5.0])

# Pass 2: Minimize J2 = -x2 subject to initial constraints + lock_constraint
res2 = scipy.optimize.milp(c=[0.0, -1.0], integrality=[1, 0], constraints=combined_constraints, bounds=bounds)
# Result: x1 = 5.0, x2 = 0.0, J2* = 0.0
```

---

## Technical Finding for Option B

```text
B_RUNTIME_VALIDATION = NOT_EXECUTABLE_IN_CURRENT_ENVIRONMENT
REASON = SciPy public milp() does not expose multi-objective parameters, and highspy is not installed.
```
Option B cannot be executed in the current environment without installing `highspy` or using undocumented private SciPy C++ wrappers.
