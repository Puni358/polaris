# CONSTRAINT INDEX AUDIT

## CONSTRAINT MATRIX INDEXING AND INTEGRITY MAP ($0 \dots 312$)

| Constraint Row Range | Constraint Group | Count | Mathematical Form | Matrix Bounds |
|---|---|---|---|---|
| $0 \dots 263$ | Base Physical Constraints | 264 | See `CURRENT_BASE_MODEL.md` | Equalities & Inequalities |
| $264 \dots 287$ | Critical Demand Balance | 24 | $P_{\text{served,crit}} + P_{\text{unmet,crit}} = P_{\text{demand,crit}}$ | Equalities ($= P_{\text{demand,crit}}$) |
| $288 \dots 311$ | EBR Shortfall Relations | 24 | $E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR\_target}}(t)$ | Lower bounds ($[E_{\text{EBR\_target}}, \infty)$) |
| $312$ | Terminal Reserve Relation | 1 | $E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}$ | Lower bound ($[E_{\text{term\_target}}, \infty)$) |

Index range $0 \dots 312 \implies 313$ rows. Zero collisions, zero missing rows.
