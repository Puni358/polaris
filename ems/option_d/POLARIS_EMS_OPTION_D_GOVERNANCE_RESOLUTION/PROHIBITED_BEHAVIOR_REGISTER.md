# POLARIS EMS — PROHIBITED BEHAVIOR REGISTER FOR OPTION D

## 1. Executive Summary

This register establishes the explicit operational prohibitions governing Option D. Any control logic, runtime implementation, or optimization module that violates these prohibitions is non-compliant with governed policy.

---

## 2. Prohibited Behavior Register

| Prohibition ID | Prohibited Action | Governed Rationale & Boundary Rule |
|----------------|-------------------|------------------------------------|
| **PRH-001** | **Noncritical Battery Discharge** | Battery discharge ($P_{\text{BD}} > 0$) must **NEVER** be used to power noncritical loads or serve general station demand during `UNKNOWN_INVALID`. Discharge is restricted solely to authorized protected critical loads under D2/D3. |
| **PRH-002** | **Diesel-Only-for-Charging** | Diesel generators must **NEVER** be started or operated merely to charge the battery bank. Diesel operation is authorized solely when required to maintain protected critical load under D6. |
| **PRH-003** | **Unapproved Category Priority** | Control algorithms must **NEVER** impose unapproved category priority rankings (e.g. Heating > Water > Comms) during critical load deficits under D4. Power must be proportionally allocated across minimum viable levels unless explicit category hierarchy is authorized. |
| **PRH-004** | **Dynamic Equipment Redefinition** | Optimization algorithms must **NEVER** dynamically re-classify or alter which physical equipment is protected. Equipment membership is strictly fixed by station engineering configuration under D1. |
| **PRH-005** | **Automatic Shutdown on Escalation** | Reaching a D5 escalation boundary must **NEVER** trigger automatic disconnection of protected critical loads. Escalation alerts the operator; electrical support continues as long as physical resources permit under D3/D4. |
| **PRH-006** | **Prototype Parameter Promotion** | Synthetic test parameters (e.g. $72\text{h}$, $30\text{ kW}$, $10\text{ kW}$ min diesel) must **NEVER** be converted into deployment policy or hardcoded production constraints. |
| **PRH-007** | **Operator-Independent Threshold Alteration** | Control software must **NEVER** autonomously alter governed time ($T_{\text{max,degraded}}$) or resource ($SOC_{\text{min}}$, $F_{\text{reserve,min}}$) escalation boundaries without authorized human command. |
| **PRH-008** | **False 100% SOC Assumption** | Software must **NEVER** assume "battery full / charging complete" implies $100\text{ SOC}\%$ if technical charge acceptance, C-rate, or thermal limits prevent further power absorption under D6. |
| **PRH-009** | **Autonomous Noncritical Optimization** | Long-horizon 24-hour MILP optimization (`EnergyOptimizer`) of noncritical loads must **NEVER** execute while ECD status is `UNKNOWN_INVALID`. |
| **PRH-010** | **Unverified Operational State Change** | Control software must **NEVER** autonomously transition out of Option D back to `NORMAL` without valid ECD inputs or authenticated operator override. |

---

## 3. Compliance Enforcement

All future software code reviews, runtime integration tests, and deployment verification audits MUST verify 100% compliance with PRH-001 through PRH-010.

Status: `PROHIBITED_BEHAVIOR_REGISTER_SEALED`
