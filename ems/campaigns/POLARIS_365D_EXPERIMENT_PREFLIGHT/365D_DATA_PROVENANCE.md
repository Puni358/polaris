# 365D DATA PROVENANCE & REAL-STATION CLAIM FIREWALL

## Data Provenance Classification Matrix

| Input Field | Provenance Class | Source & Dataset | Location / Asset Details | Hash / Signature |
| :--- | :--- | :--- | :--- | :--- |
| **Solar SW_IN** | `REAL_MEASURED` | SITES Nuolja Middle Station AWS | 68.36 N, 18.74 E (Mount Nuolja) | `0a2b9d2cbf3fea14a75d2e448f9650534f2ff540601d8c89df69e3b9334fa1f8` |
| **Solar PV Power** | `DERIVED_ENGINEERING_QUANTITY` | PV array conversion formula | $P_{PV} = \min(\text{SW\_IN} \times 300 \times 0.20 \times 0.85, 60\text{kW})$ | Derived deterministically from SW_IN |
| **Wind Speed Proxy** | `CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY` | SMHI Station 188790 Abisko Aut | 10m height, 4.1 km from Nuolja | `b7f694aa957af57103176d9a2cb77bd506e2c0f56402eab5cc584ebd02d379fd` |
| **Wind Power** | `SYNTHETIC_ENGINEERING_SCENARIO` | Generic polar reference turbine curve | 60 kW rated capacity | Calculated from wind speed proxy |
| **Station Demand** | `SYNTHETIC` | H1.0 Synthetic station load generator | 15.0 kW to 45.0 kW diurnal curve | Deterministic synthetic formula |
| **Battery Storage** | `GENERIC_REFERENCE` | 200 kWh / 50 kW Li-ion spec | 20% min SOC, 95% max SOC, 92% efficiency | Configured in `battery.yaml` |
| **Diesel Generator** | `GENERIC_REFERENCE` | 100 kW genset spec | 10 kW min power, 5.0 L/h base, 0.25 L/kWh | Configured in `diesel.yaml` |

## Canonical Fixture Verification
- **Canonical Scenario File**: `system/data/scenarios/h10_scenario_temp.json`
- **Canonical Fixture Source**: `POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv` (SHA256: `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023`)
- **Provenance Manifest File**: `POLARIS_HYBRID_FIXTURE_H1_0/provenance.json` (SHA256: `ed505b118ee774a628eeac1c8a437b8754f91c71fd2e22764b96e192385a0498`)
