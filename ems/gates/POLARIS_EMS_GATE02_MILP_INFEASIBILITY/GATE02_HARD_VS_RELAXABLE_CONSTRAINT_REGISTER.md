# POLARIS GATE-02 — HARD VS RELAXABLE CONSTRAINT REGISTER
## FORMAL CLASSIFICATION REGISTER OF SYSTEM CONSTRAINTS AND OBJECTIVES

---

## 1. COMPREHENSIVE CONSTRAINT & OBJECTIVE REGISTER

```text
+----------------------------------------------------------------------------------------------------+
| CONSTRAINT / OBJECTIVE NAME      | TIER CATEGORY        | RELAXATION RULE      | GOVERNANCE STATUS |
+----------------------------------+----------------------+----------------------+-------------------+
| Critical Load Demand             | Tier A (Hard)        | NEVER RELAX          | SEALED MANDATE    |
| Busbar Power Balance             | Tier A (Hard)        | NEVER RELAX          | SEALED MANDATE    |
| Diesel Generator Max Power       | Tier A (Hard)        | NEVER RELAX          | PHYSICAL LIMIT    |
| Battery Capacity Max Wh          | Tier A (Hard)        | NEVER RELAX          | PHYSICAL LIMIT    |
| Battery Physical Min SOC         | Tier A (Hard)        | NEVER RELAX          | ASSET SAFETY      |
| Flexible Load Service            | Tier B (Relaxable)   | Governed Relaxation  | AUTHORIZED (C)    |
| Interruptible Load Service       | Tier B (Relaxable)   | Governed Relaxation  | AUTHORIZED (C)    |
| Renewable Curtailment Limit      | Tier B (Relaxable)   | Governed Relaxation  | AUTHORIZED (C)    |
| Operational Battery SOC Reserve  | Tier B (Relaxable)   | Governed Relaxation  | GOVERNANCE_REQ    |
| Terminal Horizon SOC Reserve Target| Tier B (Relaxable)  | Governed Relaxation  | GOVERNANCE_REQ    |
| Generator Min Up/Down Time       | Tier C (Engineering) | Conditional Slack    | GOVERNANCE_REQ    |
| Generator Ramping Limit          | Tier C (Engineering) | Conditional Slack    | GOVERNANCE_REQ    |
| J1 Fuel Consumption              | Tier D (Objective)   | N/A (Cost Weight)    | PROTECTED TERM    |
| J2 Battery Degradation           | Tier D (Objective)   | N/A (Cost Weight)    | PROTECTED TERM    |
| J3 Renewable Utilization         | Tier D (Objective)   | N/A (Cost Weight)    | PROTECTED TERM    |
| J4 Operational Stability         | Tier D (Objective)   | N/A (Cost Weight)    | PROTECTED TERM    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. DETAILED TIER DEFINITIONS

### Tier A: Hard Constraints (Never Relax)
- **Critical Load ($L_{\text{critical}}$)**: Must be satisfied 100% in every timestep $k \in \{0, \dots, 24\}$. Infeasibility in critical load requires failure escalation, never soft penalty relaxation.
- **Physical Conservation Laws**: Busbar energy conservation $\sum P_{\text{gen}} = \sum P_{\text{load}}$ cannot be mathematically violated.
- **Physical Hardware Safety Limits**: Battery minimum physical SOC (e.g. $10\%$) and generator maximum nameplate rating ($50\text{ kW}$) cannot be exceeded without risk of physical equipment destruction.

### Tier B: Governed-Relaxable Constraints
- **Flexible & Interruptible Loads**: Non-essential commercial or industrial loads that may be shed or deferred to restore critical system balance.
- **Renewable Curtailment**: Permitting solar/wind output to be spilled or curtailed when system generation exceeds total load and battery charge capacity.
- **Reserve Targets**: Operational buffer reserves (SOC reserve, spinning reserve, terminal SOC target) that preserve long-term health but may be temporarily encroached upon during emergency or tight operational conditions.

### Tier C: Engineering & Model Constraints
- Ramping limits and minimum run-time requirements arising from mechanical generator constraints. May be relaxed via soft slacks under strict physical validator review.

### Tier D: Objective Preferences (J1–J4)
- Lexicographic or weighted cost terms in the objective function ($J_1$ fuel, $J_2$ degradation, $J_3$ renewables, $J_4$ stability). These express optimization preferences, **NOT physical constraints**, and are evaluated natively by the optimizer without constraint relaxation.
