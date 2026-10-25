# POLARIS EMS — DEC-004 OPTION C: OPERATOR / MANUAL INTERVENTION

## 1. Executive Summary

This document provides a factual, evidence-based forensic analysis of **Option C: Operator / Manual Intervention** as an operational response to ECD `UNKNOWN_INVALID`.

---

## 2. Concept & Operational Mechanism

- **Concept**: If the ECD returns `UNKNOWN_INVALID` at timestep $k$, the system treats the input failure as a fatal control fault (`CRITICAL_TERMINATION`), immediately halts the automated MPC dispatch loop, and locks state until a human operator inspects and acknowledges the fault.
- **Runtime Interpretation**: Maps directly to existing `FaultEvent(fault_class="INVALID_SURVIVABILITY_ASSESSMENT", severity="CRITICAL_TERMINATION", response="FAILED_TERMINATED")` in `system/runtime/runner.py`.

---

## 3. Benefits & Technical Rationale

1. **Security & Governance Enforcement**: Prevents automated algorithms from executing dispatch decisions under corrupted, stale, or unauthenticated operational inputs.
2. **Existing Implementation Support**: Reuses the native `CRITICAL_TERMINATION` failure handling path in `PolarisLocalRunner`.

---

## 4. Operational Hazards & Latency Dependencies

1. **Automation Disruption**: Automated energy management is suspended immediately upon detection of `UNKNOWN_INVALID`.
2. **Human Operator Latency**: The microgrid's operational continuity during the lockout period depends on local hardware protective relays and operator response time.

---

## 5. Implementation & Engineering Dependencies

- **Runner Wiring**: Requires raising `CRITICAL_TERMINATION` in `PolarisLocalRunner` when ECD outputs `UNKNOWN_INVALID`.
- **HMI / SCADA Notification**: Exposes fault details in `run_report.json` and UI API.

Status: `ANALYSIS_COMPLETE`
