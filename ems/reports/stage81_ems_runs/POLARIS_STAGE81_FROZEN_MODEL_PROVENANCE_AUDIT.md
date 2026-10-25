# POLARIS — STAGE 8.1 FROZEN MODEL PROVENANCE + RECOVERY AUDIT
**Final Read-Only Investigation Before Any New Forecasting Branch**

---

### 1. EXECUTIVE FINDING

An exhaustive, read-only scientific provenance audit was conducted across the POLARIS project workspace (`/home/punith-bs/01polaris (Copy)`), adjacent project backup locations (`01polaris`, `01polaris_pre_spatial_backup`), repository git commit history across all branches/tags, research manifests, and historical audit reports.

**Core Audit Finding:**
> **Zero serialized fitted model state objects (`.pkl`, `.joblib`, `.pickle`, `.model`, `.onnx`, `.pt`, `.pth`, `.h5`, `.bin`, `.sav`) exist for Stage 8.1.**
> The original Stage 8.1 model (`HistGradientBoostingRegressor`) was instantiated and fitted in RAM during research execution (`run_official_odd_evaluation.py` / `run_stage8_1.py`) on EVEN origins, used to generate predictions on ODD origins to `stage8_1_official_odd_predictions.csv`, and then discarded from memory without serializing the fitted model estimator weights to disk.

**Recovery Classification:**
**`C = MODEL_REFERENCED_OR_HISTORICALLY_PRESENT_BUT_NOT_RECOVERABLE`**

- **Authoritative Frozen Model Found:** `NO`
- **Authoritative Frozen Model Recoverable:** `NO`
- **Candidate A Authorization:** `NOT_GRANTED`
- **Model Retraining:** `NOT AUTHORIZED`

---

### 2. PREVIOUS CAUSAL REPLAY GATE

The preceding Stage 8.1 Causal Rolling-Forecast Audit established:
- `CAUSAL_STAGE81_ROLLING_REPLAY = C (CAUSAL_REPLAY_NOT_REPRODUCIBLE_FROM_FROZEN_ARTIFACTS)`
- The frozen prediction CSV (`stage8_1_official_odd_predictions.csv`) contains static 24-hour forecasts at 48-hour origin spacing (173 ODD origins), leaving 87.5% of hourly MPC origins without predictions.
- The supporting feature sources for the frozen 37-feature pipeline are not available for arbitrary hourly MPC origins.
- Exact causal hourly replay could not be established without an authoritative fitted model runtime package.

The current audit strictly verifies whether an authoritative fitted Stage 8.1 model artifact was preserved in project backups or archives.

---

### 3. SEARCH SCOPE

The read-only provenance search encompassed project-scoped locations ONLY:
1. **Active Repository Workspace:** `/home/punith-bs/01polaris (Copy)` (including `stage7/stage8/`, `stage4/`, `stage6/`, `chronos/`, `scratch/`, `experiments/`).
2. **Adjacent Project Directories:**
   - `/home/punith-bs/01polaris`
   - `/home/punith-bs/01polaris_pre_spatial_backup`
3. **Git History & Repositories:** Full commit history (`git log --all`), file deletion logs (`git log --name-only`), and string content matches (`git log -S`).
4. **Project Manifests & Inventory Files:** `POLARIS_STAGE8_1_CHAMPION_MANIFEST.json`, `POLARIS_REPRODUCIBILITY_INVENTORY.json`, pre-Opus verification logs, and forensic audit reports.

---

### 4. CANDIDATE MODEL ARTIFACTS FOUND

The extension scan (`*.pkl`, `*.joblib`, `*.pickle`, `*.model`, `*.onnx`, `*.pt`, `*.pth`, `*.h5`, `*.bin`, `*.sav`) across the entire workspace and adjacent project directories identified **zero** Scikit-Learn / Stage 8.1 model files.

The only `.bin` files discovered in the workspace belong to unrelated HuggingFace Chronos time-series foundation model fine-tuning experiments:
1. `chronos/polaris_lora_1000/checkpoint-100/training_args.bin` (5,265 bytes)
2. `chronos/polaris_lora_500/checkpoint-100/training_args.bin` (5,265 bytes)
3. `chronos/polaris_lora_expB_500/checkpoint-300/training_args.bin` (5,265 bytes)
4. `chronos/polaris_lora_expC_500/checkpoint-200/training_args.bin` (5,265 bytes)
5. `chronos/polaris_lora_pilot/checkpoint-10/training_args.bin` (5,265 bytes)

**Zero Stage 8.1 fitted model estimators exist on disk.**

---

### 5. CANDIDATE MODEL HASHES

No candidate Stage 8.1 model artifacts exist to hash.

For immutable baseline compliance, the hashes of the official Stage 8.1 artifacts were verified:

| Artifact Path | SHA-256 Hash | Status |
| :--- | :--- | :--- |
| `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv` | `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707` | **FROZEN & VERIFIED** |
| `stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv` | `e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541` | **FROZEN & VERIFIED** |
| `stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py` | `fbab8b975e5f35eb270a4a946bbfad99c924bcbe84d8fbcfc3fc38ffeb95ae76` | **FROZEN & VERIFIED** |
| `stage7/stage8/stage8_1_700hpa_wind/run_official_odd_evaluation.py` | `051877ee7ebbfeb4380eb9a5ed6ff538c6444aa95bbf9fd6fec3fa8cce71ecfb` | **FROZEN & VERIFIED** |
| `stage7/stage8/stage8_1_700hpa_wind/POLARIS_STAGE8_1_CHAMPION_MANIFEST.json` | `c7d7e79929e74ce6603a11e2efefce616616e257007f3006bb4ebdb49d794cb5` | **FROZEN & VERIFIED** |

---

### 6. PROVENANCE EVIDENCE

Static analysis of `run_official_odd_evaluation.py` (lines 190–215) and `run_stage8_1.py` proves the exact lifetime of the Stage 8.1 model estimator:
1. `model_e1 = HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)` is instantiated in Python RAM.
2. `model_e1.fit(X_tr_st81, res_tr)` fits the model on daytime EVEN origin feature rows.
3. `pred_res_e1 = model_e1.predict(X_odd_st81)` predicts daytime ODD origin residuals in RAM.
4. `df_odd_preds["pred_stage8_1_candidate"]` writes predictions to `stage8_1_official_odd_predictions.csv`.
5. Neither `joblib.dump()` nor `pickle.dump()` was ever called on `model_e1`.
6. Python process execution terminated, releasing the fitted model parameters from RAM.

---

### 7. GIT / HISTORY EVIDENCE

`git log --all --name-only` across all commits, branches, and tags was searched for `.pkl`, `.joblib`, `.pickle`, `.model`, and `.bin` filenames.

- **Historical Model Files Committed to Git:** `0`
- **Historical Model File Deletions:** `0`
- **Result:** No Stage 8.1 serialized model binary was ever committed or tracked in Git history.

---

### 8. CHECKPOINT / ARCHIVE EVIDENCE

The champion manifest `POLARIS_STAGE8_1_CHAMPION_MANIFEST.json` records:
- `manifest_version`: `"1.0"`
- `model_family`: `"HistGradientBoostingRegressor"`
- `hyperparameters`: `loss="absolute_error"`, `max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `random_state=42`
- `feature_count`: `37`
- `status`: `"FROZEN_OPERATIONAL_CHAMPION"`

The manifest records hyperparameters and offline evaluation metrics, but contains no reference to a binary model weight artifact path or binary model checksum.

Prior audit documents (`STAGE8_17A_FINAL_ARTIFACT_RECOVERY_AUDIT.md`, `STAGE8_17A_REPRODUCTION_FORENSIC_AUDIT.md`) also explicitly confirm:
- `Serialized Model Checkpoint (*.pkl/*.joblib): NOT RECOVERED.`

---

### 9. EXTERNAL ARTIFACT REFERENCES

Project documentation and research logs were inspected for references to external artifact stores (Google Drive, HuggingFace, AWS S3, private servers):
- **External Model Storage References:** `None`
- **External Accounts/Urls Specified:** `None`

The original research model existed solely as transient RAM state during the evaluation run.

---

### 10. EXACT FROZEN-MODEL IDENTITY ASSESSMENT

- **Does a fitted binary model object exist?** `NO`
- **Can the exact frozen fitted model state be loaded?** `NO`
- **Can prediction outputs be re-generated without retraining?** `NO`
- **Can arbitrary hourly MPC origins be evaluated without a fitted model?** `NO`

---

### 11. RECOVERY CLASSIFICATION

Formally classified as:

**`C = MODEL_REFERENCED_OR_HISTORICALLY_PRESENT_BUT_NOT_RECOVERABLE`**

*Rationale:* The existence of the Stage 8.1 model instance is historically established via code (`run_official_odd_evaluation.py`), hyperparameters (`POLARIS_STAGE8_1_CHAMPION_MANIFEST.json`), and output predictions (`stage8_1_official_odd_predictions.csv`), but the actual binary fitted model bytes were never saved to disk and cannot be recovered from any project artifact or backup.

---

### 12. MISSING ARTIFACTS

The following critical runtime artifacts are missing and unavailable:
1. `stage8_1_model.joblib` / `stage8_1_model.pkl` (Fitted HistGradientBoostingRegressor estimator object).
2. Arbitrary hourly MPC origin feature extraction runtime package for the 37 steering-wind features.

---

### 13. WHAT REMAINS SCIENTIFICALLY FROZEN

1. **Frozen Offline Prediction Benchmark:** `stage8_1_official_odd_predictions.csv` (SHA-256: `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`) remains fully valid and immutable for offline evaluation on its 173 ODD 24-hour origins.
2. **Frozen Feature Matrix:** `stage8_1_full_37_feature_matrix_2024.csv` (SHA-256: `e7b304186eef6c7e6135ba7a9aa9d20a4d2f32eeb9b65085ef8e10e34ea0b541`) remains fully valid and immutable.
3. **Frozen 173-Trajectory Experiment Results:** The historical 173-trajectory EMS paired run remains frozen and unchanged.

---

### 14. CANDIDATE-A STATUS

Candidate A (receding-horizon semantics correction) requires evaluating Stage 8.1 forecasts at hourly MPC origins $t = 0, 1, 2, \dots, 23$.

Because:
1. No fitted Stage 8.1 model artifact exists to evaluate hourly origins, and
2. Retraining a model without separate governance authorization is strictly forbidden,

**`CANDIDATE_A_AUTHORIZATION = NOT_GRANTED`**
**`CANDIDATE_A = BLOCKED`**

---

### 15. REQUIRED FUTURE GOVERNANCE DECISION

Because the frozen Stage 8.1 model state was never saved to disk and exact causal hourly replay cannot be established from frozen artifacts:

1. **Formal Closure:** The frozen Stage 8.1 rolling-replay path is formally closed.
2. **New Forecasting Branch Required:** Any future attempt to generate hourly receding-horizon solar forecasts for EMS integration requires a **NEW forecasting branch**.
3. **Governance Gate for New Branch:** A new forecasting branch must include:
   - Explicit project governance approval for model fitting/training.
   - Complete end-to-end feature extraction for all hourly origins.
   - Mandatory serialization of fitted model estimators (`.joblib` / `.pkl`) with SHA-256 tracking in champion manifests prior to any EMS testing.
