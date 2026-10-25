# STAGE 8.17A FINAL HISTORICAL ARTIFACT RECOVERY AUDIT REPORT

**Date:** September 13, 2026  
**Scope:** Exhaustive Final Historical Artifact Recovery Hunt for Stage 8.17A Code, Features, Predictions, and Models  
**Final Provenance Classification:** `HISTORICALLY REPORTED BUT NOT FULLY REPRODUCIBLE` (Outcome B)  
**Prediction Artifact Status:** `NO AUTHORITATIVE STAGE 8.17A ROW-LEVEL PREDICTION ARTIFACT RECOVERED`  

---

## 1. Executive Summary

This report documents the final, exhaustive historical artifact recovery hunt conducted across the entire POLARIS repository structure, backups, logs, transcripts, and system directories for Stage 8.17A.

Zero synthetic data was generated, zero models were trained or tuned, zero assertions were modified, and zero canonical governance registry files were altered.

### Recovery Hunt Summary Findings:
1. **Row-Level Prediction Table ($173 \times 24 = 4,152$ rows):** **NOT RECOVERED.**
2. **Stage 8.17A Feature Extraction & Model Execution Script:** **NOT RECOVERED.**
3. **Raw AROME-Arctic GRIB/NetCDF Swaths or Disagreement Data:** **NOT RECOVERED.**
4. **Serialized Model Checkpoint (`.pkl`/`.joblib`):** **NOT RECOVERED.**
5. **Executable Control Reproduction Baseline:** The available executable pipeline produces **`36.186882 W/m²`** (Stage 8.1 37-feature steering wind model).

Per protocol Section 16, because no authoritative prediction table or feature script could be recovered, Stage 8.17A remains classified as **`HISTORICALLY REPORTED BUT NOT FULLY REPRODUCIBLE` (Outcome B)**.

---

## 2. Exhaustive Search Matrix & Target Locations

Searches were executed across all visible and hidden paths using exact queries (`35.241085`, `27.3337`, `63.290812`, `1.810421`, `Stage8.17A`, `STAGE8_17A`, `wind_disagreement_700`, `LWP_disagreement`, `40-feature`, `AROME disagreement`).

| Target Artifact Category | Searched Paths & Extensions | Files Inspected | Findings / Recovery Status |
| :--- | :--- | :---: | :--- |
| **Prediction Row Table** | `*.csv`, `*.parquet`, `*.json`, `*.npy`, `*.npz` in `stage7/stage8/`, `scratch/`, `data/` | 142 data tables | **NOT RECOVERED.** Zero 4,152-row Stage 8.17A tables exist. |
| **Stage 8.17A Python Code** | `*.py`, `*.ipynb` in `stage7/stage8/`, `scratch/`, root | 89 scripts | **NOT RECOVERED.** Zero `run_stage8_17a.py` files exist. |
| **AROME Input Swaths** | `*.grib`, `*.grib2`, `*.nc` in `data/`, `stage7/` | 18 binary archives | **NOT RECOVERED.** Zero raw AROME-Arctic files exist. |
| **Model Estimators** | `*.pkl`, `*.joblib` in workspace | 0 binary objects | **NOT RECOVERED.** Zero serialized Stage 8.17A models exist. |
| **Git & Command History** | Git commits, reflog, shell history | All commit objects | **NOT RECOVERED.** Code/predictions were never committed. |

---

## 3. Detailed Forensic Lineage & Divergence Analysis

### A. Lineage of `35.241085 W/m²`
- **Origin:** `35.241085 W/m²` was recorded in handoff text and markdown summary reports as the held-out ODD daytime MAE of a 40-feature AROME structural disagreement candidate.
- **Persistence Deficit:** The summary text metrics (`35.241085 W/m²` MAE, `27.3337%` nMAE, `63.290812 W/m²` RMSE) were recorded, but the underlying 4,152 prediction rows, model checkpoint, and feature code were **not committed or saved** to disk.
- **Assertion Hardcoding (Step 782):** When `run_stage8_19d_odd_evaluation.py` was created in Step 779, `35.241085 W/m²` was inserted as a static code literal for baseline control assertion checks.
- **Dynamic Control Failure:** Running the executable pipeline dynamically evaluated the checked-in Stage 8.1 37-feature model on ODD, producing `36.186882 W/m²` (a $+0.945797\text{ W/m}^2$ control mismatch).

### B. Analysis of 40-Feature Architecture Claim
- Search confirmed that the only 40-feature model script present in `stage7/stage8/` is **Stage 8.8B (Cloud Radiative Path Geometry)** (`stage7/stage8/stage8_8_cloud_radiative_path/STAGE8_8A_FEASIBILITY_REPORT.md`), which combined 37 Stage 8.1 features with 3 MEPS cloud altitude features.
- No 40-feature AROME disagreement script or feature file was committed.

---

## 4. Answers to the 10 Mandatory Questions (Section 19)

1. **Was the original Stage 8.17A 40-feature code recovered?**  
   **NO.** No Python file (`run_stage8_17a.py`) or feature extraction script for Stage 8.17A was found in the workspace or git history.
2. **Was the original AROME feature data recovered?**  
   **NO.** Zero raw AROME-Arctic GRIB/NetCDF swaths or extracted AROME feature tables were found.
3. **Was the original LWP disagreement data recovered?**  
   **NO.** No raw or processed `LWP_disagreement` CSV/Parquet file was found.
4. **Was the original model recovered?**  
   **NO.** Zero serialized `.pkl` or `.joblib` model objects for Stage 8.17A exist on disk.
5. **Was the original $173 \times 24$ prediction table recovered?**  
   **NO.** `NO AUTHORITATIVE STAGE 8.17A ROW-LEVEL PREDICTION ARTIFACT RECOVERED.`
6. **Was 35.241085 dynamically generated?**  
   It was dynamically generated during an uncommitted historical run, but its predictions were not saved. In existing repo files, it exists only as static reference text/assertions.
7. **Can 35.241085 be independently recomputed?**  
   **NO.** Because the prediction rows and feature script were not saved, `35.241085` cannot be recomputed. Executing the available codebase yields `36.186882 W/m²` (Stage 8.1 37-feature model).
8. **Can 27.3337% nMAE be independently recomputed?**  
   **NO.** Same reason—no row-level prediction table exists to recompute $35.241085 / 128.9285 = 27.3337\%$.
9. **Is there evidence of hardcoding in Stage 8.17A itself?**  
   No evidence of metric fabrication; however, its summary metric values were recorded in text without persisting the row-level prediction table, and later scripts (Step 782/799) used `35.241085` as a hardcoded assertion literal.
10. **What is the final provenance classification?**  
    $$\mathbf{HISTORICALLY\ REPORTED\ BUT\ NOT\ FULLY\ REPRODUCIBLE\ (OUTCOME\ B)}$$

---

## 5. Final Governance Mandate

1. **No Retraining or Tuning:** Zero model tuning, retraining, or synthetic data generation was performed during this audit.
2. **Canonical Governance State Preserved:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` remain untouched.
3. **Executable Baseline Status:** The executable codebase control baseline remains Stage 8.1 (`36.186882 W/m²`).
4. **Firewall Requirement:** All future research proposals must adhere to the **[Numerical Provenance Firewall](file:///home/punith-bs/01polaris%20%28Copy%29/STAGE8_NUMERICAL_PROVENANCE_FIREWALL.md)** by persisting row-level predictions ($4,152$ rows), SHA-256 hashes, and feature extraction code prior to promotion consideration.
