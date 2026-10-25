# POLARIS PRE-TRAINING LOCAL SPATIAL 3X3 AUDIT REPORT

**Date:** September 14, 2026  
**Audit Verdict:** **`PRE-TRAINING AUDIT PASS — AUTHORIZED FOR SINGLE CANDIDATE EXPERIMENT`**  
**Training Status:** `MODEL TRAINING NOT YET STARTED`  

---
## 1. Model Architecture & Parameter Verification

- **Model Class:** `PreRegisteredLocalSpatial3x3Model`
- **Trainable Parameters:** `15,633` (Expected: `15,633`) -> `MATCH (VERIFIED)`
- **Forward Pass Check:** `PASSED`
- **Backward Pass Check:** `PASSED`

---
## 2. Cached Tensor & Control Baseline Verification

- **EVEN Forecast Origins:** `173 / 173` verified
- **Control Predictions CSV SHA256:** `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366` (`VERIFIED`)
- **Control Daytime MAE:** `47.451469 W/m²`
- **Control Daytime nMAE:** `36.8045 %`
- **Control Daytime RMSE:** `74.376601 W/m²`

---
## 3. Pre-Training Programmatic Checklist (15 Items)

| Check | Item Description | Status |
| :---: | :--- | :---: |
| `1_` | xact parameter count 15633 | `PASSED` |
| `2_` | orward pass shape correct | `PASSED` |
| `3_` | ackward pass gradients valid | `PASSED` |
| `4_` | ven origins count 173 | `PASSED` |
| `5_` | ached tensors available 173 | `PASSED` |
| `6_` | ocal patch shape 24 11 3 3 | `PASSED` |
| `7_` | tation anchor center grid 209 548 | `PASSED` |
| `8_` | ero odd origins accessed | `PASSED` |
| `9_` | ero network fetches | `PASSED` |
| `10` | no new features extracted | `PASSED` |
| `11` | g6 control csv sha256 verified | `PASSED` |
| `12` | g6 control metrics verified | `PASSED` |
| `13` | fixed daytime normalizer 128 9284 | `PASSED` |
| `14` | preregistration artifacts finalized | `PASSED` |
| `15` | model training not yet started | `PASSED` |

---
## 4. ODD Firewall Verification

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`

---
## 5. Cryptographic Provenance

- **Pre-Registration MD SHA256:** `e997b9d6a18858095c7dbc350c198ef0546cd8eda313fd946d7f0d19d588f4c5`
- **Pre-Registration JSON SHA256:** `1c0929ffea75490ee23137f5822fc69c806942572b7922e343dcf72d87c8e4fb`
- **Pre-Training Audit Script SHA256:** `42de7945e028ff4c7e9a4eb073bac16b2ee00f98fabb21317d0bb9dcb0e9b8df`
- **Pre-Training Audit JSON Artifact:** [`PRE_TRAINING_LOCAL_SPATIAL_3X3_AUDIT.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/PRE_TRAINING_LOCAL_SPATIAL_3X3_AUDIT.json)
  - SHA256: `993e9f169e2530bb9b69ec459fb20d5bb6d2c3787fb488f48ce2a6b8a13cd29a`