# POLARIS EMS — OPTION D SCHEMA IMPACT AUDIT

## 1. Executive Summary

This document presents the schema impact audit evaluating data structures across the POLARIS pipeline: `ForecastBundle`, `StationState`, `DispatchPlan`, `EmergencyAssessment`, and `CriticalLoadTrajectory`.

> [!IMPORTANT]
> **BASELINE SEMANTICS PRESERVATION**:
> Baseline schema fields (e.g. `demand.point` in `ForecastBundle`) must **NEVER** be repurposed or relabeled to represent critical demand. `demand.point` retains its established meaning as total station demand. Additive schema fields are used for critical load trajectories.

---

## 2. Comprehensive Schema Classification Table

| Target Schema | Proposed / Required Field | Classification | Field Purpose & Usage Rule |
|---------------|---------------------------|----------------|----------------------------|
| `ForecastBundle` | `demand.point` | `EXISTING` | Total station demand trajectory. Preserved unchanged. |
| `ForecastBundle` | `solar.point` | `EXISTING` | Solar generation forecast trajectory. Preserved unchanged. |
| `ForecastBundle` | `wind.point` | `EXISTING` | Wind generation forecast trajectory. Preserved unchanged. |
| `ForecastBundle` | `critical_demand_w` | `ADDITIVE_REQUIRED` | Additive `List[float]` supplying dynamic $P_{\text{critical}}(t)$ vector. |
| `StationState` | `battery_energy_wh` | `EXISTING` | Battery energy level. Preserved unchanged. |
| `StationState` | `diesel_running` | `EXISTING` | Diesel generator running status. Preserved unchanged. |
| `StationState` | `critical_circuit_status` | `ADDITIVE_REQUIRED` | Additive dictionary mapping critical circuit breaker states. |
| `DispatchPlan` | `p_chg` / `p_dis` / `p_diesel` | `EXISTING` | Controllable power setpoint trajectories. Preserved unchanged. |
| `DispatchPlan` | `protected_critical_load_w` | `ADDITIVE_REQUIRED` | Additive metadata float recording served critical load power. |
| `DispatchPlan` | `shed_noncritical_load_w` | `ADDITIVE_REQUIRED` | Additive metadata float recording shed noncritical load power. |
| `EmergencyAssessment` | `operating_mode` | `EXISTING` | Enum output (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`). Preserved. |
| `EmergencyAssessment` | `validity_status` | `EXISTING` | Enum output detailing input validity status. Preserved. |
| `EmergencyAssessment` | `escalation_flag` | `ADDITIVE_REQUIRED` | Additive boolean flag indicating D4/D5 operator escalation. |
| `CriticalLoadTrajectory` | `evaluate_w(t)` | `EXISTING` | Protocol method evaluating critical load power. Preserved. |

---

## 3. Schema Boundary Rules

1. **Zero Breaking Changes**: All proposed schema extensions are purely additive (`Optional` fields with `None` defaults). Existing baseline code remains 100% backward compatible.
2. **Schema Audit Status**: No schemas have been modified. Implementation requires prior human governance authorization.

Status: `SCHEMA_IMPACT_SEALED`
