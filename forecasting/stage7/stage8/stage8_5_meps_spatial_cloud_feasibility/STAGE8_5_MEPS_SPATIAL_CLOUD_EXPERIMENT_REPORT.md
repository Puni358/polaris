# STAGE 8.5 — CAUSAL MEPS SPATIAL CLOUD-ADVECTION EXPERIMENT REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.5 CAUSAL MEPS SPATIAL CLOUD-ADVECTION EXPERIMENT  
**Date:** September 12, 2026  
**Status:** **REJECTED / FAIL EVEN GATES**  

---

## 1. Executive Summary & Core Hypothesis

Stage 8.5 evaluated the physical hypothesis that spatial cloud structure from causal MEPS forecasts (D-1 18Z), combined with the 700 hPa steering wind, provides predictive information about cloud transitions approaching/leaving SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).

* **Control Model:** Frozen Stage 8.1 37-feature Champion (`HistGradientBoostingRegressor`).
* **Control EVEN CV MAE:** `35.270823 W/m²` (Verified Stage 8.1 Method A reproduction baseline).
* **Control EVEN CV nMAE:** `36.2419%` | **RMSE:** `56.761152 W/m²` | **Bias:** `+2.674980 W/m²`
* **Candidate Model:** Frozen Stage 8.1 37 features + 14 causal spatial cloud/advection features (51 total features).
* **Candidate EVEN CV MAE:** `35.085741 W/m²` (Delta MAE: `-0.185082 W/m²`).
* **Candidate EVEN CV nMAE:** `36.6190%` (Delta nMAE: `+0.3772 pp`).
* **Candidate EVEN CV RMSE:** `56.585549 W/m²` (Delta RMSE: `-0.175603 W/m²`).
* **Candidate EVEN CV Bias:** `+2.583969 W/m²` (Delta Bias: `-0.091011 W/m²`).
* **Folds Improved:** `2/5`.
* **Max Fold Degradation:** `+0.090224 W/m²`.
* **Final Verdict:** **REJECTED / FAIL EVEN GATES**

---

## 2. Predeclared Acceptance Gates (Clarified Governance)

| Gate | Description | Threshold | Actual Result | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Gate 1** | Primary Performance (MAE) | $\Delta\text{MAE} \le -0.500000\text{ W/m}^2$ | `-0.185082 W/m²` | **FAIL** |
| **Gate 2** | Fold Improvement Consistency | $\ge 4/5$ EVEN Folds | `2/5` | **FAIL** |
| **Gate 3** | Worst-Fold Degradation | $\le +0.500000\text{ W/m}^2$ | `+0.090224 W/m²` | **PASS** |
| **Gate 4** | nMAE & RMSE Consistency | $\text{Cand nMAE} \le \text{Ctrl}, \text{Cand RMSE} \le \text{Ctrl}$ | $\Delta\text{nMAE} = +0.3772\text{ pp}, \Delta\text{RMSE} = -0.175603\text{ W/m}^2$ | **FAIL** |
| **Gate 5** | Absolute Causality | $t_{\text{issuance}} \le t_0$ | 347/347 origins 100% verified | **PASS** |
| **Gate 6** | Control Reproduction | Method A Baseline Match | `35.270823 W/m²` | **PASS** |

---

## 3. Fold-by-Fold Performance Summary

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Fold Improved | Degradation Pass |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| F1 | 41.728068 | 41.800304 | +0.072236 | 24.9858 | 25.0290 | NO | PASS |
| F2 | 66.190911 | 65.174275 | -1.016637 | 34.6293 | 34.0974 | YES | PASS |
| F3 | 40.078480 | 40.126262 | +0.047782 | 27.9560 | 27.9893 | NO | PASS |
| F4 | 26.340965 | 26.221949 | -0.119016 | 37.5445 | 37.3749 | YES | PASS |
| F5 | 2.015690 | 2.105913 | +0.090224 | 56.0937 | 58.6045 | NO | PASS |

---

## 4. Causality & Coordinate Audit

1. **Forecast Issuance Rule:** All spatial cloud features are extracted from the D-1 18Z MEPS run ($t_{\text{issuance}} = t_0 - 6\text{h} \le t_0$).
2. **Temporal Tendency Rule:** $dN/dt = [N(t_0+H) - N(t_0+H-1)] / 1\text{h}$ uses forecast cloud fractions from the SAME D-1 18Z run.
3. **Coordinate Projection:** Grid coordinates use actual MEPS Lambert Conformal Conic 2.5 km projected grid ($dx = dy = 2500\text{ m}$).
4. **ODD Governance:** ODD target values, predictions, and metrics remained 100% unaccessed.

---

## 5. Conclusion & Handoff Recommendation

* Stage 8.5 candidate evaluation is complete.
* Final decision: **REJECTED / FAIL EVEN GATES**.
