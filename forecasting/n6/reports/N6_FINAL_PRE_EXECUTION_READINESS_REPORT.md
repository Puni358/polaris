# POLARIS — Final Pre-Execution Readiness and Blocker Closure Report

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md` (starting point per the owner's directive), `DIESEL_COMPARISON_PREREQUISITE_PLAN.md`, `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.4.0, `N6_MULTI_ORIGIN_HARNESS_REPORT.md`.
**Nature of this document:** Final pre-execution readiness report for one coordinated pass across five workstreams. **No replay, campaign, dispatch evaluation, optimization experiment, or replay-equivalent simulation was run.** No real `N6SolarForecastEngine` / `GAP19HighsNativeOptimizer` / `EMSControlRouter` / `DigitalTwinSimulator` / `reserve_policy_guard.evaluate_dispatch_safety` was constructed or called — every new adapter test in this pass runs exclusively against hand-built Fakes. The sealed 2025 blind partition was not accessed. No model was trained, tuned, recalibrated, or promoted. No `PROTECTED_FILES` entry was edited. `winner: null` is unchanged. **No authorization record was created, forged, or self-approved — see Workstream 1, the finding of this pass that governs everything else.** No `epsilon_tol`, reserve-shortfall ceiling, or solar-credit cap was invented. Nothing was staged, committed, or pushed.

---

## Workstream 1 — Authorization (first priority)

### The exact question: does a genuine signed approval exist for the N6 multi-origin campaign?

**No. It does not.** This is stated plainly, with the evidence below, because this finding gates everything else in this report.

**File inspected:** `N6_MULTI_ORIGIN_CAMPAIGN_AUTHORIZATION_RECORD_PROPOSAL.json` (root and `N6_REMEDIATION_REPORTS/` mirror, re-read byte-for-byte this pass).

- Its own top-level field is `"proposal_status": "DRAFT_PROPOSAL -- NOT IMPLEMENTED, NOT SIGNED, NOT AUTHORIZED"`.
- Its `_comment` states explicitly: *"No code in this repository reads this file."*
- Every field that would carry a real value is `null`: `origin_set.value` is `null`; `arms.value` is `{"baseline": null, "candidate": null}`; the entire `required_fields_per_signed_section` block is a schema of field *names* and *descriptions*, not a filled, signed record — there is no `decision`, `signer_name`, `signed_at_utc`, or hash value anywhere in the file, filled or otherwise.
- Its own closing section, `what_this_proposal_does_not_do`, states: *"Does not create, forge, or self-approve any authorization,"* and *"Does not select an origin set, arm pair, or any hash value — every 'value' field above is null by design."*

I scrutinized this specifically for anything that could be mistaken for a signature (per this task's explicit instruction to be suspicious of anything that "looks like" one): there is no `signer_name`, no `signed_at_utc`, no hash, no `"decision": "APPROVE"` anywhere in the file. It is a schema template only.

**File inspected:** `system/evaluation/replay_harness.py` (re-read this pass). `FactorIsolatedReplayHarness.execute_experiment_a()` / `.execute_experiment_b()` both raise `CampaignExecutionNotAuthorizedError` **unconditionally** — no flag, config value, environment variable, or record of any kind is consulted before the raise. `ExperimentBConfig.__post_init__` additionally requires `authorization_token` to equal a module-level sentinel object (`_EXPERIMENT_B_AUTHORIZATION_TOKEN = object()`) that the module's own docstring states is "deliberately never set to any real/guessable value by this remediation" — no code path in the repository can satisfy it.

**File inspected:** `system/evaluation/n6_multi_origin_harness/harness.py` (re-read this pass; not edited this pass). `MultiOriginCampaignHarness.execute_campaign()` forwards directly to `FactorIsolatedReplayHarness.execute_experiment_a()` — confirmed again by direct read of the method body (reproduced verbatim in Workstream 5 below) — so it inherits the same unconditional raise. `execute_origin_dispatch_cell` (the per-origin DI loop, built in the prior consolidated pass) is called by neither `execute_campaign` nor `MultiOriginCampaignHarness` anywhere in the module — confirmed by a fresh regression check this pass (Workstream 5).

### Exact authorized signer and approval mechanism (as proposed — not as implemented)

The proposal names, but does not instantiate, a mechanism modeled on the one genuine precedent that exists in this repository: `experiments/exp_three_arm_2024/AUTHORIZATION_RECORD.json` (schema v2), checked in code by `experiments/exp_three_arm_2024/scripts/preflight.py:check_authorization()`. I re-read both this pass:

- **Base-record signer role:** `"project lead"`, matched case-insensitively (`preflight.py:298`, `_signature_failures`). The existing exp_three_arm_2024 record shows this working in practice — `signer_name: "PuNi"`, `signer_role: "project lead"`, bound to exact `package_manifest_sha256`/`experiment_config_sha256` values, with a separate `execute_instruction_ref` single-use guard for the execute stage specifically (`_execution_history` in `preflight.py` scans `results/run_*/RUN_STATUS.json` and fails closed if any prior run already consumed a given ref, or if run history is unreadable/ambiguous).
- **This is the right model to propose** — I confirm the proposal's own citation of it is accurate — but it is **not wired to the N6 multi-origin comparison today**. `replay_harness.py` has no `check_authorization`-equivalent function, no `AUTHORIZATION_RECORD.json`-equivalent file it reads, and no code path that would ever consult `N6_MULTI_ORIGIN_CAMPAIGN_AUTHORIZATION_RECORD_PROPOSAL.json` even if every field in it were filled in today.

### What this pass did and did not do about it

Per the directive's explicit boundary ("do not implement or enable a new execution-authorization path... without the separately required governance approval for that code change"), **no checking code was added** anywhere — not to `replay_harness.py`, not to `harness.py`, not as a new standalone module. The proposal file was re-read and re-verified, not edited, not filled in, not signed.

**Important, separate observation (not this comparison's authorization):** `experiments/exp_three_arm_2024/AUTHORIZATION_RECORD.json` itself *does* carry a real, past, project-lead-signed execution authorization (signer `PuNi`, `signer_role: "project lead"`, `signed_at_utc: 2026-10-11T07:52:41Z`, consumed by `run_20261011T075716Z`, `history` entry 2). This is a genuine signature — but it is for a *different, already-executed-and-rejected* experiment (`EXP-THREE-ARM-2024`, Arms A/A_FIX/B/C, no N6 involvement — confirmed by register `FOR-05`), it is already consumed (single-use, cannot authorize a second run), and nothing in it names, scopes, or extends to the N6-vs-baseline multi-origin comparison this directive is about. I flag this explicitly so it is not later mistaken for, or conflated with, authorization for the N6 campaign — it is neither.

### Workstream 1 conclusion

**No genuine signed approval exists for the N6 multi-origin campaign.** `CampaignExecutionNotAuthorizedError` remains the unconditional, unmodified gate. **Execution stays blocked.**

---

## Workstream 2 — Production adapter integration

### Exact interfaces of the one existing real single-origin integration

Direct re-read of `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/run_n6_closed_loop_simulation.py` this pass confirms the real call sequence and signatures:

| Real component | Signature | Called |
|---|---|---|
| `N6SolarForecastEngine` | `.predict(station_state: StationState, context: Dict) -> ForecastBundle` | **once**, for the full 24-hour horizon |
| `EMSControlRouter` | `.evaluate_and_route(station_state, bundle, configs) -> (assessment, route)` | once per horizon |
| `GAP19HighsNativeOptimizer` | `.optimize(bundle, station_state, configs) -> DispatchPlan` | **once**, producing all 24 hours at once |
| `DigitalTwinSimulator` | `.step(station_state, one_hour_dispatch_plan_slice, actual_t) -> StationState` | **24 times**, slicing the single plan |
| `reserve_policy_guard.evaluate_dispatch_safety` | `(plan: Dict, min_e_wh, reserve_shortfall_authorization_wh) -> SafetyEvaluationResult` | post-hoc |

### The one critical mismatch this pass surfaced

`harness.py`'s `execute_origin_dispatch_cell` loop calls `optimizer.optimize(...)` **once per step inside the step loop**, implying a receding-horizon (replan-every-hour) control strategy. The real integration above does the opposite: **one** optimization call produces the full 24-hour plan, and the per-step loop only *simulates* across slices of that one plan. No script, test, or document in this repository has ever exercised GAP19 in a per-step replanning loop — only the single-shot-then-slice pattern has ever run, and only once, in one smoke script, never as a campaign.

This is not a bug to silently fix. It is a design decision requiring review, so this pass documents it (`IntegrationAssumption` `IA-1` in the new adapter module, with three more: `IA-2` the missing router "slot" in `harness.py`'s four Protocols; `IA-3` that per-origin initial state must be supplied, never invented; `IA-4` that `reserve_shortfall_authorization_wh` stays `None`, matching SAF-03's standing deferral) and implements **only** the single-shot-then-slice variant, since that is the only pattern this repository has ever actually run.

### What was built — `system/evaluation/n6_multi_origin_harness/adapters.py` (new)

Translation-only adapter classes, each wrapping an **injected** object typed `Any` at runtime (real class names appear only inside a `TYPE_CHECKING` guard, never evaluated — confirmed by a new static regression test, below):

- `StationStateCodec` — plain-dict ↔ real `StationState` via its own existing `to_dict`/`from_dict`.
- `ForecastBundleStepView` — extracts one step's values from an already-produced `ForecastBundle`.
- `DispatchOutcomeView` — extracts per-hour scalars (`diesel_consumed_liters`, `critical_unmet_load_wh`, `total_unmet_load_wh`, `constraint_status`) from a real `DispatchPlan`, correctly handling the real script's own convention of a single-hour value repeated 24 times to form a valid slice.
- `N6ForecastProviderAdapter` — calls the injected real forecast engine **once per origin** (not per step), caches the bundle, returns per-step views (resolves `IA-1`'s forecast half).
- `RoutedOptimizerAdapter` — calls the injected real router then the injected real optimizer **once per origin**, caching the resulting plan; folds the router's `route` decision into the returned dict rather than dropping it (resolves `IA-2`).
- `SingleShotPlanSlicingSimulatorAdapter` — slices the cached plan and calls the injected real simulator once per hour; requires a caller-supplied, per-origin/per-step ground-truth actual, never fabricates one.
- `ReservePolicyGuardSafetyEvaluatorAdapter` — calls the injected real `evaluate_dispatch_safety`, `reserve_shortfall_authorization_wh=None` by default (`IA-4`); returns `None` (never a fabricated pass) when no real plan dict was supplied for an outcome.

**Tested exclusively against Fakes:** `system/tests/test_n6_multi_origin_harness_adapters.py` (new, 20 tests) builds hand-written `_Fake*` classes whose *method shapes* mirror the real classes (confirmed against the script read above), never a real production object. Key assertions: the real engine/optimizer are each called **exactly once per origin**, never once per step (`test_07`, `test_10`); missing feature matrices, configs, ground-truth actuals, and the router-bundle linkage all fail closed with `ValueError` (`test_08`, `test_11`, `test_12`, `test_14`, `test_15`); missing safety evidence returns `None`, never a fabricated pass (`test_17`); `reserve_shortfall_authorization_wh` defaults to `None` (`test_16`). Two static regression tests (`test_19`, `test_20`) confirm `adapters.py` imports no real production module outside its `TYPE_CHECKING` block, and that `harness.py` does not reference `adapters.py` at all (i.e., the adapters are not wired into campaign execution).

```
$ python3 -m pytest system/tests/test_n6_multi_origin_harness_adapters.py -q
20 passed in 0.12s
$ python3 -m pytest system/tests/test_n6_multi_origin_harness.py system/tests/test_n6_multi_origin_harness_adapters.py system/tests/test_forecast_lineage_and_replay_harness.py -q
85 passed in 0.17s
```

### What remains an open integration assumption requiring an authorized smoke test

All four (`IA-1` through `IA-4`, full text in `adapters.py`) require, at minimum, an owner/engineering decision plus a subsequently *authorized* single-origin smoke test against real objects before any multi-origin use — none of which this pass performs or grants. Specifically: (1) confirm single-shot-then-slice is the intended pattern (or authorize building/testing a receding-horizon variant instead); (2) confirm folding the router into the optimizer adapter is acceptable, or decide to extend `harness.py` with a fifth Protocol; (3) a concrete per-origin initial-state table does not exist for any multi-origin set and must be assembled, never synthesized; (4) no change needed to proceed with `reserve_shortfall_authorization_wh=None`.

**No real solver, model-backed dispatch, replay, or replay-equivalent simulation was run to build or test this adapter layer.** The adapters remain disconnected from `execute_campaign`/`MultiOriginCampaignHarness` (confirmed, `test_20`).

---

## Workstream 3 — Comparison definition and manifest

### Finite comparison specification (proposed, not executed)

- **Arms:** exactly two — baseline (existing authorized established forecast provider) vs. candidate (`n6_solar`, already classified `CAUSAL_PROVIDER_NAMES` in `forecast_lineage.py`, confirmed causal not oracle).
- **Origins:** must be an explicit, finite, named list — the existing `exp_three_arm_2024` 123-origin set is the only already-hashed, already-cited candidate set in this repository (`experiments/exp_three_arm_2024/manifests/*.sha256`); no new origin set was selected or invented by this pass.
- **Time window / horizon:** 24-hour decision-time-only horizon per origin, matching both the real single-origin script and `ScenarioSpec`'s existing shape.
- **Input provenance:** N6 model hash from `CANDIDATE_N_MANIFEST.json` (re-verified this pass, see below); baseline code/configuration/input hashes from `experiments/exp_three_arm_2024/manifests/`.
- **Forecast-causality requirement:** enforced automatically and already tested — `ScenarioSpec.__post_init__` calls `reject_if_oracle`; **`realized_sw_in` and any other future-realized value is excluded from forecast inputs by this existing mechanism**, not newly added by this pass.
- **Metrics:** diesel litres consumed (both arms, absolute and percentage change), critical/total unmet load, safety-evidence status (`UNKNOWN_NOT_VERIFIED` vs. `VERIFIED`), run/optimizer status — all already defined in `harness.py`'s `OriginRunResult`/`CampaignAggregateResult`, unchanged this pass.
- **Missing-data handling:** a missing diesel/unmet-load metric is excluded from aggregation and separately counted, never zero-filled (`aggregate_origin_results`, re-verified unchanged); missing safety evidence is `UNKNOWN_NOT_VERIFIED`, never a pass.
- **Output schema:** `OriginRunResult` (per-origin) and `CampaignAggregateResult` (per-arm aggregate), both already implemented and tested.
- **Separate outputs, explicitly:** a **descriptive-metrics** report (diesel litres, unmet load, run status — reportable today once execution is authorized) is kept distinct from any **DSL-01 research-acceptance verdict** (Wilcoxon p<0.05 + BCa CI, which additionally requires `epsilon_tol`). This report does not claim the latter and no comparison should either, unless `epsilon_tol` is preregistered first.

### Manifest — real hashes verified this pass, instance deliberately left uninstantiated

Ran `load_known_existing_hash_sources` (read-only; no campaign, no model loading) against the live repository this pass:

```
n6_model_sha256:            b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197
n6_model_manifest_source:   stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json
baseline_code_sha256:       42 entries (experiments/exp_three_arm_2024/manifests/CODE.sha256)
baseline_configuration_sha256: 5 entries (.../CONFIGURATION.sha256)
baseline_inputs_sha256:     4 entries (.../INPUTS.sha256)
```

Attempted to build a full `CrossArmReproducibilityManifest` with these real values plus a placeholder `experiment_configuration_sha256=''` and `authorization_reference=None` — confirmed it **fails closed exactly as designed**:

```
ValueError: Fail-closed: experiment_configuration_sha256 is required and must be non-empty.
```

**No manifest instance was created.** Missing fields, exactly: (1) `experiment_configuration_sha256` — no experiment-configuration file for this specific N6-vs-baseline comparison exists yet (the comparison spec above is descriptive, not yet a committed config file); (2) `authorization_reference` — no genuine authorization exists (Workstream 1); (3) a concrete, cited `origins` tuple — the 123-origin baseline set is proposed, not yet formally adopted for this comparison; (4) `runtime_dependency_versions` — not captured for a run that has not happened. `output_hashes` correctly stays empty (no outputs exist).

---

## Workstream 4 — Owner and evidence dependencies

Re-checked, not re-litigated, this pass:

- **`epsilon_tol`:** re-grepped (`epsilon_tol` across `*.md`/`*.json`/`*.py`) — 21 hits, all narrative (tracing/deferral text in prior reports and the register); **zero numeric values anywhere in the repository.** Remains unset by the owner's own standing deferral (register §21, `OWNER_DECISION_REQUIRED`). **No value selected, inferred, or invented this pass.** A bare descriptive diesel/unmet-load report does not require it; DSL-01's own Candidate-2 research-acceptance verdict does.
- **EVID-02 (real Nuolja critical-load measurement):** re-searched this pass (`find . -iname "*nuolja*.csv"`) — 12 matches, every one meteorological (`SW_IN`, multivariate weather, terrain/horizon, clear-sky decomposition) or a solar-radiance subset; **none is an electrical critical-load measurement.** Unchanged: `EXTERNAL_EVIDENCE_REQUIRED`. Any unmet-critical-load figure in a future comparison report must be labeled `SYNTHETIC_ENGINEERING_SCENARIO`-relative (CL-01's provisional 11.6 kW value), never real-station-validated.
- **SAF-05's four gates:** re-checked `system/safety/reserve_policy_guard.py`'s `SAFETY_GATE_REGISTRY` directly this pass — all four entries still carry `authorized=False` with an explicit `"AUTHORIZATION_REQUIRED"` note. **Unauthorized, unchanged.**
- **No reserve-shortfall ceiling, solar-credit cap, or reliability threshold was invented.** SAF-03/SAF-04 remain exactly as the register records them (owner deferrals, not this pass's to resolve).
- **Frozen models, `winner: null`, protected files, reserve ceilings, solar-credit caps:** none changed (see Workstream 5).

---

## Workstream 5 — Validation and integrity

```
$ python3 -m pytest system/tests/test_n6_multi_origin_harness.py system/tests/test_n6_multi_origin_harness_adapters.py system/tests/test_forecast_lineage_and_replay_harness.py -q
85 passed in 0.17s
```
(42 pre-existing harness tests + 20 new adapter tests + 23 pre-existing replay/lineage tests, all passing; the 42 harness tests are unchanged from the prior consolidated pass — `harness.py` was not edited this pass.)

**Protected-file hashes — re-verified this pass, identical to every prior pass:**
```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  system/optimization/implementations/gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  system/optimization/implementations/option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  system/control/ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  system/control/router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  system/simulation/simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  system/runtime/runner.py
```
No `PROTECTED_FILES` entry was opened for editing this pass.

**`winner: null`:** re-confirmed at `stage7/.../candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json:5` (`"winner": null`), unchanged.

**Campaign guard, re-verified by direct source read this pass:**
```python
def execute_campaign(self, config: MultiOriginCampaignConfig) -> None:
    self._replay_harness.execute_experiment_a(config.experiment_a_config)
```
— still forwards unconditionally to `FactorIsolatedReplayHarness.execute_experiment_a`, which still raises `CampaignExecutionNotAuthorizedError` unconditionally. A new static test (`test_20`) confirms `harness.py`'s source contains no reference to the new `adapters.py` module at all.

**Blind-partition exclusion:** re-confirmed — no file under any `blind`/`sealed` path was read, listed, or referenced by any new code this pass (`grep -rn "blind" system/evaluation/n6_multi_origin_harness/adapters.py system/tests/test_n6_multi_origin_harness_adapters.py` → no matches).

**Exact changed-file list, this pass:**

| Path | Type | Workstream |
|---|---|---|
| `system/evaluation/n6_multi_origin_harness/adapters.py` | new | 2 |
| `system/tests/test_n6_multi_origin_harness_adapters.py` | new (20 tests) | 2 |
| `N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` | new (this file) | all |
| `N6_REMEDIATION_REPORTS/N6_FINAL_PRE_EXECUTION_READINESS_REPORT.md` | new (mirror) | all |

Confirmed via `git status --porcelain`: only the two new files above (plus this report and its mirror) are untracked/changed as a result of this pass; `harness.py`, `reproducibility_manifest.py`, `replay_harness.py`, the register, and the prior reports were read but **not edited** this pass. **Nothing was staged, committed, or pushed** (`git add` was never run).

---

## Final classification

**BLOCKED_ON_AUTHORIZATION** (Workstream 1 — no genuine signed campaign-execution approval exists; `N6_MULTI_ORIGIN_CAMPAIGN_AUTHORIZATION_RECORD_PROPOSAL.json` is confirmed, by direct re-inspection this pass, to be an all-`null`, explicitly-unsigned draft schema, and `replay_harness.py`'s gate is unconditional and unmodified)

combined with

**BLOCKED_ON_ENGINEERING** (Workstream 2 — four integration assumptions, most significantly the single-shot-vs-receding-horizon optimizer-call-pattern mismatch (`IA-1`), require an owner/engineering decision plus a subsequently *authorized* real-object smoke test before any adapter may be used for real)

combined with

**BLOCKED_ON_OWNER_DECISION** (Workstream 4 — DSL-01's `epsilon_tol` remains unset by standing owner deferral; required only for a DSL-01 research-acceptance verdict, not for a bare descriptive report)

combined with

**BLOCKED_ON_EXTERNAL_EVIDENCE** (Workstream 4 — EVID-02, no real Nuolja critical-load measurement exists anywhere in the repository).

**No single status covers this honestly.** The engineering done this pass (adapter interface mapping, 20 new passing tests, a verified-real-hash manifest assembly proof that correctly refuses to instantiate) is complete and `ENGINEERING_READY_FOR_REVIEW` for what it covers, but the project as a whole cannot reach an actual N6-vs-baseline execution without, independently: (1) a genuine execution authorization this pass cannot grant itself, (2) resolution of at least `IA-1` (and ideally all four integration assumptions) plus an authorized smoke test, (3) an owner decision on `epsilon_tol` if a DSL-01 verdict is ever wanted, and (4) external Nuolja evidence this pass cannot produce from inside the repository.

---

## Exact minimal checklist for the next prompt

- [ ] **Authorization.** A genuinely signed record exists — matching or exceeding `N6_MULTI_ORIGIN_CAMPAIGN_AUTHORIZATION_RECORD_PROPOSAL.json`'s fields (signer role, scope, origin set, arms, all four hash fields, one-time `execute_instruction_ref`) — AND `replay_harness.py` (or a separately governance-reviewed extension) actually checks it in code. Neither exists today.
- [ ] **Engineering decision on `IA-1`.** Confirm the single-shot-plan-then-slice pattern (as implemented in `adapters.py`) is the intended control strategy for this comparison, or explicitly authorize a different, separately-built-and-tested variant.
- [ ] **Engineering decision on `IA-2`.** Confirm folding `EMSControlRouter.evaluate_and_route` into `RoutedOptimizerAdapter.optimize` is acceptable, or decide to extend `harness.py` with a fifth Protocol (a reviewable change to already-tested code).
- [ ] **Per-origin initial-state table (`IA-3`)** assembled from a real, cited source for the specific origin set this comparison will use — not synthesized.
- [ ] **An authorized single-origin smoke test** against real production objects, only after authorization (item 1) and the two engineering decisions above — this report does not and cannot run one.
- [ ] **DSL-01's `epsilon_tol`** preregistered, or the owner formally/permanently declines it — required only if a DSL-01 Candidate-2 research-acceptance verdict will be claimed; not required for a bare descriptive report.
- [ ] **Every unmet-critical-load figure** in any resulting report explicitly labeled `SYNTHETIC_ENGINEERING_SCENARIO`-relative (EVID-02 still open) — never presented as real-station-validated.
- [ ] **A filled `CrossArmReproducibilityManifest`**, assembled using the real hashes already verified this pass (`n6_model_sha256`, baseline 42/5/4 hash sets) plus a real `experiment_configuration_sha256` (once an actual config file for this comparison exists) and the genuine `authorization_reference` from item 1 — assembled *as part of* the authorization record, not reconstructed afterward.
- [ ] **All six `PROTECTED_FILES` hashes** re-verified immediately before execution, matching the values recorded in this report.
- [ ] **Sealed 2025 blind partition** confirmed untouched by the execution plan.
- [ ] **No SAF-05 production-promotion claim** attached to the comparison's results unless SAF-05's four gates (still `authorized=False`, re-verified this pass) have separately, actually been authorized by a governance authority.
