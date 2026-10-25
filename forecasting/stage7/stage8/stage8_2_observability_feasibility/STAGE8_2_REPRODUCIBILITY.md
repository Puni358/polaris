# STAGE 8.2 — REPRODUCIBILITY MANIFEST

**Project:** POLARIS  
**Stage:** STAGE 8.2 OBSERVABILITY FEASIBILITY AUDIT  
**Date:** September 12, 2026  
**Environment:** Python 3.10+ (`.venv`), pandas, numpy, netCDF4, json  
**Audit Executable:** `stage7/stage8/stage8_2_observability_feasibility/generate_stage8_2_audit.py`  

---

## 1. Benchmark & Location Specification

* **Target Station:** SITES Nuolja Middle Station
* **Latitude:** $68.362074^\circ\text{N}$
* **Longitude:** $18.738752^\circ\text{E}$
* **Elevation:** $675\text{ m a.s.l.}$
* **Benchmark Partition:** 347 clean origins ($2024\text{-}01\text{-}20 \dots 2024\text{-}12\text{-}31$)
* **Partition Split:** 174 EVEN origins (train/calibration), 173 ODD origins (held-out test)
* **Target Metric:** Daytime Normalized Mean Absolute Error ($\text{nMAE}_{\text{day}}$)

---

## 2. Frozen Champion Preservation

* **Active Frozen Champion:** Stage 8.1 U700+V700 Steering Wind Model
* **Held-out ODD Daytime MAE:** $36.188657\text{ W/m}^2$
* **Held-out ODD Daytime nMAE:** $28.0688\%$
* **Held-out ODD Daytime RMSE:** $64.219495\text{ W/m}^2$
* **Governance Status:** **FROZEN & UNTOUCHED**. Zero model training, zero CV runs, zero ODD access, zero hyperparameter tuning.

---

## 3. Data Query & Causality Rules

1. **Physical Causality Rule:** $t_{\text{observation}} \le t_0$ (Observation acquisition time must precede or equal forecast origin $t_0$).
2. **Operational Causality Rule:** $t_{\text{dissemination}} \le t_0$ (Product publication time must precede or equal forecast origin $t_0$).
3. **Spatial Matching Rule:** Geodesic Haversine distance $d \le 50.0\text{ km}$ from SITES Nuolja station.
4. **Missingness Handling:** Fill values (e.g. `-9999.0` or `255`) and polar-night optical gaps ($SZA > 84^\circ$) are explicitly tagged and tracked as unobserved, never forward-filled or backward-filled from future observations.

---

## 4. Verification Command

To verify and reproduce all Stage 8.2 audit CSVs, JSONs, and metrics:

```bash
.venv/bin/python stage7/stage8/stage8_2_observability_feasibility/generate_stage8_2_audit.py
```

All generated files are output atomically to:
`stage7/stage8/stage8_2_observability_feasibility/`
