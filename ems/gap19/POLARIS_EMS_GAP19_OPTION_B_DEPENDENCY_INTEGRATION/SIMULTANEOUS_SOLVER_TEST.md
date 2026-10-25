# Simultaneous Toy Solver Execution Test

```text
SCIPY_MILP_TOY = PASS
HIGHSPY_MILP_TOY = PASS
SIMULTANEOUS_SOLVER_TEST = PASS
```

Both `scipy.optimize.milp` and native `highspy.Highs()` successfully solve independent toy problems within the same process context.
