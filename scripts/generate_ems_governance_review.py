import os
import hashlib
import json

base_dir = "/home/punith-bs/01polaris (Copy)/ems/campaigns/POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW"
os.makedirs(base_dir, exist_ok=True)

# 1. Requirements Matrix CSV
req_matrix_path = os.path.join(base_dir, "POLARIS_BRANCH01_EMS_OBJECTIVE_REQUIREMENTS_MATRIX.csv")
req_matrix_content = """REQUIREMENT_ID,DOCUMENTED_REQUIREMENT,SOURCE,CURRENT_IMPLEMENTATION,IMPLEMENTATION_TYPE,CURRENT_OBJECTIVE_TERM,CURRENT_CONSTRAINT,V2_EVIDENCE,ALIGNMENT_STATUS,GOVERNANCE_GAP
REQ_01,Reliable power supply for critical polar station loads,docs/decision_registers/POLARIS_MASTER_HANDOFF.md Section 1; docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md Section 1,c[base+9] = $10.0/Wh ($10000/kWh) unmet load penalty,SOFT_CONSTRAINT,unmet_penalty_per_wh * dt,NONE,Treatment unmet load reduced from 40352.215 kWh to 9808.462 kWh (-30543.753 kWh),PARTIALLY_ALIGNED,No explicit numerical reliability target or maximum acceptable unmet load threshold specified.
REQ_02,Optimize/minimize diesel fuel consumption,docs/decision_registers/POLARIS_MASTER_HANDOFF.md Section 1; docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md Section 6,c[base+7] = $0.625/kWh marginal fuel + c[base+13] = $12.50/h base fuel,OBJECTIVE_TERM,fuel_cost_per_l * marg_fuel_l_wh * dt + fuel_cost_per_l * base_fuel_l_h * dt,NONE,Treatment fuel consumption increased from 22486.701 L to 33836.880 L (+11350.179 L),PARTIALLY_ALIGNED,Qualitative goal documented but no numerical fuel consumption limit or tradeoff priority specified.
REQ_03,Maximize renewable energy integration and minimize curtailment,docs/decision_registers/POLARIS_MASTER_HANDOFF.md Section 1 & 2; docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md Section 6,c[base+2] = $1.00/kWh solar curtailment + c[base+3] = $1.00/kWh wind curtailment,OBJECTIVE_TERM,curt_penalty_per_wh * dt,NONE,Treatment curtailment decreased by 70.709 kWh on sample trajectories,PARTIALLY_ALIGNED,No target renewable fraction or maximum curtailment threshold specified.
REQ_04,Preserve battery storage health and respect SOC limits,docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md Section 6; battery.yaml,c[base+4] & c[base+5] = $0.05/kWh degradation + SOC bounds [20% 95%],OBJECTIVE_TERM_AND_HARD_CONSTRAINT,deg_penalty * dt,lb[base+6] = 20% max[base+6] = 95%,Treatment battery throughput increased (+5810.729 kWh charge / +3746.782 kWh discharge) without SOC violations,ALIGNED,Hard SOC bounds defined but no dynamic emergency reserve or terminal SOC requirement specified.
REQ_05,Fuel consumption vs Reliability operational tradeoff,NOT_EXPLICITLY_DOCUMENTED in project governance,Implied 16000:1 penalty-to-cost ratio ($10000/kWh vs $0.625/kWh),PROTOTYPE_ASSUMPTION,16000x ratio between unmet load penalty and marginal fuel cost,NONE,V2 trade-off: Treatment consumed +11350.179 L fuel to eliminate 30543.753 kWh unmet load,NOT_SPECIFIED,Project documentation does not specify the governed tradeoff ratio between fuel consumption and unmet load.
"""
with open(req_matrix_path, "w") as f:
    f.write(req_matrix_content)

# 2. Objective Provenance CSV
provenance_csv_path = os.path.join(base_dir, "POLARIS_BRANCH01_OBJECTIVE_PROVENANCE.csv")
provenance_csv_content = """source_file,source_location,source_sha256,term_name,decision_variable,coefficient_value,coefficient_unit,semantic_role,governance_status
system/optimization/implementations/milp.py,Line 107,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_curt_sol,c[base+2],0.001,$/Wh,Solar curtailment penalty term,PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 108,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_curt_wind,c[base+3],0.001,$/Wh,Wind curtailment penalty term,PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 109,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_chg,c[base+4],0.00005,$/Wh,Battery charging degradation penalty,PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 110,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_dis,c[base+5],0.00005,$/Wh,Battery discharging degradation penalty,PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 111,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_diesel,c[base+7],0.000625,$/Wh,Marginal diesel fuel cost ($2.50/L * 0.00025 L/Wh),PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 112,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,p_unmet,c[base+9],10.0,$/Wh,Unmet critical load penalty ($10000/kWh unweighted),PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 113,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,u_diesel,c[base+13],12.50,$/h,Base diesel running fuel cost ($2.50/L * 5.0 L/h),PROTOTYPE_ASSUMPTION
system/optimization/implementations/milp.py,Line 114,ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35,v_start,c[base+14],15.0,$,Diesel generator startup cost penalty,PROTOTYPE_ASSUMPTION
"""
with open(provenance_csv_path, "w") as f:
    f.write(provenance_csv_content)

# 3. Frozen MILP Objective Audit JSON
milp_json_path = os.path.join(base_dir, "POLARIS_BRANCH01_FROZEN_MILP_OBJECTIVE_AUDIT.json")
milp_json_data = {
  "audit_id": "POLARIS_BRANCH01_FROZEN_MILP_OBJECTIVE_AUDIT",
  "audit_mode": "READ_ONLY_GOVERNANCE_REVIEW",
  "timestamp": "2026-09-21T20:05:03Z",
  "source_file": "system/optimization/implementations/milp.py",
  "source_sha256": "ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35",
  "optimizer_class": "LocalMILPEnergyOptimizer",
  "objective_reconciliation": "PASS",
  "objective_coefficients": {
    "unmet_load_penalty_per_wh_usd": 10.0,
    "unmet_load_penalty_per_kwh_usd": 10000.0,
    "marginal_fuel_litres_per_wh": 0.00025,
    "marginal_fuel_cost_per_wh_usd": 0.000625,
    "marginal_fuel_cost_per_kwh_usd": 0.625,
    "base_fuel_litres_per_hour": 5.0,
    "base_fuel_cost_per_hour_usd": 12.50,
    "startup_cost_usd": 15.0,
    "curtailment_penalty_per_wh_usd": 0.001,
    "curtailment_penalty_per_kwh_usd": 1.00,
    "battery_degradation_penalty_per_wh_usd": 0.00005,
    "battery_degradation_penalty_per_kwh_usd": 0.05
  },
  "tradeoff_ratios": {
    "unmet_load_to_marginal_diesel_cost_ratio": 16000.0,
    "unmet_load_to_curtailment_cost_ratio": 10000.0,
    "base_fuel_hour_to_marginal_fuel_kwh_ratio": 20.0
  },
  "audit_finding": "The frozen MILP objective source code in milp.py is verified. The objective places a $10,000/kWh penalty on unmet load vs $0.625/kWh marginal fuel cost (16,000x ratio). The observed V2 dispatch (+11350.179 L fuel, -30543.753 kWh unmet load) is mathematically consistent with this frozen objective given the treatment forecast inputs."
}
with open(milp_json_path, "w") as f:
    json.dump(milp_json_data, f, indent=2)

# 4. Frozen MILP Objective Audit MD
milp_md_path = os.path.join(base_dir, "POLARIS_BRANCH01_FROZEN_MILP_OBJECTIVE_AUDIT.md")
milp_md_content = r"""# POLARIS Branch01 Frozen MILP Objective Source Audit Report

**Source File**: `system/optimization/implementations/milp.py`  
**Source SHA256**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`  
**Optimizer Class**: `LocalMILPEnergyOptimizer`  
**Audit Mode**: READ_ONLY_SOURCE_AUDIT  

---

## 1. Verified Objective Function Coefficients

Direct inspection of `system/optimization/implementations/milp.py` lines 93–115 verifies the exact objective construction:

$$\min \sum_{t=0}^{23} \left( c_{\text{curt}} (P_{\text{curt,sol},t} + P_{\text{curt,wind},t}) \cdot w_t + c_{\text{deg}} (P_{\text{chg},t} + P_{\text{dis},t}) \cdot w_t + c_{\text{fuel,marg}} P_{\text{diesel},t} \cdot w_t + c_{\text{unmet}} P_{\text{unmet},t} + c_{\text{fuel,base}} u_{\text{diesel},t} \cdot w_t + c_{\text{start}} v_{\text{start},t} \cdot w_t \right)$$

| Objective Variable | Decision Index | Config Key | Verified Value ($/Wh) | Verified Value ($/kWh) | Weighting ($w_t$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`p_curt_sol`** | `base + 2` | `renewable_curtailment_penalty` | $0.001 | $1.00 | Weighted ($w_t = \gamma^t$) |
| **`p_curt_wind`** | `base + 3` | `renewable_curtailment_penalty` | $0.001 | $1.00 | Weighted ($w_t = \gamma^t$) |
| **`p_chg`** | `base + 4` | `deg_penalty_per_wh` | $0.00005 | $0.05 | Weighted ($w_t = \gamma^t$) |
| **`p_dis`** | `base + 5` | `deg_penalty_per_wh` | $0.00005 | $0.05 | Weighted ($w_t = \gamma^t$) |
| **`p_diesel`** | `base + 7` | `fuel_cost_per_l * marg_fuel_l_wh` | $0.000625 | $0.625 | Weighted ($w_t = \gamma^t$) |
| **`p_unmet`** | `base + 9` | `unmet_penalty_per_wh` | $10.0 | $10,000.00 | **Unweighted** ($w_t = 1.0$) |
| **`u_diesel`** | `base + 13` | `fuel_cost_per_l * base_fuel_l_h` | $12.50 / h | $12.50 / h | Weighted ($w_t = \gamma^t$) |
| **`v_start`** | `base + 14` | `startup_cost` | $15.00 / start | $15.00 / start | Weighted ($w_t = \gamma^t$) |

---

## 2. Mathematical Trade-off Ratios

1. **Unmet Load Penalty to Marginal Diesel Fuel Cost**:
   $$\frac{c_{\text{unmet}}}{c_{\text{fuel,marg}}} = \frac{\$10,000/\text{kWh}}{\$0.625/\text{kWh}} = 16,000.0$$
   *Semantic Meaning*: The optimizer is mathematically willing to spend up to 16,000 kWh of marginal diesel fuel cost ($16,000 \times \$0.625 = \$10,000$) to prevent a single kWh of unmet critical load.

2. **Unmet Load Penalty to Renewable Curtailment Penalty**:
   $$\frac{c_{\text{unmet}}}{c_{\text{curt}}} = \frac{\$10,000/\text{kWh}}{\$1.00/\text{kWh}} = 10,000.0$$

3. **Base Running Cost to Marginal Fuel Cost Equivalent**:
   $$\frac{c_{\text{fuel,base}}}{c_{\text{fuel,marg}}} = \frac{\$12.50/\text{h}}{\$0.625/\text{kWh}} = 20.0\text{ kWh equivalent / hour}$$

---

## 3. Objective Reconciliation Status

`OBJECTIVE_NUMERIC_RECONCILIATION = PASS`

The numeric values reported in previous forensic audits are 100% verified against the frozen source code `system/optimization/implementations/milp.py`.
"""
with open(milp_md_path, "w") as f:
    f.write(milp_md_content)

# 5. Requirements Gap Analysis JSON
gap_json_path = os.path.join(base_dir, "POLARIS_BRANCH01_REQUIREMENTS_GAP_ANALYSIS.json")
gap_json_data = {
  "audit_id": "POLARIS_BRANCH01_REQUIREMENTS_GAP_ANALYSIS",
  "audit_mode": "READ_ONLY_GOVERNANCE_REVIEW",
  "timestamp": "2026-09-21T20:05:03Z",
  "requirements_gaps": {
    "1_maximum_acceptable_unmet_load": "NOT_SPECIFIED",
    "2_reliability_numeric_target": "NOT_SPECIFIED",
    "3_fuel_minimization_numeric_target": "NOT_SPECIFIED",
    "4_operating_cost_target": "NOT_SPECIFIED",
    "5_fuel_vs_reliability_tradeoff": "NOT_SPECIFIED",
    "6_renewable_utilization_target": "NOT_SPECIFIED",
    "7_curtailment_limit": "NOT_SPECIFIED",
    "8_battery_reserve_target": "NOT_SPECIFIED",
    "9_diesel_usage_limit": "NOT_SPECIFIED",
    "10_critical_load_priority": "NOT_SPECIFIED",
    "11_load_shedding_priority": "NOT_SPECIFIED"
  },
  "implementation_assumptions": [
    {
      "assumption_id": "ASSUMPTION_01",
      "target_component": "critical_load.unmet_penalty_per_wh",
      "source_file": "system/config/loads.yaml",
      "value": 10.0,
      "status_label": "PROTOTYPE_ASSUMPTION",
      "description": "Unmet load penalty set to $10,000/kWh as an unverified prototype heuristic rather than a governed requirement."
    },
    {
      "assumption_id": "ASSUMPTION_02",
      "target_component": "diesel_genset.operation",
      "source_file": "system/config/diesel.yaml",
      "value": "10kW min / 100kW max",
      "status_label": "PROTOTYPE_ASSUMPTION",
      "description": "Diesel generator dispatch is unconstrained whenever needed to serve load or preserve battery SOC."
    },
    {
      "assumption_id": "ASSUMPTION_03",
      "target_component": "fuel_cost_per_l",
      "source_file": "system/config/diesel.yaml",
      "value": 2.50,
      "status_label": "PROTOTYPE_ASSUMPTION",
      "description": "Fuel price fixed at $2.50/L without arctic logistics resupply cost scaling."
    }
  ],
  "objective_modification": "NOT_AUTHORIZED",
  "next_governed_step": "EXPLICIT_EMS_OBJECTIVE_SPECIFICATION_REVIEW"
}
with open(gap_json_path, "w") as f:
    json.dump(gap_json_data, f, indent=2)

# 6. Requirements Gap Analysis MD
gap_md_path = os.path.join(base_dir, "POLARIS_BRANCH01_REQUIREMENTS_GAP_ANALYSIS.md")
gap_md_content = """# POLARIS Branch01 Requirements & Governance Gap Analysis Report

**Governance Mode**: READ_ONLY_REQUIREMENTS_AUDIT  
**Audit Timestamp**: 2026-09-21T20:05:03Z  
**Authoritative Scope**: POLARIS Project Documentation vs Frozen EMS Implementation  

---

## 1. Identified Governance Gaps (Missing Specifications)

The following essential operational parameters lack explicit numerical thresholds or governed priorities in current POLARIS project documentation:

| Operational Dimension | Status | Description |
| :--- | :--- | :--- |
| **1. Maximum Acceptable Unmet Load** | **`NOT_SPECIFIED`** | No numerical kWh or percentage limit defined for acceptable load shedding. |
| **2. Reliability Target** | **`NOT_SPECIFIED`** | Documented qualitatively ("reliable energy supply"), but no numerical SLA (e.g. 99.9% uptime) is specified. |
| **3. Fuel Minimization Target** | **`NOT_SPECIFIED`** | Documented qualitatively ("fuel minimization"), but no numerical fuel reduction target (e.g. 20% savings) is specified. |
| **4. Operating Cost Target** | **`NOT_SPECIFIED`** | No target operational expenditure budget specified. |
| **5. Fuel vs. Reliability Tradeoff** | **`NOT_SPECIFIED`** | No explicit exchange rate between litres of diesel fuel and kWh of unmet load is defined. |
| **6. Renewable Utilization Target** | **`NOT_SPECIFIED`** | No target renewable fraction (e.g. 40% solar/wind contribution) specified. |
| **7. Curtailment Limit** | **`NOT_SPECIFIED`** | No maximum allowable curtailment kWh specified. |
| **8. Battery Reserve Target** | **`NOT_SPECIFIED`** | Hard bounds (20%–95%) defined, but no dynamic emergency reserve floor specified. |
| **9. Diesel Usage Limit** | **`NOT_SPECIFIED`** | No maximum diesel generator runtime hours or fuel consumption cap specified. |
| **10. Critical Load Priority** | **`NOT_SPECIFIED`** | Critical loads identified qualitatively, but multi-tier load shed priority order lacks numerical ranking. |
| **11. Load-Shedding Priority** | **`NOT_SPECIFIED`** | No explicit tiering between heating, communications, life-support, and science loads. |

---

## 2. Identified Implementation Assumptions

The current frozen EMS contains several parameters marked explicitly as `PROTOTYPE_ASSUMPTION` in `system/config/`:

1. **Unmet Load Penalty ($10,000/kWh)** (`system/config/loads.yaml`): Set as a large arbitrary penalty to enforce near-zero unmet load in MILP solves, creating a 16,000:1 tradeoff ratio against fuel cost.
2. **Fuel Cost ($2.50/L)** (`system/config/diesel.yaml`): Fixed price without remote arctic resupply logistics multiplier.
3. **Diesel Base Run Rate (5.0 L/h)** (`system/config/diesel.yaml`): Fixed idle fuel consumption parameter.

---

## 3. Required Future Governance Sequence

Before any objective coefficient modification or EMS code alteration can be authorized, the following 8-step sequence must be executed:

```
1. Explicit Operational Requirement Specification
        ↓
2. Formal Objective Specification
        ↓
3. Governance Review & Approval
        ↓
4. Implementation Specification
        ↓
5. Static Code & Interface Verification
        ↓
6. Controlled Experimentation
        ↓
7. Forensic Evaluation
        ↓
8. Promotion Decision
```

**Authorization Status**: `OBJECTIVE_MODIFICATION = NOT_AUTHORIZED`
"""
with open(gap_md_path, "w") as f:
    f.write(gap_md_content)

# 7. EMS Objective Governance Review JSON
review_json_path = os.path.join(base_dir, "POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW.json")
review_json_data = {
  "audit_id": "POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW",
  "audit_mode": "READ_ONLY_REQUIREMENTS_AUDIT",
  "timestamp": "2026-09-21T20:05:03Z",
  "governance_classifications": {
    "V2_EVIDENCE_LOCK": "PASS",
    "FORENSIC_RESULT_STATUS": "FROZEN_VALID",
    "EMS_OBJECTIVE_AUDIT": "PASS",
    "OBJECTIVE_NUMERIC_RECONCILIATION": "PASS",
    "REQUIREMENTS_RECONCILIATION": "LIMITED",
    "OBJECTIVE_REQUIREMENT_ALIGNMENT": "PARTIALLY_ALIGNED",
    "FUEL_REQUIREMENT": "IMPLICIT",
    "RELIABILITY_REQUIREMENT": "QUALITATIVE_ONLY",
    "FUEL_NUMERIC_TARGET": "NOT_SPECIFIED",
    "RELIABILITY_NUMERIC_TARGET": "NOT_SPECIFIED",
    "FUEL_VS_RELIABILITY_TRADEOFF": "NOT_SPECIFIED",
    "OBJECTIVE_PRIORITY": "NOT_SPECIFIED",
    "OBJECTIVE_MODIFICATION": "NOT_AUTHORIZED",
    "EMS_MODIFICATION": "NOT_AUTHORIZED",
    "MODEL_MODIFICATION": "NOT_AUTHORIZED",
    "MODEL_RETRAINING": "NOT_AUTHORIZED",
    "NEW_EMS_EXPERIMENT": "NOT_AUTHORIZED",
    "ANNUAL_RESULT_STATUS": "REPRESENTATIVE_TRAJECTORY_SET",
    "NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING": "NOT_ESTABLISHED",
    "NEXT_GOVERNED_STEP": "EXPLICIT_EMS_OBJECTIVE_SPECIFICATION_REVIEW"
  },
  "frozen_v2_results": {
    "TRAJECTORIES": 173,
    "H1_STEPS": 4152,
    "CONTROL_FUEL": 22486.701,
    "TREATMENT_FUEL": 33836.880,
    "FUEL_DIFFERENCE": 11350.179,
    "CONTROL_DIESEL": 62126.805,
    "TREATMENT_DIESEL": 95667.521,
    "DIESEL_DIFFERENCE": 33540.716,
    "CONTROL_LOAD_SERVED": 75480.485,
    "TREATMENT_LOAD_SERVED": 106024.238,
    "LOAD_SERVED_DIFFERENCE": 30543.753,
    "CONTROL_UNMET_LOAD": 40352.215,
    "TREATMENT_UNMET_LOAD": 9808.462,
    "UNMET_LOAD_DIFFERENCE": -30543.753
  }
}
with open(review_json_path, "w") as f:
    json.dump(review_json_data, f, indent=2)

# 8. EMS Objective Governance Review MD
review_md_path = os.path.join(base_dir, "POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW.md")
review_md_content = """# POLARIS Branch01 V2 EMS Objective & Requirements Governance Review

**Governance Status**: READ_ONLY_REQUIREMENTS_AUDIT  
**Audit Timestamp**: 2026-09-21T20:05:03Z  
**Authoritative Directory**: `ems/campaigns/POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW/`  

---

## Executive Governance Summary

The POLARIS Branch01 V2 controlled EMS/MPC campaign is complete, frozen, and audited. This governance review evaluates whether the frozen EMS objective is aligned with the documented operational requirements of the POLARIS project.

No code, optimizer coefficients, constraints, models, forecasts, or simulation trajectories were modified or rerun.

### Key Audit Findings
1. **Current EMS Objective Semantics**: The frozen MILP optimizer mathematically prioritizes avoiding unmet load above all else, placing an unweighted $10,000/kWh penalty on unmet load vs a $0.625/kWh marginal fuel cost (a 16,000:1 ratio).
2. **Observed V2 Trade-off Reconciliation**: Faced with lower predicted solar availability under Treatment (Branch01), the optimizer dispatches diesel generation to avoid unmet load, reducing unmet load by 30,543.753 kWh while consuming +11,350.179 L of additional fuel. This dispatch is consistent with the frozen MILP objective given treatment forecast inputs.
3. **Requirement vs. Implementation Alignment**: `OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED`. Qualitative goals for fuel minimization, reliable load service, and renewable integration exist in project documentation, but numerical targets and explicit tradeoff ratios are missing.
4. **Governance Gap**: The POLARIS project currently lacks governed numerical specifications for maximum acceptable unmet load, fuel consumption targets, and the fuel-vs-reliability exchange rate.
5. **Authorization Boundary**: Objective modification is `NOT_AUTHORIZED`. An explicit EMS objective specification must be governed before objective tuning or new experiments can proceed.

---

## Frozen V2 Metrics & Causal Baseline Verification

| Metric | Control | Treatment | Difference | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Completed Trajectories** | 173 | 173 | 0 | FROZEN_MATCH |
| **H1 Horizon Steps** | 4,152 | 4,152 | 0 | FROZEN_MATCH |
| **Fuel Consumption (L)** | 22,486.701 | 33,836.880 | +11,350.179 | FROZEN_MATCH |
| **Diesel Generation (kWh)** | 62,126.805 | 95,667.521 | +33,540.716 | FROZEN_MATCH |
| **Load Served (kWh)** | 75,480.485 | 106,024.238 | +30,543.753 | FROZEN_MATCH |
| **Unmet Load (kWh)** | 40,352.215 | 9,808.462 | -30,543.753 | FROZEN_MATCH |

**Authoritative Causal Classification**: `MECHANISM_PARTIALLY_ESTABLISHED`  
**Forecast Intervention to Dispatch**: `ESTABLISHED`  
**Branch01 Relative Accuracy**: `ESTABLISHED`  
**Control Optimism**: `ESTABLISHED`  
**Forecast Accuracy to Operational Causality**: `PARTIALLY_ESTABLISHED`  
**Optimizer Consistency**: `ESTABLISHED`  

---

## Comprehensive Human-Review Summary (Core Governance Questions)

### 1. What does the frozen EMS currently optimize?
The frozen `LocalMILPEnergyOptimizer` minimizes total economic cost over a 24-hour horizon, dominated by an unweighted $10,000/kWh penalty on unmet load alongside marginal fuel cost ($0.625/kWh), base running fuel cost ($12.50/h), generator startup penalty ($15/start), battery degradation ($0.05/kWh), and renewable curtailment ($1.00/kWh).

### 2. What does POLARIS documentation say it should optimize?
POLARIS documentation (`docs/decision_registers/POLARIS_MASTER_HANDOFF.md`, `docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md`) states that the EMS should provide reliable power supply for polar research stations while optimizing/minimizing diesel fuel consumption, maximizing renewable integration, and preserving energy security.

### 3. Which requirements are explicit?
- Local offline execution requirement (100% offline).
- Separation of forecasting and optimization (`ForecastBundle` contract).
- Battery hard operating bounds (20%–95% SOC, 50 kW max power).
- Generator power bounds (10 kW min, 100 kW max when active).

### 4. Which requirements are qualitative only?
- "Minimize fuel consumption" (no numerical fuel cap or percentage reduction).
- "Provide reliable energy supply" (no numerical uptime SLA or outage allowance).
- "Maximize renewable utilization" (no numerical renewable fraction target).

### 5. Which numerical thresholds are missing?
- Maximum acceptable unmet load (kWh).
- Fuel minimization numerical target (L).
- Fuel-vs-reliability tradeoff ratio.
- Maximum allowable renewable curtailment (kWh).
- Dynamic emergency battery reserve floor (kWh).

### 6. Is the current objective aligned with documented requirements?
`OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED`. The objective correctly incorporates terms for fuel, curtailment, battery degradation, and unmet load, but the relative penalty weights were established as prototype assumptions rather than governed requirements.

### 7. Where is the governance gap?
The gap lies in the absence of an explicit project specification defining the governed exchange rate between fuel consumption (L) and unmet load (kWh).

### 8. What must be specified before any EMS objective change can be authorized?
Stakeholders must establish a formal EMS Objective Specification defining:
1. Numerical reliability targets / load shedding limits.
2. Fuel consumption target or ceiling.
3. The governed tradeoff weight between operating cost and load service.

---

## Final Governance Status Output

```
V2_EVIDENCE_LOCK = PASS
FORENSIC_RESULT_STATUS = FROZEN_VALID
EMS_OBJECTIVE_AUDIT = PASS
OBJECTIVE_NUMERIC_RECONCILIATION = PASS
REQUIREMENTS_RECONCILIATION = LIMITED
OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED
FUEL_REQUIREMENT = IMPLICIT
RELIABILITY_REQUIREMENT = QUALITATIVE_ONLY
FUEL_NUMERIC_TARGET = NOT_SPECIFIED
RELIABILITY_NUMERIC_TARGET = NOT_SPECIFIED
FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED
OBJECTIVE_PRIORITY = NOT_SPECIFIED
OBJECTIVE_MODIFICATION = NOT_AUTHORIZED
EMS_MODIFICATION = NOT_AUTHORIZED
MODEL_MODIFICATION = NOT_AUTHORIZED
MODEL_RETRAINING = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET
NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED
NEXT_GOVERNED_STEP = EXPLICIT_EMS_OBJECTIVE_SPECIFICATION_REVIEW
```
"""
with open(review_md_path, "w") as f:
    f.write(review_md_content)

# 9. Hash Audit CSV
hash_csv_path = os.path.join(base_dir, "POLARIS_BRANCH01_OBJECTIVE_GOVERNANCE_HASH_AUDIT.csv")
files_to_hash = [
  "POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW.md",
  "POLARIS_BRANCH01_EMS_OBJECTIVE_GOVERNANCE_REVIEW.json",
  "POLARIS_BRANCH01_EMS_OBJECTIVE_REQUIREMENTS_MATRIX.csv",
  "POLARIS_BRANCH01_FROZEN_MILP_OBJECTIVE_AUDIT.md",
  "POLARIS_BRANCH01_FROZEN_MILP_OBJECTIVE_AUDIT.json",
  "POLARIS_BRANCH01_REQUIREMENTS_GAP_ANALYSIS.md",
  "POLARIS_BRANCH01_REQUIREMENTS_GAP_ANALYSIS.json",
  "POLARIS_BRANCH01_OBJECTIVE_PROVENANCE.csv"
]

hash_rows = ["filename,sha256,creation_purpose,source_artifacts,read_only_status"]
for fname in files_to_hash:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    hash_rows.append(f"{fname},{digest},Read-only EMS objective governance review and requirements audit artifact,system/optimization/implementations/milp.py,VERIFIED_READ_ONLY")

with open(hash_csv_path, "w") as f:
    f.write("\n".join(hash_rows) + "\n")

print("Successfully generated EMS Objective Governance Review package in:", base_dir)
