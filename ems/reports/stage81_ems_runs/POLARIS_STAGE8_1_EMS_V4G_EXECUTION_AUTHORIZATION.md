# POLARIS Stage 8.1 EMS V4.G Single-Horizon Mechanism Isolation
## Formal Execution Authorization Gate Report
## AUTHORIZATION REVIEW ONLY — NO EMPIRICAL EXECUTION — NO PILOT — NO SMOKE TEST — NO ORIGIN 1

```yaml
GOVERNANCE_STATUS: V4G_EXECUTION_AUTHORIZED
CANDIDATE_ID: V4.G_SINGLE_HORIZON_ISOLATED_DISCOUNTING
CLASSIFICATION: A — V4.G EXECUTION AUTHORIZED
V3_STATUS: ACCEPTED_AND_FROZEN
V3_RAW_CSV: POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv
V3_RAW_SHA256: a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e
V3_MECHANISM_BRANCH: CLOSED
V4_DESIGN_GATE: COMPLETE
V4G_SPECIFICATION: FROZEN
V4G_IMPLEMENTATION: COMPLETE
V4G_STATIC_AUDIT: PASSED_CLASSIFICATION_A
V4G_EXECUTION_AUTHORIZATION: AUTHORIZED
V4G_EMPIRICAL_EXECUTION: NOT_YET_EXECUTED
TARGET_HORIZON: h=14
TARGET_DECISION_INDEX: t=13
V4_G_WEIGHT: 0.5133
ALL_OTHER_WEIGHTS: 1.0
RESOURCE_CONFIGURATION:
  MAX_WORKERS: 2
  RESOURCE_CHANGE_TYPE: NON_SCIENTIFIC_RUNTIME_CONFIGURATION
  SCIENTIFIC_PROTOCOL_CHANGED: NO
  EMS_CHANGED: NO
  OPTIMIZER_SCIENTIFIC_LOGIC_CHANGED: NO
  FORECAST_ARTIFACT_CHANGED: NO
  SIMULATOR_CHANGED: NO
  STATISTICAL_DESIGN_CHANGED: NO
THERMAL_SAFETY:
  PREVIOUS_8_WORKER_INCIDENT: TRUE
  PREVIOUS_2_WORKER_FORMAL_REPLAY: COMPLETED
  PREVIOUS_2_WORKER_REPORTED_CPU_TEMPERATURE: "<75C"
  V4G_EXECUTION_WORKER_CONFIGURATION: 2
  THERMAL_MONITORING_MODE: MANUAL
  MONITORING_REQUIREMENT: Execution must be continuously monitored, and the process must be manually halted if thermal limits are exceeded.
```

---

## 1. Governance State & Executive Summary

This document establishes the official **Formal Execution Authorization Gate** for **Candidate V4.G — Single-Horizon Mechanism Isolation** in the POLARIS Energy Management System (EMS).

### Current Governed State:
- **V1 Execution**: `ACCEPTED + FROZEN`
- **V2 Replay Execution**: `ACCEPTED + FROZEN`
- **V3 Class F Execution**: `VALID COMPLETED EXECUTION + FROZEN`
- **V3 Raw Evidence**: `FROZEN` (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`, SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)
- **V3 Mechanism Branch**: `CLOSED`
- **V4 Design Gate**: `COMPLETE`
- **V4.G Specification Gate**: `FROZEN`
- **V4.G Implementation Gate**: `COMPLETE (CLASSIFICATION A)`
- **V4.G Static Audit**: `PASSED`
- **V4.G Execution Authorization**: `AUTHORIZED (CLASSIFICATION A)`
- **V4.G Empirical Execution**: `NOT YET EXECUTED`

> [!IMPORTANT]
> **MANDATORY HARD STOP**: This task is strictly a governance authorization review. **ZERO V4.G origins were executed during this task.** No pilot, smoke test, pretest, or origin 1 replay was triggered. Empirical execution is authorized for a future separate task.

---

## 2. Independent SHA256 Provenance Audit

All 16 required system components, forecast artifacts, contracts, simulators, implementation files, and governance documents were independently verified from the filesystem:

| Artifact / Protected Source File | Verified SHA256 Hash | Provenance Status |
|---|---|---|
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` | `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e` | `FROZEN` |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION.json` | `5c84d72bc13d52d9b1580ca02b66a5e1281db2bd1be97405e3a27f6cf4c0ff95` | `FROZEN` |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION.md` | `b348f98ec448d37e69f8c05e197c36ca2cfdf5137df776fa2e7d77b817e948c3` | `FROZEN` |
| `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv` | `052e43be4cbe4599a0a4cb402b805ecdbbdab1cf2bf13b5bf0314bd94bf6ffea` | `FROZEN` |
| `system/schemas/forecast_bundle.py` | `090b8f44ff5ae7a8c3d9a16fbdadcd7acae6e511487ea0b7fb5ca8fa7b78972d` | `FROZEN` |
| `system/schemas/station_state.py` | `ffcd75b6aedbf12d4d98d28a3f8fa3ddf7a14e9185a767431bf3bb79a835b3ec` | `FROZEN` |
| `system/schemas/dispatch_plan.py` | `d76dbdcf1b3fb457385906f3458db9ebddbc8e0fdb291079d8efd4df6a83a005` | `FROZEN` |
| `system/simulation/simulator.py` | `aa7668697b0932bb821b016f4d221cd88bb82d36fb56358c2be6ce8806296cc7` | `FROZEN` |
| `system/runtime/runner.py` | `4f32fb0f9aef7c11f74fa18cbf5e7ffecdf61681b4efb489bb2dfabf972b220e` | `FROZEN` |
| `system/forecasting/implementations/s81_solar.py` | `b99e746a51d95bf085c88cbb5f154563a6f1d171e544ae5d01fbffbbbe834167` | `FROZEN` |
| `system/optimization/implementations/milp.py` | `e2a05fbdfedcd89574d71587d65b4c1069ebbd18cfcb9bcf51bfef252f4c9bf6` | `VERIFIED_V4G` |
| `POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.md` | `b181ca55d78a9c4ce8c707db3b8398e0bb50b5fd03b22b72edbf32efb692aa06` | `FROZEN` |
| `POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.json` | `dbe9ec598f683e390c58eeb2951b147dd39542a275326759fcce82410a562479` | `FROZEN` |
| `POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.md` | `165c71d603a11b81fa3cbddedac4a7aaefefdd5dffdfceecaaae8ebc9fceaa3b` | `FROZEN` |
| `POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.json` | `d0ffc17f4260907d4b4a243eec3bfac0dddf9fe0f3531ea908ad76a445d470d9` | `FROZEN` |
| `test_v4g_static_implementation.py` | `a6ddfe1aa8ecff2a7e78d910a30cdfae6cae8d3568fa05ef1c6d860d5b5ec584` | `FROZEN` |

---

## 3. Authoritative Specification & Code Verification

### Specification & Index Semantics Verification:
- **Target Forecast Horizon**: $h = 14$
- **Target MILP Decision Index**: $t = 13$ ($h = t + 1$)
- **Frozen V4.G Weight**: $w_{13} = 0.5133$ (Exact frozen parameter inherited from $0.95^{13}$, untuned).
- **All Other Timestep Weights**: $w_t = 1.0$ for all $t \ne 13$.

### MILP Implementation Logic Inspection (`milp.py`):
```python
            # Horizon Weighting: Baseline (gamma=1.0), Class F (gamma=0.95), or V4.G Single-Horizon Mode (t=13 -> w_13=0.5133)
            opt_cfg = config.get("optimizer", {})
            if opt_cfg.get("v4g_single_horizon_mode", False):
                t_target = int(opt_cfg.get("v4g_target_index", 13))
                w_target = float(opt_cfg.get("v4g_weight", 0.5133))
                w_t = w_target if t == t_target else 1.0
            else:
                gamma = float(opt_cfg.get("horizon_discount_factor_gamma", 1.0))
                w_t = gamma ** t
```
- **Verification**: The conditional branch cleanly activates V4.G weighting when `v4g_single_horizon_mode=True`. When `v4g_single_horizon_mode=False`, the standard `gamma ** t` logic executes, ensuring $100\%$ backward compatibility for V1, V2, and V3 Class F.

---

## 4. Objective Invariants & V3/V4.G Isolation Verification

### Objective-Term Mapping Invariants:
1. **Weighted Operational Terms**: $w_t$ modifies only:
   - Solar Curtailment Penalty (`c[base + 2]`)
   - Wind Curtailment Penalty (`c[base + 3]`)
   - Battery Charge Degradation (`c[base + 4]`)
   - Battery Discharge Degradation (`c[base + 5]`)
   - Diesel Marginal Fuel Cost (`c[base + 7]`)
   - Diesel Base Running Fuel Cost (`c[base + 13]`)
   - Diesel Generator Startup Cost (`c[base + 14]`)
2. **Unweighted Term Invariant**: Unmet Critical Load Penalty (`c[base + 9]`) is strictly **UNWEIGHTED** ($w_{\text{unmet}, t} = 1.0$).

### Structural Isolation Verification:
- **Arm 2 (V3 Reference)** vs. **Arm 3 (V4.G Candidate)**:
  - Both arms consume identical Stage 8.1 prediction vectors (`POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`).
  - Both arms use identical initial station states (`StationState`), physical battery limits ($20\%\dots 95\%$), generator min/max power ($10\text{ kW}\dots 100\text{ kW}$), inverter efficiency ($92\%$), linear constraints, and HiGHS solver parameters.
  - The **ONLY** difference between Arm 2 and Arm 3 is the objective weight vector $w$:
    - Arm 2 (V3): $w_t = [1.0, 0.95, 0.95^2, \dots, 0.95^{13}, \dots, 0.95^{23}]$
    - Arm 3 (V4.G): $w_t = [1.0, 1.0, 1.0, \dots, 0.5133, \dots, 1.0]$

---

## 5. Future Truth Firewall & Telemetry Protocols

### Future Truth Firewall:
The information flow strictly enforces temporal causality:
$$\text{Forecast Engine } (\hat{y}_t) \;\longrightarrow\; \text{Energy Optimizer } (w_t, MILP) \;\longrightarrow\; \text{Dispatch Plan } (P_{d,t}) \;\longrightarrow\; \text{Simulator / Ground Truth } (y_{t,\text{actual}}) \;\longrightarrow\; \text{Telemetry}$$
- **Verification**: Zero future realized ground truth enters forecast generation, objective weighting, or optimizer decision logic. Truth is realized solely inside `DigitalTwinSimulator.step()` after dispatch decisions are locked.

### Telemetry Protocol:
- Observational, passive, non-interventional V2/V3 telemetry collector (`V2TelemetryCollector` / `V3TelemetryCollector`) remains active.
- Telemetry schema and semantics are unchanged. Zero new scientific variables added.

---

## 6. Statistical & Resource Execution Protocol

### Statistical Protocol:
- **Experimental Unit**: $N = 173$ paired forecast origins across the governed 347-window dataset.
- **Primary Endpoint**: Total diesel fuel consumption per 24h origin ($\text{L/origin}$), evaluated as paired delta $(V4.G - V3)$.
- **No Peeking / No Cherry-Picking**:
  - All 173 eligible origins must be executed sequentially.
  - Zero result-dependent stopping, zero selective origin removal, zero parameter tuning during or after execution.
  - Any failed origin will be recorded explicitly as a failure event; no silent reruns permitted.

### Resource & Thermal Execution Safeguards:
- **Worker Configuration**: Formally set to **`MAX_WORKERS = 2`** (Resource configuration correction). The selected configuration is 2 workers because the previous formally executed Stage 8.1$\rightarrow$EMS replay completed successfully at 2 workers with reported CPU temperature remaining below $75^\circ\text{C}$, whereas an earlier 8-worker attempt produced unsafe thermal behavior.
- **Thermal Safety Monitoring**: Execution must be continuously monitored, and the process must be manually halted if thermal limits are exceeded (`THERMAL_MONITORING_MODE = MANUAL`).

---

## 7. Formal Gate Authorization & Classification

### Gate Classification:
- **Classification**: `A — V4.G EXECUTION AUTHORIZED`

### Verification Summary:
1. **Specification**: Frozen parameter $w_{13} = 0.5133$ and index mapping $t=13 \leftrightarrow h=14$ verified.
2. **Implementation**: Verified in `milp.py` with 8/8 passing static mechanical unit tests.
3. **SHA256 Provenance**: All 16 protected files independently verified from filesystem.
4. **Isolation**: Arm 2 vs Arm 3 structural isolation established; objective weight vector is the single scientific variable.
5. **Truth Firewall & Telemetry**: Causality firewall and non-interventional telemetry verified.
6. **Execution Integrity**: Zero origins executed during authorization review.

---

## 8. Final Governance State & Execution Hard Stop

```yaml
V3_STATUS: ACCEPTED_AND_FROZEN
V3_MECHANISM_BRANCH: CLOSED
V4_DESIGN_GATE: COMPLETE
V4G_SPECIFICATION: FROZEN
V4G_IMPLEMENTATION: COMPLETE
V4G_STATIC_AUDIT: PASSED_CLASSIFICATION_A
V4G_EXECUTION_AUTHORIZATION: AUTHORIZED
V4G_EMPIRICAL_EXECUTION: NOT_YET_EXECUTED
```

---
**ABSOLUTE HARD STOP.**  
*This task was an AUTHORIZATION REVIEW ONLY. Zero empirical origins, zero pilots, zero smoke tests, and zero origin 1 replays were executed. The formal V4.G 173-origin empirical execution is authorized to proceed in a separate dedicated task.*
