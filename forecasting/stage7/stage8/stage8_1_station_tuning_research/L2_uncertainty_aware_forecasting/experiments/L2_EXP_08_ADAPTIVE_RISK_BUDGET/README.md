# L2-EXP-08 — Pre-Registered Adaptive Risk-Budget EMS Interface

## Experiment Overview
This experiment tests whether an adaptive, uncertainty-dependent solar planning rule can retain most of the microgrid reliability gained by conservative $q_{10}$ planning (established in L2-EXP-07) while avoiding the heavy fuel (+38.2%) and curtailment (+92.9%) penalties of constant worst-case conservatism.

## Core Governance
- **Strictly Research-Only**: Zero production files modified.
- **Pre-Registration Lock**: Policy designed and locked using only pre-2024 development data (2020–2022).
- **2024 Evaluation**: 2024 operational fixture is held out strictly for post-registration replay.

## Comparison Arms
1. **Arm A — Point Control**: Candidate F point forecast baseline.
2. **Arm B — Static $q_{10}$**: Conservative $q_{10\text{,cal}}$ physical lower bound from L2-EXP-07.
3. **Arm C — Adaptive Risk**: Pre-registered adaptive risk-budget policy ($\lambda_t$).
4. **Arm D — Perfect Foresight**: Realized actual solar diagnostic benchmark.

## Key Files
- [`PRE_REGISTERED_POLICY.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/experiments/L2_EXP_08_ADAPTIVE_RISK_BUDGET/PRE_REGISTERED_POLICY.md): Detailed mathematical derivation and proofs.
- [`pre_registered_policy.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/experiments/L2_EXP_08_ADAPTIVE_RISK_BUDGET/pre_registered_policy.json): Machine-readable parameter configuration and hash lock.
- [`run_l2_exp_08_adaptive_risk_budget.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/experiments/L2_EXP_08_ADAPTIVE_RISK_BUDGET/run_l2_exp_08_adaptive_risk_budget.py): Execution runner script.
