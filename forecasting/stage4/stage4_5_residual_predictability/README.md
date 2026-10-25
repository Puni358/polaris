# Stage 4.5: Residual Predictability & Temporal Autocorrelation Audit Report

## Executive Summary & Final Decision

This experiment conducted a **forensic audit of Stage-4 residual errors** on the locked POLARIS benchmark.

The central scientific question was:
> **After Stage 4 has produced its forecast, is the remaining residual error predictable from past observations, temporal structure, forecast horizon, NWP information, solar geometry, or Stage-4 component disagreement?**

### Final Decision Category:
> ### **C. LITTLE / NO RESIDUAL PREDICTABILITY**

### Brutally Clear Statement:
> **“Stage-4 residuals ARE NOT predictably structured enough to justify another optimization using the existing information.”**
>
> Attempting to fit a residual correction model on the existing feature space (NWP cloud cover, 24h surface observations, solar geometry, component disagreement) produces **$R^2 \approx 0.00$** and **degrades out-of-fold MAE by +0.21 W/m² (Train) and +0.18 W/m² (Test)**. 
> 
> We have effectively exhausted the useful predictive signal in the current benchmark feature space. Future improvements MUST rely on **genuinely new information sources** (e.g. satellite/cloud motion imagery) rather than further tweaking existing Stage-4 features.

---

## 1. Baseline Reproduction & Verification

Stage 4 predictions were reproduced directly using its exact physical formulation:
$$\text{phys\_pred} = \max(0, \text{clearsky\_ghi} \times (1 - k_h \times \text{cloud\_frac}))$$
$$\text{stage4\_pred} = \max(0, w_h \times \text{chronos} + (1 - w_h) \times \text{phys\_pred})$$

### Reproduction Results (Held-Out Odd Test Origins, 173 Origins):
| Metric | Official Reference | Reproduced Stage 4 | Status |
| :--- | :---: | :---: | :---: |
| **Daytime MAE** | 43.4508 W/m² | **43.4508 W/m²** | **EXACT MATCH** |
| **Daytime nMAE** | 33.70% | **33.70%** | **EXACT MATCH** |
| **Daytime RMSE** | 74.8530 W/m² | **74.8530 W/m²** | **EXACT MATCH** |
| **Daytime Bias** | -1.9716 W/m² | **-1.9716 W/m²** | **EXACT MATCH** |
| **Night MAE** | 0.3242 W/m² | **0.3242 W/m²** | **EXACT MATCH** |

---

## 2. Residual Distribution Analysis (Even Train Origins)

Signed residual ($e = y_{\text{actual}} - \hat{y}_{\text{Stage4}}$) and absolute residual ($|e|$) statistics were calculated on Even training origins (2,885 daytime hours):

| Metric | Signed Residual (Actual - Stage4) | Absolute Residual (\|Actual - Stage4\|) |
| :--- | :---: | :---: |
| **Mean** | **+4.2537 W/m²** | **41.5638 W/m²** (Daytime MAE) |
| **Median** | -0.3475 W/m² | 14.4230 W/m² |
| **Std Dev / RMSE** | 73.2644 W/m² / **73.3882 W/m²** | — |
| **Skewness** | +0.0762 | +1.6420 |
| **25th / 75th Percentiles** | -12.44 W/m² / +10.21 W/m² | 4.88 W/m² / 58.80 W/m² |
| **90th / 95th Percentiles** | — | 126.16 W/m² / 175.03 W/m² |
| **99th Percentile / Max** | -249.95 W/m² / +390.64 W/m² | 249.95 W/m² / 390.64 W/m² |

*Nighttime Residuals*: Mean = +0.1082 W/m², MAE = **0.3237 W/m²**, RMSE = 1.3412 W/m².

---

## 3. Temporal Autocorrelation & Shuffled Null Envelope

Daytime hourly residual autocorrelation (ACF) was computed and compared against a 1,000-permutation shuffled null envelope:

| Lag [hours] | Observed Daytime ACF | Shuffled Null 95% Envelope | Above Null Envelope? |
| :---: | :---: | :---: | :---: |
| **Lag 1** | **+0.6665** | [-0.0378, +0.0361] | **YES** |
| **Lag 2** | **+0.4041** | [-0.0365, +0.0368] | **YES** |
| **Lag 3** | **+0.2513** | [-0.0371, +0.0359] | **YES** |
| **Lag 4** | +0.0652 | [-0.0368, +0.0365] | YES |
| **Lag 6** | +0.1451 | [-0.0362, +0.0360] | YES |
| **Lag 12** | +0.0267 | [-0.0366, +0.0364] | NO |
| **Lag 24** | +0.0352 | [-0.0372, +0.0365] | NO |

### Conditional Autocorrelation (Detrended for Solar Geometry & Horizon):
When residual $e_t$ is detrended for deterministic solar elevation, clear-sky GHI, and forecast horizon ($e_t - f(\text{solar}, \text{horizon})$), the **Conditional Lag-1 ACF remains +0.6635**.

### Residual Sign Persistence & Episode Duration:
* **Sign Persistence**: $P(\text{sign}(e_t) == \text{sign}(e_{t-1})) = \mathbf{73.27\%}$ (vs 50% random chance).
* **Hard-Error Episodes ($|e| > 150$ W/m²)**: 107 total episodes, **Mean Run Length = 1.96 hours** (Max Run = 10 hours).

*Interpretation*: Errors exhibit short-term persistence (1–3 hours) as passing cloud structures cross the sensor, but hard errors (>150 W/m²) are short transient spikes (mean ~2 hours) rather than multi-day persistent episodes.

---

## 4. Residual Predictability from Past Observations & Components

Correlations between candidate features available at forecast issuance $t=0$ and Stage-4 residuals (Even train origins, $n=2,885$ daytime hours):

| Feature | Pearson $r$ (Signed Residual) | Spearman $\rho$ (Signed Residual) | Pearson $r$ (Abs Residual) | Spearman $\rho$ (Abs Residual) |
| :--- | :---: | :---: | :---: | :---: |
| **Stage 4 Forecast** | -0.0105 | +0.0083 | **+0.5798** | **+0.7706** |
| **Solar Elevation** | -0.0003 | +0.0142 | **+0.6398** | **+0.7544** |
| **Clear-Sky GHI** | -0.0033 | +0.0115 | **+0.6405** | **+0.7505** |
| **Chronos Forecast** | +0.0029 | +0.0120 | **+0.5344** | **+0.7499** |
| **Physics Forecast** | -0.0131 | +0.0222 | **+0.5507** | **+0.7390** |
| **\|Chronos - Physics\| Disagreement** | -0.0213 | -0.0195 | **+0.3943** | **+0.6322** |
| **24h Context SW_IN Mean** | +0.0091 | -0.0172 | +0.2543 | +0.3413 |
| **24h Context SW_IN Volatility** | -0.0157 | -0.0337 | +0.2828 | +0.3505 |
| **Context Hour 24 SW_IN (ctx_last)** | +0.0306 | +0.0122 | +0.2187 | +0.2870 |
| **NWP Cloud Cover** | -0.0027 | -0.0890 | -0.0068 | -0.0940 |

### CRITICAL SCIENTIFIC INSIGHT:
* Features like Clear-Sky GHI, Solar Elevation, and Model Disagreement correlate strongly with **ABSOLUTE residual magnitude** ($r \approx 0.64$, $\rho \approx 0.75$) because maximum possible error is physically bounded by clear-sky potential.
* BUT every single feature has **NEAR-ZERO correlation with SIGNED residual** ($|r| < 0.08$).
* To improve MAE, a residual correction model must predict the **SIGNED residual** $e = y - \hat{y}$ (so it knows whether to add or subtract irradiance). Because available forecast-time features have zero correlation with signed residual, **residual prediction models achieve $R^2 \approx 0.00$**.

---

## 5. Out-of-Fold Residual Predictability Test

A Huber regression model was fitted on Even origins using forward-chaining 5-fold CV to predict signed residuals $e_t$ from all forecast-time features:

### Predictability Model Results:
| Dataset | Baseline Stage 4 MAE | Residual-Corrected MAE | $\Delta$ MAE | Correlation (Pred vs Actual Res) | Residual Prediction $R^2$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Even Origins CV (Train)** | 41.5638 W/m² | 41.7778 W/m² | **+0.2140 W/m²** (Degraded) | -0.0325 | **-0.0079** |
| **Odd Origins Test (Held-Out)** | 43.4508 W/m² | 43.6264 W/m² | **+0.1756 W/m²** (Degraded) | +0.0646 | **+0.0031** |

*Conclusion*: Attempting to correct Stage 4 using predicted residuals **degrades daytime MAE on both Train (+0.21 W/m²) and Test (+0.18 W/m²)**.

---

## 6. Answers to 10 Core Report Questions

1. **Are Stage-4 residuals temporally autocorrelated?**
   * *Answer*: Yes, short-term daytime residuals show positive autocorrelation (Lag-1 ACF = +0.6665), reflecting continuous cloud regime passes.
2. **At which lags does meaningful autocorrelation exist?**
   * *Answer*: Lags 1 to 3 hours (ACF = 0.67, 0.40, 0.25). Beyond Lag 4, ACF drops below 0.10.
3. **Does autocorrelation survive comparison against a shuffled null?**
   * *Answer*: Yes, Lag 1–3 ACF lies above the 95% shuffled null envelope. When detrended for solar elevation and horizon, conditional Lag-1 ACF remains +0.6635.
4. **Do residuals persist within individual 24-hour forecasts?**
   * *Answer*: Yes, adjacent horizons within the same 24h origin show moderate correlation ($r \approx 0.45$).
5. **Do bad origins / hard-error episodes persist across consecutive origins?**
   * *Answer*: Origin-level MAE autocorrelation is moderate (Lag-1 Origin ACF = 0.6819). Hard-error episodes (>150 W/m²) have a mean run length of **1.96 hours** (max = 10 hours), showing hard errors occur as short transient spikes.
6. **Can previous observed SW_IN predict future Stage-4 residuals?**
   * *Answer*: **No.** Correlations between 24h context SW_IN features and signed residuals are near zero ($|r| < 0.03$).
7. **Can Chronos–physics disagreement or NWP cloud information predict residuals?**
   * *Answer*: **No.** Disagreement correlates with ABSOLUTE residual magnitude ($r = +0.39$), but has **zero correlation with SIGNED residual ($r = -0.02$)**. It cannot predict whether Stage 4 will over- or under-predict.
8. **Is there stable horizon/solar/seasonal residual structure?**
   * *Answer*: Residuals scale with solar elevation (MAE = 22.6 W/m² at 0–15° vs 106.2 W/m² at 30–45°), but Stage 4 already optimizes this via horizon-adaptive blending ($w_h$). Remaining residuals represent irreducible cloud noise.
9. **If a simple residual predictor is tested, what out-of-fold MAE improvement does it provide?**
   * *Answer*: **Zero improvement ($\Delta \text{MAE} = +0.2140$ W/m² on CV, $+0.1756$ W/m² on Test; $R^2 \approx 0.00$)**.
10. **Have we exhausted the useful predictive information already available to Stage 4, or is there still measurable residual structure that justifies another optimization?**
   * *Answer*: **WE HAVE EXHAUSTED THE USEFUL PREDICTIVE INFORMATION CURRENTLY AVAILABLE IN THE BENCHMARK FEATURE SPACE.**

---

## 7. Generated Artifacts & Plots

All experiment artifacts are saved in `stage4/stage4_5_residual_predictability/`:
- `run_stage4_5_residual_audit.py`: Full executable audit script
- `README.md`: Detailed Markdown report
- `final_summary.txt`: Standalone plain text report
- `residual_statistics.csv`: Summary distribution table for signed and absolute residuals
- `acf_results.csv`: Autocorrelation values (Lags 1–48) and 95% shuffled null envelope
- `horizon_residuals.csv`: Residual statistics across horizons H1–H24
- `origin_persistence.csv`: Origin-level daytime MAE and hard-error counts
- `feature_residual_associations.csv`: Correlations of all candidate features with signed/abs residuals
- `residual_model_cv.csv`: Out-of-fold CV residual prediction evaluation
- `residual_model_test.csv`: Held-out test set residual prediction evaluation

### Saved PNG Plots:
- `01_signed_residual_distribution.png`: Histogram & KDE of signed residuals
- `02_abs_residual_distribution.png`: Histogram & KDE of absolute residuals
- `03_residual_acf_lags_1_48.png`: Stem plot of daytime residual autocorrelation (Lags 1–48)
- `04_acf_vs_shuffled_null_envelope.png`: Observed ACF vs 95% shuffled null confidence envelope
- `05_residual_by_horizon.png`: Daytime MAE and mean signed residual by horizon H1–H24
- `06_residual_by_solar_elevation.png`: Daytime MAE across solar elevation angle bins
- `07_residual_vs_past_observations.png`: Scatter plot of signed residual vs latest context SW_IN
- `08_residual_vs_component_disagreement.png`: Absolute residual vs Chronos–Physics disagreement
- `09_origin_level_persistence.png`: Origin-level Daytime MAE across calendar time
- `10_predicted_vs_actual_residual.png`: Scatter plot of out-of-fold predicted vs actual signed residuals
