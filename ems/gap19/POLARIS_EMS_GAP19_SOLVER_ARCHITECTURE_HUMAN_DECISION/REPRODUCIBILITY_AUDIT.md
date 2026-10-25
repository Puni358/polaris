# REPRODUCIBILITY AUDIT

## Determinism & Reproducibility Evaluation

This document evaluates the determinism and reproducibility of Option A and Option B across execution runs and environments.

---

## Reproducibility Comparison

| Metric | Option A | Option B |
| :--- | :--- | :--- |
| **Deterministic Output** | **100% Deterministic**. Sequential SciPy `milp()` calls produce bit-for-bit identical decision vectors $x^*$ across repeated runs. | **100% Deterministic** in C++ solver engine if random seed and thread count are fixed. |
| **Cross-Environment Portability** | **High**. Uses standard SciPy public API available on any Python system with SciPy installed. | **Medium**. Tied to specific HiGHS C++ library versions and `highspy` build flags. |
| **Audit Traceability** | **High**. Each stage's intermediate objective value $J_k^*$, status code, and lock constraint are logged in Python. | **Medium**. Intermediate stage objective values require parsing HiGHS C++ log streams or solver attributes. |

---

## Technical Finding

```text
A_B_REPRODUCIBILITY = BOTH_DETERMINISTIC_UNDER_FIXED_SEEDS
```
Both options produce deterministic results when executed in a clean process with fixed solver seeds and single-threaded execution.
