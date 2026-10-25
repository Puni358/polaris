# MILP-v2 Diagnostic Branch: Causal Decomposition Report

**Scope**: Diagnostic instrumentation only. R1/R2, production code
(`gap19_highs_native.py`), and all frozen research assumptions are **unmodified** — the
real, unmodified `GAP19HighsNativeOptimizer.optimize()` was called exactly as R1/R2 call it;
no objective, weighting, constraint, or terminal formula was changed. Validated on a small,
deliberately chosen 3-origin / 6-cycle replay (`DIAGNOSTIC_REPLAY_RESULTS.json`), not a rerun
of the full 347-origin R1/R2 experiment.

**Instrumentation added**: `diagnostic_instrumentation.py` exposes, per timestep, for each
already-solved (unmodified) `DispatchPlan`: the native EBR target, the research
terminal-target's value, which one dominates the pointwise-max envelope, the per-timestep
`s_J2` shortfall (already present in `DispatchPlan.reserve_shortfall` but never inspected
per-element before this), diesel/battery/SOC/curtailment/unmet-load per timestep, and J1–J4
totals. The EBR-target replica (`replicate_ebr_target_wh_list`) and envelope replica
(`replicate_e_stage2_target`) are the exact formulas from
`gap19_highs_native.py:126-131,146-151`, copied verbatim for read-only replay — not
re-derived or approximated.

**Stated limitation (carried into every result below)**: attributing diesel to a specific
timestep's binding status is a **same-timestep association**, not a rigorous causal
isolation. GAP19 solves all 24 hours jointly; diesel at one hour can serve a reserve
requirement that only binds at another hour. A true isolation would require a counterfactual
re-solve with a component removed — explicitly out of scope here ("do not change optimizer
behavior yet").

---

## Instrumentation validation (3 origins, 6 cycles, all `OPTIMAL`, all `NORMAL` route)

| Origin | Engine | `terminal_target_wh` | `ebr_target[23]` (fixed) | Binding timesteps |
|---|---|---|---|---|
| 2024-08-12 | baseline | 148,596.5 | 12,608.7 | none |
| 2024-08-12 | stage8_1_corrected | 152,490.1 | 12,608.7 | **[23] only** |
| 2024-06-19 | baseline | 148,596.5 | 12,608.7 | none |
| 2024-06-19 | stage8_1_corrected | 147,368.6 | 12,608.7 | none |
| 2024-06-01 | baseline | 148,596.5 | 12,608.7 | none |
| 2024-06-01 | stage8_1_corrected | 145,351.8 | 12,608.7 | none |

Confirms, per-cycle (not just by magnitude argument as in the prior review):
`terminal_target_wh` dominates the t=23 envelope in all 6 cycles (it is always ≥
`ebr_target[23]`, which is fixed at 12,608.7 Wh in every cycle since it depends only on
critical demand). The EBR formula (`t = 0..22`) never binds in any of the 6 cycles —
`binding_timesteps` is empty except for exactly one case.

## Causal decomposition — the 4 requested categories

### 1. Research terminal-target formula

**Real but small and localized where it is active.** It is the term that actually occupies
the t=23 envelope slot in all 6 cycles (confirmed above). It only produces a measurable
diesel effect in the one cycle where it actually binds (2024-08-12, Stage 8.1): at that exact
hour (t=23), diesel is 61,600 W for Stage 8.1 vs. 57,842 W for baseline at the same hour — a
**+3,758 W (+6.5%) same-hour increment specifically coincident with the binding timestep.**
This is the formula's own, directly-localized contribution in this sample.

### 2. Native GAP19 EBR (t = 0–22)

**Zero measured contribution in this sample.** The EBR target is never the binding
constraint at any timestep in any of the 6 instrumented cycles — `binding_timesteps` is
empty for every cycle except the one TERMINAL-sourced case above. (Caveat: this is a 3-origin
sample; it does not rule out EBR ever binding across the full 347-origin window, only that it
did not in this validation set.)

### 3. Strict J2-before-J3 lexicographic priority

**Not a diesel source itself — the structural enabler that lets (1) and, if it occurred,
(2) become diesel at all.** Confirmed from code (unchanged from the prior review): without
this strict ordering, a nonzero `s_J2` would not force any extra fuel spending. This category
is a *rule*, not a *quantity*; it is not separately measurable in liters, only observable as
"when `s_J2 > 0` at t=23, diesel at t=23 is elevated relative to baseline's same-hour value" —
which is exactly what is shown in §1.

### 4. Direct energy balance — the dominant proximate driver at the hourly level

**This is the largest measured contributor in every one of the 6 instrumented cycles,
including the one where J2 binds.** Even in the 2024-08-12 Stage 8.1 cycle (the one case with
a binding reserve constraint), diesel at the 23 **non-binding** hours sums to 99,209.4 W,
versus 61,600 W at the one binding hour (t=23) — i.e., **the majority of that cycle's
elevated diesel use occurs at hours where the reserve envelope is not binding at all,**
pointing to the direct bus-bar energy-balance effect (lower forecasted solar requiring more
diesel to meet ordinary demand, independent of the reserve mechanism) as the larger
contributor even within a reserve-binding cycle. In 2024-06-19 (zero binding anywhere), 100%
of the elevated diesel (non-binding-hour sum 196,223.8 W for Stage 8.1 vs. 69,442.0 W for
baseline) is, by construction, attributable to this mechanism alone.

---

## Correction to the prior forensic report's attribution

The earlier report (`R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md`) found that 87.3% of the
*cycle-level* total diesel delta occurred in cycles where J2 bound *somewhere* in the 24h
plan, and treated this as evidence that the terminal-reserve mechanism was the dominant
cause. **The per-timestep instrumentation built here shows that claim conflated two different
things**: "this cycle happens to also have a binding reserve constraint" (a correlation,
cycle-level) is not the same as "this cycle's extra diesel was caused by that binding
constraint" (a causal, hour-level claim). In the one binding cycle instrumented here, the
constraint's own localized effect (+3,758 W at t=23) is a modest fraction of that cycle's
total elevated diesel; most of it occurs at other hours where the direct energy-balance
effect — not the reserve mechanism — is the better-supported explanation. **This does not
overturn the finding that J2-binding cycles tend to have higher diesel** (both effects can
be, and plausibly are, driven by the same underlying cause: a day with much lower forecasted
solar than baseline both triggers the reserve envelope *and* independently requires more
diesel for ordinary balance) — but it means the 87.3% figure should not be read as "87.3% of
the diesel increase is caused by the terminal-reserve formula." The direct energy-balance
effect appears, from this instrumented sample, to be the larger proximate driver even in
reserve-binding cycles.

## What remains unresolved (explicitly, not glossed over)

- This correction is based on **3 origins only** — sufficient to validate the instrumentation
  and demonstrate the method, not to re-quantify the full 245-origin NORMAL-route split from
  the prior report. Re-running the full window with this same instrumentation would answer
  that precisely, but doing so was out of scope for this task ("run only a small diagnostic
  replay").
- A rigorous causal isolation (not same-timestep association) of "diesel caused by the
  terminal-target formula alone" would require a counterfactual re-solve with
  `terminal_target_wh` held at a fixed/zero value while leaving everything else — including
  the solar forecast — unchanged. This is explicitly not done here, per instruction ("do not
  change optimizer behavior yet," "do not choose a new terminal formula").
- Whether native EBR ever binds across the full 347-origin window (it did not in this
  3-origin sample) is unresolved.

---

## STOP

No optimizer behavior was changed. No new terminal formula or objective weighting was
chosen. R1 and R2 remain frozen, unmodified controls. This diagnostic branch
(`POLARIS_EMS_GAP19_MILP_V2_DIAGNOSTIC_BRANCH/`) is additive instrumentation + a small
validation replay only, and is not wired into `worker.py` or any production path.
