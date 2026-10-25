# POLARIS — IA-1 / IA-2 N6 Multi-Origin Harness Design Resolution Report

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` (Workstream 2, most important prior input) and `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.4.0.
**Nature of this document:** Design-documentation-and-fake-tests-only pass resolving the engineering design questions `IA-1` (optimizer call pattern) and `IA-2` (router interface) for `system/evaluation/n6_multi_origin_harness/`, through source inspection and fake-based tests only. **No replay, campaign, dispatch evaluation, optimization experiment, or replay-equivalent simulation was run.** No real `N6SolarForecastEngine` / `GAP19HighsNativeOptimizer` / `EMSControlRouter` / `DigitalTwinSimulator` / `reserve_policy_guard.evaluate_dispatch_safety` was constructed or called anywhere in this pass — every new test runs exclusively against hand-built Fakes. `harness.py`, `adapters.py`, `replay_harness.py`, and all six `PROTECTED_FILES` (including `router.py`) were read for citation only, never edited. No authorization record was created or implied. No model was trained, tuned, recalibrated, or promoted. No `epsilon_tol`, safety threshold, reserve ceiling, solar-credit cap, or critical-load value was invented. Nothing was staged, committed, or pushed.

---

## 1. IA-1 resolution — optimizer call pattern

### The two real patterns, with exact citations

**(a) Single-shot-then-slice** — the pattern `run_n6_closed_loop_simulation.py` actually exercises (the only existing real single-origin N6 integration):
```
n6_bundle = N6SolarForecastEngine().predict(st_initial, context)       # ONCE  (line ~142)
assessment, route = EMSControlRouter().evaluate_and_route(...)          # ONCE  (line ~155)
plan = GAP19HighsNativeOptimizer().optimize(n6_bundle, st_initial, ...) # ONCE, full 24h (line ~160)
for t in range(24):
    curr_st = DigitalTwinSimulator(...).step(curr_st, one_hour_slice_of(plan, t), actual_t)  # 24x (line ~221)
```
`adapters.py`'s `N6ForecastProviderAdapter`/`RoutedOptimizerAdapter` implement exactly this: both cache on first call and return the same cached bundle/plan on every subsequent call for the same origin (`adapters.py` lines 383–404, 431–470; locked in by `test_n6_multi_origin_harness_adapters.py` `test_07`/`test_10` and this pass's `test_22`).

**(b) Receding horizon** — re-forecast, re-route, re-optimize fresh on every simulated step. This is **not** a hypothetical invented by `harness.py`; it is the literal, standing structure of the only two real production dispatch runtimes in this repository, confirmed by direct read this pass:
```
system/orchestration/worker.py:283   for k in range(current_step, self.end_step):
system/orchestration/worker.py:375       bundle = self.forecast_engine.predict(st_k, runtime_ctx)
system/orchestration/worker.py:402       assessment, route = self.router.evaluate_and_route(st_k, bundle, self.configs)
system/orchestration/worker.py:404/406   plan = self.optimizer.optimize(...)  /  self.option_d_solver.solve(...)   # route-branched

system/runtime/runner.py:130          bundle = self.forecast_engine.predict(current_state, runtime_context)
system/runtime/runner.py:149          assessment, route = self.router.evaluate_and_route(current_state, bundle, self.configs)
system/runtime/runner.py:151          plan = self.optimizer.optimize(bundle, current_state, self.configs)
```
Both loops call `forecast_engine.predict` → `router.evaluate_and_route` → `optimizer.optimize`/`option_d_solver.solve` **fresh, every single step** — i.e. exactly the shape `harness.py`'s `execute_origin_dispatch_cell` loop (lines 606–619) already has, calling `optimizer.optimize(...)` once per `step_index`.

### The correction this pass makes to the prior report's framing

`N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` (Workstream 2) states: *"No script, test, or document in this repository has ever run GAP19 in a per-step replanning loop."* Re-inspection this pass shows that statement needs a precise qualifier. Confirmed by `grep -rn "forecast_engine\s*=" system/orchestration/worker.py` and `system/runtime/runner.py`:
```
worker.py:78/82/85   self.forecast_engine = None | None | LocalBaselineForecastEngine(...)
runner.py:74/76      self.forecast_engine = Stage81ForecastEngine(...) | LocalBaselineForecastEngine(...)
```
and `grep -rln "N6SolarForecastEngine" system/orchestration/` / `system/runtime/` → **no matches**.

So, precisely:
- **Receding-horizon itself is not unprecedented.** It is the standing, exercised production control law in both `worker.py`'s Cell B path and `runner.py`'s live runtime, for whichever forecast engine is configured — `LocalBaselineForecastEngine` or `Stage81ForecastEngine`.
- **What is genuinely unprecedented is `N6SolarForecastEngine` running inside that per-step loop.** N6 has never been instantiated in `system/orchestration/` or `system/runtime/` — only in the one standalone smoke script (single-shot pattern) and `n6_operational_pipeline.py` (per FOR-02, not re-audited line-by-line this pass).
- Conversely, **single-shot-then-slice has been validated once with N6** but does not match how the real production runtimes (`worker.py`/`runner.py`) structurally operate for any other engine they have actually run.

### Behavioral and evaluation implications (documented, not ranked)

| | Single-shot-then-slice | Receding horizon |
|---|---|---|
| GAP19 solves per origin | 1 | up to N (one per simulated hour) |
| Matches real production control law (`worker.py`/`runner.py`) | No — smoke-test-only pattern | Yes, structurally identical |
| Ever run with N6 specifically | Yes (once, one smoke run) | No — never, with any engine other than baseline/Stage81 |
| What it measures | N6 forecast quality under an **open-loop dispatch policy** (dispatch decisions fixed at t0; only simulated *state* — SOC, fuel — is closed-loop via `DigitalTwinSimulator`) | N6 forecast quality under the **actual operating control law** — dispatch is also re-decided every hour from fresh information |
| Cost for a 123-origin × 24h campaign | ~123 GAP19 solves | up to ~2,952 GAP19 solves |
| Validated solver behavior at that cadence with N6 | Yes (once) | Unknown — no data on GAP19 convergence/latency/`constraint_status` stability under hourly N6 re-forecasting |

A diesel-reduction figure produced under single-shot describes a materially different control policy than the one the production system actually enacts for any other engine; it is not interchangeable with a receding-horizon result, and this pass does not claim either pattern is "the" right one to use for the upcoming comparison — that is a scientific-scope decision, not an engineering one.

### Engineering recommendation

Two defensible paths, in order of immediate availability:

1. **(Recommended as the immediate next step, not as final scope.)** Scope the first N6-vs-baseline comparison explicitly as evaluating *N6 forecast quality under an open-loop/single-shot dispatch policy* — this is what `adapters.py` already implements and tests (20 existing tests + this pass's 3 new ones), requires no new adapter engineering, and is the only pattern ever validated with N6 at all. Any resulting report must say exactly this in its scope statement, not imply it reflects the live operational control law.
2. If the owner instead wants the comparison to reflect the system's real operating logic, authorize building and fake-testing a receding-horizon N6 adapter variant (mirroring `worker.py`/`runner.py`'s loop shape) **before** any multi-origin run, accepting the added engineering time and the up-to-~24× GAP19 solve-count increase, plus a subsequently authorized real-object smoke test to check GAP19 actually stays `OPTIMAL` under hourly N6 re-forecasting (currently unknown).

### Owner decision required (exact)

**Which control policy the N6-vs-baseline diesel-reduction comparison is meant to evaluate: open-loop/single-shot (cheap, already adapter-built and tested, but not how `worker.py`/`runner.py` operate for any other engine) or receding-horizon (matches the real production control law, but has never been run with N6 and requires new adapter engineering plus an authorized smoke test).** This determines what the eventual diesel-litres number *means*, not just how much compute it costs — it is a scientific-validity decision belonging to the owner, not something this pass selects on the owner's behalf.

A second, smaller, newly-surfaced item under this same heading (see Section 3, `test_21`): regardless of which pattern is chosen, `N6ForecastProviderAdapter` as written cannot currently receive the real `StationState` it needs from inside `execute_origin_dispatch_cell`'s existing per-step `context` dict (`{"scenario_key":..., "arm":...}` — no `"state"` key). This is a concrete, additional engineering item to close before either IA-1 option can be wired for real; it is not a new authorization or scope question.

---

## 2. IA-2 resolution — router interface

### Trace

`EMSControlRouter.evaluate_and_route` (`system/control/router.py` lines 34–106, a `PROTECTED_FILE`, read-only this pass) wraps `self.ecd.evaluate(...)` (`system/control/ecd.py`, also `PROTECTED_FILE`) and returns `(EmergencyAssessment, route)` where `route ∈ {"NORMAL", "EMERGENCY", "UNKNOWN_INVALID"}` (lines 98–106). Every production and research call site found this pass (`worker.py:402`, `runner.py:149`, `run_n6_closed_loop_simulation.py:155,259`, `n6_operational_pipeline.py:257`, plus ten further research/experiment scripts under `stage7/`) calls it **immediately before** `optimizer.optimize(...)` (route `"NORMAL"`) or `option_d_solver.solve(...)` (route `"EMERGENCY"`), branching on the result, and never caches or reuses a routing decision across steps independently of the optimize/solve call it gates.

`harness.py`'s four Protocols (`ForecastProviderProtocol`, `DispatchOptimizerProtocol`, `SimulationStepperProtocol`, `SafetyEvaluatorProtocol`) have no fifth, router-specific slot. `adapters.py`'s `RoutedOptimizerAdapter` (lines 407–470) resolves this today by calling the router first and folding its `route` decision into the dict `DispatchOptimizerProtocol.optimize` returns (`result["route"]`), never silently dropping it — this is the adapter-only interim choice `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` already flagged as `IA-2`, re-confirmed unchanged this pass.

### Effects on testability, provenance, and interface consistency

**Current fold-in (`RoutedOptimizerAdapter`):**
- *Testability:* no change to `harness.py`'s already-tested four-Protocol signature; the 42 pre-existing `test_n6_multi_origin_harness.py` tests are untouched. Confirmed by `test_09`/`test_10` (adapter tests) and this pass's `test_22`, which lock in router+optimizer each called exactly once per origin through the real, unmodified loop.
- *Provenance (a gap this pass newly surfaces):* `OriginRunResult` (`harness.py` lines 166–183) has **no `route` field**. `execute_origin_dispatch_cell` never reads `plan.get("route")` for anything (confirmed by direct read of the loop, lines 606–619) — the router's decision is computed and threaded through the adapter's return dict, then **dropped before it ever reaches the persisted per-origin record**. This pass's `test_23` confirms the resulting `OriginRunResult` carries nothing about which route was taken. Since `EMERGENCY` vs `NORMAL` determines whether `option_d_solver` or GAP19 actually ran (`worker.py:404/406`, `runner.py:151` + sibling branch), this is a safety-relevant signal that a multi-origin N6-vs-baseline comparison would currently have no way to record per origin, even though it is computed on every call.
- *Interface consistency:* keeps the four-Protocol contract stable at the cost of baking a 5-component real call sequence (forecast → route → optimize → simulate → safety) into a 4-slot structural contract; a future adapter for a differently-coupled real router/optimizer pair would need to repeat this same fold-in trick.

**Alternative — extend `harness.py` with a fifth `RouterProtocol`:**
- *Testability:* requires a reviewable change to `execute_origin_dispatch_cell`'s signature and `harness.py`'s already-tested public interface (42 existing tests would need re-review for compatibility).
- *Provenance:* makes the router decision a first-class, independently recorded value, naturally extensible into a new `OriginRunResult.route` field — closes the gap above directly rather than working around it in the adapter layer.
- *Interface consistency:* matches the real 5-component production sequence more faithfully, but is exactly the kind of change to already-tested code this pass's boundaries do not authorize making unilaterally.

### Engineering recommendation

Recommend **extending `harness.py` with a fifth `RouterProtocol`** and adding a `route` (or equivalently named) field to `OriginRunResult`, specifically because the current fold-in silently drops a safety-relevant signal from the persisted per-origin record: a multi-origin comparison that cannot say which origins triggered `EMERGENCY` routing (and therefore ran `option_d_solver` instead of GAP19 entirely) would be aggregating diesel/unmet-load metrics across runs that used two different solvers without recording which is which. This is a recommendation, not an implementation; no change to `router.py` itself is implied or needed either way, since `router.py` is a `PROTECTED_FILE` and its existing `evaluate_and_route` signature already supplies everything either option needs.

### Owner decision required (exact)

**Approve extending `harness.py`'s Protocol set with a `RouterProtocol` and `OriginRunResult` with a `route` field (recommended), or explicitly accept the current adapter-level fold-in — with its route-provenance gap documented and accepted — for an interim or lower-stakes use.** This pass does not make this change; it documents the tradeoff and the gap it found.

---

## 3. Tests and integrity

### New file: `system/tests/test_n6_ia1_ia2_call_sequence_integration.py` (3 new tests)

Builds entirely on hand-written Fakes (no import of any real production class), and exercises the **real, unmodified** `execute_origin_dispatch_cell` (`harness.py`) wired to the **real, unmodified** adapter classes (`adapters.py`) — going one step beyond the existing `test_n6_multi_origin_harness_adapters.py`, which tests each adapter in isolation:

- **`test_21_unshimmed_forecast_adapter_fails_closed_at_step_zero`** — wires `N6ForecastProviderAdapter` directly into `execute_origin_dispatch_cell` exactly as both files stand today. Locks in that this **fails closed** at step 0 (`FAILED_OPTIMIZATION_EXCEPTION`, a `KeyError`, never a silent wrong answer): `execute_origin_dispatch_cell`'s loop builds `context` as `{"scenario_key": ..., "arm": ...}` (no `"state"` key — confirmed by direct read, `harness.py` lines 607–610), but `N6ForecastProviderAdapter.predict` needs `context.get("state", {})` to build the real `StationState` the real N6 engine's `.predict(station_state, context)` call requires. This is a fifth, newly-surfaced, concrete interface gap beyond `IA-1`–`IA-4`, found by literally gluing the real pieces together rather than testing them in isolation.
- **`test_22_single_shot_call_counts_hold_end_to_end`** — bridges that gap with a small, clearly-labeled **TEST-ONLY** shim (not a production change to `adapters.py` or `harness.py`; documented in the test file's own docstring as evidence of the gap, not a fix for it) and locks in the full `IA-1`/`IA-2` call-sequence assumption end-to-end: the fake forecast engine, router, and optimizer are each called **exactly once per origin** (never once per step — confirming single-shot, not receding-horizon, in this adapter wiring), while the fake simulator steps **exactly once per hour** (4 of 4 in the test).
- **`test_23_safety_evidence_unknown_even_on_clean_run`** — documents that, through this exact adapter chain, safety evidence stays `UNKNOWN_NOT_VERIFIED` even on a clean `OPTIMAL` run, because `DispatchOutcomeView.at_hour`'s returned dict never carries a `"_real_plan_dict"` key for `ReservePolicyGuardSafetyEvaluatorAdapter` to act on. Consistent with the existing "missing evidence is never a pass" rule (not a new bug), but directly relevant to `IA-2`'s provenance discussion above.

### Full regression (this pass)

```
$ python3 -m pytest system/tests/test_n6_multi_origin_harness.py system/tests/test_n6_multi_origin_harness_adapters.py system/tests/test_n6_ia1_ia2_call_sequence_integration.py system/tests/test_forecast_lineage_and_replay_harness.py -q
88 passed in 0.18s
```
(42 pre-existing harness tests + 20 pre-existing adapter tests + 3 new tests this pass + 23 pre-existing replay/lineage tests. Zero edits to `harness.py`, `adapters.py`, or `replay_harness.py` this pass — all pre-existing tests pass unchanged.)

### Fakes-only and no-campaign-wiring confirmed

- Every class/function in the new test file (`_FakeStationState`, `_FakeForecastBundle`, `_FakeN6Engine`, `_FakeRouter`, `_FakeDispatchPlan`, `_FakeGAP19Optimizer`, `_FakeDigitalTwinSimulator`, `_fake_evaluate_dispatch_safety`, `_StatePassingForecastShim`) is local and hand-written; `grep -n "^from system\|^import system" system/tests/test_n6_ia1_ia2_call_sequence_integration.py` shows only `adapters.py`/`harness.py`/`replay_harness.py` imports — no real production module.
- `execute_campaign`/`MultiOriginCampaignHarness` are not imported or called anywhere in the new file. `CampaignExecutionNotAuthorizedError`'s unconditional gate (`replay_harness.py`) is untouched and not exercised.
- No sealed/blind-partition path, frozen model artifact, or real dataset is read by the new file.

### Exact changed-file list, this pass

| Path | Type |
|---|---|
| `system/tests/test_n6_ia1_ia2_call_sequence_integration.py` | new (3 tests) |
| `IA1_IA2_DESIGN_RESOLUTION_REPORT.md` | new (this file) |
| `N6_REMEDIATION_REPORTS/IA1_IA2_DESIGN_RESOLUTION_REPORT.md` | new (mirror) |

`adapters.py`, `harness.py`, `replay_harness.py`, `router.py`, `worker.py`, `runner.py`, the register, and all prior reports were read this pass but **not edited**. Nothing was staged, committed, or pushed.

---

## 4. Report — confirmations and remaining blockers

### Six protected-file hashes — re-verified this pass, identical to every prior pass

```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  system/optimization/implementations/gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  system/optimization/implementations/option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  system/control/ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  system/control/router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  system/simulation/simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  system/runtime/runner.py
```
Identical to the values recorded in `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md`. No `PROTECTED_FILES` entry was opened for editing this pass.

### Explicit confirmation: no production dispatch or campaign ran

No real `N6SolarForecastEngine`, `EMSControlRouter`, `GAP19HighsNativeOptimizer`, `DigitalTwinSimulator`, or `reserve_policy_guard.evaluate_dispatch_safety` was imported or constructed by any new code this pass — each was read (for citation of exact signatures/line numbers) but never instantiated outside Fakes. `execute_campaign`/`MultiOriginCampaignHarness.execute_campaign` were not called. `winner: null` is unchanged (not re-touched this pass; last re-confirmed in `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md`). The sealed 2025 blind partition was not accessed. No model was trained, tuned, recalibrated, or promoted. No `epsilon_tol`, safety threshold, reserve ceiling, solar-credit cap, or station critical-load value was invented. Nothing was staged, committed, or pushed.

### Remaining blockers (unchanged in kind from `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md`, restated with this pass's refinements)

1. **Authorization.** Still none. `replay_harness.py`'s unconditional `CampaignExecutionNotAuthorizedError` gate is untouched — not re-read-only-confirmed line-by-line this pass since no change was made near it, but nothing in this pass's scope could have altered it (no edits to `replay_harness.py`).
2. **`IA-1`.** Now carries a sharper, owner-decidable tradeoff (Section 1): open-loop/single-shot (cheap, already built/tested, but unlike how `worker.py`/`runner.py` operate for any other engine) vs. receding-horizon (matches the real production control law, used today with other engines, but never run with N6 and requiring new adapter engineering + an authorized smoke test). Plus a newly surfaced, smaller engineering item: `N6ForecastProviderAdapter` cannot currently source the real `StationState` it needs from `execute_origin_dispatch_cell`'s existing per-step `context` dict (`test_21`) — needs closing regardless of which `IA-1` option is chosen.
3. **`IA-2`.** Recommendation given (extend `harness.py` with a `RouterProtocol` + `OriginRunResult.route` field) to close a newly-surfaced route-provenance gap in the current fold-in (`test_23`); pending owner approval either way.
4. **`IA-3`** (per-origin initial-state table) — still not assembled; not touched this pass.
5. **`IA-4`** (`reserve_shortfall_authorization_wh` stays `None`) — unchanged, no action required per the existing SAF-03 deferral.
6. **`epsilon_tol`** — still unset by owner's standing deferral; required only for a DSL-01 research-acceptance verdict, not for a bare descriptive report.
7. **EVID-02** (real Nuolja critical-load measurement) — still absent from the repository; any unmet-critical-load figure in a future comparison report must remain labeled `SYNTHETIC_ENGINEERING_SCENARIO`-relative.
