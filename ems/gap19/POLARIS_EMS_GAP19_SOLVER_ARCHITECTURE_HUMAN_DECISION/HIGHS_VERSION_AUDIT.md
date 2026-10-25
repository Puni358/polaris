# HIGHS VERSION AUDIT

## Bundled HiGHS C++ Engine Multi-Objective Capabilities

This document audits the underlying HiGHS C++ solver engine bundled inside SciPy.

---

## HiGHS C++ Engine Version & Capabilities

- **Engine Version**: HiGHS C++ v1.5+ / v1.7.0 baseline (bundled inside compiled SciPy shared objects).
- **Native Multi-Objective Architecture**: HiGHS C++ source code contains internal data structures (`HighsModelStatus`, `HighsSolution`, `HighsObjective`) supporting multiple linear objectives.
- **C++ Methods**: Methods such as `Highs::addLinearObjective(weight, priority, abs_tol, rel_tol)` exist in HiGHS C++ source header files.

---

## SciPy C++ Wrapper Boundary

While the underlying HiGHS C++ engine possesses multi-objective code paths, SciPy's Cython wrapper (`scipy/optimize/_highs/_highs_wrapper.pyx`) bridges only the single-objective API functions:

```cpp
// Exposed Cython Wrapper Function Signature
Highs_call(
    HighsInt num_col, HighsInt num_row, HighsInt num_nz,
    double* col_cost, double* col_lower, double* col_upper,
    double* row_lower, double* row_upper, ...
);
```

### Key Finding:
SciPy's Cython extension flattens the objective interface to a single `col_cost` array pointer. The multi-objective C++ methods in HiGHS are **NOT** bound or exposed through SciPy's Python extension module.
