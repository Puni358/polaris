# STAGE 8.1 FEATURE MATRIX DATA ACCESS CHECKPOINT

> [!IMPORTANT]
> **CANDIDATE A DATA ACCESS STATUS: 100% AVAILABLE & VERIFIED**
> - **Artifact ID:** `STAGE8_1_FEATURE_MATRIX_DATA_ACCESS_CHECKPOINT`
> - **Feature Matrix Path:** [`stage8_1_full_37_feature_matrix_2024.csv`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv)
> - **Dimensions:** `8,328 rows × 45 columns` (347 origins × 24 horizons: 173 EVEN + 174 ODD)
> - **SHA-256 Checksum:** `e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541`
> - **Missingness:** `0 NaNs` (100% complete real data across all 37 features)
> - **Authenticity Verdict:** **100% Genuine Stage 8.1 Artifacts** (Zero synthetic/random data)

---

## 1. Summary of Data Access Verification

Per the request for AI assistant Candidate A (*NWP-forecast-volatility-aware regime/residual modeling*), the raw Stage 8.1 training feature matrix and component artifacts used to train the Stage 8.1 37-feature HGB champion have been identified, assembled, and verified.

---

## 2. Complete 37 Stage 8.1 Feature Column Inventory

The 37 features are grouped into 7 physical families:

1. **Solar Geometry & Temporal (5):** `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`
2. **Clear-Sky Irradiance (1):** `clearsky_ghi`
3. **Single-Level NWP Meteorology (4):** `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`
4. **Cloud Condensate & Interaction (3):** `lwp_latest`, `iwp_latest`, `lwp_x_cloud`
5. **Terrain & 360° Horizon Obstructance (4):** `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`
6. **700 hPa Free-Atmosphere Steering Wind (2):** `u700`, `v700`
7. **Historical GHI Context & Model Disagreement (18):**
   - Stage 3B GBDT Prediction: `pred_stage3b_cloud_nwp`
   - Stage 4 Physical Clear-Sky Model: `phys_pred_fold`
   - Stage 4 Dynamic Ensemble Prediction: `pred_stage4_fold`
   - NWP Disagreement Signal: `disagreement_fold`
   - Historical GHI Volatility & Trend: `ctx_std_3h`, `ctx_std_6h`, `ctx_std_12h`, `ctx_std_24h`, `ctx_abs_change_1h`, `ctx_abs_change_3h`, `ctx_abs_change_6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h`, `ctx_kt_std_6h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`

---

## 3. MEPS Cloud Fraction, LWP, and IWP Trajectories

The forecast trajectories for cloud fraction, LWP, and IWP across all 347 origins ($H1...H24$) are fully present in the matrix:
- **`cloud_frac`**: Derived from MEPS 2.5km `fc_cloud_cover / 100.0` (0.0 to 1.0).
- **`lwp_latest`**: MEPS liquid water path column integral (kg/m2).
- **`iwp_latest`**: MEPS ice water path column integral (kg/m2).
- **`lwp_x_cloud`**: Cloud-fraction-weighted LWP (lwp_latest * cloud_frac).

---

## 4. Origin & Timestamp Alignment

The matrix contains exact identifiers to align with the canonical 173 EVEN and 174 ODD benchmark origins:
- **`origin_id`**: Integer origin ID (1 to 347).
- **`forecast_start`**: Forecast origin timestamp t0 (`YYYY-MM-DD 00:00:00+00:00`).
- **`horizon_hour`**: Hourly horizon step (1 to 24).
- **`timestamp`**: Valid target timestamp (t0 + h).
- **`split`**: `EVEN` (173 origins / 4,152 rows) vs `ODD` (174 origins / 4,176 rows).

---

## 5. Artifact Paths, Dimensions, and Hashes

| Component Artifact | File Path | Dimensions | SHA-256 Hash |
| :--- | :--- | :---: | :--- |
| **Stage 8.1 Full Feature Matrix** | [`stage8_1_full_37_feature_matrix_2024.csv`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv) | `8,328 × 45` | `e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541` |
| **MEPS NWP Forecasts 2024** | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `8,328 × 10` | `c07b0e14...` |
| **Stage 6.6 LWP/IWP Features** | `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` | `8,328 × 4` | `6c471015...` |
| **Stage 7.5 Terrain Features** | `stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv` | `8,784 × 6` | `28e469c8...` |
| **Stage 8.1 700hPa Wind Features**| `stage7/stage8/stage8_1_700hpa_wind/stage8_1_extracted_features.csv` | `8,328 × 9` | `aa6ce29f...` |

---

## 6. Confirmation of Real Data Provenance

All features in `stage8_1_full_37_feature_matrix_2024.csv` were built directly from the verified 2024 MET Norway MEPS forecasts, Lantmäteriet 2m DEM terrain profiles, and SITES Nuolja ground observations. **Zero synthetic or invented data were used.**

*Checkpoint created on 2026-09-13T22:22:12.046400+05:30.*
