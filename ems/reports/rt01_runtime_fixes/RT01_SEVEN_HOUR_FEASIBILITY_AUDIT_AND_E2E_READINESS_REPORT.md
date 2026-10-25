# POLARIS — RT-01 Seven-Hour Feasibility Audit and End-to-End Readiness Report

**Date:** 2026-10-18
**Nature of this document:** Bounded, read-only, owner-authorized audit ("POLARIS — RT-01 Bounded Feasibility Audit and Return to End-to-End Delivery"), continuing directly from `RT01_TIGHT_GAP_VERIFICATION_REPORT.md`. Part 1 audits the 6 remaining flagged hours (0, 1, 5, 8, 13, 15) using **only** already-captured data in `research/rt01_diagnostics/rt01_step0_full_horizon_trace.json` — no solver re-run, no new script execution, no pipeline/campaign/training. Part 2 is a single End-to-End Readiness Decision built entirely from already-existing reports. **No source, test, config, or register file was edited. No remedy is implemented. RT-01 remains OPEN.**

---

## PART 1 — Bounded Feasibility Audit of Hours 0, 1, 5, 8, 13, 15 (Hour 20 Cited from Prior Report)

### 1.1 Method (identical in kind to the already-authorized hour-20 check)

For each flagged hour `t0`, the prior reports identified the same raw pattern: renewable forecast fully exceeds demand (and, at hours 8/13/15, a 10,000 Wh flexible load `p_flex`), yet the solver curtails **all** available renewable at `t0` and discharges the battery to cover demand instead — a seemingly free, bus-bar-neutral substitution (use the renewable directly, discharge nothing). This audit checks that substitution against the **full remaining horizon**, reusing the per-hour raw solution vector (`raw_p_curt_sol`, `raw_p_curt_wind`, `raw_p_dis`, `raw_p_chg`, `raw_E_next_wh`, forecasts) already captured for all 24 hours in `rt01_step0_full_horizon_trace.json`. No new data was read or computed outside this file plus the config constants already on record (`charge_efficiency = discharge_efficiency = 0.92`, `max_soc_pct = 95.0` → ceiling `190,000 Wh`, `min_soc_pct = 20.0` → floor `40,000 Wh`, `renewable_curtailment_penalty_per_wh = 0.05`, `deg_penalty_per_wh = 0.00005`).

Swap size `delta[t0]` = the forecast **demand** at `t0` (matching the prior report's own "cost if renewable used directly, battery left alone" calculation exactly — confirmed by reproducing its $1,373.78 / $1,358.78 / $1,228.75 / $1,122.58–1,123.08 / $1,098.71–1,099.21 / $1,153.67–1,154.17 figures to within rounding). At hours 8/13/15 the 10,000 Wh flexible-load-serving portion of discharge is left untouched, exactly as the source report's own arithmetic treated it.

Reducing `p_dis[t0]` by `delta` increases `raw_E_next_wh` at every subsequent hour by a constant offset `delta/0.92`, **carried forward unchanged until it first collides with the 190,000 Wh ceiling** (same mechanism independently proven for hour 20 in the tight-gap report, §4, item 3). Critically — and this is where a first-pass check of this audit initially went wrong before being corrected — a single collision does **not** fully absorb the offset: the minimum-cost recourse (reduce charging at the first colliding hour, forcing equal extra curtailment there, exactly the hour-20 methodology) only clips the trajectory back down to the ceiling, not back to its original baseline. Any **residual** offset (ceiling − original baseline at that hour) continues cascading to the next hour, requiring further recourse wherever it collides again. This repeats until the residual reaches zero or the horizon ends at hour 23. All six swaps were walked through this full iterative cascade, hour by hour, using only the baseline `raw_E_next_wh`/`raw_p_chg` values already in the captured trace.

### 1.2 Results, hour by hour

| Hour | Swap size (Wh) | Claimed saving | First/only ceiling collision(s) (baseline trace) | Total forced recourse (Wh) | Recourse cost | **Net result** |
|---|---|---|---|---|---|---|
| 0 | 27,448.19 | $1,373.78 | 12 → 14 → 17 → 18 → 19 (chain of 5) | 32,429.34 | $1,621.47 | **−$247.68 (WORSE)** |
| 1 | 27,148.49 | $1,358.78 | 12 → 14 → 17 → 18 → 19 (chain of 5) | 32,075.25 | $1,603.76 | **−$244.98 (WORSE)** |
| 5 | 24,550.41 | $1,228.75 | 12 → 14 → 17 → 18 → 19 (chain of 5) | 29,005.68 | $1,450.28 | **−$221.54 (WORSE)** |
| 8 | 22,429.09 | $1,122.58 | 12 → 14 → 17 → 18 → 19 (chain of 5) | 26,499.40 | $1,324.97 | **−$202.39 (WORSE)** |
| 13 | 21,952.33 | $1,098.71 | 14 → 17 → 18 → 19 (chain of 4) | 25,936.12 | $1,296.81 | **−$198.09 (WORSE)** |
| 15 | 23,050.41 | $1,153.67 | 16 → 17 → 18 → 19 (chain of 4) | 27,233.47 | $1,361.67 | **−$208.00 (WORSE)** |
| 20 *(cited, not re-run)* | 1,182.66 | $59.19 | 23 (single) | 1,397.29 | $69.86 | **−$10.67 (WORSE)** *(from `RT01_TIGHT_GAP_VERIFICATION_REPORT.md`, already final)* |

Every recourse step verified feasible from the captured data alone: at each colliding hour the required charge-reduction never exceeded that hour's actual `raw_p_chg` (e.g. hour 12's 41,459.38 Wh of charging comfortably covers the largest single required reduction, 17,566.19 Wh, for the hour-0 case), and the freed renewable at each colliding hour was already fully "used" (zero pre-existing curtailment at hours 12/14/17/18), so converting part of that use to curtailment stays within the decomposition bound (`used + curtailed = forecast`) without any sign or bound violation. No charge/discharge exclusivity binary needed to flip. The chain terminates at hour 19 in every case because hour 19's baseline `raw_E_next_wh` is already exactly at the 190,000 Wh ceiling (95.00% SOC) with zero residual headroom — the same structural fact (a baseline trajectory already pinned at the ceiling going into hours 19–23) that made hour 20's single-hour case fail, generalized across the horizon.

**For every one of the 6 hours audited, the recourse cost exceeds the claimed saving by roughly $200–248 — the fully constraint-respecting version of the proposed swap is net worse, not better, exactly as already found for hour 20.**

### 1.3 Was a fully feasible, objectively better alternative demonstrated for any hour?

**No, for none of the 7 flagged hours.** At every hour, once the swap is corrected to actually respect the real `LinearConstraint` matrix and the 190,000 Wh SOC ceiling across the remaining horizon, the net effect — computed under the model's own existing cost coefficients, using only already-captured baseline data, no counterfactual re-solve — is negative. No hour produces a demonstrated, complete, feasible, cheaper alternative.

### 1.4 What this audit establishes, and what it does not

**Establishes:**
- The naive single-hour "use renewable directly, leave the rest unchanged" substitution is **infeasible as literally stated** at all 7 flagged hours (0, 1, 5, 8, 13, 15, 20) — not just hour 20 — because the battery's horizon-end trajectory is already pinned at the 95% SOC ceiling with no spare capacity to absorb any of these swaps without displacing energy elsewhere.
- The minimum-cost, fully constraint-respecting correction of each swap is **more expensive than the claimed saving** at all 7 hours. This directly invalidates the previously reported $7,396.97 aggregate "excess cost" figure (`RT01_FULL_HORIZON_MILP_DIAGNOSTIC_REPORT.md` §5) as a measure of a real, realizable saving — it was computed from local, single-hour comparisons that did not account for the horizon-wide SOC ceiling, exactly the flaw already identified and corrected for hour 20 in the tight-gap report.
- This materially weakens **H2** (formulation/solver defect) further than the tight-gap report alone did: it is no longer just "the one counterexample offered doesn't hold" — none of the seven counterexamples offered hold, under the same consistent methodology.

**Does not establish:**
- That the solver's returned solution is the **true global optimum**. This audit only re-checked the seven specific swaps already proposed in prior reports; it did not search for, and explicitly was not authorized to search for, any other feasible reallocation elsewhere in the 360-variable decision space. A different multi-period restructuring not yet proposed could in principle still exist — this was not tested and should not be assumed either way.
- That H1 (legitimate multi-period shifting) is confirmed as a sufficient explanation — this audit shows the *opposite* naive argument (that the pattern is a solver defect) fails, which is consistent with H1/H3 remaining viable, but does not itself prove H1's magnitude case (the full-horizon report's own ≈$1,492 one-time-benefit ceiling argument, §5, is unaffected by this pass either way).
- Anything about hours outside this 24-hour step-0 window, or about whether this same pattern recurs at other MILP-routed steps across the 168h scenario — out of scope, not examined.

No INCONCLUSIVE hour was found: the captured trace contained sufficient data (forecasts, full raw solution vector, SOC trajectory, config constants) to carry the identical hour-20 methodology through to a determinate result for all six remaining hours.

### 1.5 Files created or modified; hash-check results

**Created:** this report (`RT01_SEVEN_HOUR_FEASIBILITY_AUDIT_AND_E2E_READINESS_REPORT.md`) and its mirror in `N6_REMEDIATION_REPORTS/`. **No other file was created, and no existing file was edited.** No script was run; this audit performed only arithmetic over already-persisted JSON, independently re-derivable by any reader from `research/rt01_diagnostics/rt01_step0_full_horizon_trace.json` alone.

**Hash-check (re-verified this pass, SHA-256, compared against the values already on record in `rt01_step0_full_horizon_trace.json`'s `post_execution_hash_manifest` and `POLARIS_MASTER_DECISION_REGISTER.md`'s §36.6 table):**

| File | Status |
|---|---|
| `system/optimization/implementations/milp.py` | match (`3f136ae7...`) |
| `system/optimization/implementations/gap19_highs_native.py` | match (`fd1afe10...`) |
| `system/optimization/implementations/option_d.py` | match (`cdc642f1...`) |
| `system/control/ecd.py` | match (`091358c0...`) |
| `system/control/router.py` | match (`b2a46bc5...`) |
| `system/simulation/simulator.py` | match (`8c44f757...`) |
| `system/runtime/runner.py` | match (`6d1671b6...`) |
| `system/orchestration/manifest.py` | match (`7b775693...`) |
| all 6 config YAMLs (`optimizer`, `battery`, `diesel`, `loads`, `solar_pv`, `station`) | all match |
| `synthetic_168h_endurance_scenario.json` | match (`25bb7fbe...`) |

**Zero mismatches. Every protected file, `milp.py`, every config, and the scenario file remain byte-identical to their already-recorded state.**

**Register (`POLARIS_MASTER_DECISION_REGISTER.md`/`.json`): NOT edited by this pass.** This audit's finding (the swap is infeasible/net-worse at all 7 hours, not just hour 20) strengthens rather than changes any existing register entry — RT-01's `closure_test` is defined in terms of 5 named pytest tests in `system/tests/test_offline_runtime.py`, none of which this audit ran or touched, and `current_state` already correctly reads `decided`/open per §36.5 of the register for independent reasons (2 of those 5 tests still fail). Consistent with the precedent set by this audit's own two immediate predecessor passes (`RT01_FULL_HORIZON_MILP_DIAGNOSTIC_REPORT.md`, `RT01_TIGHT_GAP_VERIFICATION_REPORT.md`), both of which also left the register untouched despite producing substantive diagnostic findings, this pass does the same: the finding is recorded in this standalone report (mirrored to `N6_REMEDIATION_REPORTS/`), not folded into the register, to avoid touching a governance artifact for a result that changes no test outcome, no closure criterion, and no owner decision already on record.

### 1.6 Final decision for Part 1

**INCONCLUSIVE is not the right label — the audit reached a determinate result for every hour. RESOLVED (for the narrow question asked) is also not quite right, since RT-01's full-system closure does not turn on this question alone. The precise classification is:**

**BLOCKER IDENTIFIED — but the blocker is *not* the one hypothesized.** The $7,396.97 "excess cost"/H2 dominance-violation theory that motivated this entire diagnostic thread is **not supported** at any of the 7 flagged hours once checked against the full horizon — the specific swaps proposed are infeasible-as-stated and net-worse-when-corrected at all 7. This closes out the H2-dominance-violation diagnostic line as a dead end (consistent with, and now extending, the tight-gap report's own hour-20 finding). It does **not** resolve RT-01 itself, whose actual, governance-recorded closure blocker is unrelated to this diagnostic thread entirely (Part 2, below).

---

## PART 2 — End-to-End Readiness Decision

**This diagnostic thread is now closed. No further investigation of the H1/H2/H3 dominance-violation question is proposed below or should be pursued from here.**

### 2.1 What is the exact current blocker to a governed end-to-end run?

Per `POLARIS_MASTER_DECISION_REGISTER.md` v1.9.10 §36.1/36.5 (the most current register state) and `POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §6–7: RT-01's own named closure rule requires all 5 of `test_flexible_load_constraints`, `test_flexible_load_no_double_counting`, `test_per_timestep_conservation_audit`, `test_cumulative_physical_conservation_168h`, `test_long_duration_closed_loop_endurance_168h` to pass, **or** a documented **and owner-accepted** explanation plus a relaxed assertion for the residual. **3 of 5 pass; 2 of 5 fail, and the owner has explicitly declined to satisfy the second half of the "or" clause for either:**
- `test_cumulative_physical_conservation_168h`: `renewable_utilization_pct = 69.37% < 75.0%` — owner explicitly declined to waive the 75% floor (register §36.3).
- `test_long_duration_closed_loop_endurance_168h`: `system_reliability_pct = 90.04% ≠ 100.0%` — owner accepted an *explanation* (prototype fuel-tank capacity under a 7-day no-refuel scenario, §36.2) but did **not** authorize relaxing the test's own assertion.

Separately, and independently blocking: the first matched synthetic diesel comparison (needed to produce any diesel-savings or Arm-A/Arm-B evidence) is **confirmed BLOCKED, not run**, by 3 independent prerequisites that remain unmet (`POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §7): the campaign-execution guard is unconditionally un-authorized; `DSL-01`'s `epsilon_tol` remains owner-deferred with no value; and no production-wired (non-mock) multi-origin harness exists to run such a comparison even if the first two were cleared.

### 2.2 Which required tests or acceptance gates remain failing or unverified?

- RT-01 closure set: **2 of 5 failing** (as above), unchanged since the register's most recent (twentieth) pass.
- Full repository test suite (`FULL_SUITE_FAILURE_TRIAGE_ADDENDUM_REPORT.md` §10): **7 of 863 failing** — of these, 2 are the RT-01 168h tests above; 2 are deliberately-left forensic-pin tests awaiting an owner retarget-vs-retire decision (since partially addressed per `POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §3: retarget chosen, not retire — but confirm this is fully applied before counting it closed); 2 are a pre-existing, unrelated test-code method-name typo (`test_critical_load_11_6kw.py`); 1 is an unauthorized research script (`n6_operational_pipeline.py`) building its own router configs with no evidence, awaiting owner decision.
- The matched diesel comparison: **not run, 3 prerequisites unmet** (§2.1 above) — no acceptance gate exists for it yet because it has never been executed.
- `EVID-01`/`EVID-02` (real station `T_required`/critical-load evidence): still `NOT_ESTABLISHED`/`EXTERNAL_EVIDENCE_REQUIRED` — every currently-passing RT-01 test runs on a clearly-labeled **synthetic** fixture (`EVID-TEST-OFFLINE-RUNTIME`), not real-station evidence, so even a hypothetical 5-of-5 pass would demonstrate code correctness "when properly authorized," not production readiness (`POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §6).

### 2.3 What is the single smallest next action that advances the project toward the end-to-end run?

**Obtain one explicit owner decision: whether to relax `test_cumulative_physical_conservation_168h`'s `renewable_utilization_pct >= 75.0` assertion for the current synthetic 168h scenario, or to authorize a bounded engineering investigation into why utilization is 69.37% instead.** This is the single remaining decision blocking RT-01's own stated closure rule (the `system_reliability_pct` residual already has an owner-accepted explanation on record, §36.2 — only the assertion-relaxation half is missing for that one, and might be grantable in the same conversation). Everything else identified above (the diesel comparison's 3 prerequisites, `EVID-01`/`EVID-02`) is a separate, larger, independently-gated decision with no smaller sub-step available; resolving the 75% item is strictly smaller and is the only one of the open items for which the technical investigation (why 69.37%, and whether it is fixable without a config change with "cross-optimizer blast radius," §36.8(ii)) has not yet even been scoped.

### 2.4 Which steps can proceed now, and which remain explicitly blocked?

**Can proceed now (no new owner authorization needed beyond what's already on record):**
- Any further read-only documentation, triage, or reporting work on already-failing/already-classified test items.
- The owner-decision retarget (not retire) of the two forensic-pin tests, if not already fully applied — this was already authorized in principle (`POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §2); verifying it is complete is a bounded, low-risk check.

**Explicitly blocked, pending owner action:**
- RT-01 closure itself (2 of 5 named tests unresolved).
- Any matched diesel comparison, Arm-A/Arm-B evidence, or diesel-savings claim (3 independent, unconditional prerequisite blockers).
- Any campaign execution of any kind (`CampaignExecutionNotAuthorizedError`, unconditional).
- Any training, tuning, or promotion of a control (`winner: null`, unchanged, no owner authorization exists).
- Any production-readiness claim (real `T_required`/critical-load evidence, `EVID-01`/`EVID-02`, remains unestablished regardless of test pass rate).

### 2.5 What constitutes a successful end-to-end result?

A governed end-to-end POLARIS validation, per the standing register criteria, requires **all** of:
1. **Runtime execution:** the real, unmodified `router.py` → optimizer (`GAP19HighsNativeOptimizer`/`LocalMILPEnergyOptimizer`/`option_d.py` fallback as routed) → `DigitalTwinSimulator` pipeline completes the full intended horizon (168h for the endurance scenario) with `constraint_status` genuinely `OPTIMAL`/`FEASIBLE` at every step reached, not a stale or partially-mocked artifact.
2. **Safety/control checks:** all 5 of RT-01's named tests pass, or every residual has **both** a documented owner-accepted explanation **and** an explicitly relaxed assertion (not just one half); the fail-closed `UNKNOWN_INVALID` behavior continues to be exercised and verified wherever authorization is absent (already independently confirmed intact, `FULL_SUITE_FAILURE_TRIAGE_ADDENDUM_REPORT.md` §9); `winner: null`, the campaign guard, and the 75% floor (if retained) remain enforced, not bypassed.
3. **Reproducibility:** bit-for-bit or tolerance-bounded identical results across repeated runs of the same scenario (already demonstrated at the 168h level — `test_long_run_deterministic_replay_168h` passes), and, for any MILP-routed step, insensitivity to MIP-gap tightening (already demonstrated for step 0 in the tight-gap report).
4. **Final evidence:** a complete test-suite run (not a narrowly-reproduced subset) with a fully classified failure list (achieved for the 863-test suite, `FULL_SUITE_FAILURE_TRIAGE_ADDENDUM_REPORT.md` §10) **and**, if any diesel-comparison or savings figure is to be reported, that comparison actually executed against real (not mock) production objects with `EVID-01`/`EVID-02`-grade evidence and a preregistered `DSL-01` significance threshold — none of which exists today.

**A passing diagnostic script or an isolated synthetic-fixture replay (such as every currently-passing RT-01 test) is explicitly not this** — it demonstrates the pipeline's mechanics are sound when properly authorized, not that the full system is production-ready end-to-end. The two are kept distinct throughout this project's own prior reports and are kept distinct here.

---

## Final status

**Part 1: BLOCKER IDENTIFIED (the H2/dominance-violation hypothesis itself is now unsupported at all 7 flagged hours; this closes the diagnostic thread, it does not close RT-01).**
**Part 2: RT-01 remains OPEN. The end-to-end run remains blocked on one explicit owner decision (the 75% renewable-utilization assertion, §2.3) plus three independent, unconditional diesel-comparison prerequisites that remain unmet. No remedy is implemented or recommended by name. Nothing staged, committed, or pushed. `winner: null` unchanged. The 75% floor is preserved exactly as the owner left it (not waived). No further diagnostics on the dominance-violation question are proposed.**
