# POLARIS EMS — ECD SCHEMA INTEGRATION SPECIFICATION

## 1. Overview

This document specifies the exact additive schema extensions required for POLARIS EMS component integration. In compliance with governance rules, **NO existing schema fields are modified or deleted**. All extensions are strictly **ADDITIVE** and backward-compatible.

---

## 2. Schema Extension Specification Table

| Schema | Proposed Field | Type | Units | Producer | Consumer | Required? | Backward Compatible? |
|--------|---------------|------|-------|----------|----------|-----------|----------------------|
| `ForecastBundle` | `critical_demand_w` | `Optional[List[float]]` | Watts | `ForecastEngine` | `EmergencyConditionDetector` | No (Optional) | **YES** (Falls back to prototype constant load if absent) |
| `StationState` | `fuel_remaining_liters` | `Optional[float]` | Liters | Telemetry / State Estimator | `EmergencyConditionDetector` | No (Optional) | **YES** (Falls back to default prototype fuel level if absent) |
| `DispatchPlan` | `emergency_assessment` | `Optional[Dict[str, Any]]` | N/A | EMS Controller | Audit System / UI | No (Optional) | **YES** (Optional metadata) |
| `EmergencyAssessment` | *(All fields defined in `system/control/ecd.py`)* | Dataclass / Dict | Mixed | `EmergencyConditionDetector` | EMS Controller | Yes (Internal) | **YES** (New standalone schema) |

---

## 3. Backward Compatibility & Legacy Execution Path

- **Legacy Mode**: When `critical_demand_w` or `fuel_remaining_liters` are omitted, the integration adapter populates synthetic default prototype assumptions ($30,000\text{ W}$ constant critical load, fuel from config).
- **ECD-Enabled Mode**: When telemetry and forecast engines supply dedicated fields, the ECD seamlessly processes production vectors.

Status: `COMPLETE`
