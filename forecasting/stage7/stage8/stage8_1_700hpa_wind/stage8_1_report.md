# POLARIS STAGE 8.1 — 700 hPa FREE-ATMOSPHERE STEERING WIND REPORT

## 1. Executive Summary
This report presents the EVEN-only 5-fold forward-chaining CV results for Stage 8.1 evaluating 700 hPa free-atmosphere steering wind features ($U_{700}, V_{700}$) derived causally from D-1 18Z MEPS deterministic forecasts.

## 2. Experimental Results Summary

| Model / Candidate | Features | MAE (W/m²) | nMAE (%) | RMSE (W/m²) | Bias (W/m²) | Delta MAE | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0 Control (Baseline)** | 31 / 35 | **38.280605** | **40.3918** | **60.750856** | **+2.419115** | -- | **REPRODUCED** |
| **E1 Candidate ($U_{700}, V_{700}$)** | 37 | **37.620054** | **37.9745** | **60.160645** | **+4.218739** | **-0.660552** | **PASS — FREEZE PENDING FORENSIC AUDIT** |

## 3. Fold-by-Fold Breakdown

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Folds Improved | Degradation Pass |
| :---: | :---: | :---: | :---: | :---: | :---: |
| F1 | 49.817392 | 49.311419 | -0.505973 | YES | PASS |
| F2 | 71.077463 | 70.568800 | -0.508662 | YES | PASS |
| F3 | 41.261951 | 40.345573 | -0.916378 | YES | PASS |
| F4 | 26.804209 | 25.770418 | -1.033791 | YES | PASS |
| F5 | 2.442011 | 2.104058 | -0.337953 | YES | PASS |

## 4. Acceptance Gates Decision

- **GATE 1 (MAE <= 38.080605 W/m²):** PASS (Actual: 37.620054 W/m²)
- **GATE 2 (Folds Improved >= 4):** PASS (Actual: 5/5)
- **GATE 3 (Max Degradation <= +0.15 W/m²):** PASS (Actual: -0.337953 W/m²)
- **GATE 4 (nMAE <= Control 40.3918%):** PASS (Actual: 37.9745%)
- **GATE 5 (RMSE <= Control 60.750856 W/m²):** PASS (Actual: 60.160645 W/m²)

**FINAL STAGE 8.1 STATUS:** **PASS — FREEZE PENDING FORENSIC AUDIT**
