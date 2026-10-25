# Candidate F: why it was flagged for "future data", and a safe way to plug it in

_2026-10-11. What I read: F's 2020–2023 audit docs (`CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md`, `CANDIDATE_L2_EXACT_38_FEATURE_PROVENANCE_AUDIT.md`), `POLARIS_MASTER_HANDOFF.md`, and pipeline **code only** (`experiments/stage4_planner_cf_consistency_2025/planner_cf_campaign_runner.py`, `experiments/candidate_s_sw_campaign_2024/run_candidate_s_sw_123_campaign.py`). Before opening each doc, I checked it for May–Aug 2025 dates (none found). I opened no CSV, telemetry, or report under any `*_2025` experiment folder, including `candidate_f_pc_sw_causal_bridge_20261008/F_PC_SW_CAUSAL_BRIDGE_REPORT.md`._

## 0. The test set problem, and it's bigger than two files

`planner_cf_campaign_runner.py:180-188` hard-codes the campaign population as the 123 origins from **2025-05-01 to 2025-08-31**. Every PC-Control / PC-S / PC-SW result in `stage4_planner_cf_consistency_2025/` was produced on the quarantined window. If the 14.95% (or 14.39%) number comes from there, it was **chosen and scored on the holdout**. That window can no longer give an unbiased final number, whatever we do with F.

## 1. Likely leak A: F's LWP/IWP features come from a run not yet published at decision time

From the F feature contract (provenance audit, §2 rows 29–31, and replay audit §3):
- The main NWP features come from the MEPS **18Z** run, with `t_init = forecast_start − 6h`, so the forecast origin is 00Z.
- `lwp_latest`, `iwp_latest`, `lwp_x_cloud` come from the MEPS **00Z** run, which is initialised *at* the origin.
- MEPS output is usually published 1–3 hours after init. At a 00Z decision time the 00Z run doesn't exist yet.
- The F audits only checked `t_init < target time`. They never checked **publication time ≤ decision time**, so this passed their "causality" gate.
- _Inferred from the docs; I haven't confirmed MEPS publication latency for those years._

## 2. Likely leak B: the pipeline's horizon tail reads a later forecast run (affects every arm, control too)

`planner_cf_campaign_runner.py:105-116`: the controller re-plans every hour for 24 steps. At step k it asks for cloud cover at `origin + k + 1 … origin + k + 24`, looked up by timestamp across the **whole** weather file. For any k > 0, the last k hours come from the **next day's** forecast run (issued at the next 00Z), which wasn't available at decision time `origin + k`.
- This is in the existing pipeline, not in F, so the 14.95% baseline probably has some lookahead too.
- When F is plugged in, the same lookup feeds F's NWP features, and a stricter checker would flag it.
- _Inferred from code, assuming one 24-row forecast per daily origin, as the runner asserts at :195._

## 3. Other things that make F's numbers untrustworthy (not leaks in the pipeline sense)
- `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold` use `k_h` / `w_h` from `ensemble_parameters.json`. If those were fitted on data that includes the evaluation year, F's 2024 score is optimistic.
- F was trained on MEPS 18Z (2020–21), validated on 2022 and blind-tested on 2023. The pipeline's 2024/2025 weather files (`POLARIS_v0_1_future_weather_forecasts_*.csv`) are a different source with only `fc_cloud_cover`. The other ~10 MEPS features (temp, RH, u700/v700, LWP/IWP) have to be fabricated or re-sourced, which is exactly where future data creeps in.
- The 28% nMAE on 2024: I couldn't find where it was computed. F's own audit reports 2023 blind-test MAE ≈ 54 W/m² (all hours), with a +28 W/m² bias (over-forecasts solar). Over-forecasting solar makes the planner under-reserve, which costs diesel.

## 4. Safe integration plan
1. **Declare May–Aug 2025 burned for this program.** Use 2024 as the dev set. Pick a fresh, untouched final holdout now (for example Sep–Dec 2025, if nothing has touched it) and don't run anything on it until the very end.
2. **Add a causality gate to the forecaster interface.** Every input carries an `available_at` time, and the gate fails the run if any `available_at > decision_time`. This covers NWP runs (init + publication latency) and station obs (strictly < t).
3. **Fix leak B in the runner**, then re-run PC-Control and the 14.95% arm on 2024. At step k, use the latest run published ≤ origin + k, and fill the tail beyond that run's horizon with that same run's last values or climatology, never the next run. Expect the baseline to move.
4. **Fix leak A in F.** Either take LWP/IWP from the previous 18Z run, or drop those 3 features and retrain F on 2020–2022, keeping 2023 blind. Re-fit `ensemble_parameters.json` on training years only.
5. **Feed F in the pipeline's shape.** The pipeline needs h = 1..24 at every hourly step, but F was trained on h = 6..24 from one daily 18Z run. Build an adapter that maps step-k lead times onto the latest available run and recomputes `ctx_*` from realized station SW_IN before `origin + k`.
6. **Check headroom before tuning further:** run the planner on 2024 with perfect solar (actual values). If that oracle stays well below 40%, no forecaster can reach the target, and the work belongs in the reserve (EBR) logic, battery sizing or diesel dispatch.
