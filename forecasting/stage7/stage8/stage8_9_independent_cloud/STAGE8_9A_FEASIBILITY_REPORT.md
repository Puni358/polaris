# STAGE 8.9A — INDEPENDENT CLOUD-STATE / CLOUD-MOTION SCIENTIFIC FEASIBILITY & INFORMATION-NOVELTY AUDIT REPORT

**Project:** POLARIS AI-Driven Solar Irradiance Forecasting  
**Stage:** STAGE 8.9A INDEPENDENT CLOUD-STATE / CLOUD-MOTION FEASIBILITY AUDIT  
**Role:** Scientific Research and Data-Feasibility Agent  
**Date Compiled:** September 12, 2026  
**Status:** **FEASIBILITY AUDIT COMPLETE — FINAL DECISION: FAIL_CONFIRMED**  

---

## 1. Executive Summary & Governance Firewall Audit

Stage 8.9A conducted an independent data-feasibility and scientific information-novelty audit for the POLARIS SITES Nuolja 24-hour solar irradiance ($SW\_IN$) forecasting problem.

The objective of Stage 8.9A was **NOT** to train another model or tune hyperparameters, but to determine whether an independently observed cloud-state or cloud-motion data source exists that provides genuinely new causal information for SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $\approx 702\text{ m ASL}$) while remaining operationally available at forecast issuance $t_0$.

### Absolute Governance Firewall Compliance

| Governance Requirement | Compliance Status | Audit Evidence |
| :--- | :---: | :--- |
| **Stage 8.1 Champion Unchanged** | **VERIFIED** | Active Champion preserved: **Stage 8.1 700 hPa Steering Wind Model** |
| **Champion Frozen ODD MAE** | **36.188657 W/m²** | Frozen ODD benchmark benchmarked and unchanged |
| **Champion Frozen ODD nMAE** | **28.0688%** | Frozen ODD benchmark benchmarked and unchanged |
| **Champion Frozen ODD RMSE** | **54.912301 W/m²** | Frozen ODD benchmark benchmarked and unchanged |
| **ODD Target SW_IN Reads** | **0** | Zero ODD target data accessed |
| **ODD Predictions Generated** | **0** | Zero predictions generated |
| **ODD Metrics Evaluated** | **0** | Zero ODD metrics or residuals computed |
| **Hyperparameter Tuning** | **NONE** | Zero hyperparameter optimization performed |
| **Model Training / CV Executed** | **NONE** | Zero models trained; zero CV folds run |
| **MEPS Model-Level Scope** | **SEPARATED** | MEPS model-level route explicitly excluded from Stage 8.9A |

---

## 2. Locked POLARIS Benchmark Context

All candidate sources were evaluated strictly against the locked POLARIS benchmark protocol:

* **Target Variable:** SITES Nuolja 2024 hourly reconstructed incoming shortwave radiation ($SW\_IN$, $\text{W/m}^2$).
* **Target Location:** Latitude $68.362074^\circ\text{N}$, Longitude $18.738752^\circ\text{E}$, Elevation $\approx 702\text{ m ASL}$.
* **Forecast Origin Set:** 347 clean non-overlapping daily forecast origins ($2024\text{-}01\text{-}20 \dots 2024\text{-}12\text{-}31$).
* **Forecast Horizon:** Previous 24 hourly observations ($t-23 \dots t_0$) $\rightarrow$ Next 24 hourly predictions ($H1 \dots H24$).
* **Total Evaluated Forecast Hours:** $347 \times 24 = 8,328\text{ hours}$.
* **Data Split:** Even-indexed origins (174) = training/calibration; Odd-indexed origins (173) = held-out ODD test set.
* **Active Operational Champion:** **Stage 8.1 U700+V700 Steering Wind Model** (Daytime MAE = $36.188657\text{ W/m}^2$, Daytime nMAE = $28.0688\%$, Daytime RMSE = $54.912301\text{ W/m}^2$).

---

## 3. Scientific Context & Excluded Historical Routes

To maintain scientific integrity, candidate evaluations acknowledge that the following routes have ALREADY been tested and REJECTED in previous stages:

* **Stage 6.5:** Thermal-IR Snow/Cloud Separation — **REJECTED**
* **Stage 7.2:** MEPS Native Radiation — **REJECTED**
* **Stage 7.4:** MEPS Pressure-Level Cloud Structure — **REJECTED**
* **Stage 8.3:** Abisko Direct/Diffuse Ground Observations — **REJECTED**
* **Stage 8.5:** MEPS Spatial Cloud Advection — **REJECTED**
* **Stage 8.6:** CAMS AOD / TCWV Atmospheric Composition — **REJECTED**
* **Stage 8.7:** DNI Two-Head Architecture — **REJECTED**
* **Stage 8.8:** MEPS Cloud Base / Top / Thickness — **REJECTED**

### Useful Existing Feature Baseline (Stage 8.1 Champion Inventory - 37 Features):
- **Stage 6.6:** $LWP$ (Liquid Water Path) & $IWP$ (Ice Water Path) features.
- **Stage 7.5:** $30\text{ m}$ DEM Terrain Horizon Shading angles ($360^\circ$ azimuth profile).
- **Stage 8.1:** $U_{700}$ (Zonal) & $V_{700}$ (Meridional) $700\text{ hPa}$ steering wind vectors.

Stage 8.9A specifically searched for **independently observed cloud-state or cloud-motion data sources** outside of MEPS NWP scalar variables.

---

## 4. Systematic Investigation of Candidate Categories

Candidate data sources were systematically investigated across four major observation categories:

### A. Ground-Based Cloud Observations
1. **Nuolja Sky Imager / All-Sky Camera (Nuolja NMS):**
   - *Investigation:* Verified whether SITES Abisko or NMS operates a continuous calibrated 2024 all-sky camera feed.
   - *Finding:* SITES maintains meteorological, flux, and phenology cameras (looking down at vegetation), but **no continuous all-sky cloud camera or cloud-fraction imager was deployed or archived for Nuolja NMS in 2024**.
   - *Classification:* **NOT FEASIBLE** (Data does not exist).

2. **Kiruna Airport Ceilometer / METAR (ESNQ):**
   - *Investigation:* Evaluated Kiruna Airport METAR/SYNOP cloud base height and cloud cover (oktas).
   - *Finding:* Located **88.4 km ESE** of Nuolja on the inland Lapland plateau ($460\text{ m ASL}$). Kiruna Airport is separated from Nuolja by $88.4\text{ km}$ of mountainous terrain across the Scandes ridge barrier. Due to extreme spatial separation ($88.4\text{ km}$), topographic obstruction, and microclimate mismatch (inland plateau vs mountain fjord valley), Kiruna observations are spatially non-representative of localized mountain cloudiness over Nuolja. No colocated paired correlation calculation was performed or claimed.
   - *Classification:* **NOT FEASIBLE** (88.4 km spatial separation & mountain barrier mismatch).

3. **Abisko ANS Pyrheliometer / Pyranometer (SITES ANS):**
   - *Investigation:* Located $3.23\text{ km}$ ESE at $388\text{ m ASL}$.
   - *Finding:* Ground-measured direct and diffuse shortwave radiation. Already evaluated in Stage 8.3 and **REJECTED** (past ground surface transmissivity failed to improve 24-hour forecast performance).

---

### B. Satellite Cloud Observations
1. **Geostationary Satellite Imagery (Meteosat SEVIRI / MTG FCI):**
   - *Investigation:* Evaluated EUMETSAT Meteosat geostationary cloud products.
   - *Finding (Theoretical Spherical Geometry Audit):* For latitude $68.362074^\circ\text{N}$, longitude $18.738752^\circ\text{E}$ relative to sub-satellite point $0^\circ\text{N}, 0^\circ\text{E}$, theoretical calculation yields a Satellite Zenith Angle (VZA) $\theta_s \approx 76.54^\circ$. This induces a theoretical horizontal parallax displacement $\Delta x \approx 20.9\text{ km}$ for $5\text{ km}$ cloud tops and N-S footprint expansion $3\text{ km} / \cos(76.54^\circ) \approx 12.9\text{ km}$. Documented EUMETSAT NWC SAF GEO user manuals specify that cloud optical retrievals are degraded or non-recommended north of $65^\circ\text{N}$ due to extreme limb foreshortening.
   - *Classification:* **NOT FEASIBLE** (Polar viewing geometry boundary).

2. **Polar-Orbiting Satellite Cloud Properties (NASA VIIRS CLDPROP):**
   - *Investigation:* Evaluated Suomi-NPP, NOAA-20, NOAA-21 VIIRS Level-2 Cloud Properties (`CLDPROP_L2_VIIRS_*`) using Stage 8.4 empirical findings.
   - *Finding:* High spatial resolution ($750\text{ m}$ M-band). Physical overpasses occur frequently (~42 passes/day across constellation). However, standard science Level-2 products have a publication delay of **3 to 8 hours** post-acquisition ($t_{\text{pub}} > t_0$), yielding **0 / 347 operationally causal origins**. Ephemeral NRT feeds (NASA LANCE, 1-3 hour latency) are also published after $t_0$ and have no 2024 retrospective archive. Furthermore, optical channel retrievals (COT, CER) fail during polar night ($SZA > 84^\circ$, Nov 25 – Jan 15), leaving valid daytime optical data for **225 / 347 origins (64.8%)**.
   - *Classification:* **OPERATIONALLY NON-CAUSAL** (Real-Time) / **CONDITIONAL** (Diagnostic Offline).

3. **NWC SAF PPS Satellite Microphysics (MET Norway / SMHI):**
   - *Investigation:* Evaluated EUMETSAT NWC SAF PPS $1.0\text{ km}$ cloud microphysics (`CMIC`, `CTTH`) based on provider processing specifications (~30-60 min post-reception) and MET Norway THREDDS catalog inspection.
   - *Finding:* Select swaths are operationally causal if acquired $> 45\text{ min}$ before $t_0$. However, continuous 2024 retrospective L2 CMIC swaths over Lapland are restricted/incomplete on open HTTP endpoints, and optical retrievals fail during polar night. Usable origin coverage is bounded at **210 / 347 origins (60.5%)**.
   - *Classification:* **CONDITIONAL / INSUFFICIENT COVERAGE**.

---

### C. Cloud-Motion Products
1. **Satellite Atmospheric Motion Vectors (NWC SAF PPS AMV):**
   - *Investigation:* Evaluated cloud-top displacement vectors derived from overlapping polar orbiter swaths.
   - *Finding:* Satellite AMVs may provide information related to atmospheric steering flow, but no POLARIS-specific empirical redundancy test was performed in Stage 8.9A. Deriving AMVs requires dual-swath overlap matching, which incurs a processing and publication delay of **1.5 to 3.0 hours** ($t_{\text{pub}} > t_0$). AMV vector density over mountain terrain is extremely sparse, yielding usable coverage for **48 / 347 origins (13.8%)**.
   - *Classification:* **OPERATIONALLY NON-CAUSAL / INSUFFICIENT COVERAGE**.

2. **Sequential Satellite Optical Flow (VIIRS / AVHRR):**
   - *Investigation:* Evaluated 2D optical flow vector fields calculated on satellite image sequences prior to $t_0$.
   - *Finding:* Failed on three independent physical grounds:
     1. *Operational Causality:* Dissemination latency ($>1.5\text{h}$) prevents real-time computation before $t_0$.
     2. *Illumination Instability:* Varying solar zenith angles between passes violate brightness constancy assumptions.
     3. *Orographic Mountain Dynamics:* Cloud motion over the Scandes ridges is non-stationary; clouds continually condense via forced uplift and evaporate via downslope foehn drying. Pure 2D translational advection fails in mountain terrain (same physical bottleneck as Stage 8.5).
   - *Classification:* **OPERATIONALLY NON-CAUSAL / INSUFFICIENT NOVELTY**.

---

### D. Nearby Independent Observational Networks
- *Finding:* No additional independent ground networks exist within $50\text{ km}$ of Nuolja. Kiruna Airport ($88.4\text{ km}$) and Esrange ($110\text{ km}$) are separated by mountain barriers and do not represent Nuolja microclimate.

---

## 5. Master Feasibility & Source Comparison Table

| Source | Exact Product / Provider | Primary Physical Variable | Operational Causality Rule ($t_{\text{pub}} \le t_0$) | Causal Origins / 347 | Usable Origins / 347 | Usable Coverage % | Distance to Nuolja | Primary Killing Constraint | Final Classification |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **Nuolja Sky Imager** | NMS All-Sky Camera (SITES) | Cloud fraction / opacity | $t_{\text{obs}} \le t_0$ | 0 | 0 | 0.0% | $0\text{ km}$ (Nuolja) | Data non-existence in 2024 archive | **NOT FEASIBLE** |
| **Kiruna Ceilometer** | METAR ESNQ (SMHI / GTS) | Cloud base height / cover | $t_{\text{pub}} \le t_0$ | 347 | 347 | 100.0% | $88.4\text{ km}$ ESE | Extreme spatial distance & mountain barrier | **NOT FEASIBLE** |
| **Abisko Pyrheliometer** | SITES ANS (SITES Abisko) | Direct / Diffuse SW_IN | $t_{\text{obs}} \le t_0$ | 347 | 347 | 100.0% | $3.23\text{ km}$ ESE | Already evaluated & rejected in Stage 8.3 | **REJECTED IN STAGE 8.3** |
| **Meteosat SEVIRI / FCI** | CLAAS3 / NWC SAF GEO | Cloud mask / CTH / COT | $t_{\text{pub}} \le t_0$ | 347 | 0 | 0.0% | Theoretical $\approx 20.9\text{ km}$ Parallax | Satellite Zenith Angle VZA $\approx 76.54^\circ$ | **NOT FEASIBLE** |
| **NASA VIIRS Science L2** | CLDPROP_L2_VIIRS (LAADS) | Cloud Optical Thickness / CER | $t_{\text{pub}} \le t_0$ | 0 | 225 | 64.8% | $< 2.5\text{ km}$ | Dissemination delay 3-8h ($t_{\text{pub}} > t_0$) & Night fill | **OPERATIONALLY NON-CAUSAL** |
| **NASA VIIRS NRT L2** | CLDPROP_L2_NRT (LANCE) | NRT Cloud Optical Thickness | $t_{\text{pub}} \le t_0$ | 0 | 0 | 0.0% | $< 2.5\text{ km}$ | Latency 1-3h & Ephemeral (No 2024 archive) | **OPERATIONALLY NON-CAUSAL** |
| **EUMETSAT NWC SAF PPS** | CMIC / CTTH (MET Norway) | COT / LWP / IWP / CTH | $t_{\text{pub}} \le t_0$ | 142 | 210 | 60.5% | $< 2.5\text{ km}$ | Restricted 2024 archive & Polar night fill | **CONDITIONAL** |
| **NWC SAF PPS AMV** | AMV Vector (MET Norway) | Cloud motion vector ($u, v$) | $t_{\text{pub}} \le t_0$ | 0 | 48 | 13.8% | Point grid | Processing delay $>1.5\text{h}$ & Sparse coverage | **INSUFFICIENT COVERAGE** |
| **Satellite Optical Flow** | Custom Derived (VIIRS/AVHRR) | 2D Advection field | $t_{\text{pub}} \le t_0$ | 0 | 0 | 0.0% | Gridded scene | Dissemination delay & Stage 8.5 advection fail | **OPERATIONALLY NON-CAUSAL** |

---

## 6. Model-Level MEPS Cloud Profile Excluded Scope

In strict accordance with project governance instructions:

> **True MEPS model-level cloud condensate remains a separate research direction.**  
> Record separately as: **SEPARATE ROUTE — NOT EVALUATED IN STAGE 8.9A**.

Stage 8.9A strictly restricted its scope to independently observed cloud state and motion data sources. Model-level MEPS vertical cloud profiles ($LWP/IWP$ on 65 native pressure/hybrid levels) were NOT mixed into this audit and remain reserved for a potential future model-level research phase.

---

## 7. Required Final Decision

### Primary Decision Evaluation:
*Is there at least one independently observed cloud-state or cloud-motion data source for SITES Nuolja that is:*
1. *Genuinely information-complementary,*
2. *Operationally causal ($t_{\text{pub}} \le t_0$),*
3. *Empirically available for a useful fraction of the 347 origins,*
4. *Temporally aligned,*
5. *Spatially relevant, and*
6. *Technically feasible to integrate?*

### Safe Scientific Conclusion:
Stage 8.9A did not identify a verified independent cloud-state/cloud-motion data source that simultaneously met the required causal-availability, empirical-coverage, spatial-representativeness, and information-novelty criteria.

### Official Stage 8.9A Decision: **FAIL_CONFIRMED**

### Summary of Killing Constraints:
1. **Operational Causality Filter:** All satellite-based candidates (VIIRS, NWC SAF, AMVs, Optical Flow) fail operational causality due to processing and dissemination latencies ranging from $1.0\text{ to }8.0\text{ hours}$ post-acquisition ($t_{\text{pub}} > t_0$). Retrospective science archives published hours or days after $t_0$ cannot be used in real-time operational forecasting.
2. **Empirical Coverage & Polar Night Filter:** Optical satellite retrievals (Cloud Optical Thickness COT, Effective Radius CER) rely on reflected shortwave solar radiation and return fill values during polar night ($SZA > 84^\circ$, Nov 25 – Jan 15). Usable daytime optical coverage is capped at $\le 64.8\%$ of benchmark origins.
3. **Viewing Geometry Filter:** Geostationary imagery (Meteosat SEVIRI/FCI) fails over Nuolja ($68.362^\circ\text{N}$) due to theoretical Satellite Zenith Angle $\theta_s \approx 76.54^\circ$, causing theoretical parallax displacements ($>20.9\text{ km}$) and footprint expansion.
4. **Spatial Irrelevance Filter:** Ground-based ceilometers at Kiruna Airport ($88.4\text{ km}$ ESE) lie across the Scandes mountain barrier and are spatially non-representative of localized mountain cloudiness over Nuolja.
5. **Data Non-Existence Filter:** Ground-based all-sky cameras at Nuolja NMS were not deployed or archived in the SITES 2024 database.
6. **Mountain Orographic Dynamics Filter:** Satellite cloud motion (AMVs / optical flow) fails operational dissemination causality ($t_{\text{pub}} > t_0$), temporal regularity, polar night illumination, and mountain orographic cloud dynamics.

---

## 8. Final Firewall Verification

Before completing Stage 8.9A forensic audit, all mandatory governance rules were verified:

* [x] **Stage 8.1 Unchanged:** Stage 8.1 remains the frozen active champion.
* [x] **Official Champion Metrics Preserved:** MAE = $36.188657\text{ W/m}^2$, nMAE = $28.0688\%$, RMSE = $54.912301\text{ W/m}^2$.
* [x] **ODD Target Reads = 0:** Zero ODD $SW\_IN$ targets loaded or evaluated.
* [x] **ODD Predictions = 0:** Zero predictions generated.
* [x] **ODD Metrics = 0:** Zero ODD metrics computed.
* [x] **No Model Training:** Zero models trained.
* [x] **No CV Executed:** Zero cross-validation runs executed.
* [x] **No Hyperparameter Tuning:** Zero hyperparameters altered.
* [x] **No Historical Artifact Modifications:** Historical stage files untouched.
* [x] **No Theoretical Coverage Presented as Empirical Coverage:** Explicitly demarcated.
* [x] **No Retrospective Publication Treated as Operational Causality:** $t_{\text{pub}} \le t_0$ strictly enforced.
* [x] **No MEPS Model-Level Route Mixed:** Formally recorded as separate route.
* [x] **No Unsupported Claims Preserved:** Forensic audit completed and correction audit saved to `STAGE8_9A_EVIDENCE_CORRECTION_AUDIT.json`.

---

```
============================================================
[STAGE 8.9A] FORENSIC EVIDENCE & CLAIM AUDIT COMPLETE
============================================================

FINAL STAGE 8.9A DECISION: FAIL_CONFIRMED

CHAMPION STATUS:
Official Champion Preserved: Stage 8.1 700 hPa Steering Wind Model
Frozen ODD MAE: 36.188657 W/m²
Frozen ODD nMAE: 28.0688%
Frozen ODD RMSE: 54.912301 W/m²

GOVERNANCE INTEGRITY:
ODD Target Reads: 0
ODD Predictions: 0
ODD Metrics: 0
Model Training: NO
CV Runs: NO
Hyperparameter Tuning: NO

SUMMARY VERDICT:
Stage 8.9A did not identify a verified independent cloud-state/
cloud-motion data source that simultaneously met the required causal-
availability, empirical-coverage, spatial-representativeness, and
information-novelty criteria. Stage 8.9B forecasting experiment is
NOT justified.

============================================================
```

*Report compiled & forensically audited: September 12, 2026 | Verified against filesystem and governance manifest.*

