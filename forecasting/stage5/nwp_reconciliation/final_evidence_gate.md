# POLARIS Stage 5 — NWP Data Reconciliation Final Evidence Gate

## ESTABLISHED
1. **CSV & API Reconciliation:** Live Open-Meteo `metno_seamless` (`_previous_day1`) queries match existing benchmark dataset `POLARIS_v0_1_future_weather_forecasts_2024.csv` with zero discrepancy (0.000000 max absolute difference across sampled dates).
2. **Model Equivalence at Nuolja:** Open-Meteo `metno_seamless` and `metno_nordic` return 100% identical outputs at Nuolja Middle Station coordinates (68.362074°N, 18.738752°E).
3. **Wind Direction Candidate Input:** `wind_direction_10m_previous_day1` is valid and non-null for 8,337 / 8,784 hours in 2024 (94.91% availability), matching 100% of `wind_speed_10m_previous_day1` availability (the remaining 447 hours are missing in raw Open-Meteo source files for both variables). Units follow standard meteorological convention (0.0° to 360.0°).
4. **Causal Availability:** The selected previous-day forecast is causally available before t0 = 00:00 CET on day D, ensuring zero forward-day observational leakage.
5. **Spatial Resolution:** Spatial variations in NWP fields become apparent at approximately the native model-grid scale, consistent with nominal MET Nordic/MEPS resolution (~2.5 km).

## UNRESOLVED
1. **Model-Run Reference Timestamp:** Open-Meteo's point API returns time series indexed by valid forecast time, but does NOT directly expose the NetCDF `forecast_reference_time` attribute (exact initialization run timestamp, e.g. 06:00, 12:00, or 18:00 UTC) or operational distribution latency.
2. **Underlying Grid Index Mapping:** Coordinate separation alone does not prove independent grid-cell mapping without explicit model grid index metadata.

## TESTABLE HYPOTHESIS
- **Hypothesis:** Candidate spatial atmospheric inputs (10m wind vector components U_10m, V_10m, cardinal spatial cloud gradients Delta C_EW, Delta C_NS, and upwind cloud advection indicators U * Delta C_EW + V * Delta C_NS) contain incremental physical information about spatial cloud structure and advection that may improve daytime GHI forecast residuals beyond Stage 5.2.

## GO / NO-GO
**GO — Stage 5.4 spatial-NWP experiment is scientifically justified.**

## REQUIRED STAGE 5.4 INPUTS
1. Zonal wind vector component: U_10m = -w_speed * sin(w_dir * pi / 180)
2. Meridional wind vector component: V_10m = -w_speed * cos(w_dir * pi / 180)
3. Cardinal spatial neighbor cloud cover features (~2.5 km spatial offsets)
4. Spatial cloud cover gradients: Delta C_EW, Delta C_NS
5. Upwind advection proxy: U_10m * Delta C_EW + V_10m * Delta C_NS

## SCIENTIFIC CLAIM LIMIT
Candidate spatial inputs are a **testable hypothesis for incremental predictive information**, NOT a demonstrated predictive improvement. Stage 5.4 must empirically determine whether these inputs improve out-of-sample performance over frozen Stage 5.2.
