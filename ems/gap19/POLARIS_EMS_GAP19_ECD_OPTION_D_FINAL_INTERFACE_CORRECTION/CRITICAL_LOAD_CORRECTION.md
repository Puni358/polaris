# Critical Load vs Total Demand Correction

## Forensic Distinction
Total station demand is **NOT EQUAL TO** protected critical load ($P_{\text{demand}}(t) \ne P_{\text{critical}}(t)$).

Do **NOT** repurpose:
- `StationState.last_observed_demand`
- `ForecastBundle.demand.point`
- `runtime_context["actual_demand"]`

as a general production critical-load definition.

## Fixture vs Production Classification

1. **Synthetic Fixture Boundary**:
   In existing synthetic demo scenarios (`demo_scenario.json`), total demand intentionally equals synthetic critical demand for software testing purposes.
   - `SYNTHETIC_FIXTURE_CRITICAL_LOAD = AVAILABLE`
   - `SYNTHETIC_SCHEMA_DELTA = NONE`

2. **General / Production Boundary**:
   - `GENERAL_CRITICAL_LOAD_INTERFACE = NOT_ESTABLISHED`
   - `PRODUCTION_CRITICAL_LOAD = ENGINEERING_INPUT_REQUIRED`

No production critical-load schema fields or arbitrary scaling factors are added.
