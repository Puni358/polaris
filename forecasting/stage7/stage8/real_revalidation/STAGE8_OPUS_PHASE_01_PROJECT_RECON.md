# POLARIS STAGE 8 — OPUS PHASE 0+1: PROJECT RECONCILIATION & EXISTING INFORMATION MAP

> [!IMPORTANT]
> **GOVERNANCE STATUS: RESEARCH INVESTIGATION ONLY — NO EXPERIMENTS**
> - **Operational Champion:** Stage 8.1 37-feature HGB Model (ODD nMAE 28.0688%)
> - **ODD Benchmark:** 100% UNTOUCHED & PROTECTED
> - **Master Handoff & Route Registry:** UNTOUCHED

---

## 1. Phase 0 — Project Reconciliation Summary

Phase 0 independently verified all 45 project artifacts (SHA256 hash-matched), cross-audited 10 closure/feasibility reports, confirmed the Stage 8.1 champion provenance (6/6 checks passed), and documented the invalidation of Stage 8.19.

### Key Reconciliation Findings
1. **Stage 8.1** is the sole valid operational champion with verified real-data ODD metrics
2. **Stage 8.19** (ABIS GNSS) is demonstrably synthetic/invalid — seed-based random features, hardcoded metric literals
3. **Stage 8.17A** (AROME Disagreement) was rejected by real-data revalidation — real AROME degraded ODD by +0.2154 W/m²
4. **Stage 8.24** (Orographic Flow) carries an implementation qualification — the pre-registered continuous Brunt-Väisälä formulation was never faithfully tested
5. **Route Registry** still lists Stage 8.19 as champion (stale) — NOT modified per governance constraints

---

## 2. Phase 1 — Existing Information Map

### Stage 8.1 Champion Feature Inventory (37 Features)

#### A. Historical Irradiance (14 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ctx_std_3h` | SW_IN variability (3h) | Point (Nuolja pyranometer) | 3-hour lookback | Observed | No position; temporal variability |
| `ctx_std_6h` | SW_IN variability (6h) | Point | 6-hour lookback | Observed | No position; temporal variability |
| `ctx_std_12h` | SW_IN variability (12h) | Point | 12-hour lookback | Observed | No position; temporal variability |
| `ctx_std_24h` | SW_IN variability (24h) | Point | 24-hour lookback | Observed | No position; temporal variability |
| `ctx_abs_change_1h` | Absolute SW_IN change (1h) | Point | 1-hour | Observed | No position; rate-of-change |
| `ctx_abs_change_3h` | Absolute SW_IN change (3h) | Point | 3-hour | Observed | No position; rate-of-change |
| `ctx_abs_change_6h` | Absolute SW_IN change (6h) | Point | 6-hour | Observed | No position; rate-of-change |
| `ctx_max_diff_6h` | Max hourly SW_IN difference (6h) | Point | 6-hour | Observed | No position; extreme transitions |
| `ctx_mean_diff_6h` | Mean hourly SW_IN difference (6h) | Point | 6-hour | Observed | No position; mean transitions |
| `ctx_slope_6h` | Linear trend of SW_IN (6h) | Point | 6-hour | Observed | No position; trend direction |
| `ctx_kt_std_6h` | Clear-sky index variability (6h) | Point | 6-hour | Derived (obs/model) | No position; cloud intermittency |
| `ctx_last_obs` | Most recent SW_IN observation | Point | Instantaneous | Observed | No position; current state |
| `ctx_mean_24h` | Mean SW_IN (24h) | Point | 24-hour | Observed | No position; daily context |
| `ctx_max_24h` | Max SW_IN (24h) | Point | 24-hour | Observed | No position; peak irradiance |

**Closest closed routes:** Stage 8.23 (local state), Cloud Evolution (ground radiometer proxies deemed redundant with these features)

#### B. Solar Geometry (3 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `solar_elevation` | Sun elevation angle above horizon | Exact (astronomical) | Per-hour | Deterministic | No |
| `solar_zenith` (= `clearsky_ghi` implicit) | Sun zenith angle | Exact | Per-hour | Deterministic | No |
| `clearsky_ghi` | Solis clear-sky GHI model | Exact | Per-hour | Modeled (parameterized) | No |

**Also encoded by:** `horizon_hour`, `month`, `hour` (temporal indices)

#### C. Terrain / Horizon Geometry (4 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `terrain_horizon_elevation_deg` | Horizon obstruction angle at solar azimuth | 30m DEM, local | Static per hour | Modeled (DEM) | No |
| `terrain_elevation_margin_deg` | Solar elevation minus horizon elevation | Local | Per-hour | Derived | No |
| `terrain_solar_obstruction_flag` | Binary: sun below terrain horizon | Local | Per-hour | Derived | No |
| `clearsky_ghi_terrain_adjusted` | Clear-sky GHI accounting for terrain | Local | Per-hour | Derived | No |

**Closed route:** Stage 7.5 (INTEGRATED), Terrain Reflection (CLOSED_IMMATERIAL)

#### D. Thermodynamic State (1 feature)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fc_temperature_2m` | MEPS 2m temperature forecast | 2.5km grid | Per-hour forecast | Modeled (NWP) | No |

**Closed routes:** Stage 8.23 (local TA/RH/dewpoint REJECTED_ON_EVEN)

#### E. Humidity (1 feature)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fc_relative_humidity_2m` | MEPS 2m relative humidity forecast | 2.5km grid | Per-hour forecast | Modeled (NWP) | No |

**Note:** MEPS also provides humidity at 925, 850, 700, 500 hPa but these are NOT in Stage 8.1 (Stage 8.0/8.10 rejected). Atmospheric radiative physics audit confirmed vertical humidity profile redistribution is immaterial (<1.8 W/m²).

#### F. Wind (2 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `u700` | MEPS 700 hPa u-wind (steering wind) | 2.5km grid | Per-hour forecast | Modeled (NWP) | Contains advection direction |
| `v700` | MEPS 700 hPa v-wind (steering wind) | 2.5km grid | Per-hour forecast | Modeled (NWP) | Contains advection direction |

**Closed routes:** Stage 8.1 (CHAMPION — these are the Stage 8.1 additions), Stage 8.24 (barrier-normal projection + Froude PROVISIONAL_REJECTION)

#### G. Cloud State (2 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fc_cloud_cover` | MEPS total cloud cover fraction | 2.5km grid | Per-hour forecast | Modeled (NWP) | No position/motion |
| `cloud_frac` | MEPS cloud fraction (diagnostic) | 2.5km grid | Per-hour forecast | Modeled (NWP) | No position/motion |

**Closed routes:** Stage 8.5 (spatial cloud fields REJECTED), Stage 8.8 (cloud geometry REJECTED), Stage 8.9A (independent cloud state REJECTED), Cloud Evolution (CLOSED_FEASIBILITY)

#### H. LWP / IWP (3 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `lwp_latest` | MEPS vertically-integrated liquid water path | 2.5km grid | Per-hour forecast | Modeled (NWP) | No position/motion |
| `iwp_latest` | MEPS vertically-integrated ice water path | 2.5km grid | Per-hour forecast | Modeled (NWP) | No position/motion |
| `lwp_x_cloud` | LWP × cloud fraction interaction | 2.5km grid | Per-hour forecast | Derived (NWP) | No position/motion |

**Closed routes:** Stage 6.6 (ACCEPTED & INTEGRATED), Stage 8.16B-1 (LWP ensemble spread REJECTED)

#### I. Spatial NWP Cloud Information
**NOT IN Stage 8.1.** Stage 8.5 tested 9×9 neighborhood cloud summaries and they failed EVEN due to NWP spatial displacement errors.

#### J. NWP Uncertainty / Revisions
**NOT IN Stage 8.1.** Stage 6.4 (NWP run-to-run revisions) and Stage 8.16B (ensemble spread) both REJECTED.

#### K. Aerosol / TCWV
**NOT IN Stage 8.1.** Stage 8.6 (CAMS AOD + TCWV) REJECTED — pristine Arctic AOD immaterial.

#### L. Local Observations
**NOT IN Stage 8.1 beyond SW_IN context features.** Stage 8.3 (Abisko ground radiation) CLOSED_NON_CAUSAL. Stage 8.23 (local TA/RH/dewpoint) REJECTED_ON_EVEN.

#### M. Orographic Indicators
**NOT IN Stage 8.1.** Stage 8.24 (barrier-normal wind + Froude) PROVISIONAL_REJECTION_IMPLEMENTATION_QUALIFIED.

#### N. Satellite Routes Already Investigated
- Stage 8.4/8.14B: NASA VIIRS Level-2 → BLOCKED_NON_CAUSAL
- Stage 8.14C: EUMETSAT SEVIRI CMIC → REJECTED (coverage & parallax)
- Stage 8.22: Satellite Cloud Motion (GEO AMV, LEO AMV, LEO Optical Flow, PPS CTH) → CLOSED_FEASIBILITY
- Cloud Evolution (LEO sequences, GEO SEVIRI IR) → CLOSED_FEASIBILITY

#### O. Radiative-Physics Routes Already Investigated
- Vertical aerosol structure → CLOSED_IMMATERIAL (<1.5 W/m²)
- Vertical water vapor profile → CLOSED_REDUNDANT + IMMATERIAL (<1.8 W/m²)
- Total column ozone → CLOSED_IMMATERIAL (<0.75 W/m²)
- Rayleigh scattering → CLOSED_REDUNDANT (100% derivable)
- Minor trace gases → CLOSED_IMMATERIAL (<0.10 W/m²)

---

## 3. CRITICAL INFORMATION GAP IDENTIFICATION

Based on the information map, the following categories of physical information are **NOT PRESENT** in Stage 8.1:

### Absent Information Categories

| Category | Description | Physical Significance | Why Absent |
| :--- | :--- | :--- | :--- |
| **Independent Cloud Observations** | Any cloud measurement from a sensor other than MEPS NWP | HIGH — cloud timing/optical errors dominate residuals | All satellite/ground cloud sources failed causality or feasibility |
| **Cloud Position / Motion / Evolution** | Where clouds are spatially, how they move, how they change | HIGH — MEPS cloud displacement is the error source | Spatial NWP failed (8.5), satellite failed (8.22), evolution failed |
| **Precipitation Observations** | Radar/rain gauge indicating active hydrometeor processes | MEDIUM — precipitation indicates cloud maturity/depth | Never investigated in POLARIS |
| **GNSS Integrated Water Vapor** | Column-integrated atmospheric moisture from GNSS delay | MEDIUM — physically independent moisture observation | Stage 8.19 used synthetic data; real GNSS untested |
| **Analysis / Assimilation Increments** | Model corrections from data assimilation (obs minus background) | MEDIUM — contains information not in forecast itself | Never investigated in POLARIS |
| **Upstream Meteorological Observations** | SYNOP/METAR from stations west of Scandes | LOW-MEDIUM — incoming weather precursors | Never investigated in POLARIS |
| **Microwave Remote Sensing** | Passive microwave LWP/IWV from satellite | MEDIUM — senses cloud differently than IR/visible | Never investigated in POLARIS |
| **Cloud Radar / Lidar Profiling** | Vertical cloud structure from active sensors | HIGH but likely INFEASIBLE — proximity required | Never investigated in POLARIS |

### Most Critical Finding

**Every single piece of cloud information in Stage 8.1 comes from the same MEPS NWP system.** There is zero observational diversity in cloud representation. The model's cloud errors are entirely determined by how well MEPS forecasts cloud state at Nuolja, and Stage 8.1 has no independent check on this.

---

## 4. Model Predictions in Feature Set (4 features)
| Feature | Physical Information | Spatial Scale | Temporal Scale | Observed/Modeled | Position/Motion/Evolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pred_stage3b_cloud_nwp` | Stage 3b cloud-NWP prediction | Point | Per-hour | Modeled (prior stage) | No |
| `phys_pred_fold` | Physics-based prediction | Point | Per-hour | Modeled (prior stage) | No |
| `pred_stage4_fold` | Stage 4 ensemble prediction | Point | Per-hour | Modeled (prior stage) | No |
| `disagreement_fold` | |Stage3b - Physics| disagreement | Point | Per-hour | Derived | No |

---

## 5. Temporal Indices (3 features)
| Feature | Physical Information |
| :--- | :--- |
| `horizon_hour` | Forecast lead time (H1–H24) |
| `month` | Calendar month (seasonal regime) |
| `hour` | Hour of day (diurnal cycle) |

---

*Report generated under POLARIS Stage 8 Governance Guidelines on 2026-09-13.*
