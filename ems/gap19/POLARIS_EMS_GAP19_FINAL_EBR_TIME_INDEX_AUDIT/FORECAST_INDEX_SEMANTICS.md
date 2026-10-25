# Forecast Index Semantics Audit (`FORECAST_INDEX_SEMANTICS.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/schemas/forecast_bundle.py`  
**VERDICT**: `CONFIRMED`

---

## 1. Schema Analysis (`ForecastBundle`)

In `system/schemas/forecast_bundle.py`:
- `origin_timestamp`: ISO-8601 string representing forecast origin $t_{\text{now}}$ (observation time).
- `timestamps`: 24-element list of ISO-8601 strings.
- Monotonicity check (line 104): `(parsed_ts[0] - parsed_origin).total_seconds() == 3600.0`
- `timestamps[0]` represents target hour ending at $t_{\text{now}} + 1\text{h}$.
- `timestamps[23]` represents target hour ending at $t_{\text{now}} + 24\text{h}$.

---

## 2. Array Index Definitions

- `point[0]`: Forecast prediction for interval $(t_{\text{now}}, t_{\text{now}} + 1\text{h}]$.
- `point[23]`: Forecast prediction for interval $(t_{\text{now}} + 23\text{h}, t_{\text{now}} + 24\text{h}]$.

```text
FORECAST_INDEX_0_SEMANTICS = T_NOW_PLUS_1H_TARGET
FORECAST_INDEX_23_SEMANTICS = T_NOW_PLUS_24H_TARGET
```
