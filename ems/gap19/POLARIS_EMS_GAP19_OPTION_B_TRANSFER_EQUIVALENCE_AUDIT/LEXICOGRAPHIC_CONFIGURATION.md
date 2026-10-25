# LEXICOGRAPHIC CONFIGURATION

## Solver Multi-Objective Option Pinning Specification

This document specifies the exact solver options required to enforce strict lexicographic mode in `highspy`.

---

## Required Solver Configuration

```python
import highspy

h = highspy.Highs()

# Enforce strict lexicographic mode (Prevent objective blending)
h.setOptionValue("blend_multi_objectives", False)

# Set MIP relative tolerance for presolve and integer branch-and-bound
h.setOptionValue("mip_rel_tolerance", 1e-4)

# Set single-threaded execution for 100% bit-for-bit determinism
h.setOptionValue("threads", 1)
```

---

## Version Pinning Requirement

- **Python Version**: `3.12+`
- **`highspy` PyPI Package**: `highspy==1.15.1`
- **Embedded HiGHS Engine**: `v1.15.1`
