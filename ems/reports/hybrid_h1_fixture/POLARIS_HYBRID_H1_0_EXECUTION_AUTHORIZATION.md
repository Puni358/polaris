# POLARIS Step 10B: Hybrid Runtime Execution Authorization

## Executive Summary

This artifact represents the formal **pre-execution authorization gate** for the first H1.0 hybrid runtime execution.

- **Experiment Type:** `SINGLE_TRAJECTORY_END_TO_END_ENGINEERING_VALIDATION`
- **Scope:** Exactly **ONE** 24-hour MPC trajectory (24 timesteps).
- **Execution Purpose:** Validate interface flow, provenance integrity, and future-truth firewall execution under closed-loop MPC control.
- **Authorization Result:** **AUTHORIZED FOR ONE TRAJECTORY ONLY**

**ZERO MILP solves** and **ZERO simulator steps** were executed during this authorization step.

---

## 1. Predeclared Trajectory Selection

- **Selection Rule:** `FIRST_VALID_COMPLETE_24_HOUR_WINDOW`
- **Fixture:** `POLARIS_HYBRID_FIXTURE_H1_0/`
- **Fixture Hash (SHA-256):** `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023`
- **Row Index Range:** 0 to 23 (24 hourly records)
- **Origin Timestamp ($t_0$):** `2024-01-01T00:00:00Z`
- **End Timestamp:** `2024-01-01T23:00:00Z`
- **Horizon Length:** 24 hours (t0 + 1h to t0 + 24h)

---

## 2. Predeclared Initial State ($t_0$)

- **Timestamp:** `2024-01-01T00:00:00Z`
- **Battery SOC:** 50.0% (100.0 kWh out of 200.0 kWh nominal capacity)
- **Diesel Generator State:** Off (`diesel_running = False`, `diesel_hours_running = 0.0`)
- **Last Observed Solar Irradiance:** `0.0 W/m^2`
- **Last Observed Demand:** `21,600.0 W` (from H1.0 row 0 `synthetic_load_W`)
- **Last Observed Wind Generation:** `0.0 W` (from H1.0 row 0 `wind_power_generic_W`)
- **Serialized Initial State SHA-256:** `3e38d4f5e3046d642c26b56a84e9e0130b0bfddea24be37640b90a4fd2c55fbd`

---

## 3. Provenance Boundary Rules

1. `solar_SW_IN_W_m2` = `REAL_MEASURED` (SITES Nuolja AWS 2024)
2. `solar_PV_power_W` = `DERIVED_ENGINEERING_QUANTITY` (D3 formula P_pv = min(SW_IN * 51, 60 kW))
3. `wind_speed_proxy_m_s` = `REAL_MEASUREMENT_PROXY` (SMHI Station 188790 Abisko Aut 10m wind speed)
4. `wind_power_generic_W` = `SYNTHETIC_ENGINEERING_SCENARIO` (`POLAR_REFERENCE_TURBINE_SCENARIO`, `NOT_NUOLJA_HARDWARE`)
5. `synthetic_load_W` = `SYNTHETIC` (`SYNTHETIC_STATION_DEMAND != NULLOJA_MEASURED_DEMAND`)

---

## 4. Predeclared Output Artifact Paths

1. Raw Telemetry: `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_RAW.csv`
2. Execution Manifest: `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION.json`
3. Execution Report: `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION.md`
4. Provenance Manifest: `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_PROVENANCE.json`
5. SHA-256 Manifest: `POLARIS_HYBRID_H1_0_ENGINEERING_VALIDATION_HASHES.json`

---

## 5. Execution Authorization Gate Table (G01 – G24)

| Gate Identifier | Status | Verification Detail |
| :--- | :---: | :--- |
| `G01_h10_fixture_hash_match` | **PASS** | Fixture CSV SHA-256 verified (762297aae21c0cb9...). |
| `G02_h10_config_match` | **PASS** | H1.0 config SHA-256 verified (b60ca342f23179ca...). |
| `G03_h10_provenance_match` | **PASS** | H1.0 provenance manifest SHA-256 verified (ed505b118ee774a6...). |
| `G04_h10_determinism_verification` | **PASS** | Step 9 determinism verification PASS confirmed. |
| `G05_step10a_audit_pass` | **PASS** | Step 10A classification verified as A (Statically Verified). |
| `G06_forecast_bundle_unchanged` | **PASS** | ForecastBundle schema hash verified (899aaa48272fd446...). |
| `G07_station_state_unchanged` | **PASS** | StationState schema hash verified (b6e78e8292bbba40...). |
| `G08_dispatch_plan_unchanged` | **PASS** | DispatchPlan schema hash verified (cbf80578a0b4fa28...). |
| `G09_optimizer_unchanged` | **PASS** | MILP EnergyOptimizer hash verified (ee913b68b736602e...). |
| `G10_simulator_unchanged` | **PASS** | DigitalTwinSimulator hash verified (7217dc2b03448021...). |
| `G11_truth_firewall_pass` | **PASS** | Future-truth firewall order verified statically in runner.py. |
| `G12_no_future_truth_leakage` | **PASS** | Zero future actual values exposed to ForecastEngine or EnergyOptimizer. |
| `G13_trajectory_selection_frozen` | **PASS** | Preselected trajectory frozen: 2024-01-01T00:00:00Z to 2024-01-01T23:00:00Z (Index 0..23). |
| `G14_initial_state_frozen` | **PASS** | Initial StationState frozen at 2024-01-01T00:00:00Z (SOC 50%, SHA 3e38d4f5e3046d64...). |
| `G15_forecast_policy_frozen` | **PASS** | Stage8.1 solar adapter D3 mapping + Wind ARX proxy + generic turbine scenario frozen. |
| `G16_telemetry_requirements_satisfied` | **PASS** | 24-step MPC trajectory telemetry collector configured to output complete execution details. |
| `G17_solver_runtime_config_frozen` | **PASS** | SCIPY_OPTIMIZE_MILP_HIGHS: The frozen LocalMILPEnergyOptimizer directly invokes scipy.optimize.milp, which uses the HiGHS MILP engine. No CBC path or solver fallback exists in the verified H1.0 execution path. |
| `G18_thermal_governance_ready` | **PASS** | Hardware baseline recorded (Load 1.16, Mem 7.8GB, Swap 4.2GB). Thermal limit 80 C active. |
| `G19_output_paths_clear` | **PASS** | Predeclared output file paths checked; zero frozen research evidence affected. |
| `G20_no_control_arm` | **PASS** | Single trajectory validation only. CONTROL_ARM = NONE, TREATMENT_ARM = NONE. |
| `G21_no_result_dependent_stopping` | **PASS** | Fixed 24-step horizon. Result-dependent stopping strictly prohibited. |
| `G22_no_pilot_smoke_test` | **PASS** | Zero execution executed during Step 10B. MILP_SOLVES = 0, SIMULATOR_STEPS = 0. |
| `G23_execution_scope_one_trajectory` | **PASS** | Scope restricted to exactly ONE 24-hour engineering trajectory (24 MPC cycles). |
| `G24_claim_boundary_accepted` | **PASS** | Strict claim boundary accepted (controlled hybrid engineering trajectory validation only). |

---

## 6. Mandatory Final Status

```plain
H1.0_FIXTURE_HASH = 762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023
H1.0_FIXTURE_INTEGRITY = PASS

STEP10A_STATUS = PASS

FORECASTBUNDLE_INTEGRITY = PASS
STATIONSTATE_INTEGRITY = PASS
DISPATCHPLAN_INTEGRITY = PASS
OPTIMIZER_INTEGRITY = PASS
SIMULATOR_INTEGRITY = PASS

TRUTH_FIREWALL = PASS
PROVENANCE_INTEGRITY = PASS
TRAJECTORY_SELECTION = FROZEN
INITIAL_STATE = FROZEN
TELEMETRY_READY = PASS
THERMAL_GOVERNANCE = READY

MILP_SOLVES_DURING_AUTHORIZATION = 0
SIMULATOR_STEPS_DURING_AUTHORIZATION = 0

FINAL_EXECUTION_AUTHORIZATION = AUTHORIZED
RUNTIME_EXECUTION = AUTHORIZED_FOR_ONE_TRAJECTORY_ONLY
```

---

## 7. Critical Execution Hard Stop

**DO NOT execute the trajectory as part of Step 10B.**

The actual command to run the authorized single trajectory must be issued separately after review of this authorization artifact.

`FINAL_EXECUTION_AUTHORIZATION` = **AUTHORIZED FOR ONE TRAJECTORY ONLY**
