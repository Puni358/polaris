# POLARIS Stage 5.4 — Spatial NWP Feature Evaluation (REVISED / AUDITED)

This directory contains the revised artifacts, experiment code, and evaluation results for POLARIS Stage 5.4 under a strict apples-to-apples baseline comparison protocol.

## Baseline Reconciliation Audit
- **Initial Discrepancy Identified:** The initial script refit Stage 4 parameters per fold for ODD testing, which altered the base predictions.
- **Corrected E0 Baseline:** Matches official frozen Stage 5.2 Architecture A ODD Daytime MAE of **39.0848 W/m²** (30.32% nMAE) with zero error.

## Summary Results Table

| Model / Experiment | Features | EVEN CV MAE | EVEN CV Delta | ODD Test MAE | ODD Test nMAE | ODD Delta vs. Frozen Champion |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stage 5.2 Champion (E0)** | **28** | **39.4236** | `0.0000` | **39.0848** | **30.32%** | **0.0000 (FROZEN CHAMPION)** |
| Candidate E1 (+ Wind) | 30 | 39.4679 | `+0.0443` | 39.1969 | 30.40% | `+0.1121` (Worse) |
| Candidate E2 (+ Probes) | 34 | 39.1629 | `-0.2607` | 39.5217 | 30.65% | `+0.4369` (Worse) |
| Candidate E3 (+ Advection)| 39 | 39.1501 | `-0.2735` | 39.5262 | 30.66% | `+0.4414` (Worse) |
| Candidate E4 (Combined) | 41 | 38.9974 | `-0.4262` | 39.6653 | 30.77% | `+0.5804` (Worse) |

## Final Conclusion
- **Decision Gate:** **GATE B — WEAK / INCONSISTENT SIGNAL**
- **Active Champion:** **Stage 5.2 Architecture A (39.0848 W/m² Daytime MAE / 30.32% nMAE)** remains the unbeaten, locked champion of the POLARIS benchmark.
- **Scientific Takeaway:** Stage 5.4 spatial NWP probes showed a modest and inconsistent improvement during EVEN forward-chaining cross-validation but failed to generalize to the held-out ODD test set. The candidate spatial features were therefore rejected from the operational champion. This result does not establish that spatial atmospheric information is intrinsically uninformative; it indicates that the tested spatial representation did not provide robust out-of-sample improvement under the current benchmark and model architecture. Candidate spatial features at approximately the native model-grid scale (~2.5 km offset) are not adopted into the champion baseline.
