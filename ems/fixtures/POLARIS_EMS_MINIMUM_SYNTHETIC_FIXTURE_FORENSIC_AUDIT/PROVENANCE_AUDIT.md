# PROVENANCE AUDIT
## PARAMETER CLASSIFICATION & PROVENANCE AUDIT

### 1. PROVENANCE CLASSIFICATION AUDIT RESULTS
- `SYNTHETIC_ENGINEERING_ASSUMPTION`: $30\text{ kW}$ critical load ($15/10/5\text{ kW}$ split), $15\text{ kW}$ flexible load, persistence $+10\%$ forecast bias rule.
- `REUSED_EXISTING_PROTOTYPE_PARAMETER`: Solar $0\text{--}50\text{ kW}$ curve, Wind $0\text{--}20\text{ kW}$ curve, $200\text{ kWh}$ battery capacity, $20\%$ SOC min floor, $95\%$ SOC max ceiling, $50\text{ kW}$ max battery power, $10\text{--}60\text{ kW}$ diesel bounds, $F = 5.0\cdot u + 0.25\cdot P$ fuel model, $500\text{L}/20\text{L}/10\text{L}$ fuel states.
- `SEALED_HUMAN_GOVERNANCE_DECISION`: $T_{\text{required\_baseline}} = 6.0\text{h}$, Option D (`DEC-004`).

### 2. CONCLUSION
`PROVENANCE_STATUS = PASS`.
