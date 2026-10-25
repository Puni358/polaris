# POLARIS Stage 5.2 — Non-Linear Architecture Research & Evaluation

## Overview
Stage 5.2 investigates whether non-linear machine learning architectures (Gradient Boosted Decision Trees, Random Forests, Multi-Stage Stackers) taking pre-forecast context volatility, solar geometry, NWP forecasts, and Stage 4 model state features can exploit non-linear structure to beat the Stage 4 champion benchmark (Daytime MAE = 43.4508 W/m², nMAE = 33.70%).

## Methodology & Strict Benchmark Rules
1. **Locked Split**: 174 EVEN training origins for 5-fold forward-chaining CV; 173 ODD test origins strictly held out.
2. **Out-of-Fold Stage 4 Parameters**: In CV, Stage 4 parameters ($w_h, k_h$) are fit strictly on fold-training origins.
3. **Causal Night Rule**: Night predictions set to 0.0 W/m² strictly using `solar_elevation <= 0` or `clearsky_ghi == 0`.
4. **Primary Metric**: Daytime MAE (baseline = 43.4508 W/m²).
5. **Statistical Verification**: 10,000-sample origin-level paired bootstrap for 95% confidence interval on $\Delta \text{MAE}$.

## Results Summary
- **Baseline Stage 4 ODD Daytime MAE**: 43.4508 W/m²
- **Winning CV Candidate**: Arch A: GBDT Residual Corrector
- **ODD Test Set Performance**: 39.0848 W/m² (Delta = -4.3660 W/m²)
- **95% Bootstrap CI for Delta MAE**: [-5.5568, -3.0981] W/m²

## Decision
**A — Non-Linear Architecture Strictly Displaces Stage 4 Champion**
