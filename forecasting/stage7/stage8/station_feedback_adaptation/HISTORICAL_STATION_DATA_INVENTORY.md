# POLARIS — Historical Station Data Inventory Report

**Location:** `stage7/stage8/station_feedback_adaptation/HISTORICAL_STATION_DATA_INVENTORY.md`  
**Purpose:** Comprehensive audit and inventory of all locally available historical station observation datasets to evaluate their capability to support station-specific solar forecasting model retraining.

---

## 1. Executive Summary

This inventory performs an empirical audit of all station observation data files within the workspace. Data availability, timestamps, date bounds, row counts, sampling frequencies, and column contents were verified directly against the underlying dataset files rather than inferred from file naming conventions.

### Key Observations:
1. **General Station Observations (Wind/Met):** Earliest verified record starts on **1985-04-18 12:00:00 UTC** (SMHI Abisko Station 188790) and extends to **2026-06-01 06:00:00 UTC** (over 41 years total time span).
2. **Target Solar Irradiance (`SW_IN`):** Verified ground-level shortwave solar irradiance observations at the target Mount Nuolja station (`SITES Abisko Nuolja AWS`, 702 m a.s.l.) exist for **2024-01-01 00:00:00** through **2025-12-31 23:50:00** (2 full calendar years, spanning 24 months / 105,264 10-minute records / 17,544 hourly records).
3. **Pre-2024 Historical Solar Data:** **None.** No ground-level solar irradiance (`SW_IN` / GHI) station data exists in the repository for years prior to 2024.
4. **Retraining Support Capability:** **PARTIAL.** The available 2024 and 2025 station solar data is sufficient to support 1-year vs 1-year cross-validation, 2-year combined fine-tuning, or station-specific recalibration. However, it cannot support multi-year pre-2024 historical retraining (e.g. 2018–2023) without acquiring external historical archives.

---

## 2. Verified Date Ranges & Time Span

| Scope | Earliest Timestamp | Latest Timestamp | Total Verified Time Span |
| :--- | :--- | :--- | :--- |
| **All Station Data (Includes SMHI Wind)** | **1985-04-18 12:00:00 UTC** | **2026-06-01 06:00:00 UTC** | **41 years, 1 month, 14 days** |
| **Solar Irradiance (`SW_IN`) at Target Station** | **2024-01-01 00:00:00 UTC+1** | **2025-12-31 23:50:00 UTC+1** | **2 years (24 full months)** |

---

## 3. Available Data Sources

The workspace contains historical observation data from three distinct station networks/sources:

1. **SITES (Swedish Infrastructure for Ecosystem Science)**  
   - *Station:* Abisko Scientific Research Station — Mount Nuolja Middle Station Automatic Weather Station (AWS), Lat 68.3621° N, Lon 18.7388° E, Altitude 702 m a.s.l.
   - *Data Level:* Level 2 Quality-Controlled 10-Minute & Processed Hourly Data.
   - *Variables:* Ground shortwave solar irradiance (`SW_IN`), Air temperature (`TA`), Relative humidity (`RH`), Soil temperature (`TS`), Precipitation (`PRECIP`), Snow depth (`D_SNOW`).

2. **SMHI (Swedish Meteorological and Hydrological Institute)**  
   - *Station:* Abisko Aut Station 188790, Lat 68.3538° N, Lon 18.8164° E, Altitude 392.2 m a.s.l.
   - *Data Level:* Quality-Controlled Historical Archive.
   - *Variables:* 10-meter Wind Speed (`ws_10m`) and 10-meter Wind Direction (`wd_10m`).

3. **NOAA ASOS / METAR**  
   - *Station:* ENEV (Evenes / Harstad-Narvik Airport), Lat 68.4913° N, Lon 16.6781° E, Altitude 27 m a.s.l.
   - *Data Level:* Hourly METAR Weather Observations (2024).
   - *Variables:* Cloud cover categories (`skyc1..4`), cloud base altitudes (`skyl1..4`), air temp, dew point, relative humidity, wind speed, surface pressure, visibility.

---

## 4. Itemized Dataset Inventory

### Dataset 1: SITES Nuolja L2 10-Minute Meteorological Data (2024)
- **Filename / Path:** [`data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv)
- **Date Range:** `2024-01-01 00:00:00` to `2024-12-31 23:50:00` (UTC+1)
- **Row Count:** 52,704 rows
- **Timestamp Resolution:** 10 minutes
- **Important Columns:** `TIMESTAMP`, `TA` (Air Temp °C), `RH` (Humidity %), `SW_IN` (Shortwave Solar Irradiance W/m²), `TS_-0.01m` (Soil Temp °C), `PRECIP` (Precipitation mm), `D_SNOW` (Snow Depth cm), `TA_STD`, `TS_STD`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN` measured by Apogee SP110 Pyranometer at 2.86m height)
- **Weather/Cloud Variables Present:** **YES** (Air Temp, Relative Humidity, Soil Temp, Precipitation, Snow Depth)

---

### Dataset 2: SITES Nuolja L2 10-Minute Meteorological Data (2025)
- **Filename / Path:** [`data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv)
- **Date Range:** `2025-01-01 00:00:00` to `2025-12-31 23:50:00` (UTC+1)
- **Row Count:** 52,560 rows
- **Timestamp Resolution:** 10 minutes
- **Important Columns:** `TIMESTAMP`, `TA`, `RH`, `SW_IN`, `TS_-0.01m`, `PRECIP`, `D_SNOW`, `TA_STD`, `TS_STD`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN` measured by Apogee SP110 Pyranometer)
- **Weather/Cloud Variables Present:** **YES** (Air Temp, Relative Humidity, Soil Temp, Precipitation, Snow Depth)

---

### Dataset 3: POLARIS Processed SITES Nuolja 2024 Hourly Multivariate Dataset
- **Filename / Path:** [`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv)
- **Date Range:** `2024-01-01 00:00:00` to `2024-12-31 23:00:00`
- **Row Count:** 8,784 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `TA`, `RH`, `SW_IN`, `TS_-0.01m`, `PRECIP`, `D_SNOW`, `TA_STD`, `TS_STD`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN` hourly mean)
- **Weather/Cloud Variables Present:** **YES** (Air Temp, Humidity, Soil Temp, Precipitation, Snow Depth)

---

### Dataset 4: POLARIS Processed SITES Nuolja 2025 Hourly Multivariate Dataset
- **Filename / Path:** [`data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_multivariate.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_multivariate.csv)
- **Date Range:** `2025-01-01 00:00:00` to `2025-12-31 23:00:00`
- **Row Count:** 8,760 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `TA`, `RH`, `SW_IN`, `TS_-0.01m`, `PRECIP`, `D_SNOW`, `TA_STD`, `TS_STD`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN` hourly mean)
- **Weather/Cloud Variables Present:** **YES** (Air Temp, Humidity, Soil Temp, Precipitation, Snow Depth)

---

### Dataset 5: POLARIS Processed SITES Nuolja 2024 Hourly 5-Variable Subset
- **Filename / Path:** [`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv)
- **Date Range:** `2024-01-01 00:00:00` to `2024-12-31 23:00:00`
- **Row Count:** 8,784 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `TA`, `RH`, `SW_IN`, `TS_-0.01m`, `PRECIP`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN`)
- **Weather/Cloud Variables Present:** **YES** (Air Temp, Humidity, Soil Temp, Precipitation)

---

### Dataset 6: POLARIS SITES Nuolja 2024 Hourly Target Series (`SW_IN`)
- **Filename / Path:** [`(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv`](file:///home/punith-bs/01polaris%20%28Copy%29/%28avg%201hr%29POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN%281%29.csv)
- **Date Range:** `2024-01-01 00:00:00` to `2024-12-31 23:00:00`
- **Row Count:** 8,784 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `SW_IN`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN`)
- **Weather/Cloud Variables Present:** **NO** (Target solar irradiance series only)

---

### Dataset 7: POLARIS SITES Nuolja 2025 Hourly Target Series (`SW_IN`)
- **Filename / Path:** [`data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv)
- **Date Range:** `2025-01-01 00:00:00` to `2025-12-31 23:00:00`
- **Row Count:** 8,760 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `SW_IN`
- **Actual Solar/Irradiance Present:** **YES** (`SW_IN`)
- **Weather/Cloud Variables Present:** **NO** (Target solar irradiance series only)

---

### Dataset 8: SMHI Station 188790 (Abisko Aut) Full Historical Wind Speed Archive
- **Filename / Path:** [`research/wind_a2/smhi_188790_ws_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_ws_full.csv)
- **Date Range:** `1985-04-18 12:00:00` to `2026-06-01 06:00:00` (UTC)
- **Row Count:** 157,844 rows
- **Timestamp Resolution:** Hourly (10-minute mean sampled hourly)
- **Important Columns:** `Datum`, `Tid (UTC)`, `Vindhastighet` (Wind Speed m/s), `Kvalitet`
- **Actual Solar/Irradiance Present:** **NO**
- **Weather/Cloud Variables Present:** **YES** (10m Wind Speed)

---

### Dataset 9: SMHI Station 188790 (Abisko Aut) Full Historical Wind Direction Archive
- **Filename / Path:** [`research/wind_a2/smhi_188790_wd_full.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_188790_wd_full.csv)
- **Date Range:** `1985-04-18 12:00:00` to `2026-06-01 06:00:00` (UTC)
- **Row Count:** 150,247 rows
- **Timestamp Resolution:** Hourly (10-minute mean sampled hourly)
- **Important Columns:** `Datum`, `Tid (UTC)`, `Vindriktning` (Wind Direction °), `Kvalitet`
- **Actual Solar/Irradiance Present:** **NO**
- **Weather/Cloud Variables Present:** **YES** (10m Wind Direction)

---

### Dataset 10: SMHI Abisko Target 2024 Wind Data
- **Filename / Path:** [`research/wind_a2/smhi_abisko_target_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/research/wind_a2/smhi_abisko_target_2024.csv)
- **Date Range:** `2024-01-01 00:00:00+00:00` to `2024-12-31 23:00:00+00:00`
- **Row Count:** 8,690 rows
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `dt`, `ws_10m`, `quality`, `wd_10m`
- **Actual Solar/Irradiance Present:** **NO**
- **Weather/Cloud Variables Present:** **YES** (10m Wind Speed and Direction)

---

### Dataset 11: ENEV Airport METAR Hourly Station Observations (2024)
- **Filename / Path:** [`data/enev_metar_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/enev_metar_2024.csv)
- **Date Range:** `2024-01-01 00:50:00` to `2024-12-30 23:50:00`
- **Row Count:** 8,746 rows
- **Timestamp Resolution:** Hourly METAR
- **Important Columns:** `station`, `valid`, `tmpf`, `dwpf`, `relh`, `drct`, `sknt`, `skyc1..skyc4` (Cloud coverage), `skyl1..skyl4` (Cloud base heights in ft), `mslp`, `vsby`
- **Actual Solar/Irradiance Present:** **NO**
- **Weather/Cloud Variables Present:** **YES** (Cloud cover levels, cloud base heights, temp, humidity, wind)

---

### Dataset 12: Nuolja Terrain Horizon & Astronomical Solar Features (2024 / 2025)
- **Filename / Path:** [`stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv) / [`data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv)
- **Date Range:** `2024-01-01 00:00:00` to `2024-12-31 23:00:00` (2024) / `2025-01-01 00:00:00` to `2025-12-31 23:00:00` (2025)
- **Row Count:** 8,784 rows (2024) / 8,760 rows (2025)
- **Timestamp Resolution:** 1 hour
- **Important Columns:** `TIMESTAMP`, `solar_elevation`, `solar_azimuth`, `clearsky_ghi`, `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`
- **Actual Solar/Irradiance Present:** **NO** (Contains calculated clear-sky GHI, not ground measurements)
- **Weather/Cloud Variables Present:** **NO** (Pure astronomical/topographical geometry calculations)

---

## 5. Verification of Pre-2024 Historical Station Data

- **General Station Observations (Non-Solar):** **YES.** SMHI Station 188790 (Abisko Aut) contains continuous wind observations starting in **April 1985** (over 38 years of pre-2024 history).
- **Target Station Solar Irradiance (`SW_IN`):** **NO.** The target station dataset (`SITES Abisko Nuolja AWS`) contains solar irradiance observations **only for 2024 and 2025**. There are no pre-2024 solar irradiance ground measurements present anywhere in the workspace.

---

## 6. Feasibility Evaluation for Station-Specific Retraining

1. **Available Retraining Windows:**
   - The workspace provides **two complete calendar years (2024 and 2025)** of high-resolution 10-minute and 1-hour ground solar irradiance observations (`SW_IN`).
   - Total solar observations count: **105,264 10-minute records** / **17,544 1-hour records**.

2. **Feasible Retraining Strategies:**
   - **Cross-Validation / Fine-Tuning:** The 2024 dataset can serve as a training split and 2025 as a holdout validation split (or vice-versa), enabling model tuning, bias correction, and station-specific adaptation.
   - **Station-Specific Recalibration:** Sufficient data exists to fit terrain shading margins, clear-sky scaling, or error residual post-processors on 2024/2025 station observations.

3. **Limitations & Non-Feasible Scenarios:**
   - **Multi-Year Pre-2024 Retraining:** Cannot be performed using existing repository files alone because ground solar irradiance data for 2018–2023 is not available locally.
   - **Cloud Base Ground Observations at Nuolja:** The Nuolja station measures `SW_IN`, `TA`, `RH`, `TS`, `PRECIP`, `D_SNOW`, but does not measure direct DNI/DHI or ceilometer cloud base heights. Auxiliary cloud base data is available from ENEV airport METAR or MEPS/AROME numerical weather forecasts.

---

EARLIEST VERIFIED DATA: 1985-04-18 12:00:00
LATEST VERIFIED DATA: 2026-06-01 06:00:00
TOTAL VERIFIED SPAN: 41 years, 1 month, 14 days (1985-2026 overall) / 2 years (2024-2025 station solar SW_IN)
DATA AVAILABLE BEFORE 2024: YES (SMHI wind 1985-2023) / NO (SITES solar SW_IN)
STATION-SPECIFIC RETRAINING DATA: PARTIAL
MOST IMPORTANT DATASET: data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv & data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv
FILES INSPECTED: data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv, data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv, data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv, data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_multivariate.csv, data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv, (avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv, data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv, research/wind_a2/smhi_188790_ws_full.csv, research/wind_a2/smhi_188790_wd_full.csv, research/wind_a2/smhi_abisko_target_2024.csv, data/enev_metar_2024.csv, stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv, data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv
