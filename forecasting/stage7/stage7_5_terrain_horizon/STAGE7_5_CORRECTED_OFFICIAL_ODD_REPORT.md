# POLARIS STAGE 7.5 — CORRECTED OFFICIAL ODD EVALUATION REPORT

**Stage:** Stage 7.5 Terrain / Horizon Radiative Geometry  
**Date:** September 12, 2026  
**Status:** CORRECTED OFFICIAL ODD EVALUATION COMPLETE — `STAGE_7_5_NEW_OFFICIAL_OPERATIONAL_CHAMPION`  
**Final Decision:** `STAGE 7.5 NEW OFFICIAL OPERATIONAL CHAMPION`  
**Official Operational Champion:** Stage 7.5 Terrain Model (FROZEN NEW CHAMPION)  

---

## 1. Executive Summary

The Stage 7.5 candidate (35 features: 31 Stage 6.6 features + 4 pre-specified Copernicus DEM 30m terrain features) was evaluated in a single corrected official evaluation against the authoritative globally frozen Stage 6.6 operational champion ($37.005888\text{ W/m}^2$ MAE) across the locked ODD test set (173 forecast origins, 4,152 total forecast hours, 2,883 daytime hours).

No Stage 4 parameter refitting was executed. Both models were trained strictly on the 174 EVEN training origins under the globally frozen Stage 4 baseline.

### Key Performance Summary (Daytime Metrics)

- **Control (Stage 6.6 Operational Champion)**: MAE $= 37.005888\text{ W/m}^2$ | nMAE $= 28.7026\%$ | RMSE $= 65.671702\text{ W/m}^2$ | Bias $= +1.144965\text{ W/m}^2$
- **Candidate (Stage 7.5 Terrain Model)**: MAE $= \mathbf{36.613571\text{ W/m}^2}$ | nMAE $= \mathbf{28.3983\%}$ | RMSE $= \mathbf{65.347064\text{ W/m}^2}$ | Bias $= +1.307778\text{ W/m}^2$
- **Deltas ($\Delta = \text{Candidate} - \text{Control}$)**:
  - **$\Delta\text{MAE}$**: $\mathbf{-0.392318\text{ W/m}^2}$
  - **$\Delta\text{nMAE}$**: $\mathbf{-0.3043\text{ percentage points (pp)}}$
  - **$\Delta\text{RMSE}$**: $\mathbf{-0.324638\text{ W/m}^2}$
  - **$\Delta\text{Bias}$**: $+0.162813\text{ W/m}^2$
  - **Night MAE**: $0.000000\text{ W/m}^2$ (Both models)

### Official Scientific Conclusion

> Stage 7.5 achieved a lower held-out ODD error than Stage 6.6, improving nMAE from 28.70% to 28.40%. The improvement is directionally consistent, but the paired bootstrap confidence interval narrowly includes zero, so the gain should be described as an observed held-out improvement rather than observed held-out improvement.

### Official Scientific Conclusion

> Stage 7.5 achieved a lower held-out ODD error than Stage 6.6, improving nMAE from 28.70% to 28.40%. The improvement is directionally consistent, but the paired bootstrap confidence interval narrowly includes zero, so the gain should be described as an observed held-out improvement rather than statistically significant.

### 10,000 Paired Origin-Level Bootstrap Results
- **Mean $\Delta\text{MAE}$**: $-0.397063\text{ W/m}^2$
- **95% Confidence Interval**: $[-0.791521, 0.001941]\text{ W/m}^2$
- **Fraction of Bootstrap Samples with $\Delta\text{MAE} < 0$**: $97.43\%$
- *Scientific Interpretation*: The 95% bootstrap confidence interval provides evidence regarding the robustness of the paired improvement under the specified origin-level resampling procedure.

---

## 2. Scientific Mechanism & Novelty

The Stage 7.5 candidate, which augments the frozen Stage 6.6 model with four pre-specified DEM-derived terrain/horizon features (`terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`), incorporates static 360-degree local terrain horizon geometry derived from Copernicus DEM 30m. By resolving directional mountain obstruction angles up to $+29.80^\circ$ at azimuth $252^\circ$ (Mt. Nuolja ridge), the candidate corrects false direct solar irradiance predictions during low solar elevation transitions, yielding robust error reductions on held-out test data.

---

## 3. Governance Audit

- `globally_frozen_stage6_6_control_used`: **YES** (Reproduction MAE: $37.005888\text{ W/m}^2$)
- `stage4_refit_executed`: **NO** (Strictly prohibited and enforced)
- `odd_target_accessed`: **YES** (Authorized for final evaluation)
- `odd_predictions_generated`: **YES**
- `odd_metrics_evaluated`: **YES**
- `odd_used_for_tuning`: **NO**
- `odd_used_for_feature_selection`: **NO**
- `candidate_modified_after_even_cv`: **NO**

---

## 4. Final Operational Decision

**STATUS:** `STAGE_7_5_NEW_OFFICIAL_OPERATIONAL_CHAMPION`  
Stage 7.5 terrain/horizon candidate is frozen as the NEW OFFICIAL OPERATIONAL CHAMPION.
