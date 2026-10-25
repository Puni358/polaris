# POLARIS Stage 8.8A — Historical Cloud-Information Audit

**Stage:** STAGE 8.8A CLOUD RADIATIVE-PATH GEOMETRY FEASIBILITY & NOVELTY AUDIT  
**Date:** September 12, 2026  
**Status:** AUTHORITATIVE HISTORICAL AUDIT COMPLETE  

---

## Executive Overview

This document presents an authoritative audit of all cloud-related information, variables, derived features, physical hypotheses, cross-validation results, and rejection mechanisms tested across POLARIS historical stages: **Stage 6.6**, **Stage 7.4**, **Stage 7.5**, **Stage 8.0**, **Stage 8.5**, **Stage 8.6**, and **Stage 8.7**.

Per the **Authoritative History Rule**, this audit is derived directly from underlying stage artifacts and manifests rather than stale selection memos. None of these historical artifacts have been altered.

---

## Historical Route Inventory

### 1. Stage 6.6 — MEPS Cloud Microphysics (LWP & IWP)
* **Variables Used:** `mass_fraction_of_cloud_condensed_water_in_air`, `mass_fraction_of_cloud_ice_in_air` from MEPS deterministic forecast.
* **Derived Features:** `lwp_latest` (column-integrated liquid water path), `iwp_latest` (column-integrated ice water path), `lwp_x_cloud` (`lwp_latest * cloud_frac`).
* **Physical Hypothesis:** Column-integrated liquid water and ice mass govern cloud optical depth ($\tau \approx \frac{3}{2 \rho_w r_{\text{eff}}} \text{LWP}$), providing direct physical optical attenuation beyond 2D cloud cover fraction.
* **Added to Model:** YES. Added to Stage 5.2 baseline to form Stage 6.6 champion (31 features).
* **EVEN CV Result:** Daytime MAE $= 38.2806\text{ W/m}^2$, nMAE $= 40.3918\%$, RMSE $= 60.7509\text{ W/m}^2$.
* **Held-Out ODD Result:** MAE reduced from $39.0848\text{ W/m}^2$ (Stage 5.2) to **$37.0059\text{ W/m}^2$** ($\Delta\text{MAE} = -2.0789\text{ W/m}^2$, $-1.61\text{ pp}$ nMAE). Bootstrap 95% CI: $[-2.81, -1.34]\text{ W/m}^2$.
* **Gate Outcome:** **PASSED / CROWNED OPERATIONAL CHAMPION**.
* **Rejection Reason:** N/A (Accepted).

---

### 2. Stage 7.4 — MEPS Vertical Cloud Structure (13 Pressure Levels)
* **Variables Used:** 13 pressure-level cloud condensate fields (`q_l_pl`, `q_i_pl`), pressure-level cloud fractions (`cloud_frac_mid`, `cloud_frac_high`).
* **Derived Features:** `f_lwp_low`, `f_lwp_mid`, `f_lwp_high`, `p_centroid_lwp`, `p_centroid_iwp`, `dp_ice_liquid_centroid`, `cloud_frac_mid`, `cloud_frac_high` (8 features).
* **Physical Hypothesis:** Multi-level vertical partitioning (pressure centroids and low/mid/high splits) of liquid/ice condensate accounts for differential vertical scattering and absorption.
* **Added to Model:** TESTED as Candidate E1 (39 features: 31 Stage 6.6 + 8 vertical cloud features).
* **EVEN CV Result:** Candidate MAE $= 38.2869\text{ W/m}^2$ ($\Delta\text{MAE} = +0.0063\text{ W/m}^2$, slight degradation vs control).
* **Gate Outcome:** **REJECTED / FAILED ALL 5 ACCEPTANCE GATES**.
* **Rejection Reason:** Pressure-level vertical features introduced vertical interpolation noise and dimensional redundancy without explicit cloud boundary markers. Fold 4 degraded by $+1.0411\text{ W/m}^2$ (exceeding the $+0.15\text{ W/m}^2$ max fold degradation limit).

---

### 3. Stage 7.5 — Surface-Aware Terrain & Horizon Geometry
* **Variables Used:** Copernicus DEM 10m/30m high-resolution elevation data, solar azimuth, solar elevation.
* **Derived Features:** `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted` (4 features).
* **Physical Hypothesis:** Topographic mountain ridges surrounding Abisko valley block the direct solar beam at low elevation angles, causing step-function drops in surface GHI.
* **Added to Model:** YES. Candidate E1 (35 features: 31 Stage 6.6 + 4 terrain features).
* **EVEN CV Result:** Daytime MAE reduced from $38.2806\text{ W/m}^2$ to **$37.8351\text{ W/m}^2$** ($\Delta\text{MAE} = -0.4455\text{ W/m}^2$).
* **Held-Out ODD Result:** Daytime MAE $= 36.6136\text{ W/m}^2$ (nMAE: $28.3983\%$).
* **Gate Outcome:** **PASSED ALL 5 ACCEPTANCE GATES / ACCEPTED**.
* **Rejection Reason:** N/A (Accepted).

---

### 4. Stage 8.0 — MEPS Model-Level & Cloud Structure Feasibility Audit
* **Variables Used:** Data archive scan of MEPS `meps_det_sfc`, `meps_det_pl`, and `meps_det_ml`.
* **Derived Features:** None (Feasibility and causality audit stage).
* **Physical Hypothesis:** Determine if 65-level model-level data (`meps_det_ml`) and cloud base/top surface diagnostics are causally available at D-1 18Z.
* **Added to Model:** N/A.
* **EVEN CV Result:** N/A (Audit stage).
* **Gate Outcome:** AUDIT COMPLETE.
* **Rejection Reason:** 65-level model-level data (`meps_det_ml`) was DISPROVED for 18Z (0/347 origins available at 18Z; only 00Z exists). However, `cloud_base_altitude` and `cloud_top_altitude` in `meps_det_sfc` were PROVED 100% available in all 347 D-1 18Z forecast runs.

---

### 5. Stage 8.5 — MEPS Causal Spatial Cloud-Advection Experiment
* **Variables Used:** MEPS 2D grid total cloud cover ($5 \times 5$ grid domain centered on Nuolja), 700 hPa steering wind (`u700`, `v700`).
* **Derived Features:** Spatial domain cloud cover means, spatial gradients ($\nabla N$), advective tendencies ($u700 \cdot \nabla N + v700 \cdot \nabla N$), upstream cloud cover (14 features).
* **Physical Hypothesis:** Spatial cloud patterns advected by 700 hPa free-atmosphere wind provide pre-arrival cloud signals at SITES Nuolja.
* **Added to Model:** TESTED as Candidate (51 features: 37 Stage 8.1 + 14 spatial advection features).
* **EVEN CV Result:** Candidate MAE $= 35.0857\text{ W/m}^2$ ($\Delta\text{MAE} = -0.1851\text{ W/m}^2$), but $\Delta\text{nMAE} = +0.3772\text{ pp}$ (degraded).
* **Gate Outcome:** **REJECTED / FAILED EVEN GATES**.
* **Rejection Reason:** Failed Gate 1 (required $\Delta\text{MAE} \le -0.50\text{ W/m}^2$), failed Gate 2 (only 2/5 folds improved), and failed Gate 4 (nMAE degraded). Spatial cloud cover fields at 2.5 km resolution suffer from horizontal phase errors; advecting coarse NWP cloud fraction introduced phase noise that harmed multi-fold generalization.

---

### 6. Stage 8.6 — CAMS Atmospheric Composition & Aerosol Experiment
* **Variables Used:** Copernicus Atmosphere Monitoring Service (CAMS) global aerosol forecasts (AOD 550nm, organic carbon, dust, sulfate).
* **Derived Features:** Total AOD, species optical depths.
* **Added to Model:** REJECTED.
* **Rejection Reason:** CAMS 00Z forecast publication time (>06:00 UTC) violates D-1 18Z causality rule. Furthermore, pristine sub-Arctic background aerosol levels (AOD ~0.05) provided near-zero variance, failing all CV performance gates.

---

### 7. Stage 8.7 — DNI Two-Head Architecture
* **Variables Used:** MEPS DNI proxy / clear-sky DNI decomposition.
* **Derived Features:** Direct and diffuse irradiance prediction heads.
* **Added to Model:** REJECTED.
* **Rejection Reason:** Severe target ambiguity (no measured DNI target at Nuolja, only GHI measured); proxy-driven DNI head degraded GHI prediction accuracy.

---

## Authoritative Historical Matrix

| Stage | Candidate Information | Model Added? | EVEN CV $\Delta\text{MAE}$ | Gate Status | Primary Rejection / Decision Reason |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Stage 6.6** | Column LWP, IWP mass | YES | $-2.08\text{ W/m}^2$ (ODD) | **PASSED** | Crowned operational champion. Direct optical mass attenuation. |
| **Stage 7.4** | 13 pressure-level LWP/IWP & cloud frac | NO | $+0.0063\text{ W/m}^2$ | **REJECTED** | Failed all 5 gates. Vertical pressure level interpolation noise without geometric boundaries. |
| **Stage 7.5** | Copernicus DEM horizon elevation & shading | YES | $-0.4455\text{ W/m}^2$ | **PASSED** | Passed all 5 gates. Surface topographic direct beam obstruction. |
| **Stage 8.0** | Model-level (ML) & Surface cloud geometry audit | N/A | N/A | **AUDIT** | ML disproved at 18Z (0/347). Surface `cloud_base` & `cloud_top` proved 100% available at 18Z. |
| **Stage 8.5** | Spatial cloud advection ($5 \times 5$ domain + wind) | NO | $-0.1851\text{ W/m}^2$ | **REJECTED** | Failed Gates 1, 2, 4. Horizontal phase/location errors in 2D NWP cloud grid. |
| **Stage 8.6** | CAMS Aerosol Optical Depth (AOD) | NO | N/A | **REJECTED** | CAMS publication delay violates D-1 18Z causality; aerosol variance near zero. |
| **Stage 8.7** | DNI Proxy / Two-Head Architecture | NO | N/A | **REJECTED** | Target ambiguity (no measured DNI); degraded GHI accuracy. |

---

## Key Historical Insights for Stage 8.8A

1. **Microphysics vs Geometry:** Stage 6.6 proved that cloud condensed mass ($LWP$) is a powerful predictor. However, $LWP$ collapses vertical height and geometric thickness into a 2D scalar.
2. **Pressure Levels vs Cloud Boundaries:** Stage 7.4 failed because fixed pressure levels ($850, 700, 500\text{ hPa}$) introduce interpolation noise. In contrast, `cloud_base_altitude` and `cloud_top_altitude` provide explicit model-diagnosed physical boundaries of the cloud layer.
3. **Horizontal vs Vertical Geometry:** Stage 8.5 showed that horizontal spatial advection of 2D cloud cover introduces phase errors. Stage 8.8A tests vertical column geometry directly over the forecast target point.
