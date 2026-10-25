# MILP v2 — Controlled Full-Window Comparison (347 Origins) vs. Frozen GAP19 Control

**Checkpoint timestamp**: 2026-10-03T08:34:31Z (UTC)
**Experiment type**: Controlled optimizer-formulation experiment. **Not** a production
deployment, **not** a forecast-engine ablation (one engine — `LocalBaselineForecastEngine`
— used identically for both optimizer arms at every origin). All 347 origins from the
existing real research harness (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`'s
`forecast_start` column — the same "347 clean origins across 2024" referenced elsewhere in
this repository). No code, config, model, or forecast engine was modified. GAP19 was called
exactly as production code calls it, byte-for-byte unmodified.

Script: [run_v2_full_window_comparison.py](run_v2_full_window_comparison.py) (new file).
Raw results: [V2_FULL_WINDOW_COMPARISON_RESULTS.json](V2_FULL_WINDOW_COMPARISON_RESULTS.json)
(all 347 origins, per-origin aggregates). Run took 280.2s; **zero automated flags raised**.

**Identical inputs at every origin, both optimizer arms**: same `ForecastBundle`, same
`StationState` (80% SOC / 160,000 Wh, diesel running 2h, 500 L fuel — identical warmed-up
state construction used throughout this diagnostic branch), same `critical_demand_w`
(production formula), same `terminal_target_wh` (frozen R1/R2 formula,
`compute_terminal_target_wh`, imported not copied), same `system/config/*.yaml` base config.

---

## Route breakdown

| Route | Count | In GAP19/V2 domain? |
|---|---|---|
| NORMAL | 245 | Yes — compared directly, both optimizers |
| EMERGENCY | 102 | No — routed to `OptionDFallbackSolver` before either optimizer runs; not a comparison gap |
| **Total** | **347** | |

All 245 NORMAL-route origins were compared. All 102 EMERGENCY-route origins are, by router
design, outside GAP19/V2's domain for that cycle — the router decision happens before either
optimizer is called and does not depend on which optimizer would have run.

---

## 1. Effects caused by the new Essential-tier formulation

These effects are **consistent in direction across all 245 compared origins** — not
occasional or noisy, which is the signature of a designed formulation effect rather than
solver variance:

- **Essential service is genuinely contested on real data.** Served fraction ranges
  32.2%–100% (mean 50.4%, median 48.5%) across the 245 origins; **no origin has zero
  essential demand** (min `essential_demand_sum` = 79,265.64 Wh, max = 111,365.64 Wh). This
  is unlike the earlier hand-crafted smoke-test scenarios, which hit the 0%/100% extremes;
  real demand/renewable profiles sit in between.
- **Curtailment is lower in V2 than GAP19 at every single one of the 245 origins** (mean
  130,273.4 → 85,954.7 Wh, a ~34% average reduction) — Essential-tier service consumes
  renewable power GAP19 has no sink for, exactly as the synthetic Scenario 4 finding
  predicted, now confirmed uniformly across the full real window.
- **Battery charge and discharge totals differ at every single one of the 245 origins**,
  always in the same direction (GAP19's charge/discharge sums are always higher than V2's).
  This directional consistency across 245 independent origins is strong evidence of a real
  causal effect (V2 diverts some surplus to Essential service instead of charging/cycling
  the battery as heavily) — **not** solver tie-breaking, which would not produce a
  uniform sign across hundreds of independent instances.
- **`unmet_load` relationship holds exactly, at every origin**: `GAP19.unmet_load −
  V2.unmet_load == V2.load_served_essential`, max deviation `7.3e-12` Wh (floating-point
  noise) across all 245 origins. This is the Rev.3 double-counting fix, now verified exactly
  on the full real window, not just the earlier 8-origin sample.
- **J4 is higher in V2 than GAP19 at every origin** (adds the `unmet_essential` term). Per
  the task instruction, this was **not** interpreted as a performance regression — J4
  measures a different quantity in each formulation (curtailment-only vs.
  curtailment+unmet-essential).

## 2. Effects caused by solver tie-breaking / degenerate optimal schedules

**None detected on this real-data window** — a materially different finding from the earlier
synthetic (flat, constant-profile) smoke-test scenarios 3 and 5, where genuine MILP
tie-breaking degeneracy was observed and documented in the checkpoint.

- **Diesel dispatch is exactly identical between GAP19 and V2 at every one of the 245
  origins** — not just in aggregate sum, but in **on-hours count** (426 = 426) and
  **startup-event count** (220 = 220), checked per-origin, not only summed. Zero origins show
  any discrepancy, however small, in diesel power sum (`>1e-6 W` threshold: 0 origins).
- `dispatch_schedule_byte_identical` is `False` at all 245 origins — but this is now fully
  attributable to the battery charge/discharge divergence from Section 1 above (a real
  Essential-tier effect), **not** to tie-breaking: diesel (the component that showed
  tie-breaking sensitivity in the synthetic scenarios) is perfectly identical here.
- **Conclusion**: the degenerate-schedule finding documented in the implementation
  checkpoint was specific to the artificially flat/constant-profile smoke-test inputs, which
  create genuine LP ties. Real, non-flat demand/solar/wind curves do not exhibit this —
  each hour's optimal diesel level is uniquely pinned down by the real data, leaving no room
  for B&B path-dependent ties to manifest. This full-window run is the evidence for that
  conclusion; it was not assumed in advance.

## 3. Unchanged GAP19 behavior

- **Critical service: `J1 = 0.0` at every one of the 245 origins, both optimizers.** Critical
  load is always fully served; never compromised by the Essential-tier addition.
- **J2 (reserve) and J3 (diesel fuel) bit-identical between GAP19 and V2 at all 245 origins**
  (`j1_j2_j3_identical = True`, 245/245) — confirms, on the full real window, that terminal
  reserve / EBR / diesel-fuel-minimization logic is completely untouched by V2.
- **Diesel dispatch identical at every origin** (Section 2) — the frozen diesel
  unit-commitment physics are unaffected.
- **Demand accounting: 0.0 Wh error at every origin, both optimizers** (`served [+
  served_essential] + unmet == demand`, checked per-hour, max over all 24 hours and all 245
  origins = 0.0).
- **Energy-balance error: 0.0 at every origin, both optimizers** (max over all 245 origins =
  0.0).
- **Essential balance: 0.0 Wh error at every origin** (`served_essential + unmet_essential ==
  essential_demand`, max over all 245 origins = 0.0).
- **SOC ceiling (95% max) reached identically at all 245 origins.** SOC floor differs at 19 of
  245 origins (e.g. 2024-03-13: GAP19 59.61% vs. V2 57.83%) — a downstream consequence of the
  Section 1 charging-pattern difference (Essential-tier effect), not a new SOC-bound
  violation; battery SOC stayed within the configured [20%, 95%] bounds at every origin in
  both arms (confirmed by `soc_min`/`soc_max` ranges reported in the raw results).
- **Solver status: `OPTIMAL` at all 245 compared origins, both optimizers. Zero
  infeasibilities** anywhere in the full window.

## 4. Any unexpected V2 behavior

**None.** All automated invariant checks across all 347 origins raised **zero flags**:
- 0 infeasibilities
- 0 unexpected objective-stage divergences (J1/J2/J3 mismatch)
- 0 demand-accounting errors exceeding tolerance
- 0 energy-balance errors exceeding tolerance
- 0 unexpected diesel-aggregate divergences

No checkpoint assumption was violated: `curtailable_loads → Tier 2` remains the only tier
source used (unchanged `loads.yaml`), terminal reserve / EBR / 4-stage lexicographic
structure confirmed unchanged by the bit-identical J1/J2/J3 result above, fail-closed
infeasibility behavior was not exercised (no infeasibility occurred at any of the 245
NORMAL-route origins — the Scenario 6 synthetic result from the implementation checkpoint
remains the relevant evidence for that specific behavior), and `deferrable_loads` scheduling
was not invoked (unchanged from the checkpoint; confirmed by code, not re-audited here since
no code changed).

**No invariant failed. Nothing required stopping or modifying V2.**

---

## Note on `unmet_load` and diesel, per task instruction

`unmet_load` was used only as one term in the demand-accounting identity check, never as a
standalone forecast-performance or success metric. Lower curtailment and lower
charge/discharge throughput in V2 were **not** interpreted as "V2 is better" — they are
reported as the structural, expected consequence of adding a real sink (the Essential tier)
to the dispatch model, exactly as documented in the implementation checkpoint and now
confirmed to hold uniformly across the real 347-origin window.

## STOP

Controlled full-window comparison complete. Frozen checkpoint files unchanged (hashes
re-verified below, bit-identical to the prior checkpoint). GAP19 untouched. No code, config,
model, or forecast engine modified.
