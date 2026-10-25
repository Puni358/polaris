# Candidate 2: Forecast-Content Ablation — Report

Scenario: `synthetic_168h_endurance_scenario.json`, same initial state, fuel budget (100L),
configs, physical constraints, and ECD bypass as the existing
`FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL` run. No production code, objective,
constraints, or configs were modified. Frozen forecast = indices 1..23 of
solar_irradiance/solar_generation/wind_generation/demand (point/lower/upper) set to
repeat the index-0 value each step; index 0 unchanged.

**The frozen-forecast MILP run did not complete the full 168 steps.** It terminated
at step 82/168 with one fault:

```
OPTIMIZATION_RUNTIME_FAILURE (step 82): DispatchPlan violates charge/discharge
exclusivity at index 8: charge=0.04, discharge=45942.94.
```

All figures below cover the 82 completed steps only. Where relevant, the real-forecast
MILP and Reactive baseline are restricted to the same first-82-step window for
comparison (see `objective_cost_comparison_first82_apples_to_apples.json`); their
full-168-step totals are also given for reference since those runs did complete.

## Unmet load (Wh, first-82-step dispatched/h1 total)

| Controller | Unmet load (Wh) |
|---|---|
| Reactive baseline | 0.0 |
| MILP real forecast | 47,117.08 |
| MILP frozen forecast | 195,835.50 |

(Full 168 steps, for reference: real-forecast MILP = 184,149.2 Wh; Reactive = 0.0 Wh.)

## Fuel used / remaining (first-82-step window)

| Controller | Fuel before (L) | Fuel after (L) | Fuel used (L) | Diesel starts |
|---|---|---|---|---|
| Reactive baseline | 100.0 | 77.5 | 22.5 | 1 |
| MILP real forecast | 100.0 | 48.9714 | 51.0286 | 2 |
| MILP frozen forecast | 100.0 | 67.8514 | 32.1486 | 1 |

## Curtailment (Wh, first-82-step h1 total)

| Controller | Curtailment (Wh) |
|---|---|
| Reactive baseline | 592,055.74 |
| MILP real forecast | 784,330.05 |
| MILP frozen forecast | 842,449.34 |

## EFC (battery equivalent full cycles, discharge-based, per `EvaluationEngine`)

| Controller | Window | Battery throughput (kWh, discharge) | EFC |
|---|---|---|---|
| Reactive baseline | full 168 | 736.48 | 3.6824 |
| MILP real forecast | full 168 | 1,407.48 | 7.0374 |
| MILP frozen forecast | 82/168 (terminated) | 585.23 | 2.9261 |

## Fixed-weight objective cost (identical weights applied to all three; same 82-step window)

Weights: curtailment 0.05/Wh, battery deg 0.00005/Wh (charge+discharge), diesel
marginal 0.000625/Wh, diesel base 12.5/running-hour, startup 15.0/start, unmet
10.0/Wh.

| Controller | Total fixed-weight cost (82 steps) |
|---|---|
| Reactive baseline | 29,712.94 |
| MILP real forecast | 510,624.87 |
| MILP frozen forecast | 2,000,639.28 |

Delta (frozen − real-forecast MILP), 82-step window: **+1,490,014.42**, driven almost
entirely by unmet_load (+1,487,184.2 in weighted terms; frozen unmet load is ~4.2x
real-forecast unmet load over the same steps). Full breakdown in
`objective_cost_comparison_first82_apples_to_apples.json`.

## Whether frozen vs. real forecast materially changes MILP behavior

Yes, on both dimensions measured:

- **Dispatch/physical outcome (82-step window):** frozen forecast produced ~4.2x the
  unmet load, ~1.07x the curtailment, fewer diesel starts (1 vs 2), and less fuel
  consumed (32.1L vs 51.0L) than the real-forecast MILP over the identical steps and
  initial conditions.
- **Solver runtime:** per-step solve time rose from a mean of 1,166.8 ms (min 22.5 ms,
  max 26,507.3 ms) in the real-forecast run (full 168 steps) to a mean of 116,970.1 ms
  (min 8.9 ms, max 927,002.3 ms — i.e. ~15.45 minutes for a single step) in the
  frozen-forecast run (82 steps).
- **Completion:** the real-forecast MILP run completed all 168 steps with 0 faults.
  The frozen-forecast run terminated at step 82/168 on an `OPTIMIZATION_RUNTIME_FAILURE`
  (DispatchPlan charge/discharge exclusivity violation: charge=0.04 vs discharge=45,942.94
  at horizon index 8 of that step's plan).

## Artifacts

- `milp_frozen_forecast_full_result.json` — full per-step trajectory (82 steps) + post-hoc metrics
- `run_metadata.json` — provenance (config/code SHA-256, initial state, frozen-forecast definition)
- `objective_cost_comparison_three_way.json` — fixed-weight cost as originally computed (frozen: 82 steps; real/reactive: full 168 steps — **mismatched windows**, kept for reference)
- `objective_cost_comparison_first82_apples_to_apples.json` — same fixed-weight cost, all three controllers restricted to the identical first 82 steps (the valid comparison)
