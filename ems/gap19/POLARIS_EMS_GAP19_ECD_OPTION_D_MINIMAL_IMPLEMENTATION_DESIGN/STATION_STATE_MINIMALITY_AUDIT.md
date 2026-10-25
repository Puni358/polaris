# StationState Minimality Audit

## Minimality Audit of `StationState` (`system/schemas/station_state.py`)

Existing `StationState` fields:
- `timestamp`: string
- `battery_soc_pct`: float
- `battery_energy_wh`: float
- `diesel_running`: bool
- `diesel_hours_running`: float
- `last_observed_solar_irradiance`: float
- `last_observed_demand`: float
- `last_observed_wind_generation`: float
- `operating_mode`: string (defaults to `"NORMAL"`)

### Evaluation of Proposed Additions:
1. `operating_mode`: **ALREADY EXISTS** in schema (`operating_mode="NORMAL"`).
2. `emergency_assessment_json`: **NOT REQUIRED**. Telemetry can be logged in runner context without schema pollution.
3. Policy override knobs (`ebr_target_wh_override`, `terminal_target_wh_override`): **EXCLUDED** per correction audit.

---

## Verdict
`STATION_STATE_EXTENSION = NONE`. Existing `StationState` carries all required inputs cleanly.
