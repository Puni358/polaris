# Candidate J — Pre-EMS-Replay Audit

**Scope**: Independent re-verification of every claim made about Candidate J across
`CANDIDATE_J_REPORT.md`, before any downstream EMS replay step. **No training was
performed. No production code, frozen artifact, config, freeze manifest, Candidate F, or
Candidate J itself was modified.** All checks below either re-read the existing code,
re-hashed existing files, or re-ran read-only `model.predict()` inference on already-fitted
models (never `.fit()`) to independently reproduce reported numbers from first principles,
following the exact methodology of `CANDIDATE_F_PRE_TRAINING_AUDIT.md`. An independent
inspection script was written to
`/tmp/.../scratchpad/audit_candidateJ.py` (read-only; grep-confirmed to contain zero `.fit()`
calls — its 3 textual matches for `"\.fit("` are all inside comments/print strings, not
executable calls) and re-runs `joblib.load()` + `.predict()` only, re-deriving every metric
independently rather than trusting `CANDIDATE_J_RESULTS.json`'s stored numbers.

---

## 1. `elevation_x_transition_cloud` construction/alignment and Candidate G boundary match — **VERIFIED**

Code (`phase10_candidateJ_training.py:116-119`):
```
d[ELEV_CLOUD_FEATURE] = d["solar_elevation"] * d["cloud_frac"]
d[TRANSITION_FLAG] = ((d["cloud_frac"] >= 0.2) & (d["cloud_frac"] < 0.6)).astype(float)
d[JOINT_FEATURE] = d["solar_elevation"] * d[TRANSITION_FLAG]
```
applied inside a loop over `(even_day, odd_day, day25)` — identical row-wise pandas pattern
to Candidate F/G, so no cross-split misalignment is possible (each DataFrame's own columns
multiplied in place, same index, no reordering).

Compared byte-for-byte against Candidate G's own definition
(`phase6_candidateG_transition_indicator.py:84`): `d[TRANSITION_FEATURE] =
((d["cloud_frac"] >= 0.2) & (d["cloud_frac"] < 0.6)).astype(float)` — **identical boundary
logic** (`>= 0.2`, `< 0.6`, half-open interval matching `cloud_frac`'s own `[0,1]` definition
elsewhere). J's claim that it reuses "Candidate G's exact transition definition" is confirmed
by direct code comparison, not merely trusted.

This audit's own independently-written feature-construction code (built from scratch in the
inspection script, not copy-pasted from `phase10_candidateJ_training.py`) reproduces the
exact same prevalence: **86/2885 = 2.9809%** of 2024-EVEN training rows in the targeted joint
regime, matching the report's claimed "86/2885 (≈3.0%)" exactly.

## 2. No target/future leakage — **VERIFIED**

- `solar_elevation` traced to `build_corrected_feature_matrix.py:122`
  (`cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]`) — pure solar
  geometry, already cleared for Candidate F.
- `cloud_frac` traced to `build_corrected_feature_matrix.py:120`: `df["cloud_frac"] =
  df["fc_cloud_cover"] / 100.0` — derived from `fc_cloud_cover`, an NWP **forecast** field,
  not an observed/actual value. Same line numbers as cited in the Candidate F audit;
  re-confirmed directly in this audit, not merely re-cited.
- `is_transition_cloud` is a deterministic threshold function of `cloud_frac` alone (no new
  columns/merges). `elevation_x_transition_cloud` is the direct row-wise product of two
  already-cleared quantities.
- Grep of `phase10_candidateJ_training.py` for `actual_SW_IN` shows it appears **only** as
  the regression target (`y_tr = even_day["actual_SW_IN"].values`, lines 176/182/188) —
  never inside `add_features()` or any feature-construction code path. Confirmed directly by
  `grep -n "actual_SW_IN" phase10_candidateJ_training.py`.

## 3. EVEN/ODD split and training provenance — **VERIFIED**

`phase10_candidateJ_training.py:150-156`: `origins = sorted(df24["forecast_start"].unique());
even = [o for i,o in enumerate(origins) if i%2==0]; odd = [...i%2==1]` — **byte-identical** in
approach to `train_corrected_stage8_1_model.py:109-111` (`all_origins = sorted(...); 
even_origins = [... i % 2 == 0]; odd_origins = [... i % 2 == 1]`), confirmed by direct
side-by-side comparison, not assumption.

`grep -n "\.fit("` on `phase10_candidateJ_training.py` returns exactly **one** real call:
`model_j.fit(X_tr, res_tr)` (line 210), where `X_tr = even_day[CANDIDATE_J_39_FEATURES].values`
(line 175) — **EVEN-split only**. Neither `odd_day` nor `day25` (nor the frozen control model
or Candidate F's artifact — both loaded via `joblib.load()` and used only through
`.predict()`) ever appears in any `.fit()` call anywhere in the script.

## 4. Blind 2025 MAE = 35.3036 — **VERIFIED, independently reproduced**

This audit reloaded all three models (`joblib.load`, **no `.fit()` call**) and re-ran
inference from scratch using independently-written feature-construction code (not the
candidate script's own code path):

```
recomputed control MAE = 35.9745
recomputed candidate F MAE = 35.4948
recomputed candidate J MAE = 35.3036
```

**Matches the reported 35.9745 → 35.4948 → 35.3036 exactly**, from an independent code path.
ODD-2024 validation also reproduced exactly: control 36.2040, F 35.4438, J 35.2972 — matches
reported values.

## 5. J vs F corrected bootstrap CI [−0.3484, −0.0364] — **VERIFIED, exact reproduction**

Re-ran `research_utils.bootstrap_mae_diff_ci_corrected()` (confirmed by direct code read:
`phase10_candidateJ_training.py` imports only `bootstrap_mae_diff_ci_corrected` from
`research_utils` — the disclosed-flawed original `bootstrap_mae_diff_ci()` is never imported
or called anywhere in the script) with the same `n_boot=2000, seed=42` defaults used
throughout this investigation, on independently-computed per-origin residuals for J and F:

```
J - F (blind 2025):        mean -0.1905, CI95 [-0.3484, -0.0364]   (reported: identical)
J - control (blind 2025):  mean -0.6682, CI95 [-1.0246, -0.3097]   (reported: identical)
```

**Exact match to reported precision.** CI excludes zero on the improving side for both
comparisons.

## 6. H1–H24 results — **VERIFIED, with one disclosed non-blocking wording imprecision**

Independently recomputed the full horizon-by-horizon MAE/bias table for J vs. F from this
audit's own inference pass (`horizon_breakdown`, saved to a scratch JSON for inspection):

- **16/24 horizons improve** in MAE under J relative to F — matches the report's "16 of 24
  horizons" claim exactly.
- Representative horizons cited in the report reproduce exactly: H9 MAE 44.80→44.56
  (bias 3.53→3.33), H12 MAE 62.46→61.93 (bias 17.32→17.43), H13 MAE 62.38→61.76
  (bias 16.45→16.26), H15 MAE 47.13→46.74 (bias 8.78→8.70), H17 MAE 30.66→30.23
  (bias 3.81→4.20) — all match to the reported decimal.

**Disclosed imprecision found**: the report's VERIFIED-claims table states "max
horizon-level bias delta is ≈0.4 W/m²." The actual **maximum absolute** bias delta across
all 24 horizons, independently computed, is **0.7550 at H8** (bias 1.5011→0.7461) — nearly
double the "≈0.4" figure. However, this H8 delta moves bias *toward* zero (an
**improvement**, less overprediction), not a regression. Checking direction explicitly: the
only horizons where bias moves *away* from zero (a genuine "uptick," i.e. worsening) are H17
(+0.39) and H10 (+0.37) — both within the report's "0.1–0.4 W/m²" characterization of
"bias upticks." No horizon shows a worsening-direction bias delta exceeding ~0.4 W/m², so the
substantive claim ("no concentrated bias regression, unlike Candidate I's multi-W/m² jumps")
**holds**. The report's phrasing is imprecise (it states an unsigned "max delta" figure that
is literally wrong, 0.4 vs. actual max |delta| 0.755) but this is a **non-blocking wording
issue, analogous to the disclosed-but-non-blocking bootstrap-calibration finding in the
Candidate F audit** — it does not reflect an actual bias-regression risk, since the largest
delta is an improvement, not a regression.

## 7. Targeted high-elevation × transition-cloud bias — **VERIFIED, exact reproduction**

Independently recomputed at the exact joint-regime cell (elevation≥30° AND cloud_frac∈[0.2,0.6), n=206):

```
                MAE        Bias       RMSE
control:     116.7071   +41.5244   147.8408
Candidate F: 114.5668   +45.3824   146.7810
Candidate J: 113.9984   +44.4706   146.1801
```

**Exact match to reported values** (control +41.52 → F +45.38 → J +44.47, J's bias
slightly better than F's, not worse). Bootstrap CI (J−F) at this cell independently
reproduced: mean −0.5516, CI [−1.9556, 0.8336] (includes zero, as reported — thin n=206,
cell-level change not independently significant, consistent with the report's own disclosed
"FAILED to reach significance alone" item in its claims table).

Aggregate subsets also reproduced exactly: high-elevation (n=978) MAE 100.9250/98.6785/98.0537,
bias 13.7469/12.7406/12.6344; transition-cloud (n=958) MAE 46.6747/45.5216/45.2913, bias
12.7376/12.1548/11.5355 — all match the report's table. Aug–Sep subset (n=1183) and its
bootstrap CI (mean −0.2606, CI [−0.5663, 0.0340]) also reproduced exactly.

## 8. Candidate J model hash and reproducibility — **VERIFIED, complete hash table present**

Freshly computed (this audit, independent `sha256sum`):

| Artifact | Freshly computed SHA256 | Matches `CANDIDATE_J_REPORT.md` table? |
|---|---|---|
| `phase10_candidateJ_training.py` | `a8e55a75e1a0045d66df93c5836ec58481588424c993ac5607a49dd3ac8ce833` | Yes |
| `CANDIDATE_J_RESULTS.json` | `27f784861d207f50a66ac07124e81f80bde21f585709207a49bba296c9da1140` | Yes |
| `model_artifacts/candidateJ_elevation_x_transition.joblib` | `952b6e76f7623da6ecb91a1731e1d8104b1a60564126f02083d6377d215f0ccf` | Yes |

`CANDIDATE_J_REPORT.md` includes a complete provenance/hash table (unlike a report that might
omit one) covering the new script, results JSON, and model artifact, plus every upstream
dependency (see §9). No gap found.

## 9. Frozen Stage 8.1 / Candidate F integrity — **VERIFIED, zero drift**

Freshly re-hashed every upstream dependency in this audit, independent of any stored claim:

| Artifact | Freshly computed SHA256 | Matches `CANDIDATE_F_PRE_TRAINING_AUDIT.md` §8 / `CANDIDATE_J_REPORT.md`? |
|---|---|---|
| Frozen Stage 8.1 control model | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` | Yes — unchanged |
| Candidate F model artifact | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | Yes — unchanged |
| Candidate F results JSON | `b8d2cb700dba26efe24f3603fca63f0328a34e7e07d9200612351b4538a8a325` | Yes — unchanged |
| 2024 feature matrix | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | Yes — unchanged |
| 2025 feature matrix | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` | Yes — unchanged |
| Freeze manifest | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` | Yes — unchanged |
| Frozen 2025 blind-predictions CSV | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` | Yes — unchanged |
| `research_utils.py` (corrected bootstrap utility) | `6d2ef251bf7c9d31b233d83a92cba2933346950511978e490907880871733baa` | Yes — unchanged |

**Zero drift detected anywhere.** Every hash above is identical to the value recorded in
both `CANDIDATE_F_PRE_TRAINING_AUDIT.md` §8 and `CANDIDATE_J_REPORT.md`'s own provenance
table, and to this audit's own independent `sha256sum` computation performed directly against
the files on disk (not copied from any JSON or report).

---

## Summary table

| # | Check | Result |
|---|---|---|
| 1 | Feature construction/alignment; G boundary match | **VERIFIED** |
| 2 | No leakage | **VERIFIED** |
| 3 | EVEN/ODD split, `.fit()` scope | **VERIFIED** |
| 4 | Blind 2025 MAE (35.9745→35.4948→35.3036) | **VERIFIED** (independently reproduced) |
| 5 | Bootstrap 95% CI (corrected, J−F and J−control) | **VERIFIED** (exact reproduction) |
| 6 | H1–H24 breakdown (16/24 improve, no regression) | **VERIFIED**, with one disclosed non-blocking wording imprecision (report's "max ≈0.4 W/m²" bias-delta figure undersells the true max \|delta\| of 0.755 at H8 — but that largest delta is an *improvement*, not a regression; worsening-direction deltas are all ≤0.4 as claimed) |
| 7 | Targeted joint-regime bias (control +41.52→F +45.38→J +44.47) | **VERIFIED** (exact reproduction) |
| 8 | Candidate J hash/provenance table completeness | **VERIFIED** |
| 9 | Frozen Stage 8.1 / Candidate F integrity | **VERIFIED** — zero drift |

No item FAILED. One item (6) carries a disclosed, non-blocking imprecision — analogous in
kind and severity to the single disclosed caveat in `CANDIDATE_F_PRE_TRAINING_AUDIT.md` §5
(both are measurement/wording imprecisions discovered by independent re-derivation that do
not change the qualitative conclusion). No item is UNKNOWN.

**AUDIT PASSED — J READY FOR EMS REPLAY.**
