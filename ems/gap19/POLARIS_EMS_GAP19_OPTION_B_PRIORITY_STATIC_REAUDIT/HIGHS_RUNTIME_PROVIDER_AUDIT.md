# HiGHS Runtime Provider Audit

## Dependency Identification

Inspection of `system/optimization/implementations/gap19_highs_native.py` shows:
```python
import highspy
```
And solver instantiation:
```python
h = highspy.Highs()
```

```text
OPTION_B_RUNTIME_HIGHS_PROVIDER = highspy (standalone C++ python bindings)
POLARIS_OPTION_B_RUNTIME_DEPENDENCY = STANDALONE_HIGHSPY_REQUIRED
```

`gap19_highs_native.py` directly requires standalone `highspy` module bindings.
