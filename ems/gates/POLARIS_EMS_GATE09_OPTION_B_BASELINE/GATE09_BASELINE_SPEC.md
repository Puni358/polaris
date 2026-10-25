# POLARIS EMS GATE-09 — OPTION B BASELINE SPECIFICATION

## 1. Executive Summary & Runtime Identity
This artifact specifies the controlled baseline configuration, software dependencies, physical microgrid asset parameters, and optimization solver identity for Option B normal operation (`GAP19HighsNativeOptimizer`).

## 2. Solver & Runtime Identity
- **Optimizer Implementation**: `GAP19HighsNativeOptimizer` (`system/optimization/implementations/gap19_highs_native.py`)
- **Protected Option B Source SHA256**: `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737`
- **Native MILP Runtime**: Scipy HiGHS C++ Native Engine (`highs_native`)
- **Input Fixture Identity**: Synthetic H1.0 Baseline Scenario (`demo_scenario.json`)
- **Optimization Horizon**: 24 hourly steps ($H=24$)

## 3. Physical Asset & Constraint Baseline Parameters

### 3.1 Battery Asset Parameters
- Capacity: $200,000 \text{ Wh}$ ($200 \text{ kWh}$)
- Operating SOC Range: $[20.0\%, 95.0\%]$ ($40,000 \text{ Wh} \le E_{\text{bat}} \le 190,000 \text{ Wh}$)
- Initial SOC: $50.0\%$ ($100,000 \text{ Wh}$)
- Charge Efficiency ($\eta_{\text{chg}}$): $0.92$ ($92\%$)
- Discharge Efficiency ($\eta_{\text{dis}}$): $0.92$ ($92\%$)
- Max Charge Power: $50,000 \text{ W}$ ($50 \text{ kW}$)
- Max Discharge Power: $50,000 \text{ W}$ ($50 \text{ kW}$)

### 3.2 Diesel Generator Parameters
- Minimum Power Output: $10,000 \text{ W}$ ($10 \text{ kW}$)
- Maximum Power Output: $100,000 \text{ W}$ ($100 \text{ kW}$)
- Base Fuel Consumption: $5.0 \text{ L/h}$
- Marginal Fuel Consumption: $0.00025 \text{ L/Wh}$ ($0.25 \text{ L/kWh}$)
- Initial Fuel Level: $100.0 \text{ L}$ (synthetic)

### 3.3 Critical Load Policy
- Critical Load Ratio: $1.0$ ($100\%$ total load treated as protected critical load per sealed Gate-02 policy).
- Hard Critical Load Penalty: Infeasible penalty $1 \times 10^9$ applied to any unmet load $P_{\text{unmet\_crit}}$. Zero relaxation permitted.
