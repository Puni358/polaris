# OBJECTIVE PRIORITY SEMANTICS

## Objective Priority Semantics Comparison

This document analyzes how objective priorities are defined and enforced under Option A and Option B.

---

## Priority Enforcement Comparison

| Option | Priority Definition Mechanism | Priority Order Enforcement | Risk of Priority Blending |
| :--- | :--- | :--- | :--- |
| **Option A** | Programmatic sequence of Python function calls (`solve(J1)` $\rightarrow$ `solve(J2)` $\rightarrow$ `solve(J3)` $\rightarrow$ `solve(J4)`). | Strict sequential execution. Pass $k+1$ cannot execute until Pass $k$ completes and appends its lock constraint. | **Zero**. Passes execute independently in Python code. |
| **Option B** | Integer priority parameter assigned to each objective structure (e.g., `priority=1`, `priority=2`). | Managed internally by HiGHS C++ multi-objective engine. | **Non-Zero**. If solver option `blend_multi_objectives` is set or if equal priority indices are passed, objectives are blended into a weighted sum. |

---

## Technical Details

1. **Option A Priority Semantics**: Priority order is 100% deterministic and controlled by POLARIS Python execution order. Stage 1 is guaranteed to be fully resolved before Stage 2 is formulated.
2. **Option B Priority Semantics**: In HiGHS C++, priority indices determine lexicographic order (e.g., Priority 1 is optimized before Priority 2). To guarantee strict lexicographic order without blending, `blend_multi_objectives` must be explicitly set to `False` in HiGHS solver options.
