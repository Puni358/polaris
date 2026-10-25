# POLARIS — SOLAR FORECAST BRANCH 01
## POST-CAMPAIGN ENERGY ACCOUNTING FORENSIC AUDIT

**Governance Gate**: Post-Campaign Energy Forensic Audit  
**Date**: 2026-09-21  
**Mode**: **READ-ONLY FORENSIC RECONCILIATION**  
**Energy Accounting Status**: **FAIL**  
**Zero Treatment Diesel Result**: **NOT_VERIFIED** (Artifact of Unfilled Demand Forecast)  

---

### 1. FORENSIC ANOMALY DISCOVERY & MECHANISTIC ROOT CAUSE

An independent read-only forensic audit of raw telemetry and system components discovered the exact mechanistic root cause for the reported zero-diesel treatment result:

1. **Unfilled Demand Forecast in Branch01 Engine**:
   - When `Branch01ForecastEngine.predict()` generated the `ForecastBundle` for treatment, it populated solar irradiance predictions but left the `demand` and `wind_generation` forecast arrays populated with **zeros** ($0.0\text{ W}$).
2. **Optimizer Scheduling Consequences**:
   - Because `LocalMILPEnergyOptimizer` received a horizon forecast demand of $0.0\text{ W}$, the optimizer determined that zero power generation was required to serve the forecast load.
   - Consequently, the MILP optimizer scheduled **$0.0\text{ W}$ diesel power**, **$0.0\text{ W}$ battery discharge**, and **$0.0\text{ W}$ wind power** for all 4,152 treatment steps.
3. **Simulator & Accounting Discrepancy**:
   - The Digital Twin simulator executed this zero-power dispatch plan. Because diesel power was dispatched at $0.0\text{ W}$, the simulator recorded $0.0\text{ kWh}$ diesel generation and $0.0\text{ L}$ fuel consumption.
   - However, in reality, the hidden actual load was $21.6\text{ kW}$ to $45.0\text{ kW}$ per hour ($864.0\text{ kWh}$ per 24-hour trajectory).
   - In live operation, this zero-power dispatch would have caused **$100\%$ microgrid blackout / unmet load**.
   - In campaign telemetry aggregation, `load_served` was calculated as `synthetic_load_W - plan.unmet_load[0]`. Because `plan.unmet_load[0]` in the MILP plan was $0.0$ (due to zero forecast demand), the reporting script mistakenly credited Treatment with serving $149,472.000\text{ kWh}$ of load!

---

### 2. RAW TELEMETRY & ENERGY RECONCILIATION SUMMARY

| Metric | Control (Stage 8.1) | Treatment (Branch01 HGB) | Accounting Reconciliation |
|---|---|---|---|
| **Total Load Served** | $149,472.000\text{ kWh}$ | $149,472.000\text{ kWh}$ | Fixed Fixture Load ($173 \times 864\text{ kWh}$) |
| **Solar Generation Used** | $52,065.063\text{ kWh}$ | $3,143.495\text{ kWh}$ | Measured |
| **Wind Generation Used** | $25,798.684\text{ kWh}$ | $0.000\text{ kWh}$ | Omitted due to 0 forecast |
| **Diesel Generation** | $52,802.079\text{ kWh}$ | $0.000\text{ kWh}$ | Dispatched 0 due to 0 forecast demand |
| **Battery Discharge** | $20,077.375\text{ kWh}$ | $0.000\text{ kWh}$ | Dispatched 0 |
| **Battery Charge** | $22,888.657\text{ kWh}$ | $3,143.495\text{ kWh}$ | Solar surplus charged |
| **Renewable Curtailment** | $8,941.083\text{ kWh}$ | $15,882.841\text{ kWh}$ | Unused solar |
| **Total Energy Input** | $150,743.201\text{ kWh}$ | $3,143.495\text{ kWh}$ | **Input Deficit: $-146,328.505\text{ kWh}$** |
| **Total Energy Output** | $150,743.201\text{ kWh}$ | $149,472.000\text{ kWh}$ | Load + Sinks |
| **Unexplained Energy Residual** | **$0.000\text{ kWh}$ (PASS)** | **$-146,328.505\text{ kWh}$ (FAIL)** | **UNACCOUNTED LOAD** |

---

### 3. OUTLIER TRAJECTORY SAMPLES

Below are 5 sample trajectories illustrating the $864.0\text{ kWh}$ unexplained energy deficit per trajectory in Treatment:

| Trajectory ID | Start Timestamp | Load Served (kWh) | Treatment Diesel (kWh) | Treatment Solar Used (kWh) | Treatment Battery Discharge (kWh) | Unexplained Energy Deficit (kWh) |
|---|---|---|---|---|---|---|
| `TRAJ_20240121` | `2024-01-21T00:00:00Z` | `864.000` | `0.000` | `3.884` | `0.000` | **`860.116 kWh`** |
| `TRAJ_20240123` | `2024-01-23T00:00:00Z` | `864.000` | `0.000` | `4.210` | `0.000` | **`859.790 kWh`** |
| `TRAJ_20240125` | `2024-01-25T00:00:00Z` | `864.000` | `0.000` | `4.891` | `0.000` | **`859.109 kWh`** |
| `TRAJ_20240127` | `2024-01-27T00:00:00Z` | `864.000` | `0.000` | `5.120` | `0.000` | **`858.880 kWh`** |
| `TRAJ_20240129` | `2024-01-29T00:00:00Z` | `864.000` | `0.000` | `5.850` | `0.000` | **`858.150 kWh`** |

---

### 4. MANDATORY FINAL AUDIT CLASSIFICATION BLOCK

```
ENERGY_ACCOUNTING =
FAIL

BATTERY_ACCOUNTING =
FAIL

UNIT_CONVERSION =
PASS

HIDDEN_ENERGY_SOURCE =
FOUND

AGGREGATE_RECONCILIATION =
FAIL

ZERO_TREATMENT_DIESEL_RESULT =
NOT_VERIFIED

INITIAL_STATE_CONSISTENCY =
PASS

DISCREPANCY_REASON =
UNFILLED_DEMAND_FORECAST_IN_BRANCH01_ENGINE

NEXT_GOVERNED_STEP =
BRANCH01_FORECASTBUNDLE_CONTRACT_REMEDIATION
```
