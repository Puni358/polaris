# POLARIS EMS — ECD ARCHITECTURAL PLACEMENT AUDIT

## 1. Executive Summary

This document establishes the precise architectural placement and system boundaries for the Emergency Condition Detector (ECD) within the POLARIS Energy Management System (EMS).

---

## 2. Conceptual Data Flow & Execution Pipeline

The canonical control pipeline sequence for POLARIS EMS is defined as follows:

```
Telemetry / Sensor Data
          │
          ▼
   StationState
          │
          ▼
   ForecastEngine ──► ForecastBundle (Demand, Solar, Pricing, Critical Demand)
          │
          ▼
┌────────────────────────────────────────────────────────┐
│        Emergency Condition Detector (ECD)              │
│                                                        │
│  Inputs:                                               │
│    - StationState (SOC, Fuel)                          │
│    - ForecastBundle (Critical Load Trajectory)        │
│    - T_required (Authenticated Operational Input)       │
│    - Equipment Configuration (Battery, Generator)      │
│                                                        │
│  Output:                                               │
│    - EmergencyAssessment (Mode, Margins, E3 Policy)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
                 EMS / MPC Controller
                           │
      ┌────────────────────┴────────────────────┐
      ▼                                         ▼
[NORMAL MODE]                           [EMERGENCY MODE]
Standard Cost Minimization              E3 Resource Preservation Policy
(EnergyOptimizer / MILP)               (Objective/Constraint Adaptations)
      │                                         │
      └────────────────────┬────────────────────┘
                           │
                           ▼
                      DispatchPlan
                           │
                           ▼
                  Actuators / Simulator
```

---

## 3. Strict Layer Separation & Boundaries

### 3.1 Detector vs. Controller Boundary
- **ECD Responsibility**: Pure state evaluation and classification (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`), margin calculations ($T_{\text{battery}}$, $T_{\text{diesel}}$, $M_{\text{battery}}$, $M_{\text{diesel}}$), and E3 resource classification (`preserved_resource`, `limiting_resource`).
- **ECD Prohibition**: The ECD **MUST NOT** select dispatch targets, schedule generator startups, shed loads, alter battery setpoints, or modify optimizer objectives.

### 3.2 Detector vs. Optimizer Boundary
- **No MILP Access**: The ECD runs **BEFORE** the MILP optimizer (`EnergyOptimizer`).
- **No Coefficient Manipulation**: The ECD **MUST NOT** modify cost parameters, penalty factors, or constraint bounds inside the MILP model directly.
- **Upstream Feeding**: The EMS/MPC controller receives the `EmergencyAssessment` from the ECD and configures the `EnergyOptimizer` mode accordingly.

---

## 4. Architectural Placement Decision

**ESTABLISHED PLACEMENT**: 
The ECD module belongs in `polaris.ems.ecd` as an independent evaluation service that executes at the start of each MPC control cycle after state estimation and forecasting, but prior to dispatch planning.

Status: `ESTABLISHED`
