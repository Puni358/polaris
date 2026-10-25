# J2 TERMINAL RESERVE AUDIT

## INDEPENDENCE OF TERMINAL RESERVE SLACK

- **Shortfall Equation**: $s_{\text{term}} \ge E_{\text{term\_target}} - E_{\text{batt}}(23)$.
- **Double-Counting Audit**: $s_{\text{term}}$ represents terminal energy capacity shortfall for lookahead continuity into the next optimization window ($H+1 \dots 2H$), distinct from hourly emergency reserve slacks $s_{\text{EBR}}(t)$.
- **Numerical Target**: $E_{\text{term\_target}}$ is a parameter (e.g. 50% SOC). Status: `GOVERNANCE_REQUIRED`.
