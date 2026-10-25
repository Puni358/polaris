# Execution Authorization Sheet: EXP-THREE-ARM-2024

**Status:** NOT AUTHORIZED. Prepared 2026-10-11 for project-lead decision. Nothing below has run.

Approval covers **only** the exact configuration listed here. Any change to a hash, arm, window or gate voids it. A command-line flag such as `authorized=True` does not count as approval. Only this signed record does.

## What would be authorized

| Field | Value |
|---|---|
| Experiment ID | EXP-THREE-ARM-2024 |
| Purpose | Offline closed-loop diagnostic: (a) reproduce the current winner on non-blind data, (b) bound the diesel value of perfect solar forecasts, (c) test a calibrated forecast with a cautious reserve |
| Evaluation window | 2024-05-01 00:00 … 2024-08-31 00:00 forecast origins (123), t0 = origin − 1 h, 24 hourly steps each |
| Calibration window (Arm C only) | 2024 origins ≤ 2024-04-29 and ≥ 2024-09-02 |
| Input data | Derived 2024-only copy of `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` (source SHA-256 `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16`). Derived file hash to be recorded at creation |
| Protected data | No 2025 file opened or loaded by any script. Runner fails closed on any non-2024 row |
| Arms | PC-Control (denominator, legacy geometry); A = PC-SW, causal-NWP γ=1, legacy geometry, labelled `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT`; **A-Fix** = A with in-memory solar-label correction only (D7a, PROTOCOL_ADDENDUM_D7a.md), DIAGNOSTIC, not promotion-eligible; B = PC-SW, perfect solar (DIAGNOSTIC, non-deployable); C = PC-SW, γ̂ point + P10 reserve, corrected geometry, compared with A-Fix |
| Rule D | ☐ Off for all arms (recommended) ☐ Add A+RuleD sub-arm |
| Planner | `experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py` `a8dd9fc7d84e3d2344ba4f99ba1b1cd0ec2165a83d8f7af438b69f8178815093` (unmodified) |
| EBR adapter | `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py` `3427da6a7b1d7763f8fa655e541cd2a344aeefdd33379137c6311501799395d0` (unmodified) |
| Executor | `system/simulation/research_realization_executor.py` `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` (unmodified) |
| Solar forecaster | `system/forecasting/implementations/causal_nwp_physics.py` `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` (unmodified) |
| Configs | `system/config/{battery,diesel,loads,solar_pv}.yaml` + `experiments/run_diesel_reduction_campaign.py` `0be61c4ce9a66d1b103be5dbdb86e1b23a688b745568464d416ef0ca994392aa` (terminal target 100,000 Wh, unchanged) |
| New files (patch) | `experiments/exp_three_arm_2024/{causal_cloud_lookup.py, test_causal_cloud_lookup.py, timestamp_guards.py, solar_convention.py, test_d7a_parity.py, run_three_arm_2024.py, calibrate_arm_c.py, PREREGISTRATION.md}`. Hashes recorded in PREREGISTRATION.md before the run |
| Gates | S1, S2, S3 (unchanged, `planner_cf_statistics.py:7-9`) ☐ + S4 total-unmet non-regression (PROTOCOL.md §5) ☐ S4 strict variant (block-bootstrap upper bound ≤ 0) |
| Decision rule | An arm counts as an improvement only if S1–S4 pass AND E1 passes. B and A-Fix are reported only; fuel and all reliability metrics are reported for both A and A-Fix with no assumed direction. Nothing is promotion-eligible; a winner change needs a separate governance decision |
| Pre-run blocker | ☐ Timestamp convention (T1): verified fixed UTC+1 in d7/D7_VERIFICATION_REPORT.md; review outcome: ______ ☐ D7 guards and D7a parity tests reviewed and passing |
| Resources | ≤ 4 worker processes; 14,760 MILP solves (5 arms × 2,952), or 17,712 with the Rule D sub-arm; ☐ total compute budget confirmed; single attempt, no automatic retries; no background jobs left running |
| Outputs | `experiments/exp_three_arm_2024/run_<UTC>/`: RUN_STATUS.json, per-origin JSONL, hourly telemetry CSV (incl. headroom and unmet classification), RESULTS.json (with embedded runner hash), calibration tables, gate report |
| On failure | Run stays FAILED. No recovery or re-run without a new authorization |
| Containment / rollback | Only the new folder is created. No edits to `system/`, frozen experiments or governance documents. To roll back, delete the new folder |

## Project-lead decision

☐ **APPROVE** exactly as above (with the boxes ticked)  ☐ **APPROVE WITH CHANGES** (list): ______  ☐ **REJECT**

Data-use rights for 2024 SITES/Open-Meteo data confirmed: ☐ Yes ☐ Not required ☐ Unknown

Name: ______ Date/time (UTC): ______ Signature/initials: ______

_The executing agent must record this sheet's SHA-256 inside PREREGISTRATION.md before the first solve. Approval text must not be added after execution starts._
