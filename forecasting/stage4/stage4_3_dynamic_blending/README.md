# POLARIS Stage 4.3 — Dynamic Blending Experiment

## Executive Summary

**Experiment**: Delta-parameterized dynamic blending with state-dependent weight adjustment  
**Status**: **REJECTED** — No improvement over Stage 4 baseline  
**Official Champion**: **Stage 4** (fixed horizon-specific weights) remains active

---

## Research Hypothesis

> The optimal balance between Chronos neural forecast and physics-based NWP forecast is STATE-DEPENDENT rather than fixed solely by horizon.

**Mathematical Formulation:**
```
logit(w_dynamic) = logit(w_stage4_h) + X_scaled @ theta
P_dynamic = w_dynamic * P_chronos + (1 - w_dynamic) * P_physics
```

where:
- `w_stage4_h` = Stage 4 fixed horizon weight (strong prior)
- `theta` = learned parameter vector (state-dependent adjustment)
- `X` = forecast-time features (10 total)

---

## Methodology

### Data Split
- **Training set**: 174 EVEN-indexed origins (2024-01-20, 2024-01-22, ..., 2024-12-31)
- **Test set**: 173 ODD-indexed origins (2024-01-21, 2024-01-23, ..., 2024-12-30)
- **Split rule**: Temporally interleaved, deterministic, no overlap
- **Training samples**: 2,885 daytime hours
- **Test samples**: 2,883 daytime hours

### Feature Set (10 features)
1. `solar_elevation` — Solar elevation angle (deterministic)
2. `clearsky_ghi` — Clear-sky irradiance from PVLIB (deterministic)
3. `horizon_hour` — Forecast lead time (1-24)
4. `cloud_frac` — NWP total cloud fraction (0-1)
5. `ctx_mean` — Mean SW_IN previous 24h (historical)
6. `ctx_max` — Max SW_IN previous 24h (historical)
7. `ctx_std` — Std dev SW_IN previous 24h (historical)
8. `pred_stage3b_cloud_nwp` — Chronos prediction (P_chronos)
9. `pred_physics` — Physics prediction (P_physics)
10. `clearsky_x_clearfrac` — Expected irradiance under forecast clouds

**Leakage Audit**: ✅ All features available at forecast issuance, no future actual SW_IN

### Model Training
- **Model**: Logistic Ridge Regression (delta-parameterization)
- **Loss**: Huber loss (δ=10 W/m²) + L2 regularization
- **Hyperparameter selection**: Forward-chaining 4-fold CV within EVEN origins
- **Selected λ**: 100.0 (CV MAE = 21.582 W/m²)
- **Optimization**: L-BFGS-B (converged in 6 iterations)

### Validation Strategy
- **Forward-chaining CV**: Training data always temporally before validation
- **Minimum training size**: 100 origins per fold
- **NO test-set information** used for model selection, feature selection, or hyperparameter tuning

---

## Results

### Test Set Performance (173 ODD Origins, Daytime)

| Model | MAE | RMSE | nMAE | nRMSE | Bias |
|-------|-----|------|------|-------|------|
| **Stage 4** (baseline) | **43.451 W/m²** | **74.853 W/m²** | **33.70%** | 58.06% | -1.972 W/m² |
| Stage 4.3 (dynamic) | 43.463 W/m² | 74.863 W/m² | 33.71% | 58.07% | -2.289 W/m² |

**Improvement:**
- Δ MAE: **+0.012 W/m²** (+0.03%) — **DEGRADATION**
- Δ nMAE: **+0.01 pp**

### Statistical Significance
- **Bootstrap 95% CI**: [-0.055, +0.063] W/m²
- **Paired t-test p-value**: 0.9791
- **Conclusion**: No statistically significant difference (p >> 0.05)

### Per-Horizon Analysis
- **Improved horizons** (Δ < -0.1): 2 / 24 (H16, H18)
- **Degraded horizons** (Δ > +0.1): 3 / 24 (H10, H11, H12)
- **Neutral horizons** (|Δ| ≤ 0.1): 19 / 24

### Weight Diagnostics

**Dynamic weight statistics:**
- Mean: 0.4361 (Stage 4: 0.4345)
- Std: 0.2628 (Stage 4: 0.2633)
- Range: [0.0908, 0.9999]

**Key Finding**: Dynamic weights are **nearly identical** to Stage 4 fixed weights across samples. The model essentially reproduced the horizon-specific baseline with minimal state-dependent adjustment.

---

## Feature Importance (Learned Coefficients)

| Feature | Coefficient | Interpretation |
|---------|-------------|----------------|
| `cloud_frac` | -0.0421 | Higher clouds → slightly toward Physics |
| `clearsky_x_clearfrac` | +0.0218 | Higher expected irradiance → toward Chronos |
| `pred_stage3b_cloud_nwp` | +0.0088 | Higher Chronos pred → trust Chronos |
| `pred_physics` | +0.0081 | Higher Physics pred → trust Physics |
| `ctx_max` | +0.0069 | Recent peak → toward Chronos |
| `ctx_std` | +0.0064 | Variability → toward Chronos |
| `solar_elevation` | -0.0041 | Higher sun → slightly toward Physics |
| `horizon_hour` | -0.0037 | Later horizon → slightly toward Physics |
| `clearsky_ghi` | -0.0037 | Higher potential → slightly toward Physics |
| `ctx_mean` | -0.0016 | Minimal effect |

**Interpretation**: All coefficients are **very small** (magnitude < 0.05), indicating weak state-dependent signal. The regularization penalty (λ=100) pulled most adjustments toward zero.

---

## Diagnostic Analysis

### Multicollinearity Warning
- **Condition number**: 1694.3 (high)
- **High correlations** (|r| > 0.7):
  - `solar_elevation` ↔ `clearsky_ghi`: 0.981
  - `ctx_mean` ↔ `ctx_max`: 0.948
  - `ctx_mean` ↔ `ctx_std`: 0.969
  - `ctx_max` ↔ `ctx_std`: 0.973
  - `pred_chronos` ↔ `pred_physics`: 0.812

**Impact**: High multicollinearity makes individual coefficient interpretation difficult and may contribute to weak feature signals.

### Component Separation
- **Mean separation** |P_chronos - P_physics|: 59.29 W/m²
- **Median separation**: 25.62 W/m²
- **% with separation < 10 W/m²**: 34.7%

**Interpretation**: In ~35% of cases, Chronos and Physics predictions agree within 10 W/m², making blend weight selection nearly irrelevant. When components disagree substantially, the optimal blend is still horizon-specific.

---

## Conclusion

**OUTCOME: REJECT Stage 4.3**

### Why Dynamic Blending Failed

1. **Weak state-dependent signal**: Features do not contain sufficient information to improve upon fixed horizon-specific weights.

2. **Effective prior**: Stage 4's horizon-adaptive weights already capture the dominant pattern. State-dependent adjustments offer negligible additional value.

3. **Multicollinearity**: Redundant features (solar elevation vs clearsky GHI, context statistics) dilute predictive power.

4. **Component agreement**: When Chronos and Physics agree, blend doesn't matter. When they disagree, horizon is the dominant discriminator.

### Scientific Validity

The experiment was **methodologically sound**:
- ✅ No test-set leakage
- ✅ Proper forward-chaining CV
- ✅ True dynamic blending (not stacking)
- ✅ Strong regularization to prevent overfitting
- ✅ Statistical significance testing
- ✅ Honest reporting (no cherry-picking)

**The hypothesis was tested rigorously and found to be invalid for this dataset.**

---

## Recommendations

### Official Champion
**Stage 4 (Fixed Horizon-Adaptive Ensemble)** remains the official POLARIS forecasting champion:
- **Daytime MAE**: 43.45 W/m²
- **Daytime nMAE**: 33.70%

### Future Research Directions (If Pursued)

**Stage 4.3.v2 Options:**

1. **Feature engineering**:
   - Remove redundant features (keep only solar_elevation OR clearsky_ghi, not both)
   - Add interaction terms (e.g., cloud × solar elevation)
   - Add temporal features (time of day, season)

2. **Alternative models**:
   - Shallow decision tree (max_depth=2-3) to capture non-linear interactions
   - Separate models for different solar/cloud regimes
   - Quantile regression for uncertainty-aware blending

3. **Data expansion**:
   - More training data (if available beyond 2024)
   - Multi-site training (if POLARIS expands to other locations)

4. **Different blend targets**:
   - Instead of SW_IN prediction, optimize blend for downstream PV power prediction
   - Optimize for probabilistic skill (e.g., Continuous Ranked Probability Score)

**However**, given the near-zero improvement, the expected value of Stage 4.3.v2 is **low**. Resources are better spent on:
- Stage 5 downstream modules (PV digital twin, battery optimization)
- Improving Stage 3 base models (fine-tuning Chronos, better NWP)
- Uncertainty quantification for robust optimization

---

## Artifacts

### Files Created
- `run_stage4_3.py` — Implementation script
- `dynamic_predictions.csv` — Per-sample predictions with dynamic weights
- `dynamic_metrics.csv` — Overall metrics (Stage 4 vs Stage 4.3)
- `model_parameters.json` — Learned theta, scaler params, CV results
- `horizon_metrics.csv` — Per-horizon breakdown
- `cloud_regime_metrics.csv` — Per-cloud-regime breakdown
- `feature_importance.csv` — Coefficient magnitudes
- `cv_results.csv` — Forward-chaining CV scores
- `diagnostics.png` — 6-panel visualization
- `experiment_log.txt` — Complete console output
- `README.md` — This document

### Reproducibility
All artifacts are fully reproducible:
1. Same random seed (42) for bootstrap
2. Deterministic optimization (L-BFGS-B)
3. Fixed train/test split (even/odd origins)
4. Frozen feature set

---

## Lessons Learned

### Positive Outcomes
1. **Rigorous methodology** validated scientific process
2. **Negative result** is scientifically valuable (rules out hypothesis)
3. **Stage 4 validation** confirms existing champion is near-optimal
4. **Infrastructure** created for future blending experiments

### Technical Insights
1. Horizon is the dominant feature for SW_IN forecast blending
2. State-dependent adjustments require stronger signals than available
3. Multicollinearity is a serious concern with solar/weather features
4. Forward-chaining CV is essential for temporal data

### Research Culture
1. **Honest reporting** more valuable than forced "improvements"
2. **Failed experiments** prevent future wasted effort
3. **Negative constraints** (what doesn't work) guide future research
4. **Champion stability** gives confidence to downstream modules

---

## Status

- **Experiment date**: 2026-09-10
- **Implementation**: Complete
- **Evaluation**: Complete
- **Decision**: **REJECT** — Stage 4.3 does not improve upon Stage 4
- **Official champion**: **Stage 4** (unchanged)
- **Future work**: Not recommended unless substantial new information emerges

---

**End of Stage 4.3 Experiment Report**
