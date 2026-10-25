import os
import json
import csv
import hashlib

base_dir = "ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION"

# 1. POLARIS_EMS_OBJECTIVE_SPECIFICATION.md
md_content = """# POLARIS — GOVERNED EMS OBJECTIVE SPECIFICATION V2
## FORMAL MATHEMATICAL SPECIFICATION & GOVERNANCE BRIDGE

**Package Directory**: `ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Document Version**: 2.2.0 (Final Bounded Governed Draft)  
**Governance Status**: `EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT`  
**Policy Mapping Status**: `POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS`  
**D15 Reconciliation**: `D15_RECONCILIATION = PASS`  
**Stakeholder Input Status**: `STAKEHOLDER_POLICY_APPROVAL = APPROVED`  
**Implementation Authorization**: `NOT_AUTHORIZED`  
**Date**: 2026-09-22  

---

## 1. ABSOLUTE GOVERNANCE BOUNDARIES

```yaml
EMS_OBJECTIVE_SPECIFICATION:           ESTABLISHED_AS_GOVERNED_DRAFT
STAKEHOLDER_POLICY_APPROVAL:           APPROVED
POLICY_DEFINITION_RESOLUTION:          APPROVED_AS_POLICY_INPUT
POLICY_TO_MATH_MAPPING:                COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS
D15_RECONCILIATION:                    PASS

STAGE2_POLICY:                         RESOLVED
STAGE2_FORMULATION:                    REQUIRES_IMPLEMENTATION_SPECIFICATION
D10_POLICY:                            RESOLVED
D10_CURTAILMENT_DECOMPOSITION:         CONCEPTUAL_DECOMPOSITION_ONLY
D10_EXECUTABLE_CLASSIFICATION:         REQUIRES_IMPLEMENTATION_SPECIFICATION
D8_POLICY:                             RESOLVED
D8_PHYSICAL_FUEL_INVENTORY:            PHYSICAL_CONSTRAINT
D8_SEASONAL_FUEL_ACCOUNTING:           REQUIRES_IMPLEMENTATION_SPECIFICATION
FUEL_RELIABILITY_INFEASIBILITY:        REQUIRES_GOVERNANCE_CLARIFICATION

EMS_OBJECTIVE_MODIFICATION:            NOT_AUTHORIZED
EMS_IMPLEMENTATION_MODIFICATION:       NOT_AUTHORIZED
EMS_EXECUTION:                         NOT_AUTHORIZED
MPC_EXECUTION:                         NOT_AUTHORIZED
MODEL_TRAINING:                        NOT_AUTHORIZED
MODEL_MODIFICATION:                    NOT_AUTHORIZED
STAGE8_1_MODIFICATION:                 NOT_AUTHORIZED
V2_RERUN:                              NOT_AUTHORIZED
NEW_EMS_EXPERIMENT:                    NOT_AUTHORIZED
PRODUCTION_DEPLOYMENT:                 NOT_AUTHORIZED
```

### Critical Four-Layer Policy Separation
```
LAYER 1: CURRENT IMPLEMENTATION (FROZEN)
         - milp.py, battery.yaml, diesel.yaml, loads.yaml, optimizer.yaml
         - Prototype facts ($10,000/kWh soft penalty, 20% min SOC, cost proxy)
    ≠
LAYER 2: APPROVED STAKEHOLDER POLICY (16 DECISIONS D1–D16)
         - ems/specification/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET/
         - ems/specification/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION/
         - Human policy decisions (100% Critical SLA, Liters fuel metric, Lexicographic priority)
    ≠
LAYER 3: GOVERNED EMS OBJECTIVE SPECIFICATION (THIS DOCUMENT)
         - Implementation-independent mathematical translation of Layer 2
         - Explicit distinction between policy requirements and unresolved math interfaces
    ≠
LAYER 4: FUTURE EMS IMPLEMENTATION (NOT AUTHORIZED)
         - Future code changes in software satisfying Layer 3
```

---

## 2. EXECUTIVE OVERVIEW

This document establishes the **Governed EMS Objective Specification V2** for POLARIS. It translates the approved stakeholder policy decisions (D1–D16) into an explicit, auditable, implementation-independent mathematical specification.

The current implementation (`milp.py`) remains **FROZEN**. This specification does not alter code or run simulations; it serves as the authoritative mathematical bridge between policy decisions and future software engineering.

---

## 3. RESOLUTION OF D1–D16 STAKEHOLDER DECISIONS INTO SPECIFICATION

### D1 — Critical Load Classification
- **Abstract Load Sets**: 
  - $L_C \subset L$: Critical loads (protected in normal operation, $100\%$ service SLA).
  - $L_E \subset L$: Essential / Flexible loads (deferrable or managed load shedding).
  - $L_I \subset L$: Interruptible / Noncritical loads (shed first during deficit).
  - Total load set $L = L_C \cup L_E \cup L_I$, disjoint union.
- **Mathematical Load Service Representation**:
  - $P_{\text{demand}, i}(t)$: Demand of load tier $i \in \{C, E, I\}$ at timestep $t$.
  - $P_{\text{served}, i}(t)$: Served power to load tier $i$ at timestep $t$.
  - $P_{\text{unmet}, i}(t)$: Unmet power to load tier $i$ at timestep $t$.
  - $P_{\text{shed}, i}(t)$: Intentional shed power to load tier $i$ at timestep $t$.
  - $P_{\text{demand}, E}(t) = P_{\text{essential\_base}}(t) + P_{\text{flex}}(t)$ (essential base demand plus deferrable load task demand).
- **Specification Status**: `FULLY_SPECIFIED` (Policy & Load Sets); `STATION_DATA_REQUIRED` (Physical Circuit Mapping).

### D2 — Automated Tier-Based Load Shedding
- **Shedding Sequence**: Lower priority loads ($L_I$) are shed first, followed by flexible/essential loads ($L_E$). Critical loads ($L_C$) are strictly protected in normal/degraded operation.
- **Restoration Semantics & Timing**: Restoration occurs in reverse priority order ($L_E$ restored before $L_I$) once generation/storage margins recover.
- **Specification Status**: `POLICY_RESOLVED`; `REQUIRES_IMPLEMENTATION_SPECIFICATION` (Exact restoration dwell time & anti-chattering logic).

### D3 — Critical Load Service Target
- **Normal Governed Operation Target**: $100\%$ continuous critical energy service target.
- **Mathematical Requirement**:
  $$\sum_{i \in L_C} P_{\text{unmet}, i}(t) = 0, \quad \forall t \in T \quad \text{(Normal Governed Operation)}$$
- **Specification Status**: `FULLY_SPECIFIED` (Policy SLA); `ENGINEERING_VALIDATION_REQUIRED` (Physical hardware feasibility).

### D4 — Maximum Acceptable Unmet Critical Load
- **Maximum Unmet Energy**: $0\text{ kWh}$ under normal governed operation.
- **Rejection of Current Penalty**: The existing $c_{\text{unmet}} = \$10,000/\text{kWh}$ soft penalty in `milp.py` is an implementation fact, **NOT** the stakeholder policy SLA.
- **Specification Status**: `FULLY_SPECIFIED` (Normal SLA); `REQUIRES_GOVERNANCE_CLARIFICATION` (Infeasibility Emergency Response).

### D5 — Interruption Duration & Sub-Hourly Reliability Boundary
- **Intentional Interruption**: $0\text{ minutes}$ intentional interruption for Critical Loads.
- **Physical Gap Distinction**: EMS intentional shedding ($0\text{ min}$) is distinguished from ATS transfer gaps, UPS hold-up time, and generator startup latency. An hourly MILP ($\Delta t = 1.0\text{ h}$) cannot mathematically guarantee sub-hourly hardware continuity.
- **Specification Status**: `FULLY_SPECIFIED` (EMS Policy SLA); `STATION_DATA_REQUIRED` (ATS transfer time, UPS hold-up time, generator startup latency).

### D6 — Reliability Formulation
- **Hard Reliability Boundary**: Critical load reliability is formulated as a Stage 1 hard constraint in normal operation, not as a scalar penalty trade-off.
- **Feasible Reliability Set**:
  $$\Omega_{\text{rel}} = \left\{ x \in \Omega_{\text{phys}} \ \middle|\ P_{\text{unmet}, C}(t) = 0, \, \forall t \in T \right\}$$
- **Specification Status**: `FULLY_SPECIFIED`.

### D7 — Definition of "Minimize Diesel Use"
- **Primary Metric**: Physical fuel volume consumed in liters ($L$).
  $$\text{Fuel}_{\text{total}} = \sum_{t=1}^{H} \text{Fuel}_{\text{liter}}(t)$$
  $$\text{Fuel}_{\text{liter}}(t) = \left[ a \cdot P_{\text{diesel}}(t)^2 + b \cdot P_{\text{diesel}}(t) + c \cdot u_{\text{diesel}}(t) \right] \Delta t + \text{Fuel}_{\text{start}} \cdot v_{\text{start}}(t)$$
- **Secondary Metric**: Diesel electrical energy generated (kWh) tracked as secondary operational KPI. Fuel cost proxies ($\$0.625/\text{kWh}$) are explicitly rejected as policy metrics.
- **Specification Status**: `POLICY_RESOLVED`; `ENGINEERING_MODEL_INTERFACE` (Quadratic Fuel Form); `STATION_DATA_REQUIRED` (Fuel Coefficients $a, b, c$); `REQUIRES_IMPLEMENTATION_SPECIFICATION` (MILP Piecewise Linearization).

### D8 — Fuel Ceiling / Budget vs Critical Reliability
- **Budget & Inventory Separation**:
  - *Physical Fuel Inventory Constraint*: $F_{\text{rem}}(t) \ge 0$ (station cannot consume fuel that does not exist).
  - *Seasonal Fuel Budget Policy*: Seasonal / resupply-cycle budget $F_{\text{budget}}$ tracked dynamically in Stage 3 optimization.
  - *Emergency Exhaustion Infeasibility*: Physical fuel exhaustion makes Stage 1 100% Critical service infeasible. Per D14, fuel budget policy NEVER forces Critical Load shedding, but physical fuel exhaustion requires an emergency governance response (`FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`).
- **Specification Status**: `D8_POLICY = RESOLVED`; `D8_PHYSICAL_FUEL_INVENTORY = PHYSICAL_CONSTRAINT`; `D8_SEASONAL_FUEL_ACCOUNTING = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`.

### D9 — Renewable Utilization
- **Policy Principle**: Minimize avoidable renewable curtailment; no arbitrary percentage target (e.g., no hardcoded 50–70% target).
- **Hierarchy Position**: Renewable utilization is Stage 4 (subordinate to reliability, resilience, and fuel).
- **Specification Status**: `FULLY_SPECIFIED`.

### D10 — Renewable Curtailment
- **Curtailment Decomposition**:
  $$P_{\text{curt}}(t) = P_{\text{curt, necessary}}(t) + P_{\text{curt, avoidable}}(t)$$
  - *Necessary Curtailment*: Required for battery overcharge protection or generator minimum load constraints (unpenalized).
  - *Avoidable Curtailment*: Inefficient dispatch curtailment (minimized at Stage 4).
- **Executable Math Status**: Designated `CONCEPTUAL_DECOMPOSITION_ONLY` and `NOT_AN_AUTHORIZED_RUNTIME_CLASSIFICATION_RULE`. Policy is resolved, but runtime classification math is marked `D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
- **Specification Status**: `D10_POLICY = RESOLVED`; `D10_CURTAILMENT_DECOMPOSITION = CONCEPTUAL_DECOMPOSITION_ONLY`; `D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.

### D11 — Emergency Battery Reserve (EBR)
- **Four Storage Layer Architecture**:
  1. *Technical Min SOC Floor* ($\text{SOC}_{\text{min\_tech}} = 20\%$): Hard cell degradation protection constraint (`CURRENT_IMPLEMENTATION_FACT`).
  2. *Baseline Emergency Reserve Floor* ($\text{SOC}_{\text{EBR\_floor}}$): Hard operational reserve floor constraint ($\text{SOC}(t) \ge \text{SOC}_{\text{EBR\_floor}} > 20\%$).
  3. *Dynamic EBR Target* ($\text{SOC}_{\text{EBR\_target}}(t)$): Dynamic risk-adaptive reserve headroom target optimized in Stage 2.
  4. *Terminal SOC Requirement* ($\text{SOC}_{\text{terminal\_target}}(H)$): End-of-horizon storage requirement.
- **Specification Status**: `STAGE2_POLICY = RESOLVED`; `STAGE2_TAUTOLOGY = CORRECTED`; `STAGE2_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `NUMERICAL_CALIBRATION_REQUIRED` (Reserve Floor %).

### D12 — Terminal SOC Requirement
- **Dynamic Terminal SOC**: Horizon-end SOC constrained by dynamic risk requirement plus baseline floor:
  $$\text{SOC}(H) \ge \text{SOC}_{\text{terminal\_req}}(H) \ge \text{SOC}_{\text{terminal\_floor}}$$
- **Specification Status**: `POLICY_RESOLVED`; `NUMERICAL_CALIBRATION_REQUIRED` (Terminal SOC Floor %); `REQUIRES_IMPLEMENTATION_SPECIFICATION` (Horizon continuity formulation).

### D13 — Forecast Uncertainty Policy
- **Methodology**: Deterministic safety margins on point forecasts combined with real-time rolling MPC feedback correction.
  - $P_{\text{solar, cons}}(t) = (1 - \gamma_{\text{solar}}) P_{\text{solar, forecast}}(t)$
  - $P_{\text{wind, cons}}(t) = (1 - \gamma_{\text{wind}}) P_{\text{wind, forecast}}(t)$
  - $P_{\text{demand, cons}}(t) = (1 + \gamma_{\text{demand}}) P_{\text{demand, forecast}}(t)$
- **Provisional Margins Note**: Numerical margin values ($\gamma_{\text{solar}} \in [0.15, 0.25]$, $\gamma_{\text{wind}} \in [0.20, 0.30]$, $\gamma_{\text{demand}} = 0.10$) are provisional engineering defaults requiring historical forecast-error calibration.
- **Specification Status**: `POLICY_RESOLVED`; `NUMERICAL_CALIBRATION_REQUIRED` (Derate Margin values $\gamma$).

### D14 — Fuel vs Reliability Trade-off
- **Absolute Dominance**: Critical reliability has absolute priority over fuel conservation and fuel budget limits.
- **Rejection of 16,000:1 Ratio**: The current $16,000:1$ ratio ($\$10,000/\text{kWh} / \$0.625/\text{kWh}$) in `milp.py` is a scalar solver weighting artifact, **NOT** a stakeholder policy exchange rate.
- **Specification Status**: `FULLY_SPECIFIED`.

### D15 — Objective Priority Hierarchy & D15 Reconciliation Gate
- **Reconciliation Result**: **PASS (UNAMBIGUOUS)**. Both decision sheet and policy resolution agree on Option A.
- **Authoritative 4-Stage Hierarchy**:
  1. **Stage 1**: Critical Reliability ($P_{\text{unmet, C}}(t) = 0$).
  2. **Stage 2**: Emergency Battery Resilience & Reserve Maintenance ($\text{SOC}(t) \ge \text{SOC}_{\text{EBR\_floor}}$).
  3. **Stage 3**: Fuel Conservation ($\min \sum \text{Fuel}_{\text{liter}}(t)$).
  4. **Stage 4**: Renewable Utilization ($\min \sum P_{\text{curt, avoidable}}(t)$).
- **Specification Status**: `FULLY_SPECIFIED` (Priority Order); `REQUIRES_IMPLEMENTATION_SPECIFICATION` (Sequential solver implementation method).

### D16 — Governance Approval Authority
- **Multi-Tier Authority**: Three distinct approval tiers (Technical Validation, Mission/Ops Validation, Final Policy Approval). No unilateral policy modification authorized.
- **Specification Status**: `FULLY_SPECIFIED` (Workflow Structure); `STATION_DATA_REQUIRED` (Named Personnel Assignments).

---

## 4. FORMAL IMPLEMENTATION-INDEPENDENT MATHEMATICAL MODEL

### 4.1 Sets & Time Indexing
- $T = \{1, 2, \dots, H\}$: Planning horizon timesteps ($\Delta t = 1.0\text{ h}$, $H = 24\text{ h}$).
- $L = L_C \cup L_E \cup L_I$: Disjoint sets of Critical ($L_C$), Essential ($L_E$), and Interruptible ($L_I$) loads.

### 4.2 State Variables
- $\text{SOC}(t) \in [0, 1]$: Battery State of Charge at timestep $t$.
- $E_{\text{bat}}(t) = C_{\text{bat}} \cdot \text{SOC}(t) \in [E_{\text{min\_tech}}, E_{\text{max}}]$: Stored battery energy (Wh).
- $F_{\text{rem}}(t) \ge 0$: Remaining diesel fuel inventory (liters).
- $u_{\text{diesel}}(t) \in \{0, 1\}$: Generator operational state at timestep $t$.

### 4.3 Decision Variables
- $P_{\text{solar\_used}}(t), P_{\text{wind\_used}}(t) \ge 0$: Renewable power dispatched to busbar (W).
- $P_{\text{curt\_solar}}(t), P_{\text{curt\_wind}}(t) \ge 0$: Renewable power curtailed (W).
- $P_{\text{bat\_chg}}(t), P_{\text{bat\_dis}}(t) \ge 0$: Battery charge/discharge power (W).
- $u_{\text{chg}}(t), u_{\text{dis}}(t) \in \{0, 1\}$: Battery charging/discharging binary exclusivity flags.
- $P_{\text{diesel}}(t) \ge 0$: Diesel generator electrical power output (W).
- $v_{\text{start}}(t) \in \{0, 1\}$: Diesel generator startup event flag at timestep $t$.
- $P_{\text{served, } i}(t), P_{\text{unmet, } i}(t), P_{\text{shed, } i}(t) \ge 0$: Load power served, unmet, and shed for tier $i \in \{C, E, I\}$ (W).

### 4.4 Busbar Energy Balance Constraint
At every timestep $t \in T$, power balance on the station AC busbar must hold:
$$P_{\text{solar\_used}}(t) + P_{\text{wind\_used}}(t) + P_{\text{bat\_dis}}(t) + P_{\text{diesel}}(t) = P_{\text{served, } C}(t) + P_{\text{served, } E}(t) + P_{\text{served, } I}(t) + P_{\text{bat\_chg}}(t)$$

With generation availability constraints:
$$P_{\text{solar\_used}}(t) + P_{\text{curt\_solar}}(t) = P_{\text{solar, cons}}(t)$$
$$P_{\text{wind\_used}}(t) + P_{\text{curt\_wind}}(t) = P_{\text{wind, cons}}(t)$$

And load balance per tier $i$:
$$P_{\text{served, } i}(t) + P_{\text{unmet, } i}(t) + P_{\text{shed, } i}(t) = P_{\text{demand, } i, \text{cons}}(t)$$
where $P_{\text{demand, } E, \text{cons}}(t) = P_{\text{essential\_base, cons}}(t) + P_{\text{flex, cons}}(t)$, ensuring deferrable loads are not double-counted.

### 4.5 Battery Dynamics Constraints
$$E_{\text{bat}}(t+1) = E_{\text{bat}}(t) + \left( \eta_{\text{chg}} \cdot P_{\text{bat\_chg}}(t) - \frac{P_{\text{bat\_dis}}(t)}{\eta_{\text{dis}}} \right) \Delta t$$
$$0 \le P_{\text{bat\_chg}}(t) \le P_{\text{chg, max}} \cdot u_{\text{chg}}(t)$$
$$0 \le P_{\text{bat\_dis}}(t) \le P_{\text{dis, max}} \cdot u_{\text{dis}}(t)$$
$$u_{\text{chg}}(t) + u_{\text{dis}}(t) \le 1 \quad \forall t \in T$$
$$E_{\text{bat}}(t) \ge C_{\text{bat}} \cdot \text{SOC}_{\text{EBR\_floor}} > C_{\text{bat}} \cdot \text{SOC}_{\text{min\_tech}} \quad \forall t \in T$$
$$E_{\text{bat}}(H) \ge C_{\text{bat}} \cdot \text{SOC}_{\text{terminal\_floor}}$$

### 4.6 Diesel Generator Constraints
$$P_{\text{diesel, min}} \cdot u_{\text{diesel}}(t) \le P_{\text{diesel}}(t) \le P_{\text{diesel, max}} \cdot u_{\text{diesel}}(t)$$
$$v_{\text{start}}(t) \ge u_{\text{diesel}}(t) - u_{\text{diesel}}(t-1), \quad v_{\text{start}}(t) \in \{0, 1\}$$
$$F_{\text{rem}}(t+1) = F_{\text{rem}}(t) - \text{Fuel}_{\text{liter}}(t), \quad F_{\text{rem}}(t) \ge 0 \quad \text{(Physical Inventory Constraint)}$$
$$\sum_{t=1}^{H} \text{Fuel}_{\text{liter}}(t) \le F_{\text{budget\_remaining}}(t_0) \quad \text{(Seasonal Resupply Policy Budget)}$$

---

## 5. LEXICOGRAPHIC OPTIMIZATION HIERARCHY

The governed EMS objective is solved via sequential multi-stage optimization:

```
STAGE 0: Physical & Safety Hard Constraints (Busbar balance, battery limits, cell protection floor, F_rem >= 0)
   ↓
STAGE 1: Critical Reliability (Min P_unmet,C -> Enforce P_unmet,C = 0)
   ↓ (Inherit Stage 1 optimal value Z1* = 0)
STAGE 2: Emergency Battery Resilience (Maximize BESS reserve headroom above baseline EBR floor)
   ↓ (Inherit Stage 2 optimal value Z2*)
STAGE 3: Fuel Conservation (Min Total Diesel Liters Consumed)
   ↓ (Inherit Stage 3 optimal value Z3*)
STAGE 4: Renewable Utilization (Min Avoidable Renewable Curtailment)
```

### Mathematical Definition of Sequential Stages

- **Stage 1 (Critical Reliability)**:
  $$Z_1^* = \min_{x \in \Omega_0} J_1(x) = \sum_{t=1}^{H} \sum_{i \in L_C} P_{\text{unmet, } i}(t) \cdot \Delta t$$
  *Policy SLA Requirement*: $Z_1^* = 0\text{ Wh}$ in normal governed operation.  
  Set $\Omega_1 = \left\{ x \in \Omega_0 \mid J_1(x) \le Z_1^* + \epsilon_1 \right\}$.

- **Stage 2 (Emergency Battery Resilience)**:
  $$Z_2^* = \min_{x \in \Omega_1} J_2(x) = \sum_{t=1}^{H} \max\left(0, \text{SOC}_{\text{EBR\_target}}(t) - \text{SOC}(t)\right) + \max\left(0, \text{SOC}_{\text{terminal\_target}}(H) - \text{SOC}(H)\right)$$
  *(where $\text{SOC}(t) \ge \text{SOC}_{\text{EBR\_floor}}$ is enforced as a hard constraint in Stage 0/1).*  
  Set $\Omega_2 = \left\{ x \in \Omega_1 \mid J_2(x) \le Z_2^* + \epsilon_2 \right\}$.

- **Stage 3 (Fuel Conservation)**:
  $$Z_3^* = \min_{x \in \Omega_2} J_3(x) = \sum_{t=1}^{H} \text{Fuel}_{\text{liter}}(t)$$
  Set $\Omega_3 = \left\{ x \in \Omega_2 \mid J_3(x) \le Z_3^* + \epsilon_3 \right\}$.

- **Stage 4 (Renewable Utilization / Avoidable Curtailment Minimization)**:
  $$Z_4^* = \min_{x \in \Omega_3} J_4(x) = \sum_{t=1}^{H} P_{\text{curt, avoidable}}(t) \cdot \Delta t$$

---

## 6. CURRENT IMPLEMENTATION GAP ANALYSIS

| Area | Current Implementation (`milp.py`) | Approved Stakeholder Policy | Match | Required Future Change |
|------|-----------------------------------|----------------------------|-------|-----------------------|
| Objective Structure | Single scalar weighted objective ($c_{\text{unmet}} \cdot P_{\text{unmet}}$) | 4-Stage Lexicographic Optimization | MISMATCH | Implement multi-stage solver formulation |
| Critical Load SLA | Soft penalty $c_{\text{unmet}} = \$10,000/\text{kWh}$ | Hard constraint ($P_{\text{unmet, C}} = 0$, 0 kWh) | MISMATCH | Replace soft penalty with Stage 1 hard constraint |
| Fuel Objective Metric | Cost proxy ($\$0.625/\text{kWh}$) | Physical liters consumed ($L$) | MISMATCH | Replace cost proxy with quadratic fuel curve in liters |
| Load Tiering | Single aggregate demand $P_{\text{load}}$ | 3 Tiers (Critical, Essential, Interruptible) | MISMATCH | Add tier decomposition and load shedding variables |
| Battery Reserve | Fixed 20% min SOC | Dynamic Emergency Reserve + Baseline Floor | MISMATCH | Add dynamic EBR layer above 20% floor |
| Terminal SOC | Unconstrained at horizon boundary | Dynamic Terminal SOC + Floor | MISMATCH | Add terminal SOC constraint at timestep $H$ |
| Fuel Budget | No fuel budget or ceiling | Seasonal fuel budget + dynamic management | MISMATCH | Add seasonal fuel budget constraint |
| Forecast Uncertainty | Deterministic point forecast | Conservative margins + rolling MPC | PARTIAL | Add forecast uncertainty margin interface |
| Curtailment | Unpenalized $P_{\text{curt}}$ | Necessary unpenalized; Avoidable minimized | PARTIAL | Separate necessary vs avoidable curtailment |
| Governance Change Control | Ad-hoc script defaults | Multi-tier governance approval structure | MISMATCH | Establish change-control workflow |

---

## 7. NUMERICAL VALUE GOVERNANCE REGISTER

All numerical values in POLARIS are strictly classified:

- **STAKEHOLDER_AUTHORIZED_VALUE**:
  - Critical Load Service Target = $100\%$ (D03)
  - Maximum Unmet Critical Load = $0\text{ kWh}$ (D04)
  - Critical Interruption Duration = $0\text{ minutes}$ (D05)
  - Primary Fuel Metric = Liters (D07)
  - Lexicographic Hierarchy Order = Stage 1->2->3->4 (D15)

- **CURRENT_IMPLEMENTATION_FACT (PROTOTYPE ONLY — NOT POLICY)**:
  - Unmet load penalty = $\$10,000/\text{kWh}$ (`milp.py`)
  - Fuel cost proxy = $\$0.625/\text{kWh}$ (`milp.py`)
  - Objective ratio = $16,000:1$ (`milp.py`)
  - Technical min SOC = $20\%$ (`battery.yaml`)
  - Battery capacity = $200\text{ kWh}$ (`battery.yaml`)
  - Diesel min/max power = $10/100\text{ kW}$ (`diesel.yaml`)
  - Baseline critical demand = $30,000\text{ W}$ (`loads.yaml`)

- **PROVISIONAL_ENGINEERING_VALUE (REQUIRES CALIBRATION — NOT POLICY)**:
  - EBR Baseline Reserve = $35\%$ SOC
  - EBR Precautionary Reserve = $45\%$ SOC
  - Terminal SOC Floor = $35\%$ SOC
  - Precautionary Terminal SOC = $55-65\%$ SOC
  - Solar Forecast Derate = $-15\% \text{ to } -25\%$
  - Wind Forecast Derate = $-20\% \text{ to } -30\%$
  - Demand Safety Margin = $+10\%$
  - Emergency Fuel Reserve = $30\text{ days}$
  - Load Dwell Time = $5\text{ minutes}$
  - Critical Unmet Event Trigger = $15\text{ minutes}$
  - Critical Unmet Cumulative Trigger = $2.0\text{ kWh}$

- **REJECTED_NOT_AUTHORIZED**:
  - Renewable Utilization Target = $50-70\%$ (Explicitly rejected by D09: "no arbitrary % target").

---

## 8. REQUIREMENTS FOR FUTURE STATION VALIDATION

Before the Governed EMS Objective Specification can be implemented in code, the following physical station parameters must be empirically validated (`STATION_DATA_REQUIRED`):

1. **Circuit Load Inventory**: Physical mapping of station electrical circuits to Critical, Essential, and Interruptible tiers.
2. **Generator Fuel Curves**: Calibrated fuel consumption curves ($a, b, c$ parameters) across ambient temperatures.
3. **ATS & UPS Hardware Specs**: Measurement of Automatic Transfer Switch gap time and local UPS hold-up duration.
4. **Fuel Logistics**: Station fuel tank storage capacity, resupply delivery schedules, and winter transport limits.
5. **Battery Health & Thermal Bounds**: Vendor-confirmed true technical minimum SOC and cell degradation curves.
6. **Historical Forecast Error Distributions**: Statistical error distributions for solar irradiance, wind speed, and station load.
7. **Governance Personnel**: Named individuals assigned to Technical, Mission/Ops, and Final Approval tiers.

---

## 9. INFEASIBILITY & EMERGENCY POLICY

If physical stress (extreme weather, generator failure, physical fuel exhaustion) renders Stage 1 ($P_{\text{unmet, C}} = 0$) physically infeasible:

```yaml
INFEASIBILITY_RESPONSE:        REQUIRES_GOVERNANCE_CLARIFICATION
AUTOMATIC_ACTION:              DECLARE_EMERGENCY_MODE
LOGGING_REQUIREMENT:           MANDATORY_HIGH_PRIORITY_AUDIT_LOG
GOVERNANCE_NOTIFICATION:       IMMEDIATE_OPERATOR_ALERT
```

The EMS software must **NEVER** silently trade off critical load shedding for fuel savings during runtime. Emergency mode entry must be explicitly logged and flagged for post-event governance review.

---

## 10. FINAL SPECIFICATION GOVERNANCE STATUS

```yaml
EMS_OBJECTIVE_SPECIFICATION:           ESTABLISHED_AS_GOVERNED_DRAFT
STAKEHOLDER_POLICY_APPROVAL:           APPROVED
POLICY_DEFINITION_RESOLUTION:          APPROVED_AS_POLICY_INPUT
D1_D16_TRACEABILITY:                   COMPLETE
POLICY_TO_MATH_MAPPING:                COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS
D15_RECONCILIATION:                    PASS

CURRENT_EMS_IMPLEMENTATION:            FROZEN
EMS_CODE_MODIFIED:                    NO
OPTIMIZER_MODIFIED:                   NO
MILP_MODIFIED:                        NO
BATTERY_CONFIG_MODIFIED:              NO
DIESEL_CONFIG_MODIFIED:               NO
LOAD_CONFIG_MODIFIED:                 NO

MODEL_TRAINED:                         NO
MODEL_INFERRED:                        NO
EMS_EXECUTED:                          NO
MPC_EXECUTED:                          NO
MILP_EXECUTED:                         NO
DIGITAL_TWIN_EXECUTED:                 NO

V2_RERUN:                             NO
NEW_EXPERIMENT:                        NO

UNAUTHORIZED_POLICY_INFERENCE:          0
UNAUTHORIZED_NUMERICAL_POLICY_VALUES:  0

IMPLEMENTATION_AUTHORIZATION:          NOT_GRANTED
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW_AND_IMPLEMENTATION_SPECIFICATION_REVIEW
```
"""

with open(os.path.join(base_dir, "POLARIS_EMS_OBJECTIVE_SPECIFICATION.md"), "w") as f:
    f.write(md_content)
print("Updated POLARIS_EMS_OBJECTIVE_SPECIFICATION.md")

# 2. POLARIS_EMS_OBJECTIVE_SPECIFICATION.json
json_spec = {
    "package_metadata": {
        "title": "POLARIS Governed EMS Objective Specification V2",
        "directory": "ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/",
        "version": "2.2.0",
        "date": "2026-09-22",
        "governance_status": "EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT",
        "policy_mapping_status": "POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS",
        "implementation_authorization": "NOT_AUTHORIZED",
        "d15_reconciliation": "PASS"
    },
    "governance_flags": {
        "STAKEHOLDER_POLICY_APPROVAL": "APPROVED",
        "POLICY_DEFINITION_RESOLUTION": "APPROVED_AS_POLICY_INPUT",
        "EMS_OBJECTIVE_SPECIFICATION": "ESTABLISHED_AS_GOVERNED_DRAFT",
        "EMS_OBJECTIVE_MODIFICATION": "NOT_AUTHORIZED",
        "EMS_IMPLEMENTATION_MODIFICATION": "NOT_AUTHORIZED",
        "EMS_EXECUTION": "NOT_AUTHORIZED",
        "MPC_EXECUTION": "NOT_AUTHORIZED",
        "MODEL_TRAINING": "NOT_AUTHORIZED",
        "MODEL_MODIFICATION": "NOT_AUTHORIZED",
        "STAGE8_1_MODIFICATION": "NOT_AUTHORIZED",
        "V2_RERUN": "NOT_AUTHORIZED",
        "NEW_EMS_EXPERIMENT": "NOT_AUTHORIZED",
        "PRODUCTION_DEPLOYMENT": "NOT_AUTHORIZED"
    },
    "residual_status_keys": {
        "STAGE2_POLICY": "RESOLVED",
        "STAGE2_CONCEPTUAL_INTERFACE": "RESOLVED",
        "STAGE2_TAUTOLOGY": "CORRECTED",
        "STAGE2_FORMULATION": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "D10_POLICY": "RESOLVED",
        "D10_CURTAILMENT_DECOMPOSITION": "CONCEPTUAL_DECOMPOSITION_ONLY",
        "D10_EXECUTABLE_CLASSIFICATION": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "D8_POLICY": "RESOLVED",
        "D8_PHYSICAL_FUEL_INVENTORY": "PHYSICAL_CONSTRAINT",
        "D8_SEASONAL_FUEL_ACCOUNTING": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "FUEL_RELIABILITY_INFEASIBILITY": "REQUIRES_GOVERNANCE_CLARIFICATION"
    },
    "unauthorized_numerical_inferences": 0,
    "code_modifications_made": False,
    "simulations_executed": False
}

with open(os.path.join(base_dir, "POLARIS_EMS_OBJECTIVE_SPECIFICATION.json"), "w") as f:
    json.dump(json_spec, f, indent=2)
print("Updated POLARIS_EMS_OBJECTIVE_SPECIFICATION.json")

