# POLARIS Operational Local System Workspace

This directory contains the operational code for the POLARIS local-first, offline-capable Energy Management System (EMS).

## Key Principles
- **Offline First:** 100% self-contained local runtime. Zero network dependency.
- **Decoupled Architecture:** Forecasting Engine (`ForecastBundle`) $\to$ Energy Optimizer (`DispatchPlan`) $\to$ Digital Twin Simulator.
- **Config Driven:** Microgrid physical properties managed via YAML configuration (`config/`).

See `POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md` in the project root for full technical specification.
