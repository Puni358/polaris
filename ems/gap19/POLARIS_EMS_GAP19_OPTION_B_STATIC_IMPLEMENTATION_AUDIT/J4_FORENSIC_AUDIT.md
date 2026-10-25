# J4 Curtailment Objective Forensics

- **Governed Expression**: $J_4 = \sum_{t=0}^{23} [P_{\text{curt,sol}}[t] + P_{\text{curt,wind}}[t]] \cdot \Delta t$
- **Units**: Watt-hours (Wh)
- **Vector Representation**: $c_4 \in \mathbb{R}^{409}$, nonzeros at `base + 2` ($1.0 \times \Delta t$) and `base + 3` ($1.0 \times \Delta t$).
- **Objective Direction**: Minimization (`priority = 4`, `weight = 1.0`).

`J4 = PASS`
