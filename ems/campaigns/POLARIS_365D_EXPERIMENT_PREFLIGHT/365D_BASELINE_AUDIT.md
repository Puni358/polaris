# 365D BASELINE CONTROL STRATEGY AUDIT

## Primary Baseline Definition
- **Baseline Classification**: `SIMPLE_DIESEL_ONLY_REFERENCE`
- **Purpose**: Answers the core empirical comparison question:
  > "How much diesel does the simple diesel-only reference consume to keep the station/load state alive over the same 2024 trajectory versus how much diesel does the complete POLARIS system consume?"
- **Operational Logic**:
  1. Supplies total station/load demand directly from the diesel generator.
  2. No predictive solar forecasting, wind forecasting, demand forecasting, Stage 8.1 ML models, Branch01 code, or POLARIS optimizer.
  3. No MPC optimization or predictive renewable dispatch.
  4. Evaluated over the identical 8,784 hourly timestamps (2024-01-01T00:00:00Z to 2024-12-31T23:00:00Z) under identical physical fuel accounting formulas (`Fuel = ON_hours * 5.0 + Gen_kWh * 0.00025`).

## Historical Control vs. New Primary Baseline Audit
- **Previous 173-Trajectory Historical Control**: `Clear-Sky Baseline Forecast + MILP MPC Optimizer` (consumed 22,486.702 L in 4,152-hour Stage 8.1 evaluation).
- **Historical Result Classification**: `HISTORICAL_50_55_RESULT = HISTORICAL / INVALID_FOR_NEW_CAUSAL_CLAIM` (due to R2 zero-padding horizon truncation defect in historical runner).
- **Provenance Relationship**: `PREVIOUS_CONTROL != NEW_PRIMARY_BASELINE`. The historical control was a Clear-Sky Baseline MILP MPC solver, whereas the new primary baseline is a simple diesel-only reference.
- **5.5% Specific Standalone Result**: `PREVIOUS_BASELINE_RECOVERY = NOT_ESTABLISHED` (historical Stage 8.1 aggregate evaluation was +50.55%).

