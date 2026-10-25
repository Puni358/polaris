# POLARIS EMS — EXISTING FAILURE BEHAVIOR AUDIT

## 1. Executive Summary

This document audits the existing failure contracts, fault event structures, and error handling mechanisms currently implemented in POLARIS EMS.

---

## 2. Existing Failure Mechanisms Audit Table

| Existing Mechanism | Trigger Condition | Current Implementation / Source | Current Operational Behavior | Can It Apply to UNKNOWN_INVALID? |
|--------------------|-------------------|----------------------------------|------------------------------|----------------------------------|
| **`FaultEvent` Logging** | Runtime exceptions or infeasibilities | `system/runtime/runner.py` (line 19) | Records diagnostic JSON object in `run_report.json` | **YES** (Structure exists, needs adapter wiring) |
| **`CRITICAL_TERMINATION` Severity** | Invalid ForecastBundle, optimization exception, malformed plan, SOC boundary violation | `system/runtime/runner.py` | Immediately halts MPC execution (`execution_status="FAILED_TERMINATED"`) | **YES** (Under Option C: Operator Intervention) |
| **`GOVERNED_DEGRADED` Severity** | MILP solver infeasibility | `system/runtime/runner.py` & `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` | Solves zero-dispatch ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$), advances state via 0-power physics, completes as `SUCCESS_WITH_GOVERNED_FAULTS` | **YES** (Under Option B: Zero-Dispatch, but currently ungoverned for ECD) |
| **D4-C0 Failure Contract** | MILP solver infeasibility | `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` | Governed zero-dispatch response | **NO** (Strictly bound to MILP infeasibility; extension requires governance decision) |
| **Plan Holding Behavior** | Mentioned in `apply_governance_corrections.py` for solver timeout | Documentation text | Conceptual proposal to retain previous plan | **NO** (Not implemented in `runner.py`) |
| **Operator Trip / HMI Alarm** | None in Python runner | `system/ui/server.py` | UI server logs error | **NO** (No automated SCADA trip handler) |

---

## 3. Key Forensic Conclusion

The POLARIS repository currently implements zero-dispatch for MILP infeasibility (`GOVERNED_DEGRADED`) and pipeline termination for fatal exceptions (`CRITICAL_TERMINATION`). **No operational action is currently governed or implemented for ECD input failure (`UNKNOWN_INVALID`)**.

Status: `AUDITED`
