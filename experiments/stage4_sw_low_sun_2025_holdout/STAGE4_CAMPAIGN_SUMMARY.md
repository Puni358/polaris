# POLARIS Stage 4: 2025 Confirmatory Holdout Campaign Summary

**Experiment:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`  
**Execution Date:** 2026-10-05  
**Governing Preregistration:** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md` (SHA-256 `9cb2d5459894be8add07a3bd01595f40ab2485c2a18510765c4d8f0264fe4e46`)  
**Holdout Population:** 123 origins (2025-05-01 through 2025-08-31), 2,952 hours per arm, 14,760 total arm-hours  
**Status:** COMPLETE (0 execution failures, 0 exclusions)

---

## 1. Executive Summary & Final Classifications

| Candidate | Role | Safety Gates | Diesel Gate | Fuel Saving (%) | 40% Target | Final Classification |
|---|---|---|---|---|---|---|
| **Candidate S-L** | Efficiency Reference | **PASS** | **PASS** | **12.81%** | Not Achieved | **SUCCESS** |
| **Candidate SW-L** | Primary Decision Candidate | **PASS** | **PASS** | **14.66%** | Not Achieved | **SUCCESS** |

---

## 2. Five-Arm Performance Summary (2025 Holdout)

| Arm | Diesel Fuel (L) | Saving vs B (%) | Critical-First Rel (%) | ΔR_CF (pp) | Proportional Rel (%) | ΔR_P (pp) | Min SOC (%) | SOC <20% |
|---|---|---|---|---|---|---|---|---|
| **Control_Frozen_B** | 6117.9691 | — | 93.669482% | — | 83.823383% | — | 54.99% | 0 |
| **Candidate_S** | 4648.3272 | 24.02% | 94.327168% | +0.657686 | 84.604885% | +0.781502 | 20.00% | 0 |
| **Candidate_SW** | 3885.0225 | 36.50% | 94.090514% | +0.421032 | 83.467189% | -0.356194 | 20.00% | 0 |
| **Candidate_SL** | 5334.1331 | 12.81% | 94.455173% | +0.785691 | 85.150455% | +1.327072 | 20.00% | 0 |
| **Candidate_SWL** | 5221.3152 | 14.66% | 94.484413% | +0.814931 | 85.264223% | +1.440840 | 20.00% | 0 |

---

## 3. Statistical Testing Results (Diesel Gate)

### Candidate S-L (vs Control B)
- **Total Saving:** 783.84 L (12.81%)
- **Mean Paired Saving:** 6.3727 L/origin
- **Median Paired Saving:** 5.9488 L/origin
- **BCa 95% Bootstrap CI:** [4.1057, 8.5926] L/origin (Strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1662.0, p = 6.9037e-07
- **Holm-Adjusted p-value:** 6.9037e-07 (Significant at alpha=0.05: True)
- **Diesel Gate:** **PASS**

### Candidate SW-L (vs Control B)
- **Total Saving:** 896.65 L (14.66%)
- **Mean Paired Saving:** 7.2899 L/origin
- **Median Paired Saving:** 7.3848 L/origin
- **BCa 95% Bootstrap CI:** [4.9970, 9.5583] L/origin (Strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1564.0, p = 2.2831e-08
- **Holm-Adjusted p-value:** 4.5662e-08 (Significant at alpha=0.05: True)
- **Diesel Gate:** **PASS**

---

## 4. Factorial Contrasts & Primary Mechanism Diagnostic (C4)

| Contrast | Description | Outcome | Mean | BCa 95% CI |
|---|---|---|---|---|
| **C1** (`SW − S`) | Wind effect without protection | Proportional Rel (pp) | -1.1377 | [-1.5910, -0.7184] |
| | | Fuel Saving (L) | -6.2057 | [-8.3797, -4.0875] |
| **C2** (`SW-L − SW`) | Protection effect under solar+wind | Proportional Rel (pp) | +1.7970 | [+1.4205, +2.1995] |
| | | Fuel Saving (L) | +10.8642 | [+8.7244, +13.0813] |
| **C3** (`S-L − S`) | Protection effect under solar-only | Proportional Rel (pp) | +0.5456 | [+0.2755, +0.8331] |
| | | Fuel Saving (L) | +5.5757 | [+3.8971, +7.4640] |
| **C4** | **Interaction / Mechanism Diagnostic** | **Proportional Rel (pp)** | **+1.2515** | **[+0.8683, +1.6546]** |
| | `(SW-L − SW) − (S-L − S)` | Fuel Saving (L) | +5.2885 | [+3.2317, +7.3345] |

---

## 5. Numerical Residue & Solver Execution Audit
- **HiGHS mip_feasibility_tolerance:** `1e-6`
- **HiGHS primal_feasibility_tolerance:** `1e-7`
- **Numerical residue threshold tau:** `0.055 W`
- **Residue Correction Events:**
  - Control_Frozen_B: 146 events (max magnitude: 0.000000 W)
  - Candidate_S: 125 events (max magnitude: 0.000000 W)
  - Candidate_SW: 150 events (max magnitude: 0.000000 W)
  - Candidate_SL: 114 events (max magnitude: 0.000000 W)
  - Candidate_SWL: 132 events (max magnitude: 0.000000 W)
- **Simultaneous Charge/Discharge Violations > tau:** 0
- **Solver Infeasibilities:** 0
- **Total Arm-Hours:** 14,760
