# POLARIS EMS — HD-05D Fuel ↔ Battery-Degradation Valuation Evidence Audit

**Audit Status**: COMPLETED (READ-ONLY)  
**Governance Scope**: Human Decision HD-05D (Numerical Fuel ↔ Degradation Tradeoff)  
**Target Directory**: [`POLARIS_EMS_HD05D_FUEL_DEGRADATION_VALUATION_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD05D_FUEL_DEGRADATION_VALUATION_AUDIT/)  

---

## Executive Summary

This evidence audit establishes whether the POLARIS repository contains sufficient scientific, economic, or stakeholder evidence to determine a numerical exchange coefficient between **diesel fuel consumption** and **battery cycling/degradation** for Stage 3 resource management.

### Key Audit Findings

1. **`c_deg` Economic Meaning**: **`HEURISTIC_CYCLING_PENALTY` / `UNCALIBRATED`**. The existing $c_{\text{deg}} = \$0.00005/\text{Wh}$ ($\$0.05/\text{kWh}$) is an uncalibrated mathematical regularizer used in the prototype MILP objective (`system/config/battery.yaml:L11`, `system/optimization/implementations/milp.py:L33`). It has no documented physical aging or monetary battery replacement cost calibration in the repository.
2. **Fuel Price Status**: **`IMPLEMENTATION_ONLY` / `PROTOTYPE_ASSUMPTION`**. The existing fuel price of $\$2.50/\text{L}$ (`system/config/diesel.yaml:L7`) is explicitly labeled `status_label: "PROTOTYPE_ASSUMPTION"` (`diesel.yaml:L2`). It is an unverified simulation default, not a policy-authorized economic valuation of diesel for operational decision-making.
3. **Numerical Tradeoff Justifications**: **`NOT_ESTABLISHED`**. Combining $c_{\text{deg}}$ ($\$0.00005/\text{Wh}$) and fuel price ($\$2.50/\text{L}$) yields a prototype marginal exchange ratio of $12.5\text{ Wh/Wh}$ or $0.02\text{ L/kWh}$ throughput. However, because both constituent numbers are prototype assumptions without empirical calibration or policy authorization, this tradeoff ratio is scientifically and governance-wise arbitrary.
4. **HD-05B Implementation Compatibility**: **`COMPATIBLE_WITHOUT_UNSUPPORTED_VALUATION`**. HD-05B ("extra diesel may be used to reduce unnecessary battery cycling") can be mathematically expressed via alternative frameworks (e.g., Lexicographic Subobjectives or Throughput Constraints/Budgets) without inventing an unsupported monetary conversion rate.

---

## 1. Closed Governance Context

The following human decisions are **FIXED** and must not be reopened:

- **HD-05A**: Battery degradation/cycling belongs in **Stage 3 — Resource Management**.
- **HD-05B**: During **NORMAL operation**, POLARIS may spend additional diesel fuel to reduce unnecessary battery cycling.
- **HD-05C**: During **EMERGENCY operation**, battery degradation does **NOT** retain equal priority. Critical service and emergency resilience take precedence.
- **HD-05D**: The **numerical fuel ↔ degradation tradeoff** remains **UNRESOLVED**.

---

## 2. Policy vs. Implementation Audit Matrix

| Item | Current Implementation | Scientific Basis | Policy Status | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **`c_deg` Value** | $\$0.00005/\text{Wh}$ ($\$0.05/\text{kWh}$) | Heuristic regularizer | `PROTOTYPE_ASSUMPTION` | `UNAUTHORIZED` |
| **Battery Aging Model** | Linear throughput proxy | Uncalibrated | `NOT_ESTABLISHED` | `LEVEL 3 — ABSENT` |
| **Fuel Price** | $\$2.50/\text{L}$ | Default simulation constant | `PROTOTYPE_ASSUMPTION` | `IMPLEMENTATION_ONLY` |
| **Marginal Fuel Rate** | $0.00025\text{ L/Wh}$ ($0.25\text{ L/kWh}$) | Technical generator curve | `IMPLEMENTATION_FACT` | `TECHNICAL_PARAM` |
| **Base Fuel Rate** | $5.0\text{ L/h}$ idle fuel | Technical generator curve | `IMPLEMENTATION_FACT` | `TECHNICAL_PARAM` |
| **Battery Replacement Cost** | Absent | None in repo | `NOT_ESTABLISHED` | `MISSING` |
| **Battery Lifetime / EFC** | Absent | None in repo | `NOT_ESTABLISHED` | `MISSING` |
| **Fuel ↔ Degradation Ratio** | $12.5\text{ Wh/Wh}$ (marginal) | Derived from 2 prototype assumptions | `UNFOUNDED` | `GOVERNANCE_GAP` |
| **Stage-3 Placement** | Embedded in composite scalar | Objective hierarchy approved | `DECIDED (HD-05A)` | `CLOSED` |
| **Normal Extra Diesel** | Permitted | Policy approved | `DECIDED (HD-05B)` | `CLOSED` |
| **Emergency Subordination** | Subordinate to critical service | Policy approved | `DECIDED (HD-05C)` | `CLOSED` |

---

## 3. Audit of Existing $c_{\text{deg}}$ and Fuel Parameters

### 3.1 Degradation Parameter $c_{\text{deg}}$
- **Source**: [`system/config/battery.yaml:L11`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) (`deg_penalty_per_wh: 0.00005`), [`milp.py:L33`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L33) (`deg_penalty = float(bat_cfg.get("deg_penalty_per_wh", 0.00005))`).
- **Units**: $\$ / \text{Wh}$ ($0.05 \ \$/\text{kWh}$).
- **Comment in Code**: `# Cycling penalty`.
- **Classification**: **`HEURISTIC_CYCLING_PENALTY`**. The repository contains zero evidence linking $c_{\text{deg}}$ to battery replacement cost, capital depreciation, levelized cost of storage (LCOS), or chemistry-specific cell wear curves.

### 3.2 Fuel Price Parameter
- **Source**: [`system/config/diesel.yaml:L7`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L7) (`fuel_cost_per_l: 2.50`), [`milp.py:L44`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L44) (`fuel_cost_per_l = float(diesel_cfg.get("fuel_cost_per_l", 2.50))`).
- **Units**: $\$ / \text{L}$.
- **Status Label**: [`system/config/diesel.yaml:L2`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L2) (`status_label: "PROTOTYPE_ASSUMPTION"`).
- **Classification**: **`IMPLEMENTATION_ONLY`**. There is no stakeholder governance record approving $\$2.50/\text{L}$ as an authorized operational valuation of diesel.

---

## 4. Evaluation of Conceptual Stage-3 Formulations

| Option | Formulation | Required Evidence / Governance | Technical Compatibility | Major Advantage / Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Option A: Monetary Stage 3** | $J_3 = \text{fuel\_cost}(\$) + \text{deg\_cost}(\$)$ | Authorized $\$/\text{L}$ fuel price AND authorized $\$/\text{Wh}$ degradation value | High (Supported by MILP/HiGHS) | **Advantage**: Single monetary metric.<br>**Risk**: Requires double-governing uncalibrated costs. |
| **Option B: Liter-Based Tradeoff** | $J_3 = \text{fuel\_liters} + \lambda_{\text{deg}} \cdot \text{throughput\_Wh}$ | Derived/governed exchange factor $\lambda_{\text{deg}} \ [\text{L/\text{Wh}}]$ | High (Supported by MILP/HiGHS) | **Advantage**: Directly minimizes physical liters.<br>**Risk**: Requires governing $\lambda_{\text{deg}}$ directly. |
| **Option C: Constrained Cycling** | $\min \text{fuel\_liters}$ s.t. $\text{cycling} \le \text{Budget}$ | Governed maximum throughput budget $B_{\text{deg}} \ [\text{Wh}]$ per horizon | High (Supported by MILP/HiGHS) | **Advantage**: No monetary tradeoff required.<br>**Risk**: Hard cap may cause infeasibility if too strict. |
| **Option D: Lexicographic Subobjectives** | Stage 3a: $\min \text{fuel\_liters}$<br>Stage 3b: $\min \text{cycling}$ s.t. $\text{fuel} \le (1+\epsilon)\text{fuel}^*$ | Governed tolerance fraction $\epsilon$ (e.g. $1\%-5\%$) | High (Supported by HiGHS native lexicographic) | **Advantage**: Directly expresses HD-05B ("extra diesel for less cycling").<br>**Risk**: Requires 2-stage solve in Stage 3. |

---

## 5. Required Audit Classifications

```plain
HD05D_ECONOMIC_TRADEOFF = NOT_ESTABLISHED
HD05D_CDEG_POLICY_VALIDITY = NOT_ESTABLISHED
HD05D_FUEL_VALUE = IMPLEMENTATION_ONLY
HD05D_BATTERY_VALUE = NOT_ESTABLISHED
HD05D_COMMON_UNIT_FORMULATION = REQUIRES_GOVERNANCE
HD05D_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
HD05D_EXECUTION_AUTHORIZATION = NOT_GRANTED
```

---

## 6. Final Verdict & Authorization Block

1. **Economic meaning of $c_{\text{deg}}$**: $c_{\text{deg}} = \$0.00005/\text{Wh}$ is an uncalibrated heuristic regularizer, not an economic replacement cost.
2. **Scientific/Economic Calibration**: None. Tagged `PROTOTYPE_ASSUMPTION` in repository configuration.
3. **Fuel Price Status**: Implementation parameter only (`status_label: "PROTOTYPE_ASSUMPTION"`), not a policy-authorized value.
4. **Defensible Tradeoff Derivation**: Impossible from current evidence alone.
5. **Missing Evidence**: Authoritative fuel valuation, physical/economic battery aging calibration, and governed Stage-3 formulation structure.
6. **HD-05B Feasibility**: Fully achievable via Lexicographic Subobjectives (Option D) or Cycling Budgets (Option C) without arbitrary numerical values.
7. **Smallest Governance Decision Needed**: Select Stage-3 mathematical structure (Option A, B, C, or D) and govern its weighting parameter or tolerance threshold.

```plain
HD05D_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD05D_EXECUTION_AUTHORIZATION=NOT_GRANTED
HD05D_NUMERICAL_TRADEOFF=GOVERNANCE_DECISION_REQUIRED
HD05D_BATTERY_AGING_ECONOMIC_VALUE=NOT_ESTABLISHED_UNLESS_EVIDENCE_FOUND
```
