# POLARIS STAGE 8.1 — OFFICIAL HELD-OUT ODD EVALUATION REPORT

**Stage:** Stage 8.1 700 hPa Free-Atmosphere Steering Wind Experiment  
**Evaluation Date:** September 12, 2026  
**Evaluation Type:** Official Held-Out ODD Evaluation  
**Stage Status:** `STAGE_8_1_NEW_OFFICIAL_OPERATIONAL_CHAMPION`  
**Official Operational Champion:** **Stage 8.1 U700+V700 Steering Wind Model** (NEW OPERATIONAL CHAMPION)  
**Previous Operational Champion:** Stage 7.5 Terrain Model ($36.613571\text{ W/m}^2$ MAE)

---

## 1. Executive Summary

The official held-out ODD evaluation of the frozen **Stage 8.1 candidate ($U_{700} + V_{700}$ steering wind model)** was executed across all 173 held-out test origins ($4,152$ total forecast hours, $2,883$ daytime validation hours).

### Key Findings
1. **Control Reproduction**: **PASS** (Frozen Stage 7.5 control daytime MAE $= 36.613571\text{ W/m}^2$, nMAE $= 28.3983\%$, RMSE $= 65.347064\text{ W/m}^2$ reproduced exactly).
2. **Candidate Performance**: Stage 8.1 achieved a daytime MAE of **$36.188657\text{ W/m}^2$** (nMAE **$28.0688\%$**, RMSE **$64.219495\text{ W/m}^2$**), outperforming Stage 7.5 on all error metrics.
3. **Out-of-Distribution Improvement**:
   - $\Delta\text{MAE} = \mathbf{-0.424913\text{ W/m}^2}$
   - $\Delta\text{nMAE} = \mathbf{-0.3296\text{ pp}}$
   - $\Delta\text{RMSE} = \mathbf{-1.127569\text{ W/m}^2}$
   - Night MAE $= 0.000000\text{ W/m}^2$ (Both models)
4. **Statistical Bootstrap**: 10,000 paired origin-level bootstrap resamples (seed $= 42$) yielded a mean $\Delta\text{MAE} = -0.424222\text{ W/m}^2$, 95% CI $[-0.887999, +0.026372]\text{ W/m}^2$, with $96.65\%$ of resamples showing candidate improvement ($\Delta\text{MAE} < 0$).
5. **Governance Compliance**: Zero Stage 4 refitting (`fit_stage4_parameters`: NO), zero feature modification post EVEN-CV, zero hyperparameter tuning.

---

## 2. Official Held-Out ODD Numerical Results

| Model | Daytime MAE (W/m²) | Daytime nMAE (%) | Daytime RMSE (W/m²) | Daytime Bias (W/m²) | Night MAE (W/m²) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Stage 7.5 Champion** | $36.613571$ | $28.3983\%$ | $65.347064$ | $+1.307778$ | $0.000000$ |
| **Stage 8.1 Candidate** | **$36.188657$** | **$28.0688\%$** | **$64.219495$** | $+1.439399$ | $0.000000$ |
| **Delta ($\Delta$)** | **$-0.424913$** | **$-0.3296\text{ pp}$** | **$-1.127569$** | $+0.131622$ | $0.000000$ |

---

## 3. Conservative Scientific Interpretation

Stage 8.1 added 700 hPa free-atmosphere $U/V$ wind to the frozen Stage 7.5 feature set and achieved a lower error on the held-out ODD set ($\Delta\text{MAE} = -0.424913\text{ W/m}^2$, $\Delta\text{RMSE} = -1.127569\text{ W/m}^2$). This provides evidence that 700 hPa wind contains additional predictive information under the POLARIS benchmark, consistent with its role as a free-atmosphere steering-flow proxy. The result does not establish that 700 hPa wind directly measures cloud motion or advection.
