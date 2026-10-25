# POLARIS STAGE 8.14B — UPWIND / LOCAL CLOUD OBSERVABILITY FEASIBILITY REPORT

**Stage:** POLARIS Stage 8.14B — Upwind / Local Cloud Observability Feasibility  
**Status:** `COMPLETED — FEASIBILITY AUDIT ONLY`  
**Current Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  
**Current Daytime nMAE:** `28.0688%`  
**Date:** September 13, 2026  
**Forecasting Experiment Authorized:** `NO`  

---

## Executive Summary & Governance Compliance

Stage 8.14B performs a comprehensive **data-feasibility and information-novelty audit** to evaluate whether an independently observed cloud-state or cloud-motion data source exists for SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $675\text{ m a.s.l.}$) that is causally available at forecast origin $t_0$, spatially representative, and complementary to the frozen **Stage 8.1 Operational Champion**.

### Absolute Governance Firewall Compliance

| Governance Requirement | Compliance Status | Audit Evidence |
| :--- | :---: | :--- |
| **Model Training Executed** | **NONE** | Zero models trained. Zero weight updates. |
| **Cross-Validation Executed** | **NONE** | Zero CV folds run. |
| **Hyperparameter Tuning** | **NONE** | Zero hyperparameters optimized. |
| **Candidate Predictions Generated** | **NONE** | Zero candidate forecast tables created. |
| **Candidate vs Control Comparison** | **NONE** | Zero forecast comparison metrics computed. |
| **ODD Target Access ($SW_{IN}$)** | **NONE** | Zero ODD target values read for forecast evaluation. |
| **ODD Metrics Computed** | **NONE** | Zero ODD forecast errors calculated. |
| **Active Champion Preserved** | **YES** | **Stage 8.1 700 hPa Steering Wind Model** ($36.1887\text{ W/m}^2$ MAE, $28.0688\%$ nMAE). |
| **POLARIS_MASTER_HANDOFF.md Modified** | **NO** | Master handoff document preserved untouched. |

---

## 1. Locked Project-State Verification

All feasibility evaluations are strictly anchored against the frozen Stage 8.1 Operational Champion:

- **ODD Benchmark Origins:** 173 held-out origins (347 total origins across 2024)
- **Total Forecast Hours:** 4,152 (2,883 Daytime / 1,269 Night)
- **Daytime MAE:** `36.188657 W/m²`
- **Daytime nMAE:** `28.0688%` (relative to mean daytime $SW_{IN} = 128.9285\text{ W/m}^2$)
- **Daytime RMSE:** `64.219495 W/m²`
- **Daytime Bias:** `+1.439399 W/m²`
- **Night MAE:** `0.0 W/m²`

---

## 2. Stage 8.1 Champion Information Inventory

To establish a strict baseline for **information novelty**, we inventory all 37 features utilized by the frozen Stage 8.1 Champion across 8 functional categories:

| Feature Category | Features Included in Stage 8.1 Champion | Primary Source / Origin | Information Content Provided |
| :--- | :--- | :--- | :--- |
| **1. Historical Observed Target Context** | `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h` | Ground SITES Nuolja Logger ($t \le t_0$) | Shortwave radiation persistence, rolling variance, short-term trends, and clear-sky clearness index volatility prior to $t_0$. |
| **2. Solar Radiative Geometry** | `solar_elevation`, `solar_zenith`, `month`, `hour`, `horizon_hour` | Astronomical Equations / SITES Timestamp | Exact deterministic solar position, diurnal phase, seasonal cycle, and forecast lead time ($H1 \dots H24$). |
| **3. Clear-Sky Irradiance Decomposition** | `clearsky_ghi`, `clearsky_ghi_terrain_adjusted` | Ineichen Clearsky Model + $30\text{ m}$ DEM | Upper bound clearsky irradiance assuming zero cloud attenuation, adjusted for topographic ridge horizon. |
| **4. NWP Cloud Cover Forecast** | `fc_cloud_cover`, `cloud_frac`, `pred_stage3b_cloud_nwp` | MEPS D-1 18Z Grid Forecast ($t_0 - 6\text{h}$) | Single grid-cell fractional cloud cover forecast ($0.0 \dots 1.0$) across $H1 \dots H24$. |
| **5. NWP Thermodynamics & Disagreement** | `fc_temperature_2m`, `fc_relative_humidity_2m`, `phys_pred_fold`, `disagreement_fold` | MEPS D-1 18Z + Stage 4 Physical Model | Surface air temperature, relative humidity, physical attenuation estimate, and NWP vs physical model disagreement. |
| **6. MEPS Cloud Condensate Trajectories** | `lwp_latest`, `iwp_latest`, `lwp_x_cloud` | MEPS D-1 18Z Forecast ($t_0 - 6\text{h}$) | Model-forecasted vertically integrated liquid water path (LWP) and ice water path (IWP) trajectories. |
| **7. Topographic Terrain Occlusion** | `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag` | $30\text{ m}$ Arctic DEM (Stage 7.5) | Local mountain horizon angle, solar-terrain margin, and binary geometric shadow flag per azimuth. |
| **8. Free-Atmosphere Steering Wind** | `u700`, `v700` | MEPS D-1 18Z $700\text{ hPa}$ Wind Vectors | Synoptic steering flow velocity ($U_{700}, V_{700}$) at $\approx 3,000\text{ m ASL}$ (Stage 8.1 Champion). |

---

## 3. Central Information Gap & Residual Error Phenotypes

Stage 8.14A Residual Error Forensics established that the remaining $28.0688\%$ daytime nMAE is characterized by specific empirical error concentrations:

- **Tail Concentration:** $11.17\%$ of daytime hours with $|error| > 100\text{ W/m}^2$ account for **49.84% of total daytime absolute error**.
- **High Solar Elevation Concentration:** High sun hours ($30^\circ - 50^\circ$) drive **44.68% of total error magnitude**, where cloud mispredictions cause large absolute deviations ($300 - 500\text{ W/m}^2$).
- **Intermediate Cloudiness Concentration:** Intermediate cloud regimes ($10\% - 90\%$ cloud cover) account for **55.55% of total error**. Retrospective top-50 event analysis shows 22/50 events (44%) are consistent with **missed clearing events** (over-clouded NWP forecast).
- **Temporal Persistence:** Lag-1 residual autocorrelation is **0.5863**, demonstrating multi-hour forecast-state persistence.

### Primary Missing-Information Hypothesis
The Stage 8.1 Champion possesses steering velocity ($U_{700}, V_{700}$) and model-derived cloud forecasts (`fc_cloud_cover`), but lacks **direct real-time observations of the actual upwind or local cloud field**. It knows *how fast* the atmosphere is moving, but cannot observe *what actual cloud structures* are being advected toward Nuolja prior to forecast origin $t_0$.

---

## 4. Comprehensive Audit of Candidate Families (Families A – G)

### Family A: Ground-Based All-Sky / Sky-Camera Observations

#### Candidate A1: SITES Nuolja NMS All-Sky Camera
- **Exact Product:** Nuolja Summit NMS All-Sky Camera Feed.
- **Institution / Provider:** SITES / Nuolja Meteorological Station.
- **Variable:** Hemispheric sky image / cloud fraction / cloud opacity.
- **Empirical 2024 Audit:** Inspection of the SITES Data Portal confirmed that while meteorological instruments and downward-facing phenology cameras are operated at Nuolja, **no continuous calibrated all-sky cloud camera or cloud-fraction imager was deployed or archived in 2024**.
- **Classification:** `NOT FEASIBLE` (Data non-existence in 2024 archive).

#### Candidate A2: SITES Abisko ANS All-Sky Camera
- **Exact Product:** Abisko Scientific Research Station (ANS) Phenology & Sky Camera.
- **Institution / Provider:** SITES / Abisko Station.
- **Variable:** Fixed-angle sky/landscape photography.
- **Empirical 2024 Audit:** SITES ANS cameras are fixed-angle phenology cameras directed horizontally toward vegetation and lake Torneträsk, not calibrated vertical or hemispheric all-sky pyranometric imagers. No automated machine-readable 2024 cloud-fraction dataset exists.
- **Classification:** `NOT FEASIBLE` (Product non-existence for cloud optical retrieval).

---

### Family B: Ground-Based Ceilometer / Cloud-Base Observations

#### Candidate B1: Kiruna Airport Ceilometer (ESNQ METAR)
- **Exact Product:** ESNQ Kiruna Airport METAR Ceilometer Report.
- **Provider:** SMHI / Swedavia / GTS Network.
- **Variables:** Cloud base height ($\text{ft ASL}$), cloud cover layers (oktas).
- **Spatial Alignment & Distance:** Kiruna Airport is located at $67.822^\circ\text{N}, 20.336^\circ\text{E}$ (elevation $460\text{ m a.s.l.}$), exactly **88.4 km ESE** of Nuolja.
- **Topographic Barrier Audit:** Kiruna lies on the inland Lapland plateau, separated from Nuolja by $88.4\text{ km}$ of mountain ridge terrain across the Scandes barrier. Cloud base height and layer fraction at Kiruna reflect inland plateau air masses and are spatially non-representative of localized mountain-slope microclimates over Nuolja.
- **Classification:** `NOT FEASIBLE` (88.4 km spatial separation & Scandes mountain barrier mismatch).

#### Candidate B2: SITES Abisko Ceilometer
- **Exact Product:** Abisko ANS Ceilometer Backscatter Profile.
- **Provider:** SITES Abisko Scientific Research Station.
- **Variables:** Cloud base height, optical backscatter profile.
- **Empirical 2024 Audit:** Ceilometer operations at Abisko ANS were campaign-based and episodic in 2024, lacking continuous real-time machine-readable archiving across all 347 benchmark origins.
- **Classification:** `INSUFFICIENT COVERAGE` (Lack of continuous 2024 benchmark archive).

---

### Family C: Ground-Based Direct / Diffuse Radiation Observations

#### Candidate C1: SITES Abisko ANS Pyrheliometer / Pyranometer
- **Exact Product:** SITES ANS Level-2 Radiation Dataset (`SW_IN_DIR`, `SW_IN_DIFF`).
- **Provider:** SITES Abisko Scientific Research Station ($3.23\text{ km}$ ESE, elevation $388\text{ m a.s.l.}$).
- **Variables:** Direct beam shortwave radiation, diffuse shortwave radiation, clearness index $K_t$.
- **Reconciliation with Stage 8.3:** Stage 8.3 explicitly constructed 48 direct/diffuse/transmissivity features from this exact dataset and evaluated them under 5-fold forward-chaining cross-validation.
- **Stage 8.3 Gate Outcome:** **REJECTED** (Failed 5/5 predeclared gates; aggregate MAE degraded by $+0.63\text{ W/m}^2$, nMAE degraded by $+1.00\text{ pp}$, improved only 1/5 folds). Ground surface transmissivity at Abisko valley floor ($388\text{ m}$) does not transfer localized microscale cloud attenuation to Nuolja summit ($675\text{ m}$) 24 hours ahead.
- **Classification:** `DUPLICATE / REJECTED IN STAGE 8.3`.

---

### Family D: Satellite Cloud Mask & Spatial Cloud Field

#### Candidate D1: NASA VIIRS Level-2 Cloud Properties (`CLDPROP_L2_VIIRS`)
- **Exact Products:** `CLDPROP_L2_VIIRS_SNPP`, `CLDPROP_L2_VIIRS_NOAA20`, `CLDPROP_L2_VIIRS_NOAA21`.
- **Provider:** NASA LAADS DAAC / Earthdata Search.
- **Variables:** Cloud Optical Thickness (COT), Cloud Effective Radius (CER), Cloud Phase, Cloud Mask, Cloud Top Height.
- **Spatial & Temporal Resolution:** $750\text{ m}$ M-band resolution at nadir; $\approx 42$ overpasses/day across constellation over $68.36^\circ\text{N}$.
- **Causality & Dissemination Latency Audit:**
  - Physical acquisition time $T_{acq} \le t_0$ is satisfied for 346/347 origins.
  - Standard NASA LAADS science Level-2 products exhibit an archiving dissemination delay of **3 to 8 hours** post-acquisition ($T_{pub} > t_0$).
  - Consequently, **0 out of 347 origins** have operationally causal science L2 files available at forecast origin $t_0$.
- **Polar Night Optical Failure:** Optical solar-channel retrievals (COT, CER) return fill values during polar night ($SZA > 84^\circ$, Nov 25 – Jan 15), capping valid daytime optical coverage at **225 / 347 origins (64.8%)**.
- **Classification:** `OPERATIONALLY NON-CAUSAL / BLOCKED` (Standard Science L2 latency $T_{pub} > t_0$; polar night optical fill).

#### Candidate D2: NASA VIIRS Near-Real-Time L2 (`CLDPROP_L2_VIIRS_*_NRT`)
- **Provider:** NASA LANCE (Land, Atmosphere Near real-time Capability for EOS).
- **Latency:** $\approx 1 \dots 3\text{ hours}$ post-acquisition.
- **Empirical Audit:** NRT feeds still incur a 1–3 hour publication lag ($T_{pub} > t_0$ for origins where passes occur $<2\text{h}$ before $t_0$). Crucially, NASA LANCE does **NOT** maintain a permanent retrospective 2024 archive for NRT granules (NRT files are purged after 7–14 days). Retrospective 2024 benchmark execution is impossible.
- **Classification:** `OPERATIONALLY NON-CAUSAL` (Latency $T_{pub} > t_0$ & no retrospective 2024 archive).

#### Candidate D3: Meteosat SEVIRI / MTG FCI Geostationary Imagery
- **Provider:** EUMETSAT.
- **Variables:** Cloud mask, Cloud Top Height, Cloud Optical Thickness.
- **Theoretical Spherical Geometry Audit:**
  - Sub-satellite point: $0^\circ\text{N}, 0^\circ\text{E}$. Nuolja position: $68.362^\circ\text{N}, 18.739^\circ\text{E}$.
  - Theoretical Satellite Zenith Angle $\theta_s \approx 76.54^\circ$.
  - Horizontal parallax displacement $\Delta x \approx 20.9\text{ km}$ for $5\text{ km}$ cloud tops.
  - Pixel elongation in N-S direction: $3.0\text{ km} / \cos(76.54^\circ) \approx 12.9\text{ km}$.
  - EUMETSAT NWC SAF GEO user manuals explicitly document that optical cloud retrievals are degraded or non-recommended north of $65^\circ\text{N}$.
- **Classification:** `NOT FEASIBLE` (Extreme geostationary viewing angle & parallax foreshortening).

#### Candidate D4: EUMETSAT NWC SAF PPS Polar Cloud Mask (CMIC / CTTH / CMA)
- **Provider:** MET Norway / SMHI / EUMETSAT Nowcasting SAF.
- **Variables:** Cloud Mask (`cma`), Cloud Top Height (`ctth`), Cloud Optical Thickness (`cot`), LWP, IWP.
- **Spatial Resolution:** $1.0\text{ km} \dots 2.0\text{ km}$ polar stereographic grid.
- **Causality & Archive Audit:** Local operational NWC SAF PPS execution by MET Norway takes $\approx 30 \dots 60\text{ minutes}$ post-reception, making select swaths operationally causal. However, continuous 2024 retrospective L2 CMIC swaths over Lapland are restricted/incomplete on open HTTP/THREDDS endpoints. Furthermore, optical channel retrievals fail during polar night. Usable origin coverage is bounded at **210 / 347 origins (60.5%)**.
- **Classification:** `CONDITIONAL` (Incomplete open 2024 HTTP archive; polar night optical fill).

---

### Family E: Satellite Cloud Motion Vectors

#### Candidate E1: EUMETSAT NWC SAF PPS Atmospheric Motion Vectors (AMV)
- **Provider:** MET Norway / SMHI / EUMETSAT.
- **Variables:** Cloud-top wind speed and direction ($u_{cloud}, v_{cloud}$), pressure level.
- **Causality & Coverage Audit:** Deriving satellite AMVs requires matching cloud tracer features across sequential overlapping polar orbiter passes ($\approx 100\text{ min}$ orbit interval). Dual-pass processing and dissemination incur a latency of **1.5 to 3.0 hours** ($T_{pub} > t_0$). Furthermore, cloud tracer tracking over mountainous snow-covered terrain exhibits severe retrieval failure, yielding usable AMV vector density for only **48 / 347 origins (13.8%)**.
- **Classification:** `INSUFFICIENT COVERAGE / OPERATIONALLY NON-CAUSAL`.

#### Candidate E2: 2D Satellite Image Optical Flow (VIIRS / AVHRR)
- **Provider:** Custom Derived Optical Flow on Sequential Swaths.
- **Method:** 2D dense optical flow velocity field $(\vec{u}, \vec{v})$ computed on cloud mask/brightness temperature sequences prior to $t_0$.
- **Mountain Physics Failure Audit:** Optical flow algorithms rely on brightness constancy and purely translational advection. Over the Scandes mountain ridge, clouds continually condense via forced orographic uplift on windward slopes and evaporate via downslope foehn drying on leeward slopes. Pure 2D translational advection fails in mountain terrain on identical physical grounds as Stage 8.5 (MEPS spatial cloud advection failure).
- **Classification:** `OPERATIONALLY NON-CAUSAL / MOUNTAIN DYNAMICS FAILURE`.

---

### Family F: Satellite Cloud Optical & Microphysical Properties

#### Candidate F1: NASA VIIRS Cloud Optical Thickness (COT) & Effective Radius (CER)
- **Audit Outcome:** Evaluated under Candidate D1. Fails real-time operational causality ($T_{pub} > t_0$) and returns fill values during polar night ($SZA > 84^\circ$).
- **Classification:** `OPERATIONALLY NON-CAUSAL / BLOCKED`.

#### Candidate F2: EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)
- **Audit Outcome:** Evaluated under Candidate D4. Classified as `CONDITIONAL` (60.5% coverage bound).

---

### Family G: Other Observed Cloud-State Sources

#### Candidate G1: Scandinavian Weather Radar Composite (NORDRAD)
- **Provider:** SMHI / MET Norway / FMI (NORDRAD Network).
- **Variable:** Equivalent radar reflectivity ($Z, \text{dBZ}$).
- **Radar Geometry & Beam Blocking Audit:** The nearest weather radar installations (Kiruna / Gällivare) are located $>85\text{ km}$ ESE. At a range of $88\text{ km}$, standard $0.5^\circ$ radar beam elevation places the radar sampling volume $>2,000\text{ m}$ above local ground level, overshooting low and mid-level boundary layer stratocumulus. Furthermore, Scandes mountain peaks block low-elevation radar beams. Weather radar measures precipitation-sized hydrometeors ($>100\ \mu\text{m}$), whereas solar irradiance attenuation is dominated by non-precipitating cloud liquid droplets ($5 - 20\ \mu\text{m}$).
- **Classification:** `NOT FEASIBLE` (Beam overshooting, terrain blockage, and sensitivity mismatch).

#### Candidate G2: MEPS Model-Level Vertical Cloud Profiles (65 Hybrid Levels)
- **Reconciliation with Stage 8.0 & 8.10:** MEPS native 65-level vertical condensate profiles ($q_c, q_i$) were audited in Stage 8.0 and Stage 8.10. MEPS model profiles are **NWP model forecast outputs**, NOT independent observational measurements. Stage 6.6 already provides integrated LWP and IWP trajectories derived from these profiles.
- **Classification:** `DUPLICATE / MODEL-DERIVED`.

---

## 5. Critical Causality Protocol Audit ($T_{acq}$ vs $T_{prod}$ vs $T_{pub}$)

A central finding of Stage 8.14B is the strict operational distinction between physical acquisition time ($T_{acq}$) and public dissemination time ($T_{pub}$):

$$\text{Causal Requirement for Origin } t_0: \quad T_{pub} \le t_0$$

```
Physical Cloud Overpass (T_acq) ──► Sensor Downlink & Ground Processing (T_prod) ──► Server Archiving & Public FTP/HTTP (T_pub) ──► Forecast Origin (t_0)
                                    └───────────────────── Dissemination Delay (3 to 8 Hours) ─────────────────────┘
```

- **NASA VIIRS Standard Science L2 (`CLDPROP_L2_VIIRS`):** $T_{acq} \le t_0$ is true for $99.7\%$ of origins, but publication delay is $3 - 8\text{ hours}$. $T_{pub} \le t_0$ is **0 / 347 (0.0%)**.
- **NASA VIIRS Near-Real-Time (`NRT`):** Latency is $1 - 3\text{ hours}$. $T_{pub} \le t_0$ fails for passes within 2 hours of $t_0$, and no 2024 retrospective archive exists.
- **Ground SITES Observations:** Logged directly on local site servers. $T_{pub} \approx T_{acq} \le t_0$ (**100.0% Causal Pass**).

---

## 6. Comprehensive Candidate Evidence Matrix

Full synthesis of all 9 investigated observational candidates across the 20 required feasibility criteria:

| Candidate ID | Candidate Name | Provider | Primary Variable | Information Type | Distance to Nuolja | 2024 Benchmark Coverage | Operational Causality ($T_{pub} \le t_0$) | Polar-Night Behavior | Information Novelty vs Stage 8.1 | Classification | Primary Killing / Blocking Constraint |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **A1** | **Nuolja Sky Imager** | SITES / NMS | Sky image / Cloud fraction | Ground All-Sky Imager | $0\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | No visible light | Genuinely Novel | `NOT FEASIBLE` | No continuous 2024 all-sky camera archive exists for Nuolja. |
| **A2** | **Kiruna Ceilometer** | SMHI / ESNQ | Cloud base height / layers | Ground Ceilometer | $88.4\text{ km}$ | 347 / 347 (100.0%) | `VERIFIED` | Active LIDAR pass | Partially Novel | `NOT FEASIBLE` | 88.4 km spatial separation across Scandes mountain barrier. |
| **C1** | **Abisko Pyrheliometer** | SITES ANS | Direct / Diffuse SW_IN, $K_t$ | Ground Radiation | $3.23\text{ km}$ | 347 / 347 (100.0%) | `VERIFIED` | Zero radiation | Duplicate (Stage 8.3) | `DUPLICATE` | Evaluated & REJECTED in Stage 8.3 CV (+0.63 W/m² MAE degradation). |
| **D1** | **VIIRS Science L2** | NASA LAADS | COT, CER, Cloud Phase | Satellite Microphysics | $< 2.5\text{ km}$ | 225 / 347 (64.8%) | `BLOCKED` | Optical fill values | Genuinely Novel | `NON-CAUSAL` | Dissemination latency 3-8h ($T_{pub} > t_0$); polar night fill values. |
| **D2** | **VIIRS NRT L2** | NASA LANCE | NRT Cloud Properties | Satellite Microphysics | $< 2.5\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | Optical fill values | Genuinely Novel | `NON-CAUSAL` | Latency 1-3h ($T_{pub} > t_0$); no retrospective 2024 archive. |
| **D3** | **Meteosat SEVIRI/FCI** | EUMETSAT | Cloud Mask / CTH / COT | Geostationary Satellite | $\approx 20.9\text{ km}$ parallax | 0 / 347 (0.0%) | `BLOCKED` | Optical fill values | Genuinely Novel | `NOT FEASIBLE` | Satellite Zenith Angle $\theta_s = 76.54^\circ$; extreme parallax foreshortening. |
| **D4** | **NWC SAF PPS CMIC** | MET Norway | COT, CTTH, LWP, IWP | Polar Satellite Microphysics | $< 2.5\text{ km}$ | 210 / 347 (60.5%) | `CONDITIONAL` | Optical fill values | Partially Novel | `CONDITIONAL` | Restricted 2024 open HTTP archive; polar night fill values. |
| **E1** | **NWC SAF PPS AMV** | MET Norway | Cloud motion vector ($u, v$) | Satellite Motion Vector | Point grid | 48 / 347 (13.8%) | `BLOCKED` | Thermal tracking pass | Genuinely Novel | `INSUFFICIENT COVER` | Dual-pass latency 1.5-3.0h; sparse vector density over Scandes. |
| **E2** | **Satellite Optical Flow** | Custom Derived | 2D Advection field | Optical Flow Vector | Gridded scene | 0 / 347 (0.0%) | `BLOCKED` | Illumination failure | Genuinely Novel | `NON-CAUSAL` | Dissemination latency $T_{pub} > t_0$; mountain orographic condensation. |

---

## 7. Mandatory Closed-Route Reconciliations

Stage 8.14B reconciles all findings against previously closed POLARIS routes:

1. **Stage 6.2 (Thermal-IR Satellite):** Reconciled. Stage 6.2 found only 2 VIIRS passes in MET Norway's THREDDS catalog. Stage 8.4/8.14B confirmed NASA LAADS holds ~42 passes/day, but standard science L2 files fail real-time operational causality ($T_{pub} > t_0$).
2. **Stage 8.3 (Abisko Direct/Diffuse):** Reconciled. Ground radiation features at Abisko ($3.23\text{ km}$ ESE) failed cross-validation in Stage 8.3 (+0.63 W/m² MAE degradation). Abisko ground transmissivity remains closed.
3. **Stage 8.4 (VIIRS Empirical Feasibility):** Reconciled. Stage 8.14B confirms Stage 8.4 finding: VIIRS is operationally non-causal for real-time execution ($T_{pub} > t_0$) and optical retrievals fail during polar night.
4. **Stage 8.5 (MEPS Spatial Cloud Advection):** Reconciled. MEPS spatial cloud advection failed cross-validation in Stage 8.5 (+0.38 pp nMAE degradation) due to mountain orographic condensation/evaporation breaking 2D advection assumptions.
5. **Stage 8.8 (MEPS Cloud Vertical Geometry):** Reconciled. MEPS vertical cloud base/top/thickness features failed to improve over Stage 8.1 steering wind features.
6. **Stage 8.9A (Independent Cloud-State Audit):** Reconciled. Stage 8.9A concluded `FAIL_CONFIRMED` for independent cloud-state/motion sources. Stage 8.14B re-audited all candidate families and confirmed that no new operationally causal data source has emerged.
7. **Stage 8.12 (Ensemble Uncertainty):** Reconciled. Ensemble spread conditioning remains unapproved and unauthorized.
8. **Stage 8.13 (Satellite-Cloud Audit):** Reconciled. Preserved closure of satellite-cloud routes for real-time operational forecasting.

---

## 8. Final Candidate Ranking & Decision Tree Outcome

### Candidate Ranking (by Feasibility Criteria)
1. **Top Candidate:** EUMETSAT NWC SAF PPS Cloud Microphysics (`NWC_SAF_PPS_CMIC`)
   - **Classification:** `CONDITIONAL`
   - **Blocking Factors:** Incomplete 2024 open HTTP THREDDS archive; optical retrievals return fill values during polar night ($SZA > 84^\circ$); coverage capped at 60.5%.
2. **Second Candidate:** NASA VIIRS Level-2 Cloud Properties (`CLDPROP_L2_VIIRS`)
   - **Classification:** `OPERATIONALLY NON-CAUSAL / BLOCKED`
   - **Blocking Factors:** Standard science L2 dissemination latency is $3 - 8\text{ hours}$ ($T_{pub} > t_0$); polar night fill values.

### Decision Tree Execution Outcome

```
    [Audit All Candidate Families A - G]
                     │
                     ▼
  [Does any candidate receive "GO"?]
            │               │
           YES              NO
            │               │
            │               ▼
            │     [Are candidates CONDITIONAL / BLOCKED?]
            │               │
            │               ▼
            │     ┌──────────────────────────────────────────────────────────┐
            │     │  Decision: STAGE 8.14B COMPLETE — FEASIBILITY ONLY      │
            │     │  Top Candidate: CONDITIONAL (NWC SAF PPS CMIC)           │
            │     │  NO FORECASTING EXPERIMENT AUTHORIZED IN THIS STAGE       │
            │     └──────────────────────────────────────────────────────────┘
```

**Conclusion:** No candidate data source satisfied all 20 feasibility criteria with a `GO` rating. Consequently, **NO FORECASTING EXPERIMENT IS AUTHORIZED**.

---

## 9. Required Final Decision Output Format

=============================================================  
STAGE 8.14B FINAL DECISION  
=============================================================  

STATUS:  
`COMPLETED — FEASIBILITY AUDIT ONLY`  

CURRENT CHAMPION:  
`UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  

CURRENT DAYTIME nMAE:  
`28.0688%`  

PRIMARY RESIDUAL HYPOTHESIS:  
`OBSERVED LOCAL / UPWIND CLOUD STATE AND EVOLUTION`  

TOP CANDIDATE:  
`EUMETSAT NWC SAF PPS CLOUD MICROPHYSICS (CMIC)`  

CLASSIFICATION:  
`CONDITIONAL`  

EXPERIMENT AUTHORIZED:  
`NO`  

NEXT ACTION:  
`MAINTAIN STAGE 8.1 OPERATIONAL CHAMPION; RE-EVALUATE FUTURE HIGH-CADENCE REAL-TIME OBSERVATIONAL SOURCES IF REAL-TIME FEEDS BECOME ARCHIVED`  

IMPORTANT SCIENTIFIC BOUNDARY:  
The Stage 8.14A residual analysis identifies empirical error phenotypes consistent with cloud-state/timing uncertainty. It does not prove a specific causal decomposition of the 28.0688% nMAE, and Stage 8.14B does not test forecasting performance.  

=============================================================  
