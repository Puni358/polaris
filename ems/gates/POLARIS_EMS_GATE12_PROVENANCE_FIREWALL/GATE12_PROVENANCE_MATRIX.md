# POLARIS EMS GATE-12 — COMPONENT PROVENANCE MATRIX

## 1. Provenance Matrix Overview
This document establishes the official component-by-component data and hardware provenance matrix for the POLARIS Energy Management System (EMS) integrated fixture.

## 2. Authoritative Provenance Matrix

| COMPONENT | SOURCE / ORIGIN | CLASSIFICATION | ESTABLISHED? | ALLOWED CLAIM | FORBIDDEN CLAIM |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Nuolja Solar / SW_IN** | Nuolja SITES Research Station Dataset | Real Station Observation | **YES** | Empirically observed / reconstructed solar irradiance at Nuolja. | Claiming zero-error solar sensor telemetry. |
| **Wind Generation Telemetry** | Abisko / SMHI Regional Meteorological Proxy | Regional Proxy Data | **NO** | Regional Arctic wind proxy input for synthetic testing. | Claiming direct Nuolja station wind generator telemetry. |
| **Station Electrical Demand** | Synthetic Engineering Load Profile ($35 \text{ kW}$ peak) | Synthetic Engineering Input | **NO** | Controlled synthetic load profile for EMS validation. | Claiming measured real Nuolja station electrical load. |
| **Wind Turbine Asset Model** | Generic / Reference $50 \text{ kW}$ Power Curve Model | Reference Asset Model | **NO** | Generic reference turbine power curve for simulation. | Claiming a verified physical Nuolja turbine hardware asset. |
| **Solar PV Conversion Model** | Engineering Irradiance-to-Power Mapping ($0.20 \text{ W/(W/m}^2\text{)}$) | Engineering Model | **NO** | Engineering PV conversion model for synthetic fixture. | Claiming empirically validated Nuolja station PV hardware efficiency. |
| **Battery Hardware Asset** | Generic $200 \text{ kWh} / 50 \text{ kW}$ Li-ion Asset Profile | Reference Hardware Model | **NO** | Standard reference battery parameter specification. | Claiming physical Nuolja station battery hardware installation. |
| **Diesel Generator Asset** | Generic $100 \text{ kW} / 5.0 \text{ L/h}$ Genset Profile | Reference Hardware Model | **NO** | Standard reference diesel generator specification. | Claiming real physical Nuolja station diesel generator hardware. |
| **EMS Governance Policy** | Formally Sealed Project Governance Decisions (Gates 01-11) | Project Governance Boundary | **YES** | Authoritative sealed project governance policy. | Claiming station operator names or specific site authorization. |
| **Digital Twin Simulation** | Closed-Loop Physics Simulator (`DigitalTwinSimulator`) | Synthetic Simulation Model | **NO** | Synthetic closed-loop simulation state evolution. | Claiming simulated trajectories represent measured future station truth. |
| **Solar Forecasting Artifacts** | Stage 8.1 / Branch 01 Chronos & Solar Models | Empirical Forecast Artifact | **YES** | Empirically evaluated solar irradiance forecast models. | Claiming validated station wind or electrical demand forecasting models. |
| **Integrated Campaign Status** | Pre-Campaign Gate Verification Framework | Gate Verification Only | **NO** | Gate-12 verification complete. | Claiming the final integrated campaign has been executed. |
