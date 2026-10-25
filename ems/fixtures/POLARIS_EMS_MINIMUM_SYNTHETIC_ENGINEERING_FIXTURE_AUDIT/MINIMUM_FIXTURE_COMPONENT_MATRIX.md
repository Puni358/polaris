# POLARIS EMS — MINIMUM FIXTURE COMPONENT COVERAGE MATRIX

## Executive Summary

This document presents the master component coverage matrix verifying that the proposed minimum synthetic fixture exercises 100% of the POLARIS software architecture.

---

## Master Component Coverage Matrix

| Component | Minimum Required? | Synthetic Inputs | Real Inputs | Architecture Behavior Tested | Claim Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Time Horizon** | `YES` | 24h horizon, 1h step | None | Receding-horizon step iteration | Software cycle execution |
| **Station State** | `YES` | Initial SOC (50%), fuel (100L) | None | State initialization & tracking | Software state update |
| **Critical Loads** | `YES` | Synthetic $P_{\text{critical}}(t)$ vector | None | D1–D6 critical service routing | **Not Nuolja critical load** |
| **Noncritical Loads** | `YES` | Synthetic $P_{\text{noncritical}}(t)$ vector | None | Option D noncritical load shedding | **Not Nuolja station load** |
| **Solar PV** | `YES` | Synthetic irradiance / power | Optional $SW\_IN$ | Solar generation integration | Synthetic solar model |
| **Wind Generation** | `YES` | Synthetic wind power | Optional wind | Wind generation integration | Synthetic wind model |
| **Battery BESS** | `YES` | $200\text{kWh}, \text{SOC}\in[20\%, 95\%]$ | None | SOC tracking & charge/discharge | Synthetic battery dynamics |
| **Diesel Genset** | `YES` | $10\text{kW}$ min, $12.5\text{L/h}$ fuel rate | None | Generator startup/stop & fuel burn | Synthetic generator model |
| **Fuel Inventory** | `YES` | $100\text{L}$ initial, $50\text{L}$ reserve | None | Fuel depletion & reserve floor | Synthetic fuel accounting |
| **ForecastBundle** | `YES` | 24h point forecasts | None | ForecastBundle v1.0.0 ingestion | Synthetic forecast data |
| **ECD Module** | `YES` | $T_{\text{required\_baseline}} = 6\text{h}$ | None | Resource endurance evaluation | Software risk classification |
| **Option D Fallback** | `YES` | Safe-state fallback rules | None | Protected critical load priority | Software policy execution |
| **EnergyOptimizer** | `YES` | HiGHS MILP formulation | None | Dispatch optimization | Software solver convergence |
| **DispatchPlan** | `YES` | Control setpoints | None | Plan schema validation | Software plan execution |
| **Digital Twin** | `YES` | Simulation actuals | None | Ground-truth state transition | Software twin simulation |
| **Evaluation** | `YES` | Energy accounting metrics | None | Performance tracking metrics | **Not Nuolja performance** |

---

## Matrix Audit Conclusion

All 16 architectural components are marked `MINIMUM_REQUIRED = YES`. Every component has a documented role in software architecture demonstration, and every synthetic parameter is bound by an explicit claim boundary.
