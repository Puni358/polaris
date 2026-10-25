# OPTION A COMPARISON

## Strictly Neutral Technical Comparison Matrix

This document provides a strictly neutral side-by-side comparison of Option A and Option B established by our isolated technical audits.

---

## Technical Comparison Table

| Technical Dimension | OPTION A (Sequential SciPy Solves) | OPTION B (Standalone `highspy` Native Solver) |
| :--- | :--- | :--- |
| **Public API Availability** | Supported via `scipy.optimize.milp` | Supported via `highspy.Highs` and `addLinearObjective` |
| **Multi-Objective Engine** | Programmatic sequence in Python | Native C++ multi-objective engine in HiGHS |
| **Additional Dependencies** | None (Uses pre-installed SciPy) | Requires `highspy` PyPI binary wheel package |
| **Private API Required** | No | No (via standalone `highspy`) |
| **Native Execution Demonstrated** | N/A (Uses sequential single-obj calls) | **Demonstrated** in isolated environment |
| **Lexicographic Behavior** | Explicit linear lock constraints ($J_k(x) \le J_k^* + \varepsilon_k$) | Explicit C++ option `blend_multi_objectives = False` |
| **Tolerance Mechanism** | Explicit lock tolerance scalars in Python | Native C++ objective tolerance fields (`abs_tolerance`) |
| **Offline Runtime** | 100% Offline | 100% Offline |
| **Version Coupling** | Low (Public SciPy API) | Medium (Tied to `highspy` binary wheel version) |
| **Reproducibility** | Verified deterministic | **Verified deterministic** on toy benchmarks |
| **POLARIS Production Validation** | Not performed (Read-only gate) | Not performed (Read-only gate) |

---

## Neutrality Statement

> [!NOTE]
> This comparison table contains strictly factual metrics. No scores, ranks, winners, or preferences are assigned.
