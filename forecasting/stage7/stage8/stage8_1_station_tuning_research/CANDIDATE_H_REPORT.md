# Candidate H — Candidate F Features + Asymmetric Quantile Loss (q=0.35)

**Scope**: Tests the "bias-aware/asymmetric loss" axis explicitly suggested by the task, as a
deliberately different mechanism from Phase 3's sample-weighting experiment (which kept the
symmetric absolute-error loss and only re-weighted rows, and made high-elevation bias worse).
Candidate H uses Candidate F's 38-feature set but switches the loss function itself to an
asymmetric quantile (pinball) loss, `quantile=0.35`, chosen to penalize under-prediction less
than over-prediction. **Control is the frozen Stage 8.1 model.** Script:
[phase7_candidateH_asymmetric_quantile_loss.py](phase7_candidateH_asymmetric_quantile_loss.py).
Raw results: [CANDIDATE_H_RESULTS.json](CANDIDATE_H_RESULTS.json).

## Forensic motivation

- `ERROR_FORENSICS_REPORT.md` §3/§7: the control's dominant error mode is **overprediction**,
  monotonically increasing with solar elevation (+13.75 W/m² at ≥30°, 45.9% of total error).
- `CANDIDATE_COMPARISON_REPORT.md` Phase 5 (cited, not re-run here): the EMS actual-solar-
  replay decomposition found **100% of realized-unmet hours coincide with the forecast
  overstating actual solar** — overprediction is the asymmetrically costly direction for the
  downstream dispatch problem.
- Phase 3's prior attempt at this problem (elevation-weighted sample weights, under the
  **same symmetric absolute-error loss**) failed to fix the asymmetry — it nudged MAE down
  marginally while making high-elevation bias **worse** (+13.75 → +19.95). Row-reweighting
  under a symmetric loss does not inherently change which error direction the model prefers.
- This candidate is the explicitly-flagged alternative axis: change the **loss function**
  itself to one that is asymmetric by construction (`quantile` loss with `quantile<0.5`
  penalizes overshoot more than undershoot), rather than hoping a row-weighting scheme
  induces the right direction as a side effect.

**Quantile choice, disclosed as un-tuned**: `quantile=0.35` was a single, pre-specified value
chosen before looking at any blind-2025 result — not grid-searched or selected on ODD, to
avoid repeating Candidate E's failure mode of overclaiming a validation-selected choice. No
sweep over quantile values was performed.

## Feature/method provenance and leakage check — VERIFIED

Identical to Candidate F (both input features forecast-time-available; see
`CANDIDATE_F_PRE_TRAINING_AUDIT.md` item 2). The loss-function change affects only how the
model is fit (`loss="quantile", quantile=0.35` vs. `loss="absolute_error"`); it does not
alter which columns the model sees and introduces no new information channel.

Governance hash check (before training): 2024 matrix MATCH, 2025 matrix MATCH, frozen model
MATCH (same three hashes as every other candidate in this directory).

## Results — VERIFIED, candidate FAILS badly

| | Control (frozen Stage 8.1) | Candidate H | Δ (H − control) |
|---|---|---|---|
| ODD 2024 MAE | 36.2040 | 37.7365 | +1.5325 (worse) |
| ODD 2024 Bias | +0.9605 | **−13.9558** | massive overshoot into underprediction |
| **Blind 2025 MAE** | 35.9745 | 36.3222 | **+0.3477 (worse)** |
| Blind 2025 RMSE | 65.9427 | 66.0909 | +0.1482 (worse) |
| Blind 2025 Bias | +4.0802 | **−10.3269** | massive overshoot into underprediction |
| Blind 2025 nMAE% | 28.2478 | 28.5208 | +0.2730 pp (worse) |

**Bootstrap 95% CI (CORRECTED), blind-2025 MAE (H − control)**: mean **+0.3439**, CI
**[−0.6653, 1.3460]** — **includes zero**; point estimate favors the control, not the
candidate.

**The asymmetric loss overshoots drastically.** Rather than modestly reducing the
overprediction bias as hypothesized, `quantile=0.35` flips the model's overall bias from
+4.08 (overprediction) to **−10.33 (underprediction)** — a swing roughly 2.5× the magnitude
of the original bias, in the opposite direction, and MAE gets slightly worse overall, not
better. This is a clean negative result for this specific, un-tuned quantile choice: 0.35 is
far too aggressive a shift for this problem's error scale.

## High-elevation subset (blind 2025, n=978, solar_elevation ≥ 30°) — VERIFIED, FAILS worse here

| | Control | Candidate H |
|---|---|---|
| MAE | 100.925 | 101.1004 (+0.18, flat/worse) |
| Bias | +13.7469 | **−21.6723** |

Bootstrap 95% CI (CORRECTED): mean **+0.1927**, CI **[−4.3605, 4.4703]** — includes zero, no
distinguishable effect on MAE. **Bias swings from +13.75 (overprediction) to −21.67
(underprediction)** — in exactly the highest-stakes regime this candidate was motivated to
fix, the correction overshoots by roughly 1.6× the original bias magnitude, in the opposite
direction. If the EMS-relevant asymmetry means overprediction is costlier than
underprediction, a *moderate* bias reduction toward zero would be desirable, but **this
candidate does not achieve a moderate correction — it replaces one large systematic error
with a different, comparably large systematic error of the opposite sign**, which is not a
demonstrated improvement for the EMS-relevant problem (not independently verified here via
EMS replay, which is out of scope, but the magnitude of the bias flip gives no basis to
assume this is better; a self-replacing bias of similar magnitude is not evidently superior
to the original without re-running the actual-solar-replay decomposition).

## H1–H24 breakdown (blind 2025) — VERIFIED, see JSON for full table

Candidate H's bias is negative (underpredicting) at **every single horizon** (H1 through
H24), with the largest swings at the midday horizons that carry the most absolute energy:
H11 bias **−24.62** (control −2.24, already slightly negative but the magnitude grows
roughly 11×), H6 −17.58 (control −1.28), H9 −13.14 (control +4.04, a full sign flip). At
several horizons (H4, H6, H8, H11, H16, H18-H20, H24) MAE is
*also* worse than control, not merely bias — the overshoot is large enough to directly hurt
accuracy, not just shift the error's sign. MAE does improve at a handful of horizons (notably
H1: 3.71→2.63, H12: 64.08→62.59, H13: 62.81→60.39, H14: 58.92→57.08), but the pattern is
inconsistent across horizons, consistent with an uncalibrated, too-aggressive asymmetric
shift rather than a horizon-coherent correction.

## Pass/fail against the promotion rule

**Rule**: blind-2025 MAE bootstrap 95% CI (CORRECTED) must exclude zero on the improving
side. Candidate H's CI `[−0.6653, 1.3460]` **includes zero** (and the point estimate is
positive, i.e. worse) — **this candidate FAILS the stated statistical bar**. Not promoted.

## UNKNOWN / not established by this test

- Whether a smaller, less aggressive quantile shift (e.g. 0.42–0.48, closer to the symmetric
  median) would achieve a *moderate* bias reduction without the large overshoot seen here —
  not tested; this report deliberately did not sweep quantile values to avoid an ODD-selected,
  overclaimed "best" choice (Candidate E's failure mode). A future single well-motivated
  follow-up (not run here) might test one additional, still-pre-specified, closer-to-median
  value.
- Whether this candidate's bias flip would be net-better or net-worse for actual EMS dispatch
  outcomes — not evaluated; would require an EMS replay re-run with this candidate's
  predictions, explicitly out of scope here, and the magnitude of the overshoot gives no
  confident basis to predict the sign of that answer.
- Whether combining a smaller quantile shift with elevation-specific application (only
  shifting at high elevation, analogous to Candidate I's targeting idea) would behave
  differently — not tested here; this candidate applies the same quantile uniformly to all
  rows.

## Provenance / hashes

| Artifact | SHA256 |
|---|---|
| `research_utils.py` (shared, corrected-bootstrap utility) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` |
| `phase7_candidateH_asymmetric_quantile_loss.py` | `dee9ff8af15870fce13ec4df43d88d8251128638ebabf56da0488a0bdf0b8294` |
| `CANDIDATE_H_RESULTS.json` | `6bea926c803c97c858c3cf375359eff4d00c2d9821ca1b3ff42186b00419773c` |
| `model_artifacts/candidateH_asymmetric_quantile.joblib` (new, research-only) | `1c42ed93bf44d5bd6f4b03c34d1b683eafbd2bedae7dc34dc6e99c2579430861` |
| Frozen Stage 8.1 model (control, re-verified unchanged) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| 2024 feature matrix (re-verified unchanged) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| 2025 feature matrix (re-verified unchanged) | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |
| Freeze manifest (re-verified unchanged) | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` |
| Frozen 2025 blind predictions CSV (re-verified unchanged) | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` |

## STOP

Candidate H test complete. Frozen Stage 8.1 artifact, both feature matrices, the freeze
manifest, and the frozen blind-predictions CSV confirmed byte-identical before and after this
experiment. No model promoted to production. This is a clean NEGATIVE result reported as
such, not reframed as a positive finding: the un-tuned quantile=0.35 asymmetric loss
overshoots the overprediction correction into a comparably large underprediction bias and
does not improve blind MAE.
