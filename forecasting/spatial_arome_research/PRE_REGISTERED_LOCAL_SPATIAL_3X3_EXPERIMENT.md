# POLARIS PRE-REGISTERED LOCAL SPATIAL 3X3 FORECASTING EXPERIMENT PROTOCOL

**Date:** September 14, 2026  
**Experiment Target:** Single Pre-Registered Horizon-Conditional Local 3×3 Spatial Experiment  
**Pre-Registration Status:** **`FROZEN AND LOCKED BEFORE TRAINING`**  

---
## 1. Primary Scientific Question

> **"Does adding a causal 3x3 local AROME cloud-state representation to the existing POLARIS forecasting inputs improve causal SW_IN forecasting under the locked POLARIS benchmark?"**

---
## 2. Absolute Governance & Firewalls

- **ODD Firewall:** UNBREACHED — 174 ODD origins completely sealed
- **Network Fetches:** 0
- **Feature Governance:** No new meteorological variables or derived features permitted. The only newly constructed representation is the pre-registered 3x3 spatial tensor formed directly from the existing frozen 11-channel causal AROME cache.

---
## 3. Frozen Architecture Specification (15,633 Parameters)

| Component | Specification | Dimensions |
| :--- | :--- | :---: |
| **Spatial Conv** | `Conv2d(11,16,k3,p1) -> BN -> ReLU -> Conv2d(16,16,k3,p1) -> BN -> ReLU` | `[16, 3, 3]` |
| **Spatial Readout** | Center `[1,1]` (16d), Flattened `3x3` (144d) `-> Linear(144,32) -> BN -> ReLU` | `32` |
| **Horizon Emb** | `nn.Embedding(24, 16)` | `16` |
| **Horizon Gate** | `concat[spat 32, horiz 16] -> Linear(48,32) -> ReLU -> Linear(32,32) -> Sigmoid` | `32` |
| **Context Enc** | `Linear(38,32) -> BN -> ReLU` | `32` |
| **Fusion Head** | `concat[gated_spat 32, ctx 32, horiz 16] = 80 -> Linear(80,32) -> ReLU -> Dropout(0.2) -> Linear(32,1)` | `1` |
| **Total Params** | **Exact Count: 15,633 Trainable Parameters** | **FROZEN** |

---
## 4. EVEN Promotion Gates (G1–G6)

- **G1:** Aggregate daytime ΔMAE <= -0.50 W/m² vs control (47.451469 W/m²)
- **G2:** At least 4 of 5 folds improve in daytime MAE
- **G3:** Maximum fold daytime MAE degradation <= +0.50 W/m²
- **G4:** Daytime nMAE <= 36.8045% AND Daytime RMSE <= 74.376601 W/m²
- **G5:** 0 parser, shape, or temporal leakage defects
- **G6:** Control prediction CSV (SHA256: b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366) verified

---
## 5. Decision Rules & Cryptographic Provenance

- **If All G1–G6 Pass:** PROMOTED to ODD evaluation
- **If Any Gate Fails:** REJECTED and local-spatial route CLOSED permanently. No retraining, rescue models, or seed sweeps.

- **Pre-Registration JSON SHA256:** `1c0929ffea75490ee23137f5822fc69c806942572b7922e343dcf72d87c8e4fb`