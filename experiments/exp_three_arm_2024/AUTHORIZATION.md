# Execution Authorization: EXP-THREE-ARM-2024

**This sheet is EXPLANATORY ONLY and is not signed** (project lead's decision, 2026-10-11T06:06:18Z, `cmsg_017TpQv3UrTPMkzn658LmXvXDN5FsK9SWj34KVbksr5eVX`). **Authoritative are: (1) `AUTHORIZATION_RECORD.json`, which the code checks, and (2) the project lead's explicit instructions in the project thread, which each signed section references.** The checkboxes below are kept as an explanatory checklist; ticking or leaving them blank authorizes nothing.

**Current state (2026-10-11):** Arm C calibration authorized (instruction 05:28:46Z; record 05:30:04Z) and run. Experiment execution is **NOT AUTHORIZED**. See `HANDOVER.md`.

Earlier header, kept as history: "Status: NOT AUTHORIZED. Package status: BLOCKED (see `reports/FINAL_READINESS_REVIEW.md`). Nothing has run."

**M9 note (2026-10-11):** decision statuses after the technical-PM pass are in `DECISIONS_LOG.md` (ledger after M9) and `HANDOVER.md`. Delegated resolutions are not signatures; every box below is still for the project lead, and none is ticked by CC.

This sheet supersedes `reports/source_prep/AUTHORIZATION_SHEET.md` (kept verbatim as history). Approval covers only the exact configuration and hashes in `manifests/`. Any change to a hash, arm, window, gate or budget voids it. A command-line flag such as `authorized=True` is not approval. (Original wording: "Only this signed record is." Superseded on 2026-10-11 by the project lead's decision above: the signed JSON record plus the referenced explicit instruction is the approval; this sheet is not.)

## Configuration to be authorized

| Field | Value |
|---|---|
| Experiment | EXP-THREE-ARM-2024: offline closed-loop diagnostic, offline-benchmark evidence only |
| Evaluation | 123 origins, 2024-05-01 … 2024-08-31 00:00 (UTC+1 labels); t0 = origin − 1 h; 24 steps. **Previously used window; not a fresh holdout** |
| Calibration (Arm C only) | Origins ≤ 2024-04-29 or ≥ 2024-09-02; 04-30 and 09-01 excluded |
| Arms | PC-Control; A (`LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT`); A-Fix (diagnostic); B (`NONCAUSAL`, never eligible); C (calibrated + P10 reserve, corrected geometry) |
| Rule D | OFF in all arms |
| Gates | S1, S2, S3, E1 (Holm family: D10 ☐ {A, C} vs Control ☐ {A, A-Fix, C} vs Control ☐ other: ____) ☐ S4 authoritative (D2) ☐ S4-strict (D6), interval ☐ two-sided 95% upper ☐ one-sided 95% upper. Status of each decision as of 2026-10-11: `reports/DECISION_RESOLUTION_2026-10-11.md` and `reports/DECISION_RESOLUTION_M7_2026-10-11.md` and `reports/DECISION_FOLLOWUP_M8_2026-10-11.md` (D10 recorded as {A, C}; D6 interval approved in M8; D10a Arm C classification conflict open). The boxes are for the project lead's signature, and none is ticked by CC |
| Data | `manifests/INPUTS.sha256`. No 2025 file is read; the runner fails closed on non-2024 rows |
| Code | `manifests/CODE.sha256` (frozen modules unmodified; package scripts including `run_three_arm_2024.py`, `calibrate_arm_c.py`, `preflight.py` and `gates_three_arm.py`, which are written but not yet reviewed) |
| Configuration | `manifests/CONFIGURATION.sha256` |
| Budget | Hard maximum 14,760 `optimize()` calls (COMPUTE_BUDGET.md); single attempt; no retries; 1 worker; no background jobs |
| Outputs | `results/run_<UTC>/` only. `logs/` for run logs. On failure the run stays FAILED; no recovery without new authorization |
| Rollback | Delete `results/run_<UTC>/`. Nothing outside this folder is written |

## Pre-run checklist (all must be ticked by the project lead)

- ☐ D1 evaluation set
- ☐ D2 S4
- ☐ D3 Rule D OFF
- ☐ D4 fuel metric
- ☐ D5 Arm C α/bins
- ☐ D6 S4-strict / E1 bootstrap
- ☐ D7 timestamp convention, review outcome: ______
- ☐ D7a
- ☐ D8 runner reviewed
- ☐ D10 Holm family
- ☐ D11 data-use rights
- ☐ Budget frozen at the count reconciled with the actual runner: ______
- ☐ All package tests pass on the device venv (command and output attached)
- ☐ Manifests regenerated after the runner was added; PACKAGE_MANIFEST hash recorded in PREREGISTRATION.md

## Project-lead decision

☐ APPROVE exactly as above ☐ APPROVE WITH CHANGES: ______ ☐ REJECT

Name: ______ Role (project lead): ______ Date/time (UTC): ______ Signature/initials: ______

_Approval text must not be added after execution starts. CC does not sign this sheet._

**Machine-checked record (schema v2, 2026-10-11):** the code reads `AUTHORIZATION_RECORD.json`, not this sheet. Sections:
- `calibration`: signed before calibration (done, 05:30:04Z). Execution preflight also checks that the calibration artifact was produced under it.
- `execution_preflight` (`scope: "PREFLIGHT_ONLY"`): lets `--preflight` pass. It **never** authorizes `--execute`.
- `execution` (`scope: "EXECUTE_EXPERIMENT"`): the **only** section `--execute` accepts. It must carry `execute_instruction_ref`, the project-thread message id of the project lead's separate explicit execute instruction.
- `history`: append-only; never read for authorization.

Every signed section needs:
- decision `APPROVE`;
- the signer's name, with the role `project lead`;
- an ISO-8601 UTC time ending in `Z`;
- the current PACKAGE_MANIFEST and config hashes.

The execution sections also need the calibration artifact SHA-256 and `solve_ceiling: 14760` as a number. The record is a plain file, not a cryptographic signature.
