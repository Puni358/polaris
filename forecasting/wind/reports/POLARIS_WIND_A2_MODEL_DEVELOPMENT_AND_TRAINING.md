# POLARIS — PATH A / WIND FORECASTING TRACK
## PHASE A2 — WIND MODEL DEVELOPMENT AND TRAINING RESEARCH REPORT

**Document ID:** `POLARIS_WIND_A2_MODEL_DEVELOPMENT_AND_TRAINING`  
**Date (UTC):** 2026-09-18  
**Track:** PATH A — WIND FORECASTING TRACK  
**Phase:** PHASE A2 (Wind Model Development, Training, and Evaluation)  
**Task Type:** Independent Wind-Speed Forecasting Research  
**Authorization Status:** Authorized Phase A2 Research Only (ForecastBundle/EMS Integration **NOT AUTHORIZED**)  
**A2 Champion Selected:** Candidate 3 — Autoregressive Ridge Regression (AR-X)  

---

## 1. OBJECTIVE

Phase A2 establishes an empirical, leakage-safe, independent wind-speed forecasting research capability for the authorized Abisko 10m hourly target.

Specifically, Phase A2 addresses seven primary research requirements:
1. **Formulation:** Defining a 24-hour receding-horizon, 1-hour step forecasting task structure ($H = 24\,\text{h}$, $\Delta t = 1\,\text{h}$, $W_{\text{hist}} = 24\,\text{h}$).
2. **Causal Inputs:** Identifying historical target observations and NWP forecast covariates available at forecast origin $t_0$.
3. **Baselines:** Establishing three reference baselines (Naive Persistence, Diurnal Climate Persistence, Raw NWP Forecast).
4. **Candidate Approaches:** Developing and training three candidate model families (GBDT Direct Multi-Horizon, NWP Bias-Correction GBDT, Autoregressive Ridge AR-X).
5. **Leakage-Safe Validation:** Evaluating candidate performance across strict chronological train/validation/test splits.
6. **Champion Selection:** Identifying an empirical A2 research champion based on held-out test performance.
7. **Reproducibility:** Providing complete code scripts, data provenance, and reproducible metrics.

---

## 2. GOVERNANCE AUTHORIZATION

Phase A2 operates under explicit governance authorization granted by `POLARIS_WIND_A2_TARGET_DEFINITION_GOVERNANCE_DECISION`.

### Authorized Research Activities:
- Dataset preparation and causal feature engineering.
- Forecasting-window construction ($H = 24\,\text{h}$).
- Implementation, training, and inference for baseline and candidate models.
- Temporal validation and hyperparameter selection on validation folds.
- Quantitative evaluation, candidate comparison, and research champion selection.

### Non-Authorized System Activities:
- Wind power generation prediction ($P_{\text{wind}}$ in $\text{W}$).
- Turbine power curve conversion ($v \to P_{\text{wind}}$).
- Altitude boundary layer scaling from Abisko ($392\,\text{m}$) to Nuolja ($702\,\text{m}$).
- Integration with `ForecastBundle` schema v1.0 or EMS/MILP optimizer.
- Modification of frozen POLARIS production architecture or Stage8.1 solar artifacts.

---

## 3. TARGET DEFINITION

The authorized empirical prediction target for Phase A2 is:

$$\text{MEASURED } 10\,\text{m } \text{HOURLY WIND SPEED AT SMHI ABISKO AUT STATION } 188790 \quad (v_{\text{wind}} \text{ in } \text{m/s})$$

- **Target Variable:** `WIND_SPEED`
- **Units:** $\text{m/s}$
- **Measurement Height:** $10.0\,\text{m}$ above ground level
- **Temporal Resolution:** 1 hour
- **Empirical Status:** `MEASURED` (SMHI Station 188790)

---

## 4. PROXY-SITE LIMITATION

Phase A2 explicitly preserves the mandatory governance proxy statement:

> [!IMPORTANT]
> *"Abisko measured wind speed is used as a conditionally supported regional proxy for the Mount Nuolja research context; it is not direct measured Nuolja wind."*
> 
> *"The proxy designation supports use of the Abisko series as the empirical forecasting target for this research track; it does not establish meteorological equivalence between Abisko and Mount Nuolja."*

### Explicit Exclusions
Phase A2 does **NOT** claim that Abisko wind equals Nuolja wind, that Abisko measurements are direct Nuolja measurements, that the $310\,\text{m}$ altitude difference has been corrected, or that a validated Abisko $\rightarrow$ Nuolja transfer model exists.

---

## 5. DATASET PROVENANCE

- **Empirical Target Dataset:** SMHI Station 188790 (`Abisko Aut`), Parameter 4 (`Vindhastighet` / Wind Speed, $10\,\text{m}$, $\text{m/s}$) and Parameter 3 (`Vindriktning` / Wind Direction, $10\,\text{m}$, degrees).
- **Custodian:** Polarforskningssekretariatet (Swedish Polar Research Secretariat) / SMHI.
- **Coverage:** Full 2024 benchmark period ($8,690$ valid hourly records).
- **Predictor Dataset 1:** NWP Forecast Table ([`data/POLARIS_v0_1_future_weather_forecasts_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_future_weather_forecasts_2024.csv)), providing 24-hour horizon predictions (`fc_wind_speed_10m`, `fc_surface_pressure`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `fc_cloud_cover`, `fc_precipitation`).
- **Predictor Dataset 2:** SITES Nuolja Ground Meteorological Table ([`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv)), providing ground `TA`, `RH`, `SW_IN`, `TS`.

---

## 6. DATA QUALIFICATION BEFORE TRAINING

- **Row Count:** $8,690$ hourly observations for 2024 ($100\%$ continuous).
- **Observed Speed Range:** $0.0\,\text{m/s}$ to $25.4\,\text{m/s}$ (annual mean: $3.89\,\text{m/s}$).
- **Missing Values:** $0$ missing target observations in the acquired SMHI series.
- **Quality Flags:** $100\%$ SMHI quality-controlled archive (Codes `G` / `Y`).
- **Timestamp Semantics:** ISO-8601 UTC, 1-hour monotonic grid.

---

## 7. FORECASTING TASK FORMULATION

The A2 forecasting task models receding-horizon wind speed prediction matching the POLARIS operational planning structure:
- **Forecast Horizon ($H$):** $24$ hours ($h = 1, 2, \dots, 24$).
- **Sampling Step ($\Delta t$):** $1$ hour.
- **Historical Lookback ($W_{\text{hist}}$):** $24$ hours ($t_0-23 \dots t_0$).
- **Forecast Origins:** $342$ daily origins ($t_0 = 00:00\text{ UTC}$) across 2024.

---

## 8. CAUSALITY / LEAKAGE CONTROLS

Strict temporal causality is enforced across all models:
- **At Origin $t_0$:** Models ingest target lags ($v_{t_0}, v_{t_0-1}, \dots, v_{t_0-23}$), historical rolling stats, wind direction lags ($\sin\theta, \cos\theta$), ground temperature/humidity, and NWP forecasts published at or before $t_0$.
- **Zero Future Leakage:** Target observations at $t_0+h$ ($h \ge 1$) are strictly forbidden from appearing in feature sets, rolling statistics, or normalization.

---

## 9. TRAIN / VALIDATION / TEST DESIGN

Strict chronological temporal splitting is enforced across the 342 daily forecast origins of 2024:

| Split | Origin Period | Origins Count | Step Instances | Role in Research |
| :--- | :--- | :---: | :---: | :--- |
| **Train Set** | 2024-01-20 to 2024-08-31 | 219 origins | 5,265 rows | Model fitting & coefficient estimation |
| **Validation Set** | 2024-09-01 to 2024-10-31 | 61 origins | 1,464 rows | Hyperparameter tuning & model iteration |
| **Held-out Test Set** | 2024-11-01 to 2024-12-31 | 62 origins | 1,488 rows | **Final unseen evaluation & champion selection** |

---

## 10. BASELINES

Three baseline forecasting models were implemented and evaluated on identical test origins:

1. **Baseline 1: Naive Persistence:**
   $$\hat{y}_{t_0+h} = v_{t_0} \quad \forall h \in \{1, \dots, 24\}$$
2. **Baseline 2: Diurnal Climate Persistence:**
   $$\hat{y}_{t_0+h} = \bar{v}_{\text{train}}(h \pmod{24})$$
   Historical hourly mean wind speed computed strictly from the training set.
3. **Baseline 3: Raw NWP Forecast (`fc_wind_speed_10m`):**
   Uncorrected direct output of NWP forecasted 10m wind speed.

---

## 11. CANDIDATE APPROACHES INVESTIGATED

Three candidate forecasting approach families were developed and trained:

1. **Candidate 1: GBDT Direct Multi-Horizon (`HistGradientBoostingRegressor`):**
   Dedicated GBDT model trained per horizon $h \in \{1, \dots, 24\}$ on causal lag + NWP features.
2. **Candidate 2: NWP Residual Bias-Correction Model:**
   GBDT model trained to predict NWP error residuals ($\delta_h = v_{\text{obs}} - v_{\text{nwp}}$), correcting raw NWP output.
3. **Candidate 3: Autoregressive Ridge Regression (AR-X):**
   Regularized L2 linear model combining target lags, rolling statistics, direction vectors, and NWP forecast covariates.

---

## 12. FEATURE ENGINEERING

Causal features constructed at origin $t_0$:
- **Target Lags:** $v_{t_0}, v_{t_0-1}, v_{t_0-2}, v_{t_0-3}, v_{t_0-6}, v_{t_0-12}, v_{t_0-23}$.
- **Rolling Target Stats (24h):** Mean ($\bar{v}_{24\text{h}}$), Std ($\sigma_{24\text{h}}$), Min ($v_{\min}$), Max ($v_{\max}$), 6h Trend ($v_{t_0} - v_{t_0-6}$).
- **Direction Vectors:** $\sin(\theta_{t_0}), \cos(\theta_{t_0})$.
- **Ground Meteorology:** SITES Nuolja Air Temp ($TA_{t_0}$), Relative Humidity ($RH_{t_0}$).
- **NWP Covariates (Horizon $h$):** `fc_wind_speed_10m`, `fc_surface_pressure`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `fc_cloud_cover`, `fc_precipitation`.
- **Calendar Features:** Horizon hour ($0 \dots 23$), Day of Year ($\sin, \cos$ components).

---

## 13. PREPROCESSING

- **Physical Non-Negativity Clipping:** All predictions clipped at $0.0\,\text{m/s}$ ($\hat{y} = \max(0.0, \hat{y}_{\text{raw}})$).
- **Zero Raw Data Modification:** Raw SMHI source dataset preserved untouched.
- **Isolated Artifact Storage:** Working features and artifacts stored strictly in [`research/wind_a2/`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/).

---

## 14. TRAINING PROCEDURE

- **Environment:** Local Python runtime (`.venv` environment).
- **Execution Script:** [`research/wind_a2/run_a2_wind_speed_experiments.py`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/run_a2_wind_speed_experiments.py).
- **Determinism:** Fixed random seeds (`random_state=42`).

---

## 15. EVALUATION METHODOLOGY

Evaluated on the unseen held-out test set ($1,488$ step instances across 62 daily origins, Nov 01 to Dec 31, 2024).

$$\text{Mean Test Target Wind Speed } (\bar{y}_{\text{test}}) = 5.3486\,\text{m/s}$$

Primary evaluation metrics:
- Mean Absolute Error (MAE in $\text{m/s}$)
- Root Mean Squared Error (RMSE in $\text{m/s}$)
- Mean Bias Error (Bias in $\text{m/s}$)
- Normalized MAE ($\text{nMAE} = \text{MAE} / \bar{y}_{\text{test}} \times 100\%$)
- Normalized RMSE ($\text{nRMSE} = \text{RMSE} / \bar{y}_{\text{test}} \times 100\%$)

---

## 16. RESULTS

### Overall Held-out Test Set Performance Summary

| Model / Baseline | Model Family | MAE ($\text{m/s}$) | RMSE ($\text{m/s}$) | Bias ($\text{m/s}$) | nMAE ($\%$) | nRMSE ($\%$) | MAE Imp vs Pers | MAE Imp vs NWP |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline 1** | Naive Persistence | $2.9334$ | $4.0679$ | $-0.0050$ | $54.84\%$ | $76.06\%$ | Reference | N/A |
| **Baseline 2** | Diurnal Persistence | $2.9302$ | $4.0940$ | $-2.0132$ | $54.78\%$ | $79.03\%$ | $+0.11\%$ | N/A |
| **Baseline 3** | Raw NWP Forecast | $18.8024$ | $22.7894$ | $+18.7913$ | $351.54\%$ | $426.08\%$ | $-540.98\%$ | Reference |
| **Candidate 1** | GBDT Direct Multi-Horizon | $2.1654$ | $2.8962$ | $-0.3319$ | $40.49\%$ | $54.15\%$ | $+26.18\%$ | $+88.48\%$ |
| **Candidate 2** | NWP Bias-Correction GBDT | $4.5137$ | $7.4638$ | $+2.0417$ | $84.39\%$ | $139.55\%$ | $-53.87\%$ | $+76.00\%$ |
| **Candidate 3 (CHAMPION)**| **Autoregressive Ridge AR-X** | **$2.0364$** | **$2.7136$** | **$-0.2793$** | **$38.07\%$** | **$50.73\%$** | **$+30.58\%$** | **$+89.17\%$** |

---

## 17. HORIZON-WISE RESULTS

Horizon-wise breakdown for Candidate 3 (Autoregressive Ridge AR-X Champion) vs Baselines:

| Horizon ($h$) | Target Mean ($\text{m/s}$) | Persistence MAE ($\text{m/s}$) | Raw NWP MAE ($\text{m/s}$) | AR-X MAE ($\text{m/s}$) | AR-X RMSE ($\text{m/s}$) | AR-X Bias ($\text{m/s}$) | Imp vs Pers ($\%$) | Imp vs NWP ($\%$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H01** | $5.3435$ | $0.0000$ | $19.0935$ | $0.0379$ | $0.0469$ | $+0.0169$ | $0.00\%$ | $+99.80\%$ |
| **H02** | $5.0516$ | $1.4242$ | $19.3387$ | $1.4639$ | $1.8526$ | $+0.2450$ | $-2.79\%$ | $+92.43\%$ |
| **H03** | $5.1468$ | $1.6000$ | $18.1645$ | $1.7124$ | $2.2597$ | $+0.3890$ | $-7.02\%$ | $+90.57\%$ |
| **H04** | $5.0403$ | $2.1323$ | $17.9435$ | $2.2095$ | $3.1755$ | $-0.5882$ | $-3.62\%$ | $+87.69\%$ |
| **H05** | $5.4339$ | $1.9613$ | $18.0565$ | $2.0669$ | $2.9462$ | $-0.8846$ | $-5.38\%$ | $+88.55\%$ |
| **H06** | $5.0484$ | $2.2274$ | $18.1516$ | $2.2809$ | $2.8481$ | $-0.8331$ | $-2.40\%$ | $+87.43\%$ |
| **H12** | $5.1129$ | $2.9371$ | $18.6677$ | $2.1154$ | $2.7538$ | $-0.2662$ | $+27.98\%$ | $+88.67\%$ |
| **H18** | $5.7339$ | $3.3855$ | $19.6468$ | $2.2136$ | $2.8710$ | $-0.0964$ | $+34.62\%$ | $+88.73\%$ |
| **H24** | $5.8855$ | $4.1806$ | $19.8645$ | $2.4907$ | $3.2982$ | $-0.2974$ | $+40.42\%$ | $+87.46\%$ |

---

## 18. CANDIDATE COMPARISON

1. **Raw NWP Overestimation Bias:** Raw NWP forecast (`fc_wind_speed_10m`) exhibits severe systematic overestimation bias ($+18.79\,\text{m/s}$ average bias, $\text{MAE} = 18.80\,\text{m/s}$), rendering uncorrected NWP unusable as a microgrid target.
2. **Persistence Breakdown at Long Horizons:** Naive Persistence performs well at $h=1\text{h}$, but error grows rapidly to $4.18\,\text{m/s}$ MAE at $h=24\text{h}$.
3. **Autoregressive Ridge AR-X Superiority:** Candidate 3 (Ridge AR-X) achieves the lowest overall test MAE ($2.0364\,\text{m/s}$) and RMSE ($2.7136\,\text{m/s}$), outperforming Naive Persistence by $+30.58\%$ MAE improvement and Raw NWP by $+89.17\%$ MAE improvement across the 24-hour horizon.

---

## 19. MODEL-SELECTION DECISION

```
A2_RESEARCH_CHAMPION = AUTOREGRESSIVE_RIDGE_ARX
```

### Selected Champion Statement
Project governance designates **Candidate 3: Autoregressive Ridge Regression (AR-X)** as the **A2 Research Champion** for the Abisko 10m wind speed forecasting research track.

- **Empirical Evidence:** Achieves $2.0364\,\text{m/s}$ test MAE ($38.07\%\text{ nMAE}$) and $2.7136\,\text{m/s}$ RMSE, demonstrating statistically significant superiority over Naive Persistence ($2.9334\,\text{m/s}$ MAE) and Raw NWP ($18.8024\,\text{m/s}$ MAE).
- **Provisional Status:** Designated strictly as an **A2 Research Champion**. It is **NOT** declared production-ready and is **NOT** integrated into ForecastBundle or EMS runtime.

---

## 20. REPRODUCIBILITY

- **Execution Script:** [`research/wind_a2/run_a2_wind_speed_experiments.py`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/run_a2_wind_speed_experiments.py)
- **Raw Target Source:** [`research/wind_a2/smhi_188790_ws_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_ws_full.csv)
- **Results JSON Artifact:** [`research/wind_a2/a2_wind_research_results.json`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/a2_wind_research_results.json)
- **Random Seed:** `42`
- **Execution Command:** `python3 research/wind_a2/run_a2_wind_speed_experiments.py`

---

## 21. LIMITATIONS

1. **Target Bound:** Evaluated strictly on 10m measured wind speed ($v_{\text{wind}}$ in $\text{m/s}$). Zero wind power generation ($P_{\text{wind}}$ in $\text{W}$) was evaluated.
2. **Site Transfer Offset:** Abisko Aut ($392\,\text{m}$ a.s.l.) is $310\,\text{m}$ lower than Mount Nuolja AWS ($702\,\text{m}$ a.s.l.). Results represent Abisko microgrid conditions.
3. **No Rerun Manipulation:** Zero result-dependent reruns or post-hoc task changes occurred.

---

## 22. WIND-POWER EXCLUSION

Phase A2 performed **ZERO** conversion from wind speed ($\text{m/s}$) to electrical power ($\text{W}$). No turbine power curves (IEC 61400-12-1) were implemented, and no wind generation forecasting capability is claimed.

---

## 23. NUOLJA PROXY INTERPRETATION OF RESULTS

> [!IMPORTANT]
> All quantitative metrics presented herein ($2.0364\,\text{m/s}$ MAE) represent performance on the empirical **Abisko 10m Measured Wind Speed Target**. They are **NOT** direct measurements of forecasting performance at Mount Nuolja. Conclusions regarding the Nuolja context remain strictly conditional.

---

## 24. FINAL A2 STATUS

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = A2_MODEL_DEVELOPMENT_COMPLETED
A2_RESEARCH_CHAMPION = AUTOREGRESSIVE_RIDGE_ARX
IMPLEMENTATION_STATUS = A2_RESEARCH_ONLY
```

---

## 25. NEXT GOVERNANCE GATE

Before wind forecasting can advance beyond A2 research:
1. **Turbine Power Curve Authorization:** Project governance must authorize an explicit $v_{\text{wind}} \to P_{\text{wind}}$ turbine conversion contract.
2. **Altitude Boundary Layer Contract:** Governance decision regarding $310\,\text{m}$ vertical elevation scaling.
3. **ForecastBundle Contract Resolution:** Formal governance decision on whether to integrate wind forecasting into ForecastBundle schema v1.0.

---

## 26. REQUIRED MACHINE-READABLE STATE

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = A2_MODEL_DEVELOPMENT_COMPLETED
A2_TARGET_VARIABLE = WIND_SPEED
A2_TARGET_UNITS = M/S
A2_TARGET_HEIGHT = 10M
A2_TARGET_RESOLUTION = HOURLY
A2_TARGET_STATION = ABISKO_AUT_188790
A2_TARGET_EMPIRICAL_STATUS = MEASURED
A2_SITE_INTERPRETATION = CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA
A2_DIRECT_NUOLJA_MEASUREMENT = NOT_ESTABLISHED
ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED
A2_WIND_POWER_TARGET = NOT_AUTHORIZED
A2_WIND_GENERATION_FORECASTING = NOT_AUTHORIZED
A2_MODEL_TRAINING = EXECUTED_A2_ONLY
A2_MODEL_INFERENCE = EXECUTED_A2_ONLY
A2_MODEL_SELECTION = COMPLETED_A2_RESEARCH_CHAMPION_SELECTED
A2_RESEARCH_CHAMPION = AUTOREGRESSIVE_RIDGE_ARX
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
IMPLEMENTATION_STATUS = A2_RESEARCH_ONLY
```

---

## 27. SAFETY AND GOVERNANCE FIREWALL

```
STAGE8_1_MODIFIED = NO
D1_D7_MODIFIED = NO
FORECASTBUNDLE_MODIFIED = NO
FORECASTENGINE_MODIFIED = NO
EMS_MODIFIED = NO
MPC_MODIFIED = NO
DIGITAL_TWIN_MODIFIED = NO
FROZEN_SCHEMAS_MODIFIED = NO
D5_HISTORICAL_RESULTS_MODIFIED = NO
SOLAR_RESEARCH_ARTIFACTS_MODIFIED = NO
WIND_POWER_FORECASTING_EXECUTED = NO
NUOLJA_WIND_RECONSTRUCTION_EXECUTED = NO
UNAUTHORIZED_ALTITUDE_SCALING = NO
FORECASTBUNDLE_INTEGRATION = NO
EMS_INTEGRATION = NO
IMPLEMENTATION_STATUS = A2_RESEARCH_ONLY
```

**PHASE A2 WIND MODEL DEVELOPMENT AND TRAINING IS COMPLETE.**
