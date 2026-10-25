# POLARIS STAGE 7.5 — ODD CONTROL DISCREPANCY FORENSIC AUDIT

**Stage:** Stage 7.5 Terrain / Horizon Radiative Geometry  
**Audit Date:** September 12, 2026  
**Audit Type:** Critical Control Discrepancy Forensic Audit  
**Audit Verdict:** `CONTROL RECONSTRUCTION DISCREPANCY IDENTIFIED`  
**Stage 7.5 Candidate Status:** `EVEN-CV PASSED / CANDIDATE FROZEN PENDING AUTHORIZED CORRECTION`  
**Official Operational Champion Status:** `STAGE 6.6 LWP/IWP MODEL RETAINED AS OFFICIAL OPERATIONAL CHAMPION`

---

## 1. Executive Forensic Summary

A forensic audit was performed to trace the source of the reported control MAE of **$37.344943\text{ W/m}^2$** in the Stage 7.5 official ODD evaluation script.

### Key Audit Findings
1. **Source of $37.344943\text{ W/m}^2$ Control**:
   - The Stage 7.5 evaluation script `run_stage7_5_official_odd_evaluation.py` executed `fit_stage4_parameters(tr_df)`, dynamically refitting Stage 4 parameters $(w_h, k_h)$ per horizon hour on the 174 EVEN training origins instead of using the globally frozen Stage 4 parameters (`ensemble_parameters.json` / `ensemble_predictions.csv`).
   - This refit shifted the Stage 4 baseline predictions and resulted in a refitted control model MAE of $37.344943\text{ W/m}^2$.

2. **Authoritative Frozen Stage 6.6 Control**:
   - Under the true globally frozen Stage 4 pipeline (`pred_stage4_full` from `stage4_results/ensemble_predictions.csv`), the Stage 6.6 Official Operational Champion ODD MAE is **$37.005888\text{ W/m}^2$** (nMAE $= 28.7026\%$, RMSE $= 65.671702\text{ W/m}^2$).
   - (The Stage 5.2 baseline control is **$39.084821\text{ W/m}^2$**).

3. **Candidate Pipeline Integrity Audit**:
   - The Stage 7.5 candidate feature set (35 features) and model architecture (`HistGradientBoostingRegressor`) remain 100% frozen and valid.
   - Evaluated under the refitted Stage 4 pipeline, candidate MAE was $36.609806\text{ W/m}^2$.
   - Evaluated under the **True Globally Frozen Stage 4 Pipeline**, candidate MAE is **$36.613571\text{ W/m}^2$** (outperforming the Stage 6.6 champion $37.005888\text{ W/m}^2$ by $\Delta\text{MAE} = -0.392318\text{ W/m}^2$).

4. **Bootstrap Validity Status**:
   - The previously reported bootstrap ($\Delta\text{MAE} = -0.743792\text{ W/m}^2$, 95% CI $[-1.376971, -0.105857]$) was computed relative to the refitted control ($37.344943\text{ W/m}^2$) and is marked **INVALID FOR FINAL CHAMPION CLAIM**.
   - Under the globally frozen pipeline, the corrected paired origin-level bootstrap yields: Mean $\Delta\text{MAE} = -0.397063\text{ W/m}^2$, 95% CI $[-0.791521, +0.001941]\text{ W/m}^2$ ($97.43\%$ of resamples $< 0$).

5. **Governance Action**:
   - Stage 6.6 LWP/IWP Model is retained as the **OFFICIAL OPERATIONAL CHAMPION** for governance purposes.
   - Stage 7.5 candidate declaration as champion is **PAUSED** pending explicit authorization for the corrected ODD evaluation.

---

## 2. Forensic Traceability Summary

| Question | Forensic Audit Finding |
|---|---|
| **A. Globally frozen Stage 4 parameters used?** | **NO**. `fit_stage4_parameters(tr_df)` refitted Stage 4 parameters on EVEN origins. |
| **B. Stage 4 refitted on EVEN origins?** | **YES**. Parameters $(w_h, k_h)$ were refitted per horizon hour on 174 EVEN training origins. |
| **C. Stage 6.6 recalibrated?** | **NO**. Model architecture and features were unchanged. |
| **D. Control model retrained?** | **YES**. Control was retrained on refitted Stage 4 residuals. |
| **E. Control predictions reconstructed?** | **YES**. Control predictions were reconstructed rather than loading authoritative Stage 6.6 predictions. |
| **F. Exact artifact producing $37.344943\text{ W/m}^2$?** | `run_stage7_5_official_odd_evaluation.py` executing `fit_stage4_parameters(tr_df)`. |

---

## 3. Governance Status & Next Steps

- **Stage 7.5 Status**: `EVEN_CV_PASSED_CANDIDATE_FROZEN_PENDING_CORRECTED_ODD_AUTHORIZATION`
- **Stage 6.6 Status**: `STAGE_6_6_LWP_IWP_PRESERVED_AS_OFFICIAL_CHAMPION`
- **Action**: Await explicit authorization to run the corrected ODD evaluation under the globally frozen Stage 4 pipeline.
