# F Training Strategy Decision

**Scope**: Decision/analysis only, directly in this session, no subagents. **No training. No
modification of F, Candidate J, frozen Stage8.1, or any artifact. No code written.** This
report builds directly on `F_STATION_FEEDBACK_AUDIT.md` (same directory) and the existing
Candidate D/F/I/J reports in `stage7/stage8/stage8_1_station_tuning_research/`. F remains the
research control; J is not promoted over F; the 2025 blind set remains untouched by this
report.

---

## 1. Current evidence

- **F** (37 control features + `elevation_x_cloud_frac`): blind-2025 MAE 35.9745→35.4948
  (Δ−0.48, bootstrap CI excludes zero) — the only forecast-level candidate that cleared the
  blind-improvement bar prior to J. High-elevation (≥30°) bias improved 13.75→12.74.
- **J** (F + `elevation_x_transition_cloud`): blind-2025 MAE improved further, 35.4948→35.3036,
  CI vs. F excludes zero at the forecast level — **but** the EMS actual-solar replay found
  (J−F) realized-unmet CI = [−26,858, +6,716] Wh, **including zero**: J's forecast-level edge
  over F did **not** translate into a statistically distinguishable EMS benefit. J is not
  promoted.
- **D** (generic untargeted OOF residual-correction second stage): improved on ODD, failed
  blind (CI ≈ centered on zero) — classic validation overfitting.
- **I** (targeted, high-elevation-only OOF residual correction, same mechanism as D but
  narrowed in scope): also failed blind, and its own targeted regime's bias got **worse than
  the frozen control** (+13.75→+20.07) — narrowing scope did not fix D's overfitting problem,
  it reproduced it in a thinner sample.
- **F's residual forensics** (`CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md`): F's remaining error
  is still substantially systematic (linear-probe R²=0.4395, barely down from the control's
  0.4457) and **regime-specific**, concentrated jointly in high-elevation × transition-cloud
  conditions (n=206, MAE 114.57, bias +45.38 — 3–4x worse than either axis alone) and in
  H10–H14/Aug–Sep. F reduced error *magnitude* in the regimes it targeted but did not change
  the *structure* of what's left.
- **Station-feedback audit** (`F_STATION_FEEDBACK_AUDIT.md`, same directory): F already
  consumes causal trailing-observation features (`ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`,
  trend/volatility stats) — persistence/recent-actual-history is **not a missing input**. What
  is missing is **F's own prediction/residual history** — F has never been run in any
  sequential/online order, so no feedback loop currently exists in any form.

**Net effect so far**: every mechanism that has actually been tried that resembles "learn from
F's own errors" (D, I) has **failed on blind data**, specifically by overfitting EVEN-internal
residual structure. Every mechanism that worked (F, J) worked by adding a **static, a-priori,
low-capacity feature** motivated by forensics, not by any form of error-feedback loop. This is
the single most important empirical fact this decision must respect.

---

## 2. Available feedback data (recap, see audit for full detail)

| Signal | Available now? | Causal at prediction time? |
|---|---|---|
| Recent actual SW_IN observations (`ctx_*`) | **Yes**, already a governed F input | Yes, strictly `timestamp < origin_ts` |
| `cloud_frac`, `solar_elevation`, month/hour/season | Yes | Yes (geometry/forecast) |
| F's own past predictions | **No** — must be constructed by running frozen F over historical origins in order | Would be, if constructed correctly |
| F's own past residuals (signed error) | **No** — depends on the above | Would be, if constructed correctly |
| Multi-model disagreement (F vs J vs control) | **Yes**, all three already have predictions on ODD/2025 | Yes — no new construction needed |
| A third, independent data vintage (to expand training) | **No** — Candidate B already established this is infeasible; only 2024/2025 exist | N/A |

---

## 3–4. Candidate methods — comparison

For each: required history, POLARIS availability, causal-at-prediction-time status, leakage
risk, behavior after detecting repeated over/underprediction, D/I applicability, blind-set
contamination risk, overfitting risk given dataset size (174 EVEN origins, ~2,900 EVEN daytime
rows), implementation complexity, and the evidence that would falsify it.

### 1. Full/partial model retraining (periodic, from scratch, on an expanded window)
- **Needs**: a third/expanded historical vintage, or willingness to retrain using 2025 rows as
  they accrue.
- **Available?** No third vintage (Candidate B: infeasible). Using 2025 to retrain mid-stream
  requires **redefining what "blind" means** — a governance decision, not a modeling one.
- **Causal at prediction time?** Only if retraining cadence strictly respects elapsed time.
- **Leakage risk**: **High by definition** under the current blind-set protocol — this is the
  one approach that structurally cannot be tested without first changing governance rules.
- **Behavior after repeated error**: would eventually "bake in" a bias shift into the whole
  model, but only after an entire retrain cycle — slow, coarse-grained adaptation.
- **D/I applicability**: not directly comparable — D/I were post-hoc correction layers, not
  full retrains; this approach's risk is procedural/governance, not statistical overfitting.
- **Blind-set contamination?** **Yes, by construction**, unless redefined.
- **Overfitting risk**: moderate (same architecture/regularization as control, just more data
  over time) — not the primary concern; the governance violation is.
- **Complexity**: high (versioning, scheduling, re-validation pipeline).
- **Falsifying evidence**: this approach is already blocked procedurally; no experiment can
  falsify it without first resolving the governance question, which is outside this report's
  authority.

### 2. Expanding-window / walk-forward retraining
- Same structural issue as #1 — walk-forward evaluation on 2025 means training on early-2025
  actuals to help predict late-2025, which **consumes the blind set incrementally**. Same
  verdict: **blocked under the current protocol**, not a statistical non-starter otherwise.
  Distinguishing it from #1: smaller retrain steps, same root problem.

### 3. Online learning (continuously updating model weights per new observation)
- **Needs**: a mechanism for incremental weight updates; HGB (the architecture used throughout)
  is not natively an online learner — this would require either a different model family or an
  approximate online-update scheme bolted onto a tree ensemble (non-trivial, no existing code
  path in this pipeline does this).
- **Available?** No existing infrastructure; would be new model-family work, not an adaptation
  of F.
- **Causal?** Yes, in principle, if done correctly per-observation.
- **Leakage risk**: low in principle (each update strictly uses only past data) but **easy to
  get wrong in practice** (e.g. inadvertently updating on a batch that includes same-day future
  horizons).
- **Behavior after repeated error**: continuous, fine-grained drift toward correcting observed
  bias — in theory the most responsive mechanism on this list.
- **D/I applicability**: not directly — D/I are batch corrections, not online updates; no
  direct evidence either way from this investigation.
- **Blind-set contamination?** Same structural tension as #1/#2 — "updating on 2025 as it
  arrives" is, again, using the blind set as training data, just continuously instead of
  periodically. **Blocked under the current protocol for the same reason.**
- **Overfitting risk**: potentially high with ~2,900 EVEN daytime rows and no batch
  regularization discipline — online updates on sparse regime-specific rows (e.g. the n=206
  high-elevation×transition-cloud cell) could overreact to single observations.
- **Complexity**: **highest on this list** — requires a new model family or bespoke online-HGB
  scheme never used anywhere else in this codebase.
- **Falsifying evidence**: would need a redefined blind protocol before any evidence could even
  be gathered; not a near-term candidate.

### 4. Rolling adaptive bias correction (e.g. EWMA of recent signed residual, applied as an additive shift to F's next prediction)
- **Needs**: F's own causal residual history (§2) — not yet constructed, but cheap and
  inference-only to build (no `.fit()`), following the exact causal-windowing convention
  `ctx_*` already uses.
- **Available?** Buildable now from existing artifacts (F's predictions + ground truth on
  2024-ODD and 2025), purely as post-hoc inference, no training required to construct it.
- **Causal at prediction time?** Yes, if windowed strictly before `origin_ts`, exactly like
  `ctx_*`.
- **Leakage risk**: **low**, with one caveat already flagged in the audit — the EVEN/ODD split
  is **positionally interleaved** (sorted-origin `i%2`), not block-separated, so building this
  history *during EVEN training* risks adjacency entanglement with ODD. **This mechanism is
  safest when evaluated purely online within a single, internally-sequential set (2025)** —
  i.e. as a test-time-only correction layer on top of the already-frozen F, not as a retrained
  component.
- **Behavior after repeated error**: a smoothed scalar shift that grows if F keeps
  over/under-predicting in the same direction, shrinks/reverses once the pattern breaks — the
  textbook "slow drift corrector."
- **D/I applicability**: **D/I's failure does not directly apply** — D/I were *learned, batch,
  high-capacity* correction models fit once on EVEN-internal OOF residuals; a rolling EWMA is a
  **single smoothing constant**, essentially zero model capacity, and is computed at test time
  from causal history rather than fit on training-set residuals. The overfitting failure mode
  that sank D/I (a flexible model learning EVEN-specific noise) has no clear analogue for a
  one-parameter smoother. This is the strongest "D/I doesn't apply" case on this list.
- **Blind-set contamination?** **No** — it can be backtested entirely online, within 2025 only,
  using only each origin's own causal past; no re-fitting of F, no use of future 2025 rows.
- **Overfitting risk**: **low** — one (or a small handful of) smoothing hyperparameter(s),
  selectable on 2024-ODD exactly like Candidate E's protocol, without the high-capacity-model
  risk that sank D/I.
- **Complexity**: **low** — simplest mechanism that actually implements genuine temporal
  feedback (as opposed to F (ensemble) or #7 below, which are static).
- **Falsifying evidence**: if the EWMA-corrected forecast's blind-2025 bootstrap CI (vs. F)
  includes zero, or if it reduces aggregate bias but **increases** bias in the high-elevation
  regime (the Phase-3 sample-weighting failure pattern), the approach is falsified by the
  exact same standard already used for every other candidate in this investigation.

### 5. Residual-learning model (a second, learned model predicting F's residual from features)
- This is **exactly Candidate D's mechanism**, generalized. **Already tested and already
  failed** on blind data. Re-attempting this as a general mechanism (not narrowed to a specific
  regime, which is Candidate I, also already failed) would be repeating a already-falsified
  experiment without new justification. **Not recommended to re-attempt in this generic form.**

### 6. Regime-specific residual correction (a learned correction per elevation/cloud/season bucket)
- This is **exactly Candidate I's mechanism**. Already tested, already failed, and failed in
  the single most informative way possible: by making its own targeted regime's bias *worse*
  than the frozen control, via thin-sample overfitting (the high-elevation EVEN subset is a
  small fraction of 174 origins; the specific jointly-targeted cell flagged by the residual
  forensics has only ~86/2885 EVEN rows). **Not recommended to re-attempt with a learned model**
  — however, a **non-learned** version (a single scalar offset per regime bucket, not a fitted
  model) is structurally closer to mechanism #4 (one parameter per bucket instead of one
  parameter overall) and inherits #4's "D/I doesn't directly apply" argument, **if** capacity is
  kept that low. A full learned correction per bucket remains falsified by existing evidence.

### 7. F + complementary-model ensemble (F blended with J and/or the frozen control)
- **Needs**: nothing new — F, J, and control predictions already exist on ODD and 2025.
- **Available?** Yes, immediately.
- **Causal?** Yes — trivially, it's a static combination of already-causal predictions.
- **Leakage risk**: lowest on this list if the blend weight is fixed or selected only on ODD.
- **Behavior after repeated error**: **this is the critical limitation** — a *fixed-weight*
  ensemble does **not** change behavior in response to observing that F has been systematically
  wrong; it only changes behavior if F and J's *errors* are sufficiently uncorrelated that
  blending reduces variance on average. Given the EMS replay already found J's edge over F is
  not statistically distinguishable at the outcome level, **this mechanism is informative about
  whether F and J carry complementary information, but it is not itself a feedback mechanism in
  the sense the central question asks about** (it cannot answer category C below).
- **D/I applicability**: not applicable — no learned residual model, no overfitting mechanism
  in the D/I sense.
- **Blind-set contamination?** No, if weight is selected on ODD only.
- **Overfitting risk**: low (one scalar weight, or even none if simple averaging).
- **Complexity**: lowest on this list.
- **Falsifying evidence**: if the blend's blind CI vs. F includes zero (likely, given the EMS
  null result already found for J vs F), the ensemble is falsified as a forecast-level
  improvement — but this would still be a clean, cheap, informative negative result.

### 8. Error-regime classifier + correction (classify which error regime is active, apply a regime-conditioned correction)
- This is a **more complex superset of #6** (regime-specific correction) with an added
  classification step. Inherits all of #6's thin-sample risk, plus adds classifier-error risk
  on top. No existing evidence in this investigation tests the classifier component
  specifically. **Not supported as a first experiment** — strictly more complex than #6 with no
  offsetting evidence advantage, and #6's *learned*-correction half is already falsified by I.

### 9. Uncertainty-aware adaptation (condition correction strength on model disagreement/uncertainty)
- **Needs**: an uncertainty signal (disagreement between F/J/control, or a quantile spread) —
  **partially available now** (stage3b/stage4 disagreement-style features already exist in the
  37-feature contract) — **plus** a residual history to decide *how* to use that signal, which
  does not yet exist.
- Most speculative mechanism on the list; no direct evidence for or against from D/I (neither
  tested uncertainty-conditioning). **Correctly ranked low only for being untested and complex,
  not for having failed** — but complexity and the missing-history prerequisite argue against
  it as a *first* experiment.

### 10. Other — a **non-learned, regime-and-time-aware rolling bias correction** (hybrid of #4 and #6's non-learned variant)
- Concretely: an EWMA-style rolling bias term, computed **separately within each of the few
  coarse regime buckets already validated by forensics** (e.g. high-elevation vs. not;
  transition-cloud vs. not), rather than one global EWMA. This combines #4's low-capacity,
  genuinely-causal-feedback design with #6's regime-awareness, while deliberately avoiding
  #6's failure mode by using **a smoothed running mean, not a fitted model**, per bucket — i.e.
  explicitly bounding capacity far below what sank Candidate I. This is a refinement, not a
  wholly new idea; evaluated below as part of the recommendation.

---

## 5. Candidate D/I lessons, applied directly to this decision

D and I both failed by the same mechanism: **a flexible, learned function fit on EVEN-internal
(or EVEN-subset) residuals generalized poorly to blind 2025**, and I's narrower scope made the
thin-sample overfitting *worse*, not better, in the exact regime it targeted. Two conclusions
follow directly, not by analogy:

1. **Any mechanism that re-introduces a learned, flexible residual-correction function
   (mechanisms #5, #6-as-learned, #8) is already falsified in its general form and should not
   be re-attempted without a materially different capacity constraint or data source** — not
   because "it's theoretically unsound" but because it has been **empirically tried twice and
   failed twice, on this exact dataset**.
2. **Mechanisms with structurally bounded capacity — a single scalar, or a small handful of
   scalars, derived from a running statistic rather than fit by gradient-boosted trees — have
   not been tried, and D/I's failure mode (overfitting a high-capacity function to a small
   training set) does not obviously transfer to them.** This is the decisive distinction this
   report rests on.

---

## 6. Recommended approach

**Mechanism #4 (rolling adaptive bias correction), specifically its regime-aware refinement in
#10: a low-capacity, smoothed running-bias correction computed separately for the small number
of coarse regimes the forensics has already validated (at minimum: high-elevation≥30° vs. not;
possibly crossed with transition-cloud), applied as a test-time additive adjustment on top of
F's existing prediction — not a retrained model, not a new feature, not a blend.**

This is explicitly **category C** (adapting future predictions using previously observed
station errors) — see §(central question) below for why this categorization matters.

---

## 7. Why it is preferred

1. **It is the only mechanism on this list that directly implements genuine temporal
   feedback** (category C — behaving differently *after* the station reveals systematic
   error) **while avoiding the exact overfitting mechanism that already falsified D and I
   empirically**, by construction keeping capacity at "a smoothed running mean" rather than "a
   fitted tree ensemble."
2. **It requires no new data** — F's residual history is buildable purely by inference
   (`.predict()`, no `.fit()`) on artifacts that already exist, following the identical causal
   windowing convention (`timestamp < origin_ts`) the existing `ctx_*` features already use and
   that this pipeline has already validated as leakage-safe.
3. **It can be evaluated with zero blind-set contamination**: backtested entirely online within
   2025 (sequential, causal-only, no re-fitting of F), the cleanest evaluation surface
   identified in §2 of the companion audit — unlike mechanisms #1/#2/#3, which structurally
   require redefining the blind-set protocol.
4. **It directly targets the specific, already-quantified residual structure** found in F's own
   forensics (regime-specific, not time-only — the joint high-elevation×transition-cloud cell is
   F's single worst slice) — this is not a generic "try feedback" proposal, it is scoped to the
   exact failure the evidence already identified, while deliberately **not** repeating the
   learned-per-regime-model approach (#6/#8) that already failed via Candidate I in that same
   regime.
5. **Mechanism #7 (ensemble) is cheaper but does not answer the central question** — a fixed
   blend doesn't adapt after detecting repeated error; it's a static combination, informative
   about model complementarity but not about feedback. #4/#10 is the cheapest mechanism that
   actually is a feedback mechanism.
6. **The Phase-3 sample-weighting lesson also applies here and is explicitly guarded against**:
   Phase 3 showed that naively pushing raw MAE down can make bias *worse* in the high-stakes
   high-elevation regime. The recommended correction must be evaluated on **bias at the targeted
   regime specifically**, not just aggregate MAE — carried into the success criteria below.

---

## 8. Exact future experiment design (NOT implemented or trained here)

**Experiment**: "Candidate K — regime-aware rolling bias correction on top of F."

- **Construction** (inference-only, no `.fit()`): for each 2025 origin `t`, compute
  `signal(t) = actual(t') - pred_F(t')` for all origins `t' < t` within 2025, using F's
  already-saved frozen weights and `.predict()` only. Maintain this as a causal running series,
  computed exactly as `ctx_*` is computed (strict `timestamp < origin_ts` windowing, per
  `build_corrected_feature_matrix.py`'s established pattern).
- **Regime buckets**: reuse exactly the bucket definitions already validated by forensics — at
  minimum `elevation >= 30` (yes/no), optionally crossed with `is_transition_cloud` (Candidate
  G's exact definition) — do not invent new bucket boundaries.
- **Correction**: for each regime bucket, maintain an EWMA (or simple trailing-window mean) of
  `signal(t')` restricted to past origins **in that same bucket**; apply
  `corrected_pred(t) = pred_F(t) + ewma_bucket(t)` at prediction time.
- **Hyperparameter** (the EWMA decay or window length): select using 2024-ODD only, by the same
  protocol Candidate E used for its grid search — **but note the EVEN/ODD interleaving caveat**
  (§2 of the companion audit): because EVEN and ODD origins are positionally interleaved, a
  residual history built to span both splits would entangle them; the safest selection protocol
  is therefore to **backtest the EWMA hyperparameter online within 2024 as a single
  continuous-time sequence** (ignoring the EVEN/ODD label for this specific construction step,
  since no re-fitting of F occurs — only F's frozen `.predict()` output is used), then apply the
  selected hyperparameter, frozen, to the 2025 backtest. This explicit protocol choice must be
  stated and justified in the eventual experiment's own report, not left implicit.
- **Final evaluation**: apply the frozen hyperparameter choice to an online backtest within
  2025 only, producing a single correction-adjusted prediction series; compare against F
  (uncorrected) exactly as every prior candidate has been compared against F/control, with the
  corrected-bootstrap methodology.

---

## 9. Leakage controls

- No `.fit()` call anywhere — F remains the frozen, already-validated model; only its
  `.predict()` output is consumed.
- Residual-history construction uses strict `timestamp < origin_ts` windowing, identical in
  spirit to the already-audited `ctx_*` feature convention.
- Hyperparameter (EWMA decay/window) selected on 2024 only; 2025 touched exactly once, as a
  pure backtest, never for selection.
- The EVEN/ODD interleaving risk (unique to this pipeline, documented in the companion audit)
  is explicitly named and the proposed protocol (treat 2024 as one continuous online sequence
  for this construction step only, since no training occurs) is disclosed rather than silently
  worked around.
- No new feature is added to F's own feature contract — this is a test-time wrapper around F's
  existing, frozen predictions, not a retraining of F.

---

## 10. Success / failure criteria

**Success** (mirrors the standing promotion bar used for every prior candidate): blind-2025
corrected-bootstrap 95% CI for (corrected − F) realized MAE difference excludes zero on the
improving side, **AND** bias at the targeted joint regime (high-elevation × transition-cloud)
does not worsen relative to F — explicitly guarding against the Phase-3 failure pattern (MAE
improves while targeted-regime bias gets worse).

**Failure**: either the CI includes zero, or the targeted-regime bias worsens even if aggregate
MAE improves. A failure here would be reported exactly as D, I, Phase 3, and J's EMS result were
— as a clean null, not reframed.

**Not itself a promotion decision**: even on success, this remains a research result pending the
same EMS-replay validation step J underwent (a forecast-level pass does not guarantee an
EMS-level benefit, as J's own result already demonstrated).

---

## 11. UNKNOWNs

- **UNKNOWN**: whether F's residual signal, once isolated as a running series, actually shows
  exploitable short-horizon autocorrelation within 2025 — this report argues the mechanism is
  *safe to test*, not that it is *likely to work*. No claim of expected success is made.
- **UNKNOWN**: whether the EVEN/ODD-interleaving-driven hyperparameter-selection protocol
  proposed in §8 is the only valid option, or whether a stricter alternative (e.g. selecting the
  EWMA decay on a held-back tail of 2024 only) would be preferable — flagged as a design choice
  for the eventual experiment's own report to defend, not resolved here.
- **UNKNOWN**: whether this mechanism, even if it passes the forecast-level bar, would survive
  an EMS replay the way J's did not — explicitly not predicted either way.
- **Not unknown, established by this report**: mechanisms #1/#2/#3 (full retrain, walk-forward,
  online learning) are blocked by the current blind-set governance definition, not by data
  availability or statistical reasoning — a distinction worth preserving precisely, since
  resolving it would require a governance decision outside this report's scope.

---

## Central question, answered directly

**Category mapping, as requested:**
- **A (improving the underlying forecast model)**: F and J themselves (already done, already
  evaluated) — not what this report is deciding between.
- **B (correcting systematic residuals after F predicts, via a learned function)**: mechanisms
  #5/#6-learned/#8 — **already empirically falsified twice** (D, I).
- **C (adapting future predictions using previously observed station errors — genuine
  feedback)**: mechanisms #4/#10 (rolling/regime-aware bias correction) and, in principle,
  #3 (online learning, currently blocked by governance) — **this is the category the central
  question is actually asking about**, and #4/#10 is the only member of this category that is
  both evidence-supported and immediately testable without a governance change.
- **D (improving the optimizer's response to forecast uncertainty)**: mechanism #9 and the
  EMS-side work already done separately in `POLARIS_EMS_GAP19_STAGE81_VS_BASELINE_RESEARCH_SIMULATION/`
  — out of scope for "training/adapting F" specifically, since it changes GAP19's dispatch
  logic, not F's predictions.

**The mechanism that can make F behave differently *after* the station reveals it has been
systematically wrong is category C — specifically mechanism #4/#10, not a retrain (blocked by
governance for #1-3) and not a static blend (#7, category-adjacent but not itself adaptive) and
not a learned residual model (#5/#6/#8, already falsified).**

---

RECOMMENDATION:
**Mechanism #4/#10 — a low-capacity, regime-aware rolling bias correction applied as a
test-time adjustment on top of F's frozen predictions (not a retrained model).**

WHY:
- It is the only tested-feasible mechanism in category C (genuine post-hoc feedback from
  observed station error), as opposed to category B (already falsified twice, by D and I) or
  a static blend (category-adjacent, not itself adaptive).
- Its capacity (a smoothed running mean, optionally per coarse regime bucket) is deliberately
  far below what sank D and I, which failed specifically by fitting a flexible tree-based
  correction to a small training set — this mechanism has no comparable flexible-fitting step.
- It requires zero new data collection — F's residual history is derivable purely from already-
  existing inference outputs, with no `.fit()` call.
- It can be fully backtested online within 2025 with zero contamination of the blind-set
  protocol, unlike full/expanding-window/online-learning retraining (#1/#2/#3), which are
  structurally blocked under the current governance definition of "blind."
- It directly targets the specific, already-quantified residual structure (high-elevation ×
  transition-cloud, H10–H14/Aug–Sep) found in F's own residual forensics, rather than being a
  generic, unmotivated feedback proposal.
- It explicitly carries forward the Phase-3 lesson (bias-at-the-targeted-regime must be checked,
  not just aggregate MAE) into its own success criteria, rather than repeating that failure mode.

NEXT EXPERIMENT:
**Candidate K — construct F's causal residual history on 2024 (continuous-time, inference-only)
and 2025 (inference-only); select an EWMA/rolling-window hyperparameter for a regime-aware
(high-elevation × transition-cloud bucket) bias correction using 2024 only; backtest the frozen
hyperparameter choice online within 2025 exactly once; evaluate against F using the corrected
paired bootstrap methodology on both blind-2025 forecast MAE and (if the forecast-level result
passes) a subsequent EMS actual-solar replay, exactly as done for Candidate J.**

DO NOT IMPLEMENT OR TRAIN IT YET.
