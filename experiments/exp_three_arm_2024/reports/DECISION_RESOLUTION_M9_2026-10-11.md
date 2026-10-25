# Decision resolution M9 (2026-10-11): technical PM pass

**Brief.** M9, `cmsg_017TpQv3UrTPMkzn658LmXvX2WPEGQjqxQQ7wSucS9sxg4` (2026-10-11T04:29:38Z, Puni, project lead): pending technical decisions are delegated to CC as technical project manager, governance lead and independent reviewer.

**Current status: `READY FOR CALIBRATION AUTHORIZATION`** (see the follow-up section at the end). **Status at the time of the M9 pass, kept as written: `BLOCKED`.** Three things still stand between the package and calibration:
1. D8 is only conditionally approved, because the device-venv test run has not been done.
2. The configuration is not frozen.
3. The calibration authorization is unsigned.

**Nothing was executed.** No calibration, forecast replay, training, real-data simulation, MILP or solver call, and no protected or 2025 file was opened. All code checks are synthetic, in a sandbox, with every solver interface mocked to fail.

## Classifications used

| Class | Meaning here | Passes preflight? |
|---|---|---|
| APPROVED | Explicit project-lead approval (M5–M8) | Yes |
| APPROVED BY EXISTING AUTHORITY | Covered by a project-lead statement already on record. Must name it in `authority` | Yes |
| RESOLVED BY DELEGATED TECHNICAL AUTHORITY | Decided by CC under the M9 delegation. Must name it in `authority` | Yes |
| CONDITIONALLY APPROVED | Decided, but an objective condition is still open | No |
| BLOCKED — EVIDENCE REQUIRED | Cannot be decided on the evidence available | No (D11-PUB is outside preflight) |
| REQUIRES PROJECT-LEAD AUTHORIZATION | Only the project lead can do it (signatures) | No |

`preflight.PASSING_STATUSES` encodes the first three. The two non-explicit statuses fail unless an `authority` is named (`preflight.status_failure`). The earlier statuses were not rewritten as approvals. Delegated entries carry the M9 authority and the date, and DECISIONS_LOG keeps the history through M8.

## Approvals preserved and not reopened

| ID | Kept exactly |
|---|---|
| D2 | S4: U(arm) ≤ U(PC-Control) over paired cells; ties pass; not evaluable = fail |
| D4 primary | Unadjusted realized litres; saving = control − arm |
| D6 | Seed 42; stationary bootstrap; 10-day mean blocks; 10,000 resamples; two-sided 95%; upper endpoint = 97.5th percentile; ΔU = arm − control; PASS iff upper ≤ 0 |
| D10 | E1 Holm family {A, C} vs PC-Control, m = 2; A-Fix diagnostic |

`test_project_lead_approvals_are_unchanged` checks these values and that none of them was relabelled as delegated.

## Decisions

### D10a: Arm C classification. RESOLVED BY DELEGATED TECHNICAL AUTHORITY

PROTOCOL.md §7 "Classes" says: "Research-only candidate: C passing S1–S4 + E1". Row B says: "Any 40% claim needs a non-diagnostic arm passing all gates". The D7a §1 cell "C | … | DIAGNOSTIC" contradicts the first passage and makes the second unsatisfiable. The D7a addendum gives no reason for that label: its §4 concerns C's geometry and comparison partner.

**Resolution:** the M8 proposal is adopted as `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`, a new versioned file. `reports/source_prep/` is unchanged, and the proposal file keeps its text, with a status line appended.

**Code change:** `LABEL_C = "RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)"`.

**Eligibility after the amendment:**
- B is a noncausal perfect-solar diagnostic and is never eligible.
- A-Fix is a geometry-fix diagnostic and is not promotion-eligible.
- C is a research-only candidate and is not promotion-eligible.
- Nothing from this experiment is promotion-eligible. No result from it alone is independently validated, and none is proof of 40%.

### D4 secondary: SoC-parity application. RESOLVED BY DELEGATED TECHNICAL AUTHORITY (per origin)

The formula text is unchanged and still verbatim from PROTOCOL §7. Its aggregation semantics are still recorded as "NOT STATED".

**Decision:** apply the formula per origin and sum the results: Σ_o [fuel_arm,o + max(0, E_end,ctrl,o − E_end,arm,o)·(1/0.92)·f]. This is recorded as a delegated clarification made before any evaluation run, not as original preregistration.

**Reasons:**
- **Fairness and daily resets.** Every origin is an independent 24 h episode that restarts at 50% SoC (`make_initial_state`). A deficit at the end of one day cannot be repaid by a surplus on another, because the surplus is discarded at the reset. The aggregate form would net such deficits away.
- **Comparability.** Per-origin pairing matches the E1 deltas.
- **Caution.** The per-origin penalty is always at least the aggregate penalty, so this is the more cautious reading.

**Limitations, recorded in the config and printed in the gate output:**
- The form is asymmetric: the arm gets no credit when it ends higher, so it penalizes noise and is biased against arms.
- Both f values (0.30 and 0.75) are reported. Neither is chosen.
- Daily resets mean the adjustment does not represent multi-day operation.
- It stays secondary and is never decision-bearing.

### Arm C method A1–A6 and A8. RESOLVED BY DELEGATED TECHNICAL AUTHORITY, each verified

The values are unchanged from M8. Each config entry now carries `basis`, which says whether the value is protocol-stated or a clarification.

| Item | Value | Basis | Verified against |
|---|---|---|---|
| A1 quantile method | split-conformal lower: r_(k), k = ⌊α(n+1)⌋ | Clarifies PROTOCOL "split-conformal … empirical α-quantile" | `calibrate_arm_c.alpha_quantile`; tests in `test_calibration_arm_c.py` |
| A2 bin boundaries | elevation right-closed; cloud [0, 0.2), [0.2, 0.8], (0.8, 1] | Clarifies PROTOCOL "<0.2, 0.2–0.8, >0.8" | `assign_bin` closed_middle; `test_a2_protocol_literal_bins`, `test_a2_integer_percent_edges_fall_in_the_middle_cloud_bin` |
| A3 insufficient bin | merge with the single neighbour, otherwise the lower elevation bin | Clarifies PROTOCOL "merge into the neighbouring elevation bin" | merge loop; `test_a3_sparse_top_bin_pools_with_15_30_and_is_used_for_high_sun_hours` |
| A4 origin-day | distinct 00:00 origins with ≥ 1 daylight hour in the bin | Clarifies PROTOCOL "origin-days" | `origin_days`; 00:00 check |
| A5 residual space | GHI (W/m²) | Clarifies PROTOCOL "r = actual − point" | `residuals`; `residual_space_diagnostic` in the artifact |
| A6 γ tie | largest γ | PROTOCOL is silent | `fit_gamma` tie branch |
| A8 daylight | elevation > 0 and clear-sky GHI > 0 | Clarifies "daylight MAE" (undefined in PROTOCOL) | `fit_gamma`; `lower_bound` uses the same rule |

**A3, the sparse >30° bin.** This is computed from pvlib geometry only, with no observations:
- 19 of 222 calibration origin-days reach above 30° (maximum 36.3°). In the evaluation window, 122 of 123 days do (maximum 45.0°).
- With the 20 origin-day minimum, every >30° cell has at most 19 origin-days, so it necessarily pools with the 15–30° cell of the same cloud class.
- High-sun evaluation hours therefore use a quantile estimated mostly from 15–30° hours. That is a transfer risk.

PROTOCOL §4 requires coverage reporting. Both diagnostics were missing and were **implemented in M9**:
- **In-sample, calibration window:** `quantile_table` now records, per cell, `own_origin_days`, `own_n_hours`, `in_sample_coverage_pooled` and `in_sample_coverage_own`. The quantiles themselves are unchanged (`test_in_sample_coverage_does_not_change_the_quantiles`).
- **Evaluation window, after the run:** the runner logs C's bound, point, bin and realized value for the executed hour. It checks alignment with the realized timestamp and refuses on mismatch. `gates.arm_c_evaluation_coverage` reports coverage per bin. It is diagnostic only and is never used to refit.

Adequate high-sun calibration coverage is **not** claimed.

### D5: Arm C values. RESOLVED BY DELEGATED TECHNICAL AUTHORITY

The protocol-stated values are: α 0.10; elevation bins 0/5/15/30/90°; cloud bins 0/0.2/0.8/1; minimum 20 origin-days; γ grid 0.10–1.00 in steps of 0.01; daylight-MAE objective. They are adopted as stated in PROTOCOL §4.

The two citations (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:19-21` and `:27`, in a 2025 campaign folder) remain **UNVERIFIED** and were not opened. They are recorded as unverified provenance, not as evidence. The values rest on the PROTOCOL text and on this decision.

### D1: evaluation set. RESOLVED BY DELEGATED TECHNICAL AUTHORITY

The 123 origins from 2024-05-01 to 2024-08-31 are adopted. Calibration uses origins ≤ 04-29 and ≥ 09-02, with 04-30 and 09-01 excluded.

PROTOCOL §2 "Prior use" says: "Not pristine … eligible as a non-blind development/validation set, not as a fresh holdout". This must be stated with every result. The 2025 window stays quarantined.

### D3: Rule D. RESOLVED BY DELEGATED TECHNICAL AUTHORITY (off)

Rule D is off in all arms, and the optional A+RuleD sub-arm is not adopted.

This is enforced in three places: the runner `ARM_CONFIGS`, `preflight.check_arms`, and the config budget flag. `test_rule_d_off_everywhere` passes.

### D7: timestamp convention. RESOLVED BY DELEGATED TECHNICAL AUTHORITY

Labels are fixed at UTC+1 (Etc/GMT-1) with no DST. No global conversion is applied. The correction is narrow: `LabelCorrectedLocation` shifts only the pvlib instants in the forecaster of A-Fix and C.

**Evidence:**
- `TIMESTAMP_VERIFICATION.md` and `reports/D7_VERIFICATION_REPORT.md` (non-evaluation months only);
- `timestamp_guards.run_all_guards`;
- tests: reserve vs 2024 decomposition max |Δ| = 0.000000°, origin/timestamp alignment, and the 1 h shift equivalence.

The review outcome is now recorded.

### D7a: A-Fix design. RESOLVED BY DELEGATED TECHNICAL AUTHORITY (after D10a)

All eight provisions were re-checked against the current code: `reports/D7A_REVIEW_M9_2026-10-11.md`, which supersedes the stale `reports/D7A_REVIEW.md`.

Provision 6 had three reporting gaps: J2 reserve shortfall, fuel-exhausted hours and final SoC. They were added to `gates.arm_metrics`, with the hourly field `diesel_fuel_remaining_l`.

### BUD: compute ceiling. RESOLVED BY DELEGATED TECHNICAL AUTHORITY

5 × 123 × 24 × 1 = **14,760** `optimize()` calls, which is 2,952 per arm. The rest of the configuration: retries 0, workers 1, no repeat check, no Rule D sub-arm.

The ceiling is hard-enforced: the budget is charged before the inner optimizer, and a breach stops the run. **No increase.**

### D8: package code. CONDITIONALLY APPROVED

**Targeted review, static, of the current scripts:**
- `optimize()` has one call site (`test_orchestration_has_exactly_one_optimize_call_site`).
- The budget guard wraps it.
- `main()` runs preflight before any forecaster, frozen-module load, data read or output directory (`test_execute_refused_on_real_package_config`, `test_main_refuses_before_reading_data`).
- `assert_no_protected_dates` runs before any row selection.
- No 2025 path appears in executable code (`test_static_no_protected_access.py`).
- The calibration reader never parses evaluation-window values (`test_two_pass_reader_never_parses_excluded_values`).
- The M9 code changes are small and covered by `tests/test_decision_resolution_m9.py`.

**Condition, not met:** the full suite must pass in the **device venv**, with its output saved and hashed. CC has no shell on the laptop in this session, so this was not run. A sandbox pass does not establish a device pass. Command, from the repo root on the laptop:

```
.venv/bin/python -I -m pytest -p no:cacheprovider -v -rA experiments/exp_three_arm_2024/tests
```

(Use the repo's own venv interpreter path if it differs.)

### D11: data-use rights

**D11 (internal research use): APPROVED BY EXISTING AUTHORITY.** M9 states: "The project lead states that they have the necessary data rights." Documentary evidence is in `reports/evidence/D11_DATA_RIGHTS_EVIDENCE_2026-10-11.md`:
- **Product:** Open-Meteo Previous Runs API, `metno_seamless`.
- **Open-Meteo terms (current page):** the free API is for non-commercial use only, and API data are provided under CC BY 4.0. Competitions are not addressed.
- **SITES:** CC BY 4.0 per the file header.
- **Gaps:** no archived terms; download date not established; licence page empty; MET Norway's own terms unchecked.
- **Restriction:** attribution is required in every output.

**D11-PUB (publication, redistribution, competition demonstration): BLOCKED — EVIDENCE REQUIRED.**
- **Why:** whether the use is non-commercial is not documented, and the terms list "promotional activities" as commercial.
- **Needed:** either a written non-commercial statement from the project lead with archived terms, or a commercial licence record.
- **Effect:** none on calibration or execution; it is outside preflight.

### D9: signatures. REQUIRES PROJECT-LEAD AUTHORIZATION

`AUTHORIZATION.md` and `AUTHORIZATION_RECORD.json` remain unsigned, and the record still reads `NOT_AUTHORIZED`. Calibration and execution need separate signatures that bind the exact package, config and (for execution) calibration-artifact hashes.

## Proposals rejected

- **Aggregate SoC-parity form.** It nets deficits across independent daily episodes.
- **Amending PROTOCOL §7 instead of D7a §1.** It is a larger change and would leave the experiment with no research-only candidate.
- **Treating the sandbox suite as satisfying D8.** Rejected: different environment.
- **Treating D11 as covering publication or competition use.** The evidence does not reach that far.
- **Freezing the configuration now.** D8 is unresolved, and the freeze must bind the post-D8 manifest.
- **Budget increase, the A+RuleD sub-arm and a repeat check.** Not adopted.
- **M6 family {A, A-Fix, C}.** Already superseded by D10 and not reopened.

## Shortest route to READY FOR CALIBRATION AUTHORIZATION

1. On the laptop, run the device-venv command above and save the full output under `reports/`.
2. If it passes, record the output hash under `D8` and set D8 to RESOLVED BY DELEGATED TECHNICAL AUTHORITY. If it fails, fix the code and re-review it; the status stays CONDITIONAL.
3. Set `frozen: true`, regenerate the manifests, and write the `PACKAGE_MANIFEST.sha256 SHA-256:` line in PREREGISTRATION §9.
4. Confirm that preflight's only remaining calibration failures are the unsigned authorization.

The package is then **READY FOR CALIBRATION AUTHORIZATION**. The project lead signs the calibration section, which CC never does.

Execution then additionally needs:
- a validated calibration artifact;
- a separate execution signature bound to that artifact's hash.

## Follow-up 2026-10-11: D8 condition met, package frozen

Message `cmsg_017TpQv3UrTPMkzn658LmXvX9LP4GbwMUWDt2Wm5yLAtDn` (2026-10-11T05:10:45Z, Puni, project lead): the device-venv run passed; continue under the M9 delegation.

- **Verified by CC** (report staged from the laptop, read in full for its header, result lines and summary):
  - `reports/DEVICE_VENV_TESTS.txt`, SHA-256 `e23786a3548aed590639e8188b5aa9d6db3b517e0a18392c43ba8622851557fc`;
  - interpreter `/home/punith-bs/01polaris (Copy)/.venv/bin/python`, Python 3.12.3, pytest 9.1.1;
  - 334 collected, 334 `PASSED` result lines, no `FAILED` or `ERROR`; summary `334 passed, 36 warnings in 35.49s`;
  - exit code 0 is from the project lead's terminal transcript (the file itself does not record it).
- **Same code:** the laptop's package files were not modified after the M9 commit (device listing), so the run covered exactly the M9 scripts and tests. The freeze changed no script. It changed the config (D8 status, `frozen`) and five governance-state tests that assert that state; the frozen suite was re-run in the sandbox (`reports/PREP_CHECKS_OUTPUT.txt`).
- **D8: RESOLVED BY DELEGATED TECHNICAL AUTHORITY**, evidence in `decisions.D8.condition_met`, checked by `test_d8_resolved_only_on_the_recorded_device_venv_pass` (recomputes the report hash and its pass counts).
- **Freeze:** `frozen: true`, config version `frozen-2026-10-11f`; manifests regenerated; the PACKAGE_MANIFEST hash is written to PREREGISTRATION §9 and HANDOVER.md (both outside the manifest).
- **Status: READY FOR CALIBRATION AUTHORIZATION.** Preflight's remaining calibration failures are only the unsigned calibration authorization (`logs/PREFLIGHT_OUTPUT.txt`). Not ready for execution authorization (no calibration artifact; execution unsigned).
- **Recommended, not required:** re-run the device-venv command once on the frozen package before signing, to confirm the five updated state tests on the laptop as well.
