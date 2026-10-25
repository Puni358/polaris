# ECD INPUT INTEGRATION AUDIT

## 1. EXISTING ECD SIGNATURE
Inspected: [EmergencyConditionDetector.evaluate()](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L208-L216)

```python
def evaluate(
    self,
    horizon_input: Union[AuthorizedHorizon, float],
    critical_load: Union[CriticalLoadTrajectory, float],
    soc_pct: float,
    fuel_remaining_liters: float,
    battery_params: BatteryParameters,
    diesel_params: DieselParameters
) -> EmergencyAssessment:
```

---

## 2. FIXTURE DATA MAPPING TO ECD INPUTS

| ECD Input Argument | Fixture Source Quantity | Fixture Value / Type | Target ECD Structure | Mapping & Adapter Requirement |
| :--- | :--- | :--- | :--- | :--- |
| `horizon_input` | Governed $T_{\text{required}}$ | $6.0$ hours | `AuthorizedHorizon(t_required_hours=6.0)` | Adapter wraps constant $6.0$ h into `AuthorizedHorizon` |
| `critical_load` | `p_critical_total_actual_kW` | $30.0$ kW ($30,000$ W) | `ConstantCriticalLoad(30000.0)` | Adapter converts $30.0$ kW -> $30,000$ W float or trajectory |
| `soc_pct` | `soc_initial_pct` / State | $80.0\%$ (or scenario initial) | Direct `float` | Direct mapping from fixture/`StationState` |
| `fuel_remaining_liters` | `v_fuel_initial_L` / State | $500.0$L, $20.0$L, $10.0$L | Direct `float` | Extracted from fixture scenario initial fuel |
| `battery_params` | Fixture / Config Specs | $200$ kWh, $20\%$-$95\%$, $50$ kW | `BatteryParameters` dataclass | Adapter builds `BatteryParameters` from config |
| `diesel_params` | Fixture / Config Specs | $10$-$60$ kW, $F(P)=5+0.25P$ | `DieselParameters` dataclass | Adapter builds `DieselParameters` ($5.0$ L/h, $0.00025$ L/Wh) |

---

## 3. ECD CORE REUSABILITY & CLASSIFICATION

- **`ECD_CORE_REUSABLE = YES`**: The core ECD class in `system/control/ecd.py` is clean, purely functional, and completely reusable without modifying any internal code.
- **`ECD_ADAPTER_REQUIRED = YES`**: An adapter is required to pull fixture data/config, construct the `AuthorizedHorizon` ($6.0$h), `BatteryParameters`, `DieselParameters`, and `ConstantCriticalLoad` ($30,000$ W), and pass them to `evaluate()`.
- **`ECD_SCHEMA_EXTENSION_REQUIRED = YES`**: `StationState` requires an additive extension to carry `fuel_remaining_liters` and critical demand so ECD can run dynamically across receding horizon iterations.
