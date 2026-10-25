# Candidate K — Causal Residual History Design Audit

**Scope**: Design audit only, worked directly in this session, no subagents. **Nothing
implemented. Nothing trained. The K experiment is not run.** This audit inspects only the files
needed to establish causal ordering and residual/feature semantics:
`stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py`,
`stage7/stage8/stage8_1_station_tuning_research/phase2_candidateF_additive_feature.py`, and
direct inspection (via `csv`, not pandas — pandas is unavailable in this environment) of
`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`'s actual row structure. All findings below
are read directly from code/data, not assumed.

---

## 1. Exact F prediction pipeline

**Origin/horizon structure, confirmed by direct inspection of the 2024 feature matrix**:
- **347 unique origins in 2024, issued exactly once per calendar day, at `00:00 UTC`**
  (`forecast_start` values are consecutive midnights: `2024-01-20 00:00:00+00:00`,
  `2024-01-21 00:00:00+00:00`, ... `2024-12-31 00:00:00+00:00` — confirmed by direct read of
  all 347 unique `forecast_start` values).
- **Each origin has exactly 24 rows, `horizon_hour` 1–24**, confirmed (8,328 total rows =
  347 × 24 exactly).
- **`timestamp = forecast_start + (horizon_hour − 1)` hours** — confirmed directly: origin
  `2024-01-20 00:00`, `horizon_hour=1` → `timestamp=2024-01-20 00:00` (same instant);
  `horizon_hour=2` → `timestamp=2024-01-20 01:00`; ... `horizon_hour=24` →
  `timestamp=2024-01-20 23:00`. **Each origin's 24 horizons cover exactly one full calendar
  day, with no gap and no overlap with the next origin's day.**
- **Consequence — no duplicate/overlapping target timestamps exist anywhere in this dataset.**
  Origins are daily and their horizon windows are contiguous, disjoint, one-per-day. This
  removes an entire class of leakage risk the task asked about (§3) by construction, not by
  mechanism design — confirmed empirically, not assumed.
- **Feature construction causal ordering** (`build_corrected_feature_matrix.py:169-222`): the
  `ctx_*` block (trailing actual-observation statistics) is computed **once per origin**, using
  `df_sites` rows with `context_start = origin_ts − 24h ≤ timestamp < origin_ts` — i.e. strictly
  before the **origin's issuance time**, not per-horizon. All 24 horizons of a given origin
  share the identical `ctx_*` values, because the entire day's forecast is issued as a single
  batch at `00:00` for all 24 hours ahead at once.
- **F's actual prediction, read directly from `phase2_candidateF_additive_feature.py:163-171`**,
  is **not** a raw model output — it is a **residual-on-stage4** construction:
  ```
  pred_F = apply_night_zero( max(0.0, pred_stage4_fold + model_F.predict(X_38features)), is_night_causal )
  ```
  i.e. F's HGB model predicts a *correction* to an upstream `pred_stage4_fold` value, the sum is
  floor-clipped at zero (`np.maximum(0.0, ...)`), and then forced to exactly zero wherever
  `is_night_causal` is true (`solar_elevation ≤ 0` or `clearsky_ghi == 0`, confirmed in
  `build_corrected_feature_matrix.py:139`). **Any residual-history mechanism for Candidate K
  must be defined on this final, clipped, night-zeroed `pred_F`**, not on the raw HGB output —
  consistent with how every metric (MAE, bias, etc.) in every prior report in this investigation
  is computed on this same final quantity.
- Training/evaluation is restricted to `is_daytime` rows (`phase2_candidateF_additive_feature.py:130-136`)
  — a separate, looser filter than `is_night_causal` (confirmed as a distinct column in the
  metadata columns list of `build_corrected_feature_matrix.py`). **This audit does not have
  independent confirmation of `is_daytime`'s exact boundary condition** (not grepped in the
  files inspected) — flagged as an UNKNOWN in §10, not assumed.

---

## 2. Exact residual definition

Per §1, F's deployed prediction is already a final, clipped, night-zeroed quantity. The
residual Candidate K must use is:

```
residual(origin O, horizon H) = actual_SW_IN(timestamp(O,H)) − pred_F(O,H)
```

where `pred_F(O,H)` is the exact quantity defined in §1 (post-clip, post-night-zero) and
`actual_SW_IN` is the same ground-truth column used for every MAE/bias calculation in every
existing report. **Units**: both terms are W/m² (confirmed — this is the same unit used
throughout `CANDIDATE_F_REPORT.md`'s MAE/bias/RMSE tables). **Sign convention**: positive
residual = underprediction (actual exceeds forecast); negative = overprediction — this matches
the "bias" sign convention already used throughout the investigation (e.g.
`ERROR_FORENSICS_REPORT.md`'s "+13.75 at high elevation" describes the *frozen model's bias*,
i.e. `bias = mean(prediction − actual)` in that report's convention — **note the sign is
opposite to the residual defined above**; §9/§10 flags this explicitly so no sign error
propagates into K's implementation).

**Alignment**: both terms are indexed by the exact same `(origin, horizon_hour, timestamp)`
triple — no join/alignment ambiguity, since both come from the same row of the same feature
matrix (confirmed: `actual_SW_IN` is a column in the same CSV `pred_F` is computed from).

---

## 3. Causal history — exact rules, derived from §1's confirmed origin/horizon structure

**Core rule** (restated from the task, now made concrete): a residual may enter the correction
history for a *decision* made at origin `O`'s issuance time (`forecast_start = O, 00:00 UTC`)
only if its `actual_SW_IN` observation timestamp is `< O`.

Applying this to the confirmed daily-batch structure in §1:

1. **Same-origin earlier horizons may NOT be used.** All 24 horizons of origin `O` are decided
   simultaneously at `O`'s single issuance instant (`00:00`). At that instant, **zero** of that
   origin's own target timestamps have occurred yet — not even horizon 1 (`timestamp = O` itself,
   simultaneous with issuance, not yet "observed"). **There is no within-origin causal ordering
   to exploit** — this is a hard "NO," not a design choice.
2. **Previous origins may be used, and in fact ALL of a previous origin's 24 horizons are fully
   resolved by the time the next origin is issued.** Origin `O`'s last horizon (`horizon_hour=24`)
   has `timestamp = O + 23h`, which is strictly before `O + 24h` (the next origin's issuance,
   confirmed as exactly 24h later in §1). **So by construction, every one of origin `O`'s 24
   residuals is available, in full, before origin `O+1`'s decision is made.** This means
   Candidate K's history, at the time of any origin's decision, can safely include **every
   horizon of every strictly-prior origin**, with no partial-availability edge case to handle.
3. **Minimum history required**: at least one fully-resolved prior origin (24 residuals) before
   any correction can be computed for the *global* correction; for a **regime-specific**
   correction (§4), the minimum is "at least one prior occurrence of that specific regime,"
   which — given regime incidence rates already quantified in prior reports (e.g. the joint
   high-elevation×transition-cloud cell is only ~86/2885 ≈ 3% of EVEN rows) — may take many
   calendar days to accumulate even a handful of in-regime observations early in a deployment
   or backtest window.
4. **What happens with insufficient history**: the correction for that regime must default to
   **zero** (i.e. `corrected_prediction = pred_F` unchanged) until a minimum-count threshold is
   met — this is a required safeguard (§5/§8), not optional, since an estimate from 0 or 1 prior
   residuals in a thin regime is not a correction, it is noise amplification.
5. **Duplicate/overlapping target timestamps**: **do not occur in this dataset** (§1) — no
   additional handling rule is needed for this specific concern. (If this pipeline were ever
   extended to sub-daily or overlapping-origin issuance, this would need revisiting — explicitly
   out of scope here since it does not describe the current data.)

---

## 4. Regime definition — smallest defensible option

Per the task's explicit instruction not to multiply buckets freely, and reusing only
already-validated, already-causal regime signals from prior reports (not inventing new ones):

- **`solar_elevation`**: continuous, forecast-time-available (pure geometry), already used as
  a raw feature and as a binning axis in `ERROR_FORENSICS_REPORT.md`.
- **`is_transition_cloud`**: `cloud_frac ∈ [0.2, 0.6)`, Candidate G's exact definition, already
  reused byte-identically by Candidate J (independently confirmed in
  `CANDIDATE_J_PRE_EMS_AUDIT.md`), itself derived from `cloud_frac = fc_cloud_cover/100`, an
  NWP-**forecast** field (not observed) — confirmed forecast-time-available.

**Comparing the three options the task poses**:

- **(A) `elevation × transition-cloud` as a single joint bucket** (the specific cell F's own
  residual forensics flagged as worst, n≈206 in blind-2025 / ~86 in EVEN): **feasible without
  leakage** (both inputs are forecast-time-available, per above), but **this is exactly the
  thinnest-support regime already shown (via Candidate I) to overfit a *learned* correction**.
  For a **low-capacity** correction (a running mean/EWMA, not a fitted model), thin support is
  still a problem — not an overfitting-to-noise problem in the Candidate-I sense, but a
  **variance/convergence** problem: an EWMA fed by ~3% of all rows updates extremely rarely and
  its running estimate will lag far behind any real drift, nearly worthless as "adaptive"
  feedback until a long synthetic or real deployment history accumulates.
- **(B) elevation buckets + transition-cloud, as two separate, additive/independent corrections**
  (not one joint bucket — a coarser bucket for elevation, e.g. `elevation ≥ 30°` yes/no,
  *and* a coarser bucket for cloud regime, e.g. transition yes/no, each maintaining its own
  independent running correction, combined e.g. by addition or by picking whichever applies):
  **feasible without leakage** (same inputs), and **structurally better-supported**: each axis
  individually has far more occurrences than their joint intersection (high-elevation alone is
  ~978/6,398 blind rows per `ERROR_FORENSICS_REPORT.md` §3; transition-cloud alone is
  ~958/6,398). **This is the smallest defensible regime representation that still targets both
  forensics-validated axes without inheriting (A)'s thin-joint-cell convergence problem.**
- **(C) another existing regime representation** — e.g. a single coarse 2-level "high-risk /
  low-risk" flag defined as `elevation ≥ 30° OR is_transition_cloud` (union, not intersection):
  simpler still, feasible without leakage, but **conflates two forensically-distinct error
  mechanisms** (monotonic elevation-bias vs. cloud-transition uncertainty) into one bucket,
  discarding the specific joint-regime signal that motivated K in the first place. Not
  recommended as the *first* design, but noted as a fallback if (B) still proves too thin in
  practice.

**Recommendation for this audit (design-level only, not implemented)**: **(B)** — two
independent, coarse, forensics-validated binary regime axes, each with its own low-capacity
running correction — is the smallest defensible design that (i) uses only forecast-time-
available information, (ii) avoids (A)'s thin-joint-cell convergence problem, and (iii) does
not discard the two specific signals the task explicitly asked to start from.

---

## 5. Correction mechanism — design options, safeguards (no hyperparameters selected)

**General form, exactly as the task specifies**:
`corrected_prediction(O,H) = pred_F(O,H) + correction(regime(O,H), causal_history(< O))`

**Options compared conceptually** (no coefficients/windows chosen):

| Option | Behavior | Strength | Weakness |
|---|---|---|---|
| **Fixed rolling mean** (simple average of the last N in-regime residuals) | Equal weight to last N observations | Simple, bounded, easy to reason about | Discontinuous jumps as old observations drop out of the window; "N" must be chosen per regime, and thin regimes may never fill a large window |
| **EWMA** (exponentially weighted moving average, decay λ) | Smooth, infinite effective memory with recency weighting | No hard window-size choice, naturally handles irregular/sparse regime occurrence (just doesn't update on off-regime days) | A single bad/extreme residual still perturbs the estimate immediately, just not as violently as a short rolling mean; needs its own minimum-history gate |
| **Clipped EWMA** (EWMA with the *input* residual capped at some ±bound before updating) | Same as EWMA, but bounds the influence of any single extreme residual | Directly addresses "one extreme residual dominating the correction" (an explicit required safeguard below) | Introduces one more hyperparameter (the clip bound) that itself needs principled selection, not guessing |
| **Minimum-history threshold (gate, not a standalone mechanism)** | Correction forced to zero until ≥K in-regime prior residuals observed | Directly addresses "regime starvation" | Not a correction mechanism by itself — a precondition layered on top of whichever of the above is chosen |

**Required safeguards, addressed design-conceptually (not numerically — no values chosen here)**:

- **One extreme residual dominating the correction** → clip the input residual before it
  updates any running statistic (clipped EWMA), and/or require the minimum-history gate so a
  single early observation can't alone define the correction.
- **Correction becoming too large** → clip the *output* correction itself (independently of
  clipping the input residuals) to some bound informed by the regime's own historically observed
  bias magnitude (e.g. not exceeding the largest bias magnitude already seen in forensics for
  that regime) — this is a second, independent clip from the input-clip above, serving a
  different purpose (bounding the *effect*, not just the *input*).
- **Regime starvation** (a regime that rarely or never occurs early in a backtest window) →
  the minimum-history gate (§3 point 4) defaulting to zero correction; additionally, the
  correction should **decay toward zero** (not freeze at its last value) if a regime goes
  unobserved for a very long stretch, to avoid staleness — a design detail (e.g. a time-based
  decay independent of the update-based EWMA decay) to resolve at implementation time, not here.
- **Correction oscillation** (the correction itself swinging up/down rapidly in response to
  noisy individual residuals) → this is precisely what EWMA's smoothing (vs. a short rolling
  mean) is designed to dampen; the decay/window hyperparameter controls this tradeoff directly
  and must be selected (on 2024 only, §6) with oscillation, not just blind MAE, as a criterion.
- **Night-time / near-zero solar behaviour** → the correction must **not** be applied to rows
  where `is_night_causal` is true — `pred_F` is already forced to exactly zero there (§1), and
  adding any nonzero correction would reintroduce a physically meaningless nonzero night
  prediction. The correction must be gated by the same `is_night_causal` mask F's own prediction
  pipeline already uses, applied identically.
- **Physically impossible negative predictions** → the final corrected prediction must go
  through the same `max(0.0, ...)` floor-clip F's own pipeline already applies (§1) — applied
  *after* adding the correction, not only before, since a negative correction could otherwise
  push an already-small `pred_F` below zero.

---

## 6. 2024 → 2025 governance protocol, made explicit

**Two distinct operations, as the task requires distinguishing:**

**(i) Using 2025 actuals, after each forecast, to update future forecasts within 2025 itself**
— i.e., once origin `O`'s actuals are observed (strictly after `O`, per §3), feed
`residual(O, ·)` into the running regime correction(s), so that origin `O+1`'s correction
reflects it. **This is the allowed operation** — it is the entire mechanism Candidate K exists
to test, and it never uses any information from origin `O+1` or later to compute origin
`O`'s own correction. This is a pure **online deployment simulation**, not training.

**(ii) Using 2025 actuals to select/tune K's hyperparameters** (the EWMA decay, the clip
bounds, the minimum-history threshold, the choice between regime representations A/B/C in §4)
— **this is NOT allowed**, exactly as the task states. Every one of these choices must be fixed
*before* the 2025 backtest begins, using only 2024 data.

**Confirmed protocol for (ii), given the EVEN/ODD structure already established** (from
`train_corrected_stage8_1_model.py`, confirmed in the companion decision report
`F_TRAINING_STRATEGY_DECISION.md` §8): because EVEN/ODD is a **positional interleaving** on
sorted origins (`i % 2`), not a block/date split, treating "2024" as a single continuous
online sequence for the *specific, narrow* purpose of selecting K's hyperparameters is the
cleanest option — **but this requires an explicit disclosure**: F itself was fit only on EVEN
origins, so F's *own* predictions on 2024-ODD origins are genuinely out-of-sample for F, while
F's predictions on 2024-EVEN origins are in-sample for F (F has seen those targets during its
own fitting). **A hyperparameter-selection backtest that runs K continuously across all of 2024
would therefore be computing residuals against F's in-sample (EVEN) and out-of-sample (ODD)
predictions interchangeably** — not a leakage of K's own training (K is not trained, only its
history is accumulated and a few scalar hyperparameters are chosen), but a **validity caveat**:
K's hyperparameter selection would be partly validated against F's own training-fit residuals,
which are not representative of F's true generalization error. **This should be disclosed, not
silently worked around, in K's eventual experiment report** — one principled resolution (stated
here as a recommendation, not a final decision) is to run the 2024 backtest **using only
F's ODD-origin predictions** (F's genuinely out-of-sample residuals) as the hyperparameter-
selection signal, skipping EVEN origins in the history/selection step entirely, since EVEN
residuals would otherwise understate F's true error and bias the selected correction.

**2025**: touched exactly once, as a single forward pass in strict origin order, residuals
feeding forward causally exactly as in (i) above, with zero re-selection of any hyperparameter
during that pass.

---

## 7. Failure modes — conditions under which K must be declared invalid even if MAE improves

1. **Any future leakage** — any residual with `actual_SW_IN` timestamp `≥` the origin whose
   correction it feeds enters the history. Given §1/§3's confirmed daily-batch structure, the
   concrete way this could happen in an implementation bug is using `<=` instead of `<` at the
   origin boundary, or accidentally including the *current* origin's own horizons in its own
   correction (§3 point 1 — this must be a hard exclusion, enforced in code, not just by
   convention).
2. **Correction history accidentally includes the current target** — a specific instance of
   (1): e.g. a bug where the history query window is `[origin − 24h, origin]` inclusive of
   `origin` itself, rather than strictly `< origin`.
3. **Hyperparameter tuning on 2025** — any K hyperparameter (decay, clip bounds, minimum-history
   threshold, regime representation choice) selected by looking at 2025 blind-MAE or blind-bias
   outcomes, even informally ("let's try a few decay values and see which looks best on 2025")
   — this invalidates the experiment regardless of the result, per the standing governance rule
   already enforced for every other candidate in this investigation.
4. **Systematic bias improvement caused by contaminated information** — e.g. if the regime
   definitions themselves were (hypothetically) redefined using 2025 statistics rather than
   reusing Candidate G/J's exact, already-frozen 2024-derived definitions.
5. **Correction improves MAE but creates large regime bias** — exactly the Phase-3 failure
   pattern (aggregate MAE improved while high-elevation bias got substantially worse): K must
   be evaluated on **bias at the targeted regime(s) specifically**, not aggregate MAE alone,
   per the success criteria already established in `F_TRAINING_STRATEGY_DECISION.md` §10.
6. **Correction creates worse EMS reliability** — even a forecast-level pass (CI excludes zero,
   no regime-bias regression) does not establish an EMS-level benefit, exactly as Candidate J's
   own forecast-level pass did not translate into a significant EMS replay result. A forecast-
   level pass for K would still require the same EMS-replay validation step before any claim of
   operational value.
7. **(Specific to K's online nature, not covered by prior candidates)**: if the online backtest
   accidentally re-orders origins (e.g. processes them out of chronological order, or
   parallelizes in a way that lets a later origin's residual update the history before an
   earlier origin's correction is computed), this silently reintroduces leakage even though no
   single line of code looks obviously wrong — this is a **process/ordering** failure mode
   unique to sequential/online mechanisms (not shared by any static candidate A–J in this
   investigation) and must be explicitly tested (e.g. an assertion that history length is
   monotonically non-decreasing and only grows with strictly-increasing origin timestamps)
   before trusting any K result.

---

## 8. (Combined into §9 implementation specification below, per the task's own output ordering — "failure criteria" content is in §7 above; this section intentionally kept short to avoid duplicating §7.)

---

## 9. Exact implementation specification (provided because the design is judged VALID — see verdict below). **Not implemented here.**

1. **Residual history construction** (inference-only, no `.fit()`): for each origin `O` in
   chronological order (2024 first for hyperparameter selection, then 2025 for the single
   backtest), after computing `pred_F(O, h)` for all `h=1..24` exactly as in §1, and once
   `actual_SW_IN(O, h)` becomes available (immediately, since all of `O`'s targets resolve
   before `O+1` per §3), compute `residual(O,h) = actual_SW_IN(O,h) − pred_F(O,h)` for all
   `h`, restricted to rows where `is_night_causal` is false (night rows contribute no
   meaningful residual signal and must be excluded from history, not merely uncorrected).
2. **Regime tagging**: tag each `(O,h)` with its two regime flags (§4 option B):
   `high_elev = (solar_elevation ≥ 30)`, `transition = is_transition_cloud` (Candidate G's exact
   `cloud_frac ∈ [0.2,0.6)` definition) — computed from already-available, already-governed
   features, no new feature engineering.
3. **Two independent running correction states**, each gated by its own minimum-history
   threshold (count TBD at hyperparameter-selection time, not chosen here) and each updated via
   a clipped-EWMA (input-residual clip and output-correction clip bounds TBD at
   hyperparameter-selection time): `correction_elev` updates only from `high_elev=true` rows;
   `correction_transition` updates only from `transition=true` rows.
4. **Combination rule** (also a hyperparameter-selection-time choice, not fixed here): e.g.
   `total_correction = correction_elev · 1[high_elev] + correction_transition · 1[transition]`
   (additive if both apply, zero if neither) — the exact combination rule for rows where both
   flags are true simultaneously must be decided and justified (e.g. additive vs. max vs.
   average) during hyperparameter selection, not assumed here.
5. **Final corrected prediction**: `corrected = max(0.0, pred_F(O,h) + total_correction)`, then
   `apply_night_zero(corrected, is_night_causal)` — identical floor-clip and night-zero steps F's
   own pipeline already uses (§1), applied a second time after the correction.
6. **Hyperparameter selection**: run the above as a pure online pass over 2024 origins in
   chronological order, using **only F's ODD-origin predictions** (per §6's disclosed
   resolution) to compute the history-feeding residuals and to score candidate hyperparameter
   settings (decay, clip bounds, minimum-history count, EVEN-origin exclusion) — selection
   criterion must include both aggregate MAE/bias **and** targeted-regime bias (per §7 item 5),
   not MAE alone.
7. **Blind 2025 backtest**: run the identical online pass, frozen hyperparameters, over all of
   2025 in chronological order exactly once; compute all standard metrics (MAE, RMSE, bias,
   nMAE, H1–H24, targeted-regime bias) plus the corrected paired bootstrap 95% CI
   (`research_utils.bootstrap_mae_diff_ci_corrected()`) for (K − F), exactly as done for every
   prior candidate.
8. **Provenance**: hash every new script/output; re-verify every frozen upstream artifact
   (control model, F's model/results, J's model/results, both feature matrices, freeze
   manifest) unchanged before and after, exactly as every prior report in this investigation
   has done.

---

## 10. UNKNOWNs

- **UNKNOWN**: the exact boundary condition of `is_daytime` (distinct from `is_night_causal`) —
  not confirmed by grep in the files inspected for this audit; flagged, not assumed, and should
  be resolved before implementation (it governs which rows are eligible to update history, not
  just which rows are scored).
- **UNKNOWN**: the exact numeric values for every hyperparameter named in §9 (decay, clip
  bounds, minimum-history count, flag-combination rule) — explicitly and correctly left
  unselected per the task's instruction; to be chosen only at 2024-only hyperparameter-selection
  time, not in this design audit.
- **UNKNOWN**: whether F's residual signal in 2025, once isolated, actually carries
  exploitable short-horizon regime-conditioned autocorrelation — this audit establishes that
  testing K is *causally safe*, not that K is *likely to succeed*; no claim of expected benefit
  is made.
- **UNKNOWN**: whether the EVEN-origin-exclusion resolution proposed in §6 is the only valid
  protocol, or whether an alternative (e.g. using a held-back late-2024 tail exclusively) would
  be preferable — flagged as a design choice for the eventual K experiment's own report to
  defend explicitly, not resolved here.
- **Not unknown, established by this audit**: the daily-origin, 24-horizon, non-overlapping
  structure (§1) and the resulting "no same-origin history, full prior-origin availability"
  rule (§3) are confirmed directly from data, not inferred from documentation.

---

## K DESIGN VALID:

**YES**

The causal information-flow is sound: origins are daily, non-overlapping, and every prior
origin's full 24-horizon residual set is guaranteed resolved before the next origin's decision
(§1, §3) — there is no partial-availability or overlapping-timestamp edge case to design around.
No same-origin horizon may feed its own origin's correction (a hard, structurally-enforced
exclusion, not a convention to remember). The recommended regime representation (§4 option B:
two independent coarse binary axes, not the thin joint cell) and the recommended correction
family (clipped EWMA with input-clip, output-clip, and minimum-history gating, §5) are both
low-capacity by design, directly addressing the specific overfitting mechanism that already
falsified Candidates D and I. The 2024/2025 governance split (§6) is enforceable with one
explicit disclosed caveat (EVEN-origin exclusion for hyperparameter selection, to avoid
contaminating the selection signal with F's own in-sample residuals) rather than a silent
workaround. The exact minimal implementation specification is given in §9.

**This verdict covers design validity only — it is not a prediction that Candidate K will pass
its own promotion bar (forecast-level bootstrap CI excluding zero, no targeted-regime bias
regression, and — if that passes — a subsequent EMS replay) once actually run.** Per the task's
instructions: **nothing has been implemented, trained, or run.**
