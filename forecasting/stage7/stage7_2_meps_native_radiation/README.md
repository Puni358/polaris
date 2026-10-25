# POLARIS Stage 7.2 — MEPS Native Surface Radiation Forecasting Experiment

## Objective
Stage 7.2 evaluates whether adding native surface shortwave radiation forecast outputs from MET Norway's MEPS NWP model (`surface_downwelling_shortwave_flux_in_air`, `integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time`, net shortwave, and DNI) improves solar irradiance forecasting accuracy beyond the frozen **Stage 6.6 LWP/IWP Champion**.

## Locked Benchmark Protocol Enforced
- **Zero ODD Access**: The 173 ODD test origins were **never loaded, read, evaluated, or predicted**.
- **Frozen Champion**: Stage 6.6 LWP/IWP Champion (ODD MAE = 37.0059 W/m², nMAE = 28.7026%) remains unmodified.
- **Model Architecture & Hyperparameters**: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)` kept strictly identical to Stage 6.6.
- **5-Fold Forward-Chaining EVEN CV**: Evaluated on 174 EVEN development origins across 5 strict forward-chaining folds.

## Experiments Tested
1. **E0 (Frozen Stage 6.6 Control)**: 31 features (28 Stage 5.2 base features + `lwp_latest` + `iwp_latest` + `lwp_x_cloud`).
2. **E1 (Native MEPS Instantaneous GHI)**: E0 + `meps_sw_instant` (Instantaneous W/m²).
3. **E2 (Hourly MEPS Accumulated-SW Derivative)**: E0 + `meps_sw_hourly_derived` (Hourly W/m² derived via $[	ext{acc}(H_k) - 	ext{acc}(H_{k-1})]/3600$).
4. **E3 (MEPS Radiation-Scheme Feature Set)**: E0 + `meps_sw_instant` + `meps_sw_hourly_derived` + `meps_net_sw_hourly_derived` + `meps_clearsky_net_sw_hourly_derived`.
5. **E4 (Optional Direct-Normal Component)**: E0 + `meps_sw_hourly_derived` + `meps_dni_hourly_derived` (with nocturnal sentinel code $9.96921 	imes 10^{36}$ masked to 0.0).

## Acceptance Gates (vs E0 Control 38.2806 W/m²)
1. Aggregate MAE improvement $\ge 0.20$ W/m² (Required MAE $\le 38.0806$ W/m²).
2. Improve at least 4 of 5 EVEN CV folds.
3. No individual fold degrades by $> +0.15$ W/m².
4. nMAE $\le 40.39$%.
5. RMSE $\le 60.7509$ W/m².

## Artifact Inventory
- `README.md`: Stage 7.2 documentation and protocol rules.
- `run_stage7_2.py`: Self-contained execution pipeline for E0-E4 CV evaluation.
- `meps_radiation_features.csv`: Extracted MEPS native radiation features across all 347 clean origins.
- `stage7_2_even_cv_results.csv`: Summary of EVEN CV results for E0-E4 candidates and gate decisions.
- `stage7_2_fold_results.csv`: Per-fold MAE and delta MAE breakdown for all candidates.
- `stage7_2_feature_inventory.json`: JSON inventory of feature sets tested.
- `stage7_2_causality_audit.csv`: 347-origin causality audit file.
- `stage7_2_temporal_alignment_audit.csv`: Multi-seasonal temporal alignment audit file.
- `stage7_2_decision.json`: Formal gate decision JSON.
- `stage7_2_report.md`: Detailed scientific report.
- `reproducibility_notes.md`: Environmental details and protocol reproduction instructions.
