# POLARIS — TOPOLOGY-PRESERVING AROME ARCHITECTURE FREEZE MANIFEST

**Date:** September 14, 2026  
**Phase:** Phase 11/12 Architecture Freeze & Pre-Training Audit  
**Audit Verdict:** `ARCHITECTURE FROZEN & AUDITED — READY FOR CONTROLLED SINGLE EVEN TRAINING EXPERIMENT`  

---
## 1. Scientific Governance & Absolute Safeguards

> **GOVERNANCE STATEMENT:**
> *NO MODEL TRAINING WAS PERFORMED IN THIS TASK. Network fetches performed = 0. ODD data remain 100% sealed (174 ODD origins). No benchmark, champion, or control parameters were altered.*

---
## 2. Scientific Statement & Core Hypothesis

> **CORRECT SCIENTIFIC PHRASING:**
> *"Global average pooling removes explicit spatial position from the pooled representation and can make the representation insensitive to where spatial activations occur, potentially discarding location- and direction-dependent information."*

### Scientific Hypothesis:
> *"Useful spatial topology exists in AROME, but the previous CNN → AdaptiveAvgPool → GRU representation may discard location- and direction-dependent information needed for irradiance forecasting."*

---
## 3. Architecture Specification & Comparison

| Specification Component | Previous Failed Candidate | New Frozen Topology-Preserving Candidate |
| :--- | :--- | :--- |
| **Architecture Name** | `SpatialTemporalCNNGRU` | **`TopologyPreservingSpatialTemporalCNNGRU`** |
| **Trainable Parameters** | `16,033` | **`48,273`** |
| **Spatial Pooling / Readout** | `AdaptiveAvgPool2d((1,1))` (Spatially Blind) | **Station-Centered Multi-Scale Readout** (`Center` + `3x3 Nbr` + `7x7 Nbr`) |
| **Spatial Topology Preserved?** | `NO (100% Wiped Out)` | **`YES (Explicit Spatial Coordinates)`** |
| **Temporal Encoder** | `GRU(32, 32)` | `GRU(64, 32)` |
| **Context Features** | `38 features` | `38 features` |
| **Output Shape** | `[B, 24]` | `[B, 24]` |

---
## 4. Cache Inventory Audit Results

- **Cache Files Found:** `173`
- **EVEN Origins Available:** `173 / 173`
- **Invalid / Missing Caches:** `0`
- **Network Fetches Performed:** `0`
- **Cache Provenance Verified:** `True`

---
## 5. Spatial-Information Sanity Test Results

| Model Architecture | North vs. South Spatial Feature Vector Difference | Sanity Test Result |
| :--- | :---: | :---: |
| Old `AdaptiveAvgPool2d((1,1))` Model | `0.000000` | `FAILED (Spatially Blind)` |
| **New Topology-Preserving Model** | **`0.689553`** | **`PASSED (Topology Sensitive)`** |

---
## 6. Pre-Training Programmatic Audit Verification (20 Checks)

| Check | Item Description | Status |
| :---: | :--- | :---: |
| `1_` | nput shape exact B 24 11 21 21 | `PASSED (True)` |
| `2_` | eal arome tensors loaded | `PASSED (True)` |
| `3_` | tation anchor at 10 10 | `PASSED (True)` |
| `4_` | o adaptive avg pool | `PASSED (True)` |
| `5_` | patial topology explicit after encoder | `PASSED (True)` |
| `6_` | enter location explicitly represented | `PASSED (True)` |
| `7_` | br3x3 retains spatial arrangement | `PASSED (True)` |
| `8_` | br7x7 retains spatial arrangement | `PASSED (True)` |
| `9_` | emporal sequence length 24 preserved | `PASSED (True)` |
| `10` | output shape B 24 | `PASSED (True)` |
| `11` | context variables count 38 | `PASSED (True)` |
| `12` | no diagnostic statistics entered model | `PASSED (True)` |
| `13` | no future actuals entered inputs | `PASSED (True)` |
| `14` | causal night masking specified | `PASSED (True)` |
| `15` | odd firewall intact | `PASSED (True)` |
| `16` | even groupkfold split 5 folds | `PASSED (True)` |
| `17` | exact parameter count | `PASSED (48273)` |
| `18` | forward pass succeeded | `PASSED (True)` |
| `19` | backward pass succeeded | `PASSED (True)` |
| `20` | no nan or inf in outputs or grads | `PASSED (True)` |

---
## 7. Frozen Training Protocol (Ready for Eventual Experiment)

- **even_origins_count**: `173`
- **cross_validation**: `GroupKFold by forecast_origin (n_splits=5)`
- **spatial_scaling**: `Per-channel Z-score fit on training fold, clip [-5, +5]`
- **optimizer**: `AdamW`
- **learning_rate**: `0.001`
- **weight_decay**: `0.0001`
- **batch_size**: `8`
- **max_epochs**: `300`
- **early_stopping_patience**: `20`
- **seed**: `42`
- **loss_function**: `Daytime MAE / L1Loss with causal night zero mask`

---
## 8. ODD Firewall Verification

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`
- **Training Status:** `NO TRAINING PERFORMED`

---
## 9. Final Decision & Cryptographic Provenance

### **`ARCHITECTURE FROZEN & AUDITED — READY FOR CONTROLLED SINGLE EVEN TRAINING EXPERIMENT`**

- **Freeze Script SHA256:** `b425cfaa59155b0c65f3d4ec13769de61826b584ea59b10866a58ac87c9eecd4`
- **Freeze JSON Artifact:** [`TOPOLOGY_PRESERVING_AROME_ARCHITECTURE_FREEZE.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/TOPOLOGY_PRESERVING_AROME_ARCHITECTURE_FREEZE.json)
  - SHA256: `363aaab5635b6e67437ddd592bfeb280bedd15b4cfde61bf86bf1def6c629335`