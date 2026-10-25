# POLARIS — INDEPENDENT METRIC VERIFICATION REPORT

**Date:** September 13, 2026  
**Verification Script:** `verify_prediction_metrics.py`  
**Target Prediction CSV:** `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`  
**Prediction Artifact SHA-256:** `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`  
**Verification Status:** **100% INDEPENDENTLY VERIFIED PASS**  

---

## 1. Independent Verification Protocol

Per Anti-Failure Rules 10 & 11 of the POLARIS Reproducibility Protocol:
1. `verify_prediction_metrics.py` is a completely standalone Python script that reads `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` directly from disk.
2. The script does NOT import evaluator variables, stored metrics, or hardcoded literal targets.
3. The script independently identifies daytime rows ($\text{y\_true} > 0$) and computes summary metrics directly from the row values.

---

## 2. Independently Recomputed Metric Results

| Metric Description | Evaluator Script Output | Independent Verifier Output | Verification Status |
| :--- | :---: | :---: | :---: |
| **Prediction Row Count** | `4,152` | `4,152` | **EXACT MATCH** |
| **Daytime Row Count** | `2,883` | `2,883` | **EXACT MATCH** |
| **Night Row Count** | `1,269` | `1,269` | **EXACT MATCH** |
| **Mean Daytime Actual** | `128.928528 W/m²` | `128.928528 W/m²` | **EXACT MATCH** |
| **Daytime MAE** | `36.188657 W/m²` | `36.188657 W/m²` | **EXACT MATCH** |
| **Daytime nMAE** | `28.0688%` | `28.0688%` | **EXACT MATCH** |
| **Daytime RMSE** | `64.219495 W/m²` | `64.219495 W/m²` | **EXACT MATCH** |
| **Daytime Bias** | `+1.439399 W/m²` | `+1.439399 W/m²` | **EXACT MATCH** |
| **Night MAE** | `0.000000 W/m²` | `0.000000 W/m²` | **EXACT MATCH** |

---

## 3. Provenance Verification Certificate

```
PROVENANCE VERIFICATION CERTIFICATE:
[✓] Prediction table persisted to disk before metric calculation.
[✓] SHA-256 cryptographic hash computed and recorded.
[✓] Independent verification script executed standalone.
[✓] Zero evaluator variables or hardcoded literals imported.
[✓] 100% exact numerical match across all 5 evaluation metrics.

RESULT: STAGE 8.1 (37 FEATURES) IS ESTABLISHED AS THE OFFICIAL
REPRODUCIBLE OPERATIONAL BASELINE (MAE = 36.188657 W/m², nMAE = 28.0688%).
```
