# POLARIS Stage 8.0 — Nuolja Point Extraction Audit

## 1. Sampling Results (y=760, x=486)
Sample extractions for 2024-01-01T00Z:

| Variable | Extracted Sample Values | Units | Valid / Masking Required |
| :--- | :--- | :--- | :--- |
| `cloud_base_altitude` | `7926.3, 7502.5, 8836.0, 9841.5, 8833.3, 9.96921e+36` | `m` | **REQUIRES FILL MASKING** (`9.96921e+36` = clear sky) |
| `cloud_top_altitude` | `8369.4, 8833.1, 9845.1, 9841.6, 8833.3, 9.96921e+36` | `m` | **REQUIRES FILL MASKING** (`9.96921e+36` = clear sky) |
| `x_wind_pl` (700 hPa) | `-0.47, -1.03, -1.47, -1.95, -2.74, -3.78` | `m/s` | **CLEAN** |
| `y_wind_pl` (700 hPa) | `-0.75, -0.74, -1.29, -2.15, -2.00, -1.70` | `m/s` | **CLEAN** |
| `surface_air_pressure` | `96034.9, 96017.1, 96052.6, 96023.3, 96003.7` | `Pa` | **CLEAN** (~960 hPa) |

## 2. Integrity Verification
- **NaNs / Infs:** Zero NaNs or Infs detected.
- **Fill Values:** `cloud_base_altitude` and `cloud_top_altitude` use $9.96921 \times 10^{36}$ when no clouds are present. Any candidate feature script MUST replace fill values with physical height bounds (e.g. 0m or surface elevation).
