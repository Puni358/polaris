# POLARIS EMS — DEC-004 FOUR-CANDIDATE GOVERNANCE FRAMEWORK UPDATE

## 1. Executive Summary

This document updates the official candidate framework for **DEC-004 (Operational Response to ECD UNKNOWN_INVALID)** to incorporate **Option D** as a fully specified, internally consistent fourth operational candidate alongside Options A, B, and C.

---

## 2. Updated Candidate Option Matrix

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

| Option ID | Candidate Title | Core Operational Response | Primary Advantage | Primary Risk / Tradeoff | Governance Status |
|-----------|-----------------|---------------------------|-------------------|-------------------------|-------------------|
| **OPTION A** | Hold Last Valid Dispatch | Re-applies setpoints/schedule from previous valid $t_{k-1}$ plan | Maintains full station power continuity | Horizon expiration & unmonitored battery drift | Candidate |
| **OPTION B** | Zero-Dispatch Fail-Closed | Enforces zero controllable generation ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$) | Absolute fuel and battery energy preservation | Immediate station-wide load blackout | Candidate |
| **OPTION C** | Operator / Manual Intervention | Immediately halts MPC pipeline (`CRITICAL_TERMINATION`) & locks control | Prevents automated actions on invalid inputs | Disruption of automated control; human latency dependency | Candidate |
| **OPTION D** | Protected Critical-Load Fallback | Suppresses noncritical loads; dispatches renewables + diesel + battery for critical load ONLY | Explicitly protects life-safety loads while conserving fuel | Sheds noncritical demand; requires load shedder hardware | **Consolidated Candidate** |

---

## 3. Comparative Operational Tradeoff Summary

1. **Option A (Hold Plan)**: Prioritizes *total station load continuity*. Suitable if telemetry dropouts are expected to be extremely transient (< 15 mins).
2. **Option B (Zero Dispatch)**: Prioritizes *absolute energy resource preservation*. Suitable if hardware protection relays independently maintain critical loads.
3. **Option C (Operator Trip)**: Prioritizes *human authority & ingress security*. Suitable if unauthenticated payloads indicate security breach.
4. **Option D (Critical Fallback)**: Prioritizes *life-safety critical service preservation*. Suitable for polar station environments where heating/water/comms must be protected while noncritical energy is conserved.

---

## 4. Governance Status & Selection Register

```text
DECISION_ID: DEC-004
DECISION_QUESTION: What operational response should POLARIS adopt when ECD returns UNKNOWN_INVALID?
ALLOWED_OPTIONS: [ OPTION_A, OPTION_B, OPTION_C, OPTION_D, DEFER ]

OPTION_D_DEFINITION_STATUS: HUMAN_GOVERNANCE_DEFINITION_CONSOLIDATED
DEC004_FINAL_SELECTION: UNDECIDED (Form open for human decision-maker selection)
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
```

Option D is consolidated and ready for human selection. The final selection between Options A, B, C, D, or DEFER remains open.

Status: `DEC004_UPDATE_SEALED`
