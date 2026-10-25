# PREREGISTRATION: EXP-THREE-ARM-2024 (RE-FROZEN 2026-10-11T06:17:35Z; first frozen 2026-10-11T05:20:26Z)

**Status:** RE-FROZEN 2026-10-11T06:17:35Z after the D9 authorization-boundary change (schema v2; project-lead approval 2026-10-11T06:06:18Z). D8 re-confirmation on the device venv is OPEN (project lead's condition). Calibrated under the first freeze (artifact `65732ccc…`); execution NOT authorized. First frozen 2026-10-11T05:20:26Z (M9 follow-up, after D8 passed in the device venv). All required decisions pass preflight (`reports/DECISION_RESOLUTION_M9_2026-10-11.md`, including its follow-up section). Freezing authorizes nothing: calibration and execution each need the project lead's separate signature in `AUTHORIZATION_RECORD.json`. Preflight reads the §9 line `PACKAGE_MANIFEST.sha256 SHA-256: <64 hex>` and refuses unless it equals the current manifest hash.

## 1. Purpose

An offline closed-loop diagnostic on non-quarantined 2024 data. It aims to:
- reproduce the current PC-SW policy (Arm A);
- measure the effect of correcting the forecaster's solar-position error (A-Fix);
- bound the value of perfect solar information (B, noncausal);
- test a calibrated forecast with a cautious reserve (C).

It does not certify superiority, promote a winner, or establish the 40% goal.

## 2. Population and data

See DATA_PROVENANCE.md.
- **Evaluation:** 123 origins, 2024-05-01 … 2024-08-31. **Prior use disclosed (D1):** the same origins were the evaluation set of EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024 and EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024, and the existing γ = 0.25 was fitted on all of 2024. This is a non-blind development/validation set, **not a fresh holdout**; every result must say so.
- **Calibration:** ≤ 04-29 / ≥ 09-02, 222 origins.
- **Buffers:** 04-30 and 09-01.
- **Inputs:** SHA-256 values in `manifests/INPUTS.sha256`.

## 3. Arms, comparisons, gates

See DESIGN_AND_GATES.md, `reports/DECISION_RESOLUTION_2026-10-11.md` and `reports/DECISION_RESOLUTION_M7_2026-10-11.md` and `reports/DECISION_FOLLOWUP_M8_2026-10-11.md`.
- **Decided (M6, M7 and M8, 2026-10-11):**
  - S4 point non-regression (D2).
  - Primary fuel = unadjusted realized litres, saving = control − arm, per origin (D4).
  - Strict S4 by paired stationary block bootstrap of mean ΔU = U_arm − U_ctrl per origin, with 10-day mean block, 10,000 resamples and seed 42 (seed confirmed as the project lead's decision in M7) (D6). E1 keeps the iid BCa.
  - Strict S4 interval: two-sided 95%, upper endpoint = 97.5th percentile, PASS iff ≤ 0 (D6, M8).
  - E1 Holm family {A, C} vs PC-Control, m = 2, as PROTOCOL §7; A-Fix diagnostic only (D10, M7/M8).
- **Open:**
  - D10a: Arm C classification (PROTOCOL §7 "Research-only candidate" vs D7a §1 "DIAGNOSTIC"); amendment proposed, not applied.
  - The secondary SoC-parity application (D4): per-origin recommended.
- The primary criterion is E1. Block-bootstrap fuel CIs are secondary.

**Arm C calibration (D5):** method in `scripts/calibrate_arm_c.py`. The six choices A1–A6 and A8 (daylight definition) have recommended resolutions awaiting approval; α, edges, γ grid, minimum count and objective are PROPOSED exactly as PROTOCOL §4 (`reports/CALIBRATION_AMBIGUITIES.md`, M7 report §4). The calibration window, buffers and isolation checks are as in §2. Evaluation-window values are never parsed by the calibration reader.

## 4. Timestamp convention (D7). Review outcome: RESOLVED BY DELEGATED TECHNICAL AUTHORITY (M9; DECISIONS_LOG ledger)

```
Convention: all 2024 inputs labelled fixed UTC+1 (Etc/GMT-1), no DST. SITES 10-min = period-ending.
Hourly = mean(HH:00..HH:50) -> HH:00. Weather: timestamp = forecast_start + (horizon_hour-1) h; forecast_start 00:00.
Simulation: t0 = forecast_start - 1 h; realized step k = forecast_start + k h. Solar geometry at label - 1 h (UTC).
Evidence: SITES header "TIME ZONE: UTC+1"; audit_clean_nwp_windows.py:16,33; compute_clearsky.py:18,45;
non-eval-month first/last light +1.4/+1.8 deg (UTC+1) vs +5.7/-2.9 deg (UTC); midpoint 11.67 vs noon 11.75.
Reserve provider vs 2024 decomposition: max |d| 0.000000 deg (pvlib 0.16.1, test output). Tolerance 0.05 deg (justified in TIMESTAMP_VERIFICATION.md).
Known defect: causal_nwp_physics.py:55,302-303,334-336 treats labels as UTC. Handling: D7a (A legacy, A-Fix corrected).
Open: Open-Meteo cloud_cover instantaneous vs hour-mean semantics not documented.
Review outcome: RESOLVED BY DELEGATED TECHNICAL AUTHORITY. Reviewer: CC, technical PM under the project lead's M9 delegation. Date (UTC): 2026-10-11 (M9 pass; recorded here 2026-10-11 during the D9 re-freeze). Guards passed on the frozen inputs at the signed preflight, 2026-10-11T05:49:20Z.
```

## 5. Arm A-Fix mechanism (D7a)

`scripts/solar_convention.py`: in A-Fix and C only, the forecaster instance's pvlib Location is wrapped so that sun position and clear-sky are evaluated at label − 1 h. No timestamp is rewritten, and the reserve is untouched.

## 6. Lookahead control (L1)

`scripts/causal_cloud_lookup.py`: each decision uses only the current origin's 24-row package. Hours beyond it hold the last value, and the held-hour count goes to telemetry. Synthetic sentinel tests pass for all 24 steps (FINAL_READINESS_REVIEW §5).

## 7. Compute

Hard maximum 14,760 `optimize()` calls (COMPUTE_BUDGET.md): 5 arms × 123 origins × 24 steps × 1 call. Derived from the runner and reconciled by `--audit-budget` (`reconciles: true`). Status: RESOLVED BY DELEGATED TECHNICAL AUTHORITY (M9; earlier text "provisionally approved, not yet APPROVED" described the pre-M9 state).

## 8. Missing before freeze (pre-M9 list, kept as history; all items resolved or tracked in the DECISIONS_LOG ledger and HANDOVER)

- Project-lead decisions on everything listed in DECISIONS_LOG as PENDING or UNRESOLVED, including the `null` settings in `config/EXPERIMENT_CONFIG.json`.
- Project-lead review of the runner, calibration, preflight and gate code (D8).
- Tests re-run in the device venv. So far they have run only in a sandbox copy.
- Open-Meteo licence evidence (D11).
- Confirmation of the project lead's identity.

## 9. Freeze record

PACKAGE_MANIFEST.sha256 SHA-256: 8c09074c4f202356c6a9ee8725de58bc75a8cd3224bb9e97051e3522e978a58c
Prior freeze (superseded): d2aedc36e90e3e923fc7d4a7f62ae5759bb27003226589d64a5ede86cbfcb668 (frozen 2026-10-11T06:17:35Z under the D9 schema-v2 re-freeze; the execution authorization of 07:52:41Z is bound to it; superseded by the post-incident re-freeze below)
Prior freeze (superseded): 4e4abd7f9e927001757499e6d9ebde9ac17a9989b989dcc1ba596b526ed23094 (frozen 2026-10-11T05:20:26Z; the calibration authorization of 05:30:04Z is bound to it; superseded by the D9 schema-v2 re-freeze)
AUTHORIZATION.md (signed) SHA-256: not used. AUTHORIZATION.md is explanatory only; AUTHORIZATION_RECORD.json and the project lead's explicit instructions govern (project lead, 2026-10-11T06:06:18Z).
Post-incident re-frozen at (UTC): 2026-10-11T12:56:53Z by: Puni, project lead, personally (NON_CMSG_REF :: sha256_of_exact_instruction_text=8fc8000c4c58613036d8c2645f1cb1dce6557c8a86fbdfc587474f4207a0cd64 :: "POLARIS -- Explicit Project-Lead Approval and Controlled Recovery", approving D8 disposition and this post-incident freeze; explicitly not an extension of the M9 delegation, whose recorded scope is limited to before any calibration or evaluation run). Corrects the solver-status telemetry defect and adds the single-use execution-authorization guard found after the run_20261011T075716Z incident. Config `experiments/exp_three_arm_2024/config/EXPERIMENT_CONFIG.json` SHA-256 9d41e3f4bd608aec5b0f9d970275c693cd7608d86ec2d5ebda37533b3d808157 (changed: D8 resolution). `manifests/CODE.sha256` SHA-256 2cc1bcb794e8f77029ffc62eeff06863ee3078bde61ad18ffad991694d1daa2b.
Re-frozen at (UTC): 2026-10-11T06:17:35Z by: CC, under the project lead's approval of the D9 Option 2 plan (cmsg_017TpQv3UrTPMkzn658LmXvXDN5FsK9SWj34KVbksr5eVX). Config `experiments/exp_three_arm_2024/config/EXPERIMENT_CONFIG.json` SHA-256 fac38b2617b2099504486ee9599c64d7445f89e9dbd7646279ff0ceb8821750e (unchanged). `manifests/CODE.sha256` SHA-256 090c2fc062db4e4d226090433cc66ced04f09d6626ad12c8d2e97af8deab506f.
First freeze, kept as history: Frozen at (UTC): 2026-10-11T05:20:26Z by: CC, technical PM under the project lead's M9 delegation (follow-up message cmsg_017TpQv3UrTPMkzn658LmXvX9LP4GbwMUWDt2Wm5yLAtDn). Config `experiments/exp_three_arm_2024/config/EXPERIMENT_CONFIG.json` SHA-256 fac38b2617b2099504486ee9599c64d7445f89e9dbd7646279ff0ceb8821750e.

## Decision pass 2026-10-11 (M9, technical-PM delegation)

See `reports/DECISION_RESOLUTION_M9_2026-10-11.md` and `HANDOVER.md`.
- **Resolved by delegated technical authority:** D1, D3, D4 secondary (per-origin application of the unchanged §7 formula; secondary only; recorded as a pre-data clarification, not original preregistration), D5 and A1–A6/A8, D7 (review outcome recorded), D7a, D10a (C = `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE`, `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`), BUD.
- **Approved by existing authority:** D11 for internal research use (project-lead attestation). D11-PUB (publication, redistribution, competition) blocked pending evidence.
- **Still open after M9:** D8 (device-venv tests), freeze, §9 hash line, both signatures. **Follow-up (same day):** D8 resolved on the device-venv pass, freeze and §9 line done; only the signatures remain.
- **Added diagnostics (PROTOCOL §4):** per-bin in-sample coverage in the calibration artifact; per-bin evaluation-window coverage after the run. Diagnostic only.
