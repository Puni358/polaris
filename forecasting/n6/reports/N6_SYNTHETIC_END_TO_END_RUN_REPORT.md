# POLARIS — Synthetic End-to-End Run: Execution Report (Not Governance)

**Date:** 2026-10-18
**Nature of this document:** Execution report. A new, thin CLI entry point was built and **actually run** against the repository's existing, previously-validated single-origin pipeline. This document reports what happened, honestly, including what is still blocked. It is not a governance/decision document and does not touch `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (out of scope for this pass, per the governing directive).

---

## 1. Exact command and input

```bash
cd "/home/punith-bs/01polaris (Copy)"
.venv/bin/python3 system/scripts/run_synthetic_critical_load_scenario.py --critical-load-kw 11.6
```

- **One required input:** `--critical-load-kw` (float, kW). This run used `11.6` (the same magnitude as register item `CL-01`, entered here as a **synthetic, user-supplied scenario parameter for this run only** — not as a claim that CL-01's research-scoped value has been promoted to any operational use).
- Optional: `--steps` (default 24, max 24 — the fixture's future-ground-truth horizon), `--output` (default: a JSON report next to the script).
- Input validation enforced before any run starts: must be a finite number, `> 0.0`, and `<= 500.0` kW (a generous sanity bound against unit-entry errors, e.g. typing watts instead of kW). Verified: `0`, `-5`, and `999999` are all rejected with a clear message before touching any code path; a missing `--critical-load-kw` is rejected by `argparse` as a required argument.

---

## 2. What was built, and why there

**New file (not protected, not touched before):** `system/scripts/run_synthetic_critical_load_scenario.py`.

**Why this location:** `system/scripts/` already holds this repository's one existing general-purpose runnable CLI (`system/scripts/polaris`, wrapping `system/runtime/cli.py`/`runner.py`) and one existing synthetic-fixture generator (`generate_synthetic_168h_scenario.py`) — it is the established convention for "a command you actually run," as opposed to the repository root, which this pass's own survey found holds ~90 single-purpose one-off research/audit scripts, not CLI entry points.

**Why a new file instead of editing an existing one:** The directive named `run_n6_closed_loop_simulation.py` (in the Candidate N6 research directory) as the existing single-origin entry point to build on — it is the only script in the repository that already demonstrates the *real* forecast→router→optimizer→simulator chain (N6 forecast engine + `EMSControlRouter` + `GAP19HighsNativeOptimizer` + `DigitalTwinSimulator`) working end to end, with cryptographic verification of the frozen model assets it depends on. That script has no CLI and no critical-load parameter — its own `run_simulation()` takes no arguments and hardcodes the critical-load figure from `loads.yaml`. Rather than edit it (even non-invasively), it was left **completely untouched** (loaded read-only via `importlib.util.spec_from_file_location`, never opened for writing; its own file hash was re-checked and is unchanged) and a new, separate, parameterized script was written that reuses its already-imported classes and constants. This satisfies "preserve all existing work" literally and "prefer a thin new entry point over broad core-code refactoring."

**What the new script actually does, end to end, per run:**
1. Re-verifies the 4 frozen Candidate-N6 asset hashes (`candidate_n6_model.joblib`, `candidate_n1_model.joblib`, `CANDIDATE_N_MANIFEST.json`, `ensemble_parameters.json`) — fails closed before running anything if any mismatch.
2. Ingests the same `POLARIS_HYBRID_FIXTURE_H1_0` / Candidate-K 36-feature matrix at the same fixed smoke origin (`2024-06-01T00:00:00Z`) the existing validated script uses.
3. Runs `N6SolarForecastEngine.predict()` for a real 24h forecast bundle (frozen model, not retrained, not refit).
4. Builds `configs["critical_demand_w"]` — a 24-length array, `min(user_critical_load_w, forecast_demand[t])` — and passes it to the optimizer via the **documented, pre-existing** config key `gap19_highs_native.py` already reads for its own critical-demand reserve constraint (lines ~88–99 of that protected file; supplying a value to an existing input slot is not an edit to its behavior).
5. Calls `EMSControlRouter.evaluate_and_route()` **unmodified**, and then branches **exactly as the real production runner does** (`system/runtime/runner.py` lines ~149–167, mirrored, not edited): `NORMAL` → `GAP19HighsNativeOptimizer`, `EMERGENCY` → `OptionDFallbackSolver`, `UNKNOWN_INVALID` → stop, no plan, fail closed.
6. Steps `DigitalTwinSimulator` (unmodified) hour by hour against real future ground truth from the fixture.
7. Writes a full JSON report with the router's route, the optimizer actually invoked and its real solver status, per-hour dispatch, and an honest comparison between the user's critical-load input and what was actually served.

---

## 3. What actually executed — route evidence, not assumption

**Full run output (`--critical-load-kw 11.6`):**

```
Router decision:            NORMAL
Optimizer executed:         GAP19HighsNativeOptimizer
Optimizer constraint_status: OPTIMAL
Optimizer objective_value:   31.0554
Steps completed:             24/24
Total unmet load (Wh):       88800.0
Total unmet vs user critical load (Wh, derived estimate): 0.0
Diesel fuel consumed (L):    29.0554
OVERALL STATUS: SUCCESS_CLEAN
```

This is **route evidence**, not an assumption: `report["optimizer_executed"] == "GAP19HighsNativeOptimizer"` is only set inside the `route == "NORMAL"` branch, and `plan.constraint_status == "OPTIMAL"` is GAP19's own solver's real return value (HiGHS), not a mocked/fabricated status. To confirm GAP19 is genuinely sensitive to the CLI's critical-load input (i.e., the input is wired to something real, not a no-op), the same run was repeated at `--critical-load-kw 5` and `--critical-load-kw 40`:

| `--critical-load-kw` | Route | Optimizer | Status | Objective | Diesel fuel (L) | Total unmet load (Wh) |
|---|---|---|---|---|---|---|
| 5.0 | NORMAL | GAP19HighsNativeOptimizer | OPTIMAL | 13.2086 | 11.2086 | 247,200.0 |
| 11.6 | NORMAL | GAP19HighsNativeOptimizer | OPTIMAL | 31.0554 | 29.0554 | 88,800.0 |
| 40.0 | NORMAL | GAP19HighsNativeOptimizer | OPTIMAL | 49.4116 | 47.4116 | 0.0 |

Fuel burn, objective value, and total unmet load all move materially and monotonically with the critical-load input — this is a real optimizer response to the CLI's value, not a mocked result. In every case, the **derived "unmet vs. user critical load" estimate was 0.0 Wh**: whenever GAP19 reaches `OPTIMAL`, the critical-priority portion of demand was fully served at every hour (non-critical demand was the part left unmet, consistent with GAP19's own priority ordering). This derived figure is explicitly labeled `DERIVED_ESTIMATE` in the JSON output and in the script's own comments, because neither `GAP19HighsNativeOptimizer` nor `OptionDFallbackSolver` populates a separate `unmet_essential` field on the `DispatchPlan` in this run (confirmed by source read) — it is computed in the new script itself as `max(0, critical_demand[t] − (demand[t] − unmet_load[t]))`, not read from an authoritative field.

**The EMERGENCY / `OptionDFallbackSolver` branch was independently verified executable** (not merely present as dead code) by constructing a depleted-battery/low-fuel station state (SOC 21%, 2.0 L fuel) with the same forecast/config pipeline: `router.evaluate_and_route()` returned `EMERGENCY`, and `OptionDFallbackSolver.solve()` ran successfully, returning `constraint_status = "OPTION_D_FALLBACK"` with real, non-trivial `diesel_power`/`unmet_load` arrays (e.g. `diesel_power[0]=13606.64 W`, `unmet_load[1]=12946.16 W`). This confirms the new script's `EMERGENCY` branch (identical code to what was exercised in this standalone check) is live, not theoretical. The default fixture/station state used by `--critical-load-kw`'s actual run happens to classify `NORMAL` (see Section 4) — this was not forced or cherry-picked; it is what `router.py`'s real, current logic produces for this state.

---

## 4. The honest finding: the router ignores the CLI's critical-load input entirely

This is the central finding this pass is required to report plainly, not soften:

- `system/control/router.py` (read-only, hash re-verified unchanged before and after this work: `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f`) computes its own internal "critical load" for the `EMSControlRouter`/ECD survivability classification from `current_state.last_observed_demand` (falling back to `bundle.demand.point[0]`, then a hardcoded `30000.0` floor) — **lines 54–59**. It never reads `configs["critical_demand_w"]`, `configs["loads"]["critical_load"]`, or any CLI-supplied value.
- In this run, that internally-derived value was `15,300.0 W` (the fixture's observed demand at the smoke origin) — unrelated to the `11.6 kW` (`11,600.0 W`) the user entered on the command line. Re-running with `5.0` or `40.0 kW` changes GAP19's dispatch (Section 3) but **does not and cannot** change the router's `NORMAL`/`EMERGENCY` decision, because the router never sees that value.
- `router.py` also still uses the **ungoverned `6.0`-hour code default** for `T_required` (line 45) — no `system/config/*.yaml` sets `ecd.t_required_hours`. This is the exact, already-documented HD-03 finding (`HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md` §1), re-confirmed unchanged by this pass's own read.
- **The project owner has already recorded fail-closed decisions for both of these gaps** — Decision A (`T_required`) = **A-iii**, Decision B (critical-load routing source) = **B-iii**, Decision C (operational response to `UNKNOWN_INVALID`) = **M-A** — in `POLARIS_MASTER_DECISION_REGISTER.md` v1.9.2, item `ECD-01` (`ECD01_OWNER_DECISIONS_RECORDED_REPORT.md`, same date). **These decisions are not implemented in code.** `router.py` and `ecd.py` are byte-identical to every prior pass's recorded hash; implementing A-iii/B-iii/M-A requires editing both protected files, which requires a separate, not-yet-granted implementation authorization (explicitly stated in both source documents, and out of this pass's boundaries regardless).
- **Consequence, stated precisely:** this run's route (`NORMAL`) reflects the **status-quo (A-i/B-i) behavior** — full-observed-demand substitution and the ungoverned 6h default — not the owner's recorded A-iii/B-iii/M-A fail-closed decision. `UNKNOWN_INVALID` remains architecturally unreachable from this call site today, exactly as `HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md` §4 already documented, because both of router.py's substitution chains always resolve to a finite, positive number regardless of what this CLI's `--critical-load-kw` is. This is not a regression introduced by this pass — it is the pre-existing, already-governed-but-not-yet-implemented gap, now additionally confirmed to persist unchanged through an actual, successful synthetic run rather than only through static code reading.

This is why the new script's design deliberately keeps the CLI's critical-load input **out of** the router/ECD call and only feeds it to GAP19's own documented reserve-constraint input slot (Section 2, step 4) — per the directive's explicit instruction that a synthetic CLI parameter is fine as a scenario input, but must not be smuggled in as an authoritative input to the protected router's survivability classification, which remains governed by decisions that are recorded but not yet implemented.

---

## 5. Tests executed — real outcomes, not mocked

```
$ .venv/bin/python3 -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -q
5 passed in 0.54s

$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py -q
22 passed in 0.35s

$ .venv/bin/python3 -m pytest system/tests/test_offline_runtime.py -q
5 failed, 30 passed in 8.18s
FAILED test_cumulative_physical_conservation_168h
FAILED test_flexible_load_constraints
FAILED test_flexible_load_no_double_counting
FAILED test_long_duration_closed_loop_endurance_168h
FAILED test_per_timestep_conservation_audit  — AssertionError: 4658.73 not less than 0.1 (bus-bar imbalance at step 22)
```

All three results are **byte-for-byte consistent with the prior reports' last recorded state** (`N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md` §3.3–3.4, §3.7): RT-02's focused closure suite remains fully clean (22/22 here is the subset actually re-run; the full 32-test combined suite including the slow MILP research file was not re-run this pass to save time, since nothing touching it changed); RT-01 remains open with the identical 5-test failure signature, same step-22 residual (`4658.729999999996` Wh), rooted in the already-isolated, already-regression-tested `option_d.py` diesel-minimum-power-floor defect (a `PROTECTED_FILES` entry, correctly left untouched this pass).

**No test result in this report is claimed from mocks.** The CLI runs in Section 3 are real executions of real frozen models, a real HiGHS-backed MILP solver, and a real digital-twin simulator stepping through real fixture ground truth — confirmed by inspecting the actual JSON output (`system/scripts/SYNTHETIC_CRITICAL_LOAD_RUN_REPORT.json`) for genuine, varying numeric values across the three `--critical-load-kw` runs, not a fixed/templated success string.

---

## 6. Protected/frozen-asset integrity — before and after

| File | Hash | Status |
|---|---|---|
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` | Unchanged, re-verified before and after |
| `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | Unchanged |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | Unchanged |
| `system/optimization/implementations/option_d.py` | `15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad` | Unchanged (post-RT-01-solar-fix value; left alone, already correctly fixed) |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | Unchanged |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | Unchanged |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | Unchanged |
| `.../run_n6_closed_loop_simulation.py` (existing single-origin entry point) | Loaded read-only via `importlib`, never opened for writing | Unchanged |

All 4 frozen Candidate-N6 model/manifest assets were cryptographically re-verified **inside every CLI run itself** (Section 2, step 1) — not just by this report's own separate check. `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (v1.9.2), `winner: null`, the sealed 2025 blind partition, all 4 `SAFETY_GATE_REGISTRY` entries, and `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard were not opened, touched, or executed this pass. `execute_campaign()` was never invoked; `system/evaluation/n6_multi_origin_harness/` was not touched. Nothing was staged, committed, or pushed (`git status --short` confirms only new, untracked files: the new script and its JSON output report).

---

## 7. Files changed this pass

| File | Change |
|---|---|
| `system/scripts/run_synthetic_critical_load_scenario.py` | **New.** Thin CLI adapter (Section 2). |
| `system/scripts/SYNTHETIC_CRITICAL_LOAD_RUN_REPORT.json` | **New.** Output of the `--critical-load-kw 11.6` run (regenerated on every invocation). |
| `N6_SYNTHETIC_END_TO_END_RUN_REPORT.md` | **New** (this file) + mirror in `N6_REMEDIATION_REPORTS/`. |

No other file was created, edited, staged, or committed. `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` was explicitly **not** touched (out of scope for this pass).

---

## 8. Single next blocker, stated precisely

Everything permitted by this pass's boundaries was executed: a working single-command synthetic run exists, takes exactly one critical-load-in-kW input, genuinely drives GAP19's optimization, genuinely exercises the EMERGENCY/Option-D branch when the station state warrants it, and is reported with real, varying numbers rather than mocked output.

**What remains blocked, and why, is entirely pre-existing and outside this pass's authority to fix:**

1. **`router.py`/`ecd.py` do not implement the owner's already-recorded A-iii/B-iii/M-A fail-closed decisions.** Fixing this requires editing two `PROTECTED_FILES` entries, which requires a separate, explicit implementation-authorization decision that has not been granted (stated in both `HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md` §9.5 and `ECD01_OWNER_DECISIONS_RECORDED_REPORT.md` §5, item 4). Until that authorization exists, no CLI, adapter, or test harness — including the one built this pass — can make the router's `NORMAL`/`EMERGENCY` classification reflect the owner's own recorded decision; it will keep reflecting the pre-decision status-quo substitution chain, as demonstrated in Section 4.
2. A distinct, already-isolated, already-regression-tested `option_d.py` defect (diesel-minimum-power-floor excess generation, step-22 residual) keeps RT-01's 5 tests failing; it also requires a `PROTECTED_FILES` edit and the same kind of governance review already called for in `RT01_RT02_FAILURE_FORENSICS_REPORT.md` and `N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md` §5(B).

**The single next action needed to progress either of these:** the project owner grants an explicit implementation authorization for one of (1) or (2) above, scoped to a specific protected file and specific change, so a future pass can edit `router.py`/`ecd.py` (to implement A-iii/B-iii/M-A) or `option_d.py` (to close the diesel-floor excess-generation gap) under that authorization. Neither this report nor the new CLI script bypasses either blocker; both are reported as open, exactly as found.
