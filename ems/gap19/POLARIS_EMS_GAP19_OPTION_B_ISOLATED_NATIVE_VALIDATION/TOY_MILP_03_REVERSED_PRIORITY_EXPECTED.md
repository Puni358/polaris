# TOY MILP 03 REVERSED PRIORITY EXPECTED SOLUTION

## Analytical Mathematical Derivation for Toy MILP 03

This document records the analytical lexicographic solution for Toy MILP 03.

---

## Analytical Derivation

1. **Stage 1 (Priority 1: Minimize $-10 x_2$)**:
   - Maximize integer $x_2$ subject to $x_1 + 3 x_2 \le 10$.
   - Max integer $x_2^* = 3$ (since $3(3) = 9 \le 10$, whereas $3(4) = 12 > 10$).
   - Optimal $J_2^* = -30.0$.

2. **Stage 2 (Priority 2: Minimize $-x_1$)**:
   - With $x_2 = 3$, constraint becomes $x_1 + 9 \le 10 \implies x_1 \le 1$.
   - Maximize integer $x_1 \implies x_1^* = 1$.
   - Optimal $J_1^* = -1.0$.

### Analytical Lexicographic Expected Result:
$$(x_1^*, x_2^*) = (1.0, 3.0), \quad J_2^* = -30.0, \quad J_1^* = -1.0$$
