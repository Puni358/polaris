# 365D PRIMARY EXPERIMENTAL COMPARISON MATRIX

## Primary 2-Cell Experimental Comparison
- **Purpose**: Direct evaluation comparing simple diesel-only load support reference against complete POLARIS closed-loop system over full 2024 trajectory.
- **Scope**: Identical 8,784 hourly cycles (2024-01-01T00:00:00Z through 2024-12-31T23:00:00Z), identical initial state conditions, identical physical fuel formulas, and identical Digital Twin evaluation boundary.

## Primary Experimental Cells

| Cell ID | Configuration Name | Forecasting Stack | Control / Dispatch Strategy | Experimental Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Cell A** | Simple Diesel-Only Baseline | NONE (No predictive forecasts) | Simple Diesel Supply (Direct demand coverage) | Absolute diesel consumption reference |
| **Cell B** | POLARIS Closed-Loop System | Authorized POLARIS Forecast Stack | Option B Native HiGHS MILP / Router | Complete POLARIS EMS evaluation |

## Metric Reporting Register
- Total Diesel Consumed [L]
- Absolute Difference [L] & Percentage Difference (%)
- Generator Runtime [hours] & Diesel Starts [count]
- Electrical Generation [kWh]
- Solar & Wind Generation Used [kWh]
- Battery Charge / Discharge Throughput [kWh] & SOC Min/Max [%]
- Renewable Curtailment [kWh]
- Unmet Load [Wh]
- Infeasibility & Emergency Event Counts

