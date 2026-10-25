# POLARIS STAGE 8 — NEXT RESEARCH-SPACE TRIAGE REPORT

> [!IMPORTANT]
> **GOVERNANCE STATUS: RESEARCH TRIAGE & SELECTION ONLY — NO EXPERIMENTS**
> - **Latest Route Status:** `ENEV_UPSTREAM_METAR` is **CLOSED_AFTER_GOVERNED_EVEN_REJECTION** (Failed G1–G4, $\Delta\text{MAE} = +0.1989\text{ W/m}^2$).
> - **Operational Champion:** **Stage 8.1 37-feature HGB Model** (`RETAINED_UNTOUCHED`)
> - **Protected ODD Benchmark Metrics:** **MAE 36.188657 W/m² | nMAE 28.0688% | RMSE 64.219495 W/m² | Bias +1.439399 W/m²**
> - **ODD Benchmark Status:** **100% UNTOUCHED & PROTECTED (`ODD_RUN = FALSE`)**
> - **Master Handoff & Route Registry:** **UNTOUCHED**
> - **Constraint Check:** NO model experiment executed. NO ODD access. NO champion modification.

---

## 1. Executive Summary & Research Context

Following the formal closure of `ENEV_UPSTREAM_METAR`, the POLARIS Stage 8 research program has completed a systematic triage of the remaining research space. The goal of this triage is to identify the single strongest remaining research axis that satisfies **BOTH**:
1. Genuine potential to add physical information beyond the frozen 37-feature Stage 8.1 control.
2. A realistic path to causal, real-data validation at SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$).

This triage strictly enforces all 8 required evaluation filters (**Physical Independence, Causal Availability, Real-Data Availability, Spatial Relevance, Temporal Resolution, Novelty, Operational Plausibility, and Experimental Testability**) across five broad research axes:
1. Cloud growth / decay / lifecycle / evolution
2. Orographic cloud formation / exact flow-regime formulation
3. Diffuse / broken-cloud radiative information
4. Other genuinely independent local or regional cloud observations
5. Any additional physical information not already tested

---

## 2. Evaluation Filters & Governance Standards

Every candidate route is evaluated against eight mandatory filters:

- **Filter A (Physical Independence):** Does the feature measure a physical quantity or relationship distinct from existing Stage 8.1 inputs (historical $SW\_IN$ context, single-level MEPS meteorology, 700 hPa Cartesian winds, 2D cloud fraction/LWP/IWP, Solis clear-sky GHI, 360° DEM horizon profile)?
- **Filter B (Causal Availability):** Was the data published and available prior to $t_0 = 00:00\text{ UTC}$ for all 2024 benchmark origins ($t_{\text{pub}} \le t_0$)?
- **Filter C (Real-Data Availability):** Does authentic 2024 observational or numerical data exist, avoiding synthetic/reconstructed placeholders?
- **Filter D (Spatial Relevance):** Is the data physically coupled to Mount Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}, 702\text{ m ASL}$) rather than distant stations decoupled by mountain barriers?
- **Filter E (Temporal Resolution):** Is the resolution sufficient (hourly or sub-hourly) to impact H1–H24 irradiance forecasts?
- **Filter F (Novelty):** Has this physical information source remained un-tested or under-tested in Stage 8?
- **Filter G (Operational Plausibility):** Could POLARIS plausibly ingest this data source in operational real-time deployment?
- **Filter H (Experimental Testability):** Can the candidate be evaluated under the locked 5-fold EVEN CV protocol without altering the benchmark?

---

## 3. Comprehensive Domain Triage across 5 Broad Axes

### Axis 1: Cloud Growth / Decay / Lifecycle / Evolution

| Candidate Route | Primary Information Source | Classification | Key Evaluation Finding |
| :--- | :--- | :---: | :--- |
| **Inter-Run MEPS Condensate Tendency ($\Delta\text{LWP}_{\text{run}}$)** | Consecutive MEPS 2.5km runs ($D-0\text{ 00Z}$ vs $D-1\text{ 18Z}$) | **CLASS B** | Causal and available across 347 origins, but measures model drift/spin-up rather than observed cloud evolution (similar to Stage 6.4). |
| **Ground Radiometer Pre-$t_0$ Transmissivity ($\frac{dk_t}{dt}$)** | Abisko pyranometer pre-$t_0$ hours | **CLASS D** | Operationally infeasible: sub-Arctic Lapland is dark from 21:00 to 00:00 UTC during winter, spring, and autumn ($t_0 = 00:00\text{ UTC}$). |
| **All-Sky Camera / Ceilometer Cloud Sequences** | Local ground optical imagery | **CLASS D** | No continuous calibrated 2024 daytime all-sky camera archive exists at Abisko (`CLOSED_FEASIBILITY`). |
| **Geostationary SEVIRI IR Cloud Tendencies** | EUMETSAT MSG SEVIRI 15-min imagery | **CLASS D** | Severe high-latitude viewing geometry ($VZA = 78.07^\circ$, $>21\text{ km}$ parallax displacement at $68.36^\circ\text{N}$). |

---

### Axis 2: Orographic Cloud Formation / Exact Flow-Regime Formulation

| Candidate Route | Primary Information Source | Classification | Key Evaluation Finding |
| :--- | :--- | :---: | :--- |
| **Faithful Scandes Orographic Flow Regime ($Fr$, $Fr_m$, $U_\perp$, $w_{\text{oro}}$)** | MEPS continuous vertical profiles ($P_{\text{sfc}} \to 700\text{ hPa}$) + 30m DEM ridge normal ($200^\circ$) | **CLASS A** | **STRONGEST CANDIDATE.** Evaluates continuous layer-integrated Brunt–Väisälä stability $N$ and Scandes barrier-normal wind $U_\perp$. Re-evaluates Orographic Flow with scientific fidelity, replacing the approximate 2-point implementation tested in Stage 8.24. |
| **Upstream Norwegian METAR Stations (ENDU, ENAN, ENTC)** | Norwegian METAR reports (Bardufoss, Andøya, Tromsø) | **CLASS B** | 100% causal and real, but 78–146 km distant WNW/NNW across $>1500\text{ m}$ Scandes ridges. ENEV rejection ($+0.1989\text{ W/m}^2$) proved coastal METARs undergo severe mountain decoupling. |
| **Upstream SYNOP Surface Stations (Katterjåkk, Narvik)** | SMHI / MET Norway SYNOP reports | **CLASS C** | Surface boundary layer temp/humidity measures surface microclimate, not column cloud optics; 100% assimilated into MEPS 18Z. |

---

### Axis 3: Diffuse / Broken-Cloud Radiative Information

| Candidate Route | Primary Information Source | Classification | Key Evaluation Finding |
| :--- | :--- | :---: | :--- |
| **Broken-Cloud Enhancement Index ($I_{\text{diffuse}}$)** | Derived from `cloud_frac` $\times (1 - \text{cloud\_frac}) \times \text{clearsky\_ghi}$ | **CLASS C** | 100% mathematically redundant with existing Stage 8.1 features. Gradient boosted decision trees naturally partition non-linear interaction products of existing inputs. |
| **Terrain-Reflected Shortwave Radiation** | Geometric horizon profile $\times$ snow albedo | **CLASS C** | Geometrically constrained ($V_{\text{terrain}} = 5.78\%$); realistic mean flux is immaterial ($2.5 \dots 4.5\text{ W/m}^2$); fully closed in reduction report. |

---

### Axis 4: Other Genuinely Independent Local or Regional Cloud Observations

| Candidate Route | Primary Information Source | Classification | Key Evaluation Finding |
| :--- | :--- | :---: | :--- |
| **Real SWEPOS GNSS Tropospheric Delay (`ABIS` ZTD / PWV)** | Real SWEPOS GNSS receiver `ABIS` at Abisko ($1.2\text{ km}$ from Nuolja) | **CLASS A** | Direct, continuous microwave observation of column moisture at Abisko. Stage 8.19 failed due to an invalid synthetic implementation, but authentic 2024 SWEPOS data exists and provides a true observational constraint. |
| **SMHI Composite Weather Radar (`comp` product)** | SMHI 5-min Sweden-wide radar composite | **CLASS C** | C-band radar measures precipitating hydrometeors ($>100\,\mu\text{m}$), not non-precipitating cloud droplets ($1\text{--}20\,\mu\text{m}$) driving SW_IN errors. Severe mountain terrain blockage below $2500\text{ m ASL}$ over Abisko; assimilated into MEPS. |
| **Kiruna / Luleå Individual Radar Volume Files (`qcvol`)** | SMHI individual radar API | **CLASS D** | Historical 2024 archive is empty in SMHI open data API (`{"days":[]}`). |

---

### Axis 5: Any Additional Physical Information Not Already Tested

| Candidate Route | Primary Information Source | Classification | Key Evaluation Finding |
| :--- | :--- | :---: | :--- |
| **MEPS Analysis Increments ($\Delta q_{\text{assim}}, \Delta T_{\text{assim}}$)** | MEPS 00Z Analysis minus 18Z Forecast background | **CLASS B** | Measures real-time observational corrections applied to NWP initial state at $t_0$. Real-data archive availability for raw analysis files requires verification. |
| **Upstream Radiosondes (Bodø 195km WSW, Sodankylä 335km ESE)** | WMO GTS soundings | **CLASS C** | 195–335 km distant across mountains; 100% assimilated into operational MEPS 18Z initialization. |
| **Atmospheric Radiative Fine Physics (3D Aerosols, $q(p)$, $O_3$, Rayleigh, Trace Gases)** | CAMS 3D profiles / HITRAN databases | **CLASS C / D** | Radiative transfer calculations prove broadband GHI impact is $<1.8\text{ W/m}^2$ (immaterial) or 100% redundant with Stage 8.1 inputs. Fully closed. |

---

## 4. Deep-Dive Specification for CLASS A & CLASS B Routes

### CLASS A Route 1: Faithful Scandes Orographic Flow Regime (Continuous $N$ + $U_\perp$ + $Fr$)

- **Exact Information Source:** Operational MEPS 2.5km vertical profile forecasts ($P_{\text{sfc}} \to 700\text{ hPa}$) + 30m DEM terrain slope & Scandes ridge normal ($200^\circ$ SSW–NNE orientation).
- **Physical Information Provided:** Continuous layer-integrated Brunt–Väisälä buoyancy frequency $N = \sqrt{\frac{g}{\theta_v}\frac{\partial\theta_v}{\partial z}}$ integrated over the surface-to-700hPa column, combined with Scandes barrier-normal wind $U_\perp = u_{700}\sin(200^\circ) + v_{700}\cos(200^\circ)$ to yield non-dimensional Froude numbers ($Fr = \frac{U_\perp}{N h}$, $Fr_m = \frac{U_\perp}{N_m h}$) and kinematic uplift rate $w_{\text{oro}} = U_\perp \cdot |\nabla z|$. Distinguishes forced mountain uplift ($Fr \ge 1.0$) from low-level flow blocking ($Fr < 1.0$).
- **Why Stage 8.1 Does Not Contain It:** Stage 8.1 contains raw Cartesian $u_{700}, v_{700}$ and single-level 2m temperature/humidity. Decision tree axis-aligned splits ($u > c$, $v > c$) cannot compute continuous layer stability integrals or rotated vector projections without deep interaction terms.
- **Expected Causal Timestamp:** Available at $t_0 = 00:00\text{ UTC}$ from MEPS 18Z forecast.
- **2024 Coverage Status:** **347 / 347 origins (100.0%)**.
- **Spatial Relationship to Nuolja:** Direct local grid cell over Mount Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$) with effective local mountain relief $h = 828\text{ m}$.
- **Likely Feature Representation:** Continuous $U_\perp$ ($\text{m/s}$), continuous $N$ ($\text{s}^{-1}$), dry Froude $Fr$, moist Froude $Fr_m$, kinematic uplift rate $w_{\text{oro}}$ ($\text{m/s}$).
- **Major Leakage Risks:** Zero (derived strictly from forecast fields valid for $t_0+h$ and static DEM).
- **EVEN Governance Compatibility:** 100% governable under standard locked EVEN protocol.
- **Qualification Note:** Stage 8.24 was provisionally rejected under an implementation qualification (it evaluated an approximate 2-point shortcut). The exact continuous formulation remains the single highest-value Class A route.

---

### CLASS A Route 2: Real SWEPOS GNSS Tropospheric Delay & Water Vapour (`ABIS` ZTD / PWV)

- **Exact Information Source:** Real SWEPOS GNSS receiver `ABIS` at Abisko ($68.353^\circ\text{N}, 18.816^\circ\text{E}$, $388\text{ m ASL}$, $1.2\text{ km}$ south of Nuolja summit).
- **Physical Information Provided:** Direct, continuous, all-weather microwave measurement of column integrated water vapor (PWV) and zenith total delay ($\text{ZTD}_{\text{latest}}$ and 3h tendency $\Delta\text{ZTD}_{3\text{h}}$) directly over Abisko.
- **Why Stage 8.1 Does Not Contain It:** Stage 8.1 relies 100% on MEPS NWP modeled humidity (`fc_relative_humidity_2m`). It contains zero independent observational column moisture measurements.
- **Expected Causal Timestamp:** Available by $23:30\text{ UTC } D-1$ ($t_0 - 30\text{ min}$).
- **2024 Coverage Status:** SWEPOS historical 2024 archive exists. (Real SWEPOS extraction script required to confirm 347-origin coverage).
- **Spatial Relationship to Nuolja:** Direct local station at Abisko valley floor ($1.2\text{ km}$ south of Nuolja).
- **Likely Feature Representation:** Real $\text{ZTD}_{\text{latest}}$ ($\text{m}$), $\Delta\text{ZTD}_{3\text{h}}$ ($\text{m}$), and moisture innovation $(\text{PWV}_{\text{obs}} - \text{PWV}_{\text{MEPS}})$.
- **Major Leakage Risks:** None (causally timestamped $t \le t_0$).
- **EVEN Governance Compatibility:** 100% governable under locked EVEN protocol.

---

### CLASS B Route 1: Causal Inter-Run MEPS Cloud Condensate Tendency ($\Delta\text{LWP}_{\text{run}}$)

- **Exact Information Source:** Consecutive MEPS 2.5km model runs ($D-0\text{ 00Z}$ issuance vs $D-1\text{ 18Z}$ issuance).
- **Physical Information Provided:** Cloud condensate build-up/dissipation rate ($\Delta \text{LWP} = \text{LWP}_{00Z} - \text{LWP}_{18Z}$) predicted by the NWP model physics engine between consecutive model runs prior to $t_0$.
- **Why Stage 8.1 Does Not Contain It:** Stage 8.1 uses a single static forecast run (D-1 18Z) and lacks multi-issuance temporal trend features.
- **Expected Causal Timestamp:** $t_0 = 00:00\text{ UTC}$.
- **2024 Coverage Status:** **347 / 347 origins (100.0%)**.
- **Spatial Relationship to Nuolja:** Direct local 2.5km grid cell.
- **Likely Feature Representation:** $\Delta\text{LWP}_{\text{run}}(t)$, $\Delta\text{IWP}_{\text{run}}(t)$, $\Delta\text{cloud\_frac}_{\text{run}}(t)$.
- **Major Leakage Risks:** Low, but risk of measuring NWP spin-up/model drift artifacts rather than true physical cloud evolution (as observed in Stage 6.4).
- **EVEN Governance Compatibility:** 100% governable.

---

### CLASS B Route 2: Upstream Norwegian METAR Stations (ENDU Bardufoss, ENAN Andøya, ENTC Tromsø)

- **Exact Information Source:** IEM ASOS / WMO METAR reports from ENDU (78km NNW), ENAN (140km WNW), ENTC (146km NNW).
- **Physical Information Provided:** Upstream cloud base height (feet AGL) and cloud cover layers (oktas) west/north of Scandes.
- **Why Stage 8.1 Does Not Contain It:** Independent observational cloud state prior to $t_0$.
- **Expected Causal Timestamp:** $23:50\text{ UTC}$ ($t_0 - 10\text{ min}$).
- **2024 Coverage Status:** Confirmed present in IEM archive.
- **Spatial Relationship to Nuolja:** 78–146 km distant, separated by $>1500\text{ m}$ Scandes mountain ridge.
- **Likely Feature Representation:** `endu_cloud_base_m`, `endu_cloud_cover_okta`.
- **Major Leakage Risks:** None.
- **EVEN Governance Compatibility:** 100% governable.
- **Reason for CLASS B:** Following the ENEV rejection ($\Delta\text{MAE} = +0.1989\text{ W/m}^2$, 86km WNW), point METAR observations on the Norwegian coastal side undergo severe mountain transformation (orographic uplift, Foehn drying) before reaching Nuolja. Spatial coupling is highly uncertain.

---

### CLASS B Route 3: MEPS Data Assimilation Analysis Increments ($\Delta q_{\text{assim}}, \Delta T_{\text{assim}}$)

- **Exact Information Source:** MET Norway MEPS 00Z Analysis minus 18Z Forecast background at $t_0$.
- **Physical Information Provided:** Direct magnitude of observational corrections applied to initial NWP state at $t_0$.
- **Why Stage 8.1 Does Not Contain It:** Stage 8.1 uses uncorrected D-1 18Z forecast profiles.
- **Expected Causal Timestamp:** $t_0 = 00:00\text{ UTC}$.
- **2024 Coverage Status:** Data archive availability for raw analysis files requires verification.
- **Spatial Relationship to Nuolja:** Direct local grid cell.
- **Likely Feature Representation:** $\Delta T_{700, \text{assim}}$, $\Delta q_{700, \text{assim}}$.
- **Major Leakage Risks:** Requires verifying that analysis files do not contain post-$t_0$ observations.
- **EVEN Governance Compatibility:** Governable if data exists.

---

## 5. Quantitative Ranking Matrix (Scientific Value × Feasibility × Independence)

| Rank | Route Name | Scientific Value (1–10) | Causal Feasibility (1–10) | Independence (1–10) | Total Score Product | Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Faithful Scandes Orographic Flow Regime ($Fr, U_\perp$)** | 10 | 10 | 9 | **900** | **CLASS A** |
| **2** | **Real SWEPOS GNSS Tropospheric Delay (`ABIS` ZTD)** | 9 | 8 | 10 | **720** | **CLASS A** |
| **3** | **Causal Inter-Run MEPS Condensate Tendency ($\Delta\text{LWP}_{\text{run}}$)** | 7 | 10 | 5 | **350** | **CLASS B** |
| **4** | **Upstream Norwegian METARs (ENDU / ENAN / ENTC)** | 6 | 9 | 9 | **486** (Coupling Penalty $\to$ **291.6**) | **CLASS B** |
| **5** | **MEPS Data Assimilation Increments ($\Delta q_{\text{assim}}$)** | 6 | 5 | 7 | **210** | **CLASS B** |

---

## 6. Final Recommendation

The **SINGLE STRONGEST REMAINING RESEARCH ROUTE** in POLARIS Stage 8 is:

> **FAITHFUL SCANDES OROGRAPHIC FLOW-REGIME FORMULATION (Continuous $N$ + $U_\perp$ + $Fr$)**

### Rationale for Selection:
1. **Physical Materiality:** Mount Nuolja ($1,169\text{ m ASL}$) sits directly in the Scandes mountain barrier ($>1,500\text{ m}$). Orographic flow-regime transitions between low-level flow blocking ($Fr < 1.0$, valley stratus trapping) and forced mountain overtopping ($Fr \ge 1.0$, wave cloudiness) govern local cloud optical depth.
2. **Causal & Benchmark Feasibility:** 100% causally available from MEPS vertical profile forecasts ($P_{\text{sfc}} \to 700\text{ hPa}$) and static 30m DEM terrain data across all 347 benchmark origins.
3. **Scientific Fidelity:** Replaces the approximate 2-point shortcut evaluated in Stage 8.24 with the continuous layer-integrated Brunt–Väisälä buoyancy frequency $N = \sqrt{\frac{g}{\theta_v}\frac{\partial\theta_v}{\partial z}}$ and barrier-normal wind projection $U_\perp$.
4. **Governed Protocol:** Can be evaluated cleanly under the locked 5-fold EVEN CV protocol without modifying the Stage 8.1 control or accessing ODD.

---

*Report generated under POLARIS Stage 8 Governance Guidelines on 2026-09-13.*
