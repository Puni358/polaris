# POLARIS — REPRODUCIBLE CONTROL FREEZE MANIFEST

**Date:** September 14, 2026  
**Freeze Status:** FROZEN NEW REPRODUCIBLE CONTROL BASELINE  
**Purpose:** Authoritative benchmark baseline for pending 21×21 Real-AROME Spatial Experiment  

---
## 1. Retirement of Historical Reference

> **GOVERNANCE STATEMENT:**
> *The historical 26.3668 W/m² Phase-10 control reference is retired from exact reproducibility claims because no authoritative model/prediction artifact survives. This new control is the reproducible benchmark for the pending 21×21 real-AROME candidate experiment.*

| Metric | Retired Historical Reference | Status |
| :--- | :---: | :---: |
| **MAE** | `26.3668` W/m² | RETIRED |
| **nMAE** | `20.4507`% | RETIRED |
| **RMSE** | `55.2513` W/m² | RETIRED |
| **Bias** | `-0.1291` W/m² | RETIRED |

---
## 2. New Frozen Control Metrics

| Metric | New Frozen Control Value | Scope |
| :--- | :---: | :--- |
| **24-hour Total MAE** | **`25.639318` W/m²** | All 4,152 EVEN horizon predictions |
| **24-hour Total nMAE** | **`19.8865`%** | Fixed normalizer `128.9284 W/m²` |
| **24-hour Total RMSE** | **`54.369219` W/m²** | All 4,152 EVEN horizon predictions |
| **24-hour Total Bias** | **`-5.043934` W/m²** | All 4,152 EVEN horizon predictions |
| **Daytime MAE** | `47.451469` W/m² | `2216` daytime rows |
| **Night MAE** | `0.672516` W/m² | `1936` forced zero night rows |

### Per-Fold OOF MAE Breakdown:
- Fold 1: MAE = `27.358628` W/m² (`35` origins)
- Fold 2: MAE = `21.591261` W/m² (`35` origins)
- Fold 3: MAE = `25.950014` W/m² (`35` origins)
- Fold 4: MAE = `29.003698` W/m² (`34` origins)
- Fold 5: MAE = `24.352342` W/m² (`34` origins)
- **Aggregate OOF MAE:** `25.651189` W/m²

---
## 3. Cryptographic Provenance & Hashes

- **Prediction Artifact CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)
- **Prediction CSV SHA256:** `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`
- **Control Script SHA256:** `dfa69828303342d65c38f10ef890b6328541eca343cfd9d689033430e45a72a7`
- **Freeze Contract JSON SHA256:** `a3c56ed184874e284e3b1d934c38317bfad6b41207e737779b0978074f502b06`

---
## 4. ODD Firewall & Execution Safeguard Audit

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`
- **Candidate Neural Training Performed:** `False` (0 weights trained)

---
## 5. Final Decision Outcome

### **`REPRODUCIBLE CONTROL FROZEN — READY FOR 21×21 REAL-AROME CANDIDATE`**