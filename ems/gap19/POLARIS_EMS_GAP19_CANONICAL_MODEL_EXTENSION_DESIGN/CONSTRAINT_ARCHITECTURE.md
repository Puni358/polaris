# CONSTRAINT ARCHITECTURE

## CANONICAL TARGET CONSTRAINT BREAKDOWN (313 TOTAL CONSTRAINTS)

| Layer | Constraint Group | Count | Mathematical Equation | Purpose |
|---|---|---|---|---|
| **Layer A** | Base Physical Constraints | 264 | See `CURRENT_BASE_MODEL.md` | Asset power, energy, exclusivity |
| **Layer B** | Critical Demand Balance | 24 | $P_{\text{served,crit}}(t) + P_{\text{unmet,crit}}(t) = P_{\text{demand,crit}}(t)$ | Critical load tracking |
| **Layer C** | EBR Reserve Shortfall | 24 | $E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR\_target}}(t)$ | Stage-2 emergency reserve relation |
| **Layer C** | Terminal Reserve Shortfall | 1 | $E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}$ | Stage-2 terminal energy relation |
| **Layer D** | Option D Critical Discharge | 24 (Cond) | $P_{\text{batt,dis}}(t) \le P_{\text{served,crit}}(t)$ in EMERGENCY | Critical-only battery discharge |

- **Total Linear Constraints ($M_{\text{target}}$)**: 313
