# TOY MILP 02 PRIORITY SPECIFICATION

## Priority Discrimination Benchmark Problem Specification

This document specifies the synthetic benchmark problem for Toy MILP 02, designed to discriminate lexicographic optimization from blended optimization.

---

## Model Definition

- $x_1 \in \{0, 1, \dots, 10\}$ (Integer variable)
- $x_2 \in \{0, 1, \dots, 10\}$ (Integer variable)
- **Constraint**: $x_1 + 3 x_2 \le 10$
- **Objective 1 ($J_1$)**: Minimize $-x_1$, Priority 1, Weight 1.0
- **Objective 2 ($J_2$)**: Minimize $-10 x_2$, Priority 2, Weight 1.0
