# POLARIS — PC-SW ONLINE REALIZED-RENEWABLE RECAPTURE REPORT

**Date:** 2026-10-08  
**Execution Type:** Isolated Research Only  
**Final Verdict:** **`FAIL — SEMANTIC/IDENTITY CHECK`**

---

## 1. Executive Summary

This experiment executed CC's "Online Realized-Renewable Recapture" heuristic across all 123 holdout origins (2,952 hourly cycles) of the certified POLARIS benchmark.

The policy was evaluated **generically at decision time at EVERY executed hour**; it **did NOT replay or reference the historical 147-event list**.

### Policy Rule
At every executed hour:
- renewable_used_by_plan = p_chg_plan + demand_realized - wind_realized - p_dis_plan - p_diesel_plan
- recapture = min(p_diesel_plan, max(0.0, solar_realized - renewable_used_by_plan))
- p_diesel_actual = p_diesel_plan - recapture

---

## 2. Key Outcome Summary

| Metric | PC-Control | PC-SW Certified Baseline | Candidate Recapture | Delta vs. PC-SW |
| :--- | :---: | :---: | :---: | :---: |
| **Diesel Fuel (L)** | 10,196.9712 | 8,729.2446 | **8624.7060** | **-104.5386 L (-1.20%)** |
| **Reliability R_CF (%)** | 99.1589% | 99.1851% | **99.1828%** | -0.0022 pp |
| **Reliability R_P (%)** | 97.7963% | 97.8047% | **97.8148%** | +0.0102 pp |
| **Critical Unmet Load (Wh)** | 288,003.06 | 279,056.33 | **279820.38** | +764.05 Wh |
| **Total Unmet Load (Wh)** | 991,887.05 | 985,870.15 | **979731.12** | -6139.03 Wh |
| **Diesel-On Hours** | 672 | 547 | **561** | +14 |
| **Diesel Starts** | 464 | 335 | **333** | -2 |
| **Diesel Energy (kWh)** | 27,347.89 | 23,976.98 | **23278.83** | -698.16 kWh |
| **Minimum Realized SOC (%)** | 41.40% | 20.00% | **20.00%** | +0.00 pp |
| **SOC Violations (<20%)** | 0 | 0 | **0** | 0 |
| **Curtailment (kWh)** | 14,964.27 | 13,209.79 | **12283.22** | -926.57 kWh |

---

## 3. Semantic & Primary Identity Check Audit

The governance contract required verifying that the policy acted strictly as an energy-source substitution without altering SOC trajectory, battery charge, discharge, or served load.

### Audit Findings

| Variable | Prescribed Condition | Measured Max Absolute Error | Status |
| :--- | :---: | :---: | :---: |
| **Realized SOC (SOC[t])** | <= 0.001 pp | **44.7700 pp** | **FAIL** |
| **Battery Energy (E_next[t])** | <= 1.0 Wh | **89537.7800 Wh** | **FAIL** |
| **Battery Charge (p_chg[t])** | <= 0.001 W | **50000.0000 W** | **FAIL** |
| **Battery Discharge (p_dis[t])** | <= 0.001 W | **17825.9900 W** | **FAIL** |
| **Served Load** | <= 0.001 W | **8926.7400 W** | **FAIL** |
| **Critical Served Load** | <= 0.001 W | **2526.7400 W** | **FAIL** |
| **Unmet Load** | <= 0.001 W | **8926.7400 W** | **FAIL** |

### Mathematical Root Cause of Identity Divergence
1. **Planned vs. Hardware Charge Capability:**
   - In the physical executor (ResearchRealizationExecutor), the battery charges up to available surplus power (p_chg_realized = min(surplus, max_charge_capability)), irrespective of the plan's advisory p_chg_plan.
   - Because realized demand frequently drops below forecast demand, baseline realization utilized surplus power to charge the battery above p_chg_plan.
2. **False Curtailment Inference:**
   - The formula renewable_used_by_plan = p_chg_plan + demand_realized - wind_realized - p_dis_plan - p_diesel_plan implicitly assumed that all generation beyond p_chg_plan was curtailed.
   - Consequently, the formula triggered in hours where baseline curtailment was zero (e.g. Origin 1, Hours 2, 3, 8), reducing diesel generation when no excess renewable power existed.
   - The diesel reduction was absorbed by reducing battery charging, leading to substantial cumulative SOC divergence (44.77 pp max drift) and trajectory decoupling.
3. **Recapture Check Failure:**
   - For triggered hours, the identity candidate_curtailment = baseline_curtailment - recapture failed (max error = 24607.66 W), demonstrating that recaptured energy did not come purely from curtailed renewables.

---

## 4. Retrospective 147-Event Overlap Analysis

*Conducted descriptive analysis after full campaign completion:*

- **Historical 147 Events Baseline Fuel:** **2619.3851 L**
- **Triggers Overlapping with 147 Population:** **132 / 147**
- **Triggers Outside Historical 147 Population:** **341**
- **Total Recapture Energy in 147 Events:** **842.96 kWh**
- **Total Recapture Energy Outside 147 Events:** **1008.58 kWh**

---

## 5. Critical Safety Gates Evaluation

| Gate | Condition | Candidate Value | Control Reference | Margin | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **S1** | R_CF_cand >= R_CF_ctrl | 99.1828% | 99.1589% | +0.0239 pp | **PASS** |
| **S2** | R_P_cand >= R_P_ctrl | 97.8148% | 97.7963% | +0.0185 pp | **PASS** |
| **S3** | Realized SOC violations below 20.0% == 0 | 0 | 0 | 0 | **PASS** |

---

## 6. Anti-Hindsight Audit

- **Audit Status:** **PASS**
- Verified that all trigger evaluations used strictly CURRENT_REALIZED, CURRENT_PLAN, or CARRIED_STATE.
- Zero future observations, zero future plan steps, and zero references to historical event IDs were utilized during decision time.

---

## 7. Formal Verdict

**Selected Verdict:** **`FAIL — SEMANTIC/IDENTITY CHECK`**

> **Declaration:**  
> This experiment tested the rule generically at decision time across all 123 origins; it did not replay the 147-event list.  
> The candidate failed the governed Primary Identity and Semantic Recapture checks because the formula's planned-charge assumption diverted power from battery storage rather than exclusively recapturing curtailed energy.  
> **No production changes are made, no controllers are promoted, and no claims of production policy readiness are asserted.**
