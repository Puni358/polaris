# HANDOVER: EXP-THREE-ARM-2024 (authoritative, after the D9 schema-v2 re-freeze, 2026-10-11T06:17Z)

Read this first in any new session or agent. Do not trust older summaries over this file and the files it names.

This file is excluded from `PACKAGE_MANIFEST.sha256` (it records that manifest's hash). It must be updated whenever the package changes.

## 0. CURRENT STATE (supersedes §1, §6 and §10 where they differ)

**INCIDENT NOTICE (2026-10-11, added by CC after this project's incident review -- supersedes the status line
below and everything in this section that assumes the package is frozen/valid):**
- Execution WAS signed (07:52:41Z, via a separate laptop session's `NON_CMSG_REF`, not independently verified
  by this project) and WAS attempted: `results/run_20261011T075716Z/`, FAILED exit 4 (a telemetry
  representation bug, not a solver failure; every solve was genuinely optimal/feasible). Preserved unmodified.
- The runner and one test file were then fixed and extended (canonical + native `solver_status`), and a
  fail-closed single-use authorization check was added to `preflight.py`. Both are sandbox-tested, not yet
  device-venv tested, and committed to this package.
- **The package is NOT frozen, NOT validated, and NOT ready to execute.** The manifest below (`d2aedc36…`) no
  longer matches the current runner/preflight/test-file hashes. D8's evidence is stale. The 07:52:41Z signature
  is still live in `AUTHORIZATION_RECORD.json`, pending the project lead's approval of its retirement to
  `history` (proposed, not applied).
- Full analysis: `DECISIONS_LOG.md` incident addendum; `INCIDENT_REVIEW_RUN_20261011T075716Z.md` and
  `RECOVERY_IMPLEMENTATION_REPORT_2026-10-11.md` (project files, `polaris/reviews/`).

**Status as of the 06:17Z re-freeze (STALE -- see the incident notice above): calibrated; re-frozen; D8 re-confirmed on the device venv (CLOSED); EXPERIMENT EXECUTION NOT AUTHORIZED.**

**D9 boundary (schema v2):** implemented on the project lead's approval of 2026-10-11T06:06:18Z (`cmsg_017TpQv3UrTPMkzn658LmXvXDN5FsK9SWj34KVbksr5eVX`).
- `AUTHORIZATION_RECORD.json` now has these sections:
  - `calibration`: unchanged, signed 05:30:04Z;
  - `execution_preflight`, scope `PREFLIGHT_ONLY`: unsigned;
  - `execution`, scope `EXECUTE_EXPERIMENT`, plus the required `execute_instruction_ref`: unsigned;
  - `history`: append-only, never read.
- `--preflight` accepts a valid `execution_preflight` or `execution`. `--execute` accepts **only** `execution`, and `execute()` re-checks it immediately before any machinery.
- The calibration artifact must have been produced under a signed calibration authorization: current config, manifest equal to the current one or to a recorded prior freeze, signed no later than the artifact's `created_at_utc`.
- **The 05:49:08Z preflight-only block** was moved verbatim to `history[0]`, together with:
  - the full v1 record text (SHA-256 `5dd3c007…711e`);
  - your "preflight stage only" wording;
  - its preflight result;
  - a correction note, `superseded_at_utc` 2026-10-11T06:10:48Z.

**Frozen hashes now:**
- `PACKAGE_MANIFEST.sha256` = **`d2aedc36e90e3e923fc7d4a7f62ae5759bb27003226589d64a5ede86cbfcb668`** (59 files). Written in PREREGISTRATION §9, re-frozen 06:17:35Z. Prior freeze `4e4abd7f…3094` is recorded as superseded.
- `config/EXPERIMENT_CONFIG.json` = `fac38b2617b2099504486ee9599c64d7445f89e9dbd7646279ff0ceb8821750e` (**unchanged**).
- `calibration/ARM_C_CALIBRATION.json` = `65732ccc134f609f2c61a2a22ba4cb17a7e5408b21ac08e76cca22269228dab1` (**unchanged**; not re-run).
- `manifests/CODE.sha256` = `090c2fc062db4e4d226090433cc66ced04f09d6626ad12c8d2e97af8deab506f`. INPUTS and CONFIGURATION manifests are unchanged.
- Scripts:
  - `run_three_arm_2024.py` `564e34d2…011c` (changed)
  - `preflight.py` `05c970e8…5233` (changed)
  - `calibrate_arm_c.py` `0a9bb08d…8675` (unchanged)
  - `gates_three_arm.py` `d8cec7b3…00b4` (unchanged)
- Files outside the manifest:
  - `AUTHORIZATION_RECORD.json` `eb876920a94adb4c2eba80feaf48606d4d03de0d49d4e880b5d46199d9d78209`
  - `AUTHORIZATION.md` `36c02711…ea4e`, now explanatory only
  - `PREREGISTRATION.md` `62005024…ddb7`

**Tests (sandbox, Python 3.13.16, every solver mocked):** 381 passed before §9 (`reports/PREP_CHECKS_OUTPUT.txt`) and 381 passed after it (`logs/POST_REFREEZE_V2_TESTS.txt`).
- That is 334 earlier tests (2 live-record tests replaced one-for-one), plus 46 in `tests/test_authorization_scope_v2.py`, plus 1 static banned-import check that runs automatically on the new file.
- A mutation check found that letting `--execute` accept the preflight section fails 7 scope tests.

**Unsigned preflight** (`logs/PREFLIGHT_V2_UNSIGNED.txt`): exit 2. The only failures are the unsigned `execution_preflight` and `execution` sections, plus "[inputs] guards skipped". The calibration-authorization check passed, and `results/` stayed empty.

**Remaining blockers:**
1. **D8 re-confirmation: DONE, CLOSED (recorded 2026-10-11T06:25:50Z).**
   - The project lead ran the updated suite in the device venv and reported exit code 0 (message 06:24:54Z, `cmsg_017TpQv3UrTPMkzn658LmXvX8225dqJyBFkVD5wBuwuSdj`).
   - Report `logs/DEVICE_VENV_TESTS_V2.txt` (copied byte-for-byte; 105,699 bytes) has SHA-256 `898352630e0709d070f33fc0964a2470d6fd135f9dadbe46abf6cea67b27c748`.
   - Contents: Python 3.12.3, pytest 9.1.1, interpreter `/home/punith-bs/01polaris (Copy)/.venv/bin/python`. 381 collected, 381 PASSED, 0 failed, 0 errors, 0 skipped. 36 warnings: 18 scipy RuntimeWarning plus 18 DegenerateDataWarning from the BCa interval on synthetic degenerate data, the same 36 as every earlier run. Summary line: "381 passed, 36 warnings in 34.89s".
   - The file does not record the exit code; it comes from the project lead's report.
   - **Correspondence to the re-frozen package:**
     - The 381 test node ids are identical to the sandbox frozen run (`reports/PREP_CHECKS_OUTPUT.txt`), including the 46 tests in `test_authorization_scope_v2.py`.
     - The device package files were hash-verified against manifest `d2aedc36…` right after the re-freeze commit.
     - No package file's modification time changed afterwards. The only newer files are this report and `__pycache__`, both excluded from the manifest.
     - The run happened after the commit (`__pycache__` 06:23:24Z, report 06:23:59Z; commit about 06:20:54Z).
   - The frozen DECISIONS_LOG addendum row still reads "D8 re-confirmation OPEN". That file is manifest-covered, so editing it would void the freeze; this section supersedes it.
2. **Execution.** Your separate explicit execute instruction, then the `execution` section:
   - APPROVE, your name, "project lead", the actual UTC time;
   - manifest `d2aedc36…cb668`, config `fac38b26…750e`, artifact `65732ccc…dab1`;
   - `solve_ceiling` 14760, as a number;
   - `execute_instruction_ref` = that message's id.

   Optionally, sign `execution_preflight` first so a preflight can be run without execute permission. CC runs `--preflight` before any `--execute`.
3. **D11-PUB**, which covers publication, redistribution and competition use only. It is unchanged, BLOCKED — EVIDENCE REQUIRED.

Sections below are the state before the D9 change, kept as history.

## 1. Status and exact blockers

**Status: `CALIBRATED — READY FOR EXECUTION AUTHORIZATION`.** Arm C calibration is complete and validated. The experiment has **not** been executed and execution is **not** authorized.

**Calibration authorization (2026-10-11):**
- PuNi (project lead) explicitly authorized Arm C calibration only, in the project thread at 2026-10-11T05:28:46Z, bound to manifest `4e4abd7f…3094` and config `fac38b26…750e`.
- On that instruction CC recorded the `calibration` section of `AUTHORIZATION_RECORD.json` with PuNi's stated values: decision APPROVE, signer_name "PuNi", role "project lead". `signed_at_utc` is `2026-10-11T05:30:04Z`, the real UTC time of recording, not backdated.
- Both hashes were verified to match immediately before recording. The `execution` section was left untouched (all null). The top-level `status` field still reads `NOT_AUTHORIZED`; it was left as is because the instruction was to update only the calibration section.

**Calibration run** (full record: `logs/CALIBRATION_RUN.txt`):
- Preflight checks (decisions, arm_c_method, hashes, package_manifest, preregistration, authorization) all PASS. No artifact existed beforehand.
- Command: `python3 -I -W default experiments/exp_three_arm_2024/scripts/calibrate_arm_c.py --repo .`, run 05:30:26–05:30:33Z. Exit 0, no warnings or errors.
- Environment: a CC sandbox replica of the repo root (system/ code, frozen modules, the four 2024 data files, this package; no 2025 file), on Python 3.13.16, numpy 2.5.3, pandas 3.0.5, pvlib 0.16.1. This is **not** the device venv (Python 3.12.3). Every code, configuration and input file was hash-verified against the frozen device-staged hashes by `check_hashes`.
- No runner, forecast evaluation, MILP or solver call was made.

**Artifact `calibration/ARM_C_CALIBRATION.json` = `65732ccc134f609f2c61a2a22ba4cb17a7e5408b21ac08e76cca22269228dab1`.**
- `load_artifact` PASS. The recorded weather hash `8d24dc72…aa16` equals the expected and on-disk hash.
- 222 origins, 2024-01-20 to 2024-12-31. None fall in 2024-04-30..2024-09-01, and none are outside 2024.
- γ̂ = 0.18, interior to the grid 0.10–1.00. Daylight MAE 62.22 W/m², on 1,826 daylight hours.
- α = 0.10, split_conformal_lower, GHI space. Pooled in-sample coverage is 0.902–0.918 in every bin.
- **Sparse-bin limitation:** the 30–90° elevation row had only 7–10 origin-days per cloud bin (fewer than 20). By the approved policy it was merged into the 15–30° row (3 merges). Own-bin in-sample coverage there is 0.968, 0.793 and 0.857, on 31, 29 and 14 hours. The evaluation window is May–August, when high-sun hours are common, so C's lower bound at high sun rests on 15–30° residuals. Watch C's evaluation coverage in that bin row.
- The A5 diagnostic found 0 hours where the PV map is non-linear, so the residual-space choice could not change any quantile.

**Freeze intact:** `PACKAGE_MANIFEST.sha256` still verifies, and the manifest and config hashes are unchanged. Only files outside the manifest changed: `AUTHORIZATION_RECORD.json`, `calibration/`, `logs/CALIBRATION_RUN.txt` and this file.

**Execution-gate audit (2026-10-11T05:40:07Z, read-only; `logs/EXECUTION_GATE_AUDIT.txt`):**
- All 13 `EXECUTION_DECISIONS` pass (preflight.py:49). Every non-explicit status names an authority, and every entry has evidence.
- `frozen` is true. The decisions, gates, arm_c_method, hashes, package_manifest, preregistration, output and calibration-artifact checks all PASS.
- Arms and budget (run_three_arm_2024.py:421 and :428) are covered by frozen tests that passed on the device and in the sandbox: test_preflight_governance.py:83, test_runner_three_arm.py:117 and :194. Budget: 123 × 24 × 5 = 14,760.
- Input guards: there is no CLI for `run_all_guards` (timestamp_guards.py has no `__main__`). The runner calls it only from `full_preflight` after every other check passes (run_three_arm_2024.py:436-444). The supported independent entry point is the frozen test `tests/test_input_integrity_2024.py::test_run_all_guards_pass`. It uses the same pvlib elevation function as the runner, and it PASSED on the device (DEVICE_VENV_TESTS.txt:167) and again in the sandbox at this audit (2 passed).
- Not covered by any real-data test: `evaluation_origins` (run_three_arm_2024.py:193-203, 443-444), which requires exactly 123 consecutive origins. It first runs at the signed `--preflight`.
- The top-level `status` field of AUTHORIZATION_RECORD.json is read by no code. `check_authorization` reads only the stage section (preflight.py:278-298). The field is informational.
- Stale docstring, harmless: timestamp_guards.py:2-3 still says "PROPOSED — NOT APPLIED". It is manifest-covered, so it is left as is to keep the freeze.

**Documented `--preflight` run (2026-10-11T05:43:50Z, sandbox, `logs/PREFLIGHT_EXECUTION_UNSIGNED.txt`):**
- The path was first confirmed by static inspection: `main` (:541-563) calls only `load_config` and `full_preflight`. `execute()` (:463) is reachable only with `--execute`. No module-level code builds or imports an optimizer, forecaster or solver.
- Exit code 2. The only failures were the 8 execution-authorization lines, plus "[inputs] input-content guards skipped".
- The guards and the 123-day check did **not** run: `full_preflight` returns before them while authorization fails (:436-439). Their real-data result is therefore still unknown.
- Hashes were unchanged after the run, and `results/` stayed empty.

**Execution section signed for the PREFLIGHT STAGE ONLY (2026-10-11):**
- PuNi's instruction is in the project thread at 05:48:40Z: "for the preflight stage only. This does NOT authorize experiment execution."
- CC recorded the section at the real UTC time, `2026-10-11T05:49:08Z`. The fields are APPROVE, "PuNi" and "project lead"; the manifest, config and artifact hashes above; and `solve_ceiling` 14760 as a number.
- All three hashes were verified to match immediately before writing.
- `AUTHORIZATION_RECORD.json` = `5dd3c007f0b3d548bcab71339e78daa694c0c5f7d766b40e80cb6b5d932d711e`. The calibration section and every other field are unchanged.

**Signed `--preflight`** (`python3 -B … --repo . --preflight`, sandbox, 05:49:20–05:49:23Z, `logs/PREFLIGHT_EXECUTION_SIGNED.txt`):
- Result: "PREFLIGHT PASSED", exit 0. Every check passed, including `timestamp_guards.run_all_guards` and the real-data 123-consecutive-day `evaluation_origins` check (:441-446).
- Hashes were unchanged afterwards, `results/` stayed empty, and nothing was executed.

**Caution:** the code cannot tell "preflight only" apart from full authorization. With this record, `--execute` would now pass its own preflight. Execution is **not** authorized. Do not run `--execute` until PuNi gives a separate explicit execute instruction.

**Next action:** PuNi's separate explicit instruction to run `--execute`.

**(Superseded) Only remaining execution blocker:** the unsigned `execution` section (preflight.py:281-298). After signing, run `run_three_arm_2024.py --repo . --preflight` first, not `--execute`. That runs the input guards and the origin check without creating any optimizer (main, :562-566).

D11-PUB (publication, redistribution, competition use) stays blocked separately. It is outside preflight.

## 2. Decision ledger

Full table: `DECISIONS_LOG.md` → "Decision ledger after M9". Rationale: `reports/DECISION_RESOLUTION_M9_2026-10-11.md`.

| ID | Status | Owner | Depends on |
|---|---|---|---|
| D1 window | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | — |
| D2 S4 | APPROVED (M6) | Project lead | — |
| D3 Rule D off | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | — |
| D4 primary | APPROVED (M6, M8) | Project lead | — |
| D4 secondary (per origin) | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | D4 |
| D5 and A1–A6, A8 | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | D1 |
| D6 strict S4 | APPROVED (M8) | Project lead | D2 |
| D7 timestamps | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | — |
| D7a A-Fix | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | D7, D10a |
| D8 code | RESOLVED BY DELEGATED TECHNICAL AUTHORITY (device venv: 334 passed, report `e23786a3…57fc`) | CC (M9) | — |
| **D9 signatures** | **REQUIRES PROJECT-LEAD AUTHORIZATION** (calibration, then execution, separately) | Project lead | Met for calibration |
| Freeze | FROZEN 2026-10-11T05:20:26Z | CC (M9) | D8 |
| D10 Holm {A, C} | APPROVED (M7, M8) | Project lead | — |
| D10a C classification | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | — |
| D11 internal use | APPROVED BY EXISTING AUTHORITY | Project lead (attestation) | — |
| **D11-PUB** | **BLOCKED — EVIDENCE REQUIRED** | Project lead | — |
| BUD 14,760 | RESOLVED BY DELEGATED TECHNICAL AUTHORITY | CC (M9) | D3 |

**Status vocabulary.** `preflight.PASSING_STATUSES` lists the passing statuses. A status other than APPROVED passes only if it names its `authority`.

## 3. Approvals not to reopen

- **D2:** S4, U(arm) ≤ U(control). Ties pass. A result that is not evaluable fails.
- **D4 primary:** unadjusted litres, saving = control − arm. The secondary metric must never become decision-bearing.
- **D6:**
  - seed 42, stationary bootstrap, 10-day mean blocks, 10,000 resamples;
  - two-sided 95% interval, using the 97.5th-percentile upper endpoint;
  - ΔU = arm − control; PASS when upper ≤ 0.
- **D10:** {A, C} vs PC-Control, m = 2. A-Fix is diagnostic only.
- **Also do not reopen:**
  - the no-execution and quarantine rules;
  - the separate calibration and execution authorizations;
  - the battery targets, reserves, objective weights and safety gates, which stay unchanged;
  - the official winner, which stays unchanged.

## 4. Design and arm eligibility

| Arm | Label | E1 family | Promotion-eligible |
|---|---|---|---|
| PC-Control | baseline, legacy geometry | reference | — |
| A | LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT | yes | no |
| A-Fix | DIAGNOSTIC — NOT PROMOTION-ELIGIBLE (geometry fix) | no | no |
| B | NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE (perfect solar) | never | never |
| C | RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (D10a, `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`) | yes | no |

- Nothing from this experiment is promotion-eligible.
- No result from this experiment alone may be presented as independently validated, or as proof of the 40% goal.
- C vs control mixes the geometry fix and the calibration. C vs A-Fix isolates the calibration and is a diagnostic comparison.
- Rule D is off.
- The run is 5 arms × 123 origins × 24 steps = 14,760 `optimize()` calls, with no retries and 1 worker.

## 5. Data and window limitations

- **Evaluation window:** 2024-05-01 … 08-31 (123 origins). It was **previously used** and is **not a fresh holdout**.
- **Calibration window:** ≤ 04-29 and ≥ 09-02 (222 origins), with 04-30 and 09-01 excluded.
- **Quarantine:** the May 1 – Aug 31 2025 blind window is quarantined. Apr 30 and Dec 31 2025 are excluded boundary dates. Never open 2025 outputs, and never run a recursive content search over the repo copy.
- **Model limits:** wind and demand are synthetic, PV is a proxy (min(51·GHI, 60 kW)), episodes reset daily, and the Open-Meteo grid point is about 12 km from the station.
- **Arm C transfer risk:** the >30° bin has 19 of 222 calibration origin-days, against 122 of 123 evaluation days. It necessarily pools with the 15–30° bin. Per-bin coverage diagnostics are implemented. Adequate high-sun coverage is **not** claimed.
- **Unverified citations:** two D5 citations, to a 2025-folder protocol, remain unverified.

## 6. Paths and hashes (SHA-256, frozen 2026-10-11T05:20:26Z)

- **Package:** `experiments/exp_three_arm_2024/` in `/home/punith-bs/01polaris (Copy)` on the laptop. Shared working copy: `/mnt/project-files/polaris/exp_three_arm_2024_pkg/experiments/exp_three_arm_2024/`.
- **Values to bind in both authorizations:**
  - **`PACKAGE_MANIFEST.sha256` = `4e4abd7f9e927001757499e6d9ebde9ac17a9989b989dcc1ba596b526ed23094`** (58 files), written in PREREGISTRATION §9.
  - **`config/EXPERIMENT_CONFIG.json` = `fac38b2617b2099504486ee9599c64d7445f89e9dbd7646279ff0ceb8821750e`** (version frozen-2026-10-11f, `frozen: true`).
- **Manifests:**
  - `manifests/CODE.sha256` = `0bbba136a16f93c66fd6eebfa0b15d3eab764506cfd637fc52c244156a4afd5f`. The frozen modules are unmodified.
  - `manifests/CONFIGURATION.sha256` = `69d1982b9895b848875473fd1093952344e25e87a04e5d1196df7392540e5234`.
  - `manifests/INPUTS.sha256` = `aa71315934663cd2a50b809fc0421676c0f519b24b2e73ed8aaeb3b40ed072c7`:
    - weather `8d24dc72…aa16`
    - SITES raw `f3fe7cf2…3473`
    - hourly `80b721a1…052d`
    - decomposition `596345aa…e52a`
- **Scripts.** All are unchanged since M9 and identical to what the device run tested:
  - `run_three_arm_2024.py` `9dddbab8…d93d`
  - `calibrate_arm_c.py` `0a9bb08d…d8675`
  - `gates_three_arm.py` `d8cec7b3…00b4`
  - `preflight.py` `877d62fc…07fa`
- **`reports/DEVICE_VENV_TESTS.txt`** = `e23786a3548aed590639e8188b5aa9d6db3b517e0a18392c43ba8622851557fc`.
- **Historical files, unchanged:**
  - `reports/source_prep/PROTOCOL.md` `31630335…cbc1`
  - `reports/source_prep/PROTOCOL_ADDENDUM_D7a.md` `b9f488a5…02d7`
- **`AUTHORIZATION_RECORD.json`** = `fb94adc150f18743fa590f23de2e7c94a09264102afbe280fd689e4293821d92` (calibration section recorded 2026-10-11T05:30:04Z; execution section unsigned). The pre-signature template was `fc22c298…a5cd`.
- **`calibration/ARM_C_CALIBRATION.json`** = `65732ccc134f609f2c61a2a22ba4cb17a7e5408b21ac08e76cca22269228dab1`. Bind this value in the execution authorization.
- **`logs/CALIBRATION_RUN.txt`** = `4f3d26dd3c0cef220ce4e70d8030b2b01947619aae39a6e236099d9e9c27f4f4`.
- **Outside the manifest.** These files can change without breaking the freeze: `PREREGISTRATION.md`, `AUTHORIZATION.md`, `AUTHORIZATION_RECORD.json`, `HANDOVER.md`, and `logs/`, `results/`, `calibration/`.
- **Any other edit to the package changes the manifest hash.** That voids the freeze and any authorization bound to it.

## 7. Tests by environment

| Environment | What ran | Result |
|---|---|---|
| **Laptop device venv:** Python 3.12.3, pytest 9.1.1, `~/01polaris (Copy)/.venv/bin/python` | Full suite on the M9 package, run by the project lead | **334 passed, 0 failed, exit 0** (`reports/DEVICE_VENV_TESTS.txt`) |
| Sandbox: Python 3.13.16, numpy 2.5.3, pandas 3.0.5, pvlib 0.16.1, scipy 1.18.1 | Full frozen suite, synthetic, every solver mocked to raise | **334 passed** before the §9 hash (`reports/PREP_CHECKS_OUTPUT.txt`) and **334 passed** after it (`logs/POST_FREEZE_TESTS.txt`) |
| Sandbox | `--preflight`, `calibrate_arm_c.py`, `--audit-budget` | Refused (exit 2), for authorization or artifact reasons only; the budget reconciles at 14,760 |
| Real data | Nothing: no calibration, replay, training, simulation or solver call | — |

**What changed after the device run.** The freeze changed no script. It changed the config (D8 status and `frozen`) and five tests that assert that governance state. The laptop has therefore not yet run those five updated tests.

**Recommended, not required:** before signing, re-run the device command once on the frozen package. If it passes, keep the new report outside the manifest, for example under `logs/`, so the freeze is not broken.

**Not tested anywhere:**
- the real HiGHS solve;
- real calibration;
- the real coverage values;
- the run's runtime on the laptop.

## 8. Data-rights evidence and restrictions

Evidence: `reports/evidence/D11_DATA_RIGHTS_EVIDENCE_2026-10-11.md`.

- **Product:** Open-Meteo Previous Runs API, `metno_seamless`.
- **Current terms (2026-10-11):** the free API is non-commercial only, and API data are under CC BY 4.0.
- **SITES:** CC BY 4.0.
- **Project-lead attestation (M9):** covers internal research use.
- **Gaps:**
  - no archived terms;
  - download date not established;
  - licence-conditions page unread;
  - MET Norway's terms unchecked.
- **Restrictions:**
  - attribution is required in every output (Open-Meteo, MET Norway, SITES, POLARIN);
  - no publication, redistribution or competition demonstration until D11-PUB is resolved.

## 9. Calibration and execution authorization requirements

**Calibration** (real-data γ̂ fit) needs all of:
- D1, D5, D7, D7a, D8 and D11 passing;
- `frozen: true`;
- the PREREGISTRATION §9 line `PACKAGE_MANIFEST.sha256 SHA-256: <hash>`;
- the `calibration` section of `AUTHORIZATION_RECORD.json` signed by the project lead (decision APPROVE, name, role "project lead", UTC time), bound to the exact manifest and config hashes;
- a separate explicit instruction from the project lead.

CC never signs or backdates.

**Execution** additionally needs:
- every decision in `EXECUTION_DECISIONS` passing;
- a validated calibration artifact (`calibration/ARM_C_CALIBRATION.json`), whose recorded weather hash matches;
- the `execution` section signed separately, bound to the artifact hash and the ceiling of 14,760.

A command-line flag is never a substitute for these.

## 10. Next actions, in dependency order

1. **Done:** calibration authorization (05:28:46Z instruction; recorded 05:30:04Z), the calibration run, and artifact validation. See §1.
2. **Optional:** a device re-run of the frozen suite into `logs/DEVICE_VENV_TESTS_FROZEN.txt`. If wanted, also a device-venv reproduction of the calibration into a scratch path outside `calibration/`, to compare γ̂ and the quantile table under Python 3.12.3. Do not overwrite the artifact.
3. **Project lead: execution authorization.** This is a separate explicit instruction plus the `execution` section:
   - `"decision": "APPROVE"`;
   - name;
   - `"signer_role": "project lead"`;
   - `"signed_at_utc"`: the actual time, formatted `…Z`;
   - `"package_manifest_sha256": "4e4abd7f9e927001757499e6d9ebde9ac17a9989b989dcc1ba596b526ed23094"`;
   - `"experiment_config_sha256": "fac38b2617b2099504486ee9599c64d7445f89e9dbd7646279ff0ceb8821750e"`;
   - `"calibration_artifact_sha256": "65732ccc134f609f2c61a2a22ba4cb17a7e5408b21ac08e76cca22269228dab1"`;
   - `"solve_ceiling": 14760`.

   CC never fills this without that instruction, and never backdates.
4. **Execution and gates.**
   - Run `run_three_arm_2024.py --repo . --execute`. The input-content guards run first.
   - Report C's coverage per bin, especially the merged 30–90° row.
   - Report both f values for the secondary metric.
5. **D11-PUB evidence** before any publication or competition use.
