# POLARIS — GAP 1 HUMAN GOVERNANCE DECISION BRIEF

## Executive Decision Framing

This decision brief presents the governance choices for **GAP 1: Credible Dispatchable Generation Modeling**. 

All options are presented in strictly neutral technical language. No option is characterized as "best", "safest", "optimal", "preferred", "correct", or "winner". The choice belongs exclusively to the human project owner.

---

### CORE GOVERNANCE QUESTION

> **"What evidence is POLARIS allowed to count as CREDIBLE dispatchable generation when determining whether six-hour critical-load survivability ($69.60\text{ kWh}$ delivered demand) is guaranteed?"**

---

### OPTION A: Nameplate Rated Capacity ($E_{\text{gen\_A}} = H \cdot \sum P_{\text{rated}}$)

- **Definition**: Assumes all installed diesel generators can produce 100% rated power continuously for 6 hours ($6.0\text{ h} \times P_{\text{max}}$).
- **Formula**: $E_{\text{gen\_A}} = 6.0 \times P_{\text{rated\_max}}$
- **Required Inputs**: Generator nameplate rated capacity $P_{\text{rated\_max}}$.
- **Currently Available Inputs**: `config["diesel"]["max_power_w"]` ($100.0\text{ kW}$).
- **Missing Inputs**: None.
- **Assumptions**: Generator is 100% operational, un-faulted, fueled, and capable of infinite continuous running.
- **Failure Modes Detected**: Total physical removal of generator component from microgrid configuration.
- **Failure Modes Missed**: Mechanical fault, lockout, fuel depletion, fuel valve freeze, thermal derating.
- **Effect on Emergency Trigger Behavior**: Reduces frequency of Emergency entry by maximizing generator credit ($600\text{ kWh}$ potential credit for $100\text{ kW}$ generator).
- **Effect on UNKNOWN_INVALID Handling**: Unaffected by telemetry drops; relies solely on static configuration.
- **Synthetic Implementation Implications**: Fully compatible with existing synthetic codebase without code changes.
- **Future Real-Station Implications**: Ignores real-station sensor faults, fuel exhaustion, and maintenance lockouts.

---

### OPTION B: Availability-Constrained Operating Capacity ($E_{\text{gen\_B}} = H \cdot \sum A_k \delta P_{\text{rated}}$)

- **Definition**: Bounds generator credit by active operational availability ($A_k \in \{0, 1\}$) and polar derating ($\delta$).
- **Formula**: $E_{\text{gen\_B}} = 6.0 \times \sum \left( A_k(t) \cdot \delta_{\text{derate}} \cdot P_{\text{rated\_k}} \right)$
- **Required Inputs**: Generator availability status $A_k(t)$, derating coefficient $\delta_{\text{derate}}$.
- **Currently Available Inputs**: `station_state.diesel_running` ($A_k = 1$ if running).
- **Missing Inputs**: Explicit `generator_faulted` boolean, environmental temperature derating table.
- **Assumptions**: If generator is reported healthy/available, sufficient fuel exists for 6 hours of continuous operation.
- **Failure Modes Detected**: Generator trip, maintenance lockout, explicit component fault.
- **Failure Modes Missed**: Fuel tank exhaustion, fuel pump failure.
- **Effect on Emergency Trigger Behavior**: Triggers Emergency Mode immediately if generator trips on fault while battery $SOC < 57.83\%$.
- **Effect on UNKNOWN_INVALID Handling**: If availability telemetry $A_k$ is missing or corrupt, system enters `UNKNOWN_INVALID`.
- **Synthetic Implementation Implications**: Compatible with current `StationState.diesel_running` flag.
- **Future Real-Station Implications**: Provides standard microgrid SCADA availability integration.

---

### OPTION C: Fuel-Constrained Deliverable Energy ($E_{\text{gen\_C}} = \min(H \cdot P_{\text{avail}}, \; E_{\text{fuel\_usable}})$)

- **Definition**: Bounds credible generation by measured usable day-tank fuel volume ($V_{\text{fuel\_usable}}$) and brake specific fuel consumption.
- **Formula**: $E_{\text{gen\_C}} = \min\left( 6.0 \times \sum A_k P_{\text{rated}}, \; \frac{V_{\text{fuel\_usable}}}{\text{BSFC}_{\text{avg}}} \right)$
- **Required Inputs**: Usable fuel volume $V_{\text{fuel}}$, fuel density $\rho$, fuel consumption curve.
- **Currently Available Inputs**: `station_state.diesel_fuel_remaining_liters` (Optional; defaults to `None`).
- **Missing Inputs**: Usable vs un-pumpable fuel dead-volume threshold, verified fuel sensor checksum.
- **Assumptions**: Measured fuel tank level is accurate and fuel lines are un-frozen.
- **Failure Modes Detected**: Day-tank fuel depletion, fuel leakage, low fuel level.
- **Failure Modes Missed**: Mechanical engine seizure when fuel is present.
- **Effect on Emergency Trigger Behavior**: Triggers Emergency Mode preemptively if remaining fuel volume is insufficient for 6 hours of critical load ($< 22.4\text{ L}$ fuel for $69.6\text{ kWh}$ critical load).
- **Effect on UNKNOWN_INVALID Handling**: Missing or corrupt fuel sensor telemetry causes transition to `UNKNOWN_INVALID`.
- **Synthetic Implementation Implications**: Requires making `diesel_fuel_remaining_liters` mandatory in `StationState`.
- **Future Real-Station Implications**: Provides physical fuel-boundary protection for remote polar microgrids.

---

### OPTION D: Critical-Load-Bounded Generation ($E_{\text{gen\_D}} = \min(H \cdot P_{\text{avail}}, \; \max(0, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}}))$)

- **Definition**: Caps generator energy credit at the net critical energy requirement over 6 hours ($69.60\text{ kWh}$ max credit). Excess unserved generator capacity above critical load is not credited toward critical safety.
- **Formula**: $E_{\text{gen\_D}} = \min\left( 6.0 \times \sum A_k P_{\text{rated}}, \; \max\left(0, \, 69.60 - E_{\text{batt\_deliverable}}\right) \right)$
- **Required Inputs**: Generator availability $A_k$, critical load demand ($11.6\text{ kW}$ / $69.60\text{ kWh}$).
- **Currently Available Inputs**: `station_state.diesel_running`, `demand_critical`.
- **Missing Inputs**: None.
- **Assumptions**: Generator capacity above critical demand cannot be used to offset critical load deficit.
- **Failure Modes Detected**: Net critical energy deficit exceeding available generation.
- **Failure Modes Missed**: Fuel exhaustion if fuel telemetry is unmeasured.
- **Effect on Emergency Trigger Behavior**: Prevents a large generator (e.g. $100\text{ kW}$) from creating an artificially inflated positive margin $M_{\text{surv}} = +165\text{ kWh}$ when critical load requires only $69.6\text{ kWh}$.
- **Effect on UNKNOWN_INVALID Handling**: Standard telemetry validation.
- **Synthetic Implementation Implications**: Provides exact dimensional balance match in `ecd.py`.
- **Future Real-Station Implications**: Standard practice for critical bus survivability accounting.

---

### OPTION E: Time-Varying Status & Constraint Generation ($E_{\text{gen\_E}} = \int_0^6 P_{\text{credible}}(\tau) d\tau$)

- **Definition**: Integrates generator availability, startup delays, minimum loading constraints, and critical load trajectories dynamically over timesteps $\tau \in [0, 6.0\text{ h}]$.
- **Formula**: $E_{\text{gen\_E}} = \int_{0}^{6.0} \min\left( \sum A_k(\tau) P_{\text{rated\_k}}, \, P_{\text{critical}}(\tau) \right) d\tau$
- **Required Inputs**: Generator startup delay $\Delta t_{\text{start}}$, minimum load $P_{\text{min}}$, dynamic availability trajectory $A_k(\tau)$.
- **Currently Available Inputs**: `station_state.diesel_running`, `diesel_hours_running`.
- **Missing Inputs**: Engine pre-heat time, warm-up transient model.
- **Assumptions**: Generator startup time and minimum load constraints follow defined dynamics.
- **Failure Modes Detected**: Startup failure, delayed synchronization, minimum loading violation.
- **Failure Modes Missed**: Unmeasured fuel exhaustion.
- **Effect on Emergency Trigger Behavior**: Accounts for temporary battery discharge during generator startup transient.
- **Effect on UNKNOWN_INVALID Handling**: Requires complete dynamic state vector.
- **Synthetic Implementation Implications**: Requires evaluating discrete timesteps in `ecd.py`.
- **Future Real-Station Implications**: Matches advanced industrial microgrid controller execution.

---

## Technical Summary Matrix

| Option | Core Mathematical Rule | Required Data | Code Status | Primary Tradeoff |
| :---: | :--- | :--- | :--- | :--- |
| **Option A** | $E_{\text{gen}} = 6.0 \times P_{\text{max}}$ | Nameplate capacity | Fully Available | High potential credit vs no fault detection |
| **Option B** | $E_{\text{gen}} = 6.0 \times A_k \delta P_{\text{max}}$ | Availability flag $A_k$ | Available (`diesel_running`) | Detects generator trips vs assumes infinite fuel |
| **Option C** | $E_{\text{gen}} = \min(6.0 P_{\text{avail}}, E_{\text{fuel}})$ | Fuel volume $V_{\text{fuel}}$ | Optional (`fuel_remaining`) | Protects against fuel outage vs sensor dependency |
| **Option D** | $E_{\text{gen}} = \min(6.0 P_{\text{avail}}, E_{\text{crit\_req}} - E_{\text{batt}})$ | Critical load $P_{\text{crit}}$ | Fully Available | Exact dimensional match vs caps generator credit |
| **Option E** | $E_{\text{gen}} = \int_0^6 P_{\text{credible}}(\tau) d\tau$ | Startup delay & trajectory | Partially Available | Models startup transients vs highest complexity |
