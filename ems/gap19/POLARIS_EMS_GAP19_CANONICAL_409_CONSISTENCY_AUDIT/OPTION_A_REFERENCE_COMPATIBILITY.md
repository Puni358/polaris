# OPTION A REFERENCE COMPATIBILITY

## MATHEMATICAL COMPATIBILITY WITH SEQUENTIAL MILP OPTION A

Option A solves 4 sequential MILP passes:
1. Pass 1: $\min c_1^T x \implies J_1^*$
2. Pass 2: $\min c_2^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1 \implies J_2^*$
3. Pass 3: $\min c_3^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1, c_2^T x \le J_2^* + \epsilon_2 \implies J_3^*$
4. Pass 4: $\min c_4^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1, c_2^T x \le J_2^* + \epsilon_2, c_3^T x \le J_3^* + \epsilon_3 \implies x_A$

Because $c_1, c_2, c_3, c_4$ are linear vectors and lock bounds are linear constraints, the 409-variable canonical target model is 100% mathematically compatible with Option A.

```text
OPTION_A_COMPATIBILITY = PASS
```
