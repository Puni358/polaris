# HiGHS Priority Semantics Verification

Under HiGHS C++ engine semantics (`highspy` 1.15.1):
1. `HighsLinearObjective.priority` is evaluated as a numeric integer rank where **larger numeric values represent higher priority**.
2. Setting `obj1.priority = 4`, `obj2.priority = 3`, `obj3.priority = 2`, `obj4.priority = 1` causes HiGHS to solve objective 1 first, then fix its optimal value (with zero tolerance) before optimizing objective 2, objective 3, and objective 4 sequentially.
3. This guarantees native multi-objective lexicographic optimization adhering to $J_1 > J_2 > J_3 > J_4$.
