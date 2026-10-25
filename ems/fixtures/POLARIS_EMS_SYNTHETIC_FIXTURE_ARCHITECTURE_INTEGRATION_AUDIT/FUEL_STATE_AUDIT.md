# FUEL STATE AUDIT

## 1. DIESEL FUEL STATE STORAGE AUDIT

The audit investigated where diesel fuel remaining ($V_{\text{fuel}}$ in Liters) is currently stored across the POLARIS codebase.

| Component / Module | Inspection Site | Fuel Storage Status | Details / Findings |
| :--- | :--- | :--- | :--- |
| **`StationState` Schema** | [station_state.py:L8](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py#L8) | **ABSENT** | `StationState` fields: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_*`. No fuel field exists. |
| **`DigitalTwinSimulator`**| [simulator.py:L54](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py#L54) | **ABSENT** | Updates `diesel_running` and `diesel_hours_running`, but does NOT track or update fuel volume. |
| **`LocalMILPEnergyOptimizer`**| [milp.py:L111](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L111) | **DERIVED COST ONLY** | Calculates hourly fuel cost in objective, but does NOT enforce fuel inventory constraint ($\sum F(P) \Delta t \le V_{\text{fuel}}$). |
| **`EmergencyConditionDetector`**| [ecd.py:L213](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L213) | **REQUIRED PARAMETER** | `evaluate()` requires `fuel_remaining_liters: float` as input argument. |

---

## 2. CLASSIFICATION & RECOMMENDATION
- **Classification**: **`STATIONSTATE_EXTENSION_REQUIRED`**
- **Required Action**: To support dynamic ECD assessment across receding horizon iterations, `fuel_remaining_liters` must be added as an optional/backward-compatible field on `StationState`, and `DigitalTwinSimulator.step()` must decrement fuel inventory based on actual generator dispatch.
