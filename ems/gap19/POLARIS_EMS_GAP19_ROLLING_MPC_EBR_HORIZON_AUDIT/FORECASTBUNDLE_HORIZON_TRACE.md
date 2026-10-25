# ForecastBundle Structure & Horizon Trace

## 1. Structure of `ForecastBundle`

The schema definition for `ForecastBundle` is defined in:
`system/schemas/forecast_bundle.py` (Version 1.0.0).

### 1.1 Structural Fields

```python
class ForecastBundle:
    schema_version: str            # Exactly "1.0.0"
    origin_timestamp: str          # ISO-8601 string of forecast origin t0
    horizon_hours: int             # Exactly 24
    timestamps: List[str]          # Exactly 24 ISO-8601 strings
    solar_irradiance: TimeseriesForecast # 24 values (unit: W/m^2)
    solar_generation: TimeseriesForecast # 24 values (unit: W)
    wind_generation: TimeseriesForecast  # 24 values (unit: W)
    demand: TimeseriesForecast           # 24 values (unit: W)
    metadata: Dict[str, Any]       # Model ID, version, provenance
```

Each `TimeseriesForecast` contains three parallel 24-element float arrays:
- `point`: 24 point forecast values.
- `lower`: 24 lower uncertainty bound values.
- `upper`: 24 upper uncertainty bound values.

---

## 2. Answers to Specific Horizon Questions

### Question 1: What exactly does `ForecastBundle` contain?
- **Finding**: `ForecastBundle` contains origin timestamp $t_0$, exactly 24 future hourly timestamps $[t_0 + 1\text{h}, \dots, t_0 + 24\text{h}]$, and four physical timeseries channels (`solar_irradiance`, `solar_generation`, `wind_generation`, `demand`), each containing 24 point forecasts and 24 lower/upper interval bounds.

### Question 2: What exactly does the 24-hour forecast horizon represent?
- **Finding**: The 24-hour horizon in `ForecastBundle` represents the **24 discrete 1-hour time intervals immediately following the forecast origin timestamp $t_0$**.
- It defines the **FORECAST INFORMATION HORIZON** supplied to the optimizer.
- In `LocalMILPEnergyOptimizer` (`milp.py`), `H = len(forecast_bundle.timestamps) = 24` is used directly as the optimization decision horizon.

### Question 7: Is the forecast horizon measured from current observation time, next dispatch interval, fixed calendar boundary, or another origin?
- **Finding**: Measured strictly from **current observation time** (`station_state.timestamp` / `origin_timestamp`).
- **Code Reference**: `baseline.py` (lines 40, 57-59) and `s81_solar.py` (lines 146, 155):
  ```python
  origin_ts_str = station_state.timestamp
  origin_dt = datetime.fromisoformat(origin_ts_str.replace("Z", "+00:00"))
  for h in range(1, 25):
      future_dt = origin_dt + timedelta(hours=h)
      timestamps.append(future_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
  ```
- **Origin Measurement Rule**:
  - Origin $t_0$ = Current observation time $t_{\text{now}}$.
  - Timestep 1 = $t_{\text{now}} + 1\text{ hour}$ (first dispatch interval).
  - Timestep 24 = $t_{\text{now}} + 24\text{ hours}$.
  - The horizon is NOT tied to a fixed calendar boundary (e.g. 00:00 UTC); it rolls dynamically with $t_{\text{now}}$.

---

## 3. Summary Matrix

| Property | Implementation Detail | Source File |
| :--- | :--- | :--- |
| **Schema Version** | `"1.0.0"` | `system/schemas/forecast_bundle.py` |
| **Horizon Duration** | `24 hours` (hardcoded validation: `len == 24`) | `system/schemas/forecast_bundle.py:L67` |
| **Origin Parameter** | `station_state.timestamp` | `system/forecasting/implementations/baseline.py:L40` |
| **Step 1 Timestamp** | `station_state.timestamp + 1h` | `baseline.py:L58` |
| **Step 24 Timestamp** | `station_state.timestamp + 24h` | `baseline.py:L58` |
| **Calendar Boundary Dependence** | `NONE` (Relative to current observation time) | `baseline.py:L58` |
