# POLARIS Stage 4 — Methodology Report

## Method: Horizon-Adaptive Cloud-Damped Clearsky Ensemble

### Model Architecture

For each forecast horizon h ∈ {1, ..., 24}:

```
SW_pred(h) = max(0, w_h · Chronos_3B(h) + (1 - w_h) · max(0, clearsky_ghi(h) · (1 - k_h · cloud_frac(h))))
```

Where:
- `Chronos_3B(h)` = locked Stage 3B prediction (Chronos-2 + solar geometry + cloud NWP)
- `clearsky_ghi(h)` = modeled clear-sky global horizontal irradiance
- `cloud_frac(h)` = NWP forecast cloud fraction (fc_cloud_cover / 100)
- `w_h` = horizon-specific Chronos weight (learned)
- `k_h` = horizon-specific cloud damping coefficient (learned)

### Train/Test Split

- **Split method**: Odd/even temporal interleaving of forecast origins
- **Train**: 174 origins (even-indexed), 4,176 total hours, 2,885 daytime
- **Test**: 173 origins (odd-indexed), 4,152 total hours, 2,883 daytime
- **Both splits cover all 12 months**
- **All parameters fitted exclusively on train data**
- **Test set used only for final evaluation**

### Fitting Procedure

For each horizon h:
1. Select all train-split daytime hours with horizon_hour == h
2. Optimize (w_h, k_h) to minimize MAE on this subset
3. Grid-search initialization: 25 points (w, k) ∈ {0.1, 0.3, 0.5, 0.7, 0.9}²
4. Nelder-Mead refinement with convergence tolerance 1e-6
5. Clip final parameters to [0, 1]

### Residual Correction Investigation

Five candidate corrections were tested (all fitted on train, evaluated on test):

1. **Global Ridge Regression** — WORSENED by +28 W/m² (overfitting to seasonal patterns)
2. **Horizon-Specific Affine** — WORSENED at most horizons 
3. **Regime-Conditioned Affine** — WORSENED by +1.5 W/m²
4. **Ridge with Physics Interactions** — WORSENED by +27–32 W/m²
5. **Isotonic Regression** — WORSENED by +1.7 W/m²

**Conclusion**: No residual correction improved upon the raw ensemble. The ensemble already captures the exploitable predictive structure in the available features.

### Why Residual Corrections Failed

The residual corrections failed because the odd/even split creates a train/test distribution mismatch 
at the individual-day level. Each day's weather is unique, and fitting a regression on even days 
does not generalize to the distinct weather patterns of odd days. The ensemble's per-horizon structure 
already captures the systematic component; what remains is stochastic weather variability that cannot 
be predicted from the available features.

### Artifacts

All artifacts saved to: `/home/punith-bs/01polaris (Copy)/stage4/stage4_results/`

| File | Description |
|---|---|
| `ensemble_parameters.json` | All 48 learned parameters (w_h, k_h for h=1..24) |
| `ensemble_predictions.csv` | Full 8,328-row prediction file |
| `final_metrics.csv` | Stage 3B vs Ensemble summary metrics |
| `horizon_comparison.csv` | Per-horizon S3B vs Ensemble (test) |
| `monthly_metrics.csv` | Monthly nMAE comparison |
| `seasonal_metrics.csv` | Seasonal nMAE comparison |
| `cloud_regime_metrics.csv` | Cloud-regime MAE comparison |
| `solar_regime_metrics.csv` | Solar-regime MAE comparison |
| `kt_bin_metrics.csv` | Clear-sky index bin comparison |
| `correction_parameters.json` | Ridge/affine parameters (for documentation) |

### Reproduction Command

```bash
/home/punith-bs/01polaris\ \(Copy\)/chronos/.venv/bin/python \
  "/home/punith-bs/01polaris (Copy)/stage4/run_stage4_pipeline.py"
```
