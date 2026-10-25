# POLARIS Stage 8.6B — CAMS AOD550 + TCWV Forecasting Experiment Report

## 1. Executive Summary & Predeclared Decision

**Stage 8.6B Decision:** **REJECTED**

Stage 8.6B evaluated the predictive impact of incorporating **ECMWF/Copernicus CAMS Aerosol Optical Depth at 550nm (`aod550`)** and **Total Column Water Vapour (`tcwv`)** into the frozen Stage 8.1 U700+V700 Steering Wind Model (37 features $\rightarrow$ 39 features).

Evaluation was conducted strictly on the **174 EVEN benchmark origins** using the authoritative 5-fold forward-chaining CV protocol. The Stage 8.1 Control model reproduced perfectly at **37.620054 W/m²** (matching the official 37.620054 W/m² baseline).

### Candidate Performance & Gate Summary:
* **Control EVEN CV MAE:** `37.620054 W/m²`
* **Candidate EVEN CV MAE:** `37.867306 W/m²`
* **Delta MAE:** `+0.247252 W/m²` (Target improvement: $\le -0.50\text{ W/m}^2$)
* **Control nMAE:** `37.9745%` | **Candidate nMAE:** `37.5944%` (`-0.3801 pp`)
* **Control RMSE:** `60.160645 W/m²` | **Candidate RMSE:** `60.524544 W/m²` (`+0.363899 W/m²`)
* **Folds Improved:** `3/5` | **Max Fold Degradation:** `+1.310037 W/m²`

> [!IMPORTANT]
> **Governance Enforcement Statement**:
> - **ODD target values were NEVER accessed, read, or evaluated.**
> - **No hyperparameter tuning or exploratory feature selection was performed.**
> - **Stage 8.6B has reached its final decision (REJECTED).**
> - **The Stage 8.1 U700+V700 Steering Wind Model remains the active, frozen operational champion.**
> - **`POLARIS_MASTER_HANDOFF.md` remains completely untouched.**

---

## 2. Predeclared Acceptance Gates Evaluation Table

| Gate | Description | Required Threshold | Candidate Value | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1 — Primary MAE** | EVEN CV MAE improvement $\ge 0.50\text{ W/m}^2$ | $\le 37.120054\text{ W/m}^2$ | `37.867306\text{ W/m}^2$` | **FAIL** |
| **Gate 2 — Fold Consistency** | Folds with MAE improvement | $\ge 4 / 5\text{ folds}$ | `3 / 5\text{ folds}` | **FAIL** |
| **Gate 3 — Worst-Fold Degradation** | Max fold MAE degradation | $\le +0.50\text{ W/m}^2$ | `+1.310037\text{ W/m}^2$` | **FAIL** |
| **Gate 4 — Directional Metrics** | Candidate nMAE $\le$ Control & RMSE $\le$ Control | $\le 37.9745\%$ & $\le 60.160645\text{ W/m}^2$ | `37.5944\%$ & `60.524544\text{ W/m}^2$` | **FAIL** |
| **Gate 5 — Physical Causality** | $t_{\text{init}} = t_0 - 12\text{h} \le t_0$, valid time == $T_h$ | 100.0% Causal Tuples | `8328/8328 (100.0%)` | **PASS** |
| **Gate 6 — Control Reproduction** | Stage 8.1 Control MAE reproduction | Expected 37.620054 $\pm 0.001$ | `37.620054\text{ W/m}^2$` | **PASS** |

**FINAL STAGE 8.6B VERDICT:** **REJECTED**

---

## 3. Fold-by-Fold Detailed Results Table

| Fold | Daytime Samples | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Delta nMAE (pp) | Control RMSE (W/m²) | Candidate RMSE (W/m²) | Delta RMSE (W/m²) | Control Bias (W/m²) | Candidate Bias (W/m²) | Delta Bias (W/m²) | Fold Improved? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 591 | 49.311419 | 48.988273 | -0.323146 | 29.5265 | 29.3330 | -0.1935 | 81.354967 | 80.946902 | -0.408065 | 2.496543 | 2.106986 | -0.389557 | YES |
| 2 | 696 | 70.568800 | 70.018421 | -0.550380 | 36.9196 | 36.6317 | -0.2879 | 103.743912 | 103.161756 | -0.582155 | 11.094607 | 8.239871 | -2.854736 | YES |
| 3 | 648 | 40.345573 | 41.655610 | +1.310037 | 28.1423 | 29.0561 | +0.9138 | 67.256670 | 69.438380 | +2.181710 | 4.228522 | 4.387655 | +0.159134 | NO |
| 4 | 396 | 25.770418 | 26.701695 | +0.931277 | 36.7313 | 38.0587 | +1.3274 | 44.613169 | 45.395516 | +0.782347 | 3.861825 | 7.247940 | +3.386115 | NO |
| 5 | 221 | 2.104058 | 1.972529 | -0.131529 | 58.5528 | 54.8926 | -3.6603 | 3.834508 | 3.680166 | -0.154342 | -0.587801 | -0.742347 | -0.154546 | YES |

---

## 4. EVEN-Only Mechanism Forensics

* **AOD550 Distribution (Daytime EVEN):**
  * 25th Percentile ($Q_{25}$): `0.0217` | 75th Percentile ($Q_{75}$): `0.0820`
  * Low AOD ($\le Q_{25}$): `722` samples
  * Mid AOD ($Q_{25} - Q_{75}$): `1442` samples
  * High AOD ($> Q_{75}$): `721` samples

* **TCWV Distribution (Daytime EVEN):**
  * 25th Percentile ($Q_{25}$): `5.56 kg/m²` | 75th Percentile ($Q_{75}$): `15.76 kg/m²`
  * Low TCWV ($\le Q_{25}$): `722` samples
  * Mid TCWV ($Q_{25} - Q_{75}$): `1442` samples
  * High TCWV ($> Q_{75}$): `721` samples

---

## 5. Artifacts Created

1. [`STAGE8_6B_EVEN_CV_SUMMARY.csv`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_EVEN_CV_SUMMARY.csv) — Fold-by-fold EVEN CV metrics comparison table.
2. [`STAGE8_6B_EVEN_CV_RESULTS.json`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_EVEN_CV_RESULTS.json) — Complete metrics and gate results JSON.
3. [`STAGE8_6B_GATE_DECISION.json`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_GATE_DECISION.json) — Official gate decision record.
4. [`STAGE8_6B_REPRODUCIBILITY.md`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_REPRODUCIBILITY.md) — Reproducibility statement with environment specs.
5. [`STAGE8_6B_CAMS_EXPERIMENT_REPORT.md`](file:///home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_6_cams_feasibility/STAGE8_6B_CAMS_EXPERIMENT_REPORT.md) — Comprehensive Markdown experiment report.

---

## 6. Champion Status & Next Steps

* **Operational Champion:** Stage 8.1 U700+V700 Steering Wind Model remains the active, frozen champion (ODD MAE: 36.188657 W/m², nMAE: 28.0688%).
* **Stage 8.6B Status:** **REJECTED**
* **Master Handoff:** `POLARIS_MASTER_HANDOFF.md` remains unchanged pending user review.
