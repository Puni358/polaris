# HIGHS NATIVE MAPPING

## OPTION B NATIVE HIGHS MULTI-OBJECTIVE MAPPING

- **API Interface**: `highspy.HighsLinearObjective`
- **Configuration Options**: `blend_multi_objectives = False`, `threads = 1`
- **Objective Assignments**:
  - $J_1$: `obj1.priority = 1`, `obj1.weight = 1.0`, `obj1.coefficients = c1`
  - $J_2$: `obj2.priority = 2`, `obj2.weight = 1.0`, `obj2.coefficients = c2`
  - $J_3$: `obj3.priority = 3`, `obj3.weight = 1.0`, `obj3.coefficients = c3`
  - $J_4$: `obj4.priority = 4`, `obj4.weight = 1.0`, `obj4.coefficients = c4`

`HIGHS_NATIVE_MAPPING` = `ESTABLISHED`
