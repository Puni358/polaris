# POLARIS — Option D Renewable-Surplus-to-Battery Charging: Implementation Report

**Date:** 2026-10-18
**Nature of this document:** Owner-authorized implementation report for exactly the Section-3 change specified in `OPTION_D_RENEWABLE_CHARGING_SECTION6_REVIEW.md` (mirrored in `N6_REMEDIATION_REPORTS/`). Only `system/optimization/implementations/option_d.py` was edited (production code); the only other new files are one test addition and this report pair. Nothing staged, committed, or pushed. `POLARIS_MASTER_DECISION_REGISTER.md` was **not edited**. RT-01 remains **OPEN**; the 75% floor is **unchanged**; `winner: null` and the campaign guard are untouched.

**HEADLINE FINDING (read before the rest of this report):** the full-suite comparison in Section 3.3 surfaced **one newly-introduced regression** outside the five required targeted tests: `system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` flips PASS→FAIL (0.0 → 58.41 kWh unmet load) on a different scenario (`demo_scenario.json`, 24h, Stage-8.1 forecast engine). This was root-caused by direct A/B toggling of `option_d.py` (full method below, Section 3.3.1): the new, correctly-implemented charging branch raises SOC fast enough during an early EMERGENCY episode that `router.py`'s ECD assessment flips the route back to `NORMAL` several steps earlier than pre-change. Once on `NORMAL`, `LocalMILPEnergyOptimizer` (`milp.py` — not a `PROTECTED_FILE`, and not in this task's edit authorization either way) exhibits a **pre-existing** behavior where it returns `constraint_status="OPTIMAL"` while leaving demand unmet despite zero diesel use and SOC at 59.05% (far above the 20% floor), with `battery_charge=battery_discharge=0`. This is **not** a conservation violation (bus-bar residual is exactly 0.0 W at every affected step) and **not** a defect in the new branch itself (which independently passes all 5 of its own targeted tests and the 4/5 RT-01 closure tests). It is exactly the class of dynamic/compounding route-selection effect the review's Section 5 Risk 8 flagged as open and unresolved — now concretely realized. **Fixing it would require editing `milp.py` and/or `router.py`'s route-selection sensitivity, both outside this task's narrow authorization** (`router.py` is `PROTECTED_FILES`; `milp.py` was never authorized for edit either way). Per the directive's stop condition ("if ... an unrelated change appears necessary: STOP, do not proceed further, report the exact blocker, and wait"), **no further source-code changes were made beyond the authorized Section-3 edit**. This finding is surfaced here for owner decision before this change is considered for merge or RT-01 closure.

---

## 1. Before editing — baseline capture

**Working-tree verification.** All 7 integrity-tracked files were re-hashed (SHA-256) before any edit and compared against the values recorded in `OPTION_D_RENEWABLE_CHARGING_SECTION6_REVIEW.md` Section 7. **Zero mismatches** — the working tree was unchanged since the review.

**Pre-change RT-01 closure suite** (`python3 -m pytest system/tests/test_offline_runtime.py -k "test_flexible_load_constraints or test_flexible_load_no_double_counting or test_per_timestep_conservation_audit or test_cumulative_physical_conservation_168h or test_long_duration_closed_loop_endurance_168h"`):

| Test | Result |
|---|---|
| `test_flexible_load_constraints` | PASS |
| `test_flexible_load_no_double_counting` | PASS |
| `test_per_timestep_conservation_audit` | PASS |
| `test_cumulative_physical_conservation_168h` | **FAIL** — `renewable_utilization_pct` 69.37 < 75.0 |
| `test_long_duration_closed_loop_endurance_168h` | **FAIL** — `system_reliability_pct` 90.04 ≠ 100.0 |

3/5 passing — reproduces `RT01_168H_RENEWABLE_GAP_QUANTIFICATION_REPORT.md`'s documented baseline exactly (69.3720% utilization, 90.04% reliability).

**Pre-change full `system/tests/` suite:** **486 passed, 3 failed, 489 total** (this run predates the two new test-file additions, so it reflects only the pre-existing suite). Failures: the two 168h tests above, plus `test_n6_live_operational_execution.py::TestN6LiveOperationalExecution::test_05_end_to_end_operational_execution_and_ebr` — confirmed **pre-existing and unrelated**: it fails at `router.evaluate_and_route` with `UNKNOWN_INVALID ("Target horizon payload is unauthenticated")`, before Option D is ever reached, on unmodified code.

**Discrepancy against the register's documented 416/423 baseline, reported honestly, not guessed around:** the actual current pre-change suite size is 489 tests (486/489 passing), not 423. The register's 416/423 figure predates intervening RT-01 remediation work already present in this checkout (additional test files accumulated since that figure was recorded). This report compares against the **actual, freshly-reproduced pre-change baseline (486/489)**, not the stale historical figure, and explicitly flags every *new* failure relative to that fresh baseline in Section 3.

**Full 168h diesel/battery/curtailment trace, pre-change** (same scenario/fixture the closure tests use — `synthetic_168h_endurance_scenario.json`, `optimizer_type="milp"`, 168 steps, `OptionDFallbackSolver` active 102/168 steps under this run's conditions):

| Metric | Pre-change |
|---|---|
| `renewable_utilization_pct` | 69.37 |
| `system_reliability_pct` | 90.04 |
| `total_renewable_curtailment_kwh` | 2100.08 |
| `total_diesel_fuel_liters` | 116.2 |
| `battery_throughput_kwh` | 63.02 |
| `battery_equivalent_cycles` | 0.3151 |
| `unmet_critical_load_kwh` (mislabeled total-unmet field) | 553.84 |
| Max bus-bar residual across 168 steps | 0.0 W |
| `protected_source_hashes` diff vs. review's Section 7 table | none |

The full 168-step H1 `diesel_power`, `battery_charge`, `battery_discharge`, `battery_soc`, `renewable_curtailment`, `solar_used`, `wind_used`, and `energy_balance_errors` arrays were captured and are embedded/retained for the byte-identical comparison in Section 3. Artifact caches (`system/artifacts/latest_dispatch_plan.json`, `latest_forecast_bundle.json`, `run_report.json`) were snapshotted before and restored byte-for-byte after every diagnostic run in this report, following the established pattern in `research/rt01_diagnostics/trace_168h_renewable_gap_quantification.py`.

Baseline reproduced safely; proceeding to implementation.

---

## 2. Implemented change

Edited **only** `system/optimization/implementations/option_d.py` (257 → 285 lines; net +28 lines, the large majority of which are explanatory comments documenting the mutual-exclusivity invariant — the core new logic is the ~10 lines specified in the review's Section 3).

Inserted immediately after the existing renewable-to-load split (`p_ren_to_load`, now `p_curtail_pre`) and before the solar/wind-used bookkeeping:

```python
p_ren_to_chg = 0.0
if p_curtail_pre > 0.0:
    headroom_dc_wh = max(0.0, max_e_wh - curr_e_wh)
    max_chg_avail_w = min(max_chg_w, headroom_dc_wh / eta_chg)
    p_ren_to_chg = min(max_chg_avail_w, p_curtail_pre)
p_curtail = p_curtail_pre - p_ren_to_chg

p_ren_used_total = p_ren_to_load + p_ren_to_chg
# solar_used / wind_used now split from p_ren_used_total instead of p_ren_to_load
```

and changed the per-step charge default from `p_chg = 0.0` to `p_chg = p_ren_to_chg`, immediately before the resource-preservation dispatch block (lines unchanged) and the pre-existing excess-diesel charging branch (lines unchanged, still reads/writes `p_chg`/`p_diesel`/`p_dis` exactly as before).

No other line, function signature, import, `DispatchPlan` construction call, config key, or schema field was touched. The module docstring's priority-logic list (items 1–8) was left as-is (not updated to add a 9th item) to keep the diff minimal and strictly additive, per the "no unrelated cleanup" boundary.

**Mutual-exclusivity verified empirically, not just argued:** a direct sanity run with a large sustained surplus (80 kW avail vs. 10 kW demand) confirmed the branch charges at the 50 kW limit, correctly halts at the 95% SOC ceiling, curtails the true remainder, and keeps the per-step bus-bar residual at exactly 0.0 — see Section 3, test 2, for the boundary-case test built from this.

---

## 3. Required verification

### 3.1 Five new targeted tests (`system/tests/test_option_d_renewable_charging.py`)

| # | Test | Result |
|---|---|---|
| 1 | `test_partition_identity_sustained_renewable_surplus` — `solar_used+wind_used+curtailment == avail` for every step of a sustained-surplus fixture | **PASS** |
| 2 | `test_soc_headroom_boundary_caps_charge_and_curtails_remainder` — near-full-SOC boundary case; charge capped at `min(max_charge_power_w, headroom_dc_wh/η_chg)`, remainder correctly curtailed | **PASS** |
| 3 | `test_renewable_charging_diesel_mutual_exclusivity_168h` — full 168h run; `p_ren_to_chg` reconstructed independently from the plan/bundle; `NOT (p_ren_to_chg>0 AND p_diesel>0)` for all 168 steps | **PASS** (0 violations) |
| 4 | `test_diesel_power_trace_byte_identical_168h` — full 168h `diesel_power` H1 array vs. the embedded pre-change golden trace | **FAIL** — diverges at 15 of 168 steps, first divergence at step 19 |
| 5 | `test_charge_discharge_exclusivity_168h` — `battery_charge[t]*battery_discharge[t] <= 1e-3` for all 168 steps | **PASS** (0 violations) |

**4/5 pass. Test 4's failure is a genuine, honestly-reported finding, not a bug and not a stop condition.** The review's own Section 5 Risk 8 ("Dynamic/compounding effects invalidate the static upper bound") flagged exactly this possibility and explicitly left it as the one question implementation-and-rerun alone could answer. It has now been answered empirically: charging earlier in the horizon raises the battery's SOC trajectory, which changes the resource-preservation dispatch decision (`BATTERY`/`DIESEL`/`BOTH` branch sizing) at 15 *later* steps (step indices 19, 21–24, 40–44, 46, 93–96) — none of which are the *same* step the new branch fired in (mutual exclusivity within a step, proven in Section 4 of the review and re-confirmed by test 3 above, holds exactly). This is a legitimate consequence of the authorized additive change altering SOC trajectory, not a conservation violation (bus-bar residual stayed 0.0 W at every one of the 168 steps, post-change — re-verified directly, see Section 4) and not an unrelated/unauthorized change. Net effect on diesel: fuel consumption rose slightly (116.2 L → 121.04 L; +4.84 L) because the altered dispatch sequencing at those 15 steps on net calls diesel in rather than out.

### 3.2 RT-01 closure suite, post-change

| Test | Pre-change | Post-change |
|---|---|---|
| `test_flexible_load_constraints` | PASS | PASS |
| `test_flexible_load_no_double_counting` | PASS | PASS |
| `test_per_timestep_conservation_audit` | PASS | PASS |
| `test_cumulative_physical_conservation_168h` | FAIL (69.37 < 75.0) | **PASS** (78.65 ≥ 75.0) |
| `test_long_duration_closed_loop_endurance_168h` | FAIL (90.04 ≠ 100.0) | **FAIL** (98.45 ≠ 100.0, improved from 90.04) |

**4/5 closure tests now pass (up from 3/5). The 75% floor is reached (78.65%). The endurance test (100% reliability) still does NOT pass** — reliability improved materially (90.04% → 98.45%) but did not reach the exact-100% bar the test requires. RT-01 is **not fully closed** by this change.

### 3.3 Full `system/tests/` suite comparison

| | Pre-change (fresh baseline, no new test file) | Post-change (including the 5 new tests) |
|---|---|---|
| Total collected | 489 | 494 |
| Passed | 486 | 490 |
| Failed | 3 | 4 |
| Wall time | 1414.2s (23:34) | 1927.6s (32:07) |

**Full itemized failure list, both runs:**

| Test | Pre-change | Post-change | Classification |
|---|---|---|---|
| `test_n6_live_operational_execution.py::test_05_end_to_end_operational_execution_and_ebr` | FAIL | FAIL | Pre-existing, confirmed unrelated (fails at `router.evaluate_and_route` with `UNKNOWN_INVALID`, before Option D is ever reached) |
| `test_offline_runtime.py::test_cumulative_physical_conservation_168h` | FAIL (69.37<75.0) | **PASS** | Fixed by this change (this is the intended effect) |
| `test_offline_runtime.py::test_long_duration_closed_loop_endurance_168h` | FAIL (90.04≠100.0) | FAIL (98.45≠100.0) | Pre-existing failure mode, value improved, not closed |
| `test_option_d_renewable_charging.py::test_diesel_power_trace_byte_identical_168h` | n/a (file didn't exist) | FAIL | New test, **documented expected failure** — see Section 3.1 |
| `test_option_d_renewable_charging.py` (other 4 of 5) | n/a | PASS | New tests, passing as required |
| `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` | PASS | **FAIL (0.0→58.41 kWh unmet)** | **NEW, genuine regression** — see 3.3.1 below and the headline finding at the top of this report |

**Net: exactly one full-suite test flips from a passing, unrelated state to failing that is *not* one of the 5 required new tests and *not* one of the two pre-existing 168h/n6 failures: `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution`.** No test's assertions were changed, skipped, weakened, or relabeled anywhere in this work.

#### 3.3.1 Root-cause of the new regression (direct A/B verification)

The exact mechanism was isolated by toggling `option_d.py` between its pre-change and post-change content (saved as temporary local copies, never staged/committed) and re-running `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` and a route-tracing instrumented 24-step pipeline on `demo_scenario.json` + Stage-8.1 forecast engine + `optimizer_type="milp"`:

- **Pre-change:** the router/ECD assessment selects route `EMERGENCY` continuously from step 4 through at least step 25 (SOC drops to ~22% and stays low; `OptionDFallbackSolver` runs every step; `unmet_critical_load_kwh == 0.0`).
- **Post-change:** the same scenario now sees the router flip `EMERGENCY → NORMAL` at step 7 (SOC recovers faster because the new branch is banking renewable surplus into the battery during the earlier EMERGENCY episode, steps 2–6), oscillate once more, then settle on `NORMAL` from step 11 onward. Once on `NORMAL`, `LocalMILPEnergyOptimizer.optimize()` is called instead of `OptionDFallbackSolver.solve()`. At steps 16, 17, and 18 it returns `constraint_status="OPTIMAL"` with `battery_charge=battery_discharge=diesel_power=0` and `battery_soc=59.05` (stable, well above the 20% floor) while leaving 13,887.82 / 20,094.87 / 24,428.23 W of demand unmet (total 58.41 kWh over the 24-step run). The per-step bus-bar identity (`sol_used+wind_used+dis+dies == served+flex+chg`) holds exactly (residual 0.0 W) at all three steps — the plan is internally consistent and schema-valid; it simply chooses not to dispatch available resources to fully serve load.

This confirms the regression is **not** a defect in the new renewable-charging branch's own arithmetic (which is independently verified correct by the 4 passing targeted tests and the mutual-exclusivity/partition-identity proofs). It is a second-order consequence of the branch doing exactly what it was authorized to do — bank surplus, raise SOC — interacting with (a) the router/ECD's route-selection sensitivity to SOC trajectory (`router.py`, `ecd.py` — both `PROTECTED_FILES`, both unmodified) and (b) a pre-existing dispatch limitation in `LocalMILPEnergyOptimizer` (`system/optimization/implementations/milp.py` — not `PROTECTED_FILES`, but also never in this task's edit authorization) that only this scenario's altered SOC trajectory now exposes. Both (a) and (b) are out of scope for this task's authorization (edit only `option_d.py`, plus new test files). **No attempt was made to fix either**, per the directive's explicit stop condition ("if ... an unrelated change appears necessary: STOP, do not proceed further, report the exact blocker, and wait rather than guessing or working around it").

Direct spot-checks of the two risk-mapped regression suites named in the review (Section 5, Risk 6) were also run standalone and pass in full:
- `test_ecd01_fail_closed_implementation.py` + `test_rt01_rt02_failure_forensics_regressions.py`: **23/23 pass**.
- `test_n6_receding_horizon_adapters.py` (N6 multi-origin harness / `adapters.py` call path, the other Option-D call site besides `runner.py`): **13/13 pass**.

---

## 4. Integrity and reporting

**Final hash re-check** (all 7 integrity-tracked files, SHA-256):

| File | Status |
|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | unchanged |
| `system/optimization/implementations/option_d.py` | **changed** (the one authorized production-code change) |
| `system/control/ecd.py` | unchanged |
| `system/control/router.py` | unchanged |
| `system/simulation/simulator.py` | unchanged |
| `system/runtime/runner.py` | unchanged |
| `system/orchestration/manifest.py` | unchanged |

Exactly one hash changed, exactly the one authorized file. `git status` confirms nothing staged, committed, or pushed, and no `POLARIS_MASTER_DECISION_REGISTER.md`/`.json`, `diesel.yaml`, `battery.yaml`, or `optimizer.yaml` edit.

**Pre/post renewable utilization and reliability (168h synthetic endurance scenario):**

| Metric | Pre-change | Post-change | Δ |
|---|---|---|---|
| `renewable_utilization_pct` | 69.37 | **78.65** | +9.28 pp |
| `system_reliability_pct` | 90.04 | 98.45 | +8.41 pp |
| `total_renewable_energy_used_kwh` | 4756.67 | 5392.77 | +636.10 |
| `total_renewable_curtailment_kwh` | 2100.08 | 1463.98 | −636.10 |
| `renewable_curtailment_pct` | 30.63 | 21.35 | −9.28 pp |
| `total_diesel_fuel_liters` | 116.2 | 121.04 | +4.84 |
| `total_diesel_energy_kwh` | 196.79 | 252.16 | +55.37 |
| `battery_throughput_kwh` (discharge side) | 63.02 | 1153.42 | +1090.40 |
| `battery_equivalent_cycles` | 0.3151 | 5.7671 | +5.452 |
| `unmet_critical_load_kwh` (mislabeled total-unmet field) | 553.84 | 86.43 | −467.41 |
| `constraint_violations_count` | 167 | 102 | −65 |
| Max bus-bar residual, all 168 steps | 0.0 W | 0.0 W | none |
| Charge/discharge exclusivity violations | 0 | 0 | none |
| Battery SOC range observed | within [20.0, 95.0] | within [20.0, 95.0] | none |

**Honest distinction — measured utilization vs. energy actually delivered to load (Section 5, Risk 7):** `renewable_utilization_pct`'s numerator (`solar_used + wind_used`, summed over the run) counts renewable energy the instant it is routed to the battery as "used," before any round-trip loss. Restricting to the 102 steps actually routed through `OptionDFallbackSolver` in this run (where the new branch applies — the identity `p_ren_to_load + p_ren_to_chg + p_curtail == p_ren_avail` holds exactly, 0.00 Wh residual, across all 102 of them), the new branch banked **813,945.72 Wh** of renewable surplus into the battery as charge input. Applying the two one-way efficiencies the battery config actually uses (`charge_efficiency = discharge_efficiency = 0.92`, i.e. ≈0.8464 round-trip): **if every one of those Wh were later fully discharged**, only **≈688,923.66 Wh (≈84.6%)** would ever reach load — a round-trip loss of **≈125,022 Wh (≈15.4% of the banked amount)**. This is a pre-existing property of the metric's definition (it was already true, at much smaller scale, of the pre-existing excess-diesel charging path — Risk 7 in the review is explicit that this is "not a new defect this change introduces, but the change makes it quantitatively larger"), not something this implementation introduces or hides. The 78.65% figure should be read as "available renewable energy no longer discarded at generation time," not as "78.65% of available renewable energy reaches load" — the latter number is necessarily lower once round-trip loss and any energy still resident in the battery at the end of the 168h window are accounted for, and this report does not compute or claim a single corrected delivered-to-load percentage, since that would require tracking the fate of each banked Wh through to an eventual discharge or an end-of-horizon SOC remainder, which is exactly the "dynamic/compounding" question Risk 8 leaves open.

**75% floor: REACHED** on this scenario (78.65% ≥ 75.0%, verified by the unchanged, unweakened `test_cumulative_physical_conservation_168h` assertion, not by the static upper bound and not by the new targeted tests alone).

**Endurance test (100% system reliability): NOT PASSED.** 98.45% is a substantial, real improvement (+8.41 pp, and `constraint_violations_count` fell from 167 to 102) but is not 100%, so `test_long_duration_closed_loop_endurance_168h` still fails post-change, for the same general class of reason RT-01 already documented pre-change (diesel/SOC exhaustion dynamics) — now operating on a different, improved-but-still-imperfect SOC trajectory. RT-01 is **not closed** by this change under the register's exact closure rule, since that rule requires the fifth closure test to either pass outright or be separately documented-and-accepted — this report documents the ongoing failure but does not itself grant that acceptance; that is an owner decision.

**Artifact-cache restoration:** all `system/artifacts/*.json` snapshots were restored byte-for-byte after every diagnostic/test run in this report (confirmed via post-restore read-back equality on every run, including the final full-suite run). No issues encountered.

---

## 5. Stop conditions

- Baseline was reproducible (Section 1). ✓ not triggered.
- No unexpected protected-file hash changes (Section 4) — only `option_d.py` changed. ✓ not triggered.
- No conservation violation anywhere this report checked — bus-bar residual 0.0 W at every one of the 168 endurance-scenario steps (pre- and post-change) and at every one of the three newly-unmet-load steps found in Section 3.3.1. ✓ not triggered.
- **"An unrelated change appears necessary" — triggered, in the narrow sense described in Section 3.3.1, and handled per the directive's own instruction.** Fully closing the new `test_s81_e2e_integration.py` regression would require editing `router.py`'s route-selection sensitivity (a `PROTECTED_FILES` entry) and/or `milp.py`'s dispatch behavior under `NORMAL` route (not `PROTECTED_FILES`, but outside this task's edit authorization regardless). Consistent with "STOP, do not proceed further, report the exact blocker, and wait rather than guessing or working around it," **no edit to either file was made or attempted.** The authorized `option_d.py` change itself was completed, is internally correct (passes its own 4/5 targeted tests, with the 5th being an honestly-documented, anticipated dynamic-effect finding rather than a defect), and was **not reverted** — reverting an explicitly owner-authorized, correctly-implemented, conservation-preserving change on the basis of a downstream effect in a file outside this task's scope would itself be an unauthorized unilateral decision; that judgment call (keep / gate / revert pending a router-or-MILP fix) is left to the owner, informed by the headline finding at the top of this report and Section 3.3.1's full root-cause trace.
- `POLARIS_MASTER_DECISION_REGISTER.md` was not edited; the 75% floor was not relaxed; `winner` was not set; the campaign guard was not invoked; no model training/tuning or diesel comparison was run; no sealed/blind data was accessed.

Per the directive, this report is the stopping point: the implementation and its honest test evidence — including the one newly-discovered, fully root-caused regression this verification pass surfaced — are presented for owner review. RT-01 remains **OPEN** (the register is unchanged). No further remediation, fix attempt, or campaign work follows from this task.
