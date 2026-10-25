# D4 MATHEMATICAL FORMULATION

## 1. SEALED MATHEMATICAL FORMULATION

For protected critical equipment set $\mathcal{C}$ defined by station engineering:

Let $P_{i,\text{min}}(t) \ge 0$ be the engineering-defined minimum viable operating requirement for protected critical system $i \in \mathcal{C}$ at timestep $t$.

Let $P_{\text{critical,available}}(t) \ge 0$ be the net electrical power available for protected critical service after accounting for generation, battery discharge limits, and physical loss constraints.

---

## 2. GOVERNED DISPATCH RULES

### Case 1: Sufficient Protected Critical Power
If $P_{\text{critical,available}}(t) \ge \sum_{i \in \mathcal{C}} P_{i,\text{min}}(t)$:
$$P_{i,\text{served}}(t) \ge P_{i,\text{min}}(t) \quad \forall i \in \mathcal{C}$$
Each protected critical system is maintained at or above its minimum viable operating requirement.

### Case 2: Insufficient Protected Critical Power
If $P_{\text{critical,available}}(t) < \sum_{i \in \mathcal{C}} P_{i,\text{min}}(t)$:
$$\alpha(t) = \frac{P_{\text{critical,available}}(t)}{\sum_{i \in \mathcal{C}} P_{i,\text{min}}(t)} \in [0, 1)$$

$$P_{i,\text{served}}(t) = \alpha(t) \cdot P_{i,\text{min}}(t) \quad \forall i \in \mathcal{C}$$

---

## 3. EDGE CASE SPECIFICATION ($\sum P_{i,\text{min}} = 0$)
If $\sum_{i \in \mathcal{C}} P_{i,\text{min}}(t) = 0$, the ratio $\alpha(t)$ is mathematically undefined ($0/0$).
- **Classification**: `ENGINEERING/IMPLEMENTATION_EDGE_CASE_REQUIRING_EXPLICIT_RUNTIME_HANDLING`
- **Governed Handling**: If total minimum viable demand is zero, $P_{i,\text{served}}(t) = 0$ for all $i \in \mathcal{C}$, and $\alpha(t)$ defaults to $1.0$.
