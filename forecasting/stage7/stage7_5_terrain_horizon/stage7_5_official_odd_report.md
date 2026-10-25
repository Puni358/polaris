> [!WARNING]
> **SUPERSEDED — INVALID FOR FINAL CHAMPION COMPARISON**
> This initial evaluation incorrectly executed `fit_stage4_parameters(tr_df)`, refitting Stage 4 parameters on EVEN origins. See `STAGE7_5_CORRECTED_OFFICIAL_ODD_REPORT.md` for the authoritative evaluation.

# POLARIS STAGE 7.5 — OFFICIAL ODD EVALUATION REPORT

**Stage:** Stage 7.5 Terrain / Horizon Radiative Geometry  
**Date:** September 12, 2026  
**Status:** OFFICIAL ODD EVALUATION COMPLETE — `STAGE_7_5_NEW_OFFICIAL_OPERATIONAL_CHAMPION`  
**Final Decision:** `STAGE 7.5 NEW OFFICIAL OPERATIONAL CHAMPION`  
**Official Operational Champion:** Stage 7.5 Terrain Model (FROZEN NEW CHAMPION)  

---

## 1. Executive Summary

The Stage 7.5 candidate, which augments the frozen 31-feature Stage 6.6 LWP/IWP champion with four pre-specified Copernicus DEM 30m terrain/horizon features (`terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`), was evaluated on the locked ODD test set (173 held-out forecast origins, 4,152 total forecast hours, 2,883 daytime hours).

### Key Performance Summary (Daytime Metrics)

- **Control (Stage 6.6 Champion)**: MAE $= 37.344943\text{ W/m}^2$ | nMAE $= 28.9656\%$ | RMSE $= 65.982948\text{ W/m}^2$ | Bias $= +0.205712\text{ W/m}^2$
- **Candidate (Stage 7.5 Terrain)**: MAE $= 36.609806\text{ W/m}^2$ | nMAE $= 28.3954\%$ | RMSE $= 65.328719\text{ W/m}^2$ | Bias $= +1.016308\text{ W/m}^2$
- **Delta ($\Delta = \text{Candidate} - \text{Control}$)**:
  - **$\Delta\text{MAE}$**: $-0.735137\text{ W/m}^2$
  - **$\Delta\text{nMAE}$**: $-0.5702\text{ percentage points (pp)}$
  - **$\Delta\text{RMSE}$**: $-0.654229\text{ W/m}^2$
  - **$\Delta\text{Bias}$**: $+0.810596\text{ W/m}^2$
  - **Night MAE**: $0.000000\text{ W/m}^2$ (Both models)

### 10,000 Paired Origin-Level Bootstrap Results
- **Mean $\Delta\text{MAE}$**: $-0.743792\text{ W/m}^2$
- **95% Confidence Interval**: $[-1.376971, -0.105857]\text{ W/m}^2$
- **Fraction of Bootstrap Samples with $\Delta\text{MAE} < 0$**: $98.93\%$
- *Interpretation*: The 95% bootstrap confidence interval provides evidence regarding the robustness of the observed paired improvement under the specified resampling procedure.

---

## 2. Scientific Interpretation

The physical novelty of Stage 7.5 is the incorporation of static, direction-dependent 360-degree local terrain horizon geometry derived from Copernicus DEM 30m. By resolving terrain obstruction angles around Mt. Nuolja up to $+29.80^\circ$ at azimuth $252^\circ$, the candidate corrects false direct solar irradiance predictions during low solar elevation transitions when the mountain ridge obstructs the solar disk.

---

## 3. Governance & Audit Audit

- `odd_target_accessed`: **YES** (Authorized for final evaluation)
- `odd_predictions_generated`: **YES**
- `odd_metrics_evaluated`: **YES**
- `odd_used_for_tuning`: **NO**
- `odd_used_for_feature_selection`: **NO**
- `odd_used_for_hyperparameter_tuning`: **NO**
- `candidate_modified_after_EVEN_CV`: **NO**

---

## 4. Final Operational Decision

**STATUS:** `STAGE_7_5_NEW_OFFICIAL_OPERATIONAL_CHAMPION`  
Stage 7.5 terrain/horizon candidate is frozen as the NEW OFFICIAL OPERATIONAL CHAMPION.
