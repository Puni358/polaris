# POLARIS GATE-04 — CONTRACT MATRIX
## MATRIX OF ENGINEERING INTERFACES, CONTRACT SCHEMAS, AND CONSUMPTION STATUS

---

## 1. ENGINEERING CONTRACT MATRIX

| Interface ID & Name | Source / Destination Module | Input Contract Schema | Output Contract Schema | Schema Type | Consumed Downstream? | Implementation Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IF-01**: `StationState → ECD` | `router.py` $\rightarrow$ `ecd.py` | `StationState` fields (`soc`, `fuel`, `demand`) | `EmergencyAssessment` | Active Code | **YES** (`runner.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-02**: `ForecastBundle → ECD` | `router.py` $\rightarrow$ `ecd.py` | `ForecastBundle.demand.point[0]` | Critical load trajectory input | Active Code | **YES** (`router.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-03**: `ECD → Router` | `ecd.py` $\rightarrow$ `router.py` | `EmergencyAssessment` | Tuple `(assessment, route_mode)` | Active Code | **YES** (`runner.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-04**: `Router → Option B` | `runner.py` $\rightarrow$ `gap19_highs_native.py` | Route `"NORMAL"`, `bundle`, `state` | `DispatchPlan` | Active Code | **YES** (`simulator.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-05**: `Router → Option D` | `runner.py` $\rightarrow$ `option_d.py` | Route `"EMERGENCY"`, `assessment`, `bundle` | `DispatchPlan` | Active Code | **YES** (`simulator.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-06**: `Option B/D → DispatchPlan`| `gap19_highs_native.py` / `option_d.py` | Solved 24h decision vectors | `DispatchPlan` (schema v1.0.0) | Active Code | **YES** (`simulator.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-07**: `DispatchPlan → DigitalTwin`| `dispatch_plan.py` $\rightarrow$ `simulator.py` | Decision vectors ($k=0$) | Actuals comparison evaluation | Active Code | **YES** (`simulator.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-08**: `DigitalTwin → next State` | `simulator.py` $\rightarrow$ `station_state.py` | Physical state step calculation | `StationState` for step $k+1$ | Active Code | **YES** (`runner.py`) | **DEFINED_AND_COMPATIBLE** |
| **IF-09**: `Emerg Return → Notification`| Unbuilt Module (Gate-03) | Return event (`EMERGENCY → NORMAL`) | Notification payload | Proposed | **NO** (Unbuilt) | **MISSING** |
| **IF-10**: `Override → Routing` | Unbuilt Module (Gate-03) | Operator override payload | Route override signal | Proposed | **NO** (Unbuilt) | **MISSING** |
| **IF-11**: `UNKNOWN_INVALID → Gate-01` | `runner.py` (lines 151–164) | Route `"UNKNOWN_INVALID"` | `FaultEvent` (`CRITICAL_TERMINATION`) | Active Code | **YES** (Software Halt) | **DEFINED_WITH_GAPS** |
| **IF-12**: `MILP Infeasibility → Gate-02`| `runner.py` (lines 184–195) | `OPTIMIZATION_INFEASIBLE` status | `FaultEvent` (`GOVERNED_DEGRADED`) | Active Code | **YES** (Safety Halt) | **DEFINED_WITH_GAPS** |
