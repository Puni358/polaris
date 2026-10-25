# CONSTRAINT MINIMUMITY AUDIT

## JUSTIFICATION AND MINIMUMITY AUDIT FOR NEW CONSTRAINTS

1. **Critical Demand Balance (24 constraints)**: Required to link served critical load and unmet critical load to the external dynamic critical demand input $P_{\text{demand,crit}}(t)$.
2. **EBR Reserve Shortfall (24 constraints)**: Required to bound the $s_{\text{EBR}}(t)$ slack variable against the dynamic reserve target $E_{\text{EBR\_target}}(t)$.
3. **Terminal Reserve Shortfall (1 constraint)**: Required to bound the $s_{\text{term}}$ slack variable against the terminal target $E_{\text{term\_target}}$.
4. **Option D Mode Constraints (24 conditional constraints)**: Required to enforce sealed Option D critical-only battery discharge policy when operating in EMERGENCY mode.

`MINIMUMITY_AUDIT` = `PASS`
