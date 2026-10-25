# POLARIS — Real-Data Revalidation Final Report

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
- **Prediction File:** `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`
- **Prediction SHA-256:** `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`
- **Standalone Verification Status:** `STATUS = INDEPENDENT VERIFICATION MATCH PASS` (`verify_prediction_metrics.py`)
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
    The Stage 8.1 Reproducible Baseline metrics calculated directly from `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`: MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`.

12. **Which historical metrics remain unverified/invalid?**  
    - Stage 8.17A (`35.241085 W/m²` MAE / `27.3337%` nMAE) remains **Unverified Historical Reference Only**.
    - Stage 8.19 (`34.821405 W/m²` MAE / `27.0081%` nMAE) remains **Permanently Invalidated & Expunged**.

---

## Governance & Compliance Summary

- **Zero Synthetic Fallbacks Used:** Complied strictly with Rules 1–4. No synthetic seeds were used.
- **Zero Post-Hoc Tuning:** No models were fitted or tuned against ODD.
- **No Evaluator Mutations:** No evaluation scripts were modified to alter assertions.
- **Governance Integrity:** Neither `POLARIS_MASTER_HANDOFF.md` nor `POLARIS_STAGE8_ROUTE_REGISTRY.*` were altered, adhering to Rule 19.
