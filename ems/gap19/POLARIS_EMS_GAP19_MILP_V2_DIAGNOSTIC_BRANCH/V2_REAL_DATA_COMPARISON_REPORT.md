# MILP v2 — Small Real-Data Comparison vs. Frozen GAP19 Control

**Scope**: 8 real-data origins, each run through the real production pipeline pieces
(`H10RuntimeAdapter`, `EMSControlRouter`, `LocalBaselineForecastEngine`,
`system/config/*.yaml`) feeding byte-identical `ForecastBundle` / `StationState` / `config`
into **both** the frozen `GAP19HighsNativeOptimizer` and the research-only
`GAP19HighsNativeOptimizerMILPV2Research`. **Not** the 347-origin R1/R2 experiment. No code,
config, or model was modified; GAP19 was not touched. Raw results:
[V2_REAL_DATA_COMPARISON_RESULTS.json](V2_REAL_DATA_COMPARISON_RESULTS.json). Script used:
[run_v2_real_data_comparison.py](run_v2_real_data_comparison.py) (new file; reuses, does not
modify, `run_research_simulation.py`'s frozen `compute_terminal_target_wh` and the existing
diagnostic-branch harness's station-state construction).

**Identical inputs confirmed per origin**: same `ForecastBundle` object, same `StationState`
object (80% SOC / 160,000 Wh, diesel running 2h, 500 L fuel remaining — the same warmed-up
state the existing diagnostic harness uses), same `critical_demand_w` (production formula:
`min(11600, demand[t])`), same `terminal_target_wh` (frozen R1/R2 formula), same
`system/config/*.yaml` base config, passed to both optimizers without alteration between calls.

---

## Origins selected (8, varied conditions across the real 347-origin set)

| Origin | Season / regime | Router outcome |
|---|---|---|
| 2024-01-25 | Deep winter, near-zero solar | **EMERGENCY** |
| 2024-03-20 | Spring equinox | NORMAL |
| 2024-06-01 | Near-solstice, high solar (also in R1/R2's own 5-origin set) | NORMAL |
| 2024-06-19 | Known diesel-stress origin (J2 non-binding), from existing diagnostic harness | NORMAL |
| 2024-08-12 | Known diesel-stress origin (J2-binding), from existing diagnostic harness | NORMAL |
| 2024-09-22 | Autumn equinox | NORMAL |
| 2024-11-15 | Late autumn, low solar | **EMERGENCY** |
| 2024-12-21 | Winter solstice, minimal solar | **EMERGENCY** |

**3 of 8 origins route to EMERGENCY** (handled by `OptionDFallbackSolver`, not GAP19/V2 — this
is the router's decision, made before either optimizer runs, and is identical regardless of
which optimizer would have been called). This is **not a comparison gap**: GAP19 and V2 are
simply not in this path's domain for these origins, exactly as the checkpoint's "infeasibility
→ OptionD routing withdrawn" finding describes (GAP19/V2 only ever see `NORMAL`-routed cycles).
**5 of 8 origins route to NORMAL** and were compared directly.

---

## Comparison results (5 NORMAL-route origins)

| Origin | GAP19 status | V2 status | J1,J2,J3 identical | Demand/essential accounting err (Wh) | Energy balance err | Dispatch schedule byte-identical |
|---|---|---|---|---|---|---|
| 2024-03-20 | OPTIMAL | OPTIMAL | **Yes** (0, 16416.499, 29.7419) | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 | No (degenerate tie) |
| 2024-06-01 | OPTIMAL | OPTIMAL | **Yes** (0, 0, 29.3605) | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 | No (degenerate tie) |
| 2024-06-19 | OPTIMAL | OPTIMAL | **Yes** (0, 0, 29.3605) | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 | No (degenerate tie) |
| 2024-08-12 | OPTIMAL | OPTIMAL | **Yes** (0, 0, 29.3605) | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 | No (degenerate tie) |
| 2024-09-22 | OPTIMAL | OPTIMAL | **Yes** (0, 16416.499, 29.7419) | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 | No (degenerate tie) |

**No infeasibility** on any NORMAL-route origin. **No unexpected objective-stage
divergence**: J1 (critical deficit), J2 (reserve shortfall), J3 (diesel fuel) are bit-identical
between GAP19 and V2 at every one of the 5 origins — confirming, on real data, exactly what
the checkpoint claims: the Essential tier only touches J4, nothing upstream of it.

### Critical service

Identical both optimizers, every origin: `sum_load_served = 278,400 Wh` (= critical demand
fully served all 24h, `critical_demand_sum`), `j1_objective = 0.0`. Critical load is never
compromised by the Essential-tier addition.

### Essential service / unmet-essential (V2 only)

| Origin | essential_demand_sum | served_essential | unmet_essential | % served |
|---|---|---|---|---|
| 2024-03-20 | 111,365.64 | 54,015.67 | 57,349.97 | 48.5% |
| 2024-06-01 | 79,265.64 | 25,562.75 | 53,702.89 | 32.2% |
| 2024-06-19 | 79,265.64 | 25,562.75 | 53,702.89 | 32.2% |
| 2024-08-12 | 79,265.64 | 25,562.75 | 53,702.89 | 32.2% |
| 2024-09-22 | 111,365.64 | 54,015.67 | 57,349.97 | 48.5% |

Essential service is genuinely contested on real data — unlike the earlier hand-crafted smoke
scenarios (where it was either trivially 0 or trivially 100%), real demand/renewable profiles
leave substantial unmet essential load. This is expected, not a defect: Essential is Tier 4 in
the lexicographic order, below critical load, reserve, and diesel-fuel minimization.

### Total demand accounting

Per-hour check `served [+ served_essential] + unmet == demand`: **max error 0.0 Wh at every
origin, both optimizers.** Confirms the 3-way balance holds exactly on real, non-flat data —
not just the hand-crafted smoke-test profiles.

**Per the task instruction, `unmet_load` was not used as forecast-performance evidence and
was not treated as a standalone success/failure metric.** It is reported only as one term in
the demand-accounting identity above, and its divergence between GAP19 and V2 is interpreted
structurally (see below), not as a performance claim.

The divergence itself is exactly the double-counting fix at work, confirmed on real data: at
every origin, `GAP19.unmet_load − V2.unmet_load == V2.load_served_essential` (e.g. 2024-03-20:
153,600 − 99,584.33 = 54,015.67, matching `served_essential` exactly). GAP19's `unmet_load`
is structurally overstated by exactly the amount V2 correctly attributes to served Essential
load — the same relationship verified in the synthetic smoke test, now confirmed on real
demand/renewable series.

### Diesel

**Bit-identical aggregate dispatch between GAP19 and V2 at every origin** (e.g. 2024-06-01:
69,442.0 W both). Consistent with `j3_objective` being bit-identical — diesel physics
completely unaffected by the Essential tier.

### Battery charge / discharge / SOC

SOC min/max bounds identical at every origin (e.g. 2024-03-20: 57.83%–95.0% both). Aggregate
charge/discharge sums differ slightly between GAP19 and V2 at every NORMAL origin (e.g.
2024-03-20: GAP19 charge 163,532.12 vs. V2 147,014.02) — **consistent with, and expected
from**, the same mechanism verified in the synthetic smoke test: V2 diverts some surplus that
GAP19 would otherwise route to charging into serving Essential load instead. This is the
intended Rev.3 behavior (Essential priority over charging when free), not a defect.

### Curtailment

V2's curtailment is lower than GAP19's at every NORMAL origin (e.g. 2024-06-01: GAP19
79,245.3 vs. V2 57,502.84), because Essential-tier service consumes renewable power GAP19 has
no sink for. Consistent with the synthetic Scenario 4 finding.

### J1–J4

J1, J2, J3 bit-identical at every origin (table above). J4 is always higher for V2 than for
GAP19 (adds the `unmet_essential` term), e.g. 2024-03-20: GAP19 79,245.3005 vs. V2
88,326.5508. **Per the task instruction, this difference was not interpreted as a performance
regression** — J4 is not comparable in isolation between the two formulations since it
measures a different quantity (curtailment only vs. curtailment + unmet-essential); its
divergence is the expected structural consequence of the new tier being represented at all.

### Solver status

`OPTIMAL` for both optimizers at all 5 NORMAL-route origins. No infeasibility encountered.

### Energy-balance errors

`0.0` for both optimizers at every origin.

### Dispatch-schedule degeneracy (carried over from the checkpoint, re-confirmed on real data)

At every one of the 5 NORMAL-route origins, `dispatch_schedule_byte_identical = False`: the
specific hour-by-hour diesel/battery schedule differs between GAP19 and V2 even where J1–J3
are bit-identical. This reproduces, on real data, the same MILP branch-and-bound tie-breaking
sensitivity to variable count (456 vs. 408) already documented in the checkpoint's Scenario
3/5 finding. Not a new issue; not attributed to any behavior change.

---

## Explicit flags

**Infeasibility**: none, on any of the 5 NORMAL-route origins. (The 3 EMERGENCY-route origins
never reach either optimizer, by router design — not an infeasibility.)

**Unexpected control/V2 divergence**: none found beyond the designed, expected divergences
documented above (essential service, J4, curtailment split, battery-charge split, schedule
degeneracy) — all of which are the intended or previously-documented consequences of the
Rev.3 design, not anomalies.

**Objective-stage change**: none beyond the expected J4 term. J1, J2, J3 bit-identical at
every compared origin — automated check (`j1_j2_j3_identical`) confirms this for all 5.

**Violation of checkpoint assumptions**: none detected.
- `curtailable_loads → Tier 2` SIMULATED_RESEARCH_ASSUMPTION: unchanged, still the only tier
  source used (`essential_max_power_w` read from `loads.yaml`'s `curtailable_loads[0]`, same
  as the checkpoint describes).
- Terminal reserve / EBR formula: unchanged — `terminal_target_wh` computed once via the
  frozen R1/R2 formula and passed identically to both optimizers; J2 values match exactly.
- 4-stage lexicographic structure: unchanged — confirmed by J1/J2/J3 bit-identity.
- Fail-closed infeasibility behavior: not exercised in this run (no infeasibility occurred on
  real data at these 8 origins), so nothing to flag; the Scenario 6 synthetic result from the
  checkpoint remains the relevant evidence for this behavior.
- `deferrable_loads` scheduling: not invoked (confirmed by code, unchanged from checkpoint).

**No issue was found. Nothing was modified in response to this comparison, per the task
instruction to stop and report rather than fix.**

## STOP

Small real-data comparison complete. No code, config, or model modified. GAP19 untouched. Not
the 347-origin experiment.
