# POLARIS GATE-01 — Physical vs Software Safety Boundary

This document explicitly establishes the governance boundary between EMS software control-flow termination and physical microgrid hardware safety.

## 1. Software Termination Non-Equivalence Principle

> [!CAUTION]
> **SOFTWARE TERMINATION DOES NOT EQUATE TO PHYSICAL SAFE STATE**:
> Software control-flow loop termination (`break` with `execution_status = "FAILED_TERMINATED"`) inside `system/runtime/runner.py` is a software exception/containment mechanism.
> It does **NOT** establish or guarantee:
> - Generator physical shutdown or safe idling;
> - Battery physical contactor isolation or thermal safety;
> - Critical load power continuation or safe load shedding;
> - Station electrical frequency or voltage stability;
> - A physical hardware safe state.

## 2. Non-Generation of DispatchPlan

- When ECD returns `OperatingMode.UNKNOWN_INVALID`, the EMS software does **NOT** emit a `DispatchPlan`.
- The absence of a `DispatchPlan` merely means the automated optimization software has ceased issuing digital control commands.
- It does **NOT** prove or guarantee that the physical station hardware is safe or operating within limits.

## 3. Separation of Concerns

1. **EMS Software Domain**: Responsible for receding-horizon optimization, ECD survivability evaluation, and generating `DispatchPlan` setpoints when inputs are valid (`NORMAL` or `EMERGENCY`).
2. **Physical Hardware Domain**: Responsible for hardware-level interlocks, SCADA watchdog timers, manual transfer switches, and site electrical protection relays. Physical hardware safety during control telemetry loss remains a separate station engineering item (`PHYSICAL_FALLBACK = UNDEFINED`).
