# POLARIS Stage 8.0 — Vertical Coordinate Audit Report

## 1. Structure of Native MEPS Hybrid Levels
- **Total Model Levels:** 65 hybrid levels (`hybrid` dimension = 65).
- **Ordering:** Top-to-bottom (Level 0 = Top of atmosphere ~10 hPa, Level 64 = lowest model level near surface ~10m a.g.l.).
- **Hybrid Pressure Equation:**
  $$p(k, y, x) = a_p(k) + b(k) \cdot p_{\text{sfc}}(y, x)$$
  where $a_p(k)$ is in Pascals, $b(k)$ is dimensionless $[0, 1]$, and $p_{\text{sfc}}$ is surface pressure in Pascals.

## 2. Nuolja Topography Alignment
- **Station Elevation:** 675 m a.s.l.
- **MEPS Surface Pressure at Nuolja ($y=760, x=486$):** ~940–960 hPa.
- **Lowest Model Level Pressure:** ~940 hPa (follows model surface elevation ~220m).
- **Physical Interpretation:** In `meps_det_ml`, levels near $k=60..64$ lie within the planetary boundary layer around Nuolja. However, because $18Z$ files are missing for `ml`, reconstructing model-level profiles is restricted to $00Z$ forecasts.
