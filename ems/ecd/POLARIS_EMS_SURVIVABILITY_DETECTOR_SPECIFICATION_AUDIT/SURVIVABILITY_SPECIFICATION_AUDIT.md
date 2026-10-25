# POLARIS EMS — EMERGENCY SURVIVABILITY METHOD & DETECTOR SPECIFICATION AUDIT REPORT

**Phase**: Emergency Survivability Method & Detector Specification Audit  
**Audit Date**: 2026-09-22  
**Status**: COMPLETED (READ-ONLY ENGINEERING & GOVERNANCE AUDIT)  
**Output Package**: `POLARIS_EMS_SURVIVABILITY_DETECTOR_SPECIFICATION_AUDIT`  

---

## 1. Executive Summary & Required Final Classifications

This report provides the read-only engineering and governance audit of the **Emergency Mode Detector** and forward **Battery & Diesel Survivability Methods** for the POLARIS Predictive Energy Management System (EMS).

### Final Governed Classifications

| Metric | Governed Classification | Justification |
| :--- | :--- | :--- |
| **`SURVIVABILITY_METHOD_STATUS`** | **`READY_FOR_FORMALIZATION`** | Mathematical equations for forward battery endurance ($T_{\text{batt}}$) and diesel endurance ($T_{\text{fuel}}$) are fully derived and causally sound based on existing physical models in `battery.yaml` and `diesel.yaml`. |
| **`EMERGENCY_DETECTOR_STATUS`** | **`REQUIRES_DATA`** | Detector architecture and state machine logic are specifiable, but calculation requires additive `fuel_remaining_l` in `StationState` and $D_{\text{critical}}$ critical demand tier in `ForecastBundle`. |
| **`OBJECTIVE_CLOSURE_STATUS`** | **`PARTIALLY_CLOSED`** | Mathematical formulation equations are closed; numerical parameters ($E_{\text{EBR,target}}$, $T_{\text{required}}$, degradation placement) await human governance authorization. |
| **`IMPLEMENTATION_AUTHORIZATION`** | **`NOT_GRANTED`** | This is a read-only audit. Implementation authorization remains strictly **NOT_GRANTED** until human governance resolves all open decisions in the decision register. |

---

## 2. Actual Repository Evidence & File/Symbol References

All analyses in this report are grounded strictly in inspected source code and configuration files:

1. **`system/schemas/station_state.py` (`StationState`)**:
   - Contains: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_solar_irradiance`, `last_observed_demand`, `last_observed_wind_generation`.
   - **Gap**: Lacks `fuel_remaining_l` (fuel tank level) and emergency assessment fields.
2. **`system/schemas/forecast_bundle.py` (`ForecastBundle`)**:
   - Contains: `timestamps` ($24\text{h}$), `solar_irradiance`, `solar_generation`, `wind_generation`, `demand`.
   - **Gap**: Only supplies aggregate `demand` vector; lacks critical demand tier $D_{\text{critical}}(t)$ breakdown and resupply arrival schedules.
3. **`system/optimization/implementations/milp.py` (`LocalMILPEnergyOptimizer`)**:
   - Contains: $360$ decision variables ($K=15$ per step over $H=24$ steps). Battery state transition: $E[t+1] = E[t] + \eta_{\text{chg}} p_{\text{chg}} \Delta t - (p_{\text{dis}} / \eta_{\text{dis}}) \Delta t$. Min energy bound: $E_{\min} = 40,000\text{ Wh}$ ($20\%$).
4. **`system/config/battery.yaml`**:
   - `capacity_wh`: $200,000.0\text{ Wh}$ ($200\text{ kWh}$). `min_soc_pct`: $20.0\%$. `max_soc_pct`: $95.0\%$. `charge_efficiency`: $0.92$. `discharge_efficiency`: $0.92$. `max_charge_power_w`: $50,000.0\text{ W}$. `max_discharge_power_w`: $50,000.0\text{ W}$. `deg_penalty_per_wh`: $0.00005$.
5. **`system/config/diesel.yaml`**:
   - `min_power_w`: $10,000.0\text{ W}$ ($10\text{ kW}$). `max_power_w`: $100,000.0\text{ W}$ ($100\text{ kW}$). `base_fuel_consumption_l_per_h`: $5.0\text{ L/h}$. `marginal_fuel_consumption_l_per_wh`: $0.00025\text{ L/Wh}$ ($0.25\text{ L/kWh}$). `fuel_cost_per_l`: $\$2.50/\text{L}$. `startup_cost`: $\$15.00$ ($6.0\text{ L}$ equivalent). `min_up_time_hours`: $2\text{ hours}$.
6. **`system/simulation/simulator.py` (`DigitalTwinSimulator`)**:
   - Closed-loop physical battery energy state update equation matching `milp.py`.

---

## 3. Battery Survivability Formulation

### 3.1 Usable Energy Definitions & Distinctions
- **Stored Battery Energy**: $E(t) = C_{\text{bat}} \times \frac{\text{SOC}(t)}{100\%} \quad [\text{Wh}]$.
- **Technical Minimum Energy Floor**: $E_{\min} = C_{\text{bat}} \times \frac{\text{min\_soc\_pct}}{100\%} = 40,000\text{ Wh} \quad (20\%)$.
- **Usable Cell Energy**: $E_{\text{usable\_cell}}(t) = \max\left(0, E(t) - E_{\min}\right) \quad [\text{Wh}]$.
- **Usable Bus Energy (Delivered to AC Load)**: $E_{\text{usable\_bus}}(t) = \left(E(t) - E_{\min}\right) \times \eta_{\text{dis}} \quad [\text{Wh}]$, where $\eta_{\text{dis}} = 0.92$.
- **Emergency Battery Reserve (EBR)**: Governed resilience target $E_{\text{EBR,target}}(t)$ above $E_{\min}$ (not a physical floor).

### 3.2 Causal Forward Battery Endurance ($T_{\text{batt}}$)
For a time-varying causal critical demand trajectory $D_{\text{critical}}(k)$ ($k=1..N$):

$$ E_{\text{critical,bus}}(N) = \sum_{k=1}^N D_{\text{critical}}(k) \cdot \Delta t \quad [\text{Wh}] $$

The forward battery endurance horizon $T_{\text{batt}}$ is the largest integer $N$ satisfying:

$$ T_{\text{batt}} = \max \left\{ N \in \mathbb{N} \;\middle|\; \frac{\sum_{k=1}^N D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}} \le E(t) - E_{\min} \quad \text{and} \quad D_{\text{critical}}(k) \le P_{\text{dis,max}}, \; \forall k \in \{1..N\} \right\} $$

---

## 4. Diesel Survivability Formulation

### 4.1 Generator Fuel Consumption Equations
From `diesel.yaml` parameters ($F_{\text{base}} = 5.0\text{ L/h}$, $F_{\text{marg}} = 0.00025\text{ L/Wh}$, $F_{\text{start}} = 6.0\text{ L}$):
When generator operates to serve critical load $D_{\text{critical}}(k)$, actual electrical output must satisfy $P_{\text{gen}}(k) = \max\left(P_{\text{diesel,min}}, D_{\text{critical}}(k)\right)$, where $P_{\text{diesel,min}} = 10,000\text{ W}$.

Fuel consumed in timestep $k$:

$$ F_{\text{step}}(k) = \left( F_{\text{base}} \cdot u_{\text{diesel}}(k) + F_{\text{marg}} \cdot P_{\text{gen}}(k) \right) \cdot \Delta t \quad [\text{Liters}] $$

### 4.2 Causal Forward Diesel Endurance ($T_{\text{fuel}}$)
Cumulative fuel required over $N$ hours to supply critical load (including startup fuel $F_{\text{start}}$ if starting from offline):

$$ F_{\text{required}}(N) = \sum_{k=1}^N F_{\text{step}}(k) + F_{\text{start}} \cdot v_{\text{start}} \quad [\text{Liters}] $$

The forward diesel endurance horizon $T_{\text{fuel}}$ is the largest integer $N$ satisfying:

$$ T_{\text{fuel}} = \max \left\{ N \in \mathbb{N} \;\middle|\; F_{\text{required}}(N) \le F_{\text{remaining}}(t) \quad \text{and} \quad D_{\text{critical}}(k) \le P_{\text{diesel,max}}, \; \forall k \in \{1..N\} \right\} $$

---

## 5. Required Survival Window & Adverse Renewable Baseline

### 5.1 Common Required Survival Window ($T_{\text{required}}$)
- **Repository Capability**: Current `ForecastBundle` provides a $24\text{-hour}$ horizon ($H=24$). Resupply schedule ($T_{\text{resupply}}$) is absent from schemas.
- **Mathematical Requirement**: Directly comparing battery and fuel survivability under Human Decision E3 requires evaluating BOTH resources against the **SAME required survival window** $T_{\text{required}}$ under the SAME critical demand trajectory. Comparing unmatched windows is mathematically invalid.
- **Governed Recommendation**: Use $T_{\text{required}} = T_{\text{resupply}}$ (hours until next authorized fuel delivery), defaulting to $H=24\text{h}$ when resupply schedule is unspecified.

### 5.2 Adverse Renewable Baseline
- **Zero Renewable Baseline ($P_{\text{solar}}=0, P_{\text{wind}}=0$)**: Fully causal; provides the most conservative, worst-case survivability baseline for storm/night emergency operation without hidden future truth (`EXISTING_ENGINEERING_ONLY`).
- **Conservative Quantile Forecast**: Uses lower uncertainty bound from `ForecastBundle`. Requires policy authorization (`MISSING_GOVERNANCE`).

---

## 6. Survivability Margins & Emergency Detector Logic

### 6.1 Survivability Margins & Normalized Ratios
For a common window $T_{\text{required}}$:
- **Hour Margins**: $M_{\text{batt}} = T_{\text{batt}} - T_{\text{required}}\quad [\text{hours}]$, $M_{\text{fuel}} = T_{\text{fuel}} - T_{\text{required}}\quad [\text{hours}]$.
- **Normalized Ratios**: $R_{\text{batt}} = \frac{T_{\text{batt}}}{T_{\text{required}}}$, $R_{\text{fuel}} = \frac{T_{\text{fuel}}}{T_{\text{required}}}$.
- **Policy E3 Limiting Resource Rule**: Under Policy E3, neither resource has permanent priority. The limiting resource is:

$$\text{Limiting Resource} = \arg\min \left( R_{\text{batt}}, R_{\text{fuel}} \right)$$

### 6.2 Detector State Machine & Interface
The `EmergencyAssessment` output struct contains:
- `operating_mode`: Enum (`NORMAL`, `EMERGENCY_BATTERY_WEAK`, `EMERGENCY_DIESEL_WEAK`, `EMERGENCY_CRITICAL_DEFICIT`).
- `t_batt_hours`, `t_fuel_hours`, `t_required_hours`, `margin_batt_hours`, `margin_fuel_hours`, `ratio_batt`, `ratio_fuel`, `limiting_resource`, `adverse_renewable_mode`, `freshness_timestamp`.
- **Architectural Placement**: StationState currently has 8 static fields. `EmergencyAssessment` requires a **dedicated new schema** or an **additive schema extension** to `StationState` (`ENGINEERING_DEFINITION_REQUIRED`).

---

## 7. Interaction with Objective Stages & Circular Loop Elimination

- **Detector Role (Pre-Solve)**: Evaluates initial state $S(t_0)$ and causal forecast exogenous to optimization. Sets `operating_mode` and `limiting_resource`.
- **Optimizer Role (Lexicographic Solve)**:
  - **Stage 1 (Reliability)**: Enforces $p_{\text{unmet,critical}} = 0$ unconditionally.
  - **Stage 2 (Resilience & EBR)**: In `EMERGENCY_BATTERY_WEAK`, Stage 2 protects battery energy. In `EMERGENCY_DIESEL_WEAK`, Stage 2/3 permits battery discharge to reduce diesel run hours.
  - **Stage 3 (Fuel)**: Minimizes fuel consumption.
  - **Stage 4 (Renewables)**: Minimizes avoidable curtailment.
- **Circular Loop Elimination**: The detector executes strictly **prior** to the MPC solve. The optimizer receives `operating_mode` as a read-only parameter and NEVER feeds its `DispatchPlan` output back into the detector for the same timestep.

---

## 8. Battery Degradation & Emergency Mode Override

- **Implementation Fact**: $c_{\text{deg}} = \$0.00005/\text{Wh}$ penalty in `milp.py`.
- **Policy Decision**: In `NORMAL` mode, degradation penalty is active to protect battery lifetime. In `EMERGENCY` mode, critical service takes absolute priority over battery lifetime; degradation penalty is **dynamically suppressed** ($c_{\text{deg}} = 0.0$).
- **Engineering Gap**: Requires formal placement of normal-mode degradation in Stage 3 or 4, and addition of dynamic override flag `c_deg=0.0` when `operating_mode != NORMAL`.

---

## 9. Definitive Human Decision Register

| Decision ID | Decision Title | Why Required | Existing Evidence | Blocking Status |
| :--- | :--- | :--- | :--- | :--- |
| **HD-01** | Authorize Numerical EBR Target ($E_{\text{EBR,target}}$) | Required for Stage 2 objective evaluation | Policy specifies EBR as resilience target; numerical value missing | **BLOCKING** |
| **HD-02** | Authorize Numerical Terminal Target ($E_{\text{terminal,target}}$) | Required for Stage 2 terminal SOC constraint | Code uses free terminal state $E(H) \ge E_{\min}$ | **BLOCKING** |
| **HD-03** | Authorize Survival Window ($T_{\text{required}}$) | Required for detector margin calculation | ForecastBundle horizon $H=24\text{h}$; resupply schedule absent | **BLOCKING** |
| **HD-04** | Authorize Adverse Renewable Assumption | Required for detector forward endurance calculation | Causal boundary requires explicit policy on future solar/wind | **BLOCKING** |
| **HD-05** | Assign Degradation Stage & Emergency Override | Required to position degradation in hierarchy | $c_{\text{deg}}=\$0.00005/\text{Wh}$ in prototype; unplaced in policy | **BLOCKING** |
| **HD-06** | Authorize Tank Capacity & Fuel Reserve Limits | Required for diesel survivability calculation | `diesel.yaml` fuel rates present; `fuel_remaining_l` missing from schema | **BLOCKING** |
| **HD-07** | Select Solver Architecture (Option A vs Option B) | Required to begin EMS implementation phase | Gap19 decision package completed; neutral evidence provided | **BLOCKING** |

---

## 10. Final Audit Responses (Closing Questions)

1. **What is already decided**:
   - Critical reliability is the highest-priority objective (Stage 1, $p_{\text{unmet,critical}}=0$).
   - EBR is a Stage 2 resilience target, not a hard physical constraint.
   - Optimizer does NOT self-declare emergency mode; an exogenous Emergency Mode Detector sets `operating_mode`.
   - Human Decision E3 governs emergency mode (neither resource has permanent priority; dynamically preserve whichever resource has the weaker survivability margin).
   - In emergency mode, critical service takes absolute priority over battery degradation cost.
2. **What is technically derivable from current code**:
   - Usable battery bus energy: $E_{\text{usable\_bus}}(t) = (E(t) - E_{\min}) \times 0.92$.
   - Forward battery endurance $T_{\text{batt}}$ for a time-varying critical demand trajectory.
   - Generator fuel consumption $F_{\text{step}}(k) = (5.0 \cdot u + 0.00025 \cdot P_{\text{gen}}) \Delta t$.
   - Forward diesel endurance $T_{\text{fuel}}$ for a time-varying critical demand trajectory.
   - Survivability ratios $R_{\text{batt}} = T_{\text{batt}}/T_{\text{required}}$, $R_{\text{fuel}} = T_{\text{fuel}}/T_{\text{required}}$, and limiting resource identification $\arg\min(R_{\text{batt}}, R_{\text{fuel}})$.
3. **What still requires human authorization**:
   - Numerical EBR target ($E_{\text{EBR,target}}$), numerical terminal energy target ($E_{\text{terminal,target}}$), required survival window ($T_{\text{required}}$), adverse renewable assumption (Zero vs Quantile), battery degradation stage assignment, fuel tank capacity/reserve bounds, and solver selection (Option A vs Option B).
4. **What data is missing**:
   - `fuel_remaining_l` in `StationState` schema.
   - $D_{\text{critical}}(t)$ critical demand tier vector in `ForecastBundle` schema.
   - `T_resupply` resupply arrival schedule in `ForecastBundle` schema.
5. **Whether we are ready to formalize the final EMS objective**:
   - **YES for mathematical equations**; **NO for numerical execution** until human decisions HD-01 through HD-07 are formally authorized.
6. **Whether implementation authorization should remain NOT_GRANTED**:
   - **NOT_GRANTED**. Implementation authorization must remain strictly **NOT_GRANTED** until human governance resolves all open decisions in the decision register.
