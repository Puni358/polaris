import os
import csv
import json
import hashlib

TARGET_DIR = "/home/punith-bs/01polaris (Copy)/ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2"
os.makedirs(TARGET_DIR, exist_ok=True)

OPT_YAML_HASH = "bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8"
MILP_PY_HASH = "ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35"
POLICY_RES_MD_HASH = "4a34d11f4bc28a81529c727af4fae52013e4b839b48878c460551b772a468dfe"
STAKEHOLDER_MD_HASH = "562834c2796a6ad8e90ba6d070f17da54e2c8479d688a29c72b0b885695d19e5"

# 1. POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.md
md_content = f"""# POLARIS — GOVERNED EMS OBJECTIVE SPECIFICATION V2
**Phase**: Policy-to-Mathematical-Specification  
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
- `REQUIRES_STAKEHOLDER_CLARIFICATION`: Applied when the policy itself is insufficient to specify a mathematical formulation.
- `REQUIRES_ENGINEERING_INPUT`: Applied when policy is clear but implementation requires station-specific engineering evidence.
- `NUMERICAL_CALIBRATION_REQUIRED`: Applied when the mathematical structure is clear but a numerical parameter value must be calibrated from empirical evidence.

---

## 2. Authoritative Policy Input & Separation Firewall

This specification strictly translates the approved **POLARIS_EMS_POLICY_DEFINITION_RESOLUTION** (Version 1.1.0, SHA-256: `{POLICY_RES_MD_HASH}`) and the completed human stakeholder decision record **POLARIS_EMS_STAKEHOLDER_DECISION_SHEET** (SHA-256: `{STAKEHOLDER_MD_HASH}`).

### Strict Separation Principles
$$ \\text{{CURRENT\\_IMPLEMENTATION}} \\neq \\text{{HUMAN-APPROVED STAKEHOLDER POLICY}} \\neq \\text{{FUTURE GOVERNED EMS IMPLEMENTATION}} $$

Current implementation facts are explicitly NOT policy:
1. **Unmet Load Penalty**: The current $10,000/kWh ($10.00/Wh) penalty in `optimizer.yaml` (`{OPT_YAML_HASH}`) is an engineering prototype fact, NOT a stakeholder policy value.
2. **Cost Ratio**: The current 16,000:1 unmet-load/marginal-diesel cost ratio ($10.00 / $0.000625) is an implementation fact, NOT a policy exchange rate.
3. **Empirical Fuel/Unmet Ratio**: The ~0.3716 L/kWh V2 aggregate fuel/unmet-load ratio is an empirical trajectory result, NOT a policy coefficient.
4. **Battery SOC Floor**: The current 20% battery SOC minimum (`min_soc_pct`) is a physical equipment boundary, NOT automatically the emergency battery reserve policy.
5. **Terminal SOC Behavior**: The current free terminal state ($E(H) \\ge E_{{\\min}}$) is prototype behavior, NOT the future terminal SOC policy.
6. **Renewable Curtailment**: The current soft penalty ($0.001/Wh) is an optimization proxy, NOT the full stakeholder renewable policy formulation.

---

## 3. Critical D15 Consistency Gate & Authority Verification

Before translating Decision 15 into mathematics, an independent verification of authoritative governance documents was performed:

- **Source 1**: `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md` (SHA-256: `{STAKEHOLDER_MD_HASH}`)
  - Recorded Choice: **Option A** — Strict Lexicographic Priority Structure (1. Critical reliability $\\to$ 2. Emergency battery reserve / resilience $\\to$ 3. Fuel conservation $\\to$ 4. Renewable utilization).
- **Source 2**: `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` (SHA-256: `{POLICY_RES_MD_HASH}`)
  - Recorded Choice: **Option A** — Strict 4-stage lexicographic priority order (Governing decisions: D06, D14, D15).

### Authority Verification Result
$$ \\text{{D15\\_AUTHORITY\\_CHECK}} = \\text{{PASS}} $$

There is zero discrepancy between authoritative sources. Decision 15 is unambiguously **Option A**.

---

## 4. Reconstructed Current EMS Model (Baseline Fact)

### A. Decision Variables
Per timestep $t \\in \\{{0, \\dots, H-1\\}}$ ($H=24$, $K=15$ variables per timestep, total $360$ variables):
1. $p_{{\\text{{sol,used}}}}(t) \\ge 0$: Solar power routed to load/battery (W)
2. $p_{{\\text{{wind,used}}}}(t) \\ge 0$: Wind power routed to load/battery (W)
3. $p_{{\\text{{curt,sol}}}}(t) \\ge 0$: Solar power curtailed (W)
4. $p_{{\\text{{curt,wind}}}}(t) \\ge 0$: Wind power curtailed (W)
5. $p_{{\\text{{chg}}}}(t) \\in [0, P_{{\\text{{chg,max}}}}]$: Battery charging power (W)
6. $p_{{\\text{{dis}}}}(t) \\in [0, P_{{\\text{{dis,max}}}}]$: Battery discharging power (W)
7. $E(t+1) \\in [E_{{\\min}}, E_{{\\max}}]$: Battery stored energy state at end of timestep $t$ (Wh)
8. $p_{{\\text{{diesel}}}}(t) \\in [0, P_{{\\text{{diesel,max}}}}]$: Diesel generator electrical output (W)
9. $p_{{\\text{{served}}}}(t) \\in [0, P_{{\\text{{demand}}}}(t)]$: Total served load power (W)
10. $p_{{\\text{{unmet}}}}(t) \\in [0, P_{{\\text{{demand}}}}(t)]$: Total unmet load power (W)
11. $p_{{\\text{{flex}}}}(t) \\in [0, P_{{\\text{{flex,max}}}}]$: Deferrable flexible load power (W)
12. $u_{{\\text{{chg}}}}(t) \\in \\{{0, 1\\}}$: Binary indicator for battery charging
13. $u_{{\\text{{dis}}}}(t) \\in \\{{0, 1\\}}$: Binary indicator for battery discharging
14. $u_{{\\text{{diesel}}}}(t) \\in \\{{0, 1\\}}$: Binary indicator for diesel generator online status
15. $v_{{\\text{{start}}}}(t) \\in \\{{0, 1\\}}$: Binary indicator for diesel generator startup event

### B. State Variables & Forecast Inputs
- State: Battery energy $E(t)$ (Wh), Diesel online status $u_{{\\text{{diesel}}}}(t-1)$
- Forecast Inputs: Point forecasts over horizon $H=24$: $P_{{\\text{{solar,gen}}}}(t)$, $P_{{\\text{{wind,gen}}}}(t)$, $P_{{\\text{{demand}}}}(t)$ (W)

### C. Current Composite Objective Function
$$ J_{{\\text{{current}}}} = \\sum_{{t=0}}^{{H-1}} w_t \\Big( c_{{\\text{{curt}}}} (p_{{\\text{{curt,sol}}}}(t) + p_{{\\text{{curt,wind}}}}(t)) \\Delta t + c_{{\\text{{deg}}}} (p_{{\\text{{chg}}}}(t) + p_{{\\text{{dis}}}}(t)) \\Delta t + c_{{\\text{{fuel}}}} F_{{\\text{{marg}}}} p_{{\\text{{diesel}}}}(t) \\Delta t + c_{{\\text{{fuel}}}} F_{{\\text{{base}}}} u_{{\\text{{diesel}}}}(t) \\Delta t + c_{{\\text{{start}}}} v_{{\\text{{start}}}}(t) \\Big) + \\sum_{{t=0}}^{{H-1}} c_{{\\text{{unmet}}}} p_{{\\text{{unmet}}}}(t) \\Delta t $$

Where:
- $c_{{\\text{{unmet}}}} = \\$10.00/Wh$ (unweighted by discount factor $w_t$)
- $c_{{\\text{{fuel}}}} = \\$2.50/L$, $F_{{\\text{{marg}}}} = 0.00025$ L/Wh, $F_{{\\text{{base}}}} = 5.0$ L/h, $c_{{\\text{{start}}}} = \\$15.00$
- $c_{{\\text{{deg}}}} = \\$0.00005/Wh$, $c_{{\\text{{curt}}}} = \\$0.001/Wh$, $w_t = \\gamma^t$ ($\\,\\gamma=1.0\\,$)

---

## 5. Governed Five-Tier Load Classification

The policy explicitly preserves the approved 5-tier load structure:

1. **CRITICAL** (e.g., life support, primary control systems, SCADA, baseline freeze protection):
   - Service Requirement: Continuous 100% supply ($p_{{\\text{{unmet,critical}}}}(t) = 0$).
   - Shedding: **PROHIBITED** under normal/degraded operation.
   - Deferral: **PROHIBITED**.
   - Restoration: N/A (uninterrupted).
2. **ESSENTIAL** (e.g., shelter heating, water processing, environmental controls):
   - Service Requirement: High availability; shedding allowed only under emergency capacity deficits after Noncritical/Interruptible/Deferrable shed.
   - Shedding: Permitted in declared emergency.
   - Deferral: **PROHIBITED**.
   - Restoration: Priority 1 restoration.
3. **DEFERRABLE** (e.g., energy storage charging, water pumping, batch processing):
   - Service Requirement: Total energy delivery volume $E_{{\\text{{flex,req}}}}$ within active window $[t_{{\\text{{start}}}}, t_{{\\text{{finish}}}}]$.
   - Shedding: Prohibited if window constraints allow completion.
   - Deferral: **PERMITTED** (time-shifting within window).
   - Restoration: Rescheduled within active horizon window.
4. **INTERRUPTIBLE** (e.g., secondary heating, ventilation, auxiliary pumps):
   - Service Requirement: Supplied when capacity permits; shed during supply tightness.
   - Shedding: **PERMITTED**.
   - Deferral: **PROHIBITED**.
   - Restoration: Automatic upon margin recovery.
5. **NONCRITICAL** (e.g., discretionary lighting, luxury loads, secondary scientific payloads):
   - Service Requirement: Lowest supply priority.
   - Shedding: **PERMITTED** (shed first).
   - Deferral: **PROHIBITED**.
   - Restoration: Restored only after full capacity recovery.

*Note*: Mapping physical station circuits to these tiers requires station-specific engineering validation (`REQUIRES_ENGINEERING_INPUT`).

---

## 6. Governed Four-Stage Lexicographic Objective Hierarchy

Under Decision 15 (Option A), objectives are solved in strict sequential priority stages:

### Stage 1: Critical Reliability Boundary
$$ \\min_{{x}} J_1 = \\sum_{{t=0}}^{{H-1}} p_{{\\text{{unmet,critical}}}}(t) \\cdot \\Delta t $$
Subject to physical equipment constraints.
Under normal governed operation: $J_1^* = 0$.

### Stage 2: Emergency Battery Reserve Target-Shortfall Minimization
$$ \\min_{{x}} J_2 = \\sum_{{t=0}}^{{H-1}} \\max\\Big(0, \\text{{EBR}}_{{\\text{{target}}}}(t) - E_{{\\text{{reserve,avail}}}}(t)\\Big) + \\max\\Big(0, \\text{{SOC}}_{{\\text{{terminal,target}}}} - \\text{{SOC}}(H)\\Big) \\cdot C_{{\\text{{bat}}}} $$
Subject to:
- Physical equipment constraints
- $J_1(x) \\le J_1^* + \\epsilon_1$ (where $\\epsilon_1 = 0$)

### Stage 3: Fuel Conservation
$$ \\min_{{x}} J_3 = \\sum_{{t=0}}^{{H-1}} \\Big( (F_{{\\text{{base}}}} u_{{\\text{{diesel}}}}(t) + F_{{\\text{{marg}}}} p_{{\\text{{diesel}}}}(t)) \\Delta t + \\text{{Startup\\_Fuel}} \\cdot v_{{\\text{{start}}}}(t) \\Big) \\quad \\text{{[Liters]}} $$
Subject to:
- Physical equipment constraints
- $J_1(x) \\le J_1^* + \\epsilon_1$
- $J_2(x) \\le J_2^* + \\epsilon_2$

### Stage 4: Renewable Utilization / Avoidable Curtailment Minimization
$$ \\min_{{x}} J_4 = \\sum_{{t=0}}^{{H-1}} p_{{\\text{{curt,avoidable}}}}(t) \\cdot \\Delta t $$
Subject to:
- Physical equipment constraints
- $J_1(x) \\le J_1^* + \\epsilon_1$
- $J_2(x) \\le J_2^* + \\epsilon_2$
- $J_3(x) \\le J_3^* + \\epsilon_3$

Where $p_{{\\text{{curt,avoidable}}}}(t) = p_{{\\text{{curt,total}}}}(t) - p_{{\\text{{curt,necessary}}}}(t)$.

---

## 7. Unit, Notation, and Dimensional Consistency Firewall

### Reconciliation of SOC vs Energy
State of Charge ($\\,\\text{{SOC}}(t) \\in [0, 100]\\%\\,$) and Stored Energy ($\\,E(t)\\,\\text{{in Wh}}\\,\\$) are explicitly reconciled via:
$$ E(t) = C_{{\\text{{bat}}}} \\cdot \\frac{{\\text{{SOC}}(t)}}{{100\\%}} \\quad \\iff \\quad \\text{{SOC}}(t) = \\frac{{E(t)}}{{C_{{\\text{{bat}}}}}} \\times 100\\% $$

### Dimensional Audit Matrix
| Quantity / Term | Symbol | Units | Dimensional Formula | Audit Status |
|-----------------|--------|-------|---------------------|--------------|
| Power | $p(t)$ | Watt ($W$) | $[M L^2 T^{-3}]$ | PASS |
| Timestep | $\\Delta t$ | Hour ($h$) | $[T]$ | PASS |
| Energy | $E(t)$ | Watt-hour ($Wh$) | $[M L^2 T^{-2}]$ | PASS |
| Fuel Consumption | $\\text{{Fuel}}(t)$ | Liter ($L$) | $[L^3]$ | PASS |
| Marginal Fuel Rate | $F_{{\\text{{marg}}}}$ | Liter per Watt-hour ($L/Wh$) | $[L^3 M^{-1} L^{-2} T^2]$ | PASS |
| Base Fuel Rate | $F_{{\\text{{base}}}}$ | Liter per Hour ($L/h$) | $[L^3 T^{-1}]$ | PASS |
| Startup Fuel | $\\text{{Startup\\_Fuel}}$ | Liter ($L$) | $[L^3]$ | PASS |
| Stage 1 Objective | $J_1$ | Watt-hour ($Wh$) | $[M L^2 T^{-2}]$ | PASS |
| Stage 2 Objective | $J_2$ | Watt-hour ($Wh$) | $[M L^2 T^{-2}]$ | PASS |
| Stage 3 Objective | $J_3$ | Liter ($L$) | $[L^3]$ | PASS |
| Stage 4 Objective | $J_4$ | Watt-hour ($Wh$) | $[M L^2 T^{-2}]$ | PASS |

$$ \\text{{UNIT\\_DIMENSION\\_CHECK}} = \\text{{PASS}} $$

---

## 8. Operating Modes & Infeasibility Governance

### Governed Operating Modes
1. **Normal Operating Mode**: All supply systems healthy, SOC above reserve floor, low forecast uncertainty.
2. **Forecast-Degraded Mode**: Telemetry or NWP source failure; expanded uncertainty margins active.
3. **Fuel-Constrained Mode**: Fuel inventory below resupply safety buffer; Stage 3 fuel target tightened.
4. **Emergency Operating Mode**: Capacity deficit or SOC below $\\text{{EBR}}_{{\\text{{target}}}}$; lexicographic fallback active, load shedding enabled for Essential/Interruptible/Noncritical tiers.

### Infeasibility Policy Status
$$ \\text{{INFEASIBILITY\\_POLICY\\_STATUS}} = \\text{{CONDITIONAL}} $$

If Stage 1 ($p_{{\\text{{unmet,critical}}}} = 0$) becomes physically infeasible due to extreme capacity shortage:
- The solver MUST NOT silently invent a policy penalty trade-off.
- The system must trigger an immediate **EMERGENCY_LOAD_SHED_ALERT** and log a governed violation.
- Station manual override and emergency protocol definition remain: `REQUIRES_STAKEHOLDER_CLARIFICATION` / `STATION_SPECIFIC_VALIDATION_REQUIRED`.

---

## 9. Current Implementation Gap Analysis Summary

1. **Objective Structure**: Composite scalar weighted sum $\\to$ 4-Stage Lexicographic MILP (`NOT_SUPPORTED`).
2. **Unmet Load Penalty**: Soft $\$10,000/kWh$ penalty $\\to$ Stage 1 Hard Constraint ($p_{{\\text{{unmet,critical}}}}=0$) (`NOT_SUPPORTED`).
3. **Load Classification**: Single composite load $\\to$ Governed 5-tier load classification (`NOT_SUPPORTED`).
4. **Diesel Metric**: Cost proxy ($\$2.50/L \\times 0.00025$ L/Wh) $\\to$ Stage 3 Actual Fuel Volume in Liters (`PARTIALLY_SUPPORTED`).
5. **Battery Reserve**: Technical $20\\%$ floor $\\to$ Stage 2 Dynamic EBR Target-Shortfall Minimization (`NOT_SUPPORTED`).
6. **Terminal SOC**: Free terminal energy $E(H) \\ge E_{{\\min}}$ $\\to$ Stage 2 Dynamic Terminal SOC constraint (`NOT_SUPPORTED`).
7. **Renewable Curtailment**: Soft $\$0.001/Wh$ penalty $\\to$ Stage 4 Avoidable Curtailment Minimization (`PARTIALLY_SUPPORTED`).
8. **Forecast Uncertainty**: Deterministic point forecast $\\to$ Deterministic safety margins + MPC correction (`NOT_SUPPORTED`).
9. **Operating Modes**: Single static regime $\\to$ 4 Governed Operating Modes (`NOT_SUPPORTED`).
10. **Infeasibility Protocol**: Soft penalty fallback $\\to$ Governed Infeasibility & Alert Protocol (`NOT_SUPPORTED`).
11. **Thermal Generator Limits**: Min-up/min-down time constraints missing $\\to$ Generator thermal cycle constraints (`NOT_SUPPORTED`).

---

## 10. Acceptance Criteria & Final Governance Summary

$$ \\text{{EMS\\_OBJECTIVE\\_SPECIFICATION}} = \\text{{CONDITIONAL}} $$

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
"""

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.md"), "w") as f:
    f.write(md_content)

# 2. POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.json
json_data = {
    "governance_status": {
        "ems_objective_specification": "CONDITIONAL",
        "stakeholder_policy_status": "HUMAN_APPROVED",
        "policy_definition_resolution": "APPROVED_INPUT",
        "current_ems_implementation": "FROZEN",
        "milp_implementation": "FROZEN",
        "ems_execution": "NOT_AUTHORIZED",
        "mpc_execution": "NOT_AUTHORIZED",
        "digital_twin_execution": "NOT_AUTHORIZED",
        "new_ems_experiment": "NOT_AUTHORIZED",
        "optimizer_modification": "NOT_AUTHORIZED",
        "objective_coefficient_modification": "NOT_AUTHORIZED",
        "model_modification": "NOT_AUTHORIZED",
        "forecasting_modification": "NOT_AUTHORIZED",
        "policy_reinterpretation": "NONE",
        "unauthorized_policy_values": 0,
        "d15_authority_check": "PASS",
        "unit_dimension_check": "PASS",
        "objective_implementation_modified": "NO",
        "milp_modified": "NO",
        "ems_executed": "NO",
        "mpc_executed": "NO",
        "digital_twin_executed": "NO",
        "new_ems_experiment_run": "NO",
        "model_modified": "NO",
        "stage8_1_modified": "NO",
        "engineering_validation_requirements_identified": "YES",
        "implementation_gaps_identified": "YES",
        "infeasibility_policy_status": "CONDITIONAL",
        "next_governed_step": "OBJECTIVE_SPECIFICATION_GOVERNANCE_REVIEW"
    },
    "d15_verification": {
        "status": "PASS",
        "selected_option": "A",
        "source_stakeholder_sheet": "POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md",
        "source_stakeholder_sheet_sha256": STAKEHOLDER_MD_HASH,
        "source_policy_resolution": "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md",
        "source_policy_resolution_sha256": POLICY_RES_MD_HASH,
        "priority_ordering": [
            "1. Critical reliability",
            "2. Emergency battery reserve / resilience",
            "3. Fuel conservation",
            "4. Renewable utilization"
        ]
    },
    "reconstructed_current_baseline": {
        "source_optimizer_yaml_sha256": OPT_YAML_HASH,
        "source_milp_py_sha256": MILP_PY_HASH,
        "current_unmet_load_penalty_per_wh": 10.0,
        "current_marginal_fuel_l_per_wh": 0.00025,
        "current_unmet_to_diesel_cost_ratio": "16000:1",
        "current_objective_type": "SINGLE_COMPOSITE_SCALAR_WEIGHTED_SUM"
    }
}

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.json"), "w") as f:
    json.dump(json_data, f, indent=2)

# 3. POLARIS_EMS_POLICY_TO_OBJECTIVE_TRACEABILITY.csv
traceability_rows = [
    ["POLICY_ID", "POLICY_STATEMENT", "MATHEMATICAL_REQUIREMENT", "TYPE", "CURRENT_IMPLEMENTATION_SUPPORT", "IMPLEMENTATION_GAP", "ENGINEERING_INPUT_REQUIRED", "STAKEHOLDER_CLARIFICATION_REQUIRED", "VALIDATION_REQUIRED", "PROVENANCE"],
    ["D01", "Operating modes concept", "Define 4 operating mode states and transition logic", "OPERATING_MODE_RULE", "NOT_SUPPORTED", "milp.py has single static mode", "Station mode transition thresholds", "NONE", "Mode transition validation", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D02", "Unmet load penalty non-policy status", "Eliminate single scalar $10,000/kWh penalty", "GOVERNANCE_RULE", "NOT_SUPPORTED", "milp.py uses c_unmet=10.0 $/Wh", "NONE", "NONE", "Solver stage 1 verification", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D03", "Emergency mode load shedding", "Allow Essential load shed only under declared emergency", "HARD_CONSTRAINT", "NOT_SUPPORTED", "milp.py permits uniform soft shedding", "Circuit mapping to Essential tier", "NONE", "Emergency shed test", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D04", "Critical load zero shedding", "p_unmet_critical(t) = 0 for all t in Stage 1", "HARD_CONSTRAINT", "NOT_SUPPORTED", "milp.py permits soft unmet critical load", "Critical load circuit inventory", "NONE", "Stage 1 MILP feasibility proof", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D05", "Five-tier load structure", "Represent 5 distinct load classes in load balance", "STATE_REQUIREMENT", "NOT_SUPPORTED", "milp.py aggregates all demand into single variable", "Station load tier assignment", "NONE", "Load decomposition audit", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D06", "Reliability as Stage 1 hard constraint", "min J1 = sum(p_unmet_critical * dt) with J1* = 0", "LEXICOGRAPHIC_OBJECTIVE", "NOT_SUPPORTED", "milp.py optimizes scalar weighted sum", "NONE", "NONE", "Lexicographic solver benchmark", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D07", "Actual fuel consumption in Liters", "min J3 = sum(Fuel_diesel(t)) in Liters", "LEXICOGRAPHIC_OBJECTIVE", "PARTIALLY_SUPPORTED", "milp.py uses linear cost proxy", "Generator fuel curve calibration", "NONE", "Fuel curve empirical test", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D08", "Seasonal / resupply fuel budget", "Enforce V_fuel_avail(t) >= 0 over horizon", "HARD_CONSTRAINT", "NOT_SUPPORTED", "milp.py does not track fuel inventory", "Fuel tank capacity & resupply schedule", "NONE", "Fuel state tracking test", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D09", "Avoidable curtailment minimization", "min J4 = sum(p_curt_avoidable * dt)", "SECONDARY_OBJECTIVE", "PARTIALLY_SUPPORTED", "milp.py applies soft penalty to total curtailment", "NONE", "NONE", "Curtailment decomposition audit", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D10", "Necessary curtailment allowance", "Exclude necessary curtailment from Stage 4 penalty", "HARD_CONSTRAINT", "NOT_SUPPORTED", "milp.py penalizes all curtailment equally", "Inverter & battery acceptance bounds", "NONE", "Curtailment classification test", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D11", "Baseline emergency battery reserve", "EBR_target(t) floor above technical min SOC", "STATE_REQUIREMENT", "NOT_SUPPORTED", "milp.py only enforces 20% technical SOC min", "Emergency hold-up duration evidence", "Authorized EBR percentage floor", "EBR hold-up simulation", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D12", "Dynamic terminal SOC requirement", "E(H) >= E_terminal_target", "LEXICOGRAPHIC_OBJECTIVE", "NOT_SUPPORTED", "milp.py has free terminal state E(H) >= E_min", "Next-day forecast & weather risk data", "Authorized terminal SOC target function", "Terminal SOC benchmark", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D13", "Deterministic uncertainty margins", "Apply safety margins to point forecasts in MPC", "OPERATING_MODE_RULE", "NOT_SUPPORTED", "milp.py uses unadjusted point forecasts", "Forecast error statistical distribution", "NONE", "MPC receding horizon stress test", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D14", "Reliability strictly dominates fuel", "Stage 1 J1 constraint enforced before Stage 3 J3", "LEXICOGRAPHIC_OBJECTIVE", "NOT_SUPPORTED", "milp.py trades fuel vs unmet load via scalar weights", "NONE", "NONE", "Lexicographic dominance proof", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D15", "Strict 4-stage lexicographic hierarchy", "Solve Stage 1 -> Stage 2 -> Stage 3 -> Stage 4", "LEXICOGRAPHIC_OBJECTIVE", "NOT_SUPPORTED", "milp.py uses single composite scalar objective", "NONE", "NONE", "Multi-stage MILP solver validation", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"],
    ["D16", "Multi-tier governance approval", "Sign-off structure for spec and implementation", "GOVERNANCE_RULE", "SUPPORTED_IN_DOCUMENTATION", "Organizational assignments pending", "NONE", "Stakeholder approval authority designation", "Governance audit review", f"POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:{POLICY_RES_MD_HASH}"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_POLICY_TO_OBJECTIVE_TRACEABILITY.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(traceability_rows)

# 4. POLARIS_EMS_MATHEMATICAL_REQUIREMENTS.csv
math_req_rows = [
    ["REQUIREMENT_ID", "NAME", "STAGE_OR_TYPE", "FORMULA", "UNITS", "TIME_BASIS", "STATUS"],
    ["MATH-01", "Stage 1 Critical Reliability", "LEXICOGRAPHIC_STAGE_1", "min J1 = sum(p_unmet_critical(t) * dt)", "Wh", "Hourly over H=24", "GOVERNED_SPECIFICATION"],
    ["MATH-02", "Stage 2 Reserve Target Shortfall", "LEXICOGRAPHIC_STAGE_2", "min J2 = sum(max(0, EBR_target(t) - E_reserve_avail(t))) + max(0, SOC_terminal_target - SOC(H)) * C_bat", "Wh", "Hourly over H=24", "GOVERNED_SPECIFICATION"],
    ["MATH-03", "Stage 3 Fuel Minimization", "LEXICOGRAPHIC_STAGE_3", "min J3 = sum((F_base * u_diesel(t) + F_marg * p_diesel(t)) * dt + Startup_Fuel * v_start(t))", "Liters", "Hourly over H=24", "GOVERNED_SPECIFICATION"],
    ["MATH-04", "Stage 4 Avoidable Curtailment", "LEXICOGRAPHIC_STAGE_4", "min J4 = sum(p_curt_avoidable(t) * dt)", "Wh", "Hourly over H=24", "GOVERNED_SPECIFICATION"],
    ["MATH-05", "Battery Energy Transition", "PHYSICAL_CONSTRAINT", "E(t+1) - E(t) - eta_chg * p_chg(t) * dt + (p_dis(t) / eta_dis) * dt = 0", "Wh", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-06", "Battery Exclusivity", "PHYSICAL_CONSTRAINT", "u_chg(t) + u_dis(t) <= 1", "Binary", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-07", "Battery SOC Bounds", "EQUIPMENT_CONSTRAINT", "E_min <= E(t) <= E_max", "Wh", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-08", "Diesel Output Bounds", "EQUIPMENT_CONSTRAINT", "P_diesel_min * u_diesel(t) <= p_diesel(t) <= P_diesel_max * u_diesel(t)", "W", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-09", "Diesel Startup Tracking", "EQUIPMENT_CONSTRAINT", "v_start(t) >= u_diesel(t) - u_diesel(t-1)", "Binary", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-10", "Bus-Bar Power Balance", "PHYSICAL_CONSTRAINT", "p_sol_used + p_wind_used + p_dis + p_diesel - p_served - p_chg - p_flex = 0", "W", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-11", "Demand Deficit Balance", "PHYSICAL_CONSTRAINT", "p_served(t) + p_unmet(t) = P_demand(t)", "W", "Hourly step", "GOVERNED_SPECIFICATION"],
    ["MATH-12", "SOC-Energy Conversion", "CONVERSION_EQUATION", "E(t) = C_bat * (SOC(t) / 100%)", "Wh vs %", "Instantaneous", "GOVERNED_SPECIFICATION"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_MATHEMATICAL_REQUIREMENTS.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(math_req_rows)

# 5. POLARIS_EMS_PARAMETER_REGISTER.csv
param_rows = [
    ["PARAMETER", "VALUE", "UNIT", "TIME_BASIS", "SOURCE", "SOURCE_SHA256", "STATUS"],
    ["capacity_wh", "200000.0", "Wh", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["min_soc_pct", "20.0", "%", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["max_soc_pct", "95.0", "%", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["charge_efficiency", "0.92", "Dimensionless", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["discharge_efficiency", "0.92", "Dimensionless", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["max_charge_power_w", "50000.0", "W", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["max_discharge_power_w", "50000.0", "W", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["min_diesel_w", "10000.0", "W", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["max_diesel_w", "100000.0", "W", "Static", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["base_fuel_consumption_l_per_h", "5.0", "L/h", "Hourly", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["marginal_fuel_consumption_l_per_wh", "0.00025", "L/Wh", "Hourly", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["startup_cost", "15.0", "$", "Per event", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["c_unmet_prototype", "10.0", "$/Wh", "Hourly", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["c_curt_prototype", "0.001", "$/Wh", "Hourly", "system/config/optimizer.yaml", OPT_YAML_HASH, "CURRENT_IMPLEMENTATION_FACT"],
    ["EBR_baseline_target_pct", "NOT_ESTABLISHED", "%", "Dynamic", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH, "NUMERICAL_CALIBRATION_REQUIRED"],
    ["SOC_terminal_target_pct", "NOT_ESTABLISHED", "%", "Dynamic", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH, "NUMERICAL_CALIBRATION_REQUIRED"],
    ["solar_forecast_margin_pct", "NOT_ESTABLISHED", "%", "Hourly", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH, "NUMERICAL_CALIBRATION_REQUIRED"],
    ["wind_forecast_margin_pct", "NOT_ESTABLISHED", "%", "Hourly", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH, "NUMERICAL_CALIBRATION_REQUIRED"],
    ["demand_forecast_margin_pct", "NOT_ESTABLISHED", "%", "Hourly", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH, "NUMERICAL_CALIBRATION_REQUIRED"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_PARAMETER_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(param_rows)

# 6. POLARIS_EMS_ENGINEERING_VALIDATION_REGISTER.csv
eng_val_rows = [
    ["ITEM_ID", "CATEGORY", "DESCRIPTION", "TYPE", "STATION_DATA_REQUIRED", "STAKEHOLDER_DECISION_REQUIRED", "STATUS"],
    ["ENG-01", "LOAD_MAPPING", "Circuit-level assignment of station loads to 5 tiers", "DATA_REQUIRED", "YES", "YES", "STATION_SPECIFIC_VALIDATION_REQUIRED"],
    ["ENG-02", "GENERATOR_FUEL", "Empirical fuel consumption curve (L/h vs kW)", "DATA_REQUIRED", "YES", "NO", "NUMERICAL_CALIBRATION_REQUIRED"],
    ["ENG-03", "GENERATOR_THERMAL", "Minimum-up and minimum-down time limits", "DATA_REQUIRED", "YES", "NO", "STATION_SPECIFIC_VALIDATION_REQUIRED"],
    ["ENG-04", "BATTERY_EBR", "Emergency hold-up time requirement & EBR target floor", "DATA_REQUIRED", "YES", "YES", "NUMERICAL_CALIBRATION_REQUIRED"],
    ["ENG-05", "TERMINAL_SOC", "Dynamic terminal SOC target function parameters", "DATA_REQUIRED", "YES", "YES", "NUMERICAL_CALIBRATION_REQUIRED"],
    ["ENG-06", "FORECAST_ERROR", "Historical error distributions for solar, wind, demand", "DATA_REQUIRED", "YES", "NO", "NUMERICAL_CALIBRATION_REQUIRED"],
    ["ENG-07", "FUEL_TANK", "Station fuel storage capacity & resupply cycle limits", "DATA_REQUIRED", "YES", "NO", "STATION_SPECIFIC_VALIDATION_REQUIRED"],
    ["ENG-08", "MPC_TIMING", "Real-time solver execution timing & horizon step dt", "DATA_REQUIRED", "YES", "NO", "STATION_SPECIFIC_VALIDATION_REQUIRED"],
    ["ENG-09", "ATS_TRANSFER", "Automatic Transfer Switch hold-up & transition timing", "DATA_REQUIRED", "YES", "NO", "STATION_SPECIFIC_VALIDATION_REQUIRED"],
    ["ENG-10", "MODE_THRESHOLDS", "Numerical triggers for mode transitions", "DATA_REQUIRED", "YES", "YES", "STATION_SPECIFIC_VALIDATION_REQUIRED"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_ENGINEERING_VALIDATION_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(eng_val_rows)

# 7. POLARIS_EMS_IMPLEMENTATION_GAP_REGISTER.csv
gap_rows = [
    ["GAP_ID", "FEATURE", "FROZEN_IMPLEMENTATION_FACT", "GOVERNED_V2_SPECIFICATION", "SUPPORT_STATUS", "ACTION_REQUIRED"],
    ["GAP-01", "Objective Structure", "Single composite scalar weighted sum", "4-Stage Lexicographic MILP", "NOT_SUPPORTED", "Replace scalar objective in milp.py with multi-stage solver"],
    ["GAP-02", "Unmet Load Penalty", "$10,000/kWh soft penalty uniform across load", "Stage 1 Hard Constraint p_unmet_critical=0", "NOT_SUPPORTED", "Enforce hard zero unmet load constraint for Critical tier"],
    ["GAP-03", "Load Tiers", "Single composite load demand vector", "5-tier load classification (Critical to Noncritical)", "NOT_SUPPORTED", "Decompose demand forecast into 5 tier vectors"],
    ["GAP-04", "Diesel Objective", "Marginal + base cost proxy in dollars", "Stage 3 Actual fuel volume in Liters", "PARTIALLY_SUPPORTED", "Formulate Stage 3 objective in physical Liters"],
    ["GAP-05", "Emergency Reserve", "20% technical minimum SOC", "Stage 2 Dynamic EBR target shortfall minimization", "NOT_SUPPORTED", "Add EBR target shortfall term to Stage 2"],
    ["GAP-06", "Terminal SOC", "Free terminal state E(H) >= E_min", "Stage 2 Terminal SOC target constraint", "NOT_SUPPORTED", "Add terminal SOC target constraint to Stage 2"],
    ["GAP-07", "Renewable Curtailment", "Soft $0.001/Wh penalty on all curtailment", "Stage 4 Avoidable curtailment minimization", "PARTIALLY_SUPPORTED", "Decompose total curtailment into necessary vs avoidable"],
    ["GAP-08", "Forecast Uncertainty", "Deterministic point forecast without margins", "Deterministic safety margins + MPC correction", "NOT_SUPPORTED", "Add safety margin adjustment layer to ForecastBundle"],
    ["GAP-09", "Operating Modes", "Single static operating regime", "4 governed operating modes", "NOT_SUPPORTED", "Implement mode state machine wrapper around optimizer"],
    ["GAP-10", "Infeasibility Protocol", "Return degraded plan with 1e9 objective", "Governed emergency alert and shedding protocol", "NOT_SUPPORTED", "Implement explicit infeasibility exception & alert handler"],
    ["GAP-11", "Thermal Cycle Limits", "No min-up / min-down time constraints", "Diesel minimum-up and minimum-down constraints", "NOT_SUPPORTED", "Add binary time-in-state constraints to MILP formulation"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_IMPLEMENTATION_GAP_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(gap_rows)

# 8. POLARIS_EMS_INFEASIBILITY_POLICY_REGISTER.csv
infeas_rows = [
    ["SCENARIO_ID", "CONDITION", "GOVERNED_BEHAVIOR", "POLICY_STATUS", "ENGINEERING_ACTION"],
    ["INF-01", "Stage 1 Infeasible (Capacity < Critical Load)", "Trigger EMERGENCY_CRITICAL_DEFICIT_ALERT; log governed exception; do not invent trade-off", "REQUIRES_STAKEHOLDER_CLARIFICATION", "Register missing emergency priority protocol"],
    ["INF-02", "Stage 2 Infeasible (EBR Target Unattainable)", "Satisfy Stage 1; minimize EBR shortfall J2; raise RESERVE_DEFICIT_WARNING", "ALREADY_POLICY_DEFINED", "Formulate Stage 2 shortfall objective"],
    ["INF-03", "Fuel Budget Exhausted (V_fuel_avail = 0)", "Operate purely on renewables + battery; trigger FUEL_EXHAUSTION_EMERGENCY", "ALREADY_POLICY_DEFINED", "Enforce hard fuel inventory bound"],
    ["INF-04", "Solver Runtime Failure / Timeout", "Raise OPTIMIZATION_RUNTIME_FAILURE; retain last valid dispatch plan", "ALREADY_POLICY_DEFINED", "Implement watchdog timer & safe fallback state"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_INFEASIBILITY_POLICY_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(infeas_rows)

# 9. POLARIS_EMS_IMPLEMENTATION_CHANGE_REGISTER.csv
change_rows = [
    ["CURRENT_COMPONENT", "REQUIRED_CHANGE", "REASON", "POLICY_SOURCE", "IMPLEMENTATION_IMPACT", "SAFETY_IMPACT", "VALIDATION_REQUIRED", "AUTHORIZATION_REQUIRED"],
    ["system/optimization/implementations/milp.py", "Replace single optimize() call with 4-stage sequential lexicographic solver", "Satisfy Decision 15 Option A priority structure", "Decision 15", "HIGH", "POSITIVE", "Multi-stage MILP benchmark", "STAGE_AUTHORIZATION_REQUIRED"],
    ["system/optimization/implementations/milp.py", "Decompose demand into 5 load tier variables", "Implement Decision 05 five-tier load classification", "Decision 05", "MEDIUM", "POSITIVE", "Load tier balance test", "STAGE_AUTHORIZATION_REQUIRED"],
    ["system/optimization/implementations/milp.py", "Add Stage 1 hard zero unmet critical load constraint", "Enforce Decision 04 critical reliability policy", "Decision 04", "HIGH", "CRITICAL", "Feasibility proof", "STAGE_AUTHORIZATION_REQUIRED"],
    ["system/optimization/implementations/milp.py", "Add Stage 2 EBR and Terminal SOC target shortfall terms", "Implement Decision 11 & 12 reserve resilience policy", "Decision 11, 12", "MEDIUM", "POSITIVE", "Resilience hold-up test", "STAGE_AUTHORIZATION_REQUIRED"],
    ["system/config/optimizer.yaml", "Deprecate c_unmet=1000.0 prototype weight", "Remove non-policy scalar penalty assumption", "Decision 02", "LOW", "NEUTRAL", "Config schema audit", "STAGE_AUTHORIZATION_REQUIRED"]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_IMPLEMENTATION_CHANGE_REGISTER.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(change_rows)

# 10. POLARIS_EMS_OBJECTIVE_PROVENANCE.csv
prov_rows = [
    ["ITEM", "STATEMENT_OR_VALUE", "CLASSIFICATION", "PROVENANCE_SOURCE", "SOURCE_SHA256"],
    ["Decision 15 Selection", "Option A: Strict Lexicographic Hierarchy (Reliability -> Resilience -> Fuel -> Renewables)", "HUMAN_STAKEHOLDER_DECISION", "POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md", STAKEHOLDER_MD_HASH],
    ["Policy Definition Resolution", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION Version 1.1.0", "DOCUMENTED_POLICY", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH],
    ["Current Unmet Load Penalty", "c_unmet = 10,000 $/kWh ($10.00/Wh)", "CURRENT_IMPLEMENTATION_FACT", "system/config/optimizer.yaml", OPT_YAML_HASH],
    ["Current Diesel Marginal Fuel", "0.00025 L/Wh (0.25 L/kWh)", "CURRENT_IMPLEMENTATION_FACT", "system/config/optimizer.yaml", OPT_YAML_HASH],
    ["Current Battery Capacity", "200,000 Wh (200 kWh)", "CURRENT_IMPLEMENTATION_FACT", "system/config/optimizer.yaml", OPT_YAML_HASH],
    ["Current Battery Min SOC", "20.0%", "CURRENT_IMPLEMENTATION_FACT", "system/config/optimizer.yaml", OPT_YAML_HASH],
    ["Provisional EBR Target", "35% / 45% (Unapproved provisional values)", "PROVISIONAL_ENGINEERING_VALUE", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH],
    ["Provisional Forecast Margins", "Solar -15..25%, Wind -20..30%, Demand +10% (Unapproved provisional values)", "PROVISIONAL_ENGINEERING_VALUE", "POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md", POLICY_RES_MD_HASH]
]

with open(os.path.join(TARGET_DIR, "POLARIS_EMS_OBJECTIVE_PROVENANCE.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(prov_rows)

# 11. POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv
generated_files = [
    "POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.md",
    "POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2.json",
    "POLARIS_EMS_POLICY_TO_OBJECTIVE_TRACEABILITY.csv",
    "POLARIS_EMS_MATHEMATICAL_REQUIREMENTS.csv",
    "POLARIS_EMS_PARAMETER_REGISTER.csv",
    "POLARIS_EMS_ENGINEERING_VALIDATION_REGISTER.csv",
    "POLARIS_EMS_IMPLEMENTATION_GAP_REGISTER.csv",
    "POLARIS_EMS_INFEASIBILITY_POLICY_REGISTER.csv",
    "POLARIS_EMS_IMPLEMENTATION_CHANGE_REGISTER.csv",
    "POLARIS_EMS_OBJECTIVE_PROVENANCE.csv"
]

hash_rows = [["PATH", "SHA256", "VERIFICATION_STATUS"]]

for fname in generated_files:
    fpath = os.path.join(TARGET_DIR, fname)
    with open(fpath, "rb") as fp:
        h = hashlib.sha256(fp.read()).hexdigest()
    rel_path = os.path.join("ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2", fname)
    hash_rows.append([rel_path, h, "VERIFIED_CALCULATED"])

hash_audit_path = os.path.join(TARGET_DIR, "POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv")
with open(hash_audit_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(hash_rows)

# Finally add hash of POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv itself to complete self-hash verification
with open(hash_audit_path, "rb") as fp:
    self_hash = hashlib.sha256(fp.read()).hexdigest()

print("All 11 artifacts generated successfully in ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2/")
print("Self hash of POLARIS_EMS_OBJECTIVE_HASH_AUDIT.csv:", self_hash)
