# Stage 7.4 MEPS Pressure Level Variable Inventory

## Archive Specification
* **Source**: MET Norway MEPS Deterministic Archive (`meps25epsarchive` on `thredds.met.no`)
* **Primary Collections**: `meps_det_pl_YYYYMMDDTHHZ.ncml` and `meps_det_sfc_YYYYMMDDTHHZ.ncml`
* **Grid Coordinates**: $y=760, x=486$ ($68.355701^\circ	ext{N}, 18.763666^\circ	ext{E}$, distance $1.24	ext{ km}$ to Nuolja)

## 13 Isobaric Pressure Levels
The MEPS pressure level collection contains exactly 13 fixed hydrostatic levels:
`[50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700.0, 800.0, 850.0, 925.0, 1000.0] hPa`

## Extracted & Audited Variables

| Variable Name in Archive | Physical Property | Standard Units | Dimension Shape | Missing Value Code |
| :--- | :--- | :---: | :---: | :---: |
| `mass_fraction_of_cloud_condensed_water_in_air_pl` | Cloud Liquid Water Content ($q_l$) | $	ext{kg/kg}$ | `(67, 13, 1069, 949)` | None ($0.0$ default) |
| `mass_fraction_of_cloud_ice_in_air_pl` | Cloud Ice Water Content ($q_i$) | $	ext{kg/kg}$ | `(67, 13, 1069, 949)` | None ($0.0$ default) |
| `cloud_area_fraction_pl` | Layer Cloud Area Fraction ($	ext{CF}_k$) | $0 \dots 1$ | `(67, 13, 1069, 949)` | None ($0.0$ default) |
| `mass_fraction_of_snow_in_air_pl` | Falling Snow Content ($q_s$) | $	ext{kg/kg}$ | `(67, 13, 1069, 949)` | None ($0.0$ default) |
| `mass_fraction_of_rain_in_air_pl` | Falling Rain Content ($q_r$) | $	ext{kg/kg}$ | `(67, 13, 1069, 949)` | None ($0.0$ default) |
| `air_temperature_pl` | Air Temperature ($T_k$) | $	ext{K}$ | `(67, 13, 1069, 949)` | None |
| `specific_humidity_pl` | Specific Humidity ($q_v$) | $	ext{kg/kg}$ | `(67, 13, 1069, 949)` | None |
| `x_wind_pl` / `y_wind_pl` | Horizontal Wind Components ($u, v$) | $	ext{m/s}$ | `(67, 13, 1069, 949)` | None |
| `surface_air_pressure` | Model Surface Air Pressure ($p_{	ext{sfc}}$) | $	ext{Pa}$ | `(67, 1, 1069, 949)` | None |

## Surface-Aware Integration Boundary
Because Nuolja is situated at elevation $702	ext{ m a.s.l.}$, model surface pressure ($p_{	ext{sfc}}$) ranges from $938.5	ext{ hPa}$ to $954.0	ext{ hPa}$. The $1000	ext{ hPa}$ level (and occasionally $925	ext{ hPa}$) is subterranean. All vertical integrations linearly interpolate at $p_{	ext{sfc}}$ and set subterranean layer weights to $0.0$.
