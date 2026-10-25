# POLARIS STAGE 7.5 — FINAL NUMERICAL & GOVERNANCE FORENSIC AUDIT

**Stage:** Stage 7.5 Terrain / Horizon Radiative Geometry Experiment  
**Audit Date:** September 12, 2026  
**Audit Type:** Read-Only Forensic Verification  
**Stage Status:** `STAGE_7_5_CANDIDATE_ACCEPTED` (EVEN-CV Passed / Candidate Frozen)  
**Official Operational Champion:** Stage 6.6 LWP/IWP Model (FROZEN OPERATIONAL CHAMPION)  
**ODD Evaluation Status:** **NOT STARTED** (Requires explicit user authorization)

---

## 1. Executive Forensic Summary

A complete, read-only forensic audit was performed on the Stage 7.5 terrain/horizon forecasting experiment artifacts to verify numerical exactness, baseline reproduction, feature causality, forward-chaining isolation, absence of tuning/result shopping, and five-point ODD access classification.

### Audit Checklist Results
- **Baseline Reproduction**: **PASS** (Control MAE $= 38.280605\text{ W/m}^2$ perfectly reproduced).
- **Candidate Feature Integrity**: **PASS** (35 features total: 31 Stage 6.6 + 4 pre-specified terrain features).
- **Causality Audit**: **PASS** (100% static DEM + deterministic astronomical solar geometry).
- **Forward-Chaining Integrity**: **PASS** (174 EVEN origins across 5 forward-chaining folds).
- **No Tuning / Shopping**: **PASS** (Zero hyperparameter search, feature selection, or post-hoc threshold adjustments).
- **Row-Level Numerical Reconciliation**: **PASS** (All fold-level and aggregate metrics recomputed exactly).
- **Gate Recomputation**: **PASS** (All 5 predeclared EVEN-CV acceptance gates verified passed).
- **ODD Governance Audit**: **PASS** (ODD target, prediction, metric, and tuning access remained locked).

---

## 2. Baseline Reproduction & EVEN-CV Numerical Reconciliation

| Metric | Stage 6.6 Control ($E0$) | Candidate $E1$ | Delta | Gate Threshold | Gate Status |
|---|---|---|---|---|---|
| **Daytime MAE** | $38.280605\text{ W/m}^2$ | $37.835137\text{ W/m}^2$ | $-0.445468\text{ W/m}^2$ | $\le 38.0806\text{ W/m}^2$ | **PASS** (Gate 1) |
| **Daytime nMAE** | $40.3918\%$ | $38.5174\%$ | $-1.8744\text{ pp}$ | $\le 40.3918\%$ | **PASS** (Gate 4) |
| **Daytime RMSE** | $60.750856\text{ W/m}^2$ | $60.307218\text{ W/m}^2$ | $-0.443637\text{ W/m}^2$ | $\le 60.750856\text{ W/m}^2$ | **PASS** (Gate 5) |
| **Daytime Bias** | $+2.419115\text{ W/m}^2$ | $+2.950526\text{ W/m}^2$ | $+0.531411\text{ W/m}^2$ | N/A | Informational |

---

## 3. Five-Fold Forward-Chaining Reconciliation

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Fold Improved? | Degradation Status |
|---|---|---|---|---|---|
| **Fold 1** | 49.817392 | 49.032799 | -0.784593 | **YES** | No Degradation |
| **Fold 2** | 71.077463 | 70.840579 | -0.236883 | **YES** | Worst Improvement (-0.2369 W/m²) |
| **Fold 3** | 41.261951 | 41.020016 | -0.241935 | **YES** | No Degradation |
| **Fold 4** | 26.804209 | 26.114319 | -0.689890 | **YES** | No Degradation |
| **Fold 5** | 2.442011 | 2.167973 | -0.274038 | **YES** | No Degradation |

### Terminology Audit & Gate 3 Clarification
- **Number of Improved Folds**: 5 out of 5 (**Gate 2 PASS**).
- **Number of Degraded Folds**: 0 out of 5.
- **Maximum Single-Fold Degradation**: $0.000000\text{ W/m}^2$ (**Gate 3 PASS**: threshold $\le +0.15\text{ W/m}^2$).
- **Worst Single-Fold Improvement**: $-0.236883\text{ W/m}^2$ (Fold 2).

---

## 4. Five-Point ODD Access & Governance Classification

- `odd_feature_accessed`: **TRUE** (Static DEM terrain feature rows were extracted across all 347 origins during common feature preparation).
- `odd_target_accessed`: **FALSE** (SITES actual SW_IN targets for the 173 ODD test origins were NEVER loaded, read, or evaluated).
- `odd_predictions_generated`: **FALSE** (Zero ODD predictions generated).
- `odd_metrics_evaluated`: **FALSE** (Zero ODD performance metrics calculated).
- `odd_used_for_tuning`: **FALSE** (Zero ODD data used for model training, feature selection, or hyperparameter tuning).

*Governance Rule*: ODD target, prediction, metric, and tuning access remained locked.

---

## 5. Official Project Status & Next Steps

- **Stage 7.5 Candidate Status**: **EVEN-CV PASSED / CANDIDATE FROZEN**. Candidate $E1$ (35 features) passed all five predeclared EVEN-CV acceptance gates.
- **Operational Champion Status**: **STAGE 6.6 LWP/IWP MODEL REMAINS FROZEN OPERATIONAL CHAMPION** (ODD Daytime MAE $= 37.005888\text{ W/m}^2$).
- **ODD Evaluation Authorization**: **NOT STARTED**. Explicit user authorization is required before evaluating the candidate on held-out ODD origins.
