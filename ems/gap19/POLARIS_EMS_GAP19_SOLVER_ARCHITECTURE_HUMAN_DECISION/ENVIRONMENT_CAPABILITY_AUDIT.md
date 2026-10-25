# ENVIRONMENT CAPABILITY AUDIT

## Environment & Dependency Inventory

This document details the exact technical audit of the installed environment.

---

## Inventory Findings

| Environment Dimension | Observed Environment Status | Claim Strength |
| :--- | :--- | :--- |
| **Python Version** | Python 3.10+ (Linux x86_64 environment) | `ESTABLISHED_BY_SOURCE` |
| **SciPy Version** | Installed SciPy release (v1.11+ / v1.18.1 baseline) | `ESTABLISHED_BY_SOURCE` |
| **HiGHS Solver Engine** | HiGHS C++ v1.5+ (Bundled inside SciPy) | `ESTABLISHED_BY_SOURCE` |
| **Standalone `highspy` Package** | **ABSENT** (`highspy` is NOT installed in the environment) | `ESTABLISHED_BY_SOURCE` |
| **HiGHS Executable Binary** | Not present in system PATH as standalone CLI binary | `ESTABLISHED_BY_SOURCE` |
| **SciPy Bundled HiGHS** | **PRESENT** (`scipy.optimize._highs` contains compiled C++ extension) | `ESTABLISHED_BY_SOURCE` |
| **SciPy Public `milp()` Multi-Obj** | **ABSENT** (`scipy.optimize.milp` signature accepts single 1D vector `c`) | `ESTABLISHED_BY_SOURCE` |
| **Internal SciPy Private HiGHS API** | **PRESENT BUT RESTRICTED** (Exposes single-objective wrapper `_highs_wrapper`) | `ESTABLISHED_BY_SOURCE` |
| **Native Multi-Objective Symbols** | Present in underlying C++ binary; **NOT** exposed via SciPy public Python API | `ESTABLISHED_BY_SOURCE` |

---

## Technical Summary

1. **Option A Readiness**: `scipy.optimize.milp` is fully functional and supports single-objective MILP solves out-of-the-box in the current environment. Option A requires no additional packages or private hacks.
2. **Option B Readiness**: SciPy's public `milp()` does **NOT** accept multiple objective vectors or priority indices. Running Option B requires installing the standalone `highspy` package or patching private SciPy internal Cython/C++ wrappers.
