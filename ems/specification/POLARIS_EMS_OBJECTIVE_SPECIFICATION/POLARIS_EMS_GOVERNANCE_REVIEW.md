# POLARIS EMS OBJECTIVE SPECIFICATION & REQUIREMENTS GOVERNANCE REVIEW

**Governance Status**: READ_ONLY_GOVERNANCE_REVIEW_COMPLETE  
**Audit Timestamp**: 2026-09-21T21:20:00Z  
**Authoritative Output Directory**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Frozen Implementation SHA-256**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`  

---

## 1. Executive Summary

This governance review converts the qualitative energy management goals of the POLARIS project into an explicit, reviewable **DRAFT EMS Objective Specification** (`POLARIS_EMS_OBJECTIVE_SPECIFICATION.md`) while preserving the frozen implementation of the POLARIS EMS and all prior campaign evidence.

This audit was conducted strictly **READ-ONLY**. No code, solver parameters, objective weights, physical constraints, model weights, or simulation trajectories were modified, tuned, rerun, or re-executed.

### Core Review Findings
1. **Explicit vs. Qualitative Separation**: Project documentation explicitly governs system operational requirements such as 100% offline local execution, receding-horizon MPC architecture, and equipment physical operating bounds (e.g., 20%–95% SOC). However, core operational targets—such as maximum allowable unmet load, annual fuel consumption ceilings, and renewable utilization fractions—remain documented **qualitatively only**.
2. **Current Objective Semantics & Implementation Ratio**: The frozen `LocalMILPEnergyOptimizer` implements a weighted economic cost objective where unmet load is penalized at $\$10,000/\text{kWh}$ ($\$10/\text{Wh}$) compared to a marginal diesel fuel cost of $\$0.625/\text{kWh}$ ($0.00025\text{ L/Wh} \times \$2.50/\text{L}$). This establishes an implicit implementation ratio of **16,000 : 1**.
3. **Implementation Fact vs. Governed Policy**: The 16,000:1 ratio is an **IMPLEMENTATION FACT** (classified as a `PROTOTYPE_ASSUMPTION`), NOT an authorized POLARIS project policy. The project currently lacks a governed fuel-vs-reliability exchange rate.
4. **V2 Operational Evidence Lock**: V2 campaign evidence (173 trajectories, 4,152 H1 steps) remains `FROZEN_VALID`. Under treatment (Branch01 lower solar forecast), the optimizer dispatches diesel to reduce unmet load by $30,543.8\text{ kWh}$ while consuming $+11,350.2\text{ L}$ of fuel. Observed dispatch is consistent with the frozen MILP objective given treatment inputs. V2 does NOT establish what the correct POLARIS policy should be.
5. **Governance Gap & Decision Register**: A Stakeholder Decision Register (`POLARIS_EMS_OBJECTIVE_DECISION_REGISTER.md`) containing 15 explicit decision questions has been drafted. All numerical targets in the draft specification are set to `VALUE = NOT_SPECIFIED` with `AUTHORIZATION_REQUIRED = TRUE`.
6. **Authorization Boundary**: Objective modification remains `NOT_AUTHORIZED`. The next step is human/stakeholder review of the drafted specification.

---

## 2. Discovered Requirements Audit

Requirements discovered across project documentation (`POLARIS_MASTER_HANDOFF.md`, `POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md`, `system/config/*.yaml`) were evaluated across 24 core operational domains:

| Domain | Requirement Description | Classification | Doc Status | Current Implementation State |
| :--- | :--- | :--- | :--- | :--- |
| **1. Critical-Load Reliability** | Continuous load service | `HARD_CONSTRAINT` | `QUALITATIVE_ONLY` | Penalized at $\$10,000/\text{kWh}$ in solver |
| **2. Max Unmet Load** | Numerical cap on unserved load | `OPERATIONAL_LIMIT` | `NOT_SPECIFIED` | Uncapped soft penalty in objective |
| **3. Max Continuous Outage** | SLA for max interruption hours | `RELIABILITY_REQUIREMENT` | `NOT_SPECIFIED` | Unconstrained in 24h horizon |
| **4. Critical-Load Service** | Life-support & station load | `PRIMARY_OBJECTIVE` | `QUALITATIVE_ONLY` | 30 kW continuous baseline (`PROTOTYPE_ASSUMPTION`) |
| **5. Load Priority Classes** | Hierarchical load categorization | `SOFT_CONSTRAINT` | `QUALITATIVE_ONLY` | Deferrable/curtailable in config |
| **6. Load-Shedding Order** | Order of load shedding | `SOFT_CONSTRAINT` | `QUALITATIVE_ONLY` | Flexible loads shed before critical |
| **7. Diesel Fuel Minimization** | Reduce fuel consumption | `PRIMARY_OBJECTIVE` | `QUALITATIVE_ONLY` | $\$0.625/\text{kWh}$ marginal + $\$12.50/\text{h}$ base cost |
| **8. Diesel Runtime** | Limit continuous/total runtime | `OPERATIONAL_LIMIT` | `QUANTITATIVE_ONLY` | Min 2h up-time in config (`PROTOTYPE_ASSUMPTION`) |
| **9. Diesel Startup Frequency** | Cap generator start cycles | `OPERATIONAL_LIMIT` | `QUANTITATIVE_ONLY` | $\$15/\text{start}$ penalty in objective |
| **10. Operating Cost** | Minimize overall microgrid cost | `SECONDARY_OBJECTIVE` | `QUALITATIVE_ONLY` | Linear cost sum in objective function |
| **11. Renewable Utilization** | Maximize solar/wind usage | `SECONDARY_OBJECTIVE` | `QUALITATIVE_ONLY` | Curtailment penalized at $\$1/\text{kWh}$ |
| **12. Renewable Fraction** | Target % renewable energy | `ASPIRATIONAL_GOAL` | `NOT_SPECIFIED` | Evaluated post-hoc in metrics |
| **13. Renewable Curtailment** | Limit wasted renewable power | `SOFT_CONSTRAINT` | `QUANTITATIVE_ONLY` | $\$1/\text{kWh}$ penalty in objective |
| **14. Battery SOC** | Physical SOC operating bounds | `HARD_CONSTRAINT` | `EXPLICITLY_GOVERNED` | $20\% \le \text{SOC} \le 95\%$ hard bounds in solver |
| **15. Battery Reserve** | Dynamic emergency reserve floor | `SAFETY_REQUIREMENT` | `NOT_SPECIFIED` | No dynamic floor above technical 20% SOC |
| **16. Terminal SOC** | 24h horizon end SOC target | `HARD_CONSTRAINT` | `NOT_SPECIFIED` | Unconstrained ($E_{24} \ge E_{\min}$) |
| **17. Battery Degradation** | Cycle life degradation cost | `SOFT_CONSTRAINT` | `QUANTITATIVE_ONLY` | $\$0.05/\text{kWh}$ throughput penalty |
| **18. Generator Min Output** | Min loading to prevent fouling | `HARD_CONSTRAINT` | `QUANTITATIVE_ONLY` | $10\text{ kW}$ min power bound when active |
| **19. Generator Max Output** | Generator continuous rating | `HARD_CONSTRAINT` | `EXPLICITLY_GOVERNED` | $100\text{ kW}$ max power rating bound |
| **20. Emergency Operation** | Fail-safe emergency mode | `SAFETY_REQUIREMENT` | `QUALITATIVE_ONLY` | Zero-dispatch degraded plan on solver infeasibility |
| **21. Forecast Uncertainty** | Reserve for forecast errors | `SAFETY_REQUIREMENT` | `NOT_SPECIFIED` | Deterministic point forecast optimization |
| **22. Long Deficit Strategy** | Multi-day renewable deficit | `OPERATIONAL_LIMIT` | `QUALITATIVE_ONLY` | Receding horizon MPC lookahead |
| **23. Energy Security** | 100% offline isolation | `SAFETY_REQUIREMENT` | `EXPLICITLY_GOVERNED` | Strict offline runtime environment |
| **24. Safety / Fail-Safe** | Failure containment protocol | `SAFETY_REQUIREMENT` | `QUALITATIVE_ONLY` | Fail-closed exception handling |

---

## 3. Current Frozen Objective Semantics

The frozen MILP objective function in `system/optimization/implementations/milp.py` (SHA `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`) minimizes total objective cost over a 24-hour horizon ($H=24$):

$$J = \sum_{t=0}^{23} \left[ c_{\text{curt}} \Delta t w_t (P_{\text{curt,sol},t} + P_{\text{curt,wind},t}) + c_{\text{deg}} \Delta t w_t (P_{\text{chg},t} + P_{\text{dis},t}) + c_{\text{marg}} \Delta t w_t P_{\text{diesel},t} + c_{\text{unmet}} \Delta t P_{\text{unmet},t} + c_{\text{base}} \Delta t w_t u_{\text{diesel},t} + c_{\text{start}} w_t v_{\text{start},t} \right]$$

### Exact Coefficient Values Verified in Code:
- **Renewable Curtailment Penalty ($c_{\text{curt}}$)**: $\$0.001/\text{Wh} = \$1.00/\text{kWh}$
- **BESS Degradation Penalty ($c_{\text{deg}}$)**: $\$0.00005/\text{Wh} = \$0.05/\text{kWh}$
- **Marginal Diesel Cost ($c_{\text{marg}}$)**: $\$2.50/\text{L} \times 0.00025\text{ L/Wh} = \$0.000625/\text{Wh} = \$0.625/\text{kWh}$
- **Unmet Load Penalty ($c_{\text{unmet}}$)**: $\$10.00/\text{Wh} = \$10,000.00/\text{kWh}$ (**Unweighted**, $\gamma^t = 1.0$)
- **Base Running Fuel Cost ($c_{\text{base}}$)**: $\$2.50/\text{L} \times 5.0\text{ L/h} = \$12.50/\text{h}$
- **Generator Startup Penalty ($c_{\text{start}}$)**: $\$15.00/\text{start}$

---

## 4. Current Implementation Assumptions

All numerical values in `system/config/*.yaml` are explicitly tagged with `status_label: "PROTOTYPE_ASSUMPTION"`.
- **`battery.yaml`**: Capacity (200 kWh), Min SOC (20%), Max SOC (95%), Charge/Discharge Efficiency (92%), Max Power (50 kW), Cycling Penalty ($\$0.05/\text{kWh}$).
- **`diesel.yaml`**: Min Power (10 kW), Max Power (100 kW), Base Fuel (5.0 L/h), Marginal Fuel (0.25 L/kWh), Fuel Cost ($\$2.50/\text{L}$), Startup Penalty ($\$15.00$).
- **`loads.yaml`**: Critical load baseline (30 kW), Unmet penalty ($\$10,000/\text{kWh}$).

> [!CAUTION]
> **GOVERNANCE RULE**: These prototype values were chosen for initial software integration testing. They MUST NOT be silently promoted into governed POLARIS project requirements without explicit stakeholder authorization.

---

## 5. Missing Requirements

The audit identified critical gaps where POLARIS documentation expresses qualitative intent but provides zero numerical specifications:
1. **Maximum Acceptable Unmet Critical Load (kWh)**
2. **Maximum Allowable Continuous Outage Duration (hours)**
3. **Annual Fuel Consumption Target or Ceiling (L)**
4. **Governed Fuel-vs-Reliability Exchange Rate Ratio**
5. **Minimum Emergency BESS Reserve Floor (kWh)**
6. **24-Hour Horizon Terminal SOC Constraint (%)**
7. **Minimum Renewable Utilization / Energy Fraction (%)**
8. **Forecast Uncertainty Margin / Stochastic Reserve Policy**

---

## 6. Fuel-vs-Reliability Governance Gap

### The 16,000 : 1 Ratio Analysis
In the current implementation:
$$\text{Penalty Ratio} = \frac{\text{Unmet Load Penalty}}{\text{Marginal Diesel Cost}} = \frac{\$10,000.00 / \text{kWh}}{\$0.625 / \text{kWh}} = 16,000 : 1$$

- **Correct Ratio Interpretation**: The unmet-load penalty is 16,000 times the marginal diesel-energy cost on a $\$/\text{kWh}$ basis. The realized fuel required to avoid a unit of unmet load depends on generator operating constraints, base fuel consumption, startup costs, battery state, renewable availability, curtailment, objective discounting, horizon dynamics, and overall feasibility.
- **Objective Coefficient Clarification**: The 16,000:1 value is therefore an objective-cost coefficient ratio, not a claim that the optimizer will literally burn a fixed quantity of diesel to avoid one kWh of unmet load.
- **Distinction of Three Core Quantities**:
  1. **A. Objective Coefficient Ratio**: $\frac{\$10,000/\text{kWh}}{\$0.625/\text{kWh}} = 16,000 : 1$ (Mathematical ratio of objective weights in `milp.py`).
  2. **B. Physical / Configured Diesel Conversion**: Marginal consumption $0.25\text{ L/kWh} \times \$2.50/\text{L} = \$0.625/\text{kWh}$ (Configured generator heat rate and fuel price in `diesel.yaml`).
  3. **C. Realized Dispatch Trade-off**: Actual fuel consumed per kWh of reduced unmet load. This is a trajectory-dependent operational outcome and cannot be derived from the 16,000:1 objective coefficient ratio alone.
- **Observed V2 Trajectory-Set Result Context**: In the V2 campaign, Treatment (Branch01) resulted in $+11,350.2\text{ L}$ of fuel and $-30,543.8\text{ kWh}$ of unmet load relative to Control. The **observed aggregate V2 fuel/unmet-load change ratio** ($\frac{11,350.2\text{ L}}{30,543.8\text{ kWh}} \approx 0.3716\text{ L/kWh}$) is a trajectory-dependent empirical outcome, NOT an objective coefficient or universal trade-off law.
- **Governance Classification**: This 16,000:1 ratio is an **IMPLEMENTATION FACT** (classified as a `PROTOTYPE_ASSUMPTION`), NOT an authorized POLARIS policy. `FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED`.

---

## 7. Objective Formulation Options (Descriptive Only)

Without ranking, selecting, or recommending any formulation, the following mathematical options are available for stakeholder consideration:

### Option A: Lexicographic / Reliability-First Optimization
- **Meaning**: Solves a sequence of optimization problems. Stage 1 minimizes unmet load to absolute feasibility ($P_{\text{unmet}}^*$). Stage 2 minimizes fuel consumption subject to $P_{\text{unmet}} \le P_{\text{unmet}}^*$.
- **Operational Implication**: Zero load shedding whenever physically possible, regardless of fuel cost.

### Option B: Reliability-Constrained Fuel Minimization
- **Meaning**: Formulates load service as a hard constraint ($P_{\text{served}} = P_{\text{demand}}$) or bounded constraint ($\sum P_{\text{unmet}} \le \text{Cap}$), directly minimizing fuel volume $\sum \text{Fuel}_t$.
- **Operational Implication**: Ensures fuel is strictly minimized subject to an authorized reliability SLA.

### Option C: Weighted Economic Objective
- **Meaning**: Single objective function combining fuel cost, degradation, and unserved energy penalty weights ($c_{\text{unmet}}$).
- **Operational Implication**: Allows economic trade-offs between fuel cost and load service based on an explicit monetary valuation of reliability.

### Option D: Multi-Objective / Pareto Formulation
- **Meaning**: Computes the Pareto frontier of non-dominated solutions trading off Fuel (L) vs Unmet Load (kWh).
- **Operational Implication**: Provides operators and stakeholders with a explicit trade-off curve to choose operational modes dynamically.

---

## 8. Draft EMS Objective Specification Status

The DRAFT EMS Objective Specification has been created as an isolated artifact (`POLARIS_EMS_OBJECTIVE_SPECIFICATION.md`).

- **Specification Status**: `DRAFT_PENDING_AUTHORIZATION`
- **Numerical Values**: All missing thresholds are set to `VALUE = NOT_SPECIFIED` with `AUTHORIZATION_REQUIRED = TRUE`.
- **Code Changes**: `OBJECTIVE_MODIFICATION = NOT_AUTHORIZED`.

---

## 9. Stakeholder Decision Register

A dedicated Decision Register (`POLARIS_EMS_OBJECTIVE_DECISION_REGISTER.md`) has been generated containing 15 explicit decision questions for stakeholder resolution:
- **`DECISION_01`**: Max acceptable unmet load (kWh)?
- **`DECISION_02`**: Max continuous interruption duration (hours)?
- **`DECISION_03`**: Critical, flexible, and shed-able load definitions?
- **`DECISION_04`**: Hard constraint vs soft penalized objective for reliability?
- **`DECISION_05`**: Fuel consumption target or annual ceiling (L)?
- **`DECISION_06`**: Primary fuel objective definition (liters, runtime, cost)?
- **`DECISION_07`**: Authorized fuel-vs-reliability penalty exchange rate?
- **`DECISION_08`**: Required renewable utilization target (%)?
- **`DECISION_09`**: Maximum acceptable renewable curtailment (kWh)?
- **`DECISION_10`**: Minimum emergency battery reserve floor (kWh)?
- **`DECISION_11`**: Horizon terminal SOC requirement (%)?
- **`DECISION_12`**: Diesel runtime and startup frequency limits?
- **`DECISION_13`**: Governed load-shedding priority hierarchy?
- **`DECISION_14`**: Forecast uncertainty handling policy (stochastic/reserve)?
- **`DECISION_15`**: Governance approval authority designation?

---

## 10. Governance Change Boundary

The following table defines the change permission status for all project components:

| Component | Current Status | Change Allowed Now? | Required Authorization |
| :--- | :--- | :--- | :--- |
| **`milp.py` (LocalMILPEnergyOptimizer)** | FROZEN | `NO` | Explicit Stakeholder Approval of EMS Spec |
| **ForecastBundle Contract** | FROZEN | `NO` | Governance Architecture Board |
| **MILP Objective Weights / Coefficients** | FROZEN | `NO` | Stakeholder Decision on `DECISION_07` |
| **MILP Physical Constraints** | FROZEN | `NO` | Stakeholder Approval of Technical Specs |
| **DispatchPlan Schema** | FROZEN | `NO` | Governance Architecture Board |
| **DigitalTwinSimulator** | FROZEN | `NO` | Governance Architecture Board |
| **Battery Operating Limits** | FROZEN | `NO` | Equipment Specification Authorization |
| **Diesel Operating Limits** | FROZEN | `NO` | Equipment Specification Authorization |
| **V2 Campaign Evidence** | FROZEN_VALID | `NO` | Permanent Evidence Lock |

---

## 11. Artifact List and Cryptographic Hashes (SHA-256)

All artifacts in the governance package have been created inside `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`:

| Artifact File Name | Path | SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- |
| **`POLARIS_EMS_OBJECTIVE_SPECIFICATION.md`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` | `272e61c563e4811b7d5272a8488eefdd9b9e5fbcd4843b023ebc0ae4ce8bb6c8` | VERIFIED_NEW |
| **`POLARIS_EMS_OBJECTIVE_SPECIFICATION.json`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.json` | `01ddb16c873a4bbf781e05dd6417fae446ec863ebc03e87ae19fa76aed1ff787` | VERIFIED_NEW |
| **`POLARIS_EMS_REQUIREMENTS_MATRIX.csv`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_REQUIREMENTS_MATRIX.csv` | `7f223cd1cf6f9dbbc06ef366119cd75bbcfb8813bc3dd1ebcb239dfb32ca984c` | VERIFIED_NEW |
| **`POLARIS_EMS_OBJECTIVE_GAP_REGISTER.csv`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_GAP_REGISTER.csv` | `db3b58db07aeab39f7cf7cbb9f6cd9e5c464b5ae1aa22d56a23ef61f5c6e9d67` | VERIFIED_NEW |
| **`POLARIS_EMS_OBJECTIVE_DECISION_REGISTER.md`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_DECISION_REGISTER.md` | `155c8bb5cf9ab553a81ea42fcefaeebc82b130e5efedcd938c5db1df6ed387ee` | VERIFIED_NEW |
| **`POLARIS_EMS_OBJECTIVE_PROVENANCE.csv`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_PROVENANCE.csv` | `0d20d440adbb14f85e4ae5ca43b02005dbdbeff065ad71d18dc44f2c00edbc6d` | VERIFIED_NEW |
| **`POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv` | `07a68ea3f350c38bd48e470817ec74662dbe7fc2d08aeb5a2f58cfbcf76a2ed0` | VERIFIED_NEW |
| **`POLARIS_EMS_GOVERNANCE_REVIEW.md`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_GOVERNANCE_REVIEW.md` | `b4ef1d619989a3f2b434458b09ad8a34bb9910d54c4146a4829ad4148b5930ac` | VERIFIED_NEW |
| **`POLARIS_EMS_GOVERNANCE_REVIEW.json`** | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_GOVERNANCE_REVIEW.json` | `73bdfc919d854e4270f2ab870c5387d84877eeb0c968fdfb6e2d935f1ffb9a24` | VERIFIED_NEW |

---

## 12. Final Governance Status

```
V2_EVIDENCE_LOCK = PASS
EMS_OBJECTIVE_SOURCE_AUDIT = PASS
OBJECTIVE_NUMERIC_RECONCILIATION = PASS
REQUIREMENTS_RECONCILIATION = PARTIAL
OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED
CURRENT_OBJECTIVE_STATUS = FROZEN_IMPLEMENTATION
RELIABILITY_REQUIREMENT = QUALITATIVE_ONLY
FUEL_REQUIREMENT = QUALITATIVE_ONLY
RENEWABLE_REQUIREMENT = QUALITATIVE_ONLY
BATTERY_REQUIREMENT = PARTIALLY_GOVERNED
FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED
OBJECTIVE_PRIORITY = NOT_SPECIFIED
OBJECTIVE_FORMULATION_POLICY = NOT_SPECIFIED
FORECAST_UNCERTAINTY_POLICY = NOT_SPECIFIED
CRITICAL_LOAD_POLICY = QUALITATIVE_ONLY
NUMERICAL_REQUIREMENTS = REQUIRES_STAKEHOLDER_SPECIFICATION
STAKEHOLDER_DECISIONS_REQUIRED = 15
EMS_OBJECTIVE_SPECIFICATION = DRAFT_PENDING_AUTHORIZATION
OBJECTIVE_MODIFICATION = NOT_AUTHORIZED
EMS_MODIFICATION = NOT_AUTHORIZED
MODEL_MODIFICATION = NOT_AUTHORIZED
MODEL_RETRAINING = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET
NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED
NEXT_GOVERNED_STEP = HUMAN_REVIEW_OF_EXPLICIT_EMS_OBJECTIVE_SPECIFICATION
```

---

## 13. Exact Next Governed Step

NEXT_GOVERNED_STEP = HUMAN_REVIEW_OF_EXPLICIT_EMS_OBJECTIVE_SPECIFICATION
