# NATIVE MULTI-OBJECTIVE MILP AUDIT

## Verification of Native Lexicographic MILP Support

This document provides the authoritative technical verification of native multi-objective MILP capabilities in HiGHS.

---

## 1. Algorithmic Verification

```text
HIGHS_NATIVE_MULTI_OBJECTIVE_MILP_STATUS = CONFIRMED_BUT_QUALIFIED
```

### Forensic Findings:
1. **HiGHS Engine Support**: HiGHS (v1.5.0+) supports native multi-objective linear optimization. For lexicographic MILP, HiGHS internally executes sequential solves while reusing the branch-and-bound tree and presolve data structures where possible.
2. **SciPy Environment Status**: In the currently installed environment, native multi-objective MILP is **NOT ACCESSIBLE** via SciPy's public API (`scipy.optimize.milp`).
3. **Qualification**: To access native multi-objective MILP, POLARIS must either:
   - Install the external `highspy` C++ wrapper package, OR
   - Use private internal SciPy C++ wrappers (`scipy.optimize._highs`).

---

## 2. Option Classification Summary

- **Option A (Sequential Solves via SciPy `milp()`)**: `FULLY_SUPPORTED_IN_CURRENT_ENVIRONMENT`.
- **Option B (Native Solver Multi-Objective)**: `REQUIRES_EXTERNAL_HIGHSPY_OR_PRIVATE_API`.
