# POLARIS EMS GATE-12 — SYNTHETIC INPUT & HARDWARE AUDIT

## 1. Audit Overview
This document audits all synthetic, proxy, and generic reference inputs used in the integrated EMS synthetic fixture (`demo_scenario.json` and system configuration files).

## 2. Detailed Synthetic Input Classifications

### 2.1 Synthetic Electrical Load Demand
- **Identification**: `SYNTHETIC_DEMAND = IDENTIFIED`
- **Details**: Daily $35 \text{ kW}$ peak demand curve used in `demo_scenario.json` is a synthetic engineering profile for testing receding-horizon MPC control.

### 2.2 Generic Wind Turbine Reference Asset
- **Identification**: `GENERIC_WIND_ASSET = IDENTIFIED`
- **Details**: Wind power generation curve ($30 \text{ kW} - 35 \text{ kW}$) is generated via a reference power curve applied to regional proxy wind speed.

### 2.3 Synthetic Engineering Asset Inputs
- **Identification**: `SYNTHETIC_ENGINEERING_INPUTS = IDENTIFIED`
- **Details**:
  - Battery capacity ($200 \text{ kWh}$), power bounds ($\pm 50 \text{ kW}$), efficiencies ($92\%$) are standard reference values.
  - Diesel generator bounds ($10 \text{ kW} - 100 \text{ kW}$) and fuel curves ($5.0 \text{ L/h}$ base, $0.25 \text{ L/kWh}$ marginal) are synthetic engineering assumptions.
  - Solar PV conversion coefficient ($0.20 \text{ W/(W/m}^2\text{)}$) is a synthetic engineering transfer function.
