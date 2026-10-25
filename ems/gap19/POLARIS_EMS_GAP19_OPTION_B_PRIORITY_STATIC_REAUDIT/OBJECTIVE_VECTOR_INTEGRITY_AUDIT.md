# Objective Vector Integrity Audit

```text
OBJECTIVE_VECTORS_INTACT = YES
```

## Objective Coefficient Inspection
- **$c_1$**: `c1[idx_unmet_crit_start + t] = 1.0 * dt`
- **$c_2$**: `c2[idx_s_ebr_start + t] = 1.0`, `c2[idx_s_term] = 1.0`
- **$c_3$**: `c3[base + 7] = marg_fuel_l_wh * dt`, `c3[base + 13] = base_fuel_l_h * dt`, `c3[base + 14] = startup_fuel_l`
- **$c_4$**: `c4[base + 2] = 1.0 * dt`, `c4[base + 3] = 1.0 * dt`

All objective vectors remain mathematically identical before and after priority modification.
