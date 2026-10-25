# CRITICAL-LOAD DATA MATRIX

## Data Classification Matrix

| Category | Data Item | Value | Units | Time Basis | Source | Classification | Station-Specific? | Reliability | Usable Now? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Essential Heating** | Nuolja Station Space Heating Power | `NOT_ESTABLISHED` | W | Time-varying | None | `G = UNVERIFIED_CLAIM` | No | Unverified | No |
| **Essential Heating** | Abisko Main Station Heat Pump Upgrade | Unquantified | kW | Seasonal | SITES / Caverion Public Disclosure | `C = AUTHORITATIVE_DOCUMENTED_INSTALLED_EQUIPMENT` | Abisko Main Station (Not Nuolja AWS) | High | No |
| **Water Treatment** | Potable Water Filtration & Pump Power | `NOT_ESTABLISHED` | W | Intermittent | None | `G = UNVERIFIED_CLAIM` | No | Unverified | No |
| **Emergency Comms** | Telemetry Logger & Radio Link Power | `NOT_ESTABLISHED` | W | Continuous | SITES Abisko AWS Metadata | `D = SCIENTIFIC_SECONDARY_SOURCE_SPECIFIC_TO_NUOLJA` | Nuolja AWS (Qualitative only) | Medium | No |
| **Circuit Mapping** | Breaker Panel & Load Channel Schedule | `NOT_ESTABLISHED` | N/A | Static | None | `G = UNVERIFIED_CLAIM` | No | Unverified | No |
| **Total Demand** | Station Electrical Demand Trajectory | 15,000 to 45,000 | W | Hourly (8,784h) | `POLARIS_HYBRID_FIXTURE_H1_0` `fixture.csv` | `F = SYNTHETIC_PROJECT_TEST_DATA` | Synthetic Engineering Fixture | High (for synthetic testing) | Yes (for synthetic dry-runs only) |
| **Critical Load Default** | Code Prototype Load Floor | 30,000 | W | Constant | `system/config/loads.yaml` | `F = SYNTHETIC_PROJECT_TEST_DATA` | Code Default (`PROTOTYPE_ASSUMPTION`) | High (for test code wiring) | No (Not real station policy) |
| **Dec-004-D1 Example** | Illustrative Conceptual Breakdown | 7,000 (4kW Heat, 2kW Water, 1kW Comms) | W | Static | `DEC-004-D1` Governance Brief | `F = SYNTHETIC_PROJECT_TEST_DATA` | Synthetic Illustrative Example | High (for concept illustration) | No (Explicitly rejected as station policy) |
