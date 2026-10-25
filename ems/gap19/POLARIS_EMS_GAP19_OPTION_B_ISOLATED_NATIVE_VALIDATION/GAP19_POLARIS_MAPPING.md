# GAP19 POLARIS MAPPING

## GAP19 EMS Objective Stage Structural Mapping

This document provides the structural mapping of GAP19 EMS objective stages to `highspy` linear objectives.

---

## Objective Mapping

```python
# Structural Mapping in highspy
import highspy
import numpy as np

h = highspy.Highs()
h.setOptionValue("blend_multi_objectives", False)

# Stage 1: Critical Reliability (Wh) - Priority 1 (Highest)
obj1 = highspy.HighsLinearObjective()
obj1.coefficients = c_critical_deficit  # 1D array over horizon H
obj1.priority = 1
h.addLinearObjective(obj1)

# Stage 2: Emergency Battery Reserve / EBR (Wh) - Priority 2
obj2 = highspy.HighsLinearObjective()
obj2.coefficients = c_battery_reserve   # 1D array over horizon H
obj2.priority = 2
h.addLinearObjective(obj2)

# Stage 3: Governed Fuel Optimization (Liters) - Priority 3
obj3 = highspy.HighsLinearObjective()
obj3.coefficients = c_fuel_consumption  # 1D array over horizon H
obj3.priority = 3
h.addLinearObjective(obj3)

# Stage 4: Avoidable Curtailment (Wh) - Priority 4
obj4 = highspy.HighsLinearObjective()
obj4.coefficients = c_curtailment        # 1D array over horizon H
obj4.priority = 4
h.addLinearObjective(obj4)
```

---

## Relevance Boundary

This code snippet proves structural compatibility only. No POLARIS coefficients, data, or production MILP matrices were used in this audit.
