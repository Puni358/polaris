# POLARIS EMS — UNKNOWN_INVALID DOWNSTREAM BEHAVIOR FORENSIC REPORT

## 1. Executive Summary

This report delivers the narrowly scoped **Forensic Verification** of downstream handling for the `UNKNOWN_INVALID` state emitted by the Emergency Condition Detector (ECD).

The objective is to verify whether existing repository code and frozen contracts actually establish the claim:
> *"UNKNOWN_INVALID $\implies$ governed FaultEvent + conservative safe state"*

### Key Forensic Findings:
1. **`UNKNOWN_INVALID` State**: **ESTABLISHED** in `system/control/ecd.py` as an explicit enum value of `OperatingMode`.
2. **`FaultEvent` Structure**: **ESTABLISHED** in `system/runtime/runner.py` (`class FaultEvent`).
3. **`GOVERNED_FAIL_CLOSED` Severity**: **NOT ESTABLISHED IN CODE** (runner.py uses `CRITICAL_TERMINATION` or `GOVERNED_DEGRADED`; `GOVERNED_FAIL_CLOSED` was proposed in the integration contract text).
4. **"Conservative Safe State" Operational Action**: **NOT ESTABLISHED** (No specific dispatch action, e.g. hold last plan vs zero dispatch, is defined for ECD invalid state in code or policy).
5. **Downstream Consumer**: **NOT IMPLEMENTED IN CODE** (No integration adapter or EMS Mode Manager is wired into `runner.py`).
6. **Summary Overstatement**: **VERIFIED**. The previous summary statement presented downstream fail-closed handling as fully established, whereas the operational action remains `UNRESOLVED_DOWNSTREAM_POLICY`.

---

## 2. Forensic Evidence Mapping Across Questions 1–6

### Question 1: Is `UNKNOWN_INVALID` defined as an ECD output state?
- **Evidence**: `system/control/ecd.py` line 18 (`OperatingMode.UNKNOWN_INVALID`). Emitted when horizon or telemetry inputs are missing, invalid, expired, or unauthorized.
- **Verdict**: `ESTABLISHED`

### Question 2: Does `FaultEvent` exist in code?
- **Evidence**: `system/runtime/runner.py` line 19 (`class FaultEvent`). Used during pipeline execution failures.
- **Verdict**: `ESTABLISHED`

### Question 3: Is `GOVERNED_FAIL_CLOSED` established in code?
- **Evidence**: `GOVERNED_FAIL_CLOSED` appears ONLY in `POLARIS_EMS_ECD_INTEGRATION_CONTRACT_AUDIT/POLARIS_EMS_ECD_UNKNOWN_INVALID_HANDLING.md`. Does not exist in Python source code.
- **Verdict**: `NOT_ESTABLISHED` (Proposed string label)

### Question 4: Is "conservative safe state" operationally defined?
- **Evidence**: `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` defines zero-dispatch for MILP infeasibility. No operational action is defined for ECD invalid input.
- **Verdict**: `NOT_ESTABLISHED`

### Question 5: Is the downstream consumer implemented?
- **Evidence**: `system/runtime/runner.py` contains no ECD handler.
- **Verdict**: `DOWNSTREAM_CONSUMER_NOT_IMPLEMENTED`

### Question 6: Is the actual resulting action established?
- **Evidence**: `POLARIS_EMS_ECD_UNKNOWN_INVALID_HANDLING.md` explicitly classifies handling as `UNRESOLVED_DOWNSTREAM_POLICY`.
- **Verdict**: `DOWNSTREAM_ACTION_NOT_ESTABLISHED`

---

## 7. Governance Status Register

```text
UNKNOWN_INVALID_STATE = ESTABLISHED
FAULT_EVENT = ESTABLISHED
GOVERNED_FAIL_CLOSED = NOT_ESTABLISHED
CONSERVATIVE_SAFE_STATE = NOT_ESTABLISHED
DOWNSTREAM_CONSUMER = NOT_ESTABLISHED
DOWNSTREAM_ACTION = NOT_ESTABLISHED
UNKNOWN_INVALID_DISTINCT_FROM_EMERGENCY = YES
FAULT_EVENT_CONTROL_EFFECT = ESTABLISHED
OVERSTATEMENT_FOUND = YES
CORRECTION_REQUIRED = YES
ECD_RUNTIME_INTEGRATION_BLOCKED = YES
ECD_MPC_INTEGRATION_BLOCKED = YES
ECD_OPTIMIZER_INTEGRATION_BLOCKED = NO
PRODUCTION_DEPLOYMENT_BLOCKED = YES
```

Status: `FORENSIC_VERIFICATION_COMPLETE`
