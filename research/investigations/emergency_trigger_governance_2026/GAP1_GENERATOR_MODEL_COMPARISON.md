# POLARIS — GAP 1 GENERATOR CREDIBILITY MODEL COMPARISON

## Executive Summary

This document presents a detailed comparative analysis of **five candidate mathematical formulations** for quantifying "credible" dispatchable generator energy ($E_{\text{gen\_credible}}$) over the governed 6-hour critical load survivability horizon ($H = 6.0\text{ hours}$, $E_{\text{critical\_req}} = 69.60\text{ kWh}$ delivered).

All models are evaluated neutrally across twelve technical criteria to prepare for human governance decision-making.

---

## 1. Candidate Model Formulations

### MODEL A — Nameplate Potential Energy
- **Mathematical Formula**:
  $$E_{\text{gen\_A}} = H \cdot \sum_{k \in K} P_{\text{rated\_k}} = 6.0 \cdot P_{\text{max}} \quad [\text{kWh}]$$
- **Concept**: Assumes all installed generators can produce 100% rated power continuously for 6 hours.

### MODEL B — Credible Operating Capacity
- **Formula**:
  $$E_{\text{gen\_B}} = H \cdot \sum_{k \in K} \left( A_k(t) \cdot \delta_{\text{derate}} \cdot P_{\text{rated\_k}} \right) \quad [\text{kWh}]$$
- **Concept**: Bounds generation by active operational availability ($A_k \in \{0, 1\}$) and environmental derating ($\delta_{\text{derate}}$).

### MODEL C — Fuel-Constrained Deliverable Energy
- **Formula**:
  $$E_{\text{gen\_C}} = \min\left( H \cdot \sum A_k \delta P_{\text{rated\_k}}, \; \frac{V_{\text{fuel\_usable}}}{\text{BSFC}_{\text{avg}}} \right) \quad [\text{kWh}]$$
- **Concept**: Bounds generation by measured usable day-tank fuel volume ($V_{\text{fuel}}$) and brake specific fuel consumption ($\text{BSFC}$).

### MODEL D — Critical-Load Bounded Energy
- **Formula**:
  $$E_{\text{gen\_D}} = \min\left( H \cdot \sum A_k P_{\text{rated\_k}}, \; \max(0, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}}) \right) \quad [\text{kWh}]$$
- **Concept**: Caps generator energy credit at the net critical energy deficit over 6 hours. Does not credit excess unserved generator potential toward critical safety.

### MODEL E — Time-Varying Status & Constraint Energy
- **Formula**:
  $$E_{\text{gen\_E}} = \int_{0}^{H} \min\left( \sum_{k \in K} A_k(\tau) P_{\text{rated\_k}}(\tau), \, P_{\text{critical}}(\tau) \right) d\tau \quad [\text{kWh}]$$
- **Concept**: Integrates generator availability, startup delays, minimum loading constraints, and critical load trajectories dynamically over time $\tau \in [0, H]$.

---

## 2. Comprehensive Comparative Matrix

| Evaluation Criteria | MODEL A: Nameplate Potential | MODEL B: Operating Capacity | MODEL C: Fuel-Constrained | MODEL D: Critical-Demand Bounded | MODEL E: Time-Varying Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Primary Mathematical Formula** | $H \cdot \sum P_{\text{rated}}$ | $H \cdot \sum A_k \delta P_{\text{rated}}$ | $\min(H \cdot P_{\text{avail}}, E_{\text{fuel}})$ | $\min(H \cdot P_{\text{avail}}, E_{\text{net\_crit}})$ | $\int_0^H \min(\sum A_k P, P_{\text{crit}}) d\tau$ |
| **2. Required Telemetry Inputs** | Generator rated power $P_{\text{rated}}$ | Asset availability $A_k$, derating $\delta$ | Usable fuel volume $V_{\text{fuel}}$, fuel curve | $A_k$, connected critical load $P_{\text{crit}}$ | $A_k(t)$, startup delay, fuel, derating |
| **3. Currently Available Codebase Inputs** | `config["diesel"]["max_power_w"]` | `station_state.diesel_running` | `diesel_fuel_remaining_liters` (Optional) | `station_state.diesel_running`, `demand_critical` | `diesel_running`, `diesel_hours_running` |
| **4. Missing Codebase Inputs** | None | Generator fault flag, derating factor | Verified fuel tank sensor, fuel density | None | Warm-up delay, multi-gen status |
| **5. Failure Modes Detected** | Total microgrid blackout only | Generator fault lockout, maintenance | Day-tank fuel depletion, fuel valve freeze | Unserved net critical load deficit | Generator trip during startup, fuel drop |
| **6. Failure Modes Missed** | Generator trip, fuel exhaustion | Fuel exhaustion, fuel tank leak | Generator mechanical seizure during run | Fuel exhaustion | Sensor noise during integration |
| **7. Risk of False Confidence** | **HIGH**: Assumes generator runs even if faulted or out of fuel | **MEDIUM**: Assumes infinite fuel if $A_k=1$ | **LOW**: Directly checks fuel sufficiency | **LOW**: Dimensionally bounds credit by demand | **LOW**: Most complete physical check |
| **8. Risk of Premature Emergency** | **LOW**: Overestimates generation credit | **LOW**: Credits available generator fully | **MEDIUM**: May trigger if fuel tank is low | **LOW**: Matches required critical energy | **MEDIUM**: Triggers if startup delay is long |
| **9. Dimensional Consistency** | $\text{h} \times \text{kW} = \text{kWh}$ (Stored/Potential) | $\text{h} \times \text{kW} = \text{kWh}$ (Potential) | $\text{kWh}$ (Bus Deliverable) | $\text{kWh}$ (Bus Deliverable) | $\text{kWh}$ (Bus Deliverable) |
| **10. Implementation Complexity** | Very Low ($O(1)$) | Low ($O(1)$) | Medium ($O(1)$) | Medium ($O(1)$) | High ($O(N)$ discrete integral) |
| **11. POLARIS Synthetic Benchmark Suitability** | High (Current default behavior) | High (Native compatibility) | Medium (Fuel is optional in code) | High (Native compatibility) | Medium (Requires startup model) |
| **12. Real-Station Adapter Suitability** | Unsuitable (Ignores real failures) | Acceptable for basic telemetry | Highly Suitable for remote stations | Highly Suitable for EMS dispatch | Highly Suitable for advanced microgrids |

---

## 3. Key Analytical Insights

### 3.1 Unbounded Potential vs. Bus-Delivered Demand
- **Models A & B** measure total generator *potential energy output* ($30\text{ kW} \times 6\text{ h} = 180\text{ kWh}$). If critical load is $11.6\text{ kW}$ ($69.6\text{ kWh}$ requirement), Models A & B credit $180\text{ kWh}$ toward $M_{\text{surv}}$.
- **Model D** caps generator credit at the actual critical load demand required ($69.6\text{ kWh}$ max credit). This prevents unserved generator capacity from masking battery depletion.

### 3.2 Fuel Dependency Tradeoff
- **Model C** introduces a direct requirement for fuel telemetry. On real polar stations, fuel tank sensors can freeze or report false levels. If fuel telemetry fails, Model C must define a fallback rule (e.g. assume safe harbor fuel or transition to `UNKNOWN_INVALID`).

### 3.3 Unit Commitment & Startup Dynamics
- **Model E** explicitly evaluates whether a stopped generator ($u=0$) can start and sync within the required time window. If a station requires 15 minutes to preheat and start a standby diesel generator, Model E accounts for battery discharge during the 15-minute startup transient.
