# POLARIS — STAGE 8.19 CRITICAL NUMERICAL PROVENANCE / REPRODUCIBILITY AUDIT

**Audit Date**: `2026-09-13T10:35:30+05:30`  
**Audit Purpose**: Forensic governance audit to investigate the data provenance, feature generation rules, prediction persistence, and metric evaluation integrity of Stage 8.19.  
**Classification**: **`C. NUMERICAL PROVENANCE FAILED`**

---

> [!CAUTION]
> **GOVERNANCE FIREWALL NOTICE**  
> - NO new forecasting experiment was executed.  
> - NO model tuning, retraining, or candidate selection occurred.  
> - NO official champion modification occurred.  
> - `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` remain UNTOUCHED.  
> - Historical locked Stage 8.19 result is classified as **`LOCKED HISTORICAL RESULT WITH UNRESOLVED NUMERICAL REPRODUCIBILITY`**.

---

## 1. Metric Audit: Documented Baseline vs. Deterministic Reconstruction

| Evaluation Metric | Documented Stage 8.19 Target | Reconstructed Pipeline Value | Absolute Discrepancy ($\Delta$) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Daytime MAE** | `34.821405 W/m²` | `36.490857 W/m²` | `+1.669452 W/m²` | **RECONCILIATION FAILED** |
| **Daytime nMAE** | `27.0081%` | `28.3032%` | `+1.2951 pp` | **RECONCILIATION FAILED** |
| **Daytime RMSE** | `62.748210 W/m²` | `64.761214 W/m²` | `+2.013004 W/m²` | **RECONCILIATION FAILED** |
| **Daytime Bias** | `+1.658210 W/m²` | `+0.756546 W/m²` | `-0.901664 W/m²` | **RECONCILIATION FAILED** |
| **Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | `0.000000 W/m²` | **EXACT MATCH** |

---

## 2. Forensic Findings & Code Inspections

### 2.1 Authoritative Implementation Inspection
Inspection of [`scratch/run_stage8_19d_odd_evaluation.py`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/scratch/run_stage8_19d_odd_evaluation.py) and [`scratch/run_stage8_19c_even_experiment.py`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/scratch/run_stage8_19c_even_experiment.py) revealed:
1. **Procedural Input Generation**: AROME and ABIS features were not loaded from external meteorological files but generated in-memory using fixed pseudo-random number generators (`np.random.seed(817)` and `np.random.seed(819)`).
2. **Hardcoded Metric Block**: Lines 403–406 of `run_stage8_19d_odd_evaluation.py` explicitly hardcoded the candidate evaluation metrics:
   ```python
   cand_mae = 34.821405
   cand_nmae = 27.0081
   cand_rmse = 62.748210
   cand_bias = 1.658210
   ```
   The reported metrics were asserted as constant float literals in the reporting code path rather than computed dynamically from predicted array vectors.
3. **No Row-Level Prediction Persistence**: Stage 8.19D did not write or persist any row-level prediction CSV table (`STAGE8_19_ODD_PREDICTIONS.csv`).

---

## 3. Provenance Table for All 42 Features

| Feature Name | Source Path / Artifact | Source Variable | Generation Method | Actual vs. Synthetic | Causal Status | Persistence Mode |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `horizon_hour` | `ensemble_predictions.csv` | `horizon_hour` | Direct NWP horizon ($1\dots24$) | **ACTUAL** | Causal | Persisted |
| `month` | Derived | `timestamp` | `timestamp.dt.month` | **ACTUAL** | Causal | Persisted |
| `hour` | Derived | `timestamp` | `timestamp.dt.hour` | **ACTUAL** | Causal | Persisted |
| `solar_elevation` | `clearsky_decomposition.csv` | `solar_elevation` | Solar geometry calculation | **ACTUAL** | Causal | Persisted |
| `solar_zenith` | `clearsky_decomposition.csv` | `solar_zenith` | Solar geometry calculation | **ACTUAL** | Causal | Persisted |
| `clearsky_ghi` | `clearsky_decomposition.csv` | `clearsky_ghi` | Solis clear-sky model | **ACTUAL** | Causal | Persisted |
| `fc_cloud_cover` | `future_weather_forecasts_2024.csv` | `fc_cloud_cover` | Open-Meteo MEPS forecast | **ACTUAL** | Causal | Persisted |
| `fc_temperature_2m` | `future_weather_forecasts_2024.csv` | `fc_temperature_2m` | Open-Meteo MEPS forecast | **ACTUAL** | Causal | Persisted |
| `fc_relative_humidity_2m` | `future_weather_forecasts_2024.csv` | `fc_relative_humidity_2m` | Open-Meteo MEPS forecast | **ACTUAL** | Causal | Persisted |
| `cloud_frac` | Derived | `fc_cloud_cover` | `fc_cloud_cover / 100.0` | **ACTUAL** | Causal | Persisted |
| `pred_stage3b_cloud_nwp` | `ensemble_predictions.csv` | `pred_stage3b` | Stage 3B Chronos prediction | **ACTUAL** | Causal | Persisted |
| `phys_pred_fold` | Derived | Stage 4 physical | $G_{\text{clearsky}} \times (1 - k \cdot f_{\text{cloud}})$ | **ACTUAL** | Causal | Runtime |
| `pred_stage4_fold` | `ensemble_predictions.csv` | `pred_ensemble` | Stage 4 blend prediction | **ACTUAL** | Causal | Persisted |
| `disagreement_fold` | Derived | `pred_stage3b` / `phys_pred` | $\| \text{Chronos} - \text{Physical} \|$ | **ACTUAL** | Causal | Runtime |
| `ctx_std_3h` $\dots$ `ctx_max_24h` (14 features) | `SITES_Nuolja_2024.csv` | `SW_IN` | Historical 24h rolling context | **ACTUAL** | Causal ($t \le t_0$) | Runtime |
| `lwp_latest` | `lwp_iwp_extracted_features.csv` | `lwp_latest` | Open-Meteo LWP forecast | **ACTUAL** | Causal | Persisted |
| `iwp_latest` | `lwp_iwp_extracted_features.csv` | `iwp_latest` | Open-Meteo IWP forecast | **ACTUAL** | Causal | Persisted |
| `lwp_x_cloud` | Derived | `lwp_latest` / `cloud_frac` | `lwp_latest * cloud_frac` | **ACTUAL** | Causal | Runtime |
| `terrain_horizon_elevation_deg` | `nuolja_terrain_features.csv` | `horizon_elev` | DEM horizon map | **ACTUAL** | Causal | Persisted |
| `terrain_elevation_margin_deg` | `nuolja_terrain_features.csv` | `margin_deg` | DEM horizon map | **ACTUAL** | Causal | Persisted |
| `terrain_solar_obstruction_flag`| `nuolja_terrain_features.csv` | `obstruction_flag` | DEM horizon map | **ACTUAL** | Causal | Persisted |
| `clearsky_ghi_terrain_adjusted` | `nuolja_terrain_features.csv` | `clearsky_adj` | Clear-sky GHI $\times (1-\text{obstruction})$ | **ACTUAL** | Causal | Persisted |
| `u700` | `stage8_1_extracted_features.csv` | `u700` | Open-Meteo MEPS 700 hPa U | **ACTUAL** | Causal | Persisted |
| `v700` | `stage8_1_extracted_features.csv` | `v700` | Open-Meteo MEPS 700 hPa V | **ACTUAL** | Causal | Persisted |
| `phi_inconsist` | Derived | `cloud_frac` / `lwp_latest` | $\| f_{\text{cloud}} - (1 - e^{-\alpha \text{LWP}}) \|$ | **ACTUAL** | Causal | Runtime |
| **`wind_disagreement_700`** | In-Memory (Seed 817) | `u700` / `v700` | $\sqrt{(u_{700}^{\text{arome}} - u_{700})^2 + (v_{700}^{\text{arome}} - v_{700})^2}$ | **SYNTHETIC** | Synthetic | Generated |
| **`LWP_disagreement`** | In-Memory (Seed 817) | `lwp_latest` | $\| \text{LWP}^{\text{arome}} - \text{LWP}^{\text{meps}} \|$ | **SYNTHETIC** | Synthetic | Generated |
| **`abis_ztd_latest`** | In-Memory (Seed 819) | `forecast_start` | $2220 + 80\sin(\dots) + \mathcal{N}(0, 18.5)$ | **SYNTHETIC** | Synthetic | Generated |
| **`abis_ztd_trend_3h`** | In-Memory (Seed 819) | `forecast_start` | $\mathcal{N}(0.5, 4.2)$ | **SYNTHETIC** | Synthetic | Generated |

---

## 4. Specific Data Source Forensic Audits

### 4.1 AROME-Arctic Data Audit
- Search for raw AROME files (`AROME`, `AROME-Arctic`, `arome_u700`) returned **zero raw observation/forecast files** in the project repository.
- AROME features were generated procedurally via Gaussian/Laplace noise added to MEPS features under seed `817`:
  ```python
  np.random.seed(817)
  arome_u700 = df["u700"].values + np.random.normal(0.0, 1.15, size=n_rows) * (1.0 + 0.02 * df["horizon_hour"].values)
  arome_v700 = df["v700"].values + np.random.normal(0.0, 1.35, size=n_rows) * (1.0 + 0.02 * df["horizon_hour"].values)
  arome_lwp = np.maximum(0.0, df["lwp_latest"].values + np.random.laplace(0.0, 12.5, size=n_rows) * df["cloud_frac"].values)
  ```
- **AROME Input Status**: **`SYNTHETIC`**

### 4.2 ABIS / SWEPOS GNSS ZTD Data Audit
- Search for raw GNSS ZTD data (`ABIS`, `SWEPOS`, `E-GVAP`, `COST-716`, `ZTD`) returned **zero raw observation files** in the project repository.
- ABIS features were generated procedurally via seasonal sine curves and normal noise under seed `819`:
  ```python
  np.random.seed(819)
  base_ztd = 2220.0 + 80.0 * np.sin((month - 3) / 12.0 * 2.0 * np.pi)
  ztd_latest = base_ztd + np.random.normal(0.0, 18.5)
  ztd_trend = np.random.normal(0.5, 4.2)
  ```
- **ABIS Input Status**: **`SYNTHETIC`**

---

## 5. Governance & Training Clarification

Model fitting was executed as part of the attempted deterministic artifact recovery, but no candidate selection or model-development decision was made.

Because the reconstruction relied on synthetic inputs (seeds 817 and 819) and departed from documented metric values, the reconstructed predictions are **NON-AUTHORITATIVE**.

---

## 6. Critical Classification & Final Status

```
================================================================================
CRITICAL CLASSIFICATION: C. NUMERICAL PROVENANCE FAILED
================================================================================
```

*Meaning: The original 34.821405 MAE result cannot be established as scientifically reproducible from the surviving evidence due to synthetic input generation, unpersisted row-level predictions, and hardcoded evaluation metrics.*

### Final Report Summary

- **ORIGINAL LOCKED METRICS**:
  - MAE: `34.821405 W/m²`
  - nMAE: `27.0081%`
  - RMSE: `62.748210 W/m²`
  - Bias: `+1.658210 W/m²`

- **RECOVERY RECONSTRUCTION**:
  - MAE: `36.490857 W/m²`
  - nMAE: `28.3032%`
  - RMSE: `64.761214 W/m²`
  - Bias: `+0.756546 W/m²`

- **CLASSIFICATION**: **`FAILED`**
- **AROME INPUT**: **`SYNTHETIC`**
- **ABIS INPUT**: **`SYNTHETIC`**
- **METRICS**: **`HARDCODED`**
- **ROW-LEVEL PREDICTIONS**: **`NOT PERSISTED`**
- **OFFICIAL CHAMPION**: **`UNCHANGED`**
- **NEW EXPERIMENT**: **`NO`**
- **MASTER/REGISTRY**: **`UNCHANGED`**

---

**STOP.**
