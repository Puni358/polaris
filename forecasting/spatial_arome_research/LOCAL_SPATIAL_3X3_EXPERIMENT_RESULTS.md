# POLARIS LOCAL SPATIAL 3X3 EXPERIMENT RESULTS REPORT

**Date:** September 14, 2026  
**Final Verdict:** **`VALID + EVEN GATES FAIL — REJECTED`**  
**Outcome Summary:** The pre-registered local 3x3 candidate model failed one or more EVEN promotion gates against the frozen reproducible control. Route is closed.  

---
## 1. Primary Official Daytime Benchmark Comparison

| Metric | Frozen Control Baseline | Candidate 3×3 Model | Delta (Cand − Ctrl) |
| :--- | :---: | :---: | :---: |
| **Primary Daytime MAE** | `47.451469` W/m² | `50.47194` W/m² | `+3.020471` W/m² |
| **Primary Daytime nMAE** | `36.8045`% | `39.1473`% | `+2.3428` pp |
| **Primary Daytime RMSE** | `74.376601` W/m² | `78.069452` W/m² | `+3.692851` W/m² |
| **Primary Daytime Bias** | `-8.863007` W/m² | `-8.460377` W/m² | `+0.402630` W/m² |

### Secondary Full-Horizon Metrics:
- **24h Total MAE:** `27.251399` W/m²
- **24h Total RMSE:** `57.065529` W/m²
- **24h Total Bias:** `-4.829043` W/m²
- **Night MAE:** `0.672516` W/m²

---
## 2. Per-Fold Daytime MAE Breakdown (5 EVEN Folds)

| Fold | Control Daytime MAE | Candidate Daytime MAE | Delta Daytime MAE | Improved? | Epochs | Daytime Rows |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | `51.357263` W/m² | `51.212555` W/m² | `-0.144708` W/m² | `YES` | `48` | `443` |
| Fold 2 | `40.240493` W/m² | `45.383297` W/m² | `+5.142804` W/m² | `NO` | `49` | `444` |
| Fold 3 | `48.35121` W/m² | `54.618599` W/m² | `+6.267389` W/m² | `NO` | `49` | `446` |
| Fold 4 | `52.923952` W/m² | `57.312267` W/m² | `+4.388315` W/m² | `NO` | `39` | `442` |
| Fold 5 | `44.393157` W/m² | `43.80172` W/m² | `-0.591438` W/m² | `YES` | `51` | `441` |

---
## 3. Promotion Gates G1–G6 Assessment

| Gate | Requirement | Candidate Result | Status |
| :---: | :--- | :---: | :---: |
| **G1** | Δ Daytime MAE <= -0.50 W/m² | `+3.020471` W/m² | `FAIL` |
| **G2** | >= 4/5 Folds Improved | `2/5 folds` | `FAIL` |
| **G3** | Max Fold Deg <= +0.50 W/m² | `+6.267389` W/m² | `FAIL` |
| **G4** | nMAE <= 36.8045% & RMSE <= 74.3766 | `nMAE=39.1473%`, `RMSE=78.069452` | `FAIL` |
| **G5** | Parser & Causal Pass | `0 defects` | `PASS` |
| **G6** | Control Verification | `100% verified` | `PASS` |

### **Overall Gate Verdict: `EVEN GATES FAIL — REJECTED`**

---
## 4. ODD Firewall Audit

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`

---
## 5. Cryptographic Provenance

- **Candidate Predictions CSV:** [`LOCAL_SPATIAL_3X3_EVEN_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/LOCAL_SPATIAL_3X3_EVEN_PREDICTIONS.csv)
  - SHA256: `9120ff9eedca48043b34f613043a221ce8c1727ae824ef222dd07ca84f2e0939`
- **Training Script SHA256:** `6fc811d07328c35b212393d38f46ae41b3f9959472194138eb86f9a8c859c0f3`
- **Results JSON Artifact:** [`LOCAL_SPATIAL_3X3_EXPERIMENT_RESULTS.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/LOCAL_SPATIAL_3X3_EXPERIMENT_RESULTS.json)
  - SHA256: `35e6348f02e82689b25c909cfd0e2f756cd5db1c6783833b63d1dd72501fde1a`