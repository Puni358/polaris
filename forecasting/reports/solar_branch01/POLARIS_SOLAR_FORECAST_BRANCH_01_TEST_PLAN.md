# POLARIS_SOLAR_FORECAST_BRANCH_01 — PHASE 2 TEST PLAN

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 2 GOVERNED IMPLEMENTATION SPECIFICATION`  
**Status:** `COMPLETE & READY FOR IMPLEMENTATION`  

---

## 1. Overview & Test Scope

This document specifies the 16 mandatory unit and integration tests that must be implemented and pass in `system/tests/test_model_reproducibility_governance.py` prior to granting model training authorization.

---

## 2. Mandatory Test Suite Specifications

### Test 1: `test_timestamp_validation`
- **Objective**: Verify that `TimestampNormalizer` parses ISO-8601 strings into UTC datetime objects and rejects non-UTC or non-monotonic timestamp series.
- **Expected Outcome**: `ModelGovernanceError` raised on timezone mismatch or non-increasing index.

### Test 2: `test_causal_availability`
- **Objective**: Verify that all feature builder outputs satisfy $t_{	ext{available}} \le t$.
- **Expected Outcome**: Test fails if any feature consumes future target values ($t' > t$).

### Test 3: `test_nwp_issue_selection`
- **Objective**: Verify that `NWPSelector` selects $t_{\text{issue}} = \max(	ext{issue\_time} \le t)$ for origins $t \in \{00:00, 03:00, 06:00, 12:00, 18:00\}$ UTC.
- **Expected Outcome**: Selects 00:00 UTC issue run; rejects future issue runs ($t_{\text{issue}} > t$).

### Test 4: `test_nwp_lead_mapping`
- **Objective**: Verify that `NWPLeadMapper` correctly computes $H_{\text{effective}} = H + (t - t_{\text{issue}})$.
- **Expected Outcome**: Effective lead ranges match `POLARIS_SOLAR_FORECAST_BRANCH_01_NWP_CAUSAL_CONTRACT.csv`.

### Test 5: `test_24h_target_alignment`
- **Objective**: Verify that `TargetBuilder` produces $Y(t) = [SW\_IN(t+1), \dots, SW\_IN(t+24)]$ without $t+0$ overlap.
- **Expected Outcome**: $Y(t)$ array shape is $(24,)$, target timestamps range from $t+1h$ to $t+24h$.

### Test 6: `test_split_boundary_protection`
- **Objective**: Verify that `EmbargoFilter` excludes origins $t \in [\text{split\_end} - 24h, \text{split\_end}]$ from train/val splits.
- **Expected Outcome**: Zero sample target horizons cross train/val or val/test boundaries.

### Test 7: `test_feature_schema`
- **Objective**: Verify that `FeatureBuilder` produces feature matrix $X(t)$ matching exact column names and order in `FEATURE_MANIFEST.json`.
- **Expected Outcome**: Columns match `['ctx_last_obs', 'ctx_mean_3h', ..., 'v700']` (16 features).

### Test 8: `test_deterministic_feature_generation`
- **Objective**: Verify that running `FeatureBuilder` twice on identical inputs yields identical numerical values.
- **Expected Outcome**: `np.array_equal(X1, X2) == True`.

### Test 9: `test_missing_data_fail_closed`
- **Objective**: Verify that missing source data or NaN values trigger immediate fail-closed behavior.
- **Expected Outcome**: Raises `ModelGovernanceError`; sets `MODEL_TRAINING_STATUS = NOT_REPRODUCIBLE`.

### Test 10: `test_model_serialization`
- **Objective**: Verify `save_model()` serializes fitted estimators to `.joblib` / `.pt` and writes `model.sha256`.
- **Expected Outcome**: `model.sha256` matches byte-level SHA-256 hash of serialized file.

### Test 11: `test_model_loading`
- **Objective**: Verify that serialized model binaries load cleanly from disk via `joblib.load()` or `torch.load()`.
- **Expected Outcome**: Loaded model predict method executes without error.

### Test 12: `test_prediction_shape_and_order`
- **Objective**: Verify that `save_predictions()` validates column names, row ordering, and row counts.
- **Expected Outcome**: Writes `predictions.json` and `predictions.csv` with SHA-256 checksum file.

### Test 13: `test_sha_verification`
- **Objective**: Verify that tampering with any serialized artifact (modifying 1 byte) causes SHA-256 verification failure.
- **Expected Outcome**: `compute_file_sha256()` mismatch raises `ModelGovernanceError`.

### Test 14: `test_replay_equivalence`
- **Objective**: Verify process-isolated `verify_independent_replay()` loads model from disk in a separate process and matches original predictions within $\text{atol}=1e-5$.
- **Expected Outcome**: Returns `success=True` and updates status to `REPRODUCIBLE`.

### Test 15: `test_manifest_completeness`
- **Objective**: Verify that `ManifestGenerator` outputs `MODEL_MANIFEST.json`, `DATA_MANIFEST.json`, `FEATURE_MANIFEST.json`, `ENVIRONMENT.json`, and `REPRODUCTION_INSTRUCTIONS.md`.
- **Expected Outcome**: All 4 master manifests conform to `POLARIS_SOLAR_FORECAST_BRANCH_01_MODEL_RUN_MANIFEST_SCHEMA.json`.

### Test 16: `test_8_worker_and_resource_logging`
- **Objective**: Verify worker count allocation (default 8) and hardware/thermal logging in `ENVIRONMENT.json`.
- **Expected Outcome**: `worker_count == 8` and system platform details recorded.
