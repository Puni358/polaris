# Constraint Classification Audit

| Constraint Category | Count | Index Range | Description |
| :--- | :--- | :--- | :--- |
| Baseline Constraints | 264 | 0 .. 263 | Energy balance, SOC evolution, power limits, diesel startup logic |
| Critical Load Constraints | 24 | 264 .. 287 | $P_{\text{served}}[t] + P_{\text{unmet,crit}}[t] = P_{\text{crit,dem}}[t]$ |
| EBR Shortfall Constraints | 24 | 288 .. 311 | $E_{\text{next}}[t] + s_{\text{EBR}}[t] \ge E_{\text{EBR,target}}$ |
| Terminal Reserve Constraint | 1 | 312 | $E_{\text{next}}[23] + s_{\text{terminal}} \ge E_{\text{terminal,target}}$ |
| Emergency Discharge Constraints | 24 (Conditional) | 313 .. 336 | $P_{\text{discharge}}[t] \le P_{\text{served}}[t]$ (If `EMERGENCY` mode active) |
