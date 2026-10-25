# STAGE 7.5 — TERRAIN / HORIZON RADIATIVE GEOMETRY FEASIBILITY VERIFICATION REPORT

**Stage:** Stage 7.5  
**Date:** September 12, 2026  
**Feasibility Recommendation:** **GO**  
**Forecasting Experiment Status:** **NOT STARTED**  
**ODD Test Set Status:** **100% UNTOUCHED & LOCKED**  

---

## 1. Executive Summary

Stage 7.5 conducted a rigorous data and causality feasibility verification to evaluate whether high-resolution local terrain and horizon geometry (Copernicus DEM 30m) around Nuolja station ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$) provides a physically distinct, causally valid information source for surface shortwave radiation forecasting.

### Key Feasibility Findings:
1. **DEM Verification:** High-resolution Copernicus GLO-30 DEM tile (`Copernicus_DSM_COG_10_N68_00_E018_00_DEM.tif`) covers Nuolja station perfectly with $30\text{ m}$ resolution. Station DEM elevation is $668.61\text{ m a.s.l.}$
2. **Horizon Profile Extraction:** 360-degree radial ray-marching out to $25\text{ km}$ revealed significant terrain horizon obstruction around Nuolja, ranging from $0.00^\circ$ (towards Torneträsk valley to the ENE) up to $29.80^\circ$ (towards Mt. Nuolja peak ridge to the WSW).
3. **Physical Shading Impact:** Out of $4,383$ daylight hours in 2024 (solar elevation $> 0^\circ$), local mountain terrain obstructs direct solar radiation for **1624 hours (36.51% of sunlit hours)**, concentrated during low solar elevation ($\gamma_s \le 12.8^\circ$) near sunrise/sunset transitions.
4. **Physical Novelty of Direction-Dependent Horizon Geometry:** Terrain obstruction provides non-trivial geometric attenuation distinct from pure solar elevation ($
ho = 0.8810$) and unadjusted clear-sky GHI ($
ho = 0.8002$).
5. **Causality & Data Lock:** Static DEM topography and astronomical solar geometry involve zero future observations or target leakage (**100% causally valid**).

**Feasibility Recommendation:** **GO** (Proceed to authorized candidate forecasting experiment when requested).

---

## 2. Quantitative Summary Table

| Metric / Parameter | Value |
|---|---|
| Target Coordinates | $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$ |
| DEM Resolution | 30 meters (Copernicus GLO-30) |
| Station Elevation | $668.61\text{ m a.s.l.}$ |
| Ray Search Radius | $25\text{ km}$ |
| Horizon Azimuths | 360 degrees ($1^\circ$ step) |
| Maximum Horizon Obstruction Angle | $29.80^\circ$ (Azimuth 252^\circ) |
| 2024 Sunlit Hours | 4448 hours |
| 2024 Terrain Obstructed Hours | **1624 hours (36.51%)** |
| Spearman $\rho$ (`terrain_elevation_margin` vs `solar_elevation`) | $0.8810$ |

---

## 3. Recommended Candidate Terrain Features (4 Features)

1. `terrain_horizon_elevation_deg`: Local terrain horizon elevation angle at solar azimuth ($^\circ$).
2. `terrain_elevation_margin_deg`: Angular margin $\gamma_s - \alpha_{\text{max}}(\theta_s)$ ($^\circ$).
3. `terrain_solar_obstruction_flag`: Binary shading flag ($1$ if shaded by terrain, $0$ otherwise).
4. `clearsky_ghi_terrain_adjusted`: A physically derived transformation of the existing clear-sky GHI feature using the local terrain obstruction geometry. The genuinely new physical information source is Copernicus DEM -> local terrain elevation -> azimuth-dependent horizon geometry.

---

## 4. Governance & Verification Checklist

- [x] DEM source verified and downloaded
- [x] Station coordinate transformation verified
- [x] Horizon geometry ray-marching complete
- [x] 100% causal alignment verified (static DEM + astronomical solar geometry)
- [x] ODD test set **100% UNTOUCHED & LOCKED**
- [x] Zero model training or CV executed
- [x] Stage 6.6 Champion preserved ($37.005888\text{ W/m}^2$ ODD MAE)
