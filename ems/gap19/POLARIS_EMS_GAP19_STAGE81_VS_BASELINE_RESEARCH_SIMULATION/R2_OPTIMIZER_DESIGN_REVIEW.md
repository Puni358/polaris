# R2 Optimizer Design Review: GAP19 Terminal-Reserve (J2) Formulation

**Scope**: Review only. No production code, config, or frozen R1/R2 assumption was changed.
No experiment was rerun. All findings below are from direct inspection of
`system/optimization/implementations/gap19_highs_native.py`, the R1/R2 formula
(`run_research_simulation.py`), and the already-computed R2 raw results
(`R2_FULL_EXPERIMENT_RAW_RESULTS.json`). R1/R2 remain frozen, unmodified controls.

---

## 1. Exact J2 calculation (code-confirmed)

Two independent components feed into one unified envelope, then one slack variable absorbs
any shortfall against it, minimized at priority 3:

**(a) Governed EBR 6-hour-lookahead target** (`gap19_highs_native.py:111-131`), applied at
every timestep `t = 0..22`:
```python
for t in range(24):
    end_k = min(t + 6, 24)
    w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
    ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
    ebr_target_wh_list.append(ebr_req_wh)
```
This depends **only on `critical_demand`** (and the fixed `eta_dis = 0.92`) — it never
references `solar_gen`, `wind_gen`, or any renewable forecast anywhere in its definition.

**(b) Terminal reserve target** (`gap19_highs_native.py:134-144`) — the single scalar this
investigation's own R1/R2 research script supplies via `config["terminal_target_wh"]`, not
part of GAP19's own governed logic; GAP19 just consumes whatever value is given.

**(c) Pointwise-maximum envelope, horizon edge only** (`gap19_highs_native.py:146-151`):
```python
e_stage2_target[t] = ebr_target_wh_list[t]   # t = 0..22
e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)  # t = 23 only
```

**(d) Constraint, every timestep** (`gap19_highs_native.py:298-305`):
```
E_next[t] + s_J2[t] >= e_stage2_target[t] + min_e_wh    for all t = 0..23
```

**(e) Objective** (`gap19_highs_native.py:333-334`): `J2 = Σ_t s_J2[t]`, priority 3 (second
highest, after J1 = critical deficit, priority 4).

**Key structural fact, confirmed numerically from R2 data**: `terminal_target_wh` ranges
40,000–172,983 Wh (mean 147,009 Wh) across the R2 run. `ebr_target_wh_list[23]`'s maximum
*possible* value, given `critical_demand` capped at 11,600 W (`loads.yaml`,
`baseline_power_w`) and `eta_dis = 0.92`, is `11,600 × 1h / 0.92 = 12,608.7 Wh`. **Since
147,009 ≫ 12,608.7 (and even the minimum observed terminal value, 40,000, still exceeds
12,608.7), `terminal_target_wh` dominates the `max()` at t=23 in every single cycle of
R1/R2.** The envelope at t=23 is, in practice, entirely the research script's own value —
the governed EBR component at that one timestep is irrelevant to the outcome.

## 2. Lexicographic priority / order (code-confirmed, unchanged fact from prior reports)

`J1 (crit. deficit, priority 4) > J2 (reserve shortfall, priority 3) > J3 (diesel fuel,
priority 2) > J4 (curtailment, priority 1)`, with `blend_multi_objectives = False`
(`gap19_highs_native.py:349`) — a **strict sequential (not weighted) solve**. No numeric
cost trade-off exists anywhere between these tiers; each is solved to its exact optimum
before the next tier is even considered.

## 3. How the terminal target is generated

Entirely outside GAP19, in this investigation's own `run_research_simulation.py:
compute_terminal_target_wh` (a `SIMULATED_RESEARCH_ASSUMPTION`, never a governed value — see
`RESEARCH_EXCEPTION_DECISION_RECORD.md`):
```
terminal_target_wh = 40,000 + max(0, Σ_{k=19..24}(demand[k] − (solar_gen[k]+wind_gen[k]))·1h) × 1.10
```
**This is the only point in the entire R1/R2 pipeline where the reserve envelope is made
sensitive to the solar forecast.** GAP19's own governed EBR formula (§1a) never looks at
solar or wind at all.

## 4. Why satisfying J2 causes diesel-funded charging

Because J2 (priority 3) is minimized *before* J3 (priority 2), the solver will accept any
amount of additional diesel fuel to reduce `s_J2` shortfall, with zero regard for fuel cost,
as long as the resulting diesel/charging plan remains feasible. Raising `E_next[t]` (battery
energy) requires either more solar/wind (fixed by forecast, not controllable) or more
charging power, which draws from the bus-bar balance (`gap19_highs_native.py:227-231`) —
and when solar+wind is insufficient, the only remaining dispatchable source is diesel. So:
lower forecasted solar → (via the R1/R2 formula) higher `terminal_target_wh` → higher
`e_stage2_target[23]` → tighter J2 constraint at t=23 → solver spends diesel (uncapped by any
cost consideration at this tier) to meet it before J3 gets to minimize fuel at all.

**Quantified** (from the prior causal forensic report, re-cited here): of the total +5,265.28
L diesel increase across 245 NORMAL-route origins, 87.3% (4,598.71 L) occurs in the 125
origins where the reserve envelope (J2) binds for at least one arm; `corr(ΔJ2, Δdiesel) =
0.770`, the strongest correlation measured. **Caveat on precision**: because `s_J2` is a
24-element vector and this investigation's stored results only retain the *summed*
`reserve_shortfall_wh` per cycle (not per-timestep), this 87.3% figure cannot be further
decomposed to isolate "shortfall specifically at t=23 (driven by the research formula)" from
"shortfall at t<23 (driven by the governed EBR formula, whose *target* is identical between
arms but whose *bindingness* can still differ because the underlying battery trajectory —
itself solar-driven — differs between arms)." This is flagged as **unresolved** below, not
asserted.

## 5. Interaction with SOC, diesel, and renewable forecasts

- **SOC**: the envelope constraint is a *minimum required energy* floor on top of the hard
  technical minimum (`min_e_wh`), so whenever it binds, it forces the battery's SOC
  trajectory upward relative to what demand alone would require.
- **Diesel**: the only other dispatchable source able to raise `E_next[t]` when renewables
  are insufficient (battery discharge cannot raise its own energy). No fuel-cost ceiling
  exists on this at the J2 tier.
- **Renewable forecasts**: enter the envelope *exclusively* through the R1/R2 research
  formula (§3), not through GAP19's own governed EBR logic (§1a), which is forecast-of-
  renewables-independent by design.

## 6. Does the formulation structurally cause excessive diesel response to accurate solar forecasts?

**Yes — but the structural cause is this investigation's own research formula interacting
with GAP19's existing (unmodified, governed) lexicographic priority — not a flaw inside
GAP19 itself.** Two separate, independently confirmed facts combine:

1. GAP19's own governed reserve logic (EBR) is, by design, insensitive to the renewable
   forecast — it only depends on critical demand. This is **not** where the sensitivity to
   Stage 8.1's (more accurate) solar comes from.
2. The R1/R2 research-only terminal-reserve formula **deliberately** computes its value
   from `demand − renewables`, which is exactly the channel that transmits solar-forecast
   accuracy into the reserve envelope — and GAP19's strict (non-weighted) lexicographic
   priority then converts any increase in that envelope directly into diesel spending, with
   no cost damping, moderation, or trade-off anywhere in the chain.

So the "excessive diesel response" is a composition of (a) a design choice made for *this
research simulation only* (tying the reserve target to the trailing forecasted deficit) and
(b) a genuine, unmodified structural property of GAP19 (strict lexicographic priority, no
cost weighting between reserve shortfall and fuel). Neither alone would necessarily produce
this effect at this magnitude; together, they do.

---

## 1. Confirmed causal problems

- The terminal-reserve envelope at t=23 is, numerically, entirely determined by the research
  script's formula in every single R1/R2 cycle (§1, min 40,000 ≫ max possible EBR value
  12,608.7).
- That formula computes its deficit from the SAME forecast channel (solar) whose accuracy
  this experiment is comparing — so it mechanically amplifies, rather than merely reflects,
  solar forecast differences into dispatch differences. This is a property of our research
  design, not of GAP19.
- GAP19's J2-before-J3 strict priority (unmodified, governed, confirmed from code) means any
  increase in required reserve is paid for in diesel with no cost ceiling — this is an
  existing, real property of GAP19, not introduced by this research.
- 87.3% of the measured diesel increase is associated with reserve-envelope binding events
  (data-confirmed), though the precise share attributable to the t=23 research-formula term
  specifically, versus t<23 EBR-envelope bindingness driven by the differing battery
  trajectory, cannot be separated with the stored per-cycle (not per-timestep) data.

## 2. Optimizer-design issues (GAP19 itself, independent of our research formula)

- **No cost trade-off between reserve shortfall and fuel.** The strict lexicographic order
  means the solver will spend an arbitrarily large amount of diesel fuel to close an
  arbitrarily small amount of reserve shortfall, as long as it is feasible — there is no
  marginal-cost reasoning anywhere between J2 and J3. (This may be an intentional, governed
  design choice — reliability-over-fuel — not necessarily a defect; flagged here as a
  structural property relevant to interpreting this experiment's diesel results, not as a
  recommendation to change it.)
- **The envelope is a single scalar per plan at the horizon edge**, with no visibility into
  what happens beyond the 24h horizon — any "terminal" target is necessarily a proxy for
  un-forecastable future conditions, by construction, for any value one might choose.

## 3. What a MILP v2 should change (description only — NOT implemented)

- Separate, in any future per-timestep instrumentation, the `s_J2[t]` shortfall and its
  binding/non-binding status *per timestep*, not only as a single per-cycle sum — this is
  needed to resolve the §4 caveat (how much of the J2 effect is t=23-only vs. t<23 EBR
  bindingness).
- If a terminal-reserve formula sensitive to renewable forecasts is to be used at all, it
  would need its own authorized numerical calibration (DEC-RES-03) rather than reusing the
  research-only R1/R2 formula — this review does not select or recommend a replacement
  formula.
- Any change to how J2 trades off against J3 (e.g., a bounded/weighted relaxation instead of
  strict lexicographic priority) is itself a governance decision (DEC-TR-05 already recorded
  "secondary lexicographic $J_2$ objective, not a hard constraint" — but "not a hard
  constraint" and "strictly prioritized with no cost trade-off" are not the same thing, and
  this review does not resolve which the governed decision actually intended).

**None of the above is implemented by this review.**

## 4. What must remain unchanged for a fair comparison

- R1 and R2 remain frozen, unmodified controls, exactly as already recorded in
  `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` and `R2_SOLAR_ABLATION_MANIFEST.md`.
- Any future MILP v2 comparison must hold the **evaluation window** (347 origins), **initial
  `StationState`**, **config YAMLs**, **frozen Stage 8.1 model/matrix**, and **wind/demand
  identity between arms** unchanged — exactly as R1/R2 already do — so that only the
  optimizer formulation (not the scenario) differs between R1/R2 and any v2 run.
- Any v2 run must be labeled and frozen (its own manifest, its own hashes) exactly as R1/R2
  were, before any full run, per the same protocol already established.

No code, config, or assumption was changed in producing this review.
