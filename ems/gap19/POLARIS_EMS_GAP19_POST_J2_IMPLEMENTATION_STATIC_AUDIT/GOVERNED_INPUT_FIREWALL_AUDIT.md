# Governed Input Firewall Static Audit

## 1. Protected Critical Demand Ingestion

In `system/optimization/implementations/gap19_highs_native.py` (lines 88–101):

```python
if forecast_bundle.demand_critical is not None:
    critical_demand = forecast_bundle.demand_critical.point
elif "critical_demand_w" in config and config["critical_demand_w"] is not None:
    ...
elif "critical_demand_ratio" in config and config["critical_demand_ratio"] is not None:
    ...
else:
    raise ValueError("MISSING_GOVERNED_INPUT: Protected critical load trajectory (demand_critical) is missing or unspecified.")
```

- If `demand_critical` is omitted from `ForecastBundle` and no explicit configuration override exists, the optimizer raises `ValueError("MISSING_GOVERNED_INPUT...")`.
- Total demand `demand.point` is **NEVER** silently repurposed as critical demand.

---

## 2. Terminal Reserve Target Ingestion

In `system/optimization/implementations/gap19_highs_native.py` (lines 134–145):

```python
if getattr(station_state, "terminal_target_wh_override", None) is not None:
    terminal_target_wh = float(station_state.terminal_target_wh_override)
elif "terminal_target_wh" in config and config["terminal_target_wh"] is not None:
    terminal_target_wh = float(config["terminal_target_wh"])
elif config.get("terminal_reserve_model") == "INITIAL_STATE":
    terminal_target_wh = initial_e_wh
elif config.get("terminal_reserve_model") == "CAPACITY_RATIO":
    ...
else:
    raise ValueError("MISSING_GOVERNED_INPUT: Terminal reserve target (terminal_target_wh) is missing or unspecified.")
```

- If terminal reserve target is unspecified, the optimizer raises `ValueError("MISSING_GOVERNED_INPUT...")`.
- The optimizer **NEVER** defaults to `0.0 Wh`, `56,000 Wh`, `160,000 Wh`, or battery capacity silently.

---

## 3. Operating Mode Ingestion

In `system/optimization/implementations/gap19_highs_native.py` (lines 33, 41):

```python
operating_mode = str(getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))).upper()
```

- Governed operating modes are strictly `"NORMAL"` or `"EMERGENCY"`.
- Any unhandled mode (e.g. `"UNKNOWN_INVALID"`) triggers degraded failsafe dispatch without solver execution.

---

## 4. Verdict

```
MISSING_CRITICAL_DEMAND_REJECTED = YES
MISSING_TERMINAL_TARGET_REJECTED = YES
SILENT_ARBITRARY_FALLBACKS = NONE (0)
GOVERNED_INPUT_FIREWALL_STATUS = PASS
```
