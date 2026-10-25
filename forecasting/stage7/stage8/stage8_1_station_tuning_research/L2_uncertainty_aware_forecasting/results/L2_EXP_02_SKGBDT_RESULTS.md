# POLARIS L2-EXP-02-SKGBDT — Experiment Results

**Execution Timestamp**: 2026-10-04 05:20:56 UTC  
**Model Class**: `sklearn.ensemble.HistGradientBoostingRegressor(loss='quantile')`  
**Implementation**: `scikit-learn 1.9.0`  
**Primary Decision**: **NO-GO**  

---

## 1. Executive Summary & Comparison with L2-EXP-01 MLP

| Metric | L2-EXP-01 MLP | L2-EXP-02-SKGBDT (Ours) | Absolute Difference |
|---|---|---|---|
| **Validation Stage C PICP** | 69.80% | **60.09%** | -9.71% |
| **Blind Stage C PICP** | 71.22% | **61.83%** | -9.39% |
| **Blind Stage C 95% CI** | [69.74%, 72.66%] | **[60.20%, 63.38%]** | - |
| **Blind Stage B PICP (Unbounded)** | 80.34% | **69.07%** | -11.27% |
| **Stage B -> Stage C Change** | -9.12% | **-7.24%** | +1.88% |
| **Blind MPIW (Sharpness)** | 182.27 W/m² | **129.12 W/m²** | -53.15 W/m² |
| **Blind Winkler Score** | 258.22 | **249.62** | -8.60 |
| **Worst Slice: h21–24 PICP** | 25.00% | **30.00%** | +5.00% |
| **Worst Slice: Low-Sun (<=15°) PICP** | 55.67% | **47.94%** | -7.73% |

## 2. Required Blind Slices Breakdown

| Slice Definition | N | Stage B PICP | Stage C PICP | Stage C MPIW | Winkler Score | Gate Status |
|---|---|---|---|---|---|---|
| **1. h06_h10** | 1065 | 70.52% | **62.44%** | 163.03 W/m² | 316.38 | **PASS** |
| **2. h11_h15** | 1260 | 71.83% | **68.81%** | 167.72 W/m² | 298.33 | **PASS** |
| **3. h16_h20** | 789 | 69.07% | **66.29%** | 72.38 W/m² | 131.94 | **PASS** |
| **4. h21_h24** | 20 | 40.00% | **30.00%** | 10.37 W/m² | 43.21 | **FAIL** |
| **5. elev_le15** | 1410 | 66.24% | **47.94%** | 44.89 W/m² | 140.06 | **FAIL** |
| **6. elev_gt15** | 2263 | 70.84% | **70.48%** | 181.59 W/m² | 317.88 | **PASS** |
| **7. clear_lt0.20** | 988 | 73.18% | **61.44%** | 120.12 W/m² | 258.31 | **PASS** |
| **8. partial_0.20_0.80** | 727 | 68.91% | **60.94%** | 141.44 W/m² | 256.58 | **PASS** |
| **9. overcast_gt0.80** | 1958 | 67.06% | **62.36%** | 129.08 W/m² | 242.66 | **PASS** |

## 3. Qualification Gate Assessment

- **P1 — Blind Overall PICP [76.0%, 84.0%]**: **FAIL** (61.83%)
- **P2 — Validation Consistency [76.0%, 84.0%]**: **FAIL** (60.09%)
- **P3 — Blind Sub-Slice Floor (>= 60.0%)**: **FAIL** (Worst slice: `4. h21_h24` = 30.00%)
- **P4 — Physical Constraints**: **PASS** (100% valid)
- **P5 — Candidate F Point Invariance**: **PASS** (0.000000 W/m² error)
