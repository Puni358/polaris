# CRITICAL LOAD ARCHITECTURE

## DYNAMIC CRITICAL LOAD TRAJECTORY INPUT INTERFACE

- **Architecture Principle**: Critical load demand $P_{\text{demand,crit}}[t]$ is an **external input trajectory** provided to the optimizer, NOT hardcoded in code.
- **Interface Definition**:
  - `forecast_bundle.demand.critical_point`: Array of size $H=24$ containing hourly protected critical power requirements ($W$).
- **Safety Boundary**: Station-specific circuit values, heating curves, and equipment mappings remain engineering-defined and are NOT hardcoded in the solver architecture.

`CRITICAL_LOAD_ARCHITECTURE` = `ESTABLISHED`
