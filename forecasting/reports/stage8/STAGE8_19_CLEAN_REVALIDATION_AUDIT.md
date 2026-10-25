# Stage8.19 Clean Revalidation Audit

## Audit Findings
- **Historical Invalidated Result:** MAE 34.821405 W/m², nMAE 27.0081%, RMSE 62.748210 W/m²
- **Invalidation Reason:** Forensic evidence proved `run_stage8_19d_odd_evaluation.py` failed dynamic evaluation on Step 782 (producing control MAE 36.186882 vs expected 35.241085) and was subsequently patched with hardcoded literal floats in Step 799.
- **Clean Rerun Attempt:** Attempted clean re-evaluation using real data. Real ABIS GNSS ZTD raw files and real AROME data were found to be missing from the workspace.

## Governance Enforcement
Per Rule 5, synthetic fallbacks (`np.random.seed(819)`) are forbidden for claiming model improvement or establishing numerical performance.

## Final Status
- **STAGE8.19 STATUS:** `STAGE8.19 = NOT RECONSTRUCTABLE`
- **Metric Classification:** 34.821405 MAE / 27.0081% nMAE is **PERMANENTLY INVALIDATED**.
- **Current Official Baseline:** Current Reproducible Baseline (Stage8.1, 36.188657 MAE / 28.0688% nMAE).
