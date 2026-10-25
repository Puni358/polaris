# POLARIS 365D EXPERIMENT — SEALED HUMAN DECISIONS REGISTER

## Authoritative Human Project Owner Decisions

### Decision 1: Time Domain Definition
- **Time Horizon**: Full-calendar-year 2024 / 8,784 hourly cycles (`2024-01-01T00:00:00Z` through `2024-12-31T23:00:00Z`).
- **Terminology Standard**: Governed artifacts must strictly use `"Full-calendar-year 2024 / 8,784 hourly cycles"` to reflect the leap year ($366 \text{ days} \times 24 \text{ hours}$). Do not refer to this period as "365 days" without qualification.
- **Timezone Standard**: UTC timestamps (`Z` suffix) used throughout.

### Decision 2: Fuel Experiment Scenarios
- **Scenario Fuel-1 (Primary)**: Infinite-reservoir / Cumulative-accounting experiment (`SCENARIO_FUEL_1_INFINITE_CUMULATIVE`). Tracks total cumulative Liters without artificial tank depletion clipping or logistics interruptions. Isolates controller fuel performance from arbitrary tank/resupply assumptions.
- **Scenario Fuel-2 (Secondary Sensitivity)**: Synthetic finite-resupply experiment (`SCENARIO_FUEL_2_SYNTHETIC_FINITE`). Experimental sensitivity scenario with frozen synthetic tank size and refill policy. Parameters must be frozen before execution; currently `GOVERNANCE/PARAMETER BLOCKED`. Must NOT be claimed as real Nuolja station logistics.
- **Scenario Fuel-3 (Physical Station Logistics)**: `PHYSICAL_STATION_RESUPPLY_MODEL = NOT_ESTABLISHED`. Real Nuolja station tank size, initial inventory, refill thresholds, and resupply logistics are NOT ESTABLISHED. Preserved for future work.

### Decision 3: Primary 2-Cell Experimental Comparison Matrix
- **Authoritative Primary Comparison**:
  - **Cell A (Simple Diesel-Only Baseline)**: Simple diesel-only reference supplying station load directly without predictive forecasting or optimization.
  - **Cell B (POLARIS Closed-Loop System)**: Complete authorized POLARIS closed-loop system using Option B HiGHS Native solver.
- **Experimental Parity Rules**:
  - Identical 8,784 hourly cycles (full calendar year 2024).
  - Identical initial conditions, physical asset models, fuel accounting formulas, and Digital Twin evaluation boundary.
- **Forecasting Provenance Rule**: Stage 8.1 fitted model contains the historical R2 horizon-truncation zero-padding defect and is NOT authorized for new causal claims.


### Decision 4: Gate-02 Option C Compliance
- **Policy Enforcement**: Critical load is compulsory / never relaxed. Governed constraint relaxation applies to authorized noncritical/flexible loads with operator notification.
- **Prohibition**: MILP infeasibility does NOT trigger emergency mode and must **NEVER** automatically invoke Option D fallback. Automatic Digital Twin advancement on unresolved infeasibility is strictly prohibited.
