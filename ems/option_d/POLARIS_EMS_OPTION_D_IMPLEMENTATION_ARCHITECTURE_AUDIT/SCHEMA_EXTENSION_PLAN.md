# SCHEMA EXTENSION PLAN

## 1. MINIMAL ADDITIVE SCHEMA EXTENSION SPECIFICATIONS

The audit specified the exact, minimal additive schema changes required across POLARIS schemas ([ForecastBundle](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py#L54), [StationState](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py#L8), [DispatchPlan](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/dispatch_plan.py#L10)).

---

## 2. SPECIFICATION BY TARGET SCHEMA

### A. `ForecastBundle` Schema Extension (Version 1.1.0)
- **Additive Field**: `critical_demand: Optional[TimeseriesForecast] = None`
- **Unit**: `"W"` (Watts)
- **Validation**: 24 horizon values, non-negative, finite.
- **Backward Compatibility**: If `None`, defaults downstream behavior to single total `demand` array.

### B. `StationState` Schema Extension
- **Additive Fields**:
  - `fuel_remaining_liters: Optional[float] = None` (Unit: Liters, non-negative).
  - `operating_mode: Optional[str] = None` (Enum string: `"NORMAL"`, `"EMERGENCY"`, `"UNKNOWN_INVALID"`).
- **Backward Compatibility**: If `None`, defaults to baseline `diesel_running` without fuel tracking.

### C. `DispatchPlan` Schema Extension (Version 1.1.0)
- **Additive Fields**:
  - `critical_load_served: Optional[List[float]] = None` (Unit: W).
  - `critical_load_unmet: Optional[List[float]] = None` (Unit: W).
  - `operating_mode: Optional[str] = None` (String).
- **Backward Compatibility**: Existing downstream consumers (`DigitalTwinSimulator`) ignore optional fields.

---

## 3. SUMMARY
- **`SCHEMA_EXTENSION_STATUS = COMPLETED_ADDITIVE_NON_BREAKING`**
- All schema extensions are strictly additive and optional. Zero existing fields are modified or repurposed.
