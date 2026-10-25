# OPTION A REFERENCE COMPATIBILITY

## SEQUENTIAL LEXICOGRAPHIC MILP REFERENCE COMPATIBILITY

The canonical target MILP is fully compatible with the independent Option A reference solver pipeline:
- Pass 1: $\min c_1^T x$
- Pass 2: $\min c_2^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1$
- Pass 3: $\min c_3^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1, c_2^T x \le J_2^* + \epsilon_2$
- Pass 4: $\min c_4^T x$ s.t. $c_1^T x \le J_1^* + \epsilon_1, c_2^T x \le J_2^* + \epsilon_2, c_3^T x \le J_3^* + \epsilon_3$

Every stage objective and lock constraint is linear, ensuring exact Option A reference compatibility.
