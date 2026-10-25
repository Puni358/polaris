# TOLERANCE SEMANTICS

## Objective Tolerance Semantics Comparison

This document analyzes how objective tolerance limits are represented and enforced under Option A and Option B.

---

## Tolerance Mechanism Comparison

| Option | Tolerance Definition | Lock Constraint Equation | Visibility & Debuggability |
| :--- | :--- | :--- | :--- |
| **Option A** | Explicit lock scalar $\varepsilon_k$ (absolute or relative) managed by POLARIS Python logic. | $$J_k(x) \le J_k^* + \varepsilon_k$$ | **High**. Lock constraint equation is explicitly added to matrix $A$ and reported in solver logs. |
| **Option B** | Native C++ objective fields `abs_tolerance` and `rel_tolerance` passed to HiGHS solver structure. | Internal C++ bound: $$J_k(x) \le J_k^* + \text{abs\_tol} + \text{rel\_tol} \cdot |J_k^*|$$ | **Internal**. Managed inside HiGHS C++ solver state; intermediate lock values are not exposed in SciPy. |

---

## Technical Details

1. **Option A Flexibility**: POLARIS can apply custom non-linear or conditional tolerance logic between solver passes (e.g., setting $\varepsilon_1 = 0.0$ for critical load, while using relative percentage tolerance for fuel).
2. **Option B Uniformity**: HiGHS applies standard absolute and relative tolerance scalars during its internal sequential passes.
