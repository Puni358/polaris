# POLARIS EMS — HD-05D-ε Governance Gap Report

**Audit Objective**: Identify the minimum unresolved governance decisions required to close the extra-fuel tolerance parameter $\epsilon$.

---

## 1. Closed vs. Open Decision Matrix

| Item | Decision ID | Status | Explanation |
| :--- | :--- | :--- | :--- |
| **Stage-3 Placement** | **HD-05A** | **CLOSED** | Battery degradation belongs in Stage 3 — Resource Management. |
| **Normal Extra Diesel** | **HD-05B** | **CLOSED** | POLARIS may spend extra diesel to reduce battery cycling during normal mode. |
| **Emergency Priority** | **HD-05C** | **CLOSED** | Battery degradation is subordinate to critical service during emergency mode. |
| **Stage-3 Structure** | **HD-05D (Structure)** | **CLOSED** | Lexicographic subobjectives: Stage 3a $\to \min \text{fuel} \to F^*$; Stage 3b $\to \min \text{cycling}$ s.t. $\text{fuel} \le F^* + \epsilon$. |
| **Tolerance Parameter** | **HD-05D-ε** | **OPEN** | **Governance Decision Required.** The numerical value and representation of $\epsilon$ are unresolved. |

---

## 2. Unresolved Governance Gaps for HD-05D-ε

### GAP-1: Representation Selection
- **Question**: Should the extra-fuel tolerance be represented as a **relative percentage fraction $\alpha$** ($\text{fuel} \le (1+\alpha) F^*$) or as an **absolute volume $\epsilon_{\text{abs}}$ in liters** ($\text{fuel} \le F^* + \epsilon_{\text{abs}}$)?
- **Impact**: Determines optimizer constraint formulation in Stage 3b.

### GAP-2: Numerical Value Governance
- **Question**: What exact numerical value is authorized for the selected representation?
  - If Relative: Authorize $\alpha \in [0.01, 0.05]$ ($1\% - 5\%$).
  - If Absolute: Authorize $\epsilon_{\text{abs}} \in [0.5, 5.0]\text{ Liters}$ per 24h horizon.
- **Impact**: Provides the required quantitative threshold for solver execution.

### GAP-3: Operating Mode Scoping
- **Question**: Confirm that $\epsilon$ applies exclusively during **NORMAL operation** and is automatically disabled ($\epsilon = 0$ or Stage 3b omitted) when the Emergency Mode Detector signals **EMERGENCY operation**.
- **Impact**: Enforces policy decision HD-05C.

---

## 3. Implementation Authorization Block

```plain
HD05D_EPSILON_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD05D_EPSILON_EXECUTION_AUTHORIZATION=NOT_GRANTED
HD05D_EPSILON_NUMERICAL_VALUE=GOVERNANCE_DECISION_REQUIRED
```
