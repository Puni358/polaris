# POLARIS GATE-02 — POLICY BOUNDARY
## AUTHORITATIVE GOVERNANCE BOUNDARIES & UNRESOLVED DECISIONS

---

## 1. AUTHORITATIVE HUMAN POLICY BOUNDARIES (SEALED)

The following policy boundaries are immutable and govern all future implementation:

```text
+-----------------------------------------------------------------------------------------+
| BOUNDARY ID | GOVERNANCE RULE STATEMENT                                                  |
+-------------+---------------------------------------------------------------------------+
| G02-PB-01   | Critical load is compulsory and MUST NEVER be relaxed under any pass.     |
| G02-PB-02   | Non-critical/flexible load relaxation is permitted ONLY via governed tier.|
| G02-PB-03   | Arbitrary multi-pass relaxation by optimizer is STRICTLY PROHIBITED.      |
| G02-PB-04   | Operator-visible notification is MANDATORY for every relaxation event.    |
| G02-PB-05   | MILP_INFEASIBLE != EMERGENCY. Option D MUST NOT be invoked automatically.|
| G02-PB-06   | MILP_INFEASIBLE != UNKNOWN_INVALID. Gate-01 remains strictly separate.    |
| G02-PB-07   | State advancement MUST NOT occur before a valid governed dispatch exists. |
+-----------------------------------------------------------------------------------------+
```

---

## 2. EXPLICITLY UNRESOLVED POLICY DECISIONS

The following items are NOT authorized human decisions and remain `GOVERNANCE_UNRESOLVED`:

1. **Non-Critical Load Shedding Priority Order**: Whether flexible heating, water treatment, or EV charging is shed first during a Tier 2 relaxation pass.
2. **Battery Reserve Encroachment Policy**: Whether operational battery reserves ($SOC_{\text{reserve}}$) may be encroached upon before shedding non-critical load.
3. **Terminal SOC Reserve Target Relaxation**: Absolute maximum percentage drop allowed for $SOC[24]$ during Tier 3 relaxation.
4. **Numerical Objective Penalty Weights ($\lambda_i$)**: Mathematical values for penalty slack terms in the MILP objective function.
5. **Notification Transport Specifications**: SCADA protocol, UI API endpoints, and database schemas for operator event delivery.

---

## 3. PROHIBITED IMPLEMENTATION INVENTIONS

Developers and AI assistants MUST NOT:
- Invent numerical slack weights or penalty factors.
- Hardcode arbitrary load-shedding percentages.
- Invent automated secondary retry passes if Tier 2 relaxation fails.
- Re-open Gate-01 or merge `UNKNOWN_INVALID` logic with Gate-02.
