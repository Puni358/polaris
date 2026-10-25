# Critical Load Representation Audit

## Audit of Demand & Critical Load Interface

1. **Current Demand Representation**:
   - `StationState.last_observed_demand`: Scalar float ($W$).
   - `ForecastBundle.demand.point`: 24h vector float ($W$).

2. **Critical Load Extraction for Synthetic Integration**:
   - In synthetic scenario fixtures (`demo_scenario.json`), total demand equals load demand.
   - `ConstantCriticalLoad(load_w)` or `TimeSeriesCriticalLoad(vector)` in `system/control/ecd.py` accepts existing demand data directly.

3. **Schema Delta Assessment**:
   - Total station demand is **NOT** repurposed as station critical demand.
   - For synthetic integration, passing load scalar/vector into `ecd.py` requires **ZERO** schema additions.

---

## Verdict
`CRITICAL_LOAD_INTERFACE = ESTABLISHED`. Zero schema modifications required.
