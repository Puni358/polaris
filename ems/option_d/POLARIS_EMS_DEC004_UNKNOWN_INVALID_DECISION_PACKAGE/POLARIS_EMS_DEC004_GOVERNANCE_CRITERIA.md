# POLARIS EMS — DEC-004 GOVERNANCE DECISION CRITERIA

## 1. Executive Summary

This document details the governance criteria derived from existing POLARIS policy artifacts (HD-01 through HD-05 and D4-C0 failure contract) to assist human decision-makers in evaluating Candidate Options A, B, C, and D for DEC-004.

---

## 2. Governed Decision Criteria Table

| Governance Criterion | Evidence Source | Policy Status | Application to DEC-004 Options (A, B, C, D) |
|----------------------|-----------------|---------------|---------------------------------------------|
| **Critical Service Protection** | HD-03 / E3 Survivability Specification | `GOVERNED_POLICY` | Option D explicitly prioritizes critical load; Option A maintains full dispatch; Option B & C result in immediate load shedding. |
| **Fail-Closed Safety Boundary** | D4-C0 Failure Contract (`POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md`) | `GOVERNED_POLICY` | Option B enforces zero dispatch; Option C halts MPC loop; Option D sheds noncritical load; Option A continues unverified full dispatch. |
| **Resource Preservation (E3)** | E3 Resource Preservation Semantics | `GOVERNED_POLICY` | Option B consumes zero fuel/battery energy; Option D conserves noncritical fuel/battery energy; Option A maintains full prior burn rate. |
| **Operator Authority & Ingress Security** | HD-03 Operational Override Precedence | `GOVERNED_POLICY` | Option C halts automated execution until human validation; Option D awaits valid operator/telemetry input. |
| **Automated Control Continuity** | System D2 Local Orchestration Spec | `GOVERNED_POLICY` | Option A and Option D maintain continuous automated dispatch; Option B forces 0-power dispatch; Option C halts MPC execution. |
| **Operational Safe-State Selection** | UNRESOLVED | `HUMAN_POLICY_DECISION_REQUIRED` | **Requires human decision-maker to select weight across above criteria.** |

Status: `CRITERIA_DERIVED`
