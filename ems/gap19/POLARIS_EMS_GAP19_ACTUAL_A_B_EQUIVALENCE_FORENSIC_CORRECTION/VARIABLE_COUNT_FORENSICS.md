# VARIABLE COUNT FORENSICS

## THE 360 → 385 DISCREPANCY ANALYSIS

```text
385 (Experiment) - 360 (Production) = 25 Additional Variables
```

### BREAKDOWN OF THE 25 ADDITIONAL VARIABLES

1. **$24 \times s_{\text{EBR}}(t)$ Continuous Slack Variables**:
   - Purpose: Represents emergency battery reserve energy shortfall at each timestep $t \in \{0, \dots, 23\}$.
   - Governance Source: GAP19 Stage 2 multi-objective formulation ($J_2$ objective).
   - Status in Production: Not present in current historical `milp.py`.
2. **$1 \times s_{\text{term}}$ Continuous Slack Variable**:
   - Purpose: Represents terminal battery energy shortfall at the end of horizon $t=23$.
   - Governance Source: GAP19 Stage 2 multi-objective formulation ($J_2$ objective).
   - Status in Production: Not present in current historical `milp.py`.

### INTEGRALITY DIFFERENCE (96 vs 120 BINARY VARIABLES)

- Production `milp.py` contains 4 binary variables per timestep ($u_{\text{chg}}, u_{\text{dis}}, u_{\text{diesel}}, v_{\text{start}}$) $\implies 96$ binaries.
- Experiment model includes $w_{\text{stop}}(t)$ (shutdown transition binary) $\implies 5$ binaries per step $\times 24 = 120$ binaries.

```text
ADDITIONAL_STAGE2_VARIABLES = 25
VARIABLE_COUNT_MATCH = NO
```
