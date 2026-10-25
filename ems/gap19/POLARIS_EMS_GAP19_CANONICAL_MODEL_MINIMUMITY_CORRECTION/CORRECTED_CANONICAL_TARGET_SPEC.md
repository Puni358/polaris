# CORRECTED CANONICAL TARGET SPECIFICATION

## MATHEMATICAL SPECIFICATION OF AUDITED MINIMUM TARGET MILP (409 VARS, 313 CONSTRAINTS)

- **Horizon $H$**: 24 hours ($t \in \{0, \dots, 23\}$)
- **Time step $\Delta t$**: 1.0 hour
- **Total Variables ($N_{\text{min}}$)**: 409
  - Binary variables: 96 ($u_{\text{chg}}, u_{\text{dis}}, u_{\text{diesel}}, v_{\text{start}}$ for $t=0..23$)
  - Continuous variables: 313 ($264 \text{ base} + 24 P_{\text{unmet,crit}} + 24 s_{\text{EBR}} + 1 s_{\text{term}}$)
- **Total Linear Constraints ($M_{\text{min}}$)**: 313
  - Base physical constraints: 264
  - Critical demand balance constraints: 24
  - Emergency battery reserve shortfall constraints: 24
  - Terminal energy reserve shortfall constraint: 1
- **Objective Structure**: 4-stage lexicographic vector $[J_1, J_2, J_3, J_4]$ mapped natively to HiGHS Option B (`highspy.HighsLinearObjective`).
