# StationState Schema Audit

Option B reads from `StationState`:
- `battery_energy_wh` (`EXISTS`)
- `diesel_running` (`EXISTS`)

All required fields are present in `system/schemas/station_state.py`.

```text
STATIONSTATE_COMPATIBILITY = ESTABLISHED
SCHEMA_EXTENSION_REQUIRED = NONE
```
