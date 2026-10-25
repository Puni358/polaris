# POLARIS — N6 IA-1 / IA-2 Remediation + Blocker Audit (One-Pass)

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `IA1_IA2_DESIGN_RESOLUTION_REPORT.md` (design-only pass that surfaced IA-1/IA-2/the StationState gap) and `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.4.0.
**Nature of this pass:** real engineering — code changes to `system/evaluation/n6_multi_origin_harness/harness.py` and `adapters.py`, plus new fakes-only regression tests — implementing three binding owner decisions (IA-1: receding-horizon; IA-2: `RouterProtocol` + `route` field; StationState handoff: fix the mechanical gap, fail closed on the evidence gap), followed by a six-item blocker status audit (A–F). **No real `N6SolarForecastEngine` / `EMSControlRouter` / `GAP19HighsNativeOptimizer` / `OptionDFallbackSolver` / `DigitalTwinSimulator` / `reserve_policy_guard.evaluate_dispatch_safety` was imported, instantiated, or called anywhere in this pass.** No campaign or replay executed. No authorization record created, reused, or implied. No model trained/tuned/recalibrated/promoted. No `epsilon_tol`/safety threshold/reserve ceiling/solar-credit cap/critical-load value invented. Nothing staged, committed, or pushed.

---

## 1. Owner decisions — binding, and their implementation status this pass

| Decision | Status this pass |
|---|---|
| IA-1: use receding-horizon control for the production-representative N6 comparison | **Implemented.** `N6RecedingHorizonForecastAdapter` / `N6RecedingHorizonRouterAdapter` / `N6RecedingHorizonOptimizerAdapter` / `RecedingHorizonPlanSlicingSimulatorAdapter` added to `adapters.py`, fake-tested in `system/tests/test_n6_receding_horizon_adapters.py`. Re-forecasts/re-routes/re-optimizes FRESH every simulated step — no cross-step caching — mirroring `worker.py`/`runner.py`'s structure. The pre-existing single-shot adapters (`N6ForecastProviderAdapter`, `RoutedOptimizerAdapter`, `SingleShotPlanSlicingSimulatorAdapter`) are **unmodified** and remain available for any caller still wanting that variant. |
| IA-2: add a fifth `RouterProtocol` + explicit `route` field on `OriginRunResult` | **Implemented.** `harness.py` gained `RouterProtocol`, `VALID_ROUTES`, `OriginRunStatus.FAILED_UNKNOWN_INVALID`, `OriginRunResult.route` / `route_history`, and `CampaignAggregateResult.route_counts`. `execute_origin_dispatch_cell` gained an **optional** `router` parameter (default `None`) — fully additive/backward-compatible; all 42 pre-existing tests pass unchanged. |
| StationState handoff: fix using authoritative evidence only; fail closed if none | **Partially implemented, honestly split.** The *mechanical* interface gap (the loop's `context` dict carried no `"state"` key, so `N6ForecastProviderAdapter.predict` could never build a real `StationState`) is **fixed**: `execute_origin_dispatch_cell` now threads its own already-tracked simulated `state` dict into `context["state"]` every step — no new value is invented; it is the exact state the loop already owns (seeded from caller-supplied `initial_state`, advanced by `simulator.step`). The *evidence* gap — no per-origin authoritative initial-state table exists anywhere in this repository — **remains open and fails closed**, by design: `resolve_authoritative_initial_state()` / `AuthoritativeInitialStateUnavailableError` (new, in `adapters.py`) raise rather than invent a substitute, confirmed by repository-wide search this pass (see Section 5). |
| Campaign authorization guard | **Unchanged.** `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` was not touched, bypassed, or weakened. Re-confirmed by a new test (`test_13_execute_campaign_still_raises_unconditionally`) that calls the guard without constructing any real production object. |
| `winner: null`, sealed 2025 blind partition | **Untouched.** Not read, re-touched, or re-asserted differently this pass. |

---

## 2. Architecture and per-step call sequence

### 2.1 The real receding-horizon sequence (confirmed by direct read this pass, `system/orchestration/worker.py` Cell B / `system/runtime/runner.py`)

```
for k in range(current_step, end_step):
    st_k          = adapter.get_station_state(k, ...)            # carries forward prior battery/diesel state
    runtime_ctx   = adapter.get_runtime_context(k)
    bundle        = forecast_engine.predict(st_k, runtime_ctx)    # FRESH every step
    assessment, route = router.evaluate_and_route(st_k, bundle, configs)  # FRESH every step
    if route == "NORMAL":   plan = optimizer.optimize(bundle, st_k, configs)
    elif route == "EMERGENCY": plan = option_d_solver.solve(assessment, bundle, st_k, configs)
    else: status = "FAILED_UNKNOWN_INVALID"; break               # fail closed, BEFORE any solver call
    step_safety   = evaluate_step_dispatch_safety(plan)           # EVERY step in production
    next_state    = simulator.step(st_k, plan, next_actual)
```

### 2.2 This pass's harness implementation (`execute_origin_dispatch_cell`, fakes-only)

```
state = dict(initial_state)
route_history = []
for step_index in range(expected_steps):
    forecast = forecast_provider.predict(origin, step_index, {"scenario_key":..., "arm":..., "state": state})
    if router is not None:
        route_result = router.evaluate_and_route(state=state, forecast=forecast, controller_settings=...)
        route = route_result["route"]                              # validated against VALID_ROUTES, fail closed else
        route_history.append(route)
        if route == "UNKNOWN_INVALID": break                       # BEFORE optimizer.optimize — mirrors worker.py
        forecast = {**forecast, **route_result, "route": route}    # threaded into the optimizer call
    plan = optimizer.optimize(state=state, forecast=forecast, controller_settings=...)
    step_result = simulator.step(state=state, dispatch_plan=plan)
    state = step_result.get("state", state)
    ... (fail-closed exception handling unchanged from the prior pass)
```

**Documented deviation (directive §3 explicitly permits this, provided it is stated):** production (`worker.py`) evaluates safety **every step** and accumulates integrity counters (reserve shortfall totals, hard-SOC-violation counts, etc.). This harness's `execute_origin_dispatch_cell` still evaluates safety only **once**, from the **last** completed step's dispatch outcome — unchanged from the prior (single-shot) pass, and **not** resolved by this pass's receding-horizon wiring. A matching forecast/route/optimize call sequence is **not** the same claim as matching per-step safety-evaluation cadence; the two remain independent, and only the former is addressed here. This is called out explicitly in `execute_origin_dispatch_cell`'s own docstring to prevent future conflation.

**A second honest deviation:** receding-horizon GAP19/Option-D solve counts scale with the number of simulated steps (potentially ~24× a single-shot run per origin, matching the prior design-resolution report's cost table). Nothing in this pass validates GAP19/Option-D convergence, latency, or `constraint_status` stability under this cadence with **real** objects — that remains completely unvalidated (see Blocker A/E below); this pass's own `IntegrationAssumption` entries (`adapters.py`) say so explicitly.

---

## 3. StationState provenance, schema, coverage, unresolved origins

- **Mechanical fix (done):** `harness.py`'s loop context now carries `"state"`. Verified: `test_21_unshimmed_forecast_adapter_now_succeeds_state_gap_fixed` (the adapter that used to fail closed with `KeyError` at step 0 now succeeds, engine called once) and `test_22b_full_chain_without_shim_also_holds` (the prior pass's TEST-ONLY `_StatePassingForecastShim` is proven redundant, not load-bearing).
- **Evidence gap (still open):** no per-origin initial-state table exists anywhere in this repository. Confirmed by repository-wide search this pass (`grep` for `initial_battery_soc_wh_by_origin`, `per_origin_initial_state`, `origins.json`/`origins.csv`, `station.yaml`) — the only hits are this harness's own existing caller-supplied-dict parameter and prior reports describing the same absence. `system/config/station.yaml` describes exactly one prototype station with no per-origin SOC/fuel/battery-energy values. The one real hand-built example, `run_n6_closed_loop_simulation.py` lines ~101–112, hardcodes literal constants (`battery_soc_pct=80.0`, `battery_energy_wh=160000.0`, `diesel_hours_running=2.0`, `diesel_fuel_remaining_liters=500.0`) for **one** smoke-test origin — not a cited, generalizable source for any other origin.
- **Fail-closed boundary, concretely implemented:** `resolve_authoritative_initial_state(origin, authoritative_initial_states_by_origin)` (new, `adapters.py`) raises `AuthoritativeInitialStateUnavailableError` naming the missing origin and artifact whenever `origin` is not in the caller-supplied registry — never returns a zero-filled/guessed dict. As of this pass, **no caller anywhere in this repository supplies a non-empty registry for any real origin** (`test_12_empty_registry_fails_closed_for_every_origin` documents this honestly).
- **Tests added:** valid handoff + copy-not-reference (`test_10`), missing origin (`test_11`), empty registry (`test_12`); malformed/incomplete `initial_state` still fails closed via the real `StationState.from_dict`-equivalent contract (`test_24_missing_required_station_state_field_fails_closed`); state isolation across two origins run through shared adapter instances (`test_07_two_origins_through_shared_adapter_instances_do_not_leak`, confirms no state/feature-matrix/route cross-contamination).
- **Unresolved origins:** all of them. Zero origins have authoritative initial-state coverage today.

---

## 4. Route field and provenance through records/reporting

- `VALID_ROUTES = {"NORMAL", "EMERGENCY", "UNKNOWN_INVALID"}` (reused verbatim from `router.py`, never redefined).
- `OriginRunResult.route: Optional[str]` (the final/last-observed route) and `route_history: Tuple[str, ...]` (the full per-step sequence) — both validated in `__post_init__`: route must be `None` or in `VALID_ROUTES`; every `route_history` entry must be in `VALID_ROUTES`; `route` must equal `route_history[-1]` when history is non-empty; `route_history` non-empty requires `route is not None`. This directly satisfies "route provenance cannot silently disappear or be replaced by a default" — it is enforced by a constructor-time exception, not merely a convention.
- `OriginRunStatus.FAILED_UNKNOWN_INVALID` — the **exact** string `worker.py`'s Cell B uses — is recorded (never a generic `INCOMPLETE_RUN`) when a router returns `UNKNOWN_INVALID`; the loop halts **before** the optimizer is ever called for that step (`test_05_unknown_invalid_halts_fail_closed_before_optimizer`).
- `CampaignAggregateResult.route_counts: Dict[str, int]` — per-arm route tallies, excluding origins with `route is None` (no router supplied) rather than folding them into any bucket (`test_08`, `test_09`).
- **Serialization/persistence:** `OriginRunResult`/`CampaignAggregateResult` are plain frozen dataclasses with no separate `to_dict`/serialization function anywhere in this module or its consumers (confirmed by `grep` — only `__init__.py` re-exports the classes). Any caller using `dataclasses.asdict(...)` (the standard mechanism) picks up the new fields automatically — there is no existing serialization path that would need a separate update to avoid dropping them, and none was found.
- **Backward compatibility:** `router` defaults to `None` on `execute_origin_dispatch_cell`; every pre-existing caller (42 harness tests, 20 adapter tests, 5 IA-1/IA-2 integration tests) is unaffected — confirmed by running them unchanged (Section 8).

---

## 5. Campaign authorization and execution boundary

Unchanged. `FactorIsolatedReplayHarness.execute_experiment_a`/`execute_experiment_b` still raise `CampaignExecutionNotAuthorizedError` unconditionally, confirmed by direct read (not modified) and by a new test that exercises the guard without constructing any real production object (`test_13_execute_campaign_still_raises_unconditionally`). No real forecast engine, router, optimizer, simulator, or safety evaluator was imported or constructed anywhere in this pass's new code — every new class in `adapters.py` and every new test is typed `Any` at runtime and exercised exclusively against hand-built Fakes.

---

## 6. Blocker status audit (A–F)

| # | Item | Status | Evidence inspected | Exact missing evidence/authorization | Changed by this pass? | Next required action |
|---|---|---|---|---|---|---|
| **A** | Campaign execution authorization | **Still blocked.** | `replay_harness.py` (read, unmodified); register SAF-05/SAF-06 entries. | A specific, written authorization for **this** multi-origin N6 comparison campaign. The register's `exp_three_arm_2024` record is for a different, already-consumed experiment and does not apply (per this pass's explicit boundary). No such record exists anywhere in this repository. | No. Guard re-confirmed unconditional, untouched. | Owner/governance issues a specific authorization naming this campaign, its scope, and its origin set, before `execute_campaign` can ever be unblocked. |
| **B** | Initial station state (per-origin) | **Still blocked for every origin.** | Repository-wide search this pass (configs, `run_n6_closed_loop_simulation.py`, prior reports); `resolve_authoritative_initial_state` fail-closed test suite. | A cited, per-origin initial-state table (battery SOC, diesel fuel remaining, demand/irradiance/wind observations at t0) for however many origins the eventual comparison covers. None exists. | Mechanical plumbing fixed (state now flows through the loop once seeded); the evidence itself is unchanged — still absent. | Assemble and cite a real per-origin initial-state table (Workstream 3 of the prior design-resolution report) before any real-object use. |
| **C** | EVID-02 (real critical-load evidence) | **Still open.** | Register EVID-02 entry (`item_type: E`, `blocking_scope: operational_validation`), classified `EXTERNAL_EVIDENCE_REQUIRED` — unresolvable from in-repo evidence alone. | Real, measured critical-load data for the Nuolja station (or whichever real origins are in scope) with provenance — not a synthetic fixture. | No. This pass's adapter tests use only synthetic `critical_load`/`unmet_load` fixtures; none substitutes for EVID-02. | Obtain and cite the real measurement; until then, any unmet-critical-load figure in a future comparison report must stay labeled `SYNTHETIC_ENGINEERING_SCENARIO`-relative. |
| **D** | DSL-01 (`epsilon_tol`) | **Owner decision still required; acceptance verdict still blocked.** | Register DSL-01 entry — `OWNER_DECISION_REQUIRED`, explicitly reclassified (not resolved) in a prior pass; no numeric value selected there or here. | A risk-tolerance decision from the owner on the acceptance threshold itself. | No. This pass neither selects nor needs a value (no acceptance verdict is computed here). | Owner selects `epsilon_tol` (or confirms it stays deliberately unset); until then, any DSL-01 formal acceptance verdict remains blocked — distinct from this report's purely descriptive engineering content, which needs no threshold. |
| **E** | Operational readiness | **Still unverified.** | `IntegrationAssumption` entries (`adapters.py`); register FOR-01/EVID-01 entries (both `EXTERNAL_EVIDENCE_REQUIRED`). | Live data-arrival/feature-availability/ingestion-timestamp evidence for N6 running in the actual operational pipeline — fundamentally different from the historical-provider publication timestamps, offline replay fixtures, and fakes-only tests this pass (and prior passes) produced. No such live-arrival evidence exists in this repository. | No. This pass adds fakes-only call-sequence/cadence tests, which are evidence of *interface correctness*, not of *operational readiness* — the two are explicitly distinguished in every new class's docstring. | A separately authorized live-ingestion evidence-gathering process, outside this pass's scope. |
| **F** | Production safety | **Still `UNKNOWN_NOT_VERIFIED`, not a pass.** | `OriginRunResult.safety_evidence_status`/`safety_passed` validation rules (`harness.py`, unmodified this pass); new tests confirm safety evidence stays unknown through the receding-horizon chain exactly as it did through the single-shot chain. | Real dispatch-outcome safety evidence from a real `reserve_policy_guard.evaluate_dispatch_safety` call against a real plan — never produced by any fakes-only test. | No. No safety threshold, reserve ceiling, or automated halt was introduced, activated, or modified. `safety_evidence_status` can never be `VERIFIED` unless a real `SafetyEvaluationResult` is supplied — still true after this pass. | A real-object, separately authorized smoke test producing genuine safety evidence; this pass does not and cannot substitute for that. |

---

## 7. Offline fake-based test suite — commands, results

```
$ python3 -m pytest system/tests/test_n6_multi_origin_harness.py \
    system/tests/test_n6_multi_origin_harness_adapters.py \
    system/tests/test_n6_ia1_ia2_call_sequence_integration.py \
    system/tests/test_n6_receding_horizon_adapters.py \
    system/tests/test_forecast_lineage_and_replay_harness.py -q
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 0.22s
EXIT_CODE=0
```

Breakdown: 42 pre-existing harness tests (unchanged) + 20 pre-existing adapter tests (unchanged) + 5 IA-1/IA-2 integration tests in `test_n6_ia1_ia2_call_sequence_integration.py` (2 updated to reflect the now-fixed mechanical gap — `test_21`, plus a new no-shim variant `test_22b` — and 1 new test, `test_24`, locking in that the evidence gap still fails closed; `test_22`/`test_23` unchanged) + 13 new tests in `test_n6_receding_horizon_adapters.py` + 23 pre-existing replay/lineage tests (unchanged) = **103**, 0 failed, 0 skipped.

A broader sweep (everything under `system/tests/` matching `n6`, `harness`, `replay`, or `lineage`) also passed cleanly:

```
$ python3 -m pytest system/tests/ -k "n6 or harness or replay or lineage" -q
144 passed, 257 deselected in 6.13s
```

**Executed vs. inspected, explicitly separated:** every test above was actually run via `pytest` (exit code 0 in all cases). `worker.py`, `runner.py`, `router.py`, and `run_n6_closed_loop_simulation.py` were **inspected by direct read only** (to confirm the real call sequence and StationState/DispatchPlan contracts) — never executed, never imported by any new test or module this pass. No test was weakened, no assertion loosened, no safety check relaxed to obtain a green result.

---

## 8. Changed files, purposes, SHA-256

| Path | Type | Purpose | SHA-256 |
|---|---|---|---|
| `system/evaluation/n6_multi_origin_harness/harness.py` | modified | `RouterProtocol`, `VALID_ROUTES`, `OriginRunStatus.FAILED_UNKNOWN_INVALID`, `OriginRunResult.route`/`route_history`, `CampaignAggregateResult.route_counts`, optional `router` param + state-threading fix on `execute_origin_dispatch_cell` | `fd87426752ed0feca4ae29709dcc7822b405b199553fd687399e4edb3c0852be` |
| `system/evaluation/n6_multi_origin_harness/adapters.py` | modified | `AuthoritativeInitialStateUnavailableError`/`resolve_authoritative_initial_state`; `N6RecedingHorizonForecastAdapter`/`N6RecedingHorizonRouterAdapter`/`N6RecedingHorizonOptimizerAdapter`/`RecedingHorizonPlanSlicingSimulatorAdapter`; updated `IntegrationAssumption` IA-1/IA-2 prose to reflect owner decisions | `38d814f976561753222e2679bc96a1dc63ac6b3eae6393890db48460023acb4e` |
| `system/tests/test_n6_ia1_ia2_call_sequence_integration.py` | modified | `test_21` updated to reflect the now-fixed mechanical gap; added `test_22b` (shim-free) and `test_24` (evidence gap still fails closed) | `b154cab3935714e38690f7df4a918556a6db13e66c2260f4c35ed433ee19e61e` |
| `system/tests/test_n6_receding_horizon_adapters.py` | new | 13 tests: receding-horizon cadence, route branching/UNKNOWN_INVALID, multi-origin isolation, route-provenance aggregation, IA-3 fail-closed lookup, campaign-guard re-confirmation | `e99db867e3e8aeb29c6f93f9b355839855372d2956e48b72a8e95c8299378bd2` |
| `system/evaluation/n6_multi_origin_harness/N6_IA1_IA2_REMEDIATION_REPORT.md` | new | this report (also mirrored to repo root and `N6_REMEDIATION_REPORTS/`) | (this file) |

`replay_harness.py`, `router.py`, `worker.py`, `runner.py`, the register, and all prior reports were read this pass but **not edited**.

---

## 9. Protected-file hash table — before/after

```
                                                                     before == after (unchanged)
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  system/optimization/implementations/gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  system/optimization/implementations/option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  system/control/ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  system/control/router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  system/simulation/simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  system/runtime/runner.py
7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35  system/orchestration/manifest.py
```

The first six values are **identical** to those recorded in `IA1_IA2_DESIGN_RESOLUTION_REPORT.md` and every prior pass (re-verified by direct `sha256sum` before and after this pass's edits). `manifest.py`'s hash was captured once (no prior-pass record to diff against in this harness's own report lineage) and, since this pass made zero edits to it, its before/after value is trivially identical by construction. **No mismatch.**

Frozen Stage 8.1/N6 model artifacts referenced by `run_n6_closed_loop_simulation.py`'s own `PROTECTED_ASSETS` dict were also independently re-verified this pass and found unchanged:

```
b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197  .../candidate_n_additive_physics/artifacts/candidate_n6_model.joblib
7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7  .../candidate_n_additive_physics/artifacts/candidate_n1_model.joblib
1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031  .../candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json
26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0  stage4/stage4_results/ensemble_parameters.json
```

---

## 10. Working-tree / staging confirmation

`git status` at the start of this pass showed `system/evaluation/n6_multi_origin_harness/` and the `system/tests/test_n6_ia1_ia2_*`/`test_n6_receding_horizon_*` files as untracked (`??`) — this entire harness package has never been committed in this repository (no commits exist on `master`). This pass added/modified the files listed in Section 8 **without running `git add`, `git commit`, or `git push`** at any point. The only staged files visible in `git status` (`POLARIS_MASTER_HANDOFF.md`, `requirements.txt`) were already staged (`A`) before this pass began and were not touched by it.

---

## 11. Confirmations

- `winner: null` — unchanged, not re-touched this pass.
- The sealed 2025 blind partition — not read, evaluated, replayed, or reopened.
- Frozen model/artifact integrity — independently re-verified (Section 9), no mismatch.
- `CampaignExecutionNotAuthorizedError` — unmodified, unconditional, re-confirmed by a new fakes-only test.
- **Explicit non-execution statement:** no real `N6SolarForecastEngine`, `EMSControlRouter`, `GAP19HighsNativeOptimizer`, `OptionDFallbackSolver`, `DigitalTwinSimulator`, or `reserve_policy_guard.evaluate_dispatch_safety` was imported, instantiated, or called by any code this pass wrote. `execute_campaign`/`MultiOriginCampaignHarness.execute_campaign` was called exactly once, in a test, and it raised `CampaignExecutionNotAuthorizedError` as required — no dispatch, replay, or campaign of any kind was executed. This pass does not claim, and explicitly disclaims, that N6 is operationally ready, validated, or production-safe as a result of fakes-only tests passing.
