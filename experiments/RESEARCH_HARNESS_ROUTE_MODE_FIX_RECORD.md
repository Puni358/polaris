# Research-Harness Fix Record: Closed-Loop EMERGENCY Mode Propagation

**Date (UTC):** 2026-10-06
**Scope:** research harness only. This is a NEW research-harness version. Historical Stage 4 results are **not** overwritten and are **not** re-derived by this change.

## 1. Defect

- `EMSControlRouter.evaluate_and_route` (`system/control/router.py:34–104`) computes `assessment.operating_mode` and returns `route_mode`.
- The research closed-loop loops received `route_mode` and logged it, but passed the **unchanged** `StationState` to the optimizer.
- `StationState.operating_mode` is initialised to `"NORMAL"` (`system/schemas/station_state.py:19,32`) and carried forward unchanged by `ResearchRealizationExecutor` (`system/simulation/research_realization_executor.py:273`).
- `ResearchNumericalGAP19Optimizer.optimize` reads `station_state.operating_mode` (`experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py:96`) and adds the EMERGENCY-only row `p_dis − p_served ≤ 0` only when it equals `"EMERGENCY"` (line 365).
- Result: the EMERGENCY constraint was never built in any closed-loop research run, while telemetry labelled 8,288 rows EMERGENCY.

## 2. Files changed

| File | Change | Pre-change SHA-256 | Post-change SHA-256 |
|---|---|---|---|
| `system/research/route_mode_propagation.py` | **NEW** helper `propagate_route_mode(state, route_mode)` returning a shallow planning copy with `operating_mode` set | — (new) | `80456f8776925860ad20c407ec92f3ac78dbd387f4863ea48dc1917490e89376` |
| `system/research/closed_loop_causal_nwp_runner.py` | import helper; `planning_state = propagate_route_mode(current_state, route_mode)`; `optimize(bundle, planning_state, …)` | `62cb1607a8dfa63edd804142f167916c1cc11bef30d49ae380d236efad03daa4` | `ef7bbd33ef3d216513b33c535b3ed345a60a412e1f5c90f035237434da047265` |
| `system/research/research_critical_demand_adapter.py` | import helper; same propagation before `optimize` | `c9aab75bfebf7fc24454ae959173a7892139b70eedafd8680a6c0ea6a3cef640` (reconstructed by reversing the three edits; the method reproduces the recorded pre-change hash exactly for the other file) | `0601e57c0a0f5f6cb37f463b9d6a35ed23ffa29a6501d2f46902e356c82a6b85` |
| `tests/test_research_route_mode_propagation.py` | **NEW** regression tests (8) | — (new) | `4e0afaa8bc31fe54987dbe69f76aa41c75c6983512d2e62cec8c4219627e4298` |

The execution state is untouched. Only the planning copy handed to the optimizer carries the router's mode. The executor still receives `current_state`.

## 3. Behavioural change

- **Before:** optimizer receives `operating_mode = "NORMAL"` on every step of every origin, whatever the router assessed. EMERGENCY-only row never built.
- **After:** optimizer receives the router's assessed mode. Under EMERGENCY, 24 rows `p_dis(t) − p_served(t) ≤ 0` are built and the plan satisfies them.
- No other constraint, objective weight, reserve formula, battery limit, diesel limit, forecast logic, or production file was changed.

## 4. Tests

Command: `.venv/bin/python -m pytest tests/test_research_route_mode_propagation.py -v`

Result: **8 passed in 1.77 s.**

| Test | Proves |
|---|---|
| `test_fixture_states_route_as_named` | Real router: NORMAL fixture → NORMAL; EMERGENCY fixture → EMERGENCY |
| `test_propagate_sets_mode_without_mutating_original` | Helper sets the mode on the copy only |
| `test_propagate_normalises_case` | `"emergency"` → `"EMERGENCY"` |
| `test_normal_assessment_reaches_milp_as_normal` | NORMAL assessment → MILP builds 0 EMERGENCY rows |
| `test_emergency_assessment_reaches_milp_and_activates_constraint` | EMERGENCY assessment → 24 EMERGENCY rows built; status OPTIMAL; plan satisfies discharge ≤ served every hour |
| `test_unpropagated_state_never_reaches_milp_as_emergency` | Reproduces the defect: router EMERGENCY but unpropagated state → 0 EMERGENCY rows |
| `test_research_loop_propagates_route_before_optimize[closed_loop…]` | AST: loop calls the helper and passes `planning_state` to `optimize` |
| `test_research_loop_propagates_route_before_optimize[research_critical_demand_adapter…]` | Same for the adapter loop |

The MILP rows are observed through a HiGHS spy (`highspy.Highs` subclass recording every `addRow`). The EMERGENCY row is identified by its exact coefficients: two entries, `+1` on `p_dis(t)`, `−1` on `p_served(t)`, bounds `(−∞, 0]`.

## 5. Production and frozen-artifact hashes

Recorded before and after the change (`/home/punith-bs/hashes_before.txt`, `/home/punith-bs/hashes_after.txt`). Files compared: production optimizer, dispatch plan, causal NWP forecaster, router, executor, station state, all Stage 4 `.py`, the research extractor, the Stage 4 freeze MD/JSON/manifest, and all Stage 4 `.json`/`.csv` artifacts.

| File | SHA-256 | Status |
|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | unchanged |
| `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` | unchanged |
| `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | unchanged |
| `system/control/router.py` | 041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f | unchanged |
| `system/simulation/research_realization_executor.py` | `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` | unchanged |
| `system/schemas/station_state.py` | e763439a6ddecbbadb9287f99258e595ab7f23f0eb9a7377f5a54beb7661df88 | unchanged |
| `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py` | `95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e` | unchanged |
| `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py` | `3427da6a7b1d7763f8fa655e541cd2a344aeefdd33379137c6311501799395d0` | unchanged |
| `experiments/stage4_sw_low_sun_2025_holdout/run_stage4_sw_low_sun_2025_campaign.py` | `8a62feb30a09a9bae7bab1261c73a1f33b857c585f2af5a37c757e29c2f0c312` | unchanged |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` | `e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7` | unchanged |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json` | `6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87` | unchanged |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE_MANIFEST.json` | `abb6091317dad672aedb3cab0c2a187b25e8b751097f5cb12834178cdb59d489` | unchanged |

The comparison covered every listed file. The only hash that changed was `closed_loop_causal_nwp_runner.py`, which is intended. The adapter change is covered by the reversal reconstruction in §2.

**Frozen Stage 4 artifacts were not touched.** The Stage 4 campaign runner and adapter are unchanged, and so are all Stage 4 telemetry, results, safety, statistics, and factorial reports.

## 6. What is NOT fixed by this change

1. **The Stage 4 campaign runner still has the defect.** `run_stage4_sw_low_sun_2025_campaign.py` has its own loop (line ~212–222) that calls the router and passes `current_state` to the optimizer. It is a frozen artifact and was not modified. Its results remain as frozen.
2. **The 2024 S/SW campaign runner has the same defect** (`experiments/candidate_s_sw_campaign_2024/run_candidate_s_sw_123_campaign.py`, line ~194–204). Not modified.
3. **The loops are not executed end-to-end by the tests.** The wiring test is an AST check plus the real router and real MILP. A full closed-loop run was not executed, per the focused-tests instruction.
4. **`UNKNOWN_INVALID` is propagated faithfully.** The extractor has a degraded fail-safe branch for that mode that returns zero diesel and zero battery flows (`research_numerical_extractor.py:110–127`). The router produces it only when the ECD assessment is neither NORMAL nor EMERGENCY. Whether that can occur in these runs is not established by these tests.
5. **Research results change.** Any new closed-loop run with this harness will differ from the historical runs wherever EMERGENCY was assessed. That is the intended correction, and it means the historical numbers are not comparable without a new preregistration.
6. **Stage 4 imports `research_critical_demand_adapter`** for `adapt_critical_demand_vector`, which is unchanged. The file's hash changed, but no frozen Stage 4 computation uses the changed branch.

## 7. Verdict

- Fix **VERIFIED** for the mechanism it targets: the router's assessed mode now reaches the research MILP in both shared research loops, and the EMERGENCY-only constraint is built and enforced when assessed.
- The harness is **ready for a separately preregistered corrected reproduction campaign** only after (a) the Stage 4 and 2024 campaign runners are replaced by corrected research-harness versions that use the same propagation, (b) at least one end-to-end closed-loop smoke test passes on a short horizon, and (c) the preregistration states that results differ from the historical Stage 4 numbers. None of these has been done.
