# Decision Resolution: D2, D6, D10, D4 and Arm C A1–A6

Prepared 2026-10-11 by CC. This is decision recording only: **no experiment execution, real-data calibration, forecast replay, training or MILP solve took place.**

**Authority.** In M6 (`cmsg_017TpQv3UrTPMkzn658LmXvX811eenQyWHcEa6oV6mYRX3`, 2026-10-11 03:16:59 UTC), Puni (`user_01Dj2JKqyS22XoGCMZ8tUQAw`) confirmed being the project lead. M6 also says that the confirmation "does not mean every proposed decision below has already been approved". Each item below is therefore classified by what M6 actually instructs:

| Class | Meaning |
|---|---|
| **APPROVED (M6)** | M6 instructs CC to record the rule as the decision once a stated check passes, and the check passed |
| **RECORDED UNDER M6 INSTRUCTION** | M6 told CC to choose a value and record it as a project-lead decision (the seed) |
| **CONFLICT** | M6's proposal conflicts with the existing protocol. M6 says to record the conflict and require an explicit resolution |
| **RECOMMENDED** | CC's choice of a methodological option. Not supported decisively by existing evidence. **Awaiting project-lead approval** |
| **BLOCKED** | A required choice is missing |

The historical protocol files in `reports/source_prep/` were not modified.

---

## 1. D2: S4 total unmet-energy non-regression. Status: **APPROVED (M6)**

**Check M6 required:** compatibility with the data schema and the protocol.
- **Protocol:** `PROTOCOL.md` §5 defines S4 identically: executor `unmet_load_w` × 1 h, summed over the identical 123 × 24 cells, `U(arm) ≤ U(PC-Control)`, ties pass, no tolerance, and missing or failed data make the arm INVALID.
- **Schema:** the runner's hourly telemetry carries `unmet_load` (from `RealizationResult.unmet_load_w`), `origin_id` and `hour` (0–23).
- **Result:** compatible. No proxy is needed.

**Rule (implemented as `gates_three_arm.s4_point`):**
- **Unit:** U(arm) = Σ over (origin, hour) cells of `unmet_load` [W] × 1 h, in Wh (realized, not planned). The sum uses `math.fsum`, so it is exact and independent of order.
- **Pairing:**
  - The arm's set of (origin, hour) cells must equal PC-Control's.
  - Every origin must have exactly hours 0–23.
  - There must be no duplicates, no non-finite values, and no non-OPTIMAL/FEASIBLE status.
  - The runner's `validate_run` already requires all 123 origins for every arm.
- **Missing, failed, invalid or unpaired data:** the comparison is NOT EVALUABLE and counts as FAIL. No cell is dropped or imputed.
- **Pass rule:** PASS iff U(arm) ≤ U(PC-Control). Exact ties pass. There is no tolerance beyond the executor's own 0.01 W rounding.
- **Scope:** every non-control arm. S4 is a reliability gate for the E1 verdict. Nothing in this experiment is promotion-eligible.
- **Reported fields:**
  - U_arm, U_ref and delta in Wh;
  - number of origins and cells;
  - origins worse, equal and better;
  - per-origin delta mean, median, min and max;
  - worst 5 origins;
  - S4 against Arm A, report-only, as PROTOCOL §5 requires.
- **Tests (`tests/test_decision_resolution.py`):**
  - a tie passes;
  - a 0.01 W regression fails;
  - an improvement passes;
  - seven missing, unpaired or failed cases are each NOT EVALUABLE;
  - a failed arm ends as NOT AN IMPROVEMENT.

## 2. D6: Strict S4 and seed governance. Status: **PARTIALLY APPROVED**

| Element | Decision | Class |
|---|---|---|
| Strict S4 is required in addition to S4, and is reported separately | Adopted (`S4_strict: ADOPTED`). A candidate needs S4_point PASS and S4_strict PASS. Both appear separately in the output | APPROVED (M6) |
| Statistic | Mean over origins of the paired per-origin delta U_o = U_arm,o − U_ctrl,o (Wh/origin), in chronological order. Hours are never treated as independent | APPROVED (M6; PROTOCOL §5) |
| Method | Politis–Romano stationary bootstrap: circular wrap-around, geometric block lengths, uniform block starts, percentile interval (`gates_three_arm.stationary_bootstrap_means`) | APPROVED (M6; PROTOCOL §5 "paired stationary block bootstrap") |
| Mean block length | 10 days = 10 origins. Supported: the runner enforces 123 consecutive daily origins (`evaluation_origins`), and origin_id order is chronological | APPROVED (M6) |
| Resamples | 10,000 | APPROVED (M6) |
| Seed | **42**, via `numpy.random.default_rng(42)`. No seed for S4-strict was preregistered (PROTOCOL §5 says only "seed preregistered"). 42 is the package's one existing preregistered seed (E1 BCa, `planner_cf_statistics.py`), reused for a separate generator. It was chosen before any result exists and not by outcome | RECORDED UNDER M6 INSTRUCTION ("propose a documented seed and record it as a project-lead decision"). You may change it before freeze |
| **Interval** | Recommended: **`two_sided_95_upper`**, the 97.5th percentile. Evidence: E1's "BCa 95% lower bound" is the lower end of a two-sided 95% interval (`stats.bootstrap(..., confidence_level=0.95)`), so the matching S4 "upper 95% bound" is the upper end of a two-sided 95% interval. This is also the more conservative choice. Alternative: `one_sided_95_upper` (95th percentile) | **RECOMMENDED, awaiting approval.** The config holds `null` plus `S4_strict_interval_recommendation` |
| E1 bootstrap | E1 keeps the preregistered iid BCa. The block bootstrap for Δfuel is a separate secondary report (PROTOCOL §7) | APPROVED (M6 D4: "Do not substitute a different primary test") |
| Metadata in the output | Algorithm text, seed, mean block, resamples, numpy version, origin count, percentile | Implemented |

**Tests:**
- the vectorized bootstrap equals a straightforward loop of the documented algorithm;
- the same seed gives the same result, and a different seed gives a different one;
- the config seed, block, resamples and interval are used;
- a candidate that passes S4_point but fails S4_strict is shown separately;
- a missing pair makes the result NOT EVALUABLE.

**Cost:** the bootstrap is arithmetic only, with 0 solver calls.

## 3. D10: E1 Holm family. Status: **CONFLICT, explicit resolution required**

**Existing specification:**
- `PROTOCOL.md` §7: "E1 as defined (Holm over decision-bearing comparisons: A vs Control, C vs Control)".
- `PROTOCOL_ADDENDUM_D7a.md` §1: "A-Fix is a diagnostic comparison."
- PROTOCOL §5, E1: "Wilcoxon (Holm) adjusted p < 0.05 AND BCa 95% lower bound > 0 L/origin. Evaluated only if the safety gates pass."

**M6 proposal:** the family is {A, A-Fix, C} vs PC-Control.

**Conflict:** M6 adds A-Fix, which the protocol and the D7a addendum designate as diagnostic. As M6 instructs, CC records the conflict and does not resolve it. The config holds `E1_holm_family: null`, and preflight and the gate code refuse to evaluate without it.

| Option | Family | Consequence |
|---|---|---|
| (a) Protocol | {A, C} | Matches the preregistered text. A-Fix stays report-only, and its fuel result vs Control carries no confirmatory claim |
| (b) M6 | {A, A-Fix, C} | Holm m = 3, which is stricter for every member. Making A-Fix's fuel claim confirmatory amends the D7a "diagnostic" status of that one comparison. It does not make A-Fix promotion-eligible |

**CC recommendation:** (b), if you explicitly amend D7a for this purpose. It is the more conservative multiplicity choice, and it stops an A-Fix fuel result being quoted without correction. Either option is supported by the code (tested).

**Agreed in both options:**
- B is excluded: it is noncausal and can never enter the family (enforced in preflight and gates).
- A vs A-Fix and A-Fix vs C are diagnostic, reported separately.

**How Holm and BCa relate (verified in the frozen code):** for each member, the arm passes E1 only if all of the following hold:
1. its Holm-adjusted two-sided Wilcoxon p < 0.05 (the adjustment uses the full configured family);
2. its own iid BCa 95% two-sided interval has a lower bound > 0 L/origin. There is no multiplicity correction on the interval; none is invented;
3. its reliability gates (S1–S3, S4, S4-strict) pass.

The family size is fixed in advance and is never shrunk when an arm fails a safety gate (tested). If the BCa interval is degenerate, the frozen scipy call returns NaN, and the lower-bound condition then fails closed.

**Reported per member:** the Wilcoxon statistic, raw p, Holm-adjusted p, family size, mean and total litres saved, and the BCa bounds.

## 4. D4: Primary fuel metric. Status: **APPROVED (M6)** for the primary metric. Secondary analysis **BLOCKED** on one choice

**Primary metric (APPROVED, M6; identical to PROTOCOL §7 "Primary fuel = unadjusted (as historically preregistered)"):**
- **Metric:** realized diesel litres from `diesel_fuel` in the hourly telemetry.
- **Pairing:** per origin, Δ_o = Fuel(PC-Control, o) − Fuel(arm, o). Positive means the arm saved diesel.
- **Primary unit:** mean litres saved per origin. Total litres saved and % change vs Control are supporting measures.
- **Inference:** E1 as above.
- **Enforcement:** the config fixes `primary_fuel_metric: "unadjusted"`. Preflight and the gate code refuse any other value. The former option of making the adjusted metric primary was removed.

**Secondary SoC-parity-adjusted analysis:**
- **Correction to my earlier records:** DESIGN_AND_GATES G-c and CALIBRATION_AMBIGUITIES said the factor f was "defined in no repository document". **That was wrong.** PROTOCOL §7 defines the analysis:
  - SoC-parity-adjusted fuel = fuel + max(0, E_end,ctrl − E_end,arm)·(1/0.92)·f;
  - f ∈ {0.30, 0.75} L/kWh, both reported;
  - f is derived from `diesel.yaml` (5 L/h base + 0.25 L/kWh, giving 0.30 at 100 kW and 0.75 at 10 kW). I verified this.
- **E_end:** `e_after_wh` after hour 23 of each origin. Episodes reset daily.
- **Missing choice:** whether the max(0, ·) is applied **per origin** (recommended, because episodes are independent daily resets) or to the **aggregate** energy gap. With per-origin application, surpluses on one day cannot offset deficits on another. This is **RECOMMENDED, awaiting approval**. The config records `application: null` and `status: BLOCKED`. Preflight refuses until the status is `APPROVED` (per-origin) or explicitly `NOT_PREREGISTERED`.
- **Interpretation:** an arm that ends with less stored energy than Control is charged the diesel needed to make up the difference, at best and worst marginal efficiency.
- **Limits:** this is reported only. It never overrides a failed primary test or a failed reliability gate. No claim of SoC parity is made; the output reports the mean end-energy gap and the number of origins where the arm ends lower.
- **Tests:**
  - the primary metric equals the unadjusted saving and is unchanged by the secondary analysis;
  - the secondary values match the formula for both f values;
  - the secondary analysis is BLOCKED unless approved;
  - the primary metric cannot be switched.

---

## 5. Arm C calibration ambiguities A1–A6. Status of each: **RECOMMENDED, awaiting your approval**

These apply to every choice:
- Calibration rows are origins ≤ 2024-04-29 or ≥ 2024-09-02. The buffers 04-30 and 09-01 are excluded.
- `read_calibration_input` (new) reads only `forecast_start` and `timestamp`, aborts on any non-2024 row, and then parses value columns **only for calibration-window lines**. Evaluation-window and buffer values are never parsed (tested with poisoned values).
- Corrected geometry is used, as in A-Fix (sun at label − 1 h through `LabelCorrectedLocation`). Labels are unchanged, and the reserve elevation path is untouched.
- Nothing is selected using evaluation results.
- There is no silent fallback: an unsupported value or missing bin raises.

**Not part of A1–A6, and still PROPOSED under D5:** α = 0.10, the bin edges, the γ grid, and the 20 origin-day minimum. α = 0.10 means q is the residual quantile (actual − point) at α, so the lower bound is exceeded by roughly 90% of calibration hours in-sample.

### A1. Quantile estimator (`quantile_method`)
- **Ambiguity:** the protocol says "split-conformal residuals" and "q_α = empirical α-quantile of r in the bin", but gives no estimator.
- **Options:** `split_conformal_lower`, r₍k₎ with k = ⌊α(n+1)⌋; a numpy estimator such as `inverted_cdf` or `linear`.
- **Recommended:** **`split_conformal_lower`**. It matches the protocol's "split-conformal" and has finite-sample coverage under exchangeability. It is never above `inverted_cdf`, so it is more cautious for the reserve.
- **Rule:** sort the bin's residuals and take r₍k₎. If k < 1, raise InsufficientBinError.
- **Leakage:** none, because it uses calibration residuals only.
- **Reliability:** hours within an origin are correlated, so coverage is approximate. The protocol already requires post-run evaluation-window coverage as a diagnostic.
- **Tests:** n = 100 gives the 10th order statistic; the estimate is ≤ `inverted_cdf`; small n raises.

### A2. Bin boundary closure (`bin_boundary_rule`)
- **Ambiguity:** "0–5°, 5–15°, 15–30°, >30°" and "<0.2, 0.2–0.8, >0.8" leave shared edges ambiguous. Cloud cover is integer percent, so 20% and 80% occur (19 and 37 calibration rows).
- **Options:** left-closed or right-closed for both dimensions; a protocol-literal rule per dimension.
- **Recommended:** **protocol-literal, per dimension**:
  - **elevation `right_closed`:** (0,5], (5,15], (15,30], (30,90]. This honours ">30°", and elevation 0 is not daylight;
  - **cloud `closed_middle`** (new): [0,0.2), [0.2,0.8], (0.8,1.0]. This honours "<0.2" and ">0.8" literally.
- **Config:** `{"elevation": "right_closed", "cloud": "closed_middle"}`. `closed_middle` refuses anything other than 3 bins.
- **Leakage:** none.
- **Reliability:** it only places boundary values.
- **Tests:** every edge value is placed as stated; a 4-bin `closed_middle` raises; a missing per-dimension rule raises.

### A3. Merge direction (`insufficient_bin_policy`)
- **Ambiguity:** "merge into the neighbouring elevation bin" does not say which neighbour.
- **Geometry evidence** (pvlib only, no observations): the >30° bin occurs on only **19 of 222** calibration days (late April and early September). Every >30° cell therefore falls below 20 origin-days and must merge downward. The old `merge_higher_elevation` would always fail. The 0–5° bin can only merge upward.
- **Options:** `fail`; always lower; always higher; neighbour determined by position.
- **Recommended:** **`merge_single_neighbour_else_lower`**:
  - an edge group merges into its only neighbour (the protocol fixes this);
  - an interior group (5–15° or 15–30°) merges into the lower neighbour. This last part is a convention: no evidence favours either direction, and sparse interior cells are not expected given the day counts (153 and 95 days).
- **Rule:** merges repeat until every group reaches 20 origin-days. If a group spans all elevation bins and is still short, raise. Merges are recorded in the artifact.
- **Leakage:** none.
- **Reliability (important):** in May–August, >30° hours are common (up to 45°). Arm C's >30° quantile will come mostly from the pooled 15–30° data plus 19 spring/autumn days. That is a transfer risk the protocol already acknowledges ("calibration months are non-summer"). The post-run evaluation-window coverage diagnostic must be reported per bin.
- **Tests:** the top bin merges down; the bottom bin merges up; an interior bin merges lower; no remaining neighbour raises.

### A4. Definition of "origin-days" (`origin_day_definition`)
- **Ambiguity:** distinct origins vs distinct target calendar days.
- **Correction to my earlier note:** my earlier text said the two "differ near midnight". **That was wrong for this data:** every origin starts at 00:00 and its targets are 00:00–23:00 of the same day, so the two counts are identical.
- **Recommended:** **distinct `forecast_start` origins with at least one daylight hour in the bin.** It is the protocol's own word and matches the origin-level pairing.
- **Rule:** calibration now refuses origins that do not start at 00:00 (new check), which keeps the two definitions equal.
- **Leakage and reliability:** none.
- **Tests:** duplicate hours from the same origins do not add origin-days; a 06:00 origin is rejected.

### A5. Residual space (`residual_space`)
- **Ambiguity:** GHI (W/m²) vs PV power (W).
- **Evidence:**
  - the PV map is min(51·GHI, 60 kW), which is linear below GHI = 1,176 W/m²;
  - peak elevation at the site is 45° (21 June), so the clip practically never binds;
  - the protocol defines γ and the bins in GHI.
- **Recommended:** **`ghi_w_m2`**, with the lower bound converted through the frozen PV map. Below the clip it equals PV space exactly (tested).
- **Leakage and reliability:** none in practice.

### A6. γ tie rule (`gamma_tie_rule`)
- **Ambiguity:** how to break an exact tie for minimum MAE.
- **Recommended:** **`largest_gamma`**. Ties are not expected with real data. If one occurs, the largest γ gives the lowest point forecast, which is the more cautious planner input. The rule is deterministic.
- **Tests:** an exact tie selects 1.00.

(A7, the ~20-minute time-centring offset, is a noted convention. It is not one of the six and stays unchanged.)

---

## 6. What changed in code (hashes in `manifests/CODE.sha256`)

- **`scripts/gates_three_arm.py`:**
  - S4_point with strict pairing and fsum;
  - S4_strict reported separately, with metadata;
  - a vectorized, documented stationary bootstrap;
  - E1 Wilcoxon statistic and fixed family size;
  - primary fuel unadjusted only;
  - the secondary SoC-parity analysis, gated;
  - a secondary block-bootstrap CI for Δfuel;
  - S4 against Arm A, report-only.
- **`scripts/calibrate_arm_c.py`:**
  - the `closed_middle` rule and per-dimension rules;
  - the `merge_single_neighbour_else_lower` policy;
  - `read_calibration_input` (two-pass, never parses excluded rows);
  - a check that origins start at 00:00;
  - `main()` uses the new reader.
- **`scripts/preflight.py`:** the primary metric must be `unadjusted`; the secondary analysis must be APPROVED or NOT_PREREGISTERED; a recommended-but-undecided interval is flagged; every Arm C entry needs a recorded status.
- **`config/EXPERIMENT_CONFIG.json`:** statuses and values as above.
- **Tests:**
  - new `test_decision_resolution.py`;
  - real-config tests updated to the new state (they still assert refusal);
  - the test-only `approve_everything` fixture now uses the config's recommended values.
- **Unchanged:** `causal_nwp_physics.py`, the frozen modules, the inputs, and every file in `reports/source_prep/`.

## 7. Remaining unresolved choices (all block execution)

1. **D10:** choose (a) {A, C} or (b) {A, A-Fix, C}. If (b), explicitly amend D7a for A-Fix's fuel comparison.
2. **D6 interval:** approve `two_sided_95_upper` (recommended) or choose `one_sided_95_upper`.
3. **D4 secondary:** approve per-origin application (recommended), or mark the secondary analysis NOT_PREREGISTERED.
4. **Arm C A1–A6:** approve or change the six recommendations.
5. **D5:** approve α = 0.10, the bin edges, the γ grid and the 20 origin-day minimum.
6. **Other decisions:** D1, D3, D7 review outcome, D7a, D8 code review, D11 (Open-Meteo licence UNVERIFIED), and BUD (CONDITIONALLY APPROVED).
7. **Before calibration and execution:** run the tests in the device venv, freeze the config, regenerate the manifests and enter the freeze line, then sign the calibration authorization and later the execution authorization.

**Status: BLOCKED.**
