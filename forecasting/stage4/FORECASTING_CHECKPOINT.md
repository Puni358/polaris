# POLARIS SW_IN Master Forecasting Checkpoint & Handoff Document

> **Document Type:** Project Checkpoint & Scientific Handoff  
> **System:** POLARIS Upstream Solar Irradiance Forecasting Module (SIH 2026)  
> **Status:** Stage 4 Active Champion (33.70% Daytime nMAE on Held-Out Test Set)  
> **Scope:** Stage 1 Baseline Evaluation → Stage 4.2 Post-Hoc Recalibration  
> **Note to Future Agents:** This document is a **checkpoint**, NOT a permanent research freeze. Future AI agents are explicitly permitted and encouraged to pursue scientifically justified improvements to the forecasting model while adhering to the locked benchmark rules defined herein.

---

## Table of Contents
1. [POLARIS Forecasting Problem](#1-polaris-forecasting-problem)
2. [SITES Nuolja Dataset](#2-sites-nuolja-dataset)
3. [Hourly Reconstruction](#3-hourly-reconstruction)
4. [Locked Original Benchmark](#4-locked-original-benchmark)
5. [Baseline Results](#5-baseline-results)
6. [Chronos-2 Zero-Shot Univariate](#6-chronos-2-zero-shot-univariate)
7. [Chronos-2 Multivariate Experiment](#7-chronos-2-multivariate-experiment)
8. [TimesFM 3.0 Evaluation](#8-timesfm-30-evaluation)
9. [Moirai 2.0 R-Small Evaluation](#9-moirai-20-r-small-evaluation)
10. [Chronos LoRA Fine-Tuning](#10-chronos-lora-fine-tuning)
11. [Clear-Sky & Clearness Index ($k_t$) Experiments](#11-clear-sky--clearness-index-k_t-experiments)
12. [NWP Dataset & Forensic Correction](#12-nwp-dataset--forensic-correction)
13. [NWP Forecast Skill Analysis](#13-nwp-forecast-skill-analysis)
14. [Stage 3: NWP Covariate Integration](#14-stage-3-nwp-covariate-integration)
15. [Stage 4: Current Champion Ensemble](#15-stage-4-current-champion-ensemble)
16. [Stage 4 Forensic Residual Diagnosis](#16-stage-4-forensic-residual-diagnosis)
17. [Stage 4.1: Cloud-Regime Isotonic Correction (Failed)](#17-stage-41-cloud-regime-isotonic-correction-failed)
18. [Stage 4.2: Per-Horizon Affine Recalibration (Failed)](#18-stage-42-per-horizon-affine-recalibration-failed)
19. [Current Experiment Leaderboard](#19-current-experiment-leaderboard)
20. [Lessons & Negative Constraints for Future Agents](#20-lessons--negative-constraints-for-future-agents)
21. [Guidelines for Future Optimization](#21-guidelines-for-future-optimization)
22. [Scientific Status of Remaining Error (~34% nMAE)](#22-scientific-status-of-remaining-error-34-nmae)
23. [Stage 5 Downstream Handoff (PV Module)](#23-stage-5-downstream-handoff-pv-module)
24. [Complete Master Inventory of Artifact Paths](#24-complete-master-inventory-of-artifact-paths)

---

## 1. POLARIS Forecasting Problem

* **Project:** POLARIS (Sub-Arctic Microgrid Energy Management & Optimization, SIH 2026)
* **Forecasting Target:** `SW_IN`
* **Target Definition:** Shortwave incoming solar radiation / global horizontal irradiance (GHI)
* **Unit of Measurement:** Watts per square meter ($\text{W/m}^2$)
* **Temporal Setup:**
  * **Context Window:** Previous 24 hourly observations ($t-23, \dots, t_0$)
  * **Forecast Horizon:** Next 24 hourly values ($t_1, \dots, t_{24}$, corresponding to $H1 \dots H24$)
* **System Context:** The irradiance forecasting module operates as an **upstream core component** of the POLARIS energy management pipeline. Future downstream modules (PV generation digital twin, synthetic load modeling, battery/diesel hybrid EMS, robust optimization, and what-if simulation) consume `SW_IN` forecasts as primary driving inputs.

---

## 2. SITES Nuolja Dataset

* **Official Source:** SITES (Swedish Infrastructure for Ecosystem Science) Nuolja 2024 Data Release.
* **Source Filename:** `SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`
* **Station Name:** Nuolja Middle Station (NMS), Abisko Scientific Research Station, Sweden.
* **Geographic Coordinates:**
  * Latitude: $68.362074^\circ\text{N}$
  * Longitude: $18.738752^\circ\text{E}$
* **Timezone:** UTC+1 (Standard Station Time)
* **Original Sampling:** 10-minute automated meteorological observations.
* **2024 Temporal Coverage:** 52,704 ten-minute rows spanning January 1, 2024 to December 31, 2024.
* **Variables Present in Source:** `TIMESTAMP`, `TA` (Air Temp), `TA_STD`, `RH` (Relative Humidity), `SW_IN` (Incoming Shortwave), `TS_-0.01m` (Soil Temp), `TS_STD`, `PRECIP` (Precipitation), `D_SNOW` (Snow Depth).
* **Data Quality Characteristics:** SITES Level 2 (L2) data undergo standard quality control for sensor range bounds and unrealistic outliers. However, data gaps caused by extreme weather or telemetry outages are left un-filled in the official release.
* **Elevation Note:** No official station elevation is claimed unless explicitly verified from site metadata documentation.

---

## 3. Hourly Reconstruction

To create a standardized hourly time series for benchmark evaluation, 10-minute observations are aggregated as follows:

* **Hourly Instantaneous/Average Variables (`TA`, `RH`, `SW_IN`, `TS_-0.01m`):**
  Six 10-minute observations from minute `:00` to `:50` (`HH:00`, `HH:10`, `HH:20`, `HH:30`, `HH:40`, `HH:50`) are averaged arithmetic-mean style and assigned to the hour timestamp `HH:00`.
* **Accumulated Variables (`PRECIP`):**
  The six 10-minute observations are summed over the hour to represent total hourly precipitation accumulation (mm).

### Clean Dataset Files Created:
1. **Clean 5-Variable Hourly Dataset:**
   * **Path:** `/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv`
   * **Dimensions:** 8,784 hourly rows $\times$ 6 columns (`TIMESTAMP`, `TA`, `RH`, `SW_IN`, `TS_-0.01m`, `PRECIP`).
   * **Completeness:** 100% complete, zero missing values across all 5 primary meteorological variables.
2. **Full Multivariate Hourly Dataset:**
   * **Path:** `/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`
   * **Dimensions:** 8,784 hourly rows $\times$ 9 columns.
   * **Data Note:** Contains `D_SNOW` which exhibits missing values due to sensor optical limits during melt/freeze transitions.

---

## 4. Locked Original Benchmark

To ensure zero scientific ambiguity and prevent data leakage across model comparisons, the original benchmark is locked under strict rules:

* **Target Variable:** `SW_IN` ($\text{W/m}^2$)
* **Historical Context Window:** 24 hours
* **Forecast Horizon:** 24 hours ($H1 \dots H24$)
* **Full Benchmark Origins:** 365 non-overlapping daily forecast windows starting at 00:00 UTC+1 each day.
* **Full Benchmark Total Hours:** $365 \times 24 = 8,760$ forecast hours.
* **Daytime Sub-Selection Rule:** Daytime hours are strictly defined as observations where actual $\text{SW\_IN} > 0$.
* **Probabilistic Quantile Rule:** Point predictions evaluate the 0.5 quantile (median) output for probabilistic model outputs.
* **Primary Evaluation Metric:** Daytime Normalized Mean Absolute Error ($\text{nMAE}_{\text{day}}$):
  $$\text{nMAE}_{\text{day}} = \frac{\text{Daytime MAE}}{\text{mean}(\text{Daytime Actual } \text{SW\_IN})} \times 100\%$$
* **Reported Secondary Metrics:** MAE (overall), RMSE (overall), Daytime MAE, Daytime RMSE.
* **Metric Exclusion Warning:** MAPE (Mean Absolute Percentage Error) is explicitly prohibited due to division-by-zero instability caused by zero and near-zero night/twilight values.
* **Benchmark Reference Artifact:**
  * **Path:** `/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv`
  * **Dimensions:** 8,760 rows $\times$ 6 columns (`forecast_start`, `horizon_hour`, `timestamp`, `actual_SW_IN`, `seasonal_naive_24h`, `persistence_24h`).

---

## 5. Baseline Results

Evaluated across the full 365 daily origins (8,760 forecast hours):

| Model / Baseline | Overall MAE ($\text{W/m}^2$) | Overall RMSE ($\text{W/m}^2$) | Daytime MAE ($\text{W/m}^2$) | Daytime RMSE ($\text{W/m}^2$) | Daytime nMAE (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Seasonal Naive (24h)** | 37.19 | 85.13 | 55.10 | 103.62 | 42.76% |
| **Persistence (24h)** | 83.49 | 169.37 | 123.71 | 206.17 | 95.99% |

---

## 6. Chronos-2 Zero-Shot Univariate

* **Model Architecture:** Amazon Chronos-2 (`amazon/chronos-2`, Version 2.3.1)
* **Input Features:** Univariate historical 24h `SW_IN` sequence only.
* **Evaluation Setup:** 365 daily forecast origins (8,760 hours).
* **Performance:**
  * **Overall MAE:** 36.59 $\text{W/m}^2$
  * **Overall RMSE:** 79.47 $\text{W/m}^2$
  * **Daytime MAE:** 54.01 $\text{W/m}^2$
  * **Daytime RMSE:** 96.73 $\text{W/m}^2$
  * **Daytime nMAE:** 41.91%
* **Prediction Artifact:** `/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv`
* **Key Observations:**
  * Outperformed persistence and slightly beat the 24h seasonal naive baseline.
  * Demonstrated strongest accuracy in the midday window ($H6\dots H15$).
  * Maintained systematic under-prediction error during peak clear-sky clear-air periods (high solar amplitude truncation).
  * Generated 338 negative raw prediction values ($< 0 \text{ W/m}^2$) which were preserved in the raw artifact for auditing.

---

## 7. Chronos-2 Multivariate Experiment

* **Model:** Chronos-2 multivariate forecasting setup.
* **Inputs:** Historical `SW_IN` combined with historical context weather variables (`TA`, `RH`, `TS`, `PRECIP`).
* **Performance:**
  * **Overall MAE:** 36.92 $\text{W/m}^2$
  * **Overall RMSE:** 79.68 $\text{W/m}^2$
  * **Daytime MAE:** 54.30 $\text{W/m}^2$
  * **Daytime RMSE:** 96.98 $\text{W/m}^2$
  * **Daytime nMAE:** 42.14%
* **Verdict:** Slightly degraded performance relative to univariate Chronos-2.
* **Lesson Learned:** Adding historical ground weather covariates alone fails to address solar amplitude truncation because past weather provides insufficient information regarding future cloud movement and solar geometry.
* **Artifact Path:** `/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv`

---

## 8. TimesFM 3.0 Evaluation

* **Model Architecture:** Google TimesFM 3.0 zero-shot.
* **Input:** Univariate historical `SW_IN`.
* **Performance (365 origins):**
  * **Overall MAE:** 58.25 $\text{W/m}^2$
  * **Overall RMSE:** 123.32 $\text{W/m}^2$
  * **Daytime MAE:** 86.17 $\text{W/m}^2$
  * **Daytime RMSE:** 150.11 $\text{W/m}^2$
  * **Daytime nMAE:** 66.87%
* **Verdict:** Performed substantially worse than zero-shot Chronos-2 and Seasonal Naive on sub-arctic solar series.
* **Artifact Path:** `/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv`

---

## 9. Moirai 2.0 R-Small Evaluation

* **Model Architecture:** Salesforce / Uni2TS Moirai 2.0 R-small.
* **Input:** Univariate historical `SW_IN`.
* **Performance (365 origins):**
  * **Overall MAE:** 72.26 $\text{W/m}^2$
  * **Overall RMSE:** 147.85 $\text{W/m}^2$
  * **Daytime MAE:** 106.56 $\text{W/m}^2$
  * **Daytime RMSE:** 179.96 $\text{W/m}^2$
  * **Daytime nMAE:** 82.69%
* **Verdict:** Performed worse than Chronos-2 and Seasonal Naive.
* **Artifact Path:** `/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv`

---

## 10. Chronos LoRA Fine-Tuning

* **Configuration Investigated:** Low-Rank Adaptation (LoRA) fine-tuning of Chronos models ($r=8$, $\alpha=16$, learning rate $= 1\text{e-}5$).
* **Experiments:** Multiple training context window splits were evaluated.
* **Outcome:** Fine-tuned LoRA variants failed to demonstrate consistent, held-out validation improvements over zero-shot Chronos-2.
* **Scientific Statement:** *"The tested LoRA configurations did not provide a robust held-out improvement, so they were not retained in the current champion pipeline."* Future agents may re-explore LoRA provided alternative adapter architectures or loss functions are used.

---

## 11. Clear-Sky & Clearness Index ($k_t$) Experiments

* **Clear-Sky Modeling:** Deterministic PVLIB clear-sky GHI, solar elevation ($\theta_{\text{el}}$), and zenith ($\theta_z$) computed for station coordinates.
* **Clearness Index Definition:** $k_t = \frac{\text{SW\_IN}}{\text{GHI}_{\text{clearsky}}}$.
* **Smart Persistence on $k_t$ ($k_t(t+h) = k_t(t)$):**
  * Daytime MAE $\approx 55.05 \text{ W/m}^2$, Daytime RMSE $\approx 103.30 \text{ W/m}^2$
* **Direct Chronos Forecasting of $k_t$:**
  * Forecasting $k_t$ via Chronos and scaling by $\text{GHI}_{\text{clearsky}}$ resulted in Daytime MAE $\approx 64.85 \text{ W/m}^2$, Daytime RMSE $\approx 118.03 \text{ W/m}^2$.
* **Verdict:** Direct neural forecasting of $k_t$ severely degraded performance due to extreme sensitivity near low solar elevation angles ($\theta_{\text{el}} \to 0$).
* **Scientific Caveat:** This finding does not invalidate all clear-sky normalization techniques; it specifically establishes that unconstrained neural prediction of raw $k_t$ ratios introduces edge instability.

---

## 12. NWP Dataset & Forensic Correction

To provide future atmospheric awareness for horizons $H1\dots H24$, Numerical Weather Prediction (NWP) forecasts were integrated:

* **NWP Data Source:** MET Norway / MET Nordic (`metno_seamless` historical forecast archive).
* **Target NWP Covariates:** Total cloud cover, 2m air temperature, 2m relative humidity, total precipitation, surface pressure, 10m wind speed.
* **Data Forensic Findings & Quality Audit:**
  * Early-January coverage gaps (447 hourly rows / 18 daily forecast origins) were present due to archive storage boundaries.
  * Low/mid/high cloud tier fields were missing from the historical seamless feed.
  * Initial attempts to backfill missing early-January origins using forward/backward fill (`ffill`/`bfill`) introduced future leakage and were rejected.
* **Cleaned NWP Benchmark Standard:**
  * **Valid Origins:** 347 forecast origins (8,328 forecast hours). 18 incomplete early-January origins strictly excluded.
* **NWP Artifact Paths:**
  * Clean NWP Forecasts: `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2024.csv`
  * NWP Audit Pass/Fail Mapping: `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_coverage_pass_fail.csv`

---

## 13. NWP Forecast Skill Analysis

Stage 2 evaluated the statistical association between forecast NWP variables and observed ground `SW_IN`:

* **Linear Pearson Correlations (Daytime/Overall):**
  * **Cloud Cover:** Overall $r \approx -0.206$, Daytime $r \approx -0.209$
  * **Air Temperature:** Overall $r \approx +0.371$
  * **Relative Humidity:** Overall $r \approx -0.420$
  * **Precipitation:** Overall $r \approx -0.109$
  * **Surface Pressure:** Overall $r \approx +0.285$
  * **Wind Speed:** Overall $r \approx -0.177$
* **Forensic Correction Note:** An earlier interim draft log reported an erroneous $H3$ precipitation correlation of $-1.125$. Investigation confirmed this was a manual text formatting glitch. The actual mathematically validated value is $r = -0.1245$. Assertions in the analysis code now enforce $r \in [-1.0, 1.0]$.
* **Skill Audit Artifacts:**
  * Script: `/home/punith-bs/01polaris (Copy)/clear_sky/analyze_nwp_forecast_skill.py`
  * Summary: `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_skill_summary.csv`

---

## 14. Stage 3: NWP Covariate Integration

Stage 3 evaluated integrating future NWP forecasts into Chronos via exogenous feature paths across the 347 clean NWP origins:

1. **Stage 3A (Solar Geometry + Clear-Sky Deterministic):**
   * Features: Solar elevation, solar zenith, clear-sky GHI.
   * Daytime MAE = 54.01 $\text{W/m}^2$, Daytime RMSE = 97.41 $\text{W/m}^2$.
2. **Stage 3B (Solar Geometry + Future Total Cloud Cover NWP):**
   * Features: Solar geometry + forecast total cloud fraction ($H1\dots H24$).
   * Daytime MAE = 52.92 $\text{W/m}^2$, Daytime RMSE = 94.77 $\text{W/m}^2$.
   * **Outcome:** Best performing Stage 3 configuration.
3. **Stage 3C (Solar Geometry + Full Available NWP):**
   * Features: Cloud, temp, RH, precip, pressure, wind speed.
   * Daytime MAE = 53.55 $\text{W/m}^2$, Daytime RMSE = 94.97 $\text{W/m}^2$.
   * **Outcome:** Adding full meteorological fields slightly degraded performance compared to Stage 3B.

* **Summary Statement:** *"Among the tested exogenous feature combinations, solar geometry combined with future total cloud cover forecasts produced the strongest empirical performance."*
* **Artifact Directory:** `/home/punith-bs/01polaris (Copy)/stage3/`

---

## 15. Stage 4: Current Champion Ensemble

Stage 4 introduced the **Horizon-Adaptive Cloud-Damped Clear-Sky Ensemble**, blending data-driven neural forecasts with physical radiative transfer principles.

### Ensembling Mathematical Formula:
$$\text{forecast}_h = w_h \cdot \text{Chronos3B}_h + (1 - w_h) \cdot \max\left(0, \text{GHI}_{\text{clearsky}, h} \cdot (1 - k_h \cdot \text{cloud\_frac}_h)\right)$$

Where:
* $\text{Chronos3B}_h$: Stage 3B Chronos prediction at horizon hour $h$.
* $\text{GHI}_{\text{clearsky}, h}$: Deterministic PVLIB clear-sky solar irradiance.
* $\text{cloud\_frac}_h$: MET Nordic forecast total cloud fraction ($[0, 1]$).
* $w_h, k_h$: Horizon-specific blending weights and cloud extinction coefficients optimized on training origins.

### Official Benchmark Performance Summary:

#### A. Full 347-Origin Clean Benchmark (8,328 hours / 5,768 daytime hours):
* **Overall MAE:** 29.54 $\text{W/m}^2$
* **Overall RMSE:** 61.08 $\text{W/m}^2$
* **Daytime MAE:** 42.51 $\text{W/m}^2$
* **Daytime RMSE:** 73.39 $\text{W/m}^2$
* **Daytime nMAE:** 32.98%
* **Daytime Bias:** -4.25 $\text{W/m}^2$
* **Night MAE:** 0.32 $\text{W/m}^2$

#### B. Rigorous Even/Odd Held-Out Test Set (173 Odd Origins / 2,883 daytime hours):
* **Overall MAE:** 30.27 $\text{W/m}^2$
* **Overall RMSE:** 62.38 $\text{W/m}^2$
* **Daytime MAE:** 43.45 $\text{W/m}^2$ (43.451 $\text{W/m}^2$)
* **Daytime RMSE:** 74.85 $\text{W/m}^2$
* **Daytime nMAE:** 33.70%
* **Daytime Bias:** -1.97 $\text{W/m}^2$
* **Night MAE:** 0.32 $\text{W/m}^2$

> **Metric Subset Clarification Note:** Stage 4 metrics appear with slightly different values across historical reports because evaluations were performed on different origin subsets:
> * **Full 347-Origin Clean Benchmark (`stage4_results/final_metrics.csv`):** Evaluates all 347 clean forecast origins (5,768 daytime hours), yielding **Daytime MAE = 42.51 W/m²** and **Daytime nMAE = 32.98%**.
> * **173 Odd-Origin Held-Out Test Set (`stage4_2_horizon_affine/final_metrics.csv`):** Evaluates the 173 odd-indexed test origins (2,883 daytime hours) used for controlled recalibration experiments, yielding **Daytime MAE = 43.451 W/m²** and **Daytime nMAE = 33.70%**.
> * **Interim Test Split Runs:** Some earlier narrative reports cited Daytime MAE = 43.292 W/m² from an interim test split pass.
> 
> The original Stage 4 final metrics artifact (`stage4_results/final_metrics.csv`) remains the authoritative source for the full Stage 4 benchmark result, while downstream calibration experiments retain their own comparison subset metrics.

* **Current Status:** **LOCKED ACTIVE CHAMPION** / Official Baseline for all future research.

---

## 16. Stage 4 Forensic Residual Diagnosis

A thorough forensic diagnosis of Stage 4 residual errors ($e_t = \hat{y}_t - y_t$) revealed:
1. **Amplitude Compression:** High solar irradiance events ($> 500 \text{ W/m}^2$) exhibit persistent under-prediction.
2. **Horizon Bias Stability:** Bias across horizon steps $H1\dots H24$ displays a stable, low-frequency diurnal wave.
3. **Cloud Regime Instability:** Error distributions partitioned strictly by NWP cloud cover bins ($[0-0.2]$, $[0.2-0.4]$, etc.) varied significantly between even-indexed training origins and odd-indexed test origins.
4. **Transition Dynamics:** Temporal cloud transition rates ($\Delta \text{cloud}/\Delta t$) provided minimal independent explanatory power for prediction errors.
5. **Concentration of Large Errors:** Severe absolute errors ($> 150 \text{ W/m}^2$) were concentrated in a narrow subset ($< 8\%$) of daytime hours characterized by broken cloud cover.

---

## 17. Stage 4.1: Cloud-Regime Isotonic Correction (Failed)

* **Hypothesis:** Post-processing predictions with per-cloud-regime isotonic calibration curves would alleviate amplitude compression.
* **Method:** Fit 5 separate isotonic regression curves (one per NWP cloud fraction regime) using training origins and evaluate on odd test origins.
* **Test Performance:**
  * **Daytime MAE:** 45.22 $\text{W/m}^2$ (vs Stage 4 Baseline: 43.45 $\text{W/m}^2$, **+1.77 W/m² worse**)
  * **Daytime nMAE:** 35.07% (vs Stage 4 Baseline: 33.70%, **+1.37 pp worse**)
* **Verdict:** **REJECTED**. Static cloud-regime calibration overfit training cloud distributions and failed to generalize to held-out weather sequences.
* **Artifact Path:** `/home/punith-bs/01polaris (Copy)/stage4/stage4_1_cloud_regime_correction/`

---

## 18. Stage 4.2: Per-Horizon Affine Recalibration (Failed)

* **Hypothesis:** Diurnal horizon-dependent bias could be eliminated via regularized per-horizon affine scaling ($\hat{y}_{h,\text{corr}} = \max(0, a_h \hat{y}_h + b_h)$ with Ridge penalty $\lambda = 0.7$).
* **Evaluation (173 Odd Test Origins):**
  * **Overall MAE:** 31.59 $\text{W/m}^2$
  * **Daytime MAE:** 44.08 $\text{W/m}^2$ (vs Stage 4 Baseline: 43.45 $\text{W/m}^2$, **+0.63 W/m² worse**)
  * **Daytime nMAE:** 34.19% (vs Stage 4 Baseline: 33.70%, **+0.49 pp worse**)
  * **Horizon Breakdown:** Improved only 1 of 24 horizon hours, degraded 11 of 24.
  * **Night MAE:** Worsened from 0.32 $\text{W/m}^2$ to 3.21 $\text{W/m}^2$ due to positive affine intercept drift ($b_h > 0$).
* **Verdict:** **REJECTED**. Post-hoc linear scaling is ineffective because error phase structure varies dynamically day-to-day.
* **Artifact Path:** `/home/punith-bs/01polaris (Copy)/stage4/stage4_2_horizon_affine/`

---

## 19. Current Experiment Leaderboard

Across the POLARIS forecasting research pipeline, 15 distinct baselines, neural foundation models, exogenous NWP configurations, clear-sky physics models, and post-hoc calibration strategies were evaluated. All evaluations below reflect standardized benchmark rules.

| Rank | Model / Experiment Stage | Evaluation Windows | Overall MAE ($\text{W/m}^2$) | Overall RMSE ($\text{W/m}^2$) | Daytime MAE ($\text{W/m}^2$) | Daytime RMSE ($\text{W/m}^2$) | Daytime nMAE (%) | Status / Note |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Stage 4 (Odd Test Split)** | **173 (Test)** | **30.27** | **62.38** | **43.45** | **74.85** | **33.70%** | **CURRENT CHAMPION** |
| 2 | Stage 4 (Full 347 Clean) | 347 (Full) | 29.54 | 61.08 | 42.51 | 73.39 | 32.98% | Full-Set Baseline Reference |
| 3 | Stage 4.2 (Horizon Affine) | 173 (Test) | 31.59 | 62.25 | 44.08 | 74.64 | 34.19% | REJECTED (Worse than Stg 4) |
| 4 | Stage 4.1 (Cloud Isotonic) | 347 (Full) | 29.71 | 60.82 | 42.48 | 73.07 | 35.07% (Test) | REJECTED (Overfit split) |
| 5 | Stage 3B (Chronos + Cloud NWP) | 347 (Full) | 36.93 | 78.87 | 52.92 | 94.77 | 41.06% | Best Pure Neural Model |
| 6 | Stage 3C (Chronos + Full NWP) | 347 (Full) | 37.34 | 79.04 | 53.55 | 94.97 | 41.55% | Exogenous NWP Exceeded |
| 7 | Stage 3A (Solar Geometry) | 347 (Full) | 37.68 | 81.07 | 54.01 | 97.41 | 41.91% | Baseline Solar Features |
| 8 | Chronos-2 Zero-Shot | 365 (Full) | 36.59 | 79.47 | 54.01 | 96.73 | 41.91% | Zero-Shot Foundation Baseline |
| 9 | Chronos-2 Multivariate | 365 (Full) | 36.92 | 79.68 | 54.30 | 96.98 | 42.14% | Ground Weather Inputs |
| 10 | Smart Persistence on $k_t$ | 365 (Full) | 37.15 | 84.86 | 55.05 | 103.30 | 42.72% | Clearness Index Baseline |
| 11 | 24h Seasonal Naive | 365 (Full) | 37.19 | 85.13 | 55.10 | 103.62 | 42.76% | Standard Reference Baseline |
| 12 | Chronos-2 (Direct $k_t$) | 365 (Full) | 43.77 | 96.96 | 64.85 | 118.03 | 50.32% | Degraded Ratio Model |
| 13 | TimesFM 3.0 Zero-Shot | 365 (Full) | 58.25 | 123.32 | 86.17 | 150.11 | 66.87% | Outperformed by Chronos |
| 14 | Moirai 2.0 R-Small | 365 (Full) | 72.26 | 147.85 | 106.56 | 179.96 | 82.69% | Outperformed by Chronos |
| 15 | 24h Persistence | 365 (Full) | 83.49 | 169.37 | 123.71 | 206.17 | 95.99% | Trivial Baseline |

---

## 20. Lessons & Negative Constraints for Future Agents

Future agents working on POLARIS forecasting **MUST NOT** repeat the following invalid practices:

1. **No Synthetic NWP Fabrication:** NEVER use `bfill`, `ffill`, or spatial interpolation to fabricate missing early-January NWP forecast horizons.
2. **No Leakage via Weather Actuals:** NEVER feed future observed weather actuals ($t+1 \dots t+24$) into a forecast model; only historical context ($t-23 \dots t$) and valid NWP forecast products are permitted.
3. **No Unverified Sub-Cloud Fields:** Do NOT assume low/mid/high cloud tier variables exist in the seamless MET Nordic historical dataset.
4. **Prohibition of MAPE Metric:** Do NOT evaluate models using MAPE.
5. **No Silent Split Alterations:** Do NOT alter the 347 clean origin list or the even/odd train/test origin split without documenting the change.
6. **No Unconstrained Ratio Prediction:** Do NOT predict unconstrained $k_t$ ratios directly near solar horizon edges ($\theta_{\text{el}} < 5^\circ$).
7. **No Deletion of Failed Research:** Do NOT delete or overwrite code/artifacts from Stage 4.1 or Stage 4.2; they serve as permanent scientific negative controls.

---

## 21. Guidelines for Future Optimization

Forecasting research on POLARIS remains **OPEN**. Future agents are encouraged to explore novel methods under the following constraints:

### Permissible Research Avenues:
* **Advanced Physics-Informed ML:** Incorporating cloud optical depth ($\tau$) or aerosol optical thickness modeling.
* **Higher-Resolution Spatial Inputs:** Satellite-derived cloud motion vectors or high-resolution ECMWF HRES data.
* **Probabilistic & Uncertainty Forecasting:** Conformal prediction intervals or deep quantile regression models.
* **Dynamic Ensembling:** Spatiotemporal attention or graph-based forecast fusion.

### Mandated Validation Protocol:
Every proposed future model must:
1. Evaluate against the locked 347-origin benchmark (or exact odd-origin held-out test split).
2. Report Daytime MAE, Daytime RMSE, and Daytime nMAE.
3. Demonstrate a statistically significant held-out nMAE reduction below **33.70%** to displace Stage 4 as champion.

---

## 22. Scientific Status of Remaining Error (~34% nMAE)

* **Current Reality:** The active champion model achieves **33.70% Daytime nMAE** on held-out test origins.
* **Accurate Characterization:** The residual error represents unresolved atmospheric variance between NWP total cloud fraction and localized sub-arctic cloud optical transmittance, combined with micro-scale terrain interactions at Abisko ($68.36^\circ\text{N}$).
* **Prohibited Claims:**
  * Do NOT claim remaining error is "proven mathematically irreducible".
  * Do NOT claim remaining error is "100% weather noise".
  * Do NOT claim "no future model can outperform Stage 4".

---

## 23. Stage 5 Downstream Handoff (PV Module)

The POLARIS system architecture connects forecasting to downstream energy management:

```
[Irradiance Forecast: SW_IN (W/m²)]  <-- (Stage 4 Champion: Active Input)
                 │
                 ▼
    [Stage 5: PV Digital Twin]       <-- (Converts SW_IN to kW AC/DC Power)
                 │
                 ▼
     [Synthetic Station Load]
                 │
                 ▼
[Battery + Diesel Hybrid EMS Optimization]
                 │
                 ▼
[Robust Optimization & What-If Simulator]
```

### Current Handoff State:
* Downstream modules (Stage 5 PV twin) shall consume **Stage 4 Ensemble Predictions** (`ensemble_predictions.csv`) as the primary solar irradiance input.
* Upstream forecasting research may continue in parallel without blocking Stage 5 development.

---

## 24. Complete Master Inventory of Artifact Paths

All paths verified on local filesystem:

| Description / Name | Absolute File System Path |
| :--- | :--- |
| **SITES Nuolja Raw 2024 CSV** | `/home/punith-bs/01polaris (Copy)/data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv` |
| **Hourly 5-Variable Dataset** | `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` |
| **Hourly Multivariate Dataset**| `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` |
| **Fixed 24h Benchmark CSV** | `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_fixed_24h_benchmark.csv` |
| **Baseline 365 Metrics** | `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_fixed_24h_baseline_metrics.csv` |
| **Chronos-2 Predictions** | `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_chronos2_predictions.csv` |
| **Chronos-2 Multivariate Preds**| `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_chronos2_multivariate_predictions.csv` |
| **TimesFM 3.0 Predictions** | `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_timesfm3_predictions.csv` |
| **Moirai 2.0 Predictions** | `/home/punith-bs/01polaris (Copy)/POLARIS_v0_1_moirai2_predictions.csv` |
| **Clearsky Decomposition CSV** | `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv` |
| **Clean NWP Forecast Data** | `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2024.csv` |
| **NWP Pass/Fail Coverage Map** | `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_coverage_pass_fail.csv` |
| **NWP Skill Analysis Script** | `/home/punith-bs/01polaris (Copy)/clear_sky/analyze_nwp_forecast_skill.py` |
| **NWP Skill Summary CSV** | `/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_skill_summary.csv` |
| **Stage 3 Directory** | `/home/punith-bs/01polaris (Copy)/stage3/` |
| **Stage 3 Script** | `/home/punith-bs/01polaris (Copy)/stage3/run_stage3_experiments.py` |
| **Stage 3 Model Comparison** | `/home/punith-bs/01polaris (Copy)/stage3/stage3_model_comparison.csv` |
| **Stage 4 Pipeline Script** | `/home/punith-bs/01polaris (Copy)/stage4/run_stage4_pipeline.py` |
| **Stage 4 Methodology Doc** | `/home/punith-bs/01polaris (Copy)/stage4/METHODOLOGY.md` |
| **Stage 4 Results Directory** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_results/` |
| **Stage 4 Predictions (Champion)**| `/home/punith-bs/01polaris (Copy)/stage4/stage4_results/ensemble_predictions.csv` |
| **Stage 4 Parameters JSON** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_results/ensemble_parameters.json` |
| **Stage 4 Final Metrics CSV** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_results/final_metrics.csv` |
| **Stage 4.1 Directory** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_1_cloud_regime_correction/` |
| **Stage 4.1 Script** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_1_cloud_regime_correction/run_stage4_1.py` |
| **Stage 4.1 Final Metrics** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_1_cloud_regime_correction/final_metrics.csv` |
| **Stage 4.2 Directory** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_2_horizon_affine/` |
| **Stage 4.2 Script** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_2_horizon_affine/run_stage4_2.py` |
| **Stage 4.2 Predictions** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_2_horizon_affine/corrected_predictions.csv` |
| **Stage 4.2 Final Metrics** | `/home/punith-bs/01polaris (Copy)/stage4/stage4_2_horizon_affine/final_metrics.csv` |
| **Master Forecasting Checkpoint**| `/home/punith-bs/01polaris (Copy)/stage4/FORECASTING_CHECKPOINT.md` |

---
*End of POLARIS Forecasting Master Checkpoint & Handoff Document.*


---

## 25. Stage 4.3: Dynamic Blending Experiment (Rejected)

* **Experiment Date:** September 10, 2026
* **Research Hypothesis:** The optimal balance between Chronos neural forecast and physics-based NWP forecast is **state-dependent** rather than fixed solely by horizon.
* **Mathematical Formulation:**
  ```
  logit(w_dynamic) = logit(w_stage4_h) + X_scaled @ theta
  P_dynamic = w_dynamic * P_chronos + (1 - w_dynamic) * P_physics
  ```
* **Methodology:** Delta-parameterized logistic blender with 10 forecast-time features, trained via Ridge regression (λ=100) with Huber loss on 174 EVEN origins using forward-chaining cross-validation.
* **Features:** solar_elevation, clearsky_ghi, horizon_hour, cloud_frac, ctx_mean, ctx_max, ctx_std, pred_chronos, pred_physics, clearsky_x_clearfrac.
* **Test Performance (173 ODD Origins, Daytime):**
  * **Daytime MAE:** 43.463 W/m² (vs Stage 4: 43.451 W/m², **Δ = +0.012 W/m²**)
  * **Daytime nMAE:** 33.71% (vs Stage 4: 33.70%, **Δ = +0.01 pp**)
  * **Statistical significance:** p = 0.9791 (not significant)
  * **Bootstrap 95% CI:** [-0.055, +0.063] W/m²
* **Weight Diagnostics:** Dynamic weights nearly identical to Stage 4 fixed weights (mean: 0.4361 vs 0.4345, std: 0.2628 vs 0.2633). Model essentially reproduced horizon-specific baseline.
* **Feature Importance:** All coefficients very small (|θ| < 0.05), with cloud_frac (-0.042) and clearsky_x_clearfrac (+0.022) having strongest but still minimal effects.
* **Per-Horizon:** Improved 2/24 horizons, degraded 3/24, neutral 19/24.
* **Verdict:** **REJECTED**. Dynamic blending provided no improvement over Stage 4 baseline. Features lack sufficient state-dependent signal. Stage 4's horizon-adaptive weights already capture dominant pattern.
* **Scientific Value:** Rigorous negative result validates Stage 4 as near-optimal and rules out state-dependent blending hypothesis for this dataset.
* **Artifact Directory:** `/home/punith-bs/01polaris (Copy)/stage4/stage4_3_dynamic_blending/`
* **Key Artifacts:**
  * Implementation: `run_stage4_3.py`
  * Predictions: `dynamic_predictions.csv`
  * Parameters: `model_parameters.json`
  * Diagnostics: `diagnostics.png`
  * Documentation: `README.md`, `EXPERIMENT_SUMMARY.txt`
* **Recommendation:** Do NOT pursue Stage 4.3.v2 without substantial new information. Retain **Stage 4 as official champion** (Daytime MAE = 43.45 W/m², nMAE = 33.70%).

---

*Last updated: September 10, 2026 — Stage 4.3 Dynamic Blending Experiment Complete (Rejected)*
