# POLARIS EMS — CAMPAIGN PROVENANCE MATRIX

## 1. Executive Statement
This document records the official component provenance matrix for the Final Integrated Campaign execution, explicitly separating empirically observed data from synthetic engineering inputs.

## 2. Final Campaign Provenance Matrix

| COMPONENT | SOURCE / ORIGIN | CLASSIFICATION | ESTABLISHED? | ALLOWED CLAIM | FORBIDDEN CLAIM |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Nuolja Solar / SW_IN** | Nuolja SITES Station Dataset | Real Station Observation | **YES** | Empirically observed solar irradiance. | Claiming zero-error solar sensor telemetry. |
| **Wind Generation** | Abisko / SMHI Regional Proxy | Regional Proxy Data | **NO** | Regional Arctic wind proxy input. | Claiming direct Nuolja wind generator telemetry. |
| **Station Demand** | Synthetic $35 \text{ kW}$ Load Profile | Synthetic Engineering Input | **NO** | Synthetic test load profile. | Claiming measured real Nuolja station electrical load. |
| **Wind Turbine** | Generic $50 \text{ kW}$ Power Curve | Reference Asset Model | **NO** | Generic reference turbine model. | Claiming physical Nuolja station turbine hardware. |
| **Battery / Diesel** | Reference $200 \text{ kWh} / 100 \text{ kW}$ Genset | Reference Hardware Model | **NO** | Reference hardware parameters. | Claiming physical Nuolja station hardware installation. |
| **Solar Forecasting** | Stage 8.1 / Branch 01 Solar Models | Qualified Forecast Artifact | **YES** | Validated solar irradiance forecast models. | Claiming validated station wind or demand forecast models. |
| **Campaign Status** | 48-Cycle Receding Horizon MPC | Integrated Fixture Run | **YES** | Synthetic integrated EMS campaign execution. | Claiming real-station validation or production readiness. |
