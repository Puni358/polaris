# DEPENDENCY VERSION GOVERNANCE

## Implementation Pinning Specifications for Option B

This document defines the strict version pinning specification for implementing Option B.

---

## Pinning Specification

```text
PYTHON_VERSION = 3.12+ (Linux x86_64)
HIGHSPY_VERSION = 1.15.1
HIGHS_ENGINE_VERSION = 1.15.1
NUMPY_VERSION = 2.5.3 (or compatible)
```

- **PyPI Package**: `highspy==1.15.1`
- **Wheel Requirement**: `highspy-1.15.1-cp312-cp312-manylinux_2_24_x86_64.whl` (or equivalent Linux wheel).
- **Offline Deployment**: Wheel artifact MUST be cached in local station package repository for 100% offline installation.
- **Rule**: Do NOT upgrade `highspy` across major/minor releases without repeating the isolated multi-objective equivalence audit.
