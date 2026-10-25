# POLARIS — Focused 24-Hour Regression Fix: Report

**Date:** 2026-10-18
**Scope:** Exactly the task authorized by the owner's directive — investigate and, if a safe non-protected-file fix exists, fix `system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` (the regression introduced by the Option D renewable-charging change), while preserving the 168h renewable-utilization improvement and not weakening any governance assertion. **One file was edited: `system/optimization/implementations/milp.py`** (not a `PROTECTED_FILES` entry — confirmed directly against `system/orchestration/manifest.py`, whose `PROTECTED_FILES` list is `gap19_highs_native.py`, `option_d.py`, `ecd.py`, `router.py`, `simulator.py`, `runner.py`; `milp.py` is absent from it). Nothing staged, committed, or pushed. No other file was modified. `router.py` and `ecd.py` were read-only throughout and were **not** the location of the real defect.

---

## Step 1 — Baseline reproduced

The regression was reproduced directly (not assumed) by instrumenting `PolarisLocalRunner.run_pipeline` for the `demo_scenario.json` / `stage81_solar` / `milp` 24-step closed loop, logging route, SOC, fuel, and every `DispatchPlan` field at each step.

**Confirmed causal chain, with exact numbers:**
- Route trace: `NORMAL(0-1) → EMERGENCY(2-6) → NORMAL(7-8) → EMERGENCY(9-10) → NORMAL(11-23)`. The renewable-charging change raises SOC fast enough during the early EMERGENCY episode that the route settles on `NORMAL` from step 11 onward (matches the implementation report's step-7/11 finding).
- At absolute steps **16, 17, 18**, route is `NORMAL`, `LocalMILPEnergyOptimizer.optimize()` returns `constraint_status="OPTIMAL"` with unmet load of **13,887.82 / 20,094.87 / 24,428.23 W** respectively — **58,410.92 Wh ≈ 58.41 kWh total**, matching the implementation report exactly. Diesel fuel remained at 100.0 L (unused) through these steps; SOC stayed flat at 59.05% (battery charge **and** discharge both zero at `rel_t=0` of each call).

**Baseline test results (before any fix), reproduced fresh:**

| Test | Result |
|---|---|
| `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` | **FAIL** (`58.41 != 0.0`) |
| `test_cumulative_physical_conservation_168h` (75% floor) | PASS (78.65%) |
| `test_long_duration_closed_loop_endurance_168h` (100% reliability) | FAIL (98.45%) |
| RT-01 5-test suite | 4/5 |
| Full `system/tests/` suite | 494 collected, 490 passed, 4 failed |

The three other pre-fix failures were the two documented pre-existing 168h findings and `test_n6_live_operational_execution.py::test_05...` (fails at `router.evaluate_and_route` before Option D/MILP is ever reached — unrelated to this task).

---

## Step 2 — Root cause (proven, not assumed) and the minimum fix

**The simulator only ever executes `rel_t=0` of each fresh 24-step MILP solve** (`system/simulation/simulator.py::DigitalTwinSimulator.step` reads `dispatch_plan.battery_charge[0]`, `[0]`, `[0]` only; `runner.py` re-solves a brand-new 24-step look-ahead horizon every real step). This was traced and proven by capturing the exact `c`, `A`, bounds, and solution vector HiGHS returned for step 16's MILP call and testing it directly:

1. **The binary commitment variables `u_chg`/`u_dis`/`u_diesel` carry no cost coefficients anywhere in `milp.py`** (confirmed by direct grep — no `c[base+11]`/`c[base+12]` assignment exists). Combined with a flat, time-invariant objective (`horizon_discount_factor_gamma` defaults to 1.0; `optimizer.yaml` sets no `custom_weight_vector`; the unmet penalty is explicitly "UNWEIGHTED" at every `t`), the MILP is **mathematically indifferent to which relative timestep within its own 24-step horizon bears an otherwise-unavoidable unmet amount** — yet only `rel_t=0` is ever actually executed.
2. **Direct proof of non-optimality:** re-solving the *identical* captured LP/MILP with an added constraint forcing `unmet[rel_t=0] = 0` remained feasible (the battery alone could cover it via discharge, with SOC never approaching the 20% floor) **and produced a strictly lower true objective value** than the original "OPTIMAL" result HiGHS had returned. This proves the original "OPTIMAL" label was not actually globally optimal.
3. **Mechanism:** `scipy.optimize.milp()` was being called with no `options`, so HiGHS used its **default `mip_rel_gap` of 1e-4 (0.01%)**. On an objective of this scale (hundreds of thousands, dominated by `unmet_penalty_per_wh=10.0`), that 0.01% tolerance is large enough in absolute terms to let HiGHS report "Optimal" on an incumbent that leaves an entire real unmet-load event unaddressed at `rel_t=0` while "optimal-but-pointless" diesel-to-battery charging happens later in the same (never fully executed) horizon.

**Minimum safe fix implemented, entirely inside `system/optimization/implementations/milp.py` (not protected):**
- Tightened the solver call to `milp(..., options={"mip_rel_gap": 1e-9})`, forcing HiGHS to prove near-exact global optimality instead of accepting the loose default gap. This directly closes the proven defect in (2)/(3).
- Added a tiny, strictly-decreasing-in-`t` tie-break multiplier on the unmet-penalty coefficient only: `c[base+9] = unmet_penalty_per_wh * dt * (1.0 + 1e-6*(H-1-t))`. `near_term_priority_eps=1e-6` is far below every real cost ratio in the objective (curtailment/diesel/degradation vs. the Wh unmet rate), so it cannot change which *total* unmet amount is optimal anywhere and does not relax or weaken the unmet penalty — it only breaks genuine mathematical ties (item 1) in favor of serving the step that is actually executed, as defense-in-depth alongside the gap fix.

No constraint, bound, penalty magnitude, conservation check, the 75% floor, or the 100% reliability assertion was touched or weakened. No operating mode was forced. No unmet load was hidden — the fix makes the optimizer genuinely serve more real demand, it does not change how unmet is computed or reported.

**Protected-file authorization blocker: none.** The fix did not require touching `router.py`, `ecd.py`, or any other `PROTECTED_FILES` entry.

---

## Step 3 — Verification of both scenarios

**24-hour scenario (demo_scenario.json, stage81_solar, milp):**

| | Before fix | After fix |
|---|---|---|
| `test_10_24h_closed_loop_mpc_execution` | FAIL (58.41 kWh unmet) | **PASS** (0.0 kWh unmet) |
| Steps 16/17/18 unmet | 13,887.82 / 20,094.87 / 24,428.23 W | 0 / 0 / 0 |
| `execution_status` | SUCCESS_CLEAN (but hiding real unmet via a misreported OPTIMAL) | SUCCESS_CLEAN, genuinely |

No unmet load is hidden or ignored; it is genuinely eliminated because the optimizer now actually uses available battery/diesel capacity that was sitting idle. Bus-bar conservation, demand-deficit balance, and charge/discharge exclusivity are enforced by the same unmodified constraint rows throughout (only objective-side coefficients and solver tolerance changed) — reconfirmed by all 14 tests in `test_s81_e2e_integration.py` passing, including `test_11_deterministic_e2e_replay` (bitwise-identical repeat runs) and `test_12_d4c1_fault_containment_preserved`.

**168-hour scenario (synthetic_168h_endurance_scenario.json, re-run via the existing evaluation procedure):**

| Metric | Pre-change (original baseline) | Post Option-D-only (prior report) | Post this fix |
|---|---|---|---|
| `renewable_utilization_pct` | 69.37 | 78.65 | **79.64** |
| `system_reliability_pct` | 90.04 | 98.45 | **99.73** |
| `total_diesel_fuel_liters` | 116.2 | 121.04 | 129.48 |
| `unmet_critical_load_kwh` (total-unmet field) | 553.84 | 86.43 | **14.97** |
| `constraint_violations_count` | 167 | 102 | 102 |

**75% floor: REACHED and improved** (79.64% ≥ 75.0%, verified by the unchanged, unweakened `test_cumulative_physical_conservation_168h` assertion — PASS). **100% reliability: NOT reached** — 99.73% is a large additional improvement (+1.28pp over the Option-D-only result, +9.69pp over the true original baseline) but `test_long_duration_closed_loop_endurance_168h` still asserts exact 100.0% and still fails (99.73 != 100.0). This is reported honestly; the assertion was not relaxed and RT-01's governance rule is not declared satisfied.

Conservation/SOC/exclusivity checks (`test_per_timestep_conservation_audit`, `test_flexible_load_constraints`, `test_flexible_load_no_double_counting`) all pass, same as before.

---

## Step 4 — RT-01 and full regression suite

**RT-01 five-test closure suite:**

| Test | Before this fix | After this fix |
|---|---|---|
| `test_flexible_load_constraints` | PASS | PASS |
| `test_flexible_load_no_double_counting` | PASS | PASS |
| `test_per_timestep_conservation_audit` | PASS | PASS |
| `test_cumulative_physical_conservation_168h` | PASS (78.65%) | PASS (79.64%) |
| `test_long_duration_closed_loop_endurance_168h` | FAIL (98.45%) | FAIL (99.73%) |

**Still 4/5. RT-01 is NOT closed.** The fix materially improves the reliability shortfall (98.45% → 99.73%, i.e. the real unmet-load total across the 168h run fell from 86.43 kWh to 14.97 kWh) but does not reach the exact 100% the governed test requires. Per the directive, this improvement does not itself authorize relaxing or declaring-satisfied that assertion, and no such claim is made here.

**Full `system/tests/` suite, fresh run, compared against the fresh baseline from Step 1:**

| | Before this fix | After this fix |
|---|---|---|
| Total collected | 494 | 494 |
| Passed | 490 | **491** |
| Failed | 4 | **3** |
| Wall time | — | 2203.85s (0:36:43) |

**Itemized failures:**

| Test | Before | After | Classification |
|---|---|---|---|
| `test_n6_live_operational_execution.py::test_05_end_to_end_operational_execution_and_ebr` | FAIL | FAIL | Pre-existing, unrelated (fails at `router.evaluate_and_route` with `UNKNOWN_INVALID`, before MILP/Option D is ever reached) |
| `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` | **FAIL** | **PASS** | **The targeted regression — fixed** |
| `test_offline_runtime.py::test_long_duration_closed_loop_endurance_168h` | FAIL (98.45%) | FAIL (99.73%) | Pre-existing failure mode, value further improved, not closed |
| `test_option_d_renewable_charging.py::test_diesel_power_trace_byte_identical_168h` | FAIL | FAIL | Pre-existing, already-documented expected divergence (dynamic SOC-trajectory effect, not a conservation defect — bus-bar residual 0.0 W throughout; diverges at a different step now because this fix also changes dispatch sequencing, but it was already failing before this fix and remains the same honestly-classified, non-stop-condition finding from the prior report) |

**Net result: exactly one test flips, from FAIL to PASS. Zero new failures were introduced. No test, conservation check, floor, or reliability assertion was weakened, skipped, or relabeled.**

Targeted spot-checks also re-run clean: `test_option_d_renewable_charging.py` (4/5, same documented exception as above), `test_ecd01_fail_closed_implementation.py` + `test_rt01_rt02_failure_forensics_regressions.py` + `test_n6_receding_horizon_adapters.py` (36/36 pass).

---

## Step 5 — Summary

**Proven root cause:** `LocalMILPEnergyOptimizer` (`system/optimization/implementations/milp.py`) solved its 24-step receding-horizon MILP with no cost on the charge/discharge commitment binaries and a flat (unweighted) unmet-load penalty, combined with scipy's default `mip_rel_gap=1e-4`. This let HiGHS report "OPTIMAL" on a solution that left real, serviceable critical demand unmet at `rel_t=0` — the only relative timestep each receding-horizon call actually executes — while "spending" available diesel/battery capacity on an equally-costed but practically pointless later-horizon allocation that is never executed. This was a **latent, pre-existing defect in `milp.py`** (confirmed never protected by `manifest.py`'s `PROTECTED_FILES`); it was not triggered before because the pre-Option-D router stayed in `EMERGENCY` long enough on `demo_scenario.json` that this particular fuel/SOC-scarce `NORMAL`-mode window was never exercised. The Option D renewable-charging improvement's faster SOC recovery (earlier `EMERGENCY→NORMAL` transition) newly exposed it.

**Minimum code changes, exact files modified:** `system/optimization/implementations/milp.py` only — two changes inside `LocalMILPEnergyOptimizer.optimize()`: (a) a tiny strictly-decreasing-in-`t` tie-break multiplier added to the existing, unweakened unmet-penalty coefficient; (b) `options={"mip_rel_gap": 1e-9}` added to the existing `scipy.optimize.milp(...)` call. No other file was touched.

**24-hour result:** before = FAIL, 58.41 kWh unmet. After = **PASS, 0.0 kWh unmet**, genuinely served (not hidden), with conservation/exclusivity/demand-deficit constraints unchanged and still enforced.

**168-hour renewable utilization:** before (Option-D-only) = 78.65%. After this fix = **79.64%** — the 75% floor is preserved and the measured value further improved; verified via the unchanged, unweakened governed test, not asserted from the raw number alone.

**RT-01 (all five tests):** `test_flexible_load_constraints` PASS, `test_flexible_load_no_double_counting` PASS, `test_per_timestep_conservation_audit` PASS, `test_cumulative_physical_conservation_168h` PASS (79.64%), `test_long_duration_closed_loop_endurance_168h` **FAIL** (99.73% vs. required 100.0%, improved from 98.45% but not closed).

**Full regression suite, before vs. after this fix:** 494/494 collected both times; 490 passed / 4 failed → **491 passed / 3 failed**. The targeted regression (`test_10_24h_closed_loop_mpc_execution`) is the one test that flipped, from FAIL to PASS. No new failure was introduced. The two remaining failures are the same pre-existing, already-documented ones (168h endurance reliability, and the 168h diesel-trace byte-identical dynamic-divergence test), neither weakened nor relabeled.

**Protected-file authorization blocker:** none. The fix lives entirely in `milp.py`, which is not in `PROTECTED_FILES`. `router.py` and `ecd.py` were read-only throughout this task and were not where the actual defect lived.

**Is RT-01 actually closed?** **No.** 4 of 5 RT-01 tests pass; `test_long_duration_closed_loop_endurance_168h` still fails because measured system reliability (99.73%) is not exactly 100.0% as the test requires. This report documents a substantial, honestly-measured improvement in that shortfall (98.45% → 99.73%, real unmet load 86.43 kWh → 14.97 kWh over the 168h run) but does not claim closure and has not relaxed the assertion. Closing RT-01 fully remains an owner decision pending further investigation of the residual ~15 kWh of unmet load over 168 hours (likely the same class of degenerate-tie/fuel-scarcity phenomenon at a smaller remaining magnitude, now also present in the Option-D fallback solver's own step-local dispatch choices rather than solely in the MILP horizon, which was out of scope for this focused task).
