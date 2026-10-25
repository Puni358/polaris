# POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD (sigma_LWP) EXPERIMENT

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD EXPERIMENT  
**Status**: `COMPLETED — REJECTED (FAILED ACCEPTANCE GATES)`  
**Candidate Feature Evaluated**: `sigma_LWP` (MEPS Column Liquid Water Path Ensemble Spread)  
**Active Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%) — **UNCHANGED**  
**Stage 8.16B-2 Authorization**: **NOT AUTHORIZED (STOP)**  

---

## 1. Executive Summary & Governance Compliance

Stage 8.16B-1 executed a 5-fold forward-chaining cross-validation experiment on the **EVEN-indexed 2024 benchmark origins** (174 EVEN origins) to test whether incorporating **$\sigma_{LWP}$** (the causally available ensemble standard deviation of MEPS column Liquid Water Path) improves upon the frozen Stage 8.1 Operational Champion (37 features).

### Strict Governance Compliance Audit
- **ODD Benchmark Origins (173 origins)**: **100% UNTOUCHED (0 evaluation reads)**.
- **Production Operational Champion**: **Stage 8.1 700 hPa Steering Wind Model** remains **FROZEN & UNCHANGED**.
- **`POLARIS_MASTER_HANDOFF.md`**: **UNTOUCHED**.
- **Further Automated Candidate Tests**: **HALTED**.

---

## 2. Feature Lineage, Causality & Feature Correlation

1. **Mathematical Definition**:
   $$\sigma_{LWP} = \text{LWP}_{latest} \times \frac{\sigma_{cloud\_frac}}{\max(0.05, \bar{N}_{total})}$$
   where $\text{LWP}_{latest}$ is the surface-aware column Liquid Water Path ($\text{g/m}^2$) integrated vertically from MEPS 3D fields.
2. **Causality Verification**:
   - $T_{init} = t_0 - 6\text{h} \le t_0$ (MEPS D-1 18Z run).
   - Valid time = forecast horizon $h$ ($h = 1 \dots 24$).
   - Operational publication causality ($T_{pub} \le t_0$): **100% VERIFIED**.
3. **Correlation with Existing Uncertainty Signals**:
   - Correlation with Stage 6.1 `meps_std_SW_IN`: **$r = +0.1408$**.
   - Proves $\sigma_{LWP}$ is **materially distinct** from scalar radiation spread `meps_std_SW_IN`.

---

## 3. EVEN CV Aggregate & Fold-by-Fold Numerical Results

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
  - Delta MAE:   -0.118390 W/m² (Modest aggregate improvement)
  - Delta nMAE:  -0.0855 pp    (Modest aggregate improvement)
  - Delta RMSE:  -0.297693 W/m² (Modest aggregate improvement)
================================================================================
```

### Fold-by-Fold Performance Audit

| Fold | Train Origins | Val Origins | Val Daytime Hours | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Delta nMAE (pp) | Delta RMSE (W/m²) | Fold Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 29 | 29 | 224 | 49.311400 | 49.378300 | **+0.066900** | +0.0384 | +0.114500 | `DEGRADED` |
| **Fold 2** | 58 | 29 | 495 | 70.568800 | 68.664300 | **-1.904500** | -1.1895 | -3.120500 | `IMPROVED` |
| **Fold 3** | 87 | 29 | 509 | 40.345600 | 41.684100 | **+1.338500** | +0.9472 | +1.842300 | `DEGRADED` |
| **Fold 4** | 116 | 29 | 215 | 25.770400 | 26.088500 | **+0.318100** | +0.1989 | +0.512000 | `DEGRADED` |
| **Fold 5** | 145 | 29 | 50 | 2.104100 | 2.061400 | **-0.042600** | -0.0682 | -0.091000 | `IMPROVED` |

---

## 4. Predeclared 5-Gate Acceptance Standard Audit

| Gate ID | Acceptance Requirement | Threshold / Criterion | Empirical Result | Status |
| :---: | :--- | :--- | :---: | :---: |
| **Gate 1** | Aggregate EVEN CV MAE | $\Delta\text{MAE} < 0.0\text{ W/m}^2$ | **$-0.118390\text{ W/m}^2$** | **PASS** |
| **Gate 2** | Aggregate EVEN CV nMAE | $\Delta\text{nMAE} < 0.0\text{ pp}$ | **$-0.0855\text{ pp}$** | **PASS** |
| **Gate 3** | Majority Fold Consistency | $\ge 3 / 5$ Folds Improved | **2 / 5 Folds Improved** (Folds 2 & 5) | **FAIL** |
| **Gate 4** | Bounded Worst-Fold Degradation | Max Degradation $\le +0.50\text{ W/m}^2$ | **$+1.338540\text{ W/m}^2$** (Fold 3) | **FAIL** |
| **Gate 5** | Aggregate EVEN CV RMSE | $\Delta\text{RMSE} < 0.0\text{ W/m}^2$ | **$-0.297693\text{ W/m}^2$** | **PASS** |

### Decision Summary
While candidate feature `sigma_LWP` achieved slight aggregate metric improvements ($\Delta\text{MAE} = -0.1184\text{ W/m}^2$, $\Delta\text{nMAE} = -0.0855\text{ pp}$), it **failed Gates 3 and 4**:
1. Only **2 out of 5 folds** showed improvement (Folds 1, 3, and 4 degraded).
2. Fold 3 experienced severe performance degradation (**$+1.338540\text{ W/m}^2 > +0.50\text{ W/m}^2$** limit).

Therefore, candidate feature `sigma_LWP` is **REJECTED** and will **NOT** be incorporated into the production model.

---

## 5. Updates to POLARIS Stage 8 Route Registry

In accordance with project governance, the Stage 8 Route Registry has been updated:

- **Route Entry**: `Stage 8.16B-1 (sigma_LWP)`
- **Classification**: `REJECTED — FAILED ACCEPTANCE GATES`
- **Rejection Rationale**: Failed Gate 3 (only 2/5 folds improved) and Gate 4 (worst-fold degradation $+1.3385\text{ W/m}^2$ exceeded $+0.50\text{ W/m}^2$ limit).
- **Stage 8.1 Operational Champion**: **UNCHANGED & FROZEN** (Daytime nMAE = 28.0688%).

---

## 6. Final Governance Check & Confirmation

```
================================================================================
POLARIS STAGE 8.16B-1 FINAL EXPERIMENTAL GOVERNANCE AUDIT
================================================================================
ODD Benchmark Target Reads:           0 (100% UNTOUCHED)
ODD Benchmark Forecast Evaluations:   0 (100% UNTOUCHED)
Stage 8.1 Operational Champion:       UNCHANGED (Daytime nMAE = 28.0688%)
POLARIS_MASTER_HANDOFF.md:            UNTOUCHED
Automated Next-Experiment Execution:  STOPPED (No auto-testing of N_cat x sigma_LWP)
================================================================================
```
