# POLARIS EMS — OPERATOR ESCALATION & FAULT EVENT AUDIT

## 1. Executive Summary

This document audits the operator escalation architecture under Option D decisions **D4 (Critical Load Shortfall)** and **D5 (Watchdog Escalation Boundary)**, evaluating compatibility with the existing `FaultEvent` logging infrastructure in `PolarisLocalRunner`.

---

## 2. Escalation Architecture & Origin Audit

```text
 ┌────────────────────────┐
 │   ECD Core Evaluator   │ ──► Emits EmergencyAssessment (mode = UNKNOWN_INVALID)
 └───────────┬────────────┘     (Pure read-only evaluator; ZERO side effects/events)
             │
             ▼
 ┌────────────────────────┐
 │    EMS Mode Manager    │ ──► Evaluates D4 Shortfall / D5 Watchdog Boundaries
 └───────────┬────────────┘
             │ (Escalation Triggered)
             ▼
 ┌────────────────────────┐
 │  PolarisLocalRunner    │ ──► Logs FaultEvent(fault_class="INVALID_SURVIVABILITY_ASSESSMENT",
 └───────────┬────────────┘                severity="CRITICAL_TERMINATION")
             │
             ▼
 ┌────────────────────────┐
 │   HMI / SCADA API      │ ──► Emits SCADA Alarm & Notifies Operator
 └────────────────────────┘
```

1. **Origin of Escalation Event**: The escalation event originates in the **EMS Mode Manager / Policy Layer** inside `PolarisLocalRunner`, **NOT** inside ECD core. ECD remains a pure read-only state evaluator.
2. **Existing Infrastructure Capability**: `PolarisLocalRunner` natively implements `FaultEvent` logging (line 19 of `system/runtime/runner.py`). It records diagnostic JSON objects in `run_report.json`.
3. **Escalation Control Authority**: Escalation under D4 (critical shortfall) or D5 (time/resource limit) is **CONTROL-AUTHORITATIVE**. It logs a `FaultEvent` and raises a SCADA alarm.
4. **Distinction from Automatic Shutdown**: As established in decision D5, operator escalation alerts the human operator but does **NOT** automatically force physical disconnection of protected critical loads if physical generation/battery capability permits continued D3 support.

---

## 3. Forensic Evidence Reconciliation with Previous Corrections

- **`GOVERNED_FAIL_CLOSED` Severity**: `NOT_ESTABLISHED` as production policy. Option D defines a degraded critical fallback, not an un-governed fail-closed state.
- **Conservative Safe State**: `NOT_ESTABLISHED` in runner code. Must be defined by station engineering.
- **Downstream Consumer**: `NOT_IMPLEMENTED` in baseline runner. SCADA alarm handler is `PROPOSED_FUTURE_IMPLEMENTATION`.

Status: `ESCALATION_AUDIT_SEALED`
