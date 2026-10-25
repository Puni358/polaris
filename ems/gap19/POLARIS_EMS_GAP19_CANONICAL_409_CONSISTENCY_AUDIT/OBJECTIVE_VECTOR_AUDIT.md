# OBJECTIVE VECTOR AUDIT

## SEPARATION OF OBJECTIVE VECTORS c1, c2, c3, c4

Every objective vector $c_1, c_2, c_3, c_4$ has length $N=409$ and nonzeros strictly partitioned by stage:
- $c_1$: Nonzeros only at $P_{\text{unmet,crit}}(t)$ indices ($360 \dots 383$).
- $c_2$: Nonzeros only at $s_{\text{EBR}}(t)$ ($384 \dots 407$) and $s_{\text{term}}$ ($408$) indices.
- $c_3$: Nonzeros only at $P_{\text{diesel}}(t)$, $u_{\text{diesel}}(t)$, $v_{\text{start}}(t)$ indices.
- $c_4$: Nonzeros only at $P_{\text{pv,curt}}(t)$, $P_{\text{wind,curt}}(t)$ indices.

Objectives are mutually disjoint in nonzeros ($c_i \cdot c_j = 0$ for $i \ne j$). Strict stage separation holds.
