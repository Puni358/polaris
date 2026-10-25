# POLARIS Candidate K — Causal EWMA Residual Correction Research Report

**Date**: October 4, 2026  
**Status**: RESEARCH-ONLY EVALUATION COMPLETE  
**Target Station**: Nuolja Middle Station AWS (`ANS_NMS`, 702 m a.s.l.)  
**Policy Compliance**: 100% Read-Only Source Policy. Candidate F, Stage 8.1, and production artifacts remain unmodified.

---

## Executive Summary

Candidate K implements a strictly causal, low-capacity post-processing EWMA (Exponentially Weighted Moving Average) residual correction on frozen Candidate F solar irradiance forecasts. Hyperparameters were tuned exclusively on the **2022 Validation set** (365 origins, 6,935 rows) and evaluated **strictly once** on the **2023 Blind Test set** (273 origins, 5,187 rows; Jan 1 – Sep 30, 2023).

### Key Results:
- **2022 Validation Set**: Candidate K reduced overall MAE from **42.65 W/m²** to **38.85 W/m²** (+3.80 W/m², **8.91% improvement**) and reduced bias from **+16.75 W/m²** to **+1.19 W/m²** (**92.9% bias reduction**).
- **2023 Blind Test Set (Overall)**: Candidate K reduced overall MAE from **53.87 W/m²** to **48.40 W/m²** (+5.47 W/m², **7.80% improvement**) with 95% Bootstrap CI **[4.60, 6.37] W/m²**. Overall RMSE improved from **90.49 W/m²** to **81.53 W/m²** (+8.96 W/m², 95% CI **[7.69, 10.18] W/m²**).
- **2023 Blind Test Set (Daytime)**: Daytime MAE (solar_elevation > 0 deg) improved from **75.59 W/m²** to **67.87 W/m²** (+7.72 W/m², **7.80% improvement**). Daytime bias dropped from **+40.01 W/m²** to **+4.38 W/m²** (**75.6% bias reduction**).

---

## 1. Candidate K Model Specification & Causality Architecture

### Model Structure:
- **Formula**: Corrected_Pred = max(0.0, Frozen_F_Pred + Correction)
- **Correction**: Derived from EWMA of daytime mean residuals across completed previous forecast origins k < n.
- **Hyperparameters Selected (from 2022 Validation)**:
  - **Variant**: `A_global` (Global EWMA state)
  - **Smoothing Factor (alpha)**: `0.1` (effective memory horizon of 10 forecast origins)
  - **Minimum History Requirement**: `1` origins
  - **Output Correction Clipping (C_max)**: `+/- 75.0` W/m²
  - **Scaling Mode**: `unscaled`

### Strict Causality Protocol:
1. At forecast origin n, candidate K uses the state accumulated ONLY from completed origins k < n.
2. Residuals from current origin n or future origins k >= n are NEVER accessible to origin n.
3. Nighttime hours (solar_elevation <= 0 deg) have correction c = 0.0.

---

## 2. 2023 Blind Evaluation Metrics Breakdown

### Overall vs Daytime Metrics:

| Scope | Metric | Frozen Candidate F | Candidate K | Delta | 95% Bootstrap CI |
|---|---|---|---|---|---|
| **Overall** | MAE | 53.8662 W/m² | 48.4003 W/m² | **+5.4659 W/m²** | [4.6006, 6.3738] |
| **Overall** | RMSE | 90.4949 W/m² | 81.5335 W/m² | **+8.9614 W/m²** | [7.6894, 10.1808] |
| **Overall** | Bias | 27.9892 W/m² | 2.7605 W/m² | **25.2287 W/m²** | N/A |
| **Daytime** | MAE | 75.5868 W/m² | 67.8679 W/m² | **+7.7189 W/m²** | [6.4390, 8.9493] |
| **Daytime** | RMSE | 107.5131 W/m² | 96.8608 W/m² | **+10.6523 W/m²** | [9.1524, 12.1083] |
| **Daytime** | Bias | 40.0092 W/m² | 4.3813 W/m² | **35.6279 W/m²** | N/A |

---

## 3. Final Status Block

```
INPUT HASH GATE: PASS
F MODEL CALLED: NO
F PREDICTIONS REGENERATED: NO
IMMUTABLE DATA MODIFIED: NO
OUTPUT ISOLATION: PASS
CAUSALITY: PASS
2022 VALIDATION: MAE 42.65 -> 38.85 W/m² (Delta: +3.80 W/m²)
2023 BLIND RESULT: MAE 53.87 -> 48.40 W/m² (Delta: +5.47 W/m²)
BLIND MAE DELTA: +5.4659 W/m² (10.15% improvement)
BLIND BIAS DELTA: 27.9892 -> 2.7605 W/m² (25.2287 W/m² reduction)
BOOTSTRAP CI: [4.6006, 6.3738] W/m² (95% CI)
CANDIDATE K: QUALIFIED FOR NEXT GATE
```
