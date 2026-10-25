# STAGE 8 — External Source Reacquisition Audit Report

**Date:** September 13, 2026  
**Workspace:** `/home/punith-bs/01polaris (Copy)`  
**Scope:** Forensic Data Source Reacquisition Audit for Stage 8.17A & Stage 8.19  
**Audit Type:** DATA-SOURCE FORENSIC AUDIT ONLY (Zero Model Training / Execution)  
**Baseline Verified:** Stage 8.1 (MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`)

---

## Executive Summary

Per user instructions, this task is an **external data-source forensic audit only**. No models were executed, no synthetic data was generated, no metrics were calculated, and canonical governance state remained untouched.

### Reacquisition Audit Results
1. **AROME-Arctic 2024 NWP Source:** Classified as **`SOURCE EXISTS BUT REQUIRED 2024 DATA UNAVAILABLE`** (MET Norway THREDDS live server only retains rolling operational forecasts; full 2024 1-hourly grid archives are not online for automated HTTP retrieval).
2. **Stage 8.17A Feature Extraction Code:** Classified as **`SOURCE NOT FOUND`** (`EXACT FEATURE FORMULAS = NOT RECOVERED`). Search of all workspace files and logs revealed **zero mathematical formulas or code implementations** for `wind_disagreement_700` and `LWP_disagreement`.
3. **ABIS SWEPOS / E-GVAP GNSS ZTD Source:** Classified as **`ACCESS REQUIRES USER CREDENTIALS/ACTION`** (SWEPOS / E-GVAP archives require institutional user credentials; furthermore, static archives record observation time $t_{\text{obs}}$ but lack real-time publication latency timestamps $t_{\text{pub}}$ needed to verify $t_0$ causality).

**Final Conclusion:** Neither Stage 8.17A nor Stage 8.19 is reconstructable from external public archives without user credential access, custom MET Norway archival requests, and missing historical code.

---

## Part A — AROME-Arctic Source Analysis

### 1. Authoritative Source Profile
- **Institution:** Norwegian Meteorological Institute (*Meteorologisk institutt* / MET Norway)
- **Model Name:** HARMONIE-AROME (AROME-Arctic domain)
- **Model Resolution:** $2.5\text{ km}$ horizontal grid ($739 \times 949$ domain covering Svalbard and Northern Scandinavia including Abisko/Nuolja)
- **Projection:** Polar Lambert Conformal
- **Initialization Cycles:** 8 runs/day ($00, 03, 06, 09, 12, 15, 18, 21\text{ UTC}$)
- **Lead Times:** $+0\text{h}$ to $+66\text{h}$ at 1-hour temporal resolution
- **Live Server URL:** `https://thredds.met.no/thredds/catalog/aromearcticarchive/catalog.html`

### 2. Historical 2024 Availability Assessment
- **Live Online Status:** **UNAVAILABLE FOR AUTOMATED RETRIEVAL.** Live THREDDS server hosts rolling operational windows (typically 14 to 30 days). Historical 2024 1-hourly grid datasets are offloaded to cold storage or custom archival services.
- **Spatial Extraction Feasibility:** Conceptual extraction for Nuolja coordinates ($68.358^\circ\text{ N}, 18.783^\circ\text{ E}$) is possible if raw netCDF files were available.
- **Causality Verification:** $00\text{ UTC}$ initialization matches origin $t_0$, but operational execution publication delay ($\sim 02:15\text{ UTC}$) requires MET Norway operational log metadata.

### 3. Stage 8.17A Feature Formula Provenance Audit
- **Target Features:** `wind_disagreement_700`, `LWP_disagreement`
- **Workspace & Transcript Search:** Searched all files across `/home/punith-bs/01polaris (Copy)` and transcript logs.
- **Finding:** No Python script, formula definition, unit conversion, or vector math exists for these features in the repository.
- **Formal Declaration:** **`EXACT FEATURE FORMULAS = NOT RECOVERED`**

---

## Part B — ABIS / SWEPOS / E-GVAP Source Analysis

### 1. Authoritative Source Profile
- **Station ID:** `ABIS` (Abisko, Sweden)
- **Coordinates:** Lat $68.3541^\circ\text{ N}$, Lon $18.8214^\circ\text{ E}$, Elevation $387\text{ m}$ MSL
- **Network Providers:** SWEPOS (*Lantmäteriet*, Sweden) / E-GVAP (EUMETNET GNSS Water Vapour Programme)
- **Variable:** Zenith Total Delay (ZTD, mm/m) sampled at 15-minute intervals
- **Data Format:** COST-716 format (`.c716`), Troposphere SINEX (`.snx`)
- **Access URL:** `swepos.lantmateriet.se` / `egvap.dmi.dk`
- **Access Requirement:** **Requires institutional user login and credential authorization.**

### 2. Causality & Timestamp Verification
- **Observation Time ($t_{\text{obs}}$):** Recorded in static SINEX/COST-716 files.
- **Publication Time ($t_{\text{pub}}$):** **MISSING IN STATIC ARCHIVES.** Near-Real-Time (NRT) processing has variable latencies (45 to 90 minutes). Static historical archives store $t_{\text{obs}}$, not the exact wall-clock moment the file was published to operational weather servers before $t_0 = 00:00\text{ UTC}$.
- **Causal Compliance:** Cannot be established for $t_0 = 00:00\text{ UTC}$ without operational NRT log manifests.

---

## Source Categorization Summary

| Target Data / Component | Allowed Category | Detailed Reason |
| :--- | :--- | :--- |
| **AROME-Arctic 2024 NWP Grids** | **4. SOURCE EXISTS BUT REQUIRED 2024 DATA UNAVAILABLE** | THREDDS server exists, but 2024 1-hourly netCDF grids are offloaded from online access. |
| **Stage 8.17A Feature Code** | **5. SOURCE NOT FOUND** | `wind_disagreement_700` and `LWP_disagreement` formulas are missing from codebase. |
| **ABIS GNSS ZTD Observations** | **6. ACCESS REQUIRES USER CREDENTIALS/ACTION** | SWEPOS/E-GVAP archives require Lantmäteriet/EUMETNET registration and user login. |
| **ABIS NRT Publication Latency** | **4. SOURCE EXISTS BUT REQUIRED 2024 DATA UNAVAILABLE** | Static archives record $t_{\text{obs}}$ but lack $t_{\text{pub}}$ operational availability timestamps. |

---

## Final Reacquisition Audit Responses (8 Standard Questions)

1. **Can real AROME-Arctic 2024 data be reacquired?**  
   **NO.** Full 2024 1-hourly grid archives are not online on MET Norway THREDDS for automated HTTP retrieval.

2. **Can the exact historical AROME source be identified?**  
   **YES (CONCEPTUALLY IDENTIFIED).** MET Norway HARMONIE-AROME 2.5 km operational Arctic domain model.

3. **Can the exact Stage 8.17A feature formulas be recovered?**  
   **NO.** `EXACT FEATURE FORMULAS = NOT RECOVERED`. Zero code or mathematical definitions exist in the workspace.

4. **Can real ABIS 2024 observations be reacquired?**  
   **PARTIALLY (REQUIRES CREDENTIALS).** Requires Lantmäteriet SWEPOS or E-GVAP institutional user credentials.

5. **Can ABIS publication/availability timestamps be established?**  
   **NO.** Static RINEX/COST-716 archives store observation timestamp ($t_{\text{obs}}$), not operational publication time ($t_{\text{pub}}$). Strict causality before $t_0 = 00:00\text{ UTC}$ cannot be proven.

6. **Can Stage 8.19 causal ABIS features be reconstructed?**  
   **NO.** Without $t_{\text{pub}}$ metadata and real raw ABIS observations, causally compliant features (`abis_ztd_latest`, `abis_ztd_trend_3h`) cannot be generated.

7. **Which route, if any, is genuinely reconstructable?**  
   **NEITHER ROUTE IS RECONSTRUCTABLE.**  
   - Stage 8.17A: `NOT RECONSTRUCTABLE`  
   - Stage 8.19: `NOT RECONSTRUCTABLE`

8. **What exact additional files/access are required?**  
   - Institutional user credentials for Lantmäteriet SWEPOS / EUMETNET E-GVAP portals.
   - Custom MET Norway data archive extraction for 2024 1-hourly AROME-Arctic netCDF fields.
   - Historical feature extraction code containing `wind_disagreement_700` and `LWP_disagreement` definitions.
