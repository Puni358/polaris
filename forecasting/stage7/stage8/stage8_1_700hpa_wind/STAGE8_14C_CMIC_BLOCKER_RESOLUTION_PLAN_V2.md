# POLARIS STAGE 8.14C — EUMETSAT NWC SAF PPS CMIC BLOCKER RESOLUTION PLAN (REVISION V2)

**Stage:** POLARIS Stage 8.14C — EUMETSAT NWC SAF PPS CMIC Blocker Resolution Plan  
**Status:** `REVISED V2 — SCIENTIFICALLY HARDENED`  
**Current Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  
**Current Daytime nMAE:** `28.0688%`  
**Forecasting Experiment Authorized:** `NO`  
**Date:** September 13, 2026  

---

## Executive Summary & Scientific Hardening Context

Stage 8.14C Revision V2 incorporates the findings of the **Scientific Hardening Audit** performed on the Stage 8.14C Blocker Resolution Plan V1.

### Key Hardening Corrections Incorporated into V2:

1. **Rejection of CTTH as an Optical Fallback:** Cloud Top Pressure (`ctth_press`) and Cloud Top Temperature (`ctth_temp`) are **strongly NWP-derived profile inversions** (RTOV radiative transfer mapping of 10.8 $\mu\text{m}$ radiances against MEPS/ECMWF temperature/humidity profiles). Using CTTH as a polar-night fallback re-introduces the rejected Stage 8.8 MEPS vertical cloud geometry under a satellite name. **V2 explicitly prohibits CTTH as a fallback for novel optical transmissivity (`cot`).**
2. **Prohibition of COT Zero-Imputation during Polar Night:** Setting missing optical retrievals to $\text{COT} = 0$ during polar night ($SZA > 84^\circ$) is physically false: $\text{COT} = 0$ represents a crystal-clear, transparent atmosphere, whereas an Arctic polar-night sky may be overcast with dense stratus. **V2 explicitly prohibits zero-imputation of COT/CER.**
3. **Introduction of Observed Thermal Cloud Mask (`cma`):** The primary non-optical satellite variable for polar-night/low-sun conditions is `cma` (Cloud Mask), derived 24/7/365 from multispectral thermal IR channels (10.8 $\mu\text{m}, 12.0\ \mu\text{m}$) without NWP vertical profile dependency.
4. **Correction of the Coverage Gate:** The full-year 347-origin benchmark contains 57 polar-night origins ($16.4\%$). Daylight optical retrievals (`cot`, `eff_radius`) can **never** exceed $83.6\%$ (290 / 347 origins). V2 splits the coverage gate into an explicit **Daylight Origin Optical Gate ($\ge 90\%$ of daylight origins)** and a **347-Origin Dual-Branch Benchmark Gate**.

---

## Hardened 6-Pillar Blocker Resolution Plan

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          HARDENED 6-PILLAR RESOLUTION PLAN                             │
├───────────────────┬───────────────────┬───────────────────┬────────────────────────┤
│ 1. ARCHIVE        │ 2. EMPIRICAL      │ 3. CAUSAL         │ 4. OBSERVATIONAL       │
│    COMPLETENESS   │    COVERAGE       │    AVAILABILITY   │    NOVELTY             │
│ (Bulk EUMETSAT    │ (Daylight Optical │ (Verified T_pub   │ (Pure COT vs           │
│  Data Store Order)│  >=90% Gate)      │  <= t0 Timestamp) │  MEPS cloud_frac)      │
├───────────────────┴───────────────────┴───────────────────┴────────────────────────┤
│ 5. POLAR-NIGHT HANDLING               │ 6. OPERATIONAL REPRODUCIBILITY          │
│ (Dual-Branch Architecture: Optical    │ (Automated Python Ingestion & Grid     │
│  COT Daylight vs CMA Thermal Night)   │  Upwind Vector Extraction Pipeline)    │
└───────────────────────────────────────┴────────────────────────────────────────┘
```

---

### Pillar 1: Archive Completeness (EUMETSAT Data Store Bulk Acquisition)
- **Problem in V1:** Open HTTP THREDDS catalog (`thredds.met.no`) maintains an incomplete retrospective 2024 archive for L2 CMIC netCDF granules over Lapland across the 347 origins.
- **V2 Solution:**
  - Submit an explicit retrospective bulk order to the **EUMETSAT Data Store** (Data Centre / Data Tailor) for MetOp-B/C AVHRR and Suomi-NPP/NOAA-20 VIIRS NWC SAF PPS L2 CMIC products across all 366 days of 2024 covering SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$).
  - Alternatively, execute local containerized NWC SAF PPS v2024 software over archived 2024 Level-1b polar orbiter swaths to generate a 100% complete 2024 CMIC granule archive.

---

### Pillar 2: Empirical Coverage (Daylight Optical Gate vs Benchmark Gate)
- **Problem in V1:** Requiring $\ge 90\%$ overall coverage on optical COT across all 347 origins was physically impossible due to polar night ($SZA > 84^\circ$ covers 57 origins / $16.4\%$).
- **V2 Solution:** Predeclare two distinct, non-overlapping coverage criteria:
  1. **Daylight Origin Optical Gate:** $\ge 90\%$ usable optical retrievals within the 290 **Daylight Origins** ($SZA \le 84^\circ$).
  2. **Benchmark Completeness Gate:** 100% of 347 origins must receive an auditable state classification in `STAGE8_14C_CMIC_ORIGIN_STATE_SCHEMA.csv` without dropping origins or violating the locked 347-origin protocol.

---

### Pillar 3: Causal Availability ($T_{pub} \le t_0$ Timestamp Verification)
- **Problem in V1:** Physical acquisition time $T_{acq} \le t_0$ was used without verifying public file publication availability $T_{pub}$.
- **V2 Solution:**
  - Audit operational logs for EARS-AVHRR / MET Norway local direct-readout reception feeds.
  - Require empirical proof that $T_{pub} \le t_0$ for every origin used in calibration or evaluation. Origins where $T_{pub} > t_0$ are classified as `CAUSALITY_REJECTED`.

---

### Pillar 4: Observational Novelty (Pure COT vs MEPS `cloud_frac`)
- **V2 Hardened Specification:**
  - Ingest `cot` (Cloud Optical Thickness) as the primary novel satellite feature, which directly measures physical radiative attenuation ($0 \dots 100+$).
  - Explicitly exclude `ctth_press`, `ctth_temp`, and `ctth_alti` from feature sets to prevent re-introducing NWP-derived cloud profile dependencies tested and rejected in Stage 8.8.
  - Verify that satellite COT provides non-redundant information beyond the Stage 8.1 37-feature baseline (`fc_cloud_cover`, `lwp_latest`, `iwp_latest`, `u700`, `v700`).

---

### Pillar 5: Polar-Night & Low-Sun Handling (Dual-Branch Architecture)
- **Problem in V1:** Proposed zero-imputation of COT/CER or fallback to NWP-derived `ctth_temp`/`ctth_press`.
- **V2 Solution:**
  - **Prohibit Zero-Imputation:** Optical retrievals returning fill values (-9999) during polar night ($SZA > 84^\circ$) must NOT be set to $\text{COT}=0$.
  - **Dual-Branch Architecture:**
    - **Daylight Branch ($SZA \le 84^\circ$):** Extract `cot`, `eff_radius`, `phase`, `cma`, and spatial optical gradients along the $U_{700}/V_{700}$ steering wind vector.
    - **Polar-Night / Low-Sun Branch ($SZA > 84^\circ$):** Extract 24/7 thermal IR observations (`cma` Thermal Cloud Mask) and explicit binary indicator flags (`is_polar_night = 1`). Mask optical channels as NaN with tree-based split handling, preserving complete benchmark compliance.

---

### Pillar 6: Operational Reproducibility & Pipeline Ingestion
- **V2 Solution:**
  - Develop an automated netCDF extraction script (`extract_cmic_features_v2.py`) to parse $1.0\text{ km}$ polar stereographic grids around Nuolja ($100\text{ km} \times 100\text{ km}$ domain).
  - Compute spatial mean, max, and upwind directional averages aligned with $U_{700}/V_{700}$ steering vectors.
  - Output an auditable 347-row feature table with strict schema validation.

---

## 6-State Origin Discrete Classification Schema

Every benchmark origin is assigned an explicit, auditable discrete state:

| Discrete State | Condition & Criteria | Feature Pipeline Handling |
| :--- | :--- | :--- |
| **`VALID_OPTICAL`** | $SZA \le 84^\circ$, granule available, $T_{pub} \le t_0$, valid optical `cot`. | Full Daylight Optical Branch (`cot`, `eff_radius`, `cma`, upwind optical gradients). |
| **`POLAR_NIGHT`** | $SZA > 84^\circ$ (Nov 25 – Jan 15). Optical channels return fill value (-9999). | Thermal Branch (`cma` Thermal Cloud Mask, `is_polar_night = 1`, optical NaNs masked). |
| **`LOW_SUN_INVALID`** | $80^\circ < SZA \le 84^\circ$ where optical retrieval fails due to low signal/stray light. | Flagged as low-sun invalid; thermal branch fallback. |
| **`NO_GRANULE`** | No satellite swath granule available over Nuolja within forecast origin window. | Classified as missing granule; MEPS baseline fallback. |
| **`QUALITY_REJECTED`** | Granule present, but pixel flagged for snow/ice surface corruption or $\theta_s > 65^\circ$. | Flagged quality rejected. |
| **`CAUSALITY_REJECTED`** | Granule present and valid, but publication timestamp $T_{pub} > t_0$. | Operationally non-causal. |

---

## Gate Upgrade Requirements for Future Research

Before CMIC can be upgraded from `CONDITIONAL` to `GO` in a future stage:

1. **Archive Completeness:** 100% of 347 benchmark origins enumerated.
2. **Daylight Optical Coverage:** $\ge 90\%$ usable optical retrievals within daylight origins ($SZA \le 84^\circ$).
3. **Causality Verification:** $100\%$ verified $T_{pub} \le t_0$ across usable origins.
4. **Novelty Check:** Established non-redundancy of COT relative to Stage 8.1 37 features.
5. **No Experiment Authorized Now:** Stage 8.14C remains a feasibility audit; zero forecasting experiments are authorized.
