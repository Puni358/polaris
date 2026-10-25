# Candidate J Through the Actual-Solar EMS Replay — vs. Candidate F and Frozen Stage 8.1

**Scope**: Runs Candidate J (the research-only 39-feature `elevation_x_transition_cloud`
joint-interaction model, `CANDIDATE_J_REPORT.md` — Candidate F's 38 features + one new
additive feature `solar_elevation × is_transition_cloud`) through the exact same
actual-solar EMS replay methodology already used for the frozen Stage 8.1 control and for
Candidate F (`CANDIDATE_F_EMS_REPLAY_REPORT.md`), on the same 245 NORMAL-route origins, same
warmed-up `StationState`, same critical-demand/terminal-reserve formula, same replay physics
(diesel/discharge held fixed from the plan; charge clipped to availability; critical load
protected before charging). **GAP19 was never re-run with actual solar as an input in any
arm** — only the forecast *model* producing `solar_generation` differs between arms; the
optimizer itself is called exactly once per arm per origin, in its normal planning role.

Only Candidate J's own arm was newly run. The frozen Stage 8.1 control and Candidate F
numbers were **pulled, unmodified**, from the already-written
`CANDIDATE_F_EMS_REPLAY_RESULTS.json` — not re-run, per task instruction — after
independently confirming (in the new script, before use) that the set of 245 NORMAL origins
recorded there for `stage81_frozen` and `candidate_F` are identical, and that Candidate J's
own run reaches NORMAL on exactly that same 245-origin set (0 mismatches).

Scripts:
- [run_candidateJ_actual_solar_replay.py](run_candidateJ_actual_solar_replay.py) — generates
  Candidate J's forecast bundle and GAP19 plan per origin, replays it against actual solar.
- [analyze_candidateJ_ems_replay.py](analyze_candidateJ_ems_replay.py) — pure post-hoc
  analysis (aggregates, per-origin win/tie/regression, corrected bootstrap CI) over the two
  already-written raw-results files; no model load, no GAP19 call, no `.fit()`.

Raw results: [CANDIDATE_J_EMS_REPLAY_RESULTS.json](CANDIDATE_J_EMS_REPLAY_RESULTS.json),
[CANDIDATE_J_EMS_REPLAY_ANALYSIS.json](CANDIDATE_J_EMS_REPLAY_ANALYSIS.json).

---

## Provenance / hash table — VERIFIED, zero drift

All hashes below were checked **before and after** the Candidate J replay run
(`run_candidateJ_actual_solar_replay.py`'s own pre/post verification, reproduced here) and
again before/after the analysis pass (`analyze_candidateJ_ems_replay.py`'s own pre/post
verification of the two JSON inputs it reads). No frozen or pre-existing input changed.

| Input | Hash | Pre-run | Post-run |
|---|---|---|---|
| Candidate J model (`candidateJ_elevation_x_transition.joblib`) | `952b6e76f7623da6ecb91a1731e1d8104b1a60564126f02083d6377d215f0ccf` | MATCH | MATCH |
| Candidate F model (`candidateF_elevation_x_cloud.joblib`) | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | MATCH | MATCH |
| Frozen Stage 8.1 model | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` | MATCH | MATCH |
| 2024 feature matrix (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` | MATCH | MATCH |
| Freeze manifest (`FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json`) | `de8c0f471bbfb16bbef180831ecd2b40c4d1cb9d3555062a11b986e4a9771b35` | MATCH | MATCH |
| `CANDIDATE_J_RESULTS.json` (forecast-only phase, read-only reference) | `27f784861d207f50a66ac07124e81f80bde21f585709207a49bba296c9da1140` | MATCH | MATCH |
| `CANDIDATE_F_EMS_REPLAY_RESULTS.json` (control+F EMS numbers, pulled not re-run) | `56974fcef86f219e2f6aec1671b14acd36b69c9c4eb9bad7245a2830dcf2fd32` | MATCH | MATCH |
| `run_actual_solar_replay.py` (replay engine, imported unmodified) | `51a107599d08c7da088c8751c80aa986ebfc1a268a0f0d1f2ffd4ebb67971807` | MATCH | MATCH |
| `run_full_experiment.py` (component builder, imported unmodified) | `8afaf9ee7862c4586c586d14debb418d78f655362d1d729407300595fce118d5` | MATCH | MATCH |
| `run_research_simulation.py` (terminal-reserve formula, imported unmodified) | `d68b343d60f67a2fc8143316278371342d3933f70d0e26d40f3c1c732d843bd1` | MATCH | MATCH |
| system/config/*.yaml (battery, diesel, loads, solar_pv, station, optimizer) | per `run_full_experiment.verify_frozen_manifest()` | MATCH (all 6) | MATCH (all 6) |

**New files produced by this task** (not frozen inputs, listed for completeness):

| File | SHA256 |
|---|---|
| `run_candidateJ_actual_solar_replay.py` | `4356362e28e519adbece72a77937bf02663641655601191ac390c310043abb45` |
| `analyze_candidateJ_ems_replay.py` | `3713394c864c22087131fe2af8e51cb650ec86b80b7656bbdf00aca172ea01d7` |
| `CANDIDATE_J_EMS_REPLAY_RESULTS.json` | `4bae35a8651e084c8dd768339cf5a230780be38fcdf07de187042b72e6b93448` |
| `CANDIDATE_J_EMS_REPLAY_ANALYSIS.json` | `ccbfcf40405f0bf151719a8327deb4a649f9f99d5ac127adb5e91bcfe340603c` |

**No production, config, or frozen artifact was modified. No `.fit()` was called anywhere in
this task's code.** Candidate J's model is a research-only artifact, loaded read-only; the
frozen Stage 8.1 model and GAP19 itself are used exactly as in every prior EMS experiment in
this diagnostic branch.

---

## 1. Aggregate results (245 NORMAL origins, identical across all three arms) — VERIFIED

| Metric | Frozen Stage 8.1 | Candidate F | Candidate J | Δ (J − F) | Δ (J − Stage8.1) |
|---|---|---|---|---|---|
| Realized diesel fuel (L) | 10,849.6015 | 10,888.1696 | 10,886.1994 | **−1.9702** | **+36.5979** |
| Realized curtailment (Wh) | 8,869,721.3 | 8,855,806.5 | 8,845,829.5 | −9,977.0 | −23,891.8 |
| **Realized critical-load unmet (Wh)** | **1,739,283.7** | **1,658,490.2** | **1,647,681.0** | **−10,809.2 (−0.6517%)** | **−91,602.7 (−5.2667%)** |
| Realized battery charge (Wh) | 36,534,371.8 | 36,657,230.9 | 36,754,214.6 | +96,983.7 | +219,842.8 |
| Realized battery discharge (Wh) | 26,575,094.1 | 26,629,563.5 | 26,698,917.6 | +69,354.1 | +123,823.5 |
| **SOC violations** | **0 / 245** | **0 / 245** | **0 / 245** | no change | no change |
| Origins with nonzero realized unmet | 220 / 245 | 219 / 245 | 220 / 245 | +1 | 0 |

n = 245 confirmed identical NORMAL-route origins across all three arms (frozen manifest/hash
re-verification above; Candidate J independently reaches NORMAL on exactly the same 245
origins as the control and Candidate F, 0 mismatches).

**Candidate J reduces aggregate realized critical-load unmet by a further 10,809.2 Wh
(−0.65%) relative to Candidate F**, and by 91,602.7 Wh (−5.27%) relative to the frozen
control — achieved with essentially flat diesel (−1.97 L vs. F, i.e. *slightly less*
committed diesel than F, not more, unlike F's own +0.36% increase over the control).
Reliability (SOC violations) is unchanged: zero for all three arms.

## 2. Per-origin wins/ties/regressions — VERIFIED, NOT a uniform win

**Tie threshold**: ±0.001 Wh (1 milliWh), chosen to match the magnitude implied by the
Candidate F report's own "(±1 mWh)" tie convention and to absorb floating-point noise from
the replay's rounding (`round(..., 4)` on Wh-scale sums) without creating false positives at
a scale that has no physical meaning.

### J vs Candidate F (realized unmet, 245 origins)

| | Count (of 245) |
|---|---|
| Origins where Candidate J has **less** realized unmet (improvement) | **124 (50.6%)** |
| Origins where Candidate J has **more** realized unmet (regression) | **94 (38.4%)** |
| Tied (±1 mWh) | 27 (11.0%) |

Largest single-origin improvement (J vs F): 2024-06-13 (−2,333.8 Wh). Largest single-origin
regression (J vs F): 2024-05-18 (+3,027.0 Wh).

**This is a narrower margin than Candidate F's own margin over the control** (F improved
56.3% of origins over control / regressed 32.7%; J improves only 50.6% of origins over F /
regresses 38.4%). The win count is barely over half, and the regression count (94) is
*larger* than F's own regression count against the control (80) — J is less uniformly
beneficial relative to its own baseline (F) than F was relative to its baseline (the frozen
control).

### J vs frozen Stage 8.1 control (realized unmet, 245 origins)

| | Count (of 245) |
|---|---|
| Origins where Candidate J has **less** realized unmet (improvement) | **143 (58.4%)** |
| Origins where Candidate J has **more** realized unmet (regression) | **77 (31.4%)** |
| Tied (±1 mWh) | 25 (10.2%) |

Against the control, J's win/regression split (58.4% / 31.4%) is comparable to — slightly
better than — F's own split against the control (56.3% / 32.7%), consistent with J carrying
forward (and marginally extending) F's net-positive effect over the control.

### Where do the J-vs-F regressions concentrate? — mechanistic check

| Month | Regressions (J vs F) | Total origins | Regression rate |
|---|---|---|---|
| Mar | 10 | 31 | 32.3% |
| Apr | 18 | 30 | **60.0%** |
| May | 15 | 31 | 48.4% |
| Jun | 16 | 30 | 53.3% |
| Jul | 12 | 31 | 38.7% |
| Aug | 11 | 31 | 35.5% |
| Sep | 6 | 30 | 20.0% |
| Oct | 6 | 31 | 19.4% |

Regressions are **not evenly spread**: April–June (spring/early-summer, the months with the
highest midday solar elevation at this latitude and the window where transition-cloud
conditions most often co-occur with high elevation) show a 48–60% regression rate, roughly
2–3× the 19–20% rate seen in September–October. This is directionally consistent with
Candidate J's feature design: `elevation_x_transition_cloud` is built specifically to act
in the `solar_elevation ≥ 30 AND cloud_frac in [0.2, 0.6)` regime, i.e. exactly the
high-elevation, partly-transitional-cloud conditions concentrated in these months. The
*forecast-only* targeted-regime audit (`CANDIDATE_J_PRE_EMS_AUDIT.md`,
`CANDIDATE_J_RESULTS.json`) found J's bias at that regime (+44.47) only marginally better
than F's (+45.38) — a small, not dramatic, improvement that is itself close to the
statistical noise floor. An EMS-level pattern where J is more often *worse* than F in the
exact months where that thin, narrowly-targeted feature is most active is consistent with
a feature correction that is real but too small and too concentrated in a thin regime
(~3.0% of training rows, per the training script's own disclosed overfitting caveat) to
reliably help every origin it touches — some origins in its target window improve, a
comparable or larger number regress, net aggregate effect still favors J but not by a
margin that holds up origin-by-origin. This is consistent with, not independently proving
beyond this replay, the training-time caveat already disclosed in
`phase10_candidateJ_training.py`.

## 3. Statistical significance — VERIFIED

**Bootstrap 95% CI (corrected origin-level paired bootstrap, 2,000 resamples, seed=42) for
the aggregate (sum) realized-unmet difference:**

| Comparison | Point estimate (Wh) | Mean (Wh) | 95% CI (Wh) | Excludes zero? |
|---|---|---|---|---|
| **J − F** | **−10,809.2** | −10,821.5 | **[−26,858.4, +6,716.5]** | **NO** |
| **J − control** | **−91,602.7** | −91,720.2 | **[−121,322.8, −61,777.2]** | **YES** |

**(J − F) does NOT exclude zero.** The point estimate favors J (−10,809.2 Wh, a further
0.65% reduction beyond Candidate F), but the 95% CI straddles zero — the apparent
improvement of Candidate J over Candidate F at the EMS level **is not statistically
distinguishable from no effect** at this sample size (n=245 origins).

**(J − control) DOES exclude zero**, entirely on the improving side — Candidate J's
aggregate improvement *relative to the frozen control* (−91,602.7 Wh, −5.27%) is
statistically significant, consistent with (and a small increment beyond) Candidate F's own
already-established, separately-verified significant improvement over the control
(`CANDIDATE_F_EMS_REPLAY_REPORT.md`: −80,793.5 Wh, CI `[−112,308.8, −49,407.8]`, excludes
zero).

## 4. Does J's forecast improvement translate into additional EMS benefit over F? — UNKNOWN / NULL RESULT, reported plainly

**Direct answer: NO — not verified.** Candidate J's forecast-level improvement over
Candidate F (blind-2025 MAE 35.4948 → 35.3036, bootstrap CI for (J−F) `[−0.3484, −0.0364]`,
excluding zero — a real but small forecast-level effect, per `CANDIDATE_J_REPORT.md`) does
**not** translate into a statistically distinguishable EMS-level benefit over Candidate F on
this replay. The point estimate is directionally favorable to J (−10,809.2 Wh, −0.65% vs. F)
and the per-origin win rate against F (50.6%) is just barely over half, but:

- The (J − F) bootstrap 95% CI **includes zero** (`[−26,858.4, +6,716.5]`) — this is a
  **clean null result** at the EMS level, in the same sense every one of Candidates C/D/E/G/H/I
  was reported as a clean null in the forecasting-only phase when the numbers showed no
  significant effect. It is not overclaimed here.
- The regression count against F (94/245, 38.4%) is *larger* than F's own regression count
  against the control (80/245, 32.7%) — J is, if anything, *less* uniformly beneficial
  relative to its own baseline than F was relative to its baseline.
- This is **plausible and expected**, not a surprising failure: Candidate J's own
  forecast-level effect over F (mean MAE diff −0.1905, CI width ≈0.31) was already
  substantially smaller than F's effect over the control (Candidate F's own forecast-level
  improvement was larger in both absolute MAE terms and in the EMS replay, where F's CI
  excluding zero had a much wider separation from zero). A smaller forecast-level signal
  propagating through the same EMS pathway (GAP19's terminal-reserve/direct-bus-bar logic,
  per `STAGE81_FORECAST_VALUE_TRANSLATION_INVESTIGATION.md`) that already attenuated F's
  larger signal down to a modest EMS effect would be expected to attenuate J's smaller
  signal down further, plausibly into statistical noise at this origin-count (n=245).
- **What IS verified**: J still carries forward a statistically significant improvement over
  the frozen control (CI excludes zero, consistent with and slightly larger than F's own
  control-relative effect). What is **not verified** is that J provides any additional,
  statistically distinguishable EMS benefit *beyond* what Candidate F already provides.

**Promotion status**: unchanged from Candidate J's own forecast-only report — Candidate J is
not promoted to production under any outcome of this test; this EMS replay provides no new
basis for promotion, and (per the null J-vs-F EMS result here) no basis for preferring J
over F operationally either, despite J passing its own forecast-only promotion bar against F.

## UNKNOWN / not established by this replay

- **Why the J-vs-F EMS effect is smaller/less consistent than the J-vs-F forecast effect's
  own statistical significance would suggest** — not decomposed beyond the month-concentration
  observation in §2; a full per-origin forensic pass (in the style of
  `STAGE81_UNMET_DECOMPOSITION_REPORT.md`) was not performed for Candidate J specifically.
- **Whether a larger origin sample (more than the frozen 245-origin 2024 window) would
  resolve the (J−F) CI's inclusion of zero** — not testable with the data available in this
  repository's EMS pipeline format (same limitation disclosed in the Candidate F EMS report).
- **Whether the EMS-level effect would hold on a true 2025 EMS replay** — not tested, same
  limitation as disclosed in `CANDIDATE_F_EMS_REPLAY_REPORT.md`.
- **Whether the small diesel decrease (−1.97 L vs. F, aggregate) has any cost/governance
  implication** — not evaluated; no authorized cost function exists for diesel vs. unmet
  trade-offs in this research track (same limitation stated in every prior report in this
  chain).

## STOP

Candidate J EMS replay complete. No production, config, or frozen artifact modified; all
input hashes re-verified MATCH before and after both the replay run and the analysis pass,
with zero drift. Result: Candidate J produces a small, directionally favorable, but
**statistically non-significant** (CI includes zero) further reduction in realized
critical-load unmet relative to Candidate F — reported here as a clean null result on the
primary J-vs-F EMS question, consistent with (not amplified beyond) what the data supports.
Candidate J's improvement over the frozen control remains statistically significant, as does
Candidate F's own improvement over the control, independently established in the prior
report.
