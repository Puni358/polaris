# Option A Reference Definition

Option A is defined as a 4-pass sequential lexicographic MILP solver:

- **Pass 1**: $\min c_1^T x \to J_1^*$. Add lock constraint $c_1^T x \le J_1^* + 10^{-6}$.
- **Pass 2**: $\min c_2^T x \to J_2^*$. Add lock constraint $c_2^T x \le J_2^* + 10^{-6}$.
- **Pass 3**: $\min c_3^T x \to J_3^*$. Add lock constraint $c_3^T x \le J_3^* + 10^{-6}$.
- **Pass 4**: $\min c_4^T x \to J_4^*$.

Lock tolerance $10^{-6}$ is classified as `TEST_CONFIGURATION_ONLY`.
