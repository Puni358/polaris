# POLARIS STAGE 7.4 — MEPS VERTICAL CLOUD STRUCTURE FORECASTING EXPERIMENT REPORT

**Stage Status:** `STAGE_7_4_CLOSED`  
**Date:** September 12, 2026  
**Candidate Decision:** REJECTED  
**Official Operational Champion:** Stage 6.6 LWP/IWP Model (FROZEN & UNTOUCHED)  
**Next Stage Status:** NOT_STARTED  

---

## 1. Executive Summary

Stage 7.4 tested the hypothesis that adding 13-level vertical cloud structure diagnostics from MEPS pressure-level forecasts (`f_lwp_low`, `f_lwp_mid`, `f_lwp_high`, `p_centroid_lwp`, `p_centroid_iwp`, `dp_ice_liquid_centroid`, `cloud_frac_mid`, `cloud_frac_high`) beyond the frozen 31-feature Stage 6.6 LWP/IWP champion improves 24-hour surface shortwave radiation forecasting accuracy.

Following the locked governance protocol:
1. **Pre-CV Audit**: All 347 clean origins ($8,328$ rows) were extracted using surface-aware pressure integration ($p_{\text{sfc}}$ boundary truncation). Range checks passed with zero NaNs, Infs, or duplicates.
2. **Exact Control Reproduction**: Candidate control E0 perfectly reproduced the frozen Stage 6.6 EVEN CV control baseline (MAE $= 38.280605\text{ W/m}^2$, nMAE $= 40.3918\%$, RMSE $= 60.750856\text{ W/m}^2$).
3. **Candidate E1 Evaluation**: Candidate E1 (39 features: 31 Stage 6.6 + 8 vertical cloud features) achieved an aggregate EVEN CV daytime MAE of $38.286927\text{ W/m}^2$ (a slight degradation of $+0.006322\text{ W/m}^2$ vs control).
4. **Acceptance Gates Audit**: Candidate E1 **FAILED all 5 predeclared acceptance gates**.

Consequently, **Stage 7.4 is REJECTED**. Stage 6.6 LWP/IWP remains the official frozen operational champion.

---

## 2. Five-Point ODD Access Classification

ODD target values were never loaded, read, evaluated, or used. No ODD predictions or ODD performance metrics were generated. ODD information was not used for tuning, feature selection, preprocessing, threshold selection, or model selection. MEPS feature inputs were nevertheless extracted for all 347 origins, including the 173 ODD origins, during the common feature-preparation step. Therefore ODD feature-input access occurred, but ODD target access and ODD evaluation did not.

- `odd_target_accessed`: **false**
- `odd_feature_accessed`: **true**
- `odd_predictions_generated`: **false**
- `odd_metrics_evaluated`: **false**
- `odd_used_for_tuning`: **false**

---

## 3. Candidate E1 Cross-Validation & Acceptance Gate Results

### Aggregate Metrics Comparison (EVEN CV Daytime)

| Metric | Control (E0) | Candidate (E1) | Delta (E1 - E0) | Status |
|---|---|---|---|---|
| **MAE** | **38.280605 W/m²** | **38.286927 W/m²** | **+0.006322 W/m²** | **Degraded** |
| **nMAE** | **40.3918%** | **40.6501%** | **+0.2583 pp** | **Degraded** |
| **RMSE** | **60.750856 W/m²** | **61.229533 W/m²** | **+0.478677 W/m²** | **Degraded** |
| **Bias** | **+2.419115 W/m²** | **+2.321601 W/m²** | **-0.097514 W/m²** | **Improved** |

### Per-Fold Breakdown (Daytime MAE in W/m²)

| Fold | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Fold Improved? | Max Degradation Gate Pass? |
|---|---|---|---|---|---|
| **Fold 1** | 49.817392 | 49.767571 | -0.049821 | **YES** | PASS |
| **Fold 2** | 71.077463 | 70.616118 | -0.461345 | **YES** | PASS |
| **Fold 3** | 41.261951 | 40.747917 | -0.514034 | **YES** | PASS |
| **Fold 4** | 26.804209 | 27.845296 | +1.041087 | **NO** | **FAIL (+1.041087 > +0.15)** |
| **Fold 5** | 2.442011 | 2.457732 | +0.015721 | **NO** | PASS |

---

## 4. Scientific Interpretation

The tested eight-feature vertical cloud structure representation did not provide robust improvement under the current POLARIS benchmark and model architecture. Although Folds 1–3 improved, Fold 4 degraded by +1.0411 W/m² and the aggregate candidate MAE was essentially unchanged (+0.0063 W/m²). The candidate therefore failed all five predefined acceptance gates and was rejected.

---

## 5. Governance & Integrity Audit Summary

- **Stage Status**: `STAGE_7_4_CLOSED`
- **Candidate Decision**: `REJECTED`
- **Stage 6.6 Champion Status**: Frozen & Unchanged (`STAGE_6_6_LWP_IWP`).
- **Next Stage Status**: `NOT_STARTED`
