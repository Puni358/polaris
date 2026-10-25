# POLARIS — TOPOLOGY-PRESERVING AROME EVEN TRAINING RESULTS

**Date:** September 14, 2026  
**Final Verdict:** `TOPOLOGY-PRESERVING AROME — VALID EVEN RESULT — REJECTED`  
**Description:** The Topology-Preserving Real-AROME candidate failed one or more EVEN promotion gates against the frozen reproducible control baseline.  

---
## 1. Official POLARIS Primary Daytime Benchmark Comparison

| Metric | Frozen Control Baseline | Topology-Preserving Candidate | Delta (Cand − Ctrl) |
| :--- | :---: | :---: | :---: |
| **Primary Daytime MAE** | `47.451469` W/m² | `63.286275` W/m² | `+15.834806` W/m² |
| **Primary Daytime nMAE** | `36.8045`% | `49.0864`% | `+12.2819` pp |
| **Primary Daytime RMSE** | `74.376601` W/m² | `92.363659` W/m² | `+17.987058` W/m² |
| **Primary Daytime Bias** | `-8.863007` W/m² | `-8.635196` W/m² | `+0.227811` W/m² |

### Secondary Full-Horizon & Night Metrics:
- **Candidate**: 24h Total MAE = `34.09065` W/m², 24h Total RMSE = `67.503506` W/m², 24h Total Bias = `-4.922347` W/m², Night MAE = `0.672516` W/m²

---
## 2. Per-Fold Primary Daytime MAE Breakdown (5 EVEN Folds)

| Fold | Control Daytime MAE | Candidate Daytime MAE | Delta Daytime MAE | Improved? | Epochs Run | Daytime Rows |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | `51.357263` W/m² | `67.278542` W/m² | `+15.921279` W/m² | `NO` | `72` | `443` |
| Fold 2 | `40.240493` W/m² | `57.794174` W/m² | `+17.553681` W/m² | `NO` | `86` | `444` |
| Fold 3 | `48.35121` W/m² | `70.498932` W/m² | `+22.147722` W/m² | `NO` | `109` | `446` |
| Fold 4 | `52.923952` W/m² | `65.313789` W/m² | `+12.389837` W/m² | `NO` | `99` | `442` |
| Fold 5 | `44.393157` W/m² | `55.478821` W/m² | `+11.085664` W/m² | `NO` | `149` | `441` |

---
## 3. Promotion Gates G1–G6 Assessment

| Gate | Description | Requirement | Candidate Result | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **G1** | Δ Daytime MAE Superiority | `Δ MAE <= -0.50 W/m²` | `+15.834806` W/m² | `FAIL` |
| **G2** | Fold Consistency | `>= 4/5 folds improved` | `0/5 folds` | `FAIL` |
| **G3** | Max Degradation Cap | `Max fold deg <= +0.50 W/m²` | `+22.147722` W/m² | `FAIL` |
| **G4** | Non-Degradation | `Daytime nMAE <= ctrl AND RMSE <= ctrl` | `nMAE=49.0864%`, `RMSE=92.363659` | `FAIL` |
| **G5** | Parser & Causal Pass | `Authentic 11-ch real-AROME tensors` | `0 validity defects` | `PASS` |
| **G6** | Baseline Reproduction | `Exact control reproduction` | `100% verified` | `PASS` |

### **Overall Gate Outcome: `REJECTED`**

---
## 4. Cryptographic Provenance & Hashes

- **Candidate Predictions CSV:** [`TOPOLOGY_PRESERVING_AROME_EVEN_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/TOPOLOGY_PRESERVING_AROME_EVEN_PREDICTIONS.csv)
  - SHA256: `8149d558def5ab63fe6738361e4b040727813f187dd2a5fa334f0849cd2488da`
- **Training Script SHA256:** `b5c6e748dbd7bf0721f9fa48629aeedccff0eb7a73d05347cc7827d8821329a0`
- **Results JSON Artifact:** [`TOPOLOGY_PRESERVING_AROME_EVEN_TRAINING_RESULTS.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/TOPOLOGY_PRESERVING_AROME_EVEN_TRAINING_RESULTS.json)
  - SHA256: `ff5dee9bdcd49436ff7bad731b0e1a471172e50c32c77ae432f270f3fcafd5d3`

---
## 5. ODD Firewall Verification

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`
- **ODD Access Action**: `STOP. No ODD evaluation authorized.`