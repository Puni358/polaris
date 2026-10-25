# PRIORITY SEMANTICS AUDIT

## Objective Priority Semantics Verification

This document records the empirical verification of priority index ordering in HiGHS C++.

---

## 1. Priority Order Direction

In HiGHS C++, priority levels are defined such that:

```text
LOWER INTEGER PRIORITY VALUE = HIGHER PRIORITY STAGE (SOLVED FIRST)
```

- `priority = 1`: Highest Priority Stage (Optimized first).
- `priority = 2`: Second Priority Stage (Optimized second).
- `priority = 3`: Third Priority Stage (Optimized third).
- `priority = 4`: Fourth Priority Stage (Optimized fourth).

---

## 2. Empirical Priority Reversal Evidence

On Toy MILP 02 / 03 ($x_1 + 3 x_2 \le 10$):
- **Test A**: $J_1 = -x_1$ (`priority=1`), $J_2 = -10 x_2$ (`priority=2`) $\implies$ Result = `[10.0, 0.0]`.
- **Test B**: $J_1 = -x_1$ (`priority=2`), $J_2 = -10 x_2$ (`priority=1`) $\implies$ Result = `[1.0, 3.0]`.

Reversing the integer priority index completely flips the optimization precedence, confirming that priority index ordering is actively enforced by the solver.

---

## Audit Verdict

```text
OBJECTIVE_PRIORITY = CONFIRMED
```
Priority semantics are deterministic and verified. Lower integer priority values correspond to higher priority optimization stages.
