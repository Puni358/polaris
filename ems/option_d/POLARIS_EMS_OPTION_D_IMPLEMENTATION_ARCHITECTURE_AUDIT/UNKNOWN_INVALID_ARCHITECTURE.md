# UNKNOWN INVALID ARCHITECTURE

## 1. FAIL-CLOSED SAFE-STATE ROUTING & EXECUTION

The audit defined the architectural handling of `OperatingMode.UNKNOWN_INVALID`.

---

## 2. DISTINCTION BETWEEN EMERGENCY AND UNKNOWN_INVALID

```text
               ┌────────────────────────────────────────────────────────┐
               │              ECD Evaluation Results                    │
               └───────────────────────────┬────────────────────────────┘
                                           │
                ┌──────────────────────────┴──────────────────────────┐
                ▼                                                     ▼
┌──────────────────────────────┐                      ┌──────────────────────────────┐
│  OperatingMode.EMERGENCY     │                      │ OperatingMode.UNKNOWN_INVALID│
├──────────────────────────────┤                      ├──────────────────────────────┤
│ Assessment VALID             │                      │ Assessment UNTRUSTED         │
│ Telemetry TRUSTED            │                      │ Telemetry CORRUPTED/EXPIRED  │
│ Margin m < 0                 │                      │ Missing T_required           │
├──────────────────────────────┤                      ├──────────────────────────────┤
│ Enforces Option D            │                      │ Invokes Safe-State Fallback  │
│ Optimization in MILP         │                      │ Zero-Dispatch / Safe Plan    │
└──────────────────────────────┘                      └──────────────────────────────┘
```

---

## 3. FAIL-CLOSED ROUTING BEHAVIOR

When ECD produces `UNKNOWN_INVALID` (`validity_status != ValidityStatus.VALID`):
1. **Bypass Mathematical Solver**: The system MUST NOT pass corrupted or unvalidated telemetry into HiGHS/MILP.
2. **Invoke Safe-State Fallback Handler**: A dedicated safe-state router generates a governed fallback `DispatchPlan`:
   - Noncritical loads shed ($P_{\text{flex}} = 0$).
   - Battery discharge permitted ONLY for protected critical load ($P_{\text{dis}} \le P_{\text{critical}}$).
   - Generator started ONLY if battery SOC is below floor ($20\%$).
   - `constraint_status` set to `"UNKNOWN_INVALID_SAFE_STATE_FALLBACK"`.
3. **Trigger Alarm Event**: A `FaultEvent` with severity `"CRITICAL_DEGRADED"` is recorded in the run report.
