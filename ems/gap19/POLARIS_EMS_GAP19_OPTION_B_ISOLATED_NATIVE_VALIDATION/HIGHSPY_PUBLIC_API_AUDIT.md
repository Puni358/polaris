# HIGHSPY PUBLIC API AUDIT

## Public API Class & Method Inspection

This document details the public API methods exposed by `highspy` (v1.15.1).

---

## Public API Symbols

```python
import highspy

# Model & Engine Handle
h = highspy.Highs()

# Multi-Objective Methods Exposed on Highs Instance
h.addLinearObjective(obj: highspy.HighsLinearObjective) -> highspy.HighsStatus
h.clearLinearObjectives() -> highspy.HighsStatus
h.getNumLinearObjectives() -> int
h.getLinearObjective(index: int) -> highspy.HighsLinearObjective
```

---

## `HighsLinearObjective` Class Specification

```python
# Data Descriptors Exposed on HighsLinearObjective
obj = highspy.HighsLinearObjective()
obj.coefficients   # 1D numpy array of float64 cost coefficients
obj.offset         # float objective offset
obj.priority       # int priority index (Lower integer = Higher priority)
obj.weight         # float objective weight scalar
obj.abs_tolerance  # float absolute objective tolerance limit
obj.rel_tolerance  # float relative objective tolerance limit
```

---

## Audit Verdict

```text
HIGHSPY_PUBLIC_API = CONFIRMED
```
All multi-objective methods and linear objective structures are exposed via public Pybind11 class interfaces. No private API, ctypes, or C++ ABI hacks are required to invoke native multi-objective MILP through `highspy`.
