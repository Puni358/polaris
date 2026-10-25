import os
import json

root_dir = '/home/punith-bs/01polaris (Copy)'
stage8_dir = os.path.join(root_dir, 'forecasting/stage7/stage8')

# 1. STAGE8_17A_REVALIDATION_PLAN
s17a_plan_md = """# STAGE8.17A Revalidation Plan

## Objective
Attempt to reconstruct and re-evaluate Stage8.17A (40-feature AROME Structural Disagreement model) on the locked 173 ODD test set using only real surviving input artifacts and exact code.

## Pre-Conditions & Input Lineage Verification
1. Real raw AROME-Arctic NWP data (GRIB2/netCDF format): **MISSING**
2. Stage8.17A 40-feature extraction script: **MISSING**
3. Historical Stage8.17A prediction table (173 x 24): **MISSING**

## Compliance Rules
- Synthetic AROME feature generation (e.g. `np.random.seed(817)`) is **PERMANENTLY FORBIDDEN** (Rule 5).
- Missing components must NOT be synthesized or guessed (Phase 4).

## Execution Decision
Because required real AROME data and 40-feature generation code are absent from the workspace:
**STATUS: STAGE8.17A = NOT RECONSTRUCTABLE**
Revalidation execution is aborted prior to ODD evaluation.
"""

s17a_plan_json = {
    "status": "STAGE8.17A = NOT RECONSTRUCTABLE",
    "reason": "Real raw AROME-Arctic data and 40-feature extraction script are missing from workspace",
    "synthetic_fallback_allowed": False,
    "preconditions_met": False
}

# 2. STAGE8_17A_REVALIDATION_AUDIT
s17a_audit_md = """# STAGE8.17A Revalidation Audit

## Forensic Audit Summary
- **Historical Reported Metric:** MAE 35.241085 W/m², nMAE 27.3337%, RMSE 63.290812 W/m², Bias +1.810421 W/m²
- **Current Executable Baseline (Stage8.1, 37 features):** MAE 36.188657 W/m², nMAE 28.0688%, RMSE 64.219495 W/m²
- **Delta:** +0.947572 W/m² MAE

## Root Cause Analysis
Historical Stage8.17A reported metrics relied on a 40-feature set incorporating AROME wind disagreement (700 hPa) and LWP disagreement. However, neither the 40-feature extraction code nor the raw AROME netCDF files nor the 4152-row prediction artifact were preserved in the repository.

Executing the surviving pipeline yields the 37-feature Stage8.1 baseline (36.188657 W/m² MAE).

## Provenance Conclusion
- **STAGE8.17A STATUS:** `STAGE8.17A = NOT RECONSTRUCTABLE`
- **Classification:** Historical reported numbers (35.241085 MAE) remain UNVERIFIED REFERENCE ONLY. They cannot be used as an authoritative benchmark without verified input lineage and prediction tables.
"""

s17a_audit_json = {
    "status": "STAGE8.17A = NOT RECONSTRUCTABLE",
    "historical_reported_mae": 35.241085,
    "current_executable_mae": 36.188657,
    "reproduced": False,
    "provenance_status": "UNVERIFIED_HISTORICAL_REFERENCE_ONLY"
}

# 3. STAGE8_19_CLEAN_REVALIDATION_PLAN
s19_plan_md = """# Stage8.19 Clean Revalidation Plan

## Objective
Conduct a clean revalidation of Stage8.19 (ABIS ZTD + AROME disagreement features) on the locked 173 ODD test set using only real surviving input artifacts.

## Governance & Anti-Failure Constraints
1. **Rule 1 & 12:** NEVER hardcode metrics into evaluation scripts or import metric variables.
2. **Rule 5:** Synthetic data (e.g. `np.random.seed(819)` / `np.random.seed(817)`) can NEVER be used to claim real-model improvement.
3. **Rule 10 & 11:** Metrics must be independently verified by loading prediction CSVs from disk.

## Pre-Conditions & Input Lineage Verification
1. Real raw ABIS GNSS ZTD observation files: **MISSING**
2. Real raw AROME-Arctic NWP data: **MISSING**
3. Stage8.19 Feature Matrix: **MISSING (Only synthetic generator script exists)**

## Execution Decision
Because real ABIS and real AROME inputs are missing, and synthetic generation is strictly prohibited:
**STATUS: STAGE8.19 = NOT RECONSTRUCTABLE**
Clean revalidation is aborted.
"""

s19_plan_json = {
    "status": "STAGE8.19 = NOT RECONSTRUCTABLE",
    "reason": "Real raw ABIS ZTD observations and real AROME data are missing",
    "synthetic_fallback_allowed": False,
    "preconditions_met": False
}

# 4. STAGE8_19_CLEAN_REVALIDATION_AUDIT
s19_audit_md = """# Stage8.19 Clean Revalidation Audit

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
"""

s19_audit_json = {
    "status": "STAGE8.19 = NOT RECONSTRUCTABLE",
    "invalidated_historical_mae": 34.821405,
    "invalidated_historical_nmae": 27.0081,
    "reason_for_invalidation": "Hardcoded metric literals following dynamic evaluation failure",
    "clean_rerun_possible": False,
    "provenance_status": "INVALIDATED_AND_EXPUNGED"
}

artifacts = [
    ('forecasting/reports/stage8/STAGE8_17A_REVALIDATION_PLAN.md', s17a_plan_md),
    ('forecasting/reports/stage8/STAGE8_17A_REVALIDATION_PLAN.json', json.dumps(s17a_plan_json, indent=2)),
    ('forecasting/reports/stage8/STAGE8_17A_REVALIDATION_AUDIT.md', s17a_audit_md),
    ('forecasting/reports/stage8/STAGE8_17A_REVALIDATION_AUDIT.json', json.dumps(s17a_audit_json, indent=2)),
    ('forecasting/reports/stage8/STAGE8_19_CLEAN_REVALIDATION_PLAN.md', s19_plan_md),
    ('forecasting/reports/stage8/STAGE8_19_CLEAN_REVALIDATION_PLAN.json', json.dumps(s19_plan_json, indent=2)),
    ('forecasting/reports/stage8/STAGE8_19_CLEAN_REVALIDATION_AUDIT.md', s19_audit_md),
    ('forecasting/reports/stage8/STAGE8_19_CLEAN_REVALIDATION_AUDIT.json', json.dumps(s19_audit_json, indent=2)),
]

for filename, content in artifacts:
    p1 = os.path.join(root_dir, filename)
    p2 = os.path.join(stage8_dir, filename)
    with open(p1, 'w') as f:
        f.write(content)
    with open(p2, 'w') as f:
        f.write(content)
    print(f'Wrote {filename} cleanly')
