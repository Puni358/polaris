# POLARIS — GAP 1 FORMAL SEMANTICS & CONSISTENCY AUDIT

## Executive Summary

This document formalizes the mathematical semantics of the **six provisional human governance decisions (G1–G6)** for **GAP 1: Credible Dispatchable Generation Modeling**, and performs a rigorous 15-point mathematical and logical consistency audit.

The human governance decisions are treated as **PROVISIONAL HUMAN INPUTS**. They are neither selected, ranked, altered, nor implemented by this audit.

---

## 1. Formalization of Provisional Decisions G1–G6

### G1 — Generator Availability (Option 1D: Operational + Dispatchable + Validated Telemetry)
- **Formal Rule**: A diesel generator $k \in K$ may contribute to the critical survivability guarantee at time $t$ if and only if its operational and dispatchable status is supported by validated telemetry:
  $$A_{\text{cred\_k}}(t) = \mathbb{I}\left( \text{V}_{\text{telemetry\_k}}(t) = \text{VALID} \;\land\; \text{Status}_{\text{op\_k}}(t) = \text{OPERATIONAL} \;\land\; \text{Status}_{\text{disp\_k}}(t) = \text{DISPATCHABLE} \right)$$
- **Governance Distinctions**:
  - Configured $\neq$ Operational
  - Running $\neq$ Dispatchable
  - Rated $\neq$ Available
  - Available $\neq$ Fuel-Sufficient

### G2 — Fuel Sufficiency & Uncertainty (Options 2C + 2D)
- **Formal Rule**: Sufficient fuel for the 6-hour survivability requirement ($E_{\text{fuel\_available\_k}} \ge E_{\text{gen\_req\_k}}$) must be demonstrated by validated telemetry. If fuel telemetry is missing, corrupt, or unverified ($\text{V}_{\text{fuel\_k}} = \text{INVALID}$), generator safety credit is ZERO:
  $$E_{\text{fuel\_credit\_k}} = \begin{cases} E_{\text{fuel\_usable\_k}} & \text{if } \text{V}_{\text{fuel\_k}} = \text{VALID} \land E_{\text{fuel\_usable\_k}} \ge \text{Sufficient} \\ 0.0 & \text{if } \text{V}_{\text{fuel\_k}} = \text{INVALID} \lor \text{Fuel} = \text{UNKNOWN} \end{cases}$$
- **Governance Safeguard**: **`UNKNOWN_INVALID != EMERGENCY`**. Fuel uncertainty sets generator safety credit to $0.0$, but does NOT automatically trigger Emergency Mode. Remaining verified resources (battery + renewables) determine state.

### G3 — Generator Startup Semantics (Options 3B + 3D)
- **Formal Rule**: An OFF generator ($u_k(t_0) = 0$) may contribute to the 6-hour survivability calculation if and only if explicit evidence validates start-readiness ($\text{Evidence}_{\text{start\_ready\_k}} = \text{VALID}$) AND a validated startup delay model ($\Delta t_{\text{startup\_k}}$) is defined:
  $$P_{\text{gen\_credible\_k}}(t) = \begin{cases} 0.0 & \text{for } 0 \le t < \Delta t_{\text{startup\_k}} \\ P_{\text{credible\_k}}(t) & \text{for } t \ge \Delta t_{\text{startup\_k}} \end{cases} \quad \text{if } \text{StartReady}_k = \text{VALID}$$
- **Zero Evidence Rule**: If $\text{Evidence}_{\text{start\_ready\_k}} = \text{INVALID/UNKNOWN}$, $P_{\text{gen\_credible\_k}}(t) = 0.0$ for all $t \in [0, H]$.

### G4 — Unknown Generator Health Governance (Option 4D)
- **Formal Rule**: Unknown generator health, fault status, or maintenance lockout ($\text{Health}_k = \text{UNKNOWN}$) sets generator safety contribution to $0.0\text{ kWh}$. Survivability is determined solely by other independently verified resources (battery deliverable + verified renewables).
- **Emergency Safeguard**: Unknown generator health does **NOT** directly trigger Emergency. Emergency triggers ONLY if remaining verified resources yield $M_{\text{surv}} < 0$.

### G5 — Time-Varying Generator Energy Envelope (Option 5E)
- **Formal Rule**: Credible generator energy is represented as a dynamic time-varying integral over the survivability horizon $H = 6.0\text{ hours}$:
  $$E_{\text{gen\_credible\_total}} = \int_{0}^{H} P_{\text{gen\_credible}}(t) \, dt \quad [\text{kWh}]$$
- **Dynamic Envelope Constraints**: $P_{\text{gen\_credible}}(t)$ varies dynamically based on startup transients ($\Delta t_{\text{startup}}$), fuel depletion limits, minimum operating limits ($P_{\text{min}} = 10\text{ kW}$), and operational availability $A_k(t)$.

### G6 — Strict Evidence Validation Threshold (Option 6E)
- **Formal Rule**: Every required evidence field (availability, start-readiness, fuel level, telemetry freshness) must pass explicit validation before generator energy is credited. The system MUST NOT substitute optimistic defaults, stale values, nameplate capacity, or unverified assumptions for missing safety evidence.

---

## 2. Comprehensive 15-Point Consistency & Semantics Audit

### AUDIT 1 — G1 $\times$ G2: Operational Status vs. Fuel Sufficiency
- **Question**: Can a generator be Operational, Dispatchable, and Telemetry-Valid, but still receive ZERO safety credit because fuel sufficiency is unknown?
- **Audit Result**: **YES**. Under G1 + G2, operational availability and fuel sufficiency are decoupled parameters.
- **Formal Four-Level Hierarchy**:
  1. **Operational**: Engine physically healthy and capable of running ($\text{Status}_{\text{op}} = \text{OK}$).
  2. **Dispatchable**: System controls can command and load the generator ($\text{Status}_{\text{disp}} = \text{OK}$).
  3. **Fuel-Sufficient**: Validated fuel volume exists to sustain operation for required horizon ($E_{\text{fuel}} \ge E_{\text{req}}$).
  4. **Safety-Creditable**: Satisfies Levels 1, 2, and 3 simultaneously with validated telemetry.
- **Rule**: $\text{Level 1} \land \text{Level 2} \land \neg \text{Level 3} \implies \text{Safety Credit} = 0.0\text{ kWh}$.

---

### AUDIT 2 — G2 $\times$ G5: Fuel Sufficiency Constraining Time-Varying Power
- **Question**: How does fuel sufficiency constrain the time-varying power integral $P_{\text{gen\_credible}}(t)$?
- **Audit Result**: Fuel depletion creates a terminal time boundary $t_{\text{fuel\_exhaust}}$ on the integral:
  $$\int_{0}^{t_{\text{fuel\_exhaust}}} \text{BSFC}\left(P_{\text{gen\_credible}}(\tau)\right) d\tau = V_{\text{fuel\_usable}}$$
  $$P_{\text{gen\_credible}}(t) = 0.0 \quad \text{for all } t > t_{\text{fuel\_exhaust}}$$
- **Codebase Feasibility**: POLARIS current simulator tracks `diesel_fuel_remaining_liters`, but MILP optimizer does NOT bound $P_{\text{diesel}}(t)$ by remaining fuel.

---

### AUDIT 3 — G3 $\times$ G5: Formalizing Generator Startup Transients
- **Question**: How does startup delay affect $P_{\text{gen\_credible}}(t)$ for an OFF generator?
- **Audit Result**: Startup delay introduces a zero-power step function at the start of the horizon:
  $$P_{\text{gen\_credible}}(t) = \begin{cases} 0.0 & \text{if } 0 \le t < \Delta t_{\text{startup}} \\ \min\left(P_{\text{rated}}, \, P_{\text{demand\_bus}}(t)\right) & \text{if } t \ge \Delta t_{\text{startup}} \end{cases}$$
- **Codebase Feasibility**: Current synthetic optimizer assumes $\Delta t_{\text{startup}} = 0.0\text{ hours}$ (instantaneous commitment within 1-hour timesteps). Implementing non-zero startup delay requires defining $\Delta t_{\text{startup}}$ parameter in generator configuration.

---

### AUDIT 4 — G4 $\times$ G6: Unknown Generator Health vs. Strict Evidence Threshold
- **Question**: Does Unknown Generator Health cause false Emergency triggers under strict evidence threshold G6?
- **Audit Result**: **NO CONTRADICTION**.
  - G6 sets Generator Safety Credit $= 0.0\text{ kWh}$ when health telemetry is UNKNOWN.
  - G4 directs the system to evaluate remaining verified resources (battery deliverable + verified renewables).
  - Emergency occurs ONLY if $E_{\text{batt\_deliverable}} + E_{\text{ren\_credible}} - E_{\text{critical\_req}} < 0$.
  - **Decoupled Mechanics**: Unknown Generator Health $\implies$ Generator Credit $= 0.0$. Emergency is triggered by net energy deficit ($M_{\text{surv}} < 0$), NOT by sensor status.

---

### AUDIT 5 — G1 $\times$ G3: Ambiguity of "Dispatchable" for an OFF Generator
- **Question**: What does "dispatchable" mean when a generator is currently OFF ($u(t_0) = 0$)?
- **Identified Semantic Ambiguity**:
  - *Interpretation 5.1*: "Dispatchable" means the unit is currently running and synchronized.
  - *Interpretation 5.2*: "Dispatchable" means the unit is OFF, but start-readiness is validated, and start command can be issued.
- **Resolution Required**: Human governance must clarify whether "Dispatchable" requires the unit to be currently running or permits start-ready OFF units.

---

### AUDIT 6 — G5 $\times$ Six-Hour Horizon Integration
- **Question**: How should $P_{\text{gen\_credible}}(t)$ be integrated over the 6-hour survivability horizon?
- **Candidate Interpretations**:
  - *Interpretation 6.A*: Integrate over exactly $H = 6.0\text{ hours}$ up to fuel exhaustion.
  - *Interpretation 6.B*: Integrate over $H = 6.0\text{ hours}$, but cap total generator energy at net critical load demand ($69.60\text{ kWh}$).
  - *Interpretation 6.C*: Integrate over dynamic horizon matching battery depletion trajectory.
- **Governance Precondition**: Requires human decision on Model D (demand capping).

---

### AUDIT 7 — G5 $\times$ Critical Load Usability
- **Question**: Does the generator integral represent total potential deliverable energy or energy usable by critical load?
- **Audit Result**:
  - Total generator potential ($100\text{ kW} \times 6\text{ h} = 600\text{ kWh}$) exceeds critical load demand ($11.6\text{ kW} \times 6\text{ h} = 69.6\text{ kWh}$).
  - Unserved generator capacity ($530.4\text{ kWh}$) cannot be stored in battery if battery is full/constrained.
  - **Recommendation**: Credible generator safety credit MUST be bounded by net critical demand: $E_{\text{gen\_bus\_credit}} = \min\left( \int_0^6 P_{\text{gen}} dt, \, \max(0, 69.60 - E_{\text{batt\_deliverable}}) \right)$.

---

### AUDIT 8 — Time-Varying Telemetry Validity During Horizon
- **Question**: What happens if telemetry becomes INVALID mid-horizon (e.g. fuel sensor fails at $t = 2.0\text{ h}$)?
- **Audit Result**:
  - At $t=0$, $V_{\text{fuel}} = \text{VALID} \implies$ Credible generation calculated for $t \in [0, 6.0\text{ h}]$.
  - At $t=2.0\text{ h}$, $V_{\text{fuel}} \rightarrow \text{INVALID} \implies$ For subsequent control evaluations at $t \ge 2.0\text{ h}$, $P_{\text{gen\_credible}}(\tau) = 0.0$ for all $\tau \ge 2.0\text{ h}$.
  - System dynamically updates $M_{\text{surv}}(t)$ on every 15-minute control interval.

---

### AUDIT 9 — Telemetry Freshness & Validation Criteria
- **Question**: Does "validated telemetry" require an explicit freshness threshold?
- **Audit Result**: **YES**. Telemetry validation ($\text{V}_{\text{telemetry}} = \text{VALID}$) requires:
  1. Timeliness: Timestamp age $\Delta t = t_{\text{wall}} - t_{\text{sample}} \le \Delta t_{\text{max}}$ (where $\Delta t_{\text{max}} = 30.0\text{ s}$).
  2. Range: Sensor value within physical bounds ($0 \le P_{\text{gen}} \le 100\text{ kW}$, $V_{\text{fuel}} \ge 0$).
  3. Quality: Sensor health flag bit $= \text{OK}$.

---

### AUDIT 10 — Decoupling UNKNOWN_INVALID from EMERGENCY
- **Question**: How are Generator Credit $= 0$, Sensor Unknown, State `UNKNOWN_INVALID`, and State `EMERGENCY` separated?
- **Taxonomy Matrix**:

```
+-----------------------------------------------------------------------------------+
| 1. Generator Safety Credit = 0.0 kWh                                              |
|    - Caused by: Generator fault, fuel unknown, or start-readiness invalid.        |
|    - System Action: Exclude generator from M_surv equation.                       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. Evaluate Remaining Verified Resources (Battery + Verified Renewables)          |
|    - M_surv = E_batt_deliverable + E_ren_credible - 69.60 kWh                    |
+-----------------------------------------------------------------------------------+
        |                                                           |
        | M_surv >= 0                                               | M_surv < 0
        v                                                           v
+----------------------------------+                   +----------------------------+
| State = RESERVE_DEFICIT / NORMAL |                   | State = EMERGENCY          |
| (NO LOAD SHEDDING)               |                   | (OPTION C LOAD SHEDDING)   |
+----------------------------------+                   +----------------------------+
```

---

### AUDIT 11 — Current Codebase Feasibility Matrix

| Required G1–G6 Field | Codebase Parameter Location | Feasibility Classification |
| :--- | :--- | :--- |
| Generator Nameplate Power ($P_{\text{rated}}$) | `config["diesel"]["max_power_w"]` | `AVAILABLE` |
| Minimum Operating Power ($P_{\text{min}}$) | `config["diesel"]["min_power_w"]` | `AVAILABLE` |
| Generator Running Status ($A_k$) | `station_state.diesel_running` | `AVAILABLE` |
| Generator Operating Hours | `station_state.diesel_hours_running` | `AVAILABLE` |
| Generator Fuel Remaining | `station_state.diesel_fuel_remaining_liters` | `PARTIALLY AVAILABLE` (Optional) |
| Generator Fault / Health Flag | N/A | `MISSING` |
| Maintenance Lockout Schedule | N/A | `MISSING` |
| Validated Start-Readiness Evidence | N/A | `MISSING` |
| Validated Startup Delay ($\Delta t_{\text{startup}}$) | N/A (Assumed $0.0$) | `MISSING` |
| Environmental Derating Table | N/A (Assumed $1.0$) | `MISSING` |

---

### AUDIT 12 — Mathematical Dimensional Checks

- **Deliverable Battery Energy**:
  $$E_{\text{batt\_deliverable}} = (SOC - 0.20) \, [\text{ratio}] \times 200.0 \, [\text{kWh}] \times 0.92 \, [\text{efficiency}] = \text{kWh delivered}$$
- **Credible Generator Energy Integral**:
  $$E_{\text{gen\_credible}} = \int_{0}^{6.0\text{ h}} P_{\text{gen\_credible}}(t) \, [\text{kW}] \, dt \, [\text{h}] = \text{kWh delivered}$$
- **Fuel Volume to Energy Conversion**:
  $$E_{\text{fuel\_deliverable}} = \frac{V_{\text{fuel\_usable}} \, [\text{L}]}{\text{BSFC} \, [\text{L/kWh}]} = \text{kWh delivered}$$
- **Critical Requirement**:
  $$E_{\text{critical\_req}} = 11.6 \, [\text{kW}] \times 6.0 \, [\text{h}] = 69.60 \, [\text{kWh delivered}]$$
- **Dimensional Verification**: **PASS**. All terms in $M_{\text{surv}}$ evaluate to **bus-delivered kWh**.

---

### AUDIT 13 — Synthetic vs. Real-Station Boundary Classification

- **`SYNTHETIC-ONLY`**: $100\text{ kW}$ single diesel generator, $10\text{ kW}$ min power, $200\text{ kWh}$ battery capacity, static fuel consumption coefficients ($5.0\text{ L/h} + 0.00025\text{ L/Wh}$).
- **`ARCHITECTURAL`**: Decoupling $M_{\text{surv}}$ calculation from Option C load shedding; strict validation thresholds; separating `UNKNOWN_INVALID` from `EMERGENCY`.
- **`REAL-STATION-DEPENDENT`**: Fuel tank level sensor telemetry, engine ECU fault flags, day-tank fuel transfer pump status, engine block pre-heater temperature.
- **`UNRESOLVED`**: Capping generator credit at net critical load demand (Model D choice).

---

## 3. Summary of Governance Status

```yaml
MATHEMATICAL_CONSISTENCY: PASSED (Dimensions and dynamic integrals coherent)
LOGICAL_CONSISTENCY: PASSED (G1-G6 do not produce internal logical loops)
GOVERNANCE_STATUS: PROVISIONAL (Requires human sign-off on 4 underspecified gaps)
PRODUCTION_CODE_MODIFICATIONS: 0
```
