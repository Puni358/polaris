# Option A Reference Definition

Option A is the independent sequential MILP reference solver built using `highspy` C++ solver calls:
1. **Pass 1**: Minimize $c_1^T x \implies J_1^*$. Add lock constraint $c_1^T x \le J_1^* + 10^{-7}$.
2. **Pass 2**: Minimize $c_2^T x \implies J_2^*$. Add lock constraint $c_2^T x \le J_2^* + 10^{-7}$.
3. **Pass 3**: Minimize $c_3^T x \implies J_3^*$. Add lock constraint $c_3^T x \le J_3^* + 10^{-7}$.
4. **Pass 4**: Minimize $c_4^T x \implies J_4^* \implies J_4^*$.
