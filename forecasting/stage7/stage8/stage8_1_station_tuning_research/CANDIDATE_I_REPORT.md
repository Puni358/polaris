# Candidate I — Candidate F + Targeted High-Elevation (≥30°) Residual Correction

**Scope**: A deliberately NARROWER retry of the residual/feedback-learning axis than
Candidate D, per the task's explicit instruction that a retry "must be meaningfully
different ... targeted only at the high-elevation ... regime the forensics flagged, not a
repeat of D's untargeted approach." Candidate I adds a second-stage correction model on top
of Candidate F, trained ONLY on `solar_elevation ≥ 30°` EVEN rows (via 2-fold out-of-fold
base predictions, restricted to that subset) and applied ONLY to `solar_elevation ≥ 30°` rows
at inference; all other rows keep Candidate F's prediction unchanged. **Control is the
frozen Stage 8.1 model.** Script:
[phase8_candidateI_targeted_high_elevation_residual.py](phase8_candidateI_targeted_high_elevation_residual.py).
Raw results: [CANDIDATE_I_RESULTS.json](CANDIDATE_I_RESULTS.json).

## Forensic motivation

- `ERROR_FORENSICS_REPORT.md` §3: the `solar_elevation ≥ 30°` bucket alone accounts for
  **45.9% of total |error|** and the largest, most systematic positive bias (+13.75 W/m²) —
  the single largest avoidable-error regime identified.
- `ERROR_FORENSICS_REPORT.md` §6: R²=0.4457 for a linear probe of `|error|` on
  forecast-time-available features — exploitable residual structure exists in aggregate.
- `CANDIDATE_COMPARISON_REPORT.md` Candidate D's untargeted OOF residual correction (trained
  and applied on ALL EVEN/all rows) improved on validation (ODD) but not on blind data (CI
  centered on zero) — a textbook overfitting pattern, attributed here to the correction stage
  re-fitting base-model-specific noise across a heterogeneous, all-regime residual
  distribution rather than a genuinely separable, regime-specific signal.
- **Hypothesis under test**: a correction stage trained on a narrower, more homogeneous
  target (only the specific high-elevation regime forensics flagged) might generalize better
  than D's all-regime correction.

## Feature/method provenance and leakage check — VERIFIED

- Same 38 input features as Candidate F (37-feature contract + `elevation_x_cloud_frac`),
  all forecast-time-available (Candidate F audit item 2).
- The 2-fold OOF split used to build the correction-stage TRAINING target is computed
  entirely **within 2024-EVEN** (via a deterministic MD5 hash of each EVEN origin's
  `forecast_start` timestamp, `origin_fold()` in the script) — never touches ODD or 2025.
  Confirmed by code inspection: `model_corr.fit(X_corr_tr, oof_resid_tr)` where `X_corr_tr`
  and `oof_resid_tr` are sliced from `even_day` only (`phase8_candidateI_...py` lines
  ~168-176); `odd_day`/`day25` never appear in any `.fit()` call (grep-confirmed, same check
  pattern as the Candidate F audit used).
- `actual_SW_IN` is used only as the regression TARGET for both the base and correction
  stages (`y_tr`, `oof_resid_tr`), never as an input feature — same pattern as every prior
  candidate and the control itself.

## Methodology

Base model = Candidate F exactly (same fit on full EVEN). Correction stage: same
hyperparameters as the control/base (`HistGradientBoostingRegressor`, `max_depth=4`,
`min_samples_leaf=30`, `l2_regularization=10.0`, `loss="absolute_error"`, `random_state=42`),
fit on `n=489` high-elevation EVEN rows only (2-fold OOF residual target). Applied only to
`solar_elevation ≥ 30°` rows at inference on ODD and blind 2025; elsewhere Candidate F's
prediction is passed through unchanged. Bootstrap CI uses the CORRECTED utility.

Governance hash check (before training): 2024 matrix MATCH, 2025 matrix MATCH, frozen model
MATCH.

## Results — VERIFIED, candidate FAILS (validation-overfit pattern, same failure mode as D)

| | Control (frozen Stage 8.1) | Candidate F (base, reference) | Candidate I | Δ (I − control) |
|---|---|---|---|---|
| ODD 2024 MAE | 36.2040 | 35.4438 | **35.3792** (looks best) | −0.8248 |
| ODD 2024 Bias | +0.9605 | +0.7505 | **−0.3517** | swings past zero |
| **Blind 2025 MAE** | 35.9745 | 35.4948 | 35.5239 | **−0.4506** |
| Blind 2025 Bias | +4.0802 | +3.6959 | **+4.8951** (worse than control) | +0.8149 (worse direction) |

**Bootstrap 95% CI (CORRECTED), blind-2025 MAE (I − control)**: mean **−0.4596**, CI
**[−1.3535, 0.4329]** — **includes zero**. Despite a point estimate that looks like an
improvement (−0.46), the interval is wide and straddles zero — **not statistically
distinguishable from no effect**, and considerably less confident than Candidate F's own CI
(F: `[−0.8040, −0.1515]`, entirely excluding zero). The ODD-validation numbers (MAE 35.3792,
bias swinging from +0.75 to −0.35) looked like an improvement over even Candidate F, but
**the blind result does not confirm it** — **exactly the overfitting signature Candidate D
already exhibited**, now reproduced by this more narrowly-targeted variant.

## High-elevation subset (blind 2025, n=978, the specifically targeted regime) — VERIFIED, bias gets WORSE than control here

| | Control | Candidate F (base) | Candidate I |
|---|---|---|---|
| MAE | 100.925 | 98.6785 | **98.8561** |
| Bias | +13.7469 | +12.7406 | **+20.0706** (worse than BOTH control and F) |

Bootstrap 95% CI (CORRECTED), I vs. control: mean **−2.0275**, CI **[−7.0441, 3.0574]** —
wide, includes zero. **The targeted correction's bias in its own targeted regime is worse
than the frozen control's bias**, not merely worse than Candidate F's. This is the same
qualitative caution already raised for Phase 3's weighting experiment and now reproduced by a
different mechanism (targeted residual correction rather than sample weighting): an
intervention aimed squarely at the high-elevation overprediction problem can, on blind data,
make that regime's bias WORSE rather than better, even when validation (ODD) metrics look
favorable. Since the EMS-relevant asymmetry (100% of realized-unmet hours coincide with
forecast overprediction, per the cited but not re-run EMS replay) makes bias in exactly this
regime the highest-stakes quantity, this is a materially unfavorable result, not a borderline
one.

## H1–H24 breakdown (blind 2025) — VERIFIED, see JSON for full table

MAE improves at most horizons relative to control (18 of 24), broadly tracking Candidate F's
own pattern. However, **bias at the midday/high-elevation-correlated horizons (H9, H12–H17)
is consistently worse than control**, e.g. H13: control +15.33 → Candidate I +17.78; H16:
control +1.45 → Candidate I +6.88; H17: control +3.31 → Candidate I +8.36; H9: control +4.04
→ Candidate I +7.63. This horizon-level pattern is consistent with, and helps explain, the
aggregated high-elevation subset's bias degradation above — the correction stage's error is
not randomly distributed but concentrated at exactly the horizons/elevations it was built to
fix.

## Pass/fail against the promotion rule

**Rule**: blind-2025 MAE bootstrap 95% CI (CORRECTED) must exclude zero on the improving
side. Candidate I's CI `[−1.3535, 0.4329]` **includes zero** — **this candidate FAILS the
stated statistical bar**. Not promoted. The high-elevation-subset CI also includes zero
(`[−7.0441, 3.0574]`) and shows a bias regression even relative to the frozen control, making
this a doubly unfavorable result for the regime it specifically targeted.

## UNKNOWN / not established by this test

- Whether a different fold scheme (e.g. k>2 folds, or a wider elevation band for the
  correction-training subset) would reduce the apparent overfitting — not tested; this was a
  single, pre-specified design (2-fold, threshold exactly matching the forensics report's own
  ≥30° bucket boundary).
- Whether the correction stage's overfitting is primarily a small-sample effect (489
  high-elevation EVEN training rows is a much smaller training set than the ~2,900-row full
  EVEN set used by Candidates D/F/G/H) — plausible given the magnitude of the ODD-vs-blind gap,
  but not independently verified by a sample-size ablation here.
- EMS/dispatch-level impact — not evaluated (out of scope).

## Provenance / hashes

| Artifact | SHA256 |
|---|---|
| `research_utils.py` (shared, corrected-bootstrap utility) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` |
| `phase8_candidateI_targeted_high_elevation_residual.py` | `c4d79966a925480e0e43654321c648acc0d4293cf25a576b106970df56561814` |
| `CANDIDATE_I_RESULTS.json` | `a1da4f6429806336eb10104d1e371adce0b05dba26e4f0c7a34fa474ab4adb72` |
| `model_artifacts/candidateI_base_F.joblib` (= Candidate F's own artifact, deterministic refit) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| `model_artifacts/candidateI_high_elevation_correction.joblib` (new, research-only) | `379aaa78d732d3cc699f8ab555fc0b285ff902a706a6f14ebbb7877b646d06b1` |
| Frozen Stage 8.1 model (control, re-verified unchanged) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| 2024 feature matrix (re-verified unchanged) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| 2025 feature matrix (re-verified unchanged) | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |
| Freeze manifest (re-verified unchanged) | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` |
| Frozen 2025 blind predictions CSV (re-verified unchanged) | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` |

**Note on `candidateI_base_F.joblib`'s hash**: it is byte-identical to
`model_artifacts/candidateF_elevation_x_cloud.joblib` from the earlier Candidate F run
(`e8b89b27...`). This is EXPECTED, not an error: both are `HistGradientBoostingRegressor`
models with identical hyperparameters, `random_state=42`, fit on the identical EVEN training
rows/features/target — a deterministic fit reproduces the same artifact byte-for-byte.
Confirms reproducibility, not an accidental reuse of a stale file.

## STOP

Candidate I test complete. Frozen Stage 8.1 artifact, both feature matrices, the freeze
manifest, and the frozen blind-predictions CSV confirmed byte-identical before and after this
experiment. No model promoted to production. This is a NEGATIVE result reported as such: the
targeted high-elevation residual correction, despite being deliberately narrower than
Candidate D's untargeted approach, reproduces the same validation-overfitting failure mode —
and additionally degrades bias in its own specifically-targeted regime on blind data relative
to the frozen control.
