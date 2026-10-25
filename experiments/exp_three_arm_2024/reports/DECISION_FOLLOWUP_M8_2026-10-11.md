# Decision follow-up (M8): D6 interval, the D10/D7a wording conflict, D4 aggregation, Arm C and D5

Prepared 2026-10-11 by CC. This pass only records decisions. **No calibration, replay, training, simulation or solver call took place, and no observation or outcome value was read.**

**Authority:** M8 is message `cmsg_017TpQv3UrTPMkzn658LmXvXFnD828pU5nJWdGmJaPDLWY`, sent 2026-10-11 04:07:50 UTC by Puni (`user_01Dj2JKqyS22XoGCMZ8tUQAw`), the project lead. This report extends `reports/DECISION_RESOLUTION_M7_2026-10-11.md`.

**Unchanged:**
- `reports/source_prep/`, including PROTOCOL.md and the D7a addendum;
- every frozen module and input.

**Status preservation, checked by tests:**
- D2, D10, D4 (primary metric) and the D6 parameters keep their APPROVED status.
- No other status was changed without an explicit project-lead approval.

| Item | Status after M8 | Change |
|---|---|---|
| D2 | APPROVED | none |
| D6 | **APPROVED** (was PARTIALLY APPROVED) | M8 approves the two-sided 95% interval (97.5th percentile), with seed 42, 10-day blocks and 10,000 resamples. ΔU = arm − control and PASS iff the upper bound ≤ 0 are preserved |
| D10 | APPROVED, {A, C} | Not downgraded. Its condition ("subject to resolving the wording conflict") is tracked as the new **D10a** |
| **D10a** (new) | **CONFLICT — AMENDMENT PROPOSED, AWAITING REVIEW** | The documents contradict each other on C's diagnostic status (§1). D10a blocks execution. The amendment is in `reports/PROPOSED_AMENDMENT_D7a-1.md` |
| D4 | Primary APPROVED; secondary role approved; **application BLOCKED** | The protocol text and its aggregation semantics are now documented verbatim (§3) |
| A1–A6, A8 | PENDING (RECOMMENDED) | Unchanged, with full detail in §4 |
| D5 | PENDING | Two citations remain UNVERIFIED (§5) |
| D1, D3, D7, D7a, D8, D11, BUD | Unchanged | §6 |

---

## 1. D10 / D7a wording: exact passages and three separate questions

**Exact passages:**

| Source | Text |
|---|---|
| PROTOCOL.md §5, E1 | "**E1 (fuel):** Wilcoxon (Holm) adjusted p < 0.05 AND BCa 95% lower bound > 0 L/origin. Evaluated only if the safety gates pass." |
| PROTOCOL.md §7, "Statistics" | "E1 as defined (Holm over decision-bearing comparisons: A vs Control, C vs Control)." |
| PROTOCOL.md §7, "B" | "Gates computed and **reported, never decision-bearing.** … Any 40% claim needs a non-diagnostic arm passing all gates" |
| PROTOCOL.md §7, "Classes" | "**Diagnostic:** B, any classification of unmet hours. **Research-only candidate:** C passing S1–S4 + E1. **Promotion-eligible:** nothing from this experiment. Promotion would need a fresh holdout plus separate authorization" |
| D7a addendum §1, table | "\| **A-Fix** \| corrected: labels read as UTC+1 \| `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE` \|" … "\| C \| corrected (see §4) \| DIAGNOSTIC \|" |
| D7a addendum §1 | "A-Fix is a diagnostic comparison. It does not become the winner if it does better. Changing the official winner needs a separate governance decision (D7a item 7)." |
| D7a addendum §4 | "C should therefore be compared with A-Fix, not with A. Otherwise the comparison would mix two changes. The protocol's C-vs-A comparison becomes C-vs-A-Fix; A-vs-A-Fix isolates the timestamp fix." |

**(a) Inclusion in the confirmatory statistical family.**
- PROTOCOL §7 puts A vs Control and C vs Control in the Holm family and calls them "decision-bearing".
- The D7a addendum says nothing about E1 or Holm. Its words "Holm", "E1" and "decision-bearing" do not occur.
- **No contradiction.** The family {A, C} stands (D10), and A-Fix is not in it.
- **Implication worth noting:** PC-Control keeps the legacy geometry and C uses the corrected geometry. So C vs Control measures the timestamp fix and the calibration together. D7a §4 avoids that mix only for the diagnostic C-vs-A-Fix comparison.

**(b) Diagnostic-only status.**
- PROTOCOL §7 lists the diagnostic items as "B, any classification of unmet hours", and lists C separately as "Research-only candidate".
- The D7a addendum labels C `DIAGNOSTIC`.
- **These contradict each other.** The contradiction is material: under the D7a label, no arm could meet PROTOCOL's "non-diagnostic arm passing all gates" condition for a 40% claim.
- For A-Fix there is no conflict, because it did not exist when PROTOCOL was written. D7a defines it as diagnostic.

**(c) Promotion eligibility.**
- PROTOCOL: "Promotion-eligible: nothing from this experiment."
- D7a: A-Fix "NOT PROMOTION-ELIGIBLE", "does not become the winner".
- **Consistent.** Nothing in this experiment is promotion-eligible, C included (the runner sets `promotion_eligible: False` for every arm, and preflight enforces it).

**Outcome:**
- The three questions are not interchangeable, and only (b) is contradictory.
- Per M8, D10a is **left blocked**. The smallest amendment is proposed in `reports/PROPOSED_AMENDMENT_D7a-1.md`: change C's D7a result label from `DIAGNOSTIC` to `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE`, with nothing else changed.
- The runner label `LABEL_C` (`scripts/run_three_arm_2024.py:66`) still follows D7a as written, and will change only if the amendment is approved.
- D10a is in `preflight.EXECUTION_DECISIONS`, so execution refuses. Calibration is not affected.

**Tests:**
- `test_m8_d10a_blocks_execution_but_not_d10`;
- `test_m8_d7a_c_label_is_unchanged_until_amendment_approved`;
- `test_d10_real_config_is_the_protocol_family`;
- `test_d10_a_fix_is_diagnostic_only`.

## 2. D6: **APPROVED**

- **Rule:**
  - per origin, ΔU_o = U_arm,o − U_ctrl,o, in Wh (`gates_three_arm.py:118`);
  - the statistic is the mean over the 123 chronological origins;
  - Politis–Romano stationary bootstrap (`:122`), mean block 10 days, 10,000 resamples, `numpy.random.default_rng(42)`;
  - the upper endpoint is the 97.5th percentile (`STRICT_INTERVALS`, `:35`);
  - **PASS iff upper endpoint ≤ 0** (`:157`).
- S4-strict is reported separately from S4-point, and both must pass.
- E1 keeps the iid BCa (M6).
- **Config:** `S4_strict_interval: "two_sided_95_upper"`, with `S4_strict_interval_record` (APPROVED, M8). D6 status is APPROVED, with the M8 quote as evidence.
- **Tests:**
  - `test_d6_interval_seed_block_resamples_approved_and_used`;
  - `test_d6_delta_is_arm_minus_control`;
  - `test_d6_upper_bound_le_zero_is_the_non_regression_direction` (worse, better and tie cases);
  - `test_d6_two_sided_upper_endpoint_is_the_97_5th_percentile`.

## 3. D4: primary APPROVED; secondary application **BLOCKED**. Formula not changed

**Exact PROTOCOL §7 text** (row "SoC"). This is the only place in the protocol that defines the adjustment:

> Start 50% every origin. Terminal target fixed at 100 kWh, identical across arms, not optimized. **Primary** fuel = unadjusted (as historically preregistered). **Secondary** (report): SoC-parity-adjusted fuel = fuel + max(0, E_end,ctrl − E_end,arm)·(1/0.92)·f, with f ∈ {0.30, 0.75} L/kWh, the diesel's best/worst marginal efficiency from `diesel.yaml` (5 L/h base + 0.25 L/kWh at 100 kW and 10 kW). D4: whether the adjusted figure becomes decision-bearing

**Aggregation semantics, documented exactly:**

| Question | What the protocol says |
|---|---|
| Is `fuel` per origin or a total? | **Not stated.** No origin index, no Σ |
| Is `E_end` per origin or a total? | **Not stated.** Elsewhere the protocol says "end-of-episode SoC" is "Reported for every arm" (§5) and "Episodes reset daily" (§4); these describe episodes, not the formula |
| Where is the max(0, ·) applied? | Inside the formula, around the end-energy difference. **The level (origin or total) is not stated** |
| Denominator for % reductions | "PC-Control total fuel over the 123 origins" (§7, "Denominator") |
| Role | "Secondary (report)" (§7); D4 primary = unadjusted (M6, M8) |

**The two candidate readings:** both use the protocol formula unchanged; only the level at which it is applied differs. They are recorded in the config as `per_origin_form_proposed` and `aggregate_form_alternative`, next to the verbatim `protocol_text_verbatim`. The earlier config field `formula`, which wrote per-origin subscripts into the protocol formula, was removed, because it presented an interpretation as protocol text.
- **Per-origin:** Σ_o [fuel_arm,o + max(0, E_end,ctrl,o − E_end,arm,o)·(1/0.92)·f]
- **Aggregate:** Σ_o fuel_arm,o + max(0, Σ_o E_end,ctrl,o − Σ_o E_end,arm,o)·(1/0.92)·f

The comparison of the two is in the M7 report §3. The recommendation remains **per-origin** (daily 50% reset; it never favours the arm; it gives a per-origin series). **It is not finalized.**

**Implementation:** `gates_three_arm.secondary_soc_parity` (`:166`, per-origin at `:174`) runs only if the status is APPROVED with `application: per_origin`, and refuses `aggregate`. The output reports `protocol_text` and `applied_form` separately.

**Tests:**
- `test_m8_protocol_soc_text_is_copied_verbatim_from_protocol`: the config text is a substring of PROTOCOL.md.
- `test_d4_secondary_still_blocked_in_real_config_and_formula_unchanged`.
- `test_d4_per_origin_does_not_net_surplus_against_deficit`.
- `test_primary_fuel_is_unadjusted_and_secondary_is_separate`.

## 4. Arm C: A1–A6 and A8 (all **PENDING**, RECOMMENDED)

Implementation lines refer to `scripts/calibrate_arm_c.py` unless stated otherwise.

| ID | Exact proposed value (config `arm_c_method`) | Protocol basis (PROTOCOL.md §4) | Implementation | Evidence | Synthetic tests |
|---|---|---|---|---|---|
| A1 | `quantile_method: "split_conformal_lower"`: q = r₍k₎, k = ⌊α(n+1)⌋; raise if k < 1 | "split-conformal residuals … q_α = empirical α-quantile of r in the bin" | `alpha_quantile` :261 | Finite-sample conformal rule; ≤ `inverted_cdf`, so more cautious; n ≥ 20 in any accepted bin, so k ≥ 2 at α = 0.10 | `test_a1_split_conformal_rule` |
| A2 | `bin_boundary_rule: {"elevation": "right_closed", "cloud": "closed_middle"}` | "0–5°, 5–15°, 15–30°, >30°"; "<0.2, 0.2–0.8, >0.8" | `assign_bin` :236 (closed_middle :243) | Integer-percent cloud: 19 calibration rows at 20% and 37 at 80% (forecast input, earlier pass) | `test_a2_protocol_literal_bins`, `test_a2_integer_percent_edges_fall_in_the_middle_cloud_bin` |
| A3 | `insufficient_bin_policy: "merge_single_neighbour_else_lower"` | "Bins with fewer than 20 origin-days merge into the neighbouring elevation bin" | merge loop in `quantile_table`, :348 | Geometry only (below) | `test_a3_top_bin_merges_into_its_only_neighbour`, `test_a3_bottom_bin_merges_upward_and_interior_merges_lower`, `test_a3_no_neighbour_left_fails_closed`, `test_a3_sparse_top_bin_pools_with_15_30_and_is_used_for_high_sun_hours` |
| A4 | `origin_day_definition: "distinct forecast_start (00:00) origins with >= 1 daylight hour in the bin"` | "origin-days" | `origin_days` :323; 00:00 check :128 | All origins start 00:00, so origin-day = target calendar day | `test_a4_origin_day_counts_distinct_origins_and_requires_midnight_origins` |
| A5 | `residual_space: "ghi_w_m2"` | γ, bins and residuals stated on GHI | `residuals` :275; run time `run_three_arm_2024.py:278-282`; diagnostic `residual_space_diagnostic` :286 | Max clear-sky GHI 624 (calibration) / 724 W/m² (evaluation), below the PV clip at 1,176.5 W/m² | `test_a5_ghi_residual_space_equals_pv_space_below_clip`, `test_a5_diagnostic_zero_below_clip_and_counts_clipped_hours`, `test_a5_diagnostic_is_in_the_artifact` |
| A6 | `gamma_tie_rule: "largest_gamma"` | "minimizing daylight MAE" (ties unstated) | `fit_gamma` :208, tie :218-221 | Largest γ gives the lowest point forecast, the cautious planner input; deterministic | `test_a6_tie_rule_largest_gamma` |
| A8 | `gamma_objective.daylight_rule: "elevation>0 and clearsky_ghi>0"` | "daylight MAE" (undefined) | `attach_geometry` :190; run time `lower_bound` :382 | The same rule at calibration and at run time; night gives ŝ = 0 | `test_a8_daylight_rule_is_the_same_in_calibration_and_at_run_time`, `test_a8_recorded_as_recommendation_not_protocol` |

**A3: how the sparse >30° bin and the merge rule affect calibration.** Everything below uses only deterministic sun position (pvlib), with no outcome data.

1. Above 30°, the calibration window has 19 origin-days: late April and early September, with a maximum elevation of 36.3°. Within any cloud class there are at most 19, which is below the protocol minimum of 20. **Every >30° cell must therefore merge.**
2. The >30° bin is the top bin, so its only neighbour is 15–30°. Merging down is forced by the protocol's own edges; it is not a free choice:
   - `merge_higher_elevation` has no target, and `fail` would stop calibration;
   - neither is viable with these edges.
   - The rule's only real convention is the interior direction (5–15° or 15–30° merging down), and whether an interior merge happens depends on the calibration cloud mix. That is found only at calibration time and recorded in the artifact's `merges`.
3. **Effect on calibration:**
   - each >30° cell is pooled with the 15–30° cell of the same cloud class (95 origin-days);
   - the pooled residual quantile is dominated by 15–30° hours;
   - all four cells in a pooled group share one q_α (test: `top["q_alpha"] == mid["q_alpha"]`, n_hours = 59 in the synthetic case).
4. **Effect at run time:**
   - above-30° hours occur on 122 of 123 evaluation days (maximum 45.0°);
   - each looks up its (>30°, cloud) cell and gets the pooled quantile (test: a 40° hour uses the pooled q).
   - So the high-sun reserve bound is calibrated mainly on lower-sun spring and autumn hours. Whether that makes the bound more or less cautious than a bin-specific one cannot be known without outcomes, and it is not assessed here.
   - PROTOCOL §4 already requires evaluation-window coverage per bin as a post-run diagnostic, which will show it.
5. **Choosing the rule:** no evaluation outcome was used. The facts used are sun geometry and the protocol text.

## 5. D5: protocol values and the two unverified citations

| Value | Exact protocol text (PROTOCOL.md §4) | Config | Status |
|---|---|---|---|
| α | "**α = 0.10 proposed; needs approval (D5).**" | `alpha.value = 0.1` | PROPOSED |
| Elevation bins | "binned by solar elevation (0–5°, 5–15°, 15–30°, >30°)" | `[0, 5, 15, 30, 90]` (90 closes ">30°") | PROPOSED |
| Cloud bins | "× cloud fraction (<0.2, 0.2–0.8, >0.8)" | `[0, 0.2, 0.8, 1.0]` (1.0 closes ">0.8") | PROPOSED |
| Minimum | "Bins with fewer than 20 origin-days merge into the neighbouring elevation bin (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:27` uses 20 as the minimum subgroup)." | `min_origin_days_per_bin.value = 20` | PROPOSED; **citation UNVERIFIED** |
| γ grid and objective | "**γ̂:** grid [0.10, 1.00] step 0.01, minimizing daylight MAE (the existing protocol's criterion, `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:19-21`)." | grid 0.1–1.0 step 0.01; `daylight_MAE_W_m2` | PROPOSED; **citation UNVERIFIED** |

**The two unverified citations.** Both point to `experiments/stage4_planner_cf_consistency_2025/cloud_to_ghi_nonlinear_experiment_20261010/CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md`.
- **Listing:** a file-name listing of that folder shows two files, that protocol and `run_cloud_to_ghi_validation.py`. Neither was opened.
- **Verification attempt from non-outcome files:** I searched every non-2025 `.md`, `.py`, `.yaml` and `.txt` file in the staged repository copy (51 files: `system/`, `clear_sky/`, `experiments/candidate_s_sw_campaign_2024/` and others; 2025 folders and `.venv` excluded). The search was for "CLOUD_TO_GHI", "cloud_to_ghi", "minimum subgroup", "min_subgroup", "daylight MAE" and "daylight_mae", and printed file names only. **There were no matches.**
- The staged copy does not include `~/POLARIS_Knowledge` or the stage3–7 folders, so those were not searched.

**Result:** neither requirement can be verified from the non-outcome files available. Both stay **UNVERIFIED**, recorded as `citation_status` in the config. The values are still the protocol's own (PROTOCOL §4 states them directly), so nothing is invented. Only the claim that they come from the earlier protocol is unverified.

**Authorized source needed.** One of the following:
- (i) permission to open only `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md`, after you confirm it holds no 2025 outcome values;
- (ii) a copy of the relevant lines placed outside the campaign folder;
- (iii) a statement that PROTOCOL §4's values stand on their own and the citations are not needed.

**Also noted:** PROTOCOL §7 cites the same file (`:22`, "documented lag-4 residual autocorrelation") to justify the 10-day block. D6 is approved on your decision, but that supporting citation is equally unverified.

## 6. Other decisions: governing text and evidence in the package (all unchanged)

| ID | Governing text in the package | Evidence present | Missing | Status |
|---|---|---|---|---|
| D1 | PROTOCOL §10 item 1; §2 | §2 eligibility; prior use recorded (DESIGN_AND_GATES §6) | Your explicit approval | PENDING |
| D3 | PROTOCOL §10 item 3; §4 "Rule D **off**" | Runner and preflight enforce off | Your explicit approval | PENDING |
| D7 | M3 text in DECISIONS_LOG; `TIMESTAMP_VERIFICATION.md` | Verification report and tests | Review outcome (`TIMESTAMP_VERIFICATION.md:5`: "PENDING") | PENDING |
| D7a | M4 items 1–8; `reports/source_prep/PROTOCOL_ADDENDUM_D7a.md`; `reports/D7A_REVIEW.md` | Parity tests; item-by-item review | Your approval; now also depends on D10a | PENDING |
| D8 | PROTOCOL §10 item 8 | Code, 311 synthetic tests in a sandbox | Code review; test run in the device venv | PENDING |
| D11 | DATA_PROVENANCE §4 | SITES CC BY 4.0 (file header) | **Archived Open-Meteo licence evidence** | PENDING |
| BUD | M5 ("provisionally approved"); COMPUTE_BUDGET | `--audit-budget` reconciles at 14,760 | Your final approval | CONDITIONALLY APPROVED |

## 7. Still requiring your decision

1. **D10a:** accept, change or reject `reports/PROPOSED_AMENDMENT_D7a-1.md`.
2. **D4 secondary:** approve per-origin application, or declare the analysis NOT_PREREGISTERED.
3. **A1–A6, A8:** approve or change each.
4. **D5:** approve the protocol values, and provide an authorized source for the two citations (or waive them).
5. **D1, D3, D7 (review outcome), D7a, D8, D11 (licence evidence), BUD.**
6. **Signatures:** the calibration and execution authorizations are separate. Both are unsigned.

**Status: BLOCKED.**
