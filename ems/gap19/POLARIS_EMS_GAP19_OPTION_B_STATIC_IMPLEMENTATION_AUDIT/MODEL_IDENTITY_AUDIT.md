# Model Identity Audit

The static inspection verified the distinct identities of all POLARIS MILP formulations:

- `CURRENT_PRODUCTION_MODEL`: 360 variables / 264 constraints / scalar objective (`milp.py`).
- `HISTORICAL_385_VARIABLE_TEST_MODEL`: 385 variables / 265 constraints (legacy experiment model).
- `CANONICAL_GAP19_TARGET`: 409 variables / 313 constraints / 4 native lexicographic objectives.

The audited module `GAP19HighsNativeOptimizer` explicitly implements the `CANONICAL_GAP19_TARGET` ($N=409, M=313$).

`MODEL_IDENTITY = PASS`
