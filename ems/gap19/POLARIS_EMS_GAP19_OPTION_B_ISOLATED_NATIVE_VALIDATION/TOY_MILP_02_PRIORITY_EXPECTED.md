# TOY MILP 02 PRIORITY EXPECTED SOLUTION

## Analytical Mathematical Derivation for Toy MILP 02

This document records the analytical lexicographic solution for Toy MILP 02.

---

## Analytical Derivation

1. **Lexicographic Mode (Priority 1: $J_1 = -x_1$)**:
   - Maximize integer $x_1$ subject to $x_1 + 3 x_2 \le 10$.
   - Max integer $x_1^* = 10$ (at $x_2 = 0$).
   - Optimal $J_1^* = -10.0$.
   - At $x_1 = 10$, $10 + 3 x_2 \le 10 \implies x_2 = 0$.
   - Optimal $J_2^* = 0.0$.
   - Expected Lexicographic Vector: $(x_1^*, x_2^*) = (10.0, 0.0)$.

2. **Blended Mode (Weighted Sum $-x_1 - 10 x_2$)**:
   - Evaluate feasible integer points $(x_1, x_2)$:
     - $(10, 0) \implies -10 - 0 = -10.0$
     - $(7, 1) \implies -7 - 10 = -17.0$
     - $(4, 2) \implies -4 - 20 = -24.0$
     - $(1, 3) \implies -1 - 30 = -31.0$
   - Expected Blended Vector: $(x_1^*, x_2^*) = (1.0, 3.0)$.

---

## Priority Conflict Proof

The expected lexicographic solution $(10, 0)$ is explicitly distinct from the blended solution $(1, 3)$. Lexicographic optimization MUST NOT sacrifice $J_1$ (Priority 1) for a higher return on $J_2$.
