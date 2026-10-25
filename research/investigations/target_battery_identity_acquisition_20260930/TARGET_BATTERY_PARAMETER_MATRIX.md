# Target Battery Parameter Matrix

```yaml
PHASE_ID: target_battery_identity_acquisition_20260930
TARGET_BATTERY_IDENTITY: NOT_ESTABLISHED
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Parameter Evidence Classification Matrix

| Parameter | Value | Unit | Source | Evidence Tier | Target-Specific | Verified | Classification |
| :--- | ---: | :---: | :--- | :---: | :---: | :---: | :--- |
| **Manufacturer** | — | — | None | NONE | NO | NO | **UNKNOWN** |
| **Model** | — | — | None | NONE | NO | NO | **UNKNOWN** |
| **Chemistry** | — | — | None | NONE | NO | NO | **UNKNOWN** |
| **Cell/Module Config** | — | — | None | NONE | NO | NO | **UNKNOWN** |
| **Nominal Voltage** | — | V | None | NONE | NO | NO | **UNKNOWN** |
| **Nominal Energy** | 200.0 | kWh | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **Usable Energy** | 150.0 | kWh | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **Max Charge Power** | 50.0 | kW | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **Max Discharge Power**| 50.0 | kW | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **C-rate** | 0.25 | C | Derived (50 kW / 200 kWh) | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **SOC Limits** | 20–95% | pct | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` | Synthetic Proxy | NO | NO | **SYNTHETIC** |
| **Operating Temp** | — | °C | None | NONE | NO | NO | **UNKNOWN** |
| **Charge Efficiency** | 0.92 | fraction| `milp.py` default config | Synthetic Assumption | NO | NO | **SYNTHETIC** |
| **Discharge Efficiency**| 0.92 | fraction| `milp.py` default config | Synthetic Assumption | NO | NO | **SYNTHETIC** |
| **Round-Trip Eff** | 0.8464 | fraction| `milp.py` derived (0.92 * 0.92) | Synthetic Assumption | NO | NO | **SYNTHETIC** |
| **Cycle Life** | — | EFC | None | NONE | NO | NO | **UNKNOWN** |
| **End-of-Life Criteria**| — | % cap | None | NONE | NO | NO | **UNKNOWN** |
| **Calendar Life** | — | yrs | None | NONE | NO | NO | **UNKNOWN** |
| **BMS Telemetry** | ABSENT | — | Workspace / Site Audit | Tier A (Target) | YES | YES | **VERIFIED_ABSENT** |

---

## 2. Classification Summary

- **Verified (1 parameter)**: BMS Telemetry is verified ABSENT in the workspace.
- **Synthetic (8 parameters)**: 200 kWh capacity, 50 kW power, SOC limits, and efficiency parameters are synthetic engineering assumptions.
- **Unknown (10 parameters)**: Manufacturer, model, chemistry, configuration, voltage, temperature, cycle life, calendar life, and EOL criteria are completely **UNKNOWN**.
