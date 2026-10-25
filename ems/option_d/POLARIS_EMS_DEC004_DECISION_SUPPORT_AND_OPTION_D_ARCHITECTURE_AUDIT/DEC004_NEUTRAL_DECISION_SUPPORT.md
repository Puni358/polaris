# POLARIS EMS — DEC-004 NEUTRAL DECISION SUPPORT SUMMARY

## 1. Executive Overview

This decision-support document provides a factual, evidence-backed overview of the four operational candidate responses under review for **DEC-004 (Operational Response to ECD UNKNOWN_INVALID)**.

The Emergency Condition Detector (ECD) evaluates resource survivability and emits `UNKNOWN_INVALID` when inputs are missing, corrupted, expired, or unauthenticated. The human governance decision-maker must select which operational policy POLARIS adopts under `UNKNOWN_INVALID`.

> [!NOTE]
> **STRICT NEUTRALITY COMPLIANCE**:
> - **NO option is ranked, scored, or declared "best", "safest", "preferred", or "recommended".**
> - **`DEC004_FINAL_SELECTION = UNDECIDED`**.

---

## 2. Factual Summary of Candidate Options

### OPTION A — HOLD LAST VALID DISPATCH
- **Core Concept**: Re-applies the setpoints or schedule from the most recent valid `DispatchPlan` generated at timestep $t_{k-1}$ for a defined hold period.
- **Operational Alignment**: Maintains total station power continuity during transient telemetry dropouts.
- **Primary Technical Risk**: Risk of plan horizon expiration and unmonitored battery depletion if physical irradiance/demand diverges from the stale $t_{k-1}$ forecast.

### OPTION B — ZERO-DISPATCH FAIL-CLOSED CONTROL
- **Core Concept**: Enforces zero controllable generation and discharge ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$).
- **Operational Alignment**: Maximizes energy resource preservation and eliminates risk of unmonitored battery degradation or fuel burn.
- **Primary Technical Risk**: Causes immediate station-wide load shedding, interrupting critical life-safety services unless uncurtailed renewables directly power loads.

### OPTION C — OPERATOR / MANUAL INTERVENTION
- **Core Concept**: Immediately halts the automated MPC dispatch loop (`CRITICAL_TERMINATION`), records a fatal fault event, and locks control.
- **Operational Alignment**: Enforces strict human authority and ingress security by preventing automated control actions on invalid inputs.
- **Primary Technical Risk**: Suspends automated microgrid management; station continuity becomes entirely dependent on local hardware protective relays and human operator latency.

### OPTION D — PROTECTED CRITICAL-LOAD FALLBACK
- **Core Concept**: Suppresses noncritical loads and dispatches available renewables + diesel + battery to serve authorized protected critical loads ONLY.
- **Operational Alignment**: Explicitly protects critical life-safety services (heating, water, comms) while shedding noncritical demand and conserving fuel.
- **Primary Technical Risk**: Requires load shedding infrastructure, critical circuit mapping, and dynamic critical load trajectory inputs.

---

## 3. High-Level Factual Tradeoff Matrix

```text
                                     ┌─────────────────────────────────────┐
                                     │    ECD Returns UNKNOWN_INVALID      │
                                     └──────────────────┬──────────────────┘
                                                        │
         ┌─────────────────────────┬────────────────────┴────────────────────┬─────────────────────────┐
         ▼                         ▼                                         ▼                         ▼
 [OPTION A: HOLD PLAN]   [OPTION B: ZERO DISPATCH]                 [OPTION C: OPERATOR TRIP] [OPTION D: CRITICAL FALLBACK]
 • Maintains full power  • Preserves fuel & battery                • Enforces human authority • Protects critical load only
 • Risk of plan expiry   • Immediate station load shed             • Halts automated MPC      • Sheds noncritical demand
 • Risk of battery drift • High critical load drop risk             • Operator latency risk    • Requires load shedder
```

Status: `DECISION_SUPPORT_SEALED`
