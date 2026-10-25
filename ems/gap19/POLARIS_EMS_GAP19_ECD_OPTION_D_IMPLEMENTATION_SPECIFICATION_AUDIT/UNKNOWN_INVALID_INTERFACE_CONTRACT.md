# UNKNOWN_INVALID Fail-Closed Interface Contract

## Fail-Closed Safety Boundary
1. `UNKNOWN_INVALID != EMERGENCY`
2. `UNKNOWN_INVALID != NORMAL`

When telemetry, authorization, or configuration inputs fail validation, `EmergencyConditionDetector` returns `operating_mode = UNKNOWN_INVALID` with a specific `ValidityStatus`.

## Router Handling Interface Specification

```text
IF assessment.operating_mode == OperatingMode.UNKNOWN_INVALID:
    1. Construct FaultEvent:
       - timestep: current_step
       - fault_class: assessment.validity_status.value
       - source: "ECD_Evaluator"
       - severity: "CRITICAL_TERMINATION"
       - response: "FAILED_TERMINATED_FAIL_CLOSED"
       - state_advanced: False
       - message: assessment.failure_reason
    2. Append FaultEvent to fault_events list.
    3. Set execution_status = "FAILED_TERMINATED".
    4. HALT MPC execution loop immediately without advancing DigitalTwinSimulator.
```

---

## Verdict
`UNKNOWN_INVALID_INTERFACE = SPECIFIED`. Fail-closed handling prevents invalid state propagation.
