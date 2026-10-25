# POLARIS — LOCAL-SPATIAL 3X3 FINAL REJECTION & ROUTE CLOSURE CHECKPOINT

**Date:** September 14, 2026  
**Route Name:** `LOCAL-SPATIAL 3X3 REPRESENTATION ROUTE`  
**Route Status:** **`CLOSED / REJECTED`**  
**Final Experiment Verdict:** **`VALID + EVEN GATES FAIL — REJECTED`**  

---
## 1. Executive Summary & Authoritative Result

> **ROUTE CLOSURE STATEMENT:**
> *The single pre-registered horizon-conditional local-spatial 3×3 forecasting experiment failed EVEN promotion gates G1, G2, G3, and G4 despite passing G5 and G6. The local-spatial 3×3 representation route is formally CLOSED and REJECTED. ODD data remains 100% sealed, and the official POLARIS ODD champion (28.0688% daytime nMAE) remains protected and unaltered.*

| Metric | Frozen Control Baseline | Pre-Registered 3×3 Candidate | Delta (Cand − Ctrl) |
| :--- | :---: | :---: | :---: |
| **Primary Daytime MAE** | `47.451469` W/m² | `50.47194` W/m² | **`+3.020471` W/m²** |
| **Primary Daytime nMAE** | `36.8045`% | `39.1473`% | **`+2.3428` pp** |
| **Primary Daytime RMSE** | `74.376601` W/m² | `78.069452` W/m² | **`+3.692851` W/m²** |
| **Primary Daytime Bias** | `-8.863007` W/m² | `-8.460377` W/m² | `+0.402630` W/m² |
| **24h Total MAE** | `25.639318` W/m² | `27.251399` W/m² | `+1.612081` W/m² |
| **24h Total RMSE** | `54.369219` W/m² | `57.065529` W/m² | `+2.696310` W/m² |
| **Night MAE** | `0.672516` W/m² | `0.672516` W/m² | `0.000000` W/m² |

---
## 2. Per-Fold Primary Daytime MAE Breakdown (5 EVEN Folds)

| Fold | Control Daytime MAE | Candidate Daytime MAE | Delta Daytime MAE | Improved? |
| :---: | :---: | :---: | :---: | :---: |
| Fold 1 | `51.357263` W/m² | `51.212555` W/m² | `-0.144708` W/m² | `YES` |
| Fold 2 | `40.240493` W/m² | `45.383297` W/m² | `+5.142804` W/m² | `NO` |
| Fold 3 | `48.351210` W/m² | `54.618599` W/m² | `+6.267389` W/m² | `NO` |
| Fold 4 | `52.923952` W/m² | `57.312267` W/m² | `+4.388315` W/m² | `NO` |
| Fold 5 | `44.393157` W/m² | `43.801720` W/m² | `-0.591438` W/m² | `YES` |

*Folds Improved: 2/5 (Requires >= 4/5 for G2)*

---
## 3. Promotion Gates Assessment (G1–G6)

| Gate | Requirement | Candidate Result | Gate Status |
| :---: | :--- | :---: | :---: |
| **G1** | ΔMAE <= -0.50 W/m² | `+3.020471 W/m²` | **`FAIL`** |
| **G2** | >= 4/5 folds improved | `2/5 folds improved` | **`FAIL`** |
| **G3** | Max fold deg <= +0.50 W/m² | `+6.267389 W/m²` | **`FAIL`** |
| **G4** | nMAE <= 36.8045% & RMSE <= 74.3766 | `nMAE=39.1473%, RMSE=78.069452` | **`FAIL`** |
| **G5** | Causal / shape / parser pass | `0 defects` | **`PASS`** |
| **G6** | Control CSV SHA256 verified | `Verified b4cafe...` | **`PASS`** |

### **Final Gate Outcome: `EVEN GATES FAIL — REJECTED`**

---
## 4. ODD Firewall Verification Record

- **ODD Evaluated:** `False`
- **ODD Rows Accessed:** `False`
- **ODD Origins Sealed:** `174 origins`
- **Protected Official ODD Champion nMAE:** `28.0688%` (Unaltered)
- **Champion Status:** `True`

---
## 5. Scientific Distinction & Route Closure Protocol

> **SCIENTIFIC DISTINCTION:**
> *The preceding diagnostic audit established that local 3x3 AROME cloud state contains detectable incremental information. However, the single pre-registered forecasting experiment established that this specific 3x3 local-spatial representation and horizon-conditional architecture failed the locked forecasting promotion gates (degrading EVEN daytime MAE by +3.02 W/m²) and did not translate spatial information into improved SW_IN forecasting. The local-spatial representation route is therefore closed.*

### Strict Route Closure Prohibitions:
- [x] **No model retraining permitted**
- [x] **No hyperparameter sweeps permitted**
- [x] **No alternate random seed sweeps permitted**
- [x] **No architecture modification permitted**
- [x] **No alternate spatial footprint (5x5, 9x9, 21x21) permitted**
- [x] **No additional spatial feature engineering permitted**
- [x] **No ODD evaluation authorized**

---
## 6. Cryptographic Provenance & Artifact Hashes

- **candidate_predictions_csv_sha256:** `9120ff9eedca48043b34f613043a221ce8c1727ae824ef222dd07ca84f2e0939`
- **training_execution_script_sha256:** `6fc811d07328c35b212393d38f46ae41b3f9959472194138eb86f9a8c859c0f3`
- **results_json_sha256:** `35e6348f02e82689b25c909cfd0e2f756cd5db1c6783833b63d1dd72501fde1a`
- **results_md_sha256:** `3e181fdd7bd098ed86cbf34d34b306eea7b3265ac2fae0f25930be1e2599ea5a`
- **preregistration_protocol_md_sha256:** `e997b9d6a18858095c7dbc350c198ef0546cd8eda313fd946d7f0d19d588f4c5`
- **preregistration_protocol_json_sha256:** `1c0929ffea75490ee23137f5822fc69c806942572b7922e343dcf72d87c8e4fb`