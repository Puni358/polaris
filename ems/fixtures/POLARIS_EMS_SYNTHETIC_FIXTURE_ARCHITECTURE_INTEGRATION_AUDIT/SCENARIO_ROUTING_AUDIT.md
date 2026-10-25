# SCENARIO ROUTING AUDIT

## 1. 5-SCENARIO SELECTION & ROUTING
The synthetic fixture contains 5 deterministic 24-hour scenarios (120 rows total):

| Scenario ID | Scenario Name | Intended ECD State | Key Physical Condition | Initial Fuel | Initial SOC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SC-01** | `NORMAL_OPERATION` | `ECD-NORMAL` | High renewable & battery reserve | $500.0$ L | $80.0\%$ |
| **SC-02** | `BATTERY_LIMITED_EMERGENCY` | `ECD-EMERGENCY` | Low solar/wind, battery at floor | $500.0$ L | $20.0\%$ |
| **SC-03** | `DIESEL_LIMITED_EMERGENCY` | `ECD-EMERGENCY` | Diesel fuel exhausted ($20.0$ L) | $20.0$ L | $80.0\%$ |
| **SC-04** | `BOTH_RESOURCES_LIMITED` | `ECD-EMERGENCY` | Battery at floor & fuel exhausted ($10.0$ L) | $10.0$ L | $20.0\%$ |
| **SC-05** | `UNKNOWN_INVALID_INPUT_BOUNDARY` | `UNKNOWN_INVALID` | Invalid input / telemetry boundary | $500.0$ L | $80.0\%$ |

---

## 2. LOCATION OF SCENARIO_ID
- **Question**: Where should `scenario_id` be placed without modifying runtime semantics or breaking core schemas?
- **Options Evaluated**:
  1. Core Schema (`StationState` / `ForecastBundle` / `DispatchPlan` class attributes): **NOT RECOMMENDED** (modifies core runtime schemas).
  2. `ForecastBundle.metadata["scenario_id"]`: **RECOMMENDED** (existing metadata dictionary handles arbitrary key-values cleanly).
  3. `SyntheticFixtureProvider` / Test Harness Context: **RECOMMENDED** (keeps test orchestration clean).
- **Least Invasive Recommendation**: Store `scenario_id` in `ForecastBundle.metadata["scenario_id"]` and test harness runner context. Zero schema changes required.
