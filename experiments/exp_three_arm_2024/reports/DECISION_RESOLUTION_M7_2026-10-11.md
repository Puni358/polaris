# Decision Resolution, second pass (M7): D10, D6, D4, Arm C A1–A6/A8 and D5

Prepared 2026-10-11 by CC. This pass only records decisions. **No experiment execution, real-data calibration, forecast replay, training, simulation or MILP solve took place.** No observation or outcome value was read. The only new numbers come from solar geometry: pvlib Ineichen clear sky at the site coordinates in `causal_nwp_physics.py`, with no data file read.

This pass builds on `reports/DECISION_RESOLUTION_2026-10-11.md` (M6) and supersedes it where the two differ. The historical files in `reports/source_prep/` were not modified, and D7a was not amended.

**Authority:** M7 is message `cmsg_017TpQv3UrTPMkzn658LmXvX79mGjYAvoUtydgZmnsGAz9`, sent 2026-10-11 03:44:33 UTC by Puni (`user_01Dj2JKqyS22XoGCMZ8tUQAw`), the confirmed project lead (M6).

| Item | Status after M7 | Why |
|---|---|---|
| D10, E1 Holm family | **APPROVED: {A, C}** | M7: "Preserve the existing confirmatory Holm family {A, C}; keep A-Fix diagnostic only." This is identical to PROTOCOL §7 |
| D6, seed 42, 10-day block, 10,000 resamples | **APPROVED** | M7 confirms seed 42 "explicitly recorded as my decision" |
| D6, interval | **PROPOSED by the project lead. Awaiting your approval** | M7 says "Propose the two-sided 95% … interval". The sign check M7 asked for passed (§2) |
| D4, primary metric unadjusted | APPROVED (M6), unchanged | — |
| D4, secondary: per-origin vs aggregate | **RECOMMENDED per-origin. Awaiting your approval** | M7 asked for a comparison and a recommendation (§3) |
| A1–A6, A8 | **RECOMMENDED. Awaiting your approval** | Evidence and tests are in §4. A8 (the daylight definition) is newly identified: PROTOCOL.md does not define "daylight" |
| D5 values (α, edges, γ grid, 20 origin-days, MAE objective) | **PROPOSED (as stated in PROTOCOL §4). D5 is PENDING** | Nothing was invented. Each value is traced to PROTOCOL §4 |
| D1, D3, D7, D7a, D8, D11, BUD | Unchanged: PENDING, or CONDITIONALLY APPROVED for BUD | M7 item 5 |

Package status: **BLOCKED.**

---

## 1. D10: E1 Holm family. **APPROVED, {A, C} vs PC-Control**

- **Rule:** the E1 family is {A vs PC-Control, C vs PC-Control}, so Holm m = 2. Config: `gates.E1_holm_family = ["A", "C"]`.
- **Diagnostic only, never in the family:** A-Fix vs Control, A vs A-Fix, and A-Fix vs C. B is noncausal and never enters.
- **What did not change:** the E1 test itself. It is a two-sided paired Wilcoxon, Holm-adjusted p < 0.05, AND the arm's own iid BCa 95% lower bound > 0 L/origin, and it counts only if S1–S3, S4 and S4-strict pass. The family size is fixed at 2 and is never shrunk.
- **Superseded:** the M6 proposal {A, A-Fix, C} was not adopted.

**Protocol consistency check (M7: "Do not amend D7a unless you find a protocol conflict that requires escalation"):**
- PROTOCOL §7 says "Holm over decision-bearing comparisons: A vs Control, C vs Control". This matches.
- PROTOCOL_ADDENDUM_D7a §1 says "A-Fix is a diagnostic comparison". This matches.
- **One wording difference was found and is not escalated.** The D7a addendum's table gives C the result label `DIAGNOSTIC`, while PROTOCOL §7 makes C vs Control confirmatory.
  - My reading: the addendum's column is a result label about promotion. PROTOCOL §7 "Classes" already says "Promotion-eligible: nothing from this experiment", and calls C passing S1–S4 + E1 a "research-only candidate".
  - On that reading, C in the E1 family and C labelled "not promotion-eligible" are consistent, so no amendment is needed.
  - **Please confirm this reading.** It is listed in §6.

**Tests (`tests/test_decision_resolution_m7.py`):**
- the real config holds exactly {A, C}, and preflight raises no D10 failure;
- A-Fix gets no E1 entry, the family size is 2, and A-Fix's comparisons appear under `diagnostic_comparisons`.

The existing tests still reject B and invalid families, and still show the family is never shrunk.

## 2. D6: strict S4. **Seed, block and resamples APPROVED; interval PROPOSED**

**Sign convention, verified in code:**
- `gates_three_arm.py:118` computes per origin ΔU_o = U_arm,o − U_ctrl,o, in Wh. **Positive means the arm left more load unmet, so the arm is worse.**
- The statistic is the mean of ΔU_o over the 123 chronological origins.
- `gates_three_arm.py:157`: PASS iff the upper bound ≤ 0.
- So "upper bound ≤ 0" means that even at the pessimistic end of the interval, the arm's mean unmet energy is no higher than Control's. That is the non-regression direction S4 requires, so the criterion is correct.
- Exact ties: identical unmet energy gives all-zero resampled means, so the upper bound is 0 and the arm passes. This is consistent with S4's "ties pass".
- **Do not confuse it with fuel**, which has the opposite orientation: Δfuel_o = Fuel_ctrl − Fuel_arm, where positive means saving. The two orientations are each tested.

**Proposed interval:**
- `two_sided_95_upper`: the 97.5th percentile of the 10,000 stationary-bootstrap means (`STRICT_INTERVALS`).
- Requiring that upper endpoint ≤ 0 is a one-sided check at the 2.5% level with a zero margin.
- It matches E1's two-sided BCa 95%.
- It is stricter than `one_sided_95_upper` (95th percentile).
- In the config it is recorded as `S4_strict_interval_proposal` with status `PROPOSED — AWAITING PROJECT-LEAD APPROVAL`. `S4_strict_interval` stays `null`, so preflight still refuses.

**Approved parameters:**
- 10-day mean block (= 10 consecutive daily origins);
- 10,000 resamples;
- seed 42 (`numpy.random.default_rng(42)`), now explicitly the project lead's decision (M7);
- E1 keeps the iid BCa (M6).

**Tests:**
- ΔU is arm − control;
- arm worse on every origin → upper bound > 0 → FAIL;
- arm better → upper bound < 0 → PASS;
- identical → upper bound = 0 → PASS;
- the upper endpoint equals the 97.5th percentile of the documented bootstrap;
- the real config shows the interval as proposed, not decided.

## 3. D4: SoC-parity secondary analysis. **Per-origin RECOMMENDED, awaiting approval. Formula unchanged**

**Exact existing formula (PROTOCOL.md §7, row "SoC"), copied verbatim:**

> SoC-parity-adjusted fuel = fuel + max(0, E_end,ctrl − E_end,arm)·(1/0.92)·f, with f ∈ {0.30, 0.75} L/kWh, the diesel's best/worst marginal efficiency from `diesel.yaml` (5 L/h base + 0.25 L/kWh at 100 kW and 10 kW). D4: whether the adjusted figure becomes decision-bearing

**Terms** (each from the protocol or the config, none new):
- **fuel:** the arm's realized diesel, in litres (`diesel_fuel`).
- **E_end:** stored energy after hour 23 (`e_after_wh`), in kWh.
- **0.92:** the battery efficiency in `battery.yaml` (`charge_efficiency` and `discharge_efficiency` are both 0.92; the protocol does not say which, and they are equal).
- **f:** 0.25 + 5/P L/kWh. At P = 100 kW that is 0.30; at P = 10 kW it is 0.75.
- **Role:** reported only (M6); never decision-bearing.

**The two readings.** Write g_o = E_end,ctrl,o − E_end,arm,o and k = f/0.92.

| | Per-origin | Aggregate |
|---|---|---|
| Adjusted total | Σ_o [fuel_arm,o + k·max(0, g_o)] | Σ_o fuel_arm,o + k·max(0, Σ_o g_o) |
| Relationship | Penalty ≥ aggregate penalty, always, because Σ max(0, g_o) ≥ max(0, Σ g_o). Equal when no origin's sign differs from the total's | Never larger than per-origin |
| Physical meaning | Matches the protocol's episode structure: every origin restarts at 50% SoC (PROTOCOL §4, §7), so energy left at the end of one day cannot repay a deficit on another | Lets a surplus on day j cancel a deficit on day i, although the reset discards that surplus |
| Paired statistics | Gives an adjusted saving per origin, so the same per-origin summaries apply (mean L/origin; any interval) | Gives one total only. A per-origin series would need an allocation rule the protocol does not provide |
| Weakness | Day-to-day noise in end energy is penalized even with zero systematic deficit. Illustration, not data: with zero-mean gaps of standard deviation σ, the expected penalty is about 0.40·σ·k per origin | Hides systematic per-day deficits when they are offset by surplus days |
| Direction | Never more favourable to the arm than aggregate (conservative) | More favourable to the arm |

**Recommendation: per-origin.** It is the reading consistent with the daily reset, it gives a per-origin series, and it is the conservative one. Its noise penalty is visible, because the output already reports the mean gap and the number of origins where the arm ends lower. This is CC's recommendation and needs your approval. The alternative is to mark the secondary analysis `NOT_PREREGISTERED`.

**State:**
- The config holds `application: null`, `application_recommendation: per_origin` and status BLOCKED.
- The gate code computes only the per-origin version when the analysis is approved, and refuses `aggregate`. Implementing aggregate would need a fresh decision.

**Tests:**
- surplus on even origins does not cancel the deficit on odd ones: an aggregate gap of 0 still yields a per-origin penalty of 15 × 10 kWh × f/0.92, for both f values;
- `aggregate` is refused;
- the real config is still blocked, with the formula and f values unchanged.

## 4. Arm C: A1–A6, A8 and D5, checked against the protocol, inputs and implementation

**Calibration input and leakage controls (these apply to every choice):**
- **Input:** the 2024 weather file in `config.paths.weather`. Only the columns `forecast_start`, `horizon_hour`, `timestamp`, `fc_cloud_cover` and `actual_SW_IN` are used (`REQUIRED_COLUMNS`, `calibrate_arm_c.py:48`).
- **Calibration rows:** origins ≤ 2024-04-29 or ≥ 2024-09-02 (D1). The buffers on 04-30 and 09-01 are excluded.
- **Leakage controls in code:**
  1. `read_calibration_input` first parses only `forecast_start` and `timestamp`, and aborts on any non-2024 row. Value columns are parsed only on calibration lines, so evaluation-window values are never parsed (tested with poisoned values).
  2. `assert_calibration_isolation` re-checks after selection.
  3. Origins must start at 00:00.
  4. `main()` refuses before opening any file unless preflight passes, which includes a signed calibration authorization (tested).
  5. Nothing is selected using evaluation results or diesel.
- **Residual risk:** the calibration months are non-summer. This transfer risk is acknowledged in PROTOCOL §4 and is quantified under A3.

**Geometry evidence** (pvlib Ineichen, label − 1 h as in A-Fix; no observations):

| Window | Max elevation | Days with elevation > 30° | Max clear-sky GHI |
|---|---|---|---|
| Calibration | 36.3° | 19 of 222 | 624 W/m² |
| Evaluation | 45.0° | 122 of 123 | 724 W/m² |

The PV map is min(51·GHI, 60 kW), so it clips at 1,176.5 W/m².

| ID | Proposed value | Protocol basis | Evidence | Leakage risk | Tests |
|---|---|---|---|---|---|
| **A1** quantile | `split_conformal_lower`: r₍k₎, k = ⌊α(n+1)⌋; raise if k < 1 | §4 "split-conformal residuals … q_α = empirical α-quantile" | Finite-sample rule; never above `inverted_cdf`, so more cautious. With ≥ 20 origin-days per bin, n ≥ 20 and k ≥ 2 | None (calibration residuals only). Coverage is approximate, because hours within an origin are correlated | 10th order statistic at n = 100; ≤ `inverted_cdf`; small n raises |
| **A2** bin edges | elevation `right_closed`: (0,5], (5,15], (15,30], (30,90]; cloud `closed_middle`: [0,0.2), [0.2,0.8], (0.8,1] | §4 "0–5°, 5–15°, 15–30°, >30°", "<0.2, 0.2–0.8, >0.8" | Cloud cover is integer percent: 19 calibration rows at exactly 20% and 37 at exactly 80% (checked on calibration-window forecast inputs in the previous pass). Elevation is continuous, so edge hits have measure zero, and 0° is not daylight | None | 19%, 20%, 80%, 81% → bins 0, 1, 1, 2; every edge placed as stated; a 4-bin `closed_middle` raises |
| **A3** sparse bins | `merge_single_neighbour_else_lower` | §4 "merge into the neighbouring elevation bin" (direction unstated) | >30° has 19 calibration days, below 20 in every cloud column, so it always merges down. 0–5° can only merge up. The interior direction is a convention. **Transfer risk:** >30° hours occur on 122 of 123 evaluation days, so their quantile comes mostly from pooled 15–30° spring/autumn data | None. Merges never use evaluation data or a global quantile, and are recorded in the artifact. The post-run per-bin coverage diagnostic (PROTOCOL §4) must be read with this in mind | top bin merges down; bottom merges up; interior merges lower; no neighbour raises |
| **A4** origin-days | distinct 00:00 `forecast_start` with ≥ 1 daylight hour in the bin | §4 "origin-days" | For 00:00 origins, origin-days and target calendar days are identical (enforced) | None | duplicates do not add origin-days; a 06:00 origin is rejected |
| **A5** residual space | `ghi_w_m2`, with the bound converted through the frozen PV map | §4 defines γ, the bins and the residuals on GHI | Point ≤ clear sky ≤ 624 (calibration) and 724 W/m² (evaluation), both below the 1,176.5 W/m² clip. So the point forecast and lower bound never clip, and the two spaces agree unless a calibration hour has actual GHI > 1,176.5 W/m² (about 1.9× the calibration clear-sky maximum). **New:** the artifact records `residual_space_diagnostic.n_hours_pv_map_nonlinear`, computed at calibration time, so whether A5 mattered is on record | None | GHI and PV spaces are equal below the clip; the diagnostic counts 0, or 1 for a 1,300 W/m² hour; the diagnostic is present in the artifact |
| **A6** γ ties | `largest_gamma` | §4 "minimizing daylight MAE" (ties unstated) | Ties are not expected with real data. If one occurs, the largest γ gives the lowest point forecast, which is the cautious planner input | None | an exact tie selects 1.00 |
| **A8** daylight (new) | elevation > 0° and clear-sky GHI > 0 | §4 "daylight MAE" (undefined) | The same rule is used in calibration (`attach_geometry`) and at run time (`lower_bound`), so night hours get ŝ = 0 as the protocol requires | None | calibration and run-time daylight agree at edge cases (elevation 0, clear sky 0) |

**D5 values.** Each is traced to the protocol, kept as PROPOSED, and none is invented:

| Value | Source | Note |
|---|---|---|
| α = 0.10 | PROTOCOL §4: "α = 0.10 proposed; needs approval (D5)" | — |
| Elevation edges 0/5/15/30/90° | PROTOCOL §4 | 90° is the physical maximum that closes ">30°"; it is not a new value |
| Cloud edges 0/0.2/0.8/1.0 | PROTOCOL §4 | 1.0 is the physical maximum that closes ">0.8" |
| Minimum 20 origin-days | PROTOCOL §4, citing `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:27` | **Citation not verified**: that file is in `experiments/stage4_planner_cf_consistency_2025/…` and was not opened under the quarantine rule |
| γ grid 0.10–1.00, step 0.01 (91 values) | PROTOCOL §4 | — |
| Objective: daylight MAE | PROTOCOL §4, citing the same file `:19-21` | Citation not verified, for the same reason. The daylight definition is A8 |

## 5. Decisions that remain open (unchanged by M7)

- **D1:** evaluation and calibration windows. PENDING.
- **D3:** Rule D off. PENDING.
- **D7:** the timestamp verification review outcome. PENDING.
- **D7a:** PENDING. Not amended.
- **D8:** code review and the device-venv test run. PENDING.
- **D11:** the Open-Meteo licence stays **UNVERIFIED**. No archived licence evidence for the exact data used has been identified, and no search was repeated.
- **BUD:** 14,760 solves, CONDITIONALLY APPROVED.

## 6. Approvals still needed from the project lead

1. **D6 interval:** approve `two_sided_95_upper` (your proposal).
2. **D4 secondary:** approve per-origin application, or declare it `NOT_PREREGISTERED`.
3. **A1–A6 and A8:** approve or change each.
4. **D5:** approve α = 0.10, the edges, the γ grid, the 20 origin-day minimum and the MAE objective.
5. **D10 wording:** confirm that the D7a addendum's `DIAGNOSTIC` label for C means "not promotion-eligible" and does not conflict with C being in the E1 family.
6. **D1, D3, D7, D7a, D8, D11, BUD**, as listed in §5.
7. **Signatures, kept separate:**
   - The **calibration authorization** requires D1, D5, D7, D7a, D8 and D11 to be APPROVED (`preflight.CALIBRATION_DECISIONS`), plus a frozen config, the PREREGISTRATION freeze line and a signed calibration record.
   - The **execution authorization** additionally requires D2, D3, D4, D6, D10 and BUD (`preflight.EXECUTION_DECISIONS`), a validated calibration artifact and a separate signed execution record.
   - Both records are unsigned.

**Status: BLOCKED.**
