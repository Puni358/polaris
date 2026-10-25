# POLARIS — judge pack: where to find everything

Built 2026-10-23 from the live project. These are readable COPIES with plain names; the originals are untouched at the paths shown in the last column.

To RUN anything, use the original path from the repository root (these copies are for opening and reading).

## If a judge asks … open this

| If asked | Open | What it is |
|---|---|---|
| How did you design the terrain / mountain shading features? | `01_FORECASTER_data_building/01_build_mountain_shading_terrain_features.py` | Builds the 4 mountain-shading inputs from the Copernicus elevation model. |
| How do you guarantee no future information? | `01_FORECASTER_data_building/02_build_causal_training_dataset_with_18Z_weather_forecast.py` | Assembles the training table using only the 18:00 UTC weather run (no future data). |
| Where does the weather forecast come from? | `01_FORECASTER_data_building/03_download_MET_Norway_MEPS_18Z_forecasts.py` | Downloads the MET Norway MEPS weather forecasts. |
| Where does the weather forecast come from? | `01_FORECASTER_data_building/03b_MEPS_download_helper.py` | Helper used by the download script. |
| What is the baseline the models start from? | `01_FORECASTER_data_building/04_build_physics_plus_Chronos2_baseline.py` | Builds the baseline forecast (physics + Chronos-2) the 40 models correct. |
| What are u700 and v700? | `01_FORECASTER_data_building/05_extract_700hPa_wind_from_MEPS.py` | Extracts the upper-air wind inputs (u700, v700). |
| Is the forecast refreshed every hour? | `01_FORECASTER_data_building/06_expand_daily_forecasts_to_hourly_matrix.py` | Turns the daily midnight forecasts into the hourly table the simulation uses. |
| Show me how you trained the earlier models. | `02_FORECASTER_training/10_train_Successor_v2_forecaster.py` | Trains Successor v2 (33 causal inputs). |
| What is Candidate K? | `02_FORECASTER_training/11_train_Candidate_K_forecaster.py` | Trains Candidate K (35 inputs, baseline-conditioned). |
| Show me the code that trains the 40 models. | `02_FORECASTER_training/12_train_and_validate_Candidate_N1_and_N6.py` | Trains N1 (one tree) and N6 (25 additive + 15 specialist models) and blends them. |
| How do you know the model did not change? | `02_FORECASTER_training/13_freeze_and_export_N6_N1_models.py` | Freezes the models to files and records their SHA-256 fingerprints. |
| How do you know it is not overfitted? | `03_FORECASTER_evaluation/20_blind_2025_one_shot_test_all_models.py` | The one-time test on 2025 data that was never used for fitting. |
| How do you decide the battery reserve? | `03_FORECASTER_evaluation/21_conformal_safety_bound_and_battery_reserve_test.py` | Tests the 90% safety bound and the battery reserve it produces. |
| Have you tested forecaster and optimizer together? | `03_FORECASTER_evaluation/22_N6_closed_loop_simulation_test.py` | Closed-loop test of forecaster + optimizer together. |
| Can it run live? | `03_FORECASTER_evaluation/23_N6_live_operation_demo_with_optimizer.py` | Demonstrates one live operational cycle. |
| What is the assembler? | `03_FORECASTER_evaluation/24_N6_feature_assembler_and_live_pipeline.py` | The feature assembler: builds the 24x36 input table and checks arrival times. |
| Show me the forecaster code. | `04_FORECASTER_runtime_engine/N6_forecaster_engine__25_additive_15_specialists_blend_reserve.py` | The running forecaster: checks inputs, runs the 40 models, blends, makes the bound and the reserve. |
| How is clear-sky light calculated? | `04_FORECASTER_runtime_engine/physics_baseline_clear_sky_and_cloud_model.py` | Clear-sky (Ineichen) and cloud-based physical baseline. |
| What if the weather download fails? | `04_FORECASTER_runtime_engine/offline_fallback_forecaster.py` | Simple persistence + clear-sky fallback (prototype). |
| Why is the forecast shifted by one hour? | `04_FORECASTER_runtime_engine/forecast_to_optimizer_alignment_plus1h_shift.py` | Shifts the forecast one hour for the optimizer and fills the last step. |
| What checks sit between forecaster and optimizer? | `04_FORECASTER_runtime_engine/data_contract_forecast_bundle.py` | The checks on what the optimizer is given (24 steps, watts, no negatives). |
| Show me the optimizer / what is J1, J1b, J2, J3, J4? | `05_OPTIMIZER_GAP19/GAP19_optimizer_HiGHS_lexicographic_J1_to_J4.py` | The optimizer: 432 unknowns, 336 rules, five priorities solved in order. |
| What are you comparing against? | `05_OPTIMIZER_GAP19/basic_reactive_controller_baseline.py` | The basic controller we compare against (no forecast). |
| What does the optimizer know about the station? | `05_OPTIMIZER_GAP19/data_contract_station_state.py` | The battery / generator state handed to the optimizer every hour. |
| Is every scenario given the same inputs? Is wind real? | `06_SIMULATION_runs/00_shared_demand_and_wind_formulas.py` | The one place demand and wind are defined, identical for every scenario. |
| Show me the simulation. | `06_SIMULATION_runs/run_scenarios_2_3_4_rolling_horizon_simulation.py` | The core simulation loop used by scenarios 2, 3 and 4. |
| What is Scenario 3? | `06_SIMULATION_runs/run_scenario3_fixed_big_cushion.py` | Scenario 3 settings. |
| What is Scenario 4? | `06_SIMULATION_runs/run_scenario4_no_safety_cushion.py` | Scenario 4 settings (no safety cushion). |
| How was the baseline run? | `06_SIMULATION_runs/run_basic_controller_baseline_simulation.py` | Runs the basic controller on identical inputs. |
| How did you record the optimizer's decisions? | `06_SIMULATION_runs/run_POLARIS_with_full_decision_trace.py` | Runs POLARIS (or another forecaster) and saves every decision and plan. |
| How did you compute the 'what if' numbers? | `06_SIMULATION_runs/what_if_opposite_diesel_decision.py` | Re-solves each hour with the opposite diesel choice. |
| How is the Decision Map made? | `06_SIMULATION_runs/build_decision_map_data.py` | Prepares the data behind the Decision Map. |
| Where do the Proof page numbers come from? | `06_SIMULATION_runs/build_year_totals_for_proof_page.py` | Adds up each run's full-year diesel, hours, starts and lost load. |
| How did you choose those days? | `06_SIMULATION_runs/pick_days_worth_explaining.py` | Picks the eight highlighted days from the recorded run. |
| Is the weather real? | `07_DATA_inputs/real_weather_Nuolja_2024_hourly.csv` | REAL hourly measurements: air temperature, humidity, sunshine, soil temperature, rain, snow depth. |
| Is the sunshine real? | `07_DATA_inputs/real_weather_Nuolja_2024_hourly_5_variables.csv` | The 5-variable version used by the simulation. |
| Show me the raw station data. | `07_DATA_inputs/raw_Nuolja_station_2024_10_minute_readings.csv` | Raw 10-minute station file from the SITES data portal. |
| How do you know clear-sky light? | `07_DATA_inputs/clear_sky_and_sun_position_2024_hourly.csv` | Real sunshine next to calculated clear-sky light and sun position. |
| Show me the forecast data. | `07_DATA_inputs/MET_Norway_weather_forecasts_2024.csv` | Weather-model forecasts archive for 2024. |
| Show me the terrain data. | `07_DATA_inputs/mountain_horizon_profile_360_degrees.csv` | The mountain skyline around the station, 0-360 degrees. |
| Show me the forecaster's input table. | `07_DATA_inputs/forecaster_input_table_daily_36_clues_2024.parquet` | The 36-clue table, one forecast per day. |
| What did the simulation feed the forecaster? | `07_DATA_inputs/forecaster_input_table_hourly_used_in_simulation.parquet` | The hourly table the simulation reads (8,328 hours x 24 steps). |
| What is your train / test split? | `07_DATA_inputs/training_data_even_days.csv` | Even-numbered days: used for training. |
| What is your train / test split? | `07_DATA_inputs/test_data_odd_days.csv` | Odd-numbered days: held back for testing. |
| Is there any data the model never saw? | `07_DATA_inputs/blind_2025_data_never_used_for_fitting.csv` | The 2025 blind data. |
| Prove the split. | `07_DATA_inputs/train_test_split_list.csv` | Which origin belongs to which split. |
| Show me the model file. | `08_FORECASTER_frozen_models/N6_model_25_additive_15_specialists.joblib` | THE forecaster used in POLARIS. |
| What are the model settings? | `08_FORECASTER_frozen_models/N6_N1_manifest_settings_and_fingerprints.json` | Every setting of N6 and N1 (seeds, depth, features) and the SHA-256 fingerprints. |
| Show me the predictions vs reality. | `08_FORECASTER_frozen_models/N6_test_predictions_2024_odd_days.csv` | Predictions on the held-out odd days. |
| Show me the blind test. | `08_FORECASTER_frozen_models/N6_blind_2025_predictions.csv` | Predictions on the blind 2025 year. |
| What were the blind-test numbers? | `08_FORECASTER_frozen_models/N6_blind_2025_results.json` | The blind-test numbers. |
| Where are the full-year numbers? | `09_RESULTS_data/year_totals_all_scenarios_and_forecasters.json` | Full-year diesel, generator hours, starts, lost load, battery cycles per run. |
| Show me POLARIS's hourly output. | `09_RESULTS_data/POLARIS_hourly_results.json` | Hour-by-hour output of POLARIS. |
| Do you have tests? | `10_TESTS/test_forecaster_engine.py` | Tests the forecaster engine. |
| How do you test for leakage? | `10_TESTS/test_forecaster_no_future_data_ingestion.py` | Tests the input checks (no leakage, no missing values). |
| How do you test the reserve? | `10_TESTS/test_battery_reserve_policy.py` | Tests the reserve policy checks. |
| How do you test the optimizer? | `10_TESTS/test_optimizer_reserve_option_b.py` | Tests the optimizer's reserve objective. |
| Why N6? What else did you try? | `11_REPORTS_and_proofs/ALL_FORECASTERS_COMPARED_compendium.md` | Every candidate model tried, with results (the 14 variants). |
| How did N6 pass? | `11_REPORTS_and_proofs/N6_gates_and_blind_test_report.md` | The four gates N6 passed. |
| Can you run it in the field? | `11_REPORTS_and_proofs/N6_operational_readiness_report.md` | Data-arrival margins and live readiness. |
| Is any input from the future? | `11_REPORTS_and_proofs/N6_causal_data_contract_and_36_features.md` | Every one of the 36 inputs, its source and when it is available. |
| Prove it is causal. | `11_REPORTS_and_proofs/operational_causality_audit.md` | Independent audit that every input is available in time. |
| Who decided that? | `11_REPORTS_and_proofs/design_decisions_register.md` | Every owner design decision (including the one-hour shift). |

## Every file

| Folder | File | What it is | Original location | Size |
|---|---|---|---|---|
| 01_FORECASTER_data_building | `01_build_mountain_shading_terrain_features.py` | Builds the 4 mountain-shading inputs from the Copernicus elevation model. | `forecasting/stage7/stage7_5_terrain_horizon/build_terrain_features_2025.py` | 9 KB |
| 01_FORECASTER_data_building | `02_build_causal_training_dataset_with_18Z_weather_forecast.py` | Assembles the training table using only the 18:00 UTC weather run (no future data). | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/build_dataset_v2.py` | 13 KB |
| 01_FORECASTER_data_building | `03_download_MET_Norway_MEPS_18Z_forecasts.py` | Downloads the MET Norway MEPS weather forecasts. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/acquire_full.py` | 8 KB |
| 01_FORECASTER_data_building | `03b_MEPS_download_helper.py` | Helper used by the download script. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/fetcher.py` | 24 KB |
| 01_FORECASTER_data_building | `04_build_physics_plus_Chronos2_baseline.py` | Builds the baseline forecast (physics + Chronos-2) the 40 models correct. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/build_clean_stage4_baseline.py` | 12 KB |
| 01_FORECASTER_data_building | `05_extract_700hPa_wind_from_MEPS.py` | Extracts the upper-air wind inputs (u700, v700). | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/meps_wind_extractor.py` | 10 KB |
| 01_FORECASTER_data_building | `06_expand_daily_forecasts_to_hourly_matrix.py` | Turns the daily midnight forecasts into the hourly table the simulation uses. | `scratch/expand_rolling_matrix.py` | 3 KB |
| 02_FORECASTER_training | `10_train_Successor_v2_forecaster.py` | Trains Successor v2 (33 causal inputs). | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/train_successor_v2.py` | 21 KB |
| 02_FORECASTER_training | `11_train_Candidate_K_forecaster.py` | Trains Candidate K (35 inputs, baseline-conditioned). | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/train_candidate_k.py` | 26 KB |
| 02_FORECASTER_training | `12_train_and_validate_Candidate_N1_and_N6.py` | Trains N1 (one tree) and N6 (25 additive + 15 specialist models) and blends them. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/run_candidate_n_experiment.py` | 12 KB |
| 02_FORECASTER_training | `13_freeze_and_export_N6_N1_models.py` | Freezes the models to files and records their SHA-256 fingerprints. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/export_artifacts.py` | 14 KB |
| 03_FORECASTER_evaluation | `20_blind_2025_one_shot_test_all_models.py` | The one-time test on 2025 data that was never used for fitting. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/evaluate_2025_blind_oneshot.py` | 15 KB |
| 03_FORECASTER_evaluation | `21_conformal_safety_bound_and_battery_reserve_test.py` | Tests the 90% safety bound and the battery reserve it produces. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/evaluate_l2_conformal_ebr_2025.py` | 14 KB |
| 03_FORECASTER_evaluation | `22_N6_closed_loop_simulation_test.py` | Closed-loop test of forecaster + optimizer together. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/run_n6_closed_loop_simulation.py` | 17 KB |
| 03_FORECASTER_evaluation | `23_N6_live_operation_demo_with_optimizer.py` | Demonstrates one live operational cycle. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/demonstrate_live_operational_execution.py` | 17 KB |
| 03_FORECASTER_evaluation | `24_N6_feature_assembler_and_live_pipeline.py` | The feature assembler: builds the 24x36 input table and checks arrival times. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/n6_operational_pipeline.py` | 14 KB |
| 04_FORECASTER_runtime_engine | `N6_forecaster_engine__25_additive_15_specialists_blend_reserve.py` | The running forecaster: checks inputs, runs the 40 models, blends, makes the bound and the reserve. | `system/forecasting/implementations/n6_solar.py` | 26 KB |
| 04_FORECASTER_runtime_engine | `physics_baseline_clear_sky_and_cloud_model.py` | Clear-sky (Ineichen) and cloud-based physical baseline. | `system/forecasting/implementations/causal_nwp_physics.py` | 18 KB |
| 04_FORECASTER_runtime_engine | `offline_fallback_forecaster.py` | Simple persistence + clear-sky fallback (prototype). | `system/forecasting/implementations/baseline.py` | 11 KB |
| 04_FORECASTER_runtime_engine | `forecast_to_optimizer_alignment_plus1h_shift.py` | Shifts the forecast one hour for the optimizer and fills the last step. | `system/evaluation/n6_multi_origin_harness/adapters.py` | 110 KB |
| 04_FORECASTER_runtime_engine | `data_contract_forecast_bundle.py` | The checks on what the optimizer is given (24 steps, watts, no negatives). | `system/schemas/forecast_bundle.py` | 7 KB |
| 05_OPTIMIZER_GAP19 | `GAP19_optimizer_HiGHS_lexicographic_J1_to_J4.py` | The optimizer: 432 unknowns, 336 rules, five priorities solved in order. | `system/optimization/implementations/gap19_highs_native.py` | 26 KB |
| 05_OPTIMIZER_GAP19 | `basic_reactive_controller_baseline.py` | The basic controller we compare against (no forecast). | `system/optimization/implementations/reactive_hybrid_a2.py` | 9 KB |
| 05_OPTIMIZER_GAP19 | `data_contract_station_state.py` | The battery / generator state handed to the optimizer every hour. | `system/schemas/station_state.py` | 4 KB |
| 06_SIMULATION_runs | `00_shared_demand_and_wind_formulas.py` | The one place demand and wind are defined, identical for every scenario. | `scratch/sim_inputs.py` | 2 KB |
| 06_SIMULATION_runs | `run_scenarios_2_3_4_rolling_horizon_simulation.py` | The core simulation loop used by scenarios 2, 3 and 4. | `scratch/run_continuous_ui_rhc_scenario2.py` | 15 KB |
| 06_SIMULATION_runs | `run_scenario3_fixed_big_cushion.py` | Scenario 3 settings. | `scratch/run_continuous_ui_rhc_scenario3.py` | 1 KB |
| 06_SIMULATION_runs | `run_scenario4_no_safety_cushion.py` | Scenario 4 settings (no safety cushion). | `scratch/run_continuous_ui_rhc_scenario4.py` | 1 KB |
| 06_SIMULATION_runs | `run_basic_controller_baseline_simulation.py` | Runs the basic controller on identical inputs. | `scratch/run_reactive_matched.py` | 7 KB |
| 06_SIMULATION_runs | `run_POLARIS_with_full_decision_trace.py` | Runs POLARIS (or another forecaster) and saves every decision and plan. | `scratch/run_scenario2_full_trace.py` | 19 KB |
| 06_SIMULATION_runs | `what_if_opposite_diesel_decision.py` | Re-solves each hour with the opposite diesel choice. | `scratch/whatif_decisions.py` | 6 KB |
| 06_SIMULATION_runs | `build_decision_map_data.py` | Prepares the data behind the Decision Map. | `scratch/build_stakes_index.py` | 2 KB |
| 06_SIMULATION_runs | `build_year_totals_for_proof_page.py` | Adds up each run's full-year diesel, hours, starts and lost load. | `scratch/build_matched_aggregates.py` | 5 KB |
| 06_SIMULATION_runs | `pick_days_worth_explaining.py` | Picks the eight highlighted days from the recorded run. | `scratch/build_featured_days.py` | 6 KB |
| 06_SIMULATION_runs | `build_this_judge_pack.py` | Rebuilds this folder. | `scratch/build_judge_pack.py` | 20 KB |
| 07_DATA_inputs | `real_weather_Nuolja_2024_hourly.csv` | REAL hourly measurements: air temperature, humidity, sunshine, soil temperature, rain, snow depth. | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` | 1097 KB |
| 07_DATA_inputs | `real_weather_Nuolja_2024_hourly_5_variables.csv` | The 5-variable version used by the simulation. | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` | 757 KB |
| 07_DATA_inputs | `raw_Nuolja_station_2024_10_minute_readings.csv` | Raw 10-minute station file from the SITES data portal. | `data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv` | 3024 KB |
| 07_DATA_inputs | `clear_sky_and_sun_position_2024_hourly.csv` | Real sunshine next to calculated clear-sky light and sun position. | `data/POLARIS_v0_1_clearsky_decomposition.csv` | 758 KB |
| 07_DATA_inputs | `MET_Norway_weather_forecasts_2024.csv` | Weather-model forecasts archive for 2024. | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | 648 KB |
| 07_DATA_inputs | `mountain_horizon_profile_360_degrees.csv` | The mountain skyline around the station, 0-360 degrees. | `forecasting/stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv` | 8 KB |
| 07_DATA_inputs | `forecaster_input_table_daily_36_clues_2024.parquet` | The 36-clue table, one forecast per day. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet` | 934 KB |
| 07_DATA_inputs | `forecaster_input_table_hourly_used_in_simulation.parquet` | The hourly table the simulation reads (8,328 hours x 24 steps). | `scratch/hourly_rolling_candidate_matrix.parquet` | 2489 KB |
| 07_DATA_inputs | `training_data_even_days.csv` | Even-numbered days: used for training. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/train.csv` | 1795 KB |
| 07_DATA_inputs | `test_data_odd_days.csv` | Odd-numbered days: held back for testing. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/validation.csv` | 1784 KB |
| 07_DATA_inputs | `blind_2025_data_never_used_for_fitting.csv` | The 2025 blind data. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/blind.csv` | 3611 KB |
| 07_DATA_inputs | `train_test_split_list.csv` | Which origin belongs to which split. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/split_manifest.csv` | 115 KB |
| 08_FORECASTER_frozen_models | `N6_model_25_additive_15_specialists.joblib` | THE forecaster used in POLARIS. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` | 3332 KB |
| 08_FORECASTER_frozen_models | `N1_model_single_tree.joblib` | Candidate N1. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n1_model.joblib` | 82 KB |
| 08_FORECASTER_frozen_models | `K_model.joblib` | Candidate K. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib` | 184 KB |
| 08_FORECASTER_frozen_models | `Successor_v2_model.joblib` | Successor v2. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/artifacts_v2/candidate_f_successor_v2_model.joblib` | 173 KB |
| 08_FORECASTER_frozen_models | `N6_N1_manifest_settings_and_fingerprints.json` | Every setting of N6 and N1 (seeds, depth, features) and the SHA-256 fingerprints. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json` | 4 KB |
| 08_FORECASTER_frozen_models | `K_manifest_settings_and_features.json` | Candidate K settings and the 35 inputs. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/artifacts/CANDIDATE_K_MANIFEST.json` | 3 KB |
| 08_FORECASTER_frozen_models | `Successor_v2_manifest_settings_and_features.json` | Successor v2 settings and the 33 inputs. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/artifacts_v2/SUCCESSOR_MODEL_MANIFEST.json` | 3 KB |
| 08_FORECASTER_frozen_models | `N6_test_predictions_2024_odd_days.csv` | Predictions on the held-out odd days. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/validation_predictions.csv` | 718 KB |
| 08_FORECASTER_frozen_models | `N6_blind_2025_predictions.csv` | Predictions on the blind 2025 year. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/blind_2025_predictions.csv` | 1660 KB |
| 08_FORECASTER_frozen_models | `N6_blind_2025_results.json` | The blind-test numbers. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/BLIND_2025_RESULTS.json` | 4 KB |
| 09_RESULTS_data | `year_totals_all_scenarios_and_forecasters.json` | Full-year diesel, generator hours, starts, lost load, battery cycles per run. | `dashboard/public/data/matched/aggregates.json` | 4 KB |
| 09_RESULTS_data | `basic_controller_hourly_results.json` | Hour-by-hour output of the basic controller. | `dashboard/public/data/matched/reactive.json` | 2012 KB |
| 09_RESULTS_data | `POLARIS_hourly_results.json` | Hour-by-hour output of POLARIS. | `dashboard/public/data/trace/scenario2_initial_state_exact/series.json` | 3224 KB |
| 09_RESULTS_data | `Scenario2_plus30_rule_hourly_results.json` | Hour-by-hour output of Scenario 2 with the +30 kWh rule. | `dashboard/public/data/trace/scenario2/series.json` | 3224 KB |
| 09_RESULTS_data | `Scenario3_hourly_results.json` | Hour-by-hour output of Scenario 3. | `dashboard/public/data/trace/scenario3/series.json` | 3225 KB |
| 09_RESULTS_data | `Scenario4_hourly_results.json` | Hour-by-hour output of Scenario 4. | `dashboard/public/data/trace/scenario4/series.json` | 3190 KB |
| 09_RESULTS_data | `forecaster_physical_baseline_hourly_results.json` | Same optimizer, physical-baseline forecaster. | `dashboard/public/data/trace/cand_baseline/series.json` | 3221 KB |
| 09_RESULTS_data | `forecaster_Successor_v2_hourly_results.json` | Same optimizer, Successor v2 forecaster. | `dashboard/public/data/trace/cand_successor_v2/series.json` | 3222 KB |
| 09_RESULTS_data | `forecaster_Candidate_K_hourly_results.json` | Same optimizer, Candidate K forecaster. | `dashboard/public/data/trace/cand_k/series.json` | 3224 KB |
| 09_RESULTS_data | `forecaster_Candidate_N1_hourly_results.json` | Same optimizer, Candidate N1 forecaster. | `dashboard/public/data/trace/cand_n1/series.json` | 3224 KB |
| 09_RESULTS_data | `eight_highlighted_days.json` | The eight days worth explaining, with reasons. | `dashboard/public/data/featured_days.json` | 4 KB |
| 10_TESTS | `test_forecaster_engine.py` | Tests the forecaster engine. | `system/tests/test_n6_forecast_engine.py` | 11 KB |
| 10_TESTS | `test_forecaster_no_future_data_ingestion.py` | Tests the input checks (no leakage, no missing values). | `system/tests/test_n6_feature_ingestion_monitor.py` | 8 KB |
| 10_TESTS | `test_forecaster_decomposition_matches.py` | Checks the split-up forecaster gives identical numbers. | `system/tests/test_n6_decomposition_parity.py` | 10 KB |
| 10_TESTS | `test_forecaster_live_operation.py` | Tests a live operational cycle. | `system/tests/test_n6_live_operational_execution.py` | 7 KB |
| 10_TESTS | `test_clear_sky_physics_baseline.py` | Tests the physics baseline. | `system/tests/test_causal_nwp_physics.py` | 15 KB |
| 10_TESTS | `test_battery_reserve_policy.py` | Tests the reserve policy checks. | `system/tests/test_reserve_policy_guard.py` | 13 KB |
| 10_TESTS | `test_optimizer_reserve_option_b.py` | Tests the optimizer's reserve objective. | `system/tests/test_gap19_j2_option_b.py` | 8 KB |
| 10_TESTS | `test_forecaster_with_optimizer_integration.py` | Forecaster + optimizer integration test. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/test_n6_gap19_integration.py` | 14 KB |
| 10_TESTS | `test_hourly_rolling_horizon_adapters.py` | Tests the rolling-horizon hand-off. | `system/tests/test_n6_receding_horizon_adapters.py` | 66 KB |
| 10_TESTS | `test_per_step_safety_evaluation.py` | Tests the safety evaluation every step. | `system/tests/test_n6_per_step_safety_evaluation.py` | 16 KB |
| 11_REPORTS_and_proofs | `ALL_FORECASTERS_COMPARED_compendium.md` | Every candidate model tried, with results (the 14 variants). | `forecasting/reports/other/README_FORECASTING_RESEARCH_COMPENDIUM.md` | 44 KB |
| 11_REPORTS_and_proofs | `N6_gates_and_blind_test_report.md` | The four gates N6 passed. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/CANDIDATE_N_REPORT.md` | 13 KB |
| 11_REPORTS_and_proofs | `N6_operational_readiness_report.md` | Data-arrival margins and live readiness. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.md` | 9 KB |
| 11_REPORTS_and_proofs | `N6_causal_data_contract_and_36_features.md` | Every one of the 36 inputs, its source and when it is available. | `scratch/N6_CAUSAL_CONTRACT_AND_HOURLY_RHC_DESIGN_REPORT.md` | 30 KB |
| 11_REPORTS_and_proofs | `Candidate_K_experiment_report.md` | Why the baseline-conditioned model works. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/CANDIDATE_K_EXPERIMENT_REPORT.md` | 14 KB |
| 11_REPORTS_and_proofs | `operational_causality_audit.md` | Independent audit that every input is available in time. | `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/operational_availability_audit/operational_causality_audit.md` | 14 KB |
| 11_REPORTS_and_proofs | `design_decisions_register.md` | Every owner design decision (including the one-hour shift). | `docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md` | 263 KB |
