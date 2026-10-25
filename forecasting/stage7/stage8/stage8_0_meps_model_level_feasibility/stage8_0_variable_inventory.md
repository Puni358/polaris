# POLARIS Stage 8.0 — Variable Inventory Audit Report

## 1. Verified NetCDF Metadata

| Internal ID | Variable Name in Archive | Standard Name | Units | Product File | Verified in 2024 Archive |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `q_l_ml` | `mass_fraction_of_cloud_condensed_water_in_air_ml` | `mass_fraction_of_cloud_liquid_water_in_air` | `kg/kg` | `meps_det_ml` | **YES (00Z only)** |
| `q_i_ml` | `mass_fraction_of_cloud_ice_in_air_ml` | `mass_fraction_of_cloud_ice_in_air` | `kg/kg` | `meps_det_ml` | **YES (00Z only)** |
| `cloud_base` | `cloud_base_altitude` | `cloud_base_altitude` | `m` | `meps_det_sfc` | **YES (18Z & 00Z)** |
| `cloud_top` | `cloud_top_altitude` | `cloud_top_altitude` | `m` | `meps_det_sfc` | **YES (18Z & 00Z)** |
| `x_wind_pl` | `x_wind_pl` | `x_wind` | `m/s` | `meps_det_pl` | **YES (18Z & 00Z)** |
| `y_wind_pl` | `y_wind_pl` | `y_wind` | `m/s` | `meps_det_pl` | **YES (18Z & 00Z)** |
| `ap` | `ap` | `ak` | `Pa` | `meps_det_ml` | **YES (00Z only)** |
| `b` | `b` | `bk` | `1` | `meps_det_ml` | **YES (00Z only)** |
| `p_sfc` | `surface_air_pressure` | `surface_air_pressure` | `Pa` | `meps_det_sfc` | **YES (18Z & 00Z)** |

## 2. Unverified / Non-Existant Variables
- `cloud_thickness`: Not present as a raw variable (must be derived as `cloud_top - cloud_base`).
- `cloud_base_pressure`: Not present in 2024 `sfc` product (altitude is provided in meters).
