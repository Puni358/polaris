# Actual-Solar Replay: Planned (R1/R2) Dispatch vs. Realized Physical Outcomes

**Scope**: Research-only replay experiment. **GAP19 was never re-run with actual solar as
an input** — each plan was generated exactly once, by the real, unmodified
`GAP19HighsNativeOptimizer`, using the **original, unablated R1/R2 harness** (the real
`compute_terminal_target_wh` formula, not the solar-insensitive constant used in the prior
ablation experiment — this run uses the true frozen R1/R2 planning process, as instructed).
A separate, new, read-only analysis step then replays each plan's already-decided
controllable commands against real ground-truth solar. Script:
[run_actual_solar_replay.py](run_actual_solar_replay.py) (SHA256 `51a10759...`). Raw results:
[ACTUAL_SOLAR_REPLAY_RESULTS.json](ACTUAL_SOLAR_REPLAY_RESULTS.json) (SHA256 `38bc5510...`),
347 origins, 245 NORMAL-route compared.

`verify_frozen_manifest()` (reused, unmodified) reported **all hashes MATCH** before this run
proceeded — confirmed in the run log. **No production code, config, or frozen artifact was
modified.**

## Replay methodology (stated explicitly — this is new analysis logic, not a GAP19 change)

For each hour `t` of each already-generated plan:
- `diesel_power[t]` and `battery_discharge[t]` are **held exactly as planned, unconditionally**
  — these are committed dispatch commands that do not depend on solar in this model, and this
  script never changes them.
- `battery_charge[t]` is executed **up to** the planned amount, but clipped down to whatever
  energy remains after critical load is served (critical load is given priority over
  charging in the replay — the same priority GAP19's own `J1 ≫ J4` structure encodes; stated
  here as an explicit replay-only modeling choice, not something extracted from a second
  GAP19 solve).
- `unmet_load[t]` (critical-load-specific, see **naming disambiguation** below) is whatever
  of `critical_demand[t]` cannot be covered even after reducing realized charge to zero.
- `curtailment[t]` is whatever real solar+wind is left over once critical load and the
  (possibly-reduced) charge are both satisfied.
- Realized battery SOC is tracked hour-by-hour using the exact formula already in
  `system/simulation/simulator.py:44` (`curr_e_wh += p_chg·η_chg − p_dis/η_dis`), reused
  unmodified, and checked against the configured `[20%, 95%]` bounds every hour.
- Real solar: `actual_SW_IN` from the frozen matrix, converted via the same
  provenance-documented PV formula already used earlier in this diagnostic branch
  (`min(SW_IN × 300 × 0.20 × 0.85, 60000)`). Wind and demand are held **identical** to what
  each plan already used (shared/forecast-persistence between arms, unchanged) — this
  experiment isolates solar-forecast accuracy only, consistent with R1/R2's own design.

**Naming disambiguation (critical — per the task's "verify baseline is not credited with
unrealized solar" instruction)**: GAP19's own `unmet_load` field (used throughout R1/R2's
own result tables) is `demand[t] − critical_demand[t]` — the **non-critical** portion of
demand GAP19 never attempts to serve at all (structurally always `153,600,000`-scale Wh
totals, identical both arms, unrelated to solar — already established in prior reports).
**That quantity is untouched by this replay.** What this replay recomputes is a **different,
new** quantity: whether the **critical-load** portion (`critical_demand[t]`, which GAP19's
own planning always reports as 100% served, `J1 = 0`) can **actually** be served once real
solar replaces forecasted solar. Below, "planned critical unmet" is always `0` (by
construction of J1-minimization); "realized critical unmet" is this replay's new finding.

---

## A. Planned dispatch comparison — **VERIFIED** (unchanged from prior reports, restated for reference)

| Metric (NORMAL-route, n=245, summed) | Baseline | Stage 8.1 |
|---|---|---|
| Planned diesel fuel (L) | 5,818.32 | 10,849.60 |
| Planned curtailment (Wh) | 31,916,982.0 | 10,157,844.7 |
| Planned critical-load unmet (Wh) | **0** (J1=0, always) | **0** (J1=0, always) |
| Planned battery charge (Wh) | 41,269,237.3 | 38,658,765.6 |
| Planned battery discharge (Wh) / EFC | 28,635,629.7 / 143.18 | 26,575,094.1 / 132.88 |

Both plans, as planned, claim to fully serve critical load with zero shortfall — that is
what GAP19's J1-priority always produces, by construction, regardless of forecast quality.

## B. Realized physical comparison — **VERIFIED**

| Metric (NORMAL-route, n=245, summed) | Baseline | Stage 8.1 |
|---|---|---|
| Realized diesel fuel (L) | 5,818.32 | 10,849.60 |
| Realized curtailment (Wh) | 12,963,774.0 | 8,869,721.3 |
| **Realized critical-load unmet (Wh)** | **8,782,880.7** | **1,739,283.7** |
| Realized battery charge (Wh) | 22,396,831.6 | 36,534,371.8 |
| Realized battery discharge (Wh) / EFC | 28,635,629.7 / 143.18 (identical to planned) | 26,575,094.1 / 132.88 (identical to planned) |
| Origins with ≥1 hour of SOC bound violation | **35 / 245 (14.3%)** | **0 / 245 (0%)** |
| Worst SOC floor breach (configured floor 20%) | **9.24%** (10.76 pts below floor) | none |
| Origins with any nonzero realized critical unmet | 224 / 245 (91.4%) | 220 / 245 (89.8%) |
| Mean / median nonzero-unmet magnitude per affected origin (Wh) | 39,209.3 / 34,920.7 | 7,905.8 / 5,094.9 |
| Max single-origin realized critical unmet (Wh) | 110,026.5 (2024-10-11) | 51,771.3 |

**Baseline's realized critical-load unmet (8,782,880.7 Wh) is 5.05× Stage 8.1's (1,739,283.7
Wh)**, and baseline alone produces genuine SOC floor violations (battery driven below its
configured 20% minimum at 35 of 245 origins, down to 9.24% in the worst case) — a real
physical reliability failure that never occurs for Stage 8.1 in this replay (0/245).

## C. Diesel difference after actual-solar replay — **VERIFIED: exactly zero, for both arms, by construction**

| | Planned diesel (L) | Realized diesel (L) | Diff |
|---|---|---|---|
| Baseline | 5,818.32 | 5,818.32 | **0.0000** |
| Stage 8.1 | 10,849.60 | 10,849.60 | **0.0000** |

This is a direct, necessary consequence of the replay's own definition (§Methodology):
`diesel_power[t]` is a held-fixed committed command, never re-derived from actual solar. **The
diesel plan each arm already committed to is exactly what gets "consumed" in the replay —
the forecast error does not show up as a diesel change, it shows up entirely as realized
unmet load, realized curtailment, and reduced realized charging (§B).** This is the correct
way to read "C": there is no diesel delta to report after replay; the delta that matters is
in B.

## D. Does Stage 8.1's improved forecast now produce a better realized outcome? — **VERIFIED: yes, broadly and by a large margin**

- **215 of 245 origins (87.8%)**: Stage 8.1's realized critical-load unmet is strictly lower
  than baseline's.
- **11 of 245 origins (4.5%)**: baseline's realized unmet is strictly lower than Stage 8.1's.
- **19 of 245 origins (7.8%)**: tied (both ~0 or both equal).
- **Aggregate**: Stage 8.1's total realized critical-unmet is 5.05× smaller than baseline's.
- **Reliability**: Stage 8.1 produces **zero** SOC bound violations across all 245 origins;
  baseline produces 35.

**This is the first experiment in this investigation chain to directly test realized
(not merely planned) outcomes, and it confirms the inference carried as UNKNOWN in the prior
two reports**: baseline's "zero planned diesel, zero planned unmet" plans were not evidence
of sufficiency — replayed against real solar, they fail to serve substantial real critical
load (8.78 MWh total across the window) and drive the battery below its configured safety
floor at 35 origins. Stage 8.1's higher-diesel, lower-curtailment plans, while still
imperfect (nonzero realized unmet at 220/245 origins, smaller magnitude), are **materially
and broadly more reliable** once evaluated against what actually happened.

**What this does NOT establish**: that Stage 8.1's *planned* diesel/curtailment levels are
themselves optimal, cost-efficient, or authorized for any real use — only that, compared
head-to-head on the **same realized-reliability metric**, Stage 8.1 dominates baseline at
~88% of tested origins and never produces a safety violation that baseline produces at 35
origins.

## E. Remaining UNKNOWNs

- **Why Stage 8.1 still shows nonzero realized unmet at 220/245 origins, not fewer.**
  Stage 8.1's forecast has nonzero MAE (22.85 W/m² overall, Q1) — some residual realized
  shortfall is expected, but this experiment does not decompose *how much* of Stage 8.1's
  own realized unmet comes from (a) ordinary residual forecast error vs. (b) the same
  burst-diesel/battery-banking strategy identified in the prior direct-bus-bar investigation
  (which could, in principle, leave the battery under-charged at specific hours even when
  the day's total diesel was planned correctly). **Not decomposed here.**
- **Whether a different (non-burst) diesel dispatch schedule would reduce baseline's realized
  unmet further, given its own (still badly wrong) forecast** — not tested; this replay only
  evaluates the plans GAP19 actually produced, never an alternative schedule.
- **Whether the charge-before-unmet priority assumption used in this replay (§Methodology)
  is the only defensible choice.** An alternative replay convention (e.g., protecting the
  planned charge command and letting critical load go unmet first) would very likely show
  *even larger* realized-unmet figures for both arms, especially baseline — this experiment
  used the convention that is *most generous* to both plans (critical load protected first),
  so the 8.78 MWh / 1.74 MWh figures above are, if anything, **lower bounds** on realized
  unmet under this replay's own assumption, not upper bounds. **Not tested under the
  alternative convention.**
- **Whether real wind/demand (as opposed to the shared forecast-persistence values held
  identical to planning) would change these figures.** This replay deliberately holds
  wind/demand identical to isolate solar, per the task's own instruction and R1/R2's
  established design; a true full-realism replay (real wind AND real demand) was not run.
- **Whether this single-step-per-origin replay generalizes to a true continuous multi-day
  rollout** (where a realized SOC violation or unmet shortfall on day N would carry over and
  compound into day N+1's starting state, rather than each origin restarting from the same
  fixed 80% SOC / 500 L fuel state). **Not tested** — remains the same structural limitation
  flagged in every prior R1/R2 report.

## STOP

Actual-solar replay complete. No production code, config, or frozen artifact modified.
`run_research_simulation.py` and `run_full_experiment.py` confirmed byte-identical to their
frozen hashes before this run (manifest check: all MATCH). GAP19 was called only in its
normal planning role; actual solar was used exclusively to evaluate the resulting plans, as
instructed.
