# POLARIS — UI/UX ARCHITECTURE & VISUAL DESIGN SPECIFICATION
**(Fidelity & Implementation-Safety Corrected Specification)**

**Phase:** S8.1-UI-SPEC  
**Specification Type:** Local Industrial HMI / SCADA Control Room Interface Specification  
**Governance Decision:** **`B = UI/UX SPECIFICATION COMPLETE WITH DATA/UI LIMITATIONS`**  
**UI/UX Implementation Gate:** **`UI_UX_IMPLEMENTATION_PHASE = READY`**  
**Date:** 2026-09-19  

---

## 1. GOVERNANCE DECISION & PHASE STATUS

- **Final Governance Decision:** **`B = UI/UX SPECIFICATION COMPLETE WITH DATA/UI LIMITATIONS`**
- **Rationale:** The local HMI visual architecture, SCADA control room layout, information hierarchy, theme tokens, screen specifications, and runtime data mappings are fully defined and audit-verified. Material data limitations are explicitly embedded in the design specification: persistent synthetic mode badges, conditional regional wind proxy labeling, synthetic demand scenario indicators, and scientific claim firewalls.
- **UI/UX Implementation Phase Gate:** **`UI_UX_IMPLEMENTATION_PHASE = READY`**. Authorizes a separate future implementation phase to build the front-end presentation layer according to this frozen specification. This design phase does NOT modify any backend code or create frontend implementation files.

---

## 2. PROPOSED UI IMPLEMENTATION ARCHITECTURE

POLARIS is designed as a **Local SCADA / HMI System** for remote microgrids (such as polar research stations). The web browser serves strictly as the local graphical display surface. The POLARIS Python engine runs 100% offline on the local host machine.

```
+-------------------------------------------------------------------------+
|                           LOCAL HOST MACHINE                            |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                 POLARIS PYTHON RUNTIME ENGINE                      |  |
|  |                                                                   |  |
|  |  LocalDataProvider -> StationState -> Stage81ForecastEngine ->    |  |
|  |  ForecastBundle v1.0.0 -> LocalMILPEnergyOptimizer                |  |
|  |  (SciPy milp / HiGHS) -> DispatchPlan v1.0.0 ->                  |  |
|  |  DigitalTwinSimulator (MPC Step)                                   |  |
|  |                                                                   |  |
|  +-----------------------------+-------------------------------------+  |
|                                | Writes JSON Artifacts                  |
|                                v                                        |
|  +-------------------------------------------------------------------+  |
|  | PROPOSED LOCAL HMI SERVER / PRESENTATION ADAPTER                  |  |
|  | (Localhost HTTP Server / Presentation Layer)                     |  |
|  +-----------------------------+-------------------------------------+  |
|                                | HTTP / Localhost                       |
|                                v                                        |
|  +-------------------------------------------------------------------+  |
|  | BROWSER CONTROL ROOM DISPLAY SURFACE (SCADA HMI Dashboard)       |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

> [!NOTE]
> **ARCHITECTURE NOTICE:** The HMI server layer above represents a **PROPOSED UI IMPLEMENTATION ARCHITECTURE** for visualization. The browser remains purely a presentation surface; all forecasting, SciPy MILP optimization, MPC simulation, and evaluation logic reside entirely within the local offline POLARIS runtime.

---

## 3. DESIGN SYSTEM & VISUAL LANGUAGE

### Design Objective:
The interface must visually communicate:  
**"This machine is executing a local industrial Energy Management System for a polar microgrid."**  
It must **NOT** look like a generic consumer SaaS dashboard, startup landing page, or marketing analytics suite.

### Visual Aesthetic & Style Tokens:
- **Base Theme:** Dark Control Room Theme (`#0B0F19` deep space background, `#1E293B` slate card panels, `#334155` crisp grid borders).
- **Typography:** Industrial Monospace & Technical Sans (`JetBrains Mono` for telemetry numeric readouts, units, and timestamps; `Inter` for operational labels and structural headings).
- **Color Semantics:**
  - **GREEN (`#10B981`):** Operational / Normal / Nominal Energy Flow / Grid Active
  - **CYAN (`#06B6D4`):** Solar PV Generation / Telemetry Signals / Active Forecast
  - **AMBER (`#F59E0B`):** Warning / Diesel Generation Active / Synthetic Demand / Curtailment
  - **CRIMSON (`#EF4444`):** Fault State / D4-C1 Governed Infeasibility / Battery Low SOC Limit
  - **SLATE (`#64748B`):** Offline / Standby / Synthetic Mode / Muted Metadata
- **Panel Construction:** Square-cornered or micro-bevel ($2\text{px}$ radius max) industrial instrumentation panels with $1\text{px}$ slate borders and high contrast numeric readouts. Zero drop-shadow glow effects or fluffy cards.

### Strict Avoidance List (Anti-Patterns):
- ❌ No generic SaaS cards with floating drop shadows.
- ❌ No marketing hero sections or promotional text.
- ❌ No decorative glassmorphism, background blurs, or gradients.
- ❌ No chatbot windows or floating help bubbles.
- ❌ No futuristic 3D holographic representations.
- ❌ No fake real-time telemetry or fake live data claims.
- ❌ No unverified station turbine specifications or unvalidated wind generation claims.
- ❌ No unsupported reliability guarantees.

---

## 4. PERSISTENT SHELL SPECIFICATION

The UI layout features a persistent industrial frame with top status monitoring and left navigation.

### Top Status Bar (36px Height, Fixed Top):
```
+-------------------------------------------------------------------------------------------------------------------------+
| POLARIS HMI v1.0 | STATION: Nuolja Research Station | RUNTIME: LOCAL (OFFLINE) | CONTROL: MPC ACTIVE | 2024-06-01T12:00:00Z |
+-------------------------------------------------------------------------------------------------------------------------+
```
- **System Title:** `POLARIS Predictive EMS`
- **Station Identity:** `Nuolja Research Station (Synthetic Scenario S1)`
- **Runtime Mode Badge:** `LOCAL RUNTIME (100% OFFLINE)` *(Persistent Slate/Green Badge)*
- **Data Mode Badge:** `SYNTHETIC DEMONSTRATION` *(Persistent Amber Warning Badge)*
- **Control Loop Status:** `CLOSED-LOOP MPC: ACTIVE`
- **Simulated Timestamp Display:** Dynamic ISO timestamp populated from `StationState.timestamp`.

### Left Navigation Panel (220px Width, Fixed Left):
1. **[01] SYSTEM OVERVIEW** *(Primary Operational HMI View)*
2. **[02] ENERGY FLOW (SINGLE-LINE)** *(SCADA Electrical Bus Diagram)*
3. **[03] 24H FORECAST HORIZON** *(Stage 8.1 Irradiance & Load Bundles)*
4. **[04] OPTIMIZATION & MPC** *(SciPy MILP Horizon & DispatchPlan)*
5. **[05] DIGITAL TWIN SIMULATOR** *(State Progression & Battery SOC)*
6. **[06] ASSETS & INFRASTRUCTURE** *(Solar PV, Battery, Diesel Specs)*
7. **[07] STRESS SCENARIOS** *(S1 Normal, S2 Solar Drop, S4 Load Peak, S7 Fault)*
8. **[08] ALARMS & GOVERNANCE** *(D4-C1 Fault Logs & State Violations)*
9. **[09] ANALYTICS & REPORTS** *(EMS Performance & Fuel Metrics)*

---

## 5. SCREEN-BY-SCREEN SPECIFICATIONS

### Screen 1 — System Overview (Primary Control Room HMI)
- **Purpose:** At-a-glance operational state of the microgrid.
- **Layout:**
  - **Header Telemetry Ribbon:** Synthetic Station Load ($\text{kW}$), Solar Generation ($\text{kW}$), Diesel Generation ($\text{kW}$), Battery SOC ($\%$), Net Grid Balance.
  - **Center Panel (Energy Flow Diagram):** Microgrid AC / Energy Bus diagram connecting Solar, Diesel, Battery, and Synthetic Station Load with animated directional flow indicators.
  - **Bottom Left Panel:** 24-Hour Horizon Power Dispatch Stack (Area chart showing Solar Used, Battery Discharge, Diesel Power, and Synthetic Demand Curve).
  - **Bottom Right Panel:** Key Performance Indicators (`0 kWh unmet critical load during executed 24-step S1 synthetic trajectory`, `85.92 L diesel`, `84.82% renewable utilization`).

### Screen 2 — Energy Flow (SCADA Single-Line Diagram)
- **Purpose:** Electrical single-line SCADA representation of the microgrid energy bus.
- **Visual Elements:**
  - **Central AC Busbar (Microgrid AC / Energy Bus):** Thick solid line across screen. *(Note: Specific voltage/phase configuration is not exposed by authoritative runtime data and is labeled accordingly).*
  - **Inverter & Generator Nodes:** SCADA symbol blocks for PV Inverter, Battery Inverter, and Diesel Generator Set.
  - **Dynamic Flow Indicators:** Numerical readouts and active color highlights indicating real-time power magnitude and direction along each feeder branch.
  - **Battery Storage Gauge:** Vertical SOC level indicator ($0-100\%$) with operational limits ($20\% \text{ Min SOC} \dots 95\% \text{ Max SOC}$).

### Screen 3 — 24H Forecast Horizon
- **Purpose:** Visualize 24-hour predictive horizon produced by `Stage81ForecastEngine`.
- **Visual Elements:**
  - **Solar Irradiance Chart:** $H=24$ line chart ($\text{W/m}^2$) displaying point forecast values with degenerate point-only bounds indicator ($\text{lower} == \text{point} == \text{upper}$).
  - **Engine Metadata Card:** `Engine ID: stage81_solar`, `Features: 37-Feature HistGradientBoosting`, `Provenance: Frozen Stage 8.1 Champion`.
  - **Solar Generation Mapping Panel:** Displays qualified conversion: $\text{raw\_power} = \text{SW\_IN} \times 300\,\text{m}^2 \times 0.20 \times 0.85$, capped at $60000\,\text{W}$.
  - **Synthetic Demand Horizon Panel:** Displays synthetic demand scenario trajectory ($\text{W}$) labeled explicitly as `SYNTHETIC DEMONSTRATION DEMAND`.

### Screen 4 — Optimization & MPC Loop
- **Purpose:** Inspect SciPy MILP optimization decisions and DispatchPlan outputs.
- **Visual Elements:**
  - **MPC Status Panel:** Dynamic MPC step index ($k / N$), Solver Engine (`SciPy MILP / HiGHS`), Solve Time (`DispatchPlan.solve_time_ms` when available), Optimizer Status (`constraint_status`), Objective Value (`DispatchPlan.objective_value`).
  - **24-Step Dispatch Matrix Table:** Tabular view of `DispatchPlan` v1.0.0 showing hourly dispatch for Solar Used ($\text{kW}$), Battery Charge/Discharge ($\text{kW}$), Diesel Power ($\text{kW}$), and Curtailment ($\text{kW}$).
  - **H1 Execution Highlight:** First step ($t=1$) action highlighted in bright cyan as the executed dispatch sent to the Digital Twin.

### Screen 5 — Digital Twin & Simulation
- **Purpose:** Monitor state evolution of the simulated station across MPC steps.
- **Visual Elements:**
  - **State Trajectory Chart:** Historical SOC trajectory ($\%$), cumulative diesel energy ($\text{kWh}$), and cumulative renewable utilization ($\text{kWh}$).
  - **State Transition Monitor:** Displays step $k \rightarrow k+1$ transition details: $SOC_{k} \rightarrow SOC_{k+1}$, diesel runtime hours update, hidden ground truth alignment.

### Screen 6 — Stress Scenarios
- **Purpose:** Select and observe system response across authorized synthetic scenarios.
- **Scenario Options:**
  - **S1 Normal Operation:** Nominal synthetic load and solar profile.
  - **S2 Low Solar Availability:** Solar irradiance scaled by $0.10$.
  - **S4 High Demand:** Electrical demand scaled by $1.80$.
  - **S5 High Renewable / Curtailment:** Solar irradiance scaled by $2.00$.
  - **S6 Battery-Constrained:** Initial battery SOC set to $15\%$.
  - **S7 Governed Infeasibility / Fault:** Zero resource capacity under high load $\rightarrow$ D4-C1 zero-dispatch containment.

### Screen 7 — Alarms & Governance
- **Purpose:** Audit system alarms, D4-C1 fault containment events, and state boundary violations.
- **Visual Elements:**
  - **Alarm Log Table:** Timestamps, Severity (`GOVERNED_DEGRADED` / `CRITICAL`), Source (`EnergyOptimizer` / `DigitalTwin`), Message, State Response (`GOVERNED_ZERO_DISPATCH`).
  - **D4-C1 Governance Status Card:** Displays containment rules: `Zero Dispatch on Infeasibility`, `Objective Penalty = 1e9`, `No Ungoverned Fallbacks`.

### Screen 8 — Analytics & Reports
- **Purpose:** Post-hoc performance evaluation of EMS execution.
- **Visual Elements:**
  - **Fuel Summary:** Total Diesel Consumed ($85.92\,\text{L}$), Energy ($195.67\,\text{kWh}$), Specific Fuel Consumption ($0.439\,\text{L/kWh}$).
  - **Renewable Utilization:** Renewable Energy Used ($823.35\,\text{kWh}$), Curtailment ($147.33\,\text{kWh}$), Utilization Rate ($84.82\%$).
  - **Battery Health:** Total Throughput ($213.02\,\text{kWh}$), Equivalent Cycles ($1.065$).
  - **Scoped Reliability Display:** `0 kWh unmet critical load during the executed 24-step S1 synthetic trajectory`.

---

## 6. AUDITED RUNTIME DATA MAPPING TABLE

Every UI element is mapped to authoritative POLARIS runtime fields and classified by data status:

| UI Element | Source File / Class | Field Name | Unit | Data Status | Display Context & Limitations |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Synthetic Load** | `StationState` / `LocalDataProvider` | `last_observed_demand` | $\text{W}$ | **ESTABLISHED RUNTIME FIELD** | Labeled `SYNTHETIC DEMONSTRATION LOAD` |
| **Solar Generation** | `ForecastBundle` / `DispatchPlan` | `solar_generation.point[0]` | $\text{W}$ | **ESTABLISHED RUNTIME FIELD** | Formatted via PV engineering formula |
| **Diesel Power** | `DispatchPlan` v1.0.0 | `diesel_power[0]` | $\text{W}$ | **ESTABLISHED RUNTIME FIELD** | H1 executed diesel dispatch |
| **Battery SOC** | `StationState` | `battery_soc_pct` | $\%$ | **ESTABLISHED RUNTIME FIELD** | Simulated battery state ($0-100\%$) |
| **Battery Power** | `DispatchPlan` v1.0.0 | `battery_discharge[0] - battery_charge[0]` | $\text{W}$ | **DERIVED DISPLAY VALUE** | Positive = Discharge, Negative = Charge |
| **Solar Irradiance Forecast** | `ForecastBundle` v1.0.0 | `solar_irradiance.point` | $\text{W/m}^2$ | **ESTABLISHED RUNTIME FIELD** | Stage 8.1 24h point-only forecast horizon |
| **Optimizer Status** | `DispatchPlan` v1.0.0 | `constraint_status` | Text | **ESTABLISHED RUNTIME FIELD** | `OPTIMAL` / `OPTIMIZATION_INFEASIBLE` |
| **Objective Value** | `DispatchPlan` v1.0.0 | `objective_value` | Float | **ESTABLISHED RUNTIME FIELD** | SciPy MILP cost objective ($1e9$ on fault) |
| **Solve Time** | `DispatchPlan` v1.0.0 | `solve_time_ms` | $\text{ms}$ | **ESTABLISHED RUNTIME FIELD** | SciPy MILP solve time (when available) |
| **Total Diesel Fuel** | `run_report.json` | `ems_evaluation.total_diesel_fuel_liters` | $\text{L}$ | **ESTABLISHED RUNTIME FIELD** | Synthetic scenario total fuel |
| **Renewable Utilization** | `run_report.json` | `ems_evaluation.renewable_utilization_pct` | $\%$ | **ESTABLISHED RUNTIME FIELD** | Synthetic scenario renewable percentage |
| **Unmet Critical Load** | `run_report.json` | `ems_evaluation.unmet_critical_load_kwh` | $\text{kWh}$ | **ESTABLISHED RUNTIME FIELD** | Scoped: $0\,\text{kWh}$ during 24h S1 trajectory |
| **Execution Solar MAE** | `run_report.json` | `forecast_evaluation.solar_irradiance_metrics.mae` | $\text{W/m}^2$ | **ESTABLISHED RUNTIME FIELD** | Execution-run MAE on S1 ($42.3054\,\text{W/m}^2$) |
| **OOD Benchmark MAE** | Scientific Record | `STAGE8_1_OOD_BENCHMARK_MAE` | $\text{W/m}^2$ | **ESTABLISHED RUNTIME FIELD** | Frozen benchmark ($36.188657\,\text{W/m}^2$) |
| **Busbar Voltage/Phase** | N/A | `DATA_SOURCE_NOT_CURRENTLY_AVAILABLE` | $\text{V}$ | **DATA SOURCE NOT AVAILABLE** | Electrical configuration not exposed |
| **Nuolja Turbine Specs** | N/A | `DATA_SOURCE_NOT_CURRENTLY_AVAILABLE` | N/A | **DATA SOURCE NOT AVAILABLE** | Nuolja turbine specs not established |
| **Measured Station Load** | N/A | `DATA_SOURCE_NOT_CURRENTLY_AVAILABLE` | N/A | **DATA SOURCE NOT AVAILABLE** | Real station demand DATA BLOCKED |

---

## 7. PROVENANCE & PROHIBITED CLAIMS FIREWALL

### Wind Provenance Firewall:
- **Abisko 10m Wind Speed:** Labeled explicitly as `CONDITIONAL REGIONAL PROXY`.
- **Ross Island Enercon E-33:** Labeled explicitly as `ANTARCTIC REFERENCE TURBINE`.
- **Nuolja Turbine Specifications & Generation:** Labeled explicitly as `NOT ESTABLISHED / PROXY DATA`.

### Demand Provenance Firewall:
- Synthetic demand scenario values MUST be visually labeled `SYNTHETIC DEMONSTRATION LOAD` or `SYNTHETIC DEMAND SCENARIO` in the HMI header and charts.
- Words such as "Live station load" or "Measured station load" are **STRICTLY PROHIBITED**.

### Solar & Metric Firewall:
- **S1 Execution MAE:** Labeled `Execution-run Stage8.1 solar irradiance MAE: 42.3054 W/m² (on S1 synthetic trajectory)`.
- **Frozen Benchmark MAE:** Labeled `Frozen Stage8.1 OOD benchmark MAE: 36.188657 W/m² (on canonical frozen test set)`.
- **S1 Reliability:** Labeled `0 kWh unmet critical load during the executed 24-step S1 synthetic trajectory` (Do NOT display "100% system reliability").

---

## 8. IMPLEMENTATION FIREWALL & TRANSITION GATE

- **Implementation Firewall:** This specification phase creates **ZERO** backend or frontend code files. The underlying POLARIS Python runtime, schemas, interfaces, SciPy MILP optimizer, simulator, and scientific artifacts remain 100% untouched.
- **Transition Gate Authorization:**  
  `UI_UX_IMPLEMENTATION_PHASE = READY`  
  Authorizes a separate future UI implementation phase to build a lightweight web front-end consuming the existing POLARIS JSON runtime outputs.

---

## 9. SUCCESS CONDITION EVALUATION

```yaml
UI_UX_SPECIFICATION_STATUS: AUDITED_AND_CORRECTED
GOVERNANCE_DECISION: B_UI_UX_SPECIFICATION_COMPLETE_WITH_DATA_UI_LIMITATIONS
VISUAL_STYLE: SCADA_CONTROL_ROOM_HMI
OPTIMIZER_TERMINOLOGY: SCIPY_MILP_HIGHS_CORRECTED
UNSUPPORTED_VALUES_REMOVED: YES (400V, 42ms, 185.4, 12/24 corrected to dynamic/unexposed)
WIND_DEMAND_FIREWALLS: ENFORCED
BACKEND_CODE_MODIFIED: NO (0 Lines Modified)
FRONTEND_CODE_CREATED: NO (0 Files Created)
UI_UX_IMPLEMENTATION_PHASE: READY
```
