# Current Priority Source Trace

## Target File
`system/optimization/implementations/gap19_highs_native.py`

## Line-by-Line Inspection

The objective registration sequence in `gap19_highs_native.py` (lines 314–334) is implemented as follows:

```python
314:        # Add Objectives (Option B Priority Mapping 1, 2, 3, 4)
315:        obj1 = highspy.HighsLinearObjective()
316:        obj1.priority = 1; obj1.weight = 1.0; obj1.offset = 0.0; obj1.abs_tolerance = 0.0; obj1.rel_tolerance = 0.0
317:        obj1.coefficients = c1.tolist()
318:
319:        obj2 = highspy.HighsLinearObjective()
320:        obj2.priority = 2; obj2.weight = 1.0; obj2.offset = 0.0; obj2.abs_tolerance = 0.0; obj2.rel_tolerance = 0.0
321:        obj2.coefficients = c2.tolist()
322:
323:        obj3 = highspy.HighsLinearObjective()
324:        obj3.priority = 3; obj3.weight = 1.0; obj3.offset = 0.0; obj3.abs_tolerance = 0.0; obj3.rel_tolerance = 0.0
325:        obj3.coefficients = c3.tolist()
326:
327:        obj4 = highspy.HighsLinearObjective()
328:        obj4.priority = 4; obj4.weight = 1.0; obj4.offset = 0.0; obj4.abs_tolerance = 0.0; obj4.rel_tolerance = 0.0
329:        obj4.coefficients = c4.tolist()
```

## Solver Options Audit

Search across `gap19_highs_native.py` for solver option configurations:
- Line 296: `h.setOptionValue("output_flag", False)`
- Line 297: `h.setOptionValue("threads", 1)`
- Line 298: `h.setOptionValue("blend_multi_objectives", False)`

No other parameters or methods modify objective priorities, weights, tolerances, or objective ordering.

## Findings
- `obj1.priority` ($J_1$, Critical Deficit) is set to `1`.
- `obj2.priority` ($J_2$, EBR Reserve Shortfall) is set to `2`.
- `obj3.priority` ($J_3$, Fuel Consumption) is set to `3`.
- `obj4.priority` ($J_4$, Curtailment) is set to `4`.
- Under the verified HiGHS convention (`HIGHER_NUMBER_IS_HIGHER_PRIORITY`), `obj4` has the highest priority and `obj1` has the lowest.
