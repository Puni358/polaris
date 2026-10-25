# POLARIS Stage 6.1 — MEPS Ensemble Evaluation Directory

This directory contains the artifacts for Stage 6.1 MEPS Ensemble Extraction, Information Content Audit, and Controlled GBDT Experiment.

## Artifact Manifest
1. `README.md`: Directory overview and manifest.
2. `stage6_1_experiment_plan.md`: Detailed experiment design document.
3. `meps_ensemble_extraction.py`: Extraction and causality audit script.
4. `run_stage6_1_audit_and_experiment.py`: Master experiment execution script.
5. `ensemble_feature_summary.csv`: Summary statistics per origin x horizon.
6. `ensemble_causality_audit.csv`: Causality audit log across 262,800 member-hours.
7. `residual_information_audit.csv`: Spearman rank correlations vs Stage 5.2 residuals.
8. `even_cv_results.csv`: EVEN 5-fold CV aggregate performance comparison.
9. `per_fold_results.csv`: Per-fold CV MAE deltas and breakdown.
10. `per_horizon_results.csv`: Per-horizon H1-H24 MAE breakdown.
11. `final_summary.txt`: Executive summary text and final decision lock.
