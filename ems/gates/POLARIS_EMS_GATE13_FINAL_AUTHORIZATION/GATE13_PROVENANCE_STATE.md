# POLARIS EMS GATE-13 — PROVENANCE STATE & TRUTH FIREWALL AUDIT

## 1. Data & Asset Provenance State

| Asset / Dataset | Provenance Source | Authoritative Classification | Allowed Claim |
| :--- | :--- | :---: | :--- |
| **Nuolja Solar / SW_IN** | Nuolja SITES Station Observation | Real Station Data | Empirically observed solar irradiance. |
| **Wind Telemetry** | Abisko / SMHI Regional Proxy | Regional Proxy Data | Regional Arctic wind proxy input. |
| **Station Demand** | Synthetic $35 \text{ kW}$ Peak Load Profile | Synthetic Engineering Input | Synthetic test load profile. |
| **Wind Turbine** | Generic $50 \text{ kW}$ Power Curve | Reference Asset Model | Generic reference turbine model. |
| **Battery / Diesel Assets** | Reference $200 \text{ kWh} / 100 \text{ kW}$ Genset | Reference Hardware Model | Standard reference hardware parameters. |
| **Forecasting Artifacts** | Stage 8.1 / Branch 01 Solar Models | Qualified Forecast Artifact | Validated solar irradiance forecast models. |

## 2. Truth Firewall Verification
- **Optimization Controllers** (`Option B`, `Option D`, `ECD`, `Router`): Receive forecast bundles and current station state only. They NEVER receive future actual ground truth environmental data.
- **Digital Twin Simulator**: Queries future ground truth actuals solely to simulate physical microgrid state evolution following the committed $k=0$ dispatch action.
- Status: **VERIFIED INTACT**
