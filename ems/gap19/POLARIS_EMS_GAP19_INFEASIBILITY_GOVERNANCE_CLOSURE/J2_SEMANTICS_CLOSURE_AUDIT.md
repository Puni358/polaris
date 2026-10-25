# POLARIS EMS GAP19 — J2 SEMANTICS CLOSURE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `GOVERNANCE_REQUIRED`  

---

## 1. Objective & Governance Reconstruction

This audit evaluates the formal semantics of the $J2$ objective function across the sealed governance record and codebase implementation.

In Option B native HiGHS formulation, $J2$ represents the **Governed Reserve Shortfall Wh** (pointwise maximum envelope of 6-hour EBR lookahead requirement and 24-hour terminal reserve requirement):
$$J2 = \sum_{t=0}^{23} s_{\text{J2}}[t]$$
with priority rank 3 in the lexicographic hierarchy ($J1 \succ J2 \succ J3 \succ J4$).

---

## 2. Hard vs Soft Objective Semantics

### A. Intended Governance Semantics
* In Option B specification, $J2$ was designed as a **soft objective penalty** ($J2 > 0$).
* Because $J1$ (Critical Unmet Load) has priority rank 4 (higher than $J2$), the optimizer is intended to consume battery reserve below $E_{\text{EBR\_target}}$ ($J2 > 0$) rather than shed critical load ($J1 > 0$).

### B. Actual Implementation Mechanics
* In `gap19_highs_native.py`, $s_{\text{J2}}[t]$ is upper-bounded at `capacity_wh` ($200\text{ kWh}$).
* When required 6-hour EBR reserve $E_{\text{EBR\_target}}[t]$ exceeds $350\text{ kWh}$ (which occurs when 6-hour average critical load exceeds $53.67\text{ kW}$), the upper bound on $s_{\text{J2}}$ prevents the slack variable from absorbing the full deficit.
* As a result, the soft reserve penalty collapses into a **hard mathematical constraint**, causing HiGHS to return `kInfeasible`.

### C. Downstream Violation of Priority Hierarchy
* When `kInfeasible` occurs, `runner.py` executes a zero-dispatch fallback plan that shuts off diesel generators and drops 100% of load ($J1 = \text{total demand}$).
* Thus, an artificial ceiling on a Priority 3 soft penalty ($J2$) triggers a complete failure of the Priority 4 primary objective ($J1$).

---

## 3. Policy Evaluation Options for Human Governance

1. **Option 1 (Pure Soft Penalty Window)**: Formally authorize unbounding $s_{\text{J2}}$ (`ub = infinity`). Reserve shortfalls ($J2 > 0$) remain soft penalty outcomes in NORMAL mode. Feasibility is preserved, diesel runs to serve load ($J1=0$), and $J2$ accurately quantifies the reserve shortfall magnitude.
2. **Option 2 (Hard Operating Boundary)**: Reserve targets are hard survivability limits. If $E_{\text{next}}[t] < E_{\text{EBR\_target}}[t] + E_{\min}$, the station CANNOT operate in NORMAL mode.
3. **Option 3 (Governed Mode Switch)**: NORMAL mode requires hard reserve feasibility. If reserve target cannot be met, the runtime MUST execute a governed transition to EMERGENCY mode (or Option D fallback), dropping non-critical loads while protecting critical load.

---

## 4. Audit Finding & Verdict

The policy record specifies $J1 \succ J2 \succ J3 \succ J4$ as soft priority ordering, but no policy document has explicitly authorized how physical reserve violations ($J2 > 0$) under high load should interact with mode transitions.

`J2_SEMANTICS = GOVERNANCE_REQUIRED`
