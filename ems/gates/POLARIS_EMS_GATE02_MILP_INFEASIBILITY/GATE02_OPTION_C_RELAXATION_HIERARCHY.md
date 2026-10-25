# POLARIS GATE-02 — OPTION C RELAXATION HIERARCHY SPECIFICATION
## CONCEPTUAL CONSTRAINT CLASSIFICATION & GOVERNED RESOLVE PROTOCOL

---

## 1. CONCEPTUAL CONSTRAINT CLASSIFICATION HIERARCHY

The POLARIS EMS optimization problem constraints and preference terms are classified into four distinct conceptual tiers:

```text
+----------------------------------------------------------------------------------+
| TIER A: HARD CONSTRAINTS — NEVER RELAX                                            |
| - Critical Load Service ($L_{\text{critical}}[k]$)                               |
| - Physical Power Balance ($P_{\text{diesel}} + P_{\text{batt}} + P_{\text{renew}} = L_{\text{served}}$)|
| - Physical Asset Operating Bounds ($P_{\text{diesel, max}}$, $SOC_{\text{min, physical}}$) |
+----------------------------------------------------------------------------------+
                                        │ (If Infeasible)
                                        ▼
+----------------------------------------------------------------------------------+
| TIER B: GOVERNED-RELAXABLE CONSTRAINTS                                           |
| - Flexible / Non-Critical Load Service                                           |
| - Interruptible Load Shedding                                                    |
| - Renewable Curtailment Limits                                                   |
| - Operational Battery Reserve Targets ($SOC_{\text{reserve}}$)                    |
| - Horizon Terminal SOC Target ($SOC[24] \ge SOC_{\text{target}}$)                 |
+----------------------------------------------------------------------------------+
                                        │ (Lower Priority)
                                        ▼
+----------------------------------------------------------------------------------+
| TIER C: ENGINEERING / MODEL CONSTRAINTS                                          |
| - Generator Ramping Limits ($dP_{\text{diesel}}/dt$)                             |
| - Generator Min Up/Down Operating Time Constraints                               |
| - Battery C-Rate Operational Limits                                              |
+----------------------------------------------------------------------------------+
                                        │ (Non-Constraint Objective Terms)
                                        ▼
+----------------------------------------------------------------------------------+
| TIER D: REPORTING / PREFERENCE OBJECTIVES (J1 / J2 / J3 / J4)                     |
| - J1: Fuel Consumption Minimization Preference                                  |
| - J2: Battery Degradation / Cycling Preference                                   |
| - J3: Renewable Utilization Preference                                          |
| - J4: Operational Stability / Smoothness Preference                             |
+----------------------------------------------------------------------------------+
```

---

## 2. GOVERNED PRIORITY ORDERING & STATUS

| Constraint / Preference Element | Classification Tier | Relaxation Permitted? | Governance Priority Status |
| :--- | :--- | :--- | :--- |
| **Critical Load Service** | **Tier A (HARD)** | **NEVER** | **HARD_NEVER_RELAX** |
| **Physical Busbar Power Balance** | **Tier A (HARD)** | **NEVER** | **HARD_NEVER_RELAX** |
| **Physical Battery Min/Max Limits**| **Tier A (HARD)** | **NEVER** | **HARD_NEVER_RELAX** |
| **Terminal SOC Reserve Target** | **Tier B (GOVERNED)** | **YES (Prioritized)** | `GOVERNANCE_DECISION_REQUIRED` (Numerical Penalty Undefined) |
| **Operational Battery SOC Reserve**| **Tier B (GOVERNED)** | **YES (Prioritized)** | `GOVERNANCE_DECISION_REQUIRED` (Numerical Penalty Undefined) |
| **Flexible / Non-Critical Load** | **Tier B (GOVERNED)** | **YES (Prioritized)** | `GOVERNED_RELAXATION_ALLOWED` |
| **Interruptible Load** | **Tier B (GOVERNED)** | **YES (Prioritized)** | `GOVERNED_RELAXATION_ALLOWED` |
| **Renewable Curtailment** | **Tier B (GOVERNED)** | **YES (Prioritized)** | `GOVERNED_RELAXATION_ALLOWED` |
| **Generator Ramping / Min-Time** | **Tier C (ENGINEERING)**| **CONDITIONAL** | `GOVERNANCE_DECISION_REQUIRED` |
| **Stage Objectives (J1-J4)** | **Tier D (PREFERENCE)** | N/A (Objective Term) | Protected Lexicographic / Weighted Priorities |

*Note: No numerical penalty weights ($\lambda$), slack variable bounds ($\epsilon_{\text{max}}$), or tolerance thresholds have been invented in this document. Numerical parameterization remains `GOVERNANCE_DECISION_REQUIRED`.*

---

## 3. GOVERNED RESOLVE PROTOCOL & FEASIBILITY SEMANTICS

When Option C is implemented in future releases, runtime solver execution MUST follow this strict multi-pass sequence:

```text
Pass 1: Original MILP Solve (Option B / GAP19 HiGHS)
        │
        ├──► Returns OPTIMAL ──► Dispatch Plan published ──► DigitalTwinSimulator.step()
        │
        └──► Returns MILP_INFEASIBLE
                 │
                 ▼
Pass 2: Governed Constraint Relaxation Re-Solve
        - Soften ONLY authorized Tier B constraints (e.g., flexible load, terminal SOC target).
        - Enforce Tier A Critical Load as strict hard boundary.
        - Generate mandatory Operator Notification Event.
        │
        ├──► Returns FEASIBLE RELAXED PLAN
        │         │
        │         └──► Relaxed Dispatch Plan published ──► DigitalTwinSimulator.step()
        │
        └──► STILL INFEASIBLE
                  │
                  ▼
          STOP & CONTAIN (GOVERNANCE_DECISION_REQUIRED)
          - DO NOT invent a secondary un-governed relaxation pass.
          - DO NOT execute zero dispatch / blackout.
          - DO NOT advance Digital Twin state.
          - DO NOT invoke Option D automatically.
          - Hold current StationState as authoritative.
```

---

## 4. FIREWALL SUMMARY

- **J1/J2/J3/J4 Priority Hierarchy**: Untouched and protected. Objective terms are not conflated with physical constraints.
- **No Numerical Inventions**: Penalty weights, slack bounds, and relaxation parameters are NOT defined in this specification and will require separate governance approval before implementation.
