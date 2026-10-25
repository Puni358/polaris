# POLARIS — PATH A / WIND FORECASTING TRACK
## PHASE A3 — WIND MODEL DEVELOPMENT AND TRAINING RESEARCH REPORT

**Document ID:** `POLARIS_WIND_A3_MODEL_DEVELOPMENT_AND_TRAINING`  
**Date (UTC):** 2026-09-18  
**Track:** PATH A — WIND FORECASTING TRACK  
**Phase:** PHASE A3 (Controlled Wind Model Development Execution)  
**Task Type:** Controlled Wind Forecasting Research Execution  
**Authorization Status:** Authorized Phase A3 Execution Only (ForecastBundle/EMS Integration **NOT AUTHORIZED**)  
**Execution Status:** `EXECUTION_COMPLETED`  
**Research Champion Selected:** `Autoregressive Ridge AR-X (Frozen A2 Comparator Retained)`  
**Champion Status:** `A2_RESEARCH_CHAMPION_RETAINED`  

---

> [!IMPORTANT]
> **RESEARCH EXECUTION REPORT ONLY:**  
> This artifact documents the empirical execution of the authorized Phase A3 wind-speed forecasting research protocol (`EXP-01` through `EXP-05`).  
> **ZERO DOWNSTREAM SYSTEM MODIFICATION, ZERO FORECASTBUNDLE INTEGRATION, ZERO EMS/MPC INTEGRATION, AND ZERO WIND-POWER GENERATION MAPPING HAVE BEEN EXECUTED.**

---

## 1. OBJECTIVE AND GOVERNANCE AUTHORIZATION

Phase A3 executes the pre-registered, pre-audited wind-speed forecasting research protocol authorized by:
- `POLARIS_WIND_MODEL_DEVELOPMENT_AUTHORIZATION` (A2.5 Protocol Freeze)
- `POLARIS_WIND_MODEL_DEVELOPMENT_EXECUTION_READINESS_AUDIT` (A2.6 Audit Pass)
- `POLARIS_CAND_04_RESOLUTION` (A2.7 Candidate 4 Exclusion Gate)

### Execution Directives:
1. **Global Run Ceiling:** Fixed at **16 runs maximum**. Total executed runs: **16 runs** ($3 + 1 + 4 + 4 + 4 + 0$).
2. **Authorized Experiments:** `EXP-01` (Baselines), `EXP-02` (Frozen Comparator), `EXP-03` (Direct GBDT), `EXP-04` (NWP Residual GBDT), `EXP-05` (AR-ElasticNet).
3. **Retired Experiment:** `EXP-06` / `CAND-04` was formally excluded in A2.7 due to missing local offline weights and was **NOT EXECUTED**.
4. **Pre-Registered Selection Rule:** A candidate model replaces the frozen A2 AR-X comparator if and only if held-out test MAE improves by at least $2.0\%$ ($\text{MAE} < 1.9957\,\text{m/s}$).

---

## 2. AUTHORITATIVE FROZEN TARGET DEFINITION

The prediction target evaluated in Phase A3 is strictly defined as:

$$\text{MEASURED } 10\,\text{m } \text{HOURLY WIND SPEED AT SMHI ABISKO AUT STATION } 188790 \quad (v_{\text{wind}} \text{ in } \text{m/s})$$

- **Target Variable:** `WIND_SPEED`
- **Target Units:** $\text{m/s}$
- **Reference Height:** $10.0\,\text{m}$ above ground level
- **Temporal Resolution:** 1 hour ($1\,\text{h}$)
- **Station ID:** SMHI Station `188790` (`Abisko Aut`, Lat $68.3538^\circ\text{N}$, Lon $18.8164^\circ\text{E}$, Elevation $392.2\,\text{m}$ a.s.l.)
- **Site Interpretation:** `CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA`
- **Direct Nuolja Measurement Status:** `NOT_ESTABLISHED`
- **Altitude Transfer Method:** `NOT_AUTHORIZED` ($309.8\,\text{m}$ elevation offset preserved unscaled)

> [!WARNING]
> Wind power generation forecasting ($P_{\text{wind}}$ in $\text{W}$) remains strictly OUT OF SCOPE. No turbine power curves or Watt calculations were executed.

---

## 3. DATASET PROVENANCE AND PREDICTOR INVENTORY

### Datasets Ingested:
- **Empirical Target Dataset:** [`research/wind_a2/smhi_188790_ws_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_ws_full.csv) ($8,690$ valid 1-hour ground observations in 2024, SMHI Parameter 4 `Vindhastighet`).
- **Auxiliary Direction Dataset:** [`research/wind_a2/smhi_188790_wd_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_wd_full.csv) ($8,690$ valid 1-hour records, SMHI Parameter 3 `Vindriktning`).
- **NWP Forecast Predictor Table:** [`data/POLARIS_v0_1_future_weather_forecasts_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_future_weather_forecasts_2024.csv) ($347$ daily origins, 24h horizon forecasts of `fc_wind_speed_10m`, `fc_surface_pressure`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `fc_cloud_cover`, `fc_precipitation`).
- **SITES Ground Weather Table:** [`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv) (Ground `TA`, `RH`).

### Causal Predictor Feature Matrix (25 Features):
1. Target History Lags at Origin $t_0$: $v_{t_0}, v_{t_0-1}, v_{t_0-2}, v_{t_0-3}, v_{t_0-6}, v_{t_0-12}, v_{t_0-23}$
2. 24h Rolling Target Statistics: $\bar{v}_{24\text{h}}, \sigma_{24\text{h}}, v_{\min}, v_{\max}, v_{\text{trend,6h}}$
3. Wind Direction Lags: $\sin(\theta_{t_0}), \cos(\theta_{t_0})$
4. Ground MET at $t_0$: $TA_{t_0}, RH_{t_0}$
5. NWP Forward Covariates ($h = 1 \dots 24$): `fc_ws_10m`, `fc_press`, `fc_temp`, `fc_rh`, `fc_cloud`, `fc_precip`
6. Temporal Calendar Features: `hour`, $\sin(\text{DOY}), \cos(\text{DOY})$

---

## 4. TEMPORAL TASK FORMULATION AND SPLITS

- **Forecast Horizon ($H$):** $24$ hours ($h = 1 \dots 24$)
- **Time Step ($\Delta t$):** $1$ hour
- **Historical Context ($W_{\text{hist}}$):** $24$ hours ($t_0-23 \dots t_0$)
- **Forecast Origin Spacing:** $24$ hours ($t_0 = 00:00\text{ UTC}$ daily)

### Strict Chronological Splits:
- **TRAIN Set:** Origins $0 \dots 223$ (2024-01-20 to 2024-08-31; $219$ valid origins, $5,265$ instance rows)
- **VALIDATION Set:** Origins $224 \dots 284$ (2024-09-01 to 2024-10-31; $61$ valid origins, $1,464$ instance rows)
- **HELD-OUT TEST Set:** Origins $285 \dots 346$ (2024-11-01 to 2024-12-31; $62$ valid origins, $1,488$ instance rows)

> [!CAUTION]
> **Strict Leakage Prevention:**  
> Scalers and feature transformations were fit strictly on the TRAIN set.  
> Hyperparameter selection was performed strictly on the VALIDATION set.  
> The HELD-OUT TEST set was evaluated once after freezing all model configurations.

---

## 5. EXECUTED EXPERIMENT MATRIX (16 RUNS TOTAL)

### Validation Set Hyperparameter Selection:

| Exp Track | Run ID | Configuration Details | Validation MAE ($\text{m/s}$) | Validation Status / Outcome |
| :--- | :--- | :--- | :---: | :--- |
| **EXP-01** | `EXP-01.1` | Naive Persistence ($\hat{y} = v_{t_0}$) | $2.5102$ | Benchmark reference |
| **EXP-01** | `EXP-01.2` | Diurnal Climate Persistence | $2.5084$ | Benchmark reference |
| **EXP-01** | `EXP-01.3` | Raw NWP Forecast (`fc_ws_10m`) | $15.4210$ | Benchmark reference |
| **EXP-02** | `EXP-02.1` | Frozen A2 AR-X Comparator ($\text{Ridge}, \alpha=10.0$) | $1.8612$ | **Frozen Reference Comparator** |
| **EXP-03** | `EXP-03.1` | Direct GBDT (Config 1: $\text{lr}=0.05, \text{depth}=5, \text{leaf}=15, \text{iter}=100$) | $1.9965$ | Trial run |
| **EXP-03** | `EXP-03.2` | Direct GBDT (Config 2: $\text{lr}=0.03, \text{depth}=4, \text{leaf}=20, \text{iter}=100$) | $1.9499$ | Trial run |
| **EXP-03** | `EXP-03.3` | Direct GBDT (Config 3: $\text{lr}=0.08, \text{depth}=6, \text{leaf}=10, \text{iter}=120$) | $2.0651$ | Trial run |
| **EXP-03** | `EXP-03.4` | Direct GBDT (Config 4: $\text{lr}=0.05, \text{depth}=3, \text{leaf}=25, \text{iter}=80$) | **$1.9346$** | **Selected Best Config for EXP-03** |
| **EXP-04** | `EXP-04.1` | Residual GBDT (Config 1: $\text{lr}=0.03, \text{depth}=4, \text{leaf}=20, \text{iter}=80$) | $3.0301$ | Trial run |
| **EXP-04** | `EXP-04.2` | Residual GBDT (Config 2: $\text{lr}=0.05, \text{depth}=5, \text{leaf}=15, \text{iter}=100$) | **$2.7946$** | **Selected Best Config for EXP-04** |
| **EXP-04** | `EXP-04.3` | Residual GBDT (Config 3: $\text{lr}=0.02, \text{depth}=3, \text{leaf}=25, \text{iter}=100$) | $3.2873$ | Trial run |
| **EXP-04** | `EXP-04.4` | Residual GBDT (Config 4: $\text{lr}=0.05, \text{depth}=3, \text{leaf}=30, \text{iter}=60$) | $3.4426$ | Trial run |
| **EXP-05** | `EXP-05.1` | AR-ElasticNet (Config 1: $\alpha=0.1, \text{l1\_ratio}=0.5$) | **$1.8420$** | **Selected Best Config for EXP-05** |
| **EXP-05** | `EXP-05.2` | AR-ElasticNet (Config 2: $\alpha=1.0, \text{l1\_ratio}=0.5$) | $1.9610$ | Trial run |
| **EXP-05** | `EXP-05.3` | AR-ElasticNet (Config 3: $\alpha=0.1, \text{l1\_ratio}=0.1$) | $1.8544$ | Trial run |
| **EXP-05** | `EXP-05.4` | AR-ElasticNet (Config 4: $\alpha=1.0, \text{l1\_ratio}=0.1$) | $1.8996$ | Trial run |

---

## 6. HELD-OUT TEST SET RESULTS SUMMARY

Evaluating selected best candidate configurations and baselines on the unseen held-out test split ($1,488$ horizon step instances across $62$ origins, Nov 01 to Dec 31, 2024; Mean Target = $5.3486\,\text{m/s}$):

| Experiment / Model ID | Model Family / Description | Test MAE ($\text{m/s}$) | Test RMSE ($\text{m/s}$) | Test Bias ($\text{m/s}$) | nMAE ($\%$) | nRMSE ($\%$) | MAE Imp vs Pers | MAE Imp vs NWP |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EXP-01.1** | Naive Persistence | $2.9334$ | $4.0679$ | $-0.0050$ | $54.84\%$ | $76.06\%$ | Reference | N/A |
| **EXP-01.2** | Diurnal Climate Persistence | $2.9302$ | $4.0940$ | $-2.0132$ | $54.78\%$ | $76.54\%$ | $+0.11\%$ | N/A |
| **EXP-01.3** | Raw NWP Forecast (`fc_ws_10m`) | $18.8024$ | $22.7894$ | $+18.7913$ | $351.54\%$ | $426.08\%$ | $-540.98\%$ | Reference |
| **EXP-02.1** | **Frozen A2 AR-X (Ridge $\alpha=10.0$)** | **$2.0364$** | **$2.7136$** | **$-0.2793$** | **$38.07\%$** | **$50.74\%$** | **$+30.58\%$** | **$+89.17\%$** |
| **EXP-03** | Direct Multi-Horizon GBDT | $2.2317$ | $2.9581$ | $-0.3822$ | $41.72\%$ | $55.31\%$ | $+23.92\%$ | $+88.13\%$ |
| **EXP-04** | NWP Residual Bias-Correction GBDT | $4.1413$ | $6.3436$ | $+0.6626$ | $77.43\%$ | $118.60\%$ | $-41.18\%$ | $+77.97\%$ |
| **EXP-05** | **AR-ElasticNet ($\alpha=0.1, \text{l1\_ratio}=0.5$)**| **$2.0081$** | **$2.6988$** | **$-0.3434$** | **$37.55\%$** | **$50.46\%$** | **$+31.55\%$** | **$+89.32\%$** |

---

## 7. HORIZON-WISE METRICS BREAKDOWN

Horizon-by-horizon test set performance ($\text{MAE}$ in $\text{m/s}$) for Frozen AR-X and key candidate models:

| Horizon ($h$) | Target Mean ($\text{m/s}$) | Persistence MAE ($\text{m/s}$) | Raw NWP MAE ($\text{m/s}$) | Frozen A2 AR-X MAE ($\text{m/s}$) | Direct GBDT MAE ($\text{m/s}$) | AR-ElasticNet MAE ($\text{m/s}$) | Best Horizon Model |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **H01** | $5.3435$ | $0.0000$ | $19.0935$ | $0.0379$ | $0.8840$ | $0.2213$ | Naive Persistence |
| **H02** | $5.0516$ | $1.4242$ | $19.3387$ | $1.4639$ | $1.5989$ | $1.4552$ | Naive Persistence |
| **H03** | $5.1468$ | $1.6000$ | $18.1645$ | $1.7124$ | $1.8713$ | $1.6668$ | Naive Persistence |
| **H04** | $5.0403$ | $2.1323$ | $17.9435$ | $2.2095$ | $2.2600$ | $2.1636$ | Naive Persistence |
| **H05** | $5.4339$ | $1.9613$ | $18.0565$ | $2.0669$ | $2.0924$ | $1.9396$ | AR-ElasticNet |
| **H06** | $5.0484$ | $2.2274$ | $18.1516$ | $2.2809$ | $2.3386$ | $2.1390$ | AR-ElasticNet |
| **H07** | $4.7597$ | $2.5419$ | $17.9952$ | $2.3462$ | $2.3489$ | $2.3247$ | AR-ElasticNet |
| **H08** | $4.7484$ | $2.4629$ | $18.3387$ | $1.9486$ | $2.0829$ | $1.8639$ | AR-ElasticNet |
| **H09** | $4.8000$ | $2.6306$ | $18.0371$ | $2.0654$ | $2.2533$ | $2.0068$ | AR-ElasticNet |
| **H10** | $5.0726$ | $2.7806$ | $17.7194$ | $1.8088$ | $2.1057$ | $1.8600$ | Frozen AR-X |
| **H11** | $4.8710$ | $2.7210$ | $19.4306$ | $1.9464$ | $2.0924$ | $1.8721$ | AR-ElasticNet |
| **H12** | $5.5274$ | $2.8677$ | $18.6839$ | $1.7892$ | $2.0394$ | $1.7524$ | AR-ElasticNet |
| **H18** | $5.6306$ | $3.3871$ | $20.7274$ | $1.8910$ | $2.3567$ | $1.9577$ | Frozen AR-X |
| **H24** | $5.4145$ | $4.0226$ | $18.5032$ | $2.4364$ | $2.5995$ | $2.5447$ | Frozen AR-X |

---

## 8. MODEL SELECTION DECISION

### Pre-Registered Model Selection Rule Audit:
- **Benchmark Bar:** Frozen A2 AR-X Champion Test MAE = $2.0364\,\text{m/s}$.
- **Pre-registered Threshold:** Required $2.0\%$ improvement over $2.0364\,\text{m/s} \implies \text{MAE} < 1.9957\,\text{m/s}$.
- **Top New Candidate (EXP-05 AR-ElasticNet):** Achieved $2.0081\,\text{m/s}$ test MAE ($+1.39\%$ improvement over $2.0364\,\text{m/s}$).

### Decision Rationale:
While EXP-05 (AR-ElasticNet) demonstrated promising performance ($2.0081\,\text{m/s}$ MAE), its improvement over the frozen A2 AR-X comparator ($2.0364\,\text{m/s}$) is $+1.39\%$, which is below the pre-registered mandatory $2.0\%$ improvement threshold ($1.9957\,\text{m/s}$).

Applying the pre-registered selection rule strictly without post-hoc threshold relaxation:

```
RESEARCH_CHAMPION = Autoregressive Ridge AR-X (Frozen A2 Comparator Retained)
CHAMPION_STATUS = A2_RESEARCH_CHAMPION_RETAINED
```

The **Autoregressive Ridge AR-X** model is retained as the authoritative research champion for Path A wind forecasting.

---

## 9. REPRODUCIBILITY PACKAGE

- **Execution Script:** [`research/wind_a3/run_a3_wind_speed_experiments.py`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a3/run_a3_wind_speed_experiments.py)
- **Results JSON Artifact:** [`research/wind_a3/a3_wind_research_results.json`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a3/a3_wind_research_results.json)
- **Random Seed:** `42` (Fixed across all models)
- **Python Runtime:** Python 3.12 (`.venv` environment)
- **Determinism:** 100% reproducible numerical outputs.

---

## 10. DOWNSTREAM SAFETY AND FIREWALL AUDIT

```
WIND_SPEED_PRODUCTION_INTEGRATION = NOT_AUTHORIZED
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
WIND_GENERATION_FORECASTING = NOT_AUTHORIZED
WIND_POWER_CURVE_WORK = NOT_AUTHORIZED
ALTITUDE_TRANSFER = NOT_AUTHORIZED
PRODUCTION_DEPLOYMENT = NOT_AUTHORIZED
```

- Zero conversion from wind speed ($\text{m/s}$) to electrical power ($\text{W}$).
- Zero modification of production `ForecastBundle` schemas or `ForecastEngine` interfaces.
- Zero connection to EMS / MILP optimizer or MPC controller.

---

## 11. REQUIRED MACHINE-READABLE STATE

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = A3_EXECUTION_COMPLETED
WIND_TARGET_STATUS = CONDITIONALLY_ESTABLISHED
WIND_DATA_STATUS = SUFFICIENT_FOR_NEXT_RESEARCH_PHASE
A2_TARGET_STATUS = FROZEN
A2_MODEL_STATUS = FROZEN
RESEARCH_CHAMPION = AUTOREGRESSIVE_RIDGE_ARX
CHAMPION_STATUS = A2_RESEARCH_CHAMPION_RETAINED
TOTAL_EXECUTED_RUNS = 16
GLOBAL_RUN_CEILING = 16
EXP_01_STATUS = COMPLETED_3_RUNS
EXP_02_STATUS = COMPLETED_1_RUN
EXP_03_STATUS = COMPLETED_4_RUNS
EXP_04_STATUS = COMPLETED_4_RUNS
EXP_05_STATUS = COMPLETED_4_RUNS
EXP_06_STATUS = EXCLUDED_0_RUNS
TEST_MAE_ARX_MS = 2.0364
TEST_MAE_ELASTICNET_MS = 2.0081
TEST_MAE_GBDT_MS = 2.2317
TEST_MAE_PERSISTENCE_MS = 2.9334
TEST_MAE_RAW_NWP_MS = 18.8024
WIND_MODEL_TRAINING = EXECUTED_A3_ONLY
WIND_MODEL_INFERENCE = EXECUTED_A3_ONLY
WIND_MODEL_SELECTION = COMPLETED_PREDEF_RULE_APPLIED
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
IMPLEMENTATION_STATUS = A3_RESEARCH_COMPLETED
NEXT_GOVERNED_STEP = EXTERNAL_SCIENTIFIC_REVIEW_AND_GOVERNANCE_CLOSEOUT
```

---

## 12. FILE MODIFICATION FIREWALL

```
SOURCE_CODE_MODIFIED: NO
SCHEMA_MODIFIED: NO
STAGE8_1_MODIFIED: NO
D1_D7_MODIFIED: NO
A1_MODIFIED: NO
A2_MODIFIED: NO
A2_5_MODIFIED: NO
A2_6_MODIFIED: NO
A2_7_MODIFIED: NO
OPTION_B_MODIFIED: NO
FORECASTBUNDLE_MODIFIED: NO
FORECASTENGINE_MODIFIED: NO
STATIONSTATE_MODIFIED: NO
EMS_MODIFIED: NO
MPC_MODIFIED: NO
DIGITAL_TWIN_MODIFIED: NO
D5_MODIFIED: NO
EXTERNAL_DATA_ACQUIRED: NO
EXTERNAL_PACKAGES_INSTALLED: NO
WEIGHTS_DOWNLOADED: NO
WIND_GENERATION_MAPPING_EXECUTED: NO
IMPLEMENTATION_STATUS: A3_RESEARCH_COMPLETED
```

**PHASE A3 WIND MODEL DEVELOPMENT EXECUTION IS COMPLETE.**
