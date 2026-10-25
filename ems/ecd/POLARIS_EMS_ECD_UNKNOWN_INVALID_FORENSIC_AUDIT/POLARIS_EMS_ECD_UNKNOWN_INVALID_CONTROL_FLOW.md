# POLARIS EMS — UNKNOWN_INVALID CONTROL FLOW FORENSIC AUDIT

## 1. Overview

This document traces the actual implemented runtime control flow in `system/runtime/runner.py` against the proposed integration control flow for `UNKNOWN_INVALID`.

---

## 2. Implemented Runtime Control Flow (`system/runtime/runner.py`)

In the existing `PolarisLocalRunner.run_pipeline()` implementation:

```
[Timestep k]
     │
     ▼
1. ForecastEngine.predict() ──(Exception)──► FaultEvent("INVALID_FORECAST_BUNDLE", severity="CRITICAL_TERMINATION")
     │                                                    │
     ▼                                                    ▼
2. EnergyOptimizer.optimize() ──(Infeasible)──► FaultEvent("OPTIMIZATION_INFEASIBLE", severity="GOVERNED_DEGRADED")
     │                                                    │
     ▼                                                    ▼
3. DigitalTwinSimulator.step() ──(Violation)──► FaultEvent("FAILED_STATE_VIOLATION", severity="CRITICAL_TERMINATION")
```

**Forensic Finding**: `system/runtime/runner.py` contains active exception handling and `FaultEvent` creation for forecast errors, optimizer infeasibilities, and simulator violations, but **does NOT yet contain an ECD invocation step or an ECD `UNKNOWN_INVALID` handler**.

---

## 3. Proposed Integration Control Flow (From Integration Audit)

```
[ECD.evaluate()]
       │
       ▼
EmergencyAssessment(operating_mode=UNKNOWN_INVALID)
       │
       ▼
Integration Adapter (Proposed)
       │
       ├─► Log FaultEvent("INVALID_SURVIVABILITY_ASSESSMENT", severity="GOVERNED_FAIL_CLOSED") [PROPOSED]
       │
       └─► Route to EMS Mode Manager ──► UNRESOLVED_DOWNSTREAM_POLICY [PROPOSED / UNRESOLVED]
```

---

## 4. Gap Analysis & Conclusion

- **Producer**: `EmergencyConditionDetector` emits `UNKNOWN_INVALID` (`system/control/ecd.py`). **[ESTABLISHED]**
- **Logging Structure**: `class FaultEvent` exists in `runner.py`. **[ESTABLISHED]**
- **Severity String**: `GOVERNED_FAIL_CLOSED` is not an existing severity in `runner.py` (which uses `CRITICAL_TERMINATION` or `GOVERNED_DEGRADED`). **[NOT ESTABLISHED IN CODE]**
- **Downstream Handler**: No handler currently catches `UNKNOWN_INVALID` in `runner.py`. **[NOT IMPLEMENTED]**
- **Action / Policy**: The concrete dispatch action (hold last plan vs zero dispatch vs operator trip) is unassigned. **[NOT ESTABLISHED]**

Status: `GAP_IDENTIFIED`
