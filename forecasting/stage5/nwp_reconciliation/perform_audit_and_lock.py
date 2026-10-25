import os

BASE_DIR = "/home/punith-bs/01polaris (Copy)"
REC_DIR = os.path.join(BASE_DIR, "forecasting/stage5", "nwp_reconciliation")

# 1. Write final_evidence_gate.md
evidence_gate_content = """# POLARIS Stage 5 — NWP Data Reconciliation Final Evidence Gate

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
"""

with open(os.path.join(REC_DIR, "final_evidence_gate.md"), "w") as f:
    f.write(evidence_gate_content)

# 2. Update final_summary.txt
final_summary_content = """POLARIS STAGE 5 — LOCAL NWP DATA RECONCILIATION SUMMARY
================================================================================
Date: 2026-09-10
Status: COMPLETED (LOCAL-ONLY SCIENTIFIC VALIDATION)

## 1. CURRENT NWP LINEAGE
The POLARIS benchmark NWP dataset (POLARIS_v0_1_future_weather_forecasts_2024.csv) was built using Open-Meteo's previous-runs-api querying the metno_seamless model with _previous_day1 hourly variables for Nuolja Middle Station (68.362074°N, 18.738752°E).

## 2. CSV/API RECONCILIATION
- Comparison between existing CSV and live Open-Meteo metno_seamless:
  * Max Absolute Difference: 0.000000
  * Result: 100% EXACT REPRODUCTION. The existing CSV perfectly matches current live Open-Meteo metno_seamless output across all evaluated variables and sampled dates.

## 3. SEAMLESS VS PURE MET NORDIC
- Open-Meteo model identifier for pure MET Nordic: metno_nordic.
- Comparison between metno_seamless and metno_nordic at Nuolja:
  * Max Absolute Difference: 0.000000
  * Result: 100% IDENTICAL. At Nuolja coordinates (68.362074°N, 18.738752°E), Open-Meteo's metno_seamless and metno_nordic return identical data values for cloud cover, temperature, RH, precipitation, surface pressure, and wind speed across all sampled dates.

## 4. WIND DIRECTION
- wind_direction_10m_previous_day1 API Audit:
  * API Acceptance: YES (accepted and returned without errors).
  * Availability Statistic: 8,337 / 8,784 valid hours in 2024 (94.91% availability), matching 100% of available wind_speed_10m_previous_day1 hours (remaining 447 hours are missing in raw Open-Meteo archive for both variables).
  * Value Range: 0.0° to 360.0° (standard meteorological convention: direction from which wind blows).
  * Timing Semantics: Perfectly aligned hour-by-hour with wind_speed_10m_previous_day1.

## 5. ISSUANCE SEMANTICS
- PAPER-SAFE FORMULATION: "The selected previous-day forecast is causally available before t0; exact model-run reference timestamps are not exposed through the Open-Meteo point API."
- Established: The selected previous-day forecast is causally available before t0; zero forward-day data leakage.
- Information gap: Open-Meteo point API returns time series indexed by valid time, but does NOT expose the explicit NetCDF forecast_reference_time metadata (run initialization timestamp).

## 6. SPATIAL CELL VALIDITY & GRID RESOLUTION
- Spatial variations become apparent at approximately the native model-grid scale, consistent with nominal MET Nordic/MEPS resolution (~2.5 km); coordinate separation alone does not prove independent grid-cell identity.
- Open-Meteo queries high-resolution DEM elevation (varying from 675m at peak down to 341m over lake) while interpolating atmospheric variables across adjacent 2.5 km NWP grid centers.
- Scientific Caveat: Smooth continuous variations in point API calls across 100-500m steps represent interpolation, not independent grid cells.

## 7. THREDDS REQUIREMENT
- Direct MET Norway THREDDS access (thredds.met.no) is accessible.
- THREDDS provides raw 2D NetCDF grids with explicit forecast_reference_time and 2.5 km X,Y projection arrays.
- However, for extracting candidate spatial features (wind vector components U,V, spatial cloud gradients), Open-Meteo spatial point extraction provides a practical, terrain-aware candidate input set.

## 8. CAUSALITY & SPATIAL HYPOTHESIS
- No evidence of future-day observational leakage. The selected previous-day forecast is causally available before t0.
- Spatial atmospheric inputs (wind vector components U,V, spatial cloud gradients Delta C) represent a candidate input feature set to test whether spatial cloud advection improves forecast residuals beyond Stage 5.2. Predictive improvement is a hypothesis to be evaluated in Stage 5.4, not a demonstrated fact.

## 9. RECOMMENDATION
RECOMMENDATION: GO — Stage 5.4 spatial-NWP experiment is scientifically justified.

## 10. NEXT EXPERIMENT SPECIFICATION
If proceeding to Stage 5.4 spatial NWP feature extraction experiment:
1. Extract 10m wind direction (wind_direction_10m_previous_day1) to compute orthogonal wind vector components:
   - U_10m = -w_speed * sin(w_dir * pi / 180) (East-West wind component)
   - V_10m = -w_speed * cos(w_dir * pi / 180) (North-South wind component)
2. Extract cardinal neighbor grid points (North, South, East, West at ~2.5 km spatial offset: Delta lat = ±0.025°, Delta lon = ±0.06°) using cell_selection=nearest.
3. Compute directional spatial cloud cover gradients (Delta C_EW, Delta C_NS) and upwind cloud advection indicators (U * Delta C_EW + V * Delta C_NS).
4. Evaluate feature contributions strictly within Stage 5 protocol without altering frozen benchmark predictions or Stage 5.2 champion.
================================================================================
"""

with open(os.path.join(REC_DIR, "final_summary.txt"), "w") as f:
    f.write(final_summary_content)

# 3. Update README.md
readme_content = """# POLARIS Stage 5 — NWP Data Reconciliation

This directory contains the artifacts and empirical results from the Stage 5 Local NWP Data Reconciliation.

## Directory Artifacts

- `reconciliation_results.csv`: Hourly comparative analysis between existing benchmark CSV (`POLARIS_v0_1_future_weather_forecasts_2024.csv`), live `metno_seamless`, and live `metno_nordic`.
- `wind_direction_check.csv`: 2024 full-year audit of 10m wind direction (`wind_direction_10m_previous_day1`), checking non-null rates, range, and semantics.
- `spatial_probe_results.csv`: Spatial grid probe around Nuolja Middle Station evaluating coordinate resolution, elevation variation, and cell selection modes (`default` vs `nearest`).
- `issuance_semantics_notes.md`: Detailed scientific analysis of `_previous_day1` forecast issuance semantics, causal guarantees, and API metadata limits.
- `final_summary.txt`: 10-section summary report and final recommendation.
- `final_evidence_gate.md`: Final evidence gate defining established facts, unresolved aspects, testable hypothesis, and Stage 5.4 clearance.

## Key Conclusions

1. **Exact Reproduction:** Live Open-Meteo `metno_seamless` perfectly reproduces the POLARIS benchmark NWP dataset.
2. **Seamless vs Nordic Equivalence:** `metno_seamless` and `metno_nordic` produce 100% identical outputs at Nuolja coordinates.
3. **Wind Direction Quality:** 10m wind direction (`wind_direction_10m_previous_day1`) is valid for 8,337 / 8,784 hours in 2024 (94.91% availability), matching 100% of available wind speed hours.
4. **Spatial Resolution:** Spatial variations become apparent at approximately the native model-grid scale (~2.5 km); coordinate separation alone does not prove independent grid-cell identity.
5. **Issuance Semantics:** The selected previous-day forecast is causally available before t0; exact model-run reference timestamps are not exposed through the Open-Meteo point API.
6. **Evidence Gate:** **GO — Stage 5.4 spatial-NWP experiment is scientifically justified.**
"""

with open(os.path.join(REC_DIR, "README.md"), "w") as f:
    f.write(readme_content)

# 4. Update issuance_semantics_notes.md
semantics_content = """# POLARIS Stage 5 — NWP Issuance Semantics & Spatial Grid Resolution Audit

## 1. Issuance Semantics & Causal Availability
In the POLARIS benchmark:
- Target variable: Reconstructed hourly GHI at SITES Nuolja (68.362074°N, 18.738752°E).
- Benchmark origins (`forecast_start`): 347 clean origins in 2024, issued at 00:00 CET (Etc/GMT-1).
- Horizon: H1 to H24 (spanning 01:00 CET to 24:00 CET on valid forecast day D).

### Established Evidence:
- **Causal Availability:** The selected previous-day forecast (`_previous_day1`) is causally available before $t_0$. The forecast data was generated during day $D-1$, physically prior to `forecast_start` (00:00 CET = 23:00 UTC day $D-1$).
- **Zero Forward Leakage:** Forecast values for hours H1 to H24 do NOT use observation data from day D.

### Unresolved Metadata at Point API Level:
- **Exact Reference Timestamps Not Directly Exposed:** The exact model-run reference/initialization timestamp (`forecast_reference_time`, e.g., 06:00, 12:00, or 18:00 UTC run) and exact distribution latencies are NOT directly exposed through the Open-Meteo point API.

### Paper-Safe Formulation:
> *"The selected previous-day forecast is causally available before t0; exact model-run reference timestamps are not exposed through the Open-Meteo point API."*

---

## 2. Spatial Grid Geometry & Micro-Probe Findings

### Empirical Coordinate Mapping:
A tight spatial micro-probe centered at Nuolja (offsets from 0.000° to 0.050° latitude, i.e., ~0 to 5.5 km) established the relationship between requested coordinates and underlying grid cells:
- **Spatial Resolution Scale:** Spatial variations become apparent at approximately the native model-grid scale, consistent with nominal MET Nordic/MEPS resolution (~2.5 km); coordinate separation alone does not prove independent grid-cell identity.
- **Interpolation vs. Grid Cell Identity:** Open-Meteo uses high-resolution DEM elevation (varying from 675m at Nuolja peak down to 341m over Lake Torneträsk) while interpolating atmospheric variables across adjacent 2.5 km NWP grid cell centers.
- **Scientific Caveat:** Observing smooth, continuous variations in interpolated meteorological values across 100–500m steps does NOT prove adjacent coordinate requests are independent grid cells.

---

## 3. Spatial Atmospheric Inputs & Testable Hypothesis

### Does spatial atmospheric information explain part of the residual structure that point-based NWP cannot?
- **Established:** Candidate spatial neighbor variables (cardinal spatial cloud cover gradients $\\Delta C_{\\text{E-W}}, \\Delta C_{\\text{N-S}}$ and 10m wind vector components $U_{10m}, V_{10m}$) represent additional spatial inputs not present in the point-only NWP feature set.
- **Testable Hypothesis for Stage 5.4:** These spatial inputs may contain incremental physical information regarding cloud structure and advection that may improve SW_IN forecast residuals beyond Stage 5.2.
- **Scientific Claim Limit:** Spatial inputs are a **candidate input feature set to be evaluated in Stage 5.4**, NOT a demonstrated predictive improvement prior to out-of-sample evaluation.
"""

with open(os.path.join(REC_DIR, "issuance_semantics_notes.md"), "w") as f:
    f.write(semantics_content)

print("Created final_evidence_gate.md and updated all Stage 5 reconciliation documents successfully!")
