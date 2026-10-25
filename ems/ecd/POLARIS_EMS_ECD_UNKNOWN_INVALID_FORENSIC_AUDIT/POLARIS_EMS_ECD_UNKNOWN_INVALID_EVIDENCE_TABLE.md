# POLARIS EMS — UNKNOWN_INVALID EVIDENCE TABLE

## 1. Executive Summary

This table presents the forensic evidence mapping for claims regarding `UNKNOWN_INVALID` downstream behavior in POLARIS EMS.

---

## 2. Forensic Evidence Mapping Table

| Claim | Evidence Source | Classification | Established? |
|-------|-----------------|----------------|--------------|
| **UNKNOWN_INVALID exists** | `system/control/ecd.py` (`OperatingMode.UNKNOWN_INVALID`), `POLARIS_EMS_ECD_OUTPUT_CONTRACT.json` | `EXPLICITLY_ESTABLISHED` | **YES** |
| **UNKNOWN_INVALID semantics** | `system/control/ecd.py` (Emitted when inputs are missing, invalid, expired, or unauthorized) | `EXPLICITLY_ESTABLISHED` | **YES** |
| **FaultEvent exists** | `system/runtime/runner.py` (line 19: `class FaultEvent`), `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` | `EXPLICITLY_ESTABLISHED` | **YES** |
| **FaultEvent severity** | `system/runtime/runner.py` (`CRITICAL_TERMINATION`, `GOVERNED_DEGRADED`) | `EXPLICITLY_ESTABLISHED` | **YES** |
| **GOVERNED_FAIL_CLOSED exists** | `POLARIS_EMS_ECD_UNKNOWN_INVALID_HANDLING.md` (Line 13) | `PROPOSED_BY_AUDIT_AUTHOR` | **NO** (Not in code) |
| **FaultEvent triggered by UNKNOWN_INVALID** | `POLARIS_EMS_ECD_UNKNOWN_INVALID_HANDLING.md` | `PROPOSED_BY_AUDIT_AUTHOR` | **NO** (Adapter not in code) |
| **Conservative safe state exists** | `POLARIS_EMS_ECD_MISSING_INPUT_BEHAVIOR_MATRIX.md` | `PROPOSED_BY_AUDIT_AUTHOR` | **NO** (Conceptual text only) |
| **Safe state definition** | `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` (Defines zero-dispatch for MILP infeasibility, not ECD) | `NOT_ESTABLISHED` | **NO** |
| **Downstream consumer exists** | Integration Architecture Diagrams | `PROPOSED_BY_AUDIT_AUTHOR` | **NO** (Not in `runner.py`) |
| **Downstream action exists** | `POLARIS_EMS_ECD_UNKNOWN_INVALID_HANDLING.md` | `NOT_ESTABLISHED` | **NO** (`UNRESOLVED_DOWNSTREAM_POLICY`) |
| **UNKNOWN_INVALID ≠ EMERGENCY** | `system/control/ecd.py`, `POLARIS_EMS_ECD_MISSING_INPUT_BEHAVIOR_MATRIX.md` | `EXPLICITLY_ESTABLISHED` | **YES** |
| **FaultEvent changes control behavior** | `system/runtime/runner.py` (`CRITICAL_TERMINATION` halts pipeline; `GOVERNED_DEGRADED` sets 0-dispatch) | `EXPLICITLY_ESTABLISHED` | **YES** (For runner faults; not yet for ECD) |

Status: `AUDITED`
