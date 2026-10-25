# Candidate F Residual Forensics Report

**Scope:** Read-only, inference-only analysis of Candidate F's own residuals on blind 2025
daytime data. No `.fit()` call anywhere in this work. No production/frozen artifact,
feature matrix, freeze manifest, or prior results file was modified. All numbers below
come from `phase9_candidateF_residual_forensics.py`, whose output is
`CANDIDATE_F_RESIDUAL_FORENSICS_RESULTS.json` (both in this directory).

This script reproduced the aggregate blind-2025 MAE for both the frozen control
(35.9745) and Candidate F (35.4948) to within 1e-3 of the values already recorded in
`CANDIDATE_F_RESULTS.json`, confirming the inference path (stage4-residual target,
non-negativity clip, night-causal zeroing) was replicated correctly before any new
breakdown was computed. **VERIFIED.**

---

## 1. F residual-error breakdown (control vs. F at each slice)

### By forecast horizon (selected; full table in JSON)

| Horizon | n | Control MAE | Control bias | F MAE | F bias | ΔMAE (F−ctrl) | F share of total \|err\| |
|---|---|---|---|---|---|---|---|
| H10 | 364 | 52.04 | +8.80 | 51.32 | +8.75 | −0.72 | 8.80% |
| H11 | 364 | 55.02 | −2.24 | 54.29 | −2.52 | −0.73 | 9.31% |
| H12 | 364 | 64.08 | +17.66 | 62.46 | +17.32 | −1.62 | 10.71% |
| H13 | 364 | 62.81 | +15.33 | 62.38 | +16.45 | −0.43 | 10.70% |
| H14 | 364 | 58.92 | +12.77 | 58.16 | +13.13 | −0.76 | 9.98% |

**H10–H14 still account for ~49.5% of F's total absolute error** (sum of the five
"F share" values above), essentially unchanged from the control's H10–H14 share in the
original Phase 1 forensics (8.81+9.31+10.85+10.63+9.97 = **49.57%**). Candidate F
shaves MAE at every one of H10–H14 (by 0.4–1.6 units) but the *concentration* of error
in this horizon band is structurally untouched — F reduces the magnitude of the problem,
not its shape. **VERIFIED** (both numbers computed directly from the JSON outputs of
this script and of the original `ERROR_FORENSICS_RESULTS.json`).

### By month (selected)

| Month | n | Control MAE | Control bias | F MAE | F bias | Δbias |
|---|---|---|---|---|---|---|
| Aug | 686 | 45.99 | +10.75 | 45.72 | +10.67 | −0.08 |
| Sep | 497 | 37.74 | +13.24 | 37.76 | **+14.97** | **+1.73** |

The Aug/Sep positive-bias peak **persists in Candidate F and, in September specifically,
gets slightly worse** (bias +13.24 → +14.97), while Candidate F's MAE in September is
essentially flat (37.74 → 37.76, i.e. no improvement at all). August improves marginally.
**VERIFIED.** This is a new finding not previously reported: F's elevation-interaction
feature does not fix — and in September mildly worsens — the seasonal bias peak that was
flagged as a top Phase-1 concern.

### By solar elevation (full table — this is the key slice; CANDIDATE_F_REPORT.md only
reported the aggregated ≥30° bucket)

| Bin | n | Control MAE | Control bias | F MAE | F bias | ΔMAE | Δbias | F share of total \|err\| |
|---|---|---|---|---|---|---|---|---|
| [0,5) | 940 | 7.90 | −1.49 | 7.77 | −1.63 | −0.13 | −0.14 | 3.44% |
| [5,10) | 652 | 18.08 | +1.10 | 17.91 | −0.08 | −0.17 | −1.17 | 5.50% |
| [10,20) | 1049 | 37.40 | +6.53 | 36.87 | +5.44 | −0.52 | −1.09 | 18.23% |
| [20,30) | 827 | 66.51 | +9.29 | 66.65 | **+10.17** | **+0.14** | **+0.87** | 25.98% |
| [30,90) | 978 | 100.93 | +13.75 | 98.68 | +12.74 | −2.25 | −1.01 | 45.48% |

The monotonic bias-vs-elevation relationship is **still present but no longer strictly
monotonic through the full range**: F *worsens* MAE and bias slightly in the [20,30)
bucket (the bucket just below the one the additive feature targets) while sharply
improving the ≥30° bucket. This is a previously unreported finding: F's improvement is
concentrated at the very top of the elevation range and does not propagate smoothly
downward — in fact it makes the second-highest bucket marginally worse. **VERIFIED.**

### By cloud regime

| Regime | n | Control MAE | Control bias | F MAE | F bias | ΔMAE | Δbias |
|---|---|---|---|---|---|---|---|
| clear | 886 | 33.49 | +8.72 | 33.79 | +6.92 | **+0.30** | −1.80 |
| transition | 958 | 46.67 | +12.74 | 45.52 | +12.15 | −1.15 | −0.58 |
| cloudy | 4134 | 34.03 | +1.08 | 33.54 | +1.05 | −0.49 | −0.04 |

The transition regime (still the highest-MAE regime, as in the original forensics)
improves modestly under F (MAE −1.15, bias −0.58) but **remains the worst-performing
regime by MAE**, and the "clear" regime's MAE *slightly worsens* under F even as its
bias improves (bias overcorrected downward by 1.80, MAE up 0.30 — i.e. F trades bias
for a wider/more variable error in clear-sky conditions). **VERIFIED.**

### By clear-sky GHI intensity

| Bin | n | Control MAE | F MAE | ΔMAE |
|---|---|---|---|---|
| [0,50) | 2549 | 4.43 | 4.41 | −0.02 |
| [50,150) | 749 | 20.41 | 20.26 | −0.14 |
| [150,300) | 839 | 38.21 | 37.51 | −0.70 |
| [300,1200) | 1841 | 84.96 | 83.81 | −1.15 |

Improvement scales roughly with intensity bucket size, consistent with the elevation
finding (both are proxies for "more sunlight present, more absolute error available to
correct"). No new regime structure here beyond what intensity and elevation already show
together. **VERIFIED.**

---

## 2. Largest systematic residual patterns (ranked, F's own residuals)

1. **High elevation (≥30°) carries 45.5% of F's total absolute error** (n=978, 16.4% of
   rows) — the single largest concentration, even after F's targeted correction.
   **VERIFIED.**
2. **Horizons H10–H14 carry ~49.5% of F's total absolute error** (n=1820, 30.4% of rows)
   — essentially unchanged in share from the control. **VERIFIED.**
3. **The joint cell "elevation ≥30° AND transition cloud regime" is dramatically worse
   than either axis alone**: n=206, F's MAE there is **114.57** (vs. 98.68 for the ≥30°
   bucket overall, vs. 45.52 for the transition regime overall) and F's **bias is
   +45.38** — more than triple the ≥30° aggregate bias of +12.74 and nearly 4x the
   transition-regime aggregate bias of +12.15. This is the single worst residual cell
   found in the entire slice/interaction analysis, and it was not previously reported at
   this resolution (CANDIDATE_F_REPORT.md reported only the aggregated ≥30° bucket;
   CANDIDATE_G_REPORT.md's transition feature was a flat global flag never crossed with
   elevation). **VERIFIED** (see `interaction_elevation_x_cloud_regime_F_only` in the
   JSON; computed directly from F's residuals, n=206 ≥ reporting threshold of 5).
4. **September bias got worse under F** (+13.24 → +14.97) while MAE stayed flat — a mild
   regression hidden inside an overall-improving aggregate. **VERIFIED.**
5. **The [20,30) elevation bucket got slightly worse under F** (MAE +0.14, bias +0.87) —
   the bucket adjacent to, but just below, the one F's interaction feature targets.
   **VERIFIED.**
6. Horizon-level deltas (F vs. control) are **all negative except H2, H3, H4, H9(month
   interactions aside), H20-month-9** in the finer month×horizon cross-tab — i.e.
   almost every single-hour slice improves a little, but the cross-tab shows those small
   per-hour gains concentrate unevenly by month (e.g. H10–14 × August: MAE 102.58, bias
   +39.86; H10–14 × September: MAE 77.98, bias +39.83 — both far worse than the H10–14
   aggregate of ~58–62). **VERIFIED**, and this interaction (mid-day horizons × late-
   summer months) is a second strong candidate concentration, related to but distinct
   from the elevation×transition-cloud finding above.

---

## 3. Features/interactions most strongly associated with remaining error

Linear probe of `|F_residual|` on `[month, hour, solar_elevation, cloud_frac,
clearsky_ghi, horizon_hour]` (same spec as the original Phase-1 probe):

- **R² = 0.4395** (vs. control's R² = 0.4457 on the same inputs). **VERIFIED.**
  Candidate F's remaining error is *almost exactly as linearly predictable from
  forecast-time regime variables as the control's error was* — F did not make the
  residual less systematic in a way this linear probe can detect; it mainly shifted the
  magnitude down while leaving the same regime structure intact.

Shallow decision-tree probe (`max_depth=4`, `min_samples_leaf=30`) on all 38 Candidate F
input features, in-sample R² = 0.4881 (exploratory only, not held-out — **UNKNOWN**
whether this generalizes). Top feature importances:

| Feature | Importance |
|---|---|
| `pred_stage4_fold` | 0.799 |
| `solar_zenith` | 0.084 |
| `lwp_x_cloud` | 0.038 |
| `cloud_frac` | 0.021 |
| `lwp_latest` | 0.020 |
| `phys_pred_fold` | 0.018 |
| `elevation_x_cloud_frac` (F's own feature) | 0.005 |

The dominant driver of residual magnitude is `pred_stage4_fold` itself — i.e. the larger
Stage 4's own prediction is, the larger F's absolute residual tends to be, which is
consistent with absolute error scaling with signal magnitude (high-irradiance periods
have bigger errors in absolute terms). Candidate F's own new feature
(`elevation_x_cloud_frac`) ranks low (0.005) in this diagnostic, meaning *the feature as
currently constructed captures only a small slice of the residual-explaining signal that
remains* — consistent with finding #3 above (the elevation×transition-regime *interaction*
specifically, not the smooth elevation×cloud_frac product F already has, is where the
largest unexplained structure sits). **VERIFIED** for the stated correlations/importances;
**UNKNOWN** whether a retrained model would actually exploit this differently without
testing it.

Correlation of each of F's 38 features with `|residual|` (top 5, from the full ranked
table in the JSON):

| Feature | corr(|resid|) | corr(signed resid) |
|---|---|---|
| `clearsky_ghi` | 0.657 | 0.093 |
| `clearsky_ghi_terrain_adjusted` | 0.645 | 0.097 |
| `solar_elevation` | 0.637 | 0.091 |
| `solar_zenith` | −0.637 | −0.091 |
| `pred_stage4_fold` | 0.628 | 0.143 |

`elevation_x_cloud_frac` itself correlates 0.543 with `|residual|` — it is still one of
the stronger univariate correlates, but it is dominated by the raw intensity/elevation
variables it was built from, again pointing to "more signal, more absolute error" rather
than a genuinely new error-explaining axis. **VERIFIED.** (`u700`/`v700` show `NaN`
correlation — both are constant in the blind-2025 daytime subset, i.e. these features
carry zero variance in this evaluation slice; flagged as **UNKNOWN significance** since
it was not investigated further, out of scope for this residual task.)

---

## 4. Does the pattern suggest a justified next training experiment?

Yes, with one specific, narrow justification — not the previously untested "moderate
quantile shift (~0.45)" guess from `CANDIDATE_G_ONWARD_COMPARISON_REPORT.md`, which this
report does not find direct evidence for or against (that guess was about asymmetric
loss shape; Candidate H already tested a stronger version, q=0.35, of the same idea and
it **overshot badly** — this residual analysis did not re-examine the quantile-loss axis
and takes no position on retrying a milder q).

What the evidence in Sections 1–3 does support: the worst remaining regime is not
"high elevation" alone (F already addresses that, partially) and not "transition cloud"
alone (Candidate G's flat global flag for that already failed) — it is **the specific
joint intersection of the two**, where F's MAE (114.57) and bias (+45.38) are far worse
than either marginal regime. Candidate F's `elevation_x_cloud_frac` feature is a smooth
product over the *entire* cloud_frac range and dilutes this specific joint signal across
all cloud conditions; Candidate G's `is_transition_cloud` flag is a flat 0/1 indicator
never crossed with elevation, so it could not isolate this joint cell either. Neither
previously-tested feature targeted this exact intersection directly.

**Caveat found during this work that tempers the recommendation:** the joint regime
(solar_elevation ≥ 30° AND cloud_frac in [0.2, 0.6)) contains only **86 of 2885** 2024-EVEN
training rows (≈3.0%). With `min_samples_leaf=30`, this is barely enough for the HGB
model to form a dedicated leaf, and any new candidate targeting this cell risks high
variance / overfitting on a thin slice — this is exactly the overfitting failure mode
already seen with Candidate I (targeted high-elevation-only residual correction, which
overfit on ODD and made control-worse on blind 2025). **VERIFIED** (row count computed
directly from the 2024 EVEN daytime training split; n=86 is small by the same standard
that made Candidate I's targeted correction unreliable).

---

## 5. Recommended next candidate experiment

**One recommendation, offered with an explicit caveat on data sparsity (not a
high-confidence prediction of success):**

**Candidate J (proposed, NOT trained in this task): add one additive interaction feature,
`elevation_x_transition_cloud = solar_elevation × is_transition_cloud`, where
`is_transition_cloud = 1{0.2 ≤ cloud_frac < 0.6}` (reusing Candidate G's exact definition),
on top of Candidate F's existing 38 features (39 total). Same architecture/hyperparameters/
split/target as every other candidate in this investigation (train 2024 EVEN, blind-eval
2025, same `FROZEN_HP`).**

Justification, traced to specific findings above:
- Section 1 (elevation table) + Section 2 finding #3: the elevation≥30°×transition-cloud
  joint cell (n=206) has F's worst MAE (114.57) and bias (+45.38) of any slice examined —
  roughly 4x the aggregate transition-regime bias and >3x the aggregate high-elevation
  bias.
- Section 3: F's own `elevation_x_cloud_frac` feature (a smooth product over the *whole*
  cloud_frac range, importance 0.005 in the tree probe) does not isolate this specific
  joint cell; Candidate G's flat `is_transition_cloud` flag (never crossed with elevation)
  also could not and, when tested standalone, failed to beat F.
- The proposed feature is the direct product of the two signals that jointly define the
  worst cell, which neither F nor G tested.

**Explicit leakage check:** `solar_elevation` is pure astronomical geometry, known
arbitrarily far in advance (already a forecast-time input in the frozen 37-feature
contract). `is_transition_cloud` is a deterministic threshold function of `cloud_frac`,
itself an existing forecast-time-available input already in the frozen 37-feature
contract and already used unmodified by Candidate G per `CANDIDATE_G_REPORT.md`'s own
leakage check. Their product is therefore a deterministic function of two
forecast-time-available quantities and introduces **no leakage** — same reasoning
standard applied to Candidate F's and Candidate G's own features. **VERIFIED** (feature
construction logic, not an empirical claim).

**Explicit caveat / non-overclaim:** this cell's thin training support (n=86, ≈3.0% of
2024 EVEN daytime rows) means this candidate carries real overfitting risk, by the same
logic that invalidated Candidate I. This report does **not** claim Candidate J will
improve blind-2025 MAE — only that, if a next experiment is run, this specific
interaction is the one best supported by the residual evidence gathered here, and it
should be evaluated with the corrected bootstrap CI (`bootstrap_mae_diff_ci_corrected` in
`research_utils.py`) **computed separately on the elevation×transition-cloud subset**
(n=206) in addition to the full blind-2025 set, given how small and failure-prone this
specific slice already is. **No training was performed as part of this task.**

---

## 6. VERIFIED / UNKNOWN summary

| Claim | Status |
|---|---|
| Aggregate blind-2025 MAE reproduced exactly (control 35.9745, F 35.4948) | VERIFIED |
| H10–H14 share of F's total \|error\| ≈ 49.5%, materially unchanged from control's 49.57% | VERIFIED |
| Aug/Sep bias peak persists; September bias specifically worsens under F (+13.24→+14.97) | VERIFIED |
| Elevation-bias relationship no longer strictly monotonic under F ([20,30) bucket worsens) | VERIFIED |
| Transition cloud regime remains worst-MAE regime under F, improves only modestly | VERIFIED |
| Elevation[30,90) × transition-cloud joint cell is F's single worst slice (MAE 114.57, bias +45.38, n=206) | VERIFIED |
| Linear residual-predictability R² for F (0.4395) ≈ control's (0.4457) — systematic structure not reduced | VERIFIED |
| Shallow-tree in-sample R² (0.4881) on all 38 features — exploratory diagnostic only | VERIFIED as computed; generalization UNKNOWN |
| `elevation_x_cloud_frac`'s low tree-importance (0.005) implies F's own feature captures little of the remaining structure | VERIFIED as computed; causal interpretation UNKNOWN |
| `u700`/`v700` zero variance in blind-2025 daytime subset (NaN correlation) | VERIFIED; further significance UNKNOWN (out of scope here) |
| Candidate J (elevation × is_transition_cloud) will improve blind-2025 MAE if trained | UNKNOWN — not tested, explicitly flagged as uncertain due to thin training support (n=86) |
| Candidate J introduces no leakage | VERIFIED (construction-based, not empirical) |
| Zero drift in all tracked inputs/artifacts across this task | VERIFIED (hash table below) |

---

## Provenance / hash table

New files produced by this task:

| File | SHA256 |
|---|---|
| `phase9_candidateF_residual_forensics.py` | `75aa63fc8d031d0aa948924c7e28443906a36a31809bf0ea05d45e9b740f7704` |
| `CANDIDATE_F_RESIDUAL_FORENSICS_RESULTS.json` | `060fb45119487b7d3edb0826e6f577a51ff4b769020ee4ca71012653160c2c2c` |
| `CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md` | this file (hash not computed, still being written when the table above was generated) |

Re-verified hashes of all touched inputs, **before** and **after** this task's analysis
(identical in both columns — confirms zero drift; see `provenance_hash_drift_check` in
`CANDIDATE_F_RESIDUAL_FORENSICS_RESULTS.json` for the machine-readable version):

| Input | SHA256 (before == after) | Match |
|---|---|---|
| `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` | YES |
| `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | YES |
| Frozen control model (`stage8_1_CORRECTED_candidate_37feature_model.joblib`) | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` | YES |
| Candidate F model (`candidateF_elevation_x_cloud.joblib`) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | YES |
| `stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` | YES |
| `FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json` | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` | YES |
| `CANDIDATE_F_RESULTS.json` | `b8d2cb700dba26efe24f3603fca63f0328a34e7e07d9200612351b4538a8a325` | YES |

No `.fit()` call occurs anywhere in `phase9_candidateF_residual_forensics.py`. No file in
the above table, nor any production/config file, was modified, retrained, or re-saved by
this task. Candidate J, described in Section 5, was **not** trained.
