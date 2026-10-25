# POLARIS — BRICK T1: NARROWED TEMPORAL CHARGING TIE-BREAK CAMPAIGN REPORT

**Date:** 2026-10-08  
**Campaign Type:** Isolated 123-Origin Closed-Loop Governed Research Campaign  
**Candidate Policy:** Brick T1 — Narrowed Temporal Charging Tie-Break  
**Final Classification:** **`C`** (Safety Failure: Gate S2 Proportional Reliability Fail)

---

## 1. Executive Summary

This campaign evaluated **Brick T1: Narrowed Temporal Charging Tie-Break** across all 123 holdout origins (2,952 hourly execution cycles) under rolling closed-loop MPC execution.

The candidate policy was applied at every rolling resolve where $J_2^* == 0$. The solved binary vectors ($\mathbf{u}_{\text{diesel}}^*, \mathbf{v}_{\text{start}}^*$) were hard-pinned, and the problem was re-solved with the temporal charging objective $\min \sum_t w[t] p_{\text{chg}}[t]$ placed strictly below $J_4$:
$$\text{Priority Hierarchy: } J_1 > J_{\text{NC}} > J_2 > J_3 > J_4 > J_{\text{tie}}$$

### Core Campaign Findings:
1. **Solve-Level Invariance Audit: 100% PASS.** Across all 2,941 resolves where T1 was applied, $J_1$, $J_{\text{NC}}$, $J_2$, $J_3$, $\mathbf{u}_{\text{diesel}}$, and $\mathbf{v}_{\text{start}}$ remained bit-identical to the baseline solve (0 invariance failures).
2. **Tie-Break Reallocation: Active.** In 1,382 resolves (47.0% of applied resolves), charging profiles reallocated, yielding a **-17.93% reduction in the aggregate tie objective** (from 104,881,600.59 to 86,074,150.28 W·steps).
3. **Closed-Loop Feedback Divergence (Negative Realized Fuel Effect):** Despite open-loop temporal deferral, realized closed-loop fuel consumption **increased by +241.61 L** (+2.77% vs PC-SW baseline), with total fuel reaching **8,970.85 L**.
4. **Safety Gate S2 Failure:** Proportional reliability dropped by **-0.0015 pp** below the PC-Control baseline ($97.7948\%$ vs $97.7963\%$), violating Gate S2.
5. **Statistical Rejection:** Paired Wilcoxon $p = 0.9995$, with BCa 95% bootstrap confidence interval $[-3.2630, -0.6911]\text{ L/origin}$, confirming a statistically significant fuel increase.

---

## 2. Campaign Outcome Summary

| Metric | PC-Control Reference | PC-SW Baseline | Candidate T1 | Delta vs PC-SW | Status / Evaluation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Diesel Fuel (L)** | 10,196.9712 | 8,729.2446 | **8,970.8523** | **+241.6077 L (+2.77%)** | Higher Fuel |
| **Savings vs PC-Control (%)** | 0.00% | 14.39% | **12.02%** | -2.37 pp | Diminished Saving |
| **Reliability $R_{\text{CF}}$ (%)** | 99.1589% | 99.1851% | **99.1746%** | -0.0105 pp | **PASS (S1: $\ge 99.1589\%$)** |
| **Reliability $R_{\text{P}}$ (%)** | 97.7963% | 97.8047% | **97.7948%** | -0.0099 pp | **FAIL (S2: $< 97.7963\%$)** |
| **Critical Unmet Load (Wh)** | 288,003.06 | 279,056.33 | **282,652.53** | +3,596.20 Wh | Increased Unmet |
| **Total Unmet Load (Wh)** | 991,887.05 | 985,870.15 | **988,583.63** | +2,713.48 Wh | Increased Unmet |
| **Diesel-On Hours** | 672 | 547 | **514** | -33 hours | Fewer On-Hours |
| **Diesel Starts** | 464 | 335 | **344** | +9 starts | More Short Cycles |
| **Diesel Energy (kWh)** | 27,347.89 | 23,976.98 | **25,603.41** | +1,626.43 kWh | Higher Output Energy |
| **Minimum Realized SOC (%)** | 41.40% | 20.00% | **20.00%** | +0.00 pp | **PASS (S3: $\ge 20.00\%$)** |
| **SOC Violations (<20%)** | 0 | 0 | **0** | 0 | **PASS** |
| **Fuel Inventory Violations** | 0 | 0 | **0** | 0 | **PASS** |
| **Realized Curtailment (kWh)** | 14,964.27 | 13,209.79 | **14,417.31** | +1,207.52 kWh | Higher Curtailment |
| **Battery Throughput (kWh)** | — | 42,589.92 | **45,117.81** | +2,527.89 kWh | Increased Cycling |

---

## 3. Statistical Testing Results (vs PC-SW Baseline)

- **Mean Paired Saving:** **-1.9643 L/origin**
- **Median Paired Saving:** **-1.7620 L/origin**
- **BCa 95% Bootstrap Confidence Interval:** **[-3.2630, -0.6911] L/origin**
- **Paired Wilcoxon Test (one-sided greater):** **$W = 2,363.0, p = 0.9995$**
- **Statistically Supported Saving:** **False**

---

## 4. Resolve-Level Invariance & Tie-Break Audit

- **Total Resolves Evaluated:** **2,952**
- **T1 Applied Resolves ($J_2^* == 0$):** **2,941** (99.6%)
- **T1 Skipped Resolves ($J_2^* > 0$):** **11** (0.4%)
- **Resolves where $p_{\text{chg}}$ Changed:** **1,382** (47.0% of applied resolves)
- **Solve-Level Invariance Errors:** **0** (100% verified: $J_1, J_{\text{NC}}, J_2, J_3, \mathbf{u}_{\text{diesel}}, \mathbf{v}_{\text{start}}$ identical)
- **Aggregate Tie Objective Value:**
  - Before T1: **104,881,600.59 W·steps**
  - After T1: **86,074,150.28 W·steps**
  - Reduction: **-18,807,450.31 W·steps (-17.93%)**

### Distribution of Within-Run Charging Shifts:
- Resolves with Hour-0 Charge Shifted Later ($\Delta p_{\text{chg}}[0] < -0.1\text{ W}$): **60 resolves** (Max shift: $-43,817.28\text{ W}$)
- Resolves with Hour-0 Charge Shifted Earlier ($\Delta p_{\text{chg}}[0] > +0.1\text{ W}$): **330 resolves** (Max shift: $+50,000.00\text{ W}$)
- Resolves with Invariant Hour-0 Charge ($|\Delta p_{\text{chg}}[0]| \le 0.1\text{ W}$): **2,551 resolves**

---

## 5. Physical Root Cause Analysis of Policy Failure

Why did an open-loop tie-break that weakly preferred later charging increase realized fuel consumption and fail proportional reliability?

1. **Within-Run Asymmetry & Reallocation Dynamics:**  
   Because the objective $\min \sum_t (t_{\text{end}} - t) p_{\text{chg}}[t]$ minimizes the weighted sum across *all* hours in a diesel run, the optimizer frequently achieved a lower weighted cost by shifting charging across later runs or balancing between multiple runs in the 24-hour horizon. In 330 resolves, Hour-0 charging was actually increased to permit larger reductions in multi-hour runs later in the horizon.
2. **Closed-Loop Feedback Depletion:**  
   When charging was postponed out of Hour 0 into Hour 1 or 2, the microgrid operated Hour 0 with lower battery reserve. In subsequent rolling cycles where forecast solar/wind failed to materialize at the expected hour, the depleted battery state forced additional diesel commitments in later hours (+9 diesel starts, +1,626 kWh diesel energy).
3. **Curtailment Inefficiency:**  
   Postponed battery charging shifted battery top-up into hours closer to morning solar ramp, resulting in $+1,207.52\text{ kWh}$ of additional renewable curtailment when solar arrived with a full battery.

---

## 6. Final Classification

**Classification:** **`C`**  
*(Gate S2 Proportional Reliability dropped below PC-Control reference: $97.7948\% < 97.7963\%$, $\Delta = -0.0015\text{ pp}$).*

T1 123-ORIGIN CAMPAIGN COMPLETE — NO PRODUCTION PROMOTION.
