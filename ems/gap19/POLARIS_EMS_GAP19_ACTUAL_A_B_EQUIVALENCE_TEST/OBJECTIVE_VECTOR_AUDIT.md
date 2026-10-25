# OBJECTIVE VECTOR AUDIT

## OBJECTIVE COEFFICIENT VECTOR COMPARISON

The objective vectors $c_1, c_2, c_3, c_4$ were constructed independently for Option A and Option B using identical rules.

| Objective | Nonzero Variables | Coefficient Values | Units | Hierarchy Priority |
|---|---|---|---|---|
| $c_1$ ($J_1$) | $P_{\text{unmet}}(t)$ ($t=0..23$) | $1.0 \cdot \Delta t = 1.0$ | Wh | Priority 1 (Highest) |
| $c_2$ ($J_2$) | $s_{\text{EBR}}(t)$ ($t=0..23$), $s_{\text{term}}$ | $1.0$ | Wh | Priority 2 |
| $c_3$ ($J_3$) | $P_{\text{diesel}}(t)$, $u_{\text{diesel}}(t)$, $v_{\text{start}}(t)$ | $0.00025, 5.0, 6.0$ | Liters | Priority 3 |
| $c_4$ ($J_4$) | $P_{\text{pv,curt}}(t)$, $P_{\text{wind,curt}}(t)$ | $1.0 \cdot \Delta t = 1.0$ | Wh | Priority 4 (Lowest) |

- `c_A1 == c_B1` : `PASS`
- `c_A2 == c_B2` : `PASS`
- `c_A3 == c_B3` : `PASS`
- `c_A4 == c_B4` : `PASS`

`OBJECTIVE_IDENTITY` = `PASS`
