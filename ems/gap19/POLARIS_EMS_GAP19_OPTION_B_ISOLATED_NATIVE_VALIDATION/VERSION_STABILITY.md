# VERSION STABILITY

## Package & C++ ABI Version Stability Analysis

This document evaluates the version stability and PyPI binary wheel lifecycle of `highspy`.

---

## Technical Audit Findings

- **Tested Version**: `highspy-1.15.1`
- **Supported Python Versions**: Python 3.8 through Python 3.12 (manylinux wheel tags).
- **C++ Engine Version**: HiGHS C++ v1.15.1.
- **Future Version Compatibility**: `highspy` is maintained by the HiGHS core development team on PyPI. While `addLinearObjective` is part of HiGHS's multi-objective C++ interface, version upgrades across major releases (e.g. v2.0) should be pinned in production requirements files (`highspy==1.15.1`).
