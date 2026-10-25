# POLARIS EMS — OPTION D MILP OPTIMIZATION COMPATIBILITY AUDIT

## 1. Executive Summary

This document presents the mathematical optimization compatibility audit evaluating whether Option D policy mechanics can be represented within the existing MILP formulation (`LocalMILPEnergyOptimizer` in `system/optimization/implementations/milp.py`).

---

## 2. 10-Item MILP Capability Representation Classification

| # | Option D Mathematical Requirement | MILP Representation Classification | Formulation Mechanics & Constraints |
|---|----------------------------------|------------------------------------|--------------------------------------|
| **1** | **Protected Critical Load Representation** | `REPRESENTABLE WITH ADDITIVE MODEL/SCHEMA CHANGES` | Passed to optimizer via additive `critical_demand_w` vector in `ForecastBundle`. |
| **2** | **Noncritical Load Suppression** | `DIRECTLY REPRESENTABLE` | Set flexible/noncritical load bounds $P_{\text{flex,max}} = 0$ or pass $P_{\text{demand}} = P_{\text{critical}}(t)$. |
| **3** | **Dynamic $P_{\text{critical}}(t)$ Trajectory** | `REPRESENTABLE WITH ADDITIVE MODEL/SCHEMA CHANGES` | Time-indexed vector $P_{\text{critical},j}$ per timestep $j \in \{0 \dots N-1\}$. |
| **4** | **Proportional Critical Shortfall Allocation** | `REPRESENTABLE WITH ADDITIVE MODEL/SCHEMA CHANGES` | Multi-circuit variables $P_{\text{crit},c,j}$ constrained by proportional ratio $r_c = \frac{P_{\text{min},c}}{\sum P_{\text{min}}}$. |
| **5** | **Battery Discharge Restricted to Critical Load** | `DIRECTLY REPRESENTABLE` | Add linear upper bound constraint $P_{\text{dis},j} \le P_{\text{critical},j}$. |
| **6** | **Diesel Support of Critical Demand** | `DIRECTLY REPRESENTABLE` | Existing linear generator variables $P_{\text{diesel},j}$ bounded by $P_{\text{D,min}} \cdot u_j \le P_{\text{diesel},j} \le P_{\text{D,max}} \cdot u_j$. |
| **7** | **Renewable-First Priority** | `DIRECTLY REPRESENTABLE` | Naturally enforced by zero marginal fuel cost and positive renewable curtailment penalty $w_{\text{curt}} > 0$. |
| **8** | **Battery Charging from Diesel Minimum Excess** | `DIRECTLY REPRESENTABLE` | Energy balance equation $P_{\text{chg},j} = P_{\text{solar},j} + P_{\text{wind},j} + P_{\text{diesel},j} - P_{\text{critical},j}$ forces excess into battery up to $P_{\text{chg,max}}$. |
| **9** | **Curtailment of Remaining Excess** | `DIRECTLY REPRESENTABLE` | Slack variable $P_{\text{curt},j} = P_{\text{excess},j} - P_{\text{chg},j}$ absorbs remaining un-storable excess. |
| **10** | **Operator Escalation State** | `REPRESENTABLE WITH ADDITIVE MODEL/SCHEMA CHANGES` | Logged in `DispatchPlan` metadata when solver detects total critical shortfall. |

---

## 3. EMS Objective Hierarchy Compatibility Audit

The audit evaluated Option D against the established 4-stage lexicographic objective hierarchy:
- **Stage 1**: Critical Reliability (Minimize unmet critical load)
- **Stage 2**: Emergency Battery Reserve Target Shortfall
- **Stage 3**: Fuel Consumption Minimization
- **Stage 4**: Renewable Utilization / Curtailment Minimization

### Audit Result: `NO_CONFLICT`
Option D does **NOT** override or conflict with the lexicographic objective hierarchy. Instead, Option D modifies the input demand vector by setting noncritical load to zero and restricting active demand to $P_{\text{critical}}(t)$. The objective function continues to prioritize Stage 1 (Critical Reliability) with maximum penalty weight ($w_{\text{unmet}} = \$10.00/\text{Wh}$), perfectly aligning with life-safety load protection.

Status: `MILP_AUDIT_SEALED`
