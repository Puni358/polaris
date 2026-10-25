# POLARIS EMS GAP19 — ECD EMERGENCY AUTHORITY CONTRACT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Contract Status**: `SEALED_GOVERNANCE_CONTRACT`  

---

## 1. Governance Directive (Decision D3)

**ECD IS THE SOLE EMERGENCY AUTHORITY.**

The Emergency Condition Detector (ECD) is the exclusive system module authorized to evaluate station survivability and declare `EMERGENCY = TRUE`.

---

## 2. Strict Conceptual Separation

To eliminate ambiguity across control, optimization, and fallback layers:

| Layer / Component | System Role | Authorized Output | What It Must NOT Do |
| :--- | :--- | :--- | :--- |
| **$J2$ Reserve Shortfall** | Informational & soft optimization penalty | $J2 = \sum s_{\text{J2}}[t]$ telemetry | Must NOT declare emergency or trigger load shedding. |
| **MILP Infeasibility** | Downstream solver numerical status | `OPTIMIZATION_INFEASIBLE` signal | Must NOT trip emergency mode or execute blackout. |
| **ECD Engine** | Sole Emergency Authority | `NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID` | Must NOT compute optimal economic dispatch. |
| **Option D Fallback** | Governed emergency fallback policy | Protected critical dispatch plan (D1–D6) | Must NOT activate without ECD emergency declaration. |
| **Authority Escalation** | Operator notification pathway | External alert transmission | Must NOT modify station physical dispatch. |

---

## 3. Operational Rules

1. **Rule D3-1**: $J2 > 0$ **MUST NOT** automatically set `EMERGENCY = TRUE`.
2. **Rule D3-2**: MILP solver infeasibility **MUST NOT** automatically set `EMERGENCY = TRUE`.
3. **Rule D3-3**: Emergency mode is evaluated strictly by ECD using authenticated, fresh telemetry and survivability window $T_{\text{required}}$ rules.
