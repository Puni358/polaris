# Objective Hierarchy & Priorities Forensic Audit

## 1. Priority Verification in Native HiGHS

In `gap19_highs_native.py` (lines 349, 366–380):

```python
h.setOptionValue("blend_multi_objectives", False)

obj1.priority = 4  # J1: Critical Deficit Wh
obj2.priority = 3  # J2: Governed Reserve Shortfall Wh
obj3.priority = 2  # J3: Diesel Fuel Liters
obj4.priority = 1  # J4: Renewable Curtailment Wh
```

- Priority Order: **$J_1 > J_2 > J_3 > J_4$** (Priority 4 $\succ$ 3 $\succ$ 2 $\succ$ 1).
- `blend_multi_objectives = False` strictly forces sequential lexicographic optimization.

---

## 2. Reported Values from Synthetic Runtime Test

- **$J_1$ (Critical Deficit)** = `0.0 Wh`
- **$J_2$ (Governed Reserve Shortfall)** = `0.0 Wh`
- **$J_3$ (Diesel Fuel Liters)** = `116.5076 L`
- **$J_4$ (Renewable Curtailment)** = `0.0 Wh`

*(Note: These values are strictly results of this synthetic test configuration and do NOT constitute station policy bounds).*

---

## 3. Verdict

```
OBJECTIVE_PRIORITIES = J1 > J2 > J3 > J4 (4, 3, 2, 1)
BLEND_MULTI_OBJECTIVES = FALSE
COMPOSITE_SCALAR_OBJECTIVE = NONE (0)
OBJECTIVE_HIERARCHY_STATUS = PASS
```
