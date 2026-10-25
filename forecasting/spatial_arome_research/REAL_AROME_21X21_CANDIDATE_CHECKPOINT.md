# POLARIS — 21×21 REAL-AROME CANDIDATE EXPERIMENT CHECKPOINT

**Date:** September 14, 2026  
**Final Verdict:** `B — VALID + EVEN GATES FAIL (REJECTED)`  
**Description:** The 21×21 Real-AROME candidate failed one or more EVEN promotion gates against the frozen reproducible control baseline.  

---
## 1. Executive Metric Summary

| Metric | Frozen Control Baseline | 21×21 Candidate Model | Delta (Cand − Ctrl) |
| :--- | :---: | :---: | :---: |
| **24-hour Total MAE** | `25.639318` W/m² | `31.3268` W/m² | `+5.687482` W/m² |
| **24-hour Total nMAE** | `19.8865`% | `24.2978`% | `+4.4113` pp |
| **24-hour Total RMSE** | `54.369219` W/m² | `62.311886` W/m² | `+7.942667` W/m² |
| **24-hour Total Bias** | `-5.043934` W/m² | `-3.06515` W/m² | `+1.978784` W/m² |
| **Daytime MAE** | `47.451469` W/m² | `58.107798` W/m² | `+10.656329` W/m² |
| **Night MAE** | `0.672516` W/m² | `0.672516` W/m² | `+0.000000` W/m² |

---
## 2. Per-Fold 24-hour MAE Breakdown

| Fold | Control 24h MAE | Candidate 24h MAE | Delta MAE | Improved? | Epochs Run |
| :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | `27.358628` W/m² | `38.867352` W/m² | `+11.508724` W/m² | `NO` | `66` |
| Fold 2 | `21.591261` W/m² | `28.128925` W/m² | `+6.537664` W/m² | `NO` | `163` |
| Fold 3 | `25.950014` W/m² | `31.136938` W/m² | `+5.186924` W/m² | `NO` | `222` |
| Fold 4 | `29.003698` W/m² | `29.600183` W/m² | `+0.596485` W/m² | `NO` | `160` |
| Fold 5 | `24.352342` W/m² | `28.77846` W/m² | `+4.426118` W/m² | `NO` | `118` |

---
## 3. Promotion Gates G1–G6 Assessment

| Gate | Description | Requirement | Candidate Result | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **G1** | ΔMAE Superiority | `ΔMAE <= -0.50 W/m²` | `+5.687482` W/m² | `FAIL` |
| **G2** | Fold Consistency | `>= 4/5 folds improved` | `0/5 folds` | `FAIL` |
| **G3** | Max Degradation Cap | `Max fold deg <= +0.50 W/m²` | `+11.508724` W/m² | `FAIL` |
| **G4** | Non-Degradation | `nMAE <= ctrl AND RMSE <= ctrl` | `nMAE=24.2978%`, `RMSE=62.311886` | `FAIL` |
| **G5** | Parser & Causal Pass | `Authentic 11-ch real-AROME tensors` | `0 validity defects` | `PASS` |
| **G6** | Baseline Reproduction | `Exact control reproduction` | `100% verified` | `PASS` |

### **Overall Gate Outcome: `REJECTED`**

---
## 4. Cryptographic Provenance & Hashes

- **Prediction Artifact CSV:** [`REAL_AROME_21X21_CANDIDATE_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_CANDIDATE_PREDICTIONS.csv)
- **Candidate Predictions SHA256:** `72b54fa89c7daf2d2d23b68cf7aa7c0ffa15b6882e6d451cea24cf1dc627b94b`
- **Experiment Script SHA256:** `60a209e41e1f1cfca9eb137092df89b2701d4dffba869b086b449205bf917322`
- **Checkpoint JSON SHA256:** `ebd90a3875fe13ba14eeab3925b22d783ca9754b20e34275bb5e3d0ae458ec38`

---
## 5. ODD Firewall & Governance Verification

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`
- **ODD Access Action**: `STOP. No ODD evaluation authorized.`