# Is R2's Extra Diesel Physically Necessary, or an Artifact of MILP Dispatch Behavior?

**Scope**: Analysis only, of already-computed R2 and counterfactual (`CF-B`) data plus
direct code inspection. **No code, config, model, or assumption was changed; nothing was
re-run.** All new statistics below are aggregated from `FULL_DIAGNOSTIC_RAW_RESULTS.json`
(already-computed, unmodified-optimizer output) and from the confirmed GAP19 source
(`gap19_highs_native.py`).

**Bottom line, stated first**: the evidence supports that the extra diesel is
**predominantly physically necessary**, given the lower forecasted solar availability under
Stage 8.1 — not primarily an artifact of unnecessary MILP dispatch choices. One small,
quantifiable structural inefficiency was found (the inflexible diesel minimum-output floor),
and one confirmed-but-unquantified structural gap was found (an unenforced minimum-up-time
parameter) — both are real, both are flagged below, and neither differentially explains why
Stage 8.1 uses more diesel than baseline.

---

## 1. The decisive piece of evidence: the counterfactual isolation (already performed)

From `COUNTERFACTUAL_CAUSAL_ISOLATION_REPORT.md`:

| Mechanism | Share of the +5,031.28 L diesel increase |
|---|---|
| Solar forecast alone (terminal target held fixed) | **+101.5%** |
| Terminal-reserve objective/constraint reactivity alone (solar held fixed) | **−1.5%** |

This directly rules out "the reserve objective/constraint is forcing unnecessary diesel" as
an explanation: when that mechanism is removed (terminal target held fixed, not allowed to
react to solar), **the diesel increase still fully occurs.** Whatever is driving the extra
diesel, it is not the lexicographic J2 reserve envelope reacting to the forecast.

## 2. Diesel dispatch vs. demand/solar balance: power levels are mostly well above the
minimum floor, not clustered at it

| | Baseline | Stage 8.1 |
|---|---|---|
| Diesel-on hours (sum, 245 cycles) | 426 | 644 |
| Mean diesel power when on | 34,632.1 W | 47,388.8 W |
| Hours at-or-near the 10,000 W minimum floor (≤10,200 W) | 15 (3.5% of on-hours) | 27 (4.2% of on-hours) |

**Confirmed fact**: in both arms, the overwhelming majority (>95%) of diesel-on hours
dispatch well above the inflexible minimum floor (`min_power_w = 10,000 W`,
`gap19_highs_native.py:80,268-270`) — mean levels are 3.5–4.7× the floor. This is evidence
*against* "diesel is mostly just the unavoidable minimum output forced on by a small need" —
the model is dispatching substantial power, consistent with a real, sizeable deficit at
those hours, not a trivial one inflated by the floor.

## 3. Curtailment overlap: zero — the clearest "wasteful dispatch" signature is absent

**Confirmed fact**: across all 490 NORMAL-route cycles (both arms), there is **not one
single hour** where diesel is dispatched (`diesel_power_w > 0`) *and* renewable curtailment
is simultaneously nonzero at the same hour. If the model were burning diesel while
simultaneously wasting (curtailing) available renewable energy at the same hour — the
clearest possible signature of genuinely unnecessary dispatch — it would show up here. It
does not, in either arm.

## 4. Battery charge/discharge co-occurrence with diesel: diesel's output is being used, not
wasted, and Stage 8.1 pairs it with charging far more often

| | Baseline | Stage 8.1 |
|---|---|---|
| Diesel-on hours where battery simultaneously discharges | 0 (0.0%) | 0 (0.0%) |
| Diesel-on hours where battery simultaneously charges | 229 (53.8%) | **618 (96.0%)** |
| Diesel-on hours where battery is idle (neither) | 197 (46.2%) | 26 (4.0%) |

**Confirmed fact**: battery discharge never co-occurs with diesel in either arm (consistent
with the model never running diesel and draining the battery at the same hour — a sensible,
non-wasteful pattern). **Stage 8.1 pairs diesel with battery charging in 96.0% of its
diesel-on hours, versus 53.8% for baseline.**

**Code fact relevant to interpreting this**: the diesel output variable `p_diesel` has no
curtailment/waste variable anywhere in the model (unlike `p_sol`/`p_wind`, which have
explicit `p_curt_sol`/`p_curt_wind` slack variables — `gap19_highs_native.py:181-182`). The
bus-bar balance (`gap19_highs_native.py:227-231`) is an **equality**: whatever diesel is
generated must be fully absorbed by `p_served + p_chg + p_flex` (and `p_flex` is capped at a
negligible 500 W, line 189). **This means any diesel dispatched beyond the instant's direct
demand has only one real sink: battery charging** — it is not a separate "choice" to
opportunistically charge so much as a structural consequence of how the model is built.

**Inference** (not a direct code fact, but consistent with and not contradicted by the
above): given that diesel power levels are mostly well above the floor (§2) and the
counterfactual (§1) shows this is not driven by the reserve-envelope objective, the most
consistent explanation is that Stage 8.1's lower solar genuinely leaves the battery more
depleted going into diesel-on hours, so the model's dispatch of diesel both serves
same-hour demand *and* (mechanically, via the equality constraint, with no other sink)
recharges the battery — i.e., the high charging co-occurrence looks like a *consequence* of
genuine solar scarcity, not an independent cause of it. This is an inference, not something
directly provable without a further counterfactual (e.g., re-solving with a larger flex-load
sink) — which is out of scope here.

## 5. Diesel startup/base/marginal fuel structure, and a confirmed, unrelated structural gap

**Confirmed fact (fuel formula)**: `J3 = Σ_t [marg_fuel_l_wh · p_diesel(t) + base_fuel_l_h ·
u_diesel(t) + startup_fuel_l · v_start(t)]` (`gap19_highs_native.py:336-339`) — a flat
5 L/h is charged for every hour diesel runs, *regardless of power level*, plus a 2 L
charge per start event, on top of the 0.00025 L/Wh marginal rate.

**Confirmed fact (run pattern)**: diesel runs in short, frequent bursts in both arms —

| | Baseline | Stage 8.1 |
|---|---|---|
| New start events (0→1 transitions) | 220 | 337 |
| Mean run length (consecutive on-hours) | 1.94 h | 1.61 h |
| Max run length | 2 h | 3 h |

**Confirmed fact (code)**: `diesel.yaml`'s `min_up_time_hours: 2` parameter is **never read
or enforced anywhere in `gap19_highs_native.py`** (confirmed by exhaustive grep — the string
`min_up_time` does not appear in the optimizer file at all). The only startup-related logic
present is the `v_start` tracking constraint (`gap19_highs_native.py:277-285`), which counts
starts for the fuel objective but does not prevent a start-stop-start pattern.

**Inference, clearly separated from the above facts**: a genset that must stay on for at
least 2 governed hours once started, if it were enforced, could plausibly consolidate some
of these short (1–2 hour) bursts into fewer, longer runs, potentially changing total
base-fuel and startup-fuel cost (direction not determined without a counterfactual re-solve —
consolidating could save base-fuel/startup repetition, or could cost more marginal fuel if it
forces diesel on during hours it would otherwise be off; this report does not determine
which, and does not attempt to). **This is a real, confirmed implementation gap relative to
the governed config, but it is present equally in both arms** — it does not, by itself,
explain *why Stage 8.1 uses more diesel than baseline*, since both arms exhibit the same
short-run, frequent-restart pattern (baseline's own mean run length, 1.94h, is actually
slightly *longer* than Stage 8.1's, 1.61h — if anything, baseline's pattern is marginally
less fragmented, not more).

## 6. Active constraints and lexicographic priorities (confirmed, unchanged from prior reports)

All constraints and priorities already documented in `R2_OPTIMIZER_DESIGN_REVIEW.md` remain
as described there: strict lexicographic `J1 > J2 > J3 > J4`, no weighted trade-off, native
EBR never binds in this dataset, bus-bar balance is an equality. Nothing new was found here
beyond §4's specific observation about diesel's lack of a curtailment/waste variable.

---

## Summary: necessary vs. unnecessary, with confidence levels stated

| Finding | Necessary / Unnecessary | Confidence |
|---|---|---|
| The reserve-envelope mechanism (J2 reactivity) is NOT the cause of the extra diesel | Rules out "unnecessary due to objective design" for this specific mechanism | **Confirmed** (counterfactual isolation, §1) |
| Diesel power levels mostly well above the minimum floor | Evidence of genuine, sizeable need, not floor-forced waste | **Confirmed** (§2) |
| Zero same-hour diesel/curtailment overlap | Absence of the clearest "wasteful" signature | **Confirmed** (§3) |
| High diesel+charging co-occurrence under Stage 8.1 (96%) | Consistent with genuine need (battery more depleted by lower solar), given diesel has no waste/curtailment variable | **Inference**, code-consistent but not independently proven (§4) |
| ~4% of diesel-hours at/near the minimum floor | A small, real, quantifiable structural inefficiency (model cannot dispatch below 10 kW even if less is needed) | **Confirmed, but small in magnitude** (§2) |
| Unenforced `min_up_time_hours` causing short, frequent diesel bursts | A real structural implementation gap vs. the governed config | **Confirmed as a gap**; its fuel-cost *direction/magnitude* is **unresolved**, and it does not differentially explain Stage 8.1's extra diesel since it is present equally in baseline (§5) |

**Overall conclusion**: the extra diesel under Stage 8.1 is best supported, by the available
evidence, as **physically necessary given the lower (and more accurate) solar forecast** —
not primarily an artifact of unnecessary dispatch behavior, objective weighting, or
constraint design. The one confirmed, quantifiable inefficiency found (the minimum-output
floor) accounts for only a small share of diesel-hours (~4%) and cannot explain the bulk of
the increase. The one confirmed structural gap found (unenforced min-up-time) is real but is
shared equally by both arms and does not explain the *difference* between them.

## What remains unresolved (explicitly, not glossed over)

- The high diesel+charging co-occurrence under Stage 8.1 (§4) is interpreted, not proven, as
  a consequence of genuine solar scarcity rather than an independent driver — distinguishing
  these would require a further counterfactual (e.g., artificially enlarging the flex-load
  sink, or disabling charging during diesel-on hours) — not performed here.
- Whether enforcing `min_up_time_hours = 2` would increase or decrease total fuel use is not
  determined — would require a counterfactual re-solve with that constraint added, which
  would be an optimizer change and is explicitly out of scope ("no optimizer redesign yet").
- This analysis covers the 245 origins with `NORMAL` route in both arms; `EMERGENCY`/OptionD
  cycles were not examined here (OptionD does not read `terminal_target_wh` at all, per
  prior reports, so this question is less relevant there).

## STOP

No optimizer redesign performed or proposed in detail. R1/R2 and the diagnostic branch
remain as previously frozen/recorded; nothing was re-run to produce this report.
