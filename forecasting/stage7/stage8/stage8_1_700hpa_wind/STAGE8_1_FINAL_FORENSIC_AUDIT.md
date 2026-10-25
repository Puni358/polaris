# POLARIS STAGE 8.1 — FINAL NUMERICAL & GOVERNANCE FORENSIC AUDIT

**Stage:** Stage 8.1 700 hPa Free-Atmosphere Steering Wind Experiment  
**Audit Date:** September 12, 2026  
**Audit Type:** Read-Only Forensic Verification  
**Stage Status:** `EVEN_CV_PASSED_CANDIDATE_FROZEN`  
**Official Operational Champion:** Stage 7.5 Terrain Model (FROZEN OPERATIONAL CHAMPION)  
**ODD Evaluation Status:** **NOT STARTED** (Requires explicit user authorization)

---

## 1. Executive Forensic Summary

A complete, read-only forensic audit was performed on the Stage 8.1 steering wind experiment artifacts and source code to verify numerical exactness, baseline reproduction, feature causality, forward-chaining isolation, absence of tuning/result shopping, and nine-point governance classification.

### Audit Checklist Results
- **Numerical Audit**: **PASS** (Control MAE $= 38.280605\text{ W/m}^2$, Candidate MAE $= 37.620054\text{ W/m}^2$, $\Delta\text{MAE} = -0.660552\text{ W/m}^2$ verified).
- **Feature Audit**: **PASS** (Exact 37 features: 35 Stage 7.5 frozen features + $U_{700} + V_{700}$; zero forbidden features).
- **Data Source Audit**: **PASS** (MEPS pressure-level archive `meps_det_pl`, 700 hPa, $y=760, x=486$).
- **Causality Audit**: **PASS** (100% $D-1\ 18Z$ MEPS deterministic forecast, $t_{\text{ref}} < t_0$ for 347/347 origins).
- **Completeness / Integrity Audit**: **PASS** (347 origins, 24 horizons, 8,328 rows, 0 NaNs, 0 Infs, 0 duplicates, 0 fill-value violations).
- **Model Audit**: **PASS** (Exact frozen `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`).
- **CV Methodology Audit**: **PASS** (5-fold forward-chaining EVEN CV only; locked even/odd split preserved).
- **ODD Access Forensics**: **PASS** (Target: NO, Predictions: NO, Metrics: NO, Tuning: NO).
- **Result-Shopping Audit**: **PASS** (Single predeclared candidate $U_{700} + V_{700}$; zero feature shopping or tuning).
- **Artifact Audit**: **PASS** (All 9 required stage8_1 artifacts present and verified).
- **Gate Audit**: **PASS** (All 5 predeclared EVEN-CV gates passed).
- **Documentation**: **PASS** (Conservative scientific wording enforced; no overclaiming).
- **Overall Integrity**: **PASS**

---

## 2. Baseline Reproduction & EVEN-CV Numerical Reconciliation

| Metric | Stage 6.6/7.5 Control ($E0$) | Candidate $E1$ ($U_{700}+V_{700}$) | Delta | Gate Threshold | Gate Status |
|---|---|---|---|---|---|
| **Daytime MAE** | $38.280605\text{ W/m}^2$ | $37.620054\text{ W/m}^2$ | $-0.660552\text{ W/m}^2$ | $\le 38.080605\text{ W/m}^2$ | **PASS** (Gate 1) |
| **Daytime nMAE** | $40.3918\%$ | $37.9745\%$ | $-2.4173\text{ pp}$ | $\le 40.3918\%$ | **PASS** (Gate 4) |
| **Daytime RMSE** | $60.750856\text{ W/m}^2$ | $60.160645\text{ W/m}^2$ | $-0.590210\text{ W/m}^2$ | $\le 60.750856\text{ W/m}^2$ | **PASS** (Gate 5) |
| **Daytime Bias** | $+2.419115\text{ W/m}^2$ | $+2.950526\text{ W/m}^2$ | $+0.531411\text{ W/m}^2$ | N/A | Informational |

---

## 3. Five-Fold Forward-Chaining Fold Reconciliation

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Fold Improved? | Gate 3 Status |
|---|---|---|---|---|---|
| **Fold 1** | 49.817392 | 49.311394 | -0.505998 | **YES** | PASS |
| **Fold 2** | 71.077463 | 70.568822 | -0.508641 | **YES** | PASS |
| **Fold 3** | 41.261951 | 40.345638 | -0.916313 | **YES** | PASS |
| **Fold 4** | 26.804209 | 25.770355 | -1.033854 | **YES** | PASS |
| **Fold 5** | 2.442011 | 2.104085 | -0.337926 | **YES** | PASS |

- **Number of Improved Folds**: 5 out of 5 (**Gate 2 PASS**: threshold $\ge 4/5$).
- **Maximum Single-Fold Degradation**: $-0.337926\text{ W/m}^2$ (Zero degraded folds, **Gate 3 PASS**: threshold $\le +0.15\text{ W/m}^2$).

---

## 4. ODD Access & Governance Classification

- `odd_target_accessed`: **NO** (SITES actual SW_IN targets for the 173 ODD test origins were NEVER loaded or evaluated).
- `odd_feature_accessed`: **YES** (Static feature extraction across all 347 origins during common data preparation).
- `odd_predictions_generated`: **NO** (Zero ODD predictions generated).
- `odd_metrics_evaluated`: **NO** (Zero ODD performance metrics calculated).
- `odd_used_for_tuning`: **NO** (Zero ODD data used for training or tuning).

---

## 5. Conservative Scientific Statement

Stage 8.1 showed a robust EVEN forward-chaining improvement from adding 700 hPa free-atmosphere $U/V$ wind to the frozen Stage 7.5 feature set. The candidate improved all five validation folds ($\Delta\text{MAE} = -0.660552\text{ W/m}^2$) and passed all five predeclared acceptance gates. This provides evidence that the 700 hPa wind contains additional predictive information under the benchmark, consistent with its role as a free-atmosphere steering-flow proxy. It does not by itself establish that the variable directly measures cloud motion or advection.
