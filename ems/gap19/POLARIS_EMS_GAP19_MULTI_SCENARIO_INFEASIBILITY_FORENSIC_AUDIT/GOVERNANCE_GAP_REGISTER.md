# POLARIS EMS GAP19 — GOVERNANCE GAP REGISTER

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `GOVERNANCE_REQUIRED`  

---

## 1. Executive Summary

This register formally documents the missing policy and technical governance decisions identified during the multi-scenario infeasibility forensic audit. These governance gaps must be resolved before proceeding to subsequent implementation gates.

---

## 2. Register of Required Governance Decisions

| Ref ID | Gap Name | Current Implementation Behavior | Required Governance Resolution |
| :--- | :--- | :--- | :--- |
| **GAP-INF-01** | **$s_{\text{J2}}$ Slack Upper Bound Policy** | Capped at `capacity_wh` ($200\text{ kWh}$) as an ad-hoc implementation choice. | Formally authorize unbounding $s_{\text{J2}}$ (`ub = infinity`) so that reserve deficits are reported as soft $J2$ objective values without causing MILP solver infeasibility. |
| **GAP-INF-02** | **Runtime Infeasibility Fallback Policy** | `runner.py` executes 100% load shedding (`GOVERNED_ZERO_DISPATCH`), turning off diesel and renewables. | Formally define fallback dispatch rules (e.g., forced diesel operation to cover load, or ECD/Option D mode activation) when solver infeasibility occurs. |
| **GAP-INF-03** | **Feasible Operating Space Definition** | Scenarios can inject 6-hour critical load profiles ($>53.67\text{ kW}$) that exceed battery capacity bounds. | Establish formal station operating envelope boundaries for NORMAL mode relative to installed battery capacity ($C_{\text{bat}}$) and diesel capacity ($P_{\text{diesel\_max}}$). |
| **GAP-INF-04** | **Reporting Metric Standardization** | Evaluation reports combine pipeline completion with solver optimality (`24/24 completed`). | Mandate distinct reporting fields (`CYCLES_OPTIMAL`, `CYCLES_INFEASIBLE`, `CYCLES_STATE_ADVANCED`). |
| **GAP-INF-05** | **Emergency Load Shedding & ECD Activation** | ECD and Option D emergency modes are not activated during reserve infeasibility. | Define explicit triggering rules for when reserve deficits ($J2 > 0$) or solver infeasibility require transitioning from NORMAL mode to EMERGENCY / ECD mode. |

---

## 3. Boundary Statement

**NO DECISIONS IMPLEMENTED**: The agent has NOT made any of these governance decisions or modified code/configuration. All governance items are logged for human authority review.
