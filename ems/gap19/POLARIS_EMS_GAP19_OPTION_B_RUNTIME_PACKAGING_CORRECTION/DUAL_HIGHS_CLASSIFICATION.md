# Dual HiGHS Classification

## Corrected Definition

```text
DUAL_HIGHS_RUNTIME = YES
NATIVE_LIBRARY_COEXISTENCE = PASS
```

The validated disposable environment contains two native HiGHS C++ engines simultaneously:
1. SciPy's bundled HiGHS runtime (`1.12.0`)
2. highspy's native HiGHS runtime (`1.15.1`)

Import order tests (`scipy` then `highspy`, and `highspy` then `scipy`) and simultaneous solver executions (`scipy.optimize.milp` + `highspy.Highs()`) passed with zero C++ symbol collisions. Coexistence is verified, but production deployment remains subject to human dependency-integration authorization.
