# FIXTURE PROVIDER AUDIT

## 1. EXISTING PROVIDERS vs SYNTHETIC FIXTURE REQUIREMENTS

The audit evaluated existing data providers ([LocalDataProvider](file:///home/punith-bs/01polaris%20%28Copy%29/system/data/provider.py#L9), [H10RuntimeAdapter](file:///home/punith-bs/01polaris%20%28Copy%29/system/adapters/h10_runtime_adapter.py#L27)) against `POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE.csv`.

| Component / Function | Existing `LocalDataProvider` | Existing `H10RuntimeAdapter` | Synthetic Fixture Requirement | Required Adapter Action |
| :--- | :--- | :--- | :--- | :--- |
| **Data Format** | JSON scenario files | H10 CSV (8784 rows) | Fixture CSV (120 rows, 5 scenarios) | **`SyntheticFixtureProvider`** needed |
| **Scenario Filtering** | Single file per scenario | Single year continuous | 5 scenario blocks of 24h | Filter rows by `scenario_id` |
| **Unit Scaling** | Assumes W, W/m^2 | Assumes W, W/m^2 | Fixture in kW, kWh | Multiply power/energy by 1000.0 |
| **Critical Demand** | Total demand only | Total demand only | `p_critical_forecast_kW` | Parse critical demand columns |
| **Fuel Remaining** | Absent | Absent | `v_fuel_initial_L` | Extract initial fuel per scenario |
| **State Factory** | Basic `StationState` | H10 `StationState` | Extended `StationState` | Populate fuel & critical load |

---

## 2. MINIMUM ADAPTER SPECIFICATION (`SyntheticFixtureProvider`)
A lightweight adapter class must be created in `system/adapters/synthetic_fixture_adapter.py`:
- Reads `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv` and `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json`.
- Filters rows by `scenario_id` ("SC-01" to "SC-05").
- Scales kW -> W and kWh -> Wh.
- Constructs `StationState` (with initial SOC and initial fuel).
- Constructs `ForecastBundle` (with `demand.point` = 49.5 kW and optional `critical_demand` = 33.0 kW).
- Exposes `get_runtime_state()` and `get_future_ground_truth()` for `runner.py`.
