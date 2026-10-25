# FROZEN MODEL SPECIFICATION

## MATHEMATICAL FORMULATION OF FROZEN POLARIS MILP INSTANCE

- **Horizon**: $H = 24$ hours (steps $t \in \{0, \dots, 23\}$)
- **Time step**: $\Delta t = 1.0$ hour
- **Decision Variables**: $N = 385$
  - Standard per-timestep variables: $15 \times 24 = 360$
  - Stage 2 EBR slacks: $24$ ($s_{\text{EBR}}(t)$)
  - Stage 2 Terminal energy slack: $1$ ($s_{\text{term}}$)
- **Integrality**:
  - $120$ binary variables ($u_{\text{diesel}}, v_{\text{start}}, w_{\text{stop}}, u_{\text{ch}}, u_{\text{dis}}$ for $t=0..23$)
  - $265$ continuous variables
- **Constraints**: $M = 265$ linear constraints
  - Power Balance (24 equality constraints)
  - Diesel Min Output (24 inequality constraints)
  - Diesel Max Output (24 inequality constraints)
  - Diesel Status Transition (24 equality constraints)
  - Battery Charge Power Bound (24 inequality constraints)
  - Battery Discharge Power Bound (24 inequality constraints)
  - Battery Charge/Discharge Exclusivity (24 inequality constraints)
  - Energy Dynamics (24 equality constraints)
  - Solar Generation Balance (24 equality constraints)
  - Wind Generation Balance (24 equality constraints)
  - Emergency Battery Reserve Slack Relation (24 inequality constraints)
  - Terminal Battery Energy Constraint (1 inequality constraint)

## OBJECTIVE VECTOR SPECIFICATION

1. **$J_1$ (Critical Reliability)**:
   $$\min \sum_{t=0}^{23} P_{\text{unmet}}(t) \cdot \Delta t$$
2. **$J_2$ (Emergency Reserve Shortfall)**:
   $$\min \sum_{t=0}^{23} s_{\text{EBR}}(t) + s_{\text{term}}$$
3. **$J_3$ (Diesel Fuel Consumption)**:
   $$\min \sum_{t=0}^{23} [0.00025 \cdot P_{\text{diesel}}(t) + 5.0 \cdot u_{\text{diesel}}(t) + 6.0 \cdot v_{\text{start}}(t)] \cdot \Delta t$$
4. **$J_4$ (Avoidable Renewable Curtailment)**:
   $$\min \sum_{t=0}^{23} [P_{\text{pv,curt}}(t) + P_{\text{wind,curt}}(t)] \cdot \Delta t$$

## CANONICAL REPRESENTATION HASH
```text
MODEL_HASH = 9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c
```
