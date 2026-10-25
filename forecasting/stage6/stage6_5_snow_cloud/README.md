# POLARIS Stage 6.5 — Snow / Cloud Interaction Experiment Report

**Date:** 2026-09-12  
**Experiment:** Candidate 1 — Snow / Cloud Interaction  
**Control Baseline:** Stage 5.2 Architecture A (GBDT Residual Corrector)  
**Status:** **REJECTED**  
**ODD Test Set Status:** **ODD UNTOUCHED** (100% preserved)

---

## 1. Summary Results

| Metric | Control (Stage 5.2) | Candidate | Delta | Gate Status |
| :--- | :--- | :--- | :--- | :--- |
| **Daytime MAE (W/m²)** | 39.4236 | 39.7269 | **+0.3033** | FAIL (Target <= -0.20) |
| **Daytime nMAE (%)** | 41.46% | 42.63% | **+1.17%** | FAIL (Target <= 41.46%) |
| **Daytime RMSE (W/m²)** | 62.8290 | 63.0190 | **+0.1900** | FAIL (Target <= 62.83) |
| **Folds Improved** | - | - | **1 / 5** | FAIL (Target >= 4) |
| **Max Degradation** | - | - | **+0.6336** | FAIL (Target <= +0.15) |

---

## 2. Gate Evaluation Breakdown

1. **Gate 1 (ΔMAE <= -0.20 W/m²):** +0.3033 W/m² -> **FAILED**
2. **Gate 2 (Improved in >= 4 folds):** 1 / 5 folds -> **FAILED**
3. **Gate 3 (Max fold degradation <= +0.15 W/m²):** +0.6336 W/m² -> **FAILED**
4. **Gate 4 (nMAE <= 41.46%):** 42.63% -> **FAILED**
5. **Gate 5 (RMSE <= 62.83 W/m²):** 63.0190 W/m² -> **FAILED**

---

## 3. Five-Fold Forward-Chaining Results

```
 fold  tr_origins  val_origins  ctrl_mae  cand_mae  delta_mae  fold_pass
    1          29           29 49.900340 49.779069  -0.121271       True
    2          58           29 72.739444 73.350061   0.610617      False
    3          87           29 42.749237 42.978760   0.229523      False
    4         116           29 29.292916 29.926515   0.633599      False
    5         145           29  2.436051  2.599859   0.163808      False
```

---

## 4. Scientific Conclusion & ODD Protocol

**Decision:** Candidate FAILS predeclared gates and is REJECTED. Stage 5.2 Architecture A remains the undefeated champion.

**ODD Test Set Status:** **ODD UNTOUCHED**
