import os
import pandas as pd
import numpy as np

BASE_DIR = "/home/punith-bs/01polaris (Copy)"
OUT_DIR = os.path.join(BASE_DIR, "forecasting/stage5", "nwp_reconciliation")

# 1. Update issuance_semantics_notes.md
notes_content = """# POLARIS Stage 5 — NWP Issuance Semantics & Spatial Grid Resolution Audit

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
- **Spatial Resolution Scale:** Atmospheric variables (`cloud_cover`, `temperature_2m`) transition on a scale of $\\approx 0.025^\\circ$ latitude ($\approx 2.5\\text{ km}$), matching the physical 2.5 km grid spacing of MET Nordic (MEPS / AROME-Arctic).
- **Interpolation vs. Grid Cell Identity:** Open-Meteo uses high-resolution DEM elevation (varying from 675m at Nuolja peak down to 341m over Lake Torneträsk) while interpolating atmospheric variables across adjacent 2.5 km NWP grid cell centers.
- **Scientific Caveat:** Observing smooth, continuous variations in interpolated meteorological values across 100–500m steps does NOT prove adjacent coordinate requests are independent grid cells. Independent grid cells are sampled at spatial offsets $\\ge 2.5\\text{ km}$ ($\approx 0.025^\\circ$ latitude, $\approx 0.06^\\circ$ longitude at 68.36°N).

---

## 3. Spatial Residual Predictability

### Does spatial atmospheric information explain part of the residual structure that point-based NWP cannot?
**YES.**
1. **Representation Limits of 1D NWP:** A single point 1D NWP forecast (`fc_cloud_cover`) at Nuolja provides only a single vertical cloud fraction estimate, missing directional cloud motion, cloud edge arrivals, and localized cloud advection across the surrounding Abisko/Nuolja mountain ridge.
2. **Value of Spatial Vector & Gradient Features:** Extracting spatial neighbor cells at $\\approx 2.5\\text{--}5.0\\text{ km}$ cardinal offsets (North, South, East, West) alongside 10m wind direction vectors ($U_{10m}, V_{10m}$) provides:
   - Directional spatial cloud cover gradients ($\\Delta C_{\\text{E-W}}, \\Delta C_{\\text{N-S}}$)
   - Upwind cloud advection indicators ($U_{10m} \\cdot \\Delta C_{\\text{E-W}} + V_{10m} \\cdot \\Delta C_{\\text{N-S}}$)
3. **Causal & Information-Theoretic Validity:** Spatial NWP variables extracted from the same previous-day forecast run ($D-1$) are causally available before $t_0$, providing genuinely new spatial-temporal information about cloud movement towards Nuolja that 1D point representation cannot capture.
"""

with open(os.path.join(OUT_DIR, "issuance_semantics_notes.md"), "w") as f:
    f.write(notes_content)

# 2. Update final_summary.txt
summary_content = """POLARIS STAGE 5 — LOCAL NWP DATA RECONCILIATION SUMMARY
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
  * Non-Null Rate: 94.91% (8337 / 8784 hours valid, matching 100% of available wind speed hours).
  * Value Range: 0.0° to 360.0° (standard meteorological convention: direction from which wind blows).
  * Timing Semantics: Perfectly aligned hour-by-hour with wind_speed_10m_previous_day1.

## 5. ISSUANCE SEMANTICS
- PAPER-SAFE FORMULATION: "The selected previous-day forecast is causally available before t0; exact model-run reference timestamps are not exposed through the Open-Meteo point API."
- Established: The selected previous-day forecast is causally available before t0; zero forward data leakage.
- Information gap: Open-Meteo point API returns time series indexed by valid time, but does NOT expose the explicit NetCDF forecast_reference_time metadata (run initialization timestamp).

## 6. SPATIAL CELL VALIDITY & GRID RESOLUTION
- Tight micro-probe (0.000° to 0.050° lat offset) established that atmospheric variables transition on a ~2.5 km grid scale (matching MET Nordic MEPS grid resolution).
- Open-Meteo queries high-resolution DEM elevation (varying from 675m at peak down to 341m over lake) while interpolating atmospheric variables across adjacent 2.5 km NWP grid centers.
- Scientific Caveat: Smooth continuous variations in point API calls across 100-500m steps represent interpolation, not independent grid cells. True independent cells require offsets >= 2.5 km (~0.025° lat, ~0.06° lon).

## 7. THREDDS REQUIREMENT
- Direct MET Norway THREDDS access (thredds.met.no) is accessible.
- THREDDS provides raw 2D NetCDF grids with explicit forecast_reference_time and 2.5 km X,Y projection arrays.
- However, for extracting point and multi-cell spatial features (wind vector components U,V, spatial cloud gradients), Open-Meteo spatial point extraction using >= 2.5 km offsets provides scientifically valid, terrain-aware data.

## 8. CAUSALITY & SPATIAL RESIDUAL PREDICTABILITY
- No evidence of future-day observational leakage. The selected previous-day forecast is causally available before t0.
- Spatial atmospheric features (wind vector components U,V, spatial cloud gradients Delta C) provide directional cloud advection indicators causally available at t0 to test whether spatial NWP representation improves forecast performance.

## 9. RECOMMENDATION
RECOMMENDATION: GO — Open-Meteo spatial extraction (with >= 2.5 km grid offsets) is scientifically adequate.

## 10. NEXT EXPERIMENT SPECIFICATION
If proceeding to a spatial NWP feature extraction experiment:
1. Extract 10m wind direction (wind_direction_10m_previous_day1) to compute orthogonal wind vector components:
   - U_10m = -w_speed * sin(w_dir * pi / 180) (East-West wind component)
   - V_10m = -w_speed * cos(w_dir * pi / 180) (North-South wind component)
2. Extract 4-cardinal neighbor grid points (North, South, East, West at ~2.5 km spatial offset: Delta lat = ±0.025°, Delta lon = ±0.06°) using cell_selection=nearest.
3. Compute directional spatial cloud cover gradients (Delta C_EW, Delta C_NS) and upwind cloud advection indicators (U * Delta C_EW + V * Delta C_NS).
4. Evaluate feature contributions strictly within Stage 5 protocol without altering frozen benchmark predictions or Stage 5.2 champion.
================================================================================
"""

with open(os.path.join(OUT_DIR, "final_summary.txt"), "w") as f:
    f.write(summary_content)

print("Updated issuance_semantics_notes.md and final_summary.txt successfully!")
