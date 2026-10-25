# MODEL HASH SCOPE AUDIT

## SCOPE AND BOUNDARIES OF CANONICAL MODEL HASH

The canonical SHA-256 model hash:
```text
MODEL_HASH = 9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c
```

### PROOF OF HASH EQUIVALENCE SCOPE

- `MODEL_A_HASH == MODEL_B_HASH` proves that Option A and Option B executed on the **exact same 385-variable test model**.
- It does **NOT** prove that the 385-variable test model is identical to the historical 360-variable `milp.py` model.

```text
MODEL_A_B_IDENTITY = PASS
EXPERIMENT_TO_PRODUCTION_IDENTITY = FAIL
```
