# POLARIS Stage 4.2 — Experiment Report

> **Stage 4.2: Per-Horizon Regularized Affine Recalibration**  
> **Verdict: REJECT**

---

## A. Implementation Status

✅ Complete. Script executed, all artifacts saved.

## B. Output Directory

[`stage4/stage4_2_horizon_affine/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_2_horizon_affine/)

## C. Stage 4 vs Stage 4.2 — Test Set (Odd Origins)

| Metric | Stage 4 | Stage 4.2 | Δ | Direction |
|:---|---:|---:|---:|:---:|
| Overall MAE | 30.270 W/m² | 31.591 W/m² | **+1.321** | ⚠️ Worse |
| Overall RMSE | 62.375 W/m² | 62.251 W/m² | -0.124 | ≈ Same |
| **Daytime MAE** | **43.451 W/m²** | **44.081 W/m²** | **+0.630** | **⚠️ Worse** |
| Daytime RMSE | 74.853 W/m² | 74.642 W/m² | -0.211 | ≈ Same |
| **Daytime nMAE** | **33.70%** | **34.19%** | **+0.49 pp** | **⚠️ Worse** |
| Daytime nRMSE | 58.06% | 57.89% | -0.16 pp | ≈ Same |
| Daytime bias | -1.972 W/m² | +2.729 W/m² | +4.700 | Shifted positive |
| **Night MAE** | **0.324 W/m²** | **3.215 W/m²** | **+2.891** | **⚠️ Much worse** |

N daytime = 2,883 · N nighttime = 1,269 · Daytime mean actual = 128.93 W/m²

## D. H1–H24 Comparison

| H | N | S4 MAE | S4.2 MAE | Δ MAE | S4 Bias | S4.2 Bias |
|:---:|:---:|---:|---:|---:|---:|---:|
| H1 | 56 | 4.57 | 4.22 | -0.34 | -2.86 | -1.26 |
| H2 | 63 | 7.35 | 7.37 | +0.01 | -3.64 | -0.12 |
| H3 | 74 | 13.54 | 14.78 | **+1.24** ⚠️ | -6.22 | +0.85 |
| H4 | 87 | 20.30 | 23.71 | **+3.41** ⚠️ | -2.16 | +8.87 |
| H5 | 99 | 32.84 | 35.62 | **+2.79** ⚠️ | -3.69 | +7.93 |
| H6 | 115 | 38.48 | 39.92 | **+1.44** ⚠️ | -13.09 | +2.92 |
| H7 | 132 | 49.45 | 50.46 | **+1.01** ⚠️ | -2.96 | +7.60 |
| H8 | 145 | 54.04 | 53.75 | -0.29 | -6.65 | +1.05 |
| H9 | 170 | 56.93 | 58.40 | **+1.47** ⚠️ | -11.61 | +0.19 |
| H10 | 173 | 66.42 | 67.28 | +0.86 | -6.48 | +3.07 |
| **H11** | 173 | 77.15 | **75.98** | **-1.17** ✓ | -17.88 | -8.19 |
| H12 | 173 | 77.51 | 78.62 | **+1.12** ⚠️ | -18.57 | -16.15 |
| H13 | 173 | 61.84 | 62.21 | +0.36 | -4.62 | -3.08 |
| H14 | 173 | 63.21 | 63.02 | -0.19 | +17.40 | +16.94 |
| H15 | 173 | 54.61 | 55.42 | +0.81 | +11.61 | +14.07 |
| H16 | 158 | 51.58 | 51.84 | +0.27 | +13.84 | +14.81 |
| H17 | 144 | 35.28 | 35.85 | +0.57 | +7.05 | +9.70 |
| H18 | 126 | 24.70 | 25.08 | +0.38 | +4.01 | +1.72 |
| H19 | 111 | 16.35 | 16.85 | +0.50 | +2.72 | +0.73 |
| H20 | 96 | 11.99 | 13.05 | **+1.06** ⚠️ | -0.67 | -1.43 |
| H21 | 82 | 8.27 | 8.51 | +0.25 | +0.98 | -0.60 |
| H22 | 71 | 5.74 | 5.86 | +0.13 | -1.00 | -1.66 |
| H23 | 61 | 2.92 | 2.99 | +0.07 | -1.73 | -0.70 |
| H24 | 55 | 3.01 | 2.86 | -0.16 | -1.57 | -0.67 |

**Improved (Δ < -0.5): 1** (H11 only)  
**Unchanged (|Δ| ≤ 0.5): 12**  
**Degraded (Δ > +0.5): 11**

## E. Leakage / Split Verification

| Check | Status |
|:---|:---:|
| 174 even-origin training origins | ✅ |
| 173 odd-origin test origins | ✅ |
| No origin overlap | ✅ |
| 24 horizons | ✅ |
| Parameters fitted on train only | ✅ |
| No NaNs in predictions | ✅ |
| No negative predictions (after clip) | ✅ |
| Original pred_ensemble unchanged (max_diff = 0.0) | ✅ |
| Stage 4 w_h/k_h unchanged | ✅ |
| No Chronos retraining | ✅ |
| No future actual_SW_IN used as feature | ✅ |
| λ = 0.7 fixed (not tuned) | ✅ |
| 48 calibration parameters (24 × 2) | ✅ |

Train/test gap: Stage 4 gap = 1.43 pp, Stage 4.2 gap = 1.85 pp (modest increase, not alarming).

## F. Decision

### **REJECT Stage 4.2**

Both primary criteria failed:
- Daytime MAE: **worsened** by +0.63 W/m² (43.45 → 44.08)
- Daytime nMAE: **worsened** by +0.49 pp (33.70% → 34.19%)

Additionally:
- Only **1 out of 24** horizons improved meaningfully
- **11 out of 24** horizons degraded
- Night MAE increased **10×** (0.32 → 3.21 W/m²)
- Bias shifted from -1.97 to +2.73 W/m² (overcorrection)

## G. Stage 4 Remains Locked

**Stage 4 is the final champion for this benchmark cycle.**

| Metric | Value |
|:---|---:|
| Daytime MAE | 43.292 W/m² |
| Daytime nMAE | 33.70% |
| Daytime RMSE | 74.453 W/m² |

## H. Scientific Interpretation

Both post-hoc calibration experiments have now failed:

| Experiment | Method | Test Daytime MAE | Verdict |
|:---|:---|---:|:---:|
| Stage 4 | Locked ensemble | 43.292 W/m² | **Champion** |
| Stage 4.1 | Per-cloud-regime isotonic | 45.215 W/m² (+1.92) | Rejected |
| Stage 4.2 | Per-horizon affine (λ=0.7) | 44.081 W/m² (+0.63) | Rejected |

**Why Stage 4.2 failed**: The OLS slopes at early horizons (H1–H6) are 1.18–1.93, meaning the fitted calibration amplifies small predictions substantially. After regularization (λ=0.7), these become 1.13–1.44 — still amplifying. At late horizons (H17–H22), slopes of 0.62–0.87 compress predictions further. The problem is that these corrections improve bias on training data but **the bias patterns do not transfer cleanly to the test set** — the same horizon has different bias characteristics on even vs odd origins due to weather variability.

The 636 negative predictions (clipped to 0) and the nighttime MAE explosion (0.32 → 3.21) reveal that the affine corrections, particularly the positive intercepts at H17–H22, shift nighttime predictions away from zero.

**Broader conclusion**: The remaining Stage 4 error (~34% nMAE) appears to be dominated by **intrinsic weather forecast uncertainty** — the difference between NWP-forecast cloud cover and actual cloud transmittance at each hour. This is not addressable by recalibrating existing predictions, because the calibration-exploitable signal (horizon-dependent bias) is too small and too variable relative to the weather-driven noise. Further improvement would require either (a) better NWP inputs (higher-resolution cloud forecasts, cloud optical depth rather than cloud fraction), or (b) a fundamentally different modeling approach.
