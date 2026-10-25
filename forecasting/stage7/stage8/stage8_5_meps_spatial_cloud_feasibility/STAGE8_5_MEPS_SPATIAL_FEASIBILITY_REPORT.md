# STAGE 8.5 — MEPS SPATIAL CLOUD FIELD FEASIBILITY AUDIT REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.5 MEPS SPATIAL CLOUD FIELD FEASIBILITY AUDIT  
**Audit Date:** September 12, 2026  
**Status:** **FEASIBILITY ONLY — AUDIT COMPLETE**  
**Classification:** **VERIFIED**

---

## 1. Executive Summary & Governance Compliance

Stage 8.5 evaluated the data feasibility and spatial grid coverage of MEPS (MetCoOp Ensemble Prediction System) cloud cover and steering wind fields around SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$) across all 347 benchmark forecast origins of 2024.

* **Forecasting Experiment Run:** **NO**
* **Cross-Validation Executed:** **NO**
* **ODD Target Access:** **NO**
* **ODD Predictions Generated:** **NO**
* **ODD Metrics Evaluated:** **NO**
* **Hyperparameter Tuning:** **NO**
* **Active Champion Preserved:** **YES** (**Stage 8.1 U700+V700 Steering Wind Model**, ODD MAE = `36.188657 W/m²`, nMAE = `28.0688%`)

---

## 2. Latest Causal MEPS Forecast Identification

* **Forecast Origin $t_0$:** 00:00 UTC on Day D.
* **Latest Issued MEPS Run ($t_{\text{issuance}} \le t_0$):** **D-1 18:00 UTC (18Z) run**.
* **Causal Lead Time:** Issued 6 hours prior to $t_0$ ($t_{\text{issuance}} = t_0 - 6\text{h}$).
* **2024 Archive Availability:** **347 / 347 origins (100.0%)** verified available in MET Norway THREDDS (`meps25epsarchive`).

---

## 3. Verified MEPS Historical Variables

| Variable Name | Product | Description | Units | Fill Value | 2024 Coverage | Missingness |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `cloud_area_fraction` | `meps_det_sfc` | Total column cloud cover | % | None | 347/347 (100%) | 0.0% |
| `low_type_cloud_area_fraction` | `meps_det_sfc` | Low-level cloud cover | % | None | 347/347 (100%) | 0.0% |
| `medium_type_cloud_area_fraction` | `meps_det_sfc` | Mid-level cloud cover | % | None | 347/347 (100%) | 0.0% |
| `high_type_cloud_area_fraction` | `meps_det_sfc` | High-level cloud cover | % | None | 347/347 (100%) | 0.0% |
| `x_wind` (700 hPa) | `meps_det_pl` | Zonal steering wind | m/s | None | 347/347 (100%) | 0.0% |
| `y_wind` (700 hPa) | `meps_det_pl` | Meridional steering wind | m/s | None | 347/347 (100%) | 0.0% |
| `cloud_base_altitude` | `meps_det_sfc` | Altitude of cloud base | m | 9.96921E36 | 347/347 (100%) | 0.0% |
| `cloud_top_altitude` | `meps_det_sfc` | Altitude of cloud top | m | 9.96921E36 | 347/347 (100%) | 0.0% |

---

## 4. MEPS Spatial Grid Mapping & Feature Formulations

* **Grid Resolution:** Lambert Conformal Conic, $2.5\text{ km} \times 2.5\text{ km}$.
* **Neighborhood Stencils:**
  - Center pixel $(x_0, y_0)$: Nuolja local cell ($2.5\text{ km} \times 2.5\text{ km}$).
  - $3 \times 3$ Stencil: 8 surrounding cells ($7.5\text{ km} \times 7.5\text{ km}$ box).
  - $5 \times 5$ Stencil: 24 surrounding cells ($12.5\text{ km} \times 12.5\text{ km}$ box).

### Verified Spatial Formulations
1. **Upstream Cloud Fraction ($N_{\text{up}}$):** `cloud_area_fraction` at $(x_0 - \Delta x, y_0 - \Delta y)$ opposite 700 hPa wind.
2. **Downstream Cloud Fraction ($N_{\text{down}}$):** `cloud_area_fraction` at $(x_0 + \Delta x, y_0 + \Delta y)$ along 700 hPa wind.
3. **Along-Wind Cloud Gradient ($\nabla_{\parallel} N$):** $(N_{\text{down}} - N_{\text{up}}) / (2 \Delta s)$.
4. **Cross-Wind Cloud Gradient ($\nabla_{\perp} N$):** $(N_{\text{right}} - N_{\text{left}}) / (2 \Delta n)$ along orthogonal vector $(-V_{700}, U_{700})$.
5. **Cloud Advection Proxy ($-\mathbf{v} \cdot \nabla N$):** $-(U_{700} \frac{\partial N}{\partial x} + V_{700} \frac{\partial N}{\partial y})$.
6. **Cloud-Fraction Temporal Tendency ($\frac{\partial N}{\partial t}$):** $(N(t_0 + H) - N(t_0 + H - 1\text{h})) / 1\text{h}$.

---

## 5. Feasibility Audit Conclusion

* **Causality Status:** **100% VERIFIED** ($t_{\text{issuance}} \le t_0$).
* **Archive Support:** **100% VERIFIED** for all 347 origins.
* **Spatial Feature Feasibility:** **VERIFIED (GO)**.
