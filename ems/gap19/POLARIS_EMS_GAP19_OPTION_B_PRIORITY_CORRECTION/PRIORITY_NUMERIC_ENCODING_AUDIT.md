# Priority Numeric Encoding Audit

## Comparison of Valid Encodings

The HiGHS lexicographic multi-objective solver compares objective priorities using strict greater-than inequality ($P_i > P_j$). Therefore, any strictly monotonically decreasing integer sequence satisfies the required priority order:

$$\text{priority}(J_1) > \text{priority}(J_2) > \text{priority}(J_3) > \text{priority}(J_4)$$

### Candidate Encoding A: `(4, 3, 2, 1)`
- `obj1.priority = 4`
- `obj2.priority = 3`
- `obj3.priority = 2`
- `obj4.priority = 1`
- **Evaluation**: Valid. Simplest, minimal 1-based integer encoding for a 4-stage hierarchy.

### Candidate Encoding B: `(100, 80, 60, 40)`
- `obj1.priority = 100`
- `obj2.priority = 80`
- `obj3.priority = 60`
- `obj4.priority = 40`
- **Evaluation**: Valid. Leaves numerical gaps for potential sub-objective insertions if needed.

## Governance & Engineering Determination

- The numeric values themselves (whether $4,3,2,1$ or $100,80,60,40$) carry **zero policy or governance meaning**.
- Both encodings result in **100% identical C++ solver internal execution graphs and solution trajectories**.
- **Engineering Recommendation**: Use `(4, 3, 2, 1)` (or `(100, 80, 60, 40)`) consistently across implementation and test fixtures as a standard engineering convention.
