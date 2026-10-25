# POLARIS EMS GAP19 — GOVERNANCE DECISION REGISTER

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `GOVERNANCE_REQUIRED`  

---

## 1. Governance Decision Register Overview

This register formally logs the 7 open governance decision items required to achieve complete policy closure for POLARIS EMS GAP19.

> **CRITICAL BOUNDARY**: The AI assistant has NOT selected policy choices on behalf of human authority. All options are presented neutrally for human governance decision.

---

## 2. Open Governance Decision Items

### `DEC-GAP19-01`: $J2$ Hard vs Soft Objective Semantics
* **Question**: Under high load where battery energy falls below 6-hour EBR lookahead requirement, is $J2$ shortfall intended as a soft penalty outcome ($J2 > 0$) in NORMAL mode, a hard operating boundary, or a trigger for EMERGENCY mode?
* **Current Status**: `GOVERNANCE_REQUIRED`
* **Evidence**: Option B specification defines $J1 \succ J2 \succ J3 \succ J4$, but slack upper bound creates hard solver infeasibility.
* **Options**:
  - *Option A*: Pure soft penalty window ($s_{\text{J2}}$ unbounded).
  - *Option B*: Hard operating boundary (NORMAL mode prohibited if reserve violated).
  - *Option C*: Governed mode switch (Reserve shortfall triggers EMERGENCY mode).
* **What Can Be Decided Now**: Policy intent for $J2$ across operating regimes.
* **Human Authorization Required**: Final selection of Option A, B, or C.

---

### `DEC-GAP19-02`: $s_{\text{J2}}$ Slack Upper Bound Policy
* **Question**: Should the ad-hoc upper bound $s_{\text{J2}} \le \text{capacity\_wh}$ ($200\text{ kWh}$) be removed (`ub = infinity`) to align with soft-penalty lexicographic optimization?
* **Current Status**: `IMPLEMENTATION_FACT`
* **Evidence**: Capping $s_{\text{J2}}$ at $200\text{ kWh}$ causes artificial solver infeasibility when 6-hour critical demand exceeds $322\text{ kWh}$ ($53.67\text{ kW}$ average).
* **Options**:
  - *Option A*: Unbound $s_{\text{J2}}$ (`ub = np.inf`) in solver formulation.
  - *Option B*: Dynamic upper bound scaled to peak forecast demand.
  - *Option C*: Retain $200\text{ kWh}$ upper bound as hard cutoff.
* **Human Authorization Required**: Approval to change MILP solver variable bounds.

---

### `DEC-GAP19-03`: Runtime MILP Infeasibility Dispatch Policy
* **Question**: When MILP solver returns `kInfeasible`, what fallback dispatch should `runner.py` execute?
* **Current Status**: `DEFECT`
* **Evidence**: Current runner executes `GOVERNED_ZERO_DISPATCH` (shuts down diesel & renewables, dropping 100% of load).
* **Options**:
  - *Option A*: Governed emergency diesel fallback (dispatch diesel to cover critical load).
  - *Option B*: Invoke Option D Protected Critical-Load Fallback.
  - *Option C*: Retain zero-dispatch fallback.
* **Human Authorization Required**: Selection of runtime fallback policy during solver infeasibility.

---

### `DEC-GAP19-04`: ECD vs MILP Infeasibility Signal Routing
* **Question**: What is the architectural relationship between MILP solver infeasibility and ECD Emergency Condition Detection?
* **Current Status**: `GOVERNANCE_REQUIRED`
* **Evidence**: No code currently connects solver infeasibility to ECD or mode switching.
* **Options**:
  - *Option A*: MILP infeasibility feeds directly into ECD health monitor as a degraded telemetry signal.
  - *Option B*: MILP infeasibility bypasses ECD and directly triggers Option D fallback.
  - *Option C*: MILP infeasibility and ECD remain independent signals.
* **Human Authorization Required**: Selection of signal routing architecture.

---

### `DEC-GAP19-05`: Option D Emergency Routing Layer Architecture
* **Question**: How should Option D (DEC-004) be integrated into the runtime orchestration loop?
* **Current Status**: `SELECTED_AND_SEALED` (DEC-004), `NOT_IMPLEMENTED`
* **Evidence**: Option D policy is sealed, but runtime routing layer in `runner.py` does not exist.
* **Options**:
  - *Option A*: Dedicated `EmergencyDispatchEngine` wrapper inside `runner.py`.
  - *Option B*: Mode-switch flag passed into `EnergyOptimizer.optimize(...)`.
* **Human Authorization Required**: Approval of runtime software architecture design.

---

### `DEC-GAP19-06`: Station Feasible Operating Space & Peak Load Envelopes
* **Question**: What is the maximum allowable peak demand relative to installed battery capacity ($C_{\text{bat}}$) and diesel capacity ($P_{\text{D,max}}$) for synthetic test fixtures and NORMAL mode operations?
* **Current Status**: `GOVERNANCE_REQUIRED`
* **Evidence**: Synthetic fixtures `demand_stress` ($66.7\text{ kW}$) and `battery_stress` ($45.5\text{ kW}$) exceed 6-hour battery reserve limits.
* **Human Authorization Required**: Definition of station operating envelope limits.

---

### `DEC-GAP19-07`: Standardized Evaluation Reporting Terminology
* **Question**: Should all future evaluation reports adopt the 7-metric disambiguated reporting standard?
* **Current Status**: `CORRECTION_REQUIRED`
* **Evidence**: Historical reports conflated pipeline completion with solver optimality.
* **Human Authorization Required**: Formal adoption of reporting standard.
