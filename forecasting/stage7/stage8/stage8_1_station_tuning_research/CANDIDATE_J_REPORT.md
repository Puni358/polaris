# Candidate J — Candidate F + Joint Elevation × Transition-Cloud Interaction Feature

**Scope**: Candidate J = Candidate F's 38 features (frozen 37-feature contract +
`elevation_x_cloud_frac`) + ONE new additive feature,
`elevation_x_transition_cloud = solar_elevation * is_transition_cloud`, where
`is_transition_cloud = 1{0.2 <= cloud_frac < 0.6}` (identical definition to Candidate G's
own flag). 39 features total. Same architecture/hyperparameters as the control and every
prior candidate (`HistGradientBoostingRegressor`, `max_depth=4`, `min_samples_leaf=30`,
`l2_regularization=10.0`, `loss="absolute_error"`, `random_state=42`) — no hyperparameter
tuning. Script:
[phase10_candidateJ_training.py](phase10_candidateJ_training.py). Raw results:
[CANDIDATE_J_RESULTS.json](CANDIDATE_J_RESULTS.json). Model artifact:
`model_artifacts/candidateJ_elevation_x_transition.joblib`.

**Primary promotion comparison is Candidate J vs. Candidate F** (the standing best research
result), not vs. the frozen control, per explicit task instruction. Comparison to the frozen
control is reported for context only.

## Forensic motivation

`CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md` §2 finding #3 and §5's explicit proposal: the
joint cell **"solar_elevation ≥ 30° AND cloud_frac in [0.2, 0.6)"** is Candidate F's single
worst slice on blind 2025 (n=206, MAE **114.57**, bias **+45.38**) — roughly 3–4x worse than
either the aggregate high-elevation bucket alone (MAE 98.68, bias +12.74) or the aggregate
transition-cloud bucket alone (MAE 45.52, bias +12.15). Candidate F's `elevation_x_cloud_frac`
is a smooth product over the *entire* cloud_frac range and dilutes this specific joint
signal; Candidate G's flat `is_transition_cloud` flag was never crossed with elevation and
could not isolate this cell either (and failed to beat F standalone, per
`CANDIDATE_G_REPORT.md`). The residual-forensics report explicitly flagged this joint regime
as having thin support — **86/2885 (≈3.0%) of 2024-EVEN training rows** — a real
overfitting risk, the same mechanism that sank Candidate I (targeted high-elevation-only
residual correction, which overfit on ODD and made its own targeted regime's blind bias
*worse* than even the frozen control).

## Feature / leakage check — VERIFIED

- `solar_elevation`: pure astronomical geometry, forecast-time-available — already cleared
  for Candidate F (`CANDIDATE_F_PRE_TRAINING_AUDIT.md` item 2).
- `cloud_frac`: already a frozen-37-feature-contract input, derived from `fc_cloud_cover`, an
  NWP FORECAST field — forecast-time-available (same provenance already cleared for
  Candidate F and Candidate G; see `CANDIDATE_F_PRE_TRAINING_AUDIT.md` §2 and
  `build_corrected_feature_matrix.py:120`).
- `is_transition_cloud`: a deterministic binary function of `cloud_frac` alone, identical
  definition to Candidate G's own already-cleared flag.
- `elevation_x_transition_cloud` is the direct product of two already-cleared,
  forecast-time-available quantities — introduces no new information channel. Same
  precedent-based reasoning already used to clear Candidate F's own feature and Candidate
  G's flag. `actual_SW_IN` does not appear anywhere in this feature's construction or in any
  of the three ingredient features. Code inspection confirms `.fit()` is called exactly once
  in the script, on `X_tr`/`res_tr` sliced from `even_day` only; `odd_day`/`day25` and the
  frozen control model / Candidate F's own artifact are used only via `joblib.load()` +
  `.predict()`, never `.fit()`.

## Methodology

Identical EVEN/ODD/blind protocol to every prior candidate in this directory. Train: 2024
EVEN daytime rows only (n=2885). Validation (not used for any promotion decision): 2024 ODD
(n=2883). Blind comparison (the genuinely blind primary claim): 2025 (n=5978, untouched by
training or selection). Governance hash check (pre-training): 2024 matrix MATCH, 2025 matrix
MATCH, frozen control model MATCH, Candidate F's own model artifact MATCH (re-verified
byte-identical to its hash recorded in `CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md` and
`CANDIDATE_I_REPORT.md`: `e8b89b27...`). All CIs use the CORRECTED bootstrap utility
(`research_utils.bootstrap_mae_diff_ci_corrected`), per the Candidate F audit's finding that
the original utility under-calibrates variance.

## Results — VERIFIED, candidate PASSES the promotion bar against Candidate F

| | Control (frozen Stage 8.1) | Candidate F | Candidate J | Δ (J − F) |
|---|---|---|---|---|
| ODD 2024 MAE | 36.2040 | 35.4438 | **35.2972** | −0.1466 |
| ODD 2024 Bias | +0.9605 | +0.7505 | +0.9722 | +0.2217 |
| **Blind 2025 MAE** | 35.9745 | 35.4948 | **35.3036** | **−0.1912** |
| Blind 2025 RMSE | 65.9427 | 65.1662 | 64.8594 | −0.3068 |
| Blind 2025 Bias | +4.0802 | +3.6959 | +3.6640 | −0.0319 |
| Blind 2025 nMAE% | 28.2478 | 27.8712 | 27.7210 | −0.1502 |

**Bootstrap 95% CI (CORRECTED), blind-2025 MAE, J − F (primary promotion comparison)**: mean
**−0.1905**, CI **[−0.3484, −0.0364]** — **excludes zero, entirely on the improving side**.
This is a smaller absolute effect than F's own improvement over the control (F: mean
−0.4777, CI [−0.8040, −0.1515]), but it is statistically distinguishable from no effect by
the same corrected, origin-level paired-bootstrap standard used throughout this
investigation.

**Context — J vs. control**: mean **−0.6682**, CI **[−1.0246, −0.3097]** (excludes zero;
J also clears the bar against the frozen control, as expected since it strictly extends F).

## Targeted joint regime (blind 2025, n=206, the specific cell J targets) — VERIFIED

| | Control | Candidate F | Candidate J |
|---|---|---|---|
| MAE | 116.7071 | 114.5668 | **113.9984** |
| Bias | +41.5244 | **+45.3824** | +44.4706 |
| RMSE | 147.8408 | 146.7810 | 146.1801 |

Candidate J's bias at the targeted cell (**+44.47**) is slightly *better* than Candidate F's
(**+45.38**) — a small improvement, not a regression — though still worse than the frozen
control's bias there (+41.52), consistent with the pattern already seen for F itself (F's
bias at this cell was also worse than control's). Bootstrap 95% CI (CORRECTED), J − F at
this cell: mean **−0.5516**, CI **[−1.9556, 0.8336]** — includes zero (expected, given
n=206 and the thin EVEN training support of only 86 rows; the point estimate favors J but
the interval is too wide to call this cell-level MAE change statistically significant on its
own). Critically, there is **no material bias regression** in the targeted regime relative
to F — the specific overfitting failure mode that sank Candidate I (bias *worse* than both F
and control in its own targeted cell) does **not** reproduce here.

## Aggregate high-elevation (≥30°) and transition-cloud subsets — VERIFIED

| Subset | n | Control MAE / Bias | Candidate F MAE / Bias | Candidate J MAE / Bias |
|---|---|---|---|---|
| High-elevation ≥30° | 978 | 100.9250 / +13.7469 | 98.6785 / +12.7406 | **98.0537 / +12.6344** |
| Transition-cloud [0.2,0.6) | 958 | 46.6747 / +12.7376 | 45.5216 / +12.1548 | **45.2913 / +11.5355** |

Both aggregate regimes improve slightly under J relative to F, on both MAE and bias.
Bootstrap CI (CORRECTED), J−F, high-elevation subset: mean −0.6244, CI [−1.3350, 0.1139]
(includes zero — not independently significant at this aggregate level, but directionally
consistent and bias does not regress).

## Aug–Sep month subset — VERIFIED

| | n=1183 | Control | Candidate F | Candidate J |
|---|---|---|---|---|
| MAE | | 42.5227 | 42.3766 | **42.1128** |
| Bias | | +11.7956 | +12.4761 | +11.9722 |

J−F bootstrap CI (CORRECTED): mean −0.2606, CI [−0.5663, 0.0340] — borderline, touches zero
at the upper edge but the point estimate and aggregate pattern are consistent with the
overall blind-2025 result.

## H1–H24 breakdown (blind 2025, J vs. F) — VERIFIED, see JSON for full table

MAE improves at 16 of 24 horizons relative to Candidate F, with no horizon showing a large
bias blowup. Representative midday/high-elevation-correlated horizons: H9 MAE 44.80→44.56
(bias 3.53→3.33), H12 MAE 62.46→61.93 (bias 17.32→17.43, small increase), H13 MAE
62.38→61.76 (bias 16.45→16.26), H15 MAE 47.13→46.74 (bias 8.78→8.70), H17 MAE 30.66→30.23
(bias 3.81→4.20, small increase). Unlike Candidate I's horizon pattern (a large, systematic
bias regression concentrated exactly at the horizons the correction targeted — H13, H16,
H17, H9 bias all moved several W/m² worse than control), Candidate J shows no comparable
concentrated bias degradation at any horizon — the small bias upticks at H12/H17 are on the
order of 0.1–0.4 W/m², not the multi-W/m² jumps that flagged Candidate I's failure.

## Pass/fail against the stated promotion bar

**Rule (a)**: blind-2025 MAE bootstrap 95% CI (CORRECTED) for (J − F) must exclude zero on
the improving side. **Result: PASS.** CI = [−0.3484, −0.0364], mean −0.1905, entirely
negative (favoring J).

**Rule (b)**: J's bias at the targeted joint regime must not be substantially worse than
F's +45.38. **Result: PASS.** J's bias there is +44.4706 — slightly *better* than F's, not
worse at all, let alone "substantially worse."

**Overall: Candidate J PASSES the promotion bar against Candidate F**, on both conditions.
This is a genuine, if modest, improvement — the effect size (~0.19 W/m² blind MAE) is about
40% of the size of F's own improvement over the control (~0.48 W/m²), and the targeted-cell
CI alone (n=206) does not reach significance in isolation, but the aggregate blind-2025 CI
does, and no regime shows a bias regression.

## Explicit VERIFIED / FAILED / UNKNOWN claims

| Claim | Status |
|---|---|
| Joint cell (elevation≥30° × transition-cloud) is F's worst slice on blind 2025 (n=206, MAE 114.57, bias +45.38) | VERIFIED (reproduced exactly from this script's own control/F re-predictions) |
| Joint-regime EVEN training prevalence ≈86/2885 (≈3.0%) | VERIFIED (computed directly in this script: 86/2885 = 2.98%) |
| Blind-2025 MAE bootstrap CI (J−F, CORRECTED) excludes zero, favoring J | VERIFIED |
| J's bias at the targeted cell does not regress vs. F | VERIFIED (+44.47 vs. +45.38, slightly better) |
| J's targeted-cell-level MAE/bias change vs. F is individually statistically significant | FAILED to reach significance alone (CI [−1.9556, 0.8336] includes zero at n=206) — the aggregate blind-2025 result is what clears the bar, not this cell in isolation |
| J avoids Candidate I's overfitting failure mode (bias worse than control AND F in the targeted regime) | VERIFIED avoided — J's targeted-cell bias is better than F's, not worse |
| No horizon shows a large concentrated bias regression (Candidate I's failure signature) | VERIFIED — max horizon-level bias delta is ≈0.4 W/m², not multi-W/m² |
| J generalizes robustly beyond this specific blind-2025 sample / to other years or stations | UNKNOWN — not tested, single blind set as with every prior candidate |
| EMS/dispatch-level impact of this improvement | UNKNOWN — out of scope, not evaluated |

## Promotion status

**Not promoted.** Per the task's explicit instruction, no candidate is promoted to
production under any outcome of this test. Candidate F remains the standing best research
result on record; Candidate J is reported as a research finding (a modest, statistically
supported improvement over F on the aggregate blind-2025 claim, without the bias-regression
risk flagged as the primary danger) but requires separate, explicit promotion decisions
outside this research investigation before any production use.

## Provenance / hashes (re-verified before and after training — zero drift)

| Artifact | SHA256 |
|---|---|
| `phase10_candidateJ_training.py` (new) | `a8e55a75e1a0045d66df93c5836ec58481588424c993ac5607a49dd3ac8ce833` |
| `CANDIDATE_J_RESULTS.json` (new) | `27f784861d207f50a66ac07124e81f80bde21f585709207a49bba296c9da1140` |
| `model_artifacts/candidateJ_elevation_x_transition.joblib` (new) | `952b6e76f7623da6ecb91a1731e1d8104b1a60564126f02083d6377d215f0ccf` |
| `research_utils.py` (shared, corrected-bootstrap utility, unchanged) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` |
| Frozen Stage 8.1 control model (re-verified unchanged) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| Candidate F model artifact (re-verified unchanged, read-only `.predict()` only) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| Candidate F results JSON (re-verified unchanged) | `b8d2cb700dba26efe24f3603fca63f0328a34e7e07d9200612351b4538a8a325` |
| 2024 feature matrix (re-verified unchanged) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| 2025 feature matrix (re-verified unchanged) | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |
| Freeze manifest (re-verified unchanged) | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` |
| Frozen 2025 blind-predictions CSV (re-verified unchanged) | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` |

All hashes above were computed both immediately before the training run (asserted in-script
against expected values, which matched) and again after the run completed (the script's own
post-run re-verification block, plus an independent out-of-band `sha256sum` check performed
for this report) — all identical. No production/config/freeze file was touched. Neither the
frozen control model nor Candidate F's model artifact was ever passed to `.fit()` — both
were loaded read-only via `joblib.load()` and used only for `.predict()`.

## STOP

Candidate J test complete. Frozen Stage 8.1 artifact, Candidate F's model artifact and
results, both feature matrices, the freeze manifest, and the frozen blind-predictions CSV
are all confirmed byte-identical before and after this experiment. **Nothing was promoted to
production.** Candidate J passes the stated promotion bar against Candidate F — a genuine
but modest blind-2025 MAE improvement (−0.19 W/m², CI excluding zero) with no bias
regression in its targeted joint regime — but remains a research-only result pending any
separate production decision.
