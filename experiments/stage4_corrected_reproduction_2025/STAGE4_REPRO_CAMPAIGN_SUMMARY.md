# POLARIS Stage 4: Corrected Reproduction Campaign Summary

**Experiment:** `EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT`  
**Execution Timestamp:** 2026-10-05T20:40:02Z (Runtime: 3164.6 s)  
**Governing Preregistration:** `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md`  
**Holdout Population:** 123 origins (2025-05-01 through 2025-08-31), 2,952 hours per arm, 14,760 total arm-hours  
**Status:** COMPLETE (0 execution failures, 0 exclusions)  

---

## 1. Five-Arm Corrected Performance Summary (2025 Holdout)

| Arm | Diesel Fuel (L) | Saving vs B (%) | Critical-First Rel (%) | ΔR_CF (pp) | Proportional Rel (%) | ΔR_P (pp) | Min SOC (%) | SOC <20% | All Safety Gates |
|---|---|---|---|---|---|---|---|---|---|
| **Control Frozen B** | 6096.9004 | 0.00% | 93.753840% | +0.000000 | 83.849951% | +0.000000 | 54.99% | 0 | **REFERENCE** |
| **Candidate S** | 4687.6902 | 23.11% | 94.394461% | +0.640621 | 84.672633% | +0.822681 | 20.00% | 0 | **PASS** |
| **Candidate SW** | 3768.5494 | 38.19% | 94.036127% | +0.282287 | 83.268461% | -0.581490 | 20.00% | 0 | **SAFETY FAILURE** |
| **Candidate S-L** | 5280.2375 | 13.39% | 94.393177% | +0.639338 | 85.006435% | +1.156484 | 20.00% | 0 | **PASS** |
| **Candidate SW-L** | 5263.9645 | 13.66% | 94.494631% | +0.740792 | 85.241088% | +1.391137 | 20.00% | 0 | **PASS** |

---

## 2. Statistical Testing Results (Diesel Gate)

### Candidate S-L (vs Control B)
- **Total Fuel Saved:** 816.66 L (13.39%)
- **Mean Paired Saving:** 6.6395 L/origin
- **Median Paired Saving:** 6.4462 L/origin
- **BCa 95% Bootstrap CI:** [4.2567, 8.9562] L/origin (Strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1665.0, p = 7.1960e-07
- **Holm-Adjusted p-value:** 1.4392e-06 (Significant at alpha=0.05: True)
- **Diesel Gate Status:** **PASS**

### Candidate SW-L (Decision Candidate vs Control B)
- **Total Fuel Saved:** 832.94 L (13.66%)
- **Mean Paired Saving:** 6.7718 L/origin
- **Median Paired Saving:** 7.5372 L/origin
- **BCa 95% Bootstrap CI:** [4.3382, 9.1280] L/origin (Strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1784.0, p = 8.1659e-07
- **Holm-Adjusted p-value:** 1.4392e-06 (Significant at alpha=0.05: True)
- **Diesel Gate Status:** **PASS**

---

## 3. Factorial Contrasts & Mechanism Diagnostic (C4)

| Contrast | Description | Outcome | Mean | BCa 95% CI |
|---|---|---|---|---|
| **C1** (`SW − S`) | Wind effect without protection | Proportional Rel (pp) | -1.4042 | [-1.8353, -0.9985] |
| | | Fuel Saving (L) | -7.4727 | [-9.6877, -5.3481] |
| **C2** (`SW-L − SW`) | Protection effect under solar+wind | Proportional Rel (pp) | +1.9726 | [+1.5872, +2.4013] |
| | | Fuel Saving (L) | +12.1578 | [+10.0441, +14.2400] |
| **C3** (`S-L − S`) | Protection effect under solar-only | Proportional Rel (pp) | +0.3338 | [+0.0698, +0.6320] |
| | | Fuel Saving (L) | +4.8175 | [+3.1728, +6.5570] |
| **C4** | **Interaction / Mechanism Diagnostic** | **Proportional Rel (pp)** | **+1.6388** | **[+1.2559, +2.0576]** |
| | `(SW-L − SW) − (S-L − S)` | Fuel Saving (L) | +7.3404 | [+5.1749, +9.5504] |

