# POLARIS GATE-02 — RELAXATION HIERARCHY PROPOSAL
## PROPOSED GOVERNANCE TIER STRUCTURE & RE-SOLVE SEQUENCE

---

## 1. PROPOSED TIERED RELAXATION HIERARCHY

```text
+--------------------------------------------------------------------------------------+
| TIER 1: HARD — NEVER RELAX (Human-Authorized Mandate)                                |
| - Critical Load Service ($L_{\text{critical}}[k]$ = 100% compulsory)                 |
| - Physical Busbar Power Balance ($\sum P_{\text{gen}} = \sum P_{\text{load}}$)       |
| - Asset Physical Safety Bounds ($SOC_{\text{min, physical}}$, $P_{\text{diesel, max}}$) |
+--------------------------------------------------------------------------------------+
                                           │
                                           │ (If Primary Solve Infeasible)
                                           ▼
+--------------------------------------------------------------------------------------+
| TIER 2: GOVERNED RELAXABLE (Human-Authorized Category / Priority Order Unresolved)  |
| - Non-Critical / Flexible Load Shedding                                              |
| - Interruptible Load Shedding                                                        |
| - Renewable Curtailment Limits                                                       |
| Status: GOVERNED_RELAXATION_ALLOWED (Internal Priority Order: GOVERNANCE_UNRESOLVED) |
+--------------------------------------------------------------------------------------+
                                           │
                                           │ (Secondary Buffer Encroachment)
                                           ▼
+--------------------------------------------------------------------------------------+
| TIER 3: GOVERNANCE-UNRESOLVED RESERVES (Proposed by Agy / Requires Human Authorization)|
| - Operational Battery SOC Reserve ($SOC_{\text{reserve}}$)                            |
| - Horizon Terminal SOC Target ($SOC[24] \ge SOC_{\text{target}}$)                     |
| Status: GOVERNANCE_UNRESOLVED (Allowable encroachment bounds & penalties undefined)  |
+--------------------------------------------------------------------------------------+
                                           │
                                           │ (Model / Mechanical Bounds)
                                           ▼
+--------------------------------------------------------------------------------------+
| TIER 4: ENGINEERING-CONDITIONAL CONSTRAINTS (Proposed by Agy / Requires Engineering Review)|
| - Generator Ramping Limits ($dP_{\text{diesel}}/dt$)                                 |
| - Generator Min Up/Down Time Constraints                                             |
| Status: ENGINEERING_CONDITIONAL                                                      |
+--------------------------------------------------------------------------------------+
```

---

## 2. RE-SOLVE SEQUENCE & TERMINATION SEMANTICS

```text
Pass 1: Primary MILP Solve (Option B / HiGHS)
        │
        ├──► OPTIMAL ──► Publish DispatchPlan ──► DigitalTwinSimulator.step()
        │
        └──► MILP_INFEASIBLE
                 │
                 ▼
Pass 2: Governed Relaxation Re-Solve Pass
        - Soften ONLY Tier 2 Governed Relaxable constraints.
        - Enforce Tier 1 Critical Load as HARD NEVER RELAX.
        - Generate Mandatory Operator Notification Event.
        │
        ├──► FEASIBLE RELAXED PLAN
        │         │
        │         └──► Publish Relaxed DispatchPlan ──► DigitalTwinSimulator.step()
        │
        └──► STILL INFEASIBLE
                  │
                  ▼
          STOP & CONTAIN (GOVERNANCE_DECISION_REQUIRED)
          - DO NOT invent Pass 3 arbitrary relaxations.
          - DO NOT execute zero dispatch / blackout.
          - DO NOT advance Digital Twin state.
          - DO NOT invoke Option D automatically.
          - Preserve current StationState as authoritative.
```

---

## 3. IMPLEMENTATION CONSEQUENCES

1. **MILP Formulation Requirement**: Implementation will require introducing explicit slack variables ($\epsilon_{\text{flex}} \ge 0$) attached ONLY to non-critical load terms.
2. **Critical Load Protection**: Critical load constraints in `milp.py` / `gap19_highs_native.py` must retain strict zero-slack formulation ($\epsilon_{\text{critical}} = 0$).
3. **Event Notification Payload**: A structured event payload generator must be built into `runner.py` to publish relaxation metadata prior to re-solve execution.
