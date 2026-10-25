# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING REPRODUCIBILITY CHECKLIST

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Governance Standard:** Permanent POLARIS Model-Training Governance Rule  
**Status:** `ESTABLISHED / MANDATORY FOR FUTURE TRAINING AUTHORIZATION`  

---

## 1. 20 Mandatory Provenance Categories + Metadata Checklist

Before any future training run can be marked `MODEL_TRAINING_STATUS = REPRODUCIBLE`, all 34 checklist items must pass:

- [ ] **1. Serialized Fitted Model**: Binary `.joblib` / `.pt` saved in `model/fitted_model.*`.
- [ ] **2. Model SHA-256**: `model.sha256` matching byte-level hash.
- [ ] **3. Model ID & Class**: Recorded in `MODEL_MANIFEST.json`.
- [ ] **4. Model Version**: Semantic version string recorded.
- [ ] **5. Hyperparameters**: Complete explicit dictionary in `MODEL_MANIFEST.json`.
- [ ] **6. Random Seeds**: Seeds for Python `random`, `numpy`, `torch` recorded.
- [ ] **7. Ordered Feature List**: `feature_names` array in `FEATURE_MANIFEST.json`.
- [ ] **8. Feature Index Ordering**: Immutable index mapping in `FEATURE_MANIFEST.json`.
- [ ] **9. Preprocessing Scaler**: Fitted scaler saved and hashed.
- [ ] **10. Scaler Parameters**: Mean/std arrays saved in `FEATURE_MANIFEST.json`.
- [ ] **11. Training Dataset Path**: Source path in `DATA_MANIFEST.json`.
- [ ] **12. Training Dataset SHA-256**: SHA-256 hash recorded in `DATA_MANIFEST.json`.
- [ ] **13. Validation Dataset Path**: Source path in `DATA_MANIFEST.json`.
- [ ] **14. Validation Dataset SHA-256**: SHA-256 hash recorded in `DATA_MANIFEST.json`.
- [ ] **15. Test Dataset Path**: Source path in `DATA_MANIFEST.json`.
- [ ] **16. Test Dataset SHA-256**: SHA-256 hash recorded in `DATA_MANIFEST.json`.
- [ ] **17. Pre-Flight Check Status**: `dataset_preflight_check()` passed prior to fitting.
- [ ] **18. Chronological Split Definitions**: Train (Jan-Aug), Val (Sep-Oct), Test (Nov-Dec) recorded.
- [ ] **19. 24h Embargo Filter**: Boundary origins $[split\_end - 24h, split\_end]$ excluded.
- [ ] **20. Target Definition**: $SW\_IN$ in $\text{W/m}^2$, 1h UTC resolution recorded.
- [ ] **21. Forecast Horizon Semantics**: Complete 24h sequence $Y = [SW\_IN(t+1)\dots SW\_IN(t+24)]$.
- [ ] **22. Python & OS Environment**: Python version, platform, architecture in `ENVIRONMENT.json`.
- [ ] **23. Exact CLI Command**: Executable path and CLI args recorded in `ENVIRONMENT.json`.
- [ ] **24. Git Commit & Branch**: `commit_hash`, `branch`, `is_dirty` in `ENVIRONMENT.json`.
- [ ] **25. Git Diff Patch**: `git_diff.patch` saved if `is_dirty == True`.
- [ ] **26. Script SHA-256 Hashes**: Hashes for training, feature, eval, replay scripts.
- [ ] **27. Execution Metadata**: 8-worker count, live progress, thermal state in `ENVIRONMENT.json`.
- [ ] **28. Persistent Training Logs**: `logs/training.log` created and populated.
- [ ] **29. Evaluation Metrics**: MAE, RMSE, Bias overall and per-horizon in `metrics.json`.
- [ ] **30. Prediction Artifact**: `predictions.json` & `predictions.csv` created with SHA-256.
- [ ] **31. Reproduction Instructions**: `REPRODUCTION_INSTRUCTIONS.md` generated.
- [ ] **32. Process-Isolated Independent Replay**: Replay process loads model from disk and runs inference.
- [ ] **33. Replay Equivalence**: Max absolute difference $\le \text{atol}=1e-5$.
- [ ] **34. Governed State Transition**: Linear transition to `MODEL_TRAINING_STATUS = REPRODUCIBLE`.
