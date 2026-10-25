import os
import json

root_dir = '/home/punith-bs/01polaris (Copy)'
stage8_dir = os.path.join(root_dir, 'forecasting/stage7/stage8')

report_md = """# POLARIS — Real-Data Revalidation Final Report

**Date:** September 13, 2026  
**Workspace:** `/home/punith-bs/01polaris (Copy)`  
**Scope:** Real-Data Revalidation of Historical Stage 8.17A and Stage 8.19  
**Status:** **AUDIT COMPLETE — STAGE 8.17A & STAGE 8.19 NOT RECONSTRUCTABLE DUE TO MISSING REAL DATA**

---

## Executive Summary

Per the absolute rules governing real-data revalidation:
1. **Synthetic data generation (e.g. `np.random.seed(817)` / `np.random.seed(819)`) is strictly prohibited** for claiming model performance or establishing candidate improvements.
2. **If required real data or exact feature extraction formulas are missing, execution MUST STOP and report `NOT RECONSTRUCTABLE`.**

An exhaustive search across the local filesystem, project directories, caches, logs, and git history confirmed that:
- Real raw 2024 AROME-Arctic NWP data (GRIB2/netCDF format) and the Stage 8.17A 40-feature extraction script are **MISSING**.
- Real raw ABIS GNSS ZTD observation files (SWEPOS/E-GVAP/COST-716 format) are **MISSING**.
- No external automated retrieval pipeline exists for these datasets in the workspace.

Therefore, neither Stage 8.17A nor Stage 8.19 can be reconstructed using real data. The **Stage 8.1 (37-feature HGBR)** model remains the sole verified, reproducible baseline for the POLARIS project.

---

## Audit Findings & Baseline Verification

### 1. Authoritative Reproducible Baseline (Stage 8.1)
- **Model Architecture:** `HistGradientBoostingRegressor` (37 features)
- **ODD Test Set:** Locked 173 origins × 24 horizons = 4,152 predictions
- **Prediction File:** `forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`
- **Prediction SHA-256:** `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`
- **Standalone Verification Status:** `STATUS = INDEPENDENT VERIFICATION MATCH PASS` (`scripts/forecasting_research/verify_prediction_metrics.py`)
- **Verified Metrics:**
  - **Daytime MAE:** `36.188657 W/m²`
  - **Daytime nMAE:** `28.0688%`
  - **Daytime RMSE:** `64.219495 W/m²`
  - **Daytime Bias:** `+1.439399 W/m²`
  - **Night MAE:** `0.000000 W/m²`

---

## Summary of Revalidation Responses (12 Standard Questions)

1. **Is Stage 8.1 reproducible?**  
   **YES.** Fully reproducible and independently verified. MAE = `36.188657 W/m²`, nMAE = `28.0688%`, RMSE = `64.219495 W/m²`, Bias = `+1.439399 W/m²`, Night MAE = `0.000000 W/m²` from 4,152 persisted ODD prediction rows (SHA-256: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`).

2. **Is Stage 8.17A reproducible with REAL AROME?**  
   **NO.** Status: `STAGE8.17A = NOT RECONSTRUCTABLE`. Real raw AROME-Arctic files and 40-feature extraction script are absent. Synthetic fallbacks (`np.random.seed(817)`) are prohibited by Rule 2 & 4.

3. **What is the actual Stage 8.17A MAE?**  
   **N/A.** Cannot be computed without real AROME data and feature extraction formulas.

4. **What is the actual Stage 8.17A nMAE?**  
   **N/A.** Cannot be computed.

5. **Does Stage 8.17A beat Stage 8.1?**  
   **UNPROVEN / UNVERIFIED.** Without real AROME data and prediction tables, no claim of improvement over the `36.188657 W/m²` baseline can be made.

6. **Is Stage 8.19 reproducible with REAL ABIS + AROME?**  
   **NO.** Status: `STAGE8.19 = NOT RECONSTRUCTABLE`. Real raw ABIS GNSS ZTD observations and real AROME files are absent. Synthetic fallbacks (`np.random.seed(819)`) are prohibited.

7. **What is the actual Stage 8.19 MAE?**  
   **N/A.** Cannot be computed.

8. **What is the actual Stage 8.19 nMAE?**  
   **N/A.** Cannot be computed.

9. **Does Stage 8.19 beat Stage 8.1?**  
   **UNPROVEN / INVALIDATED.** Historical claim of `27.0081%` nMAE was produced by hardcoded literals after dynamic evaluation failure and is permanently invalidated.

10. **How do the real results compare with historical claims?**  
    - **Current Reproducible Baseline (Stage 8.1):** MAE `36.188657 W/m²` / nMAE `28.0688%` (Authoritative & Verified).
    - **Stage 8.17A Historical Claim:** MAE `35.241085 W/m²` / nMAE `27.3337%` (Unverified Historical Reference Only).
    - **Stage 8.19 Historical Claim:** MAE `34.821405 W/m²` / nMAE `27.0081%` (Permanently Invalidated & Expunged).

11. **Which metrics are authoritative?**  
    The Stage 8.1 Reproducible Baseline metrics calculated directly from `forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`: MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`.

12. **Which historical metrics remain unverified/invalid?**  
    - Stage 8.17A (`35.241085 W/m²` MAE / `27.3337%` nMAE) remains **Unverified Historical Reference Only**.
    - Stage 8.19 (`34.821405 W/m²` MAE / `27.0081%` nMAE) remains **Permanently Invalidated & Expunged**.

---

## Governance & Compliance Summary

- **Zero Synthetic Fallbacks Used:** Complied strictly with Rules 1–4. No synthetic seeds were used.
- **Zero Post-Hoc Tuning:** No models were fitted or tuned against ODD.
- **No Evaluator Mutations:** No evaluation scripts were modified to alter assertions.
- **Governance Integrity:** Neither `docs/decision_registers/POLARIS_MASTER_HANDOFF.md` nor `POLARIS_STAGE8_ROUTE_REGISTRY.*` were altered, adhering to Rule 19.
"""

report_json = {
    "timestamp": "2026-09-13T11:08:00+05:30",
    "document_title": "STAGE 8 REAL DATA REVALIDATION FINAL REPORT",
    "reproducible_baseline": {
        "stage": "Stage 8.1",
        "features": 37,
        "prediction_rows": 4152,
        "prediction_file": "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv",
        "sha256": "a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d",
        "daytime_mae_w_m2": 36.188657,
        "daytime_nmae_pct": 28.0688,
        "daytime_rmse_w_m2": 64.219495,
        "daytime_bias_w_m2": 1.439399,
        "night_mae_w_m2": 0.0,
        "verification_status": "INDEPENDENT_VERIFICATION_MATCH_PASS"
    },
    "stage8_17a_status": {
        "status": "STAGE8.17A = NOT RECONSTRUCTABLE",
        "reason": "Real raw AROME-Arctic NWP files and 40-feature extraction code missing; synthetic prohibited",
        "historical_claim_mae": 35.241085,
        "historical_claim_nmae": 27.3337,
        "provenance_classification": "UNVERIFIED_HISTORICAL_REFERENCE_ONLY"
    },
    "stage8_19_status": {
        "status": "STAGE8.19 = NOT RECONSTRUCTABLE",
        "reason": "Real raw ABIS GNSS ZTD observations and real AROME files missing; synthetic prohibited",
        "invalidated_claim_mae": 34.821405,
        "invalidated_claim_nmae": 27.0081,
        "provenance_classification": "PERMANENTLY_INVALIDATED_AND_EXPUNGED"
    },
    "authoritative_metrics": {
        "baseline_mae": 36.188657,
        "baseline_nmae": 28.0688,
        "baseline_rmse": 64.219495,
        "baseline_bias": 1.439399
    }
}

p1_md = os.path.join(root_dir, 'forecasting/reports/stage8/STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.md')
p1_json = os.path.join(root_dir, 'forecasting/reports/stage8/STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.json')
p2_md = os.path.join(stage8_dir, 'forecasting/reports/stage8/STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.md')
p2_json = os.path.join(stage8_dir, 'forecasting/reports/stage8/STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.json')

with open(p1_md, 'w') as f:
    f.write(report_md)
with open(p1_json, 'w') as f:
    f.write(json.dumps(report_json, indent=2))
with open(p2_md, 'w') as f:
    f.write(report_md)
with open(p2_json, 'w') as f:
    f.write(json.dumps(report_json, indent=2))

print('Wrote forecasting/reports/stage8/STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.md and .json to root and forecasting/stage7/stage8/')
