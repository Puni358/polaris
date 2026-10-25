# SCENARIO COVERAGE MATRIX
## DETAILED SCENARIO-TO-POLICY MAPPING MATRIX

### 1. SCENARIO DESIGN SUITE
The minimum synthetic engineering fixture uses **5 deterministic scenarios** to achieve 100% architectural coverage.

### 2. COMPREHENSIVE COVERAGE MATRIX

| Test Dimension | SC-01 (Normal Operation) | SC-02 (Battery-Limited Emergency) | SC-03 (Diesel-Limited Emergency) | SC-04 (Both-Resources Limited) | SC-05 (UNKNOWN_INVALID Fallback) |
|---|---|---|---|---|---|
| **Simulated Duration** | 24 Hours | 24 Hours | 24 Hours | 24 Hours | 24 Hours |
| **Initial Battery SOC** | 80% ($160\text{ kWh}$) | 20% ($40\text{ kWh}$) | 80% ($160\text{ kWh}$) | 20% ($40\text{ kWh}$) | 80% ($160\text{ kWh}$) |
| **Initial Fuel Volume** | $500\text{ L}$ | $500\text{ L}$ | $20\text{ L}$ ($< 75\text{ L}$) | $10\text{ L}$ ($< 75\text{ L}$) | $500\text{ L}$ |
| **Solar Generation** | $0\text{--}50\text{ kW}$ (Bimodal) | $0\text{ kW}$ (Zero PV) | $0\text{ kW}$ (Zero PV) | $0\text{ kW}$ (Zero PV) | $0\text{--}50\text{ kW}$ |
| **Wind Generation** | $0\text{--}20\text{ kW}$ (Step) | $0\text{ kW}$ (Zero Wind) | $0\text{ kW}$ (Zero Wind) | $0\text{ kW}$ (Zero Wind) | $0\text{--}20\text{ kW}$ |
| **Critical Demand** | $30\text{ kW}$ | $30\text{ kW}$ | $30\text{ kW}$ | $30\text{ kW}$ | `NaN` / Missing |
| **Flexible Demand** | $15\text{ kW}$ | $15\text{ kW}$ | $15\text{ kW}$ | $15\text{ kW}$ | $15\text{ kW}$ |
| **Expected ECD State** | `ECD-NORMAL` | `ECD-BATTERY-LIMITED` | `ECD-DIESEL-LIMITED` | `ECD-BOTH-LIMITED` | `ECD-UNKNOWN_INVALID` |
| **Policy Mode** | Normal Mode | Emergency Mode | Emergency Mode | Degraded / Emergency | Safe-State Fallback |
| **Option D Behavior** | OD-01, OD-03, OD-05 | OD-02, OD-03, OD-04 | OD-06, OD-07 | OD-08, OD-09, OD-10 | Fallback Layer |
| **Primary Test Focus** | Economic dispatch, excess charging & curtailment | Diesel start, minimum output & battery charging | Critical battery discharge, noncritical load shedding | Deficit handling, proportional allocation & escalation | Input invalidation, safe state execution |

### 3. MINIMALITY AUDIT
No redundant scenarios exist. Every scenario tests a unique operational regime of the POLARIS EMS architecture.
