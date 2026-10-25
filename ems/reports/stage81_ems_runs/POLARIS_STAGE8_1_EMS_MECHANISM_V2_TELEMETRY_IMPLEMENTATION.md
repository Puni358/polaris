# POLARIS Stage8.1 → EMS Mechanism Observability V2 Telemetry Implementation

## 1. Governance State & Final Classification

```yaml
V1 EMPIRICAL REPLAY: ACCEPTED_AND_FROZEN
V1 RESULT: UNCHANGED
V1 RERUN: NO
V2 PROTOCOL: HARDENED
V2 PRE-IMPLEMENTATION CONSISTENCY: COMPLETE
V2 TELEMETRY IMPLEMENTATION: COMPLETE
V2 RUNTIME EQUIVALENCE: NOT YET VERIFIED
V2 EXECUTION: NOT AUTHORIZED
FINAL_CLASSIFICATION: A — V2 TELEMETRY IMPLEMENTATION COMPLETE AND STATICALLY VERIFIED
```

## 2. Telemetry Field Summary

- **TOTAL UNIQUE FIELDS**: 37
- **DIRECTLY_AVAILABLE**: 23
- **REQUIRES_INSTRUMENTATION**: 14
- **NOT_AVAILABLE**: 0

## 3. Modified Source Files & Provenance Audit

| Path | Purpose | Before SHA256 | After SHA256 | Scientific Logic Changed | Decision Logic Changed |
|---|---|---|---|---|---|
| `system/runtime/runner.py` | Add passive v2_telemetry_collector hook to run_pipeline MPC execution loop | `0a1bb4f13134ea5f...` | `43b3cfb281948028...` | NO | NO |
| `system/telemetry/v2_logger.py [NEW]` | Authoritative 37-field V2 Observational Telemetry Schema and Collector Implementation | `N/A (NEW FILE)...` | `131ff6f4dc83a2a5...` | NO | NO |
| `system/tests/test_v2_telemetry.py [NEW]` | Bounded Unit and Governance Test Suite for V2 Telemetry | `N/A (NEW FILE)...` | `078bae332513898a...` | NO | NO |

## 4. Protected Artifact Verification (18/18 Verified Untouched)

| Protected File | Pre-Implementation SHA256 | Post-Implementation SHA256 | Match |
|---|---|---|---|
| `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c...` | `a4d288f9bba4a57c...` | **True** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv` | `7d9c6e7af82b6198...` | `7d9c6e7af82b6198...` | **True** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.json` | `80cf3be4955da83a...` | `80cf3be4955da83a...` | **True** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md` | `0b516787444ed5c9...` | `0b516787444ed5c9...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.md` | `8c2c8da41134b9b2...` | `8c2c8da41134b9b2...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.json` | `f3b6ecd581d6c790...` | `f3b6ecd581d6c790...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.md` | `ac4dec9e101adc8e...` | `ac4dec9e101adc8e...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.json` | `f8e574fb6f774b2a...` | `f8e574fb6f774b2a...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.md` | `c9a61cd0e726e37a...` | `c9a61cd0e726e37a...` | **True** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.json` | `3c47c8a4b283aa41...` | `3c47c8a4b283aa41...` | **True** |
| `POLARIS_STAGE8_1_EMS_V2_FINAL_PRE_IMPLEMENTATION_CONSISTENCY_CHECK.md` | `1ff1d00ddde7ece3...` | `1ff1d00ddde7ece3...` | **True** |
| `POLARIS_STAGE8_1_EMS_V2_FINAL_PRE_IMPLEMENTATION_CONSISTENCY_CHECK.json` | `35b33d1eb8582f37...` | `35b33d1eb8582f37...` | **True** |
| `POLARIS_STAGE8_1_EMS_V2_PRE_IMPLEMENTATION_CORRECTION.md` | `e064a87a09cd2fab...` | `e064a87a09cd2fab...` | **True** |
| `POLARIS_STAGE8_1_EMS_V2_PRE_IMPLEMENTATION_CORRECTION.json` | `50c23683fa9a4ad7...` | `50c23683fa9a4ad7...` | **True** |
| `POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.md` | `e6fd9974cb4fa7d3...` | `e6fd9974cb4fa7d3...` | **True** |
| `POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.json` | `629f4731cb269cd2...` | `629f4731cb269cd2...` | **True** |
| `POLARIS_STAGE8_1_EMS_V1_MECHANISM_WORDING_CORRECTION_MANIFEST.md` | `2dbdf65d2c44cc37...` | `2dbdf65d2c44cc37...` | **True** |
| `POLARIS_STAGE8_1_EMS_V1_MECHANISM_WORDING_CORRECTION_MANIFEST.json` | `e5634d69595dee2b...` | `e5634d69595dee2b...` | **True** |

## 5. Authoritative 37-Field Traceability Matrix

| Field Name | Category | Availability Class | Source Object | Source Variable | Source Code Location | Capture Method | Units | Timing Semantics |
|---|---|---|---|---|---|---|---|---|
| `origin_id` | Identity | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `execution context` | `oid` | `run_polaris_stage8_1_ems_empirical_replay.py:83` | Direct pass | `unitless` | Origin ID for 24h simulation window |
| `origin_timestamp` | Identity | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `execution context` | `t0_ts` | `run_polaris_stage8_1_ems_empirical_replay.py:95` | Direct pass | `ISO8601 UTC` | Timestamp of origin t0 |
| `mpc_timestep_idx` | Identity | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `MPC loop` | `step_k / step_idx` | `system/runtime/runner.py:112` | Direct pass | `unitless` | MPC horizon step index k |
| `timestamp` | Identity | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `StationState` | `curr_state.timestamp` | `system/schemas/station_state.py:11` | Property read | `ISO8601 UTC` | Current step timestamp |
| `treatment_forecast_vector_24` | Forecast Input | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `runtime_context / ForecastBundle` | `sw_in_forecast / bundle.solar_irradiance.point` | `system/runtime/runner.py:118` | Direct list read | `W/m^2` | 24-step irradiance forecast supplied to optimizer |
| `control_forecast_vector_24` | Forecast Input | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `runtime_context / ForecastBundle` | `control_sw_in / bundle_ctrl.solar_irradiance.point` | `system/runtime/runner.py:118` | Direct list read | `W/m^2` | Control 24-step forecast supplied to optimizer |
| `actual_solar_truth` | Forecast Input | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `future_actuals` | `next_actual['actual_SW_IN']` | `system/runtime/runner.py:191` | Dictionary read | `W/m^2` | Realized ground truth irradiance for step k |
| `treatment_h1_forecast` | Forecast Input | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `treatment_forecast_vector_24` | `treatment_forecast_vector_24[0]` | `system/telemetry/v2_logger.py:240` | Array index 0 | `W/m^2` | H1 forecast step value |
| `control_h1_forecast` | Forecast Input | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `control_forecast_vector_24` | `control_forecast_vector_24[0]` | `system/telemetry/v2_logger.py:241` | Array index 0 | `W/m^2` | Control H1 forecast step value |
| `treatment_forecast_error_h1` | Forecast Input | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `derived` | `treatment_h1 - actual_truth` | `system/telemetry/v2_logger.py:244` | Difference calculation | `W/m^2` | H1 forecast error (Treatment - Truth) |
| `control_forecast_error_h1` | Forecast Input | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `derived` | `control_h1 - actual_truth` | `system/telemetry/v2_logger.py:245` | Difference calculation | `W/m^2` | H1 forecast error (Control - Truth) |
| `forecast_difference_h1` | Forecast Input | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `derived` | `treatment_h1 - control_h1` | `system/telemetry/v2_logger.py:246` | Difference calculation | `W/m^2` | H1 forecast difference (Treatment - Control) |
| `soc_before` | State Before Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `StationState` | `curr_state.battery_soc_pct` | `system/schemas/station_state.py:21` | Property read | `%` | SOC prior to step execution |
| `diesel_state_before` | State Before Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `StationState` | `curr_state.diesel_running` | `system/schemas/station_state.py:23` | Property read | `boolean` | Diesel running status prior to step execution |
| `cumulative_diesel_fuel_before` | State Before Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `StationState / Collector` | `cumulative_diesel_fuel_l` | `system/runtime/runner.py:208` | Property read | `L` | Cumulative fuel consumed prior to step execution |
| `cumulative_diesel_energy_before` | State Before Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `StationState / Collector` | `cumulative_diesel_energy_kwh` | `system/runtime/runner.py:209` | Property read | `kWh` | Cumulative diesel energy produced prior to step execution |
| `optimizer_status` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.constraint_status` | `system/schemas/dispatch_plan.py:71` | Property read | `text` | Status returned by solver (OPTIMAL / INFEASIBLE) |
| `objective_value` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.objective_value` | `system/schemas/dispatch_plan.py:70` | Property read | `dimensionless` | MILP objective value |
| `diesel_commitment` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.diesel_power[0] > 0` | `system/schemas/dispatch_plan.py:56` | Boolean evaluation | `binary (0/1)` | Optimizer H1 binary commitment decision |
| `startup_event` | Optimizer | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `derived` | `(not diesel_state_before) and bool(diesel_commitment)` | `system/telemetry/v2_logger.py:249` | Logic comparison | `boolean` | True if diesel starts at step k |
| `shutdown_event` | Optimizer | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `derived` | `diesel_state_before and bool(not diesel_commitment)` | `system/telemetry/v2_logger.py:250` | Logic comparison | `boolean` | True if diesel shuts down at step k |
| `battery_charge_decision` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.battery_charge[0] / 1000.0` | `system/schemas/dispatch_plan.py:53` | Array index 0 / 1000 | `kW` | Optimizer H1 battery charge power decision |
| `battery_discharge_decision` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.battery_discharge[0] / 1000.0` | `system/schemas/dispatch_plan.py:54` | Array index 0 / 1000 | `kW` | Optimizer H1 battery discharge power decision |
| `reserve_status` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.reserve_status` | `system/schemas/dispatch_plan.py` | Property read | `text` | Operating reserve status from solver |
| `constraint_status` | Optimizer | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DispatchPlan` | `plan.constraint_status` | `system/schemas/dispatch_plan.py:71` | Property read | `text` | Detailed constraint fulfillment status |
| `h1_diesel_power` | Executed Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DigitalTwinSimulator` | `plan.diesel_power[0] / 1000.0` | `system/simulation/simulator.py:35` | Property read / 1000 | `kW` | Actual executed diesel power output in step k |
| `h1_battery_charge_power` | Executed Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DigitalTwinSimulator` | `plan.battery_charge[0] / 1000.0` | `system/simulation/simulator.py:33` | Property read / 1000 | `kW` | Actual executed battery charge power in step k |
| `h1_battery_discharge_power` | Executed Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `DigitalTwinSimulator` | `plan.battery_discharge[0] / 1000.0` | `system/simulation/simulator.py:34` | Property read / 1000 | `kW` | Actual executed battery discharge power in step k |
| `h1_renewable_dispatch` | Executed Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `DispatchPlan / Simulator` | `(plan.solar_used[0] + plan.wind_used[0]) / 1000.0` | `system/runtime/runner.py:218` | Summation / 1000 | `kW` | Actual dispatched renewable power in step k |
| `h1_renewable_curtailment` | Executed Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `DispatchPlan / Simulator` | `plan.renewable_curtailment[0] / 1000.0` | `system/schemas/dispatch_plan.py:59` | Array index 0 / 1000 | `kW` | Curtailed renewable power in step k |
| `h1_served_load` | Executed Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `DispatchPlan / Simulator` | `plan.load_served[0] / 1000.0` | `system/schemas/dispatch_plan.py:57` | Array index 0 / 1000 | `kW` | Demand served in step k |
| `h1_unmet_load` | Executed Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `DispatchPlan / Simulator` | `plan.unmet_load[0] / 1000.0` | `system/schemas/dispatch_plan.py:60` | Array index 0 / 1000 | `kW` | Unmet demand in step k |
| `soc_after` | State After Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `StationState (next)` | `next_state.battery_soc_pct` | `system/simulation/simulator.py:59` | Property read | `%` | SOC following step execution |
| `diesel_state_after` | State After Action | `DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT` | `StationState (next)` | `next_state.diesel_running` | `system/simulation/simulator.py:61` | Property read | `boolean` | Diesel running status following step execution |
| `cumulative_diesel_fuel_after` | State After Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `StationState (next)` | `cumulative_diesel_fuel_l` | `system/runtime/runner.py:224` | Property read | `L` | Cumulative fuel consumed following step execution |
| `cumulative_diesel_energy_after` | State After Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `StationState (next)` | `cumulative_diesel_energy_kwh` | `system/runtime/runner.py:225` | Property read | `kWh` | Cumulative diesel energy produced following step execution |
| `cumulative_battery_throughput_after` | State After Action | `REQUIRES_EXECUTION_CODE_INSTRUMENTATION` | `StationState (next)` | `cumulative_battery_throughput_kwh` | `system/runtime/runner.py:226` | Property read | `kWh` | Cumulative battery throughput following step execution |

## 6. Non-Intervention & Bounded Verification Summary

- **Passive Non-Intervention**: Optional `v2_telemetry_collector` parameter defaults to `None`. Zero overhead, zero mutation of execution inputs, plans, state, or solver parameters.
- **Future-Truth Firewall**: Ground truth actuals are accessed strictly after optimization step completion.
- **Forecast Preservation**: Raw float 24-step forecast vectors preserved with full float precision.
- **Deterministic Serialization**: Identical JSON and CSV outputs across repeated test runs.
- **Bounded Test Results**: 25 passed in 0.99s (`test_v2_telemetry.py`, `test_s81_adapter.py`, `test_d5_implementation.py`).
- **Solver Provenance**: HiGHS interface provenance ESTABLISHED; solver binary hash NOT_ESTABLISHED.
- **Zero Replay Execution**: 0 V1 origins replayed, 0 V2 origins replayed, 0 pilots, 0 smoke tests.

## 7. Required Final Governance State

```yaml
V1 = ACCEPTED + FROZEN
V1 RESULT = UNCHANGED
V1 RERUN = NO
V2 PROTOCOL = HARDENED
V2 PRE-IMPLEMENTATION CONSISTENCY = COMPLETE
V2 TELEMETRY IMPLEMENTATION = COMPLETE
V2 RUNTIME EQUIVALENCE = NOT YET VERIFIED
V2 EXECUTION = NOT AUTHORIZED
```
