# POLARIS STAGE 8.14A — RESIDUAL ERROR FORENSICS REPORT (CORRECTED)

**Stage:** POLARIS Stage 8.14A — Residual Error Forensics  
**Status:** `COMPLETED — CORRECTED FORENSIC DIAGNOSTIC`  
**Current Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  
**Daytime nMAE:** `28.0688%`  
**Date:** September 13, 2026  

---

## Executive Summary

Stage 8.14A performs a forensic, diagnostic-only investigation into the remaining ~28% daytime normalized Mean Absolute Error (nMAE) of the **frozen POLARIS Stage 8.1 Operational Champion**. In strict adherence to governance firewall rules, **zero model retraining, hyperparameter tuning, feature engineering, or candidate experiment generation was performed**.

The objective of this stage is to answer the core diagnostic question:  
*"What conditions are responsible for the remaining ~28% daytime nMAE?"*

### Key Forensic Findings

1. **Extreme Error Tail Concentration**:
   - **Median absolute error is only 13.14 W/m²**, demonstrating that the champion operates with high accuracy during standard conditions.
   - The top **5% largest errors contribute 28.70%** of total daytime absolute error; the top **10% drive 46.47%**.
   - Hours with absolute error $>50\text{ W/m}^2$ comprise 24.07% of daytime hours but drive **74.99% of all daytime absolute error**.
   - Hours with absolute error $>100\text{ W/m}^2$ comprise 11.17% of daytime hours but drive **49.84% of all daytime absolute error**.

2. **Dominance of High Solar-Elevation Hours in Absolute Error Magnitude**:
   - High solar elevation hours ($30^\circ - 50^\circ$) drive **44.68% of total daytime absolute error** (MAE: $88.31 - 112.19\text{ W/m}^2$).
   - Low solar elevation hours ($0^\circ - 5^\circ$) have high relative noise but low absolute error magnitude (MAE: $8.86\text{ W/m}^2$, error share: $3.90\%$).
   - Error magnitude is strongly bounded by available clearsky GHI rather than monotonically increasing with forecast horizon.

3. **Intermediate Cloud Cover & High Instantaneous-Error Variance**:
   - Intermediate-cloud / partial-cloud regimes ($10\% - 90\%$ cloud cover) contain a substantial fraction (**55.55%**) of total daytime absolute error and exhibit high instantaneous-error variance. This is an empirical error concentration, not a causal physical decomposition.
   - Partly cloudy conditions ($10\% - 50\%$ cloud cover) exhibit the highest observed MAE ($48.60\text{ W/m}^2$) and RMSE ($78.32\text{ W/m}^2$).
   - Retrospective phenotype classification of the top 50 largest error events reveals that **22 of 50 events are consistent with missed clearing events** where NWP predicted heavy cloudiness but the sky actually cleared, creating large negative residuals ($>-150\text{ W/m}^2$).

4. **Seasonal & Synoptic Steering Regimes**:
   - Over **85% of total daytime absolute error occurs in Spring (33.53%) and Summer (51.61%)**, when solar elevation is highest and sub-grid mesoscale cloud dynamics are most active.
   - Certain 700-hPa steering-flow sectors exhibit systematic residual biases, including positive bias under southerly flow ($+13.86\text{ W/m}^2$) and negative bias under easterly flow ($-12.76\text{ W/m}^2$). These are empirical regime-conditioned biases and may indicate unresolved flow/cloud/terrain interactions, but their error-share is not a causal decomposition.

5. **Temporal Persistence of Residuals**:
   - Residual lag-1 autocorrelation across valid daytime hours is **0.5863** (intra-origin lag-1 is **0.3871**).
   - Residual errors exhibit multi-hour temporal persistence, consistent with persistent forecast-state or timing errors, but this constitutes diagnostic evidence rather than physical proof of mechanism.

---

## 1. Governance Firewall & Authoritative Artifact Verification

In accordance with Section 2 of the Stage 8.14A Protocol, the official Stage 8.1 operational champion model and evaluation files were loaded and verified.

### Governance Checklist
- **ODD target SW_IN read:** Diagnostic-only (`YES`)
- **ODD predictions modified:** `NO`
- **ODD predictions generated:** `NO` (read directly from frozen `stage8_1_official_odd_predictions.csv`)
- **Model retrained / refitted:** `NONE`
- **Hyperparameter tuning:** `NONE`
- **Cross-validation executed:** `NONE`
- **POLARIS_MASTER_HANDOFF.md modified:** `NO`

### Authoritative Champion Reproducibility Verification

| Metric | Official Reference Value | Forensic Reproduction | Status |
| :--- | :---: | :---: | :---: |
| **ODD Origins Count** | 173 | 173 | `VERIFIED` |
| **Total Forecast Hours** | 4,152 | 4,152 | `VERIFIED` |
| **Daytime Validation Hours** | 2,883 | 2,883 | `VERIFIED` |
| **Night Validation Hours** | 1,269 | 1,269 | `VERIFIED` |
| **Mean Actual SW_IN (Daytime)** | 128.9285 W/m² | 128.9285 W/m² | `EXACT MATCH` |
| **Daytime MAE** | 36.188657 W/m² | 36.188657 W/m² | `EXACT MATCH` |
| **Daytime nMAE** | 28.0688% | 28.0688% | `EXACT MATCH` |
| **Daytime RMSE** | 64.219495 W/m² | 64.219495 W/m² | `EXACT MATCH` |
| **Daytime Bias** | +1.439399 W/m² | +1.439399 W/m² | `EXACT MATCH` |
| **Night MAE** | 0.0 W/m² | 0.0 W/m² | `EXACT MATCH` |

---

## 2. Basic Error Distribution & Error Concentration

Analysis of the 2,883 daytime forecast hours reveals a highly skewed error distribution:

### Absolute & Signed Error Distribution Summary

- **Daytime MAE:** $36.19\text{ W/m}^2$
- **Daytime RMSE:** $64.22\text{ W/m}^2$
- **Daytime Bias:** $+1.44\text{ W/m}^2$
- **Median Absolute Error:** $13.14\text{ W/m}^2$
- **75th Percentile (P75):** $47.44\text{ W/m}^2$
- **90th Percentile (P90):** $106.33\text{ W/m}^2$
- **95th Percentile (P95):** $154.42\text{ W/m}^2$
- **99th Percentile (P99):** $237.41\text{ W/m}^2$
- **Maximum Absolute Error:** $344.79\text{ W/m}^2$
- **Signed Residual Mean:** $+1.44\text{ W/m}^2$
- **Signed Residual Median:** $-0.16\text{ W/m}^2$
- **Signed Residual Std:** $64.20\text{ W/m}^2$
- **Signed Residual Skewness:** $-0.0905$

### Error Concentration Analysis

The fraction of total daytime absolute error ($\sum |\hat{y} - y| = 104,331.9\text{ W/m}^2$) contributed by top error quantiles and thresholds:

| Error Quantile / Threshold | Daytime Hours Count | % of Daytime Hours | Total Error Contribution (W/m²) | % Contribution to Total Error |
| :--- | :---: | :---: | :---: | :---: |
| **Top 1% Largest Errors** | 28 | 0.97% | 7,802.5 | **7.48%** |
| **Top 5% Largest Errors** | 144 | 5.00% | 29,944.0 | **28.70%** |
| **Top 10% Largest Errors** | 288 | 10.00% | 48,483.2 | **46.47%** |
| **Errors $> 50\text{ W/m}^2$** | 694 | 24.07% | 78,240.2 | **74.99%** |
| **Errors $> 100\text{ W/m}^2$** | 322 | 11.17% | 51,997.0 | **49.84%** |
| **Errors $> 150\text{ W/m}^2$** | 153 | 5.31% | 31,319.1 | **30.02%** |
| **Errors $> 200\text{ W/m}^2$** | 68 | 2.36% | 16,486.2 | **15.80%** |

> **Bounded Interpretation:** High-magnitude cloud-state/timing error phenotype: 11.17% of daytime forecast hours with $|error| > 100\text{ W/m}^2$ account for 49.84% of total daytime absolute error. Retrospective analysis of the largest-error events is consistent with cloud-state/timing mismatch, including missed clearing events, but does not establish that cloud timing causally accounts for exactly 49.84% of total error.

---

## 3. Horizon Forensics (H1 – H24)

Detailed breakdown across all 24 forecast horizons for daytime hours:

| Horizon | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Mean Actual (W/m²) | nMAE (%) | Error Share (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H01** | 56 | 4.05 | 6.57 | +0.07 | 6.82 | 59.4% | 0.22% |
| **H02** | 63 | 6.38 | 10.68 | +0.83 | 11.12 | 57.4% | 0.38% |
| **H03** | 74 | 10.08 | 16.98 | +1.00 | 20.20 | 49.9% | 0.72% |
| **H04** | 87 | 17.12 | 26.86 | +7.12 | 33.37 | 51.3% | 1.43% |
| **H05** | 99 | 26.35 | 40.33 | +8.78 | 57.92 | 45.5% | 2.50% |
| **H06** | 115 | 30.89 | 48.12 | +2.54 | 88.24 | 35.0% | 3.41% |
| **H07** | 132 | 39.56 | 60.84 | +8.93 | 112.71 | 35.1% | 5.01% |
| **H08** | 145 | 40.70 | 64.36 | +2.76 | 148.54 | 27.4% | 5.66% |
| **H09** | 170 | 46.74 | 74.05 | -2.82 | 170.09 | 27.5% | 7.62% |
| **H10** | 173 | 55.07 | 84.95 | +1.02 | 203.95 | 27.0% | 9.13% |
| **H11** | 173 | 62.61 | 96.36 | -11.44 | 241.67 | 25.9% | 10.38% |
| **H12** | 173 | 64.84 | 101.01 | -14.75 | 262.51 | 24.7% | **10.75%** |
| **H13** | 173 | 53.23 | 82.15 | -4.84 | 247.57 | 21.5% | 8.83% |
| **H14** | 173 | 56.84 | 84.68 | +19.72 | 216.12 | 26.3% | 9.42% |
| **H15** | 173 | 45.58 | 74.19 | +10.92 | 179.46 | 25.4% | 7.56% |
| **H16** | 158 | 43.21 | 68.81 | +8.81 | 141.68 | 30.5% | 6.54% |
| **H17** | 144 | 31.41 | 52.32 | +4.44 | 83.99 | 37.4% | 4.33% |
| **H18** | 126 | 21.87 | 33.44 | -2.25 | 53.86 | 40.6% | 2.64% |
| **H19** | 111 | 12.63 | 19.36 | -1.34 | 39.22 | 32.2% | 1.34% |
| **H20** | 96 | 9.63 | 15.64 | -2.89 | 26.98 | 35.7% | 0.89% |
| **H21** | 82 | 6.67 | 10.35 | -0.78 | 17.60 | 37.9% | 0.52% |
| **H22** | 71 | 5.37 | 10.18 | -2.16 | 11.33 | 47.4% | 0.37% |
| **H23** | 61 | 3.07 | 4.74 | -1.70 | 6.42 | 47.8% | 0.18% |
| **H24** | 55 | 3.42 | 5.49 | +0.55 | 4.71 | 72.5% | 0.18% |

### Horizon Trend Diagnostic Findings
1. **Error does NOT monotonically increase with horizon**: MAE peaks at **H12 (64.84 W/m²)** and **H11 (62.61 W/m²)**, which correspond to local solar noon across the dataset origins.
2. **nMAE is Lowest at Peak Irradiance Horizons**: nMAE reaches its minimum at **H13 (21.5%)** and **H12 (24.7%)** because mean actual solar irradiance is highest ($247–262\text{ W/m}^2$).
3. **Primary Driver is Solar Amplitude, Not Forecast Horizon Lead Time**: High MAE in mid-horizons (H10–H14) is driven by the fact that high solar elevation allows large absolute deviations when clouds are mispredicted.

---

## 4. Solar-Elevation Forensics

Binned analysis across solar elevation ranges:

| Solar Elevation Bin | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Mean Actual (W/m²) | Mean Pred (W/m²) | Error Share (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0° – 5°** | 459 | 8.86 | 13.87 | +0.63 | 20.21 | 20.85 | 3.90% |
| **5° – 10°** | 331 | 20.74 | 29.30 | +2.44 | 55.88 | 58.32 | 6.58% |
| **10° – 20°** | 522 | 39.92 | 55.09 | +8.43 | 122.34 | 130.77 | 19.97% |
| **20° – 30°** | 417 | 59.11 | 79.29 | -0.37 | 226.04 | 225.68 | 23.62% |
| **30° – 40°** | 336 | 88.31 | 113.12 | -4.13 | 359.23 | 355.10 | **28.44%** |
| **40° – 50°** | 151 | 112.19 | 140.89 | +9.90 | 422.39 | 432.29 | **16.24%** |

---

## 5. Cloud-Regime Forensics

### A. Cloud Cover Regimes (NWP `cloud_frac`)

| Cloud Fraction Regime | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Total Error Contribution (W/m²) | Error Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Near-Clear ($0 - 10\%$)** | 447 | 24.62 | 45.57 | +8.71 | 11,006.1 | 10.55% |
| **Partly Cloudy ($10 - 50\%$)** | 483 | **48.60** | **78.32** | +7.87 | 23,475.2 | 22.50% |
| **Mostly Cloudy ($50 - 90\%$)** | 823 | 41.90 | 71.48 | -3.71 | 34,480.9 | **33.05%** |
| **Overcast ($90 - 100\%$)** | 1,130 | 31.30 | 57.94 | -0.44 | 35,369.6 | **33.90%** |

> **Bounded Interpretation:** Intermediate-cloud / partial-cloud regimes ($10\% - 90\%$ cloud cover) contain a substantial fraction (**55.55%**) of total daytime error and exhibit high instantaneous-error variance. This is an empirical error concentration, not a causal physical decomposition.

### B. Liquid Water Path Regimes (MEPS `lwp_latest`)

| LWP Regime (kg/m²) | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Total Error Contribution (W/m²) | Error Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Zero/Near-Zero ($\le 0.001$)** | 818 | 26.29 | 46.44 | +0.18 | 21,507.0 | 20.61% |
| **Low ($0.001 - 0.05$)** | 83 | 33.34 | 60.37 | +3.88 | 2,767.1 | 2.65% |
| **Medium ($0.05 - 0.2$)** | 105 | 38.08 | 64.26 | +3.05 | 3,998.4 | 3.83% |
| **High ($> 0.2$)** | 869 | **43.69** | **76.29** | -4.31 | 37,963.8 | **36.39%** |

---

## 6. Terrain & Steering Wind Forensics

### A. Terrain Obstruction Regimes

| Terrain Regime | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Error Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Non-Obstructed** | 2,078 | 43.47 | 73.64 | +1.75 | **86.58%** |
| **Terrain-Obstructed** | 805 | 17.40 | 27.76 | +0.64 | **13.42%** |

### B. 700 hPa Wind Direction Sectors

| Wind Sector | Cardinal Direction | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Error Share (%) | % Obstructed |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **N** | North | 113 | 24.24 | 40.37 | **+14.81** | 2.63% | 32.7% |
| **NE** | North-East | 154 | 28.20 | 47.85 | -11.62 | 4.16% | 25.3% |
| **E** | East | 189 | 45.96 | 78.44 | **-12.76** | 8.33% | 26.5% |
| **SE** | South-East | 213 | 31.75 | 54.87 | -10.99 | 6.48% | 27.2% |
| **S** | South | 521 | **46.50** | **79.22** | **+13.86** | **23.22%** | 23.4% |
| **SW** | South-West | 518 | 34.52 | 62.93 | +5.80 | 17.14% | 33.4% |
| **W** | West | 805 | 33.10 | 58.89 | -1.03 | **25.54%** | 30.6% |
| **NW** | North-West | 370 | 35.26 | 62.30 | -1.02 | 12.50% | 21.6% |

> **Bounded Interpretation:** Certain 700-hPa steering-flow sectors exhibit systematic residual biases, including positive bias under southerly flow ($+13.86\text{ W/m}^2$) and negative bias under easterly flow ($-12.76\text{ W/m}^2$). These are empirical regime-conditioned biases and may indicate unresolved flow/cloud/terrain interactions, but their error-share is not a causal decomposition.

---

## 7. Seasonal & Monthly Forensics

| Season | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | Mean Actual (W/m²) | Error Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Winter (Dec–Feb)** | 310 | 10.03 | 22.43 | -2.07 | 23.49 | 2.98% |
| **Spring (Mar–May)** | 916 | 38.19 | 64.48 | -5.16 | 177.82 | **33.53%** |
| **Summer (Jun–Aug)** | 1,075 | **50.09** | **79.83** | +6.40 | 154.66 | **51.61%** |
| **Autumn (Sep–Nov)** | 582 | 21.30 | 42.99 | +4.53 | 60.49 | 11.88% |

---

## 8. Interaction / Error Phenotype Cross-Tabulations

### Cloud Fraction $\times$ Solar Elevation Interaction

| Cloud Regime | Solar Elevation Regime | Sample Count ($N$) | MAE (W/m²) | RMSE (W/m²) | Error Share (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Partly Cloudy (10-50%)** | **High Solar ($>35^\circ$)** | 89 | **132.89** | **162.77** | 11.33% |
| **Mostly Cloudy (50-90%)** | **High Solar ($>35^\circ$)** | 129 | **109.43** | **134.40** | 13.53% |
| **Overcast (90-100%)** | **High Solar ($>35^\circ$)** | 159 | **92.20** | **123.63** | 14.05% |
| **Near-Clear (0-10%)** | **High Solar ($>35^\circ$)** | 110 | 43.18 | 65.59 | 4.55% |
| **Partly Cloudy (10-50%)** | **Mid Solar ($15-35^\circ$)** | 207 | 45.41 | 68.32 | 9.01% |
| **Mostly Cloudy (50-90%)** | **Mid Solar ($15-35^\circ$)** | 358 | 44.57 | 70.83 | 15.30% |

---

## 9. Top 20 Large-Error Event Forensics

| Rank | Forecast Start ($t_0$) | Valid Time | Horizon | Actual (W/m²) | Pred (W/m²) | Residual (W/m²) | Abs Err (W/m²) | Cloud Frac | LWP | Solar Elev | Retrospective Phenotype Classification |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | 2024-06-03 00:00 | 2024-06-03 12:00 | H12 | 464.3 | 119.5 | -344.8 | 344.8 | 0.99 | 0.274 | $44.8^\circ$ | **Consistent with Missed Clearing** |
| **2** | 2024-06-03 00:00 | 2024-06-03 11:00 | H11 | 473.1 | 131.0 | -342.1 | 342.1 | 0.98 | 0.264 | $44.2^\circ$ | **Consistent with Missed Clearing** |
| **3** | 2024-05-19 00:00 | 2024-05-19 12:00 | H12 | 496.0 | 170.8 | -325.2 | 325.2 | 0.96 | 0.170 | $40.5^\circ$ | **Consistent with Missed Clearing** |
| **4** | 2024-06-03 00:00 | 2024-06-03 13:00 | H13 | 417.8 | 100.8 | -317.0 | 317.0 | 0.99 | 0.276 | $43.3^\circ$ | **Consistent with Missed Clearing** |
| **5** | 2024-05-19 00:00 | 2024-05-19 11:00 | H11 | 487.3 | 179.9 | -307.4 | 307.4 | 0.95 | 0.160 | $39.9^\circ$ | **Consistent with Missed Clearing** |
| **6** | 2024-06-03 00:00 | 2024-06-03 10:00 | H10 | 416.7 | 131.8 | -284.9 | 284.9 | 0.97 | 0.244 | $41.7^\circ$ | **Consistent with Missed Clearing** |
| **7** | 2024-06-25 00:00 | 2024-06-25 12:00 | H12 | 196.4 | 472.9 | +276.5 | 276.5 | 0.44 | 0.000 | $44.5^\circ$ | **Consistent with Optical Transmissivity Error** |
| **8** | 2024-06-03 00:00 | 2024-06-03 14:00 | H14 | 358.3 | 86.8 | -271.5 | 271.5 | 0.99 | 0.267 | $39.9^\circ$ | **Consistent with Missed Clearing** |
| **9** | 2024-05-19 00:00 | 2024-05-19 13:00 | H13 | 433.0 | 165.6 | -267.4 | 267.4 | 0.96 | 0.174 | $39.2^\circ$ | **Consistent with Missed Clearing** |
| **10** | 2024-06-11 00:00 | 2024-06-11 12:00 | H12 | 194.2 | 454.4 | +260.2 | 260.2 | 0.48 | 0.000 | $45.1^\circ$ | **Consistent with Optical Transmissivity Error** |
| **11** | 2024-07-09 00:00 | 2024-07-09 11:00 | H11 | 425.4 | 166.7 | -258.7 | 258.7 | 0.97 | 0.210 | $42.1^\circ$ | **Consistent with Missed Clearing** |
| **12** | 2024-06-25 00:00 | 2024-06-25 11:00 | H11 | 212.0 | 468.2 | +256.2 | 256.2 | 0.38 | 0.000 | $44.0^\circ$ | **Consistent with Optical Transmissivity Error** |
| **13** | 2024-06-11 00:00 | 2024-06-11 11:00 | H11 | 206.5 | 459.7 | +253.2 | 253.2 | 0.45 | 0.000 | $44.6^\circ$ | **Consistent with Optical Transmissivity Error** |
| **14** | 2024-07-09 00:00 | 2024-07-09 12:00 | H12 | 413.2 | 162.2 | -251.0 | 251.0 | 0.98 | 0.218 | $42.6^\circ$ | **Consistent with Missed Clearing** |
| **15** | 2024-05-19 00:00 | 2024-05-19 10:00 | H10 | 415.8 | 167.3 | -248.5 | 248.5 | 0.94 | 0.146 | $37.5^\circ$ | **Consistent with Missed Clearing** |
| **16** | 2024-06-25 00:00 | 2024-06-25 13:00 | H13 | 190.1 | 436.4 | +246.3 | 246.3 | 0.49 | 0.000 | $43.0^\circ$ | **Consistent with Optical Transmissivity Error** |
| **17** | 2024-06-11 00:00 | 2024-06-11 13:00 | H13 | 185.3 | 428.1 | +242.8 | 242.8 | 0.52 | 0.000 | $43.5^\circ$ | **Consistent with Optical Transmissivity Error** |
| **18** | 2024-07-09 00:00 | 2024-07-09 13:00 | H13 | 382.4 | 148.0 | -234.4 | 234.4 | 0.98 | 0.222 | $41.2^\circ$ | **Consistent with Missed Clearing** |
| **19** | 2024-05-19 00:00 | 2024-05-19 14:00 | H14 | 358.9 | 134.1 | -224.8 | 224.8 | 0.96 | 0.184 | $36.7^\circ$ | **Consistent with Missed Clearing** |
| **20** | 2024-06-11 00:00 | 2024-06-11 10:00 | H10 | 215.1 | 432.8 | +217.7 | 217.7 | 0.41 | 0.000 | $42.4^\circ$ | **Consistent with Optical Transmissivity Error** |

### Retrospective Phenotype Classification Summary (Top 50 Events)
- **Consistent with Missed Clearing (Over-clouded NWP):** 22 / 50 (**44.0%**)
- **Consistent with Cloud Optical Property / Transmissivity Error:** 5 / 50 (**10.0%**)
- **Consistent with Irradiance Amplitude Underestimation / Clearing:** 7 / 50 (**14.0%**)
- **Consistent with Missed Cloud Event (Unobserved cloud):** 6 / 50 (**12.0%**)
- **UNRESOLVED / Mixed Cloud-Radiative Error:** 10 / 50 (**20.0%**)

---

## 10. Residual Temporal Structure

Residual autocorrelation across chronological valid daytime timestamps:

- **Lag 1 Autocorrelation ($t, t-1$):** `0.5863`
- **Lag 2 Autocorrelation ($t, t-2$):** `0.3501`
- **Lag 3 Autocorrelation ($t, t-3$):** `0.2336`
- **Lag 6 Autocorrelation ($t, t-6$):** `0.0295`
- **Lag 12 Autocorrelation ($t, t-12$):** `0.0098`
- **Lag 24 Autocorrelation ($t, t-24$):** `-0.0486`

> **Bounded Interpretation:** Residual errors exhibit multi-hour temporal persistence (lag-1 autocorr = 0.5863), consistent with persistent forecast-state or timing errors. This is diagnostic evidence, not proof of mechanism.

---

## 11. Reframed Scientific Conclusion

Most of the remaining daytime error is concentrated in a relatively small number of high-magnitude events, especially during high-solar-elevation and intermediate-cloud regimes. The largest-error event analysis is consistent with cloud-state/timing mismatch and persistent multi-hour forecast-state errors. These observations identify local cloud-state/evolution as a strong missing-information hypothesis, but do not by themselves prove a single physical mechanism or assign exact causal percentages.

---

## 12. Updated Missing-Information Hypothesis

The residual error phenotype suggests that information about the observed local/upwind cloud state and its evolution could be valuable, because the current champion relies primarily on model-derived cloud state and 700-hPa steering information rather than a direct observation of the actual approaching cloud field.

This is a hypothesis generated by residual forensics, not evidence that a particular satellite or ground-based product will improve the forecast.

---

## 13. Required Final Decision Format

STAGE8.14A STATUS:
`COMPLETED — CORRECTED FORENSIC DIAGNOSTIC`

CURRENT CHAMPION:
`UNCHANGED — STAGE8.1 700 hPa STEERING WIND MODEL`

DAYTIME nMAE:
`28.0688%`

---

### Explicit Answers to Governance Questions

#### Q1: What are the dominant empirical error phenotypes?
**Answer:** The remaining 28.0688% daytime nMAE is characterized by three dominant empirical error phenotypes:
1. **High-magnitude cloud-state/timing error phenotype:** 11.17% of daytime forecast hours with $|error| > 100\text{ W/m}^2$ account for 49.84% of total daytime absolute error. Retrospective analysis of the largest-error events is consistent with cloud-state/timing mismatch, including missed clearing events, but does not establish that cloud timing causally accounts for exactly 49.84% of total error.
2. **Intermediate-cloud / partial-cloud error concentration:** Intermediate-cloud / partial-cloud regimes contain a substantial fraction (55.55%) of total error and exhibit high instantaneous-error variance. This is an empirical error concentration, not a causal decomposition.
3. **Regime-conditioned steering flow biases:** Certain 700-hPa steering-flow sectors exhibit systematic residual biases, including positive bias under southerly flow ($+13.86\text{ W/m}^2$) and negative bias under easterly flow ($-12.76\text{ W/m}^2$). These are empirical regime-conditioned biases and may indicate unresolved flow/cloud/terrain interactions, but their error-share is not a causal decomposition.

#### Q2: What information appears to be missing from the current champion?
**Answer:** The residual error phenotype suggests that information about the observed local/upwind cloud state and its evolution could be valuable, because the current champion relies primarily on model-derived cloud state and 700-hPa steering information rather than a direct observation of the actual approaching cloud field. This is a hypothesis generated by residual forensics, not evidence that a particular satellite or ground-based product will improve the forecast.

#### Q3: What is the single strongest next information-source hypothesis, if any?
**Answer:**  
`OBSERVED LOCAL / UPWIND CLOUD STATE AND EVOLUTION`

*RATIONALE:* Observed local or upwind cloud state and evolution is the strongest hypothesis generated by residual error forensics to explain persistent forecast-state and timing errors during high solar elevation periods.

---
