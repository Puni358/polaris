# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING SPECIFICATION

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `TRAINING SPECIFICATION + AUTHORIZATION GATE`  
**Current Authorization:** `READ-ONLY SPECIFICATION ONLY (NO TRAINING AUTHORIZED)`  
**Training Authorization State:** **`MODEL_TRAINING_AUTHORIZATION = NOT_GRANTED`**  

---

## 0. Training Authorization Firewall

> [!IMPORTANT]
> **READ-ONLY SPECIFICATION BOUNDARY**:
> This document specifies the exact requirements, data contracts, feature definitions, model architecture, hyperparameters, preflight checklist, and reproducibility package for the FIRST AUTHORIZED model-training run of Branch 01.
> 
> **THIS SPECIFICATION DOES NOT GRANT TRAINING AUTHORIZATION.**
> - `NEW_MODEL_TRAINED = NO`
> - `NEW_MODEL_INFERRED = NO`
> - `MODEL_TRAINING_AUTHORIZATION = NOT_GRANTED`
> - Zero model fitting, training, inference, benchmarking, or EMS execution will occur.

---

## 1. Training Objective & Target Semantics

The model is designed to learn station-measured Surface Downwelling Shortwave Radiation ($SW\_IN$) at the Nuolja station ($68.3582^\circ\text{ N}, 18.7842^\circ\text{ E}$).

- **Frequency**: Hourly UTC (`YYYY-MM-DDTHH:MM:SSZ`).
- **Target Vector $Y(t)$**: Multi-output 24-step direct forecast vector:
  \[Y(t) = [SW\_IN(t+1), SW\_IN(t+2), \dots, SW\_IN(t+24)]\]
- **Exclusion Rule**: $t+0$ is strictly excluded from target outputs.
- **Target Units**: $\text{W/m}^2$.
- **Formulation**: Multi-output direct regression architecture (e.g. Multi-Output HistGradientBoostingRegressor / Ridge Regressor).

---

## 2. Dataset Identity & Pre-Training Preflight

- **Source Dataset**: `(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv`
- **File Size**: 261,094 bytes
- **Raw Observations ($N_{\text{OBSERVATIONS}}$)**: `8,832` raw hourly observations in 2024
- **Supported MPC Origins ($N_{\text{SUPPORTED\_ORIGINS}}$)**: `8,784` valid hourly forecast origins ($8,832 - 48$)
- **Time Window**: `2024-01-01T00:00:00Z` to `2024-12-31T23:00:00Z`
- **Missing Value Policy**: Fail closed on missing/NaN values in target or historical lookbacks.
- **Pre-Training Preflight Gate**: Must verify SHA-256 hash, column schema, raw observation count ($8,832$), timestamp monotonicity, and zero duplicate timestamps before training.

---

## 3. Contract-Derived Forecast Origins

- **Supported Origin Formula**: Origins $t$ are derived from data contracts requiring a 24h historical lookback window ($t-23..t$) and a 24h ground-truth target window ($t+1..t+24$).
- **Governed Reference**: $N_{\text{SUPPORTED\_ORIGINS}} = 8,784$ hourly MPC origins in 2024.
- **Dynamic Derivation**: Derived programmatically via `OriginGenerator` ($N_{\text{OBSERVATIONS}} - 48 = 8,832 - 48 = 8,784$).

---

## 4. Feature Contract (18 Reconciled Authorized Features)

All features must satisfy $\text{information\_available\_time} \le t$:

1. **Historical SW_IN Lookbacks (11 features)**:
   - 7 Sampled Lags: `sw_in_lag_0h` ($t$), `sw_in_lag_1h` ($t-1$), `sw_in_lag_2h` ($t-2$), `sw_in_lag_3h` ($t-3$), `sw_in_lag_6h` ($t-6$), `sw_in_lag_12h` ($t-12$), `sw_in_lag_23h` ($t-23$)
   - 4 Summary Statistics: `sw_in_mean_24h` (mean over $t-23..t$), `sw_in_std_24h` (std over $t-23..t$), `sw_in_max_24h` (max over $t-23..t$), `sw_in_min_24h` (min over $t-23..t$)

2. **Astronomical Position & Cyclics (6 features)**:
   - `solar_elevation` (degrees), `solar_zenith` (degrees)
   - `sin_hour`, `cos_hour` (hourly cyclic encoding)
   - `sin_doy`, `cos_doy` (day-of-year cyclic encoding)

3. **Physical Clear-Sky Reference (1 feature)**:
   - `clearsky_sw_in_origin` (clear-sky $SW\_IN$ at origin $t$)

*Prohibitions*: No centered future windows, no target leakage, no Candidate A features, no Stage 8.1 feature reuse.

---

## 5. NWP Causal Selector & Lead Mapping Rules

- **Causal Rule**: $t_{\text{issue}} \le t_{\text{origin}}$. Select latest AROME issue run at or before origin $t$.
- **Effective Lead Mapping**: $H_{\text{effective}} = h + (t_{\text{origin}} - t_{\text{issue}})$.
- **Lead Bounds**: Effective leads span $1\text{h}$ to $42\text{h}$ across daily 00:00 UTC base issue runs.
- **Coverage**: 100.0% coverage verified; zero future issue leakage or terminal padding.

---

## 6. Chronological Split & Embargo Contract

- **Train Split**: `2024-01-01T00:00:00Z` to `2024-08-31T23:00:00Z` (5,832 candidate origins minus 24h embargo).
- **Validation Split**: `2024-09-01T00:00:00Z` to `2024-10-31T23:00:00Z` (1,464 candidate origins minus 24h embargo).
- **Test Split**: `2024-11-01T00:00:00Z` to `2024-12-31T23:00:00Z` (1,464 candidate origins; held back untouched until governed evaluation).
- **24-Hour Boundary Embargo**: Origins $t$ whose target window $t+1..t+24$ crosses into the next split boundary ($t \in [\text{split\_end} - 24h, \text{split\_end}]$) are excluded from the split set to prevent target leakage.

---

## 7. Preprocessing & Feature Scaling Contract

- **Scaler**: `StandardScaler` (Z-score normalization).
- **Isolation Rule**: Scaler parameters ($\mu, \sigma$) MUST be fitted **STRICTLY ON THE TRAINING SPLIT**.
- **Test/Val Protection**: Validation and Test feature matrices are transformed using the pre-fitted training scaler. Zero test set leakage allowed.

---

## 8. Authorized Candidate Model Architectures

- **Architecture Status**: `AUTHORIZED_MULTIPLE_CANDIDATES`
- **Architecture Selection**: `REQUIRES_GOVERNANCE_DECISION`
- **Authorized Candidate Models**:
  1. `MultiOutputRegressor(HistGradientBoostingRegressor)`
  2. `MultiOutputRegressor(Ridge)`
- **Common Candidate Hyperparameters**:
  - `random_state`: `42`
  - `loss`: MSE / L2 Loss
- **Output Dimension**: 24 continuous target values ($SW\_IN(t+1)...SW\_IN(t+24)$).

---

## 9. Baseline Benchmarks & Evaluation Metrics

- **Approved Baselines**:
  1. 24h Persistence Baseline ($SW\_IN(t+h) = SW\_IN(t)$)
  2. Clear-Sky Ratio Baseline ($SW\_IN(t+h) = k_t(t) \cdot CS(t+h)$)
- **Authorized Metrics**:
  - `MAE`: Mean Absolute Error ($\text{W/m}^2$)
  - `RMSE`: Root Mean Squared Error ($\text{W/m}^2$)
  - Reported overall and horizon-wise ($H1..H24$).
- **Prohibited Metrics**: `WAPE` and `Kt-RMSE` are NOT included.

---

## 10. MODEL_RUN_MANIFEST_SCHEMA & 34-Item Reproducibility Package

Future authorized training runs MUST create an immutable run directory:
`artifacts/model_runs/RUN_<unique_id>/`

Requirements:
- `MODEL_RUN_MANIFEST.json` conforming to `MODEL_RUN_MANIFEST_SCHEMA.json`.
- 34-item `TRAINING_REPRODUCIBILITY_CHECKLIST.md`.
- Serialized model binary (`model.joblib`) + byte-level SHA-256 hash.
- Serialized scaler binary (`scaler.joblib`) + SHA-256 hash.
- Full Git commit, branch, clean/dirty state, and diff SHA-256.
- Training logs, execution environment, Python version, dependency versions.
- Process-isolated replay verification report (`REPLAY_REPORT.json`, $\text{atol}=1e-5$, $\text{rtol}=1e-5$).

---

## 11. Governed State Machine

Required transition sequence for future training runs:
`IN_PROGRESS` $\rightarrow$ `TRAINING_COMPLETE` $\rightarrow$ `SERIALIZATION_VERIFIED` $\rightarrow$ `REPLAY_VERIFIED` $\rightarrow$ `REPRODUCIBLE`

Failure at any gate transitions to `NOT_REPRODUCIBLE` and blocks EMS promotion.

---

## 12. Execution & Resource Governance

- **Worker Count**: 8 workers default where technically appropriate.
- **Monitoring**: Live logging of CPU, RAM, GPU (if applicable), thermal state, and disk space.
- **Checkpointing**: Checkpoints saved at fixed epoch/iter intervals without overwriting.
- **Signals**: Graceful handling of SIGINT/SIGTERM.

---

## 13. Promotion Firewall

- `TRAINING_COMPLETE` does NOT grant `REPRODUCIBLE`.
- `REPRODUCIBLE` does NOT grant `EMS_APPROVED`.
- Stage 8.1 remains frozen and active until a separate formal EMS promotion gate review is authorized.

---

## 14. Required Final Status Block

```
BRANCH_ID =
POLARIS_SOLAR_FORECAST_BRANCH_01

PHASE3_IMPLEMENTATION =
PASS

PHASE3_GOVERNANCE_REVIEW =
PASS

TRAINING_SPECIFICATION =
PASS

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

REAL_BRANCH01_MODEL_LOADED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

STAGE8_1_MODIFIED =
NO

CANDIDATE_A_IMPLEMENTED =
NO

CANDIDATE_A_EXECUTED =
NO

MODEL_TRAINING_AUTHORIZATION =
NOT_GRANTED

NEXT_GOVERNED_STEP =
TRAINING_SPECIFICATION_GOVERNANCE_REVIEW
```
