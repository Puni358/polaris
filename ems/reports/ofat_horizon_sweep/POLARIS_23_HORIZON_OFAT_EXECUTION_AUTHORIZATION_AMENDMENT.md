# POLARIS 23-Horizon OFAT Experiment — Execution Authorization Amendment Report
## Governance Pre-Execution Verification & Implementation Amendment Gate
## FINAL EXECUTION AUTHORIZATION = AUTHORIZED

```yaml
GOVERNANCE_STATUS: IMPLEMENTATION_AMENDMENT_AUTHORIZED
ORIGINAL_AUTHORIZATION_STATUS: AUTHORIZED
IMPLEMENTATION_AMENDMENT_STATUS: AUTHORIZED
EXPERIMENT_PROTOCOL_STATUS: UNCHANGED
EXPERIMENT_EXECUTION_STATUS: NOT_EXECUTED_AFTER_REPAIR
MILP_SOLVES_SINCE_FAILED_LAUNCH: 0
FINAL_EXECUTION_AUTHORIZATION: AUTHORIZED
CANDIDATE_ID: POLARIS_23_HORIZON_OFAT_EXPERIMENT
CLASSIFICATION: A — GOVERNANCE AMENDMENT AUTHORIZED
CONTROL_ARM: Shared Frozen V3 Control (POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv) — Reused, No Rerun of V3
TREATMENT_ARMS: 23 genuine horizon treatments (j = 1..23)
EXCLUDED_ARM: j = 0 analytically excluded (0.95^0 = 1.0, Delta_0 = 0.0 liters fuel)
EXPERIMENTAL_UNIT: 173 frozen origins, 24 sequential MPC steps per origin
EXPECTED_MILP_SOLVES: 23 * 173 * 24 = 95,496 fresh exact MILP treatment solves
SOLVE_SEMANTICS: Fresh exact MILP solve per cycle. No warm starts, approximations, or skipped cycles.
RESOURCE_CONFIGURATION:
  MAX_WORKERS: 8
THERMAL_GOVERNANCE:
  TARGET_OPERATING_TEMPERATURE: 100C IS NOT AN OPERATING TARGET
  MONITORING: Active continuous CPU sensor sampling required
  HALT_RULE: Manually halt execution if temperature approaches hardware limit or thermal instability occurs
  SEMANTIC_INVARIANT: Do not alter scientific semantics or origin/cycle count for thermal reasons
TELEMETRY: Complete 37-field V2/V3 observational schema preserved (95,496 telemetry rows expected).
STATISTICS:
  DESIGN: Paired 173-origin treatment-vs-V3 comparisons (N=173)
  PRIMARY_ENDPOINT: Total diesel fuel consumption (L/24h)
  PRIMARY_MULTIPLICITY_METHOD: HOLM_BONFERRONI
  FAMILY_WISE_ALPHA: 0.05
  NUMBER_OF_HORIZON_TESTS: 23
  BH_FDR_CONFIRMATORY_STATUS: NOT_USED (Exploratory descriptive analysis only, no bearing on primary conclusion)
  HORIZON_SELECTION: Strictly predeclared. Zero result-dependent horizon selection.
PREEXECUTION_SOLVES_EXECUTED: 0 (Zero solves executed since failed initial launch)
EXECUTION_INVOCATION: python3 run_polaris_23_horizon_ofat_experiment.py --authorize-execution
```

---

## 1. Executive Summary & Amendment Scope

This document establishes the formal **Execution Authorization Amendment** for the **23-Horizon One-Factor-At-A-Time (OFAT) Experiment** in the POLARIS Energy Management System (EMS).

The original authorization record ([`POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.md)) is preserved unchanged as historical governance evidence. This separate amendment artifact authorizes the narrow implementation correction made to `system/optimization/implementations/milp.py` and records the post-repair harness provenance hash.

---

## 2. Failed Execution Event Log

1. **Initial Launch:** The authorized 23-Horizon OFAT execution was launched once from the terminal via `--authorize-execution`.
2. **Failure Point:** Halting occurred immediately in the first worker process before any MPC loop iteration or MILP solve due to a nonexistent schema method call (`StationState.default_initial_state()`) in the un-repaired harness.
3. **Execution Metrics at Failure:**
   - `MILP_SOLVES_COMPLETED = 0`
   - `TREATMENT_TRAJECTORIES_COMPLETED = 0`
   - `OFAT_OUTPUT_FINALIZED = NO`
4. **Post-Failure Status:** Halting preserved complete data isolation. No output CSV, JSON, or MD report was written or corrupted.

---

## 3. Scope of Implementation Amendment

This amendment formally authorizes **ONLY** the following narrow technical interface extension:

1. **Optimizer Extension (`system/optimization/implementations/milp.py`):**
   Authorizes the addition of the `custom_weight_vector` parameter to `LocalMILPEnergyOptimizer.optimize()`.
   - SHA256 Hash of `milp.py`: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`

2. **Repaired Harness (`run_polaris_23_horizon_ofat_experiment.py`):**
   Authorizes the reconstructed execution harness aligned with the Stage 8.1 V3 pipeline architecture.
   - SHA256 Hash of `run_polaris_23_horizon_ofat_experiment.py`: `943a7afce3eef51453e9f54354344fb53a18ab500465ca0699c112cc8befb424`

3. **Weight Vector Semantics:**
   The `custom_weight_vector` interface implements **ONLY** the predeclared OFAT objective weighting sequence:
   $$\text{For treatment arm } j \in [1, 23]: \quad w_j = 1.0, \quad w_t = 0.95^t \; (\forall t \neq j)$$

---

## 4. Technical Invariant & Non-Intervention Verification

The following code and physical invariants have been audited and verified statically:

- **Default ($\gamma = 1.0$) Behavior:** 100% unchanged.
- **V3 ($\gamma = 0.95$) Behavior:** 100% unchanged.
- **V4.G Behavior:** 100% unchanged.
- **Constraints ($A \mathbf{x} = \mathbf{b}$):** 100% unchanged across all 12 linear constraint groups.
- **Variable Bounds (`lb`, `ub`):** 100% unchanged.
- **Integrality Array:** 100% unchanged.
- **Solver Configuration:** HiGHS MILP solver parameters and precision bounds 100% unchanged.
- **Unmet-Load Penalty:** Unweighted ($c[\text{base}+9] = \text{unmet\_penalty} \cdot dt$) for all timesteps $t$.
- **Digital Twin Simulator:** Closed-loop differential physical equations 100% unchanged.
- **Schemas (`ForecastBundle`, `StationState`, `DispatchPlan`):** 100% unchanged.

---

## 5. Unchanged Scientific Protocol Declaration

All scientific protocol parameters remain **STRICTLY UNCHANGED**:

- **Treatment Arms:** 23 genuine horizon treatments ($j = 1 \dots 23$).
- **Analytical Exclusion:** $j = 0$ analytically excluded ($\Delta_0 = 0.0$ liters fuel difference by mathematical identity).
- **Experimental Population:** 173 frozen forecast origins (`POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`).
- **Sequential MPC Horizon:** 24 decision cycles per origin ($95,496$ total fresh MILP treatment solves).
- **Control Baseline:** Shared V3 control raw evidence (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`) reused verbatim with zero new control solves.
- **State Trajectory Isolation:** Independent state trajectory maintained per origin and treatment arm.
- **Future-Truth Firewall:** Ground truth isolated strictly to digital twin simulation steps.
- **Telemetry:** 37-field V2/V3 observational telemetry schema preserved (95,496 rows expected).
- **Resource Configuration:** `MAX_WORKERS = 8`.
- **Multiplicity Control:** Sole primary confirmatory procedure is Holm-Bonferroni step-down at family-wise $\alpha = 0.05$ across 23 tests.

---

## 6. Full Codebase & Provenance Hash Registry

| Protected Source / Artifact File | Verified SHA256 Hash | Provenance Status |
|---|---|---|
| `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv` | `b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c` | Frozen Stage 8.1 Forecast Index |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` | `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e` | Frozen Shared V3 Control Raw Artifact |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION.json` | `5c84d72bc13d52d9b1580ca02b66a5e1281db2bd1be97405e3a27f6cf4c0ff95` | Frozen V3 Summary Manifest |
| `POLARIS_23_HORIZON_OFAT_EXPERIMENT_SPECIFICATION.md` | `53e5f0b482526167d157257690bd45c3dfb76bb1c8ef15c0a5384eb311f5d085` | Frozen MD Specification |
| `POLARIS_23_HORIZON_OFAT_EXPERIMENT_SPECIFICATION.json` | `21703425eb572b2698cb13bcfb835419460823d55a4e1d8fbac11e529d445a23` | Frozen JSON Specification |
| `POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.md` | `35cb77160cce59d8b8ee2323c2ff6ffe23e92f04f812ba6858f6b61c754f4109` | Historical Pre-Execution Authorization MD |
| `POLARIS_23_HORIZON_OFAT_EXECUTION_AUTHORIZATION.json` | `3d973f65ed187854550fb93cb8d2a184bc0134664ae442a9fa7a073d92ec6961` | Historical Pre-Execution Authorization JSON |
| `run_polaris_23_horizon_ofat_experiment.py` | `943a7afce3eef51453e9f54354344fb53a18ab500465ca0699c112cc8befb424` | Repaired Governance Execution Harness |
| `system/optimization/implementations/milp.py` | `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` | Amended MILP Optimization Engine |
| `system/simulation/simulator.py` | `7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508` | Verified Digital Twin Simulator |
| `system/runtime/runner.py` | `605a479586777cbc81315effdf0571e52be8e0a393661c0367c7b9ef3c55c58c` | Verified Runtime Engine |
| `system/forecasting/implementations/s81_solar.py` | `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` | Verified Solar Forecast Engine |
| `system/schemas/forecast_bundle.py` | `899aaa48272fd44691cef4b32939adb931a837c99203db37edfc14a9bb2d2045` | Verified Forecast Schema |
| `system/schemas/station_state.py` | `b6e78e8292bbba407f0af0a56100024cca4831dfb80d138afb1fb38008532d1c` | Verified Station State Schema |
| `system/schemas/dispatch_plan.py` | `cbf80578a0b4fa289e26b509eeb4d672124a2dad8a77855a42a50ca267349a17` | Verified Dispatch Plan Schema |

---

## 7. Execution Directive

Execution of the 95,496 MILP solves under the amended governance authorization is formally unlocked upon invocation of:

```bash
python3 run_polaris_23_horizon_ofat_experiment.py --authorize-execution
```
