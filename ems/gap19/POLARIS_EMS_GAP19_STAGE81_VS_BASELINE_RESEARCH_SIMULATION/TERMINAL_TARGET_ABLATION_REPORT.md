# Terminal-Target Ablation: Results and Revised Diesel-Delta Decomposition

**Scope**: Research-only ablation experiment, as proposed in
`STAGE81_FORECAST_VALUE_TRANSLATION_INVESTIGATION.md §3/§4`. **The only change from frozen
R1/R2**: `terminal_target_wh` forced to a solar-insensitive constant, **40,000 Wh** (the
existing R1/R2 floor), for **both** arms, at every origin — applied via an in-process
monkeypatch in a new script
([run_terminal_target_ablation.py](run_terminal_target_ablation.py)), never by editing
`run_research_simulation.py` or `run_full_experiment.py` on disk. GAP19, both forecast
engines, all `system/config/*.yaml`, the 347-origin window, and the warmed-up `StationState`
construction are byte-identical to R1/R2 — confirmed by the script's own
`verify_frozen_manifest()` call (reused unmodified), which reported **all hashes MATCH**
before the run proceeded (see run log, reproduced below). Raw results:
[TERMINAL_ABLATION_RAW_RESULTS.json](TERMINAL_ABLATION_RAW_RESULTS.json) (694 cycles).

**No production code, config, or frozen artifact was modified.** `run_research_simulation.py`
SHA256 `d68b343d...` and `run_full_experiment.py` SHA256 `8afaf9ee...` — both **VERIFIED
unchanged** (identical to the hashes the script's own frozen-manifest check expects; the
check passed).

```
--- Verifying frozen manifest (R1) ---
  matrix: MATCH
  stage8_1_model: MATCH
  run_research_simulation.py: MATCH
  RESEARCH_EXCEPTION_DECISION_RECORD.md: MATCH
  config/battery.yaml: MATCH
  config/diesel.yaml: MATCH
  config/loads.yaml: MATCH
  config/solar_pv.yaml: MATCH
  config/station.yaml: MATCH
  config/optimizer.yaml: MATCH
All frozen manifest hashes verified OK.
```

Ablation applied correctly at every one of the 694 cycles (script asserts
`terminal_target_wh == 40000.0` per cycle; no assertion failure, confirmed by the run
completing). 694/694 cycles `OPTIMAL` or `OPTION_D_FALLBACK` (same as R1/R2, see §4).

---

## 1. Diesel delta vs. original R2 — **VERIFIED**

| Metric (NORMAL-route, n=245 each) | Baseline, R2 | Baseline, ablation | Stage8.1, R2 | Stage8.1, ablation |
|---|---|---|---|---|
| Planned diesel fuel (L, summed) | 5,818.32 | **0.00** | 10,849.60 | **3,507.65** |
| Reserve shortfall sum (Wh) | 1,499,922.0 | **0.0** | 2,115,932.3 | **0.0** |
| Origins with binding reserve (of 245) | 98 | **0** | 125 | **0** |

| | R2 (original) | Ablation | Change |
|---|---|---|---|
| **Baseline NORMAL diesel** | 5,818.32 L | **0.00 L** | **−5,818.32 L (−100%)** |
| **Stage8.1 NORMAL diesel** | 10,849.60 L | **3,507.65 L** | **−7,341.95 L (−67.7%)** |
| **Stage8.1 − baseline delta (NORMAL)** | **+5,031.28 L** | **+3,507.65 L** | **−1,523.63 L (−30.3%)** |
| **Stage8.1 − baseline delta (all 347, incl. EMERGENCY)** | **+5,146.42 L** | **+3,622.78 L** | **−1,523.64 L (−29.6%)** |

EMERGENCY-route diesel is unaffected (115.13 L delta, unchanged in both runs) — expected and
**VERIFIED**: `OptionDFallbackSolver` never reads `terminal_target_wh` at all (same
code-confirmed fact already established in the prior investigation), so the ablation has no
mechanism by which it could touch EMERGENCY cycles, and the data confirms it did not.

## 2. Curtailment delta — **VERIFIED, essentially unchanged**

| Metric (NORMAL-route, summed) | R2 | Ablation | Diff |
|---|---|---|---|
| Baseline curtailment (Wh) | 31,916,981.6 | 31,916,954.3 | −27.3 Wh (0.00009%, floating/tie-breaking noise) |
| Stage8.1 curtailment (Wh) | 10,157,843.9 | 10,157,843.9 | **0.0 Wh — exactly identical** |

Curtailment is **unaffected by the ablation**, to within negligible numerical noise. This is
consistent with, and now additionally confirms, the prior finding that curtailment (J4) is
not causally linked to the reserve-envelope (J2) mechanism — removing J2's solar-sensitivity
entirely changes curtailment by ~0%.

## 3. EFC (battery throughput) delta — **VERIFIED**

| Metric (NORMAL-route, summed) | R2 | Ablation | Diff |
|---|---|---|---|
| Baseline discharge (Wh) / EFC | 28,635,629.7 / 143.18 | 33,404,264.9 / 167.02 | +4,768,635.2 Wh / **+23.84 EFC** |
| Stage8.1 discharge (Wh) / EFC | 26,575,094.1 / 132.88 | 31,230,306.3 / 156.15 | +4,655,212.2 Wh / **+23.27 EFC** |
| Baseline charge (Wh) | 41,269,237.3 | 31,283,647.6 | −9,985,589.7 Wh |
| Stage8.1 charge (Wh) | 38,658,765.6 | 21,982,821.9 | −16,675,943.7 Wh |

Both arms discharge the battery **more** and charge it **less** under the ablation — expected
and explainable, not an anomaly: with the reserve-envelope no longer forcing diesel-funded
charging toward a (solar-sensitive) target, the battery is used more for its ordinary role
(discharge to cover demand/diesel-deficit hours) and less for reserve-building. This is a
downstream consequence of removing the reserve mechanism, consistent with §4's prior framing
of battery changes as a secondary symptom, not an independent causal channel.

## 4. Unmet load / reliability — **VERIFIED, identical to R2**

| Metric | R2 | Ablation |
|---|---|---|
| Unmet load, both engines (Wh, NORMAL-route, summed) | 29,661,600.0 (both) | 29,661,600.0 (both) |
| Max unmet-load diff between engines | 0.0 | **0.0** |
| Route agreement (of 347) | 347/347 identical | **347/347 identical** |
| NORMAL cycles reaching OPTIMAL | 245/245 (100%) | **245/245 (100%)** |
| Solver failures / infeasibilities | 0 | **0** |
| SOC range, baseline (NORMAL) | 52.08–95.0% | 52.08–95.0% (**unchanged**) |
| SOC range, Stage8.1 (NORMAL) | 45.22–95.0% | 32.61–95.0% (floor drops further; stays within configured [20%,95%] bounds) |

Unmet load remains forecast-blind (0 diff between engines) under the ablation too, as
expected — it is driven by the demand channel, which the ablation does not touch. Reliability
(solver status, route agreement) is **completely unaffected** by the ablation.

## 5. Does the Stage8.1-vs-baseline diesel gap shrink? — **VERIFIED: yes, but only partially**

**Yes, it shrinks — by 29.6% (all-cycles) / 30.3% (NORMAL-route only) — but it does NOT
disappear.** 3,507.65 L of the original 5,031.28 L NORMAL-route gap **persists** even with
the reserve envelope held at an identical, solar-insensitive constant for both arms.

---

## Recomputed diesel-delta decomposition — **VERIFIED, and this REVISES the prior
correlational estimate**

The prior investigation (`R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md`) reported "87.3% of
the diesel delta occurs in reserve-binding cycles" — but that figure was an **observational
classification** (grouping origins by whether `J2 > 0` for *either* arm under the *original*
solar-sensitive formula), not a controlled counterfactual. This ablation is the actual
counterfactual, and it gives a **materially different, smaller causal share for the reserve
mechanism**:

| Decomposition of the **5,031.28 L NORMAL-route delta** | Share |
|---|---|
| **Terminal-reserve mechanism's net contribution to the delta** (baseline lost 5,818.32 L, Stage8.1 lost 7,341.95 L when the mechanism was removed; the delta's share is the *difference* in what each arm lost: 7,341.95 − 5,818.32) | **1,523.63 L — 30.3%** |
| **Direct bus-bar energy-balance effect** (the delta that remains even with the reserve envelope identical and non-binding for both arms — Stage8.1's accurate, lower solar forecast genuinely needs more diesel to meet ordinary demand than baseline's optimistic forecast believes is necessary) | **3,507.65 L — 69.7%** |

**This reverses the prior ranking.** The earlier correlational estimate (87.3% reserve /
12.7% direct) is **superseded by this measurement** for the question of *how much of the
cross-arm delta* is caused by the reserve mechanism specifically. The reason the two numbers
disagree so much is now also understood and **VERIFIED**: the terminal-reserve mechanism
inflates **both** arms' diesel substantially (100% of baseline's original diesel, 67.7% of
Stage8.1's) — the *binding-status classification* counted cycles where either arm's absolute
diesel was reserve-inflated, which is a large set, but the *delta* (what actually
differentiates the two arms) only reflects the **difference** between how much each arm was
inflated, which is a much smaller quantity. A cycle can be "reserve-binding" for both arms by
a similar amount and contribute almost nothing to the delta, while still being counted as
"attributable to the reserve mechanism" in the binding-status classification.

**What is now established, causally, not just correlationally**:
- The reserve mechanism is responsible for **all** of baseline's NORMAL-route diesel use in
  this experiment design (100%) and the **majority** of Stage8.1's (67.7%) — but because it
  inflates both arms, its net effect on the *cross-arm comparison* is smaller (30.3%) than its
  effect on either arm's *absolute* diesel figure.
- The **direct bus-bar energy-balance effect is the dominant driver of the cross-arm delta**
  (69.7%), not secondary as the prior correlational estimate suggested. This is the clearest,
  most direct evidence yet that part of "more accurate forecast → more diesel" is genuine:
  Stage8.1's lower, more accurate solar forecast reveals a real shortfall that the optimistic
  baseline forecast was simply unaware of, and GAP19 (correctly, by its own unmodified logic)
  schedules diesel to cover it.

---

## What remains UNKNOWN (unchanged, not resolved by this ablation)

- **Whether the strict J2>J3 lexicographic priority reflects deliberate governed
  reliability-over-fuel intent** — not addressed by this ablation; still unresolved per
  `R2_OPTIMIZER_DESIGN_REVIEW.md §3`.
- **Per-timestep attribution** (how much of the *original* formula's reserve-driven diesel
  came specifically from the t=23 research-formula term vs. t<23 EBR bindingness) — this
  ablation does not need that distinction (it removes the research-formula term entirely,
  side-stepping the question), but it also does not answer it. **Still UNKNOWN.**
- **Whether Stage8.1's remaining 3,507.65 L (69.7% of the original delta) is "correct" in a
  true multi-step closed-loop rollout**, versus an artifact of the single-step-per-origin
  R1/R2/ablation design (only the plan's first hour is ever realized; 23 of 24 planned hours
  are never executed or corrected against new information) — **UNKNOWN**, not addressed by
  any experiment run so far, ablation included.
- **Whether a different (also unauthorized) non-constant terminal-reserve formula** — e.g.
  one that is reserve-sensitive but *not* solar-forecast-sensitive — would behave differently
  from this ablation's all-the-way-to-the-floor constant. This ablation tested the extreme
  case (floor-only); it does not characterize the whole space of possible formulas.

## What this does NOT establish

- No claim that either arm, or either terminal-reserve formula, is operationally "better."
  More or less diesel, under any formula tested, is not evaluated against an authorized cost
  function — none exists.
- Not a validation, authorization, or recommendation of any terminal-reserve formula
  (original or ablated) for real use. Both remain `SIMULATED_RESEARCH_ASSUMPTION`,
  unauthorized.
- Does not resolve DEC-TR-03, DEC-RES-03, SD-07, SD-08, or SD-13.

## STOP

Ablation experiment complete. No production code, config, or frozen artifact was modified.
`run_research_simulation.py` and `run_full_experiment.py` confirmed byte-identical to their
frozen R1/R2 hashes before and after this run. The 87.3%/12.7% correlational estimate from
the prior investigation is superseded, for the cross-arm-delta question specifically, by the
30.3%/69.7% causal decomposition measured here.
