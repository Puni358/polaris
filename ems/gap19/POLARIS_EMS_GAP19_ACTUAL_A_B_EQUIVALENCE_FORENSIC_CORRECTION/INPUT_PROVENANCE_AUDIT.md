# INPUT PROVENANCE AUDIT

## AUDIT OF EXPERIMENT NUMERICAL INPUT DATA

- **Demand Profile**: Generated synthetically in `run_experiment.py` via trigonometric peak profile ($1500 + 1000 \sin(...) + 500 \sin(...)$). Provenance: `NEW_EXPERIMENT_SYNTHETIC_VALUE`.
- **Solar Profile**: Generated synthetically in `run_experiment.py` via daytime half-sine wave ($3000 \sin(...)$). Provenance: `NEW_EXPERIMENT_SYNTHETIC_VALUE`.
- **Wind Profile**: Generated synthetically in `run_experiment.py` via cosine wave ($800 + 400 \cos(...)$). Provenance: `NEW_EXPERIMENT_SYNTHETIC_VALUE`.
- **Emergency Reserve Target**: Set to $3000\text{ Wh}$ ($30\%$ SOC). Provenance: `EXPERIMENT_ONLY_TEST_PARAMETER`.
- **Terminal Reserve Target**: Set to $5000\text{ Wh}$ ($50\%$ SOC). Provenance: `EXPERIMENT_ONLY_TEST_PARAMETER`.

No numerical inputs were drawn from physical station data or production runtime bundles. They serve strictly as frozen, deterministic input vectors for solver equivalence testing.

```text
EXPERIMENT_INPUT_PROVENANCE = NEW_EXPERIMENT_SYNTHETIC_VALUE
EBR_TARGET_PROVENANCE = EXPERIMENT_ONLY_TEST_PARAMETER
TERMINAL_TARGET_PROVENANCE = EXPERIMENT_ONLY_TEST_PARAMETER
```
