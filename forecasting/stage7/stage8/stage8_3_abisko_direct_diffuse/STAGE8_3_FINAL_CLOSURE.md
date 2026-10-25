# STAGE 8.3 — ABISKO DIRECT/DIFFUSE TRANSMISSIVITY EXPERIMENT FINAL CLOSURE REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.3 ABISKO DIRECT/DIFFUSE TRANSMISSIVITY EXPERIMENT  
**Date:** September 12, 2026  
**Candidate:** E1 Abisko Direct/Diffuse/Transmissivity Features (48 features total)  
**Status:** **REJECTED**  
**Current Champion:** Stage 8.1 U700+V700 Steering Wind Model (FROZEN & UNCHANGED)

---

## 1. Executive Summary & Gate Outcomes

Stage 8.3 evaluated whether observed ground-based direct shortwave (`SW_IN_DIR`), diffuse shortwave (`SW_IN_DIFF`), direct fraction, diffuse fraction, direct/diffuse ratio, and clear-sky-normalized transmissivity history from Abisko SITES ANS provide predictive value for Nuolja hourly SW_IN forecasting.

Under 5-fold forward-chaining EVEN cross-validation on 174 EVEN origins, Candidate E1 failed all five predeclared acceptance gates:

| Metric / Requirement | Control (E0) | Candidate (E1) | Delta / Observed | Gate Threshold | Result |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Aggregate MAE** | 35.069059 W/m² | 35.696286 W/m² | **+0.627227 W/m²** | $\le -0.20$ W/m² | **FAIL** |
| **Folds Improved** | — | — | **1 / 5 folds** | $\ge 4 / 5$ folds | **FAIL** |
| **Max Fold Degradation** | — | — | **+1.334685 W/m²** | $\le +0.15$ W/m² | **FAIL** |
| **Aggregate nMAE** | 35.8331% | 36.8364% | **+1.0033 pp** | $\le$ Control nMAE | **FAIL** |
| **Aggregate RMSE** | 56.691085 W/m² | 57.206395 W/m² | **+0.515310 W/m²** | $\le$ Control RMSE | **FAIL** |

**Candidate Status:** **REJECTED**. Candidate E1 is not eligible for ODD evaluation.

---

## 2. Per-Fold EVEN Cross-Validation Breakdown

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Folds Improved | Degradation Pass |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 41.735046 | 41.735046 | +0.000000 | 24.9899% | 24.9899% | YES | YES |
| 2 | 66.494581 | 67.585483 | +1.090903 | 34.7881% | 35.3589% | NO | NO |
| 3 | 39.294066 | 40.628751 | +1.334685 | 27.4088% | 28.3398% | NO | NO |
| 4 | 25.839886 | 26.455667 | +0.615782 | 36.8303% | 37.7080% | NO | NO |
| 5 | 1.981715 | 2.076482 | +0.094768 | 55.1482% | 57.7854% | NO | YES |

---

## 3. Read-Only Forensic Governance Audit

A comprehensive 13-point forensic audit verified full compliance with project governance:

1. **Exact Control Reproduction:** PASS (Stage 8.1 EVEN control reproduced exactly: MAE = 35.069059 W/m²).
2. **Exact Candidate Metrics:** PASS (Candidate MAE = 35.696286 W/m²).
3. **Exact Gate Calculations:** PASS (All 5 gates evaluated accurately; 5/5 FAIL).
4. **5-Fold EVEN Split:** PASS (Forward-chaining split across 174 EVEN origins).
5. **Causal Timestamp Handling:** PASS (Strict `observation_timestamp <= t0` enforced; 100% causal pass).
6. **No Future Abisko Observations:** PASS (0 future Abisko observations used).
7. **No ODD Target Access:** **ODD TARGET ACCESS = NO**
8. **No ODD Predictions:** **ODD PREDICTIONS = NO**
9. **No ODD Metrics:** **ODD METRICS = NO**
10. **No Hyperparameter Tuning:** **ODD TUNING = NO** (Exact HGBR architecture preserved).
11. **No Result Shopping:** PASS (Only predeclared E1 candidate tested).
12. **Champion Unchanged:** PASS (Stage 8.1 U700+V700 Steering Wind Model remains frozen champion).
13. **Artifact Consistency:** PASS (All 9 stage artifacts present and internally verified).

---

## 4. Scientific Interpretation

The tested Abisko ground-based direct/diffuse/transmissivity representation did not provide robust out-of-sample improvement for Nuolja under the current benchmark and architecture.

*Ground-based radiation observations at Abisko (station level, ~15 km away) do not directly transfer microscale cloud attenuation patterns to Nuolja peak summit under the current feature aggregation scheme.*

---

## 5. Official Project Status & Champion

* **Operational Champion:** Stage 8.1 U700+V700 Steering Wind Model
* **Champion ODD Performance:** MAE = 36.188657 W/m² | nMAE = **28.0688%** | RMSE = 64.2195 W/m²
* **Champion Modification:** **NO**
* **Next Planned Route:** Stage 8.4 VIIRS Empirical Feasibility Audit (Satellite imagery route)
