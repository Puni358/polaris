# HiGHS Version Reconciliation

## Cross-Environment Comparison

| Environment | Python | SciPy | Standalone highspy | Native HiGHS C++ Engine |
| :--- | :---: | :---: | :---: | :---: |
| **POLARIS Baseline `.venv`** | 3.12.3 | 1.18.1 | NOT INSTALLED | 1.12.0 (bundled in SciPy) |
| **Isolated Validation Venv** | 3.12.3 | 1.18.1 | 1.15.1 | 1.15.1 |

```text
VERSION_ALIGNMENT = DIFFERENT_NATIVE_HIGHS
HIGHS_VERSION_RECONCILIATION = QUALIFIED
```

### Forensic Analysis
- SciPy 1.18.1 bundles HiGHS C++ engine `1.12.0` internally for `scipy.optimize.linprog(method='highs')`.
- Standalone `highspy` 1.15.1 exposes HiGHS C++ engine `1.15.1`.
- `gap19_highs_native.py` uses `import highspy`, which executes against `highspy` 1.15.1 in environments where it is installed.
- The static audit is classified as `PASS_WITH_QUALIFICATION` because `gap19_highs_native.py` requires `highspy` 1.15.1.
