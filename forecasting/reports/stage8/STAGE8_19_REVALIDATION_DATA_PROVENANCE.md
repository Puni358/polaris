# STAGE 8.19 REVALIDATION DATA PROVENANCE AUDIT

**Date:** September 13, 2026  
**Scope:** Exhaustive Search & Causality Verification for Real ABIS/SWEPOS & AROME-Arctic Input Artifacts  
**Audit Status:** PROVENANCE BLOCKER IDENTIFIED — REQUIRED REAL INPUT ARTIFACTS ABSENT  

---

## 1. Input Data Search Summary

Per Step 1 of the Stage 8.19 Clean Revalidation Protocol, an exhaustive search was conducted across all project directories, subfolders, and artifact paths for authentic real input data.

### Searched Directories & Locations:
- `/home/punith-bs/01polaris (Copy)/data/`
- `/home/punith-bs/01polaris (Copy)/stage7/`
- `/home/punith-bs/01polaris (Copy)/stage7/stage8/`
- `/home/punith-bs/01polaris (Copy)/scratch/`
- Root workspace directory and subdirectories

---

## 2. Detailed Findings by Data Source

### A. ABIS / SWEPOS GNSS ZTD Observations

| Target Search Item | Required Format / Source | Findings in Workspace | Status |
| :--- | :--- | :--- | :---: |
| **Raw GNSS ZTD Observations** | E-GVAP COST-716 / SWEPOS station files | Zero raw ZTD observation files found. | **ABSENT** |
| **ABIS Station Data** | Hourly/sub-hourly tropospheric delay CSV/ASCII | Zero ABIS station data files found. | **ABSENT** |
| **Metadata & Timestamps** | Processing / publication timestamp logs | Zero metadata files found. | **ABSENT** |
| **2024 Archived Observations** | Continuous 2024 SWEPOS GNSS archive | Zero 2024 GNSS archive files found. | **ABSENT** |

**Conclusion for ABIS:** No real raw ABIS or SWEPOS GNSS ZTD observation artifact exists in the project repository.

---

### B. AROME-Arctic Forecast Files

| Target Search Item | Required Format / Source | Findings in Workspace | Status |
| :--- | :--- | :--- | :---: |
| **AROME-Arctic Forecast Swaths** | GRIB / GRIB2 / NetCDF files | Zero AROME-Arctic forecast files found. | **ABSENT** |
| **Initialization & Valid Times** | Model run reference timestamps | Zero run manifests found. | **ABSENT** |
| **Required Variables** | 700 hPa winds ($U, V$) & LWP fields | Zero GRIB/NetCDF variable tables found. | **ABSENT** |

**Conclusion for AROME-Arctic:** No real raw AROME-Arctic forecast files exist in the project repository.

---

## 3. Protocol Enforcement & Synthetic Prohibition

Per Protocol Instructions (Absolute Prohibitions & Step 1):

1. **Synthetic Data Prohibition:**  
   Synthetic ABIS data generation (`np.random.seed(819)`) and synthetic AROME-Arctic data generation (`np.random.seed(817)`) are **STRICTLY PROHIBITED**. Synthetic data CANNOT be substituted for missing real inputs.

2. **Mandatory Protocol Stop Condition:**  
   > *"If a required real input cannot be located, STOP and report the missing artifact. Do NOT substitute synthetic data."*

Because both required real data sources (ABIS/SWEPOS GNSS ZTD and AROME-Arctic forecast files) are **ABSENT**, real feature extraction for `abis_ztd_latest`, `abis_ztd_trend_3h`, `wind_disagreement_700`, and `LWP_disagreement` cannot be executed.

Execution of Step 4 (feature extraction) is blocked by real data non-existence.
