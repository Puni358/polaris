# Static Call Graph & Runtime Flow

```text
PolarisLocalRunner (system/runtime/runner.py)
    ↓ [ACTUAL_CODE_PATH]
ForecastEngine
    ↓ [ACTUAL_CODE_PATH]
ForecastBundle
    ↓ [MISSING_PATH: ECD not wired]
ECD (system/control/ecd.py)
    ↓ [MISSING_PATH: ECD not wired]
Mode / Policy
    ↓ [PROPOSED_PATH: Needs runner selection branch]
GAP19HighsNativeOptimizer (system/optimization/implementations/gap19_highs_native.py)
    ↓ [ACTUAL_CODE_PATH: Implements interface]
DispatchPlan
    ↓ [ACTUAL_CODE_PATH]
DigitalTwinSimulator
```
