# HIGHSPY AUDIT

## Standalone `highspy` Dependency & API Audit

This document examines the standalone `highspy` Python package and its implications for Option B implementation.

---

## 1. Presence in Installed Environment

```text
HIGHSPY_INSTALLED = NO
```
The `highspy` package is **not installed** in the user's Python environment.

---

## 2. Capability Analysis if Installed

If `highspy` were installed in a future environment, it provides direct Python C++ bindings to the full HiGHS C++ class interface:

```python
# Theoretical Option B syntax via highspy
import highspy

h = highspy.Highs()
# Pass constraints...
h.addLinearObjective(cost_j1, priority=1, abs_tol=1e-4)
h.addLinearObjective(cost_j2, priority=2, abs_tol=1e-4)
h.addLinearObjective(cost_j3, priority=3, abs_tol=1e-4)
h.addLinearObjective(cost_j4, priority=4, abs_tol=1e-4)
h.run()
```

---

## 3. Architectural & Dependency Implications

If POLARIS adopts Option B via `highspy`:
1. **New Dependency**: Adds `highspy` as a required third-party Python binary package.
2. **C++ Version Coupling**: POLARIS becomes directly tied to specific C++ wheel compilations of HiGHS.
3. **Pypi / Offline Distribution**: `highspy` contains precompiled C++ binaries; offline deployments must manage wheel artifacts across Linux GLIBC environments.
4. **SciPy Decoupling**: Optimization moves outside SciPy's standard `scipy.optimize` ecosystem into standalone HiGHS bindings.
