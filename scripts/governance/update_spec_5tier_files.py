import os
import json
import csv
import hashlib

base_dir = "ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION"

# 1. POLARIS_EMS_OBJECTIVE_SPECIFICATION.md
md_content = """# POLARIS — GOVERNED EMS OBJECTIVE SPECIFICATION V2
## FORMAL MATHEMATICAL SPECIFICATION & GOVERNANCE BRIDGE

**Package Directory**: `ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Document Version**: 2.4.0 (Final Bounded Governed Draft)  
**Governance Status**: `EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT`  
**Policy Mapping Status**: `POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS`  
**D15 Reconciliation**: `D15_RECONCILIATION = PASS`  
**Next Governed Gate**: `NEXT_GOVERNED_STEP = EMS_OBJECTIVE_SPECIFICATION_REVIEW`  
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

D1_POLICY:                             RESOLVED
LOAD_TIER_COUNT:                       5
LOAD_TIER_FORMULATION:                 REQUIRES_IMPLEMENTATION_SPECIFICATION
STATION_LOAD_MAPPING:                  STATION_DATA_REQUIRED

STAGE1_ZERO_SLA:                       NORMAL_GOVERNED_TARGET
CRITICAL_RELIABILITY_INFEASIBILITY:    REQUIRES_GOVERNANCE_CLARIFICATION
EMERGENCY_MODE_ENTRY:                  REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING

STAGE2_POLICY:                         RESOLVED
STAGE2_CONCEPTUAL_INTERFACE:           RESOLVED
STAGE2_OBJECTIVE_SEMANTICS:            TARGET_SHORTFALL_MINIMIZATION
RESERVE_HEADROOM_MAXIMIZATION:         DESCRIPTIVE_INTERPRETATION_ONLY
STAGE2_TAUTOLOGY:                      CORRECTED
STAGE2_FORMULATION:                    REQUIRES_IMPLEMENTATION_SPECIFICATION

D10_POLICY:                            RESOLVED
D10_CURTAILMENT_DECOMPOSITION:         CONCEPTUAL_DECOMPOSITION_ONLY
D10_EXECUTABLE_CLASSIFICATION:         REQUIRES_IMPLEMENTATION_SPECIFICATION

D8_POLICY:                             RESOLVED
D8_PHYSICAL_FUEL_INVENTORY:            PHYSICAL_CONSTRAINT
D8_SEASONAL_FUEL_ACCOUNTING:           REQUIRES_IMPLEMENTATION_SPECIFICATION
D8_FUEL_BUDGET_CONSTRAINT_FORM:        REQUIRES_IMPLEMENTATION_SPECIFICATION
FUEL_RELIABILITY_INFEASIBILITY:        REQUIRES_GOVERNANCE_CLARIFICATION

HASH_AUDIT_MANIFEST:                   VERIFIED
HASH_AUDIT_SELF_HASH:                  SIDE_CAR_VERIFIED

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
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW
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
         - Human policy decisions (5 Load Tiers, 100% Critical SLA, Liters fuel metric, Lexicographic priority)
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

### D1 — Critical Load Classification (Five Disjoint Stakeholder Tiers)
- **Disjoint Policy Load Tiers**:
  - $L_C \subset L$: Critical loads (protected in normal operation, $100\%$ service SLA).
  - $L_E \subset L$: Essential loads (base station power, life safety, communications).
  - $L_D \subset L$: Deferrable loads (shiftable tasks, e.g. water pumping, thermal storage tasks).
  - $L_I \subset L$: Interruptible loads (sheddable operational tasks).
  - $L_N \subset L$: Noncritical loads (amenity heating/lighting, shed first during deficit).
  - Total load set $L = L_C \cup L_E \cup L_D \cup L_I \cup L_N$, disjoint union. Deferrable loads ($L_D$) are explicitly distinct from Essential loads ($L_E$). Interruptible loads ($L_I$) are explicitly distinct from Noncritical loads ($L_N$).
- **Mathematical Load Service Representation**:
  - $P_{\text{demand}, i}(t)$: Demand of load tier $i \in \{C, E, D, I, N\}$ at timestep $t$.
  - $P_{\text{served}, i}(t)$: Served power to load tier $i$ at timestep $t$.
  - $P_{\text{unmet}, i}(t)$: Unmet power to load tier $i$ at timestep $t$.
  - $P_{\text{shed}, i}(t)$: Intentional shed power to load tier $i$ at timestep $t$.
  - $P_{\text{demand}, D}(t)$: Deferrable load task demand with scheduling bounds.
- **Specification Status**: `D1_POLICY = RESOLVED`; `LOAD_TIER_COUNT = 5`; `LOAD_TIER_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `STATION_LOAD_MAPPING = STATION_DATA_REQUIRED`.

### D2 — Automated Tier-Based Load Shedding
- **Shedding Sequence**: Noncritical loads ($L_N$) are shed first, followed by Interruptible ($L_I$), Deferrable ($L_D$), and Essential ($L_E$). Critical loads ($L_C$) are strictly protected in normal/degraded operation.
- **Restoration Semantics & Timing**: Restoration occurs in reverse priority order ($L_E$ restored before $L_D$, $L_I$, $L_N$) once generation/storage margins recover.
- **Specification Status**: `POLICY_RESOLVED`; `REQUIRES_IMPLEMENTATION_SPECIFICATION` (Exact restoration dwell time & anti-chattering logic).

### D3 — Critical Load Service Target
- **Normal Governed Operation Target**: $100\%$ continuous critical energy service target.
- **Mathematical Requirement**:
  $$\sum_{i \in L_C} P_{\text{unmet}, i}(t) = 0, \quad \forall t \in T \quad \text{(Normal Governed Operation)}$$
- **Specification Status**: `STAGE1_ZERO_SLA = NORMAL_GOVERNED_TARGET`; `ENGINEERING_VALIDATION_REQUIRED` (Physical hardware feasibility).

### D4 — Maximum Acceptable Unmet Critical Load & Stage 1 Infeasibility
- **Maximum Unmet Energy**: $0\text{ kWh}$ under normal governed operation ($Z_1^* = 0\text{ Wh}$).
- **Physical Infeasibility Distinction**: If physical constraints do not admit $P_{\text{unmet, C}}(t) = 0$, $Z_1^* > 0$ flags physical infeasibility ($\text{CRITICAL\_RELIABILITY\_INFEASIBLE} = \text{TRUE}$). It does **not** authorize trading off critical load for fuel savings.
- **Rejection of Current Penalty**: The existing $c_{\text{unmet}} = \$10,000/\text{kWh}$ soft penalty in `milp.py` is an implementation fact, **NOT** the stakeholder policy SLA.
- **Specification Status**: `FULLY_SPECIFIED` (Normal SLA Target); `CRITICAL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`; `EMERGENCY_MODE_ENTRY = REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING`.

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
  - *Physical Fuel Inventory Constraint*: $F_{\text{rem}}(t) \ge 0$ (physical constraint; station cannot consume fuel that does not exist).
  - *Seasonal Fuel Budget Policy*: Seasonal / resupply-cycle budget $F_{\text{budget}}$ tracked dynamically in Stage 3 optimization. Candidate equation $\sum \text{Fuel}_{\text{liter}}(t) \le F_{\text{budget\_remaining}}(t_0)$ is a candidate constraint form, not an authorized executable formulation.
  - *Explicit Governance Wording*: *"The candidate fuel-budget inequality does not by itself implement the D14 lexicographic hierarchy. Fuel conservation is a policy objective subordinate to Critical reliability; the physical fuel inventory is a feasibility constraint. The mathematical interaction between seasonal/resupply accounting, the receding MPC horizon, and physical fuel exhaustion requires future implementation specification."*
  - *Emergency Exhaustion Infeasibility*: Physical fuel exhaustion makes Stage 1 100% Critical service infeasible. Per D14, fuel budget policy NEVER forces Critical Load shedding, but physical fuel exhaustion requires an emergency governance response (`FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`).
- **Specification Status**: `D8_POLICY = RESOLVED`; `D8_PHYSICAL_FUEL_INVENTORY = PHYSICAL_CONSTRAINT`; `D8_SEASONAL_FUEL_ACCOUNTING = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `D8_FUEL_BUDGET_CONSTRAINT_FORM = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`.

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

### D11 — Emergency Battery Reserve (EBR) & Stage 2 Semantics
- **Four Storage Layer Architecture**:
  1. *Technical Min SOC Floor* ($\text{SOC}_{\text{min\_tech}} = 20\%$): Hard cell degradation protection constraint (`CURRENT_IMPLEMENTATION_FACT`).
  2. *Baseline Emergency Reserve Floor* ($\text{SOC}_{\text{EBR\_floor}}$): Hard operational reserve floor constraint ($\text{SOC}(t) \ge \text{SOC}_{\text{EBR\_floor}} > 20\%$).
  3. *Dynamic EBR Target* ($\text{SOC}_{\text{EBR\_target}}(t)$): Dynamic risk-adaptive reserve headroom target optimized in Stage 2.
  4. *Terminal SOC Requirement* ($\text{SOC}_{\text{terminal\_target}}(H)$): End-of-horizon storage requirement.
- **Stage 2 Objective Semantics**:
  - Formal Mathematical Objective: `TARGET_SHORTFALL_MINIMIZATION` ($\min \sum \max(0, \text{SOC}_{\text{EBR\_target}}(t) - \text{SOC}(t))$).
  - Descriptive Interpretation: *"RESERVE_HEADROOM_MAXIMIZATION IS DESCRIPTIVE, NOT AN INDEPENDENT MATHEMATICAL OBJECTIVE."*
- **Specification Status**: `STAGE2_POLICY = RESOLVED`; `STAGE2_OBJECTIVE_SEMANTICS = TARGET_SHORTFALL_MINIMIZATION`; `RESERVE_HEADROOM_MAXIMIZATION = DESCRIPTIVE_INTERPRETATION_ONLY`; `STAGE2_TAUTOLOGY = CORRECTED`; `STAGE2_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`; `NUMERICAL_CALIBRATION_REQUIRED` (Reserve Floor %).

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
- $L = L_C \cup L_E \cup L_D \cup L_I \cup L_N$: Disjoint sets of Critical ($L_C$), Essential ($L_E$), Deferrable ($L_D$), Interruptible ($L_I$), and Noncritical ($L_N$) loads.

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
- $P_{\text{served, } i}(t), P_{\text{unmet, } i}(t), P_{\text{shed, } i}(t) \ge 0$: Load power served, unmet, and shed for tier $i \in \{C, E, D, I, N\}$ (W).

### 4.4 Busbar Energy Balance Constraint
At every timestep $t \in T$, power balance on the station AC busbar must hold:
$$P_{\text{solar\_used}}(t) + P_{\text{wind\_used}}(t) + P_{\text{bat\_dis}}(t) + P_{\text{diesel}}(t) = \sum_{i \in \{C, E, D, I, N\}} P_{\text{served, } i}(t) + P_{\text{bat\_chg}}(t)$$

With generation availability constraints:
$$P_{\text{solar\_used}}(t) + P_{\text{curt\_solar}}(t) = P_{\text{solar, cons}}(t)$$
$$P_{\text{wind\_used}}(t) + P_{\text{curt\_wind}}(t) = P_{\text{wind, cons}}(t)$$

And load balance per tier $i \in \{C, E, D, I, N\}$:
$$P_{\text{served, } i}(t) + P_{\text{unmet, } i}(t) + P_{\text{shed, } i}(t) = P_{\text{demand, } i, \text{cons}}(t)$$

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
$$\sum_{t=1}^{H} \text{Fuel}_{\text{liter}}(t) \le F_{\text{budget\_remaining}}(t_0) \quad \text{(Candidate Fuel Budget Constraint Form)}$$

---

## 5. LEXICOGRAPHIC OPTIMIZATION HIERARCHY

The governed EMS objective is solved via sequential multi-stage optimization:

```
STAGE 0: Physical & Safety Hard Constraints (Busbar balance, battery limits, cell protection floor, F_rem >= 0)
   ↓
STAGE 1: Critical Reliability (Min P_unmet,C -> Enforce P_unmet,C = 0)
   ↓ (Inherit Stage 1 optimal value Z1* = 0)
STAGE 2: Emergency Battery Resilience (Target-shortfall minimization above baseline EBR floor)
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

- **Stage 2 (Emergency Battery Resilience — Target-Shortfall Minimization)**:
  $$Z_2^* = \min_{x \in \Omega_1} J_2(x) = \sum_{t=1}^{H} \max\left(0, \text{SOC}_{\text{EBR\_target}}(t) - \text{SOC}(t)\right) + \max\left(0, \text{SOC}_{\text{terminal\_target}}(H) - \text{SOC}(H)\right)$$
  *(where $\text{SOC}(t) \ge \text{SOC}_{\text{EBR\_floor}}$ is enforced as a hard constraint in Stage 0/1; "reserve-headroom maximization" is descriptive).*  
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
| Load Tiering | Single aggregate demand $P_{\text{load}}$ | 5 Tiers (Critical, Essential, Deferrable, Interruptible, Noncritical) | MISMATCH | Add 5-tier load variables & scheduling logic |
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

1. **Circuit Load Inventory**: Physical mapping of station electrical circuits to Critical, Essential, Deferrable, Interruptible, and Noncritical tiers.
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
INFEASIBILITY_RESPONSE:                               REQUIRES_GOVERNANCE_CLARIFICATION
CRITICAL_RELIABILITY_INFEASIBILITY:                   REQUIRES_GOVERNANCE_CLARIFICATION
EMERGENCY_MODE_ENTRY:                                 REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING
EMERGENCY_NOTIFICATION_WORKFLOW:                      REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING
LOGGING_REQUIREMENT:                                  MANDATORY_HIGH_PRIORITY_AUDIT_LOG
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
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW
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
        "version": "2.4.0",
        "date": "2026-09-22",
        "governance_status": "EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT",
        "policy_mapping_status": "POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS",
        "implementation_authorization": "NOT_AUTHORIZED",
        "d15_reconciliation": "PASS",
        "next_governed_step": "EMS_OBJECTIVE_SPECIFICATION_REVIEW"
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
        "D1_POLICY": "RESOLVED",
        "LOAD_TIER_COUNT": 5,
        "LOAD_TIER_FORMULATION": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "STATION_LOAD_MAPPING": "STATION_DATA_REQUIRED",
        "STAGE1_ZERO_SLA": "NORMAL_GOVERNED_TARGET",
        "CRITICAL_RELIABILITY_INFEASIBILITY": "REQUIRES_GOVERNANCE_CLARIFICATION",
        "EMERGENCY_MODE_ENTRY": "REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING",
        "STAGE2_POLICY": "RESOLVED",
        "STAGE2_CONCEPTUAL_INTERFACE": "RESOLVED",
        "STAGE2_OBJECTIVE_SEMANTICS": "TARGET_SHORTFALL_MINIMIZATION",
        "RESERVE_HEADROOM_MAXIMIZATION": "DESCRIPTIVE_INTERPRETATION_ONLY",
        "STAGE2_TAUTOLOGY": "CORRECTED",
        "STAGE2_FORMULATION": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "D10_POLICY": "RESOLVED",
        "D10_CURTAILMENT_DECOMPOSITION": "CONCEPTUAL_DECOMPOSITION_ONLY",
        "D10_EXECUTABLE_CLASSIFICATION": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "D8_POLICY": "RESOLVED",
        "D8_PHYSICAL_FUEL_INVENTORY": "PHYSICAL_CONSTRAINT",
        "D8_SEASONAL_FUEL_ACCOUNTING": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "D8_FUEL_BUDGET_CONSTRAINT_FORM": "REQUIRES_IMPLEMENTATION_SPECIFICATION",
        "FUEL_RELIABILITY_INFEASIBILITY": "REQUIRES_GOVERNANCE_CLARIFICATION",
        "HASH_AUDIT_MANIFEST": "VERIFIED",
        "HASH_AUDIT_SELF_HASH": "SIDE_CAR_VERIFIED"
    },
    "unauthorized_numerical_inferences": 0,
    "code_modifications_made": False,
    "simulations_executed": False
}

with open(os.path.join(base_dir, "POLARIS_EMS_OBJECTIVE_SPECIFICATION.json"), "w") as f:
    json.dump(json_spec, f, indent=2)
print("Updated POLARIS_EMS_OBJECTIVE_SPECIFICATION.json")

# 3. POLARIS_EMS_VARIABLE_REGISTER.csv
var_rows = [
    ["VARIABLE_NAME", "VARIABLE_TYPE", "DOMAIN", "UNITS", "DESCRIPTION", "HIERARCHY_STAGE", "GOVERNANCE_STATUS"],
    ["P_solar_used(t)", "Decision Variable", "Continuous [0, P_solar_cons(t)]", "W", "Solar generation power dispatched to AC busbar", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["P_wind_used(t)", "Decision Variable", "Continuous [0, P_wind_cons(t)]", "W", "Wind generation power dispatched to AC busbar", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["P_curt_solar(t)", "Decision Variable", "Continuous [0, P_solar_cons(t)]", "W", "Curtailed solar power", "Stage 4", "FULLY_SPECIFIED"],
    ["P_curt_wind(t)", "Decision Variable", "Continuous [0, P_wind_cons(t)]", "W", "Curtailed wind power", "Stage 4", "FULLY_SPECIFIED"],
    ["P_curt_necessary(t)", "Decision Variable", "Continuous [0, P_curt(t)]", "W", "Necessary curtailment for battery/diesel physical protection", "Stage 0", "CONCEPTUAL_DECOMPOSITION_ONLY"],
    ["P_curt_avoidable(t)", "Decision Variable", "Continuous [0, P_curt(t)]", "W", "Avoidable curtailment from inefficient dispatch", "Stage 4", "CONCEPTUAL_DECOMPOSITION_ONLY"],
    ["P_bat_chg(t)", "Decision Variable", "Continuous [0, P_chg_max]", "W", "Battery charging power from AC busbar", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["P_bat_dis(t)", "Decision Variable", "Continuous [0, P_dis_max]", "W", "Battery discharging power to AC busbar", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["u_chg(t)", "Decision Variable", "Binary {0, 1}", "dimensionless", "Battery charging state flag", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["u_dis(t)", "Decision Variable", "Binary {0, 1}", "dimensionless", "Battery discharging state flag", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["SOC(t)", "State Variable", "Continuous [SOC_min_tech, SOC_max]", "dimensionless", "Battery state of charge at timestep t", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["E_bat(t)", "State Variable", "Continuous [E_min_tech, E_max]", "Wh", "Stored battery energy at timestep t", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["P_diesel(t)", "Decision Variable", "Continuous [0, P_diesel_max]", "W", "Diesel generator electrical power output", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["u_diesel(t)", "Decision Variable", "Binary {0, 1}", "dimensionless", "Diesel generator running commitment flag", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["v_start(t)", "Decision Variable", "Binary {0, 1}", "dimensionless", "Diesel generator startup event flag", "Stage 0 - 4", "FULLY_SPECIFIED"],
    ["Fuel_liter(t)", "Dependent Variable", "Continuous [0, inf)", "liters", "Fuel volume consumed by diesel generator at timestep t", "Stage 3", "FULLY_SPECIFIED"],
    ["F_rem(t)", "State Variable", "Continuous [0, F_capacity]", "liters", "Remaining station diesel fuel inventory", "Stage 0 - 3", "PHYSICAL_CONSTRAINT"],
    ["P_served_C(t)", "Decision Variable", "Continuous [0, P_demand_C]", "W", "Served Critical load power (Tier 1)", "Stage 1", "FULLY_SPECIFIED"],
    ["P_unmet_C(t)", "Decision Variable", "Continuous [0, P_demand_C]", "W", "Unmet Critical load power (SLA: 0 in normal ops)", "Stage 1", "FULLY_SPECIFIED"],
    ["P_served_E(t)", "Decision Variable", "Continuous [0, P_demand_E]", "W", "Served Essential load power (Tier 2)", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_unmet_E(t)", "Decision Variable", "Continuous [0, P_demand_E]", "W", "Unmet Essential load power", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_shed_E(t)", "Decision Variable", "Continuous [0, P_demand_E]", "W", "Shed Essential load power", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_served_D(t)", "Decision Variable", "Continuous [0, P_demand_D]", "W", "Served Deferrable task load power (Tier 3)", "Stage 1 - 3", "POLICY_RESOLVED"],
    ["P_unmet_D(t)", "Decision Variable", "Continuous [0, P_demand_D]", "W", "Unmet Deferrable load power", "Stage 1 - 3", "POLICY_RESOLVED"],
    ["P_shed_D(t)", "Decision Variable", "Continuous [0, P_demand_D]", "W", "Shed/Deferred load power", "Stage 1 - 3", "POLICY_RESOLVED"],
    ["P_served_I(t)", "Decision Variable", "Continuous [0, P_demand_I]", "W", "Served Interruptible load power (Tier 4)", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_unmet_I(t)", "Decision Variable", "Continuous [0, P_demand_I]", "W", "Unmet Interruptible load power", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_shed_I(t)", "Decision Variable", "Continuous [0, P_demand_I]", "W", "Shed Interruptible load power", "Stage 1 - 2", "FULLY_SPECIFIED"],
    ["P_served_N(t)", "Decision Variable", "Continuous [0, P_demand_N]", "W", "Served Noncritical load power (Tier 5)", "Stage 1 - 2", "POLICY_RESOLVED"],
    ["P_unmet_N(t)", "Decision Variable", "Continuous [0, P_demand_N]", "W", "Unmet Noncritical load power", "Stage 1 - 2", "POLICY_RESOLVED"],
    ["P_shed_N(t)", "Decision Variable", "Continuous [0, P_demand_N]", "W", "Shed Noncritical load power", "Stage 1 - 2", "POLICY_RESOLVED"],
    ["SOC_EBR_target(t)", "Parameter Interface", "Continuous [SOC_EBR_floor, 1.0]", "dimensionless", "Dynamic Emergency Battery Reserve target", "Stage 2", "PARTIALLY_SPECIFIED"],
    ["SOC_terminal_target(H)", "Parameter Interface", "Continuous [SOC_terminal_floor, 1.0]", "dimensionless", "Dynamic terminal SOC target at horizon end", "Stage 2", "PARTIALLY_SPECIFIED"]
]

with open(os.path.join(base_dir, "POLARIS_EMS_VARIABLE_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(var_rows)
print("Updated POLARIS_EMS_VARIABLE_REGISTER.csv")

