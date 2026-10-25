# POLARIS L2-EXP-03 — Frozen SKGBDT Global Conformal Calibration Results

**Execution Timestamp**: 2026-10-04 05:30:01 UTC  
**Calibration Method**: Global Split-Conformal (CQR, alpha=0.20)  
**Frozen Model**: `sklearn.ensemble.HistGradientBoostingRegressor` (from L2-EXP-02)  
**Overall Decision**: **NO-GO**  

---

## 1. Executive Summary & Calibration Impact

The global conformal adjustment estimated on 2022 validation daytime rows ($N=4,069$) is **`q_hat = +9.8962 W/m²`**.

| Evaluation Set & Model State | Stage B PICP (Unbounded) | Stage C PICP (Physical) | 95% Bootstrap CI | MPIW | Winkler Score | q50 MAE |
|---|---|---|---|---|---|---|
| **Validation 2022 (Raw SKGBDT)** | 67.19% | **60.09%** | - | 122.76 W/m² | 244.67 | 51.05 W/m² |
| **Validation 2022 (Calibrated)** | **80.02%** | **69.11%** | - | 136.21 W/m² | 239.56 | 51.05 W/m² |
| **Blind 2023 (Raw SKGBDT Baseline)** | 69.07% | **61.83%** | [59.81%, 63.00%] | 129.12 W/m² | 249.62 | 51.51 W/m² |
| **Blind 2023 (Calibrated Stage B)** | **80.40%** | - | [79.09%, 81.62%] | 148.91 W/m² | 227.18 | 51.51 W/m² |
| **Blind 2023 (Calibrated Stage C)** | - | **70.05%** | **[68.53%, 71.49%]** | 144.13 W/m² | 243.68 | 51.51 W/m² |

## 2. Paired Bootstrap Statistical Comparison (Blind 2023, 2,000 Replicates)

- **Delta PICP (Stage C)**: **+8.63%** (95% CI: [+7.73%, +9.56%])
- **Delta MPIW (Stage C)**: **+17.06 W/m²** (95% CI: [+16.88, +17.23])
- **Delta Winkler Score**: **-4.75** (95% CI: [-5.98, -3.54])
- **Delta q50 MAE**: **+0.0000 W/m²** (point forecast invariant)

## 3. Required Blind Slices Breakdown (Stage C)

| Slice Definition | N | Raw Stage C PICP | Calibrated Stage B PICP | Calibrated Stage C PICP | Calibrated MPIW | Winkler Score | Status |
|---|---|---|---|---|---|---|---|
| **1. h06_h10** | 1065 | 62.44% | 78.69% | **69.20%** | 180.34 W/m² | 311.20 | **PASS** |
| **2. h11_h15** | 1260 | 68.73% | 78.73% | **73.73%** | 186.34 W/m² | 293.46 | **PASS** |
| **3. h16_h20** | 789 | 65.02% | 82.89% | **78.71%** | 90.56 W/m² | 128.63 | **PASS** |
| **4. h21_h24** | 20 | 30.00% | 90.00% | **75.00%** | 23.66 W/m² | 32.80 | **PASS** |
| **5. elev_le15** | 1410 | 47.02% | 86.38% | **60.00%** | 57.98 W/m² | 138.00 | **PASS** |
| **6. elev_gt15** | 2263 | 70.44% | 76.67% | **76.31%** | 200.97 W/m² | 311.58 | **PASS** |
| **7. clear_lt0.20** | 988 | 60.83% | 82.69% | **66.60%** | 136.12 W/m² | 257.50 | **PASS** |
| **8. partial_0.20_0.80** | 727 | 60.39% | 80.74% | **69.33%** | 158.04 W/m² | 252.35 | **PASS** |
| **9. overcast_gt0.80** | 1958 | 62.16% | 79.11% | **72.06%** | 146.66 W/m² | 235.86 | **PASS** |

## 4. Qualification Gate Assessment

- **P1 — Blind Overall PICP [76.0%, 84.0%]**: **FAIL** (70.05%)
- **P2 — Validation Consistency [76.0%, 84.0%]**: **FAIL** (69.11%)
- **P3 — Blind Sub-Slice Floor (>= 60.0%)**: **PASS** (Worst slice: `5. elev_le15` = 60.00%)
- **P4 — Physical Constraints**: **PASS** (100% valid)
- **P5 — Candidate F Point Invariance**: **PASS** (0.000000 W/m² drift)
