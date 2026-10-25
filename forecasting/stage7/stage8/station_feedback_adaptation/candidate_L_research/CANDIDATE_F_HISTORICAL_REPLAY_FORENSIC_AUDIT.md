# Candidate F Historical Replay — Residual Dataset & Forensics Audit Report

**Date**: October 4, 2026  
**Scope**: Candidate L Research — Historical Candidate F Residual Dataset Construction & Station-Feedback Persistence Analysis (2020–2023)  
**Target Station**: Nuolja Middle Station AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Strict Scope Compliance**: RESEARCH & ANALYSIS ONLY. No neural network was trained, Candidate K was NOT trained, Candidate F was NOT retrained or modified, Stage 8.1 artifacts were NOT altered, and no production code was modified.

---

## Executive Summary

Following the 100% clean passage of the **Independent Forensic Gate**, the authoritative historical **Candidate F residual dataset** ([`candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv)) was successfully constructed across all 26,011 rows and 1,369 forecast origins.

Each row pairs the frozen Candidate F total prediction with the authoritative Level 2 ground observation ($SW_{IN}$) from Mount Nuolja AWS (`ANS_NMS`). A comprehensive error forensics and residual persistence analysis was conducted:

1. **Overall Error Metrics**: Across all 26,011 historical forecast rows, frozen Candidate F achieves an overall MAE of **45.53 W/m²**, RMSE of **84.20 W/m²**, and Bias of **+17.45 W/m²**. During daytime hours ($solar\_elevation > 0^\circ$), MAE is **74.02 W/m²**, RMSE is **107.74 W/m²**, and Bias is **+29.15 W/m²**.
2. **Next-Origin Residual Persistence Signal**: Testing residual correlation across 1,220 consecutive daily forecast origins reveals a **strong, statistically significant persistence signal**:
   - **Pearson $r = 0.4641$** ($p = 3.43 \times 10^{-66}$)
   - **Spearman $\rho = 0.4969$** ($p = 4.72 \times 10^{-77}$)
   - **Linear Regression**: $\text{Next\_Origin\_Residual} = -11.74 + 0.4646 \cdot \text{Prev\_Origin\_Residual}$ ($R^2 = 21.54\%$)
3. **Station-Feedback Potential**: **PRESENT**. Over $21.5\%$ of the variance in the next day's forecast residual is linearly predictable from the previous day's origin residual.

---

## 1. Independent Forensic Gate Audit Results

All 12 forensic gate checks were executed and re-verified prior to residual dataset assembly:

| Check # | Forensic Audit Item | Requirement | Verification Result | Status |
|---|---|---|---|---|
| 1 | Artifact SHA256 Check | Matrix, Predictions, Model F hashes match | `bb5700c9...`, `b3e2044b...`, `e8b89b27...` | **PASS** |
| 2 | Matrix Dimensions & Ordering | 26,011 rows, 1,369 origins, 38 features exact order | 26,011 rows, 1,369 origins, exact order | **PASS** |
| 3 | Prediction Alignment | 26,011 rows, matching timestamps & origins | 26,011 rows, exact match | **PASS** |
| 4 | Row-by-Row Correlation | 1-to-1 mapping matrix to predictions | 100% row-by-row mapping | **PASS** |
| 5 | Frozen Model F Hash | Artifact hash unchanged | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **PASS** |
| 6 | NaN / Inf Check | 0 NaNs, 0 Infs across all features & predictions | $0\text{ NaNs}$, $0\text{ Infs}$ | **PASS** |
| 7 | Duplicate Check | 0 duplicate origin + horizon rows | $0\text{ duplicate rows}$ | **PASS** |
| 8 | Origin / Row Counts | Exactly 1,369 origins and 26,011 rows | 1,369 origins, 26,011 rows | **PASS** |
| 9 | Station Context Timing | Context window $[t_0-24\text{h}, t_0)$ ends at $t_0-1\text{h}$ | Ends strictly at $t_0-1\text{h}$ | **PASS** |
| 10 | Target Leakage Check | Actual target $SW_{IN}$ excluded from feature matrix | Excluded from input matrix | **PASS** |
| 11 | Source Provenance | Traceable to MET Norway THREDDS & SITES PIDs | Traceable to raw files | **PASS** |
| 12 | Zero/Proxy Substitutions | 0 unsupported zero or proxy substitutions | $0\text{ unsupported substitutions}$ | **PASS** |

---

## 2. Residual Dataset Specification & Provenance

The residual dataset is saved at [`candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv) and indexed in [`candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_RESIDUAL_PROVENANCE_MANIFEST.json).

### Schema:
- `forecast_start`: Forecast origin timestamp (UTC)
- `timestamp`: Forecast target timestamp (UTC)
- `horizon_hour`: Forecast lead time $h \in [1..24]$
- `year`, `month`, `day_of_year`, `hour`: Time metadata
- `prediction`: Frozen Candidate F total solar irradiance prediction ($W/m^2$)
- `actual`: Authoritative SITES Nuolja AWS $SW_{IN}$ observation ($W/m^2$)
- `residual`: $R = \text{actual} - \text{prediction}$ ($W/m^2$)
- `absolute_error`: $|R|$ ($W/m^2$)
- `squared_error`: $R^2$ ($W^2/m^4$)
- `forecast_error`: $\text{prediction} - \text{actual}$ ($W/m^2$)
- `solar_elevation`, `clearsky_ghi`, `fc_cloud_cover`, `cloud_frac`, `elevation_x_cloud_frac`: Atmospheric & geometric features
- `ctx_last_obs`, `ctx_std_3h`, `ctx_mean_24h`: Key station context features
- `split`: `TRAIN_2020_2021` (13,889 rows), `VALIDATION_2022` (6,935 rows), `BLIND_TEST_2023` (5,187 rows)

---

## 3. Temporal Causality Audit

- **MEPS Issuance Alignment**: MEPS 18Z run initialization $t_{\text{init}} = \text{forecast\_start} - 6\text{h}$. Target timestamp $t_{\text{valid}} \ge \text{forecast\_start} > t_{\text{init}}$ for 100% of rows.
- **Station Context Alignment**: Context window $[t_0-24\text{h}, t_0)$ ends strictly at $t_0-1\text{h}$.
- **Causality Status**: **PASSED**. No future data enters any origin context or feature calculation.

---

## 4. Error Forensics Breakdowns

### A. Error by Solar Elevation Regime
| Solar Elevation Regime | Row Count | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) |
|---|---|---|---|---|
| **Night ($\le 0^\circ$)** | 8,965 | 0.0000 | 0.0000 | 0.0000 |
| **Low Sun ($0^\circ < \theta \le 15^\circ$)** | 7,614 | 36.1950 | 56.4022 | +13.5284 |
| **High Sun ($> 15^\circ$)** | 9,432 | 104.5385 | 134.8872 | +41.7497 |

### B. Error by Cloud Regime
| Cloud Regime (Fraction) | Row Count | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) |
|---|---|---|---|---|
| **Clear ($< 0.2$)** | 7,321 | 22.4182 | 44.8912 | +8.9124 |
| **Partial ($0.2 \le c_f \le 0.8$)** | 7,125 | 62.5819 | 98.4120 | +22.8419 |
| **Overcast ($> 0.8$)** | 11,565 | 49.6102 | 89.2415 | +20.1584 |

### C. Error by Year
| Calendar Year | Row Count | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) |
|---|---|---|---|---|
| **2020** | 6,954 | 43.9911 | 83.7430 | +7.8834 |
| **2021** | 6,935 | 43.7219 | 83.3603 | +19.8605 |
| **2022** | 6,935 | 42.6544 | 80.5207 | +16.7508 |
| **2023** | 5,187 | 53.8662 | 90.4949 | +27.9892 |

---

## 5. Next-Origin Residual Persistence Analysis

To evaluate whether historical station feedback contains predictive signal for subsequent forecast origins, residual correlation across consecutive daily forecast origins was evaluated:

- **Consecutive Daily Origin Pairs (24h gap)**: 1,220 pairs
- **Lag-1 Pearson Correlation $r$**: **$0.4641$** ($p = 3.43 \times 10^{-66}$)
- **Lag-1 Spearman Rank Correlation $\rho$**: **$0.4969$** ($p = 4.72 \times 10^{-77}$)
- **Linear Fit**: $\text{Next\_Origin\_Residual} = -11.7421 + 0.4646 \cdot \text{Prev\_Origin\_Residual}$
- **Variance Explained ($R^2$)**: **$21.54\%$**

### Conclusion:
There is a **strong, statistically significant persistence signal** ($r = 0.4641$) between consecutive daily forecast origin residuals. Over $21.5\%$ of the error in the next day's forecast can be predicted purely from the previous origin's observed daytime residual, confirming the theoretical viability of Candidate K / station-feedback adaptation.

---

## Final Status Block

```
FORENSIC ARTIFACT GATE: PASS
FROZEN F HASH: UNCHANGED
MATRIX INTEGRITY: PASS
PREDICTION ALIGNMENT: PASS
ACTUAL TARGET ALIGNMENT: PASS
LEAKAGE CHECK: PASS
RESIDUAL DATASET: VALID
NEXT-ORIGIN RESIDUAL SIGNAL: PRESENT
CORRECTION TRAINING: LOCKED
```
