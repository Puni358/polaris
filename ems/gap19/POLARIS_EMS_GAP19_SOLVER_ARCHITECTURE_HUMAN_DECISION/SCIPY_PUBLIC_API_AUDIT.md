# SCIPY PUBLIC API AUDIT

## Signature & Capability Analysis of `scipy.optimize.milp`

This document details the public API audit of SciPy's Mixed-Integer Linear Programming solver.

---

## Function Signature Audit

```python
scipy.optimize.milp(
    c,                        # 1D array_like: Objective coefficients (Single vector)
    *,
    integrality=None,         # 1D array_like: Variable integrality types (0: cont, 1: int, 2: semi-cont, 3: semi-int)
    bounds=None,              # Bounds object specifying lower/upper bounds on variables
    constraints=None,         # LinearConstraint object specifying matrix A, lb, ub
    options=None              # Dictionary of solver options (time_limit, presolve, etc.)
)
```

---

## Parameter Capability Analysis

| Parameter / Feature | Support Status | Description |
| :--- | :--- | :--- |
| **Objective Vector `c`** | `SINGLE_VECTOR_ONLY` | Accepts a 1D array of shape `(n,)`. Does **NOT** accept 2D matrices or lists of vectors. |
| **Integrality `integrality`** | `FULLY_SUPPORTED` | Full support for continuous, integer, and binary variables. |
| **Linear Constraints** | `FULLY_SUPPORTED` | Accepts `scipy.optimize.LinearConstraint` ($lb \le A \cdot x \le ub$). |
| **Objective Priorities** | `NOT_EXPOSED` | Public API exposes zero priority arguments (`priority`, `objective_priority`). |
| **Objective Tolerances** | `NOT_EXPOSED` | Public API exposes zero objective lock tolerance parameters. |
| **Lexicographic Mode** | `NOT_EXPOSED` | Public API provides zero multi-objective or lexicographic parameters. |

---

## Audit Verdict for Public API

> [!NOTE]
> `scipy.optimize.milp` in SciPy (v1.11 through v1.18+) is strictly a **single-objective MILP solver interface**.
> 
> Implementing **Option A** using `scipy.optimize.milp` is **100% supported** by invoking `milp()` sequentially and appending lock constraints to `constraints`.
> 
> Implementing **Option B** via `scipy.optimize.milp` is **NOT POSSIBLE** without altering SciPy source code or using private internal modules.
