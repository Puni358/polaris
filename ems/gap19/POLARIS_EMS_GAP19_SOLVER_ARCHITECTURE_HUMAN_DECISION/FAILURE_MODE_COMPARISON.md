# FAILURE MODE COMPARISON

## Solver Failure Modes & Debugging Visibility Comparison

This document provides a factual comparison of failure modes, infeasibility handling, and debugging visibility between Option A and Option B.

---

## Failure Mode Comparison Matrix

| Failure / Debug Scenario | Option A (Sequential Solves) | Option B (Native Solver Multi-Obj) |
| :--- | :--- | :--- |
| **Infeasibility at Stage $k$** | **Isolated Immediately**. Returns SciPy status code (e.g., Status 2: Infeasible) on exact Pass $k$ where lock constraint caused infeasibility. | Returns overall solver status. Identifying which objective priority caused infeasibility requires inspecting C++ log streams. |
| **Unboundedness** | Detected on Pass 1 before proceeding to lower-priority stages. | Handled internally by solver engine. |
| **Tolerance Misconfiguration** | Manifests as infeasibility or loose bounds on specific Pass $k$, inspectable in Python log. | Manifests as unexpected trade-offs or blending if priority index or `blend_multi_objectives` is misconfigured. |
| **Debugging Visibility** | **High**. Intermediate objective values $J_1^*, J_2^*, J_3^*$ are directly readable as float returns in Python after each pass. | **Medium**. Requires reading multi-objective attributes or C++ stdout buffers. |

---

## Technical Summary

Option A provides granular Python-level step debugging for each lexicographic stage. Option B delegates error handling to C++ internal state, requiring C++ log inspection during solver debugging.
