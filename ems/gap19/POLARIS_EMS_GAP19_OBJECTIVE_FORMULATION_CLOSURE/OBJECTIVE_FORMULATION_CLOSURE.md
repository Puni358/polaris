# POLARIS EMS — GAP19 OBJECTIVE DEFINITION & FORMULATION CLOSURE REPORT

**Phase**: GAP19 Objective Definition & Mathematical Formulation Closure  
**Audit Date**: 2026-09-22  
**Status**: COMPLETED (READ-ONLY GOVERNANCE & MATHEMATICAL REVIEW)  
**Output Package**: `POLARIS_EMS_GAP19_OBJECTIVE_FORMULATION_CLOSURE`  

---

## 1. Executive Summary & Purpose

This review completes the mathematical formulation closure for the POLARIS Predictive Energy Management System (EMS) objective hierarchy. 

The primary objective of this phase is **solver-agnostic formulation closure**: defining the exact mathematical optimization problem that **BOTH Option A (Sequential MILP via SciPy API)** and **Option B (Native HiGHS Lexicographic Multi-Objective)** must implement. 

No solver selection (Option A vs Option B) is made. No code, configuration, schema, or previous audit artifact has been modified. No solver execution or benchmark was performed.

---

## 2. Section 1 — Exact Current Objective (Implementation Fact)

The current implementation in `system/optimization/implementations/milp.py` (`LocalMILPEnergyOptimizer`) formulates a **single scalar composite cost function** using Scipy `milp()` over a 24-hour horizon ($H=24$, $K=15$ variables per timestep, $360$ total decision variables):

$$ J_{\text{current}} = \sum_{t=0}^{H-1} w_t \Big( c_{\text{curt}} (p_{\text{curt,sol}}(t) + p_{\text{curt,wind}}(t)) \Delta t + c_{\text{deg}} (p_{\text{chg}}(t) + p_{\text{dis}}(t)) \Delta t + c_{\text{fuel}} F_{\text{marg}} p_{\text{diesel}}(t) \Delta t + c_{\text{fuel}} F_{\text{base}} u_{\text{diesel}}(t) \Delta t + c_{\text{start}} v_{\text{start}}(t) \Big) + \sum_{t=0}^{H-1} c_{\text{unmet}} p_{\text{unmet}}(t) \Delta t $$

### Current Coefficient & Weight Summary
- **Unmet Load Penalty**: $c_{\text{unmet}} = \$10.00/\text{Wh}$ ($\$10,000/\text{kWh}$), explicitly **unweighted** ($w_t = 1.0$).
- **Marginal Fuel Cost**: $c_{\text{fuel}} \cdot F_{\text{marg}} = \$2.50/\text{L} \times 0.00025\text{ L/Wh} = \$0.000625/\text{Wh}$.
- **Base Fuel Cost**: $c_{\text{fuel}} \cdot F_{\text{base}} = \$2.50/\text{L} \times 5.0\text{ L/h} = \$12.50/\text{h}$.
- **Generator Startup Cost**: $c_{\text{start}} = \$15.00$ per startup event.
- **Battery Degradation Penalty**: $c_{\text{deg}} = \$0.00005/\text{Wh}$ on charge ($p_{\text{chg}}$) and discharge ($p_{\text{dis}}$).
- **Renewable Curtailment Penalty**: $c_{\text{curt}} = \$0.001/\text{Wh}$ on solar ($p_{\text{curt,sol}}$) and wind ($p_{\text{curt,wind}}$) curtailment.
- **Temporal Discounting**: $w_t = \gamma^t$ (default $\gamma=1.0$).

---

## 3. Section 2 — Exact Governed Target Objective

The approved stakeholder policy (`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION` v1.1.0, Decision 15) establishes a **strict 4-stage lexicographic objective hierarchy**:

$$\text{Stage 1 (Critical Reliability)} \succ \text{Stage 2 (EBR \& Terminal Reserve)} \succ \text{Stage 3 (Fuel Conservation)} \succ \text{Stage 4 (Renewable Utilization)}$$

### Canonical Mathematical Expressions
- **Stage 1**: $\min J_1 = \sum_{t=0}^{H-1} p_{\text{unmet,critical}}(t) \cdot \Delta t \quad \text{[Wh]}$ (Target: $J_1^* = 0\text{ Wh}$).
- **Stage 2**: $\min J_2 = \sum_{t=0}^{H-1} \max\Big(0, E_{\text{EBR,target}}(t) - E_{\text{reserve,avail}}(t)\Big) + \max\Big(0, E_{\text{terminal,target}} - E(H)\Big) \quad \text{[Wh]}$.
- **Stage 3**: $\min J_3 = \sum_{t=0}^{H-1} \Big( (F_{\text{base}} u_{\text{diesel}}(t) + F_{\text{marg}} p_{\text{diesel}}(t)) \Delta t + F_{\text{start}} v_{\text{start}}(t) \Big) \quad \text{[Liters]}$.
- **Stage 4**: $\min J_4 = \sum_{t=0}^{H-1} (p_{\text{curt,sol}}(t) + p_{\text{curt,wind}}(t)) \cdot \Delta t \quad \text{[Wh]}$.

---

## 4. Section 3 — Structural Differences Between Current and Target

| Feature / Dimension | Current Implementation Fact | Governed Target Specification |
| :--- | :--- | :--- |
| **Objective Structure** | Single scalar cost function ($J_{\text{current}}$) | Strict 4-Stage Lexicographic Priority Hierarchy |
| **Critical Reliability** | Soft penalty ($10,000/kWh) on aggregate load | Hard boundary Stage 1 ($p_{\text{unmet,critical}} = 0$) |
| **Load Classification** | Single aggregate `demand` vector | 5-Tier load classification (Critical, Essential, etc.) |
| **Battery Reserve / EBR** | Implicit 20% technical floor (`min_soc_pct`) | Stage 2 dynamic EBR shortfall minimization |
| **Terminal SOC** | Free terminal state ($E(H) \ge E_{\min}$) | Stage 2 dynamic terminal energy target constraint |
| **Fuel Metric** | Dollar cost proxy ($\$2.50/\text{L} \times \text{consumption}$) | Stage 3 actual physical fuel volume in Liters ($L$) |
| **Curtailment Metric** | Soft penalty ($\$0.001/\text{Wh}$) | Stage 4 avoidable curtailment minimization ($Wh$) |
| **Battery Degradation** | Embedded as $\$0.00005/\text{Wh}$ in scalar objective | Unassigned in policy (`GOVERNANCE_BLOCKER`) |

---

## 5. Section 4 — Stage 1: Critical Reliability Formulation

- **Mathematical Target**: $\min J_1 = \sum_{t=0}^{H-1} p_{\text{unmet,critical}}(t) \Delta t$ [Wh], with $J_1^* = 0\text{ Wh}$.
- **Hard Constraint Equivalent**: $p_{\text{unmet,critical}}(t) = 0, \quad \forall t \in \{0, \dots, H-1\}$.
- **Infeasibility Response**: If $J_1^* > 0$, the system must log a `CRITICAL_RELIABILITY_INFEASIBLE` fault. No silent shedding or trade-off against fuel/curtailment is permitted.
- **Schema Impact**: `ForecastBundle` and `StationState` schemas currently lack tier breakdown for demand. Supplying $P_{\text{demand,critical}}(t)$ requires an additive schema enhancement (`ENGINEERING_DEFINITION_REQUIRED`).

---

## 6. Section 5 — Stage 2: EBR / Terminal Reserve Formulation

- **Governed Expression**:
  $$ \min_{x} J_2 = \sum_{t=0}^{H-1} \max\Big(0, E_{\text{EBR,target}}(t) - E_{\text{reserve,avail}}(t)\Big) + \max\Big(0, E_{\text{terminal,target}} - E(H)\Big) \quad \text{[Wh]} $$
  where $E_{\text{reserve,avail}}(t) = E(t) - E_{\min}$.
- **MILP Linearization**: Formulated using non-negative slack variables $s_{\text{EBR}}(t) \ge 0$ and $s_{\text{term}} \ge 0$:
  $$ s_{\text{EBR}}(t) \ge E_{\text{EBR,target}}(t) - (E(t) - E_{\min}), \quad s_{\text{term}} \ge E_{\text{terminal,target}} - E(H), \quad \min \sum_{t=0}^{H-1} s_{\text{EBR}}(t) + s_{\text{term}} $$
- **Coupling & Ambiguity**: At $t=H$, $E_{\text{reserve,avail}}(H) = E(H) - E_{\min}$. Terminal reserve and $t=H$ EBR are mathematically coupled through $E(H)$. If $E_{\text{terminal,target}}$ incorporates the EBR buffer, explicit deduplication is required.
- **Unresolved Parameters**: $E_{\text{EBR,target}}(t)$ and $E_{\text{terminal,target}}$ are symbolic; numerical values are not authorized in policy (`GOVERNANCE_DECISION_REQUIRED`).

---

## 7. Section 6 — Battery Degradation Status

- **Current Implementation**: Appears in `milp.py` as $c_{\text{deg}} (p_{\text{chg}}(t) + p_{\text{dis}}(t)) \Delta t w_t$ ($c_{\text{deg}} = \$0.00005/\text{Wh}$).
- **Governance Audit**: Neither `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION` nor `POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2` assigns degradation to Stage 1, Stage 2, Stage 3, or Stage 4.
- **Classification**: `BATTERY_DEGRADATION_STAGE = GOVERNANCE_BLOCKER`.
- **A/B Equivalence Impact**: Degradation placement does not break A/B equivalence as long as the assignment (e.g. Stage 3 operating cost vs Stage 4 system loss) is identical in both implementations.

---

## 8. Section 7 — Temporal Weighting Status (OI-6 Resolution)

- **Current Fact**: `milp.py` applies $w_t = \gamma^t$ ($\gamma=1.0$ default), with custom vector options. $p_{\text{unmet}}$ is explicitly unweighted ($w_t = 1.0$).
- **Governed Requirement**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2` specifies uniform timestep weighting ($w_t = 1.0, \forall t$).
- **Resolution**: Governed target is strict physical sum over horizon ($w_t = 1.0$). Receding-horizon discounting is not authorized by policy (`RESOLVED_BY_EXISTING_GOVERNANCE`).

---

## 9. Section 8 — Lexicographic Tolerance Requirements (OI-3 Resolution)

- **Objective Locking Rule**: After Stage $k$, constraint $J_k(x) \le J_k^* + \epsilon_k$ is added.
- **Physical Units**:
  - Stage 1: $\epsilon_1 = 0.0\text{ Wh}$ (exact zero critical unmet energy).
  - Stage 2: $\epsilon_2$ in $\text{Wh}$ (reserve shortfall tolerance).
  - Stage 3: $\epsilon_3$ in $\text{Liters}$ (fuel consumption tolerance, e.g. $0.001\text{ L}$).
  - Stage 4: $\epsilon_4$ (lowest stage; no locking constraint required).
- **Semantics Mapping**: Option A uses explicit RHS constraint updates ($c_k^T x \le z_k^* + \epsilon_k$). Option B passes $\epsilon_k$ to `HighsLinearObjective.abs_tolerance`.
- **A/B Equivalence Definition**: Option A and Option B are defined as operationally equivalent if active decision variables $x^*$ match within $\max(\epsilon_k, \eta)$ where $\eta=10^{-5}$ is solver tolerance.

---

## 10. Section 9 — Stage 3: Fuel Formulation

- **Governed Formulation**:
  $$ \min_{x} J_3 = \sum_{t=0}^{H-1} \left( (F_{\text{base}} u_{\text{diesel}}(t) + F_{\text{marg}} p_{\text{diesel}}(t)) \Delta t + F_{\text{start}} v_{\text{start}}(t) \right) \quad \text{[Liters]} $$
  where $F_{\text{base}} = 5.0\text{ L/h}$, $F_{\text{marg}} = 0.00025\text{ L/Wh}$, $F_{\text{start}} = 6.0\text{ Liters}$ ($\text{startup\_cost} / \text{fuel\_cost\_per\_l} = 15/2.50 = 6.0\text{ L}$).
- **Decomposition**:
  - Fuel Volume: Objective term $J_3$ [Liters].
  - Runtime: Reporting metric $\sum u_{\text{diesel}}(t) \Delta t$ [Hours].
  - Tank Minimum / Emergency Fuel: Hard lower bound constraint [Liters].
  - Cost Conversion: Reporting metric ($\$2.50/\text{L} \times J_3$).

---

## 11. Section 10 — Stage 4: Renewable Utilization Formulation

- **Governed Formulation**:
  $$ \min_{x} J_4 = \sum_{t=0}^{H-1} (p_{\text{curt,sol}}(t) + p_{\text{curt,wind}}(t)) \cdot \Delta t \quad \text{[Wh]} $$
- **Decomposition**:
  - Avoidable Curtailment: Minimized in $J_4$.
  - Physically Necessary Curtailment: Permitted without penalty under bus balance limits.
  - Utilization Percentage: Reported post-processing metric ($\frac{\text{Renewable Used}}{\text{Renewable Gen}} \times 100\%$). No arbitrary percentage floor is imposed.

---

## 12. Section 11 — DispatchPlan Reporting Requirements (OI-7 Resolution)

To ensure full auditability per MPC cycle, the following additive fields are required for `DispatchPlan`:

1. `stage1_achieved_objective`: Achieved critical unmet energy (Wh).
2. `stage2_achieved_objective`: Achieved reserve/terminal shortfall (Wh).
3. `stage3_achieved_objective`: Achieved fuel consumption (Liters).
4. `stage4_achieved_objective`: Achieved renewable curtailment (Wh).
5. `stage_optimum_values`: Array $[J_1^*, J_2^*, J_3^*, J_4^*]$.
6. `lexicographic_tolerances_applied`: Array $[\epsilon_1, \epsilon_2, \epsilon_3, \epsilon_4]$.
7. `feasibility_status`: Operating regime status (`NORMAL`, `DEGRADED`, `INFEASIBLE`).
8. `fuel_consumption_liters`: Total fuel consumed over horizon ($L$).
9. `critical_served_energy_wh` / `critical_unmet_energy_wh`: Breakdown of critical energy (Wh).
10. `terminal_soc_pct`: Final battery SOC at $t=24$ (%).

---

## 13. Section 12 — Complete Governance Blocker Register

| Item ID | Item Description | Governed Classification |
| :--- | :--- | :--- |
| **OI-01** | Stage 2 EBR Target Value ($E_{\text{EBR,target}}$) | `GOVERNANCE_DECISION_REQUIRED` |
| **OI-02** | Stage 2 Terminal Reserve Target ($E_{\text{terminal,target}}$) | `GOVERNANCE_DECISION_REQUIRED` |
| **OI-03** | Lexicographic Tolerance Epsilon Values ($\epsilon_k$) | `ENGINEERING_DEFINITION_REQUIRED` |
| **OI-04** | Battery Degradation Stage Placement | `GOVERNANCE_DECISION_REQUIRED` |
| **OI-05** | 5-Tier Load Breakdown in Schemas | `ENGINEERING_DEFINITION_REQUIRED` |
| **OI-06** | Temporal Weighting Vector ($w_t = 1.0$) | `RESOLVED_BY_EXISTING_GOVERNANCE` |
| **OI-07** | DispatchPlan Multi-Stage Additive Fields | `ENGINEERING_DEFINITION_REQUIRED` |
| **OI-08** | Fuel Tank Minimum & Seasonal Budget Limits | `GOVERNANCE_DECISION_REQUIRED` |
| **OI-09** | Empirical A/B Equivalence Benchmark Execution | `ENGINEERING_DEFINITION_REQUIRED` |
| **OI-10** | Option B Access Architecture Path (`_core` vs `highspy`) | `ENGINEERING_DEFINITION_REQUIRED` |

---

## 14. Section 13 — A/B Implementation-Neutrality Result

The mathematical formulation established in this report is **100% implementation-neutral**.

- **Decision Variables**: Identical vector $x \in \mathbb{R}^{360}$ for both A and B.
- **Constraints**: Identical feasibility bounds $[lb, ub]$ and linear constraints $A x = b$.
- **Stage Cost Vectors**: Identical stage objective vectors $c_1, c_2, c_3, c_4$ for both A and B.
- **Priority Hierarchy**: Sequential solve loop in Option A matches HiGHS priority integers $(0, 1, 2, 3)$ in Option B 1-to-1.
- **Result**: Option A and Option B solve the **exact same mathematical optimization problem**.

---

## 15. Section 14 — Clear List of Human Decisions Still Required

Before authorizing solver implementation or selecting Option A vs Option B, human governance must make the following specific policy decisions:

1. **Authorize Numerical EBR Target ($E_{\text{EBR,target}}$)**: Specify required emergency battery reserveWh (or % of capacity).
2. **Authorize Numerical Terminal Target ($E_{\text{terminal,target}}$)**: Specify required end-of-horizon battery reserve Wh (or % of capacity).
3. **Assign Battery Degradation Stage**: Formally place battery degradation into Stage 3 (Operating Costs), Stage 4 (System Losses), or convert to a hard daily throughput constraint.
4. **Authorize Fuel Budget / Minimum Tank Reserve**: Specify whether a seasonal fuel budget constraint or minimum tank reserve is active.
5. **Select Solver Architecture (Option A vs Option B)**: Choose between sequential SciPy MILP passes (Option A) and native HiGHS multi-objective MILP (Option B) based on the evidence package.
