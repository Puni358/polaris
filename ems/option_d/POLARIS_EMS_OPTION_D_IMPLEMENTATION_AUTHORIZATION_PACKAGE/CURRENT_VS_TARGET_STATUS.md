# CURRENT VS TARGET ARCHITECTURE STATUS

## Architectural State Comparison

This document contrasts the **current implementation state** of the codebase with the proposed **target pre-GAP19 architecture** (Strategy 2).

---

## Component-by-Component Comparison Matrix

| Pipeline Stage | Current Implementation State | Proposed Target Architecture (Pre-GAP19 Strategy 2) |
| :--- | :--- | :--- |
| **Data Ingestion** | Reads raw JSON fixture directly in tests; schemas lack explicit critical/flexible load splitting. | `SyntheticFixtureProvider` parses fixture into standard `StationState` + additive schema fields. |
| **State Representation** | `StationState` contains aggregate total demand `demand.point`. | Additive fields: `critical_demand`, `flexible_demand`, `minimum_viable_critical_vector`. |
| **Energy Crisis Detection** | `EnergyCrisisDetector` (ECD) exists in `system/control/ecd.py` as isolated class; **not runtime-wired**. | ECD imported into `runner.py`; processes `StationState` and outputs `ECDState` each step. |
| **Operating Mode Routing** | No `OperatingMode` enum propagation in runtime pipeline. | `OperatingMode` (`NORMAL`, `OPTION_D`, `UNKNOWN_INVALID`) explicitly routed in `runner.py`. |
| **Policy Translation** | No policy layer; single MILP call handles all state conditions. | `OptionDPolicyLayer` transforms `OperatingMode` into solver-neutral `ModeConstraintSet`. |
| **Optimization Formulation** | Current MILP in `system/optimization/implementations/milp.py` uses 13 variables and aggregate demand. | Additive 21-variable formulation with separate solar/wind, critical/flexible load, and D4/D6 bounds. |
| **Objective Function** | Uses scalar weighted sum objective ($\text{Cost} + \text{Fuel} + \text{Penalty}$). | Maintains current scalar MILP solver under SciPy HiGHS; objective weights unedited pre-GAP19. |
| **Dispatch Output** | `DispatchPlan` schema records single aggregate dispatch vector. | Additive fields: `critical_load_served`, `flexible_load_served`, `alpha_critical`, `curtailment`. |
| **Fallback & Safe-State** | Untrusted/missing inputs produce runtime crash or unhandled behavior. | `UNKNOWN_INVALID` state automatically routes to Option D protected-critical safe state. |
| **Operator Escalation** | `NOT_IMPLEMENTED`. | Marked as `ENGINEERING_GOVERNANCE_DEPENDENT`; illustrative log warning emitted. |
| **System Recovery** | `NOT_IMPLEMENTED`. | Basic interface defined; manual/governed clearance required. |

---

## Architectural Flow Comparison

### Current Execution Flow:
$$\text{Fixture JSON} \longrightarrow \text{Runner} \longrightarrow \text{MILP (13 Vars, Aggregate Demand)} \longrightarrow \text{DispatchPlan}$$

### Target Pre-GAP19 Execution Flow:
$$\text{Fixture JSON} \longrightarrow \text{FixtureAdapter} \longrightarrow \text{StationState (Additive)} \longrightarrow \text{ECD} \longrightarrow \text{OperatingMode} \longrightarrow \text{OptionDPolicyLayer} \longrightarrow \text{ModeConstraintSet} \longrightarrow \text{MILP (21 Vars)} \longrightarrow \text{DispatchPlan} \longrightarrow \text{Digital Twin}$$

> [!CAUTION]
> **NO FALSE CLAIMS**: Target architecture components (Adapter, Policy Layer, ModeConstraintSet, 21-variable MILP) do **NOT** currently exist in code. They are specified and ready for implementation upon human authorization.
