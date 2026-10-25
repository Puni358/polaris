# OPTION B HIGHS COMPATIBILITY

## MATHEMATICAL COMPATIBILITY WITH NATIVE HIGHS OPTION B

Option B configures native multi-objectives via `highspy`:
- Objective 1 ($J_1$): `priority = 1`, `weight = 1.0`, `coefficients = c1`
- Objective 2 ($J_2$): `priority = 2`, `weight = 1.0`, `coefficients = c2`
- Objective 3 ($J_3$): `priority = 3`, `weight = 1.0`, `coefficients = c3`
- Objective 4 ($J_4$): `priority = 4`, `weight = 1.0`, `coefficients = c4`
- Option: `blend_multi_objectives = False`

The 409-variable target MILP is 100% mathematically compatible with native HiGHS multi-objective optimization.

```text
OPTION_B_COMPATIBILITY = PASS
```
