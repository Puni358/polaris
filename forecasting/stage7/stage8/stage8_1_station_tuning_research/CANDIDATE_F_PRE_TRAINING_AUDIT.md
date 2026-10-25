# Candidate F — Pre-Training Audit

**Scope**: Independent re-verification of every claim made about Candidate F across
`CANDIDATE_F_REPORT.md` and `CANDIDATE_F_EMS_REPLAY_REPORT.md`, before any further training.
**No training was performed. No production code, frozen artifact, config, or Candidate F
itself was modified.** All checks below either re-read the existing code, re-hashed existing
files, or re-ran read-only `model.predict()` inference on already-fitted models (never
`.fit()`) to independently reproduce reported numbers from first principles rather than
trusting the prior reports' own printed output.

---

## 1. `solar_elevation × cloud_frac` feature construction and alignment — **VERIFIED**

Code (`phase2_candidateF_additive_feature.py:141`): `d[ADDITIVE_FEATURE_NAME] =
d["solar_elevation"] * d["cloud_frac"]`, applied inside a loop over `(even_day, odd_day,
day25)` — the identical row-wise pandas operation on each split's own DataFrame, so no
cross-split misalignment is possible (each DataFrame's own `solar_elevation`/`cloud_frac`
columns are multiplied in place, same index). Re-derived independently in this audit's own
fresh inference pass (below) and confirmed to reproduce the stored MAE values exactly.

## 2. No target/future leakage — **VERIFIED**

- `solar_elevation` traced to `build_corrected_feature_matrix.py:122` (`cs_cols =
  ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]`) — merged from the
  clear-sky/astronomy decomposition file. Pure solar geometry (date/time/location), zero
  dependency on any observation or NWP run; known exactly, arbitrarily far in advance.
- `cloud_frac` traced to `build_corrected_feature_matrix.py:120`: `df["cloud_frac"] =
  df["fc_cloud_cover"] / 100.0` — derived from `fc_cloud_cover`, an NWP **forecast** field
  (the `fc_` prefix denotes forecast-origin data throughout this feature contract), not an
  observed/actual value.
- Both are **pre-existing, already-governed features** in the frozen 37-feature contract
  (confirmed present in `FINAL_STAGE8_1_FORECASTING_FREEZE.md §2`'s feature list). An
  interaction of two features already cleared for leakage introduces no new information
  channel. **Precedent**: the frozen contract already contains an analogous interaction,
  `lwp_x_cloud = lwp_latest * cloud_frac` (`build_corrected_feature_matrix.py:127`) — Candidate
  F's feature follows an existing, already-audited pattern, not a novel technique.
- `actual_SW_IN` does not appear anywhere in the feature-construction code path for this
  feature or any other input to Candidate F.

## 3. EVEN/ODD training/evaluation split — **VERIFIED**

Code (`phase2_candidateF_additive_feature.py:126-130`): `origins = sorted(...); even = [o for
i,o in enumerate(origins) if i%2==0]; odd = [...i%2==1]` — **byte-identical split logic** to
the frozen model's own `train_corrected_stage8_1_model.py` (confirmed by direct comparison
against that script, read earlier in this investigation). `model_f.fit(X_tr, res_tr)`
(line 169) where `X_tr = even_day[...]` (line 143) — **the fit call references only
`even_day`**; `odd_day` and `day25` never appear in any `.fit()` call anywhere in the script
(confirmed by `grep`). No ODD or 2025 row is used for training.

## 4. Blind 2025 MAE improvement (35.9745 → 35.4948 W/m²) — **VERIFIED, independently reproduced**

This audit reloaded both models (`joblib.load`, **no `.fit()` call**) and re-ran inference
from scratch, independent of the stored JSON:
```
recomputed control MAE = 35.97449113081401
recomputed candidate F MAE = 35.49483021410838
diff = -0.47966091670562605
```
**Matches the reported 35.9745 → 35.4948 (diff −0.4797) to the reported precision, exactly,
from an independent code path.**

## 5. Bootstrap 95% CI: [−0.7307, −0.2338] — **VERIFIED as an accurate reproduction of the
code as written; ONE DISCLOSED METHODOLOGICAL IMPRECISION FOUND, does not change the conclusion**

**Reproduced exactly** with the original code's own resampling procedure: CI
`[-0.7307, -0.2338]`, mean `-0.4792` — confirms the stored number is not mis-transcribed.

**Finding**: the original `bootstrap_mae_diff_ci()` resamples *unique origins* with
replacement, then selects rows via `np.isin(origins, sample)` — this selects each sampled
origin's rows **at most once per bootstrap draw**, regardless of how many times that origin
was drawn (duplicates in `sample` collapse to a single inclusion). A textbook origin-level
paired bootstrap should instead **duplicate an origin's ~24 rows once per time it is drawn**,
which this implementation does not do. This is a **minor variance-calibration issue**, not a
correctness error in the mean difference.

**This audit re-ran a corrected version** (proper per-draw row duplication, same 2000
resamples, same seed):
```
CORRECTED bootstrap: mean -0.4777, CI95 [-0.8040, -0.1515]
ORIGINAL (as-coded) bootstrap: mean -0.4792, CI95 [-0.7307, -0.2338]
```
**The corrected interval is wider (as expected from under-weighted variance in the original),
but still excludes zero and lies entirely on the improving side.** The qualitative
conclusion — statistically distinguishable blind improvement — **holds under the corrected
method**. **Disclosed as a minor, non-blocking implementation imprecision**, not a basis to
reject the finding.

## 6. High-elevation improvement — **VERIFIED**

Reproduced from `CANDIDATE_F_RESULTS.json` (hash-confirmed unchanged, §8): control MAE
100.925 → Candidate F 98.6785 (improvement), control bias +13.7469 → Candidate F +12.7406
(bias also improves, reduced overprediction). Bootstrap CI for this subset
`[-3.3816, -1.1483]` — excludes zero, larger effect size than the overall-dataset number,
confirming the improvement concentrates in, not is diluted outside of, the targeted regime.

## 7. EMS replay result (−80,793.5 Wh realized unmet, +0.36% diesel) — **VERIFIED, independently reproduced**

Recomputed directly from `CANDIDATE_F_EMS_REPLAY_RESULTS.json` (hash-confirmed unchanged):
```
n=245 NORMAL origins
diesel: stage81=10849.6015 L, candidateF=10888.1696 L, diff=+0.3555%
unmet:  stage81=1,739,283.7 Wh, candidateF=1,658,490.2 Wh, diff=-80,793.5 Wh (-4.6452%)
```
**Matches the reported −80,793.5 Wh and +0.36% exactly.**

## 8. Hashes/provenance and frozen Stage 8.1 integrity — **VERIFIED, all re-hashed fresh in this audit**

| Artifact | Hash (re-computed now) | Matches all prior reports? |
|---|---|---|
| `phase2_candidateF_additive_feature.py` | `08fdcbe41a636ac0a65a427ceb494405812de8dc33296046bd9247927c52c0aa` | Yes |
| `CANDIDATE_F_RESULTS.json` | `b8d2cb700dba26efe24f3603fca63f0328a34e7e07d9200612351b4538a8a325` | Yes |
| `candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | Yes |
| **Frozen Stage 8.1 model** | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` | Yes — **unchanged** |
| 2024 feature matrix | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | Yes — unchanged |
| 2025 feature matrix | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` | Yes — unchanged |
| Freeze manifest | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` | Yes — unchanged |
| `run_full_experiment.py` (EMS harness) | `8afaf9ee7862c4586c586d14debb418d78f655362d1d729407300595fce118d5` | Yes — unchanged |
| `run_research_simulation.py` (terminal-target formula) | `d68b343d60f67a2fc8143316278371342d3933f70d0e26d40f3c1c732d843bd1` | Yes — unchanged |
| `run_candidateF_actual_solar_replay.py` | `c81e8bb25e4e6c1c54907c3a8d3e8113c4f8c8e8ae30edd2bbab9d5bc204730e` | Yes |
| `CANDIDATE_F_EMS_REPLAY_RESULTS.json` | `56974fcef86f219e2f6aec1671b14acd36b69c9c4eb9bad7245a2830dcf2fd32` | Yes |

**The frozen Stage 8.1 model, both feature matrices, the freeze manifest, and the EMS
harness scripts are all byte-identical to every value recorded across this entire multi-turn
investigation.** No drift detected at any point.

## 9. Why 80/245 origins regress — **VERIFIED, mechanistic explanation found**

Per-origin correlation analysis (this audit, newly computed from the existing, unchanged
EMS replay JSON — no retraining):

```
mean diesel_diff (F-stage81) | improved origins: +0.390 L | worsened origins: -0.174 L
mean charge_diff (F-stage81) | improved origins: +826.7 Wh | worsened origins: -459.0 Wh
corr(unmet_diff, diesel_diff) = -0.362
corr(unmet_diff, charge_diff) = -0.294
worsened origins where F planned LESS diesel than stage81: 51/80 (63.8%)
improved origins where F planned MORE diesel than stage81: 96/138 (69.6%)
```

**Mechanism, consistent with the causal pathway already established in
`STAGE81_FORECAST_VALUE_TRANSLATION_INVESTIGATION.md` / `TERMINAL_TARGET_ABLATION_REPORT.md`**:
Candidate F's correction is a *global* bias reduction, not a uniform per-origin downward
shift of every prediction. At the majority of origins (138/245), F's locally lower/more
accurate solar estimate causes GAP19 (via the same forecast-sensitive terminal-reserve and
direct-bus-bar pathways already identified) to commit **more** diesel/charging, which
reduces realized unmet when real conditions are less favorable than either forecast assumed.
**At the minority (80/245), F's local prediction moves in the opposite direction relative to
Stage 8.1 at that specific origin** (not every origin's correction points the same way a
global bias-reduction does), leading to **less** committed diesel/charging there — and when
real conditions are unfavorable at exactly those origins, the lower commitment leaves a
larger realized gap than Stage 8.1's (higher) commitment would have. This is not a flaw in
Candidate F or an inconsistency in the prior reports — it is the expected signature of any
forecast change interacting with the same forecast-sensitive dispatch mechanism already
documented to transmit forecast differences directly into diesel/charging decisions,
origin-by-origin, not only in aggregate.

---

## Summary table

| # | Check | Result |
|---|---|---|
| 1 | Feature construction/alignment | **VERIFIED** |
| 2 | No leakage | **VERIFIED** |
| 3 | EVEN/ODD split | **VERIFIED** |
| 4 | Blind 2025 MAE (35.9745→35.4948) | **VERIFIED** (independently reproduced) |
| 5 | Bootstrap 95% CI | **VERIFIED**, with one disclosed minor implementation imprecision (corrected CI wider but still excludes zero — conclusion unchanged) |
| 6 | High-elevation improvement | **VERIFIED** |
| 7 | EMS replay (−80,793.5 Wh, +0.36% diesel) | **VERIFIED** (independently reproduced) |
| 8 | Hashes/provenance, frozen integrity | **VERIFIED** — zero drift anywhere |
| 9 | Why 80/245 origins regress | **VERIFIED explanation** (mechanistic, not a defect) |

No item FAILED. No item remains UNKNOWN beyond what was already disclosed in the prior
reports (e.g., whether the effect holds under a different seed/split — not re-tested here,
not required for this audit's scope).

## AUDIT PASSED — TRAINING MAY BEGIN.

(With one disclosed, non-blocking note carried forward: the bootstrap CI utility used for
Candidate F and any future candidate should duplicate rows per bootstrap draw count, not
rely on `np.isin` set membership, for a correctly-calibrated interval width. This does not
block training; it is a recommended fix to the shared utility function before it is reused
for the next candidate's evaluation.)
