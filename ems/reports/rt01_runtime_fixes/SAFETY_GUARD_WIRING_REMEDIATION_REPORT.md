# POLARIS — Wire Dispatch Safety Guard Into Evaluation and Worker

**Date:** 2026-10-17
**Scope:** Close the single highest-priority blocker identified in
`N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` Section 9.1: `system/safety/reserve_policy_guard.py`
existed but was not wired into `system/evaluation/evaluator.py` or `system/orchestration/worker.py`.
This pass wires it into both, per the project owner's exact scoped protocol, and nothing else.
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist). Nothing was
committed, staged, pushed, or run as a campaign/replay/blind-evaluation in this pass.

---

## 1. Status: COMPLETE (within authorized scope)

The guard is now called from the real evaluation/result path in both target files, using actual
`DispatchPlan` values (never placeholders). `reserve_policy_guard.py` itself was **not modified**
(out of the authorized file set — only "evaluation/orchestration source files and their focused
tests" were in scope). All four numeric policy decisions the guard itself leaves open
(reserve-shortfall ceiling, solar-credit cap, gate authorization, and whether to wire the guard at
all) remain `AUTHORIZATION_REQUIRED` — this pass answers "wire it in", not "what are the
thresholds."

---

## 2. Exact changed files and line ranges

### 2.1 `system/evaluation/evaluator.py` (308 lines, was 157)
- **Line 9:** `from system.safety import reserve_policy_guard`.
- **Lines 94–229** (inside `evaluate_ems_performance`): per-plan dispatch-safety evaluation added
  alongside the pre-existing physical aggregation loop (the original aggregation lines —
  `total_solar_used_wh += s`, etc. — are untouched, same code, same order). For each plan: builds a
  `safety_plan` dict sliced to the same `exec_indices` already used for the physical totals (H1-only
  for closed-loop MPC, full 24h for a standalone plan); converts `battery_soc` from **percent** to
  **Wh** (see unit note in Section 4); calls `reserve_policy_guard.evaluate_dispatch_safety(...)`
  inside a `try/except ReservePolicyViolation`; aggregates `critical_unmet_total_wh`,
  `reserve_shortfall_total_wh`, `hard_soc_violation_any`, `solver_infeasible_step_count`,
  `optimal_but_unsafe_step_count`, and tracks which plans used `unmet_essential` vs. fell back to
  `unmet_load`.
- **Lines 233–281:** resolves the critical-vs-total labeling and builds the `dispatch_safety` dict
  (min_e_wh used, hard-SOC verdict, critical-unmet total + source label, reserve-shortfall total +
  `AUTHORIZATION_REQUIRED` status, `optimal_but_unsafe_step_count`, failure reasons/notes, a
  `proposed_safety_gate_would_pass` flag explicitly marked `safety_gate_formally_authorized: False`).
- **Lines 284–308:** the function's return dict gains `total_unmet_load_kwh` (correctly named alias),
  `unmet_critical_load_kwh_label_warning` (explicit deprecation note), and `dispatch_safety`. The
  pre-existing keys (`total_diesel_fuel_liters`, `unmet_critical_load_kwh`,
  `system_reliability_pct`, `constraint_violations_count`, etc.) are **numerically unchanged** —
  verified by reverting to the original file and confirming byte-identical pre-existing test
  results (Section 5).

### 2.2 `system/orchestration/worker.py` (577 lines, was 401)
- **Line 21:** `from system.safety import reserve_policy_guard`.
- **Lines 99–190:** new method `_evaluate_step_dispatch_safety(self, plan)` — converts the H1
  (executed) action's `battery_soc[0]` from percent to Wh using the same `battery.yaml`
  `capacity_wh`/`min_soc_pct` GAP19 itself reads; calls the guard in a `try/except
  ReservePolicyViolation`; determines `critical_unmet_source` (`unmet_essential` /
  `fallback_total_unmet_load` / `unavailable`); computes `solver_infeasible` and `optimal_but_unsafe`.
- **Lines 211–222** and **245–256:** `integrity_counters` gains six new additive keys
  (`reserve_shortfall_total_wh`, `hard_soc_violation_count`, `solver_infeasible_safety_flagged_count`,
  `optimal_but_unsafe_step_count`, `unmet_critical_load_source_fallback_count`,
  `unmet_critical_load_source_unavailable_count`), both at initialization and backfilled via
  `setdefault` on checkpoint resume (so a resume from an older checkpoint never crashes or drops the
  pre-existing counters).
- **Line ~290:** `step_safety` default (`applicable: False`) set before cell branching, for Cell A
  (SIMPLE_DIESEL_ONLY_BASELINE), which produces no MILP `DispatchPlan`.
- **Line 338:** Cell A2 (`ReactiveHybridA2Optimizer`) path — `step_safety =
  self._evaluate_step_dispatch_safety(plan)` right after the plan is produced.
- **Line 431:** Cell B (GAP19) path — the same call, placed **after** the Gate-02
  infeasibility/relaxation block resolves, so it evaluates the FINAL adopted plan (post-relaxation
  if that occurred), not a discarded infeasible first attempt.
- **Lines ~453–469:** integrity-counter bookkeeping block (only when `step_safety["applicable"]`)
  that **actually increments `integrity_counters["unmet_critical_load_wh"]`** — fixing the
  pre-existing dead-counter bug the N6 report flagged ("declares... but never increments it
  anywhere in the file").
- **Line 483:** `rec["safety"] = step_safety` — persists the per-step finding into
  `trajectory_records.json`.
- **Lines 533–end:** `safety_summary` dict built from the final `integrity_counters`, included both
  in the persisted `trajectory_records.json` and in `execute()`'s returned result dict (previously
  only `cell_id`/`worker_id`/`status`/`completed_cycles`/`cumulative_fuel_l`).

### 2.3 New test files (not modifications to existing tests — none existed for these two files)
- `system/tests/test_evaluator_safety_wiring.py` (228 lines, 12 tests)
- `system/tests/test_worker_safety_wiring.py` (230 lines, 8 tests)

No other file was opened for editing. `system/safety/reserve_policy_guard.py` is byte-identical to
the prior pass's version (confirmed — see Section 5).

---

## 3. Safety behavior: before vs. after

| Scenario | Before this pass | After this pass |
|---|---|---|
| GAP19 returns `OPTIMAL` with nonzero `unmet_essential` | Reported as a clean, successful dispatch; `constraint_violations_count` never increments (GAP19's soft `s_J2` slack absorbs it without infeasibility) | `dispatch_safety.optimal_but_unsafe_step_count` ≥ 1, `critical_unmet_total_wh` > 0 with source `unmet_essential (critical-specific, verified)`, `failure_reasons` populated, `proposed_safety_gate_would_pass = False` |
| GAP19 returns `OPTIMAL` with nonzero `reserve_shortfall` | `j2_objective`/`reserve_shortfall` never read downstream at all | `dispatch_safety.reserve_shortfall_total_wh` reports the measured value; `reserve_shortfall_authorization_status` explicitly says `AUTHORIZATION_REQUIRED` — no invented pass/fail |
| Hard battery SOC floor violated | Never checked outside GAP19's own MILP bounds | Independent out-of-band check (`validate_hard_soc_floor`, called via the guard) flags `hard_soc_violation = True`; the guard's `ReservePolicyViolation` is caught and converted into a visible, structured finding rather than crashing the evaluation/worker loop |
| `unmet_essential` absent from a plan (e.g. produced by a non-GAP19 optimizer) | `unmet_critical_load_kwh` silently computed from `unmet_load` (total), presented as if critical-specific | Still backward-compatible (`unmet_critical_load_kwh` unchanged), but now accompanied by `unmet_critical_load_kwh_label_warning` and `dispatch_safety.critical_unmet_source = "FALLBACK_TO_TOTAL_UNMET_LOAD: ... OVER-COUNTS ..."` |
| `worker.py`'s `integrity_counters["unmet_critical_load_wh"]` | Declared, initialized to `0.0`, **never incremented** (dead counter) | Incremented every applicable step from the real plan's `unmet_essential`/`unmet_load` value |
| Worker's final result dict | `{cell_id, worker_id, status, completed_cycles, cumulative_fuel_l}` only | Adds `safety_summary` (unmet-critical totals, reserve-shortfall totals, hard-SOC/solver-infeasible/optimal-but-unsafe counts, explicit `AUTHORIZATION_REQUIRED` note, `any_safety_finding` flag) — also persisted in `trajectory_records.json`, never reset afterward |
| Arm A_FIX-shaped pattern (lower diesel, higher critical unmet) | Would be reported as a fuel-savings win by `evaluate_ems_performance` alone | `dispatch_safety.optimal_but_unsafe_step_count ≥ 1` and `proposed_safety_gate_would_pass = False` on the candidate even though its diesel total is lower (test: `TestArmAFixShapedRegression`) |

---

## 4. Key design decisions (and why)

1. **Guard itself untouched.** `reserve_policy_guard.py` was deliberately left unmodified — it was
   outside the authorized file set ("evaluation/orchestration source files and their focused
   tests"). All adaptation happens at the call sites.
2. **Unit conversion for hard-SOC check.** `DispatchPlan.battery_soc` is a **percent** (0–100), not
   Wh (confirmed by reading `gap19_highs_native.py` lines 429/440: `soc_pct = (e_next /
   capacity_wh) * 100.0`). `reserve_policy_guard.validate_hard_soc_floor` expects Wh, the same unit
   as `min_e_wh`. Passing the raw percentage directly (e.g. `60.0` vs. a `min_e_wh` of `40000.0`)
   would make the check **always fail**, a silent correctness bug that would have made the guard
   useless if wired in naively. Both call sites convert `(pct / 100.0) * capacity_wh` using the same
   `battery.yaml` `capacity_wh`/`min_soc_pct` GAP19 itself reads — this mirrors, never alters, the
   existing policy.
3. **`ReservePolicyViolation` is caught, not left to propagate.** The guard raises unconditionally on
   a hard-SOC violation by design (a physical constraint, not a policy call). Letting that exception
   propagate out of `evaluate_ems_performance`/`execute()` would crash the entire pipeline/worker run
   with no caller in `runner.py`/`worker_cli.py`/`master.py` catching it (all three are out of this
   pass's authorized scope, so they could not be changed to add a `try/except`). Both call sites
   catch it and convert it into a visible, structured finding (`hard_soc_violation=True`,
   `failure_reasons` populated) — this is reporting the failure, not suppressing it.
4. **Backward compatibility via additive keys, not renames.** `evaluate_ems_performance`'s
   pre-existing keys (`unmet_critical_load_kwh`, `total_diesel_fuel_liters`,
   `constraint_violations_count`, etc.) keep their exact prior values and meaning — confirmed by
   diffing against the unmodified file (Section 5). The known mislabeling
   (`unmet_critical_load_kwh` is actually total, not critical) is **documented via a new
   `unmet_critical_load_kwh_label_warning` field**, not silently fixed under the same key name,
   per protocol item 9 ("clearly document any schema changes"). `worker.py`'s
   `integrity_counters` gains new keys with `setdefault` backfill on checkpoint resume so an
   older checkpoint never crashes or loses its pre-existing counters.
5. **No invented thresholds.** `reserve_shortfall_authorization_wh=None` is passed explicitly at
   both call sites; every output surfaces `"AUTHORIZATION_REQUIRED"` for the ceiling rather than
   silently treating "no ceiling" as "pass." `SAFETY_GATE_REGISTRY`'s `authorized=False` state is
   not changed; `proposed_safety_gate_would_pass`/`safety_gate_formally_authorized: False` make clear
   any gate verdict is advisory only.

---

## 5. Test results (all commands actually executed this session)

| Suite | Command | Result |
|---|---|---|
| New evaluator wiring tests | `python3 -m pytest system/tests/test_evaluator_safety_wiring.py -q` | **12 passed** |
| New worker wiring tests | `python3 -m pytest system/tests/test_worker_safety_wiring.py -q` | **8 passed** |
| Existing guard suite (untouched file) | `python3 -m pytest system/tests/test_reserve_policy_guard.py -q` | **24 passed** (unchanged — confirms the guard itself was not altered) |
| Combined new + guard | `python3 -m pytest system/tests/test_evaluator_safety_wiring.py system/tests/test_worker_safety_wiring.py system/tests/test_reserve_policy_guard.py -q` | **44 passed** |
| Pre-existing targeted evaluator-population test | `python3 -m pytest system/tests/test_offline_runtime.py -q -k test_closed_loop_h1_only_evaluator_population` | **1 passed** |
| Pre-existing short-pipeline smoke tests | `python3 -m pytest system/tests/test_offline_runtime.py -q -k "test_network_isolation or test_c6_c7_c8_execution_status_and_report"` | **2 passed** |
| Full `test_offline_runtime.py` excluding the 168h endurance tests (`-k "not 168h"`) | `python3 -m pytest system/tests/test_offline_runtime.py -q -k "not 168h"` | **28 passed, 3 failed** — see below |

**On the 3 failures (`test_flexible_load_constraints`, `test_flexible_load_no_double_counting`,
`test_per_timestep_conservation_audit`):** these are **pre-existing and unrelated to this
remediation**. All three assert energy-conservation residuals purely between GAP19's raw
`latest_dispatch_plan.json` output and `latest_forecast_bundle.json` — they never call
`evaluate_ems_performance` or reference any new field. I verified this directly: I temporarily
restored the original, pre-remediation `evaluator.py` (the file this pass edited; `worker.py` is not
even in this test's call path — `test_offline_runtime.py` drives `PolarisLocalRunner`
(`runner.py`), not `CampaignWorker`) and re-ran the same three tests — **they failed identically**,
with the exact same residual values (e.g. `5852.500000000004` renewable-availability imbalance at
step 4), before this pass's changes existed. I then restored this pass's `evaluator.py` exactly
(verified byte-identical via `diff`) before continuing. These failures are therefore out of this
task's authorized scope (they concern GAP19/forecast-bundle numerics, a protected file this pass did
not and must not touch) and are flagged here for the project owner, not fixed.

**Not run, per protocol:** the 168h endurance tests in `test_offline_runtime.py`, any full historical
replay, the sealed 2025 blind evaluation, and `tests/test_gap19_highs_native.py` /
`system/tests/test_gap19_ecd_option_d.py` / `system/tests/test_gap19_milp_v2_research.py` (unmodified,
heavy HiGHS-backed suites, no reason to run them against unmodified GAP19 code).

---

## 6. Protected-artifact / governance verification (post-change)

**Protected-file SHA-256 — unchanged, matches the prior report's recorded values exactly:**

| File | SHA-256 |
|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/optimization/implementations/option_d.py` | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` |
| `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` |
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` |

(Recomputed independently this session; all six match `N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md`
Section 8 exactly — none of these files were opened for editing.)

- **`winner: null`:** confirmed unchanged in
  `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json`.
- **`system/safety/reserve_policy_guard.py`:** not modified (confirmed by file inspection — identical
  to the version read at the start of this task).
- **Production defaults:** `runner.py` still defaults `forecast_engine_type="baseline"`;
  `worker.py` still instantiates `GAP19HighsNativeOptimizer()` as the governed optimizer for Cell B;
  no behavior of the optimizer, router, simulator, or runner was changed — only the evaluation/result
  *reporting* layer around their outputs.
- **Pre-existing untracked research artifacts:** all preserved; `git status` shows only
  `system/evaluation/evaluator.py`, `system/orchestration/worker.py` modified and
  `system/tests/test_evaluator_safety_wiring.py`, `system/tests/test_worker_safety_wiring.py`,
  `SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md` newly added. `system/artifacts/*.json` files were
  regenerated (pre-existing behavior of `runner.py` on every pipeline run; not new source).
- No commit, push, dispatch campaign, historical replay, sealed-data access, or live-service call was
  made.

---

## 7. Remaining UNKNOWN / NOT_VERIFIED fields

- `dispatch_safety.critical_unmet_total_wh` / `reserve_shortfall_total_wh` report
  `"UNKNOWN_NOT_VERIFIED"` (a string, not a silent `0.0`) whenever a plan carries neither
  `unmet_essential` nor `unmet_load`, or no plan carries `reserve_shortfall` at all — e.g. plans
  from optimizers that never set these optional fields (confirmed via
  `TestMissingSafetyFieldsStayUnknown` / `TestWorkerMissingReserveShortfallStaysUnknown`).
- `dispatch_safety.critical_unmet_source` always states explicitly whether the number shown is a
  genuine `unmet_essential` measurement or a `FALLBACK_TO_TOTAL_UNMET_LOAD` over-count — never
  presented ambiguously.

## 8. Policy decisions still requiring explicit project-owner authorization (unchanged from the prior report — not resolved by this pass, and not invented here)

1. A numeric reserve-shortfall ceiling (Wh) to pass as `reserve_shortfall_authorization_wh`.
2. A maximum authorized solar-credit fraction for `compute_bounded_solar_credit` (that function was
   not touched or called in this pass — no production code path computes a solar credit).
3. Whether the four `SAFETY_GATE_REGISTRY` proposed gates should become formally authorized
   governance requirements (`proposed_safety_gate_would_pass` is advisory-only output, not a gate).
4. Whether a verified hard-SOC violation or `optimal_but_unsafe` step should actively change
   `execution_status`/pipeline control flow (e.g. force `BLOCKED_INFEASIBLE`-style halting) — this
   pass only makes such findings **visible**, per the protocol's explicit scope ("surface... keep
   findings visible"); changing control flow in `runner.py` (protected) or adding new halting
   behavior was not authorized and was not done.

---

## 9. Next authorized action

The guard is now wired in and its findings are visible end-to-end in both `evaluator.py`'s returned
dict and `worker.py`'s final result / persisted trajectory record. The smallest safe next action is
the project owner reviewing Section 8 above — in particular item 4, whether a verified safety finding
should be allowed to affect `execution_status` or halt a run, since that would require touching
`runner.py` (protected) and is explicitly out of this pass's scope.
