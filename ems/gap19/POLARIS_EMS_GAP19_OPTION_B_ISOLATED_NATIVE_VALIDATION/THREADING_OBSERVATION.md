# THREADING OBSERVATION

## Solver Threading Test Observation

This document records the solver thread count observation (`threads = 1` vs `threads = 4`).

---

## Threading Test Observations

| Thread Count Setting | Solution Vector $(x_1^*, x_2^*)$ | Model Status | Output Match |
| :--- | :--- | :--- | :--- |
| `threads = 1` | `[10.0, 0.0]` | `HighsModelStatus.kOptimal` | Baseline |
| `threads = 4` | `[10.0, 0.0]` | `HighsModelStatus.kOptimal` | Identical |

---

## Technical Summary

Thread count changes did not alter the returned decision vector on the synthetic toy MILP.
