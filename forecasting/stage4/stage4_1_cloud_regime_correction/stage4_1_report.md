# POLARIS Stage 4.1 — Experiment Report

> **Stage 4.1: Cloud-Regime-Conditioned Amplitude Correction**  
> **Verdict: REJECT**

---

## A. Exact Method Implemented

Per-cloud-regime isotonic regression (Pool Adjacent Violators algorithm).

For each of 5 cloud regimes (classified by NWP `fc_cloud_cover` forecast):
- **Clear (0–10%)**: 352 training daytime hours
- **Few (10–30%)**: 266 training daytime hours  
- **Scattered (30–60%)**: 317 training daytime hours
- **Broken (60–80%)**: 346 training daytime hours
- **Overcast (80–100%)**: 1,604 training daytime hours

One monotonic isotonic mapping was fitted: `ensemble_prediction → corrected_prediction`.

## B. Exact Training Data Used

- **Training origins**: 174 even-indexed forecast origins (locked split)
- **Training rows**: 2,885 daytime hours only
- **Target**: `actual_SW_IN` (training split only)
- **Input feature**: `pred_ensemble` (Stage 4 prediction)
- **Regime classification**: `fc_cloud_cover` from NWP forecast

## C. Leakage Confirmation

✅ Test `actual_SW_IN` was **never** used during fitting.  
✅ Cloud regime classification uses NWP forecast, not actual observations.  
✅ Isotonic parameters were frozen after training, before any test evaluation.  
✅ No hyperparameter was adjusted after inspecting test results.  
✅ No alternative methods were tried or selected based on test performance.

## D. Calibration Parameters

Saved to [`calibration_parameters.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/calibration_parameters.json).

| Regime | N Train | Linear Slope | Linear Intercept | Train MAE Before | Train MAE After |
|:---|:---:|:---:|:---:|:---:|:---:|
| Clear (0–10%) | 352 | 0.9626 | +7.84 | 35.67 | 32.49 |
| Few (10–30%) | 266 | 0.9117 | +14.82 | 47.20 | 41.72 |
| Scattered (30–60%) | 317 | 1.0813 | +4.78 | 42.78 | 37.83 |
| Broken (60–80%) | 346 | 1.1132 | +6.25 | 52.78 | 46.43 |
| Overcast (80–100%) | 1,604 | 0.9786 | +5.96 | 39.26 | 36.72 |

> [!WARNING]
> All regimes show **positive intercepts** (+5 to +15 W/m²), meaning the isotonic calibration systematically shifts predictions upward. This is a response to the positive residual bias in training data but **does not generalize** to the test set.

## E. Stage 4 vs Stage 4.1 — Test Set Metrics

| Metric | Stage 4 (Test) | Stage 4.1 (Test) | Δ |
|:---|---:|---:|---:|
| **Overall MAE** | 30.270 W/m² | 31.679 W/m² | **+1.409 W/m²** |
| **Overall RMSE** | 62.375 W/m² | 64.306 W/m² | **+1.931 W/m²** |
| **Daytime MAE** | 43.451 W/m² | 45.215 W/m² | **+1.764 W/m²** |
| **Daytime RMSE** | 74.853 W/m² | 77.166 W/m² | **+2.313 W/m²** |
| **Daytime nMAE** | 33.70% | 35.07% | **+1.37 pp** |
| **Daytime nRMSE** | 58.06% | 59.85% | **+1.79 pp** |
| **Daytime Bias** | -1.972 W/m² | **+10.580 W/m²** | **+12.552 W/m²** |
| **Nighttime MAE** | 0.324 W/m² | 0.927 W/m² | **+0.603 W/m²** |

> [!CAUTION]
> **Every primary metric worsened on the test set.** Daytime MAE increased by +1.76 W/m², nMAE increased by +1.37 pp, and bias shifted dramatically from -2.0 to +10.6 W/m². The correction is **not generalizing**.

### Train/Test Gap (Overfitting Signal)

| Model | Train nMAE | Test nMAE | Gap |
|:---|:---:|:---:|:---:|
| Stage 4 | 32.27% | 33.70% | 1.43 pp |
| Stage 4.1 | 30.87% | 35.07% | **4.20 pp** |

The train/test gap **tripled** from 1.43 pp to 4.20 pp — a clear overfitting signature.

## F. High-Solar Comparison (Test, actual > 500 W/m²)

| Metric | Stage 4 | Stage 4.1 | Δ |
|:---|---:|---:|---:|
| N test hours | 173 | 173 | — |
| Mean actual | 585.97 W/m² | 585.97 W/m² | — |
| Mean prediction | 470.64 W/m² | 485.57 W/m² | +14.93 W/m² |
| **MAE** | 119.10 W/m² | **103.26 W/m²** | **-15.84 W/m²** |
| **Bias** | -115.33 W/m² | **-100.40 W/m²** | **+14.93 W/m²** |

Also for actual > 300 W/m² (n=455): MAE **102.58 → 89.45** (Δ = -13.13 W/m²).

> [!NOTE]
> The **only area of genuine improvement** is high-solar events, where the amplitude compression was partially corrected. However, this gain is more than offset by degradation elsewhere.

## G. Cloud-Regime Comparison (Test, Daytime)

| Regime | N | Stage 4 MAE | Stage 4.1 MAE | Δ MAE | Stage 4 Bias | Stage 4.1 Bias |
|:---|:---:|---:|---:|---:|---:|---:|
| Clear (0–10%) | 447 | 31.83 | 34.64 | **+2.81** ⚠️ | -0.67 | +2.27 |
| Few (10–30%) | 238 | 48.55 | 51.79 | **+3.23** ⚠️ | -3.11 | +4.42 |
| Scattered (30–60%) | 406 | 53.92 | 53.27 | -0.65 | -8.02 | +16.20 |
| Broken (60–80%) | 396 | 44.55 | 48.15 | **+3.60** ⚠️ | -13.64 | +16.16 |
| Overcast (80–100%) | 1,396 | 42.94 | 44.30 | **+1.36** ⚠️ | +2.87 | +11.08 |

**4 out of 5 cloud regimes degraded.** Only scattered showed marginal improvement (-0.65 W/m²). Bias shifted positive across all regimes.

## H. Horizon Comparison (Test, Daytime)

| H | N | Stage 4 MAE | Stage 4.1 MAE | Δ | Degraded? |
|:---:|:---:|---:|---:|---:|:---:|
| H1 | 56 | 4.57 | 3.95 | -0.62 | |
| H2 | 63 | 7.35 | 7.57 | +0.21 | |
| H3 | 74 | 13.54 | 13.40 | -0.14 | |
| H4 | 87 | 20.30 | 22.78 | +2.47 | ⚠️ |
| H5 | 99 | 32.84 | 32.72 | -0.12 | |
| H6 | 115 | 38.48 | 38.08 | -0.39 | |
| H7 | 132 | 49.45 | 53.01 | +3.56 | ⚠️ |
| H8 | 145 | 54.04 | 54.69 | +0.65 | |
| H9 | 170 | 56.93 | 57.46 | +0.54 | |
| H10 | 173 | 66.42 | 67.25 | +0.83 | |
| H11 | 173 | 77.15 | 74.66 | -2.49 | ✓ |
| H12 | 173 | 77.51 | 74.31 | -3.19 | ✓ |
| H13 | 173 | 61.84 | 63.99 | +2.14 | ⚠️ |
| H14 | 173 | 63.21 | 69.37 | **+6.17** | ⚠️ |
| H15 | 173 | 54.61 | 56.70 | +2.09 | ⚠️ |
| H16 | 158 | 51.58 | 56.55 | **+4.97** | ⚠️ |
| H17 | 144 | 35.28 | 38.96 | +3.68 | ⚠️ |
| H18 | 126 | 24.70 | 27.91 | +3.21 | ⚠️ |
| H19 | 111 | 16.35 | 21.03 | **+4.68** | ⚠️ |
| H20 | 96 | 11.99 | 16.91 | **+4.92** | ⚠️ |
| H21 | 82 | 8.27 | 12.00 | +3.73 | ⚠️ |
| H22 | 71 | 5.74 | 9.04 | +3.31 | ⚠️ |
| H23 | 61 | 2.92 | 3.87 | +0.95 | |
| H24 | 55 | 3.01 | 3.65 | +0.64 | |

**12 out of 24 horizons degraded by >1.0 W/m².** The worst degradation is at afternoon/evening horizons H14–H22 (Δ = +3 to +6 W/m²), where the isotonic calibration's upward bias shift is most damaging because actual irradiance is declining.

## I. Season/Month Comparison (Test, Daytime)

| Season | N | Stage 4 MAE | Stage 4.1 MAE | Δ MAE |
|:---|:---:|---:|---:|---:|
| DJF | 310 | 10.60 | **9.86** | -0.73 ✓ |
| MAM | 916 | 46.28 | 47.17 | +0.88 ⚠️ |
| JJA | 1,075 | 60.05 | 62.16 | **+2.11** ⚠️ |
| SON | 582 | 25.84 | 29.68 | **+3.84** ⚠️ |

Only DJF (winter, low irradiance) improved marginally. JJA and SON degraded substantially.

## J. Pathological Predictions

- **Negative predictions**: 0 ✓
- **Predictions > 1.5× clearsky GHI**: 157 (mostly at low solar elevations where clearsky GHI is small)
- **Predictions > 2.0× clearsky GHI**: 75 (all at low clearsky GHI values 10–25 W/m², where the ratio is inflated by a small denominator — the actual prediction values of 30–60 W/m² are not unreasonable)
- **Night predictions shifted upward**: mean 0.324 → 0.920 W/m² (the isotonic mappings learn a positive intercept that leaks into nighttime hours with nonzero Stage 4 predictions)
- **Max corrected prediction**: 633.67 W/m² (max actual = 745.87 W/m²) — not pathological

## K. Leakage Assessment

✅ No target leakage during fitting.  
✅ No test-set model selection.  
✅ No hyperparameter tuning on test data.  
⚠️ However, the calibration **overfits to training data** — the regime-specific isotonic mappings learn noise patterns in 266–352 sample regimes that do not transfer.

## L. Scientific Interpretation

The experiment reveals an important finding: **per-cloud-regime isotonic calibration overfits** on this dataset.

**Root cause of failure**: The isotonic regression with only 266–352 training daytime samples per regime (except overcast with 1,604) memorizes the specific amplitude relationship in the training origins. Because the interleaved holdout means adjacent days alternate between train and test, weather-regime persistence creates **systematically different bias profiles** in training vs test within the same cloud-regime bin. The isotonic calibration learns the training-specific bias (which happens to be more negative on average) and overcorrects on the test set (which has different bias characteristics).

**Why high-solar improved but everything else worsened**: The training data's positive-residual high-solar events are common enough that the isotonic upward correction at the high end of the prediction range is directionally correct. But the same upward correction gets applied to moderate and low predictions within each regime, introducing a +10.6 W/m² positive bias shift across all conditions.

**Key insight**: The amplitude compression problem is real, but it cannot be fixed by a static per-regime calibration with this sample size and split design. A correction that is **specifically conditioned on prediction amplitude** (not just cloud regime) would be needed, but this requires more careful parameterization to avoid the same overfitting problem.

---

## M. Recommendation

### **REJECT**

The cloud-regime-conditioned isotonic calibration:

1. **Worsens** test daytime MAE by +1.76 W/m² (33.70% → 35.07% nMAE)
2. **Degrades** 12 out of 24 horizons by >1 W/m²
3. **Degrades** 4 out of 5 cloud regimes
4. **Triples** the train/test gap (1.43 pp → 4.20 pp), indicating overfitting
5. **Shifts** daytime bias from -2.0 to +10.6 W/m² (massive overcorrection)
6. **Corrupts** nighttime predictions (mean 0.324 → 0.920 W/m²)

The high-solar improvement (-15.84 W/m² MAE) is real but is overwhelmed by degradation elsewhere.

**Stage 4 remains the locked baseline. Stage 4.1 is rejected.**

---

## Artifacts

All saved to [`stage4_1_cloud_regime_correction/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/):

- [`run_stage4_1.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/run_stage4_1.py) — implementation script
- [`calibration_parameters.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/calibration_parameters.json) — fitted parameters
- [`corrected_predictions.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/corrected_predictions.csv) — all predictions
- [`final_metrics.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/final_metrics.csv) — overall metrics
- [`horizon_metrics.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/horizon_metrics.csv) — per-horizon comparison
- [`cloud_regime_metrics.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/cloud_regime_metrics.csv) — per-regime comparison
- [`seasonal_metrics.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/seasonal_metrics.csv) — seasonal comparison
- [`monthly_metrics.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_1_cloud_regime_correction/monthly_metrics.csv) — monthly comparison
