# TOY MILP 01 EXPECTED SOLUTION

## Analytical Mathematical Derivation for Toy MILP 01

This document records the analytical lexicographic solution for Toy MILP 01.

---

## Analytical Derivation

1. **Stage 1 (Priority 1: Minimize $-x_1$)**:
   - $x_1 \in [0, 5]$. Maximize $x_1$ subject to $x_1 + x_2 \le 10$.
   - Max integer $x_1^* = 5$.
   - Optimal $J_1^* = -5.0$.

2. **Stage 2 (Priority 2: Minimize $-x_2$)**:
   - With $x_1 = 5$, constraint becomes $5 + x_2 \le 10 \implies x_2 \le 5$.
   - Maximize integer $x_2$ subject to $x_2 \le 5 \implies x_2^* = 5$.
   - Optimal $J_2^* = -5.0$.

### Analytical Lexicographic Expected Result:
$$(x_1^*, x_2^*) = (5.0, 5.0), \quad J_1^* = -5.0, \quad J_2^* = -5.0$$
