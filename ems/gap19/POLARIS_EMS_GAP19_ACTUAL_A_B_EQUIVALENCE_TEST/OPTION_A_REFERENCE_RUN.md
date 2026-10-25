# OPTION A REFERENCE RUN REPORT

## SEQUENTIAL LEXICOGRAPHIC MILP WITH EXPLICIT LOCKS

Option A was executed as a 4-pass sequential solver pipeline using SciPy `milp` (which internally wraps HiGHS):

- **Pass 1**: Solved $\min J_1(x)$. Result: $J_1^* = 0.00000000$. Status: Feasible/Optimal.
- **Pass 2**: Added constraint $J_1(x) \le 0.00000000 + 10^{-7}$. Solved $\min J_2(x)$. Result: $J_2^* = 0.00000000$. Status: Feasible/Optimal.
- **Pass 3**: Added constraint $J_2(x) \le 0.00000000 + 10^{-7}$. Solved $\min J_3(x)$. Result: $J_3^* = 0.00000000$. Status: Feasible/Optimal.
- **Pass 4**: Added constraint $J_3(x) \le 0.00000000 + 10^{-7}$. Solved $\min J_4(x)$. Result: $J_4^* = 0.00000000$. Status: Feasible/Optimal.

Option A produced a fully feasible solution $x_A$ with maximum constraint residual $9.0949470177e-13$.
