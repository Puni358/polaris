# Decomposing Stage 8.1's Remaining ~1,739 kWh Realized Critical-Load Unmet

**Scope**: Research-only decomposition of the finding in `ACTUAL_SOLAR_REPLAY_REPORT.md`
(§B/§E) that Stage 8.1's realized critical-load unmet totals 1,739,283.7 Wh across the 245
NORMAL-route origins, despite its forecast being far more accurate than baseline's. Script:
[run_stage81_unmet_decomposition.py](run_stage81_unmet_decomposition.py) (SHA256
`8800ccb5...`). Raw results:
[STAGE81_UNMET_DECOMPOSITION_RESULTS.json](STAGE81_UNMET_DECOMPOSITION_RESULTS.json) (SHA256
`975b9c81...`). `verify_frozen_manifest()` (reused, unmodified) reported all hashes MATCH,
including `config/diesel.yaml` (SHA256 `42112096...`, confirmed **unchanged on disk** before
and after this run — the counterfactual below only overrides one value in an in-memory dict
passed to specific extra calls, exactly as already disclosed and used for
`terminal_target_wh` in the prior ablation). **No production code, config, or frozen
artifact was modified.**

## Method (three plans per origin, all replayed identically)

1. **`orig`** — the real Stage 8.1 plan, unmodified config (same as `ACTUAL_SOLAR_REPLAY_RESULTS.json`).
2. **`perfect`** (Counterfactual A) — a **new** GAP19 planning call given the **actual**
   realized solar as its own forecast input (real cost structure, real terminal-reserve
   formula, unchanged). Isolates the **physical feasibility ceiling**: can GAP19, with its
   real, unmodified constraints, avoid unmet at all, given perfect information?
3. **`nobase`** (Counterfactual B) — a **new** GAP19 planning call given the **same** Stage
   8.1 (imperfect) forecast, with `base_fuel_consumption_l_per_h` overridden to `0.0` in the
   **in-memory config dict for this one call only** (file unchanged, hash-verified). Isolates
   the **scheduling/burst-banking contribution** identified in
   `DIRECT_BUS_BAR_PATHWAY_INVESTIGATION.md`: removing the only fixed-per-on-hour cost term
   removes the incentive to concentrate diesel into few, large, battery-banking bursts,
   without changing the forecast or any other input.

All three are replayed against the same actual solar with the exact same
`replay_plan_against_actual_solar` function already used and disclosed in
`run_actual_solar_replay.py` (imported, not duplicated) — methodology held consistent.

---

## 1. How much of the remaining unmet is caused by residual solar forecast error — **VERIFIED**

**Per-hour trigger (simple classification, no re-solve needed): 100% of the 1,217 unmet-hours
across all 245 origins occur at an hour where the forecast overstated actual solar
(`forecast_solar[t] > actual_solar[t]`).** Zero unmet-hours occur where the forecast was
accurate or conservative at that specific hour. **There is no hour, anywhere in this dataset,
where unmet occurs despite a locally-accurate-or-conservative forecast.**

**Aggregate magnitude (via Counterfactual A, perfect foresight): if Stage 8.1's forecast had
been perfect, realized unmet would have been `0.0 Wh` across all 245 origins** (and
`constraint_status = OPTIMAL` at all of them, zero SOC violations). **So, taken at face
value, 100% of the unmet is attributable to forecast imperfection in the sense that perfect
information eliminates it entirely.** However, this does not mean scheduling plays no role in
*how much* unmet a given imperfect forecast produces — see §2.

## 2. How much is caused by GAP19 diesel/battery scheduling — **VERIFIED**

Comparing `orig` (imperfect forecast, real burst-prone cost structure) against `nobase`
(same imperfect forecast, burst incentive removed):

| | Total realized unmet (Wh, 245 origins) | Share of `orig` |
|---|---|---|
| `orig` | 1,739,283.7 | 100% |
| `nobase` | 1,418,551.2 | 81.6% |
| **Scheduling-attributable reduction** (`orig − nobase`) | **320,732.5** | **18.4%** |

**Mean diesel ON-hours per origin: `orig` = 2.63, `nobase` = 10.36** — confirms the burst
incentive is real and large (nearly 4× more ON-hours once the fixed per-hour cost is
removed), and this schedule change alone recovers 18.4% of the total realized unmet, **using
the exact same (imperfect) forecast input**, with zero change in constraint status (both
`OPTIMAL` at every origin) or SOC violations (zero in both).

**Per-origin distribution** (of the 220 origins with nonzero `orig` unmet):
- **160/220 (72.7%)**: scheduling fix helps (reduces unmet).
- **9/220 (4.1%)**: scheduling fix very slightly *hurts* (by ≤390 Wh each — negligible in
  magnitude, not a systematic effect).
- **51/220 (23.2%)**: no measurable effect.
- The benefit is **not concentrated in a few outliers**: the top-10 origins by scheduling
  benefit account for only 27.6% of the total 320,732.5 Wh recovered.

## 3. Whether diesel burst/banking behavior contributes to the unmet load — **VERIFIED: yes, measurably, but it is secondary, not dominant**

Burst/banking **is a real, quantified contributor**: removing it (same forecast) recovers
18.4% of the total realized unmet, broadly (not narrowly) across 72.7% of affected origins.
**It is not the dominant cause** — 81.6% of the original unmet persists even once the burst
incentive is removed, and that remainder goes to exactly zero only once the forecast itself
is also made perfect (§1). **An important, non-obvious nuance, also VERIFIED**: in the
`perfect`-foresight counterfactual, GAP19 retains the **real** (unmodified) burst-prone cost
structure — yet still achieves `0.0 Wh` unmet. The single-origin check (2024-10-11) showed
`perfect` using the same 5 diesel ON-hours as `orig` (not more, not spread out) — **bursting
itself is not inherently harmful; bursting placed according to a wrong (imperfect-forecast)
schedule is what causes misses.** The `nobase` counterfactual's 18.4% improvement comes from
making the *imperfect* schedule more *robust* to being wrong (smoother, more continuous
dispatch has less to lose at any single mistimed hour) — a genuinely different, complementary
mechanism from "perfect timing of the same number of bursts."

## 4. Smallest valid counterfactual(s) run — **done, this session**

Two counterfactual GAP19 planning calls per origin (245 origins, 490 additional solves),
both reusing the frozen optimizer/router/config/StationState/forecast-engine code unmodified,
differing only in (A) the forecast input (actual solar fed as GAP19's own forecast) or (B)
one in-memory config value (`base_fuel_consumption_l_per_h = 0.0`) — the smallest possible
changes that isolate, respectively, the physical-feasibility ceiling and the
scheduling/burst-banking contribution, without touching the forecast-error question (which
required no re-solve at all, only the per-hour classification in §1).

## 5. Quantified potential improvement from each cause — **VERIFIED**

| Cause | Wh recoverable (245-origin total) | % of original 1,739,283.7 Wh |
|---|---|---|
| **Scheduling / burst-banking** (achievable with the *same* forecast, via `nobase`) | **320,732.5** | **18.4%** |
| **Residual forecast error** (the remainder, only closed by perfect information, via `nobase → perfect`) | **1,418,551.2** | **81.6%** |
| **Physical feasibility** (hard capacity/power/energy limit GAP19 cannot plan around even with perfect info) | **0.0** | **0.0%** |

---

## Distinguishing the four requested categories

| Category | Finding |
|---|---|
| **Forecast error** | **Dominant**, 81.6% of the total — VERIFIED via the `nobase → perfect` gap, and independently corroborated by the 100%-of-unmet-hours-coincide-with-local-overstatement finding (§1). |
| **Optimizer behavior** | **Secondary but real**, 18.4% — VERIFIED via the `orig → nobase` gap. GAP19's own fixed-per-on-hour diesel cost term (`base_fuel_consumption_l_per_h`, governed/configured, not a bug) creates a genuine, broadly-distributed (72.7% of affected origins) burst-banking tendency that, under imperfect forecasts, measurably worsens realized reliability relative to a smoother schedule — though the `perfect`-foresight result shows bursting itself is not inherently the problem; mistimed bursting under wrong information is. |
| **Physical feasibility** | **Not binding, at all** — VERIFIED (`perfect` achieves `OPTIMAL` and `0.0` unmet at all 245 origins, with zero SOC violations). The diesel generator's 100 kW max rating and the battery's power/energy bounds are never the limiting factor here; this is entirely an information/scheduling problem, not a hardware capacity problem. |
| **Governance assumptions** | **Held constant, not re-tested here.** The `terminal_target_wh` research formula (`SIMULATED_RESEARCH_ASSUMPTION`) was used identically in `orig` and `nobase` (same value, explicitly pinned), and recomputed consistently (from the now-accurate solar) in `perfect` — it was not ablated in this experiment, unlike the prior terminal-target ablation. **Whether a different (also-unauthorized) terminal-reserve formula would change this specific 18.4%/81.6% split is UNKNOWN**, not tested here (see below). |

## Remaining UNKNOWNs

- **Whether a different terminal-reserve formula (or the solar-insensitive ablated constant
  from the prior experiment) would change the 18.4%/81.6% split.** This decomposition held
  the original (unablated) formula fixed throughout, per the task's "keep replay methodology
  consistent" instruction. Combining the two ablations (terminal-target AND burst-cost) in
  one run was not done here.
- **Why scheduling fix very slightly *hurts* at 9/220 origins** (magnitude ≤390 Wh each) —
  not investigated further; likely a minor MILP tie-breaking artifact (consistent with the
  degenerate-schedule finding documented in the implementation checkpoint), not a systematic
  effect, but not confirmed.
- **Whether a partial reduction in the fixed per-hour diesel cost** (rather than the full
  `0.0` ablation tested here) would recover a different, intermediate fraction of the 18.4%
  — not tested; this experiment used the extreme (zero-cost) case only.
- **Whether these findings generalize to a true multi-day rollout** rather than independent
  single-step origins — same structural limitation flagged in every prior report in this
  chain, still not addressed.

## STOP

Decomposition complete. No production code, config, or frozen artifact modified.
`diesel.yaml` and all other frozen manifest files confirmed byte-identical to their expected
hashes before this run. GAP19 itself was never changed — only the in-memory inputs to two
clearly-disclosed additional planning calls per origin differed from the original R1/R2 call.
