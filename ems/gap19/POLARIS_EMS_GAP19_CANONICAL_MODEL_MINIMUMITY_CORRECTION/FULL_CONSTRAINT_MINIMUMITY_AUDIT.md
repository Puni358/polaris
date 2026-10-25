# FULL CONSTRAINT MINIMUMITY AUDIT

## EVALUATION OF PROPOSED CONSTRAINTS (+49 CONSTRAINTS)

1. **Base Physical Constraints**: 264 linear constraints (Retained from base `milp.py`).
2. **Critical Demand Balance Constraints**: 24 linear constraints ($P_{\text{served,crit}} + P_{\text{unmet,crit}} = P_{\text{demand,crit}}$). Status: `REQUIRED_FOR_OBJECTIVE`.
3. **EBR Reserve Shortfall Constraints**: 24 linear constraints ($E_{\text{batt}} + s_{\text{EBR}} \ge E_{\text{EBR\_target}}$). Status: `REQUIRED_FOR_OBJECTIVE`.
4. **Terminal Reserve Shortfall Constraint**: 1 linear constraint ($E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}$). Status: `REQUIRED_FOR_OBJECTIVE`.

- **Total Audited Constraints ($M_{\text{min}}$)**: $264 + 24 + 25 = \mathbf{313}$ linear constraints.

```text
313_CONSTRAINT_CLAIM = VALIDATED
CONSTRAINT_COUNT_STATUS = MINIMUM
```
