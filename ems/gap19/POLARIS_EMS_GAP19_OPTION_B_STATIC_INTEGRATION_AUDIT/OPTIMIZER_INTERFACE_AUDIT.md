# Optimizer Interface Audit

| Interface Property | Existing Optimizer (`LocalMILPEnergyOptimizer`) | Option B (`GAP19HighsNativeOptimizer`) | Compatible? |
| :--- | :--- | :--- | :--- |
| Constructor | `__init__(self)` | `__init__(self)` | **YES** |
| `optimize` Signature | `(self, forecast_bundle, station_state, config)` | `(self, forecast_bundle, station_state, config)` | **YES** |
| `StationState` Input | `StationState` object | `StationState` object | **YES** |
| `ForecastBundle` Input | `ForecastBundle` object | `ForecastBundle` object | **YES** |
| Horizon | 24 hours | 24 hours | **YES** |
| Timestep | 1.0 hour | 1.0 hour | **YES** |
| Return Type | `DispatchPlan` | `DispatchPlan` | **YES** |
| Exceptions | Raises / returns degraded plan | Returns degraded plan on non-optimal | **YES** |
| Operating Mode | Ingests `config["operating_mode"]` | Ingests `config["operating_mode"]` | **YES** |
| Configuration | `config: Dict[str, Any]` | `config: Dict[str, Any]` | **YES** |

```text
CURRENT_OPTIMIZER_INTERFACE = EnergyOptimizer (system/optimization/interface/base.py)
OPTION_B_INTERFACE = GAP19HighsNativeOptimizer(EnergyOptimizer)
INTERFACE_COMPATIBILITY = COMPATIBLE
```
