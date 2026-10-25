# POLARIS EMS — P_CRITICAL(t) & OPTION D INTERACTION AUDIT

## 1. Executive Summary

This document audits the interaction between **Protected Critical Load ($P_{\text{critical}}(t)$)** and sealed **Option D Governance** (`OPTION_D_PROTECTED_CRITICAL_LOAD_FALLBACK`).

---

## 2. Option D Rule Verification for $P_{\text{critical}}(t)$

### Rule D1: Dynamic Protected Critical Load
- Protected equipment is station-defined (essential heating, water treatment, emergency comms).
- $P_{\text{critical}}(t)$ may vary dynamically over time. The EMS optimizer must NOT reclassify noncritical loads into protected equipment.

### Rule D2 & D3: Restricted Battery Discharge
- Battery discharge is permitted **ONLY** for protected critical loads ($P_{\text{critical}}$).
- Noncritical loads MUST NOT receive battery discharge during Option D fallback under any circumstances.

### Rule D4: Proportional Shortfall Allocation
- When total available power (renewable + diesel + battery) is less than total critical demand $P_{\text{critical}}(t)$:
  1. Maintain all protected systems at/above minimum viable operating levels ($P_{\text{min,critical}}$).
  2. If available power is insufficient to satisfy all minimum levels, proportionally allocate available power across protected critical systems based on engineering-defined minimum viable levels.
  3. Do NOT invent arbitrary category priorities (e.g., shedding water before heating unless authorized by station policy).
  4. Mandatory operator escalation occurs under Rule D5.

### Rule D6: Excess Diesel Generation Handling
- If diesel generator is running to supply $P_{\text{critical}}(t)$ and minimum generator output ($P_{\text{gen,min}}$) exceeds $P_{\text{critical}}(t)$:
  1. Charge battery using unavoidable excess diesel generation up to battery charge acceptance limits.
  2. Curtail any remaining excess diesel generation.
  3. **Firewall Rule**: Do NOT start diesel generator merely to charge the battery when critical loads do not require diesel output.

---

## 3. Option D Implementation Readiness Audit

| Option D Requirement | Governed Rule | Current Code Implementation Status | Readiness Classification |
| :--- | :--- | :--- | :--- |
| **Protected Critical Load Routing** | Rule D1 / D2 | Breaker actuator control logic `NOT_IMPLEMENTED`. | `NOT_READY` |
| **Proportional Allocation Solver** | Rule D4 | Lexicographic proportional solver `NOT_IMPLEMENTED`. | `NOT_READY` |
| **Minimum Viable Power Levels** | Rule D4 | $P_{\text{min}}$ thresholds `NOT_ESTABLISHED`. | `NOT_READY` |
| **Allocation Weight Vector** | Rule D4 | Weighting parameters `NOT_ESTABLISHED`. | `NOT_READY` |
| **Excess Diesel Battery Charging** | Rule D6 | Charging logic `NOT_IMPLEMENTED`. | `NOT_READY` |

---

## 4. Status Classification

```yaml
P_CRITICAL_OPTION_D_READINESS: NOT_READY
GOVERNANCE_STATUS: SEALED (DEC-004 Option D policy is sealed)
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED (Zero code exists in system/ runtime)
```
