# Candidate G — Candidate F + Transition-Cloud-Regime Indicator

**Scope**: Refinement of Candidate F (the research baseline — see `CANDIDATE_F_REPORT.md`,
the only prior candidate whose blind-2025 MAE bootstrap CI excludes zero). Candidate G adds
ONE more additive feature on top of Candidate F's 38-feature set: `is_transition_cloud =
1{0.2 <= cloud_frac < 0.6}` (39 features total). **Control is still the frozen Stage 8.1
model** — Candidate F is a baseline-to-beat, not a second control, per the task's explicit
instruction. Script: [phase6_candidateG_transition_indicator.py](phase6_candidateG_transition_indicator.py).
Raw results: [CANDIDATE_G_RESULTS.json](CANDIDATE_G_RESULTS.json).

## Forensic motivation

`ERROR_FORENSICS_REPORT.md` §4 ("Error by cloud regime"): the **transition** cloud bucket
(`cloud_frac` in `[0.2, 0.6)`) has the **highest MAE (46.67) and highest bias (+12.74)** of
the three cloud regimes examined — worse than both "clear" (MAE 33.49, bias +8.72) and
"cloudy" (MAE 34.03, bias +1.08). Candidate F's `elevation_x_cloud_frac` interaction gives
the model a continuous signal but no explicit discontinuous marker for this specific
documented worst-case boundary. This candidate tests whether an explicit regime flag helps
beyond what the continuous interaction already captures.

## Feature provenance and leakage check — VERIFIED

`is_transition_cloud` is a deterministic threshold of `cloud_frac`, which (per
`CANDIDATE_F_PRE_TRAINING_AUDIT.md` item 2 and `build_corrected_feature_matrix.py:120`) is
itself derived from `fc_cloud_cover`, an NWP **forecast** field — forecast-time-available,
not observed/actual. Thresholding an already-cleared, forecast-time-available feature
introduces no new information channel. `actual_SW_IN` does not appear in this feature's
construction (confirmed by reading `phase6_candidateG_transition_indicator.py:add_features`).
Prevalence of the flag: EVEN 0.1727, ODD 0.1706, 2025 0.1603 (consistent across splits, no
sign of split-specific artifact).

## Methodology

Identical EVEN/ODD/blind protocol and architecture/hyperparameters as every prior candidate
(`HistGradientBoostingRegressor`, `max_depth=4`, `min_samples_leaf=30`,
`l2_regularization=10.0`, `loss="absolute_error"`, `random_state=42`) — only the feature set
changes (37 control → 39 Candidate G). **Bootstrap CI uses the CORRECTED utility**
(`research_utils.bootstrap_mae_diff_ci_corrected`, row-duplication-per-draw-count), per the
Candidate F audit's disclosed recommendation — this report does NOT reuse the original
`np.isin`-based utility for any number quoted below.

Governance hash check (before training): 2024 matrix `aeca026d...` MATCH, 2025 matrix
`9fe6b9f8...` MATCH, frozen model `64ea4aba...` MATCH.

## Results — VERIFIED

| | Control (frozen Stage 8.1) | Candidate G | Δ (G − control) |
|---|---|---|---|
| ODD 2024 MAE | 36.2040 | 35.7400 | −0.4640 |
| ODD 2024 Bias | +0.9605 | +1.6116 | +0.6511 (worse direction) |
| **Blind 2025 MAE** | 35.9745 | **35.5386** | **−0.4359** |
| Blind 2025 RMSE | 65.9427 | 65.2305 | −0.7122 |
| Blind 2025 Bias | +4.0802 | +3.8765 | −0.2037 |
| Blind 2025 nMAE% | 28.2478 | 27.9055 | −0.3423 pp |

**Bootstrap 95% CI (CORRECTED), blind-2025 MAE (G − control)**: mean **−0.4354**, CI
**[−0.7685, −0.1258]**. **Excludes zero, entirely on the improving side.**

**Comparison to Candidate F directly** (not a formal hypothesis test, point estimates only):
Candidate F's blind MAE was 35.4948 (Δ −0.4797 vs. control); Candidate G's is 35.5386 (Δ
−0.4359 vs. control) — **Candidate G is marginally WORSE than Candidate F** on the point
estimate, by 0.0438 W/m². The added transition-regime flag does not improve on the continuous
interaction alone; if anything it adds noise. Both candidates' CIs vs. control overlap
heavily and both exclude zero on the same side, so this is reported as **no demonstrated
incremental benefit from the explicit flag**, not as a meaningful regression.

## High-elevation subset (blind 2025, n=978, solar_elevation ≥ 30°) — VERIFIED

| | Control | Candidate G |
|---|---|---|
| MAE | 100.925 | **98.7687** |
| Bias | +13.7469 | **+12.6700** |
| nMAE% | 25.7694 | 25.2188 |

Bootstrap 95% CI (CORRECTED): mean **−2.1486**, CI **[−3.634, −0.7158]** — excludes zero.
Both MAE and bias improve together (consistent with Candidate F's pattern, not the Phase 3
weighting failure mode of trading bias for MAE). Candidate G's high-elevation bias
(+12.67) is very slightly better than Candidate F's own (+12.74) — the one metric where G
edges out F, though the difference (0.07 W/m²) is far smaller than either candidate's CI
width and not treated as a distinguishable effect.

## Transition-cloud-regime subset (blind 2025, n=958, the specifically targeted regime) — VERIFIED

| | Control | Candidate G |
|---|---|---|
| MAE | 46.6747 | **46.0048** |
| Bias | +12.7376 | **+13.0726** (worse direction) |

Bootstrap 95% CI (CORRECTED): mean **−0.6764**, CI **[−1.3077, −0.0378]** — excludes zero on
the MAE-improving side, but the interval's upper bound sits very close to zero (barely
excludes it), and **bias in this specific targeted regime gets slightly WORSE** (+12.74 →
+13.07), the same qualitative caution flagged for Phase 3's weighting experiment (MAE
improvement does not necessarily track bias improvement in this problem). This is a weaker,
less clean result than the high-elevation subset's.

## H1–H24 breakdown (blind 2025) — VERIFIED, see JSON for full table

Candidate G's MAE improves over control at nearly every horizon (delta_mae negative at 21 of
24 horizons); the three horizons where it is flat-to-slightly-worse are H2 (+0.08), H3
(+0.57), H4 (+0.70) — low-magnitude early-morning horizons where absolute errors are small in
both models (control MAE 4.3–11.4 W/m² at these horizons) and a small absolute change
reflects proportionally more noise. The largest absolute improvements are concentrated at
H10–H14 (−0.42 to −1.65 W/m²), the same late-morning/midday horizons Phase 1 flagged as the
largest absolute-error contributors (§1 of the forensics report) and where solar elevation is
typically highest.

## Pass/fail against the promotion rule

**Rule**: blind-2025 MAE bootstrap 95% CI (CORRECTED) must exclude zero on the improving side.
Candidate G's overall CI `[−0.7685, −0.1258]` **excludes zero** — **this candidate passes the
stated statistical bar**, same as Candidate F. **This does not constitute promotion.**
Consistent with every other report in this investigation, the frozen Stage 8.1 artifact
remains the sole control, untouched, and this is reported as a research-only finding for
governance review, not an authorization to deploy.

**Important caveat**: Candidate G's point estimate is marginally worse than Candidate F's own
(35.5386 vs. 35.4948 MAE), and the transition-regime-specific subset shows a bias trade-off
(MAE improves, bias in the targeted regime worsens). **The added transition-cloud flag does
not demonstrate incremental benefit beyond Candidate F's existing continuous interaction** —
this is reported as a null/non-improving refinement, not reframed as a positive finding
merely because it passes the same statistical bar as F (which it does mostly by inheriting
F's own effect via the shared elevation_x_cloud_frac feature, not by the new flag's own
contribution).

## UNKNOWN / not established by this test

- Whether the marginal G-vs-F point-estimate difference (0.0438 W/m²) is itself
  statistically distinguishable from zero — not tested; both candidates were only compared
  against the frozen control, not against each other via a paired bootstrap.
- Whether a different transition-regime threshold (e.g. `[0.3, 0.5)` instead of `[0.2, 0.6)`,
  copying Phase 1's own bucket boundary exactly as used in the forensics table) would perform
  differently — only the forensics report's exact boundary was tested, not a sweep.
- Whether this effect would persist under a different seed/split or additional blind years —
  same caveat already disclosed for Candidate F, not re-tested here.
- EMS/dispatch-level impact — not evaluated (forecasting-only investigation, consistent with
  scope).

## Provenance / hashes

| Artifact | SHA256 |
|---|---|
| `research_utils.py` (shared, corrected-bootstrap utility) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` |
| `phase6_candidateG_transition_indicator.py` | `ed8f19a0c614b69152d03a2be0f69581d5b0a143eca8e5dc18eb912484d73c48` |
| `CANDIDATE_G_RESULTS.json` | `137e2675eaf7bb0a33a68435da2d646d1669bddc6623dcaa1050f78fe3cb628c` |
| `model_artifacts/candidateG_transition_indicator.joblib` (new, research-only) | `90cdfd78c8f8d782e4c7f6ec08c175c9afa8573112d558d5f6f84f6c36c61185` |
| Frozen Stage 8.1 model (control, re-verified unchanged) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| 2024 feature matrix (re-verified unchanged) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| 2025 feature matrix (re-verified unchanged) | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |
| Freeze manifest (re-verified unchanged) | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` |
| Frozen 2025 blind predictions CSV (re-verified unchanged) | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` |

## STOP

Candidate G test complete. Frozen Stage 8.1 artifact, both feature matrices, the freeze
manifest, and the frozen blind-predictions CSV confirmed byte-identical before and after this
experiment. No model promoted to production; this is a research-only result reported for
governance review.
