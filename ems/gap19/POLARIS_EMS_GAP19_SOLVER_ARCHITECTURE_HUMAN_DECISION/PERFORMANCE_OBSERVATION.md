# PERFORMANCE OBSERVATION

## Solver Pass Count & Execution Time Observations

This document records the performance metrics observed during toy MILP evaluation.

> [!WARNING]
> **NO EXTRAPOLATION NOTICE**:
> Observed timing metrics on a synthetic 2-variable toy MILP **MUST NOT** be extrapolated to predict full POLARIS EMS runtime performance over 24-step MPC horizons (504 decision variables).

---

## Toy Experiment Performance Observations

| Performance Metric | Option A (Sequential Solves) | Option B (Native Multi-Objective) |
| :--- | :--- | :--- |
| **Python Solver Function Calls** | 2 Calls (Pass 1 + Pass 2) | 1 Call (Theoretical) |
| **Observed Wall-Clock Time (Toy)** | $\approx 2.5\text{ ms}$ total across 2 passes | Not Executable in current environment |
| **Presolve Re-use** | Presolve runs independently per SciPy `milp()` invocation. | Presolve and basis reused internally in C++ engine across stages. |
| **Overhead Source** | Python interpreter call overhead between passes. | Internal C++ multi-objective data structure management. |

---

## Technical Summary

```text
A_B_PERFORMANCE_OBSERVATION = TOY_TIMING_OBSERVED_NOT_EXTRAPOLATED_TO_PRODUCTION
```
Option A incurs small Python invocation overhead per stage solve. Option B reduces Python call overhead by executing a single C++ call, but requires binary dependency management.
