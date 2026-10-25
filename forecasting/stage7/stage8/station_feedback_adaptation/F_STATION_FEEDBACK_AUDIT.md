# F Station-Feedback Adaptation Audit

**Scope**: Conceptual/data-availability audit only. **No training. No code. No modification of
F, Candidate J, frozen Stage8.1, production code, governance files, or any frozen artifact.**
Candidate F remains the research control. This report answers the six questions in the task
from direct inspection of existing files only (listed in §7) — no repo-wide search, no
re-running of prior experiments.

---

## 1. Available station feedback — what already exists, as of forecast-time t

Inspected directly: `stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py`
and the resulting 37-feature matrix header (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`
/ `..._2025_CORRECTED.csv`).

**Already present as governed, forecast-time-causal features** (`build_corrected_feature_matrix.py:139,162-221`):
the `ctx_*` block is computed from `df_sites` (the actual-observation series) **strictly
restricted to `timestamp < origin_ts`** (the forecast-issuance time), per origin, before being
merged onto the feature matrix:

| Feature | What it is | Available? |
|---|---|---|
| `ctx_last_obs` | most recent actual SW_IN observation before forecast issuance | **YES — already in the 37-feature contract** |
| `ctx_mean_24h`, `ctx_max_24h` | 24h trailing actual-observation mean/max | **YES — already present** |
| `ctx_std_3h/6h/12h/24h` | trailing observed-volatility | **YES — already present** |
| `ctx_abs_change_1h/3h/6h`, `ctx_max_diff_6h`, `ctx_mean_diff_6h`, `ctx_slope_6h` | trailing trend/change statistics on actual observations | **YES — already present** |
| `ctx_kt_std_6h` | trailing clear-sky-index volatility (uses `clearsky_ghi`, also causal) | **YES — already present** |
| `solar_elevation`, `solar_zenith`, `month`, `hour` | pure geometry/calendar | **YES** |
| `cloud_frac` (= `fc_cloud_cover/100`) | NWP **forecast** cloud cover, not observed | **YES, forecast-origin, not an observation** |

**Conclusion: "previous actual solar generation" (persistence) is NOT a missing input — it is
already a governed input to F**, via `ctx_last_obs`/`ctx_mean_24h`/`ctx_max_24h` and the
trend/volatility statistics. Any new adaptation mechanism proposing to add "recent actual
solar history" would be **substantially redundant** with features F already has, unless it
targets something the `ctx_*` block does not capture (see below).

**NOT currently present as a feature, confirmed by direct grep of the feature-matrix build
script and both Candidate F/J training scripts — no column for any of these exists anywhere
in the pipeline today:**

| Candidate feedback signal | Exists today? | Where it would have to come from |
|---|---|---|
| **F's own previous prediction** (`pred_F(t-1)`, `pred_F(t-2)`, ...) | **NO** | Would require re-running F's inference over historical origins and storing a prediction history — F has no deployed prediction history yet (it is a research artifact, never run in production sequence) |
| **F's own previous residual / error** (`actual(t-1) - pred_F(t-1)`) | **NO** | Same constraint — depends on the (non-existent) F prediction history above |
| **Rolling/persistent bias state** (e.g. EWMA of F's recent residual) | **NO** | Derived from the above — does not exist until F has a prediction history |
| Recent residual **history over >1 step** (a residual time series, not just `t-1`) | **NO** | Same constraint |

**This is the central finding of this audit**: *F has rich observed-actual history as an input
already, but zero history of its own predictions or residuals*, because F has never been run
sequentially in anything resembling production or rolling-evaluation order — it exists only as
a single batch of EVEN-trained weights scored once against ODD and once against the 2025 blind
set. Every "adaptive"/"feedback" mechanism in §3 below that depends on F's own past error
(A, B, C, D, G) is gated on first constructing this residual history — which is itself a
**research step with its own leakage obligations** (see §2), not a free input.

**Not investigated / out of scope for this audit (would require going outside the two Stage8.1
directories and is not confirmed present or absent here)**: any station-side raw instrument
feed beyond what `build_corrected_feature_matrix.py` already merges in. This audit does not
claim such data doesn't exist elsewhere in the repo — only that nothing beyond the table above
was found in the files inspected.

---

## 2. Temporal information flow

```
forecast_F(t)              -- F's prediction, issued at origin time t, using only features
                               with timestamp < t (ctx_*, cloud_frac/fc_*, geometry)
     |
     v
actual(t)                  -- ground-truth SW_IN observed at/after t (becomes available only
                               after t has elapsed — by construction, after the forecast was
                               already issued and, in a real deployment, already acted on)
     |
     v
error(t) = actual(t) - forecast_F(t)     -- computable only once actual(t) is observed
     |
     v
adaptation / state update   -- e.g. append error(t) to a rolling buffer, update an EWMA bias
                                estimate, or retrain a correction model on a window ending at t
     |
     v
forecast_F(t+1)             -- the adapted/updated model issues the NEXT forecast, now allowed
                                to condition on error(t), error(t-1), ..., i.e. feedback up to
                                but not including t+1 itself
```

**Leakage risks identified, specific to this pipeline's EVEN/ODD structure** (verified from
`train_corrected_stage8_1_model.py:109-111`: `all_origins = sorted(...); i % 2 == 0/1` —
**positional alternation on sorted time**, not a block/date-range split):

1. **EVEN and ODD origins are temporally interleaved, not temporally separated.** Origin `k`
   (EVEN) and origin `k+1` (ODD) are adjacent in time. A feedback mechanism that uses
   "the previous origin's residual" as a feature **during EVEN-only training** would, for most
   EVEN origins, be using the residual from an **ODD origin** (or vice versa, depending on
   direction) as an input — this does not leak the *target* `actual_SW_IN` for the row being
   predicted, but it does mean the EVEN training set and ODD held-out set become **statistically
   entangled through time-adjacency**, which is a different and more subtle violation than
   classic leakage: it could inflate the *apparent* independence of the ODD validation metric
   from training, because ODD-origin actuals partially leak into EVEN-origin **features** (not
   targets) by adjacency. **This must be explicitly handled** (e.g. by using only same-split
   residual history, or accepting a short causal gap, and disclosing the choice) in any
   mechanism design, not glossed over.
2. **The 2025 blind set has no such interleaving problem internally** — 2025 origins are used
   "whole" (per `CANDIDATE_F_REPORT.md`'s own note on there being no EVEN/ODD split for 2025),
   so an *online/sequential* adaptation mechanism evaluated purely within 2025 (ingesting
   `error(t)` only after it's observed, never touching `error(t')` for `t' > t`) is the cleanest
   place to test real feedback behavior with the least structural leakage risk.
3. **Constructing the residual history itself requires running F's frozen weights over a
   sequence of origins "as if" deployed.** This is an inference-only exercise (no `.fit()`), but
   must be done in strict temporal order and must not use any origin's own future rows to build
   its own `ctx_*`-style trailing statistics — the existing `ctx_*` convention in
   `build_corrected_feature_matrix.py` already demonstrates the correct pattern (strict
   `timestamp < origin_ts` windowing) and should be copied exactly for any new "residual
   history" feature, not reinvented.
4. **Any correction model trained on a residual history must not be tuned/selected using 2025**
   data, per the standing governance rule already followed by every candidate (B through J) in
   this investigation — tuning happens only on 2024-ODD (with the entanglement caveat in
   point 1 now disclosed), and 2025 remains the blind test exactly once.

---

## 3–4. Candidate adaptation mechanisms — feasibility, data, leakage, complexity, failure mode

| # | Mechanism | Required data | Does POLARIS have it now? | Leakage risk | Implementation complexity | Likely failure mode | Evaluable on existing 2024/2025 data? |
|---|---|---|---|---|---|---|---|
| A | **Adaptive residual correction** (a learned function of recent residual state, updated continuously) | F residual history, strictly causal | **NO** (must be constructed first, per §1) | Moderate — must respect point 1/§2 interleaving caveat if trained on EVEN | High — needs a residual-history pipeline plus a correction model | Same as Candidate D (generic residual correction already failed blind) unless the *conditioning* is meaningfully different (see §5) | Yes, but only after building the residual-history artifact (an inference-only, not training, prerequisite) |
| B | **Rolling bias correction** (e.g. EWMA of recent signed error, subtracted from the next forecast) | F residual history (signed, not absolute) | **NO** | Low if purely online within 2025 (point 2, §2); higher if also fit/tuned on EVEN due to interleaving | Low — simplest mechanism on this list, a single smoothing constant | A pure rolling-mean bias correction can only correct a *slowly varying* bias; Phase-1 forensics show bias varies **systematically with elevation/cloud regime/season**, not just slowly in time — a time-only rolling correction may systematically lag or misfire across regime transitions (e.g. a run of clear mornings followed by a cloudy afternoon) | Yes — can be backtested purely online on 2025, no retraining required, cheapest mechanism to actually try first |
| C | **Regime-specific residual correction** (separate bias/correction term per elevation/cloud/season bucket, updated from that bucket's own residual history) | F residual history, bucketed by the same bins already used in forensics (elevation, cloud regime, month) | **NO** (residual history) but the **bucket definitions already exist and are reused** (Candidate G's `is_transition_cloud`, the elevation bins from `ERROR_FORENSICS_REPORT.md`) | Low-moderate — same causal constraint as A/B, plus thinner per-bucket sample sizes raise a different (statistical, not leakage) risk | Moderate | **Directly predicted by evidence already in hand**: Candidate I (a targeted, regime-specific residual correction restricted to the high-elevation bucket) already failed exactly this way — see §5. A per-bucket rolling correction risks the same thin-sample overfitting unless very simply parameterized (e.g. a single scalar per bucket, not a learned model per bucket) | Yes, with the same prerequisite as A |
| D | **Expanding-window retraining** (periodically refit F from scratch on all data up to the current point, including newly observed actuals) | Full historical feature+target history, retrained periodically | Partially — 2024 EVEN exists; this would mean retraining *during* 2025 using 2025 actuals as they accrue | **High** — this explicitly uses 2025 (the blind set) as training data partway through the blind period, which **directly contradicts this investigation's standing governance rule** ("2025 is the blind set, untouched by training for any candidate") unless the evaluation protocol is redefined (e.g. "blind" redefined origin-by-origin as "not yet retrained on") | High — full retraining pipeline, versioning, and a redefinition of what "blind" means | Governance/definitional failure mode, not a modeling one: without a very carefully redefined protocol, this mechanism **cannot be evaluated against the existing 2025 blind set as currently governed** | **No, not under the current blind-set definition** — would require a new, explicitly-approved protocol change, out of scope for this audit to propose unilaterally |
| E | **Periodic retraining** (same as D but on a fixed schedule rather than continuously expanding) | Same as D | Same constraint as D | Same as D | Same as D | Same as D | Same as D — **No**, same governance blocker |
| F | **Ensemble/blending with complementary models** (e.g. blend F with Candidate J, or with the frozen control, by a learned or fixed weight) | Predictions from ≥2 already-fitted models (F, J, control) — **this data already exists**, no residual history needed | **YES** — F, J, and the frozen control already have predictions on 2024-ODD and 2025 | Low if the blend weight is fixed/pre-specified (e.g. a simple average) or selected only on ODD; higher if a *learned* blending model is fit — must still respect EVEN/ODD-only-for-fitting discipline | Low (fixed weight) to moderate (learned blend) | Already have a directly relevant negative data point: **J's own EMS-replay result showed J's forecast-level gain over F did not translate to a significant EMS benefit, with a bootstrap CI crossing zero** — a naive F/J blend is likely to land *between* F and J on both forecast and EMS metrics, i.e. plausibly **no better than F alone**, since J does not demonstrably add orthogonal information at the EMS-relevant level, only a correlated forecast-level nudge | **Yes — immediately, no new data/history needed**, the cheapest mechanism on this entire list to test |
| G | **Uncertainty/error-regime adaptation** (model outputs or conditions on its own predicted confidence/error-regime, adapting correction strength accordingly) | Residual history (to characterize regimes) **plus** some uncertainty signal (e.g. ensemble spread across F/J/control, or a quantile-regression spread) | **Partially** — F/J/control disagreement (`disagreement_fold`-style signal already exists for stage3b/stage4 in the 37-feature contract, confirmed by the feature-matrix header) could proxy for uncertainty without new history; a full error-regime *correction strength* adapter would still need the residual history from §1 | Same constraints as A/C for the residual-history-dependent half; low for the disagreement-based half (already-governed feature) | High — most complex mechanism on this list, combines a residual-history component and an uncertainty-adaptation component | Most speculative; without the residual-history prerequisite, cannot be built; even with it, no existing evidence in this investigation addresses error-*regime*-conditioned correction strength specifically | Partially — the disagreement-based half is testable now; the full mechanism needs the same prerequisite as A/C |

**Headline ranking by near-term feasibility (not by promise of success)**: **F (ensemble/blend)**
is the only mechanism testable **today**, on existing artifacts, with no new data construction
and no governance ambiguity. **B (rolling bias correction)** is the cheapest mechanism requiring
new (but purely-online, 2025-internal) history construction. **A/C/G** all share the same
residual-history prerequisite and inherit real risk already demonstrated by D and I (§5).
**D/E (retraining mechanisms) are currently blocked by the governance definition of "blind,"**
not by data availability — any attempt at them should first get an explicit decision on
redefining the blind-set protocol, which is outside this audit's authority to decide.

---

## 5. Why Candidate D failed, and what it implies for designing a better feedback mechanism

Reusing existing evidence only (`CANDIDATE_COMPARISON_REPORT.md` §"Candidate D";
`CANDIDATE_I_REPORT.md` and `CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md` for the related,
later Candidate I failure) — **no re-run performed**.

**Candidate D** (generic, untargeted residual correction): base model fit on EVEN; a second-stage
HGB trained to predict `actual_SW_IN − oof_base_prediction` using 2-fold **out-of-fold** base
predictions within EVEN (specifically to avoid training the correction on in-sample-overfit
residuals — a real attempt to control for the obvious leakage risk). Result: ODD MAE improved
substantially (36.20→35.53) but **blind-2025 MAE did not** (35.97→36.07, slightly worse);
bootstrap CI ≈ centered on zero. **Textbook validation-set overfitting**: the correction model
learned structure in the EVEN-internal OOF residuals that did not generalize to a genuinely
different year.

**Candidate I** (targeted version of the same idea, restricted only to the high-elevation≥30°
subset, built later in this investigation specifically to address D's untargeted-overfitting
critique by narrowing scope): still failed — ODD looked good (bias swung to −0.35) but blind CI
included zero, and critically **the targeted regime's own bias got worse than even the frozen
control** (+13.75→+20.07), the opposite of the intended effect, attributed to thin per-bucket
sample size (the high-elevation EVEN subset is a small fraction of 174 EVEN origins).

**What this implies for any new feedback mechanism** (direct inference from the above, not
a re-test):

1. **Narrowing the correction's scope (D→I) did not fix the core problem — it reproduced it in
   a smaller, thinner sample.** Any residual/feedback mechanism in §3 that works by *learning*
   a correction function (A, C, G) faces the same risk unless it is (a) much more heavily
   regularized / lower-capacity than a full second-stage HGB, or (b) validated with a
   much stricter generalization check than 2024-ODD alone (which Candidate J's own EMS result
   already shows can diverge from blind/EMS-level significance even for a candidate that *did*
   pass the forecast-level blind bar).
2. **A low-capacity, non-learned mechanism (B: a single scalar rolling bias term, or F: a fixed
   blend weight) is structurally less able to overfit** than a full second-stage model — this is
   the strongest evidence-based argument for trying B or F before attempting a learned
   residual-correction mechanism (A/C/G) again.
3. **Both D and I's failures occurred specifically on blind-2025, not on 2024-ODD** — reinforcing
   that **any new mechanism's promotion bar must be the blind-2025 corrected-bootstrap CI**,
   exactly as already standardized in this investigation, and that a strong ODD/validation
   result alone (as D and I both had) is **not evidence of anything** by itself.
4. Neither D nor I used genuine **temporal feedback** (a residual history updated causally over
   time) — both used a single static OOF-based correction fit once on EVEN. **The specific
   "station feedback" framing of this task (adaptation from a running residual history) has
   literally never been tested in this investigation** — D/I's failure is evidence about
   *static residual-correction-as-a-second-model*, not about *temporal/rolling feedback* per
   se. This is a meaningful distinction: it means D/I's failure, while a strong cautionary
   signal, does not by itself rule out mechanism B or F.

---

## 6. Recommended next single experiment

**Recommended: Mechanism F — a fixed-weight ensemble/blend of Candidate F and Candidate J's
predictions (not a learned blend), backtested on 2024-ODD for weight selection and scored once
on blind-2025, with both forecast metrics and an EMS replay.**

**Why this one, specifically, over B or a residual-history mechanism:**
- It is the **only mechanism in §3/§4 requiring no new data construction** (F and J predictions
  on ODD/2025 already exist as artifacts in `stage8_1_station_tuning_research/`) — lowest
  implementation risk, fastest to execute correctly.
- It **uses F as the baseline** (F is one of the two blend components; the blend is only
  interesting if it beats F alone) and **leaves the untouched 2025 blind set untouched for
  weight selection** — the blend weight would be chosen on 2024-ODD only, exactly like
  Candidate E's hyperparameter selection protocol, then scored once, blind, on 2025.
- It **sidesteps D/I's specific failure mode entirely** — there is no learned correction model
  to overfit; the only "parameter" is a single scalar blend weight (or even a fixed 50/50
  average as the simplest first cut), which is the low-capacity design §5 point 2 argues for.
- It **directly answers an open question already raised by the EMS replay result**: J's
  forecast-level gain over F didn't translate to a significant EMS benefit (CI crossed zero) —
  a blend test would clarify whether F and J's residual patterns are *complementary* (blend
  beats both) or *redundant* (blend is no better than F alone, consistent with the EMS null
  result already found), which is scientifically informative either way and does not require
  presupposing success.
- It **has strict temporal ordering trivially satisfied** (no sequential/online component at
  all — it's a static combination of two already-fitted models' predictions on the same rows),
  avoiding every leakage subtlety raised in §2.
- It is **fully reproducible with existing provenance conventions** (hash F's and J's existing
  prediction artifacts, hash the new blend script and its output, re-verify the frozen
  control/feature-matrix/freeze-manifest hashes before and after, use
  `research_utils.bootstrap_mae_diff_ci_corrected()` exactly as J's audit did).
- It **can include EMS replay metrics** using the exact same `run_candidateF_actual_solar_replay.py`
  /`run_candidateJ_actual_solar_replay.py` pattern already established, on the same 245 NORMAL
  origins, with corrected paired bootstrap CIs — both forecast-level and EMS-level evaluation are
  directly feasible with zero new infrastructure.

**Explicitly not recommending** B (rolling bias correction) as the *first* experiment, despite
also being low-complexity and feasible: B requires constructing F's causal residual history on
2025 for the first time in this investigation (§1/§2), which is a real, if modest, new
implementation surface with its own leakage-discipline obligations (§2 point 3) — whereas the
ensemble blend requires building nothing new. **If the blend result is a clean null (most likely
outcome given the EMS replay finding above), mechanism B — the cheapest mechanism that actually
tests genuine temporal feedback rather than static combination — is the natural next step after
this one**, not a competing first choice.

**This recommendation is conditional and non-speculative**: it identifies the lowest-risk,
most-evidence-grounded next test, not a prediction that the blend will beat F. Per instruction,
**no model is trained and no code is written in this report.**

---

## 7. Explicit UNKNOWNs / missing data

- **UNKNOWN**: whether any station-side raw data exists beyond what
  `build_corrected_feature_matrix.py` already merges — not searched for (out of scope per the
  "no repo-wide review" instruction); this audit can only state what is confirmed present or
  absent in the files it inspected.
- **UNKNOWN / missing**: F's own prediction/residual history does not exist yet in any form —
  constructing it (inference-only, causally ordered) is a prerequisite for mechanisms A, B, C,
  G, not something this audit found already built.
- **UNKNOWN**: whether the EVEN/ODD temporal-interleaving entanglement (§2 point 1) has
  measurably affected any *prior* candidate's reported ODD-vs-blind gap (e.g. whether it
  partly explains why D/I looked good on ODD but failed blind) — plausible as a contributing
  factor, not established as causal by this audit; no claim is made that it was the primary
  cause of D/I's failure (the overfitting explanation in §5 is the one directly supported by
  the existing reports).
- **UNKNOWN**: whether mechanisms D/E (retraining) could be made governance-compatible under
  a redefined blind-set protocol — this audit does not have the authority to redefine
  governance and does not attempt to.
- **Not missing, but worth flagging as a scope boundary**: this audit did not re-run or
  re-verify any hashes, since no artifact was read for the purpose of numeric reproduction
  (only for structural/column inspection) — no training, no inference, no modification
  occurred, consistent with the task's explicit constraints.

---

## Files inspected (complete list — no other files read for this audit)

- `stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py`
- `stage7/stage8/stage8_1_corrected_2025/train_corrected_stage8_1_model.py`
- `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` (header only)
- `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` (header only)
- `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv` (header only)
- `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_official_odd_predictions_2024.csv` (header only)
- `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_F_REPORT.md`
- `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_COMPARISON_REPORT.md`
- `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md`
- (already in session context, not re-read: `CANDIDATE_F_PRE_TRAINING_AUDIT.md`,
  `CANDIDATE_I_REPORT.md`-derived findings as cited in the above reports,
  `CANDIDATE_J_PRE_EMS_AUDIT.md`, `CANDIDATE_J_EMS_REPLAY_REPORT.md`)

No file was modified. No model was trained. No `.fit()` call was made. No code was written
other than this report.

---

## STOP — terminal summary

- F remains research control: **YES**
- J promoted over F: **NO**
- Station feedback sufficient for causal adaptation study: **PARTIALLY** — observed-actual
  history is already present (`ctx_*`); F's own prediction/residual history is **not yet
  constructed** and is a prerequisite for most feedback mechanisms (A/B/C/G), though not for
  the recommended next experiment (F: ensemble blend, which needs no new history).
- Recommended next experiment: **a fixed-weight (not learned) ensemble blend of Candidate F
  and Candidate J, weight-selected on 2024-ODD only, scored once on blind-2025 with both
  forecast metrics and an EMS replay, using the existing corrected-bootstrap methodology.**
- Files inspected: `build_corrected_feature_matrix.py`, `train_corrected_stage8_1_model.py`,
  2024/2025 feature-matrix headers, 2024/2025 prediction-file headers,
  `CANDIDATE_F_REPORT.md`, `CANDIDATE_COMPARISON_REPORT.md`,
  `CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md`.
