# CONSTRAINT COUNT AUDIT

## RECONSTRUCTION OF THE 313 CONSTRAINTS

- **Base Constraints**: 264 linear constraints ($11 \times 24$ steps)
- **Layer B Critical Load Balances**: 24 linear constraints ($P_{\text{served,crit}} + P_{\text{unmet,crit}} = P_{\text{demand,crit}}$)
- **Layer C EBR Shortfall Constraints**: 24 linear constraints ($E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR\_target}}(t)$)
- **Layer C Terminal Shortfall Constraint**: 1 linear constraint ($E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}$)
- **Total Linear Constraints**: $264 + 24 + 24 + 1 = 313$.

```text
CONSTRAINT_COUNT = PASS
```
