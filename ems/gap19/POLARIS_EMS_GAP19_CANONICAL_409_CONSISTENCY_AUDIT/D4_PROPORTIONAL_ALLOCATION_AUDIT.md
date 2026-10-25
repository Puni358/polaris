# D4 PROPORTIONAL ALLOCATION AUDIT

## MATHEMATICAL CONSISTENCY OF PROPORTIONAL ALLOCATION

- **D4 Equation**: $P_{i,\text{served}}(t) \ge \alpha(t) P_{i,\text{min}}(t)$ where $\alpha(t) = \frac{P_{\text{avail,crit}}(t)}{\sum P_{i,\text{min}}(t)} \in [0, 1]$.
- **Edge Case $\sum P_{i,\text{min}} = 0$**: Handled cleanly with $\alpha(t) = 1.0$.
- **Consistency**: Proportional allocation factor $\alpha(t)$ is computed from inputs/available power and requires ZERO decision variables.

```text
D4_PROPORTIONAL_ALLOCATION = CONSISTENT
```
