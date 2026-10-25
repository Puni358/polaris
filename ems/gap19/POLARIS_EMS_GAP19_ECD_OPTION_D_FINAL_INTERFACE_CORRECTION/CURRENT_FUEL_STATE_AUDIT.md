# Current Fuel vs Initial Fuel Audit

## Source Inspection Findings (`system/simulation/simulator.py` & `system/schemas/station_state.py`)

1. **`StationState` Inspection**:
   - Fields: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_solar_irradiance`, `last_observed_demand`, `last_observed_wind_generation`, `operating_mode`.
   - **Finding**: `StationState` does **NOT** contain a `diesel_fuel_remaining_liters` field!

2. **`DigitalTwinSimulator.step()` Inspection**:
   - Updates battery Wh, SOC, `diesel_running`, `diesel_hours_running`.
   - **Finding**: `DigitalTwinSimulator` does **NOT** subtract diesel fuel from a running tank volume across steps!

---

## Corrected Classification
- `INITIAL_FUEL_CONFIG = ESTABLISHED` (`configs["diesel"]["initial_fuel_l"]`)
- `CURRENT_FUEL_STATE = NOT_ESTABLISHED` (Simulator does not physically propagate fuel remaining in `StationState`)
- `ECD_ROLLING_FUEL_INPUT = INTERFACE_REQUIRED` (Rolling ECD evaluation requires a fuel tracking interface or state propagation mechanism)

Do **NOT** treat initial fuel configuration as dynamic current fuel.
