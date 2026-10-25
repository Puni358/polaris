# 365D FORECAST CAUSALITY & FEATURE AVAILABILITY AUDIT

## Causality Guarantee Precondition
For every hour $k$ of the 365-day experiment, all information consumed by the `ForecastEngine` at forecast origin $t_k$ must satisfy:
$$t_{\text{information\_available}} \le t_k$$

## Forensic Inspection of Forecast Implementations
1. **`Stage81ForecastEngine`** (`system/forecasting/implementations/s81_solar.py`):
   - Consumes 37 frozen tabular features derived from satellite/NWP inputs available at or before $t_k$.
   - Transforms predicted $SW\_IN$ to PV power via frozen transformation $P_{PV} = \min(SW\_IN \times 51.0, 60000.0\text{ W})$.
   - Zero future ground truth target values enter feature construction.
2. **`WindSpeedARXForecastEngine`** (`system/forecasting/implementations/wind_arx.py`):
   - Consumes causal lag history of SMHI wind speed proxy at or before $t_k$.
   - Applies Ridge AR-X lag coefficients without looking ahead.
3. **`LocalBaselineForecastEngine`** (`system/forecasting/implementations/baseline.py`):
   - Consumes `station_state.last_observed_solar_irradiance`, `last_observed_wind_generation`, `last_observed_demand`.
   - Uses astronomical clear-sky solar curve and persistence lag. Zero future actuals accessed.

## Causality Verification Result
- **Future Truth Leakage**: 0 instances across all 8,784 cycles.
- **Causality Status**: **VERIFIED CAUSAL**.
