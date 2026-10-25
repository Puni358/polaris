# POLARIS EMS — UNKNOWN_INVALID EVIDENCE CORRECTION REPORT

## 1. Executive Summary

This correction report clarifies the exact evidentiary status of claims regarding downstream handling of the `UNKNOWN_INVALID` state. In strict compliance with forensic rules, **NO previously sealed audit artifacts have been modified or overwritten**.

---

## 2. Comparison of Claim vs. Empirical Evidence

### Original Summary Claim:
> *"UNKNOWN_INVALID $\implies$ governed FaultEvent + conservative safe state"*

### Forensic Re-Evaluation against Repository Evidence:

1. **`UNKNOWN_INVALID` State**:
   - **Claim**: `UNKNOWN_INVALID` is an established ECD output state.
   - **Actual Evidence**: **SUPPORTED**. `OperatingMode.UNKNOWN_INVALID` is a formal enum value in `system/control/ecd.py`.

2. **`FaultEvent` Structure**:
   - **Claim**: `FaultEvent` is the established diagnostic recording structure.
   - **Actual Evidence**: **SUPPORTED**. `class FaultEvent` is defined in `system/runtime/runner.py`.

3. **`GOVERNED_FAIL_CLOSED` Severity**:
   - **Claim**: `severity = "GOVERNED_FAIL_CLOSED"` is an established severity class.
   - **Actual Evidence**: **NOT SUPPORTED**. `runner.py` currently defines `CRITICAL_TERMINATION` and `GOVERNED_DEGRADED`. `GOVERNED_FAIL_CLOSED` was proposed in the integration contract audit markdown as a new label.

4. **"Conservative Safe State" Operational Action**:
   - **Claim**: "Conservative safe state" is an established operational response for ECD `UNKNOWN_INVALID`.
   - **Actual Evidence**: **NOT ESTABLISHED**. `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` defines zero-dispatch for MILP infeasibility (`GOVERNED_DEGRADED`), but no operational action (e.g. hold last plan vs zero dispatch) is currently defined in code or governance for ECD `UNKNOWN_INVALID`.

5. **Downstream Consumer**:
   - **Claim**: A downstream consumer is implemented in `runner.py`.
   - **Actual Evidence**: **NOT SUPPORTED**. No ECD integration adapter or `EMS Mode Manager` currently exists inside `system/runtime/runner.py`.

---

## 3. Corrected Classification & Implication

- **Corrected Classification**: `UNKNOWN_INVALID_BEHAVIOR_PARTIALLY_ESTABLISHED`
- **Implication**:
  - ECD Core Implementation: **UNAFFECTED & VERIFIED** (ECD core correctly outputs `UNKNOWN_INVALID`).
  - Integration Implementation: **GATED BY DOWNSTREAM POLICY** (Site governance must decide whether `UNKNOWN_INVALID` halts the pipeline (`CRITICAL_TERMINATION`) or holds the previous dispatch plan).

Status: `CORRECTION_COMPLETE`
