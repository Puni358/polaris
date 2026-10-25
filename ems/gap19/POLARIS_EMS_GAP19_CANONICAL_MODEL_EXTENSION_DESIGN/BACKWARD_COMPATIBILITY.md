# BACKWARD COMPATIBILITY

## BACKWARD COMPATIBILITY ASSURANCES

- Legacy single-demand inputs (`demand.point`) map cleanly to total station load.
- If `demand.critical_point` is omitted, the solver defaults safely to treating $P_{\text{demand,crit}}(t) = P_{\text{demand,total}}(t)$ or 0.0 based on `operating_mode`.
- Existing `DispatchPlan` outputs (`solar_used`, `wind_used`, `battery_charge`, etc.) retain identical field names and units.
