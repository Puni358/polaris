# Static Trace of `PolarisLocalRunner.run_pipeline()`

```text
BEFORE_SELECTION_ARCHITECTURE =
LocalDataProvider -> ForecastEngine -> ForecastBundle -> LocalMILPEnergyOptimizer -> DispatchPlan -> DigitalTwinSimulator

CURRENT_ARCHITECTURE =
LocalDataProvider -> ForecastEngine -> ForecastBundle -> self.optimizer.optimize(...) -> DispatchPlan -> DigitalTwinSimulator

NEW_OPTION_B_EFFECT =
When optimizer_type="highs_native", self.optimizer is GAP19HighsNativeOptimizer. Zero pipeline flow modifications.
```
