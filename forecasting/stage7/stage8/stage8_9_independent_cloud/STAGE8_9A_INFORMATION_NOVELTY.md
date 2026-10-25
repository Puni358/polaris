# STAGE 8.9A — INFORMATION NOVELTY AUDIT

**Project:** POLARIS SIH Forecasting  
**Stage:** STAGE 8.9A INDEPENDENT CLOUD-STATE / CLOUD-MOTION AUDIT  
**Baseline Inventory:** Stage 8.1 Champion Feature Set (37 Features)  
**Date:** September 12, 2026  

---

## 1. Context & Baseline Feature Inventory (Stage 8.1 Champion)

The current official frozen champion is the **Stage 8.1 700 hPa Steering Wind Model** (ODD Daytime MAE = $36.188657\text{ W/m}^2$, nMAE = $28.0688\%$, RMSE = $54.912301\text{ W/m}^2$).

The Stage 8.1 champion utilizes a 37-feature inventory categorized into physical information channels:

1. **Autoregressive Target History ($t-23 \dots t_0$):**
   - 24 hourly values of observed SITES Nuolja `SW_IN` ($W/m^2$).
   - Encodes historical atmospheric transmissivity, cloud shading, and diurnal decay prior to $t_0$.

2. **Deterministic Solar Geometry & Clearsky Reference ($t_0 \dots t_0+24$):**
   - Solar Zenith Angle ($SZA$), Solar Azimuth Angle ($SAA$), Clearsky GHI ($GHI_{\text{clearsky}}$ via Ineichen/Perez model).

3. **MEPS NWP Cloud Moisture & Microphysics ($t_0 \dots t_0+24$):**
   - Total Cloud Cover (`TCC`), Low Cloud Cover (`LCC`), Medium Cloud Cover (`MCC`), High Cloud Cover (`HCC`).
   - Liquid Water Path (`LWP`), Ice Water Path (`IWP`) (integrated column condensate).

4. **Terrain & Horizon Shading Features (Stage 7.5):**
   - High-resolution $30\text{ m}$ DEM terrain horizon obstruction angles ($360^\circ$ azimuth profile) masking direct solar beam when $SZA > \text{Horizon}(\phi_{az})$.

5. **Free-Atmosphere Advection & Steering Winds (Stage 8.1):**
   - $700\text{ hPa}$ Geostrophic Wind Components: $U_{700}$ (zonal steering wind, $m/s$) and $V_{700}$ (meridional steering wind, $m/s$) extracted from MEPS model pressure levels.

---

## 2. Information Novelty Criterion

To be classified as **genuinely information-novel**, a candidate data source must observe a physical state variable that:
1. Is **physically unrepresented** or **severely mismodeled** by the existing 37-feature inventory.
2. Cannot be linearly or non-linearly reconstructed from combinations of $\{SW\_IN_{\text{hist}}, GHI_{\text{clear}}, TCC, LWP, IWP, U_{700}, V_{700}, \text{Horizon}\}$.
3. Provides predictive signal for the future forecast horizon ($H1 \dots H24$) at issuance $t_0$.

---

## 3. Detailed Novelty Audit by Candidate Source

### A. Candidate Source: Ground-Based Sky Imagers / All-Sky Cameras (Nuolja / Abisko)
- **Observed Physical State:** Hemispherical cloud fraction, cloud type (cumulus/stratus/cirrus), cloud-edge position, optical opacity.
- **Redundancy Analysis against Stage 8.1:**
  - Past sky camera imagery at $t \le t_0$ provides local cloud fraction at $t_0$.
  - However, past 24-hour target history ($SW\_IN_{t-23 \dots t_0}$) and SITES direct/diffuse measurements already measure the exact integrated radiometric effect of ground cloudiness up to $t_0$.
  - Sky camera observations at $t_0$ provide no direct information about cloud evolution at forecast horizons $H6 \dots H24$ beyond what is advected by MEPS NWP forecast fields.
- **Novelty Verdict:** **INSUFFICIENT NOVELTY** (Redundant with $SW\_IN$ target history at $t \le t_0$; provides no future horizon trajectory).

---

### B. Candidate Source: Satellite Cloud Microphysics (VIIRS / NWC SAF PPS CMIC)
- **Observed Physical State:** Satellite-retrieved Cloud Optical Thickness ($\tau_{cloud}$), Cloud Effective Radius ($r_{eff}$), Cloud Top Temperature ($CTT$), Cloud Top Height ($CTH$), Cloud Phase (Liquid / Ice / Mixed).
- **Redundancy Analysis against Stage 8.1:**
  - **Cloud Optical Thickness ($\tau_{cloud}$):** MEPS NWP predicts Liquid Water Path ($LWP$) and Ice Water Path ($IWP$). Physical optical thickness is related via:

    $$\tau_{cloud} \approx \frac{3}{2} \frac{LWP}{\rho_w r_{eff}} + \frac{3}{2} \frac{IWP}{\rho_i r_{ice}}$$

  - **Observed vs Predicted Discrepancy:** VIIRS/NWC SAF provides *observed* $\tau_{cloud}$ at $t \le t_0$, whereas MEPS provides *forecasted* $LWP/IWP$ for $H1 \dots H24$.
  - **Temporal Decay of Initial Observed State:** An observed satellite cloud state snapshot at $t_0 - 1.5\text{ h}$ provides initial state correction for $H1 \dots H2$. However, cloud advection across Northern Lapland ($U_{700} \approx 15\text{ m/s} \approx 54\text{ km/h}$) clears the initial $25\text{ km}$ satellite scene within $30\text{ minutes}$. By horizon $H3 \dots H24$, the forecast is entirely governed by incoming advected airmasses.
- **Novelty Verdict:** **MODERATE NOVELTY AT $t_0$, LOW NOVELTY FOR HORIZONS $H3 \dots H24$**.

---

### C. Candidate Source: Satellite-Derived Cloud Motion Vectors (AMVs / CMVs) & Optical Flow
- **Observed Physical State:** Feature tracking of cloud elements in consecutive satellite swaths to yield 2D displacement vectors $(u_{cmv}, v_{cmv})$ and cloud arrival/departure timing.
- **Redundancy & Physical Audit:**
  - *Audit Note:* Satellite AMVs and optical flow products may provide information related to atmospheric steering flow, but no POLARIS-specific empirical redundancy test was performed in Stage 8.9A.
  - However, Stage 8.1 already incorporates MEPS $U_{700}$ and $V_{700}$ steering winds from NWP model pressure levels.
  - Furthermore, Stage 8.5 tested MEPS spatial cloud advection (advecting cloud fields along steering wind vectors) and **FAILED** to improve over the scalar Stage 8.1 champion.
  - Advecting an observed 2D satellite cloud field faces the exact same physical bottleneck as Stage 8.5: mountain clouds over the Scandes ridges undergo continuous localized forced condensation (orographic uplift) and evaporation (lee-side drying). 2D translational advection of a frozen cloud field assumes non-divergent, conservative cloud mass, which is physically false in mountain terrain.
- **Novelty Verdict:** **INSUFFICIENT NOVELTY** (Invalidated by Stage 8.5 mountain advection physics; publication latency $t_{\text{pub}} > t_0$ precludes operational use).

---

### D. Candidate Source: Kiruna Airport Ceilometer & METAR (ESNQ)
- **Observed Physical State:** Cloud base height (CBH) and cloud cover (oktas) at Kiruna Airport ($88.4\text{ km}$ ESE).
- **Redundancy Analysis against Stage 8.1:**
  - Kiruna cloud observations reflect interior plateau weather. Stage 8.8 already evaluated MEPS Cloud Base Height (`CBH`), Cloud Top Height (`CTH`), and Cloud Thickness (`CTH - CBH`) at Nuolja and was **REJECTED**.
  - A distant point observation $88.4\text{ km}$ away adds no information beyond MEPS gridded cloud fields.
- **Novelty Verdict:** **INSUFFICIENT NOVELTY** (Redundant with MEPS cloud profile; spatially non-representative).

---

## 4. Comprehensive Information Novelty Summary Table

| Candidate Source | Physical Variable Observed | Primary Baseline Equivalent in Stage 8.1 | Physical Discrepancy / New Signal | Horizon Relevance ($H1 \dots H24$) | Information Novelty Rating |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **All-Sky Camera (Nuolja)** | Local cloud fraction / opacity | Past $SW\_IN$ history ($t-23 \dots t_0$) | Instantaneous visual cloud boundaries at $t_0$ | Rapid decay ($H1$ only) | **INSUFFICIENT NOVELTY** |
| **VIIRS / NWC SAF CMIC** | Observed Cloud Optical Thickness ($\tau$) | MEPS $LWP / IWP$ forecasts | Realized optical depth vs model condensate | $H1 \dots H2$ only | **MODERATE (Killed by Causality & Night)** |
| **Satellite Cloud Motion (AMV)** | 2D Cloud displacement vector | MEPS $U_{700} / V_{700}$ steering winds | Tracked cloud top movement (No empirical pairing test executed) | High overlap with $U_{700}/V_{700}$ | **INSUFFICIENT NOVELTY (Stage 8.5 Fail)** |
| **Optical Flow Sequences** | Satellite image advection vector | MEPS $U_{700} / V_{700}$ + Stage 8.5 Advection | Realized image translation | Invalid in mountain terrain | **INSUFFICIENT NOVELTY (Stage 8.5 Fail)** |
| **Kiruna Ceilometer (ESNQ)** | Distant cloud base height ($88.4\text{ km}$) | MEPS gridded `CBH` (Stage 8.8) | Distant plateau cloud base | Zero correlation with Nuolja | **INSUFFICIENT NOVELTY** |

---

## 5. Summary Conclusion on Information Novelty

Stage 8.9A did not identify a verified independent cloud-state/cloud-motion data source that simultaneously met the required causal-availability, empirical-coverage, spatial-representativeness, and information-novelty criteria.

