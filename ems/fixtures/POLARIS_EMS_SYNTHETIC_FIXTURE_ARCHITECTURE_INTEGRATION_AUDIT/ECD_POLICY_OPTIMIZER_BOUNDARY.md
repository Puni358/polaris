# ECD POLICY OPTIMIZER BOUNDARY AUDIT

## 1. INTENDED OPERATIONAL SEQUENCE
The governed control architecture specifies the following sequential execution boundary:

```text
[1. StationState & Horizon Input]
               │
               ▼
[2. Emergency Condition Detector (ECD)]
               │
               ▼  (EmergencyAssessment: NORMAL / EMERGENCY / UNKNOWN_INVALID)
[3. Operating Mode & Policy Router]
               │
               ▼  (Option D Policy Constraints / Mode Directives)
[4. EnergyOptimizer / MILP]
               │
               ▼  (Optimal Dispatch Schedule)
[5. DispatchPlan]
```

---

## 2. RUNTIME WIRING GAP ASSESSMENT
The audit checked actual code implementations against this intended sequence:

| Integration Gate | Intended Status | Current Code Implementation Status | Code Evidence | Missing Artifact / Action |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1: ECD Execution** | Execute ECD at each MPC step | `MISSING_RUNTIME_WIRING` | `runner.py` does not call `ECD.evaluate()` | Add ECD call in `runner.py` |
| **Gate 2: ECD → Policy Router**| Route `EmergencyAssessment` to Policy | `MISSING_COMPONENT` | No policy router class exists in `system/control/` | Create Policy Router component |
| **Gate 3: Policy → Optimizer** | Apply Option D constraints to MILP | `MISSING_INTERFACE` | `LocalMILPEnergyOptimizer` signature rejects policy inputs | Extend optimizer signature & formulation |
| **Gate 4: Dispatch Registration**| Record ECD state in `DispatchPlan` | `MISSING_SCHEMA` | `DispatchPlan` does not store `operating_mode` | Add optional metadata field |

---

## 3. SUMMARY
- **`ECD_POLICY_OPTIMIZER_BOUNDARY_STATUS = MISSING_RUNTIME_WIRING`**
- All components must be wired sequentially before a controlled runtime test can be executed.
