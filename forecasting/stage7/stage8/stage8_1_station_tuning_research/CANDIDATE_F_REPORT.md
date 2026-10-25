# Candidate F — `solar_elevation × cloud_frac` Additive Feature

**Scope**: Tests only the single Phase-1-motivated candidate recommended in
`CANDIDATE_COMPARISON_REPORT.md`. Reuses the frozen EVEN/ODD methodology exactly: train on
**2024 EVEN** only, held-out **2024 ODD** reported as validation (not the blind claim), final
comparison on **2025 — the genuinely blind set, untouched by training**. Script:
[phase2_candidateF_additive_feature.py](phase2_candidateF_additive_feature.py). Raw results:
[CANDIDATE_F_RESULTS.json](CANDIDATE_F_RESULTS.json).

**Note on "2025 ODD" in the task wording**: the 2025 matrix carries no EVEN/ODD split of its
own in this pipeline (the frozen model's own methodology only ever splits 2024 that way;
2025 is used whole, as the blind set — see `FINAL_STAGE8_1_FORECASTING_FREEZE.md §4-5` and
every prior report in this investigation). "2025 ODD" is read here as "the 2025 blind set,"
consistent with that established, frozen methodology — not a new split invented for this
candidate.

**Governance, VERIFIED by hash check before any training**:
- `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`: `aeca026d1acf62f...` — **MATCH**
- `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv`: `9fe6b9f8b46b89e2...` — **MATCH**
- Frozen model `stage8_1_CORRECTED_candidate_37feature_model.joblib`: `64ea4abada78a257...` — **MATCH**

All three assertions passed (script halts on any mismatch) — the frozen Stage 8.1 control
was **not modified**. Candidate F is a new, separate 38-feature model (the existing 37 +
`elevation_x_cloud_frac = solar_elevation × cloud_frac`), same architecture and
hyperparameters as the frozen control (`HistGradientBoostingRegressor`, `max_depth=4`,
`min_samples_leaf=30`, `l2_regularization=10.0`, `loss="absolute_error"`,
`random_state=42`). No production/config/freeze file touched.

---

## Results — VERIFIED

| | Control (frozen Stage 8.1) | Candidate F | Δ (F − control) |
|---|---|---|---|
| **ODD 2024 (validation)** MAE | 36.2040 | 35.4438 | −0.7602 |
| ODD 2024 RMSE | 64.5752 | 63.3192 | −1.2560 |
| ODD 2024 Bias | +0.9605 | +0.7505 | −0.2100 |
| ODD 2024 nMAE% | 28.0807 | 27.4911 | −0.5896 pp |
| **Blind 2025** MAE | 35.9745 | **35.4948** | **−0.4797** |
| Blind 2025 RMSE | 65.9427 | 65.1662 | −0.7765 |
| Blind 2025 Bias | +4.0802 | +3.6959 | −0.3843 |
| Blind 2025 nMAE% | 28.2478 | 27.8712 | −0.3766 pp |

**Bootstrap 95% CI for (candidate − control) blind-2025 MAE difference** (2,000 resamples
over origins): **mean −0.4792, CI [−0.7307, −0.2338]**. **The interval excludes zero, and
lies entirely on the improving side.** This is the first candidate in this entire
investigation (Candidates B–E, the sample-weighting experiment, all tested previously) to
clear this bar — every prior candidate's blind-MAE CI included zero.

The validation (ODD) improvement (−0.76) and the blind improvement (−0.48) are of the same
order of magnitude (blind retains ~63% of the validation effect) — unlike Candidates D and E,
where the blind effect shrank to near-zero or below statistical significance relative to a
much larger validation-only effect. This is consistent with (though does not, by itself,
prove) a genuinely generalizing effect rather than validation-set overfitting.

## High-elevation overprediction check — VERIFIED: improves, in the correct direction

This was the specific regime the feature was motivated by (Phase 1: elevation ≥30° bucket
contributed 45.9% of total error, with the model's largest positive bias, +13.75 W/m²).

| Blind 2025, solar_elevation ≥ 30° (n=978) | Control | Candidate F |
|---|---|---|
| MAE | 100.925 | **98.6785** |
| Bias | +13.7469 | **+12.7406** |
| nMAE% | 25.7694 | 25.1958 |

**Bootstrap 95% CI for the high-elevation-subset MAE difference: mean −2.238, CI
[−3.3816, −1.1483]** — also excludes zero, also entirely on the improving side, and the
effect size here (−2.24 W/m²) is **larger** than the overall-dataset effect (−0.48), meaning
**the improvement is concentrated in, not diluted outside of, the targeted regime**.

**Critically, unlike the Phase 3 sample-weighting experiment** (which reduced high-elevation
MAE slightly while *increasing* bias there from +13.75 to +19.95 — the wrong direction),
**Candidate F reduces both MAE and bias together in the high-elevation regime** (+13.75 →
+12.74). This directly addresses the specific error mode identified in Phase 1 and is
relevant to, though not a re-test of, the EMS forecast-driven unmet finding (which was
triggered by forecast overprediction in exactly this kind of regime).

## Decision, per the task's explicit rule

**Rule**: *"If blind CI includes zero, do NOT promote."* Here, the blind CI
(**[−0.7307, −0.2338]**) does **not** include zero, and lies entirely on the improving side.
**This candidate passes the stated statistical bar for consideration** — it is the only one
in this entire multi-phase investigation to do so.

**This report does not itself constitute promotion to production.** Consistent with every
other document in this investigation, Stage 8.1's frozen artifact remains the control,
untouched, and this finding is reported as a **VERIFIED, statistically-supported research
result warranting a formal promotion review** (new model validation, governance sign-off,
operational re-evaluation) — not as an authorization to deploy. No production/config/freeze
file was changed to produce this result.

## UNKNOWN / not established by this test

- **Whether this single interaction feature's benefit would persist under a different
  random seed, a different EVEN/ODD assignment, or additional blind years** — only one
  seed (42, matching the frozen control) and one 2024/2025 split were tested.
- **Whether this improvement would translate into a measurably better EMS realized-unmet
  outcome** — that would require re-running the actual-solar-replay decomposition with this
  candidate's predictions in place of the frozen model's, which was explicitly out of scope
  and not performed here.
- **Whether combining this feature with any other previously-tested axis (E's hyperparameters,
  D's residual correction) would help further or simply reproduce the same effect** — not
  tested; this experiment varied only the feature set, per the task's explicit scope
  ("Test ONLY the ... additive feature candidate").

## Provenance / hashes

| Artifact | SHA256 |
|---|---|
| `phase2_candidateF_additive_feature.py` | `08fdcbe41a636ac0a65a427ceb494405812de8dc33296046bd9247927c52c0aa` |
| `CANDIDATE_F_RESULTS.json` | `b8d2cb700dba26efe24f3603fca63f0328a34e7e07d9200612351b4538a8a325` |
| `model_artifacts/candidateF_elevation_x_cloud.joblib` (new, research-only) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| Frozen Stage 8.1 model (control, re-verified unchanged) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |
| 2024 feature matrix (re-verified unchanged) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| 2025 feature matrix (re-verified unchanged) | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` |

## STOP

Candidate F test complete. Frozen Stage 8.1 artifact, feature matrices, and production/config
files confirmed unchanged (hash-verified before and after). No model promoted to production;
this is a research-only result reported for governance review.
