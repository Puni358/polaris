# POLARIS EMS — ECD SCHEMA IMPACT AUDIT

## 1. Overview

This audit identifies all schema modifications required to support the Emergency Condition Detector (ECD). In accordance with governance constraints, **NO existing schema fields are modified or removed**. All required changes are strictly **ADDITIVE** and backward-compatible.

---

## 2. Schema Impact Analysis Table

| Schema | Proposed Field | Type | Units | Semantics | Producer | Consumer | Additive? | Backward Compatible? |
|--------|---------------|------|-------|-----------|----------|----------|-----------|----------------------|
| `ForecastBundle` | `critical_demand_w` | `List[float]` or `float` | Watts | Dedicated critical service load trajectory (separate from total station demand) | ForecastEngine | ECD | Yes | Yes (Optional with fallback to default prototype parameter) |
| `StationState` | `fuel_remaining_liters` | `float` | Liters | Current diesel fuel quantity remaining in station storage tank | Telemetry / State Estimator | ECD, Generator Controller | Yes | Yes (Optional float) |
| `DispatchPlan` | `emergency_assessment` | `EmergencyAssessment` | N/A | Full ECD assessment output for auditability and MPC record | EMS Controller | Audit System / UI | Yes | Yes (Optional field) |
| `EmergencyAssessment` (NEW) | *(All Output Fields)* | Schema | N/A | Dedicated schema for ECD output audit trail | ECD | EMS Controller, Dispatch, Audit | New Schema | Yes |

---

## 3. Detailed Schema Requirements

### 3.1 `ForecastBundle` Extension
- **Current State**: Contains `demand.point` representing total station electrical demand.
- **Critical Requirement**: Total station demand `demand.point` **MUST NOT** be silently reinterpreted as critical demand. Critical load represents life-safety, communications, and emergency services only.
- **Additive Extension**: Add optional field `critical_demand_w: Optional[List[float]] = None`.

### 3.2 `StationState` Extension
- **Current State**: Tracks battery SOC, temperatures, grid status. Lacks fuel inventory.
- **Additive Extension**: Add optional field `fuel_remaining_liters: Optional[float] = None`.

### 3.3 New Schema: `EmergencyAssessment`
- **Purpose**: Fully encapsulates ECD execution results, margins, classifications, and provenance.
- **Fields**:
  - `operating_mode`: `Enum["NORMAL", "EMERGENCY", "UNKNOWN_INVALID"]`
  - `battery_endurance_hours`: `float`
  - `diesel_endurance_hours`: `float`
  - `battery_margin_hours`: `float`
  - `diesel_margin_hours`: `float`
  - `preserved_resource`: `Enum["BATTERY", "DIESEL", "BOTH", "NONE"]`
  - `limiting_resource`: `Enum["BATTERY", "DIESEL", "BOTH", "NONE"]`
  - `tie_status`: `bool`
  - `validity_status`: `Enum["VALID", "MISSING_T_REQUIRED", "EXPIRED_T_REQUIRED", "UNAUTHORIZED_T_REQUIRED", "INVALID_TELEMETRY"]`
  - `failure_reason`: `Optional[str]`
  - `timestamp`: `str`

---

## 4. Audit Conclusion

Schema Impact Status: `IDENTIFIED` (All required extensions documented; zero breaking changes).
