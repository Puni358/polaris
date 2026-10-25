# POLARIS — GAP 1 GENERATOR INPUT INVENTORY & CODEBASE AUDIT

## Executive Summary

This inventory documents the actual implementation status of generator and fuel parameters across the POLARIS codebase (`system/schemas/station_state.py`, `system/simulation/simulator.py`, `system/optimization/implementations/gap19_highs_native.py`, and `config/`).

Every field is audited and classified into one of five categories:
1. `PROJECT FACT`: Documented benchmark station property.
2. `SYNTHETIC ASSUMPTION`: Engineering value assigned for benchmark simulation.
3. `IMPLEMENTED MODEL`: Active mathematical representation in POLARIS code.
4. `MISSING`: Field required for real-station credibility but absent in current runtime.
5. `UNKNOWN`: Unspecified or unverified parameter.

---

## 1. Codebase Inventory & Classification Matrix

| Parameter / Field Name | Code Location | Default Value | Audit Classification | Codebase Representation & Status |
| :--- | :--- | :---: | :--- | :--- |
| **Rated Generator Power ($P_{\text{rated}}$)** | `config["diesel"]["max_power_w"]` | $100,000.0\text{ W}$ ($100\text{ kW}$) | `SYNTHETIC ASSUMPTION` | Upper boundary in MILP decision variable $u_{\text{diesel}}(t) \cdot P_{\text{max}}$. |
| **Minimum Operating Power ($P_{\text{min}}$)** | `config["diesel"]["min_power_w"]` | $10,000.0\text{ W}$ ($10\text{ kW}$) | `SYNTHETIC ASSUMPTION` | Lower boundary when binary unit commitment $u_{\text{diesel}}(t) = 1$. |
| **Base Fuel Consumption Rate** | `config["diesel"]["base_fuel_consumption_l_per_h"]` | $5.0\text{ L/h}$ | `SYNTHETIC ASSUMPTION` | Idle/no-load fuel burn when generator is running ($u=1$). |
| **Marginal Fuel Consumption Rate** | `config["diesel"]["marginal_fuel_consumption_l_per_wh"]` | $0.00025\text{ L/Wh}$ ($0.25\text{ L/kWh}$) | `SYNTHETIC ASSUMPTION` | Linear fuel burn coefficient per Wh delivered. |
| **Generator Startup Fuel Cost** | `config["diesel"]["startup_fuel_l"]` | $2.0\text{ L}$ | `SYNTHETIC ASSUMPTION` | Penalty fuel consumed on binary transition $0 \rightarrow 1$. |
| **Generator Running Status** | `station_state.diesel_running` | `bool` | `IMPLEMENTED MODEL` | Boolean flag indicating whether generator is active at $t_0$. |
| **Continuous Running Hours** | `station_state.diesel_hours_running` | `float` (hours) | `IMPLEMENTED MODEL` | Tracks consecutive operating hours for runtime limits. |
| **Fuel Remaining Volume** | `station_state.diesel_fuel_remaining_liters` | `Optional[float]` (Default: `None`) | `SYNTHETIC ASSUMPTION` | Optional telemetry. Defaults to `initial_fuel_l = 100.0\text{ L}` if `None`. |
| **Generator Fault State** | N/A | Absent | `MISSING` | No `is_faulted` boolean in `StationState` or `config`. |
| **Generator Maintenance Status** | N/A | Absent | `MISSING` | No lockout schedule or maintenance state in runtime. |
| **Environmental Derating Factor** | N/A | Absent ($1.0$) | `MISSING` | No temperature/altitude power derating implemented. |
| **Number of Generators** | N/A | $1$ (Single aggregate) | `SYNTHETIC ASSUMPTION` | System models single aggregated generator unit. |
| **Independent Generator Control** | N/A | Single unit | `MISSING` | Cannot dispatch multiple generator sets independently. |
| **Generator Startup Delay** | N/A | $0.0\text{ seconds}$ (Instant) | `SYNTHETIC ASSUMPTION` | Binary decision variable $u(t)$ engages instantly in same step. |
| **Day-Tank vs Main Fuel Separation** | N/A | Single tank | `MISSING` | No distinction between day-tank and main fuel storage. |
| **Fuel Density & Energy Content** | N/A | Implicit | `UNKNOWN` | Fuel burn measured directly in Liters; no kWh/L density conversion. |

---

## 2. In-Depth Analysis of Codebase Inputs

### 2.1 StationState Telemetry Capabilities
In `system/schemas/station_state.py`, `StationState` encapsulates runtime state. The diesel fields present are:
- `diesel_running: bool`: Indicates whether generator was running in previous step.
- `diesel_hours_running: float`: Accumulates continuous running duration.
- `diesel_fuel_remaining_liters: Optional[float]`: Remaining fuel volume. 

**Critical Telemetry Observation**: `diesel_fuel_remaining_liters` is `Optional` and defaults to `None`. In standard MILP optimization (`GAP19HighsNativeOptimizer`), fuel availability is **NOT** passed as a linear constraint on total horizon generation. The optimizer assumes infinite cumulative fuel unless explicitly constrained.

### 2.2 DigitalTwinSimulator Fuel Dynamics
In `system/simulation/simulator.py`:
- Fuel consumption for a single timestep $\Delta t = 1.0\text{ h}$ is computed as:
  $$\text{Fuel Required} = \left( (5.0 \text{ if } P_{\text{diesel}} > 0 \text{ else } 0) + 0.00025 \times P_{\text{diesel}} \right) \times 1.0 \quad [\text{Liters}]$$
- If `diesel_fuel_remaining_liters` is `None`, the simulator initializes `initial_fuel_l = 100.0\text{ L}`.
- Generator power is continuous between $P_{\text{min}} = 10.0\text{ kW}$ and $P_{\text{max}} = 100.0\text{ kW}$.

### 2.3 GAP19 MILP Optimizer Representation
In `system/optimization/implementations/gap19_highs_native.py`:
- Decision variables for timestep $t \in [0, 23]$:
  - Binary commitment variable: $u_{\text{diesel}}(t) \in \{0, 1\}$
  - Continuous power output: $P_{\text{diesel}}(t) \ge 0$
- Constraints:
  - $10,000 \cdot u_{\text{diesel}}(t) \le P_{\text{diesel}}(t) \le 100,000 \cdot u_{\text{diesel}}(t)$
- **No Fuel Constraint**: The optimizer does **NOT** enforce $\sum_{t=0}^{23} \text{Fuel}(t) \le V_{\text{fuel\_remaining}}$. Generator credibility is treated as unbounded capacity potential up to nameplate $100\text{ kW}$.

---

## 3. Identification of Missing Information for Real-Station Credibility

To evaluate generator credibility on a real polar research station (e.g. Nuolja or Troll station), the current POLARIS state representation lacks five essential telemetry items:

1. **Explicit Asset Health / Fault Telemetry**: Currently, if a generator trips or fails, `StationState` has no `generator_healthy` or `fault_code` field to signal unserviceability.
2. **Usable Fuel Level Measurement**: `diesel_fuel_remaining_liters` is optional and unverified by sensor checksums.
3. **Fuel Transfer / Day-Tank Pump Status**: Real stations transfer fuel from bulk storage to day tanks. Day-tank pumps can fail or freeze.
4. **Startup Readiness & Warm-Up Time**: Cold diesel generators in polar regions require engine block pre-heating and 5–15 minute warm-up cycles before accepting full load.
5. **Multi-Generator Dispatch Topology**: Real stations utilize $2$ to $4$ modular generator sets (e.g. $3 \times 30\text{ kW}$). POLARIS models a single $100\text{ kW}$ aggregate generator.
