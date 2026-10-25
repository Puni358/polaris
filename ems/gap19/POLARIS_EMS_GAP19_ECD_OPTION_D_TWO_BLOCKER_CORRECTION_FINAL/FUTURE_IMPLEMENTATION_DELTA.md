# Future Implementation Delta Specification

## Current Status vs Future Implementation Modification

To maintain absolute transparency, this document specifies current modifications (ZERO) versus required future implementation modifications:

### 1. Current Modifications Status
- `CURRENT_SOURCE_MODIFICATIONS` = **ZERO**
- `CURRENT_SCHEMA_MODIFICATIONS` = **ZERO**
- `RUNTIME_EXECUTION` = **NONE**

---

### 2. Future Source & Schema Modification List (When Authorized)

| Target File | Modification Type | Exact Required Modification |
| :--- | :--- | :--- |
| `system/schemas/station_state.py` | Schema Extension | Add optional `diesel_fuel_remaining_liters: Optional[float] = None` |
| `system/simulation/simulator.py` | Source Modification | Compute fuel consumed by $k=0$ action and advance fuel in `StationState` |
| `system/runtime/runner.py` | Source Modification | Call router between forecasting & solver; pass dynamic fuel to ECD |
| `system/control/router.py` | New Source File | Implement `EMSControlRouter` policy state machine |
| `system/optimization/implementations/option_d.py` | New Source File | Implement `OptionDFallbackSolver` DEC-004 logic |
