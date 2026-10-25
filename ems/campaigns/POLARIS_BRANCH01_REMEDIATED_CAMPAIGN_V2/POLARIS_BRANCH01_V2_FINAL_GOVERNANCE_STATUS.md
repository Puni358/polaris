# POLARIS — Branch 01 Remediated EMS Campaign V2 Final Governance Report

**Campaign ID**: `POLARIS_BRANCH01_REMEDIATED_CAMPAIGN_V2`  
**Governance Status**: **COMPLETE & SCIENTIFICALLY VALIDATED**  
**Timestamp**: 2026-09-21 12:26:49 UTC  

---

### Key Verification Gates Summary

- **Completed Trajectories**: 173 / 173 (4,152 H1 execution steps)
- **Branch01 Inferences**: 4,152 / 4,152 (24 receding-horizon inferences per trajectory)
- **Non-Solar Forecast Inheritance**: 100% Exact Demand & Wind Match (`control_demand_hash == treatment_demand_hash`, `control_wind_hash == treatment_wind_hash`)
- **Energy Balance Accounting**: `ENERGY_ACCOUNTING_STATUS = PASS` (0 unexplained energy residual)
- **Battery State Accounting**: `BATTERY_ACCOUNTING_STATUS = PASS` (0 SOC boundary or physical energy violations)
- **Future-Truth Firewall**: `FUTURE_TRUTH_FIREWALL_STATUS = PASS` (0 future-truth leakage events)
- **Zero-Placeholder Firewall**: `PASS` (0 unauthorized default fallbacks)

---

### Paired Campaign Results (173 Trajectories)

| Metric | Control (Stage 8.1 GHI) | Treatment (Branch01 HGB) | Difference (Treatment - Control) |
|---|---|---|---|
| **Diesel Generation (kWh)** | 62,126.805 | 95,667.521 | +33,540.716 |
| **Fuel Consumption (L)** | 22,486.701 | 33,836.880 | +11,350.179 |
| **Load Served (kWh)** | 75,480.485 | 106,024.238 | +30,543.753 |
| **Unmet Load (kWh)** | 40,352.215 | 9,808.462 | -30,543.753 |
| **Solar Power Used (kWh)** | 17,130.029 | 17,125.575 | -4.454 |
| **Wind Power Used (kWh)** | 12,358.639 | 13,142.536 | +783.897 |
| **Renewable Curtailment (kWh)** | 9,647.175 | 6,835.509 | -2,811.665 |

---

### Paired Distribution Metrics

- **Mean Trajectory Fuel Difference**: `+65.6080 L`
- **Median Trajectory Fuel Difference**: `+66.5836 L`
- **Trajectories with Fuel Savings (Treatment < Control)**: `13`
- **Trajectories with Fuel Increase (Treatment > Control)**: `160`
- **Tied Trajectories (Treatment == Control)**: `0`

---

### Mandatory Governance Classification Block

```
CAMPAIGN_STATUS = COMPLETE
MODEL_IDENTITY_STATUS = PASS
TRAJECTORY_IDENTITY_STATUS = PASS
CONTROL_FORECAST_IDENTITY_STATUS = PASS
DEMAND_INHERITANCE_STATUS = PASS
WIND_INHERITANCE_STATUS = PASS
SOLAR_ONLY_INTERVENTION_STATUS = PASS
CAUSALITY_STATUS = PASS
FUTURE_TRUTH_FIREWALL_STATUS = PASS
FORECASTBUNDLE_STATUS = PASS
OPTIMIZER_INPUT_TRACEABILITY_STATUS = PASS
ENERGY_ACCOUNTING_STATUS = PASS
BATTERY_ACCOUNTING_STATUS = PASS
PROVENANCE_STATUS = PASS
CHECKPOINT_INTEGRITY_STATUS = PASS
FROZEN_ARTIFACT_IMMUTABILITY_STATUS = PASS
ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET
NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED
```
