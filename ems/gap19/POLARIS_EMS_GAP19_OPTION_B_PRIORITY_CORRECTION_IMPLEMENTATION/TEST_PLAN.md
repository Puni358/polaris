# Test Plan for Implementation Verification

Six isolated tests were designed to verify implementation correctness before static re-audit:

1. **Test 1 — Priority Mapping**: Verify `obj1.priority = 4`, `obj2.priority = 3`, `obj3.priority = 2`, `obj4.priority = 1` in source code.
2. **Test 2 — Lexicographic Blend Mode**: Verify `blend_multi_objectives = False` in source code.
3. **Test 3 — Objective Vectors**: Verify `c1, c2, c3, c4` construction remains untouched.
4. **Test 4 — Model Structure**: Verify $N=409, M=313$ variable and constraint dimensions.
5. **Test 5 — Tolerances**: Verify `abs_tolerance = 0.0, rel_tolerance = 0.0`.
6. **Test 6 — Isolated Toy Sanity Test**: Verify priority 4 over 1 in `highspy` drives decision variable to Objective A optimum ($x = 0.0$).
