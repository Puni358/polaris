# CANONICAL 409 RECONSTRUCTION

## MATHEMATICAL RECONSTRUCTION OF THE 409-VARIABLE TARGET MILP

```text
N_target = N_base (360) + N_crit_unmet (24) + N_EBR_slack (24) + N_term_slack (1) = 409
M_target = M_base (264) + M_crit_balance (24) + M_EBR_shortfall (24) + M_term_shortfall (1) = 313
```

- **Horizon $H$**: 24 hours ($t \in \{0, \dots, 23\}$)
- **Time step $\Delta t$**: 1.0 hour
- **Binary Variables**: 96 (Retained 100% from base `milp.py`: `u_chg`, `u_dis`, `u_diesel`, `v_start` for $t=0..23$)
- **Continuous Variables**: 313 ($264 \text{ base} + 24 P_{\text{unmet,crit}} + 24 s_{\text{EBR}} + 1 s_{\text{term}}$)
