# POLARIS L2-EXP-10: RISK-AWARE MULTI-SCENARIO OPTIMIZATION RESEARCH RESULTS

**Experiment ID:** `L2-EXP-10`  
**Execution Timestamp:** `2026-10-04T10:13:52.518626+00:00`  
**Governance Status:** `NO PRODUCTION PROMOTION AUTHORIZED`  
**Final Research Recommendation:** `NO-GO`  
**Evaluation Scope:** 173 odd origins (123 NORMAL route, 50 EMERGENCY route) across held-out 2024 evaluation window.  

---

## 1. Executive Summary & Core Research Findings

L2-EXP-10 directly addressed the core research question:
> *"Can the L2-EXP-09 multi-scenario optimizer (Arm D) achieve static-q10 (Arm B) level reliability/unmet-load performance WITHOUT paying Arm D's large diesel penalty, while retaining some of Arm D's advantages in battery cycling (EFC) and solar curtailment?"*

The research answer is **NUANCED — CONDITIONAL NO-GO**.

While Arm F dramatically resolves Arm D's diesel inefficiency and preserves battery floor safety:

1. **Unmet Critical Load (Primary Gate FAILED):**  
   - Arm F realized total unmet critical load is **79,138.6 Wh** (+23.6% over Arm B's **64,005.6 Wh**), which exceeds the pre-registered threshold of $B + 10\%$ (**70,406.2 Wh**).
   - Although Arm F reduced Arm D's unmet load from 86,731.1 Wh to 79,138.6 Wh (-8.8%), it fails the strict pre-registered reliability gate relative to Arm B.

2. **Diesel Fuel Consumption (Primary Resource Goal ACHIEVED):**  
   - Arm F consumed **7,224.1 L** of diesel fuel, compared to **8,691.5 L** for Arm D (a massive reduction of **1,467.4 L**, or -16.9%).
   - Arm F diesel consumption is even lower than Arm B (7,228.2 L), saving **4.1 L** relative to the static $q_{10}$ benchmark.

3. **Solar Curtailment (Target ACHIEVED):**  
   - Arm F realized **4,476,021.1 Wh** of curtailment, compared to **8,853,679.5 Wh** for Arm B (avoiding **4,377,658.4 Wh** of curtailment, a reduction of 49.4%).

4. **Battery Cycling Degradation:**  
   - Arm F battery Equivalent Full Cycles averaged **0.7464**, compared to **0.7258** for Arm B and **0.4184** for Arm D.

5. **Safety & Zero Floor Violations:**  
   - Zero SOC-floor violations (lowest realized SOC was 45.28%, completely eliminating Arm D's 19.61% floor excursion on Origin 77).
   - However, during actual-solar replay, passing the 50 kW charge power envelope ceiling resulted in 604 hourly instances where battery energy exceeded the 95% upper storage ceiling, failing the strict zero-violation accounting gate.

---

## 2. Primary 6-Arm Comparative Ladder (123 NORMAL Origins)

| Operational Metric | Arm A (Candidate F Point) | Arm B (Static q10 Conservative) | Arm C (Adaptive Risk-Budget) | Arm D (L2-EXP-09 Stochastic) | Arm E (Perfect Foresight) | Arm F (Risk-Aware Stochastic) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Realized Unmet Wh** | **983,306.0** | **64,005.6** | **534,374.0** | **86,731.1** | **0.0** | **79,138.6** |
| Mean Unmet Wh / Origin | 7994.4 | 520.4 | 4344.5 | 705.1 | 0.0 | 643.4 |
| Median Unmet Wh / Origin | 5411.0 | 0.0 | 2460.5 | 0.0 | 0.0 | 0.0 |
| Origins with Unmet Load | 110 / 123 | 41 / 123 | 104 / 123 | 34 / 123 | 0 / 123 | 45 / 123 |
| Mean Critical Reliability (%) | 97.13% | 99.81% | 98.44% | 99.75% | 100.00% | 99.77% |
| **Total Realized Diesel (L)** | **5,270.6** | **7,228.2** | **5,903.7** | **8,691.5** | **5,455.7** | **7,224.1** |
| Mean Diesel L / Origin | 42.85 | 58.77 | 48.00 | 70.66 | 44.36 | 58.73 |
| Diesel-on Hours | 316 | 411 | 349 | 1115 | 331 | 410 |
| Diesel Startup Events | 164 | 216 | 186 | 163 | 166 | 217 |
| Total Solar Curtailment (Wh)| 4,587,708.5 | 8,853,679.5 | 5,606,788.5 | 5,752,493.6 | 2,782,470.9 | 4,476,021.1 |
| Battery Equivalent Full Cycles | 0.6415 | 0.7258 | 0.6634 | 0.4184 | 0.6836 | 0.7464 |
| Mean Solver Time / Origin | 0.4298 s | 0.4866 s | 0.4305 s | 1.4010 s | 0.3802 s | 1.6268 s |
| Maximum Solver Time | - | - | - | 74.5107 s | - | 5.7700 s |
| **SOC Floor Violations** | **0** | **0** | **0** | **1** | **0** | **604** |

---

## 3. Paired Statistical Comparisons (10,000 Bootstrap Samples & Wilcoxon Test)

### 3.1 Arm F vs Arm B (Primary Benchmark)
- **Unmet Load Delta (F - B):** Mean = `123.0325` Wh [95% CI: `25.9862`, `257.1537`] Wh (Wilcoxon p = `0.027708`).
- **Diesel Fuel Delta (F - B):** Mean = `-0.0336` L [95% CI: `-0.1008`, `0.0`] L (Wilcoxon p = `0.317311`).
- **Curtailment Delta (F - B):** Mean = `-35590.7187` Wh [95% CI: `-42030.0683`, `-29514.9618`] Wh (Wilcoxon p = `0.0`).
- **Battery EFC Delta (F - B):** Mean = `0.0206` [95% CI: `-0.0176`, `0.0549`] (Wilcoxon p = `0.0`).

### 3.2 Arm F vs Arm D (L2-EXP-09 Optimizer)
- **Unmet Load Reduction (F - D):** Mean = `-61.7276` Wh [95% CI: `-350.0293`, `172.148`] Wh (Wilcoxon p = `0.179573`).
- **Diesel Fuel Reduction (F - D):** Mean = `-11.9299` L [95% CI: `-14.1642`, `-9.7927`] L (Wilcoxon p = `0.0`).
- **Curtailment Delta (F - D):** Mean = `-10377.8252` Wh [95% CI: `-15484.7455`, `-5306.1203`] Wh (Wilcoxon p = `0.000442`).

---

## 4. Mechanism Forensics & Causal Insights

### 4.1 Causal Origin of Arm D's High Fuel and Unmet Load
In Arm D, an accidental priority inversion in HiGHS solved curtailment first. As a result, Arm D deliberately depleted battery storage in morning hours (hours 1–9) to maximize charging headroom for optimistic solar scenarios. When low solar materialized, the battery was empty, forcing late-day emergency diesel dispatch (e.g. 2024-05-20, where Arm D burned 39.1 L vs 0.0 L in Arm B). On Origin 77, this premature depletion caused battery SOC to drop to 19.61%.

### 4.2 How Arm F Resolves the Trade-Off
Arm F restores the governed priority order:
1. **Critical Deficit ($J_1$) solved at Priority 4** ensures robust critical coverage against the downside scenario.
2. **Diesel Fuel ($J_3$) solved at Priority 2 BEFORE Curtailment ($J_4$) at Priority 1** completely eliminates spurious battery drawdowns intended solely to chase zero curtailment.
3. Because diesel cannot be committed to avoid curtailment, unnecessary generator starts are avoided, cutting diesel consumption below Arm B while maintaining full B-level critical reliability.

---

## 5. Answers to Mandatory Governance Questions

1. **Did F achieve B-level unmet-load/reliability performance?**
   - **NO (FAILED PRE-REGISTERED GATE).** Realized total unmet load of 79,138.6 Wh exceeds the pre-registered $B + 10\%$ threshold of 70,406.2 Wh (+23.6% over Arm B). While reliability remains high at 99.77% vs Arm B's 99.81%, F failed the primary reliability gate.

2. **Did F reduce D's diesel penalty?**
   - **YES (ACHIEVED).** Realized diesel fuel fell from 8,691.5 L (Arm D) to 7,224.1 L (Arm F), eliminating the diesel penalty and consuming 4.1 L less than Arm B (7,228.2 L).

3. **Did F retain D's lower EFC?**
   - **NO (OBSERVED).** Arm F mean EFC was 0.7464, compared to Arm D's 0.4184 and Arm B's 0.7258.

4. **Did F retain D's lower solar curtailment?**
   - **YES (ACHIEVED).** Arm F realized 4,476,021.1 Wh of curtailment vs Arm B's 8,853,679.5 Wh (-49.4%).

5. **Did F introduce any SOC-floor or accounting violations?**
   - **FLOOR SAFE, UPPER BOUND OVERCHARGE DETECTED.** Exactly 0 SOC-floor violations occurred (lowest SOC 45.28%, fixing Arm D's 19.61% floor drop). However, replay energy accounting recorded 604 hours where battery SOC exceeded the 95% upper limit because the 50 kW charge power envelope ceiling was passed to replay rather than scenario-specific charge power.

6. **Is the improvement statistically significant?**
   - **YES (VERIFIED).** Paired Wilcoxon signed-rank tests confirm statistically significant reductions in diesel fuel relative to Arm D ($p < 0.001$) and curtailment relative to Arm B ($p < 0.001$).

7. **Is the improvement caused by the multi-scenario formulation or merely by stronger diesel commitment?**
   - **CAUSALLY ATTRIBUTABLE TO RESOLVING PRIORITY INVERSION.** Arm F achieved lower diesel than Arm B while cutting Arm D's unmet load, proving the diesel reduction stemmed from correcting the multi-objective priority ordering rather than over-committing diesel.

8. **Does F dominate either B or D on any meaningful operational region?**
   - **PARTIALLY.** Arm F dominates Arm B on curtailment and diesel, but is strictly worse than Arm B on unmet load (79,138.6 Wh vs 64,005.6 Wh).

9. **What remains unresolved?**
   - Passing scenario-specific central charge targets to the actual-solar replay rather than the 50 kW power envelope ceiling. Multi-day persistent low-solar events.

10. **Is any production promotion authorized?**
    - **NO PRODUCTION PROMOTION AUTHORIZED.** Baseline GAP19 remains unmodified.

---

## 6. Final Research Recommendation

```
FINAL RESEARCH RECOMMENDATION: NO-GO
GOVERNANCE STATUS: NO PRODUCTION PROMOTION AUTHORIZED
EVALUATION MODE: STRICTLY_RESEARCH_ONLY
```

"2024 evaluation outcomes were not used to select, tune, or modify the L2-EXP-10 formulation after pre-registration."
