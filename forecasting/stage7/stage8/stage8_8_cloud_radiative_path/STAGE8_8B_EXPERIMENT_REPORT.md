# POLARIS STAGE 8.8B — CLOUD RADIATIVE-PATH GEOMETRY FORECASTING EXPERIMENT REPORT

**Stage:** STAGE 8.8B CLOUD RADIATIVE-PATH GEOMETRY FORECASTING EXPERIMENT  
**Date:** September 12, 2026  
**Status:** COMPLETE — **DECISION: REJECTED**  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, Elev: $702\text{ m a.s.l.}$)  
**Official Operational Champion:** Stage 8.1 700 hPa Steering Wind Model (FROZEN & UNTOUCHED)  

---

## 1. Executive Summary & Core Verdict

Stage 8.8B evaluated the physical hypothesis that adding 3 explicit MEPS cloud vertical geometry features (`cloud_base_altitude_causal`, `cloud_top_altitude_causal`, `cloud_geometric_thickness`) to the frozen 37-feature Stage 8.1 champion improves 24-hour surface shortwave radiation forecasting accuracy.

> [!WARNING]
> **OFFICIAL STAGE 8.8B DECISION: REJECTED**
> 
> * **Control Model (37 features):** Stage 8.1 Champion (`HistGradientBoostingRegressor`).
> * **Control EVEN CV MAE:** `35.270823 W/m²` (Exact reproduction check passed: diff $\le 0.01\text{ W/m}^2$).
> * **Control EVEN CV nMAE:** `36.2419%` | **RMSE:** `56.761152 W/m²` | **Bias:** `+2.674980 W/m²`
> * **Candidate Model (40 features):** Control 37 features + 3 MEPS cloud geometry features.
> * **Candidate EVEN CV MAE:** `35.417182 W/m²` (Delta MAE: **`+0.146360 W/m²`**).
> * **Candidate EVEN CV nMAE:** `37.0364%` (Delta nMAE: **`+0.7946 pp`**).
> * **Candidate EVEN CV RMSE:** `56.870775 W/m²` (Delta RMSE: **`+0.109623 W/m²`**).
> * **Candidate EVEN CV Bias:** `+3.210776 W/m²` (Delta Bias: **`+0.535796 W/m²`**).
> * **Folds Improved:** `2/5`.
> * **Max Fold Degradation:** `+0.564104 W/m²`.
> * **10,000 Paired Bootstrap 95% CI:** `[-0.097347, +0.408509] W/m²` (Mean delta: `+0.154597 W/m²`).

---

## 2. Predeclared Six Decision Gates Audit

| Gate | Description | Threshold | Candidate Result | Gate Status |
| :--- | :--- | :---: | :---: | :---: |
| **G1** | Primary MAE Improvement | $\Delta\text{MAE} \le -0.50\text{ W/m}^2$ | `+0.146360 W/m²` | **FAIL** |
| **G2** | Multi-Fold Consistency | $\ge 4/5$ EVEN Folds | `2/5` | **FAIL** |
| **G3** | Worst-Fold Degradation | $\le +0.50\text{ W/m}^2$ | `+0.564104 W/m²` | **FAIL** |
| **G4** | nMAE & RMSE Consistency | $\text{Cand nMAE} \le \text{Ctrl}, \text{RMSE} \le \text{Ctrl}$ | $\Delta\text{nMAE} = +0.7946\text{ pp}, \Delta\text{RMSE} = +0.109623\text{ W/m}^2$ | **FAIL** |
| **G5** | Absolute Causality | 100% D-1 18Z Causal | 347/347 origins 100% verified | **PASS** |
| **G6** | Control Reproduction | Exact Match vs Baseline | `35.270823 W/m²` (Diff $\le 0.01$) | **PASS** |


---

## 3. Five-Fold Forward-Chaining Breakdown (Daytime MAE & nMAE)

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Fold Improved? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | 41.728068 | 42.107977 | +0.379909 | 24.9858% | 25.2133% | NO |
| Fold 2 | 66.190911 | 65.894589 | -0.296322 | 34.6293% | 34.4742% | **YES** |
| Fold 3 | 40.078480 | 40.642585 | +0.564104 | 27.9560% | 28.3494% | NO |
| Fold 4 | 26.340965 | 26.296786 | -0.044179 | 37.5445% | 37.4815% | **YES** |
| Fold 5 | 2.015690 | 2.143975 | +0.128286 | 56.0937% | 59.6637% | NO |


---

## 4. Control Reproduction Audit (Hard Gate G6)

* **Expected Stage 8.1 EVEN CV MAE:** `35.270823 W/m²`
* **Stage 8.8B Control EVEN CV MAE:** `35.270823 W/m²`
* **Absolute Discrepancy:** `0.000000 W/m²` (Tolerance: $\le 0.01\text{ W/m}^2$)
* **Control Reproduction Status:** **PASSED**

---

## 5. Candidate Feature Definitions & Preprocessing

The 3 candidate features added to the 37 Stage 8.1 features (total **40 features**):
1. `cloud_base_altitude_causal`: MEPS `meps_det_sfc` cloud base height ($m$ ASL), zero-masked (`0.0 m`) during clear-sky / sentinel hours ($9.96921 \times 10^36$).
2. `cloud_top_altitude_causal`: MEPS `meps_det_sfc` cloud top height ($m$ ASL), zero-masked (`0.0 m`) during clear-sky / sentinel hours ($9.96921 \times 10^36$).
3. `cloud_geometric_thickness`: Column envelope depth $\max(0.0, z_{\text{top}} - z_{\text{base}})$, zero-masked (`0.0 m`) during clear-sky / sentinel hours.

---

## 6. Scientific Interpretation & Physical Limitations

1. **Experimental Finding:** Adding MEPS vertical cloud geometry features did NOT provide sufficient improvement to pass all six predeclared decision gates under the locked EVEN CV protocol.
2. **Physical Scope:** Geometric thickness $\Delta z$ represents a total column envelope depth, which collapses intermediate clear-sky gaps in multi-layer cloud systems. It is an independent geometric path variable, distinct from column-integrated optical mass ($LWP, IWP$).
3. **Scoped Conclusion:** This specific 3-feature cloud-geometry augmentation did not improve the frozen Stage 8.1 architecture under the locked protocol. This result does NOT imply vertical cloud information is physically useless, but rather that surface-diagnosed column envelope thickness at 2.5 km resolution is redundant with existing LWP/IWP and cloud fraction in HistGradientBoostingRegressor.

---

## 7. ODD Firewall Verification

* **ODD Target Reads:** `0`
* **ODD Predictions Generated:** `0` (if REJECTED)
* **ODD Metrics Calculated:** `0` (if REJECTED)
* **Stage 8.1 Champion Modified:** **FALSE** (Frozen)
* **POLARIS_MASTER_HANDOFF.md Modified:** **FALSE** (Untouched)
* **Historical Stage Artifacts Modified:** **FALSE** (Untouched)
