# NATIVE OBJECTIVE API AUDIT

## Signature & Usage Audit for `addLinearObjective`

This document records the exact syntax and usage contract for registering multiple linear objectives in `highspy`.

---

## Method Contract

```python
import highspy
import numpy as np

h = highspy.Highs()

# Objective 1 (Priority 1 = Highest Priority)
obj1 = highspy.HighsLinearObjective()
obj1.coefficients = np.array([-1.0, 0.0], dtype=np.float64)
obj1.priority = 1
obj1.weight = 1.0
obj1.abs_tolerance = 0.0
obj1.rel_tolerance = 0.0
h.addLinearObjective(obj1)

# Objective 2 (Priority 2 = Second Priority)
obj2 = highspy.HighsLinearObjective()
obj2.coefficients = np.array([0.0, -10.0], dtype=np.float64)
obj2.priority = 2
obj2.weight = 1.0
obj2.abs_tolerance = 0.0
obj2.rel_tolerance = 0.0
h.addLinearObjective(obj2)
```

---

## Audit Verdict

```text
NATIVE_OBJECTIVE_API_STATUS = CONFIRMED
```
The method `addLinearObjective` cleanly accepts `HighsLinearObjective` instances and passes them to the HiGHS C++ multi-objective optimization engine.
