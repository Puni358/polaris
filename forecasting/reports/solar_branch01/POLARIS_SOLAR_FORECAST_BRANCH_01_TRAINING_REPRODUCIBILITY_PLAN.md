# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING REPRODUCIBILITY PLAN

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `TRAINING REPRODUCIBILITY PLAN`  
**Status:** `GOVERNED REPRODUCIBILITY CONTRACT`  

---

## 1. MODEL_RUN_MANIFEST_SCHEMA & 34-Item Reproducibility Checklist Framework

For EVERY training run, regardless of model type or size, the execution engine MUST generate the complete reproducibility package conforming to `MODEL_RUN_MANIFEST_SCHEMA.json` and verify all items in `34-item TRAINING_REPRODUCIBILITY_CHECKLIST.md`:

1. **Serialize Fitted Model**: Store `model.joblib`.
2. **Model SHA-256**: Calculate byte-level SHA-256 of `model.joblib`.
3. **Training Config**: Save exact hyperparameter dictionary and random seeds (`42`).
4. **Hyperparameters**: Record loss, max_depth, learning_rate, l2_regularization.
5. **Random Seeds**: Record global numpy, python, and model seeds.
6. **Feature Names & Order**: Record exact 18-element ordered feature list.
7. **Feature Code SHA-256**: Record SHA-256 of `feature_matrix_builder.py` and feature modules.
8. **Dataset Identity & SHA-256**: Record dataset filenames and SHA-256 hashes.
9. **Temporal Split Specification**: Record exact train/val/test UTC datetime ranges.
10. **Target & Horizon Semantics**: Record $Y(t) = [SW\_IN(t+1)...SW\_IN(t+24)]$.
11. **Runtime & Dependencies**: Record Python version, OS, numpy, pandas, scikit-learn versions.
12. **Git Commit & State**: Record Git commit SHA, branch, clean/dirty state, and diff SHA.
13. **Training Logs**: Save stdout/stderr execution log file.
14. **Validation Metrics**: Record MAE and RMSE across all 24 horizons.
15. **Prediction Hashes**: Record SHA-256 hash of validation/test predictions.
16. **MODEL_RUN_MANIFEST.json**: Machine-readable JSON conforming to `MODEL_RUN_MANIFEST_SCHEMA.json`.
17. **DATA_MANIFEST.json**: Machine-readable dataset provenance manifest.
18. **FEATURE_MANIFEST.json**: Machine-readable feature pipeline provenance manifest.
19. **ENVIRONMENT.json**: System, OS, CPU, RAM hardware environment manifest.
20. **REPRODUCTION_INSTRUCTIONS.md**: Standalone document detailing exact CLI command to replay training.

---

## 2. Independent Replay Protocol

- **Separate Process**: Replay MUST execute in an independent Python subprocess (`multiprocessing`).
- **Disk Load**: Model binary and scaler binary loaded strictly from disk (zero in-memory object reuse).
- **Tolerance**:
  \[\text{atol} = 1e-5, \quad \text{rtol} = 1e-5\]
- **Replay Report**: Writes `REPLAY_REPORT.json` recording prediction bit-level comparison.

---

## 3. State Machine Transitions

`IN_PROGRESS` $\rightarrow$ `TRAINING_COMPLETE` $\rightarrow$ `SERIALIZATION_VERIFIED` $\rightarrow$ `REPLAY_VERIFIED` $\rightarrow$ `REPRODUCIBLE`
