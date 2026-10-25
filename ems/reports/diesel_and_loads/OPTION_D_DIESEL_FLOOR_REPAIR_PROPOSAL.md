# POLARIS — Option-D Diesel-Minimum-Power-Floor Repair Proposal (Phase 2, Proposal Only)

**Date:** 2026-10-18
**Nature of this document:** A narrowly-scoped **implementation proposal**, not an implementation. `system/optimization/implementations/option_d.py` is a `PROTECTED_FILES` entry; this pass's governing directive explicitly did **not** authorize editing it ("Phase 2 ... Not authorized by this instruction. Do not edit option_d.py during Phase 1."). No edit was made. This document identifies the exact violated energy-balance equation, the minimal proposed code change, and the tests needed to prove conservation — it stops there.

---

## 1. The defect, precisely located

`OptionDFallbackSolver.solve()` (`system/optimization/implementations/option_d.py`), in the `ResourceSelection.DIESEL`-preserved branch and the `BOTH`/`TIE`-balanced branch, computes diesel output as:

```python
p_diesel_req = max(min_diesel_w, p_rem_demand_after_bat)   # or p_rem_after_bat in the BOTH branch
p_diesel = min(max_diesel_w, p_diesel_req)
```

`min_diesel_w` (`configs["diesel"]["min_power_w"]`, default 10,000 W) is a **non-dispatchable physical floor**: once the diesel generator is committed to run, it cannot be throttled below this output. When `p_rem_demand_after_bat` (the demand still unmet *after* the battery has already been discharged earlier in the same branch) is positive but **less than** `min_diesel_w`, the generator is forced to produce `min_diesel_w`, which exceeds what is needed by `excess_diesel_w = p_diesel - p_rem_demand_after_bat`.

The code has exactly one mechanism to account for such excess ("5. Excess Diesel Generation Battery Charging"):

```python
if p_diesel > 0 and p_dis == 0:
    excess_diesel_w = max(0.0, p_diesel - p_rem_demand)
    ...
    p_chg = min(max_chg_avail_w, excess_diesel_w)
```

This is gated on `p_dis == 0`. But in exactly the branch combination described above, `p_dis` (the earlier battery discharge) is **already positive** — so this guard is false, the excess-charging logic is skipped entirely, and the excess energy is recorded nowhere: not in `battery_charge[t]`, not in `load_served[t]` (which is explicitly capped — see below — at what was actually needed), and not in `renewable_curtailment[t]`.

Separately, `load_served` accounting caps diesel's contribution to what was needed, independent of what was generated:

```python
p_total_served = p_ren_to_load + p_dis + min(p_diesel, p_rem_demand)
```

`diesel_power.append(p_diesel)` still records the **full**, uncapped value (correctly, for fuel-consumption accounting — the generator did burn fuel to produce it) — but that same full value is never reconciled against any sink.

## 2. The exact violated energy-balance equation

This is not a hypothesis — it is the repository's **own existing invariant**, already encoded in `system/tests/test_offline_runtime.py::test_per_timestep_conservation_audit` (lines ~226–227), which this defect causes to fail:

```
bus_err = abs((sol_u + wind_u + dis + dies) - (serv + flex + chg))
assert bus_err < 1e-1      # fails: observed residual 4658.73 Wh at step 22 (168h endurance scenario)
```

In words: **declared generation** (solar used + wind used + battery discharge + diesel power) must equal **declared consumption + storage** (load served + flexible load + battery charge) at every timestep. The diesel-floor excess described in Section 1 is generation that is counted (it consumes fuel, and is stored in `diesel_power[t]`) but has no corresponding sink in `serv`, `flex`, or `chg` — so the left side exceeds the right side by exactly `excess_diesel_w` whenever the triggering branch combination occurs. This is the `RT01_RT02_FAILURE_FORENSICS_REPORT.md` / `N6_SYNTHETIC_END_TO_END_RUN_REPORT.md`-documented "step-22 residual," independently re-confirmed still present and unchanged by this pass's own re-run (Section 4 of the companion implementation report): `test_per_timestep_conservation_audit` still fails, same mechanism, same signature.

A secondary, related observation: `energy_balance_errors` — a field that exists in the `DispatchPlan` schema apparently *for exactly this purpose* — is hardcoded to `[0.0] * horizon_steps` in `option_d.py` and never actually computed from the dispatch arrays. The plan's own self-reported audit trail currently always claims zero imbalance, unconditionally, regardless of the real underlying residual.

## 3. Minimal proposed code change (NOT implemented)

Two changes, deliberately kept as small and mechanically separable as possible:

**(a) Stop silently dropping the excess.** Change the excess-diesel-charging guard from requiring `p_dis == 0` to computing the excess unconditionally whenever `p_diesel > 0`, and attempt to charge the battery with it regardless of whether the battery also discharged earlier in the same step:

```python
if p_diesel > 0:
    excess_diesel_w = max(0.0, p_diesel - p_rem_demand)
    if excess_diesel_w > 0:
        headroom_dc_wh = max(0.0, max_e_wh - curr_e_wh)
        max_chg_avail_w = min(max_chg_w, headroom_dc_wh / eta_chg)
        p_chg = min(max_chg_avail_w, excess_diesel_w)   # NOTE: see caveat below
```

**Caveat requiring engineering judgment before this is actually implemented:** a real battery cannot physically charge and discharge in the same timestep. If `p_dis > 0` from an earlier step in the same branch, `p_chg` computed here would be charging the *same* battery the code just decided to discharge, in the *same* timestep — numerically "balances the bus bar" but is not physically meaningful as written. The more correct minimal fix addresses the root sequencing instead:

**(a′, preferred) Re-sequence the `ResourceSelection.DIESEL` and `BOTH`/`TIE` branches** so that diesel's mandatory floor (once it is known diesel must run at all) is applied to `p_rem_demand` **before** battery discharge is sized, not after. Concretely, in the `DIESEL`-preserved branch: if `available_fuel > 0` and `p_rem_demand` is low enough that diesel's own floor alone would exceed it, run diesel first at `p_diesel = min(max_diesel_w, max(min_diesel_w, p_rem_demand))` and only discharge the battery for `max(0.0, p_rem_demand - p_diesel)` — i.e. swap the order of the two resource computations so the non-negotiable floor is accounted for before deciding how much (if any) battery backup is still needed, rather than computing both independently against the same `p_rem_demand` figure. This removes the double-supply at its source instead of trying to reconcile it after the fact, and makes `p_dis == 0` whenever diesel's floor alone would have sufficed — at which point change (a)'s original `p_dis == 0` guard becomes correct again, with no physical-simultaneity concern.

**(b) Make the audit trail honest regardless of (a)/(a′).** Actually compute `energy_balance_errors[t]` from the dispatch arrays (`(sol_u + wind_u + dis + dies) - (serv + flex + chg)`) instead of hardcoding `0.0`, so any future residual — from this mechanism or a new one — is visible in the plan's own output rather than silently claimed as zero. This is independent of, and should be implemented alongside, whichever of (a) or (a′) is selected.

**Not proposed:** changing `min_diesel_w`'s value, changing dispatch *priority* semantics (which resource is preserved), or touching anything in `router.py`/`ecd.py` (already addressed, Phase 1) or `gap19_highs_native.py` (unrelated optimizer, not implicated in this mechanism).

## 4. Tests needed to prove conservation (to be written only under separate authorization)

1. **Per-timestep bus-bar conservation**, including the specific previously-failing step-22 residual in the 168h endurance scenario — `test_per_timestep_conservation_audit` and `test_cumulative_physical_conservation_168h` (both already exist in `system/tests/test_offline_runtime.py`; they should pass, unmodified, once the defect is fixed — they are the acceptance test, not new tests to write).
2. **Diesel minimum-power behavior and battery charge/discharge interaction** — a new, narrow unit test directly on `OptionDFallbackSolver.solve()` (bypassing the full pipeline) constructing the exact triggering condition (preserved_resource=DIESEL, a demand step where `0 < p_rem_demand_after_bat < min_diesel_w`) and asserting: no timestep has both `battery_discharge[t] > 0` and `battery_charge[t] > 0`; `diesel_power[t] - load_served_from_diesel[t]` is fully accounted for in `battery_charge[t]` + `renewable_curtailment[t]` (an explicit per-step reconciliation, not just the aggregate bus-bar check).
3. **No double-counting of generated or stored energy** — `test_flexible_load_no_double_counting` (exists) plus a new assertion that the sum of `diesel_power` over the horizon times its fuel-consumption rate matches the fuel actually debited from `available_fuel`/`current_state.diesel_fuel_remaining_liters` (currently this *should* already hold, since fuel accounting uses the same `p_diesel` the bug leaves unreconciled elsewhere — this test would catch a regression if the fix changes `p_diesel`'s value itself rather than just its reconciliation).
4. **Flexible-load constraints and scheduling** — `test_flexible_load_constraints` (exists; currently fails for the same root cause via the full pipeline, not a distinct flexible-load bug).
5. **Long-duration 168-hour physical conservation and reliability regressions** — `test_long_duration_closed_loop_endurance_168h`, `test_long_run_deterministic_replay_168h`, `test_solver_computational_stability_168h`, `test_fair_endurance_milp_vs_rulebased` (all exist in `system/tests/test_offline_runtime.py`).
6. **The previously-failing offline-runtime suite as a whole**, plus the focused RT-01/RT-02 regression file (`system/tests/test_rt01_rt02_failure_forensics_regressions.py`) and the GAP19/Option-D unit suites (`tests/test_gap19_highs_native.py`, `tests/test_gap19_ecd_option_d.py`) — re-run in full, not sampled, before declaring RT-01 resolved.

**RT-01 must not be declared resolved unless every test above actually passes, on a real run, with the physical balance demonstrated numerically (not merely "the code looks right").**

## 5. Authorization required before any implementation

None of the above may be implemented without a **separate, explicit implementation authorization** scoped specifically to `system/optimization/implementations/option_d.py`, naming which of (a) or (a′) in Section 3 is selected (they are not equivalent — (a′) is the structurally correct fix; (a) alone has the physical-simultaneity caveat noted above and should not be implemented as written without first confirming the `p_dis>0` case cannot actually co-occur after fix (a′), or explicitly deciding it is acceptable as a numerically-reconciling-only patch). This proposal does not select between them on the owner's behalf, and no edit to `option_d.py` was made in preparing it.

---

**PROPOSAL ONLY. NO CODE CHANGE MADE. `option_d.py` HASH UNCHANGED (`15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad`, re-verified in the companion implementation report's Section 6). RT-01 REMAINS OPEN.**
