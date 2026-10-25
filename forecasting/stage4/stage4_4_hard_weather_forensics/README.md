# POLARIS Optimization #4 — Hard-Weather Forensics & Predictability Report

## Executive Summary

This forensic experiment investigated **Optimization #4: "Exploit the 8% hard-weather subset"** for the POLARIS benchmark. 

The primary scientific question was:
> **"Can the large Stage-4 forecasting errors (>150 W/m²) be identified using information available AT forecast issuance, BEFORE seeing the future actual observation?"**

### Core Decision & Answer
**NO. There is NOT enough forecast-time signal to justify building a hard-weather specialist or mixture-of-experts model.**

While features like Clear-Sky GHI and Chronos–Physics model disagreement correlate with error magnitude (since maximum possible absolute error is physically bounded by clear-sky irradiance), they **cannot reliably predict WHICH specific hours will experience a severe cloud mismatch vs a passing clear window** before the actual weather occurs. Attempting to deploy a hard-weather specialist model based on forecast-time signals produces a high false-positive rate (>65%), which would degrade performance on normal/easy daytime hours.

---

## A. Reproducibility

The Stage 4 official pipeline was reproduced directly using its physical formulation:
$$\text{phys\_pred} = \max(0, \text{clearsky\_ghi} \times (1 - k_h \times \text{cloud\_frac}))$$
$$\text{stage4\_pred} = \max(0, w_h \times \text{chronos} + (1 - w_h) \times \text{phys\_pred})$$

### Reproduction Results (Held-Out Odd Test Set, 173 Origins):
| Metric | Reference Stage 4 | Reproduced Stage 4 | Discrepancy |
| :--- | :---: | :---: | :---: |
| **Daytime MAE** | 43.45 W/m² | **43.4508 W/m²** | < 0.001 W/m² |
| **Daytime nMAE** | 33.70% | **33.70%** | < 0.01% |
| **Daytime RMSE** | 74.85 W/m² | **74.8530 W/m²** | < 0.001 W/m² |
| **Daytime Bias** | -1.97 W/m² | **-1.9716 W/m²** | < 0.001 W/m² |
| **Night MAE** | 0.32 W/m² | **0.3242 W/m²** | < 0.001 W/m² |

*Status: Exact match confirmed. Baseline reproduction verified.*

---

## B. Error-Tail Statistics & Threshold Analysis

The daytime forecast error distributions were analyzed across four threshold regimes on both Even (train/cal) and Odd (held-out test) origins:

### Threshold Breakdown (Even Train Origins — 2,885 Daytime Hours)
| Threshold | Hours Count | % Daytime Hours | Sub-Regime MAE | MAE Contribution | % Total Abs Error Contributed | Mean Signed Error (Actual - Pred) | Sub-Regime RMSE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **> 50 W/m²** | 815 | 28.25% | 117.47 W/m² | 33.19 W/m² | **79.95%** | +71.18 W/m² | 136.21 W/m² |
| **> 100 W/m²** | 407 | 14.11% | 163.67 W/m² | 23.10 W/m² | **55.70%** | +93.20 W/m² | 179.35 W/m² |
| **> 150 W/m²** | **210** | **7.28%** | **202.94 W/m²** | **14.77 W/m²** | **35.65%** | **+105.88 W/m²** | **215.93 W/m²** |
| **> 200 W/m²** | 92 | 3.19% | 243.10 W/m² | 7.75 W/m² | **18.65%** | +117.84 W/m² | 251.97 W/m² |

### Threshold Breakdown (Odd Test Origins — 2,883 Daytime Hours)
| Threshold | Hours Count | % Daytime Hours | Sub-Regime MAE | MAE Contribution | % Total Abs Error Contributed | Mean Signed Error (Actual - Pred) | Sub-Regime RMSE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **> 50 W/m²** | 808 | 28.03% | 123.68 W/m² | 34.66 W/m² | **79.77%** | +73.45 W/m² | 141.52 W/m² |
| **> 100 W/m²** | 425 | 14.74% | 164.61 W/m² | 24.26 W/m² | **55.83%** | +96.42 W/m² | 179.31 W/m² |
| **> 150 W/m²** | **210** | **7.28%** | **213.87 W/m²** | **15.58 W/m²** | **35.85%** | **+115.82 W/m²** | **219.57 W/m²** |
| **> 200 W/m²** | 106 | 3.68% | 254.04 W/m² | 9.34 W/m² | **21.50%** | +128.56 W/m² | 256.82 W/m² |

### Error-Tail Quantiles & Impact of Error Capping
- **Median Absolute Error**: **16.45 W/m²** on Test (14.42 W/m² on Train)
- **75th Percentile**: **60.86 W/m²** on Test
- **90th Percentile**: **126.37 W/m²** on Test
- **95th Percentile**: **177.32 W/m²** on Test
- **99th Percentile**: **276.88 W/m²** on Test
- **Maximum Error**: **381.41 W/m²** on Test (390.64 W/m² on Train)

If all >150 W/m² errors were eliminated, the daytime MAE on Test would drop from **43.45 W/m² (33.70% nMAE)** down to **27.87 W/m² (~21.6% nMAE)** — a massive potential improvement of **-15.58 W/m² (-12.1pp nMAE)**!

---

## C. Hard-Weather Characteristics

Comparing the 210 hard daytime hours (>150 W/m²) against the 2,675 non-hard daytime hours on Even origins:

| Feature | Hard Cases Mean | Non-Hard Cases Mean | Cohen's d | Pearson r | Spearman ρ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clear-Sky GHI** | 548.0 W/m² | 180.9 W/m² | +1.80 | +0.64 | +0.75 |
| **Solar Elevation** | 34.1° | 11.1° | +1.71 | +0.64 | +0.75 |
| **Stage 4 Forecast** | 325.3 W/m² | 106.3 W/m² | +1.59 | +0.58 | +0.77 |
| **Chronos Forecast** | 322.3 W/m² | 107.3 W/m² | +1.47 | +0.53 | +0.75 |
| **Physics Forecast** | 332.2 W/m² | 124.4 W/m² | +1.38 | +0.55 | +0.74 |
| **\|Chronos - Physics\| Disagreement** | 125.3 W/m² | 59.2 W/m² | +0.84 | +0.39 | +0.63 |
| **24h Context Volatility** | 82.1 W/m² | 59.1 W/m² | +0.63 | +0.28 | +0.35 |
| **NWP Cloud Cover** | 74.4% | 68.7% | +0.16 | -0.01 | -0.09 |

### Testing the "Broken Cloud" Hypothesis
- **NWP Cloud Cover Breakdown of Hard Cases**:
  - Overcast (80–100%): **56.7% of all hard errors** (119 out of 210)
  - Broken (60–80%): **19.1% of all hard errors** (40 out of 210)
  - Scattered (30–60%): **9.1% of all hard errors** (19 out of 210)
  - Few (10–30%): **9.5% of all hard errors** (20 out of 210)
  - Clear (0–10%): **5.7% of all hard errors** (12 out of 210)

- **Solar Elevation Breakdown**:
  - 0–15°: 0.47% hard rate (MAE = 22.60 W/m²)
  - 15–30°: 8.05% hard rate (MAE = 64.27 W/m²)
  - 30–45°: **30.66% hard rate** (MAE = 106.16 W/m²)
  - >45°: **100.0% hard rate** (3/3 hours, MAE = 216.41 W/m²)

*Key Insight*: Over half (56.7%) of hard errors occur when NWP predicts Heavy Overcast (>80%), but actual weather has clear sky breaks. Under high solar elevation (>30°), this leads to massive under-predictions (mean signed error = +105.88 W/m²).

---

## D. Forecast-Time Predictability

While solar elevation and clear-sky GHI strongly correlate with error magnitude ($r \approx 0.64$), **this correlation is trivial/physical rather than predictive**:
- When clear-sky GHI is 50 W/m², the maximum possible error is bounded by 50 W/m².
- When clear-sky GHI is 600 W/m², a cloud cover misforecast can cause a 300+ W/m² error.

High clear-sky GHI is a **necessary condition**, but **not a sufficient condition** for a hard error:
- Out of 489 hours with solar elevation >30°, **152 hours (31%)** produced >150 W/m² errors, while **337 hours (69%)** produced normal/easy errors!

---

## E. Cross-Validation Results

Using forward-chaining 5-fold cross-validation on Even origins (with candidate features: solar elevation, clear-sky GHI, NWP cloud, context volatility/mean/slope, Chronos–Physics disagreement):

| Model | Out-of-Fold ROC-AUC | Out-of-Fold PR-AUC | Out-of-Fold Precision | Out-of-Fold Recall |
| :--- | :---: | :---: | :---: | :---: |
| **Base Rate / Dummy** | 0.5000 | 0.0728 | 0.00% | 0.00% |
| **Shallow Decision Tree (depth=3)** | 0.8622 | 0.2340 | 21.4% | 58.6% |
| **Logistic Regression (L2)** | **0.9044** | **0.3485** | **31.2%** | **74.8%** |

### Held-Out Test Set Performance (Odd Origins):
- **Test ROC-AUC**: **0.9081**
- **Test PR-AUC**: **0.3725**
- **Precision at default 0.5 threshold**: **33.1%**

*Interpretation*: The ROC-AUC (~0.90) appears high because the model easily separates high-sun daytime hours from twilight/low-sun hours. However, the **PR-AUC is only 0.35**, meaning **over 67% of hours flagged as "hard" are false positives**.

---

## F. Scientific Conclusion

**Selected Scientific Conclusion**:
> **Option 3: Little/no evidence; hard errors are likely dominated by irreducible cloud variability.**

Hard errors (>150 W/m²) stem from localized micro-scale cloud dynamics and NWP cloud phase timing errors that cannot be observed 1–24 hours in advance using synoptic NWP or past surface observations.

---

## G. Next Experiment Recommendation

1. **DO NOT build a hard-weather specialist or mixture-of-experts model** using forecast-time features.
2. **DO NOT attempt dynamic regime switching based on cloud cover or model disagreement**.
3. **Future Research Direction**: Explore probabilistic/quantile forecasting or real-time satellite imagery / sky-camera assimilation (if real-time data becomes available at forecast horizon 0), rather than trying to force deterministic switching on uninformative NWP features.

---

## Generated Artifacts

All experiment artifacts are saved in `stage4/stage4_4_hard_weather_forensics/`:
- `run_hard_weather_forensics.py`: Full executable analysis pipeline
- `threshold_summary.csv`: Summary of thresholds (>50, >100, >150, >200 W/m²)
- `feature_associations.csv`: Feature correlation and effect size table
- `classifier_results.csv`: Out-of-fold and test classification metrics
- `per_hour_error_features.csv`: Full per-hour dataset with all features and errors
- `final_summary.txt`: Standalone text summary
- `01_error_distribution.png`: Histogram of signed Stage 4 errors
- `02_error_cdf.png`: Cumulative distribution function of absolute errors
- `03_abs_error_vs_solar_elevation.png`: Error vs Solar Elevation scatter plot
- `04_abs_error_vs_cloud_fraction.png`: Error across NWP Cloud Regimes boxplot
- `05_abs_error_vs_disagreement.png`: Error vs Chronos–Physics Disagreement scatter plot
- `06_abs_error_vs_horizon.png`: Error distribution across H1–H24 horizons
- `07_hard_vs_easy_features.png`: Boxplots of top features (Hard vs Non-Hard)
- `08_threshold_mae_contribution.png`: MAE contribution bar chart by threshold
- `09_classifier_roc_pr_curves.png`: Out-of-fold ROC and Precision-Recall curves
