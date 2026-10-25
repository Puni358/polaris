# STAGE 8.3 — ABISKO OBSERVED DIRECT/DIFFUSE TRANSMISSIVITY EXPERIMENT REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.3 ABISKO EXPERIMENT  
**Date:** September 12, 2026  
**Candidate:** E1 Abisko Direct/Diffuse/Transmissivity Features (48 features)  
**Status:** **REJECTED**  

---

## 1. Executive Summary & Governance Compliance

* **Active Operational Champion:** Stage 8.1 U700+V700 Steering Wind Model (FROZEN)
* **ODD Target Access:** **NO** (Zero ODD targets loaded, read, or evaluated)
* **ODD Predictions Generated:** **NO**
* **Champion Modified:** **NO**
* **EVEN CV Gate Decision:** **REJECTED**

---

## 2. 5-Fold EVEN Cross-Validation Results

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Folds Improved | Degradation Pass |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 41.7350 | 41.7350 | +0.0000 | 24.99% | 24.99% | YES | YES |
| 2 | 66.4946 | 67.5855 | +1.0909 | 34.79% | 35.36% | NO | NO |
| 3 | 39.2941 | 40.6288 | +1.3347 | 27.41% | 28.34% | NO | NO |
| 4 | 25.8399 | 26.4557 | +0.6158 | 36.83% | 37.71% | NO | NO |
| 5 | 1.9817 | 2.0765 | +0.0948 | 55.15% | 57.79% | NO | YES |

### Aggregate Metrics Summary

* **Control (Stage 8.1 Baseline):** MAE = `35.069059 W/m²` | nMAE = `35.8331%` | RMSE = `56.691085 W/m²`
* **Candidate (Stage 8.3 Abisko):** MAE = `35.696286 W/m²` | nMAE = `36.8364%` | RMSE = `57.206395 W/m²`
* **Absolute Deltas:** $\Delta	ext{MAE} = \mathbf{+0.627227	ext{ W/m}^\mathbf{2}}$ | $\Delta	ext{nMAE} = \mathbf{+1.0033	ext{ pp}}$ | $\Delta	ext{RMSE} = \mathbf{+0.515310	ext{ W/m}^\mathbf{2}}$

---

## 3. Predeclared EVEN CV Acceptance Gates

1. **Gate 1 (Aggregate MAE Improvement $\ge 0.20$ W/m²):** **FAIL** (`35.696286 W/m²`, delta: `+0.627227 W/m²`)
2. **Gate 2 (Folds Improved $\ge 4/5$):** **FAIL** (`1/5 folds`)
3. **Gate 3 (Max Single-Fold Degradation $\le +0.15$ W/m²):** **FAIL** (`+1.334685 W/m²`)
4. **Gate 4 (Candidate nMAE $\le$ Control nMAE):** **FAIL** (`36.8364%`)
5. **Gate 5 (Candidate RMSE $\le$ Control RMSE):** **FAIL** (`57.206395 W/m²`)

---

## 4. Scientific Interpretation

The tested Abisko direct/diffuse radiation representation did not provide robust out-of-sample improvement under the current benchmark and architecture, failing one or more predeclared acceptance gates. Stage 8.1 remains the frozen operational champion.
