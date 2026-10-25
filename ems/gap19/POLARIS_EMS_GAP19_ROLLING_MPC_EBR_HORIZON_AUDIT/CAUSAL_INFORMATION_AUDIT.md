# Causal Information & Truth Firewall Audit

## 1. Truth Firewall Principles

To maintain scientific integrity and prevent causal leakage in energy management systems:
1. **Observable Past Information**: At step `step_idx` ($t_{\text{now}}$), the optimizer and forecast engine may ONLY access historical observations up to $t_{\text{now}}$.
2. **Hidden Ground Truth**: Future actual solar, wind, and demand observations ($t > t_{\text{now}}$) must be strictly isolated from the controller and used solely by the digital twin simulator and evaluation engine.
3. **Causal Forecast Generation**: Forecasts must be generated causally using only past observations, clear-sky models, or trained ML models without accessing future telemetry.

---

## 2. Audit of Implementation: `LocalDataProvider`

The data access interface is implemented in:
`system/data/provider.py` (`LocalDataProvider`).

### 2.1 Causal Runtime Context Method (`get_runtime_state`)
```python
def get_runtime_state(self, current_index: int) -> Dict[str, Any]:
    # STRICTLY limits returned history to current_index
    history = self.timesteps[:current_index + 1]
    current_step = self.timesteps[current_index]
    return {
        "origin_timestamp": current_step["timestamp"],
        "history": history,
        "last_observed_solar_irradiance": current_step["actual_SW_IN"],
        "last_observed_demand": current_step["actual_demand"],
        "last_observed_wind_generation": current_step["actual_wind_generation"],
        "clearsky_ghi": current_step["clearsky_ghi"]
    }
```
- **Audit Verification**: `get_runtime_state()` returns `timesteps[:current_index + 1]`. Future array elements `timesteps[current_index + 1:]` are **physically sliced out** and completely inaccessible to the forecast engine and optimizer.

### 2.2 Hidden Ground Truth Method (`get_future_ground_truth`)
```python
def get_future_ground_truth(self, current_index: int, horizon_hours: int = 24) -> List[Dict[str, Any]]:
    start = current_index + 1
    end = min(start + horizon_hours, self.total_timesteps)
    return self.timesteps[start:end]
```
- **Audit Verification**: `get_future_ground_truth()` is called in `runner.py` (line 193) **AFTER** `forecast_engine.predict()` and `optimizer.optimize()` have already completed. It is passed strictly to `simulator.step()` for ground-truth physical integration.

---

## 3. Truth Firewall Verdict

```text
TRUTH_FIREWALL = PASS
CAUSAL_LEAKAGE = ZERO
FUTURE_GROUND_TRUTH_CONTAMINATION = NONE
```

- `ForecastEngine` receives zero future actual observations.
- `EnergyOptimizer` receives zero future actual observations.
- `PolarisLocalRunner` maintains strict isolation between causal decision components and ground-truth simulation components.
