# OPTION A LOCK FORENSICS

## LOCK CONSTRAINT RESIDUAL AND FEASIBILITY VERIFICATION

Every higher-priority objective lock added in Option A was explicitly evaluated on the final decision vector $x_A$:

1. **$J_1$ Lock Residual**:
   - Bound: $J_1^* + \epsilon_1 = 0.00000010$
   - Actual $J_1(x_A)$: $0.00000000$
   - Residual Slack: $1.0 \times 10^{-7}$ (Satisfied)
2. **$J_2$ Lock Residual**:
   - Bound: $J_2^* + \epsilon_2 = 0.00000010$
   - Actual $J_2(x_A)$: $0.00000000$
   - Residual Slack: $1.0 \times 10^{-7}$ (Satisfied)
3. **$J_3$ Lock Residual**:
   - Bound: $J_3^* + \epsilon_3 = 0.00000010$
   - Actual $J_3(x_A)$: $0.00000000$
   - Residual Slack: $1.0 \times 10^{-7}$ (Satisfied)

All Option A lock constraints are satisfied without violation, establishing that Option A is a valid lexicographic reference.
