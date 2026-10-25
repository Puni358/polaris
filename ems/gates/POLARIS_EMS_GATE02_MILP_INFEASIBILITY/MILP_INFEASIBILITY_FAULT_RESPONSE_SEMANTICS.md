# POLARIS GATE-02 — MILP INFEASIBILITY FAULT RESPONSE SEMANTICS RECONCILIATION
## FORENSIC AUDIT OF FAULT EVENT RESPONSE LABELS & CONSUMER TRACE

---

## 1. FORMAL SEMANTIC RECONCILIATION SUMMARY

```text
FAULT_EVENT_RESPONSE_CONSUMER =
    REPORTING_METRICS_AND_UNIT_TESTS_ONLY

GOVERNED_ZERO_DISPATCH_MEANING =
    HISTORICAL_ZERO_POWER_ACTION_METADATA

PHYSICAL_ZERO_DISPATCH_EXECUTED =
    NO

FAULT_RESPONSE_LABEL_STATUS =
    SEMANTICALLY_MISLEADING

LABEL_CHANGE_REQUIRED =
    GOVERNANCE_DECISION_REQUIRED

GATE02_SAFETY_INVARIANT =
    PASS

GATE02_OPERATIONAL_POLICY =
    GOVERNANCE_DECISION_REQUIRED

GATE02_STATUS =
    GOVERNANCE_DECISION_REQUIRED
```

---

## 2. REPOSITORY CONSUMER TRACE OF FAULT EVENT SEMANTICS

A full repository trace was conducted for `FaultEvent` fields (`fault_class`, `severity`, `response`, `state_advanced`) and specifically `response = "GOVERNED_ZERO_DISPATCH"`.

### A. Runtime Control Logic (`system/runtime/runner.py`)
- **Finding**: Runtime control logic in `runner.py` does **NOT** consume `ev.response` to dictate state transitions, dispatch commands, or solver routing.
- Control flow for solver infeasibility is triggered strictly by `plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")`.
- `ev.response` is populated purely as a metadata field inside the `FaultEvent` object.

### B. Reporting & Metrics Engine (`system/robustness/metrics.py`)
- **Finding**: `system/robustness/metrics.py` (line 136) contains:
  ```python
  governed_zero_dispatch_responses = sum(
      1 for f in fault_events if f.get("response") == "GOVERNED_ZERO_DISPATCH"
  )
  ```
- This metric is compiled into `execution_and_fault_metrics` under key `"governed_zero_dispatch_responses_count"` and written to `run_report.json`.
- `response` is consumed here purely for offline telemetry reporting and audit logging.

### C. Unit Test Suite (`tests/test_gate02_milp_infeasibility_safety.py`)
- **Finding**: Unit tests assert `fe["response"] == "GOVERNED_ZERO_DISPATCH"` to verify that the historical fault event metadata string is logged without unauthorized mutation.

### D. Downstream UI / Visual Documentation
- **Finding**: `POLARIS_UI_UX_ARCHITECTURE_AND_VISUAL_SPEC.md` lists `response` as `"GOVERNED_ZERO_DISPATCH"` under Alarm Log Table state response metadata.

---

## 3. SEMANTIC ANALYSIS OF `GOVERNED_ZERO_DISPATCH`

### Historical Context
Historically, when `gap19_highs_native.py` returned `OPTIMIZATION_INFEASIBLE`, the runner:
1. Logged `FaultEvent(response="GOVERNED_ZERO_DISPATCH", state_advanced=True)`.
2. Passed a $0\text{ kW}$ diesel / $0\text{ kW}$ battery dispatch vector to `DigitalTwinSimulator.step()`.
3. Advanced the simulator state by 1 timestep under a full blackout scenario.

Under that historical behavior, `GOVERNED_ZERO_DISPATCH` accurately reflected that a zero-power dispatch action was executed in the simulator.

### Current Safety-Corrected Context
Under the Gate-02 Safety Invariant Correction:
1. `FaultEvent(response="GOVERNED_ZERO_DISPATCH", state_advanced=False)` is logged.
2. `DigitalTwinSimulator.step()` is **NOT** invoked (`break` from loop).
3. **No physical or simulated zero-dispatch action is committed or executed.**
4. Fuel and battery SOC remain unchanged; authoritative `StationState` is preserved.

### Semantic Conclusion
Because **NO zero-dispatch action is executed**, retaining the string label `"GOVERNED_ZERO_DISPATCH"` creates a semantic conflict between the label text and actual system behavior.
Therefore, `FAULT_RESPONSE_LABEL_STATUS = SEMANTICALLY_MISLEADING`.

---

## 4. GOVERNANCE VS. ENGINEERING CLASSIFICATION

Changing the string label `response = "GOVERNED_ZERO_DISPATCH"`:
1. **Would NOT alter physical runtime behavior**: The runner loop breaks regardless of the string content.
2. **Would break metric filters & contract specifications**: Downstream metrics tools (`system/robustness/metrics.py`) and existing test assertions expect `"GOVERNED_ZERO_DISPATCH"`.
3. **Constitutes a governance terminology decision**: Defining a new governed response label (e.g. `"GOVERNED_STATE_HELD"` or `"GOVERNED_EXECUTION_BLOCKED"`) requires formal governance authorization to update system contract specifications.

Therefore, `LABEL_CHANGE_REQUIRED = GOVERNANCE_DECISION_REQUIRED`. The string `"GOVERNED_ZERO_DISPATCH"` is preserved in source code as a historical diagnostic placeholder until formal governance updates the fault terminology specification.
