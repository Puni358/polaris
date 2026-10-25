# POLARIS EMS GAP19 — CYCLE STATUS TERMINOLOGY AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `REPORTING_TERMINOLOGY_CORRECTION_REQUIRED`  

---

## 1. Context & Wording Ambiguity

The multi-scenario evaluation report stated:
> "24/24 Cycles Attempted & Completed"

This phrasing created ambiguity by equating **pipeline completion** (the MPC loop executed 24 steps without crashing) with **solver optimality** (the optimizer successfully found a valid dispatch plan).

---

## 2. Disambiguated Multi-Scenario Cycle Counts

To eliminate all reporting ambiguity across the 96 authorized cycles ($4 \text{ scenarios} \times 24 \text{ cycles}$):

| Granular Cycle Metric | `normal_demo` | `renewable_stress` | `demand_stress` | `battery_stress` | Total Aggregate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`CYCLES_ATTEMPTED`** | 24 | 24 | 24 | 24 | **96** |
| **`CYCLES_OPTIMAL`** | 24 | 24 | 4 | 0 | **52** |
| **`CYCLES_INFEASIBLE`** | 0 | 0 | 20 | 24 | **44** |
| **`CYCLES_STATE_ADVANCED`** | 24 | 24 | 24 | 24 | **96** |
| **`CYCLES_TERMINATED`** | 0 | 0 | 0 | 0 | **0** |
| **`CYCLES_WITH_VALID_DISPATCH_PLAN`** | 24 | 24 | 24 | 24 | **96** *(20 fallback zero-dispatch)* |

---

## 3. Standardized Terminology Definitions

1. **`CYCLES_ATTEMPTED`**: Total MPC loop iterations initiated by `runner.py`.
2. **`CYCLES_OPTIMAL`**: Cycles where HiGHS returned `HighsModelStatus.kOptimal` and a valid dispatch plan satisfying all constraints and reserves.
3. **`CYCLES_INFEASIBLE`**: Cycles where HiGHS returned `HighsModelStatus.kInfeasible` due to constraint bounds.
4. **`CYCLES_STATE_ADVANCED`**: Cycles where the Digital Twin successfully executed $k=0$ action and stepped `StationState` to $t+1$.
5. **`CYCLES_TERMINATED`**: Cycles where execution halted prematurely due to an unhandled exception or critical error.

---

## 4. Audit Verdict

`CYCLE_STATUS_TERMINOLOGY = REPORTING_TERMINOLOGY_CORRECTION_REQUIRED`

*(Future reports must separate `CYCLES_OPTIMAL` from `CYCLES_INFEASIBLE` and avoid using "completed" as a synonym for "optimal").*
