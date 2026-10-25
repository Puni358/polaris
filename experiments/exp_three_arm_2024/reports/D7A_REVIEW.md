# D7a Review: item-by-item status

Source: project-thread message M4 (2026-10-11 02:20:08 UTC). Decision status: **PENDING** (worded as a conditional approval, but marked "Proposed for project-lead approval"). Mechanism: `reports/source_prep/PROTOCOL_ADDENDUM_D7a.md`. Tests: `tests/test_d7a_parity.py`. Results are from the sandbox run recorded in `reports/PREP_CHECKS_OUTPUT.txt`.

| # | M4 condition | Status | Evidence |
|---|---|---|---|
| 1 | Arm A unchanged, reproduces PC-SW incl. the defect, labelled `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT` | Specified. **Not implementable until the runner exists.** The label check is in `test_arm_configs_identical_except_correction`, which **FAILED: runner missing** | DESIGN_AND_GATES.md §2 |
| 2 | A-Fix corrects the conversion in memory before sun position; source files and timestamps preserved | Implemented in `scripts/solar_convention.py` (Location wrapper, label − 1 h for pvlib only). `causal_nwp_physics.py` hash unchanged | `test_corrected_solar_equals_legacy_shifted_one_hour` PASSED; `test_source_files_unchanged[...]` PASSED |
| 3 | Everything except the correction identical between A and A-Fix; unavoidable differences documented | Forecaster level: timestamps, wind and demand are identical and only solar differs. Arm-config level: needs the runner | `test_only_solar_channel_differs` PASSED; `test_arm_configs_identical_except_correction` FAILED (runner missing). Unavoidable difference: the reserve uses the pvlib provider instead of the winner's precomputed CSV; the two agree to 0.000000° on 2024 and the difference applies equally to A and A-Fix |
| 4 | Same verified convention applied to the appropriate solar-position calculations; forecaster and reserve audited separately; no double conversion | Static audit done (addendum §2-§3). The reserve is untouched and already UTC+1-correct. The forecaster is corrected only in A-Fix and C | `test_reserve_elevation_not_double_converted` PASSED; `test_corrected_forecaster_matches_reserve_geometry` PASSED; `test_refuses_double_wrap` PASSED |
| 5 | Fail-closed tests for conversion, alignment, unchanged sources and arm parity | Written. All pass except the two that need the missing runner | FINAL_READINESS_REVIEW.md §5 |
| 6 | Report fuel and all reliability metrics for both arms; no assumed direction | Specified in DESIGN_AND_GATES.md §4. Not implementable until the runner exists | — |
| 7 | A-Fix is diagnostic; a winner change needs separate governance | Recorded (DESIGN_AND_GATES §2; DECISIONS_LOG footer) | — |
| 8 | Record the extra solves and confirm the total budget before execution | A-Fix adds 2,952 (not "about 4,000"). Total 14,760 reconciles on the reference loop; **cannot be frozen until the runner exists** | COMPUTE_BUDGET.md |

**Arm C geometry:** the addendum chose corrected geometry for C and for the γ̂ calibration. M5 adopts this ("corrected solar geometry"). It still sits under PENDING D5/D7a.
