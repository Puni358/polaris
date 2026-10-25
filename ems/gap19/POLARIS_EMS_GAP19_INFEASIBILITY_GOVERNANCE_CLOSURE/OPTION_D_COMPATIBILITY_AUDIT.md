# POLARIS EMS GAP19 — OPTION D COMPATIBILITY AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `NOT_ESTABLISHED` (Routing Layer Missing)  

---

## 1. Option D Sealed Governance Baseline

Option D (**Protected Critical-Load Fallback**, DEC-004) is human-selected and sealed:
- **Decision Record**: `POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/DEC004_FINAL_SELECTION.md`
- **Core Directive**: When an emergency condition or `UNKNOWN_INVALID` telemetry state occurs, non-critical loads are immediately shed, and available power (diesel + renewables + battery) is dedicated strictly to serving protected critical load ($P_{\text{critical}}(t)$). Under insufficient power (D4 clause), power is allocated proportionally to minimum viable requirements ($P_{i,\min}$).

---

## 2. Compatibility Assessment with MILP Infeasibility

| Feature / Aspect | Option D Governance Requirement | Current MILP Infeasibility Fallback Behavior | Compatibility Verdict |
| :--- | :--- | :--- | :---: |
| **Critical Load Protection** | Protect $P_{\text{critical}}(t)$ using diesel, battery, renewables. | Drops 100% of load (`unmet_load = demand`, `diesel_power = 0`). | **INCOMPATIBLE** |
| **Diesel Generator Usage** | Dispatch diesel generator up to $P_{\text{D,max}}$ to support critical load. | Shuts off diesel generator (`diesel_power = 0`). | **INCOMPATIBLE** |
| **Non-Critical Load Shedding** | Shed flexible/non-critical load to zero. | Sheds ALL load (critical and non-critical). | **PARTIAL / HAZARDOUS** |
| **Proportional Allocation (D4)** | Allocate available power proportionally to $P_{i,\min}$. | Zero allocation across all circuits. | **INCOMPATIBLE** |

---

## 3. Required Routing Layer & Missing Inputs

### A. Routing Layer Requirement
Current MILP infeasibility handling is **incompatible** with Option D policy because `runner.py` defaults to `GOVERNED_ZERO_DISPATCH` (total blackout) rather than invoking Option D rules. An explicit **Emergency Routing Layer** is required to catch solver infeasibility or ECD alerts and construct an Option D compliant critical dispatch plan.

### B. Deferred Engineering & Governance Inputs
Before Option D runtime integration can be implemented, the following inputs remain missing:
1. **Protected Critical Equipment Inventory & Circuit Mapping**: Station-specific mapping of critical loads.
2. **Dynamic Critical Load Trajectory $P_{\text{critical}}(t)$**: Concrete mathematical formulation for critical load.
3. **Proportional Allocation Ratios ($P_{i,\min}$)**: Numerical minimum viable requirements for D4 proportional sharing.
4. **Implementation Authorization**: Explicit human governance gate authorizing code modifications.

---

## 4. Audit Verdict

`OPTION_D_COMPATIBILITY = NOT_ESTABLISHED`

*(Runtime routing layer between solver infeasibility and Option D is missing; implementation remains blocked until authorized).*
