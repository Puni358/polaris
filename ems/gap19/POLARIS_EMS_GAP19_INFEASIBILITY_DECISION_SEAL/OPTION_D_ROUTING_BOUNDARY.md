# POLARIS EMS GAP19 — OPTION D ROUTING BOUNDARY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Contract Status**: `SEALED_GOVERNANCE_CONTRACT`  

---

## 1. Option D Sealed Policy Baseline

Option D (**Protected Critical-Load Fallback**, DEC-004) is human-selected and sealed:
* When ECD evaluates system state as `EMERGENCY` or `UNKNOWN_INVALID`, non-critical loads are shed, and available power (diesel, renewables, battery) is allocated strictly to protected critical load ($P_{\text{critical}}(t)$).
* Under insufficient power (Clause D4), available critical power is allocated proportionally based on minimum viable requirements ($P_{i,\min}$).

---

## 2. Interface Boundary with Optimization & Control

```mermaid
flowchart TD
    ECD["ECD Engine"] -- "NORMAL" --> MPC["Normal MPC (Option B HiGHS Native)"]
    ECD -- "EMERGENCY / UNKNOWN_INVALID" --> OptD["Option D Fallback Dispatch Engine"]
    
    MPC -- "J2 Telemetry" --> ECD
    MPC -- "MILP Infeasible Signal" --> ECD
    
    OptD --> D1["D1: Protected Critical Load Only"]
    OptD --> D4["D4: Proportional Allocation (P_i,min)"]
    OptD --> D6["D6: Battery Charge from Diesel Excess"]
    
    OptD --> Dispatch["Emergency DispatchPlan"]
    OptD --> Escalation["Trigger Authority Escalation"]
```

---

## 3. Boundary Rules & Implementation Constraints

1. **Option D Trigger Constraint**: Option D is invoked **ONLY** when ECD returns `EMERGENCY` or `UNKNOWN_INVALID`. It cannot be triggered directly by MILP solver status.
2. **Dispatch Plan Representation**: In emergency mode, Option D constructs an emergency `DispatchPlan` where `load_served` is restricted to $P_{\text{critical}}(t)$ and `flexible_load_schedule = 0`.
3. **Runtime Status**: Option D runtime execution is **NOT IMPLEMENTED** and **NOT AUTHORIZED** for execution during this gate.
