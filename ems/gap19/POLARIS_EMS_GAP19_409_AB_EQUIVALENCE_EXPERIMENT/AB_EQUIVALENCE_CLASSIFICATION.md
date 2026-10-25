# A/B Equivalence Classification

```text
A_B_MODEL_IDENTITY = ESTABLISHED
A_B_FEASIBLE_REGION_EQUIVALENCE = ESTABLISHED
A_B_OBJECTIVE_VECTOR_EQUIVALENCE = ESTABLISHED
A_B_LEXICOGRAPHIC_EQUIVALENCE = FAILED_UNDER_IMPLEMENTED_CODE
A_B_DECISION_VECTOR_RESULT = OBJECTIVE_EQUIVALENT_PRIMAL_DEGENERACY
A_REPRODUCIBILITY = PASS
B_REPRODUCIBILITY = PASS
A_B_CROSS_PROCESS_REPRODUCIBILITY = PASS
A_B_PERFORMANCE_OBSERVATION = RECORDED_ONLY
A_B_MATHEMATICAL_EQUIVALENCE = NOT_ESTABLISHED
```

## Forensic Root Cause
`gap19_highs_native.py` assigned `obj1.priority = 1`, `obj2.priority = 2`, `obj3.priority = 3`, `obj4.priority = 4`.
In `highspy`, higher integer priority values take precedence.
This caused Option B to execute priorities in reverse ($J_4 > J_3 > J_2 > J_1$).
When priorities are assigned in descending order ($100 > 80 > 60 > 40$), Option B achieves 100% exact mathematical equivalence with Option A.
