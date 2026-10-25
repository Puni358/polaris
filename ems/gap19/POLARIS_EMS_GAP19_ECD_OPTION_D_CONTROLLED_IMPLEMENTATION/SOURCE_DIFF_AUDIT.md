# POLARIS EMS GAP19 — Source Diff Audit Report

## Source Modification Summary

- **Total Protected Files Modified**: 0
- **Total Allowed Files Modified**: 1 (`system/simulation/simulator.py`)
- **Total New Files Created**: 4 (`system/control/router.py`, `system/optimization/implementations/option_d.py`, `tests/test_gap19_ecd_option_d.py`, `tests/test_isolated_components.py`)

## Exact Git Diff for `system/simulation/simulator.py`

```diff
--- a/system/simulation/simulator.py
+++ b/system/simulation/simulator.py
@@ -60,11 +60,11 @@ class DigitalTwinSimulator:
         diesel_hours = (current_state.diesel_hours_running + 1.0) if diesel_running else 0.0
 
         # Physical fuel consumption calculation for committed first action (k=0)
-        fuel_consumed = ((self.base_fuel_lph if diesel_running else 0.0) + (self.marginal_fuel_lpwh * p_diesel)) * 1.0
-        curr_fuel = current_state.diesel_fuel_remaining_liters
-        if curr_fuel is None:
-            curr_fuel = self.initial_fuel_l
-        next_fuel = max(0.0, curr_fuel - fuel_consumed)
+        required_fuel = ((self.base_fuel_lph if diesel_running else 0.0) + (self.marginal_fuel_lpwh * p_diesel)) * 1.0
+        available_fuel = current_state.diesel_fuel_remaining_liters
+        if available_fuel is None:
+            available_fuel = self.initial_fuel_l
+        next_fuel = max(0.0, available_fuel - required_fuel)
 
         return StationState(
             timestamp=next_ts,
```
