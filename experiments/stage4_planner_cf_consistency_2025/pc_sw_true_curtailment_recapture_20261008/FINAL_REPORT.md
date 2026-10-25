# POLARIS — RULE D: TRUE-CURTAILMENT DIESEL RECAPTURE REPORT

**Date:** 2026-10-08  
**Execution Type:** Isolated Research Only  
**Final Verdict:** **`FAIL — SEMANTIC/IDENTITY CHECK`**

---

## 1. Executive Summary

This experiment executed CC-validated **Rule D: True-Curtailment Diesel Recapture** across all 123 holdout origins (2,952 hourly execution cycles) of the certified POLARIS benchmark.

> **Declaration:**  
> Rule D was evaluated generically at every executed hour using the executor's native physical curtailment calculation and did not use the historical 147-event list.

### Rule D Semantics
At every executed hour:
1. **Pass 1:** Native execution with original plan ($p_{\text{diesel, plan}}$) determines physical curtailment.
2. **Evaluation:** If native curtailment $> 10^{-4}\text{ W}$ and diesel $> 10^{-4}\text{ W}$, calculate $\delta = \min(\text{diesel}, \text{curtailment})$.
3. **Pass 2:** Re-run native execution using $p_{\text{diesel, final}} = \text{diesel} - \delta$. The recovered energy is supplied by renewable power that otherwise would have been curtailed.
4. **State Carryover:** Carry the resulting `next_state` forward into the subsequent rolling MPC cycle.

---

## 2. Key Outcome Summary

| Metric | PC-Control | PC-SW Certified Baseline | Rule D Candidate | Delta vs. PC-SW |
| :--- | :---: | :---: | :---: | :---: |
| **Diesel Fuel (L)** | 10,196.9712 | 8,729.2446 | **8,672.6241** | **-56.6205 L (-0.65%)** |
| **Reliability R_CF (%)** | 99.1589% | 99.1851% | **99.1851%** | +0.0000 pp |
| **Reliability R_P (%)** | 97.7963% | 97.8047% | **97.8116%** | +0.0070 pp |
| **Critical Unmet Load (Wh)** | 288,003.06 | 279,056.33 | **279,056.33** | +0.00 Wh |
| **Total Unmet Load (Wh)** | 991,887.05 | 985,870.15 | **982,478.27** | -3,391.88 Wh |
| **Diesel-On Hours** | 672 | 547 | **554** | +7 |
| **Diesel Starts** | 464 | 335 | **333** | -2 |
| **Diesel Energy (kWh)** | 27,347.89 | 23,976.98 | **23,610.50** | -366.49 kWh |
| **Minimum Realized SOC (%)** | 41.40% | 20.00% | **20.00%** | +0.00 pp |
| **SOC Violations (<20%)** | 0 | 0 | **0** | 0 |
| **Curtailment (kWh)** | 14,964.27 | 13,209.79 | **12,484.74** | -725.05 kWh |

---

## 3. Primary Identity Gates Audit & Failure Root Cause

The governance specification strictly required that Rule D preserve exact battery state, SOC, charge, discharge, and served load across all 2,952 executed hours against the certified baseline trajectory.

### Identity Verification Results Against Baseline

| Variable | Prescribed Tolerance | Measured Max Absolute Error | Status |
| :--- | :---: | :---: | :---: |
| **Realized SOC (SOC[t])** | <= 0.01 pp | **28.9700 pp** | **FAIL** |
| **Battery Energy (E_next[t])** | <= 15.0 Wh | **57,947.43 Wh** | **FAIL** |
| **Battery Charge (p_chg[t])** | <= 0.0001 W | **44,640.22 W** | **FAIL** |
| **Battery Discharge (p_dis[t])** | <= 0.0001 W | **17,825.99 W** | **FAIL** |
| **Served Load** | <= 0.0001 W | **1,912.59 W** | **FAIL** |
| **Critical Served Load** | <= 0.0001 W | **0.0000 W** | **PASS** |
| **Unmet Load** | <= 0.0001 W | **1,912.59 W** | **FAIL** |

**Identity Gate Status:** **FAIL** (Divergence observed across 82 downstream hours).

### Root Cause of Trajectory Divergence: Closed-Loop Fuel Feedback
1. **Local (Single-Step) Invariance:** Within the triggered hour itself (Pass 1 vs. Pass 2), Rule D preserves exact battery charge, battery discharge, battery energy, and served load bit-identically ($< 10^{-11}\text{ W}$ error).
2. **Fuel State Interaction:** Because diesel was reduced during triggered hours, the candidate accumulated fuel savings ($F_{\text{rem, candidate}}[t] > F_{\text{rem, baseline}}[t]$).
3. **Downstream MPC Divergence:** In subsequent hours (e.g., Origin 2 Hour 20, Origin 9 Hour 20, Origin 10 Hour 18), the baseline PC-SW controller had exhausted its fuel budget, rendering the diesel hour-0 feasibility constraint ($5 u_{\text{diesel}}[0] + 0.00025 p_{\text{diesel}}[0] \le F_{\text{rem}}$) active and preventing baseline from running diesel.
4. **Altered Candidate Dispatch:** The candidate controller, possessing additional unburned fuel saved by Rule D, found diesel dispatch feasible and turned on diesel in those downstream hours.
5. **Coupling Violation:** Consequently, while Rule D is non-invasive open-loop, under true closed-loop rolling execution with fuel-inventory tracking, fuel savings alter the downstream feasible set of the MPC planner, causing closed-loop trajectories to diverge from baseline.
6. Per governance instructions: *"If identity fails: classify implementation as FAILED/BLOCKED and stop before interpreting fuel savings."*

---

## 4. Physical & Recapture Checks

- **Candidate Busbar Balance Error:** **0.000000 W** (Max error <= 1e-4 W: PASS)
- **Local Recapture Bounds ($0 \le \delta \le p_{\text{diesel}}$):** **PASS**
- **Candidate Internal Diesel Recapture Identity:** **PASS** (Max error $= 1.45 \times 10^{-11}\text{ W}$)
- **Candidate vs. Baseline Global Trajectory Identity:** **FAIL** (Due to closed-loop fuel feedback divergence across 82 hours)

---

## 5. Retrospective 147-Event Overlap Analysis

*Descriptive analysis after full campaign completion:*

- **Historical 147 Events Baseline Fuel:** **2,619.3851 L**
- **Rule D Triggers Overlapping with Historical 147:** **146 / 147**
- **Rule D Triggers Outside Historical 147:** **3** (Total triggers: 149)
- **Total Campaign Recapture Energy:** **743.68 kWh**
- **Total Campaign Marginal Fuel Saved:** **185.9210 L**

---

## 6. Critical Safety Gates & Anti-Hindsight Audit

### Critical Safety Gates Against PC-Control
- **S1 (R_CF >= 99.1589%):** **PASS** (99.1851% >= 99.1589%, delta = +0.0262 pp)
- **S2 (R_P >= 97.7963%):** **PASS** (97.8116% >= 97.7963%, delta = +0.0153 pp)
- **S3 (Zero realized SOC violations below 20%):** **PASS** (0 violations)
- **Fuel Inventory Gate (Zero violations):** **PASS** (0 violations)

### Anti-Hindsight Audit
- **Audit Status:** **PASS**
- Verified that all trigger evaluations used strictly `CURRENT_REALIZED`, `CURRENT_PLAN`, or `CARRIED_STATE`.
- Zero future observations, zero lookahead planning steps, and zero references to historical event IDs were used during execution.

---

## 7. Formal Verdict

**Selected Verdict:** **`FAIL — SEMANTIC/IDENTITY CHECK`**

> **Declaration:**  
> Rule D was evaluated generically at every executed hour using the executor's native physical curtailment calculation and did not use the historical 147-event list.  
> However, because Rule D reduced fuel consumption, the carried-forward fuel inventory relaxed downstream fuel constraints in later rolling MPC cycles, causing the candidate trajectory to diverge from the certified baseline in 82 hours (max SOC error 28.97 pp).  
> In accordance with the governance stop conditions (*"STOP if identity diverges... Do not improvise around any stop condition"*), the verdict is **`FAIL — SEMANTIC/IDENTITY CHECK`**.  
> **No production changes are made, no controllers are promoted, and no claims of production policy readiness are asserted. This is isolated research evidence only.**
