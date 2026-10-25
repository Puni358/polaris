# POLARIS EMS GAP19 — HARD RELIABILITY SEMANTICS AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `GOVERNANCE_REQUIRED`  

---

## 1. Architectural Semantics Tracing

In POLARIS GAP19 Option B native HiGHS formulation, objectives are arranged in a strict lexicographic hierarchy:
$$J1 \text{ (Critical Load Deficit Wh)} \succ J2 \text{ (Reserve Shortfall Wh)} \succ J3 \text{ (Diesel Fuel L)} \succ J4 \text{ (Curtailment Wh)}$$

### Objective Priority Hierarchy
* **Priority 4 ($J1$)**: Critical unmet load ($W_{\text{unmet\_crit}}$). Must be $0.0\text{ Wh}$ whenever physically possible.
* **Priority 3 ($J2$)**: Governed reserve shortfall ($\sum s_{\text{J2}}$). Soft penalty measuring deviation from 6-hour EBR + 24-hour terminal reserve envelope.
* **Priority 2 ($J3$)**: Diesel fuel consumption.
* **Priority 1 ($J4$)**: Renewable curtailment.

---

## 2. Contradiction Between Hard vs Soft Reserve Intent

1. **Intended Soft Semantics of $J2$**:
   Because $J1$ is higher priority than $J2$, the system is designed to prefer violating reserve targets ($J2 > 0$) over shedding critical load ($J1 > 0$).
2. **Actual Codebase Implementation Conflict**:
   Because $s_{\text{J2}}$ is hard-bounded at `capacity_wh` ($200\text{ kWh}$), when required EBR reserve $E_{\text{EBR\_target}}$ exceeds $350\text{ kWh}$, the reserve constraint becomes a **hard constraint** that cannot be relaxed by $s_{\text{J2}}$.
3. **Cascading Failure to $J1$**:
   When the solver encounters this hard infeasibility, it returns `kInfeasible`. The runtime fallback plan sets `diesel_power = 0` and `load_served = 0`, causing **100% unmet load** ($J1 = \text{total demand}$).
   Thus, an artificial ceiling on a Priority 3 soft objective ($J2$) causes a catastrophic violation of the Priority 4 primary objective ($J1$)!

---

## 3. Governance Evaluation Options

* **Option 1 (Soft Objective Window)**: $J2$ reserve shortfall is allowed as a soft objective when physical reserve cannot be met ($s_{\text{J2}}$ upper bound = $\infty$). Feasibility is preserved; diesel runs to cover load ($J1=0$); $J2$ reports reserve deficit.
* **Option 2 (Hard Reserve Boundary)**: Reserve targets are hard survivability limits. If they cannot be met, the station cannot operate in NORMAL mode.
* **Option 3 (Mode Switch Architecture)**: NORMAL mode requires hard reserve feasibility. If reserve target cannot be met, runtime MUST execute an explicit governed transition to EMERGENCY mode (or ECD / Option D), dropping non-critical loads rather than shutting down the plant.

---

## 4. Audit Finding & Classification

The sealed codebase contains an incomplete bridge between MILP slack formulation and operational mode transitions.

`HARD_RELIABILITY_SEMANTICS = GOVERNANCE_REQUIRED`

Human governance must formally specify whether $J2$ is a soft penalty across all demand regimes or whether exceeding reserve capacity triggers governed mode transitions.
