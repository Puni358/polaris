# Compute Budget (FROZEN 2026-10-11 with the configuration)

**Status (M9, 2026-10-11):** BUD is RESOLVED BY DELEGATED TECHNICAL AUTHORITY at 14,760 with no increase (project lead's provisional M5 maximum, verified against the runner). Earlier status: provisionally approved (DECISIONS_LOG `BUD`, CONDITIONALLY APPROVED). The derived count from the actual runner now **reconciles** with it (below). It is **frozen** with the configuration (2026-10-11, after D8 passed in the device venv); execution still needs the project lead's signed `solve_ceiling`. No solves were performed during preparation: the budget was derived from code and checked with a solver-free audit and with tests where every solver entry point raises if called.

## Accounting unit

One **solve** is one call to `PlannerCFV1Optimizer.optimize()`. That call runs `highspy.Highs.run()` exactly once (`research_numerical_extractor_planner_cf_v1.py:344-367`, one `h.run()` per call, with `blend_multi_objectives=False`).

Inside that one `run()`, HiGHS handles the five priority levels J1 > J_NC > J2 > J3 > J4 (`:85`) as a lexicographic sequence. That can mean up to 5 internal MILP sub-solves per call. The budget counts calls, not internal sub-solves. Counted as internal sub-solves, the maximum would be 5 × 14,760 = 73,800.

## Derivation from the runner (`scripts/run_three_arm_2024.py`)

| Level | Count | Where in the code |
|---|---|---|
| Arms | 5: PC-Control, A, A_FIX, B, C | `ARM_CONFIGS`; `execute()` loops `for arm in ARMS` |
| Origins per arm | 123 (2024-05-01 … 2024-08-31, consecutive days at 00:00, checked by `evaluation_origins`) | `execute()` loops over `evaluation_origins(...)` |
| Steps per origin | 24 | `run_origin`: `for step in range(STEPS_PER_ORIGIN)`, with `STEPS_PER_ORIGIN = 24` |
| `optimize()` calls per step | 1 | the only `optimize(` call site in `run_origin` |
| `Highs.run()` per `optimize()` | 1 | Planner-CF v1 `:344-367` |
| Retries | 0 | a non-OPTIMAL/FEASIBLE status raises `ArmInvalid`; `execute()` stops at the first failure |

| Arm | Origins | Steps | `optimize()` = `Highs.run()` calls |
|---|---|---|---|
| PC-Control | 123 | 24 | 2,952 |
| A (`LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT`) | 123 | 24 | 2,952 |
| A_FIX (diagnostic) | 123 | 24 | 2,952 |
| B (perfect solar, NONCAUSAL) | 123 | 24 | 2,952 |
| C (calibrated point + lower-bound reserve) | 123 | 24 | 2,952 |
| **Total (hard maximum)** | | | **14,760** |

**Solver-free audit:** `run_three_arm_2024.py --repo . --audit-budget` prints this derivation and `"reconciles": true` against `config/EXPERIMENT_CONFIG.json` `budget` (per arm 2,952, total 14,760). It constructs no forecaster, optimizer or solver. The output is in `reports/PREP_CHECKS_OUTPUT.txt`.

**Tests backing the count** (`tests/test_runner_three_arm.py`):
- An AST check finds exactly one `optimize(` call site in the orchestration (in `run_origin`, inside the single `for step in range(STEPS_PER_ORIGIN)` loop), plus the budget wrapper's delegation.
- Driving `run_origin` with a fake optimizer gives exactly 24 calls per origin.
- The audit gives 2,952 per arm and 14,760 total, and a changed ceiling makes preflight fail.

## Enforcement

- Every `optimize()` goes through `BudgetedOptimizer`, which charges `SolveBudget` **before** the inner call. It raises `BudgetExceeded` above 2,952 for any arm or 14,760 in total. The arm is then INVALID and the run FAILED.
- Preflight fails if the configured ceilings differ from the derived count, if `retries ≠ 0`, or if the repeat check or the Rule D sub-arm are marked included.
- The execution authorization must state `solve_ceiling = 14760`, or preflight fails.
- One worker, one attempt, no background jobs.

## Items that are not solves (0, listed so nothing is hidden)

- **Arm C calibration** (`calibrate_arm_c.py`): γ̂ grid search and quantiles are arithmetic only. It is still real-data calibration, so it needs its own signed authorization and has **not** been run.
- **Gates and statistics** (`gates_three_arm.py`, `planner_cf_statistics.py`): no solver. The D6 stationary bootstrap (10,000 resamples per arm for ΔU, plus the secondary Δfuel CI) is NumPy arithmetic only and adds 0 solver calls.
- **Preflight**: no solver.
- **Tests:** no solver. `highspy.Highs`, the runner's planner loader and `PlannerCFV1Optimizer.optimize` are replaced by mocks that raise if called (`tests/conftest.py`). A test confirms that the real optimizer raises when called under the mock.

## Excluded from the ceiling

- **The old runner's "G7 repeat"** (re-running PC-Control on origin 1, +24): not implemented in this runner. Adding it would make the total 14,784 and needs renewed approval.
- **Optional A + Rule D sub-arm** (+2,952): not implemented. Rule D is OFF in every arm, and the runner has no Rule D code path.

## Rules

- 14,760 is a hard maximum. Unused budget is not permission to add runs, retries or arms.
- Any optimizer failure makes the arm INVALID, and the remaining budget is not used to repair it. Partial output is written only as `PARTIAL_HOURLY_TELEMETRY_INVALID.csv` and is never evaluated.
