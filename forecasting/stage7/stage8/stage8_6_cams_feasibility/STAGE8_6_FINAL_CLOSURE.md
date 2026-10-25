# POLARIS Stage 8.6 CAMS Route — Final Audit & Governance Closure Report

**Date of Closure:** 2026-09-12  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Dataset Examined:** ECMWF / Copernicus Atmosphere Monitoring Service (CAMS) Global Atmospheric Composition Forecasts (`cams-global-atmospheric-composition-forecasts`)  
**Variables Examined:** Total Aerosol Optical Depth at 550 nm (`aod550`) and Total Column Water Vapour (`tcwv`)  

---

## 1. Route Summary & Distinction

The Stage 8.6 CAMS investigation consisted of two distinct, decoupled operational phases:

1. **Stage 8.6A — Empirical Feasibility & Causality Audit:** **PASS**
   * *Conclusion:* CAMS Global Atmospheric Composition Forecasts are 100% available, complete, spatially aligned, and causally valid across all 347 POLARIS benchmark origins ($8,328 / 8,328$ forecast-hour tuples verified).

2. **Stage 8.6B — Predeclared Forecasting Experiment:** **REJECTED**
   * *Conclusion:* Adding CAMS AOD550 and TCWV feature channels to the frozen Stage 8.1 Steering Wind model ($37 \rightarrow 39$ features) failed 4 out of 6 predeclared acceptance gates, yielding an overall EVEN CV MAE degradation of $+0.247252\text{ W/m}^2$.

### Overall Route Outcome & Scientific Interpretation:

$$\text{DATA FEASIBILITY: } \mathbf{\text{PASS}} \quad \vert \quad \text{FORECASTING UTILITY: } \mathbf{\text{REJECTED}} \quad \vert \quad \text{MODEL STATUS: } \mathbf{\text{NOT ADDED}}$$

> **Official Scientific Statement:**  
> *"CAMS was successfully validated as a causally accessible atmospheric-composition data source, but the predeclared forecasting experiment showed insufficient and inconsistent predictive benefit, so CAMS AOD550 and TCWV were rejected from the operational POLARIS model."*

---

## 2. Stage 8.6A Audit Details (Data Feasibility: PASS)

Stage 8.6A established empirical feasibility and causal validity prior to model training:

* **Source Archive:** ECMWF CAMS Global Atmospheric Composition Forecasts (`cams-global-atmospheric-composition-forecasts`).
* **Variables:** Total Aerosol Optical Depth at 550nm (`aod550`) and Total Column Water Vapour (`tcwv`).
* **Benchmark Coverage:** 347 / 347 clean forecast origins verified; 8,328 / 8,328 forecast-hour tuples ($100\%$ complete, 0 missing, 0 fill values).
* **Archived Provenance:** 12 raw monthly GRIB files stored in `stage7/stage8/stage8_6_cams_feasibility/raw_grib/`; 16,656 total GRIB messages inspected and verified via ecCodes/cfgrib.
* **Spatial Alignment:** Nearest regular $0.4^\circ$ grid point $(68.4^\circ\text{N}, 18.8^\circ\text{E})$, located approximately $4.91\text{ km}$ from Nuolja station ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$). No spatial averaging or spatial interpolation applied.
* **Causal Protocol:**
  * Forecast Initialization: $t_{\text{init}} = t_0 - 12\text{h}$ (D-1 12Z CAMS run for midnight POLARIS origins).
  * Valid Time Alignment: POLARIS lead $H_h$ ($t_0 + (h-1)\text{h}$) mapped to CAMS valid time $T_h$.
  * Lead Range: $+12\text{h}$ to $+35\text{h}$.
  * Zero post-$t_0$ leakage; zero analysis/reanalysis data used.
* **Operational Buffer:** CAMS 12Z operational run is guaranteed available by ~22:00 UTC (D-1), providing a minimum $2\text{-hour}$ operational lead buffer prior to midnight $t_0$.
* **Empirical Distributions (Daytime EVEN):**
  * **AOD550:** Mean $= 0.0546$, Median $= 0.0352$, Min $= 0.0008$, Max $= 0.9976$, $Q_{25} = 0.0172$, $Q_{75} = 0.0724$.
  * **TCWV:** Mean $= 9.63\text{ kg/m}^2$, Median $= 7.95\text{ kg/m}^2$, Min $= 1.27\text{ kg/m}^2$, Max $= 28.48\text{ kg/m}^2$, $Q_{25} = 4.61\text{ kg/m}^2$, $Q_{75} = 13.78\text{ kg/m}^2$.

---

## 3. Stage 8.6B Audit Details (Forecasting Utility: REJECTED)

Stage 8.6B evaluated the 39-feature candidate model against the 37-feature Stage 8.1 control across 174 EVEN origins using 5-fold forward-chaining cross-validation.

### Predeclared Acceptance Gates Evaluation:

| Gate | Description | Required Threshold | Candidate Value | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Gate 1 — Primary MAE** | Candidate EVEN MAE improvement $\ge 0.50\text{ W/m}^2$ | $\le 37.120054\text{ W/m}^2$ | `37.867306 W/m²` (`+0.247252 W/m²`) | **FAIL** |
| **Gate 2 — Fold Consistency** | Folds with MAE improvement | $\ge 4 / 5\text{ folds}$ | `3 / 5 folds` (Folds 1, 2, 5 improved; 3, 4 degraded) | **FAIL** |
| **Gate 3 — Worst-Fold Degradation** | Max fold MAE degradation | $\le +0.50\text{ W/m}^2$ | `+1.310037 W/m²` (Fold 3) | **FAIL** |
| **Gate 4 — Directional Metrics** | Candidate nMAE $\le$ Control AND RMSE $\le$ Control | nMAE $\le 37.9745\%$ & RMSE $\le 60.160645\text{ W/m}^2$ | nMAE: `37.5944%` (Pass), RMSE: `60.524544 W/m²` (Fail) | **FAIL** |
| **Gate 5 — Physical Causality** | $t_{\text{init}} = t_0 - 12\text{h} \le t_0$, valid time == $T_h$ | 100.0% Causal Tuples | `8,328 / 8,328` (100.0%) | **PASS** |
| **Gate 6 — Control Reproduction** | Stage 8.1 Control MAE reproduction | Expected 37.620054 $\pm 0.001\text{ W/m}^2$ | `37.620054 W/m²` (Error: 0.000000 W/m²) | **PASS** |

### Fold-by-Fold Performance Breakdown:

| Fold | Daytime Samples | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Delta nMAE (pp) | Control RMSE (W/m²) | Candidate RMSE (W/m²) | Delta RMSE (W/m²) | Fold Improved? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Fold 1** | 591 | 49.311419 | 48.988273 | -0.323146 | 29.5265 | 29.3330 | -0.1935 | 81.354967 | 80.946902 | -0.408065 | **YES** |
| **Fold 2** | 696 | 70.568800 | 70.018421 | -0.550380 | 36.9196 | 36.6317 | -0.2879 | 103.743912 | 103.161756 | -0.582155 | **YES** |
| **Fold 3** | 648 | 40.345573 | 41.655610 | +1.310037 | 28.1423 | 29.0561 | +0.9138 | 67.256670 | 69.438380 | +2.181710 | **NO** |
| **Fold 4** | 396 | 25.770418 | 26.701695 | +0.931277 | 36.7313 | 38.0587 | +1.3274 | 44.613169 | 45.395516 | +0.782347 | **NO** |
| **Fold 5** | 221 | 2.104058 | 1.972529 | -0.131529 | 58.5528 | 54.8926 | -3.6603 | 3.834508 | 3.680166 | -0.154342 | **YES** |

---

## 4. Governance & Operational Locks

1. **ODD Target Firewall:**
   * **0 ODD target values read.**
   * **0 ODD predictions generated.**
   * **0 ODD evaluation metrics computed.**
   * **0 hyperparameter tuning or feature selection based on ODD.**

2. **Active Operational Champion:**
   * **Champion:** Stage 8.1 U700+V700 Steering Wind Model (37 features).
   * **Official Held-Out ODD Performance:**
     * **MAE:** `36.188657 W/m²`
     * **nMAE:** `28.0688%`
   * **EVEN CV Baseline:** `37.620054 W/m²`

3. **No Retuning / No Rescue Protocol:**
   * Per predeclared governance rules, no post-hoc tuning, species selection, threshold engineering, or secondary experiments were attempted to rescue CAMS.
   * Stage 8.6 is officially closed and locked.

---

## 5. Artifact Inventory

All Stage 8.6 artifacts are archived in [`stage7/stage8/stage8_6_cams_feasibility/`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/):

* **Audit Scripts:**
  * [`inspect_cams_smoke_test_grib.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/inspect_cams_smoke_test_grib.py)
  * [`run_stage8_6a_cams_full_audit.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/run_stage8_6a_cams_full_audit.py)
  * [`run_stage8_6b_experiment.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/run_stage8_6b_experiment.py)
* **Stage 8.6A Audit Records:**
  * [`STAGE8_6A_CAMS_SUMMARY.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_SUMMARY.json)
  * [`STAGE8_6A_CAMS_FEASIBILITY_REPORT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_FEASIBILITY_REPORT.md)
  * [`STAGE8_6A_CAMS_PROVENANCE_MANIFEST.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_PROVENANCE_MANIFEST.json)
  * [`STAGE8_6A_CAMS_ORIGIN_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_ORIGIN_AUDIT.csv)
  * [`STAGE8_6A_CAMS_FORECAST_HOURS_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_FORECAST_HOURS_AUDIT.csv)
  * [`STAGE8_6A_CAMS_CAUSALITY_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_CAUSALITY_AUDIT.csv)
  * [`STAGE8_6A_CAMS_VARIABLE_INVENTORY.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6A_CAMS_VARIABLE_INVENTORY.csv)
* **Stage 8.6B Experiment Records:**
  * [`STAGE8_6B_EVEN_CV_RESULTS.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_EVEN_CV_RESULTS.json)
  * [`STAGE8_6B_GATE_DECISION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_GATE_DECISION.json)
  * [`STAGE8_6B_EVEN_CV_SUMMARY.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_EVEN_CV_SUMMARY.csv)
  * [`STAGE8_6B_REPRODUCIBILITY.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_REPRODUCIBILITY.md)
  * [`STAGE8_6B_CAMS_EXPERIMENT_REPORT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_CAMS_EXPERIMENT_REPORT.md)
* **Stage 8.6 Final Closure Records:**
  * [`STAGE8_6_FINAL_DECISION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6_FINAL_DECISION.json)
  * [`STAGE8_6_FINAL_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6_FINAL_CLOSURE.md)
