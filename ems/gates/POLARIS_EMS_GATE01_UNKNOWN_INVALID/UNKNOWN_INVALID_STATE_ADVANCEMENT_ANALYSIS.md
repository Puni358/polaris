# POLARIS GATE-01 — Digital Twin State Advancement Analysis

This document evaluates the Digital Twin state advancement rules for candidate `UNKNOWN_INVALID` operational actions.

## 1. Candidate Option State Advancement Matrix

```
Option A (Hold Last Plan) -------> STATE_ADVANCES = YES  (Executes next step of prior plan)
Option B (Zero Dispatch) --------> STATE_ADVANCES = YES/NO (Executes zero power step)
Option C (Operator Hold) --------> STATE_ADVANCES = NO   (Freezes state advancement)
Option D (Option D Fallback) ----> STATE_ADVANCES = YES  (Executes Option D dispatch step)
```

## 2. Authoritative Baseline Rule

The authoritative baseline for `UNKNOWN_INVALID` state advancement is:

$$\text{STATE\_ADVANCES} = \mathbf{NO}$$

### Technical Rationale
- When `OperatingMode.UNKNOWN_INVALID` is returned, the current physical state telemetry is either invalid, missing, unauthenticated, or expired.
- Stepping the Digital Twin simulator (`DigitalTwinSimulator.step()`) requires a valid committed action acting on true ground truth actuals.
- Executing physical state transitions when telemetry is invalid corrupts battery energy accounting ($E_{\text{bat}}$), rolling fuel accounting ($F_{\text{diesel}}$), and demand tracking.
- Therefore, the Digital Twin state **MUST NOT** advance automatically (`state_advanced = False`).
