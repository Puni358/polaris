# POLARIS EMS — EMERGENCY CONDITION DETECTOR SCHEMA GAP AUDIT

## 1. DETAILED SCHEMA FIELD AUDIT

The table below audits every required data field for the Emergency Condition Detector against current codebase schemas:

| Target Schema | Required Field | Current Status in Repo | Required Additive Action |
| :--- | :--- | :--- | :--- |
| `StationState` | `battery_soc_pct` | `EXISTS` | None |
| `StationState` | `battery_energy_wh` | `EXISTS` | None |
| `StationState` | `diesel_running` | `EXISTS` | None |
| `StationState` | `diesel_hours_running` | `EXISTS` | None |
| `StationState` | `fuel_remaining_liters` | `MISSING` | Additive schema extension required |
| `ForecastBundle` | `demand` (total) | `EXISTS` | None |
| `ForecastBundle` | `critical_demand` (5-tier) | `MISSING` | Additive schema extension required |
| `ForecastBundle` | 72h forecast trajectory | `MISSING` (covers 24h only) | Additive extension or 72h trajectory payload |
| `EmergencyAssessment` | `operating_mode` | `MISSING` (schema uncreated) | New additive output schema required |
| `EmergencyAssessment` | `battery_time_margin_hours` | `MISSING` (schema uncreated) | New additive output schema required |
| `EmergencyAssessment` | `diesel_time_margin_hours` | `MISSING` (schema uncreated) | New additive output schema required |
| `EmergencyAssessment` | `limiting_resource` | `MISSING` (schema uncreated) | New additive output schema required |
| `EmergencyAssessment` | `preserved_resource` | `MISSING` (schema uncreated) | New additive output schema required |

---

## 2. PROPOSED ADDITIVE SCHEMA EXTENSIONS (AUDIT ONLY)

No code modifications are authorized in this audit. The following structures represent future additive schema candidates:

### 1. Additive `StationState` Extension:
```python
# Future additive field in StationState:
fuel_remaining_liters: float  # Remaining diesel fuel in station tank (liters)
```

### 2. New `EmergencyAssessment` Payload Schema Candidates:
```python
class EmergencyAssessment:
    operating_mode: str               # "NORMAL", "EMERGENCY", "FAIL_CLOSED", "GOVERNANCE_REQUIRED"
    T_required_hours: float           # Exogenous resolved survival window (72.0 for prototype)
    battery_survivability_hours: float# T_battery: Battery survival duration under zero renewable (hours)
    diesel_survivability_hours: float # T_diesel: Diesel survival duration under zero renewable (hours)
    battery_time_margin_hours: float  # M_battery = T_battery - T_required (hours) [PRIMARY]
    diesel_time_margin_hours: float   # M_diesel = T_diesel - T_required (hours) [PRIMARY]
    battery_energy_margin: float      # E_margin,batt [DIAGNOSTIC ONLY]
    diesel_energy_margin: float       # E_margin,diesel [DIAGNOSTIC ONLY]
    battery_survivability_ratio: float# R_batt = T_batt / T_required [DIAGNOSTIC ONLY]
    diesel_survivability_ratio: float # R_diesel = T_diesel / T_required [DIAGNOSTIC ONLY]
    limiting_resource: str            # "BATTERY", "DIESEL", "TIE / BOTH", or "NONE" (smaller margin)
    preserved_resource: str           # "BATTERY", "DIESEL", "TIE / BOTH", or "NONE" (larger margin)
    assessment_timestamp: str         # ISO-8601 timestamp string
    provenance: str                   # Traceability metadata / audit reference
```
