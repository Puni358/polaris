# SCENARIO MATRIX
## DETERMINISTIC FIVE-SCENARIO TEST MATRIX

### 1. SCENARIO OVERVIEW
The synthetic engineering fixture contains **5 deterministic scenarios** covering all required operational regimes and Emergency Condition Detector (ECD) states.

### 2. DETAILED SCENARIO MATRIX

| Scenario ID | Scenario Name | Initial SOC | Initial Fuel | Solar PV Generation | Wind Generation | Demand Profile | Intended ECD State | Primary Architectural Behavior Tested |
|---|---|---|---|---|---|---|---|---|
| **SC-01** | `NORMAL_OPERATION` | $80.0\%$ ($160\text{ kWh}$) | $500.0\text{ L}$ | $0\text{--}50\text{ kW}$ (Bimodal) | $0\text{--}20\text{ kW}$ (Step) | $30\text{ kW}$ Crit / $15\text{ kW}$ Flex | `ECD-NORMAL` | Normal MPC economic dispatch, excess generation charging & curtailment |
| **SC-02** | `BATTERY_LIMITED_EMERGENCY` | $20.0\%$ ($40\text{ kWh}$) | $500.0\text{ L}$ | $0.0\text{ kW}$ (Zero PV) | $0.0\text{ kW}$ (Zero Wind) | $30\text{ kW}$ Crit / $15\text{ kW}$ Flex | `ECD-BATTERY-LIMITED` | Emergency mode trigger, Option D diesel critical support, excess battery charging |
| **SC-03** | `DIESEL_LIMITED_EMERGENCY` | $80.0\%$ ($160\text{ kWh}$) | $20.0\text{ L}$ ($< 75\text{ L}$) | $0.0\text{ kW}$ (Zero PV) | $0.0\text{ kW}$ (Zero Wind) | $30\text{ kW}$ Crit / $15\text{ kW}$ Flex | `ECD-DIESEL-LIMITED` | Emergency mode trigger, critical battery discharge, noncritical load shedding |
| **SC-04** | `BOTH_RESOURCES_LIMITED` | $20.0\%$ ($40\text{ kWh}$) | $10.0\text{ L}$ ($< 75\text{ L}$) | $0.0\text{ kW}$ (Zero PV) | $0.0\text{ kW}$ (Zero Wind) | $30\text{ kW}$ Crit / $15\text{ kW}$ Flex | `ECD-BOTH-LIMITED` | Severe deficit, proportional critical load allocation, operator escalation |
| **SC-05** | `UNKNOWN_INVALID_SAFE_STATE_FALLBACK` | $80.0\%$ ($160\text{ kWh}$) | $500.0\text{ L}$ | $0\text{--}50\text{ kW}$ (Bimodal) | $0\text{--}20\text{ kW}$ (Step) | `NaN` / Missing Input | `ECD-UNKNOWN_INVALID` | Invalidation boundary handling, safe-state fallback policy layer execution |

### 3. DETERMINISTIC REPRODUCIBILITY GUARANTEE
All five scenarios use fixed initial conditions, fixed parabolic/stepped trajectories, and explicit floating-point precision ($4$ decimal places). Zero random noise is introduced.
