# HiGHS Native Objective Audit

HiGHS multi-objective registration audit (lines 294-334):
- Solver Option: `h.setOptionValue("blend_multi_objectives", False)`
- Objective 1: `priority = 1`, `coefficients = c1` ($J_1$)
- Objective 2: `priority = 2`, `coefficients = c2` ($J_2$)
- Objective 3: `priority = 3`, `coefficients = c3` ($J_3$)
- Objective 4: `priority = 4`, `coefficients = c4` ($J_4$)

Lexicographic ordering is strictly enforced natively by HiGHS in priority order $1 \to 2 \to 3 \to 4$.

`HIGHS_NATIVE_OBJECTIVES = PASS`
`LEXICOGRAPHIC_MODE = PASS`
