# POLARIS STAGE 8.15A — LOCAL / UPWIND CLOUD OBSERVATION FEASIBILITY AUDIT

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.15A — LOCAL/UPWIND CLOUD OBSERVATION FEASIBILITY AUDIT  
**Status**: COMPLETED — FEASIBILITY AUDIT ONLY  
**Current Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%)  
**Strongest Candidate Evaluated**: EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC) — `CONDITIONAL`  
**Stage 8.15B Authorization**: **NOT AUTHORIZED**  
**Final Scientific Conclusion**: **Stage 8.15B NOT JUSTIFIED.**  

---

## 1. Executive Summary & Absolute Governance Firewall Compliance

Stage 8.15A performs an exhaustive feasibility and information-novelty audit to determine whether **any genuinely local or upwind observational source** exists that can provide causally available, spatially representative, and unmodelled cloud-state/cloud-evolution information for the locked 2024 SITES Nuolja solar-irradiance forecasting benchmark.

### Strict Governance Compliance Audit
- **Model Modifications**: **NONE (0)**. Zero weights updated.
- **Dataset / Pipeline Modifications**: **NONE (0)**. Benchmark split preserved.
- **ODD Target Access ($SW_{IN}$)**: **NONE (0)**. Zero ODD target values read for forecast evaluation.
- **ODD Forecast Predictions / Metrics**: **NONE (0)**. Zero candidate prediction tables generated.
- **Hyperparameter Tuning**: **NONE (0)**.
- **Production Model Features**: **NONE (0)**.
- **Stage 8.15B Execution**: **NOT AUTHORIZED (0)**.
- **Active Operational Champion**: **Stage 8.1 700 hPa Steering Wind Model** (Frozen; Daytime MAE = $36.1887\text{ W/m}^2$, Daytime nMAE = $28.0688\%$, Daytime RMSE = $64.2195\text{ W/m}^2$).
- **`POLARIS_MASTER_HANDOFF.md`**: **UNTOUCHED**.

---

## 2. Reconciliation of Previously Closed Stage 8.x Routes

To prevent re-auditing already-closed scientific routes, Stage 8.15A reconciles all findings against prior Stage 8 feasibility audits:

1. **Stage 8.0 / 8.10 (MEPS Model-Level Vertical Profiles)**: `CLOSED / REJECTED`. MEPS 65-level vertical profiles ($q_c, q_i$) are NWP forecast model outputs, not independent observational measurements. Integrated LWP/IWP trajectories are already in Stage 8.1.
2. **Stage 8.3 (Abisko Ground Radiation)**: `CLOSED / REJECTED`. Direct/diffuse radiation features from Abisko ANS ($3.23\text{ km}$ ESE, $388\text{ m}$ ASL) failed 5-fold cross-validation (+0.63 W/m² MAE degradation). Ground transmissivity at valley floor level does not transfer microscale summit cloud attenuation 24 hours ahead.
3. **Stage 8.4 / 8.14B (NASA VIIRS Science Level-2)**: `CLOSED / BLOCKED`. Standard science L2 products (`CLDPROP_L2_VIIRS`) exhibit 3–8 hour dissemination latency ($T_{pub} > t_0$ for 100% of origins). Polar night illumination ($SZA > 84^\circ$) produces fill values (`-9999`).
4. **Stage 8.5 (MEPS Spatial Cloud Advection)**: `CLOSED / REJECTED`. Spatial advection of NWP cloud fields failed cross-validation (+0.38 pp nMAE degradation) because mountain orographic uplift/evaporation breaks 2D translational advection assumptions over Scandes terrain.
5. **Stage 8.6 (CAMS Solar Radiation)**: `CLOSED / REJECTED`. CAMS products are model/reanalysis-derived with multi-day dissemination latency.
6. **Stage 8.8 (MEPS Vertical Cloud Geometry)**: `CLOSED / REJECTED`. NWP cloud base/top/thickness features proved redundant with Stage 8.1 steering wind features.
7. **Stage 8.9A (Independent Cloud-State Audit)**: `CLOSED / REJECTED`. Concluded `FAIL_CONFIRMED` for independent cloud-state/motion sources.
8. **Stage 8.12 (Ensemble Uncertainty)**: `CLOSED / UNAPPROVED`. Ensemble spread conditioning remains unapproved.
9. **Stage 8.13 (Satellite-Cloud Real-Time Audit)**: `CLOSED / REJECTED`. Real-time satellite execution rejected due to dissemination latency and polar night optical blackout.
10. **Stage 8.14C Phase 1 & 2 (EUMETSAT NWC SAF PPS CMIC)**: `CLOSED / CONDITIONAL`. Public HTTP open catalog daylight optical coverage is 70.11% (failing the $\ge 90\%$ gate); 27 swaths lack verified publication timestamps; EUMETSAT Data Store live REST browse query returned HTTP 404 / collection absent from 188 live collections.
11. **Stage 8.14C Live Access Audit (EUMETSAT Optimal Cloud Analysis CDR `EO:EUM:DAT:0617`)**: `CLOSED / TEMPORAL CUTOFF`. Live REST metadata verified: Record covers 2004-01-19 through 2019-08-31. CLOSED for 2024 benchmark.

---

## 3. Detailed Audit of Candidate Observational Source Families (15 Criteria)

### Candidate Family A: Local / All-Sky Observations

#### Candidate A1: SITES Nuolja Summit All-Sky Camera (Nuolja Summit, 675 m ASL)
1. **Exact Product**: Nuolja Summit NMS All-Sky Camera Feed.
2. **Exact Variables**: Hemispheric sky image / cloud fraction / cloud optical opacity.
3. **2024 Coverage**: **0 / 347 origins (0.0%)**. No continuous calibrated all-sky optical imager or machine-readable cloud dataset was deployed or archived on Nuolja summit in 2024.
4. **Temporal Resolution**: N/A.
5. **Spatial Location**: $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$ (Nuolja Summit).
6. **Distance from Nuolja**: $0.0\text{ km}$.
7. **Terrain Separation**: $0.0\text{ m}$.
8. **Observation Type**: Direct local physical sky observation.
9. **Information Novelty**: Genuinely novel relative to Stage 8.1.
10. **Acquisition Timestamp ($T_{acq}$)**: N/A.
11. **Publication Timestamp ($T_{pub}$)**: N/A.
12. **Causal Availability ($T_{pub} \le t_0$)**: `BLOCKED`.
13. **Empirical Benchmark Coverage**: 0 / 347 origins.
14. **H1-H24 Support**: Cannot support due to non-existence.
15. **Limitations**: Data non-existence in 2024 archive; optical blackout during polar night ($SZA > 84^\circ$).
- **Classification**: `REJECTED — DATA NON-EXISTENCE`.

#### Candidate A2: SITES Abisko ANS Sky Camera (Abisko ANS, 388 m ASL)
1. **Exact Product**: Abisko Scientific Research Station Phenology & Sky Camera.
2. **Exact Variables**: Fixed-angle landscape/sky photography.
3. **2024 Coverage**: Uncalibrated RGB photographs archived for phenology.
4. **Temporal Resolution**: Hourly.
5. **Spatial Location**: $68.3533^\circ\text{N}, 18.8164^\circ\text{E}$.
6. **Distance from Nuolja**: $3.23\text{ km}$ ESE.
7. **Terrain Separation**: $287\text{ m}$ elevation difference (Valley floor vs. Summit).
8. **Observation Type**: Direct physical photograph.
9. **Information Novelty**: Partially novel.
10. **Acquisition Timestamp ($T_{acq}$)**: $t \le t_0$.
11. **Publication Timestamp ($T_{pub}$)**: Batch archived post-campaign.
12. **Causal Availability ($T_{pub} \le t_0$)**: `UNVERIFIED`.
13. **Empirical Benchmark Coverage**: 0 / 347 machine-readable cloud records.
14. **H1-H24 Support**: No quantitative optical thickness or cloud fraction stream.
15. **Limitations**: Fixed-angle camera pointing horizontally toward vegetation/lake Torneträsk; non-calibrated for vertical/hemispheric cloud optical thickness.
- **Classification**: `REJECTED — PRODUCT MISMATCH`.

#### Candidate A3: SITES Nuolja Surface Logger Context Features (Nuolja Summit, 675 m ASL)
1. **Exact Product**: SITES Nuolja Meteorological Station Logger Stream ($t \le t_0$).
2. **Exact Variables**: $SW_{IN}$ persistence, rolling variance, short-term trends, clearness index $K_t$ volatility.
3. **2024 Coverage**: 347 / 347 origins (100.0%).
4. **Temporal Resolution**: 1-minute logged; 1-hour aggregated.
5. **Spatial Location**: $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$.
6. **Distance from Nuolja**: $0.0\text{ km}$.
7. **Terrain Separation**: $0.0\text{ m}$.
8. **Observation Type**: Direct local radiometer measurement.
9. **Information Novelty**: **NOT NOVEL**.
10. **Acquisition Timestamp ($T_{acq}$)**: $T_{acq} \le t_0$.
11. **Publication Timestamp ($T_{pub}$)**: $T_{pub} \le t_0$.
12. **Causal Availability ($T_{pub} \le t_0$)**: `VERIFIED` (100.0%).
13. **Empirical Benchmark Coverage**: 347 / 347 origins (100.0%).
14. **H1-H24 Support**: Fully integrated into Stage 8.1.
15. **Limitations**: Provides zero information about future cloud advection beyond persistence/variance.
- **Classification**: `NOT NOVEL — ALREADY IN STAGE 8.1`.

---

### Candidate Family B: Ceilometer / Cloud-Base Observations

#### Candidate B1: Nuolja Summit Ceilometer
1. **Exact Product**: Nuolja Summit Laser Ceilometer Cloud-Base Profile.
2. **2024 Coverage**: **0 / 347 origins (0.0%)**. No ceilometer was installed or operated on Nuolja summit in 2024.
- **Classification**: `REJECTED — NON-EXISTENT`.

#### Candidate B2: SITES Abisko ANS Ceilometer (Abisko ANS, 388 m ASL)
1. **Exact Product**: Abisko ANS Atmospheric Ceilometer Backscatter Profile.
2. **Exact Variables**: Cloud base height ($\text{m ASL}$), LIDAR backscatter profile.
3. **2024 Coverage**: Episodic campaign measurements; missing continuous 2024 archive across benchmark origins.
4. **Temporal Resolution**: Irregular.
5. **Spatial Location**: $68.3533^\circ\text{N}, 18.8164^\circ\text{E}$.
6. **Distance from Nuolja**: $3.23\text{ km}$ ESE.
7. **Terrain Separation**: $287\text{ m}$ elevation difference.
8. **Observation Type**: Active optical LIDAR profile.
9. **Information Novelty**: Genuinely novel.
10. **Acquisition Timestamp ($T_{acq}$)**: $T_{acq} \le t_0$.
11. **Publication Timestamp ($T_{pub}$)**: $T_{pub} > t_0$ (campaign batch export).
12. **Causal Availability ($T_{pub} \le t_0$)**: `UNVERIFIED`.
13. **Empirical Benchmark Coverage**: $<15\%$ of origins covered.
14. **H1-H24 Support**: Cannot support due to incomplete archive.
15. **Limitations**: Discontinuous 2024 operation; valley floor position ($388\text{ m}$) undercounts summit slope clouds ($675\text{ m}$).
- **Classification**: `REJECTED — INSUFFICIENT COVERAGE`.

#### Candidate B3: Kiruna Airport Ceilometer (ESNQ METAR)
1. **Exact Product**: ESNQ Kiruna Airport Automated METAR Ceilometer Feed.
2. **Exact Variables**: Cloud base height ($\text{ft ASL}$), layer cloud fraction (Oktas).
3. **2024 Coverage**: 347 / 347 origins (100.0%).
4. **Temporal Resolution**: 30 minutes / 1 hour.
5. **Spatial Location**: $67.822^\circ\text{N}, 20.336^\circ\text{E}$ (Kiruna Airport).
6. **Distance from Nuolja**: **$88.4\text{ km}$ ESE**.
7. **Terrain Separation**: Inland Lapland plateau ($460\text{ m}$ ASL) separated from Nuolja ($675\text{ m}$ ASL) by $88.4\text{ km}$ of Scandes mountain barrier terrain.
8. **Observation Type**: Direct local LIDAR at Kiruna.
9. **Information Novelty**: Partially novel.
10. **Acquisition Timestamp ($T_{acq}$)**: $T_{acq} \le t_0 - 15\text{ min}$.
11. **Publication Timestamp ($T_{pub}$)**: $T_{pub} \le t_0 - 10\text{ min}$ (GTS METAR broadcast).
12. **Causal Availability ($T_{pub} \le t_0$)**: `VERIFIED` (100.0%).
13. **Empirical Benchmark Coverage**: 347 / 347 origins.
14. **H1-H24 Support**: Spatially unrepresentative of Nuolja microclimate.
15. **Limitations**: Cloud base height and layer fraction at Kiruna reflect inland plateau air masses and fail to represent microscale alpine cloud formation over SITES Nuolja.
- **Classification**: `REJECTED — SPATIAL & TERRAIN MISMATCH`.

#### Candidate B4: Regional Ceilometer Network (Sodankylä, Ivalo, Tromsø, Tarfala)
1. **Exact Product**: FMI / MET Norway / ACTRIS Regional Ceilometer Network.
2. **Spatial Separation**: **$100\text{ km} \dots 250\text{ km}$**.
3. **Limitations**: Extreme geographic separation across major mountain barriers; non-representative of Nuolja microclimate.
- **Classification**: `REJECTED — SPATIAL & TERRAIN MISMATCH`.

---

### Candidate Family C: Nearby / Upwind Surface & Radiosonde Observations

#### Candidate C1: SITES Abisko ANS Ground Surface Radiation (Abisko ANS, 388 m ASL)
1. **Exact Product**: SITES ANS Level-2 Radiation Dataset (`SW_IN_DIR`, `SW_IN_DIFF`).
2. **Exact Variables**: Direct beam shortwave radiation, diffuse shortwave radiation, transmissivity.
3. **2024 Coverage**: 347 / 347 origins (100.0%).
4. **Reconciliation with Stage 8.3**: Evaluated under 5-fold cross-validation in Stage 8.3 and **REJECTED** (+0.63 W/m² MAE degradation, +1.00 pp nMAE degradation).
- **Classification**: `REJECTED — DUPLICATE (STAGE 8.3)`.

#### Candidate C2: Riksgränsen / Katterat Upwind Surface Station (MET Norway, ~30–35 km W)
1. **Exact Product**: MET Norway Automatic Weather Station Feed (Riksgränsen/Katterat).
2. **Exact Variables**: Surface 2m Temperature, Relative Humidity, 10m Wind, Surface Pressure.
3. **Distance from Nuolja**: $30\text{ km} \dots 35\text{ km}$ West (Upwind along E10 valley).
4. **Information Novelty**: **NOT NOVEL**. Surface relative humidity is strongly correlated with MEPS 2m RH (already included in Stage 8.1). Station does not observe vertical cloud optical thickness or 3D cloud structure.
- **Classification**: `NOT NOVEL — REDUNDANT WITH MEPS RH`.

#### Candidate C3: Bodø Radiosonde Sounding (MET Norway, ~220 km WSW)
1. **Exact Product**: Bodø Upper-Air Sounding (00Z / 12Z Radiosonde).
2. **Distance from Nuolja**: **$220\text{ km}$ WSW** across Norwegian Sea/fjords.
3. **Limitations**: 12-hour temporal resolution; $220\text{ km}$ maritime distance; non-causal for hourly forecast origins; redundant with MEPS 3D atmospheric initial state.
- **Classification**: `REJECTED — LOW CADENCE & SPATIAL MISMATCH`.

---

### Candidate Family D: Operational Satellite & Composite Cloud Observational Sources

#### Candidate D1: EUMETSAT NWC SAF PPS CMIC (`EO:EUM:DAT:MULT:PPS-CMIC`)
1. **Exact Product**: EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC) L2 Swaths.
2. **Exact Variables**: Cloud Optical Thickness (`cot`), Particle Effective Radius (`eff_radius`), Cloud Mask (`cma`), Cloud Phase (`phase`).
3. **2024 Public Coverage**: **190 / 271 daylight origins (70.11%)**.
4. **Temporal Resolution**: ~42 polar passes per day over Lapland.
5. **Spatial Resolution**: $1.0\text{ km}$ polar stereographic grid.
6. **Distance from Nuolja**: $< 1.0\text{ km}$ pixel proximity.
7. **Observation Type**: Direct polar satellite radiance retrieval.
8. **Information Novelty**: Genuinely novel satellite solar/thermal retrieval.
9. **Acquisition Timestamp ($T_{acq}$)**: $T_{acq} \le t_0$ for 346/347 origins.
10. **Publication Timestamp ($T_{pub}$)**: Unverified on open HTTP catalog for 27 origins.
11. **Causal Availability ($T_{pub} \le t_0$)**: `CONDITIONAL / UNVERIFIED`.
12. **Empirical Benchmark Coverage**: 190 / 347 origins (`VALID_OPTICAL`), 76 (`POLAR_NIGHT`), 34 (`NO_GRANULE`), 27 (`CAUSALITY_REJECTED`), 20 (`LOW_SUN_INVALID`).
13. **Daylight Optical Coverage Gate**: **70.11%** (Fails predeclared $\ge 90.0\%$ threshold).
14. **Live Data Store Audit**: Direct REST query `https://api.eumetsat.int/data/browse/collections/EO:EUM:DAT:MULT:PPS-CMIC` returned **HTTP 404**; identifier absent from all 188 exposed live collections.
15. **Limitations**: Open HTTP mirror archive incomplete; optical retrievals return fill values (`-9999`) during polar night ($SZA > 84^\circ$).
- **Classification**: `CONDITIONAL — UNVERIFIED LIVE ROUTE & COVERAGE GATE FAIL`.

#### Candidate D2: EUMETSAT Optimal Cloud Analysis CDR (`EO:EUM:DAT:0617`)
1. **Exact Product**: Optimal Cloud Analysis Climate Data Record Release 1 - MSG - 0 degree.
2. **Variables**: Cloud Optical Thickness, Effective Radius, Cloud Top Pressure.
3. **Live Metadata Audit**: Endpoint `https://api.eumetsat.int/data/browse/1.0.0/collections/EO%3AEUM%3ADAT%3A0617?format=json` returned **HTTP 200**.
4. **Temporal Record**: **2004-01-19 through 2019-08-31** (15-minute resolution).
5. **Decision**: **CLOSED / NOT USABLE** for the locked POLARIS 2024 benchmark because data record terminates in August 2019.
- **Classification**: `REJECTED — TEMPORAL CUTOFF (ENDS 2019)`.

#### Candidate D3: NASA VIIRS Science Level-2 Cloud Properties (`CLDPROP_L2_VIIRS`)
1. **Exact Product**: `CLDPROP_L2_VIIRS_SNPP`, `CLDPROP_L2_VIIRS_NOAA20`, `CLDPROP_L2_VIIRS_NOAA21`.
2. **Causality Audit**: Standard NASA LAADS science Level-2 products exhibit an archiving dissemination delay of **3 to 8 hours** post-acquisition ($T_{pub} > t_0$). $T_{pub} \le t_0$ is **0 / 347 origins (0.0%)**.
3. **Polar Night**: Optical channels return fill values for $SZA > 84^\circ$.
- **Classification**: `BLOCKED — OPERATIONALLY NON-CAUSAL (LATENCY 3-8H)`.

#### Candidate D4: NASA VIIRS Near-Real-Time Level-2 (`CLDPROP_L2_VIIRS_*_NRT`)
1. **Causality & Archive Audit**: Dissemination latency is 1–3 hours ($T_{pub} > t_0$ for near-$t_0$ passes). Crucially, NASA LANCE does **NOT** maintain a permanent retrospective 2024 archive for NRT granules (purged after 7–14 days).
- **Classification**: `BLOCKED — OPERATIONALLY NON-CAUSAL & NO 2024 ARCHIVE`.

#### Candidate D5: Meteosat SEVIRI / MTG FCI Geostationary Imagery
1. **Geostationary Viewing Geometry**: Sub-satellite point $0^\circ\text{N}, 0^\circ\text{E}$. Nuolja position $68.36^\circ\text{N}, 18.74^\circ\text{E}$.
2. **Limitations**: Satellite Zenith Angle $\theta_s \approx 76.54^\circ$. Parallax displacement $\Delta x \approx 20.9\text{ km}$ for $5\text{ km}$ cloud tops. Severe N-S pixel stretching ($3\text{ km} / \cos(76.54^\circ) \approx 12.9\text{ km}$). EUMETSAT NWC SAF explicitly does not recommend geostationary cloud optical retrievals north of $65^\circ\text{N}$.
- **Classification**: `REJECTED — PARALLAX & HIGH LATITUDE GEOMETRY`.

#### Candidate D6: Scandinavian Weather Radar Composite (NORDRAD)
1. **Radar Geometry & Physics Audit**: Kiruna radar ($88\text{ km}$ ESE) beam elevation ($0.5^\circ$) places sampling volume $>2,000\text{ m}$ above ground level at Nuolja range, overshooting low boundary-layer clouds. Scandes peaks block low beams. Radar detects precipitation hydrometeors ($>100\ \mu\text{m}$), whereas solar attenuation is dominated by cloud droplets ($5-20\ \mu\text{m}$).
- **Classification**: `REJECTED — RADAR GEOMETRY & SENSITIVITY MISMATCH`.

---

## 4. Master Candidate Evidence & Classification Matrix

| ID | Candidate Source Name | Provider / Location | Distance to Nuolja | 2024 Benchmark Coverage | Causal Availability ($T_{pub} \le t_0$) | Information Novelty vs Stage 8.1 | Classification | Primary Blocking / Killing Constraint |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **A1** | **Nuolja Summit Sky Imager** | SITES Nuolja | $0.0\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | Genuinely Novel | `REJECTED` | No continuous calibrated 2024 all-sky camera archive exists. |
| **A2** | **Abisko ANS Sky Camera** | SITES ANS | $3.23\text{ km}$ | 0 / 347 (0.0%) | `UNVERIFIED` | Partially Novel | `REJECTED` | Fixed-angle landscape phenology camera; non-calibrated for cloud COT. |
| **A3** | **Nuolja Radiation Context** | SITES Logger | $0.0\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | **NOT NOVEL** | `NOT NOVEL` | 14 radiation persistence/variance features already in Stage 8.1 champion. |
| **B1** | **Nuolja Summit Ceilometer** | SITES Nuolja | $0.0\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | Genuinely Novel | `REJECTED` | Non-existent; no ceilometer installed on Nuolja summit in 2024. |
| **B2** | **Abisko ANS Ceilometer** | SITES ANS | $3.23\text{ km}$ | $<15\%$ origins | `UNVERIFIED` | Genuinely Novel | `REJECTED` | Episodic campaign data; lacks continuous 2024 machine-readable archive. |
| **B3** | **Kiruna METAR Ceilometer** | SMHI / ESNQ | $88.4\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | Partially Novel | `REJECTED` | 88.4 km separation across Scandes mountain ridge; plateau air mass mismatch. |
| **B4** | **Regional Ceilometers** | FMI / MET Norway | $>100\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | Partially Novel | `REJECTED` | Extreme geographic distance (>100–250 km) across mountain barriers. |
| **C1** | **Abisko Ground Radiation** | SITES ANS | $3.23\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | Duplicate | `REJECTED` | Evaluated & REJECTED in Stage 8.3 CV (+0.63 W/m² MAE degradation). |
| **C2** | **Riksgränsen AWS Weather** | MET Norway | $30-35\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | **NOT NOVEL** | `NOT NOVEL` | Surface T/RH/Pressure redundant with MEPS 2m RH in Stage 8.1. |
| **C3** | **Bodø Radiosonde Sounding** | MET Norway | $220\text{ km}$ | 347 / 347 (100%) | `REJECTED` | Partially Novel | `REJECTED` | 12h resolution, 220 km maritime separation; non-causal for hourly origins. |
| **D1** | **EUMETSAT NWC SAF CMIC** | MET Norway / EUM | $<1.0\text{ km}$ | 190 / 271 (70.1%) | `CONDITIONAL` | Genuinely Novel | `CONDITIONAL` | Open HTTP daylight coverage 70.11% fails >=90% gate; live product 404. |
| **D2** | **EUMETSAT OCA CDR 0617** | EUMETSAT | Gridded 0° | 0 / 347 (0.0%) | `REJECTED` | Genuinely Novel | `REJECTED` | Live REST metadata confirms record ends in August 2019; closed for 2024. |
| **D3** | **NASA VIIRS Science L2** | NASA LAADS | $<2.5\text{ km}$ | 225 / 347 (64.8%) | `BLOCKED` | Genuinely Novel | `BLOCKED` | Dissemination latency 3–8h ($T_{pub} > t_0$); polar night optical fill values. |
| **D4** | **NASA VIIRS NRT L2** | NASA LANCE | $<2.5\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | Genuinely Novel | `BLOCKED` | Latency 1–3h ($T_{pub} > t_0$); no retrospective 2024 archive maintained. |
| **D5** | **Meteosat SEVIRI/FCI** | EUMETSAT | $\approx 20.9\text{ km}$ | 0 / 347 (0.0%) | `BLOCKED` | Genuinely Novel | `REJECTED` | Viewing zenith $\theta_s = 76.54^\circ$; severe parallax and high-latitude distortion. |
| **D6** | **NORDRAD Weather Radar** | SMHI / FMI | $>85\text{ km}$ | 347 / 347 (100%) | `VERIFIED` | Genuinely Novel | `REJECTED` | Beam overshooting (>2000m ASL), terrain blocking, precip-droplet mismatch. |

---

## 5. Ranked Shortlist & Stage 8.15B Authorization Audit

### Ranked Shortlist of Top Candidates
1. **Top Candidate**: **EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)**
   - Classification: **`CONDITIONAL`**
   - Rationale: High spatial proximity (<1 km) and direct satellite optical/thermal retrieval (`cot`, `eff_radius`, `cma`).
2. **Second Candidate**: **Kiruna Airport Ceilometer (ESNQ METAR)**
   - Classification: **`REJECTED — SPATIAL & TERRAIN MISMATCH`**
   - Rationale: 100% causal 2024 archive, but $88.4\text{ km}$ spatial separation across Scandes mountain barrier makes cloud base height non-representative of Nuolja microclimate.

---

### Mandatory 6-Point Gate Check for Stage 8.15B Authorization

To authorize Stage 8.15B, the strongest candidate (**EUMETSAT NWC SAF PPS CMIC**) must satisfy **ALL 6** pre-declared conditions:

| Gate Condition | Evaluation Result | Supporting Evidence / Audit Finding |
| :--- | :---: | :--- |
| **1. Causal availability empirically demonstrated ($T_{pub} \le t_0$)** | **FAIL** | 27 swaths lack verified publication timestamps ($T_{pub}$) on open HTTP mirrors. |
| **2. 2024 coverage is sufficient ($\ge 90.0\%$ daylight optical gate)** | **FAIL** | Empirical daylight optical coverage is **70.11%** (190 / 271 daylight origins), failing the $\ge 90.0\%$ threshold. |
| **3. Spatial / terrain representativeness is defensible** | **PASS** | $1.0\text{ km}$ polar stereographic grid centered over SITES Nuolja. |
| **4. Information is genuinely novel relative to Stage 8.1** | **PASS** | Satellite Cloud Optical Thickness (`cot`) and Effective Radius (`eff_radius`) are novel satellite retrievals. |
| **5. Extraction is operationally reproducible** | **FAIL** | Live EUMETSAT Data Store REST query for collection `EO:EUM:DAT:MULT:PPS-CMIC` returned **HTTP 404** (product ID absent from 188 live collections). |
| **6. No future observation leakage is possible** | **PASS** | Strict timestamp filtering enforced ($t \le t_0$). |

---

### Mandatory Gate Outcome & Stage 8.15B Authorization Decision

Because the strongest candidate fails Gate Conditions 1, 2, and 5:

- **Stage 8.15B Authorization**: **NOT AUTHORIZED**
- **Explicit Conclusion**:

$$\Large \mathbf{Stage\ 8.15B\ NOT\ JUSTIFIED.}$$

---

## 6. Required Final Verification Statement

```
================================================================================
POLARIS STAGE 8.15A FINAL FEASIBILITY AUDIT SUMMARY
================================================================================
Candidates Investigated:             13 candidate sources across 4 families (A - D)
Strongest Candidate Evaluated:       EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)
Strongest Candidate Classification:  CONDITIONAL
Daylight Optical Coverage:           70.11% (190 / 271 daylight origins)
Predeclared Coverage Gate (>= 90%): FAILED (70.11% < 90.0%)
Live Catalogue Product ID Status:    HTTP 404 / ABSENT (EO:EUM:DAT:MULT:PPS-CMIC)

PRIMARY BLOCKERS:
1. Public open HTTP THREDDS archive daylight optical coverage (70.11%) fails predeclared >=90.0% daylight coverage threshold.
2. Live REST query for collection EO:EUM:DAT:MULT:PPS-CMIC returned HTTP 404 and is absent from 188 live collections.
3. Operational publication timestamps (T_pub <= t0) remain unverified on 27 historical open HTTP swaths.
4. Optical retrievals (COT, CER) return physical fill values during polar night (SZA > 84 deg, 76 origins / 21.9%).
5. All other local/upwind candidate sources suffer from severe spatial/terrain mismatch, non-existence in 2024, or non-causal latency.

STAGE 8.15B AUTHORIZED:               NO
FINAL SCIENTIFIC CONCLUSION:          Stage 8.15B NOT JUSTIFIED.

FIREWALL CONFIRMATION:
- Stage 8.1 Operational Champion:    UNTOUCHED (Daytime nMAE = 28.0688%)
- ODD Benchmark Target Access:       UNTOUCHED (0 evaluation reads)
- Master Benchmark & Handoff:        UNTOUCHED (0 changes)
- Forecasting Experiments Executed:  0
================================================================================
```
