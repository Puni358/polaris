# Native HiGHS Priority Configuration Audit

```text
obj1.priority = 4  (J1: Critical Deficit Wh)
obj2.priority = 3  (J2: Reserve Shortfall Wh)
obj3.priority = 2  (J3: Diesel Fuel Liters)
obj4.priority = 1  (J4: Curtailment Wh)
blend_multi_objectives = False
NATIVE_LEXICOGRAPHIC_CONFIGURATION = PASS
```

Native HiGHS hierarchy confirmed: `J1 > J2 > J3 > J4`.
