#!/usr/bin/env python3
"""
Builds docs/POLARIS_JUDGE_PACK/: readable, plainly named COPIES of every script, dataset, model, test and
report a judge might ask to see, plus a master index. Originals are never moved or modified.
Run again at any time to refresh the copies:  .venv/bin/python scratch/build_judge_pack.py
"""
import os, shutil, textwrap, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACK = os.path.join(ROOT, "docs/POLARIS_JUDGE_PACK")
S8 = "forecasting/stage7/stage8/stage8_1_station_tuning_research"
CN = f"{S8}/candidate_n_additive_physics"

# (section folder, new file name, original path, one-line meaning, "if a judge asks ..." phrase)
ITEMS = [
 # ---------------- 1 forecaster: data building ----------------
 ("01_FORECASTER_data_building", "01_build_mountain_shading_terrain_features.py", "forecasting/stage7/stage7_5_terrain_horizon/build_terrain_features_2025.py", "Builds the 4 mountain-shading inputs from the Copernicus elevation model.", "How did you design the terrain / mountain shading features?"),
 ("01_FORECASTER_data_building", "02_build_causal_training_dataset_with_18Z_weather_forecast.py", f"{S8}/candidate_f_successor_18z/build_dataset_v2.py", "Assembles the training table using only the 18:00 UTC weather run (no future data).", "How do you guarantee no future information?"),
 ("01_FORECASTER_data_building", "03_download_MET_Norway_MEPS_18Z_forecasts.py", f"{S8}/candidate_f_successor_18z/acquire_full.py", "Downloads the MET Norway MEPS weather forecasts.", "Where does the weather forecast come from?"),
 ("01_FORECASTER_data_building", "03b_MEPS_download_helper.py", f"{S8}/candidate_f_successor_18z/fetcher.py", "Helper used by the download script.", "Where does the weather forecast come from?"),
 ("01_FORECASTER_data_building", "04_build_physics_plus_Chronos2_baseline.py", f"{S8}/candidate_f_successor_18z/build_clean_stage4_baseline.py", "Builds the baseline forecast (physics + Chronos-2) the 40 models correct.", "What is the baseline the models start from?"),
 ("01_FORECASTER_data_building", "05_extract_700hPa_wind_from_MEPS.py", f"{CN}/meps_wind_extractor.py", "Extracts the upper-air wind inputs (u700, v700).", "What are u700 and v700?"),
 ("01_FORECASTER_data_building", "06_expand_daily_forecasts_to_hourly_matrix.py", "scratch/expand_rolling_matrix.py", "Turns the daily midnight forecasts into the hourly table the simulation uses.", "Is the forecast refreshed every hour?"),
 # ---------------- 2 forecaster: training ----------------
 ("02_FORECASTER_training", "10_train_Successor_v2_forecaster.py", f"{S8}/candidate_f_successor_18z/train_successor_v2.py", "Trains Successor v2 (33 causal inputs).", "Show me how you trained the earlier models."),
 ("02_FORECASTER_training", "11_train_Candidate_K_forecaster.py", f"{S8}/candidate_k_baseline_conditioning/train_candidate_k.py", "Trains Candidate K (35 inputs, baseline-conditioned).", "What is Candidate K?"),
 ("02_FORECASTER_training", "12_train_and_validate_Candidate_N1_and_N6.py", f"{CN}/run_candidate_n_experiment.py", "Trains N1 (one tree) and N6 (25 additive + 15 specialist models) and blends them.", "Show me the code that trains the 40 models."),
 ("02_FORECASTER_training", "13_freeze_and_export_N6_N1_models.py", f"{CN}/export_artifacts.py", "Freezes the models to files and records their SHA-256 fingerprints.", "How do you know the model did not change?"),
 # ---------------- 3 forecaster: evaluation ----------------
 ("03_FORECASTER_evaluation", "20_blind_2025_one_shot_test_all_models.py", f"{CN}/evaluate_2025_blind_oneshot.py", "The one-time test on 2025 data that was never used for fitting.", "How do you know it is not overfitted?"),
 ("03_FORECASTER_evaluation", "21_conformal_safety_bound_and_battery_reserve_test.py", f"{CN}/evaluate_l2_conformal_ebr_2025.py", "Tests the 90% safety bound and the battery reserve it produces.", "How do you decide the battery reserve?"),
 ("03_FORECASTER_evaluation", "22_N6_closed_loop_simulation_test.py", f"{CN}/run_n6_closed_loop_simulation.py", "Closed-loop test of forecaster + optimizer together.", "Have you tested forecaster and optimizer together?"),
 ("03_FORECASTER_evaluation", "23_N6_live_operation_demo_with_optimizer.py", f"{CN}/demonstrate_live_operational_execution.py", "Demonstrates one live operational cycle.", "Can it run live?"),
 ("03_FORECASTER_evaluation", "24_N6_feature_assembler_and_live_pipeline.py", f"{CN}/n6_operational_pipeline.py", "The feature assembler: builds the 24x36 input table and checks arrival times.", "What is the assembler?"),
 # ---------------- 4 forecaster: runtime engine ----------------
 ("04_FORECASTER_runtime_engine", "N6_forecaster_engine__25_additive_15_specialists_blend_reserve.py", "system/forecasting/implementations/n6_solar.py", "The running forecaster: checks inputs, runs the 40 models, blends, makes the bound and the reserve.", "Show me the forecaster code."),
 ("04_FORECASTER_runtime_engine", "physics_baseline_clear_sky_and_cloud_model.py", "system/forecasting/implementations/causal_nwp_physics.py", "Clear-sky (Ineichen) and cloud-based physical baseline.", "How is clear-sky light calculated?"),
 ("04_FORECASTER_runtime_engine", "offline_fallback_forecaster.py", "system/forecasting/implementations/baseline.py", "Simple persistence + clear-sky fallback (prototype).", "What if the weather download fails?"),
 ("04_FORECASTER_runtime_engine", "forecast_to_optimizer_alignment_plus1h_shift.py", "system/evaluation/n6_multi_origin_harness/adapters.py", "Shifts the forecast one hour for the optimizer and fills the last step.", "Why is the forecast shifted by one hour?"),
 ("04_FORECASTER_runtime_engine", "data_contract_forecast_bundle.py", "system/schemas/forecast_bundle.py", "The checks on what the optimizer is given (24 steps, watts, no negatives).", "What checks sit between forecaster and optimizer?"),
 # ---------------- 5 optimizer ----------------
 ("05_OPTIMIZER_GAP19", "GAP19_optimizer_HiGHS_lexicographic_J1_to_J4.py", "system/optimization/implementations/gap19_highs_native.py", "The optimizer: 432 unknowns, 336 rules, five priorities solved in order.", "Show me the optimizer / what is J1, J1b, J2, J3, J4?"),
 ("05_OPTIMIZER_GAP19", "basic_reactive_controller_baseline.py", "system/optimization/implementations/reactive_hybrid_a2.py", "The basic controller we compare against (no forecast).", "What are you comparing against?"),
 ("05_OPTIMIZER_GAP19", "data_contract_station_state.py", "system/schemas/station_state.py", "The battery / generator state handed to the optimizer every hour.", "What does the optimizer know about the station?"),
 # ---------------- 6 simulation ----------------
 ("06_SIMULATION_runs", "00_shared_demand_and_wind_formulas.py", "scratch/sim_inputs.py", "The one place demand and wind are defined, identical for every scenario.", "Is every scenario given the same inputs? Is wind real?"),
 ("06_SIMULATION_runs", "run_scenarios_2_3_4_rolling_horizon_simulation.py", "scratch/run_continuous_ui_rhc_scenario2.py", "The core simulation loop used by scenarios 2, 3 and 4.", "Show me the simulation."),
 ("06_SIMULATION_runs", "run_scenario3_fixed_big_cushion.py", "scratch/run_continuous_ui_rhc_scenario3.py", "Scenario 3 settings.", "What is Scenario 3?"),
 ("06_SIMULATION_runs", "run_scenario4_no_safety_cushion.py", "scratch/run_continuous_ui_rhc_scenario4.py", "Scenario 4 settings (no safety cushion).", "What is Scenario 4?"),
 ("06_SIMULATION_runs", "run_basic_controller_baseline_simulation.py", "scratch/run_reactive_matched.py", "Runs the basic controller on identical inputs.", "How was the baseline run?"),
 ("06_SIMULATION_runs", "run_POLARIS_with_full_decision_trace.py", "scratch/run_scenario2_full_trace.py", "Runs POLARIS (or another forecaster) and saves every decision and plan.", "How did you record the optimizer's decisions?"),
 ("06_SIMULATION_runs", "what_if_opposite_diesel_decision.py", "scratch/whatif_decisions.py", "Re-solves each hour with the opposite diesel choice.", "How did you compute the 'what if' numbers?"),
 ("06_SIMULATION_runs", "build_decision_map_data.py", "scratch/build_stakes_index.py", "Prepares the data behind the Decision Map.", "How is the Decision Map made?"),
 ("06_SIMULATION_runs", "build_year_totals_for_proof_page.py", "scratch/build_matched_aggregates.py", "Adds up each run's full-year diesel, hours, starts and lost load.", "Where do the Proof page numbers come from?"),
 ("06_SIMULATION_runs", "pick_days_worth_explaining.py", "scratch/build_featured_days.py", "Picks the eight highlighted days from the recorded run.", "How did you choose those days?"),
 ("06_SIMULATION_runs", "build_this_judge_pack.py", "scratch/build_judge_pack.py", "Rebuilds this folder.", ""),
 # ---------------- 7 data ----------------
 ("07_DATA_inputs", "real_weather_Nuolja_2024_hourly.csv", "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv", "REAL hourly measurements: air temperature, humidity, sunshine, soil temperature, rain, snow depth.", "Is the weather real?"),
 ("07_DATA_inputs", "real_weather_Nuolja_2024_hourly_5_variables.csv", "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv", "The 5-variable version used by the simulation.", "Is the sunshine real?"),
 ("07_DATA_inputs", "raw_Nuolja_station_2024_10_minute_readings.csv", "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv", "Raw 10-minute station file from the SITES data portal.", "Show me the raw station data."),
 ("07_DATA_inputs", "clear_sky_and_sun_position_2024_hourly.csv", "data/POLARIS_v0_1_clearsky_decomposition.csv", "Real sunshine next to calculated clear-sky light and sun position.", "How do you know clear-sky light?"),
 ("07_DATA_inputs", "MET_Norway_weather_forecasts_2024.csv", "data/POLARIS_v0_1_future_weather_forecasts_2024.csv", "Weather-model forecasts archive for 2024.", "Show me the forecast data."),
 ("07_DATA_inputs", "mountain_horizon_profile_360_degrees.csv", "forecasting/stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv", "The mountain skyline around the station, 0-360 degrees.", "Show me the terrain data."),
 ("07_DATA_inputs", "forecaster_input_table_daily_36_clues_2024.parquet", f"{S8}/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet", "The 36-clue table, one forecast per day.", "Show me the forecaster's input table."),
 ("07_DATA_inputs", "forecaster_input_table_hourly_used_in_simulation.parquet", "scratch/hourly_rolling_candidate_matrix.parquet", "The hourly table the simulation reads (8,328 hours x 24 steps).", "What did the simulation feed the forecaster?"),
 ("07_DATA_inputs", "training_data_even_days.csv", f"{S8}/candidate_f_successor_18z/dataset_v2/train.csv", "Even-numbered days: used for training.", "What is your train / test split?"),
 ("07_DATA_inputs", "test_data_odd_days.csv", f"{S8}/candidate_f_successor_18z/dataset_v2/validation.csv", "Odd-numbered days: held back for testing.", "What is your train / test split?"),
 ("07_DATA_inputs", "blind_2025_data_never_used_for_fitting.csv", f"{S8}/candidate_f_successor_18z/dataset_v2/blind.csv", "The 2025 blind data.", "Is there any data the model never saw?"),
 ("07_DATA_inputs", "train_test_split_list.csv", f"{S8}/candidate_f_successor_18z/dataset_v2/split_manifest.csv", "Which origin belongs to which split.", "Prove the split."),
 # ---------------- 8 frozen models ----------------
 ("08_FORECASTER_frozen_models", "N6_model_25_additive_15_specialists.joblib", f"{CN}/artifacts/candidate_n6_model.joblib", "THE forecaster used in POLARIS.", "Show me the model file."),
 ("08_FORECASTER_frozen_models", "N1_model_single_tree.joblib", f"{CN}/artifacts/candidate_n1_model.joblib", "Candidate N1.", ""),
 ("08_FORECASTER_frozen_models", "K_model.joblib", f"{S8}/candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib", "Candidate K.", ""),
 ("08_FORECASTER_frozen_models", "Successor_v2_model.joblib", f"{S8}/candidate_f_successor_18z/artifacts_v2/candidate_f_successor_v2_model.joblib", "Successor v2.", ""),
 ("08_FORECASTER_frozen_models", "N6_N1_manifest_settings_and_fingerprints.json", f"{CN}/artifacts/CANDIDATE_N_MANIFEST.json", "Every setting of N6 and N1 (seeds, depth, features) and the SHA-256 fingerprints.", "What are the model settings?"),
 ("08_FORECASTER_frozen_models", "K_manifest_settings_and_features.json", f"{S8}/candidate_k_baseline_conditioning/artifacts/CANDIDATE_K_MANIFEST.json", "Candidate K settings and the 35 inputs.", ""),
 ("08_FORECASTER_frozen_models", "Successor_v2_manifest_settings_and_features.json", f"{S8}/candidate_f_successor_18z/artifacts_v2/SUCCESSOR_MODEL_MANIFEST.json", "Successor v2 settings and the 33 inputs.", ""),
 ("08_FORECASTER_frozen_models", "N6_test_predictions_2024_odd_days.csv", f"{CN}/artifacts/validation_predictions.csv", "Predictions on the held-out odd days.", "Show me the predictions vs reality."),
 ("08_FORECASTER_frozen_models", "N6_blind_2025_predictions.csv", f"{CN}/artifacts/blind_2025_predictions.csv", "Predictions on the blind 2025 year.", "Show me the blind test."),
 ("08_FORECASTER_frozen_models", "N6_blind_2025_results.json", f"{CN}/artifacts/BLIND_2025_RESULTS.json", "The blind-test numbers.", "What were the blind-test numbers?"),
 # ---------------- 9 results data ----------------
 ("09_RESULTS_data", "year_totals_all_scenarios_and_forecasters.json", "dashboard/public/data/matched/aggregates.json", "Full-year diesel, generator hours, starts, lost load, battery cycles per run.", "Where are the full-year numbers?"),
 ("09_RESULTS_data", "basic_controller_hourly_results.json", "dashboard/public/data/matched/reactive.json", "Hour-by-hour output of the basic controller.", ""),
 ("09_RESULTS_data", "POLARIS_hourly_results.json", "dashboard/public/data/trace/scenario2_initial_state_exact/series.json", "Hour-by-hour output of POLARIS.", "Show me POLARIS's hourly output."),
 ("09_RESULTS_data", "Scenario2_plus30_rule_hourly_results.json", "dashboard/public/data/trace/scenario2/series.json", "Hour-by-hour output of Scenario 2 with the +30 kWh rule.", ""),
 ("09_RESULTS_data", "Scenario3_hourly_results.json", "dashboard/public/data/trace/scenario3/series.json", "Hour-by-hour output of Scenario 3.", ""),
 ("09_RESULTS_data", "Scenario4_hourly_results.json", "dashboard/public/data/trace/scenario4/series.json", "Hour-by-hour output of Scenario 4.", ""),
 ("09_RESULTS_data", "forecaster_physical_baseline_hourly_results.json", "dashboard/public/data/trace/cand_baseline/series.json", "Same optimizer, physical-baseline forecaster.", ""),
 ("09_RESULTS_data", "forecaster_Successor_v2_hourly_results.json", "dashboard/public/data/trace/cand_successor_v2/series.json", "Same optimizer, Successor v2 forecaster.", ""),
 ("09_RESULTS_data", "forecaster_Candidate_K_hourly_results.json", "dashboard/public/data/trace/cand_k/series.json", "Same optimizer, Candidate K forecaster.", ""),
 ("09_RESULTS_data", "forecaster_Candidate_N1_hourly_results.json", "dashboard/public/data/trace/cand_n1/series.json", "Same optimizer, Candidate N1 forecaster.", ""),
 ("09_RESULTS_data", "eight_highlighted_days.json", "dashboard/public/data/featured_days.json", "The eight days worth explaining, with reasons.", ""),
 # ---------------- 10 tests ----------------
 ("10_TESTS", "test_forecaster_engine.py", "system/tests/test_n6_forecast_engine.py", "Tests the forecaster engine.", "Do you have tests?"),
 ("10_TESTS", "test_forecaster_no_future_data_ingestion.py", "system/tests/test_n6_feature_ingestion_monitor.py", "Tests the input checks (no leakage, no missing values).", "How do you test for leakage?"),
 ("10_TESTS", "test_forecaster_decomposition_matches.py", "system/tests/test_n6_decomposition_parity.py", "Checks the split-up forecaster gives identical numbers.", ""),
 ("10_TESTS", "test_forecaster_live_operation.py", "system/tests/test_n6_live_operational_execution.py", "Tests a live operational cycle.", ""),
 ("10_TESTS", "test_clear_sky_physics_baseline.py", "system/tests/test_causal_nwp_physics.py", "Tests the physics baseline.", ""),
 ("10_TESTS", "test_battery_reserve_policy.py", "system/tests/test_reserve_policy_guard.py", "Tests the reserve policy checks.", "How do you test the reserve?"),
 ("10_TESTS", "test_optimizer_reserve_option_b.py", "system/tests/test_gap19_j2_option_b.py", "Tests the optimizer's reserve objective.", "How do you test the optimizer?"),
 ("10_TESTS", "test_forecaster_with_optimizer_integration.py", f"{CN}/test_n6_gap19_integration.py", "Forecaster + optimizer integration test.", ""),
 ("10_TESTS", "test_hourly_rolling_horizon_adapters.py", "system/tests/test_n6_receding_horizon_adapters.py", "Tests the rolling-horizon hand-off.", ""),
 ("10_TESTS", "test_per_step_safety_evaluation.py", "system/tests/test_n6_per_step_safety_evaluation.py", "Tests the safety evaluation every step.", ""),
 # ---------------- 11 reports ----------------
 ("11_REPORTS_and_proofs", "ALL_FORECASTERS_COMPARED_compendium.md", "forecasting/reports/other/README_FORECASTING_RESEARCH_COMPENDIUM.md", "Every candidate model tried, with results (the 14 variants).", "Why N6? What else did you try?"),
 ("11_REPORTS_and_proofs", "N6_gates_and_blind_test_report.md", f"{CN}/CANDIDATE_N_REPORT.md", "The four gates N6 passed.", "How did N6 pass?"),
 ("11_REPORTS_and_proofs", "N6_operational_readiness_report.md", f"{CN}/N6_OPERATIONAL_READINESS_REPORT.md", "Data-arrival margins and live readiness.", "Can you run it in the field?"),
 ("11_REPORTS_and_proofs", "N6_causal_data_contract_and_36_features.md", "scratch/N6_CAUSAL_CONTRACT_AND_HOURLY_RHC_DESIGN_REPORT.md", "Every one of the 36 inputs, its source and when it is available.", "Is any input from the future?"),
 ("11_REPORTS_and_proofs", "Candidate_K_experiment_report.md", f"{S8}/candidate_k_baseline_conditioning/CANDIDATE_K_EXPERIMENT_REPORT.md", "Why the baseline-conditioned model works.", ""),
 ("11_REPORTS_and_proofs", "operational_causality_audit.md", f"{CN}/operational_availability_audit/operational_causality_audit.md", "Independent audit that every input is available in time.", "Prove it is causal."),
 ("11_REPORTS_and_proofs", "design_decisions_register.md", "docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md", "Every owner design decision (including the one-hour shift).", "Who decided that?"),
]

def main():
    if os.path.exists(PACK):
        shutil.rmtree(PACK)
    os.makedirs(PACK)
    rows, missing = [], []
    for sec, new, orig, what, ask in ITEMS:
        src = os.path.join(ROOT, orig)
        if not os.path.exists(src):
            missing.append(orig)
            continue
        dst_dir = os.path.join(PACK, sec)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dst_dir, new))
        rows.append((sec, new, what, ask, orig, os.path.getsize(src)))
    # hand-written extras (presentation map, notes) live in scratch/judge_pack_extra/
    extra = os.path.join(ROOT, "scratch", "judge_pack_extra")
    if os.path.isdir(extra):
        for f in sorted(os.listdir(extra)):
            shutil.copy2(os.path.join(extra, f), os.path.join(PACK, f))
    # master index
    out = ["# POLARIS — judge pack: where to find everything", "",
           f"Built {datetime.date.today().isoformat()} from the live project. These are readable COPIES with plain names; the originals are untouched at the paths shown in the last column.", "",
           "To RUN anything, use the original path from the repository root (these copies are for opening and reading).", "",
           "## If a judge asks … open this", "", "| If asked | Open | What it is |", "|---|---|---|"]
    for sec, new, what, ask, orig, size in rows:
        if ask:
            out.append(f"| {ask} | `{sec}/{new}` | {what} |")
    out += ["", "## Every file", "", "| Folder | File | What it is | Original location | Size |", "|---|---|---|---|---|"]
    for sec, new, what, ask, orig, size in rows:
        out.append(f"| {sec} | `{new}` | {what} | `{orig}` | {size/1024:.0f} KB |")
    if missing:
        out += ["", "## Not found when this was built", ""] + [f"- `{m}`" for m in missing]
    open(os.path.join(PACK, "00_START_HERE_where_to_find_everything.md"), "w").write("\n".join(out) + "\n")
    print(f"copied {len(rows)} files, {len(missing)} missing")
    for m in missing: print("  missing:", m)

if __name__ == "__main__":
    main()
