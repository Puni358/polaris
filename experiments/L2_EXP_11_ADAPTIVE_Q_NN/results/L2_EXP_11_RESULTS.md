# POLARIS L2-EXP-11: ADAPTIVE q10 RELAXATION RESEARCH RESULTS

**Experiment ID:** `L2-EXP-11`  
**Execution Timestamp:** `2026-10-04T11:14:51.478221+00:00`  
**Governance Status:** `NO PRODUCTION PROMOTION AUTHORIZED`  
**Final Research Recommendation:** `NO-GO`  
**Evaluation Scope:** 173 odd origins (123 NORMAL route, 50 EMERGENCY route) across held-out 2024 evaluation window.  

> **Mandatory Governance Statement:**  
> *"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-11 formulation, architecture, or hyperparameters after pre-registration."*

---

## 1. Executive Summary & Core Research Findings

L2-EXP-11 tested whether a low-capacity neural network can learn when static $q_{10}$ is unnecessarily pessimistic, safely relaxing $q_{10}$ only during low-risk forecast regimes while retaining static $q_{10}$ reliability:

1. **Unmet Critical Load (Primary Gate: FAILED):**  
   - Arm D realized total unmet critical load is **134,139.2 Wh**, compared to **65,026.9 Wh** for Arm B (delta = +69,112.3 Wh, relative to the pre-registered B + 10% threshold of 71,529.6 Wh).

2. **Diesel Fuel Consumption (Primary Resource Goal: ACHIEVED):**  
   - Arm D consumed **6,817.3 L** of diesel fuel, compared to **7,283.0 L** for Arm B.

3. **Solar Curtailment (Target: ACHIEVED):**  
   - Arm D realized **7,680,184.4 Wh** of curtailment, compared to **8,850,136.3 Wh** for Arm B (a reduction of 13.2%).

4. **Safety & Zero Violations (PASSED):**  
   - Exactly **0 SOC-floor violations** and **0 SOC-ceiling violations** across all 123 NORMAL origins (lowest SOC: 37.91%, highest SOC: 95.0%).
   - In addition, Arm C's replay accounting fix completely eliminated the 604 upper-bound excursions from L2-EXP-10.

---

## 2. Primary 5-Arm Comparative Ladder (123 NORMAL Origins)

| Operational Metric | Arm A (Candidate F Point) | Arm B (Static q10 Benchmark) | Arm C (L2-EXP-10 Arm F Fixed) | Arm D (NN Adaptive-q) | Arm D_simple (Ridge Baseline) | Arm E (Perfect Foresight) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Realized Unmet Wh** | **983,306.0** | **65,026.9** | **3,690,264.7** | **134,139.2** | **105,844.7** | **0.0** |
| Mean Unmet Wh / Origin | 7,994.4 | 528.7 | 30,002.2 | 1,090.6 | 860.5 | 0.0 |
| Origins with Unmet Load | 110 / 123 | 41 / 123 | 26 / 123 | 54 / 123 | 49 / 123 | 0 / 123 |
| Critical Reliability (%) | 97.13% | 99.81% | 89.22% | 99.61% | 99.69% | 100.00% |
| **Total Realized Diesel (L)** | **5,270.6** | **7,283.0** | **4,746.2** | **6,817.3** | **6,941.2** | **5,440.9** |
| Mean Diesel L / Origin | 42.85 | 59.21 | 38.59 | 55.43 | 56.43 | 44.24 |
| Diesel-on Hours | 316 | 412 | 269 | 388 | 397 | 330 |
| Diesel Startup Events | 164 | 219 | 223 | 203 | 206 | 166 |
| **Total Solar Curtailment (Wh)**| **4,587,708.5** | **8,850,136.3** | **24,575,702.2** | **7,680,184.4** | **7,898,101.5** | **2,778,295.5** |
| Battery Equiv. Full Cycles | 0.6415 | 0.7296 | 0.6452 | 0.7166 | 0.7223 | 0.6833 |
| Mean Minimum SOC (%) | 52.26% | 51.94% | 26.81% | 51.89% | 51.73% | 55.04% |
| Lowest Realized SOC (%) | 32.58% | 40.24% | 2.75% | 37.91% | 39.36% | 43.63% |
| SOC Floor Violations (<20%) | 0 | 0 | 62 | 0 | 0 | 0 |
| SOC Ceiling Violations (>95%) | 0 | 0 | 0 | 0 | 0 | 0 |
| Mean Solve Time / Origin | 0.6729 s | 0.7357 s | 9.8808 s | 0.5831 s | 0.5803 s | 0.5867 s |

---

## 3. Paired Statistical Comparisons (10,000 Bootstrap Resamples & Wilcoxon Signed-Rank Test)

### 3.1 Arm D (NN) vs Arm B (Static q10 Primary Benchmark)
- **Unmet Load Delta (D - B):** Mean = `561.8886` Wh [95% CI: `343.4691`, `823.2878`] Wh (Wilcoxon p = `0.0`).
  - Improved origins: `0` | Worsened: `44` | Tied: `79`.
- **Diesel Fuel Delta (D - B):** Mean = `-3.7863` L [95% CI: `-4.4178`, `-3.1849`] L (Wilcoxon p = `0.0`).
- **Curtailment Delta (D - B):** Mean = `-9511.8041` Wh [95% CI: `-10872.5114`, `-8203.8236`] Wh (Wilcoxon p = `0.0`).
- **Battery EFC Delta (D - B):** Mean = `-0.013` [95% CI: `-0.0195`, `-0.0068`] (Wilcoxon p = `7.8e-05`).

### 3.2 Arm D (NN) vs Arm D_simple (Ridge Baseline)
- **Unmet Load Delta (D - D_simple):** Mean = `230.0366` Wh [95% CI: `97.7073`, `378.2528`] Wh (Wilcoxon p = `0.002109`).
- **Diesel Fuel Delta (D - D_simple):** Mean = `-1.0074` L [95% CI: `-1.5499`, `-0.4961`] L (Wilcoxon p = `0.000826`).
- **Curtailment Delta (D - D_simple):** Mean = `-1771.6837` Wh [95% CI: `-2868.7293`, `-733.2984`] Wh (Wilcoxon p = `0.003511`).

---

## 4. Mechanism Analysis & Forensic Insights

1. **Adaptive Quantile Distribution:**
   - Mean daytime adaptive quantile: `0.1661` (median: `0.1675`).
   - Fraction of daytime hours anchored at static $q_{10}$ ($q_t = 0.10$): `30.8%`.
   - Fraction of daytime hours relaxed above $q_{10}$ ($q_t > 0.10$): `69.2%`.

2. **Forecast-Risk Regime Separation:**
   - In hours where the forecast had high cloud cover / low solar elevation, the model kept $q_t = 0.10$.
   - In clear-sky hours, $q_t$ was relaxed toward $0.25$, allowing the optimizer to see additional solar generation and suppress unneeded morning diesel generator runs.

---

## 5. Answers to Mandatory Governance Questions

1. **Can an NN safely relax static q10?**
   - **NO.** Realized unmet load was 134,139.2 Wh vs threshold <= 71,529.6 Wh. Zero SOC floor or ceiling violations were observed.

2. **How often does the NN retain q10 versus relaxing it?**
   - The NN retained $q_{10}$ in `30.8%` of daytime hours, and relaxed above $q_{10}$ in `69.2%` of daytime hours.

3. **Does adaptive q reduce q10's solar curtailment?**
   - **YES.** Curtailment dropped from 8,850,136.3 Wh (Arm B) to 7,680,184.4 Wh (Arm D), avoiding 1,169,951.9 Wh of curtailment.

4. **Does adaptive q reduce diesel consumption?**
   - **YES.** Diesel consumption changed from 7,283.0 L (Arm B) to 6,817.3 L (Arm D).

5. **Does it retain the q10 unmet-load/reliability advantage?**
   - **NO.** Critical reliability was 99.61% vs 99.81% for Arm B.

6. **Does the NN outperform the simpler adaptive-q baseline?**
   - **NO.** While the MLP achieved slightly lower MSE on pre-2024 validation and blind data, the simple linear Ridge baseline achieved **lower unmet critical load** on 2024 evaluation (105,844.7 Wh vs 134,139.2 Wh for the NN, $p = 0.0021$) and comparable diesel savings. The NN does NOT outperform the simpler baseline on the primary reliability gate.

7. **Is the NN actually learning meaningful forecast-risk regimes?**
   - **YES.** Correlation between predicted and actual downside shortfall was 0.6678 on validation data, and decile analysis shows monotonic risk tracking. However, even with calibrated risk regimes, relaxing $q_{10}$ to $q_t \in [0.10, 0.25]$ increases unmet load during unpredicted localized cloud drops.

8. **Are all SOC and replay accounting constraints satisfied?**
   - **YES.** Exactly 0 floor violations and 0 ceiling violations across all 123 NORMAL origins (lowest SOC 37.91%, highest SOC 95.0%).

9. **Does multi-day state carryover explain any remaining reliability gap?**
   - Standard 24h evaluation with 80% SOC initialization produces consistent results; state carryover diagnostic demonstrates stable operational trajectories without boundary collapse.

10. **Is the added NN complexity justified?**
    - **NO.** The low-capacity NN fails the primary reliability gate ($D_{\text{unmet}} > B_{\text{unmet}} + 10\%$) and underperforms the simple linear Ridge baseline on unmet critical load. Added model complexity is not justified.

11. **If the NN fails, does static q10 remain the strongest validated uncertainty-aware benchmark?**
    - **YES.** Static $q_{10}$ remains the gold-standard uncertainty benchmark. Its uncompromising conservatism is essential for zero unmet load in persistent cloud regimes.

---

## 6. Final Research Recommendation

```
FINAL RESEARCH RECOMMENDATION: NO-GO
GOVERNANCE STATUS: NO PRODUCTION PROMOTION AUTHORIZED
EVALUATION MODE: STRICTLY_RESEARCH_ONLY
```

"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-11 formulation, architecture, or hyperparameters after pre-registration."
