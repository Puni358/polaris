# FAILURE MODE AUDIT

## Programmatic Failure Classification & Separation

This document establishes the programmatic failure classification isolating solver failures from runtime system states.

---

## Failure Domain Classification Matrix

| Failure Category | Trigger Condition | System Response & Classification | Handled By |
| :--- | :--- | :--- | :--- |
| **`SOLVER_FAILURE`** | Solver internal exception, memory error, or C++ runtime crash. | Raises `RuntimeError("OPTIMIZATION_RUNTIME_FAILURE")`. | `LocalMILPEnergyOptimizer` error block |
| **`MODEL_INFEASIBILITY`** | Feasible region $\mathcal{F}_0$ is empty ($A x \le b$ infeasible). | Returns zero-dispatch degraded `DispatchPlan` with `constraint_status = "OPTIMIZATION_INFEASIBLE"`. | Optimizer status handler |
| **`ECD_UNKNOWN_INVALID`** | Telemetry inputs invalid, missing, stale, or unauthorized. | Routes system to `OperatingMode.UNKNOWN_INVALID` and safe-state dispatch. | `EnergyCrisisDetector` & runner |
| **`MPC_FAILURE`** | Receding horizon simulation step failure. | Triggered if Digital Twin step execution fails ground truth checks. | Digital Twin simulator |

---

## Technical Finding

`SOLVER_FAILURE` and `MODEL_INFEASIBILITY` are solver-level outcomes handled strictly inside `LocalMILPEnergyOptimizer`. They are distinct from telemetry-level `ECD_UNKNOWN_INVALID` routing.
