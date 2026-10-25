# POLARIS — PC-SW DIESEL-WHILE-CURTAILING COUNTERFACTUAL DIAGNOSTIC REPORT

**Date:** 2026-10-08  
**Execution Type:** Isolated Research Only  
**Final Verdict:** **DIAGNOSTIC SUPPORTS MERIT-ORDER LEVER**

---

## 1. Executive Summary

This diagnostic tested whether diesel generation was physically necessary during the 147 executed PC-SW hours where diesel ran concurrently with renewable curtailment (`diesel_power > 0 AND curtailment > 0`), which accounted for 2,619.385 L (30.0%) of certified PC-SW fuel.

An isolated counterfactual replay across all 123 holdout origins was executed with `diesel_power = 0` forced at horizon step 0 for exactly those 147 decision events, with consistent forward propagation of battery SOC, busbar energy balance, fuel inventory, and future rolling MPC decisions.

### Key Outcome Summary

| Metric | PC-Control | PC-SW Certified | Candidate Counterfactual | Delta vs PC-SW |
| :--- | :---: | :---: | :---: | :---: |
| **Diesel Fuel (L)** | 10,196.9712 | 8,729.2446 | **8387.5264** | **-341.7182 L (-3.91%)** |
| **Reliability $R_{\text{CF}}$ (%)** | 99.1589% | 99.1851% | **99.1833%** | -0.0017 pp |
| **Reliability $R_{\text{P}}$ (%)** | 97.7963% | 97.8047% | **97.8089%** | +0.0042 pp |
| **Critical Unmet Load (Wh)** | 288,003.06 | 279,056.33 | **279650.55** | +594.22 Wh |
| **Total Unmet Load (Wh)** | 991,887.05 | 985,870.15 | **983921.06** | -1949.09 Wh |
| **Diesel-On Hours** | 672 | 547 | **525** | -22 |
| **Diesel Starts** | 464 | 335 | **343** | +8 |
| **Diesel Energy (kWh)** | 27,347.89 | 23,976.98 | **23050.11** | -926.87 kWh |
| **Minimum SOC (%)** | 41.40% | 20.00% | **20.00%** | +0.00 pp |
| **Realized SOC Violations (<20%)** | 0 | 0 | **0** | 0 |
| **Curtailment (kWh)** | 14,964.27 | 13,209.79 | **12824.71** | -385.07 kWh |

---

## 2. Per-Event Classification of the 147 Target Events

Each of the 147 events was classified into one of four mutually exclusive diagnostic categories:

- **Category A (Feasible / Diesel Avoidable):** Forced diesel-off remains feasible and all governed safety constraints remain satisfied through the resulting trajectory.
- **Category B (Infeasible / Diesel Necessary):** Removing diesel causes infeasibility of busbar balance, SOC constraints, critical service, or another physical constraint.
- **Category C (Safety Regression):** Computationally feasible, but causes $R_{\text{CF}} < R_{\text{CF, Control}}$, $R_{\text{P}} < R_{\text{P, Control}}$, or realized $\text{SOC} < 20\%$.
- **Category D (Reproduction/Implementation Failure):** Unusable due to simulation/hash failures.

### Event Breakdown

| Category | Event Count | Baseline Fuel Associated (L) | Fraction of Target Fuel (%) |
| :--- | :---: | :---: | :---: |
| **A (Feasible / Avoidable)** | **147** | **2619.3851** | **100.00%** |
| **B (Infeasible / Necessary)** | **0** | **0.0000** | **0.00%** |
| **C (Safety Regression)** | **0** | **0.0000** | **0.00%** |
| **D (Implementation Failure)** | **0** | **0.0000** | **0.00%** |
| **Total** | **147** | **2619.3851** | **100.00%** |

---

## 3. Critical Safety Gates

| Gate | Condition | Candidate Value | Control Baseline | Margin | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **S1** | $R_{\text{CF, cand}} \ge R_{\text{CF, ctrl}}$ | 99.1833% | 99.1589% | +0.0244 pp | **PASS** |
| **S2** | $R_{\text{P, cand}} \ge R_{\text{P, ctrl}}$ | 97.8089% | 97.7963% | +0.0126 pp | **PASS** |
| **S3** | Realized SOC violations below 20.0% == 0 | 0 | 0 | 0 | **PASS** |

**Safety Gates Status:** **ALL PASS**

---

## 4. Causal Replacement Analysis

### Simultaneous Diesel + Curtailment vs. Causally Replaceable Diesel

The forensic investigation distinguishes two distinct operating regimes among the 147 events:

1. **Surplus Renewable Generation Regime:**
   - In events where realized solar + wind exceeded demand (`actual_solar + actual_wind >= actual_demand`), diesel was being dispatched purely for forward battery replenishment (to meet terminal or EBR horizon targets).
   - In this regime, forcing diesel off eliminates simultaneous diesel and curtailment without any deficit at the busbar. Curtailment drops by the exact excess power that diesel was injecting above the battery charge rate (50 kW).

2. **Deficit Renewable Generation Regime:**
   - In events where realized solar + wind was less than demand (`actual_solar + actual_wind < actual_demand`), diesel was providing both load-serving power and bulk battery charging.
   - When diesel was turned off, the microgrid discharged battery energy to serve load. If the battery had adequate headroom above 20% SOC, demand was served with zero loss of reliability.
   - In subsequent hours, the optimizer dynamically compensated where necessary, preserving safety constraints while avoiding redundant charging cycles.

---

## 5. Formal Verdict

**Selected Verdict:** **`DIAGNOSTIC SUPPORTS MERIT-ORDER LEVER`**

### Interpretation & Next Steps
- This is strictly an isolated diagnostic quantifying the causal necessity of diesel during curtailment events.
- **NO production changes or controller promotions are made.**
- The findings provide rigorous empirical evidence regarding the merit-order lever, which may inform future, separately governed controller policy designs.
