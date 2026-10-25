# J3 Fuel Objective Forensics

- **Governed Expression**: $J_3 = \sum_{t=0}^{23} [F_{\text{marg}} P_{\text{diesel}}[t] + F_{\text{base}} u_{\text{diesel}}[t] + F_{\text{start}} v_{\text{start}}[t]] \cdot \Delta t$
- **Units**: Physical Liters (L)
- **Vector Representation**: $c_3 \in \mathbb{R}^{409}$, nonzeros at `base + 7` ($F_{\text{marg}} \Delta t$), `base + 13` ($F_{\text{base}} \Delta t$), and `base + 14` ($F_{\text{start}}$).
- **Objective Direction**: Minimization (`priority = 3`, `weight = 1.0`).
- **Monetary Penalty Firewall**: Zero monetary scalar penalties ($/Wh) mixed into $J_3$.

`J3 = PASS`
