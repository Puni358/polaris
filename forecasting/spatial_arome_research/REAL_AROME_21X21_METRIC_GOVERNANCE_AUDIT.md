# POLARIS — 21×21 REAL-AROME METRIC & GOVERNANCE AUDIT REPORT

**Date:** September 14, 2026  
**Audit Status:** COMPLETE  
**Final Verdict:** `21×21 REAL-AROME — VALID EVEN RESULT — REJECTED`  

---
## 1. Audit Governance Statements

> **CRITICAL AUDIT SAFEGUARDS:**
> 1. *No candidate retraining was performed during this audit.*
> 2. *No ODD data were accessed.*
> 3. *No rerun of AROME tensor extraction was performed.*
> 4. *Evaluated strictly from pre-existing prediction artifacts.*

---
## 2. Metric Discrepancy & Clarification

### Why Previous nMAE Was Not Directly Comparable:
The initial candidate training report presented nMAE based on **24-hour total MAE** (`19.8865%` control, `24.2978%` candidate), which averaged over 1,936 night forced-zero hours.

However, the official POLARIS benchmark defines primary nMAE strictly on **daytime MAE** normalized by the fixed daytime mean actual SW_IN (`128.9284 W/m²`):

$$\text{Daytime nMAE} = \frac{\text{Daytime MAE}}{128.9284 \text{ W/m}^2} \times 100\%$$

> **FORMAL DISCLAMER:**  
> *The previously reported 24-hour-derived nMAE values (`19.8865%` control / `24.2978%` candidate) are designated as **NON-OFFICIAL / 24-HOUR-DERIVED nMAE — DO NOT COMPARE WITH POLARIS CHAMPION**.*

---
## 3. Official POLARIS Primary Benchmark Comparison

| Benchmark / Model | Primary Daytime MAE | Primary Daytime nMAE | Primary Daytime RMSE | Primary Daytime Bias |
| :--- | :---: | :---: | :---: | :---: |
| **POLARIS Official Champion** | `36.188657` W/m² | `28.0688`% | `64.219495` W/m² | `+1.439399` W/m² |
| **Frozen Reproducible Control** | `47.451469` W/m² | `36.8045`% | `74.376601` W/m² | `-8.863007` W/m² |
| **21×21 Real-AROME Candidate** | `58.107798` W/m² | `45.0698`% | `85.254312` W/m² | `-5.155466` W/m² |
| **Delta (Candidate − Control)** | **`+10.656329` W/m²** | **`+8.2653` pp** | **`+10.877710` W/m²** | **`+3.707541` W/m²** |

### Secondary 24-Hour & Night Metrics:
- **Control**: 24h MAE = `25.639318` W/m², 24h RMSE = `54.369219` W/m², 24h Bias = `-5.043934` W/m², Night MAE = `0.672516` W/m²
- **Candidate**: 24h MAE = `31.326800` W/m², 24h RMSE = `62.311886` W/m², 24h Bias = `-3.065150` W/m², Night MAE = `0.672516` W/m²

---
## 4. Per-Fold Daytime MAE Breakdown (5 EVEN Folds)

| Fold | Control Daytime MAE | Candidate Daytime MAE | Delta Daytime MAE | Improved? | Daytime Rows |
| :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | `51.357263` W/m² | `73.179676` W/m² | `+21.822413` W/m² | `NO` | `443` |
| Fold 2 | `40.240493` W/m² | `52.609044` W/m² | `+12.368551` W/m² | `NO` | `444` |
| Fold 3 | `48.35121` W/m² | `58.1203` W/m² | `+9.769090` W/m² | `NO` | `446` |
| Fold 4 | `52.923952` W/m² | `54.025159` W/m² | `+1.101207` W/m² | `NO` | `442` |
| Fold 5 | `44.393157` W/m² | `52.582981` W/m² | `+8.189824` W/m² | `NO` | `441` |

- **Total Folds Improved:** `0 / 5`
- **Maximum Fold Daytime MAE Degradation:** `+21.822413` W/m²

---
## 5. Recomputed Promotion Gates G1–G6 Assessment

| Gate | Description | Benchmark Requirement | Recomputed Result | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **G1** | Δ Daytime MAE Superiority | `Δ MAE <= -0.50 W/m²` | `+10.656329` W/m² | `FAIL` |
| **G2** | Fold Consistency | `>= 4/5 folds improved` | `0/5 folds` | `FAIL` |
| **G3** | Max Degradation Cap | `Max fold deg <= +0.50 W/m²` | `+21.822413` W/m² | `FAIL` |
| **G4** | Non-Degradation | `Daytime nMAE <= ctrl AND RMSE <= ctrl` | `nMAE=45.0698%`, `RMSE=85.254312` | `FAIL` |
| **G5** | Parser & Causal Pass | `Authentic 11-ch real-AROME tensors` | `0 validity defects` | `PASS` |
| **G6** | Baseline Reproduction | `Exact control reproduction` | `100% verified` | `PASS` |

### **Overall Recomputed Gate Outcome: `REJECTED`**

---
## 6. Cryptographic Provenance & Hashes

- **Control Predictions CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)
  - SHA256: `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`
- **Candidate Predictions CSV:** [`REAL_AROME_21X21_CANDIDATE_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_CANDIDATE_PREDICTIONS.csv)
  - SHA256: `72b54fa89c7daf2d2d23b68cf7aa7c0ffa15b6882e6d451cea24cf1dc627b94b`
- **Audit JSON Contract:** [`REAL_AROME_21X21_METRIC_GOVERNANCE_AUDIT.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_METRIC_GOVERNANCE_AUDIT.json)
  - SHA256: `bd395662db9dc4ac74a46d83b99ed05c8d80aa1d1f26140cbeb8ede7c06104d5`

---
## 7. ODD Firewall Verification

- **odd_origins_accessed**: `False`
- **odd_tensors_loaded**: `False`
- **odd_predictions_generated**: `False`
- **odd_metrics_evaluated**: `False`
- **firewall_status**: `UNBREACHED — 174 ODD origins completely sealed`

---
## 8. Final Scientific & Governance Verdict

### **`21×21 REAL-AROME — VALID EVEN RESULT — REJECTED`**

Under the official POLARIS primary daytime benchmark metric, the 21×21 Real-AROME CNN-GRU candidate model suffers significant daytime degradation relative to the frozen 37-feature control baseline ($+10.66 \text{ W/m}^2$ daytime MAE, $+8.27 \text{ pp}$ daytime nMAE, $+10.88 \text{ W/m}^2$ daytime RMSE, $0/5$ folds improved). The candidate fails promotion gates G1–G4.

**ABSOLUTE STOP.** No candidate retraining, no ODD evaluation, no hyperparameter tuning, no rescue variants.