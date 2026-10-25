# POLARIS STAGE 8.14C — EUMETSAT NWC SAF PPS CMIC BLOCKER RESOLUTION PLAN

**Stage:** POLARIS Stage 8.14C — EUMETSAT NWC SAF PPS CMIC Feasibility Audit  
**Status:** `CMIC REMAINS CONDITIONAL — NO FORECASTING EXPERIMENT AUTHORIZED`  
**Current Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`  
**Current Daytime nMAE:** `28.0688%`  
**Date:** September 13, 2026  

---

## Executive Summary

Stage 8.14C evaluated **EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)** as the single strongest candidate data source identified in POLARIS research. The audit confirmed that CMIC Cloud Optical Thickness (`cot`) is **genuinely information-novel** relative to the 37 features of the frozen Stage 8.1 Champion and directly targets the dominant Stage 8.14A error phenotype (cloud optical attenuation and missed clearing events).

However, CMIC cannot be upgraded to `GO` at this time because of three critical blocking constraints:
1. **Incomplete Open 2024 Archive:** The open HTTP THREDDS catalog (`thredds.met.no`) does not maintain a complete, contiguous 2024 retrospective archive for Level-2 CMIC netCDF granules over Lapland across all 347 origins.
2. **Polar-Night Optical Fill Values:** Optical solar-channel retrievals (`cot`, `eff_radius`, `lwp`, `iwp`) return fill values during Arctic polar night ($SZA > 84^\circ$, Nov 25 – Jan 15), capping usable benchmark coverage at **60.5% of origins (210 / 347)**.
3. **Unverified Historical Publication Latency ($T_{pub}$):** While operational NRT feeds take $\approx 30 \dots 60\text{ minutes}$, historical file timestamps on open HTTP THREDDS servers do not empirically verify $T_{pub} \le t_0$ for all origins.

This document outlines the exact 4-step technical resolution plan required before CMIC can be upgraded to `GO` in future research.

---

## 4-Step Technical Resolution Plan

### Step 1: Complete 2024 Bulk Archive Acquisition
- **Requirement:** Acquire or process complete 2024 Level-2 CMIC netCDF granules for all 347 benchmark origins covering SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$).
- **Action Plan:**
  - Submit a custom retrospective bulk ordering request to the **EUMETSAT Data Store** (Data Centre / Data Tailor) for MetOp-B/C AVHRR and Suomi-NPP/NOAA-20 VIIRS NWC SAF PPS L2 CMIC products for 2024.
  - Alternatively, execute local containerized NWC SAF PPS v2024 processing over archived 2024 Level-1b polar orbiter swaths to generate a 100% complete 2024 CMIC dataset.

### Step 2: Empirical Publication Timestamp ($T_{pub}$) Audit
- **Requirement:** Establish empirical proof that $T_{pub} \le t_0$ for every origin used in calibration and evaluation.
- **Action Plan:**
  - Audit exact header metadata and file arrival logs for EARS-AVHRR / MET Norway operational feeds.
  - Construct an explicit 347-origin timestamp verification table mapping $T_{acq}$, $T_{proc}$, and $T_{pub}$ relative to forecast origin $t_0$.

### Step 3: Daylight / Polar-Night Hybrid Pipeline Architecture
- **Requirement:** Resolve optical retrieval fill values during low-sun / polar-night origins ($SZA > 84^\circ$).
- **Action Plan:**
  - Implement a dual-mode feature pipeline:
    - **Daylight Mode ($SZA \le 84^\circ$):** Ingest `cot`, `eff_radius`, `phase`, and `cma`.
    - **Polar-Night / Low-Sun Mode ($SZA > 84^\circ$):** Gracefully mask optical features and fallback to thermal-IR 24/7 channels (`ctth_temp`, `ctth_press`) or zero-imputation without dropping origins or causing missing-feature NaNs.

### Step 4: Programmatic Operational Pipeline Specification
- **Requirement:** Define a fully reproducible, automated Python ingestion script.
- **Action Plan:**
  - Write an automated netCDF extraction script (`extract_cmic_features.py`) to parse $1.0\text{ km}$ polar stereographic grids around Nuolja ($100\text{ km} \times 100\text{ km}$ domain), computing spatial mean, max, and upwind directional averages aligned with $U_{700}/V_{700}$ steering vectors.

---

## Summary of Gate Conditions for `GO` Upgrade

| Requirement | Current Status | Target for `GO` Upgrade | Resolution Path |
| :--- | :---: | :---: | :--- |
| **2024 Benchmark Archive** | Incomplete (THREDDS gaps) | 100% complete 347-origin archive | EUMETSAT Data Store bulk order or local NWC SAF PPS run |
| **Usable Origin Coverage** | 60.5% (210 / 347) | $\ge 90\%$ usable origins | Polar-night hybrid pipeline handling $SZA > 84^\circ$ fill values |
| **Publication Causality ($T_{pub} \le t_0$)** | Unverified for historical HTTP | $100\%$ verified $T_{pub} \le t_0$ | EARS-PPS operational log audit |
| **Operational Reproducibility** | Conditional | Automated Python extraction pipeline | Standardized `extract_cmic_features.py` script |

---

## Governance & Action Boundary

- **Stage 8.14C Decision:** `CONDITIONAL`
- **Forecasting Experiment Authorized:** `NO`
- **Operational Champion:** `UNCHANGED — STAGE 8.1 700 hPa STEERING WIND MODEL`
- **Daytime nMAE:** `28.0688%`

> **Note:** Only after all 4 steps in this resolution plan are completed and verified by an independent audit may a future forecasting experiment (Stage 8.15) be formally proposed.
