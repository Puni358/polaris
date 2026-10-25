# POLARIS Stage 6.2 — Experiment Specification Plan: Satellite Thermal-IR Observation (FINAL)

**Stage Title:** Stage 6.2 — Satellite Thermal-IR Cloud Observation & Feasibility Characterization  
**Date:** 2026-09-10  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Frozen Champion Reference:** Stage 5.2 Architecture A ($39.084821\text{ W/m}^2$ ODD Daytime MAE / $30.32\%\text{ nMAE}$)  
**Baseline EVEN-CV Reproducibility Target:** Stage 5.2 EVEN-CV MAE = $39.4236\text{ W/m}^2$

---

## 1. Executive Summary & Purpose

Stage 6.2 evaluates pre-origin thermal-IR satellite observations acquired over Nuolja to test whether actual observational cloud-mask information provides genuine incremental predictive signal beyond the frozen Stage 5.2 champion.

* **Why Thermal-IR?** At $68.36^\circ\text{N}$, Nuolja experiences total polar night from November through February ($SZA > 90^\circ$). Visible satellite channels ($0.6\mu\text{m}$) receive zero solar illumination during winter. Longwave thermal-IR channels ($10.8\mu\text{m}, 12.0\mu\text{m}$) emit continuous thermal radiation 24/7, providing all-season cloud-top temperature and optical depth indicators.
* **Scope Limits:** Strictly point/ROI pre-origin observational features ($t_{\text{acq}} \le t_0$). Zero cloud motion vector extraction. Zero post-origin or future satellite data. Held-out ODD test set remains 100% UNTOUCHED unless predefined EVEN-CV gates are passed.

---

## 2. Satellite Data Products & Sensor Inspections

### A. Archive Location & Products
* **Server:** MET Norway Remote Sensing Archive (`thredds.met.no`)
* **Archive Path:** `https://thredds.met.no/thredds/dodsC/remotesensingsatellite/polar-swath/2024/MM/DD/`
* **Access Protocol:** OPeNDAP (`dodsC`) / HTTPS `fileServer` NetCDF access.

### B. Sensor Channel Selection (First Candidate Experiment)
To maintain a clean, longwave thermal-IR experiment, Stage 6.2 focuses exclusively on longwave window channels (excluding MWIR M12 $3.7\mu\text{m}$ due to reflected-solar sensitivity):
1. **VIIRS (NOAA-20 / NOAA-21 / Suomi-NPP):**
   * **M15 ($\sim 10.76\mu\text{m}$):** Longwave Infrared Clean Window
   * **M16 ($\sim 12.01\mu\text{m}$):** Longwave Infrared Dirty Window
   * **Split-Window Difference:** $\Delta T = \text{M15} - \text{M16}$ (Cloud phase / optical thickness indicator)
2. **AVHRR (NOAA-18 / NOAA-19 / MetOp-B / MetOp-C):**
   * **Channel 4 ($\sim 10.80\mu\text{m}$):** Longwave Thermal IR
   * **Channel 5 ($\sim 12.00\mu\text{m}$):** Thermal Split-Window (if present in archive product)

### C. Archive Variable Metadata Audit (Pre-Extraction Verification)
Prior to extracting full datasets, representative 2024 files from each sensor will be inspected and explicitly documented:
* Platform and instrument name
* Exact NetCDF variable names (e.g. `M15`, `M16`, `CHANNEL_4`, `CHANNEL_5`)
* Units (e.g., $\%$, $\text{K}$, $\text{W/m}^2/\text{sr}/\mu\text{m}$) and calibration metadata
* Scale factors, offsets, fill/missing value flags (e.g. `_FillValue = NaN`)
* Geolocation variables (`latitude`, `longitude`)
* **Radiance vs Brightness Temperature:** If the file provides calibrated top-of-atmosphere radiance rather than brightness temperature, the exact sensor-specific Planck inverse conversion formula documented in file metadata will be applied. Generic conversions will NOT be invented.

---

## 3. Pixel/Scanline Acquisition Timestamp Logic

### A. Strict Causality Rule
An observation acquired at timestamp $t_{\text{acq}}$ is causally eligible for a target origin $t_0 = 00:00\text{ CET}$ if and only if:
$$t_{\text{acq}} \le t_0 = 00:00\text{ CET} \quad (\text{i.e.}, t_{\text{acq}} \le 23:00\text{ UTC winter} \text{ / } 22:00\text{ UTC DST})$$

### B. Timestamp Hierarchy
1. **Preferred Rule:** Use the actual per-pixel or per-scanline acquisition timestamp associated with the Nuolja/ROI pixels when stored in the NetCDF product.
2. **Fallback Rule:** If only swath-level start/end acquisition timestamps are stored, use the conservative swath-level timestamp ($t_{\text{swath\_start}}$ or $t_{\text{swath\_end}}$) and document that choice. Do not use file-level "pass end" timestamps if precise scanline timestamps exist.
3. **Standard Conservative Causality Wording:**  
  *"The selected satellite observation acquisition timestamp precedes t0 and is therefore causally eligible under the benchmark forecast-issuance protocol."*

---

## 4. Spatial Representation & Geodesic Footprint

* **ROI Definition:** $3\times 3$ native satellite-pixel ROI centered on the nearest valid pixel to Nuolja coordinates ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).
* **Footprint Accounting:** Physical footprint is determined directly from swath geolocation arrays (`latitude`, `longitude`) rather than assumed from nominal resolution.
* **Geodesic Distance Audit:** During extraction, actual geodesic distances (in meters) between the $3\times 3$ pixels will be calculated and reported using exact lat/lon coordinates.
* *Terminology Lock:* These pixels are strictly termed "native satellite pixels" and will NOT be referred to as "MEPS grid cells" or assumed to have $2.5\text{ km}$ spacing.

---

## 5. Missing-Data Handling Protocol

In the event of orbital coverage gaps or missing pre-$t_0$ satellite passes:
* **Explicit Missingness Flag (`sat_obs_available`):** Binary indicator ($1.0$ if valid pre-$t_0$ pass exists, $0.0$ if missing).
* **Default Neutral Feature Value:** Missing numerical thermal features are set to 0.0, and `sat_obs_available = 0.0` is passed directly to decision tree splitters.
* **Zero Imputation Rule:** NO silent `ffill`, `bfill`, or linear interpolation across origins.

---

## 6. Predeclared Candidate Feature Set (Compact 6-Feature Set)

To prevent post-hoc feature selection bias, the Stage 6.2 candidate feature set is pre-declared as follows:

1. `sat_bt_11um_point`: Pre-origin $10.8\mu\text{m}$ thermal-IR signal at nearest pixel to Nuolja.
2. `sat_bt_11um_roi_mean`: $3\times 3$ native satellite-pixel ROI mean $10.8\mu\text{m}$ thermal-IR signal.
3. `sat_bt_11um_roi_std`: $3\times 3$ native satellite-pixel ROI $10.8\mu\text{m}$ thermal-IR spatial standard deviation.
4. `sat_split_window_diff`: Split-window difference $\Delta T = T_{10.8\mu\text{m}} - T_{12.0\mu\text{m}}$ at nearest pixel.
5. `sat_obs_age_hours`: Time difference $\Delta t = t_0 - t_{\text{acq}}$ ($\text{hours}$).
6. `sat_obs_available`: Binary availability flag ($1.0$ if valid pre-$t_0$ pass exists, $0.0$ if missing).

---

## 7. Causality Audit Protocol

Every extracted satellite record will be audited against:
- $t_{\text{acq}} \le t_0$ (Pass/Fail).
- Platform & sensor name explicitly recorded.
- Geodesic distance from the nearest valid satellite pixel to the station is recorded; the extraction reports the actual distance and applies a predeclared coverage-quality threshold.
- Valid time horizon bounds ($H1\text{--}H24$) strictly maintained for downstream forecasting.
- Output log: `satellite_causality_audit.csv`.

---

## 8. Baseline Reproducibility Gate

Before evaluating satellite features, the Stage 6.2 pipeline MUST reproduce:
- **Stage 5.2 EVEN 5-Fold CV Baseline MAE:** **$39.4236\text{ W/m}^2$** EXACTLY.
- Stage 4 parameters ($w_h, k_h$) are NOT refit; exact Stage 4 benchmark outputs are preserved.

---

## 9. Predefined EVEN-CV Decision Gate

The candidate model (Stage 5.2 Base + 6 Predeclared Satellite Features) must achieve **ALL** of the following on EVEN 5-fold forward-chaining CV to qualify for ODD test evaluation:

1. **Aggregate MAE Delta:** Candidate EVEN-CV MAE $\le 39.2236\text{ W/m}^2$ ($\ge -0.20\text{ W/m}^2$ improvement over Stage 5.2 baseline of $39.4236\text{ W/m}^2$).
2. **Per-Fold Consistency:** Improvement in at least **4 out of 5 folds ($\ge 80\%$)** with zero single-fold degradation exceeding $+0.15\text{ W/m}^2$.
3. **Secondary Metrics:** Both nMAE ($\le 41.46\%$) and RMSE ($\le 62.83\text{ W/m}^2$) must improve or remain neutral.

---

## 10. ODD Test Isolation & Gate Rule (LOCKED)

* **ODD Evaluation Condition:** Held-out ODD test set (173 origins) will be evaluated **IF AND ONLY IF** the candidate passes ALL 4 predefined EVEN-CV decision gates.
* **If EVEN Gate Fails:** ODD test split remains **100% UNTOUCHED**, and the final Stage 6.2 decision is locked as `SATELLITE OBSERVATION — WEAK SIGNAL` or `SATELLITE OBSERVATION — NO IMPROVEMENT`.
* **Frozen Benchmark Champion:** Stage 5.2 Architecture A remains the unbeaten frozen champion ($39.084821\text{ W/m}^2$ ODD Daytime MAE / $30.32\%\text{ nMAE}$).

---

## 11. Updated Scientific Framing (LOCKED)

* **Constraint:** Do not claim that satellite observations will improve the forecast merely because they contain actual atmospheric information. Out-of-sample improvement must be empirically demonstrated under the locked benchmark.
* **Exact Wording:**  
  *"Failure to improve would indicate that the tested point/ROI satellite representation did not provide robust incremental predictive value under the current benchmark and architecture. It would not establish that satellite information is intrinsically uninformative."*

---

## 12. Expected Artifact List

Directory to be created upon approval: `stage6/stage6_2_satellite_observation/`

1. `README.md`: Directory overview and manifest.
2. `stage6_2_experiment_plan.md`: Detailed experiment design document.
3. `satellite_observation_extraction.py`: Extraction and causality audit script for polar swaths.
4. `run_stage6_2_audit_and_experiment.py`: Master experiment execution script.
5. `satellite_feature_summary.csv`: Extracted point/ROI thermal features per origin.
6. `satellite_causality_audit.csv`: Causality audit log for satellite acquisition timestamps.
7. `residual_information_audit.csv`: Spearman rank correlation audit vs Stage 5.2 residuals.
8. `even_cv_results.csv`: EVEN 5-fold CV aggregate performance table.
9. `per_fold_results.csv`: Per-fold CV MAE breakdown.
10. `per_horizon_results.csv`: Per-horizon H1-H24 MAE breakdown.
11. `final_summary.txt`: Executive summary text and decision lock.
