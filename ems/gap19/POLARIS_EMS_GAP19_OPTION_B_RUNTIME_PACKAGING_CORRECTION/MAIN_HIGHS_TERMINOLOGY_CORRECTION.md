# Main POLARIS HiGHS Terminology Correction

## Corrected Classification

```text
MAIN_POLARIS_STANDALONE_HIGHSPY = NOT_INSTALLED
MAIN_POLARIS_BUNDLED_HIGHS = 1.12.0
```

### Forensic Distinction
- The main POLARIS environment (`.venv`) contains SciPy 1.18.1, which bundles internal HiGHS C++ engine version `1.12.0` (`scipy.optimize._highspy`).
- The main POLARIS environment does **not** contain the standalone `highspy` Python module package.
- Describing the main POLARIS environment as having "no HiGHS" was inaccurate. The environment has SciPy-bundled HiGHS 1.12.0, but lacks standalone `highspy`.
