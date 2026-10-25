# Objective Vector Integrity

```text
OBJECTIVE_VECTORS_CHANGED = NO
```

## Objective Vector Verification

- **$c_1$ (Critical Deficit Wh)**: `c1[idx_unmet_crit_start + t] = 1.0 * dt` — UNCHANGED
- **$c_2$ (Reserve Shortfall Wh)**: `c2[idx_s_ebr_start + t] = 1.0`, `c2[idx_s_term] = 1.0` — UNCHANGED
- **$c_3$ (Fuel Consumption Liters)**: `c3[base + 7] = marg_fuel_l_wh * dt`, `c3[base + 13] = base_fuel_l_h * dt`, `c3[base + 14] = startup_fuel_l` — UNCHANGED
- **$c_4$ (Curtailment Wh)**: `c4[base + 2] = 1.0 * dt`, `c4[base + 3] = 1.0 * dt` — UNCHANGED
