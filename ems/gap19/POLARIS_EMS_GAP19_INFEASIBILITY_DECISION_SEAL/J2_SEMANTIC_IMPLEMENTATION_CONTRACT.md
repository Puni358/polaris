# POLARIS EMS GAP19 — J2 SEMANTIC IMPLEMENTATION CONTRACT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Contract Status**: `SEALED_GOVERNANCE_CONTRACT`  

---

## 1. Role & Intent of Objective $J2$

Objective $J2$ is defined as the **Governed Reserve Shortfall Wh** (pointwise maximum envelope of 6-hour EBR lookahead requirement and 24-hour terminal reserve requirement):
$$J2 = \sum_{t=0}^{23} s_{\text{J2}}[t]$$

In accordance with **Decision D1**, $J2$ functions under a **HYBRID / MODE-DEPENDENT** contract:
1. **In NORMAL Mode**: $J2$ serves as a soft objective penalty at Priority 3 ($J1 \succ J2 \succ J3 \succ J4$) in the lexicographic hierarchy. It provides feedback to the controller regarding the magnitude of reserve envelope shortfall.
2. **Boundary with Emergency Authority**: A non-zero shortfall ($J2 > 0$) indicates that the desired reserve envelope could not be fully maintained by normal MPC. However, $J2 > 0$ **does NOT declare an emergency** and does NOT alter system operating mode.
3. **Information Handoff**: The value of $J2$ and individual slack variables $s_{\text{J2}}[t]$ are logged in `DispatchPlan` metadata as telemetry inputs to the Emergency Condition Detector (ECD).

---

## 2. Mathematical Contract Rules

* **Priority Order**: Priority 3 ($J1 \succ J2 \succ J3 \succ J4$).
* **Lexicographic Separation**: Critical load serving ($J1$) strictly dominates reserve shortfall penalty ($J2$). The optimizer must prefer consuming reserve ($J2 > 0$) over shedding critical load ($J1 > 0$).
* **Non-Emergency Guarantee**: Evaluating $J2 > 0$ during optimization MUST NOT trigger mode switches, operator escalation, or load shedding within the solver.

---

## 3. Implementation Restrictions

* Do NOT invent hardcoded numerical reserve targets.
* Do NOT treat $J2$ as an emergency trip mechanism.
* Do NOT alter `gap19_highs_native.py` until authorized by future implementation gate.
