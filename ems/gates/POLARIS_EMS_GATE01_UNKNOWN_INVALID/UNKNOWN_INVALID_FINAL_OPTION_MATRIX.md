# POLARIS GATE-01 — Final Option Evaluation & Critical Safety Matrix

This document evaluates the 5 governance options (Option A, Option B, Option C, Option D, Option E) against the 12 mandatory critical safety questions.

## 1. 12-Question Critical Safety Evaluation Matrix

| Safety Question | Option A: Retain Software Termination | Option B: Operator Intervention Mode | Option C: Protected-Critical Fallback | Option D: Governed Hybrid | Option E: Remain Unresolved (Selected) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Critical-Load Service** | External hardware fallback dependent | `GOVERNANCE_DECISION_REQUIRED` | Serves protected critical load ($P_{\text{crit\_demand}}$) | Serves protected critical load ($P_{\text{crit\_demand}}$) | `GOVERNANCE_DECISION_REQUIRED` |
| **2. Authority Source** | External hardware / Site engineer | Authenticated Human Operator | Automatic EMS Policy | Hybrid (Operator + EMS Policy) | `UNDEFINED` |
| **3. Digital Twin Advances?** | **NO** (`state_advanced = False`) | **NO** (`state_advanced = False`) | **YES** | **NO** (during hold phase) | **NO** (`state_advanced = False`) |
| **4. Physical Station Operating?** | `GOVERNANCE_DECISION_REQUIRED` | Continues under manual control | Continues under fallback | Continues under fallback | `GOVERNANCE_DECISION_REQUIRED` |
| **5. Diesel Generator State** | Un-commanded by software | Manual setpoints issued | Dispatched per D1–D6 | Dispatched per D1–D6 | Un-commanded by software |
| **6. Battery State** | Floating / Un-commanded | Manual setpoints issued | Dispatched per D1–D6 | Dispatched per D1–D6 | Floating / Un-commanded |
| **7. Renewable Generation** | Self-regulating / Curtailed | Manual setpoints issued | Direct to load first | Direct to load first | Self-regulating / Curtailed |
| **8. Persisting Condition** | External station fallback | Escalation timeout required | Fallback continues | Escalation timeout required | Execution halted at blocker |
| **9. What Ends Condition?** | Valid telemetry restored | Operator manual reset | Valid telemetry restored | Operator / Valid telemetry | Valid telemetry restored |
| **10. Return Authority** | Site engineer | Authenticated Operator | `GOVERNANCE_DECISION_REQUIRED` | Authenticated Operator | `GOVERNANCE_DECISION_REQUIRED` |
| **11. Required Evidence** | Valid ECD telemetry | Operator signoff + Valid ECD | Valid ECD telemetry | Operator signoff + Valid ECD | Valid ECD telemetry |
| **12. Operator Comm Lost** | Hardware fallback | `GOVERNANCE_DECISION_REQUIRED` | Local fallback continues | Local fallback continues | `GOVERNANCE_DECISION_REQUIRED` |

---

## 2. Rationale for Option E Selection

Option E (`REMAIN UNRESOLVED`) is selected as the current governance status because:
- Options A, B, C, and D all require station-specific hardware, communication, or authority parameters that are currently `NOT_ESTABLISHED`.
- Option C (Protected Fallback) violates the semantic distinction $UNKNOWN\_INVALID \ne EMERGENCY$ by executing fallback calculations on unverified/invalid telemetry.
- Selecting any candidate operational policy without site engineering data would invent un-governed physical risk.
