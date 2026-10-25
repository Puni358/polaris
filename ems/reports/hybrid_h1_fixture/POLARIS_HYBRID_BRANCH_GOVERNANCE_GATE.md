# POLARIS — Step 7: Hybrid Real-Data / Synthetic Engineering Branch Governance Gate

> **Governance Phase:** Step 7 — Hybrid Engineering Validation Branch Governance Gate  
> **Final Classification:** `HYBRID ENGINEERING BRANCH — DESIGN AUTHORIZED, EXECUTION NOT YET AUTHORIZED`  
> **Execution Mode:** Read-Only Specification & Governance Gate  
> **MILP Solves Executed:** `0` | **Simulations Executed:** `0` | **Architecture Modified:** `NO`  
> **Governance Date (UTC):** 2026-09-20  

---

## 1. Executive Summary & Closure of Real-Data Acquisition Track

The bounded real-data acquisition and contact campaign is now **closed** for the current research cycle. This decision is grounded in empirical findings from Steps 3 through 6:

- **Step 3 (Real-Data Readiness Audit):** Established `REAL_DEMAND_DATA = DATA_BLOCKED`. Zero high-resolution measured station demand files existed in the repository.
- **Step 4 (Bounded Route Reconnaissance):** Identified legitimate custodian access routes across 7 international polar organizations (AADC, SANAP, IPF, ACEP, BAS UK PDC, AWI PANGAEA, NPI), but zero raw data files were received locally (`ACTUALLY_RECEIVED = NO`).
- **Step 5 (Human Contact Execution Audit):** Confirmed that authenticated external email dispatches and web form submissions were unavailable in the automated CLI sandbox environment. Per Rule 5, no fake dispatches were produced, and 7 ready-to-send packages were logged for human review (`CONTACT_REQUESTS_SUBMITTED = 0`).
- **Step 6 (Public Repository Qualification Audit):** Audited public datasets across Princess Elisabeth (IPF), PANGAEA (AWI), and Norwegian Polar Data Centre (NPDC). Result: **NO qualifying publicly downloadable measured electrical-demand dataset exists** in open scientific repositories (`STEP6_FINAL_CLASSIFICATION = D`).

### Directive:
1. **STOP** searching for additional station electrical demand datasets.
2. **STOP** the email and contact dispatch campaign.
3. **STOP** all further synthetic optimization research until this hybrid branch is formally defined and governed.
4. **TRANSITION** to the governed **HYBRID REAL-DATA / SYNTHETIC ENGINEERING VALIDATION BRANCH**.

---

## 2. Current Evidence State & Governance Freeze

All prior frozen research evidence and governance states remain strictly intact:

```
STAGE8_1_FORECAST_RESEARCH   = FROZEN
V3_REFERENCE                = FROZEN
OFAT                        = COMPLETED / FROZEN RESEARCH
OFAT_PRODUCTION_CHAMPION    = NOT_ESTABLISHED

REAL_STATION_DEMAND         = DATA_BLOCKED
NUOLJA_WIND_GENERATION       = NOT_ESTABLISHED

SYSTEM_ARCHITECTURE         = VALIDATED
```

*Rule:* No blocked or non-established state is upgraded merely by authorizing the design of this hybrid engineering branch.

---

## 3. Hybrid Branch Purpose

The **Governed Hybrid Engineering Validation Branch** defines a scientifically honest, transparent validation pathway:

$$\begin{matrix}
\text{\textbf{REAL MEASURED INPUTS}} \\
\text{(SITES Nuolja } SW_{\text{in}}\text{ Solar Irradiance)} \\
+ \\
\text{\textbf{CONDITIONALLY ESTABLISHED PROXY INPUTS}} \\
\text{(SMHI 188790 Abisko 10m Wind Speed Proxy)} \\
+ \\
\text{\textbf{EXPLICIT SYNTHETIC ENGINEERING INPUTS}} \\
\text{(Synthetic Station Demand \& Reference Turbine Scenario)}
\end{matrix}
\quad \Longrightarrow \quad
\begin{matrix}
\text{\textbf{FROZEN POLARIS FORECAST / EMS}} \\
\text{(ForecastEngine } \rightarrow \text{ ForecastBundle} \rightarrow \text{ EMS MILP)} \\
\downarrow \\
\text{\textbf{CONTROLLED DIGITAL TWIN}} \\
\text{(DigitalTwin Simulator Execution)} \\
\downarrow \\
\text{\textbf{ENGINEERING EVALUATION}} \\
\text{(Causal Runtime \& MPC Integration Audit)}
\end{matrix}$$

### Authorized Purpose:
- Validate full end-to-end system integration.
- Validate causal runtime data flow across all components.
- Validate receding-horizon MPC and EMS dispatch behavior under deterministic constraints.
- Validate interface compatibility between `ForecastEngine`, `ForecastBundle`, `EnergyOptimizer`, `DispatchPlan`, and `DigitalTwin`.
- Evaluate engineering performance metrics under explicit, declared assumptions.

### Prohibited Scope (What this Hybrid Branch is NOT):
- **NOT** real Nuolja station demand validation.
- **NOT** measured station-demand empirical validation.
- **NOT** empirical proof of real diesel fuel savings at Nuolja.
- **NOT** empirical proof of real polar station grid reliability.
- **NOT** empirical proof of real Nuolja wind generation.
- **NOT** global real-world robustness certification.

---

## 4. Input Provenance Matrix

Every input stream entering the Hybrid Engineering Branch is strictly classified in the provenance matrix below:

| Input Variable | Source & Institution | Provenance Status | Real vs. Synthetic | Allowed Operational Use |
| :--- | :--- | :--- | :---: | :--- |
| **Nuolja Solar Irradiance ($SW_{\text{in}}$)** | SITES Nuolja Middle Station AWS (CY 2024, 8,784 steps) | `REAL_MEASURED` | **REAL MEASURED** | Solar forecasting and solar generation availability input only |
| **Wind Speed ($v_{\text{wind}}$)** | SMHI Station 188790 (Abisko Aut, 10m anemometer) | `CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY` | **REAL MEASUREMENT PROXY** | Explicitly proxy-labelled wind input only (**NOT** direct Nuolja measurement) |
| **Station Electrical Demand ($P_{\text{load}}$)** | POLARIS Synthetic Load Generator (Deterministic baseline) | `DATA_BLOCKED` | **SYNTHETIC** | Controlled engineering and digital-twin validation only (**NOT** real station load) |
| **Wind Electrical Generation ($P_{\text{wind}}$)** | Generic IEC 61400-12 Reference Turbine Specification | `NUOLJA_GENERATION_NOT_ESTABLISHED` | **SYNTHETIC ENGINEERING SCENARIO** | Controlled engineering scenario only if explicitly authorized (**NOT** Nuolja hardware) |
| **Solar-to-PV Mapping (D3)** | $P_{\text{raw}} = SW_{\text{in}} \times 300\text{ m}^2 \times 0.20 \times 0.85$; $P_{\text{solar}} = \min(P_{\text{raw}}, 60000\text{ W})$ | `ENGINEERING_MAPPING` | **ENGINEERING ASSUMPTION** | Synthetic PV array conversion model (**NOT** empirical station PV validation) |

---

## 5. Explicit Input Labeling & Anti-Deception Rules

To prevent any misleading presentation of results, every hybrid runtime log, CSV output, plot, and documentation artifact must enforce strict labeling:

1. **Synthetic Demand Trace:** Must be explicitly labeled **`SYNTHETIC_STATION_DEMAND`**. Never call it *"measured station load"* or *"Nuolja demand"*.
2. **Abisko Wind Speed:** Must be explicitly labeled **`ABISKO_10M_REGIONAL_WIND_PROXY`**. Never call it *"Nuolja measured wind"*.
3. **Synthetic Wind Generation:** Must be explicitly labeled **`GENERIC_ENGINEERING_WIND_SCENARIO`**. Never call it *"Nuolja wind generation"*.
4. **Solar PV Conversion:** Must be labeled **`D3_ENGINEERING_PV_MODEL`**. Never present it as *"measured station solar power"*.

---

## 6. Architecture & Interface Preservation

The frozen POLARIS system architecture and schemas must remain 100% unaltered:

```text
Data Provider (LocalDataProvider)
  │
  ▼
ForecastEngine (Stage8.1 Champion / Causal Receding Horizon)
  │
  ▼
ForecastBundle v1.0 (24h Receding Horizon, 1h Timestep)
  │
  ▼
EnergyOptimizer (EMS MILP / Class-F Solver)
  │
  ▼
DispatchPlan v1.0 (24h Dispatch Schedule)
  │
  ▼
DigitalTwin Simulator (D4-C1 Fault Containment)
  │
  ▼
Evaluation (Engineering Performance Audit)
```

### Closed-Loop MPC Protocol Preserved:
$$\text{Observe } \text{StationState}(t_0) \rightarrow \text{Forecast } H=24\text{h} \rightarrow \text{Optimize } H=24\text{h} \rightarrow \text{Execute } H_1 \rightarrow \text{Update } \text{StationState}(t_1) \rightarrow \text{Repeat}$$

*Rule:* Zero schema changes to `ForecastBundle`, `StationState`, `DispatchPlan`, `EMS Optimizer`, or `DigitalTwin` are authorized.

---

## 7. Hybrid Scenario Design (Design Only — Execution Prohibited)

The baseline hybrid scenario is specified below for future implementation:

- **SOLAR:** Real measured SITES Nuolja $SW_{\text{in}}$ solar irradiance (CY 2024, 8,784 timesteps).
- **WIND:** Abisko SMHI Station 188790 10m hourly wind speed (explicitly proxy-labelled).
- **DEMAND:** Synthetic station electrical demand trace generated by the frozen deterministic load profile generator.
- **WIND GENERATION:** Generic IEC micro-wind turbine power curve mapping (only if required by EMS schema; explicitly labeled generic assumption).
- **BATTERY STORAGE:** Existing frozen synthetic battery specification (50 kWh capacity, 25 kW max charge/discharge, 90% round-trip efficiency).
- **DIESEL GENERATOR:** Existing frozen synthetic diesel generator specification (60 kW rated, 15 kW minimum operating threshold, non-linear fuel curve).
- **EMS OPTIMIZER:** Frozen POLARIS Class-F MILP optimizer.
- **SIMULATION ENVIRONMENT:** Controlled synthetic DigitalTwin environment under D4-C1 fault containment semantics.

---

## 8. Synthetic Input Specification Requirements

### 8.1 Synthetic Demand Generator Requirements
Before any future execution, the synthetic demand generator must be formally specified and frozen with the following parameters:
- `base_demand_w`: Base continuous electrical load (W)
- `daily_profile_shape`: Deterministic 24-hour diurnal load shape
- `seasonal_profile_shape`: Polar winter/summer heating and lighting load multiplier
- `stochastic_noise_component`: Controlled pseudo-random noise term
- `peak_demand_w` & `min_demand_w`: Explicit physical load bounds
- `physical_units`: Explicitly declared (Watts W or kW)
- `random_seed`: Fixed integer seed ensuring 100% deterministic reproducibility
- `naming_rule`: Must be strictly named **`SYNTHETIC STATION DEMAND`**.

### 8.2 Wind Generation Scenario Requirements
Because Nuolja wind generation is `NOT_ESTABLISHED`, any scenario incorporating wind generation must document:
- `assumed_turbine_rated_power_w`: Rated capacity (e.g., 60 kW)
- `cut_in_speed_ms`, `rated_speed_ms`, `cut_out_speed_ms`: Standard IEC 61400-12 parameters
- `power_curve_source`: Standard mathematical model or generic commercial datasheet
- `scaling_assumptions`: Explicit rotor area and air density assumptions
- `naming_rule`: Must be strictly labeled **`GENERIC ENGINEERING ASSUMPTION — NOT NULLOJA HARDWARE`**.

---

## 9. Hybrid Claim Boundaries

All future POLARIS reports, presentations, and documentation MUST adhere to these exact claim boundaries:

### Allowed Claims:
> *"POLARIS was evaluated in a controlled hybrid engineering environment combining real measured solar irradiance, a conditionally established regional wind-speed proxy, and explicitly synthetic station demand."*

> *"The hybrid environment evaluates system integration, causal data flow, and EMS/MPC dispatch behavior under declared engineering assumptions."*

### Prohibited Claims:
> ❌ *"POLARIS was validated on real Nuolja station demand."*  
> ❌ *"POLARIS achieved X% fuel savings at Nuolja Station."*  
> ❌ *"Nuolja wind generation was forecast by POLARIS."*  
> ❌ *"System reliability was empirically demonstrated at the operational polar station."*  

---

## 10. Evaluation Metrics

All engineering evaluation metrics computed in the hybrid environment must carry the explicit designation **`HYBRID SYNTHETIC-ENVIRONMENT RESULT`**:

1. `diesel_fuel_liters` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
2. `diesel_energy_kwh` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
3. `renewable_energy_used_kwh` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
4. `renewable_curtailment_kwh` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
5. `battery_throughput_kwh` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
6. `battery_equivalent_cycles` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
7. `unmet_synthetic_critical_load_kwh` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
8. `constraint_violations_count` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
9. `forecast_rmse_mae` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
10. `optimizer_status_code` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)
11. `execution_time_ms` (`HYBRID SYNTHETIC-ENVIRONMENT RESULT`)

---

## 11. Required Pre-Execution Gates & Exclusions

### Required Pre-Execution Gates (Must be satisfied before ANY execution pass):
1. Formal specification and freeze of `SYNTHETIC_STATION_DEMAND` generator parameters.
2. Formal specification and freeze of `GENERIC_ENGINEERING_WIND_SCENARIO` parameters (if wind is included).
3. Formal governance authorization package approving the hybrid scenario execution plan.
4. Static audit verifying zero modifications to frozen `ForecastBundle`, `EMS`, and `DigitalTwin` contracts.

### Explicit Exclusions (STRICTLY PROHIBITED in Step 7):
- **ZERO** MILP solves executed.
- **ZERO** DigitalTwin simulations executed.
- **ZERO** model training or parameter tuning passes executed.
- **ZERO** modifications to production or EMS code.
- **ZERO** modifications to frozen V3, V4G, or OFAT evidence.
- **ZERO** resending of custodian email or contact requests.

---

## 12. Final Governance Decision

```
HYBRID_BRANCH_STATUS          = DESIGN_AUTHORIZED / EXECUTION_NOT_YET_AUTHORIZED
REAL_DEMAND_DATA              = DATA_BLOCKED
NUOLJA_WIND_GENERATION        = NOT_ESTABLISHED
REAL_STATION_VALIDATION       = NOT_AUTHORIZED / NOT_ESTABLISHED
HYBRID_ENGINEERING_VALIDATION = DESIGN-AUTHORIZED
```

---

## 13. Mandatory Safety & Governance Status Block

```
FROZEN_EVIDENCE_MODIFIED      = NO
MILP_SOLVES_EXECUTED          = 0
EXPERIMENT_RERUN              = NO
NEW_MODELING                  = NO
NEW_TUNING                    = NO
ARCHITECTURE_MODIFIED         = NO

STEP7_FINAL_CLASSIFICATION    = HYBRID ENGINEERING BRANCH — DESIGN AUTHORIZED, EXECUTION NOT YET AUTHORIZED
```
