# POLARIS Stage 8.1 Causal Rolling-Forecast Reproduction Audit Report

> [!CAUTION]
> **FINAL REPLAY AUDIT CLASSIFICATION:** **`C = CAUSAL_REPLAY_NOT_REPRODUCIBLE_FROM_FROZEN_ARTIFACTS`**  
> **CANDIDATE A AUTHORIZATION:** **`NOT_GRANTED`**  
> **EMS EXPERIMENT STATUS:** **`BLOCKED / NOT EXECUTED`**  

---

## 1. Governance & Objective Verification

This read-only scientific audit evaluated whether the frozen Stage 8.1 solar forecasting champion can be causally replayed at arbitrary hourly MPC decision origins ($t_k$) to generate a complete 24-hour lookahead ($t_k+1\text{h} \dots t_k+24\text{h}$) without retraining, using future information, or violating governance rules.

- **Previous EMS Experiment Status:** **`FROZEN & IMMUTABLE`** (`experiments/stage81_multi_trajectory/`)
- **EMS Trajectory Execution:** **`ZERO TRAJECTORIES EXECUTED`** (No MPC, MILP, or Simulator run)
- **Stage 8.1 Model Refitting:** **`ZERO MODEL REFITTING EXECUTED`**

---

## 2. Frozen Input Artifact Hashes

| Artifact | Path | SHA-256 |
| :--- | :--- | :--- |
| **Prediction Artifact** | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv` | 213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707 |
| **Feature Matrix** | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv` | e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541 |
| **H1.0 Fixture CSV** | `POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv` | 762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023 |
| **ODD Evaluation Code** | `stage7/stage8/stage8_1_700hpa_wind/run_official_odd_evaluation.py` | c1c99c60b43f00ce1845a68ca166783a30d2ac9dc986bc01a7947381165a3f41 |
| **Stage 8.1 Training Code** | `stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py` | 51e256a6bacc0aa8861fcdf93f889edc23591915fb68945a9e0d9facb63feb31 |

---

## 3. Findings on Model State & Replay Feasibility

### Question 1 & 2: Model Definition and Model State Location
- **Model Definition:** `sklearn.ensemble.HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)` defined in `run_official_odd_evaluation.py` (lines 217–235).
- **Fitted Model State Location:** **`NONE. NO SERIALIZED FITTED MODEL ARTIFACT EXISTS ON DISK.`**
- **Lifecycle:** The model `model_e1` was instantiated in RAM, fitted on 174 EVEN origins (`even_day[candidate_37_features].values`), evaluated on 173 ODD origins, exported to `stage8_1_official_odd_predictions.csv`, and discarded from RAM without saving a `.pkl` or `.joblib` binary.

### Question 3: Can the exact fitted model be loaded?
- **NO.** Loading a pre-fitted model binary is impossible because no model checkpoint artifact was saved (`CAUSAL_REPLAY_NOT_REPRODUCIBLE_FROM_FROZEN_ARTIFACTS`).

---

## 4. Feature Matrix & Origin Coverage Audit

### Question 4, 5, 8 & 9: Origin Spacing and Feature Availability
1. **37-Feature Architecture:**
   - Base 28: `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`.
   - Stage 6.6 (+3): `lwp_latest`, `iwp_latest`, `lwp_x_cloud`.
   - Stage 7.5 (+4): `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`.
   - Stage 8.1 (+2): `u700`, `v700`.

2. **Feature Origin Coverage Deficit:**
   - In `stage8_1_full_37_feature_matrix_2024.csv`, all 347 origins occur **STRICTLY AT 00:00:00Z (DAILY)**.
   - Upstream feature source tables (`POLARIS_v0_1_future_weather_forecasts_2024.csv`, `lwp_iwp_extracted_features.csv`, `stage8_1_extracted_features.csv`, `ensemble_predictions.csv`) contain feature inputs **ONLY FOR 00:00:00Z ORIGINS**.
   - Zero feature rows exist for non-00:00 UTC MPC origins ($t_k = 01:00, 02:00, \dots, 23:00\text{ UTC}$).

3. **Causal Horizon Block:**
   - Generating a full 24-hour lookahead at step $k \ge 1$ (e.g. $t_1 = 01:00\text{ UTC}$) requires predictions for $t_1+24\text{h} = 01:00\text{ tomorrow}$.
   - Feature inputs for target $01:00\text{ tomorrow}$ from origin $t_1 = 01:00\text{ UTC}$ **do not exist** in the frozen tables.
   - Obtaining a prediction from origin `00:00 tomorrow` at step $t_1 = 01:00	ext{ today}$ is strictly prohibited ($	ext{prediction\_origin} \le \text{current\_MPC\_time}$), as it constitutes **future-origin information leakage**.

---

## 5. Answers to Mandatory Governance Questions

| Question | Audit Answer |
| :--- | :--- |
| **1. Exact Stage 8.1 model definition?** | `HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)` in `run_official_odd_evaluation.py`. |
| **2. Exact fitted model state?** | **`NONE.`** No `.pkl` or `.joblib` saved on disk. |
| **3. Can fitted model be loaded?** | **`NO.`** Binary checkpoint is missing. |
| **4. What are the 37 features?** | 28 base + 3 satellite (LWP/IWP) + 4 terrain + 2 steering wind ($U_{700}, V_{700}$). |
| **5. Are features causal?** | Astronomical & SITES lags are causal. NWP, satellite LWP/IWP, 700hPa wind, and Stage 4 baseline exist **only for 00:00 UTC origins**. |
| **6. What does one prediction row mean?** | Predicted daytime $\text{SW\_IN}\text{ (W/m}^2\text{)}$ for target $t_k+h$ given origin $t_k$. |
| **7. Why origins 48h apart in CSV?** | Evaluated on 173 held-out ODD origins (every 48h in 2024 EVEN/ODD split). |
| **8. Can model be evaluated at arbitrary origin?** | **`NO.`** Missing input feature rows for non-00:00 UTC origins. |
| **9. Can 24h forecast be generated at every MPC origin?** | **`NO.`** Missing feature rows for steps $k=1 \dots 23$. |
| **10. Would doing so require retraining?** | **`YES.`** Building a model for arbitrary origins requires retraining (prohibited). |
| **11. Would doing so require synthetic fill / leakage?** | **`YES.`** Would require zero-padding, interpolation, or future-origin leakage (prohibited). |
| **12. Is exact causal model replay possible?** | **`NO.`** |
| **13. Final Classification?** | **`C = CAUSAL_REPLAY_NOT_REPRODUCIBLE_FROM_FROZEN_ARTIFACTS`** |
| **14. Candidate A Authorization?** | **`NOT_GRANTED`** |

---

## 6. Final Governance Status Block

```plain
FROZEN_PREVIOUS_EXPERIMENT_MODIFIED = NO
ORIGINAL_173_TRAJECTORY_RERUN = NO
NEW_173_TRAJECTORY_RUN = NO
NEW_10_TRAJECTORY_RUN = NO
TWO_TRAJECTORY_STEP_A_RUN = NO

CAUSAL_STAGE81_ROLLING_REPLAY = C
CANDIDATE_A_AUTHORIZATION = NOT_GRANTED

FITTED_MODEL_FILE_EXISTS = NO
FEATURE_MATRIX_HOURLY_ORIGINS_EXIST = NO
FUTURE_ORIGIN_LEAKAGE = NONE
SYNTHETIC_FILLING = NONE
RESERVED_EMS_EXECUTION = HELD
```
