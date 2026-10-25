# POLARIS EMS — OPTION D ARCHITECTURE COMPATIBILITY AUDIT

## 1. Executive Summary & Compatibility Verdict

This document presents the end-to-end pipeline trace and architectural placement audit for **Option D: Protected Critical-Load Fallback**.

### Architectural Compatibility Verdict:
```text
COMPATIBILITY_VERDICT = ARCHITECTURALLY_COMPATIBLE_WITH_ADDITIVE_CHANGES
```
Option D fits naturally into the established POLARIS EMS control pipeline without altering the fundamental responsibilities of ECD, MPC, MILP, or DigitalTwinSimulator. Implementation requires specific additive schema and runner policy router additions.

---

## 2. End-to-End Control Pipeline Trace

The diagram below maps the exact data flow and architectural placement of Option D across the POLARIS pipeline:

```text
 ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
 │  StationState  │ ──► │ ForecastEngine │ ──► │ ForecastBundle │
 └────────────────┘     └────────────────┘     └───────┬────────┘
                                                       │
                                                       ▼
                                          ┌──────────────────────────┐
                                          │ CriticalLoadTrajectory   │
                                          └────────────┬─────────────┘
                                                       │
                                                       ▼
 ┌────────────────┐     ┌────────────────┐     ┌──────────────────────────┐
 │ Emergency-     │ ◄── │   ECD Core     │ ◄── │  Integration Adapter     │
 │ Assessment     │     │   Evaluator    │     └──────────────────────────┘
 └───────┬────────┘     └────────────────┘
         │ (mode = UNKNOWN_INVALID)
         ▼
 ┌──────────────────────────────────────────────────────────────────────┐
 │                  EMS Mode Manager / Policy Layer                     │
 │  - Identifies UNKNOWN_INVALID state                                  │
 │  - Applies Option D Policy: Suppresses noncritical loads            │
 │  - Restricts MILP load demand to P_critical(t)                       │
 │  - Authorizes diesel/battery fallback rules (D2/D3/D6)               │
 └──────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
 ┌────────────────┐     ┌────────────────┐     ┌──────────────────────────┐
 │  DispatchPlan  │ ◄── │ LocalMILP-     │ ◄── │ Model Predictive Control │
 │  (Metadata)    │     │ EnergyOptimizer│     │ (MPC Horizon Loop)       │
 └───────┬────────┘     └────────────────┘     └──────────────────────────┘
         │
         ▼
 ┌────────────────┐
 │  DigitalTwin-  │ (Advances simulator state via renewable + diesel + battery power
 │  Simulator     │  applied to critical load ONLY)
 └────────────────┘
```

---

## 3. ECD Responsibility Boundary Verification

The architectural audit confirmed strict compliance with the ECD separation boundary:

1. **ECD Core Evaluator (`system/control/ecd.py`)**:
   - Evaluates resource survivability against $T_{\text{required}}$.
   - Emits `EmergencyAssessment(mode=UNKNOWN_INVALID, validity_status=...)`.
   - *Boundary Verification*: ECD contains **ZERO** dispatch logic, **ZERO** load shedding logic, and **ZERO** solver code. It acts strictly as a read-only state classifier.
2. **EMS Mode Manager / Policy Layer**:
   - Consumes `EmergencyAssessment`. When `mode == UNKNOWN_INVALID`, engages Option D fallback policy.
   - Configures `ForecastBundle` / load parameters passed to `LocalMILPEnergyOptimizer` (restricting demand to $P_{\text{critical}}(t)$ and zeroing noncritical load).
   - Coordinates SCADA alerts and operator escalation pathways.
3. **EnergyOptimizer / MILP (`system/optimization/implementations/milp.py`)**:
   - Solves receding-horizon power allocation subject to policy constraints configured by Mode Manager.

---

## 4. Enumeration of Exact Additive Changes Required

To achieve full production execution of Option D, the following additive components are required:

1. **Additive Schema Extensions**:
   - Add `protected_critical_load_w: Optional[float]` and `shed_noncritical_load_w: Optional[float]` to `DispatchPlan` metadata.
   - Add `critical_demand_w: List[float]` trajectory vector to `ForecastBundle`.
2. **Additive Policy Router Module**:
   - Implement an `OptionDPolicyRouter` inside `system/runtime/runner.py` to intercept `UNKNOWN_INVALID` and configure degraded optimization inputs.
3. **Additive Critical Load Trajectory Adapter**:
   - Implement a trajectory adapter supplying $P_{\text{critical}}(t)$ from station configuration or ambient temperature models.

Status: `ARCHITECTURE_COMPATIBILITY_SEALED`
