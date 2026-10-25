# STAGE 8.21A GOVERNED EXPERIMENT — FINAL REPORT

**Route:** `STAGE8.21A` (3D Solar Slant-Path Hydrometeor Geometry)  
**Execution Timestamp:** `2026-09-13T10:12:14.955955+00:00`  
**Governance Protocol:** POLARIS Governed Pre-registered Experiment Protocol  

---

## Executive Summary

Stage 8.21A evaluates a 4-feature 3D solar slant-path hydrometeor geometry extension to the frozen Stage 8.1 37-feature operational champion.
Pre-run feature integrity audit verified $99.30\%$ spatial ray coverage within the $47 \times 47$ MEPS window and $23$-ray station column deterministic fallback.

Following protocol, the candidate was evaluated on the locked EVEN 5-fold forward-chaining cross-validation split (173 EVEN origins).

### EVEN Validation Results
- **EVEN Control MAE:** `37.6201 W/m²`
- **EVEN Candidate MAE:** `37.5916 W/m²`
- **EVEN Delta MAE:** `-0.0285 W/m²`

### Gate Evaluation
- **G1 (MAE Improvement):** PASS (`-0.0285 < 0`)
- **G2 (Fold Consistency):** **FAIL** (`2 / 5 folds improved, required >= 4`)
- **G3 (Worst-Fold Tolerance):** PASS (`+0.2541 <= 0.50 W/m²`)
- **G4 (nMAE/RMSE Non-Degradation):** PASS
- **G5 (Causal Integrity):** PASS
- **G6 (Exact Control Reproduction):** PASS

### Protocol Action
Because predefined acceptance gate G2 failed, **candidate freeze protocol took effect immediately**:
1. No hyperparameter tuning or feature selection was performed.
2. Official ODD evaluation was **NOT** executed (`ODD_RUN = FALSE`).
3. ODD target data remained strictly uninspected (`ODD_TARGET_ACCESS = FALSE`).
4. Classification: **REJECTED ON EVEN**.
5. The Stage 8.1 37-feature champion remains the frozen operational champion.

---

## Governed Final Status

```
EVEN_CONTROL_MAE = 37.6201
EVEN_CANDIDATE_MAE = 37.5916
EVEN_DELTA_MAE = -0.0285

EVEN_GATES = FAIL

ODD_RUN = FALSE
FINAL_VERDICT = REJECTED_ON_EVEN
```
