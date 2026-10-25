# Schema Provenance Forensic Audit

## 1. Schema Field Semantics Verification

1. `demand.point`: Retains total station demand semantics ($20,000\text{ W}$). It was **NOT** repurposed as critical demand.
2. `demand_critical.point`: Separately represented as an additive schema attribute ($20,000\text{ W}$).
3. `operating_mode`: Separately represented in `StationState` (value `"NORMAL"`).
4. `ebr_target_wh_override` / `terminal_target_wh_override`: Explicit optional override attributes in `StationState`.

---

## 2. Distinction Between Test and Production Inputs

- Schema inputs explicitly accept `demand_critical` and `terminal_target_wh_override`.
- Absence of governed inputs raises an explicit hard exception (`ValueError("MISSING_GOVERNED_INPUT...")`) in production, ensuring test-only inputs cannot bleed into production defaults.

---

## 3. Verdict

```
DEMAND_POINT_REPURPOSED = NO
CRITICAL_DEMAND_SEPARATED = YES
SCHEMA_FIELDS_ADDITIVE = YES
SCHEMA_PROVENANCE_STATUS = PASS
```
