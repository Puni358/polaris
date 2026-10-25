# Simultaneous Solver Test Results

In a disposable Python 3.12.3 environment containing SciPy 1.18.1 and highspy 1.15.1:
- `scipy.optimize.milp(...)` solved an integer toy problem $\to$ Status `0`, $x=0.0$.
- `highspy.Highs()` solved an integer toy problem $\to$ Status `kOptimal`, $x=0.0$.

Both solvers executed simultaneously in the same process without interference or error.

```text
SIMULTANEOUS_SOLVER_TEST = PASS
```
