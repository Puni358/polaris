# POLARIS EMS — HD-05D-ε Extra-Fuel Tolerance Evidence Audit

**Audit Status**: COMPLETED (READ-ONLY)  
**Governance Scope**: Human Decision HD-05D-ε (Numerical Extra-Fuel Tolerance for Stage 3 Lexicographic Formulation)  
**Target Directory**: [`POLARIS_EMS_HD05D_EPSILON_EVIDENCE_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD05D_EPSILON_EVIDENCE_AUDIT/)  

---

## Executive Summary

This evidence audit establishes whether the POLARIS repository contains an authoritative numerical basis or defensible derivation for the **extra-fuel tolerance $\epsilon$** in the governed Stage-3 lexicographic formulation:

$$\text{Stage 3a: } \min \text{Fuel} \to F^*$$
$$\text{Stage 3b: } \min \text{Battery Cycling} \quad \text{subject to } \quad \text{Fuel} \le F^* + \epsilon \quad \left(\text{or } \text{Fuel} \le (1 + \alpha) F^*\right)$$

### Key Audit Findings

1. **Existence of Numerical $\epsilon$**: **`NOT_ESTABLISHED`**. No numerical value for $\epsilon$ (absolute liters or relative percentage $\alpha$) exists in any code, configuration, schema, or governance document within the repository.
2. **Derivability from Existing Data**: **`NOT_POSSIBLE_WITH_CURRENT_EVIDENCE`**. $\epsilon$ cannot be derived from existing generator parameters, fuel prices, or battery configurations without introducing unauthorized engineering assumptions.
3. **Solver Tolerance Confusion**: **`DISTINCT_CONCEPT`**. [`system/config/optimizer.yaml:L9`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/optimizer.yaml#L9) specifies `solver_tolerance: 1e-5`. This is a numerical solver feasibility tolerance, **not** an operational or policy extra-fuel allowance $\epsilon$.
4. **Fuel Budget Relationship**: **`INSUFFICIENT`**. The seasonal fuel budget policy concept (Decision 08) defines a tracking requirement, but its numerical fuel volume is explicitly classified as `STATION_DATA_REQUIRED / NOT_STAKEHOLDER_AUTHORIZED`. It does not mathematically establish $\epsilon$.
5. **Structural Closure vs. Parameter Resolution**: **`STRUCTURALLY_CLOSED / PARAMETER_OPEN`**. HD-05D is structurally closed as a Lexicographic Subobjective model (Stage 3a $\to F^*$, Stage 3b $\to \min \text{cycling}$ s.t. $\text{fuel} \le F^* + \epsilon$). The numerical value of $\epsilon$ remains a required human governance decision.

---

## 1. Closed Governance Context

The following decisions are **FIXED** and must not be reopened:

- **HD-05A**: Battery degradation/cycling belongs in **Stage 3 — Resource Management**.
- **HD-05B**: During **NORMAL operation**, POLARIS may spend additional diesel fuel to reduce unnecessary battery cycling.
- **HD-05C**: During **EMERGENCY operation**, battery degradation does **NOT** retain equal priority. Critical service and emergency resilience take precedence.
- **HD-05D Structure**: Stage 3 uses the **Lexicographic Subobjective formulation**:
  - Stage 3a: $\min \text{Fuel} \to F^*$
  - Stage 3b: $\min \text{Battery Cycling}$ subject to $\text{Fuel} \le F^* + \epsilon$
- **HD-05D Parameter ($\epsilon$)**: The numerical value of $\epsilon$ is **UNRESOLVED**.

---

## 2. Policy vs. Implementation Audit Matrix

| Element | Repository Status | Source File / Location | Policy Classification | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **Numerical $\epsilon$ Value** | Absent | None | `NOT_ESTABLISHED` | `GOVERNANCE_REQUIRED` |
| **Tolerance Representation** | Unspecified | None | `UNRESOLVED` | `GOVERNANCE_REQUIRED` |
| **`solver_tolerance` (1e-5)** | Present | [`optimizer.yaml:L9`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/optimizer.yaml#L9) | `IMPLEMENTATION_FACT` | Numerical solver tolerance only |
| **Marginal Fuel Rate** | $0.00025\text{ L/Wh}$ | [`diesel.yaml:L6`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L6) | `IMPLEMENTATION_FACT` | Technical generator curve |
| **Idle Fuel Rate** | $5.0\text{ L/h}$ | [`diesel.yaml:L5`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L5) | `IMPLEMENTATION_FACT` | Technical generator curve |
| **Seasonal Fuel Budget** | Conceptual structure only | Policy Decision 08 | `HUMAN_SELECTED_POLICY` | Numerical volume `STATION_DATA_REQUIRED` |
| **Survival Window $T_{\text{required}}$** | Unresolved | HD-03 Evidence Audit | `ABSENT` | `GOVERNANCE_REQUIRED` |
| **Emergency Subordination** | Mode-dependent priority | Policy Decision HD-05C | `CLOSED_POLICY` | $\epsilon$ applies to NORMAL mode only |

---

## 3. Derivation Potential Audit

| Derivation Source | Existing Evidence | Derivability | Required Unauthorized Assumption |
| :--- | :--- | :--- | :--- |
| **A. Fuel Budget** | Structure approved; volume absent | **No** | Requires inventing an unbacked fuel allocation. |
| **B. Fuel Survivability** | Minimum reserve absent | **No** | Requires equating emergency reserve to normal slack. |
| **C. Resupply Window** | $T_{\text{required}}$ absent | **No** | Requires equating 24h MPC horizon to resupply interval. |
| **D. Generator Operating Curve** | Minimum output $10\text{ kW}$, idle $5\text{ L/h}$ | **No** | Requires assuming minimum run step is acceptable slack. |
| **E. Battery Degradation Cost** | $c_{\text{deg}} = \$0.00005/\text{Wh}$ prototype | **No** | Requires assuming prototype cost equals physical trade. |
| **F. Historical EMS Telemetry** | Prototype scalar runs | **No** | Requires promoting prototype artifact to policy. |

---

## 4. Required Audit Classifications

```plain
HD05D_EPSILON_EVIDENCE = NOT_ESTABLISHED
HD05D_EPSILON_NUMERICAL_VALUE = NOT_ESTABLISHED
HD05D_EPSILON_REPRESENTATION = UNRESOLVED
HD05D_EPSILON_POLICY_BASIS = GOVERNANCE_REQUIRED
HD05D_EPSILON_OPERATIONAL_BASIS = ABSENT
HD05D_EPSILON_DERIVATION = NOT_POSSIBLE_WITH_CURRENT_EVIDENCE
HD05D_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
HD05D_EXECUTION_AUTHORIZATION = NOT_GRANTED
```

---

## 5. Final Verdict & Authorization Block

1. **Authoritative Numerical $\epsilon$**: Does not exist in the repository.
2. **Derivability**: Impossible from current repository evidence without unauthorized assumptions.
3. **Tolerance Representation**: Unresolved (neither absolute liters nor percentage fraction is established).
4. **Fuel Budget Sufficiency**: Insufficient; numerical fuel budget is uncalibrated.
5. **Emergency Survivability Sufficiency**: Insufficient; emergency mode suppresses degradation rather than defining normal $\epsilon$.
6. **Historical Behavior**: Prototype runs used a single scalar objective, providing no policy-authorized $\epsilon$.
7. **Missing Input**: Stakeholder decision selecting either a relative fraction $\alpha$ (e.g., $1\%-5\%$) or absolute volume $\epsilon_{\text{abs}}$ in liters per 24h.
8. **Structural Closure Status**: HD-05D structure is **CLOSED**, while parameter $\epsilon$ is **GOVERNANCE_DECISION_REQUIRED**.

```plain
HD05D_EPSILON_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD05D_EPSILON_EXECUTION_AUTHORIZATION=NOT_GRANTED
HD05D_EPSILON_NUMERICAL_VALUE=GOVERNANCE_DECISION_REQUIRED
```
