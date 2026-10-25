# POLARIS — PATH A / WIND FORECASTING TRACK
## PHASE A2.5 — WIND MODEL DEVELOPMENT PROTOCOL FREEZE GATE

**Document ID:** `POLARIS_WIND_MODEL_DEVELOPMENT_AUTHORIZATION`  
**Date (UTC):** 2026-09-18  
**Track:** PATH A — WIND FORECASTING TRACK  
**Phase:** PHASE A2.5 (Wind Model Development Protocol Freeze Gate)  
**Task Type:** Pre-Execution Research Governance / Experiment Design Freeze  
**Authorization Status:** Authorized Phase A2.5 Protocol Freeze Only (Model Execution / Training / Inference **NOT AUTHORIZED**)  
**Research Protocol Status:** `COMPLETE_AND_READY_FOR_EXECUTION_AUTHORIZATION`  
**Next Governed Step:** `WIND_MODEL_DEVELOPMENT_EXECUTION_AUTHORIZATION`  

---

> [!IMPORTANT]
> **PROTOCOL FREEZE EXERCISE ONLY:**  
> This artifact defines and freezes the pre-execution experiment design, data specifications, temporal splits, causal boundaries, candidate model space, and evaluation protocols for a FUTURE separately authorized wind forecasting execution phase.  
> **ZERO MODEL TRAINING, ZERO INFERENCE, ZERO BENCHMARKING, ZERO CODE MODIFICATION, AND ZERO DATA ACQUISITION HAVE BEEN EXECUTED.**

---

## 1. AUTHORITATIVE FROZEN FOUNDATION

This protocol freeze builds strictly upon the verified results of prior governance phases:

### A1 Target & Data Qualification Foundation:
- **A1 Qualification Record:** [`POLARIS_WIND_FORECASTING_A1_TARGET_AND_DATA_QUALIFICATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_WIND_FORECASTING_A1_TARGET_AND_DATA_QUALIFICATION.md) / `.json`
- **A1 Target Status:** `WIND_TARGET_STATUS = CONDITIONALLY_ESTABLISHED`
- **A1 Data Status:** `WIND_DATA_STATUS = SUFFICIENT_FOR_NEXT_RESEARCH_PHASE`

### A2 Research & Evidence Audit Foundation:
- **A2 Target Governance Decision:** [`POLARIS_WIND_A2_TARGET_DEFINITION_GOVERNANCE_DECISION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_WIND_A2_TARGET_DEFINITION_GOVERNANCE_DECISION.md) / `.json`
- **A2 Model Development & Training:** [`POLARIS_WIND_A2_MODEL_DEVELOPMENT_AND_TRAINING.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_WIND_A2_MODEL_DEVELOPMENT_AND_TRAINING.md) / `.json`
- **A2 Evidence Audit Record:** [`POLARIS_WIND_A2_EVIDENCE_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_WIND_A2_EVIDENCE_AUDIT.md) / `.json`
- **A2 Research Results Artifact:** [`research/wind_a2/a2_wind_research_results.json`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/a2_wind_research_results.json)

### Core Frozen Parameters:
- **Target Station:** SMHI Station `188790` (`Abisko Aut`, Lat $68.3538^\circ\text{N}$, Lon $18.8164^\circ\text{E}$, Elev $392.2\,\text{m}$ a.s.l.)
- **Target Variable:** Measured $10\,\text{m}$ hourly wind speed ($v_{\text{wind}}$ in $\text{m/s}$)
- **Site Interpretation:** `CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA`
- **Direct Nuolja Wind Measurement Status:** `NOT_ESTABLISHED`
- **Altitude Transfer Method:** `NOT_ESTABLISHED` ($309.8\,\text{m}$ elevation offset preserved unscaled)
- **A2 Research Champion:** `AUTOREGRESSIVE_RIDGE_ARX` (Candidate 3, $2.0364\,\text{m/s}$ test MAE)
- **A2 Champion Status:** `VERIFIED`
- **A2 Audit Status:** `VERIFIED_WITH_LIMITATIONS`
- **Forecast Horizon ($H$):** $24$ hours ($h = 1 \dots 24$)
- **Sampling Step ($\Delta t$):** $1$ hour
- **Historical Lookback ($W_{\text{hist}}$):** $24$ hours ($t_0-23 \dots t_0$)

---

## 2. PRIMARY OBJECTIVE & SCOPE

The objective of Phase A2.5 is to specify a fully reproducible, pre-registered research protocol for a future wind model development phase BEFORE any code execution begins.

This document establishes pre-registered specifications for:
1. Data source and provenance boundaries.
2. Target definition and forecast origin conventions.
3. Causal inputs and leakage prevention rules.
4. Default chronological train/validation/test splits.
5. Reference baselines and the frozen A2 AR-X comparator.
6. Mechanistically justified candidate model families (max 4 new families).
7. Bounded experiment matrix and hyperparameter search budget.
8. Primary and secondary evaluation metrics.
9. Comparative and statistical decision rules.
10. Minimum reproducibility requirements.
11. Hard stopping rules and safety firewalls.

---

## 3. DATASET AND PROVENANCE FREEZE

### Target Dataset Specification:
- **Exact File Path:** [`research/wind_a2/smhi_188790_ws_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_ws_full.csv)
- **Target Column:** `Vindhastighet` (SMHI Parameter 4, 10m wind speed in $\text{m/s}$)
- **Auxiliary Target Column:** `Vindriktning` ([`research/wind_a2/smhi_188790_wd_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_wd_full.csv), SMHI Parameter 3, degrees)
- **Custodian / Source:** Swedish Meteorological and Hydrological Institute (SMHI) / Polarforskningssekretariatet
- **Timestamp Semantics:** ISO-8601 UTC
- **Temporal Frequency:** Monotonic $1$-hour step
- **Dataset Coverage:** Full 2024 calendar year ($8,690$ valid hourly records)
- **Missingness:** $0$ missing target observations
- **Quality Control:** $100\%$ SMHI quality-controlled archive (Codes `G` / `Y`)

### Predictor Dataset Specifications:
- **NWP Forecast Table:** [`data/POLARIS_v0_1_future_weather_forecasts_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_future_weather_forecasts_2024.csv) ($347$ daily origins, 24h horizon forecasts of `fc_wind_speed_10m`, `fc_surface_pressure`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `fc_cloud_cover`, `fc_precipitation`).
- **SITES Ground Meteorology Table:** [`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv) (Ground `TA`, `RH`, `SW_IN`, `TS`).

> [!NOTE]
> No data resampling, value filling, interpolation, target reconstruction, or external data acquisition is permitted.

---

## 4. TARGET AND FORECAST TASK FREEZE

- **Forecast Horizon:** $H = 24$ hours ($h = 1, 2, \dots, 24$)
- **Time Step:** $\Delta t = 1$ hour
- **Historical Lookback:** $W_{\text{hist}} = 24$ hours ($t_0-23 \dots t_0$)
- **Forecast Origin ($t_0$):** Daily $00:00\text{ UTC}$
- **Target Alignment:** For origin $t_0$, step $h$ predicts measured wind speed at timestamp $t_0 + h\text{h}$.
- **Valid Origin Rule:** An origin $t_0$ is valid if and only if:
  1. Target values exist for all $24$ historical lookback hours $[t_0-23, t_0]$.
  2. Target values exist for all $24$ future horizon hours $[t_0+1, t_0+24]$.
  3. NWP forecast covariates published at or before $t_0$ exist for all $24$ horizon steps.

> [!WARNING]
> Wind power generation forecasting ($P_{\text{wind}}$ in $\text{W}$) remains strictly OUT OF SCOPE.

---

## 5. CAUSAL / LEAKAGE GOVERNANCE

### Strict Causal Rule:
$$\text{NO INFORMATION AVAILABLE AFTER } t_0 \text{ MAY ENTER A FORECAST FOR ORIGIN } t_0.$$

### Causal Predictor Inventory at Origin $t_0$:
1. **Target History Lags (Observed):** $v_{t_0}, v_{t_0-1}, v_{t_0-2}, v_{t_0-3}, v_{t_0-6}, v_{t_0-12}, v_{t_0-23}$
2. **Rolling Target Statistics (Observed over $[t_0-23, t_0]$):** Mean ($\bar{v}_{24\text{h}}$), Std ($\sigma_{24\text{h}}$), Min ($v_{\min}$), Max ($v_{\max}$), 6h Trend ($v_{t_0} - v_{t_0-6}$)
3. **Wind Direction Lags (Observed):** $\sin(\theta_{t_0}), \cos(\theta_{t_0})$
4. **Ground MET (Observed at $t_0$):** Air Temp ($TA_{t_0}$), Relative Humidity ($RH_{t_0}$)
5. **NWP Forward Covariates (Published $\le t_0$):** `fc_wind_speed_10m`, `fc_surface_pressure`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `fc_cloud_cover`, `fc_precipitation`

### Leakage Containment Directives:
- Feature scaling, mean/std normalization, PCA, and model parameter fitting MUST be fit on the **TRAIN split only**.
- Target actuals at $t_0+h$ ($h \ge 1$) are strictly forbidden from appearing in feature matrices, rolling statistics, or preprocessing transformations.
- Validation and test split targets are strictly held out from model fitting.

---

## 6. TEMPORAL SPLIT FREEZE

The protocol freezes the exact chronological split established during A2 across the 2024 benchmark period:

| Split Name | Date Range (UTC) | Valid Origins Count | Horizon Step Instances | Role in Research |
| :--- | :--- | :---: | :---: | :--- |
| **TRAIN** | 2024-01-20 to 2024-08-31 | 219 origins | 5,265 rows | Feature fitting, scaler fitting, model coefficient training |
| **VALIDATION** | 2024-09-01 to 2024-10-31 | 61 origins | 1,464 rows | Hyperparameter tuning, model iteration, early stopping |
| **TEST** | 2024-11-01 to 2024-12-31 | 62 origins | 1,488 rows | **Strictly held-out final evaluation & comparison** |

> [!CAUTION]
> **Held-Out Test Set Boundary:**  
> The TEST split MUST remain strictly un-peeked during research development.  
> Zero test-based hyperparameter tuning, feature selection, model selection, or stopping rules are permitted.

---

## 7. REFERENCE BASELINES & FROZEN COMPARATOR

Every future candidate evaluation must be benchmarked against four reference models:

1. **Baseline 1: Naive Persistence:**
   $$\hat{y}_{t_0+h} = v_{t_0} \quad \forall h \in \{1 \dots 24\}$$
2. **Baseline 2: Diurnal Climate Persistence:**
   $$\hat{y}_{t_0+h} = \bar{v}_{\text{train}}(h \pmod{24})$$
   (Hourly target mean computed strictly on the TRAIN split).
3. **Baseline 3: Raw NWP Forecast:**
   Direct uncorrected `fc_wind_speed_10m` forecast values.
4. **Baseline 4: Frozen A2 AR-X Champion (FROZEN COMPARATOR):**
   - **Model Class:** Autoregressive Ridge Regression ($\text{Ridge}(\alpha=10.0)$)
   - **Historical Performance:** Test MAE = $2.0364\,\text{m/s}$, RMSE = $2.7136\,\text{m/s}$, Bias = $-0.2793\,\text{m/s}$
   - **Governance Directive:** The A2 AR-X champion is a FROZEN REFERENCE COMPARATOR. It SHALL NOT be retrained, retuned, or modified. Its verified test metric ($2.0364\,\text{m/s}$ MAE) serves as the benchmark bar for future candidate models.

---

## 8. CANDIDATE MODEL RESEARCH SCOPE

To prevent unconstrained architecture search, the future research scope is strictly limited to **FOUR (4)** mechanistically justified new candidate model families:

### Candidate Family 1: Direct Multi-Horizon Gradient Boosted Decision Trees (GBDT-Direct)
- **Mechanism Tested:** Non-linear feature interaction and threshold-based regime splitting per horizon step.
- **Model Class:** `sklearn.ensemble.HistGradientBoostingRegressor`
- **Inputs:** Target lags, 24h rolling statistics, direction vectors, SITES MET, NWP covariates.
- **Search Budget:** Max 4 hyperparameter configurations (tuned on VALIDATION).

### Candidate Family 2: NWP Residual Bias-Correction GBDT (GBDT-Residual)
- **Mechanism Tested:** Explicit error residual modeling ($\delta_h = v_{\text{obs}} - v_{\text{nwp}}$) to correct systematic high-altitude NWP grid bias.
- **Model Class:** `HistGradientBoostingRegressor` predicting NWP error residuals.
- **Inputs:** Causal target lags, NWP forecast delta, surface pressure, temperature.
- **Search Budget:** Max 4 hyperparameter configurations.

### Candidate Family 3: ElasticNet Regularized Autoregressive Model (AR-ElasticNet)
- **Mechanism Tested:** Joint L1/L2 regularization for linear feature selection and sparsity control across high-dimensional NWP inputs.
- **Model Class:** `sklearn.linear_model.ElasticNet`
- **Inputs:** Full causal lag and NWP feature matrix.
- **Search Budget:** Max 4 hyperparameter configurations ($\alpha \in [0.1, 1.0, 10.0]$, $\text{l1\_ratio} \in [0.1, 0.5]$).

### Candidate Family 4: Pre-Trained Time-Series Foundation Model Zero-Shot (Foundation-ZeroShot)
- **Mechanism Tested:** Zero-shot generalization of large pre-trained foundation models (e.g. TimesFM 1.0 / Chronos) on pure historical target lags.
- **Model Class:** Zero-shot foundation model inference (NO fine-tuning, NO weight updates).
- **Inputs:** Target historical lag sequence ($W_{\text{hist}} = 24\text{h}$ or $48\text{h}$).
- **Search Budget:** Max 2 zero-shot context length configurations ($24\text{h}, 48\text{h}$).

---

## 9. BOUNDED EXPERIMENT MATRIX

The future research phase is restricted to the following bounded experiment matrix (Total Budget: Max 14 experiment runs):

| Exp ID | Candidate Family | Hypothesis / Mechanism | Input Set | Target | Tuning Set | Max Runs | Primary Metric | Baseline Comparator |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **EXP-01** | Reference Baselines | Benchmark reference baselines | Target / NWP | $v_{\text{wind}}$ | None | 3 | MAE ($\text{m/s}$) | Persistence / Raw NWP |
| **EXP-02** | Frozen A2 AR-X | Verify frozen reference comparator | Causal Matrix | $v_{\text{wind}}$ | None | 1 | MAE = $2.0364$ | Historical A2 Result |
| **EXP-03** | GBDT-Direct | Test non-linear multi-horizon GBDT | Full Causal | $v_{\text{wind}}$ | Validation | 4 | MAE ($\text{m/s}$) | Frozen A2 AR-X |
| **EXP-04** | GBDT-Residual | Test explicit NWP residual correction | NWP + Lags | $\delta_{\text{nwp}}$ | Validation | 4 | MAE ($\text{m/s}$) | Raw NWP / A2 AR-X |
| **EXP-05** | AR-ElasticNet | Test L1/L2 feature selection linear model | Full Causal | $v_{\text{wind}}$ | Validation | 4 | MAE ($\text{m/s}$) | Frozen A2 AR-X |
| **EXP-06** | Foundation-ZeroShot| Test zero-shot foundation model skill | Target Lags | $v_{\text{wind}}$ | None | 2 | MAE ($\text{m/s}$) | Persistence / A2 AR-X |

> [!IMPORTANT]
> **Bounded Execution Budget:**  
> The total number of model fits across all candidate families SHALL NOT exceed **18 total runs**.  
> No additional experiments may be added without a formal governance protocol revision.

---

## 10. HYPERPARAMETER GOVERNANCE

- **Tuning Set:** Hyperparameters MUST be selected using the TRAIN and VALIDATION splits only.
- **Search Strategy:** Bounded grid search over pre-registered parameter ranges.
- **Forbidden Practices:** No adaptive expansion of search grids after inspecting validation errors; no repeated testing or peeking at the TEST split.

---

## 11. PRIMARY AND SECONDARY METRICS

### Primary Metric:
$$\text{Mean Absolute Error (MAE)} = \frac{1}{N \cdot H} \sum_{i=1}^N \sum_{h=1}^{24} |y_{i,h} - \hat{y}_{i,h}| \quad (\text{in } \text{m/s})$$

### Secondary Metrics:
- **Root Mean Squared Error (RMSE):** $\sqrt{\frac{1}{N \cdot H} \sum (y_{i,h} - \hat{y}_{i,h})^2}$ ($\text{m/s}$)
- **Mean Bias Error (Bias):** $\frac{1}{N \cdot H} \sum (\hat{y}_{i,h} - y_{i,h})$ ($\text{m/s}$)
- **Normalized MAE (nMAE):** $\text{MAE} / \bar{y}_{\text{test}} \times 100\%$ ($\%$)
- **Normalized RMSE (nRMSE):** $\text{RMSE} / \bar{y}_{\text{test}} \times 100\%$ ($\%$)

### Horizon-wise Metrics:
Individual metric reporting for steps $h = 1, 2, 3, 4, 5, 6, 12, 18, 24$.

---

## 12. STATISTICAL & COMPARATIVE GOVERNANCE

1. **Identical Test Population:** All models must be evaluated on the exact same $62$ held-out test origins ($1,488$ horizon step instances).
2. **Paired Error Comparison:** Candidate superiority requires paired sample error differences ($\Delta \text{MAE} = \text{MAE}_{\text{candidate}} - \text{MAE}_{\text{AR-X}}$).
3. **Champion Selection Rule:** A candidate model may replace the frozen A2 AR-X champion if and only if:
   - Held-out test MAE is lower than $2.0364\,\text{m/s}$ by at least $2.0\%$ ($\text{MAE} < 1.9957\,\text{m/s}$).
   - Zero future leakage is verified.
   - Non-negativity clipping ($\hat{y} \ge 0.0\,\text{m/s}$) and 24h horizon completeness are satisfied.

---

## 13. REPRODUCIBILITY REQUIREMENTS

The future execution phase must produce a complete reproducibility package containing:
- Source file paths and SHA-256 checksums.
- Environment manifest (`requirements.txt`, Python version).
- Fixed random seeds (`random_state = 42`).
- Complete origin list and train/validation/test index assignments.
- Saved candidate model weights/artifacts in `research/wind_a3/`.
- JSON execution summary with per-origin and per-horizon errors.

---

## 14. HARD STOPPING RULES

The future execution phase MUST STOP IMMEDIATELY if:
1. Future target leakage is detected in any feature matrix.
2. Target alignment or timestamp mismatch is identified.
3. Test split data enters model training or hyperparameter selection.
4. Experiment count exceeds the bounded matrix budget ($18$ runs).
5. Source datasets or frozen A2 artifacts are modified.
6. External data is acquired or downloaded.
7. Wind speed to power conversion or turbine curve modeling is attempted.
8. POLARIS production code (`ForecastBundle`, `ForecastEngine`, `EMS`, `MPC`) is modified.

---

## 15. RESEARCH FIREWALL

The following activities remain strictly **NOT AUTHORIZED**:

```
WIND_MODEL_TRAINING = NOT_YET_AUTHORIZED
WIND_MODEL_INFERENCE = NOT_YET_AUTHORIZED
WIND_MODEL_SELECTION = NOT_YET_AUTHORIZED
WIND_FORECAST_EXPERIMENT = NOT_YET_AUTHORIZED
WINDSPEED_PRODUCTION_INTEGRATION = NOT_AUTHORIZED
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
WIND_GENERATION_MAPPING = NOT_AUTHORIZED
WIND_POWER_CURVE_WORK = NOT_AUTHORIZED
ALTITUDE_TRANSFER = NOT_AUTHORIZED
EXTERNAL_DATA_ACQUISITION = NOT_AUTHORIZED
```

---

## 16. PROTOCOL STATUS DECISION

Project governance hereby classifies the pre-execution research protocol:

```
RESEARCH_PROTOCOL_STATUS = COMPLETE_AND_READY_FOR_EXECUTION_AUTHORIZATION
NEXT_GOVERNED_STEP = WIND_MODEL_DEVELOPMENT_EXECUTION_AUTHORIZATION
```

> [!NOTE]
> `COMPLETE_AND_READY_FOR_EXECUTION_AUTHORIZATION` indicates that the research protocol is fully specified, causally sound, and evidence-backed. It DOES NOT authorize model training or execution. A separate explicit execution authorization gate is required.

---

## 17. REQUIRED MACHINE-READABLE STATE

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = A2_5_PROTOCOL_FROZEN
WIND_TARGET_STATUS = CONDITIONALLY_ESTABLISHED
WIND_DATA_STATUS = SUFFICIENT_FOR_NEXT_RESEARCH_PHASE
A2_TARGET_STATUS = FROZEN
A2_MODEL_STATUS = FROZEN
A2_RESEARCH_CHAMPION = AUTOREGRESSIVE_RIDGE_ARX
A2_CHAMPION_STATUS = VERIFIED
RESEARCH_PROTOCOL_STATUS = COMPLETE_AND_READY_FOR_EXECUTION_AUTHORIZATION
WIND_MODEL_TRAINING = NOT_YET_AUTHORIZED
WIND_MODEL_INFERENCE = NOT_YET_AUTHORIZED
WIND_MODEL_SELECTION = NOT_YET_AUTHORIZED
WIND_FORECAST_EXPERIMENT = NOT_YET_AUTHORIZED
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
WIND_GENERATION_MAPPING = NOT_AUTHORIZED
IMPLEMENTATION_STATUS = PROTOCOL_FREEZE_ONLY
NEXT_GOVERNED_STEP = WIND_MODEL_DEVELOPMENT_EXECUTION_AUTHORIZATION
```

---

## 18. FILE MODIFICATION FIREWALL

```
SOURCE_CODE_MODIFIED: NO
SCHEMA_MODIFIED: NO
STAGE8_1_MODIFIED: NO
D1_D7_MODIFIED: NO
A1_MODIFIED: NO
A2_MODIFIED: NO
A2_MODEL_ARTIFACT_MODIFIED: NO
OPTION_B_MODIFIED: NO
FORECASTBUNDLE_MODIFIED: NO
FORECASTENGINE_MODIFIED: NO
STATIONSTATE_MODIFIED: NO
EMS_MODIFIED: NO
MPC_MODIFIED: NO
DIGITAL_TWIN_MODIFIED: NO
D5_MODIFIED: NO
EXPERIMENT_EXECUTED: NO
MODEL_TRAINING_EXECUTED: NO
MODEL_INFERENCE_EXECUTED: NO
MODEL_SELECTION_EXECUTED: NO
EXTERNAL_DATA_ACQUIRED: NO
WIND_GENERATION_MAPPING_EXECUTED: NO
IMPLEMENTATION_STATUS: PROTOCOL_FREEZE_ONLY
```

**PHASE A2.5 WIND MODEL DEVELOPMENT PROTOCOL FREEZE IS COMPLETE.**
