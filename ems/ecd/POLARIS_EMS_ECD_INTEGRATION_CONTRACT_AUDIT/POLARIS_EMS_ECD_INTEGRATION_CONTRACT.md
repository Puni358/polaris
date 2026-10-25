# POLARIS EMS — ECD INTEGRATION CONTRACT

## 1. Executive Summary & Purpose

This document establishes the official **ECD Integration Contract** for POLARIS EMS. It specifies the exact architectural integration mechanisms required to connect the verified isolated Emergency Condition Detector (ECD) into the receding horizon MPC pipeline without altering existing system behavior during normal operations.

---

## 2. Integrated Control Pipeline Call-Flow

```
Telemetry / SCADA Input
          │
          ▼
   StationState(t_k)
          │
          ▼
   ForecastEngine.predict() ──► ForecastBundle(24h)
          │
          ▼
   Integration Adapter ────────► CriticalLoadTrajectory
          │
          ▼
┌────────────────────────────────────────────────────────┐
│        Emergency Condition Detector (ECD)              │
│                                                        │
│  Inputs:                                               │
│    - StationState (SOC, Fuel)                          │
│    - CriticalLoadTrajectory (Critical Demand)          │
│    - AuthorizedHorizon (T_required Payload)           │
│    - Battery & Diesel Equipment Parameters             │
│                                                        │
│  Output:                                               │
│    - EmergencyAssessment (Mode, Margins, E3 Policy)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
            EMS Mode Manager / Policy Layer
                           │
      ┌────────────────────┴────────────────────┐
      ▼                                         ▼
[NORMAL MODE]                           [EMERGENCY MODE]
Standard Cost Optimization              E3 Resource Preservation
(EnergyOptimizer / MILP)               (Preserved Resource Policy)
      │                                         │
      └────────────────────┬────────────────────┘
                           │
                           ▼
                      DispatchPlan
                           │
                           ▼
             DigitalTwinSimulator.step()
```

---

## 3. Mandatory Firewall Statements

1. **NO Production Code Alterations**: Zero production files (`system/runtime/runner.py`, `system/optimization/implementations/milp.py`, `system/schemas/`) were modified during this audit.
2. **NO MILP / Optimizer Changes**: The ECD core remains completely isolated from the solver and MILP matrix generation.
3. **NO Unresolved Deployment Decisions**: Deployment decisions DEC-001 (TTL), DEC-002 (Max-Age), and DEC-003 (Upstream Crypto) remain flagged as site deployment configuration dependencies.

---

## 4. Contract Status

- **`ECD_INTEGRATION_CONTRACT_STATUS`**: `CONTRACT_READY_FOR_IMPLEMENTATION_AUTHORIZATION`

Status: `AUDIT_COMPLETE`
