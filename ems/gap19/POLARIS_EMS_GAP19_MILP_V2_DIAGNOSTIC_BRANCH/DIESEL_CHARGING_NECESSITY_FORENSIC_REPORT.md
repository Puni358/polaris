# Is Stage 8.1's High Diesel+Charging Overlap (96%) Necessary, or Avoidable?

**Scope**: Analysis only, of already-computed R2/diagnostic data plus direct code
inspection, plus one minimal, read-only forensic verification (confirming an equality
constraint's algebraic consequence — no re-solve, no forecast re-generation beyond
inspecting an already-stored cycle). **No code, config, model, or assumption was changed;
no new experiment was run.** Representative case: Stage 8.1, origin 2024-10-04
(`FULL_DIAGNOSTIC_RAW_RESULTS.json`, `constraint_status = OPTIMAL`).

---

## 1. Confirmed facts

### 1a. A structural fact not previously flagged: non-critical demand is unconditionally
unservable in this model, by equality constraints, not by cost

`gap19_highs_native.py:233-236` (constraint "Total Demand Deficit Balance"):
`p_served + p_unmet = demand[t]` (equality).
`gap19_highs_native.py:288-295` (Layer B, "Critical Demand Balance"):
`p_served + P_unmet_crit[t] = critical_demand[t]` (equality).

Both constraints share the **same** `p_served` variable. Since `P_unmet_crit[t] ≥ 0`, the
second equation forces `p_served ≤ critical_demand[t]` **always** — regardless of how much
generation is available. Substituting into the first equation:
`p_unmet[t] = demand[t] − p_served[t] ≥ demand[t] − critical_demand[t] > 0` whenever
`demand[t] > critical_demand[t]` (which is essentially every hour, since
`critical_demand[t] = min(11,600 W, demand[t])`). **Non-critical demand is therefore always
left unmet by construction, with zero objective penalty anywhere** (no `c1`–`c4` coefficient
references the `p_unmet`/`unmet_load` variable at all — only `P_unmet_crit`, via `c1`, is
costed). Confirmed directly in the representative cycle: `unmet_load` is nonzero at **every
one of the 24 hours** (3,400–9,400 W), even at hours with substantial diesel generation and
zero curtailment.

**Consequence**: dispatch in this model is not organized around serving total demand at
all — it is organized around (a) fully serving critical demand (J1, hard priority), (b)
meeting the EBR/terminal reserve SOC trajectory (J2), (c) minimizing diesel fuel (J3), and
(d) minimizing curtailment (J4). "Demand" in the everyday sense plays essentially no role in
the charging decisions examined below.

### 1b. The representative cycle's per-hour trace (Stage 8.1, 2024-10-04, `OPTIMAL`)

| t | diesel (W) | charge (W) | discharge (W) | SOC % | reserve target `e_stage2_target` (Wh) | shortfall (Wh) | curtailment (W) |
|---|---|---|---|---|---|---|---|
| 0 | 40,628 | 32,088 | 0 | 94.76 | 75,652 | 0.0 | 0 |
| 1–6 | 0 | 0 | 6,040–11,600 | 67.24–91.11 | 75,652 | 0.0 | 0 |
| 7 | 59,804 | 50,000 | 0 | 90.24 | 75,652 | 0.0 | 0 |
| 8–20 | 0 | 0 | 1,150–11,600 | 45.22–86.78 | 75,652 → 50,435 | 0.0 | 0 |
| 21 | 19,823 | 8,223 | 0 | 49.00 | 37,826 | 0.0 | 0 |
| 22 | 61,600 | 50,000 | 0 | 72.00 | 25,217 | 0.0 | 0 |
| 23 | 61,040 | 50,000 | 0 | 95.00 | **172,367** | **22,367.0** | 0 |

**Confirmed, directly from this table**: at t=0, SOC is driven to 94.76% while that hour's
own reserve requirement (`e_stage2_target[0] = 75,652 Wh = 37.8%` of the 200,000 Wh
capacity) is already far exceeded — the pre-charge is roughly **2.5× the required level**.
The same pattern recurs at t=7 (SOC reaches 90.24% against the same 75,652 Wh / 37.8%
requirement) and at t=21–22 (SOC already above that hour's own requirement *before* the
charging in question, per the same table). Only the t=23 charging cluster is clearly
oriented toward an unmet need (the 172,367 Wh terminal target, which the plan still falls
22,367 Wh short of even after maxing SOC at 95%).

## 2. Feasible-dispatch evidence

At t=0, t=7, t=21, and t=22, **slack exists in the reserve constraint before that hour's own
charging is applied** — i.e., a dispatch that charged less (or not at all) at those specific
hours, while still meeting that hour's own `e_stage2_target`, is not ruled out by that
hour's constraint in isolation. This is evidence that the charging observed at those hours
is not *locally* forced by the constraint active at that same hour.

**However, this does not establish that an alternative dispatch exists with equal or lower
total diesel fuel.** The reported solve status is `OPTIMAL` — HiGHS's branch-and-bound
MILP solver certifies this as a provably globally fuel-minimal solution (at the J3 priority
tier, after J1/J2 are satisfied) for the given inputs. **This is a confirmed property of the
solver's output, not an assumption**: if a feasible alternative existed using *strictly
less* total diesel while still satisfying J1 and J2 as well as this solution does, HiGHS
would have found it (that is what `OPTIMAL` means for this solver). So: no feasible
alternative with **less** total diesel fuel exists for this cycle, given the current inputs
and constraints.

**What is not established, and cannot be from existing data without a new solve**: whether
an *alternative, equally fuel-optimal* dispatch exists that redistributes this specific
charging to different hours (e.g., deferring the t=0/t=7 charge to be absorbed into the
t=21–23 cluster instead). MILP optimal solutions are not always unique; HiGHS reports one
optimal vertex, not the full optimal set. Determining whether a same-cost alternative
pattern exists would require a new counterfactual re-solve (e.g., forcing
`battery_charge[0]=0` and re-optimizing) — **explicitly out of scope here** ("do not run a
new broad experiment," "do not redesign the optimizer").

## 3. Inference (clearly separated from the above)

- **A plausible, code-consistent explanation for the t=0/t=7 pattern**: the fuel objective
  charges a flat `base_fuel_l_h` (5 L) for every hour diesel runs, *regardless of power
  level* (`gap19_highs_native.py:336-339`), plus a flat 2 L per start. Given this cost
  structure, once diesel must run at a given hour anyway (e.g., to cover critical demand
  when solar is at or near zero — consistent with zero curtailment at t=0/t=7, meaning no
  renewable surplus existed there), using that same hour's "already paid for" base-fuel
  window to also deliver extra charging (marginal cost only 0.00025 L/Wh) is less costly,
  in total 24-hour fuel terms, than deferring that energy need to a separate later hour that
  might require an *additional* start/base-fuel charge. This is **inference**: it is
  consistent with the confirmed cost structure and the confirmed `OPTIMAL` status, but it is
  not independently proven without decomposing HiGHS's internal solution path (not
  attempted here).
- Whether diesel needed to run at t=0/t=7 *at all* (for critical-demand reasons alone, with
  zero charging) was not independently verified from stored data — the per-timestep records
  used here do not include raw solar/wind availability at those hours; confirming "solar was
  exactly zero at t=0/t=7" would need a minimal additional read-only forecast inspection,
  which was not performed in this pass (flagged as unresolved, not assumed).
- The t=23 cluster's charging is well-supported as need-driven (it is explicitly chasing an
  unmet, logged shortfall), unlike the t=0/t=7/t=21-22 instances.

---

## Summary

| Hour cluster | Locally required by that hour's own reserve constraint? | Fuel-optimal given J1>J2>J3 priorities? |
|---|---|---|
| t=0, t=7 | **No** — SOC already ~2.5× the hour's own requirement before charging | Consistent with `OPTIMAL` status (no cheaper alternative found by the solver); pattern-level uniqueness unresolved |
| t=21, t=22 | **No** — SOC already above the hour's own (declining) requirement before charging | Same as above |
| t=23 | **Yes** — plan still falls 22,367 Wh short of this hour's (dominant, terminal-formula-driven) requirement even after charging | Need-driven, not discretionary |

**Overall**: a meaningful share of the diesel+charging co-occurrence in this representative
cycle is **not locally required by the constraint active at that same hour** — it reflects
the solver's joint, whole-day optimization exploiting the flat per-hour diesel cost
structure, not an hour-by-hour physical necessity. At the same time, the `OPTIMAL` solve
status is a **confirmed, solver-certified guarantee that no feasible dispatch uses less
total diesel fuel** for this cycle's inputs — so this is better described as **"not locally
necessary but part of a certified globally fuel-minimal pattern,"** not as "wasteful" in the
sense of leaving cheaper fuel savings on the table. Whether a *differently-timed but
equally-cheap* alternative exists is unresolved and would require a new counterfactual
re-solve, which is out of scope for this report.

## What was NOT done (per instruction)

- No production code, config, model, or assumption was changed.
- No new broad experiment or optimizer redesign was performed.
- Only one representative cycle was traced in full per-hour detail; this is illustrative,
  not a full-window re-quantification (the full-window counterfactual in the prior report
  already established the aggregate 101.5%/−1.5% split; this report examines *why* the
  diesel-charging pattern looks the way it does within that aggregate, for one example).

## STOP

Forensic report complete. No optimizer redesign proposed or implemented.
