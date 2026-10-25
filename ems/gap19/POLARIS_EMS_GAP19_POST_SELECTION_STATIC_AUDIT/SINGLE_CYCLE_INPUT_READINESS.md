# Single-Cycle Test Input Readiness Matrix

| Input Parameter | Status | Note |
| :--- | :--- | :--- |
| `StationState` | `AVAILABLE` | Instantiated from test fixture |
| `ForecastBundle` | `AVAILABLE` | 24h synthetic solar/wind/demand point forecasts |
| 24h Solar Trajectory | `AVAILABLE` | `forecast_bundle.solar_generation.point` |
| 24h Wind Trajectory | `AVAILABLE` | `forecast_bundle.wind_generation.point` |
| 24h Total Demand | `AVAILABLE` | `forecast_bundle.demand.point` |
| 24h Critical Demand | `AVAILABLE` | Passed explicitly in `config["critical_demand_w"]` |
| Fuel State | `AVAILABLE` | Passed in `station_state` & `config["diesel"]` |
| Operating Mode (`NORMAL`)| `AVAILABLE` | Passed in `config["operating_mode"] = "NORMAL"` |
