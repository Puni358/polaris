# Final Readiness Review: EXP-THREE-ARM-2024

**Current status (2026-10-11, after the D9 boundary change, §13): calibrated; execution NOT authorized; D8 re-confirmation OPEN.** Status as written after the M9 follow-up, kept as written: **`READY FOR CALIBRATION AUTHORIZATION`** (2026-10-11, after the M9 follow-up). D8 passed in the device venv and the configuration is frozen. The only remaining calibration blocker is the project lead's unsigned calibration authorization (§11). Not ready for execution authorization: that additionally needs a validated calibration artifact. The PACKAGE_MANIFEST hash is in PREREGISTRATION §9 and `HANDOVER.md`.

First reviewed 2026-10-11 by CC (consolidation). Updated 2026-10-11 after implementing the runner and the Arm C calibration, again after the M6 decision pass (`reports/DECISION_RESOLUTION_2026-10-11.md`), after the M7 decision pass (`reports/DECISION_RESOLUTION_M7_2026-10-11.md`), after the M8 follow-up (`reports/DECISION_FOLLOWUP_M8_2026-10-11.md`), and after the M9 technical-PM pass (`reports/DECISION_RESOLUTION_M9_2026-10-11.md`). Handover: `HANDOVER.md`. Preparation only: **no experiment execution, calibration on real data, forecast replay, training or MILP solve was performed.**

## 1. Repository and location

- **Repository root:** `/home/punith-bs/01polaris (Copy)` on device `punith-bs-megabook-t1-tgl`. It is the only POLARIS repository in the home folder and the one used by every earlier audit.
- **Package:** `experiments/exp_three_arm_2024/`. It did not exist before this review.

**Git:**
- `.git` is present: branch `master`, remote `https://github.com/Puni358/models.git`.
- There are **no commits**: `refs/heads` is empty.
- The index stages 2 files, `POLARIS_MASTER_HANDOFF.md` and `requirements.txt`. Their current blob hashes equal the staged ones (`9119b09c…`, `c65e9776…`), so neither is modified since staging.
- Every other file is untracked.
- `git status` could not be run, because this session has no shell on the device. The state above was derived from `.git/HEAD`, `config` and `index`.
- Git therefore provides no history evidence for any artifact.

**Notes:**
- The repository folder is itself named "(Copy)", and it contains a nested `01polaris (Copy)/01polaris (Copy)/` holding only `.venv`, `chronos` and `moirai`. Both were left untouched.
- Which folder is the authoritative original was not otherwise documented. Treating this one as the working repository rests on project memory and on every earlier audit having used it.

## 2. Inventory

| Action | Files |
|---|---|
| Copied verbatim (byte-compared with `cmp`, all identical) | `reports/source_prep/{PROTOCOL.md, PROPOSED_PATCH.diff, AUTHORIZATION_SHEET.md, PROTOCOL_ADDENDUM_D7a.md, POLARIS_winner_and_safety_audit.md, candidate_F_future_data_findings.md}`; `reports/source_prep/d7/*` (8 files); `reports/D7_VERIFICATION_REPORT.md`; `scripts/solar_convention.py`; `scripts/timestamp_guards.py` |
| Extracted unchanged | `scripts/causal_cloud_lookup.py` (from PROPOSED_PATCH.diff) |
| Adapted (changes in CHANGELOG) | `tests/test_causal_cloud_lookup.py`, `tests/test_d7a_parity.py` |
| Created | README, PREREGISTRATION (draft), AUTHORIZATION (unsigned), DECISIONS_LOG, CHANGELOG, DATA_PROVENANCE, TIMESTAMP_VERIFICATION, DESIGN_AND_GATES, COMPUTE_BUDGET, `tests/{conftest.py, test_static_no_protected_access.py, test_input_integrity_2024.py}`, `reports/{D7A_REVIEW.md, FINAL_READINESS_REVIEW.md, PREP_CHECKS_OUTPUT.txt}`, `manifests/*`, `PACKAGE_MANIFEST.sha256`, `logs/.keep`, `results/.keep` |
| Added 2026-10-11 (implementation) | `config/EXPERIMENT_CONFIG.json`, `AUTHORIZATION_RECORD.json`, `scripts/{preflight, calibrate_arm_c, run_three_arm_2024, gates_three_arm}.py`, `tests/{synthetic_fixtures, test_preflight_governance, test_calibration_arm_c, test_runner_three_arm}.py`, `reports/CALIBRATION_AMBIGUITIES.md` |
| Modified outside the package | **None** |
| Left untouched | Every other repository file, including the frozen modules, the winner's artifacts, governance records, and the 10-10 replay (FAILED) and recovery records with their original statuses |

## 3. Artifacts

**Now present** (written 2026-10-11, unreviewed): `scripts/run_three_arm_2024.py`, `scripts/calibrate_arm_c.py`, `scripts/preflight.py`, `scripts/gates_three_arm.py`, `config/EXPERIMENT_CONFIG.json`, `AUTHORIZATION_RECORD.json` (template), four new test files, and `reports/CALIBRATION_AMBIGUITIES.md`.

**Still missing:**
- A signed AUTHORIZATION.md and a filled AUTHORIZATION_RECORD.json.
- The D7 review outcome.
- The calibration artifact. It is created only by an authorized calibration.
- Test results from the device venv. All results so far come from a sandbox copy.

## 4. Decision statuses (see DECISIONS_LOG.md)

| ID | Status after M9 |
|---|---|
| D1 evaluation set | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (disclosed prior use; not a fresh holdout) |
| D2 S4 point | **APPROVED (M6)** |
| D3 Rule D | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (off in all arms) |
| D4 fuel metric | **APPROVED (M6, M8)** primary unadjusted; secondary SoC-parity RESOLVED BY DELEGATED TECHNICAL AUTHORITY: per-origin application of the unchanged §7 formula, secondary only, both f values, limitations recorded |
| D5 Arm C values; A1–A6, A8 | RESOLVED BY DELEGATED TECHNICAL AUTHORITY. Values as PROTOCOL §4; clarifications verified in code; two citations still UNVERIFIED provenance; per-bin coverage diagnostics implemented |
| D6 strict S4 | **APPROVED (M8)**: two-sided 95% interval (97.5th-percentile upper endpoint), seed 42, 10-day blocks, 10,000 resamples; ΔU = arm − control; PASS iff upper ≤ 0 |
| D7 timestamp convention | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (fixed UTC+1; narrow correction) |
| D7a | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (`reports/D7A_REVIEW_M9_2026-10-11.md`) |
| D8 code | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (follow-up): targeted review passed; device-venv suite 334 passed, 0 failed (`reports/DEVICE_VENV_TESTS.txt`) |
| D9 signatures | **REQUIRES PROJECT-LEAD AUTHORIZATION** (unsigned; calibration and execution separately) |
| Budget 14,760 | RESOLVED BY DELEGATED TECHNICAL AUTHORITY; hard-enforced; no increase |
| D10 Holm family | **APPROVED (M7, M8): {A, C} vs PC-Control**, A-Fix diagnostic only |
| D10a Arm C classification | RESOLVED BY DELEGATED TECHNICAL AUTHORITY: C = research-only candidate, not promotion-eligible (`PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`) |
| D11 data rights (internal research use) | APPROVED BY EXISTING AUTHORITY (project-lead attestation, M9); documentary gaps listed |
| D11-PUB publication / redistribution / competition | **BLOCKED — EVIDENCE REQUIRED** (outside preflight) |

Project-lead identity: **confirmed by Puni in M6.**

## 5. Tests (sandbox; exact output in `reports/PREP_CHECKS_OUTPUT.txt`)

**Environment:**
- Sandbox: Python 3.13.16, numpy 2.5.3, pandas 3.0.5, pvlib 0.16.1, pytest 9.1.1, scipy 1.18.1, highspy 1.15.1. highspy is imported only; `Highs` is mocked to raise.
- The sandbox held: the repo `system/` code; the frozen experiment modules (EBR adapter, Planner-CF v1, candidate extractor, statistics, telemetry); `run_diesel_reduction_campaign.py`, for AST parsing and its hash only; the four 2024 data files; and this package.
- **No 2025 data file was present.**
- Device venv (not yet used for these tests): Python 3.12, same pandas, pvlib, pytest and highspy versions.

| Command | Exit | Result |
|---|---|---|
| `python3 -I -m py_compile experiments/exp_three_arm_2024/scripts/*.py experiments/exp_three_arm_2024/tests/*.py` | 0 | All compile |
| `python3 -I -m pytest -p no:cacheprovider -v -rA experiments/exp_three_arm_2024/tests` | 0 | **334 passed, 0 failed** after the M9 pass (311 after M8, 302 after M7, 285 after M6, 238 before) |
| `run_three_arm_2024.py --repo . --audit-budget` | 0 | 2,952 per arm, 14,760 total, `reconciles: true` |
| `run_three_arm_2024.py --repo . --preflight` (after manifest regeneration) | 2 | PREFLIGHT FAILED: decisions, gates, Arm C method, preregistration, calibration artifact, authorization. Output in `logs/PREFLIGHT_OUTPUT.txt` |
| `calibrate_arm_c.py --repo .` | 2 | CALIBRATION REFUSED (preflight failed) |

**Solver isolation:** the autouse fixture in `tests/conftest.py` replaces `highspy.Highs`, the runner's planner loader and `PlannerCFV1Optimizer.optimize` with mocks that raise `SolverCalled`. `test_real_planner_optimize_is_blocked` confirms that the real optimizer raises under the mock. Loop tests use a `FakeOptimizer` that returns a zero-dispatch plan.

**Coverage, by required item:**
- Unsigned or missing authorization blocks execution: `test_execute_refused_on_real_package_config` (exit 2; no frozen module, forecaster, data read or output directory) and the `test_preflight_governance.py` authorization tests.
- Unresolved D2, D6 and D10 block execution: real-config tests, and the parametrized decision and gate tests.
- Hash mismatch, missing file and manifest drift.
- Non-2024 rows: calibration aborts on 2025 and 2023 rows; cloud lookup.
- Calibration rejects evaluation-window, buffer and 2025 data, and fails closed even with a broken filter.
- Bins: unresolved policy, `fail`, merge recorded, no neighbour, missing bin in `lower_bound`, determinism.
- A vs A-Fix parity: configs, forecasters, reserve elevation.
- Pinned sources byte-identical: all 28 pinned hashes.
- No reserve double conversion.
- Timestamp and origin alignment: plan hour 0 equals the realized hour; t0 = origin − 1 h.
- No horizon-tail lookahead: the sentinel cloud value is never used; held hours = step.
- Arm B is noncausal and never eligible.
- Rule D is off.
- Budget audit, with an AST check of the single `optimize()` call site.
- A missing calibration artifact blocks Arm C and execution.
- No overwrite of the run directory, `RESULTS.json` or the calibration artifact.
- Partial or failed output is never evaluated: exit 3 or 4, no `RESULTS.json`.

**History:**
- The consolidation run was 51 passed and 2 failed. Both failures were caused by the then-missing runner, and both now pass.
- In this task, the first runs exposed two test-fixture defects, both corrected (see CHANGELOG): a too-sparse synthetic calibration set, and an exact float comparison against the executor's rounded output. No code under test was changed to make a test pass.
- The runner docstring was reworded so it no longer names the banned reference module. The static guard was not changed.

## 6. Timestamp and geometry

See TIMESTAMP_VERIFICATION.md.
- Fixed UTC+1, period-ending, no DST. Supported by documentary and data evidence.
- The forecaster's 1 h defect is confirmed in code.
- The two reserve methods agree exactly (test-backed).
- The 0.05° tolerance is justified there.
- The Latnjajaure record is not used as evidence.

## 7. Hashes

The full lists are in `manifests/INPUTS.sha256`, `CODE.sha256`, `CONFIGURATION.sha256` and `PACKAGE_MANIFEST.sha256`. Key inputs:
- SITES raw `f3fe7cf2…3e43473`
- weather `8d24dc72…26aa16`
- hourly `80b721a1…7052d`
- decomposition `596345aa…70e52a`

**The manifests describe the package as it stands. They do not claim a frozen configuration,** because decisions are open and `frozen: false`. They were regenerated after the runner was added. After any change, and at freeze, they must be regenerated again and the PACKAGE_MANIFEST hash entered in PREREGISTRATION §9.

## 8. Solve counts

Derived from the runner (`run_origin`: one `optimize()` per step, 24 steps; `execute()`: 123 origins × 5 arms):

| Arm | `optimize()` = `Highs.run()` calls |
|---|---|
| PC-Control | 2,952 |
| A | 2,952 |
| A_FIX | 2,952 |
| B | 2,952 |
| C | 2,952 |
| **Total** | **14,760** |

- This equals the provisional ceiling.
- Internal lexicographic sub-solves are at most 5 per call (73,800).
- G7 repeat, Rule D sub-arm, retries, calibration, gates and tests all count 0.
- The hard budget is enforced in code before every call. See COMPUTE_BUDGET.md.

## 9. Calibration isolation and leakage

**Calibration window:** 222 origins (≤ 04-29 / ≥ 09-02). Buffers 04-30 and 09-01 are excluded. This is now enforced in code (`select_calibration_rows`, then `assert_calibration_isolation`, which raises PermissionError) and in `load_artifact`, which refuses an artifact listing any origin outside the window. Both are tested synthetically. Calibration has **not** been run.

**Lookahead:** L1 is fixed (`causal_cloud_lookup.py`) and exercised through the runner loop with a sentinel. The runner uses `SolarElevationProvider(None)`. No package script references a 2025 data path (static tests).

**Arm B:** `causal: false`, a NONCAUSAL label and bundle metadata. It is rejected from the E1 family, the gate verdict is fixed to NEVER ELIGIBLE, and `winner` is `null`.

**Wind and demand forecasts:** identical across arms (tested). They remain biased against the synthetic realized profiles, which is a documented limitation.

## 10. Data-use rights

- **SITES:** CC BY 4.0, stated in the file header. SITES must be cited and POLARIN acknowledged.
- **Open-Meteo:** Previous Runs API, `metno_seamless`. Current terms: free API non-commercial only; data CC BY 4.0. No archived terms, download date not established, licence page unread (`reports/evidence/D11_DATA_RIGHTS_EVIDENCE_2026-10-11.md`).
- **Status (M9):** D11 internal research use APPROVED BY EXISTING AUTHORITY (project-lead attestation). D11-PUB (publication, redistribution, competition demonstration) BLOCKED — EVIDENCE REQUIRED.

## 11. Blockers (after the M9 follow-up freeze)

1. **D9 calibration signature** (project lead only), bound to the frozen PACKAGE_MANIFEST and config hashes. This is the only calibration blocker.
2. For execution, additionally: a validated calibration artifact (none exists) and a separate execution signature bound to its hash and to the 14,760 ceiling.
3. D11-PUB blocks publication, redistribution and competition use only.

Resolved: D8 (device venv, follow-up), freeze; in M9: D1, D3, D4 secondary, D5 and A1–A6/A8, D7, D7a, D10a, BUD, D11 (internal use).

**Remaining risks (not blockers):**
- The evaluation window was previously used.
- Origins are serially correlated.
- Wind and demand are synthetic.
- PV is a proxy.
- The Open-Meteo grid point is about 12 km from the station.
- Open-Meteo cloud-cover time semantics are undocumented.
- There is a ~20 min centring offset between hourly SW_IN and the instantaneous clear sky (`CALIBRATION_AMBIGUITIES.md` A7).
- AUTHORIZATION_RECORD.json is not cryptographically signed.
- **Arm C transfer risk:** the >30° elevation bin occurs on only 19 of 222 calibration days but on 122 of 123 evaluation days (geometry only; max elevation 36.3° vs 45.0°), so it necessarily merges into the 15–30° bin. Per-bin in-sample coverage (artifact) and evaluation-window coverage (gate output) are now implemented (M9). Adequate high-sun coverage is not claimed.
- **D5 citations unverified:** the 20 origin-day minimum and the MAE objective cite `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md`, which sits in a 2025 campaign folder and was not opened under the quarantine rule.
- **C vs Control mixes two changes:** PC-Control keeps the legacy geometry while C uses the corrected geometry, so the confirmatory C comparison measures the timestamp fix and the calibration together (D7a §4 separates them only in the diagnostic C-vs-A-Fix comparison).
- **D4 per-origin noise penalty:** the secondary analysis (per origin, M9) also penalizes random day-to-day end-energy differences (reported only; never decision-bearing).
- A degenerate BCa interval returns NaN in the frozen statistics call, and E1 then fails closed.

**Process note:** a recursive name search for "open-meteo" scanned the read-only staged repo copy, which includes 2025-campaign output files. Only matching file names were printed; no contents or values were displayed or used. Details are in CHANGELOG.

## 12. Evidence message ids (project thread)

- M1 `cmsg_017TpQv3UrTPMkzn658LmXvXS7C8tEJAbFRK1MDNgCdTuw`
- M2 `cmsg_017TpQv3UrTPMkzn658LmXvX6gm9nCaQLng7ueWG2DbdJn`
- M3 `cmsg_017TpQv3UrTPMkzn658LmXvXUZtMG7h35sd9c3VarHeojp`
- M4 `cmsg_017TpQv3UrTPMkzn658LmXvXBkuZNqLCGj2HXCJAfU9gAA`
- M5 `cmsg_017TpQv3UrTPMkzn658LmXvXE95c27ANx1fTiaVFcY4TYf`
- M6 `cmsg_017TpQv3UrTPMkzn658LmXvX811eenQyWHcEa6oV6mYRX3`
- M7 `cmsg_017TpQv3UrTPMkzn658LmXvX79mGjYAvoUtydgZmnsGAz9`
- M8 `cmsg_017TpQv3UrTPMkzn658LmXvXFnD828pU5nJWdGmJaPDLWY`
- M9 `cmsg_017TpQv3UrTPMkzn658LmXvX2WPEGQjqxQQ7wSucS9sxg4`

## 13. D9 authorization boundary (schema v2, 2026-10-11)

- Calibration was authorized (05:28:46Z instruction; signed 05:30:04Z) and run. Artifact `65732ccc…`, see `logs/CALIBRATION_RUN.txt`.
- The `execution` section was then signed at 05:49:08Z "for the preflight stage only", and the signed `--preflight` passed. Schema v1 would also have accepted that signature for `--execute`.
- Schema v2 separates `execution_preflight` (PREFLIGHT_ONLY) from `execution` (EXECUTE_EXPERIMENT plus the project lead's `execute_instruction_ref`). `--execute` accepts only the latter, and `execute()` re-checks it before any machinery. The 05:49:08Z block is preserved verbatim in `history`, which grants nothing.
- Suite: 381 passed in the sandbox, every solver mocked.

**Blockers now:**
1. D8 re-confirmation: device-venv run of the updated suite, then the project lead confirms.
2. The project lead's separate explicit execute instruction, plus the `execution` signature bound to the new manifest, config `fac38b26…`, artifact `65732ccc…`, `solve_ceiling` 14760 and that instruction's id.
3. D11-PUB, which covers publication, redistribution and competition use only.
