# POLARIS — STAGE8.1 → EMS MECHANISM OBSERVABILITY V2 PROTOCOL
## HARDENED DESIGN-ONLY SPECIFICATION

```
============================================================
PROTOCOL GOVERNANCE STATUS
============================================================
PROTOCOL_ID: STAGE8.1_EMS_MECHANISM_OBSERVABILITY_REPLAY_V2
PROTOCOL_HARDENING_STATUS: A — V2 PROTOCOL HARDENED AND READY FOR FUTURE AUTHORIZATION
PROTOCOL_TYPE: DESIGN_ONLY_FUTURE_OBSERVABILITY_REPLAY_PROTOCOL
EXECUTION_AUTHORIZATION_STATUS: EXECUTION_NOT_AUTHORIZED_DESIGN_ONLY
V2_ENGINEERING_STATUS: LOCKED
V2_IMPLEMENTED: NO
V2_EXECUTED: NO
V1_RERUN: NO
V1_RESULT_CHANGED: NO
EMS_CHANGED: NO
OPTIMIZER_CHANGED: NO
SIMULATOR_CHANGED: NO
MODEL_CHANGED: NO
FUTURE_AUTHORIZATION_GATE: REQUIRED
============================================================
```

> **CRITICAL MANDATE**:
> THIS IS A DESIGN ARTIFACT ONLY.
> NO V2 EXECUTION IS AUTHORIZED.
> NO CODE OR SOURCE MODIFICATION HAS OCCURRED OR IS PERMITTED.

---

### 1. SYSTEM PROVENANCE & COMPONENT IDENTITIES

The cryptographic hashes and authoritative paths of all frozen system components have been established from the repository:

| System Component | Authoritative File Path | SHA256 Hash | Provenance Status |
| :--- | :--- | :--- | :--- |
| **Control Engine** | `system/forecasting/implementations/baseline.py` | `905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993` | **ESTABLISHED** |
| **Stage8.1 Engine** | `system/forecasting/implementations/s81_solar.py` | `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` | **ESTABLISHED** |
| **EMS MILP Optimizer** | `system/optimization/implementations/milp.py` | `274926d2d04a26f9b105d313c83063e14a9a06c15848dbad828dc393edef6bde` | **ESTABLISHED** |
| **Digital Twin Simulator** | `system/simulation/simulator.py` | `7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508` | **ESTABLISHED** |
| **Evaluator Engine** | `system/evaluation/evaluator.py` | `79af472d52aab4b63180aaccac044ee48c9893f257c4f6988ccff7da1cec8729` | **ESTABLISHED** |
| **ForecastBundle Schema** | `system/schemas/forecast_bundle.py` | `899aaa48272fd44691cef4b32939adb931a837c99203db37edfc14a9bb2d2045` | **ESTABLISHED** |
| **StationState Schema** | `system/schemas/station_state.py` | `b6e78e8292bbba407f0af0a56100024cca4831dfb80d138afb1fb38008532d1c` | **ESTABLISHED** |
| **DispatchPlan Schema** | `system/schemas/dispatch_plan.py` | `cbf80578a0b4fa289e26b509eeb4d672124a2dad8a77855a42a50ca267349a17` | **ESTABLISHED** |
| **Replay Runner Script** | `run_polaris_stage8_1_ems_empirical_replay.py` | `c305aa8179015efb892b9517a44fa9aa3abb1899a6584db3039e0798e7e5c4fc` | **ESTABLISHED** |
| **Treatment Artifact** | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` | **ESTABLISHED** |
| **HiGHS MILP Solver** | C++ HiGHS MILP Solver Interface v1.7+ | Pre-compiled Shared Binary | **ESTABLISHED** |

---

### 2. TIMESTEP TELEMETRY SEMANTICS

The telemetry layer is hardened to capture un-collapsed, structured data across 6 conceptual categories at every MPC timestep $k \in \{0 \dots 23\}$:

> **Timestep Telemetry Principle**:
> *"For every paired origin and every MPC timestep $k$, telemetry records the state, forecast inputs, optimizer decisions, physical action, and resulting state transition associated with that timestep."*

#### Six Conceptual Data Categories
- **Category A: FORECAST-HORIZON DATA**: The complete 24-step forecast vector ($\hat{y}_{k \dots k+23}$) provided to the optimizer at step $k$.
- **Category B: H1 DECISION DATA**: The first-horizon forecast value $\hat{y}_{k+1}$ and executed H1 decision at step $k$.
- **Category C: STATE-BEFORE-ACTION**: The `StationState` entering the MPC optimizer at step $k$ ($\text{SOC}_k$, generator state).
- **Category D: ACTION**: The `DispatchPlan` H1 physical action selected by the MILP optimizer at step $k$ ($P_{\text{diesel}}, P_{\text{charge}}, P_{\text{discharge}}$).
- **Category E: STATE-AFTER-ACTION**: The `DigitalTwin` state resulting from action execution at step $k+1$ ($\text{SOC}_{k+1}$).
- **Category F: CUMULATIVE STATE**: Running totals for diesel fuel, diesel energy, battery throughput, and curtailment after step $k$.

---

### 3. HARDENED TIMESTEP TELEMETRY SCHEMA

```
HARDENED_V2_TELEMETRY_SCHEMA:
├── IDENTITY:
│   ├── origin_id (int)
│   ├── origin_timestamp (iso_string)
│   ├── mpc_timestep_idx (int: 0..23)
│   └── timestamp (iso_string)
├── FORECAST_INPUT:
│   ├── treatment_forecast_vector_24 (float[24])
│   ├── control_forecast_vector_24 (float[24])
│   ├── actual_solar_truth (float W/m2)
│   ├── treatment_h1_forecast (float W/m2)
│   ├── control_h1_forecast (float W/m2)
│   ├── treatment_forecast_error_h1 (float W/m2)
│   ├── control_forecast_error_h1 (float W/m2)
│   └── forecast_difference_h1 (float W/m2)
├── STATE_BEFORE_ACTION:
│   ├── soc_before (float 0..1)
│   ├── diesel_state_before (string: ON/OFF)
│   ├── cumulative_diesel_fuel_before (float L)
│   └── cumulative_diesel_energy_before (float kWh)
├── OPTIMIZER_TELEMETRY:
│   ├── optimizer_status (string: Optimal/Infeasible)
│   ├── objective_value (float)
│   ├── diesel_commitment (int: 0 or 1)
│   ├── startup_event (boolean)
│   ├── shutdown_event (boolean)
│   ├── battery_charge_decision (float W)
│   ├── battery_discharge_decision (float W)
│   ├── reserve_status (float W)
│   └── constraint_status (string)
├── EXECUTED_ACTION:
│   ├── h1_diesel_power (float W)
│   ├── h1_battery_charge_power (float W)
│   ├── h1_battery_discharge_power (float W)
│   ├── h1_renewable_dispatch (float W)
│   ├── h1_renewable_curtailment (float W)
│   ├── h1_served_load (float W)
│   └── h1_unmet_load (float W)
└── STATE_AFTER_ACTION:
    ├── soc_after (float 0..1)
    ├── diesel_state_after (string: ON/OFF)
    ├── cumulative_diesel_fuel_after (float L)
    ├── cumulative_diesel_energy_after (float kWh)
    └── cumulative_battery_throughput_after (float kWh)
```

---

### 4. EXPLICIT V1 $\rightarrow$ V2 EQUIVALENCE RULES

V2 is valid **only if** the telemetry layer is observational and injects **zero physical or operational divergence** relative to V1:

1. `V2_CONTROL_EQUIVALENCE_TO_V1 = REQUIRED`
2. `V2_TREATMENT_EQUIVALENCE_TO_V1 = REQUIRED`
3. `V2_INITIAL_STATE_EQUIVALENCE = REQUIRED`
4. `V2_REALIZED_TRAJECTORY_EQUIVALENCE = REQUIRED`
5. `V2_FORECAST_INPUT_EQUIVALENCE = REQUIRED`
6. `V2_EMS_CONFIGURATION_EQUIVALENCE = REQUIRED`
7. `V2_OPTIMIZER_EQUIVALENCE = REQUIRED`
8. `V2_SIMULATOR_EQUIVALENCE = REQUIRED`
9. `V2_SOLVER_EQUIVALENCE = REQUIRED`

---

### 5. TARGET TEMPORAL MECHANISM CHAIN

The future V2 protocol will test the operational sequence:

$$\text{Forecast Difference} \rightarrow \text{MPC Decision Divergence} \rightarrow \text{Executed Diesel Decision} \rightarrow \text{Battery/SOC Response} \rightarrow \text{Renewable Curtailment} \rightarrow \text{Cumulative Fuel Outcome}$$

Each arrow requires direct timestep evidence before it can be classified as:
- **A — DIRECTLY OBSERVED**
- **B — STRONGLY SUPPORTED**

Correlation alone remains classified as **C — EXPLORATORY ASSOCIATION ONLY**.

---

### 6. HARD STOP & GOVERNANCE SUMMARY

```
============================================================
FINAL GOVERNANCE ARCHITECTURE STATE
============================================================
CONTROL_IMPLEMENTATION_PROVENANCE: ESTABLISHED
EMS_PROVENANCE:                   ESTABLISHED
OPTIMIZER_PROVENANCE:             ESTABLISHED
SIMULATOR_PROVENANCE:             ESTABLISHED
SOLVER_PROVENANCE:                ESTABLISHED
TIMESTEP_TELEMETRY_SEMANTICS:     HARDENED
V1_EQUIVALENCE_REQUIREMENTS:      HARDENED
V2_EXECUTION_AUTHORIZATION:       NOT_AUTHORIZED
V2_IMPLEMENTED:                   NO
V2_EXECUTED:                   NO
V1_RERUN:                         NO
V1_RESULT_CHANGED:                NO
EMS_CHANGED:                      NO
OPTIMIZER_CHANGED:                NO
SIMULATOR_CHANGED:                NO
MODEL_CHANGED:                    NO
============================================================
```

#### Artifact Location Summary
1. **Hardened V2 Protocol MD**: [`POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.md)
2. **Hardened V2 Protocol JSON**: [`POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.json)
