# Priority Semantics Version Scope

## Scope Analysis

```text
ISOLATED_HIGHSPY_PRIORITY_SEMANTICS = ESTABLISHED
POLARIS_RUNTIME_PRIORITY_SEMANTICS = NOT_ESTABLISHED
CROSS_VERSION_PRIORITY_TRANSFER = QUALIFIED
```

1. **Isolated `highspy` 1.15.1**: Empirically proved that `HIGHER_NUMBER_IS_HIGHER_PRIORITY` for both LP and MILP formulations.
2. **POLARIS Baseline `.venv`**: Lacks `highspy` installation, so standalone priority semantics are not established in that isolated sub-environment without `highspy`.
