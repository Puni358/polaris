# POLARIS 23-Horizon OFAT Experiment Specification & Execution Gate
## Formal Governance & Scientific Protocol Specification
## SPECIFICATION COMPLETE — EXECUTION LOCKED PENDING EXPLICIT AUTHORIZATION

```yaml
GOVERNANCE_STATUS: SPECIFICATION_COMPLETE_EXECUTION_LOCKED
CANDIDATE_ID: POLARIS_23_HORIZON_OFAT_EXPERIMENT
CLASSIFICATION: A — SPECIFICATION COMPLETE (EXECUTION NOT AUTHORIZED)
EXECUTION_GATE: EXECUTION NOT AUTHORIZED — REQUIRES SEPARATE APPROVAL
EXECUTION_STATUS: NOT_AUTHORIZED
EXPERIMENT_PURPOSE: Determine downstream EMS effect of individually restoring genuine horizon weights (w_j = 1.0) from V3 Stage 8.1 objective
CONTROL_ARM: V3 Stage 8.1 (w_t = 0.95^t, t=0..23) — Frozen Audited Evidence Reused (No rerun of V3)
TREATMENT_ARMS: j = 1..23 (23 independent treatment arms)
EXCLUDED_ARM: j = 0 analytically recorded as Delta_0 = 0.0 (w_0 = 1.0 is identical to V3)
EXPERIMENTAL_UNIT: 173 frozen forecast origins, 24 sequential MPC cycles per origin
TOTAL_TREATMENT_SOLVES: 23 * 173 * 24 = 95,496 fresh exact MILP solves
SOLVE_SEMANTICS: Fresh exact MILP solve per cycle. No warm starts, approximations, skipped cycles, or tuning.
SAFE_OPTIMIZATIONS:
  - Model structure precomputation per (origin, MPC step)
  - Parallelization across independent origins/arms
  - Complete independent state trajectory isolation
RESOURCE_CONFIGURATION:
  MAX_WORKERS: 8
THERMAL_GOVERNANCE:
  TARGET_OPERATING_TEMPERATURE: DO NOT DEFINE 100C TARGET OPERATING TEMPERATURE
  MONITORING: Continuous manual/system thermal monitoring required
  HALT_RULE: Manually halt execution if temperature approaches machine limits or thermal instability occurs
  SEMANTIC_INVARIANT: Do not alter scientific semantics, origin count, or cycle limits for thermal constraints
TELEMETRY: Preserve 37-field V2/V3 observational schema. Logging must not be weakened.
STATISTICAL_PLAN:
  DESIGN: Paired 173-origin treatment-vs-V3 comparisons (N=173)
  PRIMARY_MULTIPLICITY_METHOD: HOLM_BONFERRONI
  FAMILY_WISE_ALPHA: 0.05
  NUMBER_OF_HORIZON_TESTS: 23
  BH_FDR_CONFIRMATORY_STATUS: NOT_USED
  PRIMARY_CONFIRMATORY_PROCEDURE: Holm-Bonferroni step-down control of family-wise error rate at alpha = 0.05 across 23 horizon tests.
  SECONDARY_EXPLORATORY_PROCEDURE: Benjamini-Hochberg FDR (q=0.05) retained strictly for secondary/exploratory descriptive analysis with NO bearing on the primary confirmatory conclusion.
  HORIZON_SELECTION: Predeclared. No result-dependent horizon selection.
CODE_EXECUTION: ZERO CODE EXECUTED DURING THIS TASK
```

---

## 1. Executive Summary & Scientific Purpose

This document establishes the formal, immutable **Experiment Specification & Execution Gate** for the **23-Horizon One-Factor-At-A-Time (OFAT) Experiment** in the POLARIS Energy Management System (EMS).

### Scientific Purpose
In V3 Stage 8.1, the objective function applied an exponential discount sequence $w_t = 0.95^t$ across all decision timesteps $t \in [0, 23]$. To isolate the downstream EMS sensitivity and marginal value of individual forecast horizons, this OFAT experiment systematically restores **one genuine horizon weight at a time** to full value ($w_j = 1.0$), while leaving all other timesteps at their baseline V3 discounted values ($w_t = 0.95^t$ for $t \neq j$).

### Key Invariants:
1. **Computational Basis**: Built on the completed computational tractability investigation. Optimization search is closed.
2. **Frozen Control**: The audited V3 execution artifact (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`) is reused as the shared control arm across all paired origin comparisons. V3 is **not rerun**.
3. **Execution Gate**: This task produces **only** the formal governance and specification package. **ZERO code was executed**, zero MILP solves were performed, and execution remains **LOCKED** until separate explicit authorization is granted.

---

## 2. Exact Arm Inventory

The experiment comprises **1 Control Arm** (frozen V3 baseline) and **23 Treatment Arms** ($j = 1 \dots 23$).

> [!IMPORTANT]
> **Analytical Exclusion of $j=0$**: For timestep $t=0$, $0.95^0 = 1.0$. Consequently, restoring $w_0 = 1.0$ yields a weight sequence identical to V3 ($w_t = 0.95^t$). Executing treatment $j=0$ would be redundant. Treatment $j=0$ is analytically excluded, and its effect is recorded pre-execution as $\Delta_0 = 0.0$ liters fuel difference by mathematical identity.

### Complete Arm Specification Matrix:

| Arm ID | Treatment $j$ | Target Step $t$ | Horizon $h$ | Weight Sequence Specification | Status / Execution Mode | Expected MILP Solves |
|---|---|---|---|---|---|---|
| `ARM_00_CONTROL` | $j=0$ (Control) | $t=0\dots 23$ | $h=1\dots 24$ | $w_t = 0.95^t$ for all $t \in [0, 23]$ | Shared Control (Reused V3 Artifact) | 0 (Reused) |
| `ARM_01_TREATMENT` | $j=1$ | $t=1$ | $h=2$ | $w_1 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 1)$ | Treatment Arm 1 | 4,152 |
| `ARM_02_TREATMENT` | $j=2$ | $t=2$ | $h=3$ | $w_2 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 2)$ | Treatment Arm 2 | 4,152 |
| `ARM_03_TREATMENT` | $j=3$ | $t=3$ | $h=4$ | $w_3 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 3)$ | Treatment Arm 3 | 4,152 |
| `ARM_04_TREATMENT` | $j=4$ | $t=4$ | $h=5$ | $w_4 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 4)$ | Treatment Arm 4 | 4,152 |
| `ARM_05_TREATMENT` | $j=5$ | $t=5$ | $h=6$ | $w_5 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 5)$ | Treatment Arm 5 | 4,152 |
| `ARM_06_TREATMENT` | $j=6$ | $t=6$ | $h=7$ | $w_6 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 6)$ | Treatment Arm 6 | 4,152 |
| `ARM_07_TREATMENT` | $j=7$ | $t=7$ | $h=8$ | $w_7 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 7)$ | Treatment Arm 7 | 4,152 |
| `ARM_08_TREATMENT` | $j=8$ | $t=8$ | $h=9$ | $w_8 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 8)$ | Treatment Arm 8 | 4,152 |
| `ARM_09_TREATMENT` | $j=9$ | $t=9$ | $h=10$ | $w_9 = 1.0$, $w_t = 0.95^t \; (\forall t \neq 9)$ | Treatment Arm 9 | 4,152 |
| `ARM_10_TREATMENT` | $j=10$ | $t=10$ | $h=11$ | $w_{10} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 10)$ | Treatment Arm 10 | 4,152 |
| `ARM_11_TREATMENT` | $j=11$ | $t=11$ | $h=12$ | $w_{11} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 11)$ | Treatment Arm 11 | 4,152 |
| `ARM_12_TREATMENT` | $j=12$ | $t=12$ | $h=13$ | $w_{12} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 12)$ | Treatment Arm 12 | 4,152 |
| `ARM_13_TREATMENT` | $j=13$ | $t=13$ | $h=14$ | $w_{13} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 13)$ | Treatment Arm 13 | 4,152 |
| `ARM_14_TREATMENT` | $j=14$ | $t=14$ | $h=15$ | $w_{14} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 14)$ | Treatment Arm 14 | 4,152 |
| `ARM_15_TREATMENT` | $j=15$ | $t=15$ | $h=16$ | $w_{15} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 15)$ | Treatment Arm 15 | 4,152 |
| `ARM_16_TREATMENT` | $j=16$ | $t=16$ | $h=17$ | $w_{16} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 16)$ | Treatment Arm 16 | 4,152 |
| `ARM_17_TREATMENT` | $j=17$ | $t=17$ | $h=18$ | $w_{17} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 17)$ | Treatment Arm 17 | 4,152 |
| `ARM_18_TREATMENT` | $j=18$ | $t=18$ | $h=19$ | $w_{18} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 18)$ | Treatment Arm 18 | 4,152 |
| `ARM_19_TREATMENT` | $j=19$ | $t=19$ | $h=20$ | $w_{19} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 19)$ | Treatment Arm 19 | 4,152 |
| `ARM_20_TREATMENT` | $j=20$ | $t=20$ | $h=21$ | $w_{20} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 20)$ | Treatment Arm 20 | 4,152 |
| `ARM_21_TREATMENT` | $j=21$ | $t=21$ | $h=22$ | $w_{21} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 21)$ | Treatment Arm 21 | 4,152 |
| `ARM_22_TREATMENT` | $j=22$ | $t=22$ | $h=23$ | $w_{22} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 22)$ | Treatment Arm 22 | 4,152 |
| `ARM_23_TREATMENT` | $j=23$ | $t=23$ | $h=24$ | $w_{23} = 1.0$, $w_t = 0.95^t \; (\forall t \neq 23)$ | Treatment Arm 23 | 4,152 |

---

## 3. Solve-Count Accounting & MPC Rollout Mechanics

### Experimental Unit Structure:
- **Population**: 173 frozen forecast origins (`POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`).
- **Sequential MPC Horizon**: 24 decision cycles per origin ($k = 0 \dots 23$).
- **State Propagation**: Each treatment arm maintains its own independent state trajectory ($S_{k+1} = f(S_k, \mathbf{u}_k, \mathbf{y}_{k,\text{actual}})$).

### Solve Accounting Equation:
$$\text{Total Treatment MILP Solves} = 23 \text{ treatment arms} \times 173 \text{ origins} \times 24 \text{ MPC steps} = 95,496$$

```
+-------------------------------------------------------------------------+
|                              SOLVE ACCOUNTING                           |
+------------------------------------+------------------------------------+
| Parameter                          | Value                              |
+------------------------------------+------------------------------------+
| Frozen Control Arm (V3 Stage8.1)   | Reused Artifact (0 new solves)     |
| Executed Treatment Arms            | 23 arms (j = 1..23)                |
| Origins per Treatment Arm          | 173 origins                        |
| MPC Steps per Origin               | 24 sequential cycles               |
| Solves per Treatment Arm           | 4,152 MILP solves                  |
| Total New Treatment Solves         | 95,496 MILP solves                 |
| Optimization Precision             | Fresh exact MILP solve per cycle   |
| Warm starts / Approximations       | PROHIBITED                         |
| Skipped cycles / Reduced origins   | PROHIBITED                         |
+------------------------------------+------------------------------------+
```

---

## 4. Safe Computational Optimizations

To ensure computational efficiency without altering scientific semantics, three safe optimizations are pre-approved:

1. **Model Precomputation Structure**: Constraint matrix structure and variable bounds per (origin, MPC step) are precomputed once where mathematically identical across treatment arms. Only the objective cost vector $\mathbf{c}$ is mutated with the arm-specific weight sequence $w^{(j)}$.
2. **Parallel Worker Dispatch**: Independent origins and treatment arms are parallelized across process workers using worker-isolated memory spaces.
3. **State Trajectory Isolation**: State trajectories for each treatment arm are computed independently and stored in isolated memory data structures to guarantee zero cross-arm state contamination.

---

## 5. Resource Configuration & Execution Settings

```yaml
RESOURCE_SETTINGS:
  MAX_WORKERS: 8
  WORKER_PARALLELISM: Multiprocessing ProcessPoolExecutor
  ORIGIN_BATCHING: Dynamic process queue per origin/arm pair
  MEMORY_ISOLATION: Strict per-worker process boundary
```

- **Worker Constraint**: `MAX_WORKERS = 8` is strictly set as the ceiling for concurrent execution.
- **Process Isolation**: Each worker runs an independent python process, preventing global state leak or GIL contention.

---

## 6. Thermal Governance Protocol

> [!CAUTION]
> **THERMAL SAFETY DIRECTIVE**: Do NOT define 100°C as a target operating temperature. Operating near thermal breakdown invalidates physical hardware stability and risks unrecoverable hardware throttling or failure.

### Governance Rules:
1. **Target Operating Temperature Policy**: 100°C is explicitly rejected as a operational target. Operating temperatures must remain well below hardware thermal limits.
2. **Continuous Monitoring Requirement**: Execution must be continuously monitored via active CPU sensor sampling.
3. **Thermal-Stop Rule**: If system temperatures approach machine thermal thresholds or thermal instability occurs, **the operator or monitoring supervisor must manually halt execution immediately**.
4. **Scientific Invariant**: Thermal conditions must **NEVER** be mitigated by altering scientific logic (e.g., reducing origin count, skipping MPC steps, relaxing solver tolerances, or shortening horizon lengths).

---

## 7. Required Telemetry & Data Preservation

Telemetry logging standards from Stage 8.1 V2/V3 are strictly preserved.

### Observational Schema (37 Fields):
- Timestep & Origin Metadata (`origin_id`, `mpc_step`, `timestamp`)
- Objective Costs (`fuel_cost`, `startup_cost`, `curtailment_cost`, `degradation_cost`)
- Generator & Battery States (`generator_status`, `p_diesel_kw`, `soc_fraction`, `p_chg_kw`, `p_dis_kw`)
- Renewable Dispatch (`pv_available_kw`, `pv_dispatched_kw`, `wind_available_kw`, `wind_dispatched_kw`)
- Telemetry Row Count: Exactly 95,496 treatment telemetry records must be written to CSV/JSON output upon execution.
- **Logging Integrity**: Logging level and field completeness must **not** be reduced or suppressed to save runtime.

---

## 8. Statistical & Multiple-Testing Plan

### Paired Origin Design:
- **Sample Size**: $N = 173$ origins.
- **Pairing Structure**: Origin $i$ of Treatment Arm $j$ is directly paired with Origin $i$ of the frozen V3 Control.
- **Primary Endpoint**: Total diesel fuel consumption (liters) over the 24-hour origin simulation window ($\text{Fuel}_{i, j} - \text{Fuel}_{i, \text{V3}}$).
- **Secondary Endpoints**:
  1. Battery Throughput ($\text{Wh}$)
  2. Renewable Curtailment ($\text{Wh}$)
  3. Generator Startup Events (Count)
  4. Unmet Load ($\text{Wh}$)

### Multiple-Testing Correction Protocol:
Because 23 simultaneous hypothesis tests are conducted ($H_{0, j}: \mu_{\text{treatment } j} = \mu_{\text{V3}}$ for $j = 1 \dots 23$), multiple testing procedures are strictly governed:

1. **Sole Primary Confirmatory Procedure**:
   - **Holm-Bonferroni Step-Down Procedure**: `PRIMARY_MULTIPLICITY_METHOD = HOLM_BONFERRONI`. $p$-values from the 23 paired comparisons (`NUMBER_OF_HORIZON_TESTS = 23`) are ordered $p_{(1)} \le p_{(2)} \le \dots \le p_{(23)}$. Step $k$ evaluates against threshold $\alpha / (23 - k + 1)$ with overall Family-Wise Error Rate `FAMILY_WISE_ALPHA = 0.05`.
   - **Bonferroni Single-Step Benchmark**: Adjusted per-test significance threshold $\alpha_{\text{adj}} = \frac{0.05}{23} \approx 0.0021739$.

2. **Secondary / Exploratory Descriptive Analysis Only**:
   - **Benjamini-Hochberg Procedure**: `BH_FDR_CONFIRMATORY_STATUS = NOT_USED`. Benjamini-Hochberg FDR ($q = 0.05$) is **NOT** used as a confirmatory decision rule and has no bearing on the primary confirmatory conclusion. If presented at all, it is retained strictly for secondary/exploratory descriptive reporting.

3. **Pre-registered Exclusion**:
   - Arm $j=0$ is analytically assigned $\Delta_0 = 0.0, p_0 = 1.0$ and is excluded from the 23-test multiplicity penalty.

4. **Non-Selection Invariant**:
   - No post-hoc selection of horizons based on observed effect size. All 23 comparisons are reported in full.

---

## 9. Protected Input & Artifact SHA256 Hashes

All core codebase components, schemas, engines, and historical control artifacts have been verified and locked:

| Protected File / Artifact Path | Verified SHA256 Hash | Provenance & Status |
|---|---|---|
| `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv` | `b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c` | Frozen Stage 8.1 Forecast Index |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` | `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e` | Frozen V3 Control Execution Raw Evidence |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION.json` | `5c84d72bc13d52d9b1580ca02b66a5e1281db2bd1be97405e3a27f6cf4c0ff95` | Frozen V3 Execution Summary Manifest |
| `POLARIS_STAGE8_1_EMS_V3_EXECUTION.md` | `b348f98ec448d37e69f8c05e197c36ca2cfdf5137df776fa2e7d77b817e948c3` | Frozen V3 Execution Governance Report |
| `system/optimization/implementations/milp.py` | `e2a05fbdfedcd89574d71587d65b4c1069ebbd18cfcb9bcf51bfef252f4c9bf6` | Verified MILP Formulation Engine |
| `system/simulation/simulator.py` | `aa7668697b0932bb821b016f4d221cd88bb82d36fb56358c2be6ce8806296cc7` | Verified Digital Twin Simulator |
| `system/runtime/runner.py` | `4f32fb0f9aef7c11f74fa18cbf5e7ffecdf61681b4efb489bb2dfabf972b220e` | Verified Execution Runner |
| `system/forecasting/implementations/s81_solar.py` | `b99e746a51d95bf085c88cbb5f154563a6f1d171e544ae5d01fbffbbbe834167` | Verified Stage 8.1 Forecast Engine |
| `system/schemas/forecast_bundle.py` | `090b8f44ff5ae7a8c3d9a16fbdadcd7acae6e511487ea0b7fb5ca8fa7b78972d` | Verified Forecast Bundle Schema |
| `system/schemas/station_state.py` | `ffcd75b6aedbf12d4d98d28a3f8fa3ddf7a14e9185a767431bf3bb79a835b3ec` | Verified Station State Schema |
| `system/schemas/dispatch_plan.py` | `d76dbdcf1b3fb457385906f3458db9ebddbc8e0fdb291079d8efd4df6a83a005` | Verified Dispatch Plan Schema |

---

## 10. Execution Gate Declaration

> [!WARNING]
> **EXPLICIT EXECUTION GATE**:
> - Specification Status: **COMPLETE AND EXECUTION-READY**
> - Execution Status: **NOT_AUTHORIZED — LOCKED PENDING SEPARATE EXPLICIT APPROVAL**
> - Code Execution: **ZERO CODE EXECUTED**
>
> Execution requires a separate, explicit governance authorization command. No trial runs, smoke tests, or partial origin replays were performed or authorized during this specification step.
