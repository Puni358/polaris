# MILP Model Structure & Objectives Static Audit

## 1. Dimensional Audit

In `system/optimization/implementations/gap19_highs_native.py` (lines 162–165):

### Total Decision Variables ($N = 408$):
- Base 15 variables per timestep $\times 24 = 360$ variables ($96$ binary decision variables, $264$ continuous operational variables).
- Layer B Protected Critical Deficit $P_{\text{unmet\_crit}}[t]$ ($24$ continuous variables, indices $360..383$).
- Layer C Governed Reserve Shortfall $s_{J2}[t]$ ($24$ continuous variables, indices $384..407$).
- Total: $96$ binary + $312$ continuous = **408 variables**.

### Total Linear Constraints ($M = 312$ in `NORMAL` mode):
- Base operational constraints ($11$ per timestep $\times 24 = 264$ constraints).
- Layer B Protected Critical Balance ($24$ constraints, indices $264..287$).
- Layer C Governed Pointwise Maximum Reserve Envelope ($24$ constraints, indices $288..311$).
- Total: **312 linear constraints**.

---

## 2. Objective Hierarchy & Priority Audit

In lines 366–385 of `gap19_highs_native.py`:

```python
obj1.priority = 4  # J1: Critical Deficit Wh
obj2.priority = 3  # J2: Governed Reserve Shortfall Wh
obj3.priority = 2  # J3: Diesel Fuel Liters
obj4.priority = 1  # J4: Renewable Curtailment Wh
```

- Native HiGHS lexicographic priority sequence: **$J_1 > J_2 > J_3 > J_4$**.
- `h.setOptionValue("blend_multi_objectives", False)` (line 349) strictly enforces lexicographic hierarchical optimization.
- No scalar weighted composite objective remains active on Option B.

---

## 3. Verdict

```
MODEL_VARIABLE_COUNT = 408 (96 Binary, 312 Continuous)
MODEL_CONSTRAINT_COUNT = 312
OBJECTIVE_HIERARCHY = J1 > J2 > J3 > J4 (Priorities 4, 3, 2, 1)
BLEND_MULTI_OBJECTIVES = FALSE
MILP_STRUCTURE_STATUS = PASS
```
