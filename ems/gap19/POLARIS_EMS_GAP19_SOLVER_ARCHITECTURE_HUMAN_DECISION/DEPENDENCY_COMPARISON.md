# DEPENDENCY COMPARISON

## Third-Party Package & API Dependency Comparison

This document provides a factual comparison of software dependencies required by Option A and Option B.

---

## Dependency Comparison Table

| Dependency Dimension | Option A | Option B |
| :--- | :--- | :--- |
| **Python Standard Library** | Compatible | Compatible |
| **Public SciPy API (`scipy.optimize.milp`)** | **Required** (v1.11+) | Not Used (Public API lacks multi-obj parameters) |
| **Private SciPy Module (`scipy.optimize._highs`)** | **Not Required** | Required if using internal SciPy C++ wrappers |
| **Standalone `highspy` Package** | **Not Required** | Required if using official HiGHS Python bindings |
| **Compiled C++ Binary Extension** | Standard SciPy wheel (`_highs.so`) | Dedicated `highspy` wheel or patched SciPy wheel |
| **Virtual Environment Modifications** | **None** (Works out-of-the-box) | Requires `pip install highspy` or custom SciPy build |

---

## Technical Summary

- **Option A**: Zero new dependencies. Operates entirely within standard public SciPy.
- **Option B**: Requires adding `highspy` to package requirements or relying on private, undocumented SciPy internal C++ wrappers.
