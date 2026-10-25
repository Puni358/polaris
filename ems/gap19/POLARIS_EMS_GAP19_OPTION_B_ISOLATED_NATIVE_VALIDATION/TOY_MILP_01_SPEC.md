# TOY MILP 01 SPECIFICATION

## Toy Benchmark Problem 01 Specification

This document specifies the synthetic benchmark problem for Toy MILP 01.

---

## Model Definition

- $x_1 \in \{0, 1, 2, 3, 4, 5\}$ (Integer variable)
- $x_2 \in \{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10\}$ (Integer variable)
- **Constraint**: $x_1 + x_2 \le 10$
- **Objective 1 ($J_1$)**: Minimize $-x_1$, Priority 1
- **Objective 2 ($J_2$)**: Minimize $-x_2$, Priority 2
