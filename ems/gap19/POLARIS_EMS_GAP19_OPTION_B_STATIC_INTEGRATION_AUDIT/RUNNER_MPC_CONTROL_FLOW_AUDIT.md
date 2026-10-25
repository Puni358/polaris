# Runner / MPC Control-Flow Audit

```text
ACTUAL_RUNTIME_FLOW =
LocalDataProvider -> ForecastEngine -> ForecastBundle -> LocalMILPEnergyOptimizer -> DispatchPlan -> DigitalTwinSimulator

TARGET_OPTION_B_FLOW =
StationState -> ForecastEngine -> ForecastBundle -> ECD -> OperatingMode -> GAP19HighsNativeOptimizer -> DispatchPlan -> DigitalTwinSimulator
```

| Transition | Status |
| :--- | :--- |
| `StationState` -> `ForecastEngine` | `IMPLEMENTED` |
| `ForecastEngine` -> `ForecastBundle` | `IMPLEMENTED` |
| `ForecastBundle` -> `ECD` | `NOT_IMPLEMENTED` |
| `ECD` -> `OperatingMode` | `NOT_IMPLEMENTED` |
| `OperatingMode` -> `GAP19HighsNativeOptimizer` | `PARTIAL` (Reads from config) |
| `GAP19HighsNativeOptimizer` -> `DispatchPlan` | `IMPLEMENTED` |
| `DispatchPlan` -> `DigitalTwinSimulator` | `IMPLEMENTED` |
