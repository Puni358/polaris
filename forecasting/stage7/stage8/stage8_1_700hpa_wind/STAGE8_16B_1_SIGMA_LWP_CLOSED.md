# POLARIS STAGE 8.16B-1 — CLOSED EXPERIMENTAL CHECKPOINT

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD EXPERIMENT  
**Status**: `CLOSED — REJECTED`  
**Active Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%) — **UNCHANGED**  
**Governance Firewall Status**: 100% Compliant (0 ODD target reads, 0 model changes, 0 master handoff edits).  

---

## 1. Executive Summary & Authoritative Closure Statement

Stage 8.16B-1 evaluated whether adding candidate feature **$\sigma_{LWP}$** (the causally available MEPS column Liquid Water Path ensemble spread) improves upon the frozen Stage 8.1 Operational Champion across 174 EVEN-indexed 2024 benchmark origins under a 5-fold forward-chaining cross-validation protocol.

### Authoritative Closure & Rejection Statement
> **STATUS**: `CLOSED — REJECTED`  
> **REASON**: $\sigma_{LWP}$ produced modest aggregate metric improvements ($\Delta\text{MAE} = -0.118390\text{ W/m}^2$, $\Delta\text{nMAE} = -0.0855\text{ pp}$) but **failed the predefined consistency acceptance gates** because only 2 out of 5 folds improved (Gate 3 FAIL) and the worst-fold degradation was **$+1.338540\text{ W/m}^2$** (Gate 4 FAIL), exceeding the $+0.50\text{ W/m}^2$ allowable limit.

---

## 2. Frozen Operational Champion Baseline

The operational champion remains strictly frozen and unchanged:

- **Model Name**: Stage 8.1 700 hPa Steering Wind Model
- **Daytime nMAE**: `28.0688%`
- **Daytime MAE**: `36.188657 W/m²`
- **Daytime RMSE**: `64.219495 W/m²`
- **Daytime Bias**: `+1.439399 W/m²`
- **Night MAE**: `0.0 W/m²`
- **Status**: **FROZEN OPERATIONAL CHAMPION**

---

## 3. Authoritative EVEN CV Experimental Audit Results

```
================================================================================
POLARIS STAGE 8.16B-1 EVEN CV RESULTS SUMMARY (174 EVEN ORIGINS)
================================================================================
Control Baseline (Stage 8.1 Champion, 37 Features):
  - Daytime MAE:  45.091280 W/m²
  - Daytime nMAE: 32.5790%
  - Daytime RMSE: 76.985584 W/m²
  - Daytime Bias: +1.439399 W/m²

Candidate Model (Stage 8.1 + sigma_LWP, 38 Features):
  - Daytime MAE:  44.972891 W/m²
  - Daytime nMAE: 32.4934%
  - Daytime RMSE: 76.687891 W/m²
  - Daytime Bias: +1.385150 W/m²

Aggregate Deltas:
  - Delta MAE:   -0.118390 W/m²
  - Delta nMAE:  -0.0855 pp
  - Delta RMSE:  -0.297693 W/m²
================================================================================
```

### Fold-by-Fold Performance Audit

| Fold | Train Origins | Val Origins | Val Daytime Hours | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Delta nMAE (pp) | Fold Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 29 | 29 | 224 | 49.311400 | 49.378300 | **+0.066900** | +0.0384 | `DEGRADED` |
| **Fold 2** | 58 | 29 | 495 | 70.568800 | 68.664300 | **-1.904500** | -1.1895 | `IMPROVED` |
| **Fold 3** | 87 | 29 | 509 | 40.345600 | 41.684100 | **+1.338500** | +0.9472 | `DEGRADED` |
| **Fold 4** | 116 | 29 | 215 | 25.770400 | 26.088500 | **+0.318100** | +0.1989 | `DEGRADED` |
| **Fold 5** | 145 | 29 | 50 | 2.104100 | 2.061400 | **-0.042600** | -0.0682 | `IMPROVED` |

---

## 4. Predeclared Acceptance Gate Decision Matrix

| Gate ID | Acceptance Requirement | Threshold / Criterion | Empirical Result | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **Gate 1** | Aggregate EVEN CV MAE | $\Delta\text{MAE} < 0.0\text{ W/m}^2$ | **$-0.118390\text{ W/m}^2$** | **PASS** |
| **Gate 2** | Aggregate EVEN CV nMAE | $\Delta\text{nMAE} < 0.0\text{ pp}$ | **$-0.0855\text{ pp}$** | **PASS** |
| **Gate 3** | Majority Fold Consistency | $\ge 3 / 5$ Folds Improved | **2 / 5 Folds Improved** (Folds 2 & 5) | **FAIL** |
| **Gate 4** | Bounded Worst-Fold Degradation | Max Degradation $\le +0.50\text{ W/m}^2$ | **$+1.338540\text{ W/m}^2$** (Fold 3) | **FAIL** |
| **Gate 5** | Aggregate EVEN CV RMSE | $\Delta\text{RMSE} < 0.0\text{ W/m}^2$ | **$-0.297693\text{ W/m}^2$** | **PASS** |

---

## 5. Future-AI Firewall Directives

**ALL FUTURE AI AGENTS OPERATING ON POLARIS MUST OBEY THE FOLLOWING FIREWALL DIRECTIVES:**

1. **RE-PROPOSAL RESTRICTION**:
   > *"Do NOT re-propose sigma_LWP as a new route unless there is a materially different formulation/data source that is not mathematically equivalent to the tested Stage 8.16B-1 signal."*

2. **SCIENTIFIC INTERPRETATION BOUNDARY**:
   > *"Do NOT interpret the result as proving that LWP uncertainty contains no useful information. The scientifically supported conclusion is only that the tested sigma_LWP formulation did not satisfy the project's predefined robustness gates."*

3. **NEXT-ROUTE ISOLATION**:
   > *"Do NOT automatically proceed to test N_cat x sigma_LWP or any other Stage 8.16 candidate without a new, explicit user authorization."*

---

## 6. Final Governance Check & Confirmation

```
================================================================================
POLARIS STAGE 8.16B-1 FINAL CLOSURE GOVERNANCE AUDIT
================================================================================
ODD Benchmark Target Reads:           0 (100% UNTOUCHED)
ODD Benchmark Forecast Evaluations:   0 (100% UNTOUCHED)
ODD Hyperparameter Tuning:            0
Stage 8.1 Operational Champion:       UNCHANGED (Daytime nMAE = 28.0688%)
New Production Model:                 NONE
POLARIS_MASTER_HANDOFF.md:            UNTOUCHED
Stage 8.16B-1 Status:                 CLOSED — REJECTED
================================================================================
```
