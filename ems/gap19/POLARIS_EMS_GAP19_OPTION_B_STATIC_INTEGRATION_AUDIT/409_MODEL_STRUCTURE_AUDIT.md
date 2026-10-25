# 409-Variable Model Structure Audit

```text
TOTAL_VARIABLES = 409 (96 Binary, 313 Continuous)
TOTAL_CONSTRAINTS = 313 (Base M=313; M=337 in EMERGENCY mode)
409_MODEL_STRUCTURE = ESTABLISHED
```

- 0..359: Historical 360 baseline variables (24h x 15)
- 360..383: 24 P_unmet_crit[t] continuous variables
- 384..407: 24 s_EBR[t] continuous variables
- 408: 1 s_terminal continuous variable
