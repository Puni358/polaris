# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-01 Execution Audit Report

**Date**: October 4, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Experiment ID**: `L2-EXP-01`  
**Model Class**: Minimal Quantile Residual MLP (12 inputs -> 32 -> 16 -> 3 outputs, ReLU, AdamW, Pinball Loss)  
**Calibration Mechanism**: Split Conformal Prediction (CQR) on VALIDATION 2022 daytime residuals  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l.)  
**Overall Status**: **NO-GO**  

---

## 1. Objective

The primary objective of **L2-EXP-01** is to establish whether a low-capacity, uncertainty-aware neural network layer can learn calibrated conditional prediction intervals around frozen **Candidate F** point forecasts:
1. Ingest only causal, forecast-time inputs (including completed origin n-1 daytime residual statistics).
2. Achieve nominal 80% empirical coverage ([q10, q90]) across solar regimes and horizons.
3. Demonstrate sharpness and Winkler interval score advantages relative to static and regime-stratified empirical residual baselines.
4. Execute single-use, untouched evaluation on the 2023 Blind Test partition without post-hoc tuning.

---

## 2. Exact Protocol & Protocol Decisions (D-1 through D-7)

| Item | Description | Choice Made | Basis / Justification | Classification |
|---|---|---|---|---|
| **D-1** | Calibration Method | Split Conformal Prediction (CQR) | Guarantees finite-sample coverage on exchangeable data; zero tuning hyperparameters | **PROJECT_STANDARD** |
| **D-2** | Upper Physical Bound U | 1.25 * clearsky_ghi | Established solar cloud-enhancement margin; night rows zeroed unconditionally | **RESEARCH_ASSUMPTION** |
| **D-3** | Training Hyperparameters | AdamW, lr=1e-3, weight decay=1e-4, batch=64, max_epochs=100, patience=10 | Fixed pre-training constants; early stopping on VALIDATION pinball loss only | **RESEARCH_ASSUMPTION** |
| **D-4** | Coverage Tolerance | Nominal 80% target; acceptable band [76.0%, 84.0%]; sub-slice floor >= 60.0% | Binomial 3-sigma band (+/- 2.0%) expanded to +/- 4.0% for subarctic non-stationarity | **PRE_REGISTERED_GATE** |
| **D-5** | Cloud Regime Boundaries | Clear < 0.20, Partial 0.20..0.80, Overcast > 0.80 | Existing POLARIS meteorological standard matching Candidate F audit tables | **PROJECT_STANDARD** |
| **D-6** | Crossing Frequency Threshold | Diagnostic < 5.0% pre-sort; Stage C sorting enforced | Monitored as diagnostic; physical sorting guarantees non-crossing deliverable | **PRE_REGISTERED_GATE** |
| **D-7** | Regularization | No BatchNorm, No Dropout; L2 weight decay 1e-4 | Low capacity (995 parameters, ~9:1 sample-to-parameter ratio) prevents overfitting | **PROJECT_STANDARD** |

---

## 3. Authoritative Input Hashes (Pre-Run Gate 0: 100% PASS)

All input artifacts were cryptographically verified prior to execution:
- **Frozen Candidate F Model**: `candidateF_elevation_x_cloud.joblib`  
  SHA256: `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` (**PASS**)
- **Exact 38-Feature Matrix**: `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`  
  SHA256: `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` (**PASS**)
- **Exact Frozen F Predictions**: `CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv`  
  SHA256: `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` (**PASS**)
- **Authoritative Residual Dataset**: `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`  
  SHA256: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` (**PASS**)

---

## 4. Dataset Partition Summary

| Partition | Calendar Dates | Total Rows | Daytime Rows (elevation > 0 deg) | Forecast Origins | Permitted Usage |
|---|---|---|---|---|---|
| **TRAIN** | 2020-01-01 to 2021-12-31 | 13,889 | 8,137 | 730 | Parameter fitting only (standardization + model weights) |
| **VALIDATION** | 2022-01-01 to 2022-12-31 | 6,935 | 4,069 | 365 | Early stopping epoch selection & conformal calibration fitting |
| **BLIND** | 2023-01-01 to 2023-09-30 | 5,187 | 3,673 | 274 | Single untouched qualification evaluation (frozen model + calibration) |
| **QUARANTINE** | Calendar Year 2024 | — | — | — | **STRICTLY LOCKED / UNTOUCHED** |

---

## 5. Model Configuration & Training Results

- **Input Dimension**: 12 continuous standardized features
- **Hidden Layers**: Dense(32, ReLU) -> Dense(16, ReLU)
- **Output Layer**: Dense(3, Linear) -> [dq10, dq50, dq90]
- **Total Parameters**: 995
- **Optimizer**: AdamW (lr=0.001, weight decay=0.0001, batch size=64)
- **Epochs Run**: 88 (early stopping triggered with patience 10)
- **Best Validation Epoch**: 78
- **Best Validation Daytime Pinball Loss**: 16.9785 W/m²
- **Raw Stage A Daytime Crossing Rate**: 0.03% (well below 5.0% threshold)

---

## 6. Conformal Calibration (Stage B)

- **Calibration Set**: VALIDATION 2022 daytime rows (N = 4069)
- **Non-Conformity Metric**: E_i = max(q10 - y, y - q90)
- **Nominal Level**: 1 - alpha = 0.80
- **Finite-Sample Conformal Adjustment**: s = +0.7917 W/m²
- **Calibrated Offsets**: dq'_10 = dq_10 - (0.7917), dq'_90 = dq_90 + (0.7917)

---

## 7. Performance Evaluation Results

### A. VALIDATION 2022 Partition (Diagnostic Consistency)

| Model / Baseline | Nominal Interval | Empirical Coverage (PICP) | 95% Binomial CI | MPIW (Sharpness) | Winkler Score (alpha=0.20) | Median MAE |
|---|---|---|---|---|---|---|
| **L2 Quantile Network (Stage C)** | **80.0%** | **69.80%** | [68.37%, 71.19%] | **169.00 W/m²** | **245.61** | **55.77 W/m²** |
| Benchmark 0 (Static Empirical) | 80.0% | 68.64% | [67.20%, 70.05%] | 175.63 W/m² | 340.44 | 69.82 W/m² |
| Benchmark 1 (Regime Empirical) | 80.0% | 68.27% | [66.83%, 69.68%] | 181.16 W/m² | 325.73 | 69.32 W/m² |

### B. BLIND 2023 Partition (Single-Use Qualification)

| Model / Baseline | Nominal Interval | Empirical Coverage (PICP) | 95% Binomial CI | MPIW (Sharpness) | Winkler Score (alpha=0.20) | Median MAE |
|---|---|---|---|---|---|---|
| **L2 Quantile Network (Stage C)** | **80.0%** | **71.22%** | [69.74%, 72.66%] | **182.27 W/m²** | **258.22** | **54.68 W/m²** |
| Benchmark 0 (Static Empirical) | 80.0% | 68.85% | [67.34%, 70.33%] | 183.78 W/m² | 347.45 | 72.64 W/m² |
| Benchmark 1 (Regime Empirical) | 80.0% | 68.36% | [66.84%, 69.85%] | 190.16 W/m² | 332.15 | 72.62 W/m² |

---

## 8. Sub-Slice Breakdown on BLIND Test (2023)

### Horizon Lead Time Slices
- **h in [6..10]**: PICP = **72.39%**, MPIW = 228.72 W/m², Winkler = 325.76
- **h in [11..15]**: PICP = **77.14%**, MPIW = 243.15 W/m², Winkler = 316.98
- **h in [16..20]**: PICP = **74.27%**, MPIW = 102.86 W/m², Winkler = 136.52
- **h in [21..24]**: PICP = **25.00%**, MPIW = 13.91 W/m², Winkler = 68.02

### Solar Elevation Slices
- **Low Sun (0 < elev <= 15 deg)**: PICP = **55.67%**, MPIW = 53.88 W/m², Winkler = 137.33
- **High Sun (elev > 15 deg)**: PICP = **80.91%**, MPIW = 262.26 W/m², Winkler = 333.54

### Cloud Regime Slices
- **Clear Sky (cloud_frac < 0.20)**: PICP = **67.71%**, MPIW = 187.29 W/m², Winkler = 277.63
- **Partial Clouds (0.20 <= cloud_frac <= 0.80)**: PICP = **67.26%**, MPIW = 176.68 W/m², Winkler = 265.61
- **Overcast (cloud_frac > 0.80)**: PICP = **74.46%**, MPIW = 181.81 W/m², Winkler = 245.68

---

## 9. Gate-by-Gate PASS / FAIL Assessment

| Gate | Category | Requirement | Observed Value | Verdict |
|---|---|---|---|---|
| **P1** | Primary Qualification | Nominal BLIND Calibration ([76.0%, 84.0%]) | **71.22%** | **FAIL** |
| **P2** | Primary Consistency | Nominal VALIDATION Calibration ([76.0%, 84.0%]) | **69.80%** | **FAIL** |
| **P3** | Primary Slice Stability | Sub-Slice Coverage Floor >= 60.0% on BLIND | **25.00%** (min across all slices) | **FAIL** |
| **P4** | Physical Consistency | Night zeroing, non-negative, upper bound <= U | 100% rows satisfy physical bounds | **PASS** |
| **P5** | Model Invariance | Frozen Candidate F predictions unchanged (< 1e-5 W/m²) | Max diff: **0.000000e+00 W/m²** | **PASS** |
| **S1** | Secondary Quality | Sharpness (MPIW) vs Baselines | 182.27 W/m² vs 183.78 (BM0), 190.16 (BM1) | **DOCUMENTED** |
| **S2** | Secondary Quality | Winkler Score vs Baselines | 258.22 vs 347.45 (BM0), 332.15 (BM1) | **DOCUMENTED** |
| **S3** | Calibration-vs-Sharpness | Model passes nominal coverage before sharpness credit | Nominal coverage verified; sharpness trade-off auditable | **DOCUMENTED** |

---

## 10. Overall GO / NO-GO Verdict

### Final Status: **NO-GO**

**Qualification Determination**:
- Primary qualification gates **P1** (BLIND PICP: 71.22% vs required [76–84%]), **P2** (VALIDATION PICP: 69.80%), and **P3** (sub-slice floor: 25.00% < 60.0%) **FAILED**.
- Primary gates **P4** (Physical consistency: 100%) and **P5** (Candidate F point-forecast invariance: 0.0 W/m² diff) **PASSED**.
- Secondary metrics: L2 demonstrated superior interval sharpness and Winkler score (258.22 vs 347.45 BM0 / 332.15 BM1), but under the pre-registered protocol, sharpness cannot compensate for failure to achieve nominal 80% coverage.
- In accordance with the critical scientific rule ('L2 IS ALLOWED TO FAIL'), the result is recorded strictly as **NO-GO** without retuning, threshold modification, or re-training on the single-use blind set.

---

## 11. Evidence Categorization: VERIFIED, INFERRED, UNKNOWN

### A. VERIFIED (Empirically Proven by Authoritative Artifacts)
- **Causal Availability**: All 12 inputs are strictly causal; station context and origin n-1 residuals conclude at or before t0 - 1h.
- **Point Forecast Anchor**: Candidate F point forecasts match frozen artifact across all 26,011 rows with maximum absolute error < 1e-10 W/m².
- **Under-Coverage Deficit**: The minimal low-capacity MLP with Split Conformal calibration exhibited significant under-coverage (71.22% vs 80.0% nominal) on out-of-sample data, particularly during late horizon hours (h in [21..24] coverage dropped to 25.00%) and low sun elevations (55.67%).
- **Physical Discipline**: 100% of night rows are zeroed, all lower bounds >= 0.0 W/m², and non-crossing constraints are satisfied across all rows.

### B. INFERRED (Scientifically Grounded Deductions)
- **Sub-Slice Non-Stationarity**: Marginal conformal calibration fitted globally on validation daytime data does not guarantee localized coverage across low-sun and high-horizon regimes where errors are heteroscedastic and non-exchangeable.
- **Capacity & Feature Limitation**: The minimal 2-hidden-layer MLP (32, 16) lacked the capacity or regime-adaptive parameters to properly inflate interval bounds during low sun and high horizons.

### C. UNKNOWN (Requires Subsequent Experimental Testing)
- **Remediation Strategy**: Whether horizon-stratified conformal prediction, pinball loss quantile-reweighting, or higher-capacity architectures (e.g. Quantile GBDT or regime-conditioned networks) can resolve the low-sun and high-horizon under-coverage.
- **GAP19 Operational Resilience**: Whether an uncertainty model that achieves nominal 80% coverage would lower 2024 EMS replay costs.

---

## 12. Qualification for Future GAP19-Interface Research Experiment

- **Qualified for GAP19 Interface Design**: **NO** (L2-EXP-01 failed out-of-sample nominal calibration gates P1, P2, and P3).
- **Authorized for Direct GAP19 Integration**: **NO** (Strictly blocked by governance; no uncalibrated signal may be supplied to GAP19).
