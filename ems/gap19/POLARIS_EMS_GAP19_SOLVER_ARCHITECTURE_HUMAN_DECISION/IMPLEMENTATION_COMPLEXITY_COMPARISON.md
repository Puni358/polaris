# IMPLEMENTATION COMPLEXITY COMPARISON

## Factual Software Complexity & Maintenance Surface Comparison

This document provides a factual, unranked comparison of implementation complexity between Option A and Option B.

---

## Factual Complexity Comparison Table

| Software Dimension | Option A (Sequential Solves) | Option B (Native Solver Multi-Obj) |
| :--- | :--- | :--- |
| **Python Code Surface** | $\approx 80\text{--}120$ lines of Python orchestration code (managing passes, locks, and bounds). | $\approx 30\text{--}50$ lines of Python setup code (registering objectives, priorities, and options). |
| **Solver Pass Loop** | Explicit `for stage in stages:` loop in Python. | Single `solver.solve()` call in Python. |
| **Dependency Management** | Zero external dependency setup; uses pre-installed SciPy. | Requires managing `highspy` binary package or private Cython C++ wrappers. |
| **C++ / Cython Coupling** | None. Standard Python library usage. | High. Directly tied to HiGHS C++ class methods and Cython extension ABI. |
| **Debugging Complexity** | Python-level step-by-step variable inspection between passes. | Multi-objective state debugging inside C++ engine. |
| **Presolve / Basis Management** | Presolve runs on each SciPy `milp()` call unless warm-start options are passed. | Presolve and basis reused natively in C++ solver engine. |

---

## Neutral Summary

Option A requires more Python orchestration lines but zero extra binary dependencies. Option B requires fewer Python orchestration lines but introduces binary dependency coupling and C++ solver binding complexity.
