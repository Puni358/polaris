# POLARIS — GAP 1 GENERATOR CREDIBILITY RESEARCH REPORT

## Executive Summary

This research report provides the technical, mathematical, and forensic foundation for resolving **GAP 1 — Credible Dispatchable Generation Modeling** for POLARIS Emergency Governance.

The locked human governance decisions remain strictly unchanged:
1. Validated critical-load service failure $\implies$ immediate Emergency.
2. Emergency may trigger before actual critical-load failure when 6-hour critical load survivability ($69.60\text{ kWh}$ delivered demand) cannot be credibly guaranteed ($M_{\text{surv}} < 0$).
3. Reserve deficit alone ($SOC < 37.83\%$ / $75.652\text{ kWh}$ stored) NEVER triggers Emergency.
4. Resource loss triggers Emergency ONLY when remaining resources cannot guarantee 6-hour critical survivability.
5. Emergency may automatically return to NORMAL when conditions clear and survivability is secure, with operator notification and override.

This report evaluates what evidence POLARIS is permitted to count as "credible" dispatchable generation over the 6-hour horizon. **No implementation is performed, and no governance decision is made or selected.**

---

## 1. Specification Lineage & Artifact Traceability (Task 1)

### 1.1 First Appearance of Generator Credibility
Generator credibility first appeared in `EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.md` under Section 2.2, which proposed:

$$E_{\text{gen\_credible}}(t, 6\text{h}) = \sum_{k \in K} \int_{0}^{6} A_k(t+\tau) \cdot P_{\text{gen\_k, max}}(t+\tau) \, d\tau$$

Assuming constant generator capability over 6 hours, this simplified to:

$$E_{\text{gen\_credible}} = 6.0 \cdot \sum \left( A_k \cdot P_{\text{gen\_max}} \right)$$

### 1.2 Discrepancies Between Artifacts
- **Draft Spec (`EMERGENCY_TRIGGER_IMPLEMENTATION_SPEC.md`)**: Modeled $E_{\text{gen\_credible}}$ as total potential generator energy output ($6.0 \text{ h} \times 100.0\text{ kW} = 600.0\text{ kWh}$ potential energy for a $100\text{ kW}$ generator).
- **Mathematical Reconciliation (`EMERGENCY_TRIGGER_MATH_RECONCILIATION.md`)**: Identified a dimensional mismatch between unserved potential generator capacity and actual bus-delivered critical load demand ($69.60\text{ kWh}$).
- **Gap Audit (`EMERGENCY_TRIGGER_GAP_AUDIT.md`)**: Formulated the unresolved question: *"What evidence is POLARIS allowed to count as CREDIBLE dispatchable generation?"* and catalogued candidate Models A through E.

---

## 2. Inventory & Classification of the Codebase Generator Model (Task 2)

Forensic inspection of `system/schemas/station_state.py`, `system/simulation/simulator.py`, and `system/optimization/implementations/gap19_highs_native.py` establishes the codebase inventory:

| Parameter / Feature | Value / Code Representation | Classification | Codebase Evidence |
| :--- | :---: | :--- | :--- |
| **Rated Generator Power ($P_{\text{rated}}$)** | $100,000.0\text{ W}$ ($100\text{ kW}$) | `SYNTHETIC ASSUMPTION` | `config["diesel"]["max_power_w"]` |
| **Minimum Power Output ($P_{\text{min}}$)** | $10,000.0\text{ W}$ ($10\text{ kW}$) | `SYNTHETIC ASSUMPTION` | `config["diesel"]["min_power_w"]` |
| **Base Fuel Consumption** | $5.0\text{ L/h}$ | `SYNTHETIC ASSUMPTION` | `config["diesel"]["base_fuel_consumption_l_per_h"]` |
| **Marginal Fuel Consumption** | $0.00025\text{ L/Wh}$ | `SYNTHETIC ASSUMPTION` | `config["diesel"]["marginal_fuel_consumption_l_per_wh"]` |
| **Startup Fuel Cost** | $2.0\text{ L}$ per start | `SYNTHETIC ASSUMPTION` | `config["diesel"]["startup_fuel_l"]` |
| **Generator Running Status** | `station_state.diesel_running` | `IMPLEMENTED MODEL` | Boolean flag in `StationState` |
| **Continuous Running Hours** | `station_state.diesel_hours_running` | `IMPLEMENTED MODEL` | Float in `StationState` |
| **Fuel Remaining Volume** | `station_state.diesel_fuel_remaining_liters` | `SYNTHETIC ASSUMPTION` | Optional in `StationState`; defaults to `None` |
| **Generator Fault State** | Absent | `MISSING` | No `is_faulted` boolean in code |
| **Maintenance Lockout State** | Absent | `MISSING` | No lockout schedule |
| **Environmental Derating Factor** | Absent ($1.0$) | `MISSING` | No thermal/polar derating applied |
| **Number of Generators** | $1$ Aggregate Unit | `SYNTHETIC ASSUMPTION` | Single unit model |

---

## 3. Mathematical Formulations of Credible Generation (Task 3)

### MODEL A — Nameplate Potential Energy
- **Formula**: $E_{\text{gen\_A}} = H \cdot \sum_{k \in K} P_{\text{rated\_k}} = 6.0 \cdot P_{\text{max}} \quad [\text{kWh}]$
- **Evaluation**: Assumes maximum rated generator output for 6 hours ($600\text{ kWh}$ for $100\text{ kW}$ generator). Overestimates credible energy because it ignores asset faults, maintenance lockouts, and fuel limits.

### MODEL B — Available Operating Capacity
- **Formula**: $E_{\text{gen\_B}} = H \cdot \sum_{k \in K} \left( A_k(t) \cdot \delta_{\text{derate}} \cdot P_{\text{rated\_k}} \right) \quad [\text{kWh}]$
- **Semantic Audit of Availability ($A_k(t)$)**: "Available" in POLARIS currently means `diesel_running == True` or `u_diesel == 1`. It does NOT verify whether fuel tanks contain 6 hours of fuel or whether maintenance lockouts exist.

### MODEL C — Fuel-Constrained Deliverable Energy
- **Formula**: $E_{\text{gen\_C}} = \min\left( H \cdot \sum A_k \delta P_{\text{rated\_k}}, \; \frac{V_{\text{fuel\_usable}}}{\text{BSFC}_{\text{avg}}} \right) \quad [\text{kWh}]$
- **Required Telemetry Evidence**: Usable fuel volume $V_{\text{fuel\_usable}}$, fuel density $\rho$, brake specific fuel consumption ($\text{BSFC}$). If `diesel_fuel_remaining_liters` is `None` (as in standard runs), Model C cannot be computed without a default fallback rule.

### MODEL D — Critical-Load Bounded Energy
- **Formula**: $E_{\text{gen\_D}} = \min\left( H \cdot \sum A_k P_{\text{rated\_k}}, \; \max\left(0, \, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}}\right) \right) \quad [\text{kWh}]$
- **Evaluation**: Caps generator credit at net critical energy demand ($69.60\text{ kWh}$ max). Prevents unserved generator capacity from inflating the survivability margin $M_{\text{surv}}$.

### MODEL E — Time-Varying Status & Constraint Energy
- **Formula**: $E_{\text{gen\_E}} = \int_{0}^{H} \min\left( \sum_{k \in K} A_k(\tau) P_{\text{rated\_k}}(\tau), \, P_{\text{critical}}(\tau) \right) d\tau \quad [\text{kWh}]$
- **Evaluation**: Dynamic integral accounting for generator availability, minimum loading ($10\text{ kW}$), startup fuel, and critical load trajectories over time $\tau \in [0, 6.0\text{ h}]$.

---

## 4. Dimensional Audit: Power vs. Energy (Task 4)

A critical distinction is required between **Instantaneous Power (kW)** and **Delivered Energy (kWh)**:

- **Rated Power ($P_{\text{rated}}$)**: Instantaneous electrical capability [$100.0\text{ kW}$].
- **Available Power ($P_{\text{available}}$)**: Instantaneous capability accounting for availability $A_k(t)$ and derating $\delta_{\text{derate}}$ [$100.0\text{ kW}$].
- **Credible Power ($P_{\text{credible}}$)**: Power output verified by physical fuel and operational constraints [$100.0\text{ kW}$].
- **Required Critical Power ($P_{\text{critical}}$)**: Continuous electrical load demanded by protected station assets [$11.6\text{ kW}$].
- **Deliverable Energy ($E_{\text{deliverable}}$)**: Time-integrated energy actually supplied to the bus over horizon $H = 6.0\text{ h}$ [kWh].

### Dimensional Check:
$$\text{Energy [kWh]} = \int_{0}^{6.0\text{ h}} P(\tau) \, d\tau = P_{\text{average}} \, [\text{kW}] \times 6.0 \, [\text{h}]$$

Multiplying $P_{\text{rated}} \times 6.0\text{ h}$ yields potential energy ($600\text{ kWh}$), but does NOT guarantee that fuel or continuous operating limits permit sustaining $P_{\text{rated}}$ for 6 hours.

---

## 5. Fuel Credibility & Availability Levels (Task 5)

Fuel credibility establishes five distinct operational tiers:

```
Tier 1: Generator Physically Available (Nameplate asset installed)
  ↓
Tier 2: Generator Operationally Available (Enabled, un-faulted, no lockout)
  ↓
Tier 3: Generator Fuelled (Day-tank contains fuel above minimum pump suction)
  ↓
Tier 4: Generator Fuel-Sufficient for 6 Hours (Usable fuel >= 22.4 Liters for 69.6 kWh)
  ↓
Tier 5: Generator Guaranteed to Serve Critical Load (All Tiers met + un-frozen lines)
```

**Codebase Reality**: POLARIS `StationState` currently verifies Tiers 1 and 2 (`diesel_running`), but does NOT enforce Tiers 3, 4, or 5 during MILP optimization.

---

## 6. Startup & Transient Semantics (Task 6)

When a diesel generator is currently **OFF** ($u_{\text{diesel}}(t_0) = 0$), five transient factors influence credibility:
1. **Startup Delay**: Engine cranking, oil pressure build-up, and speed governor settling ($30\text{ s}$ to $5\text{ min}$).
2. **Cold-Start Warm-Up**: Polar conditions require low-load warm-up before applying full load ($5\text{ min}$ to $15\text{ min}$).
3. **Minimum Loading Requirement**: POLARIS enforces $P_{\text{min}} = 10.0\text{ kW}$. Running below $10.0\text{ kW}$ causes engine wet-stacking and soot accumulation.
4. **Startup Fuel Penalty**: POLARIS models $2.0\text{ L}$ startup fuel penalty per start cycle.

---

## 7. Polar Environmental Operating Conditions (Task 7)

Polar operating environments impose specific constraints on diesel generator credibility:

- **Cold Ambient Temperature Derating**: Extremely cold intake air ($<-30^\circ\text{C}$) can degrade combustion efficiency and cause fuel line waxing if fuel heaters fail.
- **Altitude / Density Derating**: High-altitude polar plateaus (e.g. Dome C / Amundsen-Scott at $>2,800\text{ m}$) derate diesel output by $10\%$ to $20\%$ due to low air density.
- **Continuous Run Limits**: Extended continuous running without oil changes or maintenance can trigger engine failure.

### Evidence Classification:
- `DOCUMENTED FACT`: Diesel engines require positive fuel pressure and intake air to run.
- `ENGINEERING INTERPRETATION`: Polar fuel derating can be represented as a multiplicative factor $\delta_{\text{derate}} \in [0.80, 1.00]$.
- `POLARIS ASSUMPTION`: Current benchmark code assumes $\delta_{\text{derate}} = 1.00$ (no polar derating applied).

---

## 8. Safety & Failure Mode Evaluation Matrix (Task 8)

| Candidate Model | Failure Modes Detected | Failure Modes Missed | Telemetry Trusted | Risk of False Confidence | Risk of Premature Emergency | Real-Station Suitability |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **MODEL A** (Nameplate) | Component removal | Faults, fuel exhaustion | Static Config | **HIGH** | **LOW** | Unsuitable |
| **MODEL B** (Operating Cap) | Asset fault, lockout | Fuel exhaustion, leaks | `diesel_running` | **MEDIUM** | **LOW** | Acceptable (Basic) |
| **MODEL C** (Fuel Bounded) | Fuel depletion, low level | Engine mechanical seizure | Fuel volume sensor | **LOW** | **MEDIUM** | Highly Suitable |
| **MODEL D** (Demand Bounded) | Unserved critical deficit | Fuel exhaustion | `diesel_running`, Load | **LOW** | **LOW** | Highly Suitable |
| **MODEL E** (Time-Varying) | Startup delay, min load | Fuel sensor drop | Dynamic state vector | **LOW** | **MEDIUM** | Advanced SCADA |

---

## 9. Synthetic Benchmark vs. Real-Station Boundary (Task 9)

- **POLARIS Synthetic Benchmark**: Single $100\text{ kW}$ diesel generator, $10\text{ kW}$ min power, $200\text{ kWh}$ battery, $11.6\text{ kW}$ critical load. Fuel is modeled in simulator ($100\text{ L}$ initial) but optional in `StationState`.
- **Real Polar Station Boundary**: Real stations (e.g. Nuolja or Troll) utilize multiple redundant diesel generator sets, main bulk fuel tanks ($>10,000\text{ L}$), day-tanks ($500\text{ L}$), automated fuel transfer pumps, and SCADA engine control modules (ECUs).

---

## 10. Neutral Human Governance Decision Brief Options (Task 10)

*(Refer to [`GAP1_HUMAN_DECISION_BRIEF.md`](file:///home/punith-bs/01polaris%20%28Copy%29/investigations/emergency_trigger_governance_2026/GAP1_HUMAN_DECISION_BRIEF.md) for full neutral decision framing. No option is recommended or ranked).*

- **Option A**: Nameplate Rated Capacity ($E_{\text{gen\_A}} = H \cdot \sum P_{\text{rated}}$)
- **Option B**: Availability-Constrained Operating Capacity ($E_{\text{gen\_B}} = H \cdot \sum A_k \delta P_{\text{rated}}$)
- **Option C**: Fuel-Constrained Deliverable Energy ($E_{\text{gen\_C}} = \min(H \cdot P_{\text{avail}}, E_{\text{fuel\_usable}})$)
- **Option D**: Critical-Load Bounded Energy ($E_{\text{gen\_D}} = \min(H \cdot P_{\text{avail}}, \max(0, E_{\text{crit}} - E_{\text{batt}}))$)
- **Option E**: Time-Varying Status & Constraint Energy ($E_{\text{gen\_E}} = \int_0^H P_{\text{credible}}(\tau) d\tau$)

---

## 11. Decision Preconditions (Task 11)

- **Can the decision be made NOW using existing POLARIS evidence?**
  - **YES**. The human project owner can select between Options A, B, C, D, or E based on desired governance policy regarding fuel telemetry dependency and generator capacity capping.
  - No new synthetic experiments are required to make the governance choice.

---

## 12. Downstream Dependencies (Task 12)

The eventual GAP 1 decision impacts four downstream items:
1. **GAP 2 (Renewable Derating)**: Dictates how much net critical energy deficit remains for renewables to cover.
2. **GAP 3 (Emergency Exit)**: Determines whether generator availability ($A_k=1$) is required to exit Emergency Mode.
3. **GAP 4 (Missing Forecast Fallback)**: If generator energy alone covers $69.60\text{ kWh}$, missing renewable forecasts have zero impact.
4. **GAP 5 (Exit Path Topology)**: Influences whether the system can exit Emergency directly into `RESERVE_DEFICIT` mode once diesel generation is online.
