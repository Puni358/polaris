# Constraint Index Forensics

Constraint matrix $A$ rows and indexing audit:

| Row Index Range | Count | Purpose | Physical Relation |
| :--- | :---: | :--- | :--- |
| `0 .. 263` | 264 | Base Production Constraints ($11 \times 24$) | Solar/Wind decomp, Bus balance, Load balance, Charge/Discharge bounds, Battery SOC transition, Diesel min/max/startup |
| `264 .. 287` | 24 | Layer B: Critical Balance | $P_{\text{served}}[t] + P_{\text{unmet,critical}}[t] == P_{\text{critical\_demand}}[t]$ |
| `288 .. 311` | 24 | Layer C: EBR Shortfall | $E_{\text{next}}[t] + s_{\text{EBR}}[t] \ge E_{\text{EBR\_target}}[t]$ |
| `312` | 1 | Layer C: Terminal Shortfall | $E_{\text{next}}[23] + s_{\text{terminal}} \ge E_{\text{terminal\_target}}$ |

Total Constraints in NORMAL mode: $264 + 24 + 24 + 1 = 313$.

`CONSTRAINT_INDEXING = PASS`
