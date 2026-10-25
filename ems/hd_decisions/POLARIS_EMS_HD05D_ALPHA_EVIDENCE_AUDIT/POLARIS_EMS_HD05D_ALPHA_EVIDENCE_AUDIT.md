# POLARIS EMS — HD-05D-α Relative Extra-Fuel Tolerance Evidence Audit

**Audit Status**: COMPLETED (READ-ONLY)  
**Governance Scope**: Human Decision HD-05D-α (Numerical Relative Extra-Fuel Tolerance for Stage 3 Lexicographic Objective)  
**Target Directory**: [`POLARIS_EMS_HD05D_ALPHA_EVIDENCE_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD05D_ALPHA_EVIDENCE_AUDIT/)  

---

## Executive Summary

This evidence audit establishes whether the POLARIS repository contains sufficient scientific, operational, or stakeholder evidence to derive or justify a **numerical relative extra-fuel tolerance $\alpha$** for the governed Stage-3 lexicographic formulation:

$$\text{Stage 3a: } \min \text{Fuel} \to F^*$$
$$\text{Stage 3b: } \min \text{Battery Cycling} \quad \text{subject to } \quad F_{\text{diesel}} \le (1 + \alpha) F^*$$

### Key Audit Findings

1. **Existence of Numerical $\alpha$**: **`NOT_ESTABLISHED`**. No numerical value for relative fuel tolerance $\alpha$ (e.g., $1\%, 2\%, 5\%$) exists anywhere in repository code, configurations, schemas, or governance records.
2. **Derivability from Existing Data**: **`NOT_POSSIBLE_WITH_CURRENT_EVIDENCE`**. $\alpha$ cannot be mathematically derived from existing generator curves, fuel prices, battery settings, or historical runs without introducing unauthorized engineering assumptions.
3. **Qualitative Policy vs. Quantitative Parameter**: **`QUALITATIVE_ONLY`**. HD-05B establishes the qualitative policy ("extra diesel may be spent to reduce battery cycling"), but explicitly leaves the quantitative parameter $\alpha$ unresolved (`GOVERNANCE_DECISION_REQUIRED`).
4. **Zero-Fuel Edge Case ($F^* = 0$)**: **`PRESENT`**. On days when minimum diesel consumption $F^* = 0$ (100% solar/wind coverage), $(1+\alpha) F^* = 0$. The relative formulation naturally permits **zero extra diesel** when no diesel is strictly needed.
5. **Structural Closure Status**: **`STRUCTURALLY_CLOSED / PARAMETER_OPEN`**. The mathematical formulation ($F_{\text{diesel}} \le (1+\alpha)F^*$) is **CLOSED**, while the numerical parameter $\alpha$ remains **GOVERNANCE_DECISION_REQUIRED**.

---

## 1. Closed Governance Context

The following decisions are **FIXED** and must not be reopened:

- **HD-05A**: Battery degradation/cycling belongs in **Stage 3 — Resource Management**.
- **HD-05B**: During **NORMAL operation**, POLARIS may spend additional diesel fuel to reduce unnecessary battery cycling.
- **HD-05C**: During **EMERGENCY operation**, battery degradation does **NOT** retain equal priority. Critical service and emergency resilience take precedence.
- **HD-05D Structure**: Stage 3 uses the **Lexicographic Subobjective formulation**:
  - Stage 3a: $\min \text{Fuel} \to F^*$
  - Stage 3b: $\min \text{Battery Cycling}$ subject to $F_{\text{diesel}} \le (1 + \alpha) F^*$
- **HD-05D-ε Representation**: **RELATIVE** dimensionless fraction $\alpha$. (Relative representation choice is **CLOSED**).

---

## 2. Policy vs. Implementation Audit Matrix

| Element | Repository Status | Location / Reference | Classification | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Numerical $\alpha$ Value** | Absent | None | `NOT_ESTABLISHED` | `GOVERNANCE_REQUIRED` |
| **Qualitative Permission** | Present | Policy Decision HD-05B | `CLOSED_POLICY` | Extra diesel allowed in normal mode |
| **Seasonal Fuel Budget** | Conceptual structure only | Policy Decision D08 | `HUMAN_SELECTED_POLICY` | Numerical volume `STATION_DATA_REQUIRED` |
| **Survival Window $T_{\text{required}}$** | Unresolved | HD-03 Evidence Audit | `ABSENT` | `GOVERNANCE_REQUIRED` |
| **Battery Preservation Cap** | Absent | None | `NOT_ESTABLISHED` | No quantitative throughput cap |
| **Ridge Hyperparameter `alpha`** | Present ($1.0$) | [`test_model_reproducibility.py:L96`](file:///home/punith-bs/01polaris%20%28Copy%29/system/tests/test_model_reproducibility_governance.py#L96) | `UNRELATED` | Machine learning test hyperparameter only |
| **Zero-Fuel Edge Case ($F^*=0$)** | Present | Mathematical identity | `MATHEMATICAL_FACT` | $(1+\alpha)0 = 0$; forces 0 extra diesel |

---

## 3. Derivation Pathway Matrix

| Derivation Pathway | Available Evidence | Derivability | Missing Input / Assumption |
| :--- | :--- | :--- | :--- |
| **A. Fuel Budget (D08)** | Structure approved; volume absent | **No** | Requires inventing an unbacked fuel allocation. |
| **B. Resupply Interval (HD-03)** | $T_{\text{required}}$ absent | **No** | Requires assuming resupply period equals 24h MPC horizon. |
| **C. Fuel Survivability** | Minimum reserve absent | **No** | Requires equating emergency reserve to normal slack. |
| **D. Generator Physics** | Idle $5\text{ L/h}$, min $10\text{ kW}$ | **No** | Requires assuming min generator run is acceptable $\alpha$. |
| **E. Battery Preservation Target** | $c_{\text{deg}} = \$0.00005/\text{Wh}$ prototype | **No** | Requires promoting prototype regularizer to policy. |
| **F. Historical EMS Telemetry** | Scalar MILP runs | **No** | Requires converting composite cost weights into $\alpha$. |
| **G. Stakeholder Governance** | HD-05B qualitative decision | **No** | Qualitative permission does not specify a percentage. |

---

## 4. Required Audit Classifications

```plain
HD05D_ALPHA_EVIDENCE = NOT_ESTABLISHED
HD05D_ALPHA_NUMERICAL_VALUE = NOT_ESTABLISHED
HD05D_ALPHA_POLICY_BASIS = GOVERNANCE_REQUIRED
HD05D_ALPHA_OPERATIONAL_BASIS = ABSENT
HD05D_ALPHA_DERIVATION = NOT_POSSIBLE_WITH_CURRENT_EVIDENCE
HD05D_ALPHA_ZERO_FUEL_EDGE_CASE = PRESENT
HD05D_ALPHA_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
HD05D_ALPHA_EXECUTION_AUTHORIZATION = NOT_GRANTED
```

---

## 5. Final Verdict & Authorization Block

1. **Authoritative Numerical $\alpha$**: Does not exist in the repository.
2. **Derivability**: Impossible from current repository evidence without unauthorized assumptions.
3. **Fuel Budget Constrains $\alpha$**: Insufficient; numerical fuel budget is uncalibrated (`STATION_DATA_REQUIRED`).
4. **Resupply/Survivability Constrains $\alpha$**: Insufficient; $T_{\text{required}}$ is unresolved.
5. **Battery Preservation Constrains $\alpha$**: Insufficient; no quantitative throughput target exists.
6. **Stakeholder Governance**: HD-05B provides qualitative permission only, not a quantitative percentage.
7. **Historical Experiments**: Prototype scalar runs do not authorize a relative lexicographic percentage $\alpha$.
8. **Scientific Derivation**: None available without inventing numbers.
9. **Missing Input**: Stakeholder decision selecting the numerical percentage $\alpha$ (e.g., $\alpha = 0.02$).
10. **Structural Closure Status**: HD-05D structure is **CLOSED**, while parameter $\alpha$ is **GOVERNANCE_DECISION_REQUIRED**.

```plain
HD05D_ALPHA_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD05D_ALPHA_EXECUTION_AUTHORIZATION=NOT_GRANTED
HD05D_ALPHA_NUMERICAL_VALUE=GOVERNANCE_DECISION_REQUIRED
```
