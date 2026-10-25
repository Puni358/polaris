# Candidates G–I — Summary and Next-Step Recommendation

**Scope**: Continuation of the station-tuning research campaign, starting from Candidate F
(the only prior candidate to clear the blind-improvement bar) as the research baseline.
Per the Candidate F audit's disclosed, non-blocking recommendation, **every bootstrap CI
quoted in this report and in `CANDIDATE_G_REPORT.md`/`CANDIDATE_H_REPORT.md`/
`CANDIDATE_I_REPORT.md` uses the CORRECTED origin-level bootstrap** (row duplication per
draw count, `research_utils.bootstrap_mae_diff_ci_corrected`), not the original, disclosed-
imprecise `np.isin`-based utility. This utility was independently validated against the
audit's own corrected re-computation of Candidate F (reproduced exactly: mean −0.4777, CI
[−0.8040, −0.1515]) before being used for any new candidate.

**Governance, confirmed throughout**: the frozen Stage 8.1 model
(`stage8_1_CORRECTED_candidate_37feature_model.joblib`, SHA256 `64ea4aba...`), both feature
matrices, the freeze manifest, and the frozen 2025 blind-predictions CSV were **never
modified, retrained, or re-saved** — re-hashed before and after every experiment in this
report (table below). All new candidates are EVEN-only research models, trained on
2024-EVEN, validated on 2024-ODD, and finally checked on 2025 (genuinely blind, never touched
by training or tuning for any candidate). **No candidate in this report is promoted.**

Scripts: [phase6_candidateG_transition_indicator.py](phase6_candidateG_transition_indicator.py),
[phase7_candidateH_asymmetric_quantile_loss.py](phase7_candidateH_asymmetric_quantile_loss.py),
[phase8_candidateI_targeted_high_elevation_residual.py](phase8_candidateI_targeted_high_elevation_residual.py),
shared utility [research_utils.py](research_utils.py). Raw results:
[CANDIDATE_G_RESULTS.json](CANDIDATE_G_RESULTS.json),
[CANDIDATE_H_RESULTS.json](CANDIDATE_H_RESULTS.json),
[CANDIDATE_I_RESULTS.json](CANDIDATE_I_RESULTS.json).

---

## What was tested and why

| Candidate | Axis | Forensic motivation | Relationship to prior failed attempts |
|---|---|---|---|
| **G** | Justified feature engineering (refinement of F) | Transition cloud regime (`cloud_frac` 0.2–0.6) has the highest MAE (46.67) and bias (+12.74) of three cloud buckets (`ERROR_FORENSICS_REPORT.md` §4) | Direct refinement of F's continuous interaction with an explicit discontinuous flag for the specific worst bucket |
| **H** | Sample weighting / asymmetric loss | Dominant error mode is overprediction, worst at high elevation (§3); EMS replay (cited) found 100% of realized-unmet hours coincide with forecast overprediction | Explicitly a DIFFERENT mechanism from Phase 3's elevation-weighted sample weights (which kept the symmetric loss and made bias worse); H changes the loss function itself to be asymmetric |
| **I** | Residual/feedback learning (targeted) | High elevation (≥30°) bucket = 45.9% of total error, systematic bias (§3); R²=0.4457 residual-predictability probe (§6) | Explicitly NARROWER than Candidate D's untargeted OOF correction, per task instruction — trained and applied ONLY on the high-elevation subset |

## Results table (blind 2025, vs. frozen control, CORRECTED bootstrap)

| Candidate | Blind MAE (control → candidate) | Blind ΔMAE | Bootstrap 95% CI (CORRECTED) | Blind bias (control → candidate) | Passes blind-improvement bar? |
|---|---|---|---|---|---|
| F (baseline, re-verified) | 35.9745 → 35.4948 | −0.4797 | [−0.8040, −0.1515] | +4.0802 → +3.6959 | **Yes** (re-verified under corrected method) |
| **G** | 35.9745 → 35.5386 | −0.4359 | **[−0.7685, −0.1258]** | +4.0802 → +3.8765 | **Yes**, but point estimate marginally worse than F's own (35.5386 vs. 35.4948); transition-regime bias slightly worsens (+12.74→+13.07) |
| **H** | 35.9745 → 36.3222 | +0.3477 | [−0.6653, 1.3460] | +4.0802 → **−10.3269** | **No** — CI includes zero; MAE worse; bias overshoots into a comparably large underprediction |
| **I** | 35.9745 → 35.5239 | −0.4506 | [−1.3535, 0.4329] | +4.0802 → **+4.8951** | **No** — CI includes zero; bias in its own targeted (high-elevation) regime is WORSE than the frozen control |

**High-elevation subset (≥30°, n=978) bias, control → candidate**: F +13.75→+12.74
(improves); G +13.75→+12.67 (improves, marginally more than F); H +13.75→**−21.67**
(overshoots badly); I +13.75→**+20.07** (worsens, worse than control itself).

## VERIFIED conclusion

**No candidate tested in this report (G, H, I) demonstrates a blind-2025 improvement that is
both statistically distinguishable from zero AND meaningfully better than the existing
Candidate F baseline.** Candidate G technically clears the same statistical bar as F (CI
excludes zero) but does not outperform F's own point estimate and shows a small bias
trade-off in its specifically-targeted subregime — it is not reported as a new, superior
finding, but as a redundant/non-improving variant of F. Candidates H and I both fail the
blind-improvement bar outright, and both do so via the SAME underlying pathology in
different guises: an intervention explicitly aimed at the high-elevation overprediction bias
(a more aggressive loss shift for H, a narrower/targeted residual correction for I) makes
that specific regime's bias WORSE on blind data, not better, despite looking favorable on
ODD validation. This echoes Phase 3's sample-weighting failure and Candidate D's residual-
correction failure — **three independent mechanisms (sample weighting, asymmetric loss,
targeted residual correction) have now all failed to safely reduce the high-elevation
overprediction bias without either overshooting it or failing to generalize from
validation to blind data.**

**No candidate is promoted.** The frozen Stage 8.1 model remains the sole control and
production artifact. Candidate F remains the only candidate across the entire multi-phase
investigation (Phases 1–8 combined) with both a statistically-distinguishable blind
improvement AND no demonstrated bias trade-off.

## UNKNOWN / not established

- Whether a smaller-magnitude asymmetric-loss shift (closer to quantile=0.5, not swept here —
  see `CANDIDATE_H_REPORT.md`'s UNKNOWN section) could achieve a moderate, non-overshooting
  bias correction. Not tested; would require one additional, still-pre-specified (not
  ODD-selected) quantile value.
- Whether Candidate I's apparent overfitting is primarily a small-training-sample artifact
  (489 high-elevation EVEN rows vs. ~2,900 for the full-EVEN candidates) — plausible but not
  independently isolated via a sample-size ablation.
- Whether combining Candidate G's transition flag with Candidate F but WITHOUT the
  continuous interaction (i.e. flag alone, not flag + interaction together) would perform
  differently — not tested; G always included both features together.
- EMS/dispatch-level impact of G, H, or I — not evaluated for any of the three (forecasting-
  only investigation, consistent with scope throughout).
- Whether Candidate F's own blind improvement (the one still-standing positive result)
  would persist under a different seed, split, or additional blind years — same caveat
  already disclosed in `CANDIDATE_F_REPORT.md`, not re-tested here.

## Recommendation for the next single experiment

**Candidates G, H, and I, as tested, do not justify further pursuit in their current form.**
If one single next experiment were to be chosen, it should NOT be a direct variant of H or I
as tested — both already demonstrate that an aggressive, uniform intervention at the
high-elevation regime (whether via loss shift or targeted residual correction) overshoots or
overfits on blind data; repeating the same mechanism with different constants is unlikely to
be qualitatively different without first understanding why (small sample for I; too-large a
shift for H).

The one narrowly-motivated, not-yet-tried variant this investigation surfaces is: **a single,
small, PRE-SPECIFIED, non-ODD-selected quantile shift close to the symmetric median (e.g.
quantile=0.45) on top of Candidate F's feature set** — testing whether a much more modest
asymmetric-loss nudge (roughly 1/3 the magnitude of this report's quantile=0.35) achieves a
partial, non-overshooting bias reduction, rather than either no effect (absolute-error loss,
Candidate F) or a large overshoot (quantile=0.35, Candidate H). **This recommendation is
conditional and not a promotion or a prediction of success**: it is the most direct, still
forensics-motivated next step along the one axis (asymmetric loss) that has not yet been
tried at a moderate magnitude, consistent with the task's explicit statement that EMS-
relevant bias asymmetry (not raw MAE alone) is the variable that matters most for this
problem. Per instruction, no model is promoted and no speculative claim of improvement is
made for this untested next step.

---

## Reproducible artifacts, hashes, and provenance (this report's scope: Candidates G/H/I)

| Artifact | Role | SHA256 |
|---|---|---|
| `research_utils.py` | Shared metrics/bootstrap/night-zero/horizon-breakdown utility (corrected bootstrap) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` |
| `phase6_candidateG_transition_indicator.py` | Candidate G script | `ed8f19a0c614b69152d03a2be0f69581d5b0a143eca8e5dc18eb912484d73c48` |
| `CANDIDATE_G_RESULTS.json` | Candidate G raw output | `137e2675eaf7bb0a33a68435da2d646d1669bddc6623dcaa1050f78fe3cb628c` |
| `model_artifacts/candidateG_transition_indicator.joblib` | Candidate G model (research-only) | `90cdfd78c8f8d782e4c7f6ec08c175c9afa8573112d558d5f6f84f6c36c61185` |
| `phase7_candidateH_asymmetric_quantile_loss.py` | Candidate H script | `dee9ff8af15870fce13ec4df43d88d8251128638ebabf56da0488a0bdf0b8294` |
| `CANDIDATE_H_RESULTS.json` | Candidate H raw output | `6bea926c803c97c858c3cf375359eff4d00c2d9821ca1b3ff42186b00419773c` |
| `model_artifacts/candidateH_asymmetric_quantile.joblib` | Candidate H model (research-only) | `1c42ed93bf44d5bd6f4b03c34d1b683eafbd2bedae7dc34dc6e99c2579430861` |
| `phase8_candidateI_targeted_high_elevation_residual.py` | Candidate I script | `c4d79966a925480e0e43654321c648acc0d4293cf25a576b106970df56561814` |
| `CANDIDATE_I_RESULTS.json` | Candidate I raw output | `a1da4f6429806336eb10104d1e371adce0b05dba26e4f0c7a34fa474ab4adb72` |
| `model_artifacts/candidateI_base_F.joblib` | Candidate I base model (= Candidate F's artifact, deterministic refit) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| `model_artifacts/candidateI_high_elevation_correction.joblib` | Candidate I correction-stage model (research-only) | `379aaa78d732d3cc699f8ab555fc0b285ff902a706a6f14ebbb7877b646d06b1` |

**Frozen artifacts, re-verified byte-identical before AND after this entire G/H/I
campaign (no drift at any point)**:

| File | SHA256 |
|---|---|
| `model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib` | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |
| `stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` |
| `FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json` | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` |

## STOP

Campaign complete (Candidates G, H, I). **No candidate promoted. No frozen artifact, freeze
manifest, production runtime, or production config modified at any point** (re-hashed and
confirmed unchanged before the first experiment and after the last). Every VERIFIED claim
traces to a hash-confirmed input and a script in this directory; every negative/null result
(Candidates H and I, and Candidate G's non-improvement over F) is reported as such, not
reframed as a positive finding. Candidate F remains the sole standing research result with a
statistically-distinguishable blind improvement and no demonstrated bias trade-off, and
remains a research finding only, not a promoted production model.
