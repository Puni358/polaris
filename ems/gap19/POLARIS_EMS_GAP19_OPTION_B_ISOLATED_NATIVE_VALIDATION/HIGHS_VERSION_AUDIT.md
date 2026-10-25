# HIGHS VERSION AUDIT

## Embedded HiGHS C++ Engine Audit

This document details the HiGHS C++ solver engine version embedded within `highspy`.

---

## C++ Engine Audit Findings

- **Engine Major Version**: `1` (`HIGHS_VERSION_MAJOR = 1`)
- **Engine Minor Version**: `15` (`HIGHS_VERSION_MINOR = 15`)
- **Engine Patch Version**: `1` (`HIGHS_VERSION_PATCH = 1`)
- **Full Engine Version**: `HiGHS C++ v1.15.1`
- **Native Multi-Objective C++ Capabilities**: Native C++ engine contains full multi-objective data structures and C++ optimization methods (`Highs::addLinearObjective`, `Highs::clearLinearObjectives`).
