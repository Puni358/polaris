# POLARIS Stage 6.1 — Experiment Specification Plan

## 1. Executive Summary & Purpose
Stage 6.1 evaluates the 30-member MET Norway MEPS ensemble prediction system to determine whether ensemble uncertainty summary statistics provide incremental predictive value beyond the frozen Stage 5.2 champion ($39.084821\text{ W/m}^2$ ODD Daytime MAE / $30.32\%\text{ nMAE}$).

## 2. Predeclared Candidate Features (6)
1. `meps_mean_SW_IN`: Ensemble mean GHI (W/m²)
2. `meps_std_SW_IN`: Ensemble GHI spread (W/m²)
3. `meps_mean_total_cloud`: Ensemble mean cloud fraction ([0, 1])
4. `meps_std_total_cloud`: Ensemble cloud fraction spread ([0, 1])
5. `meps_std_wind_speed`: Ensemble 10m wind speed spread (m/s)
6. `meps_std_precip`: Ensemble precipitation accumulation spread (kg/m²)

## 3. Predefined EVEN-CV Decision Gate
- Aggregate EVEN MAE Delta $\le -0.20\text{ W/m}^2$.
- Per-fold consistency: $\ge 4/5$ folds improved ($\\ge 80\%$).
- Max single-fold degradation $\le +0.15\text{ W/m}^2$.
- Neutral/improved nMAE and RMSE metrics.

## 4. Benchmark Verification
- Base Stage 5.2 EVEN-CV Baseline: 39.4236 W/m² (100% Reproduction).
