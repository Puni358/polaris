# POLARIS GATE-01 — Candidate Governance Option Evaluation Matrix

This document presents a comprehensive descriptive evaluation of candidate options for the `UNKNOWN_INVALID` operational response.

## Candidate Options Evaluation Matrix

| Criterion | Option A: Hold Last Valid Plan | Option B: Zero Dispatch | Option C: Operator Intervention | Option D: Protected Fallback |
| :--- | :--- | :--- | :--- | :--- |
| **Operational Concept** | Continue executing $k+1$ action from previously committed plan | Set all controllable dispatch commands ($P_{\text{chg}}, P_{\text{dis}}, P_{\text{diesel}}$) to $0$ | Freeze automatic progression, emit diagnostic telemetry, await operator authority | Route automatically to `OptionDFallbackSolver` |
| **State Advances?** | **YES** (Simulates/executes next plan step) | **NO / UNCERTAIN** | **NO** (`state_advanced = False`) | **YES** (Executes Option D dispatch step) |
| **Critical Load Protection** | **UNCERTAIN** (Depends on state drift & horizon) | **FAIL** (Drops power to critical loads instantly) | **PRESERVED BOUNDARY** (Awaits override) | **UNSAFE** (Option D runs on untrusted telemetry) |
| **Truth Firewall Preserved?** | **RISK** (Assumes old state holds) | **FAIL** (Ignores generation & load truth) | **YES** (No false state calculated) | **FAIL** (Treats untrusted state as valid) |
| **Preserves $UNKNOWN\_INVALID \ne EMERGENCY$?** | **YES** (Does not declare emergency) | **YES** (Does not declare emergency) | **YES** (Classifies as interface blocker) | **NO** (Incorrectly equates invalid telemetry with emergency) |
| **Authority Required** | Unassigned / Implicit | Unassigned / Implicit | Authenticated Operator Authority | Automatic EMS Policy |
| **Horizon Expiry Risk** | **HIGH** (Plan expires after 24h) | N/A | **MEDIUM** (Requires escalation timeout) | N/A |
| **Station Safety Verdict** | **REJECTED** (Unmonitored state drift risk) | **REJECTED** (Violates critical load protection) | **REQUIRES GOVERNANCE** (Interface defined, authority needed) | **REJECTED** (Violates semantic distinction) |

---

## Detailed Option Analysis

### Option A — Hold Last Valid Dispatch
- **Pros**: Maintains short-term continuity if telemetry drop is transient (seconds).
- **Cons & Risks**: If state changes (e.g. demand spikes, battery SOC drops, fuel consumes), executing a stale plan can cause catastrophic battery over-discharge or fuel exhaustion. When the 24h horizon expires, no plan exists.
- **Verdict**: **UNSAFE AS GENERAL POLICY**.

### Option B — Zero Dispatch
- **Pros**: Electrically isolates controllable sources.
- **Cons & Risks**: Sheds all loads including protected critical heating, water filtration, and emergency comms. Zero dispatch is an active shutdown action, not a safe state for an isolated polar microgrid.
- **Verdict**: **VIOLATES CRITICAL LOAD PROTECTION GOVERNANCE**.

### Option C — Operator / Manual Intervention (Engineered Hold)
- **Pros**: Respects `UNKNOWN_INVALID` classification without inventing un-governed dispatch actions. Stops automatic state advancement (`state_advanced = False`).
- **Cons & Risks**: Requires formal definition of escalation timeout, notification interfaces, and operator authority protocols.
- **Verdict**: **PRESERVES SAFETY BOUNDARY BUT REQUIRES GOVERNANCE AUTHORIZATION**.

### Option D — Protected-Critical Fallback
- **Pros**: Leverages existing sealed Option D heuristic code.
- **Cons & Risks**: Option D relies on valid critical load and telemetry estimates. Executing Option D when ECD returns `UNKNOWN_INVALID` forces Option D to calculate dispatch using invalid or corrupted inputs.
- **Verdict**: **VIOLATES SEMANTIC DISTINCTION ($UNKNOWN\_INVALID \ne EMERGENCY$)**.
