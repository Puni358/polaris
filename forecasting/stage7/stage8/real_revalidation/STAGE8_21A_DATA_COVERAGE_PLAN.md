# POLARIS STAGE 8.21A — DATA COVERAGE PLAN REPORT

## 1. Domain Lock & Extraction Bounds

- **Extracted Spatial Window:** $47 \times 47$ MEPS Grid Window ($57.5\text{ km}$ cardinal radius, $81.32\text{ km}$ corner radius, $115.0\text{ km}$ physical span)
- **Bounding Box Indices (MEPS Grid):** $y \in [736:783]$, $x \in [462:509]$ (centered at Nuolja $y=760, x=486$)
- **Solar Elevation Domain:** Solar elevation $\ge 5.0^\circ$ ($\theta_z \le 85.0^\circ$)
- **Relevant Solar Ray Population:** $N = 3,285$ tuples
- **Empirically Covered Rays:** $N = 3,262$ tuples (**$99.30\%$ coverage**)
- **Outside-Window Handling:** $N = 23$ rays ($0.70\%$). Deterministic fallback to station grid column 1D vertical column optical thickness without benchmark denominator alteration.

---

## 2. Server-Side OPeNDAP Extraction Protocol

- **Archive Source:** MET Norway MEPS Deterministic Archive (`meps25epsarchive`)
- **Dataset Pattern:** `meps_det_pl_YYYYMMDDT18Z.ncml` ($D-1$ $18:00\text{ UTC}$ run)
- **Extracted Variables (4 Float32 Fields):**
  1. `mass_fraction_of_cloud_condensed_water_in_air_pl` ($q_l$)
  2. `mass_fraction_of_cloud_ice_in_air_pl` ($q_i$)
  3. `air_temperature_pl` ($T$)
  4. `specific_humidity_pl` ($q_v$)
- **Vertical Levels:** 13 pressure levels ($50 \dots 1000\text{ hPa}$)
- **Batch Payload Size:** $\mathbf{3.56\text{ GB}}$ total across 347 benchmark origins ($\sim 10.51\text{ MB}$ per origin).
- **OPeNDAP Execution Time:** Estimated $< 25\text{ min}$ batch download with local disk caching.
