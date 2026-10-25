# Uncertainty-Aware Terminal Reserve — Research Design & Feasibility Audit

**RESEARCH DESIGN DOCUMENT ONLY. No experiment was run. No code was written or executed.
No production, Stage 8.1, F, K, or immutable artifact was touched. Nothing is promoted.**

## Basis

Built directly on `K_EMS_DEGRADATION_FORENSICS.md` and `EMS_REPLAY_REPORT.md`. Established
finding (solver-level isolation: **partial**, not absolute — planned hour-by-hour MILP
arrays were not fully saved, so the mechanism is inferred from strong correlational and
hour-level worked-example evidence, not a complete solver trace): Candidate K's late-window
solar correction changes `compute_terminal_target_wh`'s deficit term, which changes the
required ending-SOC target, which changes the optimizer's daytime
charge/curtail/discharge posture, which changes realized unmet critical load once actual
solar is substituted in — independent of, and sometimes opposed to, K's forecast-accuracy
gain.

The current terminal-reserve formula (`run_research_simulation.py:74-85`, reused unmodified
throughout):

```
terminal_target_wh = TERMINAL_FLOOR_WH + deficit_wh * (1.0 + UNCERTAINTY_MARGIN)
```

where `deficit_wh` sums `max(0, crit_demand[k] - renewable_avail[k])` over the last
`LOOKAHEAD_WINDOW_HOURS=6` horizon hours, using **only that arm's own point forecast** for
`renewable_avail`. `UNCERTAINTY_MARGIN=0.10` is a **flat scalar**, identical regardless of
how uncertain that forecast actually is for that origin/regime. This is the mechanism the
forensics report identifies as the channel through which K's forecast volatility converts
into EMS-reliability loss: a point-forecast-derived target has no way to distinguish "K is
confidently right" from "K is swinging wildly" — both produce the same kind of terminal
target behavior, scaled only by the point forecast's magnitude, never by its dispersion.

## 1. Candidate uncertainty-aware terminal-reserve mechanisms

Three candidate mechanisms, ordered by how much new numerical policy they require. All
three keep `TERMINAL_FLOOR_WH` and `LOOKAHEAD_WINDOW_HOURS=6` **unchanged** (methodological
control: only the margin term is varied).

**Mechanism A — Empirical-quantile margin (regime-conditional, no new scalar invented).**
Replace the flat `UNCERTAINTY_MARGIN=0.10` with a margin read from an **empirical,
out-of-sample error-quantile lookup table**, built once from frozen `TRAIN_2020_2021` /
`VALIDATION_2022` residuals (never from `BLIND_TEST_2023` or the 2024 evaluation window),
stratified by a regime key already present in the data (e.g. `disagreement_fold` decile ×
horizon bucket). At runtime: `margin_wh(origin, hour) = Q_q(|residual| | regime(origin,
hour))`, looked up, not fit live. This is "testable without arbitrary tuning" in the sense
that the **functional form and the regime stratification come from existing, already-frozen
historical error data**, not a hand-picked constant — but the **quantile level `q`** itself
(e.g. 80th vs 90th percentile) is still a policy choice with no governance authorization and
must be marked a research assumption (see §6).

**Mechanism B — Disagreement-scaled multiplicative margin.** Keep the current
multiplicative structure (`deficit_wh * (1 + margin)`) but replace the constant `0.10` with
`margin(origin) = base_margin * (1 + normalized_disagreement(origin))`, where
`normalized_disagreement` is `disagreement_fold` (or `ctx_std_6h`) for the lookahead window,
normalized by its own frozen `TRAIN_2020_2021`/`VALIDATION_2022` distribution (e.g.
min-max or z-score using only historical statistics, never 2024 statistics). This keeps the
*shape* of the existing (already-unauthorized) formula, making the margin move with
day-specific forecast difficulty rather than being flat — but `base_margin` is exactly
as unauthorized as today's `0.10`, and the normalization function's parameters (which
window, which statistic) are also unresolved (§6).

**Mechanism C — Additive, regression-fit disagreement margin.** Fit
`margin_wh(origin) = β · disagreement_signal(origin, lookahead window)` by linear (or
isotonic) regression of **historical realized residual magnitude on the disagreement
signal**, fit only on `TRAIN_2020_2021`/`VALIDATION_2022`. This is the most "data-driven"
option (the coefficient `β` is estimated, not chosen) but introduces a new free modeling
decision (regression form, regularization) that itself needs documentation and is not
pre-existing in any frozen artifact — higher research/review burden than A or B.

**Recommendation for first test:** Mechanism A. It reuses an already-established pattern in
this repository (empirical quantile/bucket lookup, the same spirit as K's own regime
buckets in `candidate_K_experiment.py`'s unused `B_high_sun`/`C_transition`/`D_two_regime`
variants) and requires the fewest new free parameters — only `q` is unresolved, versus
`base_margin` + normalization choices (B) or a fitted regression (C).

## 2. Existing artifacts that can provide the uncertainty signal (no new data)

All of the following already exist, are already hash-verified/frozen, and are already used
elsewhere in this research line — none require new collection or synthesis:

| Signal | Source | Already present for | Causal? |
|---|---|---|---|
| `disagreement_fold` (\|cloud-NWP pred − physical pred\|) | `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` (hash `bb5700c9...`, `split` column: `TRAIN_2020_2021`/`VALIDATION_2022`/`BLIND_TEST_2023`); also present in `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` (hash `aeca026d...`, already used unmodified by the EMS replay) | 2020–2023 and 2024 | Yes — computed from same-cycle NWP/physical model outputs, no future information |
| `ctx_std_3h` (rolling std of recent observed SW_IN) | Same two matrices; 2024 matrix additionally has `ctx_std_6h/12h/24h` | 2020–2023 (3h only) and 2024 (3/6/12/24h) | Yes — backward-looking window only |
| F's own historical residual distribution by `split`/regime | `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` (hash `1337a568...`, already used unmodified by the K EMS replay and the forensics analysis) | 2020–2023 (not 2024) | Yes, as a fitting source (never evaluated on its own fitting window) |
| K's own per-origin `\|correction\|` magnitude | `candidate_K_predictions_2023.csv` / re-derivable from `candidate_K_experiment.run_simulation` (imported unmodified) | 2023 (2024 re-derivable, already done once in the EMS replay / forensics scripts) | Yes, but reflects *K's own bias-correction size*, not independent forecast dispersion — weaker, secondary signal only |

No new synthetic, fabricated, or externally-sourced data is required for the signal itself.

## 3. F as control, K as stress/test arm

The existing EMS replay (`ems_replay.py`, already executed and frozen in
`ems_replay_origin_level.csv` / `EMS_REPLAY_MANIFEST.json`) already is the control
condition: **F forecast + current fixed-margin formula**. It must **not** be re-run or
altered by this next experiment — it is the frozen baseline the new arms are compared
against.

The new experiment adds exactly one new factor — **which terminal-reserve formula is
used** — crossed with the existing **which forecast feeds the optimizer** factor, giving a
2×2 design:

| | Current fixed-margin formula (existing, frozen) | Uncertainty-aware formula (new) |
|---|---|---|
| **F forecast** | Control, already measured (`EMS_REPLAY_REPORT.md`) | New cell: isolates the formula's own effect, forecast held at its (already good) baseline |
| **K forecast** | Stress arm, already measured (the degradation this design responds to) | New cell: the actual test — does the mechanism recover K's reliability while K still carries its accuracy gain? |

F remains the **control forecast** throughout (never modified, never re-tuned). K remains
the **stress/test forecast** throughout (never modified, never re-tuned — same frozen
`A_global, alpha=0.1, min_history=1, max_clip=75, unscaled` config). Only the
**terminal-reserve formula** is the manipulated variable. This directly satisfies the
instruction that F stay control and K stay the stress arm: neither candidate's forecast
logic changes at any point in this design.

## 4. Required ablations to isolate terminal-reserve effects from forecast effects

1. **Primary 2×2 factorial** (above): `{F, K} × {fixed-margin, uncertainty-aware}`. The
   terminal-reserve effect is isolated as `(K, uncertainty-aware) − (K, fixed-margin)` and
   `(F, uncertainty-aware) − (F, fixed-margin)`; the forecast effect is isolated as
   `(K, fixed-margin) − (F, fixed-margin)` (already measured) and
   `(K, uncertainty-aware) − (F, uncertainty-aware)` (new). If the new mechanism works, the
   second forecast-effect comparison should show K no longer worse than F (or less worse),
   while the within-K formula comparison should show a measurable reliability gain.
2. **Degeneracy regression test** (sanity, not a scientific ablation): the new formula code
   path, when its margin is forced back to the constant `0.10` for every origin, must
   reproduce the existing frozen F and K control-arm numbers in
   `ems_replay_origin_level.csv` **exactly**. This is required *before* trusting any new
   numbers — it proves the new formula is a strict generalization, not a silent
   reimplementation drift.
3. **Signal-source ablation** (secondary, optional for a first pass): uncertainty-aware
   margin driven by `disagreement_fold` alone vs `ctx_std_3h` alone vs both combined —
   to determine which signal (if any) is doing the work, without being required for the
   primary go/no-go.
4. **Leakage audit** (mandatory, not optional): explicit written check that the
   signal-to-margin mapping (whichever mechanism is chosen) was fit **only** on
   `TRAIN_2020_2021`/`VALIDATION_2022` rows of the frozen 2020–2023 matrix, and that no
   2024 origin's own outcome (forecast, actual, or replay result) was used anywhere in
   fitting that mapping. This mirrors exactly how K's own hyperparameters were selected
   (2022-only) before being applied, unmodified, to 2024.
5. **Tail-concentration check**: because the original degradation was concentrated in ~20–30
   origins (`K_EMS_DEGRADATION_FORENSICS.md`, Finding 3), the new mechanism's effect must be
   reported **both** as an aggregate paired delta **and** specifically on that same
   previously-identified worst-origin subset (by `forecast_start`, already enumerated in the
   forensics report) — an aggregate-only result could hide whether the mechanism actually
   fixes the origins that caused the problem, versus moving the mean through unrelated
   origins.

## 5. Metrics and statistical tests

Reuse, unmodified, the exact metric set and methodology already defined in `ems_replay.py`
and used in `EMS_REPLAY_REPORT.md` / `K_EMS_DEGRADATION_FORENSICS.md` — no new metric
definitions are needed:

- Realized unmet critical load (Wh/origin, and reliability = 1 − unmet/critical-demand).
- Diesel fuel (L), diesel-on hours, diesel startups.
- Curtailment (Wh), battery EFC, SOC-floor violations, terminal SOC (%).
- Optimizer failures (`constraint_status != OPTIMAL`), route (`NORMAL` vs other) and
  **route-mismatch count across all four cells**, not just two.
- Solve time (s), tracked for completeness (not expected to be materially affected by a
  formula change, unlike a model change).

Statistical test: the **same origin-level paired bootstrap** already used (2000 iterations,
seed 42, 95% CI on the paired mean delta) — applied pairwise across all relevant cells of
the 2×2 (at minimum: `(K,new)` vs `(K,old)`, and `(K,new)` vs `(F,new)`), reported for (a)
all origins routed `NORMAL` in both cells being compared, and (b) the worst-origin subset
per Ablation 5. No new statistical method needs to be invented.

This experiment does **not** re-measure K's forecast-accuracy metrics (MAE/bias on SW_IN) —
those are frozen in `candidate_K_blind_results.csv` and are untouched by a terminal-reserve
formula change, since the formula change never alters K's predicted solar values. This
should be stated explicitly in any results report to avoid conflating "K's forecast is
still accurate" with "K's EMS outcome is now acceptable."

## 6. Governance-authorized vs research-assumption parameters

| Parameter | Status | Notes |
|---|---|---|
| `LOOKAHEAD_WINDOW_HOURS = 6` | **GOVERNANCE_AUTHORIZED** (`T_REQUIRED=6h`, per `RESEARCH_EXCEPTION_DECISION_RECORD.md`) | Unchanged by this proposal |
| `TERMINAL_FLOOR_WH` (= technical-min-SOC fraction × capacity) | `SIMULATED_RESEARCH_ASSUMPTION` (already so in the current frozen system) | Unchanged by this proposal; not re-litigated here |
| `UNCERTAINTY_MARGIN = 0.10` (current, flat) | `SIMULATED_RESEARCH_ASSUMPTION` — explicitly borrowed from an **unauthorized** advisory figure (NC-07), per the decision record | This is the exact term the proposal targets for replacement |
| Quantile level `q` (Mechanism A) | **RESEARCH ASSUMPTION, UNRESOLVED** | No governance basis exists for choosing e.g. 80th vs 90th vs 95th percentile; must be justified or explicitly left as a sensitivity sweep, never silently hard-coded |
| `base_margin` (Mechanism B) | **RESEARCH ASSUMPTION, UNRESOLVED** | Same unauthorized status as current `0.10`; replacing the shape does not resolve the underlying authorization gap |
| Regime stratification key (`disagreement_fold` decile vs `ctx_std` window vs combination) | **RESEARCH ASSUMPTION, UNRESOLVED** | No existing governance document specifies which signal is authoritative for EMS risk margins |
| Regression form/coefficients (Mechanism C) | **RESEARCH ASSUMPTION, UNRESOLVED** | Additional modeling choice beyond what any frozen artifact specifies |
| Margin cap/floor (any mechanism) | **RESEARCH ASSUMPTION, UNRESOLVED** | Needed to prevent unbounded reserve claims in extreme-disagreement regimes; no existing analogue except K's own `max_clip=75`, which is itself a research (not governance) choice |
| Train/validation split used to fit the mapping (`TRAIN_2020_2021` + `VALIDATION_2022`, excluding `BLIND_TEST_2023` and 2024) | **METHODOLOGICAL CONTROL, not a numeric policy value** | Directly mirrors how K's own hyperparameters were selected; does not require new authorization, but should be stated explicitly in any write-up |

No numeric policy value is proposed or assumed by this document. Every quantity above that
would require a specific number is explicitly marked unresolved.

## 7. Can the existing 2024 EMS replay support this without new synthetic/fabricated data?

**Yes, with one explicit constraint.** The EMS physics harness (fixture, origins, router,
optimizer, replay mechanics) is unchanged and reusable as-is — no new EMS data of any kind
is needed. The uncertainty **signal** (`disagreement_fold`, `ctx_std_*`) is already present,
unmodified, in the same hash-verified 2024 matrix already used by `ems_replay.py`. The
**mapping** from signal to margin must be fit from the frozen 2020–2023 matrix's
`TRAIN_2020_2021`/`VALIDATION_2022` rows only (both already hash-verified, already reused
elsewhere in this research line) — never from `BLIND_TEST_2023` or from the 2024 evaluation
window itself, to avoid fitting the margin on the same data it will be evaluated against.
Subject to that constraint, **no new data collection, synthesis, or fabrication of any kind
is required** to run this experiment once a mechanism and its unresolved parameters (§6)
are resolved or explicitly swept as a sensitivity analysis.

---

RESEARCH QUESTION: Can an uncertainty-aware terminal-reserve mechanism (margin derived from
an existing forecast-disagreement/volatility signal, rather than a flat point-forecast-only
multiplier) recover the EMS reliability K loses under the current fixed-margin formula,
without altering K's forecast itself?

CONTROL: Candidate F's forecast, held frozen and unmodified; the current fixed-margin
terminal-reserve formula (`TERMINAL_FLOOR_WH + deficit × 1.10`), unmodified, as the baseline
formula condition.

CANDIDATE MECHANISM: Mechanism A (empirical out-of-sample quantile margin, regime-keyed by
`disagreement_fold` decile × horizon, fit only on `TRAIN_2020_2021`/`VALIDATION_2022`) —
recommended first test; Mechanisms B and C documented as alternatives with higher
free-parameter burden.

REQUIRED DATA: all already exists and is already hash-verified/frozen —
`CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` (signal + split column, for fitting),
`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` (signal, for the 2024 replay, already
in use), `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` (residual magnitudes, for
fitting), plus the existing `POLARIS_HYBRID_FIXTURE_H1_0` EMS fixture (already in use,
unchanged). No new or synthetic data required.

KEY ABLATIONS: (1) 2×2 factorial {F,K} × {fixed-margin, uncertainty-aware}; (2) degeneracy
regression test (new formula at constant 0.10 must exactly reproduce existing frozen
results); (3) signal-source ablation (`disagreement_fold` vs `ctx_std` vs combined,
secondary); (4) leakage audit (mapping fit only on TRAIN/VALIDATION, never on BLIND_TEST or
2024); (5) tail-concentration check on the previously-identified worst-origin subset, not
aggregate-only.

GOVERNANCE GAPS: the quantile level (or base-margin / regression coefficients, depending on
mechanism), the choice of regime-stratification signal, and any margin cap/floor are all
unresolved research assumptions with no existing governance authorization — exactly as the
current `UNCERTAINTY_MARGIN=0.10` itself is unauthorized (borrowed from an explicitly
unauthorized advisory figure). This proposal does not close that authorization gap; it only
replaces one unauthorized constant with an explicitly-flagged unauthorized function, pending
the same human/governance sign-off the current formula has always lacked.

GO/NO-GO FOR IMPLEMENTATION: **CONDITIONAL GO** for a first bounded experiment — specifically
Mechanism A, run only after (a) the quantile level `q` is either explicitly chosen and
justified by a human reviewer or is run as a small, disclosed sensitivity sweep (e.g. 3–4
values, not silently fixed), and (b) the degeneracy regression test (Ablation 2) passes
before any new result is trusted. No mechanism should be implemented, and no result should
be reported as an improvement, without the leakage audit (Ablation 4) passing and the
tail-concentration check (Ablation 5) being reported alongside any aggregate number. This
remains a research-only exploration; nothing in this design authorizes promoting K or
changing the production terminal-reserve formula.
