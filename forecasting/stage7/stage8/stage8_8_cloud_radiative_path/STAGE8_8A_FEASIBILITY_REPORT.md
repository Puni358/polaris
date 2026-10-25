# POLARIS STAGE 8.8A — CLOUD RADIATIVE-PATH GEOMETRY FEASIBILITY & NOVELTY REPORT

**Stage:** STAGE 8.8A CLOUD RADIATIVE-PATH GEOMETRY FEASIBILITY & NOVELTY AUDIT  
**Date:** September 12, 2026  
**Status:** FEASIBILITY & SCIENTIFIC NOVELTY AUDIT COMPLETE — **DECISION: PASS**  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, Elev: $702\text{ m a.s.l.}$)  
**Official Operational Champion:** Stage 8.1 700 hPa Steering Wind Model (FROZEN & UNTOUCHED)  
**Held-out ODD Champion Benchmark:** MAE $= 36.188657\text{ W/m}^2$, nMAE $= 28.0688\%$, RMSE $= 54.912301\text{ W/m}^2$  

---

## Executive Summary & Official Decision

> [!IMPORTANT]
> **OFFICIAL STAGE 8.8A AUDIT DECISION: PASS**
> 
> Cloud Radiative-Path Geometry (`cloud_base_altitude`, `cloud_top_altitude`, `cloud_geometric_thickness`) is **100% available and causally compliant** across all 347 forecast origins ($8,328$ total forecast hours) in the D-1 18Z MEPS deterministic archive (`meps_det_sfc`).
> 
> An exact inventory of the frozen 37 Stage 8.1 features confirms that **NO existing feature contains explicit vertical cloud height or depth**. The proposed candidate features supply **genuinely novel, independent geometric path information** that cannot be derived from column-integrated liquid/ice water path ($LWP, IWP$) or 2D cloud fraction alone.
> 
> Clear-sky sentinel values ($9.96921 \times 10^{36}$) are handled cleanly via prospective zero-masking guardrails. The candidate route receives a **PASS** decision to proceed to a Stage 8.8B forecasting experiment upon explicit user authorization.
> 
> **STRICT GOVERNANCE:** Stage 8.8B forecasting experiment was **NOT** run. No models were trained, no cross-validation was executed, no ODD targets were read, no ODD predictions were generated, and no hyperparameters were tuned.

---

## 1. Task 1 — Exact Current Feature Inventory

The frozen Stage 8.1 operational champion utilizes exactly **37 features**. An exhaustive code and manifest inspection confirms that **0 of the 37 features contain explicit vertical cloud geometry**:

| Feature Group | Count | Features Included | Contains Cloud Geometry? |
| :--- | :---: | :--- | :---: |
| **Stage 4 Base** | 28 | `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h` | **NO** |
| **Stage 6.6 Microphysics** | 3 | `lwp_latest`, `iwp_latest`, `lwp_x_cloud` | **NO** |
| **Stage 7.5 Terrain** | 4 | `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted` | **NO** |
| **Stage 8.1 Steering Wind** | 2 | `u700`, `v700` | **NO** |
| **TOTAL** | **37** | **Frozen Champion Feature Set** | **0 / 37** |

*The full itemized 37-feature manifest is documented in `STAGE8_8A_EXISTING_FEATURE_INVENTORY.csv`.*

---

## 2. Task 2 — Historical Cloud Information Audit

Inspection of historical stage artifacts confirms that cloud vertical geometry has **never been evaluated in POLARIS**:

| Stage | Candidate Information | Added to Model? | EVEN CV Result | Decision | Primary Rejection / Outcome Reason |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Stage 6.6** | Column $LWP, IWP$ mass | YES | $-2.08\text{ W/m}^2$ (ODD) | **ACCEPTED** | Crowned champion. Integrated water mass attenuation. |
| **Stage 7.4** | 13 pressure-level $LWP, IWP$ splits | NO | $+0.0063\text{ W/m}^2$ | **REJECTED** | Fixed pressure level interpolation noise without geometric boundaries. |
| **Stage 7.5** | Copernicus DEM horizon mask | YES | $-0.4455\text{ W/m}^2$ | **ACCEPTED** | Topographic direct beam mountain shading. |
| **Stage 8.0** | Model-level & surface cloud audit | NO | N/A | **AUDIT** | Model levels disproved at 18Z. Surface `cloud_base` & `cloud_top` proved 100% available. |
| **Stage 8.5** | Spatial cloud advection ($5 \times 5$ grid) | NO | $-0.1851\text{ W/m}^2$ | **REJECTED** | 2D horizontal phase/location errors in NWP grid. |
| **Stage 8.6** | CAMS Aerosol Optical Depth | NO | N/A | **REJECTED** | Publication delay violated D-1 18Z causality; aerosol variance near zero. |
| **Stage 8.7** | DNI Proxy / Two-Head Architecture | NO | N/A | **REJECTED** | Target ambiguity (no measured DNI); degraded GHI. |

*Detailed historical analysis is provided in `STAGE8_8A_CLOUD_HISTORY_AUDIT.md`.*

---

## 3. Task 3 & Task 11 — Data Availability & Strict Causality

Audit of the MEPS forecast archive across all 347 forecast origins and 8,328 forecast hours:

* **Variable Names:** `cloud_base_altitude`, `cloud_top_altitude` in MEPS product `meps_det_sfc`.
* **Units & Reference:** Meters ($m$) above sea level.
* **Coverage:** 347 / 347 origins (100.0%) and 8,328 / 8,328 forecast hours (100.0%).
* **Missing Count:** 0 missing steps.
* **Sentinel Value Behavior:** Clear-sky hours populate NetCDF fill value $9.96921 \times 10^{36}$. In the 2024 Nuolja dataset, 1,782 forecast hours (~21.4%) are clear sky (`fc_cloud_cover == 0`), where sentinel values occur.
* **Invalid Count:** 0 (excluding clear sky sentinels). All non-sentinel values satisfy $0 \le z_{\text{base}} \le z_{\text{top}} \le 12,000\text{ m}$.
* **Strict Causality:** All features are extracted from the MEPS D-1 18Z deterministic run ($t_{\text{ref}} = \text{D-1 18:00 UTC}$). Lead times range from $h=1$ ($t_0 - t_{\text{ref}} = 6\text{h}$) to $h=24$ ($t_0 + 23\text{h} - t_{\text{ref}} = 29\text{h}$). Causality pass rate: **100% (347/347 origins)**.

*Itemized data audit manifests are stored in `STAGE8_8A_CLOUD_GEOMETRY_FEASIBILITY.csv` and `STAGE8_8A_CAUSALITY_AUDIT.csv`.*

---

## 4. Task 4 & Task 6 — Physical Semantics & Multi-Layer Limitations

1. **Geometric Depth vs Optical Depth:** Geometric thickness $\Delta z = z_{\text{top}} - z_{\text{base}}$ is **NOT equivalent** to optical path length $\tau$. $LWP$ governs cloud optical mass density, whereas $\Delta z$ governs physical spatial depth and slant path length $s = \Delta z / \sin(\theta_{\text{elev}})$.
2. **Multi-Layer Collapse Limitation:** In `meps_det_sfc`, `cloud_base_altitude` reports the lowest base and `cloud_top_altitude` reports the highest top in the column. In multi-layered cloud systems, intermediate clear-sky gaps are collapsed into a single column envelope depth. Reconstructing discrete sub-layers is impossible without model-level data (`meps_det_ml`), which was disproved at 18Z in Stage 8.0.

*Full physical semantics analysis is detailed in `STAGE8_8A_PHYSICAL_SEMANTICS.md`.*

---

## 5. Task 5, 7, 8, 9 — Novelty, Solar Ray Geometry, & Redundancy

1. **Genuine Novelty:** `cloud_base_altitude`, `cloud_top_altitude`, and `cloud_geometric_thickness` supply independent vertical geometric boundaries not present in $LWP$, $IWP$, or 2D cloud fraction.
2. **Solar Ray Geometry:** Gradient boosted decision trees (`HistGradientBoostingRegressor`, depth=4) naturally partition $(\Delta z, \theta_{\text{elev}}, LWP)$ feature space to capture slant path scattering without requiring hardcoded attenuation equations.
3. **Terrain Redundancy Check:** **LOW REDUNDANCY**. Terrain features model solid mountain shading; cloud geometry features model atmospheric hydrometeor scattering.
4. **Stage 8.5 Comparison:** Stage 8.5 tested 2D horizontal advection; Stage 8.8A tests 1D vertical column depth. The error mechanisms are physically distinct.

*Detailed novelty analysis is provided in `STAGE8_8A_NOVELTY_ANALYSIS.md`.*

---

## 6. Task 10 — Minimal Prospective Candidate Definition

The prospective minimal candidate feature set for Stage 8.8B consists of **3 new features**:

1. `cloud_base_altitude_causal`: Cloud base altitude ($m$), zero-masked during clear-sky / sentinel hours.
2. `cloud_top_altitude_causal`: Cloud top altitude ($m$), zero-masked during clear-sky / sentinel hours.
3. `cloud_geometric_thickness`: Column envelope depth $\max(0.0, z_{\text{top}} - z_{\text{base}})$, zero-masked during clear-sky / sentinel hours.

Combining these 3 candidate features with the 37 Stage 8.1 features yields a **40-feature candidate model** for Stage 8.8B.

---

## 7. Task 12 & Task 13 — Polar Conditions & Predeclared Failure Modes

* **Polar Night Behavior:** During polar night ($\theta_{\text{elev}} \le 0^\circ$), clear-sky GHI is zero, and night-zero forcing sets predictions to $0.0\text{ W/m}^2$. MEPS cloud geometry features remain 100% defined in data files but have zero impact during night.
* **Predeclared Failure Modes:**
  1. Multi-layer clear-air gap collapse inflating geometric depth.
  2. Geometrically thick but optically thin clouds (low condensate density).
  3. Sub-grid cloud diagnostic spatial displacement in complex topography.
  4. Decision tree feature saturation with existing $LWP$ and cloud fraction.

---

## 8. Task 15 — Predeclared Stage 8.8B Experiment Plan (PROPOSED ONLY)

If explicitly authorized to proceed to Stage 8.8B, the experiment will strictly follow this protocol:

```
Candidate Model: 40 Features (37 Stage 8.1 + 3 Cloud Geometry)
Model Architecture: HistGradientBoostingRegressor (FROZEN)
  - loss: 'absolute_error'
  - max_depth: 4
  - min_samples_leaf: 30
  - l2_regularization: 10.0
  - random_state: 42

Evaluation Protocol: Locked 5-fold EVEN forward-chaining CV
Control Baseline: Stage 8.1 Champion (Exact reproduction check required)

Predeclared Acceptance Gates:
  - Gate 1: Aggregate Daytime MAE reduction >= 0.20 W/m2 vs Control
  - Gate 2: Multi-fold improvement consistency (>= 4 of 5 folds improve)
  - Gate 3: Max fold degradation limit <= +0.15 W/m2
  - Gate 4: nMAE & RMSE consistency (Candidate nMAE <= Control, RMSE <= Control)
  - Gate 5: Absolute D-1 18Z causality verification (100% pass)
  - Gate 6: Control reproduction match (MAE = 35.2708 W/m2)
```

---

## 9. Firewall Verification Audit

At completion of Stage 8.8A:
* **ODD target reads:** 0
* **ODD predictions generated:** 0
* **ODD metrics calculated:** 0
* **ODD hyperparameter tuning:** 0
* **Stage 8.1 champion modified:** 0 (Frozen)
* **POLARIS_MASTER_HANDOFF.md modified:** 0
* **Historical Stage 6.6/7.4/7.5/8.0/8.1/8.5/8.6/8.7 artifacts modified:** 0

---

## Conclusion & Action Item

Stage 8.8A is complete. Decision is **PASS**.  
**STOP.** Do not train. Do not run CV. Wait for explicit user authorization before initiating Stage 8.8B.
