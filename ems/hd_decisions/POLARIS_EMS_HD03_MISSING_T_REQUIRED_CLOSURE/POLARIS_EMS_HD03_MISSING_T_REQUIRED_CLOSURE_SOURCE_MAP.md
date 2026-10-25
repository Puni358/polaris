# POLARIS EMS — HD-03 MISSING T_required FAIL-CLOSED SOURCE MAP

## 1. COMPONENT & FAULT INTERFACE MAP

The diagram below details the operational data flow and fail-closed fault signaling when no valid $T_{\text{required}}$ is available.

```
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│ DEPLOYMENT CONFIGURATION (OPTION C) │         │ AUTHORIZED OPERATIONAL INPUT (OPT A)│
└──────────────────┬──────────────────┘         └──────────────────┬──────────────────┘
                   │                                               │
                   │ payload (configured)                          │ payload (operational)
                   v                                               v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 T_required RESOLVER                                 │
│                                                                                     │
│ Evaluates validity, freshness, and precedence rules.                                │
│ If no valid T_required can be produced:                                             │
│ Emits NULL / INVALID status payload (No numerical value passed).                    │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           │ INVALID / NULL T_required status
                                           v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            EMERGENCY CONDITION DETECTOR                             │
│                                                                                     │
│ Role: CONSUMER ONLY                                                                 │
│ Condition: Triggered by INVALID / NULL T_required status                             │
│ Behavior: FAILS CLOSED                                                              │
│ Output: NO_CLASSIFICATION (Zero NORMAL / EMERGENCY flag issued)                      │
│ Raises: Explicit ModelGovernanceError / Status Exception                            │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           │ Status = UNRESOLVED_SURVIVABILITY_FAULT
                                           v
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM FAULT / EMS HANDLER                                │
│                                                                                     │
│ Handles safety-critical status. Prevents ungrounded survivability claims.           │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. INTERFACE BOUNDARIES & RESPONSIBILITY SEPARATION

1. **Resolver Boundary**:
   - The resolver evaluates input availability and validity.
   - If invalid/missing, it passes an invalid status flag to the Emergency Condition Detector.
2. **Emergency Detector Boundary**:
   - Consumes the invalid status flag and immediately executes `FAIL_CLOSED`.
   - Strictly prohibited from emitting a fallback classification (`NORMAL` or `EMERGENCY`).
   - Strictly prohibited from deriving a substitute numerical horizon.
3. **Downstream System Handler Boundary**:
   - Operational microgrid actions (such as logging an error, raising an alarm, or safe-parking dispatch) belong to the downstream system fault handler, not the Emergency Detector.
