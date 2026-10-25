# POLARIS — Section-6 Governance Review: Option D Renewable-Surplus-to-Battery Charging

**Date:** 2026-10-18
**Nature of this document:** Owner-authorized, narrowly-scoped Section-6 `PROTECTED_FILES` governance **review and written change proposal only**, per the verbatim directive "POLARIS — Authorize Section-6 Review of Option D Renewable Charging." This document does **not** implement, patch, prototype, or modify any file. `system/optimization/implementations/option_d.py` was read in full but **not edited**. No protected file, test, config, scenario, or governance-register file was touched. No pipeline, campaign, diagnostic, training/tuning run, or diesel comparison was executed. Nothing staged, committed, or pushed. RT-01 remains **OPEN**; the 75% floor is **unchanged**; `winner: null` and the campaign guard are untouched. This review does **not** assume the 75% floor will be achieved by the proposed change — that remains this review's own open question.

---

## 1. Exact scope and files inspected

**Authorizing evidence carried forward (not recomputed):** `RT01_168H_RENEWABLE_GAP_QUANTIFICATION_REPORT.md` — baseline `renewable_utilization_pct = 69.3720%`; `OptionDFallbackSolver` active steps 1–167 of 168 (99.4%); total curtailment 2,100,084.63 Wh; only 385,897.18 Wh (18.4% of total curtailment) of additional recovery needed to clear the 75% floor; static per-step eligibility bound (SOC ceiling, 50 kW charge limit, 0.92 efficiency) = 100% of curtailment on the observed trajectory, with dynamic/compounding recovery explicitly flagged as unproven; bus-bar residual exactly 0.0 W across all 168 steps in the unmodified code. Also carried forward: `RT01_69PCT_RENEWABLE_UTILIZATION_GAP_INVESTIGATION.md` (confirms Option D's only charging path is gated on excess diesel, never renewables) and `RT01_STEP0_MILP_DISPATCH_ROOT_CAUSE_REVIEW.md` (unrelated `milp.py` finding, not in scope here; confirms `PROTECTED_FILES` has exactly 6 entries, `manifest.py` itself is hashed as a 7th integrity-tracked file by convention).

**Files read this pass (read-only):**
- `system/optimization/implementations/option_d.py` — in full (257 lines; the file under review).
- `system/optimization/interface/base.py` — `EnergyOptimizer` abstract interface.
- `system/orchestration/manifest.py` — `PROTECTED_FILES` constant and hashing logic.
- `system/schemas/dispatch_plan.py`, `system/schemas/station_state.py` — schema contracts `DispatchPlan`/`StationState` that bound what Option D may return.
- `system/control/ecd.py` (`EmergencyAssessment`, `ResourceSelection` definitions only).
- `system/config/battery.yaml`, `system/config/optimizer.yaml`, `system/config/diesel.yaml` — live config values.
- `system/runtime/runner.py` (lines 70–170) and `system/orchestration/worker.py` — confirmed exactly how/where `OptionDFallbackSolver.solve()` is invoked (`route == "EMERGENCY"` branch only).
- `system/tests/test_offline_runtime.py` — the 5 named RT-01 closure tests plus the adjacent conservation/double-counting/flexible-load/battery-bounds tests, read in full to extract their exact assertions.
- `POLARIS_MASTER_DECISION_REGISTER.md` — confirmed RT-01's open status and closure rule.

**Not read/executed (out of scope, per directive):** `gap19_highs_native.py`'s full body (already summarized in prior reports — bus-bar balance places solar/wind-used and `p_chg` on the same equation), `router.py`/`simulator.py` internals beyond confirming the call site, any scenario/fixture data, any sealed/blind data, any test run, any pipeline run.

---

## 2. Current dispatch logic relevant to this review (as read, unmodified)

`OptionDFallbackSolver.solve()` runs a 24-step loop. Per step `t`:

1. `p_ren_avail = p_solar_avail + p_wind_avail` (forecast renewables).
2. `p_ren_to_load = min(p_ren_avail, p_crit_demand)`; **`p_curtail = max(0.0, p_ren_avail - p_ren_to_load)`** (line 106) — any renewable above critical demand is curtailed unconditionally. This is the single line that structurally forecloses renewable-to-battery charging.
3. `p_rem_demand = p_crit_demand - p_ren_to_load` drives a resource-preservation branch (`BATTERY`/`DIESEL`/`BOTH`) that may set `p_diesel` and/or `p_dis`.
4. The **only** existing charging path (lines 192–199): `if p_diesel > 0 and p_dis == 0: p_chg = min(max_chg_avail_w, excess_diesel_w)` — charges only from diesel generation that exceeds remaining demand, gated on the battery not discharging that same step.
5. `curr_e_wh += (p_chg * eta_chg - p_dis / eta_dis)`, clipped to `[min_e_wh, max_e_wh]`.
6. `energy_balance_errors[t] = abs((p_sol_used + p_win_used + p_dis + p_diesel) - (p_served_actual + flex + p_chg))` — the bus-bar identity the repository's own conservation tests re-derive independently.

**Key structural fact established by direct read, not previously stated this precisely:** `p_curtail > 0` (step 2) is algebraically possible **only when** `p_ren_avail >= p_crit_demand`, which forces `p_rem_demand = 0`. Since `p_diesel` and `p_dis` are only ever set inside the `if p_rem_demand > 0:` block (lines 130–191), **curtailment and the demand-dispatch block (and therefore the existing diesel-excess charging branch) are mutually exclusive within a single step** — they never both fire. This is the load-bearing fact that makes the proposed insertion point low-risk (Section 4).

`OptionDFallbackSolver` does not literally implement `EnergyOptimizer.optimize(forecast_bundle, station_state, config)` — it is called separately in `runner.py`/`worker.py` as `solve(assessment, bundle, current_state, configs)` on the `route == "EMERGENCY"` branch, alongside (not through) the `EnergyOptimizer` interface used for `route == "NORMAL"`. The common contract both paths must satisfy is the output: a schema-valid `DispatchPlan` (24-entry, non-negative, charge/discharge-exclusive, finite) whose fields are consumed identically downstream by `simulator.py` and `evaluator.py` regardless of which solver produced them.

---

## 3. Proposed minimal change

Insert a new branch **between** step 2 (renewable-to-load split) and the solar/wind-used bookkeeping, using the renewable surplus that step 2 already computes. No other line in the file needs to move; no new config key, schema field, or interface change is required.

```text
# existing, unchanged
p_ren_to_load = min(p_ren_avail, p_crit_demand)
p_curtail_pre = max(0.0, p_ren_avail - p_ren_to_load)
p_rem_demand  = p_crit_demand - p_ren_to_load          # == 0 whenever p_curtail_pre > 0

# NEW: renewable-surplus-to-battery charging
#   - fires only when there IS a renewable surplus (p_curtail_pre > 0), which by
#     the invariant above means p_rem_demand == 0 this step, i.e. this branch
#     can never be live in the same step as the demand-dispatch block that sets
#     p_diesel/p_dis -- see Section 4 for why this makes the two charging paths
#     mutually exclusive by construction, not by an added guard.
p_ren_to_chg = 0.0
if p_curtail_pre > 0.0:
    headroom_dc_wh   = max(0.0, max_e_wh - curr_e_wh)       # same SOC-ceiling expr as existing excess-diesel path
    max_chg_avail_w  = min(max_chg_w, headroom_dc_wh / eta_chg)  # same charge-power/efficiency expr as existing path
    p_ren_to_chg     = min(max_chg_avail_w, p_curtail_pre)

p_curtail = p_curtail_pre - p_ren_to_chg                 # final curtailment reported, replaces old p_curtail

# existing solar/wind split, EXTENDED to include the newly-charged renewable energy
# so that renewable_utilization_pct's numerator (solar_used + wind_used) reflects
# surplus that was banked, not just surplus that served load directly
p_ren_used_total = p_ren_to_load + p_ren_to_chg
if p_ren_avail > 0:
    p_sol_used = p_ren_used_total * (p_solar_avail / p_ren_avail)
    p_win_used = p_ren_used_total * (p_wind_avail  / p_ren_avail)
else:
    p_sol_used = 0.0
    p_win_used = 0.0

# ... (resource-preservation / diesel / battery-discharge block: UNCHANGED) ...

# existing default, CHANGED from literal 0.0 to the renewable charge computed above
p_chg = p_ren_to_chg      # was: p_chg = 0.0
p_dis = 0.0
p_diesel = 0.0

# ... (existing excess-diesel charging branch at lines 192-199: UNCHANGED, and
#      per Section 4 can never overwrite a nonzero p_ren_to_chg in the same step) ...

# curr_e_wh update, bus-bar energy_balance_errors computation, served/unmet
# accounting: ALL UNCHANGED -- they already consume p_chg, p_sol_used,
# p_win_used, renewable_curtailment generically and do not need to know the
# charge came from renewables rather than diesel.
```

**Net diff footprint:** roughly 8–10 new/changed lines, all inside the per-timestep loop, none touching the function signature, the `DispatchPlan` construction call, imports, or any other file.

---

## 4. Interactions with the rest of the dispatch contract

- **Battery discharge (`p_dis`):** Proven mutually exclusive with the new branch within a step, because `p_curtail_pre > 0 ⇒ p_rem_demand == 0 ⇒` the only block that can set `p_dis` never executes. The existing cross-step exclusivity check in `DispatchPlan` (`charge[t] * discharge[t] <= 1e-3`) is therefore satisfied by construction, not by a new runtime guard — this should still be exercised by a regression test (Section 5) rather than taken on faith.
- **Diesel dispatch (`p_diesel`) and the existing excess-diesel charging branch:** Same mutual-exclusivity argument — `p_curtail_pre > 0 ⇒ p_rem_demand == 0 ⇒ p_diesel` stays at its loop-start default of `0.0` for that step, so the line-194 condition `p_diesel > 0 and p_dis == 0` is false whenever `p_ren_to_chg > 0`, and the new initialization `p_chg = p_ren_to_chg` is never overwritten by the old branch in the same step. The two charging paths are therefore additive-safe without needing to be combined into one expression — but this is exactly the kind of invariant that should be asserted directly by a test (Section 5), not just argued in a review document, since a future change to either branch could silently break it.
- **Emergency routing / ECD (`router.py`, `ecd.py`):** No change proposed to either file (both remain `PROTECTED_FILES`, untouched, hashes re-verified below). The new branch only consumes `assessment`/`bundle`/`current_state` the same way the existing code already does; it does not change which route (`NORMAL`/`EMERGENCY`) is selected, nor `preserved_resource`/`limiting_resource` semantics. Because EMERGENCY/Option-D governs 167 of 168 steps in the diagnosed scenario, this is also where essentially all of the available recovery opportunity lives — consistent with the RT-01 quantification.
- **`EnergyOptimizer` interface / `GAP19HighsNativeOptimizer`:** No change. `base.py`'s abstract `optimize()` contract is not touched; Option D does not implement it and this proposal does not change that. The new branch makes Option D's charging *behavior* more like GAP19's (which already allows surplus renewables onto the bus-bar's `p_chg` term), but does not merge, delegate to, or alter GAP19's code — `gap19_highs_native.py` remains fully untouched.
- **Downstream consumers (`simulator.py`, `evaluator.py`):** Both already consume `solar_used`/`wind_used`/`battery_charge`/`renewable_curtailment` generically (they do not care which solver, or which internal cause, produced a given `DispatchPlan`'s numbers). No schema or evaluator change is implied or required.

---

## 5. Risks and the evidence required to clear each one

| # | Risk | Mechanism by which the proposed change could cause it | Evidence/test required to clear it |
|---|---|---|---|
| 1 | **Energy non-conservation at the bus bar** | A coding error in the new branch adds energy to `solar_used`/`wind_used` without a matching addition to `p_chg` (or vice versa) | `test_per_timestep_conservation_audit` and `test_cumulative_physical_conservation_168h` bus-bar residual must stay < 0.1 W per step across the full 168h run (same threshold already enforced) |
| 2 | **Double-counting of renewable energy** (counted as both "used for load" and "charged to battery", or counted in `renewable_utilization_pct` while *also* still appearing in `renewable_curtailment`) | `p_ren_to_load` and `p_ren_to_chg` must partition `p_ren_avail` without overlap; `p_curtail` must equal `p_curtail_pre - p_ren_to_chg` exactly | A new targeted assertion: for every step, `p_ren_to_load + p_ren_to_chg + p_curtail == p_ren_avail` (within float tolerance); `test_flexible_load_no_double_counting`'s existing bus-bar identity must still hold unchanged |
| 3 | **SOC ceiling or charge-power limit violated** | `headroom_dc_wh`/`max_chg_avail_w` computed incorrectly, or the new branch's `p_chg` combines badly with a later, unrelated SOC clip | `test_battery_physics_exclusivity_and_bounds` (SOC in `[19.99, 95.01]`, `battery_charge[t] <= max_charge_power_w`) must still pass; a new test should specifically push a scenario with large renewable surplus near a near-full SOC and assert the charge is correctly capped, not just incidentally within bounds |
| 4 | **Charge/discharge exclusivity violated** | The mutual-exclusivity argument in Section 4 is wrong, or a future edit breaks it silently | A new explicit regression assertion: for every step, `NOT (p_ren_to_chg > 0 AND p_diesel > 0)` and `NOT (battery_charge[t] > 0 AND battery_discharge[t] > 0)` — the latter is already checked by `DispatchPlan`'s constructor-level validator and by `test_battery_physics_exclusivity_and_bounds` |
| 5 | **Diesel dispatch regression** (diesel runs more, less, or at different times than before, changing fuel economics or the "diesel never started solely to charge battery" rule in the file's own docstring) | Should be impossible in principle, since the new branch never sets `p_diesel` and never fires in the same step the diesel-dispatch block fires — but this is exactly the kind of "should be impossible" claim that needs direct verification | `test_diesel_fuel_conversion_consistency`, `test_diesel_min_max_limits` must be unaffected; diff the full 168-step `diesel_power` array before/after the change and confirm it is byte-identical (a stronger check than just "tests still pass") |
| 6 | **Emergency-routing/fallback regression** (change alters `assessment`/route selection, or Option D's behavior under a route other than the one tested) | The new branch does not read or write `assessment.preserved_resource`/`limiting_resource`, and does not change which route `router.py` selects — but Option D is also invoked from `worker.py` and the N6 multi-origin harness (`adapters.py`), not only `runner.py` | Re-run (post-implementation only) the targeted Option D unit tests already in the repo that call `OptionDFallbackSolver().solve(...)` directly (`system/tests/test_rt01_rt02_failure_forensics_regressions.py`, `test_ecd01_fail_closed_implementation.py`) to confirm they still pass unmodified |
| 7 | **Metric-gaming without physical benefit** (renewable energy banked into the battery and credited as "used" in `renewable_utilization_pct`, but a meaningful fraction is lost to the 0.92/0.92 round-trip efficiency before ever reaching load) | This is a property of the **existing** metric definition (`used = available − curtailed`, honest "not thrown away immediately" accounting, already true of the pre-existing diesel-excess charging path) — not a new defect this change introduces, but the change makes it quantitatively larger | Not a pass/fail test, but should be stated in any future owner decision: report both `renewable_utilization_pct` **and** the round-trip-loss-adjusted Wh actually delivered to load from battery-sourced renewable charge, so the owner is not presented with a metric improvement that overstates physically delivered energy |
| 8 | **Dynamic/compounding effects invalidate the static upper bound** | Charging earlier raises SOC entering later steps, which can change discharge headroom, EMERGENCY routing persistence, or diesel usage later in the horizon — RT-01's own §3.5 explicitly flags this as unproven | This is the central open question this review does **not** resolve. It can only be cleared by actually implementing the change and re-running the full 168h closure suite (Section 6) — which is implementation, not review, and is explicitly out of scope here |

---

## 6. Required tests and acceptance criteria

**New targeted tests required before implementation can be considered complete** (conservation / SOC / no-double-counting / mutual-exclusivity, scoped to the new branch):
1. Partition identity: `p_ren_to_load + p_ren_to_chg + p_curtail == p_ren_avail` (± 1e-6) for every step of a scenario with sustained renewable surplus.
2. SOC-headroom boundary case: construct a step where surplus renewable exceeds remaining charge headroom and assert `p_ren_to_chg` is capped at `max_chg_avail_w`/headroom, with the *remainder* correctly still curtailed (not silently dropped or double-applied).
3. Mutual exclusivity: for every step across a full run, assert `NOT (p_ren_to_chg > 0 AND p_diesel > 0)`.
4. Byte-identical diesel trace: `diesel_power` array unchanged vs. the pre-change baseline on the same 168h scenario (stronger than "tests pass").
5. Charge/discharge exclusivity preserved (already enforced by `DispatchPlan`'s constructor, re-confirmed via `test_battery_physics_exclusivity_and_bounds`).

**Exact five-test RT-01 closure suite** (unchanged, per the governance register's existing closure rule — must all pass or be documented-and-accepted per the rule's disjunction):
```
python3 -m pytest system/tests/test_offline_runtime.py -k "test_flexible_load_constraints or test_flexible_load_no_double_counting or test_per_timestep_conservation_audit or test_cumulative_physical_conservation_168h or test_long_duration_closed_loop_endurance_168h"
```
- `test_flexible_load_constraints`: unaffected by this change (flexible load is independent of the new branch; `flexible_load_schedule` stays hardcoded to zero in Option D).
- `test_flexible_load_no_double_counting`: `total_supplied == total_consumed` bus-bar identity must still hold (± 0.1 W) — directly exercises this change's core conservation claim.
- `test_per_timestep_conservation_audit`: bus-bar, demand-decomposition, and renewable-decomposition residuals must stay < 0.1 W per step.
- `test_cumulative_physical_conservation_168h`: `renewable_utilization_pct >= 75.0` — this is the floor the change is intended to help clear, **not guaranteed by this review**, plus the already-separate honest-labeling assertion on `critical_unmet_source` (unaffected by this change).
- `test_long_duration_closed_loop_endurance_168h`: `system_reliability_pct == 100.0` — currently fails at 90.04% for reasons RT-01 has already documented as unrelated to curtailment (diesel/SOC exhaustion dynamics); this change could in principle move this number (for better or worse) since it alters SOC trajectory — must be re-checked, not assumed unaffected.

**Acceptance criteria for implementation (not met by this review, listed for the follow-on decision):** all 5 new targeted tests pass; all 5 closure tests either pass outright or, if not, are documented and accepted under the register's existing disjunctive rule exactly as `test_long_duration_closed_loop_endurance_168h` already is; the 7 `PROTECTED_FILES`/`manifest.py` hash table is regenerated and the diff is limited to `option_d.py` alone; the full `system/tests/` suite (416/423 baseline per the register) shows no *new* failures beyond the pre-existing/RT-01-dispositioned set.

---

## 7. Integrity status

All 7 files independently re-hashed (SHA-256) this pass and compared against the values recorded in `RT01_168H_RENEWABLE_GAP_QUANTIFICATION_REPORT.md` / `RT01_69PCT_RENEWABLE_UTILIZATION_GAP_INVESTIGATION.md`:

| File | Hash (abbreviated) | Status |
|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10...18a2e737` | match |
| `system/optimization/implementations/option_d.py` | `cdc642f1...911be62511` | match |
| `system/control/ecd.py` | `091358c0...fd9e41c96db` | match |
| `system/control/router.py` | `b2a46bc5...87bc9074e90f3` | match |
| `system/simulation/simulator.py` | `8c44f757...fceed4204c74b3c5e5f` | match |
| `system/runtime/runner.py` | `6d1671b6...a5680d062f8dc53b10` | match |
| `system/orchestration/manifest.py` | `7b775693...a6c75610c12c927d8bb35` | match |

**Zero mismatches. All 7 hashes identical to the recorded baseline.** No file was opened for writing other than this report and its `N6_REMEDIATION_REPORTS/` mirror. `git status` continues to show the entire `system/` tree as untracked (`??`) — the pre-existing baseline in this no-commits-yet repository; nothing was staged or committed by this pass.

---

## 8. Recommendation

**IMPLEMENTATION REVIEW JUSTIFIED.**

Reasons:
- The mechanism is now understood precisely enough to specify an exact, minimal (~8–10 line) insertion point, with no interface, schema, or cross-file contract change required.
- The two charging paths (existing diesel-excess, proposed renewable-surplus) are **provably mutually exclusive within a step** from the existing code's own structure (`p_curtail_pre > 0 ⇒ p_rem_demand == 0 ⇒ p_diesel/p_dis stay at 0`), not merely by an added guard — this substantially lowers the risk that the change interferes with diesel dispatch, battery discharge, or emergency routing.
- Energy conservation is preserved **by construction**, not by a follow-on reconciliation step: the same Wh added to `solar_used`/`wind_used` (source side) is added to `p_chg` (sink side) of the identical bus-bar equation the repository's own tests already check.
- The RT-01 quantification shows a wide margin (only 18.4% of total curtailment needs recovering against a static upper bound of 100%), meaning even a materially imperfect dynamic realization of this change has room to still clear the 75% floor.
- Every risk identified in Section 5 maps to a concrete, specific test or diff check already namable in terms of this repository's existing test idioms (bus-bar residual, SOC bounds, charge/discharge exclusivity, byte-identical diesel trace) — none requires inventing new unverifiable criteria.

Explicit caveats, carried forward unweakened:
- **This review does not demonstrate the 75% floor will be reached.** The static upper bound (100%) is a frozen-trajectory calculation; RT-01 §3.5/§3.6 and this review's own Section 5, Risk 8 both flag that dynamic/compounding effects of a higher SOC trajectory on later-step dispatch remain unproven and can only be resolved by actually implementing the change and re-running the closure suite.
- **This review is not an implementation authorization.** Per the directive's stop condition, the next step is a separate owner decision to authorize implementing exactly the change specified in Section 3, subject to the tests in Section 6, followed by re-verification of all protected-file hashes and the full test suite before RT-01 can close.
- RT-01 remains **OPEN**; the 75% floor is **unchanged**; `winner: null` and the campaign guard are **untouched** by this review.
