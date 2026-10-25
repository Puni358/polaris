# Phases 2–5 — Station-Specific Learning Candidates vs. Frozen Stage 8.1 Control

**Governance, confirmed throughout**: frozen Stage8.1 (`stage8_1_CORRECTED_candidate_37feature_model.joblib`,
SHA256 `64ea4aba...`) remains the control and was **never modified, retrained, or re-saved**
— re-hashed after every step in this investigation, unchanged. All new models are
**EVEN-only research candidates**, trained on 2024-EVEN exactly like the control, tuned on
2024-ODD, and finally checked on **2025 — genuinely blind, never touched by training or
tuning for any candidate in this report**. The 37-feature contract is preserved for every
candidate except where explicitly noted. No candidate is promoted.

Scripts: [phase2_train_candidates.py](phase2_train_candidates.py) (SHA256 `f8430829...`),
[phase3_weight_experiment.py](phase3_weight_experiment.py) (SHA256 `cd9a59f2...`). Raw
results: [CANDIDATE_RESULTS.json](CANDIDATE_RESULTS.json) (SHA256 `0cd7410c...`),
[WEIGHT_EXPERIMENT_RESULTS.json](WEIGHT_EXPERIMENT_RESULTS.json) (SHA256 `a41fd56c...`).
Model artifacts (all new, all research-only): `model_artifacts/candidateC_H*.joblib`,
`candidateD_base.joblib`, `candidateD_secondstage.joblib`, `candidateE_best.joblib` (hashes
in the appendix table, §8).

**Reproduction/methodology note, disclosed**: this report's Candidate A ("frozen control")
numbers are the frozen artifact's own predictions, re-scored by this investigation's own
metric code — after correcting one methodological gap (the `is_night_causal` zero-override
the original training/evaluation scripts apply within the daytime-filtered subset, initially
missed in this report's first pass and fixed before any candidate numbers were finalized),
Candidate A reproduces the freeze doc's published numbers **exactly** (ODD MAE 36.2040,
Bias +0.9605; Blind-2025 MAE 35.9745, Bias +4.0802) — confirming this report's evaluation
code is methodologically consistent with the frozen model's own documented procedure before
any candidate comparison is drawn.

---

## Candidate B — "expanded same-station historical data": NOT TESTABLE, explicitly

**Not implemented. Marked UNKNOWN/infeasible, not worked around.** This repository contains
exactly two station-matched data vintages: **2024** (347 origins, split EVEN-train/ODD-held-out
by the frozen model's own methodology) and **2025** (364 origins, the genuinely blind test
set). There is no third, additional same-station historical vintage to "expand" into.
Using 2024-ODD for additional training would contaminate the one in-sample held-out
comparison point the frozen model itself reports; using any part of 2025 for training would
contaminate the only genuinely blind set available for *every* candidate in this report,
including B itself. **Per the explicit governance constraint ("never use blind ODD targets
for training/tuning"), no substitute or workaround was invented.** This candidate requires
data this repository does not have.

---

## Candidate C — Horizon-specific models (4 buckets: H1–6, H7–12, H13–18, H19–24)

Same architecture/hyperparameters as the frozen control, fit separately per bucket on
174-EVEN-origin daytime rows restricted to that horizon range (n=478–969 per bucket).

| | ODD 2024 (tuning) | Blind 2025 |
|---|---|---|
| MAE | 36.2040 | **36.3793** (control: 35.9745) |
| RMSE | 64.6672 | 66.8019 (control: 65.9427) |
| Bias | +1.1823 | +5.1031 (control: +4.0802) |
| nMAE% | 28.0807 | 28.5657 (control: 28.2478) |

**Result: worse than control on blind data, across every metric.** Splitting the already-
limited 174-origin training set 4 ways reduces per-bucket sample size enough to outweigh any
horizon-specific adaptation benefit — consistent with `horizon_hour` already being a usable
*feature* in the single unified model, which can already learn horizon-dependent splits
without sacrificing sample size. **Bootstrap 95% CI for (candidate − control) blind MAE:
[−0.03, +0.85]** — the interval barely includes zero on the "no difference" side; the point
estimate and nearly the whole interval indicate this candidate is **not better**, and quite
possibly worse.

## Candidate D — Residual-correction second stage

Base model = same architecture as control, fit on EVEN. Second-stage HGB trained to predict
`actual_SW_IN − oof_base_prediction` using 2-fold **out-of-fold** base predictions within
EVEN (to avoid training the correction on in-sample-overfit residuals). Final prediction =
base + second-stage correction.

| | ODD 2024 (tuning) | Blind 2025 |
|---|---|---|
| MAE | **35.5313** (control: 36.2040, looks better) | 36.0656 (control: 35.9745, **slightly worse**) |
| RMSE | 63.515 | 66.6733 (control: 65.9427) |
| Bias | −3.3436 | +1.1394 (control: +4.0802) |
| nMAE% | 27.5589 | 28.3193 (control: 28.2478) |

**Result: improves on the validation (ODD) set, does NOT improve on genuinely blind data** —
a textbook validation-overfitting pattern, exactly what Phase 4's "must improve on genuinely
blind data, not merely training/validation" requirement is designed to catch, and this
candidate fails that bar. **Bootstrap 95% CI: [−0.49, +0.66]** — centered almost exactly on
zero; no detectable blind effect in either direction. (Bias on blind-2025 *does* improve,
+1.14 vs. control's +4.08 — a genuine partial reduction in the overprediction tendency — but
this does not translate into a lower blind MAE/RMSE.)

## Candidate E — Hyperparameter search (144-point grid, selected by 2024-ODD MAE)

Grid: `max_depth∈{3,4,5,6} × min_samples_leaf∈{15,30,50,100} × l2_regularization∈{1,10,30} ×
learning_rate∈{0.05,0.1,0.2}`. Best by ODD MAE: `max_depth=5, min_samples_leaf=50,
l2_regularization=30.0, learning_rate=0.2`.

| | ODD 2024 (selection metric) | Blind 2025 |
|---|---|---|
| MAE | **34.6337** (control: 36.2040, −4.3%) | **35.7928** (control: 35.9745, **−0.5%**) |
| RMSE | 61.6846 | 65.2354 (control: 65.9427) |
| Bias | +2.1199 | +5.3735 (control: +4.0802, **worse**) |
| nMAE% | 26.8627 | 28.1051 (control: 28.2478) |

**Result: the only candidate with a blind-MAE point estimate in the improving direction**,
but the improvement (−0.18 W/m², −0.5% relative) is **far smaller than the −4.3% validation
improvement suggested**, and **bias actually worsens** (more overprediction, +5.37 vs.
control's +4.08 — the wrong direction for the EMS-relevant problem, see Phase 5).
**Bootstrap 95% CI: [−0.66, +0.29]** — includes zero; **not statistically distinguishable
from no effect** at the 95% level, despite being the best-looking candidate on paper.

## Phase 3 — Sample-weighting experiment (elevation-weighted training)

**Weighting rule, defined before evaluation** (from Phase 1's finding that the solar-elevation
≥30° bucket contributes 45.9% of total error): `sample_weight = 1.0 + clip(solar_elevation,0,90)/30.0`,
computed only from `solar_elevation` (known in advance, no target leakage). Same architecture/
hyperparameters as control, trained on EVEN with these weights.

| | ODD 2024 | Blind 2025 |
|---|---|---|
| MAE | 35.4913 (control: 36.2040) | 35.8626 (control: 35.9745, **−0.3%**) |
| Bias | +1.5671 | +5.1920 (control: +4.0802, **worse**) |

**Bootstrap 95% CI (blind MAE diff): [−0.44, +0.22]** — includes zero, not significant.
**High-solar-elevation subset specifically** (the targeted regime, blind-2025, n=978):
MAE improves slightly (99.43 vs. 100.93) **but bias worsens substantially** (+19.95 vs.
+13.75) — the weighting nudges raw error down marginally while making the systematic
overprediction *worse* in exactly the regime most responsible for the EMS-relevant problem.

**The four distinct "weight" meanings, explicitly distinguished per instruction**:
1. **ML sample weighting** (tested above: elevation-based row weights during HGB fitting).
2. **Model hyperparameter tuning** (Candidate E, above: a materially different concept —
   varies model *structure* parameters, not training-row influence).
3. **Ensemble weighting** (not applicable here — there is no ensemble of models being
   blended in this pipeline; not tested, not relevant to a single HGB estimator).
4. **Optimizer objective weights** (the EMS GAP19 `J1`–`J4` lexicographic priorities) —
   **explicitly NOT touched anywhere in this investigation**, per instruction.

---

## Phase 4 — Strict evaluation summary (train / validate / blind, as required)

| Candidate | Training period | Validation/tuning period | Blind eval period | Blind ΔMAE vs. control | Bootstrap 95% CI | Passes "blind improvement" bar? |
|---|---|---|---|---|---|---|
| A (control) | 2024 EVEN | 2024 ODD | 2025 | — | — | — (reference) |
| B | *(infeasible — no additional data exists)* | | | | | N/A |
| C (horizon-specific) | 2024 EVEN (per bucket) | 2024 ODD | 2025 | **+0.40** (worse) | [−0.03, +0.85] | **No** |
| D (residual correction) | 2024 EVEN (+ 2-fold OOF) | 2024 ODD | 2025 | +0.09 (flat) | [−0.49, +0.66] | **No** |
| E (hyperparameter search) | 2024 EVEN | 2024 ODD (selection) | 2025 | −0.18 (tiny improvement) | [−0.66, +0.29] | **No — CI includes 0** |
| Weight experiment (Phase 3) | 2024 EVEN | 2024 ODD | 2025 | −0.11 (tiny improvement) | [−0.44, +0.22] | **No — CI includes 0** |

**VERIFIED conclusion: no candidate tested in this investigation demonstrates a
statistically distinguishable improvement over the frozen Stage 8.1 control on genuinely
blind (2025) data.** Every candidate's 95% bootstrap confidence interval for the blind-MAE
difference includes zero. Candidate C is the only one trending toward being measurably
*worse*; the others are indistinguishable from no effect.

---

## Phase 5 — Forecast-value relevance to the 1,418,551 Wh component

**Per instruction, operational improvement is not claimed from forecast metrics alone — and
in this case the question is largely moot**, because **no candidate passed Phase 4's blind-
improvement bar in the first place**. There is no statistically-supported "materially
improved" candidate to check for regime-relevance.

What **can** be stated, as a secondary, directly-relevant observation: **every candidate
that nudged raw MAE in the improving direction (E, and the Phase 3 weighting experiment) did
so while making bias *worse* (more overprediction)** — specifically in the high-solar-
elevation regime Phase 3 targeted. Since the EMS actual-solar-replay decomposition
(`STAGE81_UNMET_DECOMPOSITION_REPORT.md`, separate investigation) established that **100% of
realized-unmet hours coincide with the forecast overstating actual solar at that hour**, a
candidate that reduces aggregate MAE by *increasing* overprediction bias in the
highest-stakes regime would, if anything, be **counter-productive** for the EMS-relevant
problem — not merely unhelpful. **This is a VERIFIED directional finding** (bias numbers
above), **not a claim that any candidate was deployed or would measurably worsen EMS
outcomes** (that would require re-running the EMS replay with a new model's predictions,
which was not done here and is explicitly out of scope for this forecasting-only
investigation).

---

## Recommendation for the single next candidate experiment

**None of the five tested approaches (C, D, E, sample-weighting, and B's explicit
infeasibility) justify promotion or further pursuit in their current form.** If one single
next experiment were to be chosen, it should **not** be a variant of C/D/E/weighting as
tested — all three already explored the "same features, different model-fitting mechanics"
axis without a statistically supported result. The one **Phase 1 finding not yet tested as a
candidate** is **Item F (additive features)**, specifically: the error forensics show a
**monotonic bias-vs-elevation relationship** (§3) that the current model, despite having
`solar_elevation` as a raw feature, is not fully correcting for. **The single most
narrowly-motivated next experiment** would be to add one additive, demonstrably-available-
at-runtime interaction feature — `solar_elevation × cloud_frac` (the product of the two
variables Phase 1 showed carry the strongest *individual* signal, `cloud_frac` coefficient
2.83 and `solar_elevation` coefficient 0.35 in the residual-predictability probe, §6 of the
forensics report) — and re-run the identical EVEN/ODD/blind-2025 protocol used here. **This
recommendation is conditional and not a promotion**: it identifies the most Phase-1-motivated
untested axis, not a prediction that it will pass the blind-improvement bar; per instruction,
no model is promoted and no speculative claim of improvement is made.

---

## 8. Reproducible artifacts, hashes, and provenance

| Artifact | Role | SHA256 |
|---|---|---|
| `phase1_error_forensics.py` | Phase 1 script | `77c2a11fea23928768726da17bda9b637f917673fe149209e50a21c013225d26` |
| `ERROR_FORENSICS_RESULTS.json` | Phase 1 raw output | `963366677e3a47d0e9067d12be720be1b9b227c1444805b3e7e2325655a5709a` |
| `phase2_train_candidates.py` | Phase 2 script (C, D, E) | `f8430829f81d075ac477247cc53c458a64748e948f7fa87034a03d2e990b946a` |
| `CANDIDATE_RESULTS.json` | Phase 2 raw output | `0cd7410cfe62d5885bd1170cd5edc6e73442dc5a04c4b95e38eae6e0c9a2d736` |
| `phase3_weight_experiment.py` | Phase 3 script | `cd9a59f2b46d1eeec57f9189b16628d28c42057513dd89bc86ad98d0a4ef2482` |
| `WEIGHT_EXPERIMENT_RESULTS.json` | Phase 3 raw output | `a41fd56c2d6bd084c6de606292b76d7a3ae4842ea01a7512f676cf3c70f49831` |
| `model_artifacts/candidateC_H1_6.joblib` | Candidate C, bucket H1-6 | `f7e637f39020248cb7691f266aa9cd42885161f3a3be35d1c8b7e70f6dc06038` |
| `model_artifacts/candidateC_H7_12.joblib` | Candidate C, bucket H7-12 | `b621a2a047c2ad289ee9a36a785d3568c9cf504ae15c1fe3eb71cbbb15849a98` |
| `model_artifacts/candidateC_H13_18.joblib` | Candidate C, bucket H13-18 | `5a898d626c27a0f41034acf2b39d04880f76e6ea6ab8a747b0010e62c98e5377` |
| `model_artifacts/candidateC_H19_24.joblib` | Candidate C, bucket H19-24 | `4df8d8c6df668883da8308c33c295c249fc50e2b3a2e506c885ed561182f032e` |
| `model_artifacts/candidateD_base.joblib` | Candidate D, base model | `7aded9e4672e9a1a284c52fbd05d2840090b2db4f0d64b69b9c22dfda8dcebd6` |
| `model_artifacts/candidateD_secondstage.joblib` | Candidate D, correction stage | `8d2a34b8a926666f5b5671e5ee91fe717d34469db2e92c9643d53e655f6de5c8` |
| `model_artifacts/candidateE_best.joblib` | Candidate E, best grid point | `3a6a460cbd1220d3f02efa50af11970473f134e96e3fcee1d9cb0c851854f1d7` |

**Frozen artifacts, re-verified unchanged after this entire investigation**:

| File | SHA256 | Matches freeze doc? |
|---|---|---|
| `model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib` | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` | Yes |
| `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | Yes |
| `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` | Yes |
| `stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` | Yes |
| `FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json` | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` | (production runtime manifest; not re-written by this investigation) |

## STOP

Investigation complete across Phases 1–5. **No candidate promoted. No frozen artifact,
freeze manifest, production runtime, or production config modified.** Every VERIFIED claim
traces to a hash-confirmed input and a script in this directory; every negative/null result
(Candidates B, C, D, E, and the Phase 3 weighting experiment) is reported as such, not
reframed as a positive finding.
