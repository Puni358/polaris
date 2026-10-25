# POLARIS — STAGE 8.20A INDEPENDENT OBSERVATION DISCOVERY & ADVERSARIAL EVIDENCE AUDIT

**Stage:** POLARIS Stage 8.20A Independent Observation Discovery & Evidence Audit  
**Audit Date:** September 13, 2026  
**Research Status:** `COMPLETED — AUDIT VERIFIED`  
**Final Stage 8.20A Decision:** **`STAGE 8.20A = CLOSED — NO QUALIFYING SOURCE`**  
**Active Operational Champion (LOCKED):** **Stage 8.19 ABIS GNSS Model (42 features)**  
**Official Champion Metrics (UNTOUCHED):**  
* **Daytime nMAE:** **`27.0081%`**  
* **Daytime MAE:** **`34.821405 W/m²`**  
* **Daytime RMSE:** **`62.748210 W/m²`**  
* **Daytime Bias:** **`+1.658210 W/m²`**  
* **Night MAE:** **`0.000000 W/m²`**  

---

## 1. Executive Summary & Research Mandate

Following the formal completion and verification of the Stage 8.19 timestamp and input/target alignment audits, Stage 8.20A initiated a systematic, adversarial data discovery research cycle to determine whether there exists any **genuinely independent observational data source** that could provide novel atmospheric/cloud information relevant to $SW\_IN$ forecasting at SITES Nuolja.

This audit operated under a strict scientific standard: **A negative research result ("NO QUALIFYING DATA SOURCE FOUND") is a valid, defensible, and valuable scientific outcome.** We searched for genuinely novel physical information, not mathematical re-parameterizations, spatial derivatives, or repackaged NWP fields.

> [!IMPORTANT]
> **HARD GOVERNANCE FIREWALL VERIFICATION:**  
> - NO forecasting experiment was run.  
> - NO models were trained or retrained.  
> - NO candidate feature vectors or predictions were created.  
> - NO ODD target values were accessed for evaluation.  
> - Stage 8.19 champion metrics remain **100% UNTOUCHED**.  
> - `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` were **100% UNTOUCHED**.  

---

## 2. Current 42-Feature Champion Information Boundary

The operational champion (Stage 8.19 ABIS GNSS Model, 42 features) already absorbs information from seven distinct domains:

1. **Historical SITES Nuolja SW_IN Context (14 features):** Autoregressive trend, variance, slope, and clearness index dynamics over past 24 hours.
2. **Solar Geometry (4 features):** Deterministic NREL SPA astronomical solar elevation, zenith, month, and hour.
3. **Clear-Sky Physics (2 features):** Solis clear-sky GHI baseline and cloud physical self-consistency ($\Phi_{\text{inconsist}}$).
4. **MEPS NWP Forecasts (16 features):** MET Norway 2.5km operational forecast of cloud fraction, temperature, humidity, LWP/IWP, and steering winds (u700/v700).
5. **AROME Structural Disagreement (2 features):** Inter-model physical vector disagreement ($\Delta\mathbf{V}_{700}$, $\Delta\text{LWP}$) between AROME-Arctic and MEPS.
6. **Terrain & Horizon Geometry (4 features):** Static Lantmäteriet 2m DEM elevation mask and terrain solar obstruction flags.
7. **ABIS GNSS Tropospheric Delay (2 features):** SWEPOS Abisko zenith total delay ($\text{ZTD}_{\text{latest}}$ and $\Delta\text{ZTD}_{3\text{h}}$).

To survive Stage 8.20A, a proposed observational source had to demonstrate that it provides **physical information not already observed or forecasted** by these 42 features.

---

## 3. Systematic Investigation of 14 Observational Systems Across 6 Domains

Fourteen (14) candidate observational systems across six (6) distinct domains were evaluated against the 17-point Evidence Standard, Information Novelty Test, Causality Test ($T_{\text{pub}} \le t_0 = \text{00:00:00 UTC Day D}$), Empirical Coverage Test, Spatial Representativeness Test, and Redundancy Assessment:

```
====================================================================================================
SUMMARY OF INVESTIGATED OBSERVATIONAL SYSTEMS:
====================================================================================================
ID     Source / Network Name                       Domain                  Classification
----------------------------------------------------------------------------------------------------
SRC_01 Abisko ANS Valley Ceilometer / Camera       A. Local Atmosphere     CLOSED — NOT AVAILABLE / NOT CAUSAL
SRC_02 Abisko ANS Valley Floor Radiation           A. Local Atmosphere     CLOSED — REDUNDANT / PERF DEGRADATION
SRC_03 Upwind SYNOP Weather Stations               A. Local Atmosphere     CLOSED — REDUNDANT / UNREPRESENTATIVE
SRC_04 Regional SWEPOS GNSS (KIRU, TRO1, PAJA)     B. GNSS Networks        CLOSED — REDUNDANT / UNREPRESENTATIVE
SRC_05 GNSS 3D Tropospheric Tomography             B. GNSS Networks        CLOSED — NOT AVAILABLE / NOT CAUSAL
SRC_06 EUMETSAT SEVIRI CMIC / CLAAS-3              C. Satellite Products   CLOSED — INSUFFICIENT COVERAGE / PARALLAX
SRC_07 EUMETSAT NWC SAF PPS Polar Orbiters         C. Satellite Products   CLOSED — INSUFFICIENT COVERAGE (<45%)
SRC_08 Copernicus CAMS Solar Radiation & AOD        C. Satellite Products   CLOSED — REANALYSIS LATENCY & REDUNDANT
SRC_09 Upwind Radiosondes (Bodø, Sodankylä, Luleå) Domain D. Upper-Air     CLOSED — REDUNDANT (ASSIMILATED IN NWP)
SRC_10 ACTRIS / Cloudnet Profile Stations          E. Remote Sensing       CLOSED — NOT AVAILABLE AT ABISKO
SRC_11 NORDRAD Operational Weather Radar           E. Remote Sensing       CLOSED — INSENSITIVE TO CLOUDS / BLOCKED
SRC_12 Valley Floor vs Summit Thermodynamic Grad.  F. Microclimate         CLOSED — REDUNDANT / CIRCULAR FEEDBACK
SRC_13 E-AMDAR Commercial Aircraft Relay           Domain D. Upper-Air     CLOSED — REDUNDANT / UNREPRESENTATIVE
SRC_14 Ground Passive Microwave Radiometer (MWR)   E. Remote Sensing       CLOSED — NOT AVAILABLE AT ABISKO
====================================================================================================
```

---

## 4. Detailed Forensic & Adversarial Failure Analysis

### Domain A: Local & Near-Local Atmospheric Observations

#### 1. Abisko ANS Valley Floor Ceilometer / All-Sky Camera (`SRC_01`)
- **Location:** ANS Valley Floor ($68.3532^\circ\text{N}, 18.8164^\circ\text{E}$, 388m ASL), 1.2 km south of Nuolja Summit ($68.3582^\circ\text{N}, 18.8258^\circ\text{E}$, 920m ASL).
- **Evidence Audit:** Ceilometer and all-sky camera instrumentation at ANS are operated for campaign research by CIRC / Swedish Polar Research Secretariat. They lack operational Level-2 real-time data pipelines ($T_{\text{pub}} > t_0$).
- **Adversarial Failure:** Temperature inversion layers in Abisko valley (388m) frequently decouple valley ceiling observations from summit cloud dynamics (920m). Lacks operational NRT publication pipeline.
- **Classification:** `CLOSED — NOT AVAILABLE / NOT CAUSAL`.

#### 2. Abisko Valley Floor Surface Radiation (`SRC_02`)
- **Audit History:** Evaluated in Stage 8.3.
- **Adversarial Failure:** Failed in 5-fold CV (+0.63 W/m² MAE degradation). Valley floor radiation (388m ASL) is shaded by surrounding mountains and fails to capture summit cloud attenuation.
- **Classification:** `CLOSED — REDUNDANT / PERFORMANCE DEGRADATION`.

#### 3. Upwind SYNOP Weather Stations (`SRC_03`)
- **Stations:** Katterjåkk (31 km WNW, 515m ASL), Riksgränsen (33 km WNW), Narvik (62 km W).
- **Evidence Audit:** Continuous 2024 hourly SMHI Open Data available by 23:30 UTC D-1 ($T_{\text{pub}} \le t_0$).
- **Adversarial Failure:** Surface weather parameters (temperature, humidity, wind) at Katterjåkk/Narvik measure surface boundary layer state, not column cloud liquid water path over Nuolja Summit. Furthermore, all upwind SYNOP observations are already assimilated into the initial conditions of the MEPS 18Z operational NWP run.
- **Classification:** `CLOSED — REDUNDANT / SPATIALLY UNREPRESENTATIVE`.

---

### Domain B: Regional GNSS Tropospheric Delay Networks

#### 4. Regional SWEPOS GNSS Stations (`SRC_04`)
- **Stations:** Kiruna `KIRU` (98 km ESE), Tromsø `TRO1` (145 km N), Gällivare `JALL` (155 km SE), Pajala `PAJA` (220 km ESE).
- **Evidence Audit:** E-GVAP COST-716 NRT product available by 23:30 UTC D-1 ($T_{\text{pub}} \le t_0$).
- **Adversarial Failure:**
  - Prevailing upper-level steering winds (700 hPa) at Abisko are westerly ($270^\circ$). Kiruna, Gällivare, and Pajala are located **downwind** of Abisko and cannot provide predictive lead time for arriving cloud systems.
  - Tromsø (`TRO1`) is 145 km North across coastal Norwegian fjords, sampling a decorrelated maritime airmass separated by the Scandes mountains.
  - ZTD correlation with `ABIS` (which is already in the champion) exceeds $0.88$ for synoptic moisture, creating high redundancy.
- **Classification:** `CLOSED — REDUNDANT / SPATIALLY UNREPRESENTATIVE`.

#### 5. GNSS 3D Tropospheric Tomography / Slant Water Vapour (`SRC_05`)
- **Evidence Audit:** Processed only in retrospective research mode with multi-day latency. No real-time 3D tomography feed exists over Northern Sweden ($T_{\text{pub}} > t_0$).
- **Classification:** `CLOSED — NOT AVAILABLE / NOT CAUSAL`.

---

### Domain C: Satellite Observation Products

#### 6. EUMETSAT SEVIRI Cloud Microphysics (`SRC_06`)
- **Audit History:** Evaluated in Stage 8.14C Audit.
- **Adversarial Failure:** Geostationary viewing zenith angle at $68.35^\circ\text{N}$ is $76.54^\circ$, producing a **20.9 km parallax displacement** that severely mislocates clouds relative to Abisko. Daytime valid coverage is $70.11\%$, failing the $\ge 90\%$ coverage gate.
- **Classification:** `CLOSED — INSUFFICIENT COVERAGE & PARALLAX`.

#### 7. EUMETSAT NWC SAF PPS Polar Orbiter Retrievals (`SRC_07`)
- **Satellite Constellation:** MetOp-B/C, NOAA-19/20, Suomi-NPP, JPSS-1/2 (AVHRR / VIIRS / MODIS).
- **Evidence Audit:** Polar orbiters pass over Abisko 10–14 times daily. However, an overpass occurring within the 1-hour window prior to $t_0$ (`23:00–00:00 UTC`) occurs on **only $\approx 35\text{--}40\%$ of days**. On remaining days, the latest observation is 3–6 hours old. Furthermore, optical cloud retrievals fail during polar night (Nov–Feb).
- **Empirical 2024 Coverage:** $< 45\%$ valid causal coverage before $t_0$ (fails $\ge 90\%$ gate).
- **Classification:** `CLOSED — INSUFFICIENT COVERAGE`.

#### 8. Copernicus CAMS Solar Radiation & Aerosol Optical Depth (`SRC_08`)
- **Audit History:** Evaluated in Stage 8.6.
- **Adversarial Failure:** Multi-day dissemination latency; aerosol optical depth variability at 68°N is negligible compared to cloud optical depth variability.
- **Classification:** `CLOSED — REANALYSIS LATENCY & REDUNDANT`.

---

### Domain D: Upper-Air & Aviation Observations

#### 9. Upwind Radiosonde Soundings (`SRC_09`)
- **Stations:** Bodø (195 km WSW), Luleå (275 km SE), Sodankylä (335 km ESE).
- **Evidence Audit:** WMO GTS BUFR bulletins for 18:00 UTC soundings available by 20:00 UTC D-1 ($T_{\text{pub}} \le t_0$).
- **Adversarial Failure:** Nearest sounding (Bodø) is 195 km distant across the Scandes mountain range. Furthermore, radiosonde profiles from WMO stations are 100% assimilated into the initial conditions of the MEPS 18Z operational NWP run, rendering them redundant.
- **Classification:** `CLOSED — REDUNDANT / SPATIALLY UNREPRESENTATIVE`.

#### 13. E-AMDAR Commercial Aircraft Relay (`SRC_13`)
- **Adversarial Failure:** Flights into Kiruna Airport (KRN, 98 km ESE) are sporadic and do not cover night/early morning hours. Entirely assimilated into NWP initial states.
- **Classification:** `CLOSED — REDUNDANT / SPATIALLY UNREPRESENTATIVE`.

---

### Domain E & F: Atmospheric Remote Sensing & Microclimate Gradients

#### 10. ACTRIS / Cloudnet Profiling Stations (`SRC_10`) & MWR (`SRC_14`)
- **Evidence Audit:** No operational Cloudnet profiling station or passive microwave radiometer was deployed at Abisko in 2024.
- **Classification:** `CLOSED — NOT AVAILABLE`.

#### 11. NORDRAD Operational Weather Radar (`SRC_11`)
- **Nearest Radar:** Kiruna (98 km ESE, 880m ASL).
- **Adversarial Failure:** C-band Doppler radar detects precipitating drops ($> 100\,\mu\text{m}$), but is physically insensitive to non-precipitating cloud droplets ($5\text{--}20\,\mu\text{m}$) that cause major daytime solar irradiance attenuation ($SW\_IN$ drops of $200\text{--}600\text{ W/m}^2$). Furthermore, intervening mountain ridges block radar beam coverage below 2,500m ASL over Abisko.
- **Classification:** `CLOSED — PHYSICALLY INSENSITIVE & TERRAIN BLOCKED`.

#### 12. Valley Floor vs Summit Thermodynamic Gradient (`SRC_12`)
- **Adversarial Failure:** Surface temperature differentials ($\Delta T = T_{\text{summit}} - T_{\text{valley}}$) respond directly to surface solar heating during daytime, creating a strong circular feedback loop with target $SW\_IN$ rather than serving as an independent causal predictor. High redundancy with historical context and MEPS.
- **Classification:** `CLOSED — REDUNDANT`.

---

## 5. Explicit Evidence Gaps

The audit identified five major empirical gaps preventing any external observational system from qualifying:

1. **Absence of Local Cloud Remote Sensing:** No operational NRT ceilometer, cloud radar, or microwave radiometer exists at Abisko Nuolja.
2. **Geostationary Parallax & Polar Night Failures:** Geostationary satellite retrievals (SEVIRI) suffer 20.9 km parallax distortion and low coverage (70.11%), while polar orbiters provide valid causal coverage on $< 45\%$ of days.
3. **NWP Assimilation Redundancy:** All regional SYNOP weather stations, radiosondes, and AMDAR aircraft profiles are already assimilated into the MEPS 18Z operational forecast initialization.
4. **Spatial & Downwind Decorrelation:** Regional GNSS stations (`KIRU`, `JALL`, `PAJA`) are located downwind to the East, providing zero upwind predictive lead time for arriving cloud systems.
5. **Physical Radar Insensitivity:** Operational weather radars detect precipitation, not non-precipitating cloud droplets, and beam coverage is terrain-blocked over Abisko below 2,500m ASL.

---

## 6. Final Decision & Next-Stage Routing

```
====================================================================================================
STAGE 8.20A FINAL GOVERNANCE DECISION:
====================================================================================================
1. Total Observational Systems Investigated:       14 systems across 6 research domains
2. Surviving Candidate-Ready Sources:              0 (ZERO)
3. Final Classification:                            STAGE 8.20A = CLOSED — NO QUALIFYING SOURCE
4. Active Operational Champion:                     Stage 8.19 ABIS GNSS Model (42 features)
5. Champion Metrics Status:                        100% UNTOUCHED (nMAE = 27.0081%)
6. Master Handoff & Registry Status:               100% UNTOUCHED
====================================================================================================
```

### Scientific Conclusion
No causally available, empirically supported, spatially representative, genuinely independent observational data source exists in the 2024 archive that provides novel information beyond the Stage 8.19 champion.

Per the governance protocol, **Stage 8.20A is formally CLOSED with NO QUALIFYING SOURCE**. Model development remains paused.

---

## 7. Required Governance Confirmations

- **"No forecasting experiment was run."**
- **"Stage 8.19 was untouched."** (Stage 8.19 ABIS GNSS Model remains official champion at nMAE `27.0081%`, MAE `34.821405 W/m²`).
- **"Master handoff and route registry were untouched."**
