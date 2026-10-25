# PUBLIC VS PRIVATE API

## Public API vs Private API Classification

This document classifies the API surface used for Option B standalone `highspy` validation.

---

## API Classification Table

| API Domain | Access Method | Classification | Stability Status |
| :--- | :--- | :--- | :--- |
| **`highspy.Highs`** | Standard module import | `PUBLIC_HIGHSPY_API` | Documented Pybind11 Public Class |
| **`addLinearObjective`** | Method on `Highs` instance | `PUBLIC_HIGHSPY_API` | Documented C++ Engine Wrapper |
| **`HighsLinearObjective`** | Data structure class | `PUBLIC_HIGHSPY_API` | Documented Attribute Container |
| **`scipy.optimize._highs`** | Private SciPy C++ module | `PRIVATE_SCIPY_MODULE` | **NOT USED** in standalone validation |

---

## Technical Summary

```text
PRIVATE_API_REQUIRED = NO
```
Standalone `highspy` provides a 100% public API for native multi-objective MILP optimization.
