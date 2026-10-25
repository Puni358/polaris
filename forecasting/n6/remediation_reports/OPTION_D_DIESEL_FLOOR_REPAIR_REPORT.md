# POLARIS — Option-D Diesel-Minimum-Power-Floor Repair Implementation Report (RT-01)

**Date:** 2026-10-18
**Authorization:** Explicit, narrowly-scoped owner directive ("POLARIS — Explicit Option-D Physical-Conservation Repair Authorization (RT-01)"), selecting approach **(a′) — sequencing correction**, scoped to exactly one file: `system/optimization/implementations/option_d.py`.
**Baseline document:** `OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md` (repo root, mirrored in `N6_REMEDIATION_REPORTS/`).

---

## 1. Root cause confirmed by the baseline run

Re-read `OptionDFallbackSolver.solve()` before editing and re-ran the baseline tests (command below) to re-establish the state the proposal described, rather than trusting the historical report alone.

**Confirmed mechanism** (exactly as the proposal located it, lines ~135–163 of the pre-fix file): in the `ResourceSelection.DIESEL`-preserved branch and the `BOTH`/`TIE`/`NONE` branch, the battery's discharge (`p_dis`) was sized against the *full* `p_rem_demand` **before** diesel's non-negotiable minimum-power floor (`min_diesel_w`) was applied to the *remainder* (`p_rem_demand_after_bat` / `p_rem_after_bat`). When that remainder was positive but below the floor, diesel was forced to produce more than needed, and the only reconciliation path for that excess ("5. Excess Diesel Generation Battery Charging") was gated on `p_dis == 0` — which was false whenever the battery had already discharged earlier in the same branch, so the excess was recorded nowhere (not curtailed, not charged, not served, not unmet).

**Baseline test run** (before any edit, `option_d.py` SHA-256 = `15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad`, matching the proposal's recorded value exactly):

```
python -m pytest system/tests/test_offline_runtime.py system/tests/test_rt01_rt02_failure_forensics_regressions.py tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py -q
```
Result: **18 failed, 44 passed** (62 collected).

Confirmed by direct re-run that the exact residual the proposal cites is reproduced byte-for-byte:
- `test_per_timestep_conservation_audit`: `4658.729999999996` Wh bus-bar imbalance at **step 22**.
- `tests/test_gap19_ecd_option_d.py::test_O_excess_diesel_charges_battery`: `plan.battery_charge[0]` was `0.0`, not `> 0.0`, under a hand-built demand=4000 W / min_power=10,000 W scenario — the same mechanism, isolated.
- `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestOptionDDieselMinimumPowerExcessGenerationUnaccounted` (mechanism-4 test from the prior pass) reproduced its documented ~6000 W unaccounted excess exactly as recorded.

Of the 18 baseline failures, only **2** are caused by this mechanism at the direct-unit level (`test_O_excess_diesel_charges_battery`, and the mechanism-4 regression test, which was written to assert the *buggy* behavior). The remaining 16 are the pre-existing, unrelated router/ECD fail-closed consequence from the prior pass (see Section 3).

## 2. Sequencing and audit changes made

All changes are confined to `system/optimization/implementations/option_d.py`.

**(a′) Sequencing correction**, applied symmetrically to both affected branches:

- **`ResourceSelection.DIESEL` branch**: after computing `p_diesel` from the floor (`max(min_diesel_w, p_rem_demand_after_bat)`), added: if `p_diesel > p_rem_demand_after_bat` (i.e. the floor actually forced diesel above the true remainder), resize `p_dis = max(0.0, min(max_dis_avail_w, p_rem_demand - p_diesel))`. This makes diesel's floor-constrained output authoritative and shrinks battery discharge so the two resources are never sized against overlapping demand.
- **`BOTH`/`TIE`/`NONE` branch**: identical correction, applied to `p_rem_after_bat` / the 50%-split `p_dis`.
- The correction is a no-op whenever the floor does not bind (i.e. whenever `p_diesel == p_rem_demand_after_bat` would have held anyway, including every case where `max_power_w` — not the floor — is diesel's limiting constraint), so existing dispatch-priority semantics are preserved everywhere except the exact defect condition, per the directive's constraint.
- Verified algebraically and by direct test: when the correction triggers, `p_dis + p_diesel` reduces to exactly `p_rem_demand` (or `0`/`p_rem_demand` in the edge case where the floor alone exceeds total demand), which makes `p_dis == 0` in that edge case — so the pre-existing excess-diesel-charging guard (`if p_diesel > 0 and p_dis == 0:`) now opens correctly and needed **no change itself**.
- The `ResourceSelection.BATTERY` branch was **not** touched — it already computes diesel (with its floor) before sizing battery discharge against the remainder, so it was never affected by this defect.
- Diesel minimum/maximum power, fuel-availability gating, and dispatch-priority order (preserved-resource semantics) are all unchanged.

**(b) Honest `energy_balance_errors`**: replaced the hardcoded `[0.0] * horizon_steps` with a per-timestep computation from the actual dispatch arrays, using the identical sign convention and formula as the repository's own audit (`system/tests/test_offline_runtime.py::test_per_timestep_conservation_audit`):
```python
bus_bar_err = abs((p_sol_used + p_win_used + p_dis + p_diesel) - (p_served_actual + flexible_load_schedule[t] + p_chg))
```
No unit conversion was needed: every quantity is an instantaneous power in Watts applied over a 1-hour timestep, so the numeric residual is equivalently in Wh — the same convention `curr_e_wh`'s own update already uses.

Battery charge/discharge simultaneity, SOC bounds, efficiencies, and fuel-consumption accounting were not touched and remain governed by the pre-existing code.

## 3. New regression test, and exact commands run

Added to `system/tests/test_rt01_rt02_failure_forensics_regressions.py` (the file where the mechanism-4 characterization already lived):

1. **Updated** `TestOptionDDieselMinimumPowerExcessGenerationUnaccounted::test_diesel_min_power_floor_creates_unaccounted_excess_when_battery_also_discharges` — its docstring explicitly anticipated this: *"a correct fix ... should flip this test's assertion to `excess_w == pytest.approx(0.0, abs=1e-3)`."* Updated to assert the corrected values (`battery_discharge == 0`, `diesel_power == 10000`, `battery_charge == 3000`, `excess_w ≈ 0`, `energy_balance_errors[0] ≈ 0`) instead of the previously-documented buggy ones. This is a correction of a test that documented a known bug to assert the authorized fix, not a weakening of any assertion.
2. **New** `TestOptionDDieselFloorRepairAcceptanceRegression::test_partial_battery_discharge_below_floor_reconciles_physically` — the exact condition named by the directive: residual demand after battery dispatch (9000 W) is positive but below the floor (10,000 W), in a case where the battery still ends up discharging a *reduced, nonzero* amount (2000 W) rather than being zeroed out entirely. Asserts: no timestep has simultaneous `battery_charge > 0` and `battery_discharge > 0`; bus-bar reconciliation (`energy_balance_errors ≈ 0`) at every step; fuel consumption matches `base_lph + marginal_lpwh * p_diesel` summed over actual diesel dispatch; SOC stays within `[20%, 95%]`; power stays within configured discharge/charge/diesel limits; diesel never runs below its floor once committed.
3. **New** `TestOptionDDieselFloorRepairAcceptanceRegression::test_both_tie_branch_floor_binding_also_reconciles` — same mechanism in the `BOTH`/`TIE` branch (demand=9000 W, floor=10,000 W exceeds total demand), confirming the symmetric correction and full reconciliation there too.

**Commands run** (all from the repository root, `.venv` activated):
```
python -m pytest system/tests/test_offline_runtime.py system/tests/test_rt01_rt02_failure_forensics_regressions.py tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py -q
python -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -q
python -m pytest tests/test_gate05_synthetic_fixture.py tests/test_ecd_option_d_integration.py tests/test_gate08_ecd_routing_fixture.py tests/test_isolated_components.py tests/test_gate11_option_d_fixture.py tests/test_gate07_fuel_propagation_fixture.py tests/test_gate02_milp_infeasibility_safety.py -q
```
(The last command was run as an extra, non-mandated check of every other test file that directly instantiates `OptionDFallbackSolver`, to catch any regression the mandated list might not surface.)

## 4. Before/after residuals and pass/fail counts

**Step-22 residual** (`test_per_timestep_conservation_audit`, full-pipeline route via `demo_scenario.json`): **unchanged**, `4658.729999999996` Wh, before and after the fix. This is **not** a failure of the fix — see Section 3 below (full-pipeline tests never reach `OptionDFallbackSolver` at all in this environment; this residual comes from a stale pre-existing artifact file, not from a fresh run). The fix **is** proven at the unit level: the isolated mechanism-4 scenario that reproduces this exact defect now shows **0.0** Wh residual (was ~6000 W unaccounted).

**Mandated-file suite, before fix:** 18 failed, 44 passed (62 collected).
**Mandated-file suite, after fix** (including the 2 new tests + 1 updated test): **17 failed, 47 passed** (64 collected).

Net change: **+1 test now passing that was failing before** (`test_O_excess_diesel_charges_battery`), **+1 previously-buggy-behavior test corrected to assert fixed behavior and now passing** (mechanism-4 test), **+2 new acceptance tests passing**. **Zero new failures** introduced. The 17 remaining failures are an exact, unchanged subset of the 18 baseline failures (the 18th, `test_O`, is now fixed) — see Section 3 for the breakdown by cause.

Additional extra-scope check (7 more test files that directly exercise `OptionDFallbackSolver`, not in the directive's mandated list): 15 failed / 38 passed. Of those 15: `test_01_option_d_sha256_unmodified` is an **expected, authorized** failure (it pins a frozen hash that this authorized edit deliberately changes); `test_L_option_d_proportional_allocation`, `test_M_renewable_first_behavior`, `test_P_diesel_not_started_solely_for_charging` fail with `AttributeError: 'DummyBundle' object has no attribute 'solar_generation'` at a line this pass did not touch (pre-existing fixture/interface drift from the earlier, separately-authorized mechanism-2 fix, confirmed unrelated by inspecting the stack trace); the rest are the same pre-existing router/ECD `UNKNOWN_INVALID` fail-closed pattern as Section 3. No new regression found.

## 5. Protected-file and frozen-asset integrity

| File | Before | After | Status |
|---|---|---|---|
| `system/optimization/implementations/option_d.py` | `15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | **Changed — authorized, expected** |
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | *(same)* | Unchanged |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | *(same)* | Unchanged |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | *(same)* | Unchanged |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | *(same)* | Unchanged |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | *(same)* | Unchanged |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | *(same)* | Unchanged |

All six protected-file-besides-option_d.py hashes were re-verified byte-identical before and after this pass. `winner: null`, the sealed 2025 blind partition, frozen Stage 8.1/N6 artifacts, and the campaign lock were not accessed or touched. No file other than `system/optimization/implementations/option_d.py` and `system/tests/test_rt01_rt02_failure_forensics_regressions.py` (test additions/updates) was edited. Nothing was staged, committed, or pushed.

## Verdict

**The diesel-minimum-power-floor sequencing defect in `option_d.py` is fixed and verified at the direct-unit level**: every isolated reproduction of the exact triggering condition (residual demand after battery dispatch positive but below the floor, in both the `DIESEL`-preserved and `BOTH`/`TIE` branches, including the partial-battery-discharge sub-case) now shows a bus-bar residual of `0.0` (down from the ~6000 W / 4658.73 Wh unaccounted excess), no simultaneous battery charge/discharge, correct fuel accounting, and valid SOC/power bounds. `energy_balance_errors` is now genuinely computed from the dispatch arrays rather than hardcoded to zero.

**However, the directive's own full-pipeline acceptance test — `test_per_timestep_conservation_audit`'s step-22 residual — does not pass**, and I am not permitted to, and did not, claim resolution on the strength of the unit tests alone. The reason is a **separate, pre-existing, out-of-scope defect**: `system/control/router.py`'s `evaluate_and_route()` fails closed (`UNKNOWN_INVALID`, `"Target horizon payload is unauthenticated"`) at timestep 0 for both `demo_scenario.json` and `synthetic_168h_endurance_scenario.json`, before `OptionDFallbackSolver` is ever invoked (`completed_steps == 0` in both cases, confirmed by direct re-run). This is exactly the "~37 pre-existing router/ECD fail-closed tests" consequence of the prior, separate ECD/router fail-closed pass described in this session's context — `router.py` is explicitly out of scope and read-only for this task. Because the pipeline never reaches the optimizer, it never regenerates `system/artifacts/latest_dispatch_plan.json`; the file `test_per_timestep_conservation_audit` and `test_flexible_load_no_double_counting` read is a **stale artifact left over from a run that predates both this fix and the router regression**, so its contents (and therefore these two tests' pass/fail outcome) are completely decoupled from `option_d.py`'s current, corrected behavior. The 168h endurance/reliability/replay tests fail for the identical reason (0 completed steps).

**Verdict: RT-01 STILL OPEN** (at the full-system/integration-acceptance level named by the directive), **with the specific diesel-minimum-power-floor mechanism this pass was authorized to fix now demonstrably resolved at the unit/component level**. Full closure of RT-01's own named full-pipeline tests additionally requires the separate, already-identified, out-of-scope router.py critical-load/target-horizon-authorization defect to be fixed under its own authorization — this pass did not and was not authorized to touch it.
