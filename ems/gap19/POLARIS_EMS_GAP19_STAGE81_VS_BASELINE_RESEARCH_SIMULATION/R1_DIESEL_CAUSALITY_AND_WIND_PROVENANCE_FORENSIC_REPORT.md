# R1 Forensic Report: Diesel-Causality Trace & Wind-Forecast Provenance Audit

**Scope**: Investigation only. No code, config, assumption, or model was modified. No new
experiment was run. This report traces the already-completed R1 run
(`RESEARCH_FULL_EXPERIMENT_RAW_RESULTS.json`, 694 cycles) through the actual code paths, plus
a small number of read-only, diagnostic `ForecastEngine.predict()` calls (forecast generation
only — no optimizer, no simulator, no config change) needed to inspect values not stored in
the raw results (the `ForecastBundle` arrays themselves). This is not a rerun of the
experiment: the MILP optimizer and simulator were never invoked during this investigation.

---

## A) R1 DIESEL-CAUSALITY FINDING

### A.1 Root cause (confirmed)

**The entire observed difference traces to one input: the `solar_generation` forecast.**
`demand` and `wind_generation` are bit-identical between the baseline and Stage 8.1 arms at
every origin tested (confirmed directly: `bundle_b.demand.point == bundle_s.demand.point` and
`bundle_b.wind_generation.point == bundle_s.wind_generation.point` both `True` for all 4
origins inspected — see §B for why). Only `solar_generation` differs, and it differs
substantially and systematically:

| Origin | Baseline solar_gen (Wh, 24h sum) | Stage 8.1 solar_gen (Wh, 24h sum) | Reduction |
|---|---|---|---|
| 2024-08-12 | 310,685.9 | 133,130.2 | −57.1% |
| 2024-03-25 | 310,685.9 | 110,460.4 | −64.4% |
| 2024-06-19 | 310,685.9 | 94,547.2 | −69.6% |
| 2024-06-01 | 310,685.9 | 255,455.0 | −17.8% |

**The baseline's daily solar sum is the same constant value (310,685.9 Wh) at every origin
tested** — confirmed by code: `LocalBaselineForecastEngine.predict()`
(`system/forecasting/implementations/baseline.py:61-72`) computes solar purely from
`future_dt.hour` with a fixed diurnal `sin()` curve and a fixed `0.75` persistence-cloud
factor — it has no dependence on date, season, or actual weather. Stage 8.1's solar output
varies by origin because it is a real model inference over day-specific NWP/terrain/cloud
features (`system/forecasting/implementations/s81_corrected_solar.py:233-249`).

### A.2 Two concrete propagation mechanisms (both evidenced in code + raw results)

**Mechanism 1 — direct energy-balance effect (present in every high-delta cycle inspected).**
GAP19's bus-bar balance constraint
(`gap19_highs_native.py:227-231`: `p_sol_used + p_wind_used + p_dis + p_diesel = p_served + p_chg + p_flex`)
means diesel (`p_diesel`) is one of only two dispatchable sources (the other being battery
discharge) that can fill the gap left by solar. When `solar_generation` is forecast lower, the
bus-bar balance requires more `p_diesel` and/or `p_dis` to meet the same served load — and
because J3 (diesel fuel) is minimized ahead of J4 (curtailment) in the lexicographic order
(`gap19_highs_native.py:8,365-385`: priority 2 > priority 1), *less available solar also means
less curtailment*, since there is simply less surplus solar to curtail. This single mechanism
is consistent with the simultaneous "more diesel + much less curtailment" pattern seen in
every one of the 8 origins with the largest diesel increase (§A.3), **including the 2024-06-19
case, where the governed reserve envelope (J2) was not binding at all for either arm
(`reserve_shortfall = 0.0` both arms) yet the diesel delta was still +38,676.5 W at t0** — i.e.
Mechanism 1 alone, with no reserve-envelope contribution, is sufficient to produce a large
diesel increase.

**Mechanism 2 — indirect terminal-reserve-envelope effect (present in a subset of cycles,
reinforcing but not independent of Mechanism 1).** The R1 `terminal_target_wh` formula
(`run_research_simulation.py: compute_terminal_target_wh`) computes its deficit from
`demand − (solar_generation + wind_generation)` over the forecast's own trailing 6 hours
(hours 19–24). Since wind is identical between arms (§B) and demand is identical, any
difference in this deficit — and hence in `terminal_target_wh` — comes entirely from the same
solar-forecast difference as Mechanism 1. When Stage 8.1's trailing-6h solar is lower, its
computed `terminal_target_wh` is higher, which raises the governed reserve envelope
`e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)`
(`gap19_highs_native.py:151`). Because J2 (reserve shortfall, priority 3) is minimized strictly
*before* J3 (diesel, priority 2) in the lexicographic solve
(`gap19_highs_native.py:365-385`), the solver will accept additional diesel fuel cost to reduce
reserve shortfall before it will accept reserve shortfall to save fuel. Evidence this channel
is real and active: across the 245 NORMAL-route origins, `planned_reserve_shortfall_wh` (the
`s_J2` slack, taken directly from each cycle's own `DispatchPlan.reserve_shortfall`) is nonzero
in 98/245 baseline cycles vs. 125/245 Stage 8.1 cycles, and in 6 of the top-8
diesel-increase origins the Stage 8.1 shortfall is both present and larger than baseline's
(e.g. 2024-03-25: baseline shortfall 16,416.5 Wh vs. Stage 8.1 22,932.0 Wh).

### A.3 Quantification from the stored R1 raw results (no new run)

Across all 245 NORMAL-route origins (`RESEARCH_FULL_EXPERIMENT_RAW_RESULTS.json`):

| Quantity | Value |
|---|---|
| Mean Δ terminal_target_wh (Stage8.1 − baseline) | +1,946.68 Wh |
| Mean Δ planned diesel fuel (Stage8.1 − baseline) | +20.54 L/cycle |
| Mean Δ planned curtailment (Stage8.1 − baseline) | −88,812.81 Wh/cycle |
| Correlation(Δ terminal_target_wh, Δ planned diesel fuel) | **+0.687** |
| Correlation(Δ planned curtailment, Δ planned diesel fuel) | +0.015 (≈ none, linearly) |

The top 8 origins by diesel increase all show Stage 8.1 planned curtailment collapsing to
**exactly 0.0 Wh** (vs. baseline's 79,245–107,041 Wh), confirming Mechanism 1 is active in
every one of them; 6 of those 8 also show a larger, binding `s_J2` reserve shortfall for
Stage 8.1 (Mechanism 2 reinforcing). The moderate (not perfect) correlation between
Δ`terminal_target_wh` and Δ`diesel` (+0.687) is consistent with Mechanism 2 being a real,
partial contributor riding on top of Mechanism 1, not the sole or dominant cause by itself.

### A.4 What is NOT established (would require a new, out-of-scope run)

**The exact quantitative split between Mechanism 1 and Mechanism 2 cannot be determined from
existing evidence alone.** Isolating them would require a controlled counterfactual MILP solve
(e.g., holding `terminal_target_wh` fixed while varying only solar input) — that is a new
experiment, explicitly out of scope for this investigation. This report does not estimate a
percentage split and does not claim one is "dominant" in a precise quantitative sense beyond
what §A.2–A.3 show: Mechanism 1 is evidenced to be sufficient on its own (06-19 case);
Mechanism 2 is evidenced to be real and additionally contributing in a majority-but-not-all of
the largest-delta cases.

### A.5 Other causal factors checked and ruled out

- **Battery efficiency/SOC parameters**: identical config (`battery.yaml`, hash-verified
  identical for both arms per the frozen manifest) — not a source of difference.
- **Initial `StationState`**: identical, fixed, hard-coded for both arms at every origin
  (`run_full_experiment.py: run_one_cycle`) — not a source of difference.
- **Router/route selection**: identical for both arms at all 347 origins (0 disagreements,
  established in the prior results report) — the diesel difference occurs *within* matched
  NORMAL-route cycles, not from differential routing.
- **Objective/cost coefficients** (`marg_fuel_l_wh`, `base_fuel_l_h`, curtailment weight=1.0,
  etc.): identical config for both arms — not a source of difference.

---

## B) WIND FORECAST PROVENANCE

### B.1 Forecast engine / class actually used for wind in R1

For the **baseline arm**: `LocalBaselineForecastEngine.predict()`
(`system/forecasting/implementations/baseline.py:39-121`) computes `wind_generation` directly
at lines 74-76:
```python
w_val = max(0.0, round(last_obs_wind + 5000.0 * math.sin(h * math.pi / 6.0), 2))
```
— a deterministic persistence-plus-diurnal-sine-wave formula seeded only from
`station_state.last_observed_wind_generation`, with no weather-model input.

For the **Stage 8.1 arm**: `Stage81CorrectedForecastEngine.predict()`
(`system/forecasting/implementations/s81_corrected_solar.py:259-265`) contains:
```python
control_bundle = runtime_context.get("control_bundle")
if "wind_generation" in runtime_context and isinstance(runtime_context["wind_generation"], TimeseriesForecast):
    wind_gen = runtime_context["wind_generation"]
elif control_bundle is not None and hasattr(control_bundle, "wind_generation"):
    wind_gen = control_bundle.wind_generation
else:
    wind_gen = self.baseline_engine.predict(station_state, runtime_context).wind_generation
```
`self.baseline_engine` is itself a `LocalBaselineForecastEngine` instance, constructed at
`s81_corrected_solar.py:128-130` with the module's own comment stating: *"Baseline engine used
SOLELY to provide wind/demand channels when no control_bundle is supplied ... Solar fields
from this sub-engine are never used."*

### B.2 Which branch R1 actually took (confirmed, not inferred)

In both `run_research_simulation.py` and `run_full_experiment.py`, the Stage 8.1 engine is
called as:
```python
bundle = engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})
```
`runtime_context` contains only the key `"stage8_1_feature_matrix"` — no `"wind_generation"`
key, no `"control_bundle"` key. Therefore the **third branch (line 265) was taken on every one
of the 347 Stage 8.1 cycles in R1**: `wind_gen = self.baseline_engine.predict(...).wind_generation`,
i.e. the exact same persistence/diurnal-sine formula as the baseline arm, evaluated on the
same `station_state` the baseline arm also received. Confirmed empirically by direct
inspection of both bundles at 4 sample origins: `bundle_b.wind_generation.point ==
bundle_s.wind_generation.point` → `True` in all 4 cases (and, since the formula is a pure
function of `last_obs_wind` + hour-of-day, and both arms share the identical `station_state`
at every origin, this equality holds at all 347 origins by construction, not only the 4
sampled).

### B.3 Answers to the specific audit questions

| Question | Answer |
|---|---|
| Forecast engine/class | `LocalBaselineForecastEngine` (both arms — Stage 8.1's own engine delegates to it for wind) |
| Source inputs | `station_state.last_observed_wind_generation` (persistence) + deterministic `sin(h·π/6)` diurnal term; no NWP, no measured wind time series, no learned model |
| Horizon values | 24 hourly values, `h=1..24`, formula re-evaluated per `h` — same formula shape at every origin, differing only via the persistence seed `last_obs_wind` (which itself comes from the H1.0 fixture's recorded value at that cycle's index) |
| Validated Stage 8.1 wind, another validated model, or baseline/persistence? | **Baseline/persistence.** There is no "Stage 8.1 wind model" anywhere in this codebase — `Stage81CorrectedForecastEngine` is solar-only by design (confirmed by its own module docstring and the `self.baseline_engine` comment above); it does not produce, and was never built to produce, a wind forecast. |
| Identical between arms? | **Yes, bit-identical, confirmed.** |

---

## C) SUMMARY

### Confirmed facts
1. Only the `solar_generation` forecast channel differs between the R1 baseline and Stage 8.1
   arms; `demand` and `wind_generation` are bit-identical at every origin (code-confirmed,
   not merely observed).
2. The baseline's solar forecast is a fixed diurnal curve, constant across all 347 origins
   regardless of date/season/weather; Stage 8.1's solar forecast varies by origin and is, at
   the 4 sampled origins (including all of the top-8 diesel-delta origins checked), 18–70%
   lower in daily total.
3. Two concrete, code-grounded mechanisms propagate that solar difference into higher diesel
   use under Stage 8.1: (1) the bus-bar energy-balance constraint directly requiring more
   diesel when solar is lower, confirmed sufficient on its own in at least one case
   (2024-06-19, zero reserve shortfall on both arms); and (2) the R1 terminal-reserve formula
   computing a higher `terminal_target_wh` from the same lower trailing-6h solar, which — via
   GAP19's strict J2-before-J3 lexicographic priority — can force additional diesel-funded
   battery charging; confirmed active (nonzero, larger shortfall for Stage 8.1) in 6 of the
   top-8 diesel-delta origins.
4. The wind forecast used in R1 for *both* arms is the same unvalidated persistence/diurnal
   baseline formula, not a Stage 8.1 or any other validated wind model.

### Unresolved / not established by this investigation
1. The exact quantitative contribution split between Mechanism 1 and Mechanism 2 (would
   require a new controlled counterfactual run — out of scope here).
2. Whether Stage 8.1's lower solar predictions are more or less accurate than the baseline's
   fixed curve on these specific dates (this investigation traces mechanism, not forecast
   skill/ground truth) — answering that is a separate question this report does not address.
3. Whether this same diesel-increase pattern would hold under a different (also unauthorized)
   terminal-reserve formula/margin choice — not tested here.

No recommendations or parameter changes are made in this report, per instruction.
