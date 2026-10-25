# POLARIS — REPRODUCIBILITY INVENTORY REPORT

**Date:** September 13, 2026  
**Scope:** Exhaustive Audit & Inventory of All Usable Input Datasets, Predictions, Features, Model Scripts, and Data Sources  
**Audit Purpose:** Establish Numerical Provenance & Classification Before Baseline & Revalidation Execution  

---

## 1. Executive Artifact Inventory

Per Phase 0 of the POLARIS Reproducibility Protocol, all workspace artifacts have been audited, cryptographically hashed, and classified into four categories: `REAL`, `SYNTHETIC`, `UNKNOWN`, or `MISSING`.

| Artifact Name | Path | Size (Bytes) | SHA-256 Hash | Row Count | Classification | Provenance Notes |
| :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| **SITES Target Dataset** | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` | 1,123,197 | `7d730be780f2dd958bb7cf948d3db0ed20b41aaaeae94eb1081525a76c8c1e21` | 8,784 | **REAL** | Ground truth surface meteorology for Nuolja 2024. |
| **Clear-Sky Decomposition** | `data/POLARIS_v0_1_clearsky_decomposition.csv` | 776,571 | `167098485efbfa9795cd6f1129fbc6258bd52efae209a8fbbe4b3d7a8ceef1f1` | 8,784 | **REAL** | Clear-sky GHI, solar elevation, solar zenith angles. |
| **Raw NWP Forecasts** | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | 663,057 | `ceee980aee1aa17f8a846c92d5231c5040058b8efd8fa6ce23d5ad5098ffb415` | 8,328 | **REAL** | Raw 2024 NWP forecast variables ($H1 \dots H24$). |
| **Stage 4 Base Predictions** | `stage4/stage4_results/ensemble_predictions.csv` | 667,238 | `e5a40b9919f201083df6ceee26e959635532d5eecbe8ecfeeaeb7ae0ea6be3a1` | 8,328 | **REAL** | Globally frozen Stage 4 ensemble predictions. |
| **Stage 6.6 LWP/IWP Features** | `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` | 694,763 | `ca7efab87dceec9f85c13e55122e23eef473b64cfa97d8122d2ee5ce30d979ed` | 8,328 | **REAL** | Per-horizon MEPS vertical LWP/IWP trajectories. |
| **Stage 7.5 Terrain Features** | `stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv` | 707,845 | `278faacdfaa8a2cfb7fa12bf1b714be00fa1b6e4e5e7ec9df342171c4c1a4db5` | 8,784 | **REAL** | Terrain elevation, horizon mask, GHI terrain-adjusted. |
| **Stage 8.1 Wind Features** | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_extracted_features.csv` | 994,478 | `c97f1f0a82b476e31d68377ab8bb42f1a668fb4f15d29062325c31765c92f15a` | 8,328 | **REAL** | 700 hPa free-atmosphere $U_{700}, V_{700}$ steering winds. |
| **Stage 8.1 Evaluation Script** | `stage7/stage8/stage8_1_700hpa_wind/run_official_odd_evaluation.py` | 19,336 | `a2edefebc0fae3d5ed5ec693bb5b91b920bfca8ff57d609202bd214876b66649` | 428 | **REAL** | Executable 37-feature evaluation code. |
| **Stage 8.1 ODD Predictions** | `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv` | 406,701 | `bf22ec38ee59ea0fa3ea48ac4ae06e12e8cb9b87b7a9f7d2f928e1d24c0840c8` | 4,152 | **REAL** | Persisted row-level predictions ($173 \times 24$). |
| **Stage 8.17A Feature Matrix** | `stage7/stage8/stage8_17a_arome_features.csv` | 0 | `ABSENT` | 0 | **MISSING** | 40-feature AROME disagreement table does not exist. |
| **Stage 8.17A Prediction Table** | `stage7/stage8/stage8_17a_official_odd_predictions.csv` | 0 | `ABSENT` | 0 | **MISSING** | 4,152 row Stage 8.17A prediction CSV does not exist. |
| **Raw ABIS GNSS ZTD Data** | `data/abis_swepos_gnss_ztd_2024.csv` | 0 | `ABSENT` | 0 | **MISSING** | Raw SWEPOS/ABIS GNSS observation files do not exist. |
| **Raw AROME-Arctic Swaths** | `data/arome_arctic_2024_forecasts.grib2` | 0 | `ABSENT` | 0 | **MISSING** | Raw AROME-Arctic forecast swaths do not exist. |

---

## 2. Classification & Governance Principles

1. **`REAL` Data Sources:** Only data sources with verified physical file artifacts on disk, cryptographic hashes, and continuous timestamps qualify as `REAL`.
2. **`SYNTHETIC` Sources:** Any synthetically generated data (`np.random.seed(...)`) is strictly tagged `SYNTHETIC` and CANNOT be used to claim model improvement.
3. **`MISSING` Sources:** Any source without an executable file artifact is classified `MISSING`. Missing sources CANNOT be substituted with synthetic data.
