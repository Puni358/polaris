# POLARIS GATE-01 — UNKNOWN_INVALID Safety & Semantic Analysis

This document provides the technical safety and semantic analysis for `OperatingMode.UNKNOWN_INVALID`.

## 1. Fundamental Semantic Distinction ($UNKNOWN\_INVALID \ne EMERGENCY$)

```
+-------------------------------------------------------------------------+
|                              ECD EVALUATION                             |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  OperatingMode.       |                       |  OperatingMode.       |
|  EMERGENCY            |                       |  UNKNOWN_INVALID      |
+-----------------------+                       +-----------------------+
| - Survivability       |                       | - Assessment itself   |
|   failure established |                       |   cannot be trusted   |
| - Telemetry valid     |                       | - Telemetry missing/  |
| - m_bat < 0 or        |                       |   invalid/expired     |
|   m_diesel < 0        |                       | - Target horizon      |
| - Enters Option D     |                       |   unauthorized/missing|
+-----------------------+                       +-----------------------+
```

### Safety Implication
Routing `UNKNOWN_INVALID` to Option D would assume that the telemetry inputs (SOC, fuel, demand, irradiance) are valid enough to compute Option D's renewable-first and resource-preservation dispatch. If `UNKNOWN_INVALID` was triggered by NaN/Inf telemetry or expired horizon authority, Option D will calculate mathematically invalid or unsafe setpoints.

---

## 2. Fail-Closed Principles vs. Invented Actions

The concept of "fail-closed" safety in system architecture means:
1. The system must **NOT** proceed with unverified or unsafe automatic state progression.
2. The system must **NOT** silently invent an operational policy merely to satisfy Python control flow.

Equating "fail-closed" with zero-dispatch or station shutdown is an architectural error for an Antarctic microgrid where un-commanded loss of power to heating or life support can cause catastrophic physical damage.

---

## 3. Truth Firewall Integrity

- The Truth Firewall requires that physical state transitions in the Digital Twin (`DigitalTwinSimulator.step()`) are driven strictly by validated actions acting on ground truth actuals.
- Executing an un-governed action (such as holding last plan or forcing zero dispatch) during an `UNKNOWN_INVALID` telemetry state corrupts the closed-loop state tracking and violates the Truth Firewall.
