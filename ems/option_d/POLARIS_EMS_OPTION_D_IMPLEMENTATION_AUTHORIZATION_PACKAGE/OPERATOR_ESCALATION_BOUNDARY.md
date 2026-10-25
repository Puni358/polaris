# OPERATOR ESCALATION BOUNDARY

## Governance Dependency & Threshold Specification

This document defines the architectural boundary for **Operator Escalation** during degraded or emergency states (D5).

---

## Sealed Governance Rule (D5)

- **Dual Escalation Triggers**: Operator escalation is triggered by either a **Time boundary** OR a **Resource-survivability boundary**, whichever occurs first.

---

## Status of Quantitative Thresholds

```text
OPERATOR_ESCALATION_STATUS = GOVERNANCE_AND_ENGINEERING_DEPENDENT
THRESHOLDS_SEALED = FALSE
```

> [!WARNING]
> **ILLUSTRATIVE VALUES ONLY**:
> Quantitative threshold values such as `6 hours`, `50 Liters`, or `2 solver cycles` are **ILLUSTRATIVE EXAMPLES ONLY**. They are **NOT** sealed production governance thresholds and must **NOT** be hardcoded into production source code without explicit human governance authorization.

---

## Pre-GAP19 Implementation Boundary

1. In pre-GAP19 code, if `ECDState == DEGRADED` or `OperatingMode == OPTION_D`, `runner.py` emits a structured warning log:
   ```text
   [OPERATOR_ESCALATION_ALERT] System operating under Option D degraded mode.
   Escalation condition active: Time/Resource boundary monitoring active.
   ```
2. Real station escalation protocols (SMS alerts, satellite links, physical alarms) remain deferred to site-specific engineering integration.
