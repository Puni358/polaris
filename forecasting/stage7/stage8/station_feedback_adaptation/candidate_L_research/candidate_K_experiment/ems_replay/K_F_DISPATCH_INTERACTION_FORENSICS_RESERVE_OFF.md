# F vs K Dispatch-Interaction Forensics — Terminal Reserve OFF

**RESEARCH-ONLY. Diagnosis only — no fix proposed, no new candidate created. Built
entirely from already-saved artifacts of previously-completed, already-approved runs: no
historical forecast experiment, K blind test, EMS replay, or terminal-reserve ablation was
re-run. No production, Stage 8.1, F, or K artifact touched. No subagents used.**

## 1. Question

With the terminal-reserve constraint confirmed OFF (`TERMINAL_RESERVE_ABLATION_REPORT.md`:
removing it only closes 8.1% of the gap, CI consistent with zero), what *ordinary*
forecast-trajectory → dispatch interaction is actually driving K's ~474.7 Wh/origin worse
realized unmet critical load than F, on the same 245 2024 NORMAL origins?

## 2. Data/artifacts actually available (no recomputation)

| Artifact | Contents used | Granularity |
|---|---|---|
| `terminal_reserve_ablation_origin_level.csv` | F_OFF/K_OFF realized unmet, charge, discharge, curtailment, diesel fuel, diesel-on-hours, SOC min/max, terminal SOC, critical demand — per origin | Daily aggregate (347 origins × 4 cells) |
| `TERMINAL_RESERVE_ABLATION_MANIFEST.json` | Per-origin, per-cell (`F_OFF`, `K_OFF`) hourly `realized_unmet_load_w`, `realized_soc_pct`, `realized_battery_charge_w`, `realized_curtailment_w` (24-length arrays each) | **Hourly** (replay-physics outputs only) |
| `/tmp/ai_forensics_merged.csv` (prior session artifact, already computed for `K_EMS_DEGRADATION_FORENSICS.md`, re-used here, not regenerated) | Per-origin F vs K solar-forecast energy delta, full-day and last-6h window | Daily aggregate, derived once from the frozen F model + K's frozen EWMA correction, identical regardless of reserve mode (forecasts don't depend on `terminal_target_wh`) |

**Explicitly NOT available from any saved artifact** (confirmed by inspecting the manifest's
own keys): hourly `diesel_power[t]`, hourly `battery_discharge[t]`, or any **planned**
(pre-replay) per-hour array for either arm. Only the **planned** 24h *sums* (diesel fuel
total, SOC min/max) and the **realized** (replay-physics) hourly arrays listed above were
ever serialized. Diesel-on-hours and diesel-startup *counts* (not timing) were computed and
saved at the origin level only. This limitation is stated here, not inferred around.

## 3. Direct F vs K differences (VERIFIED, n=245 both-OFF-NORMAL origins)

Origin-level paired correlations between `unmet_delta_off` (`K_OFF − F_OFF` realized unmet
load, Wh/origin — positive = K worse) and other already-saved per-origin quantities:

| Quantity | r vs. `unmet_delta_off` |
|---|---|
| Full-day solar forecast delta (K−F, Wh) | **+0.846** |
| Last-6h solar forecast delta (K−F, Wh) | **+0.788** |
| Realized battery **discharge** delta (K−F, Wh) | **−0.657** |
| Realized diesel fuel delta (K−F, L) | −0.462 |
| Realized curtailment delta (K−F, Wh) | −0.449 |
| Terminal SOC delta (K−F, %) | +0.530 |
| Realized SOC-min delta (K−F, %) | +0.464 |
| Diesel-on-hours delta (K−F) | −0.277 |
| Realized battery charge delta (K−F, Wh) | −0.157 (weak) |

**VERIFIED**: the full-day solar-forecast delta is, if anything, a *stronger* correlate of
the unmet-load gap with the reserve OFF (r=0.846) than it was with the reserve ON (r=0.827,
`K_EMS_DEGRADATION_FORENSICS.md`). The terminal-reserve mechanism was never the only channel
through which K's forecast volatility reached the EMS outcome — removing it leaves this
relationship intact, essentially unchanged.

**VERIFIED**: among dispatch-side quantities, realized battery **discharge** delta is by far
the strongest correlate (r=−0.657) — materially stronger than curtailment (−0.449), diesel
fuel (−0.462), or charge (−0.157). When K's realized discharge is *lower* than F's, K's
unmet load tends to be *higher*.

## 4. Hour-level / trajectory mechanism

**Aggregate pattern (VERIFIED, from already-saved origin-level data)**: K's EMS degradation
correlates with K's solar forecast being *more* optimistic than F's (positive full-day and
late-6h delta) **and**, at the same time, K ending up with *less* realized battery discharge
and *more* terminal SOC than F. This is the signature of an optimistic-forecast → reduced
discharge-commitment interaction: because `battery_discharge[t]` is "executed exactly as
planned, unconditionally" in the replay (`replay_plan_against_actual_solar`'s own documented
physics, unchanged since `run_actual_solar_replay.py`), a plan that commits to less discharge
because it expects more solar to cover the load cannot be revised when that solar does not
materialize — the shortfall shows up as unmet critical load.

**Worked example 1 — single worst OFF origin, 2024-05-17 (`unmet_delta_off` = +6,293.1 Wh,
largest K-worse case)** — all values **VERIFIED**, read directly from
`TERMINAL_RESERVE_ABLATION_MANIFEST.json`, no recomputation:

- Forecast: K predicted +15,691.9 Wh more solar than F over the full day (late-6h: +3,138.4 Wh).
- Realized discharge (24h total): F = 139,704.8 Wh vs. K = 136,114.2 Wh — **K discharged
  3,590.6 Wh less than F**.
- Realized unmet load by hour: F has unmet only at hours 6 (2,291.9 W) and three late hours
  (17: 94.0, 18: 719.0, 20: 298.8, 21: 194.9 W). K has unmet at hours 3 (670.8), 5 (490.6),
  6 (3,076.5 — worse than F's same-hour value), **and every one of hours 17–22**
  (878.6, 1,503.6, 459.7, 1,083.4, 979.5, 749.1 W) — a materially wider and deeper unmet
  window than F, concentrated in the evening.
- Realized SOC: K's SOC trajectory is *lower* than F's through the early-to-mid day (e.g.
  hour 9: F=58.17% vs K=56.23%) but **higher** than F's by the evening (hour 20: F=71.54% vs
  K=73.25%; hour 24: F=52.94% vs K=55.07%) — consistent with K holding back discharge that F
  used, ending the day with more SOC *despite* having more unmet load along the way.

**Worked example 2 — a strong K-better OFF origin, 2024-09-08 (`unmet_delta_off` = −3,436.7 Wh)**
— mirror-image pattern, also **VERIFIED** directly from the same manifest:

- Forecast: K predicted 7,710.3 Wh *less* solar than F over the full day.
- Realized discharge (24h total): F = 136,562.0 Wh vs. K = 140,680.1 Wh — **K discharged
  4,118.1 Wh more than F**.
- Realized unmet load by hour: K is lower than or equal to F at every hour with any unmet
  load (hour 6: 464.1 vs 1,014.8; hour 7: 1,407.5 vs 1,958.2; hour 8: 4,362.2 vs 4,583.3;
  hour 16: 0.0 vs 2,433.2; hour 17: 0.0 vs 419.8) — K's more pessimistic forecast led to a
  plan that discharged more battery up front, and that commitment paid off when actual
  solar that day apparently underperformed enough to make K's forecast the better-calibrated
  one for dispatch purposes.

Both worked examples show the same structural mechanism in opposite directions: **the sign
and magnitude of K's solar-forecast delta relative to F predicts the sign and magnitude of
K's discharge-commitment delta, which predicts the realized unmet-load delta** — entirely
through ordinary hour-by-hour planning, with no terminal-reserve or EBR-target involvement
(both held structurally identical to F's case; EBR itself depends only on critical demand,
which is shared between arms).

## 5. Strongest evidence

1. The full-day and late-6h solar-forecast-delta correlations with `unmet_delta_off`
   (r=0.846, r=0.788) are the strongest, most consistent signal in the dataset — **VERIFIED**,
   unchanged in direction and (if anything) strengthened compared to the reserve-ON case.
2. Realized discharge delta is the strongest dispatch-side correlate (r=−0.657),
   materially ahead of curtailment, diesel, or charge — **VERIFIED**.
3. Both worked hourly examples show the complete, internally consistent chain (forecast
   delta sign → discharge delta sign → unmet-load pattern by hour) in both directions
   (K-worse and K-better) — **VERIFIED** from saved hourly arrays, not inferred.
4. Concentration: as with the reserve-ON result, the OFF-mode degradation is dominated by a
   minority of origins — top 20 of 245 origins account for 44.2% of the total "K worse"
   unmet-load sum; top 50 account for 81.3% — **VERIFIED** from the origin-level CSV. The
   mechanism is not a small uniform effect; it concentrates on origins where K's forecast
   diverges most from F's.

## 6. What remains UNKNOWN

- **Hourly diesel-power and discharge schedules were never saved** for either arm (only 24h
  totals/counts). The specific hour-by-hour *decision* that sets the discharge commitment
  low or high (a direct MILP-objective/constraint trade-off) cannot be read from any saved
  artifact — only its *aggregate* and *realized-physics* consequences (SOC trajectory,
  unmet-load-by-hour) are observable. This is stated as UNKNOWN, not estimated.
- **No planned (pre-replay) hourly arrays were saved** for charge or discharge either. The
  hourly charge/curtailment/SOC arrays used above are all *realized* (replay-physics)
  arrays, which for discharge is identical to the plan by construction (discharge is
  "executed exactly as planned" — this makes the *aggregate realized discharge delta* a
  valid proxy for the planned discharge delta, but the *hourly* planned discharge schedule
  itself remains UNKNOWN).
- Why K's day-to-day solar-forecast delta is as large and volatile as it is (a single
  global EWMA state reacting to recent F residuals) was already explained in
  `K_EMS_DEGRADATION_FORENSICS.md` and is not re-derived here.
- Whether the discharge-commitment channel identified here is the *complete* explanation,
  or whether curtailment/diesel timing (weaker but non-trivial correlates, r=−0.449 and
  r=−0.462) contribute an additional, separable effect, is UNKNOWN from the data available —
  distinguishing them would require the planned hourly arrays that were never saved.

## 7. Conclusion — most defensible explanation for K's degradation (terminal reserve OFF)

**INFERRED, built on VERIFIED correlational and hourly worked-example evidence**: K's worse
realized unmet critical load, independent of the terminal-reserve mechanism, is best
explained by an **ordinary forecast-driven battery-discharge-commitment mismatch**: K's
day-to-day solar forecast (via its global EWMA correction) swings further from actual
realized solar than F's does on a concentrated subset of origins; on those origins, the
optimizer commits — through the normal per-hour generation/demand balance, not through any
reserve target — to *less* battery discharge when K is more optimistic about upcoming solar
(or *more* discharge when K is more pessimistic). Because discharge, once planned, is
executed unconditionally in the replay, an optimistic K forecast that doesn't materialize
leaves a dispatch-already-committed shortfall that surfaces as unmet critical load, while a
pessimistic K forecast that doesn't materialize produces the opposite (K outperforming F).
This is the same class of "optimistic forecast → under-provisioned commitment → unmet load
when the forecast doesn't hold" failure mode identified for the terminal-reserve channel in
the earlier forensics report, but operating through ordinary hourly dispatch planning rather
than the end-of-horizon reserve target — consistent with why removing the terminal reserve
left the core relationship (forecast delta ↔ unmet-load delta) statistically unchanged.

This conclusion is **not** a claim about the exact MILP mechanism (hourly planned arrays are
UNKNOWN, per §6) — it is the most defensible pattern supported by the hourly *realized*
evidence and the origin-level correlations actually available, clearly distinguished from
what remains unverified.

## Files referenced (no files created beyond this report)

- `terminal_reserve_ablation_origin_level.csv`, `TERMINAL_RESERVE_ABLATION_MANIFEST.json` (already existing)
- `/tmp/ai_forensics_merged.csv` (already existing, prior-session artifact, reused read-only)
