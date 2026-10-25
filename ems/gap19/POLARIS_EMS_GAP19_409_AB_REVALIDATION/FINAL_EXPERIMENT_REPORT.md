# Final Experiment Report

## Master Comparison Register

| Property | Option A Reference | Option B Implementation | Equivalent? |
| :--- | :---: | :---: | :---: |
| **Model Variables ($N$)** | 409 | 409 | **YES** |
| **Constraints ($M$)** | 313 | 313 | **YES** |
| **Binary Variables** | 96 | 96 | **YES** |
| **Continuous Variables** | 313 | 313 | **YES** |
| **Model Fingerprint** | `4a57d155...` | `4a57d155...` | **YES** |
| **Feasible Region** | Identical | Identical | **YES** |
| **Stage 1 ($J_1$)** | Exact Match | Exact Match | **YES** |
| **Stage 2 ($J_2$)** | Exact Match | Exact Match | **YES** |
| **Stage 3 ($J_3$)** | Exact Match | Exact Match | **YES** |
| **Stage 4 ($J_4$)** | Exact Match | Exact Match | **YES** |
| **Max Constraint Residual** | $< 10^{-10}$ | $< 10^{-10}$ | **YES** |
| **Max Bound Violation** | $0.0$ | $0.0$ | **YES** |
| **Max Integrality Violation** | $0.0$ | $0.0$ | **YES** |
| **Decision Vector** | Degenerate Optimum | Degenerate Optimum | **OBJECTIVE EQUIVALENT** |
| **Solver Status** | `OPTIMAL` | `OPTIMAL` | **YES** |
| **Fresh-Process Replay** | Pass | Pass | **YES** |

## Regime Results

| Regime | $J_1$ A | $J_1$ B | $J_2$ A | $J_2$ B | $J_3$ A | $J_3$ B | $J_4$ A | $J_4$ B | Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Renewable Surplus** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1885168.2 | 1885168.2 | **PASS** |
| **Diesel Required** | 0.0 | 0.0 | 0.0 | 0.0 | 142.5690 | 142.5690 | 0.0 | 0.0 | **PASS** |
| **High Curtailment** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4285168.2 | 4285168.2 | **PASS** |
