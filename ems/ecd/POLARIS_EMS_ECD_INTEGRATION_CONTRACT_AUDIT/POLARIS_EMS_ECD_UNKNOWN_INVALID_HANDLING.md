# POLARIS EMS — UNKNOWN_INVALID HANDLING AT INTEGRATION BOUNDARY

## 1. Executive Summary

This document specifies the handling contract for the `UNKNOWN_INVALID` state when emitted by the Emergency Condition Detector (ECD) at the integration boundary.

---

## 2. Safety Firewall Rules

1. **NO Emergency Collapse**: `UNKNOWN_INVALID` **MUST NOT** be collapsed into `EMERGENCY`. Declaring an emergency on invalid data could force unwarranted diesel startup or emergency load shedding.
2. **NO Normal Collapse**: `UNKNOWN_INVALID` **MUST NOT** be collapsed into `NORMAL`. Treating invalid data as normal could silently execute cost-optimization over corrupt or missing telemetry.
3. **Explicit Diagnostic Event**: The integration adapter logs a `FaultEvent` (`fault_class = "INVALID_SURVIVABILITY_ASSESSMENT"`, `severity = "GOVERNED_FAIL_CLOSED"`).

---

## 3. Integration Handling Routing

```
                          [ECD Output]
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
           [NORMAL]       [EMERGENCY]  [UNKNOWN_INVALID]
               │               │               │
               ▼               ▼               ▼
         Standard Cost   E3 Resource      Fail-Closed
         Optimization    Preservation   Safety Boundary
                                          (Hold Conservative
                                           State & Log Event)
```

Classification: `UNRESOLVED_DOWNSTREAM_POLICY` (Integration contract defines handling routing; specific SCADA fallback action gated by site governance).

Status: `ESTABLISHED`
