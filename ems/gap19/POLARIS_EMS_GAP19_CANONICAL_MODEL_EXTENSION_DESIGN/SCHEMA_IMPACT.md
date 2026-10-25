# SCHEMA IMPACT

## ADDITIVE SCHEMA EXTENSION REQUIREMENTS

1. **`ForecastBundle`**:
   - Add optional field `demand.critical_point: Optional[List[float]]` (Hourly protected critical load demand).
2. **`StationState`**:
   - Add optional field `operating_mode: Optional[str]` (`"NORMAL"`, `"EMERGENCY"`, `"UNKNOWN_INVALID"`).
3. **`DispatchPlan`**:
   - Add optional fields `j1_critical_deficit`, `j2_reserve_shortfall`, `j3_fuel_liters`, `j4_curtailment_wh`.

All schema extensions are strictly **additive** and preserve existing required fields.
