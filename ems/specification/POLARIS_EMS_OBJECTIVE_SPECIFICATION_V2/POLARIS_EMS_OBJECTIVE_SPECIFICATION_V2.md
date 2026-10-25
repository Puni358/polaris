# POLARIS — GOVERNED EMS OBJECTIVE SPECIFICATION V2
**Phase**: Policy-to-Mathematical-Specification (Targeted Governance Correction)  
**Governance Document ID**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2`  
**Status**: `CONDITIONAL`  
**Stakeholder Policy Status**: `HUMAN_APPROVED`  
**Policy Definition Resolution**: `APPROVED_INPUT` (Version 1.1.0)  

---

## 1. Governance Status — Locked Execution State

```
STAKEHOLDER_POLICY_STATUS = HUMAN_APPROVED
POLICY_DEFINITION_RESOLUTION = APPROVED_INPUT

CURRENT_EMS_IMPLEMENTATION = FROZEN
MILP_IMPLEMENTATION = FROZEN

EMS_EXECUTION = NOT_AUTHORIZED
MPC_EXECUTION = NOT_AUTHORIZED
DIGITAL_TWIN_EXECUTION = NOT_AUTHORIZED

NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
OPTIMIZER_MODIFICATION = NOT_AUTHORIZED
OBJECTIVE_COEFFICIENT_MODIFICATION = NOT_AUTHORIZED

MODEL_MODIFICATION = NOT_AUTHORIZED
FORECASTING_MODIFICATION = NOT_AUTHORIZED
```

### Gap & Calibration Classifications Used
- `SPECIFICATION_CORRECTION_REQUIRED`: Applied to correct mathematical domain inconsistencies or previous non-conforming representations.
- `IMPLEMENTATION_MECHANISM_DEFERRED`: Applied when physical load/scheduling mechanisms are deferred to implementation architecture review without altering policy.
- `SHEDDING_ORDER_REQUIRES_GOVERNANCE_CLARIFICATION`: Applied when exact load shedding or restoration sequence between non-critical tiers requires explicit governance authorization.
- `REQUIRES_STAKEHOLDER_CLARIFICATION`: Applied when the policy itself is insufficient to specify a mathematical formulation.
- `REQUIRES_ENGINEERING_INPUT`: Applied when policy is clear but implementation requires station-specific engineering evidence.
- `NUMERICAL_CALIBRATION_REQUIRED`: Applied when mathematical structure is clear but a numerical parameter value must be calibrated from empirical evidence.

---

## 2. Authoritative Policy Input & Separation Firewall

This specification strictly translates the approved **POLARIS_EMS_POLICY_DEFINITION_RESOLUTION** (Version 1.1.0, SHA-256: `4a34d11f4bc28a81529c727af4fae52013e4b839b48878c460551b772a468dfe`) and the completed human stakeholder decision record **POLARIS_EMS_STAKEHOLDER_DECISION_SHEET** (SHA-256: `562834c2796a6ad8e90ba6d070f17da54e2c8479d688a29c72b0b885695d19e5`).

### Strict Separation Principles
$$ \text{CURRENT\_IMPLEMENTATION} \neq \text{HUMAN-APPROVED STAKEHOLDER POLICY} \neq \text{FUTURE GOVERNED EMS IMPLEMENTATION} $$

Current implementation facts are explicitly NOT policy:
1. **Unmet Load Penalty**: The current $10,000/kWh ($10.00/Wh) penalty in `optimizer.yaml` (`bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8`) is an engineering prototype fact, NOT a stakeholder policy value.
2. **Cost Ratio**: The current 16,000:1 unmet-load/marginal-diesel cost ratio ($10.00 / $0.000625) is an implementation fact, NOT a policy exchange rate.
3. **Empirical Fuel/Unmet Ratio**: The ~0.3716 L/kWh V2 aggregate fuel/unmet-load ratio is an empirical trajectory result, NOT a policy coefficient.
4. **Battery SOC Floor**: The current 20% battery SOC minimum (`min_soc_pct`) is a physical equipment boundary, NOT automatically the emergency battery reserve policy.
5. **Terminal SOC Behavior**: The current free terminal state ($E(H) \ge E_{\min}$) is prototype behavior, NOT the future terminal SOC policy.
6. **Renewable Curtailment**: The current soft penalty ($0.001/Wh) is an optimization proxy, NOT the full stakeholder renewable policy formulation.

---

## 3. Critical D15 Consistency Gate & Authority Verification

Before translating Decision 15 into mathematics, an independent verification of authoritative governance documents was performed:

- **Source 1**: `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md` (SHA-256: `562834c2796a6ad8e90ba6d070f17da54e2c8479d688a29c72b0b885695d19e5`)
  - Recorded Choice: **Option A** — Strict Lexicographic Priority Structure (1. Critical reliability $\to$ 2. Emergency battery reserve / resilience $\to$ 3. Fuel conservation $\to$ 4. Renewable utilization).
- **Source 2**: `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` (SHA-256: `4a34d11f4bc28a81529c727af4fae52013e4b839b48878c460551b772a468dfe`)
  - Recorded Choice: **Option A** — Strict 4-stage lexicographic priority order (Governing decisions: D06, D14, D15).

### Authority Verification Result
$$ \text{D15\_AUTHORITY\_CHECK} = \text{PASS} $$

There is zero discrepancy between authoritative sources. Decision 15 is unambiguously **Option A**.

---

## 4. Reconstructed Current EMS Model (Baseline Fact)

### A. Decision Variables
Per timestep $t \in \{0, \dots, H-1\}$ ($H=24$, $K=15$ variables per timestep, total $360$ variables):
1. $p_{\text{sol,used}}(t) \ge 0$: Solar power routed to load/battery (W)
2. $p_{\text{wind,used}}(t) \ge 0$: Wind power routed to load/battery (W)
3. $p_{\text{curt,sol}}(t) \ge 0$: Solar power curtailed (W)
4. $p_{\text{curt,wind}}(t) \ge 0$: Wind power curtailed (W)
5. $p_{\text{chg}}(t) \in [0, P_{\text{chg,max}}]$: Battery charging power (W)
6. $p_{\text{dis}}(t) \in [0, P_{\text{dis,max}}]$: Battery discharging power (W)
7. $E(t+1) \in [E_{\min}, E_{\max}]$: Battery stored energy state at end of timestep $t$ (Wh)
8. $p_{\text{diesel}}(t) \in [0, P_{\text{diesel,max}}]$: Diesel generator electrical output (W)
9. $p_{\text{served}}(t) \in [0, P_{\text{demand}}(t)]$: Total served load power (W)
10. $p_{\text{unmet}}(t) \in [0, P_{\text{demand}}(t)]$: Total unmet load power (W)
11. $p_{\text{flex}}(t) \in [0, P_{\text{flex,max}}]$: Deferrable flexible load power (W)
12. $u_{\text{chg}}(t) \in \{0, 1\}$: Binary indicator for battery charging
13. $u_{\text{dis}}(t) \in \{0, 1\}$: Binary indicator for battery discharging
14. $u_{\text{diesel}}(t) \in \{0, 1\}$: Binary indicator for diesel generator online status
15. $v_{\text{start}}(t) \in \{0, 1\}$: Binary indicator for diesel generator startup event

### B. State Variables & Forecast Inputs
- State: Battery energy $E(t)$ (Wh), Diesel online status $u_{\text{diesel}}(t-1)$
- Forecast Inputs: Point forecasts over horizon $H=24$: $P_{\text{solar,gen}}(t)$, $P_{\text{wind,gen}}(t)$, $P_{\text{demand}}(t)$ (W)

### C. Current Composite Objective Function
$$ J_{\text{current}} = \sum_{t=0}^{H-1} w_t \Big( c_{\text{curt}} (p_{\text{curt,sol}}(t) + p_{\text{curt,wind}}(t)) \Delta t + c_{\text{deg}} (p_{\text{chg}}(t) + p_{\text{dis}}(t)) \Delta t + c_{\text{fuel}} F_{\text{marg}} p_{\text{diesel}}(t) \Delta t + c_{\text{fuel}} F_{\text{base}} u_{\text{diesel}}(t) \Delta t + c_{\text{start}} v_{\text{start}}(t) \Big) + \sum_{t=0}^{H-1} c_{\text{unmet}} p_{\text{unmet}}(t) \Delta t $$

Where:
- $c_{\text{unmet}} = \$10.00/Wh$ (unweighted by discount factor $w_t$)
- $c_{\text{fuel}} = \$2.50/L$, $F_{\text{marg}} = 0.00025$ L/Wh, $F_{\text{base}} = 5.0$ L/h, $c_{\text{start}} = \$15.00$
- $c_{\text{deg}} = \$0.00005/Wh$, $c_{\text{curt}} = \$0.001/Wh$, $w_t = \gamma^t$ ($\,\gamma=1.0\,$)

---

## 5. Governed Five-Tier Load Classification

The policy explicitly preserves the approved 5-tier load structure:

1. **CRITICAL** (e.g., life support, primary control systems, SCADA, baseline freeze protection):
   - Service Requirement: Continuous 100% supply ($p_{\text{unmet,critical}}(t) = 0$).
   - Shedding: **PROHIBITED** under normal/degraded operation.
   - Deferral: **PROHIBITED**.
   - Restoration: N/A (uninterrupted).
2. **ESSENTIAL** (e.g., shelter heating, water processing, environmental controls):
   - Service Requirement: High availability; shedding allowed only under declared emergency.
   - Shedding: Permitted only in declared emergency.
   - Deferral: **PROHIBITED**.
   - Restoration / Precedence: `SHEDDING_ORDER_REQUIRES_GOVERNANCE_CLARIFICATION`.
3. **DEFERRABLE** (e.g., energy storage charging, water pumping, batch processing):
   - Service Requirement: Energy delivery volume within active window.
   - Deferral / Scheduling Window: `IMPLEMENTATION_MECHANISM_DEFERRED`.
   - Restoration / Precedence: `SHEDDING_ORDER_REQUIRES_GOVERNANCE_CLARIFICATION`.
4. **INTERRUPTIBLE** (e.g., secondary heating, ventilation, auxiliary pumps):
   - Service Requirement: Supplied when capacity permits; shed during capacity tightness.
   - Restoration / Precedence: `SHEDDING_ORDER_REQUIRES_GOVERNANCE_CLARIFICATION`.
5. **NONCRITICAL** (e.g., discretionary lighting, luxury loads, secondary scientific payloads):
   - Service Requirement: Lowest supply priority.
   - Restoration / Precedence: `SHEDDING_ORDER_REQUIRES_GOVERNANCE_CLARIFICATION`.

---

## 6. Governed Four-Stage Lexicographic Objective Hierarchy (Canonical Energy Domain)

Under Decision 15 (Option A), objectives are solved in strict sequential priority stages. All Stage 2 quantities are formulated consistently in the **ENERGY DOMAIN (Wh/kWh)**:

### Stage 1: Critical Reliability Boundary
$$ \min_{x} J_1 = \sum_{t=0}^{H-1} p_{\text{unmet,critical}}(t) \cdot \Delta t \quad \text{[Wh]} $$
Subject to physical equipment constraints.
Under normal governed operation: $J_1^* = 0$.

### Stage 2: Emergency Battery Reserve & Terminal Energy Shortfall Minimization (Canonical Energy Domain)
$$ \min_{x} J_2 = \sum_{t=0}^{H-1} \max\Big(0, E_{\text{EBR,target}}(t) - E_{\text{reserve,avail}}(t)\Big) + \max\Big(0, E_{\text{terminal,target}} - E(H)\Big) \quad \text{[Wh]} $$
Where:
- $E_{\text{EBR,target}}(t)$ is the energy-domain emergency battery reserve target at timestep $t$ [Wh].
- $E_{\text{reserve,avail}}(t) = E(t) - E_{\min}$ is the available reserve energy above technical minimum [Wh].
- $E_{\text{terminal,target}}$ is the required terminal stored energy target at horizon end $t=H$ [Wh].
- $E(H)$ is the actual battery stored energy state at horizon end $t=H$ [Wh].

Domain Conversion Equation:
$$ E(t) = C_{\text{bat}} \cdot \frac{\text{SOC}(t)}{100\%} $$

Subject to:
- Physical equipment constraints
- $J_1(x) \le J_1^* + \epsilon_1$ (where $\epsilon_1 = 0$)

### Stage 3: Fuel Conservation
$$ \min_{x} J_3 = \sum_{t=0}^{H-1} \Big( (F_{\text{base}} u_{\text{diesel}}(t) + F_{\text{marg}} p_{\text{diesel}}(t)) \Delta t + \text{Startup\_Fuel} \cdot v_{\text{start}}(t) \Big) \quad \text{[Liters]} $$
Subject to:
- Physical equipment constraints
- $J_1(x) \le J_1^* + \epsilon_1$
- $J_2(x) \le J_2^* + \epsilon_2$

### Stage 4: Renewable Utilization / Avoidable Curtailment Minimization
$$ \min_{x} J_4 = \sum_{t=0}^{H-1} p_{\text{curt,avoidable}}(t) \cdot \Delta t \quad \text{[Wh]} $$
Subject to:
- Physical equipment constraints
- $J_1(x) \le J_1^* + \epsilon_1$
- $J_2(x) \le J_2^* + \epsilon_2$
- $J_3(x) \le J_3^* + \epsilon_3$

Where $p_{\text{curt,avoidable}}(t) = p_{\text{curt,total}}(t) - p_{\text{curt,necessary}}(t)$.

---

## 7. Unit, Notation, and Dimensional Consistency Firewall

### Canonical Domain Selection & Reconciled Equations
State of Charge ($\,\text{SOC}(t) \in [0, 100]\%\,$) and Stored Energy ($\,E(t)\,\text{in Wh}\,\$) are explicitly reconciled via:
$$ E(t) = C_{\text{bat}} \cdot \frac{\text{SOC}(t)}{100\%} \quad \iff \quad \text{SOC}(t) = \frac{E(t)}{C_{\text{bat}}} \times 100\% $$

### Dimensional Audit Matrix
| Quantity / Term | Symbol | Units | Dimensional Formula | Audit Status |
|-----------------|--------|-------|---------------------|--------------|
| Power | $p(t)$ | Watt ($W$) | $[M L^2 T^-3]$ | PASS |
| Timestep | $\Delta t$ | Hour ($h$) | $[T]$ | PASS |
| Energy | $E(t)$ | Watt-hour ($Wh$) | $[M L^2 T^-2]$ | PASS |
| Fuel Consumption | $\text{Fuel}(t)$ | Liter ($L$) | $[L^3]$ | PASS |
| Marginal Fuel Rate | $F_{\text{marg}}$ | Liter per Watt-hour ($L/Wh$) | $[L^3 M^-1 L^-2 T^2]$ | PASS |
| Base Fuel Rate | $F_{\text{base}}$ | Liter per Hour ($L/h$) | $[L^3 T^-1]$ | PASS |
| Startup Fuel | $\text{Startup\_Fuel}$ | Liter ($L$) | $[L^3]$ | PASS |
| Stage 1 Objective | $J_1$ | Watt-hour ($Wh$) | $[M L^2 T^-2]$ | PASS |
| Stage 2 Objective | $J_2$ | Watt-hour ($Wh$) | $[M L^2 T^-2]$ | PASS (Canonical Energy Domain) |
| Stage 3 Objective | $J_3$ | Liter ($L$) | $[L^3]$ | PASS |
| Stage 4 Objective | $J_4$ | Watt-hour ($Wh$) | $[M L^2 T^-2]$ | PASS |

$$ \text{UNIT\_DIMENSION\_CHECK} = \text{PASS} $$

---

## 8. Operating Modes & Infeasibility Response

### Governed Operating Modes
1. **Normal Operating Mode**: All supply systems healthy, SOC above reserve floor, low forecast uncertainty.
2. **Forecast-Degraded Mode**: Telemetry or NWP source failure; expanded uncertainty margins active.
3. **Fuel-Constrained Mode**: Fuel inventory below resupply safety buffer; Stage 3 fuel target tightened.
4. **Emergency Operating Mode**: Capacity deficit or SOC below reserve floor; emergency shedding permitted for non-critical tiers.

### Infeasibility Response Protocol
If Stage 1 ($p_{\text{unmet,critical}} = 0$) is detected as physically infeasible due to extreme capacity shortage:
- Operational State: `CRITICAL_RELIABILITY_INFEASIBLE = DETECTED`
- Governed Action:
  1. Infeasibility must be surfaced immediately.
  2. Governed fault must be logged.
  3. No silent objective trade-off or arbitrary critical shedding may be invented.
- Emergency / Fallback Operational Response: `REQUIRES_GOVERNANCE_CLARIFICATION`. (No unauthorized automated dispatch shutdown or unapproved dispatch action is assumed).

---

## 9. Current Implementation Gap Analysis Summary

1. **Objective Structure**: Composite scalar weighted sum $\to$ 4-Stage Lexicographic MILP (`NOT_SUPPORTED`).
2. **Unmet Load Penalty**: Soft $\$10,000/kWh$ penalty $\to$ Stage 1 Hard Constraint ($p_{\text{unmet,critical}}=0$) (`NOT_SUPPORTED`).
3. **Load Classification**: Single composite load $\to$ Governed 5-tier load classification (`NOT_SUPPORTED`).
4. **Diesel Metric**: Cost proxy ($\$2.50/L \times 0.00025$ L/Wh) $\to$ Stage 3 Actual Fuel Volume in Liters (`PARTIALLY_SUPPORTED`).
5. **Battery Reserve**: Technical $20\%$ floor $\to$ Stage 2 Dynamic EBR target-shortfall minimization (`NOT_SUPPORTED`).
6. **Terminal SOC**: Free terminal energy $E(H) \ge E_{\min}$ $\to$ Stage 2 Dynamic Terminal Energy Target constraint (`NOT_SUPPORTED`).
7. **Renewable Curtailment**: Soft $\$0.001/Wh$ penalty $\to$ Stage 4 Avoidable Curtailment Minimization (`PARTIALLY_SUPPORTED`).
8. **Forecast Uncertainty**: Deterministic point forecast $\to$ Deterministic safety margins + MPC correction (`NOT_SUPPORTED`).
9. **Operating Modes**: Single static regime $\to$ 4 Governed Operating Modes (`NOT_SUPPORTED`).
10. **Infeasibility Protocol**: Soft penalty fallback $\to$ Governed Infeasibility Detection & Fault Logging (`NOT_SUPPORTED`).
11. **Thermal Generator Limits**: Min-up/min-down time constraints missing $\to$ Generator thermal cycle constraints (`NOT_SUPPORTED`).

---

## 10. Acceptance Criteria & Final Governance Summary

$$ \text{EMS\_OBJECTIVE\_SPECIFICATION} = \text{CONDITIONAL} $$

### Status Justification
The mathematical objective hierarchy, equations, units, gap analysis, and traceability matrix are fully defined and verified against Decision 15. However, implementation requires explicitly registered station-specific engineering inputs (generator fuel curves, station load circuit mappings, dynamic EBR calibration).

### Final Declarations
- `STAKEHOLDER_POLICY_INPUT`: `HUMAN_APPROVED`
- `POLICY_REINTERPRETATION`: `NONE`
- `UNAUTHORIZED_POLICY_VALUES`: `0`
- `D15_AUTHORITY_CHECK`: `PASS`
- `UNIT_DIMENSION_CHECK`: `PASS`
- `OBJECTIVE_IMPLEMENTATION_MODIFIED`: `NO`
- `MILP_MODIFIED`: `NO`
- `EMS_EXECUTED`: `NO`
- `MPC_EXECUTED`: `NO`
- `DIGITAL_TWIN_EXECUTED`: `NO`
- `NEW_EMS_EXPERIMENT`: `NO`
- `MODEL_MODIFIED`: `NO`
- `STAGE8_1_MODIFIED`: `NO`
- `ENGINEERING_VALIDATION_REQUIREMENTS_IDENTIFIED`: `YES`
- `IMPLEMENTATION_GAPS_IDENTIFIED`: `YES`
- `INFEASIBILITY_POLICY_STATUS`: `CONDITIONAL`
- `NEXT_GOVERNED_STEP`: `OBJECTIVE_SPECIFICATION_GOVERNANCE_REVIEW`
