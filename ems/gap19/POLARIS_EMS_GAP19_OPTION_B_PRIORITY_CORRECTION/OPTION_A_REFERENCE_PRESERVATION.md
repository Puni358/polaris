# Option A Reference Preservation

## Firewall Declaration

Option A is the independent, unedited mathematical reference solver.

## Reference Properties

1. **Architecture**: Sequential MILP solver using standard single-objective solves.
2. **Algorithm**:
   - Solve Stage 1 ($J_1$) $\to$ Fix $J_1 \le J_1^* + \epsilon$
   - Solve Stage 2 ($J_2$) $\to$ Fix $J_2 \le J_2^* + \epsilon$
   - Solve Stage 3 ($J_3$) $\to$ Fix $J_3 \le J_3^* + \epsilon$
   - Solve Stage 4 ($J_4$)
3. **Status**: Unmodified throughout all Option B forensic and correction gates.

Option A serves as the gold-standard benchmark against which Option B revalidation will be measured.
