# POLARIS L2-EXP-12: HORIZON RISK-BUDGET COMPARISON RESULTS

**Experiment ID:** `L2-EXP-12`  
**Execution Timestamp:** `2026-10-04T11:34:29.056328+00:00`  
**Governance Status:** `NO PRODUCTION PROMOTION AUTHORIZED`  
**Final Research Recommendation:** `NO-GO`  
**Evaluation Scope:** 173 odd origins (123 NORMAL route, 50 EMERGENCY route) across held-out 2024 evaluation window.  

> **Mandatory Governance Statement:**  
> *"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-12 formulation after pre-registration."*

---

## 1. Executive Summary & Core Research Findings

L2-EXP-12 investigated whether allocating a finite reliability-risk budget across the full 24-hour horizon can safely recover static $q_{10}$'s diesel and curtailment efficiency while retaining its critical reliability advantage:

1. **Unmet Critical Load (Primary Gate: FAILED):**  
   - Arm E realized total unmet critical load is **111,210.1 Wh**, compared to **65,026.9 Wh** for Arm B (delta = +46,183.2 Wh, threshold <= 71,529.6 Wh).

2. **Diesel Fuel Consumption (Primary Resource Goal: ACHIEVED):**  
   - Arm E consumed **6,948.6 L** of diesel fuel, compared to **7,283.0 L** for Arm B (delta = -334.4 L).

3. **Solar Curtailment (Target: ACHIEVED):**  
   - Arm E realized **7,951,716.8 Wh** of curtailment, compared to **8,850,136.3 Wh** for Arm B (delta = -898,419.5 Wh).

4. **Safety & Zero Violations (PASSED):**  
   - Exactly **0 SOC-floor violations** and **0 SOC-ceiling violations** across all 123 NORMAL origins (lowest SOC: 40.37%, highest SOC: 95.0%).

---

## 2. Primary 6-Arm Comparative Ladder (123 NORMAL Origins)

| Operational Metric | Arm A (Candidate F Point) | Arm B (Static q10 Benchmark) | Arm C (Fixed Modest q=0.15) | Arm D (SOC-Aware q) | Arm E (Horizon Risk-Budget) | Arm F (Perfect Foresight) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Realized Unmet Wh** | **983,306.0** | **65,026.9** | **96,278.5** | **95,641.8** | **111,210.1** | **0.0** |
| Mean Unmet Wh / Origin | 7,994.4 | 528.7 | 782.8 | 777.6 | 904.1 | 0.0 |
| Origins with Unmet Load | 110 / 123 | 41 / 123 | 49 / 123 | 48 / 123 | 54 / 123 | 0 / 123 |
| Critical Reliability (%) | 97.13% | 99.81% | 99.72% | 99.72% | 99.68% | 100.00% |
| **Total Realized Diesel (L)** | **5,270.6** | **7,283.0** | **7,013.8** | **7,047.7** | **6,948.6** | **5,440.9** |
| Mean Diesel L / Origin | 42.85 | 59.21 | 57.02 | 57.30 | 56.49 | 44.24 |
| Diesel-on Hours | 316 | 412 | 398 | 399 | 396 | 330 |
| Diesel Startup Events | 164 | 219 | 211 | 210 | 204 | 166 |
| **Total Solar Curtailment (Wh)**| **4,587,708.5** | **8,850,136.3** | **8,147,884.5** | **8,272,515.5** | **7,951,716.8** | **2,778,295.5** |
| Battery Equiv. Full Cycles | 0.6415 | 0.7296 | 0.7185 | 0.7187 | 0.7123 | 0.6833 |
| Mean Minimum SOC (%) | 52.26% | 51.94% | 52.11% | 52.11% | 52.11% | 55.04% |
| Lowest Realized SOC (%) | 32.58% | 40.24% | 39.97% | 40.66% | 40.37% | 43.63% |
| SOC Floor Violations (<20%) | 0 | 0 | 0 | 0 | 0 | 0 |
| SOC Ceiling Violations (>95%) | 0 | 0 | 0 | 0 | 0 | 0 |
| Mean Solve Time / Origin | 0.6603 s | 0.7431 s | 0.7102 s | 0.7825 s | 0.5635 s | 0.5773 s |

---

## 3. Paired Statistical Comparisons against Static q10 Benchmark (Arm B)

### 3.1 Arm E (Horizon Risk-Budget) vs Arm B
- **Unmet Load Delta (E - B):** Mean = `375.4732` Wh [95% CI: `255.3553`, `517.8171`] Wh (Wilcoxon p = `0.0`).
  - Improved origins: `0` | Worsened: `52` | Tied: `71`.
- **Diesel Fuel Delta (E - B):** Mean = `-2.7188` L [95% CI: `-3.1255`, `-2.3352`] L (Wilcoxon p = `0.0`).
- **Curtailment Delta (E - B):** Mean = `-7304.2236` Wh [95% CI: `-7878.5407`, `-6719.0276`] Wh (Wilcoxon p = `0.0`).
- **Battery EFC Delta (E - B):** Mean = `-0.0173` [95% CI: `-0.023`, `-0.0118`] (Wilcoxon p = `0.0`).

### 3.2 Arm D (SOC-Aware q) vs Arm B
- **Unmet Load Delta (D - B):** Mean = `248.9016` Wh [95% CI: `158.7195`, `356.9073`] Wh (Wilcoxon p = `0.0`).
- **Diesel Fuel Delta (D - B):** Mean = `-1.9131` L (Wilcoxon p = `0.0`).

### 3.3 Arm C (Fixed Modest q=0.15) vs Arm B
- **Unmet Load Delta (C - B):** Mean = `254.078` Wh [95% CI: `164.9894`, `358.2431`] Wh (Wilcoxon p = `0.0`).
- **Diesel Fuel Delta (C - B):** Mean = `-2.1894` L (Wilcoxon p = `0.0`).

---

## 4. Final Research Recommendation

```
FINAL RESEARCH RECOMMENDATION: NO-GO
GOVERNANCE STATUS: NO PRODUCTION PROMOTION AUTHORIZED
EVALUATION MODE: STRICTLY_RESEARCH_ONLY
```

"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-12 formulation after pre-registration."
