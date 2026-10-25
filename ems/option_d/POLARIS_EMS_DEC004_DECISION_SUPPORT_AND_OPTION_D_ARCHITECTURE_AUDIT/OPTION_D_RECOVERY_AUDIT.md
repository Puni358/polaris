# POLARIS EMS — OPTION D STATE RECOVERY AUDIT

## 1. Executive Summary

This document audits state recovery mechanisms across Options A, B, C, and D when ECD inputs transition from `UNKNOWN_INVALID` back to `VALID` (or upon human operator manual override).

---

## 2. Option-by-Option State Recovery Matrix

| Candidate Option | MPC Loop Resumption | Previous Plan Handling | Operator Reset Required? | Critical Fallback Persistence | Battery/Diesel State Revalidation | Governed Transition Event |
|------------------|---------------------|------------------------|--------------------------|------------------------------|-----------------------------------|---------------------------|
| **Option A (Hold Plan)** | Automated MPC resumes immediately | Discards cached hold plan; generates new 24h MILP plan | No | Clears hold state immediately | Revalidates SOC and diesel running status in `StationState` | Logged in `run_report.json` |
| **Option B (Zero Dispatch)** | Automated MPC resumes immediately | Discards 0-power dispatch plan; generates new 24h MILP plan | No | Clears 0-power state immediately | Revalidates SOC and diesel running status in `StationState` | Logged in `run_report.json` |
| **Option C (Operator Trip)** | Remains HALTED | Discards failed plan | **YES** (Requires manual SCADA fault reset) | Locks in `FAILED_TERMINATED` until operator reset | Requires physical equipment inspection prior to reset | SCADA `FaultResetEvent` required |
| **Option D (Critical Fallback)** | Automated MPC resumes immediately (unless D5 escalated) | Discards degraded critical plan; generates new 24h MILP plan | No (Automatic if inputs valid; YES if D5 escalated) | Clears load shed state; re-engages noncritical loads | Revalidates SOC and diesel running status in `StationState` | Logged in `run_report.json` |

---

## 3. Explicit Classification of Missing Recovery Behavior

1. **Option D Recovery Transition Logic**: `REQUIRES_IMPLEMENTATION_AUTHORIZATION` (Requires runner state handler clearing load shed relays upon `NORMAL` return).
2. **Post-Escalation Operator Reset**: `GOVERNANCE_DECISION_REQUIRED` (Unresolved whether returning to valid telemetry after D5 escalation automatically clears `CRITICAL_TERMINATION` or requires SCADA sign-off).

Status: `RECOVERY_AUDIT_SEALED`
