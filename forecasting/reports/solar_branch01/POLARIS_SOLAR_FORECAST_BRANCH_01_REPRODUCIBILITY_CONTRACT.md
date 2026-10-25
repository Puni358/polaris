# POLARIS_SOLAR_FORECAST_BRANCH_01 — REPRODUCIBILITY GOVERNANCE CONTRACT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Governance Authority:** Mandatory 20-Point POLARIS Model-Training Governance Rule  
**Status:** `ESTABLISHED / MANDATORY FOR ALL FUTURE TRAINING RUNS`  

---

## 1. Governance Mandate

From `POLARIS_SOLAR_FORECAST_BRANCH_01` onward, **NO model-training run is considered scientifically or operationally complete** unless the complete 20-point fitted-model reproducibility package is persisted in an immutable, isolated run directory and verified via an independent replay loop in a fresh process context.

---

## 2. Immutable Directory Architecture

Every training run receives a unique immutable run ID (`RUN_<YYYYMMDD_HHMMSS>_<SHORT_HASH>`) and an isolated artifact directory:

```
forecasting/
└── solar_branch_01/
    └── runs/
        └── RUN_20260921_120000_A1B2C3/
            ├── model/
            │   ├── fitted_model.joblib (or fitted_model.pt)
            │   └── model.sha256
            ├── data/
            │   ├── DATA_MANIFEST.json
            │   └── dataset_hashes.sha256
            ├── features/
            │   └── FEATURE_MANIFEST.json
            ├── environment/
            │   └── ENVIRONMENT.json
            ├── logs/
            │   └── training.log
            ├── predictions/
            │   ├── predictions.json
            │   ├── predictions.csv
            │   └── predictions.sha256
            ├── evaluation/
            │   └── metrics.json
            ├── manifests/
            │   └── MODEL_MANIFEST.json
            ├── replay/
            │   ├── replay_predictions.json
            │   └── REPLAY_REPORT.json
            └── REPRODUCTION_INSTRUCTIONS.md
```

### Absolute Rules:
1. **NO OVERWRITING**: Previous model-training runs must NEVER be overwritten, mutated, or deleted for storage capacity reasons.
2. **IMMUTABILITY**: Once written, run directories are set to read-only mode.
3. **FAIL-CLOSED**: If any serialization, hashing, manifest, or replay step fails, set `MODEL_TRAINING_STATUS = NOT_REPRODUCIBLE` and block EMS promotion.

---

## 3. Mandatory 34-Item Reproducibility Checklist

Every valid training run must record:

1. `fitted_model_binary`: Serialized model file (`.joblib` or `.pt`).
2. `model_id`: Unique string identifier.
3. `model_version`: Semantic version string.
4. `model_sha256`: SHA-256 hash of `fitted_model_binary`.
5. `training_dataset_id`: SHA-256 hash & path of training dataset.
6. `training_dataset_sha256`: SHA-256 hash of training CSV.
7. `validation_dataset_id`: Path of validation dataset.
8. `validation_dataset_sha256`: SHA-256 hash of validation CSV.
9. `test_dataset_id`: Path of test dataset.
10. `test_dataset_sha256`: SHA-256 hash of test CSV.
11. `complete_feature_list`: Exact ordered array of input feature names.
12. `exact_feature_ordering`: Immutable index mapping of features.
13. `preprocessing_configuration`: Scaler / encoder parameters.
14. `preprocessing_artifact_hash`: SHA-256 hash of fitted scaler file.
15. `hyperparameters`: Complete explicit dictionary of hyperparameters.
16. `random_seeds`: Seeds for Python `random`, `numpy`, `torch`, `sklearn`.
17. `training_command`: Exact CLI invocation string.
18. `configuration_file`: Complete YAML/JSON run configuration.
19. `source_code_commit`: Git commit hash (and dirty flag).
20. `relevant_source_code_sha256`: SHA-256 hash of training script.
21. `python_version`: `sys.version` string.
22. `operating_system_info`: OS platform, kernel, architecture.
23. `dependency_versions`: Explicit versions of `numpy`, `pandas`, `scipy`, `scikit-learn`, `torch`, `yaml`.
24. `training_timestamp`: ISO-8601 UTC timestamp of run initiation.
25. `train_val_test_split_definitions`: Explicit timestamp ranges.
26. `forecast_predictions`: Full prediction artifact (`predictions.json` / `.csv`).
27. `prediction_artifact_sha256`: SHA-256 hash of prediction artifact.
28. `evaluation_metrics`: MAE, RMSE, Bias overall and per-horizon.
29. `training_logs`: Complete stdout/stderr log file.
30. `data_provenance_manifest`: `DATA_MANIFEST.json`.
31. `causal_feature_manifest`: `FEATURE_MANIFEST.json`.
32. `model_manifest`: `MODEL_MANIFEST.json`.
33. `environment_manifest`: `ENVIRONMENT.json`.
34. `independent_replay_result`: Replay verification report and status.

---

## 4. Independent Replay Verification Protocol

After model training and serialization complete:
1. Launch a **fresh, isolated Python process**.
2. Load the fitted model from disk using `joblib.load()` or `torch.load()`.
3. Verify `model.sha256` checksum matches the serialized file bytes.
4. Load test dataset features matching `FEATURE_MANIFEST.json`.
5. Execute inference to generate replay predictions `Y_replay`.
6. Compare `Y_replay` against original `predictions.json` (`Y_original`):
   $$\max |Y_{	ext{replay}} - Y_{	ext{original}}| \le 	ext{atol}$$
   Default deterministic tolerance: $	ext{atol} = 1e-5$, $	ext{rtol} = 1e-5$.
7. Record the exact max absolute difference in `REPLAY_REPORT.json`.
8. Assign `MODEL_TRAINING_STATUS = REPRODUCIBLE` iff max difference $\le 	ext{atol}$ AND all hashes match.

---

## 5. EMS Promotion Firewall

No forecasting model may be promoted to EMS integration unless:
- `MODEL_TRAINING_STATUS == "REPRODUCIBLE"`
- `INDEPENDENT_REPLAY_PASS == True`
- `PROVENANCE_STATUS == "COMPLETE"`
- Separate EMS authorization has been granted by governance review.
