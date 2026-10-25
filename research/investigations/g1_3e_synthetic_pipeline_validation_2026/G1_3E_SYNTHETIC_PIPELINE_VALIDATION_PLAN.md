# G1.3-E POLARIS Synthetic End-to-End Pipeline Validation Plan

## 1. Executive Summary & Objective

This document authorizes and establishes the plan for a dedicated synthetic validation track of the existing POLARIS end-to-end pipeline. Following the formal freezing of the EVD-02 acquisition attempt (`EVD02_STATUS: FROZEN_BLOCKER`), this validation track assesses the operational readiness and behavior of the existing forecasting, optimization, dispatch, and reporting components using controlled synthetic scenario inputs.

```text
Synthetic Inputs
    ↓
Weather / Renewable Generation
    ↓
Load Forecast
    ↓
Renewable Forecast
    ↓
Optimization / Dispatch (MILP)
    ↓
Battery / Renewable / Diesel Decisions
    ↓
Diesel Generation
    ↓
Energy / Dispatch Report
```

## 2. Epistemic & Governance Boundary Firewall

> [!IMPORTANT]
> **Strict Governance Firewall**: Synthetic scenario execution is strictly classified as `PIPELINE_VALIDATION` and `SCENARIO / STRESS TEST`. It does **NOT** constitute empirical telemetry evidence and cannot be used to establish G1.3-E freshness rules, Nuolja generator facts, or production safety thresholds.

```yaml
G1_3E_POLICY: LOCKED
UNIVERSAL_FRESHNESS_THRESHOLD: NONE
RESOURCE_SPECIFIC_FRESHNESS_RULES: 0/8
NUOLJA_SPECIFIC_FRESHNESS_RULES: 0
EVIDENCE_BOUNDARY: C
PRODUCTION_IMPLEMENTATION: BLOCKED
GOVERNANCE_PROMOTION: NONE
EMPIRICAL_EXPERIMENTS_EXECUTED: 0
EVD02_STATUS: FROZEN_BLOCKER
SYNTHETIC_DATA_STATUS: NON_EMPIRICAL / NON_AUTHORITATIVE
```

## 3. Scenario Ladder

The validation plan defines four progressive synthetic scenarios:

### Scenario S0 — Baseline / Normal
- **Duration**: 48 hours (48 timesteps @ 1h resolution)
- **Load Profile**: Nominal steady 35,000 W (35 kW) demand profile
- **Renewable Profile**: Nominal solar peak (494 W/m²) & steady wind generation (30,000 W)
- **Telemetry State**: Fresh, contiguous, valid telemetry
- **Purpose**: Establish end-to-end pipeline completion under nominal operating conditions.

### Scenario S1 — Renewable Degradation
- **Duration**: 48 hours
- **Load Profile**: Elevated demand (40,000 W)
- **Renewable Profile**: 80% reduction in solar irradiance (peak 98.8 W/m²), 70% reduction in wind (9,000 W)
- **Telemetry State**: Fresh, contiguous
- **Purpose**: Verify forecasting and optimization response under worsening renewable resource availability.

### Scenario S2 — Telemetry Degradation
- **Duration**: 48 hours
- **Load Profile**: Baseline load with synthetic telemetry holds & delayed sample intervals
- **Renewable Profile**: Baseline renewable inputs with sample gaps / stale holds
- **Telemetry State**: Synthetic telemetry holds (4-hour frozen state propagation)
- **Purpose**: Observe pipeline robustness and forecasting behavior when inputs suffer telemetry quality degradation.

### Scenario S3 — Combined Severe Stress
- **Duration**: 48 hours
- **Load Profile**: Severe high load (45,000 W)
- **Renewable Profile**: Complete solar outage (0 W/m²), 90% wind drop (3,000 W)
- **Telemetry State**: Stale telemetry holds combined with severe resource deficits
- **Purpose**: Characterize dispatch behavior, battery SOC depletion, and diesel generation dispatch under compound extreme stress.

## 4. Parameter Classification

All parameters utilized within this synthetic validation plan are explicitly classified:
- `SYNTHETIC_SCENARIO_PARAMETER`: Solar irradiance scaling, wind availability factors, demand scaling, synthetic telemetry hold durations.
- `LOCKED_SYNTHETIC_ENGINEERING_ASSUMPTION`: Battery capacity (100 kWh), min/max SOC (20%/90%), diesel min load (30%), critical demand ratio.

None of these synthetic scenario parameters represent `SOURCE_DERIVED`, `EMPIRICAL`, or `SAFETY_REQUIREMENT` data.

## 5. Pipeline Component Scope

The validation targets the current authoritative POLARIS components in `system/`:
- **Data Provider**: `LocalDataProvider` (`system/data/provider.py`)
- **Forecasting Engine**: `ForecastEngine` (`system/forecasting/`)
- **Optimization Router**: `EMSControlRouter` / `EnergyOptimizer` (`system/optimization/implementations/milp.py`)
- **Simulation**: `DigitalTwinSimulator` (`system/simulation/`)
- **Reporting & Evaluation**: `EvaluationEngine` (`system/evaluation/`)
