# POLARIS EMS GAP19 — REPORTING TERMINOLOGY STANDARD

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `CORRECTION_REQUIRED`  

---

## 1. Executive Summary

This document establishes the mandatory standardized metric definitions and physical constraint reporting rules for all future POLARIS EMS test gates and evaluation artifacts.

Historical reports that conflated "pipeline completion" with "solver optimality" remain preserved as sealed artifacts, but all future reporting MUST adhere to the standards below.

---

## 2. Mandatory Evaluation Metric Definitions

| Metric Identifier | Exact Definition & Reporting Scope | Mandatory Exclusions |
| :--- | :--- | :--- |
| **`CYCLES_ATTEMPTED`** | Total number of MPC receding-horizon loop iterations initiated by the orchestrator (`runner.py`). | Excludes un-started steps. |
| **`CYCLES_OPTIMAL`** | Cycles where HiGHS returned `HighsModelStatus.kOptimal` and a valid dispatch plan satisfying all physical constraints and reserve targets. | Must NOT include infeasible or fallback cycles. |
| **`CYCLES_INFEASIBLE`** | Cycles where HiGHS returned `HighsModelStatus.kInfeasible` (or any non-optimal model status). | Must NOT be reported as optimal or clean steps. |
| **`CYCLES_STATE_ADVANCED`** | Cycles where the Digital Twin successfully executed $k=0$ action and stepped `StationState` to $t+1$. | Excludes cycles where simulator execution failed. |
| **`CYCLES_TERMINATED`** | Cycles where pipeline execution halted prematurely due to an unhandled exception or critical runtime crash. | Excludes governed degraded steps. |
| **`DISPATCH_PLAN_OBJECT_RETURNED`** | Number of optimizer invocations that successfully returned a `DispatchPlan` Python instance (optimal, degraded, or fallback). | Does not imply solver optimality. |
| **`FEASIBLE_DISPATCH_SOLUTION`** | A dispatch plan containing a mathematically and physically valid dispatch meeting all hard physical constraints. | Excludes plans with un-mitigated constraint violations. |

---

## 3. Physical Constraint Reporting Standard

Reports MUST explicitly separate physics engine state validity from solver constraint satisfaction:

1. **`PHYSICAL_BOUNDS_ENFORCED`**: Indicates whether battery SOC bounds ($20\%\dots95\%$), power limits ($50\text{ kW}$), and bus-bar balance equations were enforced by solver formulation and physics simulator (`VERIFIED / NOT_VERIFIED`).
2. **`RESERVE_CONSTRAINTS_SATISFIED`**: Indicates the exact number of cycles where 6-hour EBR lookahead and 24-hour terminal reserve target envelopes were satisfied without $J2$ shortfall or MILP infeasibility (`COUNT / TOTAL`).

---

## 4. Audit Verdict

`REPORTING_TERMINOLOGY = CORRECTION_REQUIRED`

*(All future gate reports must use the disambiguated 7-metric standard).*
