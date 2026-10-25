# CONSTRAINT FORENSICS

## RESIDUAL VIOLATION ANALYSIS FOR ALL 265 CONSTRAINTS

For every linear constraint $i \in \{1, \dots, 265\}$, residuals were evaluated as:
$$\text{residual}_{i,\text{lhs}} = \max(0, l_i - A_i x), \quad \text{residual}_{i,\text{rhs}} = \max(0, A_i x - u_i)$$

- **Option A Maximum Residual**: $9.0949470177e-13$
- **Option B Maximum Residual**: $6.6613381478e-12$
- **Feasibility Threshold**: $1.0 \times 10^{-6}$

Both solutions satisfy all 265 physical equality and inequality constraints with residuals well below $10^{-6}$.

`CONSTRAINT_FEASIBILITY` = `PASS`
