# POLARIS RT-01 — Stage 1 Cross-Horizon Reservation Prototype: Implementation & Validation Report

**Date:** 2026-10-18
**Nature of this document:** Implementation and validation report for Stage 1 of `RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md` (Candidate 4, Stage 1 only — the static, config-driven skeleton). Code **was** written and executed this pass, under the explicit authorization "POLARIS RT-01 — AUTHORIZE STAGE 1 RESERVATION PROTOTYPE ONLY." Stage 2 (the forecast-outlook trigger) was **not** implemented. The startup-fuel accounting fix (Candidate A from `RT01_VERIFIED_ROOT_CAUSE_AND_MILP_CORRECTION_PROPOSAL.md`) was **not** combined with this work. Nothing was staged, committed, or pushed. **RT-01 remains OPEN** — Stage 1, as implemented and sized, does **not** close the steps-119–121 shortfall (see §2 below) and the closure rule is not satisfied.

---

## 1. What was implemented

**Files touched (exactly the directive's authorized scope, nothing else):**
- `system/optimization/implementations/milp.py` (not protected) — added the two new continuous slack variables and two new soft constraint rows, read the two new config knobs defensively, and populated `DispatchPlan.reserve_shortfall`.
- `system/config/optimizer.yaml` (not protected) — added `weights.reserve_shortfall_penalty: 0.5` and a new `reservation:` block (`terminal_target_soc_pct: 40.0`, `fuel_reserve_target_l: 20.0`).
- `system/tests/test_milp_reservation_mechanism.py` (new file) — 6 structural tests. **Note:** this file was first created as `test_milp_stage1_reservation.py`; that name tripped the project's own `test_offline_runtime.py::test_research_artifact_firewall` (which forbids any filename containing `"stage"` or `"odd"` anywhere under `system/`, a pre-existing guard against stray Stage-7/8 research artifacts). This was a real, self-caused regression, caught by the first full-suite run (§Validation Step 4) and fixed by renaming the file before the final full-suite run — no test assertion was touched or weakened.
- `research/rt01_diagnostics/trace_stage1_reservation_counterfactual.py` (new diagnostic script) + its output `research/rt01_diagnostics/rt01_stage1_reservation_counterfactual_trace.json`.
- This report and its mirror in `N6_REMEDIATION_REPORTS/`.

**Mechanism, precisely as built:**
- Variable layout extended from `H*K=360` to `362` variables: index 360 = `s_term` (Wh, continuous, ≥0, unbounded above), index 361 = `s_fuel` (L, continuous, ≥0, unbounded above). Neither is binary; neither participates in any existing row unless explicitly added.
- New soft row A (terminal-energy reservation): `E[23] + s_term ≥ e_term_target_wh`, where `e_term_target_wh = clip(capacity_wh * terminal_target_soc_pct/100, min_e_wh, max_e_wh)`, computed once per call from static config — **no forecast-outlook signal is read** (Stage 2 only).
- New soft row B (fuel-reserve preference): `sum(marg_fuel_l_wh*dt*p_diesel[t] + base_fuel_l_h*dt*u_diesel[t]) − s_fuel ≤ current_fuel_l − fuel_reserve_target_l`, using the **same** fuel coefficients as the existing hard row, as an independent additional row.
- Objective: `c[s_term] = reserve_shortfall_penalty` ($/Wh); `c[s_fuel] = reserve_shortfall_penalty / marg_fuel_l_wh` ($/L, via the diesel energy-equivalence ratio, documented in code). Neither term is scaled by the per-timestep horizon-discount `w_t` (both rows are horizon-level, not per-timestep flows).
- `DispatchPlan.reserve_shortfall[23] = round(s_term + s_fuel/marg_fuel_l_wh, 2)`; all other 23 indices are `0.0` (neither row is per-timestep). Populated on every successful solve (and `[0.0]*24` on the pre-existing infeasible-fallback path); never omitted.
- **The existing hard SOC floor/ceiling (`lb[E]=min_e_wh`, `ub[E]=max_e_wh`) and the existing hard cumulative fuel-budget row (`≤ current_fuel_l`, no slack) are untouched** — confirmed structurally in §3, not just by code inspection.
- Backward-compatibility: if `optimizer.yaml`'s new keys are absent, `reserve_shortfall_penalty` defaults to `0.0` and `terminal_target_soc_pct` defaults to `min_soc_pct` / `fuel_reserve_target_l` to `0.0` — a fully inert no-op, verified in §3.

**A real bug was caught and fixed during this pass, before any conclusions were drawn:** the first implementation read `config.get("reservation", {})` at the top level, but `optimizer.yaml`'s content (including the new `reservation:` block) is loaded by `runner.py` under `self.configs["optimizer"]`, not `self.configs["reservation"]`. This was corrected to `config.get("optimizer", {}).get("reservation", {})` before any validation run; all results below reflect the corrected code.

---

## 2. Honest result: Stage 1 does **not** close or reduce the steps-119–121 shortfall

A dedicated baseline-vs-Stage-1 counterfactual (`research/rt01_diagnostics/trace_stage1_reservation_counterfactual.py`, same real-unmodified-168-step-pipeline / instance-method-wrapping pattern as `trace_step119_counterfactual.py`) was run comparing the real pipeline with Stage 1's config knobs forced in-memory to their inert defaults ("baseline") against the real pipeline using the actual shipped `optimizer.yaml` values ("stage1"):

| Metric | Baseline | Stage 1 | Delta |
|---|---|---|---|
| Steps 119–121 unmet load | **14,974.11 Wh** | **14,974.11 Wh** | **0.00 Wh (bit-identical)** |
| Total 168h unmet load | 14.9741 kWh | 14.9741 kWh | 0.00 kWh |
| Total diesel fuel (L) | 120.56 | 124.25 | **+3.69 L (worse)** |
| Renewable utilization | 79.76% | 78.83% | **−0.93pp (worse, still >75%)** |
| System reliability | 99.73% | 99.73% | 0.00pp |
| First fuel-exhaustion step | 68 | **49** | **−19h (fuel runs out sooner)** |
| Last NORMAL/MILP step | 45 | 44 | −1h |
| Per-168-step solve wall time | 21.9s | 23.5s | +1.6s (negligible per-step) |

**The steps-119–121 shortfall is bit-identical, down to the hundredth of a watt-hour, with Stage 1 active.** The mechanism is confirmed genuinely *engaged* (not a dead no-op): the soft reservation rows paid a real, nonzero penalty on 7 of the real NORMAL-route calls (steps 19, 20, 40–44), cumulative shortfall ≈662 kWh across those calls' own 24h-horizon solves. But paying that penalty earlier in the run did not translate into more fuel or battery margin surviving to steps 119–121 — if anything, fuel is exhausted **19 hours earlier** under Stage 1 (step 49 vs. 68), and total fuel burn and renewable utilization both moved slightly in the *wrong* direction. This is consistent with — and does not contradict — the design memo's own risk flag (§5): Stage 1 alone, with no forecast-outlook trigger, is untargeted; it tries to hold a modest SOC/fuel margin on *every* call, which can cost a little extra diesel early without any mechanism connecting that cost to the specific night-119 deficit 95+ hours away. The memo explicitly called this outcome plausible ("Candidate 3... unlikely alone (untargeted)"); this pass demonstrates it is, for the configuration implemented here.

**No further escalation to Stage 2 or Candidate 2 is performed or recommended by this pass** — per the directive, that would require separate owner authorization. **RT-01 remains OPEN**, and this pass's own evidence does not move it closer to the closure rule beyond what is already true today (see §4).

---

## 3. Validation Step 1 — structural tests (`system/tests/test_milp_reservation_mechanism.py`, new, 6 tests, all passing)

1. `test_hard_soc_floor_and_ceiling_unchanged_across_reservation_configs` — captures the real `lb`/`ub` arrays passed to `scipy.optimize.milp` (via a thin wrapper around the imported `milp` function that still calls the real solver) across 3 reservation configs (none, inert, aggressively active) and asserts every `E[t]` bound is exactly `capacity_wh*min_soc_pct/100` / `capacity_wh*max_soc_pct/100` in all three. **PASSED.**
2. `test_hard_fuel_cap_row_unchanged_across_reservation_configs` — locates the hard cumulative fuel-budget row by its defining signature (RHS = `current_fuel_l` exactly, zero coefficient on the new `s_fuel` column) and asserts its coefficients are byte-identical across all 3 configs, and its RHS is never reduced by `fuel_reserve_target_l`. **PASSED.**
3. `test_reserve_shortfall_field_always_present` — asserts `DispatchPlan.reserve_shortfall` is never `None`/omitted. **PASSED.**
4. `test_reserve_shortfall_zero_when_inert` — at documented-inert config, shortfall is exactly `0.0` (true no-op, not just "small"). **PASSED.**
5. `test_reserve_shortfall_nonzero_when_target_unreachable_without_penalty` — forces a 95%-SOC target unreachable within 24h at a throttled charge rate; asserts a genuinely nonzero, surfaced shortfall (>1.0 Wh) **and** that the hard 95% SOC ceiling is still respected (no energy fabricated). **PASSED.**
6. `test_baseline_vs_stage1_steps_119_121_delta_reported_and_safety_preserved` — real, full 168-step baseline-vs-Stage-1 run (pytest-embedded version of §2's diagnostic), re-verifies the hard SOC floor/ceiling across every produced plan, re-verifies all 7 `PROTECTED_FILES` hashes unchanged before/after, and reports (prints, does not presuppose) the steps-119–121 delta; only fails on an implausible-magnitude regression, not on "did it help." **PASSED.**

```
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1HardConstraintsUnchanged::test_hard_fuel_cap_row_unchanged_across_reservation_configs PASSED
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1HardConstraintsUnchanged::test_hard_soc_floor_and_ceiling_unchanged_across_reservation_configs PASSED
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1ReserveShortfallSurfacing::test_reserve_shortfall_field_always_present PASSED
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1ReserveShortfallSurfacing::test_reserve_shortfall_nonzero_when_target_unreachable_without_penalty PASSED
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1ReserveShortfallSurfacing::test_reserve_shortfall_zero_when_inert PASSED
system/tests/test_milp_reservation_mechanism.py::TestMilpStage1BaselineVsStageOneCounterfactual168h::test_baseline_vs_stage1_steps_119_121_delta_reported_and_safety_preserved PASSED
6 passed in 46.52s
```

## Validation Step 2 — baseline-vs-Stage-1 168h counterfactual

Covered in full in §2 above (`research/rt01_diagnostics/trace_stage1_reservation_counterfactual.py` / `rt01_stage1_reservation_counterfactual_trace.json`). Protected-file hash diffs detected during that script's own pre/post check: `{}` (empty — all 7 unchanged).

## Validation Step 3 — Stage-8.1 integration suite + 5 RT-01 closure tests

**`system/tests/test_s81_e2e_integration.py` — 14/14 passed** (identical to the pre-Stage-1 baseline run of the same suite, re-run before any edit):
```
14 passed in 37.10s
```

**The 5 RT-01 closure tests in `system/tests/test_offline_runtime.py` — 4/5 passed, 1 failed, identical to the pre-Stage-1 baseline:**
```
test_cumulative_physical_conservation_168h   PASSED
test_flexible_load_constraints               PASSED
test_flexible_load_no_double_counting        PASSED
test_long_duration_closed_loop_endurance_168h  FAILED  (AssertionError: 99.73 != 100.0)
test_per_timestep_conservation_audit         PASSED
4 passed, 1 failed
```
This is the **same single failure, with the same exact value (99.73%)**, before and after Stage 1 — Stage 1 changed nothing about which or how many of the 5 closure tests pass. The pre-existing baseline (re-run before any edit this pass) was byte-identically 4 passed / 1 failed with the same 99.73% figure.

## Validation Step 4 — full suite

Per the directive, since the targeted checks in Steps 1–3 passed (no regression), the full `system/tests/` suite was run (`python3 -m pytest system/tests/ -q`), untimed, to completion, twice:

**First run (before a self-caused regression was caught and fixed):** `2 failed, 498 passed, 2 warnings in 1458.73s (0:24:18)`. The two failures were:
1. `test_long_duration_closed_loop_endurance_168h` — the pre-existing, expected RT-01 failure (`99.73 != 100.0`), identical to the baseline figure re-confirmed before any edit this pass. Not a regression.
2. `test_research_artifact_firewall` — a genuine, **self-caused** regression: this project's own pre-existing firewall test asserts no filename anywhere under `system/` contains the substring `"stage"` (a guard against stray Stage-7/8 research artifacts leaking into the production tree). The new structural-test file was first named `test_milp_stage1_reservation.py`, which tripped this guard. **Fixed** by renaming it to `system/tests/test_milp_reservation_mechanism.py` (content unchanged, no assertion anywhere touched or weakened) before drawing any conclusions.

**Second (final) run, after the rename:**
```
........................................................................ [ 14%]
........................................................................ [ 28%]
........................................................................ [ 43%]
........................................................................ [ 57%]
.........F.............................................................. [ 72%]
........................................................................ [ 86%]
....................................................................     [100%]
FAILED system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_long_duration_closed_loop_endurance_168h
1 failed, 499 passed, 2 warnings in 1919.62s (0:31:59)
```
**Exactly 1 failed, 499 passed — the single pre-existing RT-01 failure only, zero new regressions anywhere in the suite.** This is the same test, same assertion, same exact value (`99.73 != 100.0`) as the pre-Stage-1 baseline. The 499 passed include this pass's 6 new structural tests; the full suite was not independently collected/run before this pass's edits (only the targeted subsets in Validation Steps 1–3 were, and those showed zero regressions against their own pre-edit baselines), so the pre-pass full-suite count is not independently re-verified here — what is directly verified is that this full run's only failure is the one already-failing, already-documented RT-01 test, with no other test newly broken.

## Validation Step 5 — exact figures, diff, and hash verification

**Protected-file hash verification (all 7 `PROTECTED_FILES` + `manifest.py`, before vs. after this entire pass):**

| File | Hash (before) | Hash (after) | Changed? |
|---|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a6...58a2e737` | `fd1afe10a6...58a2e737` | No |
| `system/optimization/implementations/option_d.py` | `022cc6a0ae...af0f6531` | `022cc6a0ae...af0f6531` | No |
| `system/control/ecd.py` | `091358c08b...9e41c96db` | `091358c08b...9e41c96db` | No |
| `system/control/router.py` | `b2a46bc5bd...9074e90f3` | `b2a46bc5bd...9074e90f3` | No |
| `system/simulation/simulator.py` | `8c44f75705...4c74b3c5e5f` | `8c44f75705...4c74b3c5e5f` | No |
| `system/runtime/runner.py` | `6d1671b6ef...062f8dc53b10` | `6d1671b6ef...062f8dc53b10` | No |
| `system/orchestration/manifest.py` | `7b7756932a...27d8bb35` | `7b7756932a...27d8bb35` | No |

**All 7 byte-identical before and after.** (Full 64-hex-char values re-verified by direct `sha256sum`-equivalent Python check at the start and end of this pass; truncated above for table width only.)

**Files authorized to change, and confirmed changed (as intended, not protected):**
- `system/optimization/implementations/milp.py`: `a5ae64102b0e623a5da5086f40a427723f4bd4d38d870535aec80b283f58a3e0` → `f10b0d6db236612a7c11188eedad12ca62ed0e087ff33720ed77d05df8307fb2`
- `system/config/optimizer.yaml`: `bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8` → `8dbe98ae49731a27ed4ae85fa1ba5faa27a0837e3f04414ca24085731e9bafd6`

**Baseline-vs-candidate metrics:** see §2 table (steps-119-121 unmet load, total unmet, total diesel fuel, renewable utilization, reliability, fuel-exhaustion step, last-NORMAL step, solve time).

**Final working-tree diff (this is a no-prior-commit repository; listed as created/modified rather than a unified diff):**
- Modified: `system/optimization/implementations/milp.py` (+~45 net lines: 2 slack vars, 2 soft rows, reserve_shortfall population, extensive inline documentation of the mechanism and its boundaries), `system/config/optimizer.yaml` (+10 lines: 1 new weight, 1 new `reservation:` block).
- Created: `system/tests/test_milp_reservation_mechanism.py`, `research/rt01_diagnostics/trace_stage1_reservation_counterfactual.py`, `research/rt01_diagnostics/rt01_stage1_reservation_counterfactual_trace.json`, this report + its `N6_REMEDIATION_REPORTS/` mirror.
- Nothing else touched. No scenario, battery/diesel/loads YAML, or governance file edited. `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` not opened for writing.

---

## 4. Does this move RT-01 closer to its closure rule?

**No, not materially.** The closure rule (register §36.1) requires all 5 named tests in `test_offline_runtime.py` to pass, or a documented-and-accepted explanation **plus** a relaxed assertion. Before this pass: 4/5 pass, 1 fails (`test_long_duration_closed_loop_endurance_168h`, 99.73% ≠ 100.0%, directly caused by the steps-119–121 shortfall this Stage 1 pass targeted). After this pass: **identically 4/5 pass, 1 fails, same 99.73% value.** Closing that one test required actually eliminating the steps-119-121 shortfall (reliability would read 100.0% only if it does), and §2 demonstrates Stage 1, as implemented and sized, does not do that. No assertion was relaxed (none is authorized to be). **RT-01 remains exactly as open as it was before this pass**, now with one additional piece of real, reproducible evidence: a targeted, non-outlook-driven static reservation mechanism inside `milp.py` is confirmed insufficient on its own — consistent with, not contradicting, the design memo's own prediction. Per the directive, this result is reported honestly and this pass stops here; Stage 2 (the genuine forecast-outlook trigger) or Candidate 2 (full-horizon reformulation) would each require separate, explicit owner authorization before any further design or implementation work begins.
