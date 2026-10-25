# CONSTRAINT COUNT FORENSICS

## CONSTRAINT AUDIT AND STRUCTURE COMPARISON

```text
Production Base Constraints = 264
Experiment Constraints = 265
Net Difference = +1 Constraint
```

### STRUCTURAL RECONCILIATION

1. **Elimination of $p_{\text{served}}$ Variable & Constraint Consolidation**:
   - Production `milp.py` maintains separate Bus-Bar Balance (24) and Demand Deficit Balance (24) constraints using the explicit served power variable $p_{\text{served}}(t)$ ($24 + 24 = 48$ constraints).
   - Experiment model combined these into a single direct Power Balance constraint per timestep ($P_{\text{diesel}} + P_{\text{batt,dis}} + P_{\text{pv,use}} + P_{\text{wind,use}} + P_{\text{unmet}} - P_{\text{batt,ch}} = P_{\text{load}}$), saving 24 constraints ($264 - 24 = 240$ base constraints).
2. **Addition of 25 Stage-2 Constraints**:
   - Emergency Battery Reserve Slack Relations: $E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge 3000$ ($24$ constraints)
   - Terminal Battery Energy Relation: $E_{\text{batt}}(23) + s_{\text{term}} \ge 5000$ ($1$ constraint)
   - Total Stage-2 Constraints added: 25 constraints.
3. **Total Calculation**:
   - $240 \text{ (Consolidated Base)} + 25 \text{ (Stage-2 Slacks)} = 265 \text{ constraints}$.

```text
ADDITIONAL_STAGE2_CONSTRAINTS = 25
CONSTRAINT_COUNT_MATCH = NO
```
