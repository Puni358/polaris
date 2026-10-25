# J1 Forensic Audit

- **Governed Expression**: $J_1 = \sum_{t=0}^{23} P_{\text{unmet,critical}}[t] \cdot \Delta t$
- **Units**: Watt-hours (Wh)
- **Vector Representation**: $c_1 \in \mathbb{R}^{409}$, where $c_1[360 + t] = 1.0 \times \Delta t$ for $t=0..23$, and all other entries are $0.0$.
- **Objective Direction**: Minimization (`priority = 1`, `weight = 1.0`).

`J1 = PASS`
