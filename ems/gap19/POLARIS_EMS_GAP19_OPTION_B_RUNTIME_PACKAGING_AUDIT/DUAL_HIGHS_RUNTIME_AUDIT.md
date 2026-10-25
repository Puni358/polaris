# Dual HiGHS Runtime Audit

```text
DUAL_HIGHS_RUNTIME = YES
```

- SciPy 1.18.1 provides native HiGHS `1.12.0`.
- `highspy` 1.15.1 provides native HiGHS `1.15.1`.
- Both runtime engines coexist inside the Python process without namespace collisions because SciPy encapsulates its binary in `scipy.optimize._highspy` while `highspy` exposes top-level `highspy`.
