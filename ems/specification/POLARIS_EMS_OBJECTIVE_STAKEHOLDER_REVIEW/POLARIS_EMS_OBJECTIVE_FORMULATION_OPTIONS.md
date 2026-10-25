# POLARIS EMS OBJECTIVE FORMULATION OPTIONS
## Descriptive Technical Analysis for Stakeholder Review

**Document Version**: 1.0.0  
**Governance Status**: DESCRIPTIVE_OPTIONS_ONLY  
**Audit Timestamp**: 2026-09-21T21:56:54Z  
**Authoritative Directory**: `POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/`  

---

> [!IMPORTANT]
> **GOVERNANCE DISCLAIMER**: This document describes mathematical formulation options for the POLARIS Energy Management System (EMS) objective function. **It DOES NOT select, rank, or recommend any option, and DOES NOT imply stakeholder approval of any option.** The choice of objective formulation is a policy decision reserved exclusively for authorized POLARIS stakeholders.

---

### Option A: Lexicographic / Reliability-First Optimization

- **Mathematical Structure**: Solves a sequential series of linear/integer programs:
  1. **Stage 1**: Minimize total unserved critical demand:
     $$\min \sum_{t=1}^{H} P_{\text{unmet},t} \quad \text{subject to physical constraints} \implies P_{\text{unmet}}^{*}$$
  2. **Stage 2**: Minimize total fuel consumption subject to optimal reliability:
     $$\min \sum_{t=1}^{H} \text{Fuel}_t \quad \text{subject to } \sum_{t=1}^{H} P_{\text{unmet},t} \le P_{\text{unmet}}^{*}$$
- **Required Policy Decisions**: Confirmation that critical load service has absolute priority over fuel cost under all operating conditions.
- **Required Numerical Information**: Definition of critical load threshold and allowable flexible loads.
- **Operational Implications**: Guarantees zero load shedding whenever physically feasible, regardless of fuel cost. Eliminates arbitrary soft penalty tuning.

---

### Option B: Reliability-Constrained Fuel Minimization

- **Mathematical Structure**: Formulates critical load service as a hard constraint or bounded Service Level Agreement (SLA) limit, directly minimizing total fuel volume or cost:
  $$\min \sum_{t=1}^{H} \left( f_{\text{base}} u_{\text{diesel},t} + f_{\text{marg}} P_{\text{diesel},t} \right) \Delta t$$
  $$\text{subject to: } P_{\text{served},t} = P_{\text{demand},t} \quad \text{(Hard SLA)}$$
  $$\text{or: } \sum_{t=1}^{H} P_{\text{unmet},t} \le \text{SLA}_{\text{max}} \quad \text{(Bounded SLA)}$$
- **Required Policy Decisions**: Authorization of the maximum allowable unmet load ceiling ($\text{SLA}_{\text{max}}$).
- **Required Numerical Information**: Numerical SLA value (in kWh per horizon or per year).
- **Operational Implications**: Ensures diesel fuel is strictly minimized subject to an explicit, authorized reliability SLA. Returns explicit solver infeasibility if SLA cannot be met.

---

### Option C: Weighted Economic Objective (Current Implementation Structure)

- **Mathematical Structure**: Single scalar objective function combining linear monetary weights for fuel, degradation, startup penalties, and unserved energy:
  $$\min \sum_{t=1}^{H} \left( c_{\text{fuel}} P_{\text{diesel},t} + c_{\text{deg}} P_{\text{bess},t} + c_{\text{curt}} P_{\text{curt},t} + c_{\text{unmet}} P_{\text{unmet},t} + c_{\text{start}} v_{\text{start},t} \right) \Delta t$$
- **Required Policy Decisions**: Explicit stakeholder authorization of all cost coefficients, particularly the penalty ratio $\frac{c_{\text{unmet}}}{c_{\text{fuel}}}$.
- **Required Numerical Information**: Governed monetary valuation of unserved energy ($\$/\text{kWh}$).
- **Operational Implications**: Allows explicit economic trade-offs between fuel expenditure and reliability. Requires careful tuning to avoid unintended load shedding or excessive fuel burn.

---

### Option D: Multi-Objective / Pareto Optimization

- **Mathematical Structure**: Evaluates a vector-valued objective trading off Fuel Consumption ($J_1$) against Unmet Load ($J_2$):
  $$\min \left[ J_1(\mathbf{x}), J_2(\mathbf{x}) \right] = \min \left[ \sum \text{Fuel}_t, \sum P_{\text{unmet},t} \right]$$
- **Required Policy Decisions**: Criteria for selecting operating points along the Pareto frontier (e.g. Normal, High-Reliability, Fuel-Conservation modes).
- **Required Numerical Information**: Operational thresholds defining mode switching boundaries.
- **Operational Implications**: Provides operators and stakeholders with an explicit trade-off curve showing exact fuel cost per kWh of avoided unmet load for every operating regime.

---

### Summary Comparison Table

| Formulation Option | Reliability Handling | Fuel Minimization | Required Governance Input | Operational Characteristic |
| :--- | :--- | :--- | :--- | :--- |
| **Option A: Lexicographic** | Absolute Stage-1 priority | Stage-2 minimization | Critical load definition | Zero load shedding when feasible |
| **Option B: Constrained SLA** | Hard constraint / Bounded SLA | Direct objective minimization | Authorized SLA ceiling ($\text{SLA}_{\text{max}}$) | Explicit fuel minimization within SLA |
| **Option C: Weighted Economic** | Soft penalty weight ($c_{\text{unmet}}$) | Weighted cost term ($c_{\text{fuel}}$) | Authorized penalty exchange rate ratio | Soft trade-off governed by cost weights |
| **Option D: Multi-Objective** | Vector objective term ($J_2$) | Vector objective term ($J_1$) | Operating mode selection policy | Dynamic Pareto trade-off curve |
