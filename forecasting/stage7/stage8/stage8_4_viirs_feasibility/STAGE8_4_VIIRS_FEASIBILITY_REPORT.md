# STAGE 8.4 — VIIRS EMPIRICAL FILE-LEVEL FEASIBILITY EXTRACTION REPORT

**Project:** POLARIS  
**Stage:** STAGE 8.4 VIIRS EMPIRICAL FEASIBILITY EXTRACTION  
**Date:** September 12, 2026  
**Status:** **FEASIBILITY ONLY — AUDIT COMPLETE**  
**Classification:** **CONDITIONAL**

---

## 1. Executive Summary & Governance Compliance

Stage 8.4 conducted an empirical granule-level search across the NASA LAADS / Earthdata CMR archive for VIIRS Level-2 Cloud Property observations (`CLDPROP_L2_VIIRS_SNPP`, `CLDPROP_L2_VIIRS_NOAA20`, `CLDMSK_L2_VIIRS_NOAA21`) over SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$) across all 347 benchmark forecast origins of 2024.

* **Forecasting Experiment Run:** **NO**
* **Cross-Validation Executed:** **NO**
* **ODD Target Access:** **NO**
* **ODD Predictions Generated:** **NO**
* **ODD Metrics Evaluated:** **NO**
* **Hyperparameter Tuning:** **NO**
* **Active Champion Preserved:** **YES** (**Stage 8.1 U700+V700 Steering Wind Model**, ODD MAE = `36.188657 W/m²`, nMAE = `28.0688%`)

---

## 2. Empirical Archive Enumeration Results

| Metric / Scope | Suomi-NPP | NOAA-20 | NOAA-21 | Constellation Union |
| :--- | :---: | :---: | :---: | :---: |
| **Actual Usable Origins** | **90 / 347** | **135 / 347** | **0 / 347** | **225 / 347** |
| **Empirical Usable Rate** | 25.9% | 38.9% | 0.0% | **64.8%** |

### Breakdown by Criteria
* **Physical Causal Origins ($t_{acq} \le t_0$):** **346 / 347** (100.0%)
* **Operationally Causal Origins ($t_{pub} \le t_0$):** **0 / 347** (0.0% for standard science L2 files; delay = 3–8 hours)
* **Valid Cloud Optical Thickness (COT):** **225**
* **Valid Cloud Effective Radius (CER):** **225**
* **Valid Cloud Phase:** **346**
* **Quality Valid ($d \le 50\text{ km}$):** **346**

---

## 3. Reconciliation with Stage 6.2 Empirical Finding

* **Stage 6.2 Result:** 332 AVHRR vs 2 VIIRS observations in MET Norway THREDDS catalog.
* **Stage 8.4 Empirical Reconciliation:** EXPLAINED. MET Norway's direct-reception Scandinavian antenna server ingested primarily AVHRR L1b/L2 swaths in 2024, whereas NASA LAADS DAAC maintains the global science archive for Suomi-NPP and NOAA-20. VIIRS overpasses occur regularly (~42 passes/day across the constellation).

---

## 4. Practical Extraction & Operational Assessment

* **Total Files / Granules Required:** ~2,500 6-minute swath granules for 2024.
* **Storage Burden:** ~25–40 GB total HDF5 volume.
* **Operational Dissemination Delay:** Standard NASA LAADS L2 science products (`CLDPROP_L2_VIIRS_*`) exhibit a 3 to 8 hour publication delay. Real-time operation requires NASA LANCE NRT feeds (`CLDPROP_L2_VIIRS_*_NRT`), which have 1–3 hour latency.

---

## 5. Classification & Recommendation

* **VIIRS Classification:** **CONDITIONAL**
* **Forecasting Experiment Justified:** **CONDITIONAL** (High physical value for offline diagnostic evaluation, but dissemination latency requires careful operational framing).
