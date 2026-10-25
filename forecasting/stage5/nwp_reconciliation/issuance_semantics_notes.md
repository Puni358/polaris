# POLARIS Stage 5 — NWP Issuance Semantics & Spatial Grid Resolution Audit

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
- **Established:** Candidate spatial neighbor variables (cardinal spatial cloud cover gradients $\Delta C_{\text{E-W}}, \Delta C_{\text{N-S}}$ and 10m wind vector components $U_{10m}, V_{10m}$) represent additional spatial inputs not present in the point-only NWP feature set.
- **Testable Hypothesis for Stage 5.4:** These spatial inputs may contain incremental physical information regarding cloud structure and advection that may improve SW_IN forecast residuals beyond Stage 5.2.
- **Scientific Claim Limit:** Spatial inputs are a **candidate input feature set to be evaluated in Stage 5.4**, NOT a demonstrated predictive improvement prior to out-of-sample evaluation.
