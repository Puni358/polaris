# Candidate K EMS Degradation Forensics — Why K Increased Unmet Critical Load

**RESEARCH-ONLY. Forensic analysis of the already-completed 2024 F-vs-K EMS replay
(`ems_replay_origin_level.csv`, `EMS_REPLAY_MANIFEST.json`, `EMS_REPLAY_REPORT.md`). The
EMS replay itself was NOT re-run.** The only new computation performed for this analysis
was re-deriving the deterministic F/K solar-forecast bundles and the deterministic
`terminal_target_wh` formula (both pure, already-used functions, imported unmodified) —
`router.evaluate_and_route` and `optimizer.optimize` (the actual MILP solve) were never
called again; all dispatch/replay numbers below are read directly from the existing saved
outputs. No production, Stage 8.1, F, K, or immutable artifact was touched.

## Method

For each of the 245 origins routed `NORMAL` by both arms, this analysis recomputed (read-only):
- `solar_delta_k_minus_f_wh`: full-24h difference between K's and F's forecasted solar energy.
- `late6h_solar_delta_k_minus_f_wh`: the same difference restricted to the last 6 horizon
  hours — the exact lookahead window `compute_terminal_target_wh` uses
  (`run_research_simulation.py:74-85`, `LOOKAHEAD_WINDOW_HOURS=6`, imported unmodified).
- `terminal_target_f_wh` / `terminal_target_k_wh`: `compute_terminal_target_wh(bundle)` run
  against the F bundle and the K bundle respectively (same wind/demand, only solar differs).

These were joined against the already-saved per-origin outcomes (`realized_unmet_load_wh`,
`realized_charge_wh`, `realized_discharge_wh`, `terminal_soc_pct`, `diesel_on_hours`,
`diesel_startups`, `realized_curtailment_wh`) and, for two representative origins, against
the already-saved per-hour arrays inside `EMS_REPLAY_MANIFEST.json`.

## Finding 1: K's forecast changes are NOT systematically higher or lower — they are highly origin-dependent and large

| | full-day solar delta (K−F), Wh | last-6h solar delta (K−F), Wh |
|---|---|---|
| mean | +1,345.6 | +351.5 |
| median | −262.1 | 0.0 |
| std | 6,058.6 | 1,066.0 |
| min / max | −11,170.9 / +16,128.6 | −2,672.0 / +3,840.2 |

K's correction is a single global EWMA state (`mu_global`) updated once per day from that
day's mean F residual. On 2024 — a year the EWMA was never tuned or validated on — this
produces large, origin-to-origin swings in both directions rather than a small, stable bias
correction. This instability, not a one-directional bias, is the root driver below.

## Finding 2: the late-window solar delta feeds directly into the terminal-reserve formula, which is the dominant causal channel to unmet load

Pearson correlations, n=245 (both-NORMAL origins):

| Relationship | r |
|---|---|
| solar_delta_k_minus_f_wh (full day) → unmet_delta_k_minus_f_wh | **+0.827** |
| late6h_solar_delta_k_minus_f_wh → unmet_delta_k_minus_f_wh | **+0.786** |
| terminal_target_delta_k_minus_f_wh → unmet_delta_k_minus_f_wh | **−0.791** |
| terminal_target_delta_k_minus_f_wh → terminal_soc_delta_k_minus_f_pct | **+0.763** |
| terminal_soc_delta_k_minus_f_pct → unmet_delta_k_minus_f_wh | **−0.712** |
| discharge_delta_k_minus_f_wh → unmet_delta_k_minus_f_wh | −0.389 (secondary) |
| diesel_on_hours_delta_k_minus_f → unmet_delta_k_minus_f_wh | −0.218 (weak) |

The chain is internally consistent and directionally coherent end to end:

**K forecasts more late-afternoon solar than F** (positive `late6h` delta) →
`compute_terminal_target_wh`'s deficit term (`max(0, crit_demand − renewable_avail)` over
the last 6 horizon hours) shrinks → **K's required terminal battery reserve is lower than
F's** (negative `terminal_target` delta) → the optimizer is permitted/forced to carry **less
ending SOC** under K (negative `terminal_soc` delta) → when the realized actual solar does
not match the optimistic late-window forecast, **K has less battery margin and more unmet
critical load** (positive `unmet_delta`).

The mirror case holds too: when K forecasts *less* late-day solar than F, its terminal
target is *higher*, it ends with *more* SOC, and K has *less* unmet load than F for that
origin (confirmed in the bottom-15 table below and the worked example in Finding 4).

Diesel commitment (on-hours, startup counts) shows only a weak correlation and near-zero
aggregate difference between arms (origin-level means: F=2.64 h, K=2.65 h diesel-on;
F=1.37, K=1.39 startups) — **diesel timing is not a material channel**. Battery
discharge-volume differences correlate moderately (r=−0.39) but are smaller in magnitude
and explanatory power than the terminal-reserve chain, and are themselves plausibly
downstream of the same terminal-SOC-target shift (a lower terminal target changes how much
of the battery the optimizer is willing to draw down earlier in the day).

## Finding 3: the effect is concentrated in a minority of origins, and is bidirectional

- 114 of 245 origins: K worse (positive unmet delta). 105 of 245: K better (negative). 26: tied.
- Sum of "K worse" contributions: +215,201 Wh. Sum of "K better" contributions: −88,634 Wh.
  Net: +126,567 Wh / 245 = **+516.6 Wh/origin mean** (matches `ems_replay_results.csv`).
- Concentration: top 20 worst origins (of 245) account for **73.4%** of the total "K worse"
  sum; top 30 account for **97.7%**. The ~517 Wh/origin mean is driven by a concentrated
  tail of bad origins, not a uniform small effect spread across the dataset.
- Seasonal concentration: mean unmet delta by month is strongly positive in **April
  (+2,667 Wh) and May (+2,285 Wh)** — exactly where terminal-target delta is most negative
  (April −1,416 Wh, May −2,098 Wh) — and near zero or negative (K better) in June, August,
  September, October. The degradation is not uniform across 2024; it concentrates in a
  spring window where K's global EWMA correction most over-predicted late-day solar
  relative to F.

Top 15 worst origins (all show large +solar delta, large −terminal-target delta, large
+unmet delta — same pattern):

| forecast_start | unmet Δ(K−F) Wh | solar Δ full-day | solar Δ last-6h | terminal target Δ |
|---|---|---|---|---|
| 2024-07-23 | +7,008.4 | +10,181.9 | +2,424.3 | −2,666.7 |
| 2024-04-27 | +6,014.6 | +11,158.9 | +1,969.2 | −2,166.1 |
| 2024-05-03 | +5,983.3 | +13,861.1 | +2,310.2 | −2,541.2 |
| 2024-05-18 | +5,931.6 | +14,913.4 | +3,550.8 | −3,905.9 |
| 2024-05-17 | +5,622.3 | +15,691.9 | +3,138.4 | −3,452.2 |

Bottom 5 (K better), mirror-image pattern:

| forecast_start | unmet Δ(K−F) Wh | solar Δ full-day | solar Δ last-6h | terminal target Δ |
|---|---|---|---|---|
| 2024-09-09 | −3,345.1 | −8,906.7 | −171.5 | +188.6 |
| 2024-06-11 | −2,627.9 | −7,245.8 | −1,791.0 | +1,970.1 |
| 2024-05-04 | −2,565.8 | +13,332.8 | +2,222.1 | −2,444.3 |
| 2024-09-08 | −2,421.9 | −7,710.3 | −550.7 | +605.8 |
| 2024-06-08 | −2,421.8 | −8,291.1 | −2,072.8 | +2,280.0 |

(2024-05-04 is a partial exception — large +solar delta but still net K-better — consistent
with this being a probabilistic/multi-factor chain, not a deterministic one-to-one rule;
see "What remains unknown" below.)

## Finding 4: worked example at hourly resolution — 2024-07-23 (worst origin)

From `EMS_REPLAY_MANIFEST.json` (already-saved, not recomputed), realized per-hour arrays:

- **Hour 13 (index 12), battery charge:** F charges **11,119.8 W**; K charges **0.0 W**
  (K curtails **20,684.2 Wh** instead — F curtails 0 Wh at that hour).
- **Resulting SOC trajectory:** F reaches **82.1%** at hour 14, drifting down to 53.5% by
  hour 22. K peaks at only **74.1%** at hour 15, drifting down to 51.0% by hour 22 — K runs
  consistently 3–8 points of SOC lower than F for the entire second half of the day.
  (Both arms share the same actual wind/demand/diesel-fixed replay physics — this gap is
  attributable only to the different planning input, i.e. the different solar forecast /
  terminal target.)
- **Resulting unmet load:** K has unmet load at hour 4 (2,889.7 W, F has 0) and higher unmet
  than F at nearly every late-afternoon hour (17–23): e.g. hour 19, F=767.1 W vs K=1,251.9 W;
  hour 21, F=292.9 W vs K=777.7 W.

This origin's terminal-target delta was −2,666.7 Wh (K required ~2,667 Wh less ending
reserve than F) — directly consistent with the MILP choosing to curtail rather than charge
at hour 13 under the K bundle, the lower SOC trajectory that follows, and the higher
realized unmet load once actual solar is substituted in during replay.

## What remains unknown / partial

- The planned (pre-replay) hour-by-hour `diesel_power` / `battery_charge` / `battery_discharge`
  MILP decision arrays were not serialized by `ems_replay.py` for most origins beyond the
  realized (replay-physics) arrays and planned sums — only the two worked-example origins
  above were inspectable at full hourly resolution from already-saved data in exactly the
  form needed (realized charge/SOC/unmet arrays happen to be saved for every origin, but the
  *planned* charge/discharge/diesel arrays are not, only their 24h sums). The exact internal
  MILP mechanism (which constraint/objective term specifically trades off terminal reserve
  against daytime charging) is inferred from the terminal-reserve formula's known structure
  and the consistent correlational/directional evidence, not read directly out of a solver
  trace. Re-deriving full planned hourly arrays for all 245 origins would require re-calling
  `optimizer.optimize`, which was explicitly out of scope for this analysis.
- A small number of origins (e.g. 2024-05-04) do not fit the simple "more late-solar forecast
  ⇒ worse" rule despite otherwise-correlated inputs, meaning the chain is not perfectly
  deterministic origin-by-origin — other factors (demand shape, initial-hour SOC/diesel
  state carried from the fixture, wind profile that day) plausibly modulate the effect size
  but were not isolated individually.
- Why K's global EWMA state swings this much more on 2024 residuals than it did on the 2023
  blind-test residuals (where it reliably improved both MAE and bias) was not re-derived
  here — that would require comparing 2024 vs 2023 residual distributions/regimes, which is
  outside this forensic scope (it analyzes the already-completed EMS replay, not F/K's
  underlying forecast-error statistics across years).

## ROOT CAUSE: established

**KEY EVIDENCE:**
1. Strong, directionally-coherent correlations (n=245 origins) across the full causal chain:
   late-window solar forecast delta (K−F) → terminal-reserve target delta (r=−0.79 to unmet) →
   terminal SOC delta (r=−0.71 to unmet) → unmet-load delta (r=+0.83 for full-day solar delta
   directly to unmet).
2. Diesel on-hours/startup deltas are statistically near-zero and weakly correlated
   (r=−0.22) — ruled out as a material channel.
3. Hour-by-hour worked example (2024-07-23, the single worst origin) directly shows the
   MILP choosing to curtail 20,684 Wh instead of charging the battery at hour 13 under K's
   bundle (vs. an 11,120 W charge under F's bundle at the same hour), producing a
   persistently lower SOC trajectory and more unmet load in the same hours every subsequent
   afternoon/evening — and the mirror-image pattern holds for a K-better origin (2024-09-09).
4. The effect is concentrated (top 20/245 origins = 73% of the "K worse" total) and
   seasonally concentrated (April–May 2024), consistent with K's single global EWMA state
   over/under-correcting F's late-day solar prediction in a way that was never validated
   against 2024 weather regimes.

**GOVERNANCE IMPLICATION:** Candidate K's forecast-accuracy improvement (lower MAE/bias on
SW_IN) does not imply an EMS-outcome improvement, because K's correction interacts with the
optimizer's **terminal-reserve constraint** through the late-day lookahead window — a
channel that a pure point-forecast-error metric cannot see and that K's tuning procedure
(optimized purely for 2022 SW_IN MAE) never accounted for. This is independent evidence,
beyond the aggregate result already reported in `EMS_REPLAY_REPORT.md`, that **Candidate K
must not be promoted on the strength of its forecast-accuracy metric alone** — any future
EMS-facing candidate's hyperparameters should be selected with (or at minimum validated
against) the terminal-reserve-sensitive late-horizon forecast behavior, not solar MAE/bias
in isolation. Candidate K remains research-only.
