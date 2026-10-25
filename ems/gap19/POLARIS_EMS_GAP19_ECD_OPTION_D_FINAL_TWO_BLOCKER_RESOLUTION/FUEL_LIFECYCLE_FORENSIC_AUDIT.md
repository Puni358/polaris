# Fuel Lifecycle Forensic Audit

## Forensic Inspection Trace

```text
initial_fuel_l (configs["diesel"].yaml)
   │
   ├──> StationState Initialization: StationState lacks diesel_fuel_remaining_liters
   │
   ├──> DispatchPlan Execution: DispatchPlan contains diesel_power[0]
   │
   ├──> DigitalTwinSimulator.step():
   │       Updates battery Wh, SOC, diesel_running, diesel_hours_running
   │       DOES NOT subtract diesel fuel volume!
   │
   └──> next StationState:
           Lacks diesel_fuel_remaining_liters!
```

---

## Detailed Findings
1. **Initial Fuel Source**: `configs["diesel"]["initial_fuel_l"]` (e.g., $100.0	ext{ L}$).
2. **Fuel Consumption Model**: `base_fuel_consumption_l_per_h` + `marginal_fuel_consumption_l_per_wh` in `DieselParameters` (`system/control/ecd.py`).
3. **Fuel Consumption Location**: Currently defined **ONLY** in `system/control/ecd.py` for survivability evaluation.
4. **Fuel State Storage Location**: Currently **NOT STORED** in `StationState` (`system/schemas/station_state.py`).
5. **Fuel State Update Location**: Currently **NOT UPDATED** in `DigitalTwinSimulator.step()` (`system/simulation/simulator.py`).
6. **Fuel State Next Cycle Source**: Currently defaults back to `configs["diesel"]["initial_fuel_l"]` on every step!

---

## Verdict
Fuel is currently **NOT TRACKED AT ALL** in physical state propagation across timesteps. Rolling ECD evaluation requires physical fuel state propagation.
