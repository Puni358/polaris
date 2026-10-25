# RECOVERY BOUNDARY

## System Recovery Specification

This document defines the architectural boundary for transitioning the system back from **Option D Fallback** to **Normal Dispatch**.

---

## Current Recovery Status

```text
RECOVERY_POLICY_STATUS = UNRESOLVED_GOVERNANCE_DEPENDENCY
AUTOMATIC_RECOVERY = NOT_AUTHORIZED
```

---

## Pre-GAP19 Recovery Interface

To prevent premature automatic switching back to Normal mode during transient resource spikes, pre-GAP19 code enforces the following recovery interface:

1. **Condition Resolution Evaluation**:
   - System resource survivability $T_{\text{surv}}$ must exceed $T_{\text{required}} = 6.0\text{h}$ plus a governed recovery margin $\Delta T_{\text{margin}}$ for $N_{\text{stable}}$ consecutive solver steps.
2. **Explicit Operator Clearance Interface**:
   - Until a formal automated recovery policy is sealed by human governance, returning to `OperatingMode.NORMAL` requires explicit operator clearance (`operator_recovery_ack = True`).
3. **Pre-GAP19 Implementation Behavior**:
   - In synthetic tests, recovery is tested by injecting synthetic clearance flags into the test harness to verify mode transition correctness.
