# POLARIS Solar Forecast Branch 01 — Implementation README

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 3 GOVERNED IMPLEMENTATION`  

## Module Architecture

- `implementation/data_loader.py`: Deterministic source loading & fail-closed validation.
- `implementation/timestamp_normalizer.py`: UTC ISO-8601 timestamp normalizer.
- `implementation/source_validator.py`: Fail-closed schema & SHA-256 hash validator.
- `implementation/target_builder.py`: Ground-truth 24-step target matrix constructor \(Y(t) = [SW\_IN(t+1)...SW\_IN(t+24)]\).
- `implementation/origin_generator.py`: Contract-derived MPC origin generator.
- `implementation/nwp_selector.py`: Strictly causal NWP issue selector (\(t_{\text{issue}} \le t\)).
- `implementation/nwp_lead_mapper.py`: Effective NWP lead mapper (\(H_{\text{effective}} = h + (t - t_{\text{issue}})\)).
- `implementation/astronomical_features.py`: Deterministic solar elevation, zenith, azimuth, cyclics.
- `implementation/lookback_features.py`: Causal historical SW_IN lookback window features.
- `implementation/clearsky_features.py`: Physical clear-sky reference features.
- `implementation/feature_matrix_builder.py`: Deterministic feature matrix assembler \(X(t)\).
- `implementation/split_builder.py`: Chronological split builder with 24h embargo protection.
- `implementation/baseline_interface.py`: Abstract & reference baseline predictors.
- `implementation/model_interface.py`: Generic model interface & `TEST_ONLY` mock model.
- `implementation/preprocessing_interface.py`: Scaler contract with zero test leakage.
- `implementation/model_serializer.py`: Deterministic serialization & SHA-256 calculation.
- `implementation/hash_generator.py`: Central SHA-256 utility functions.
- `implementation/manifest_generator.py`: Draft-07 JSON Schema manifest builder.
- `implementation/replay_runner.py`: Process-isolated replay verification runner.
- `implementation/evaluation_interface.py`: Authorized MAE & RMSE evaluation metrics.
- `implementation/governance_integration.py`: Model reproducibility framework state machine wrapper.

## Execution Rules

- **No Model Training**: `fit()` must NOT be called on a real forecasting model.
- **No Real Inference**: Zero scientific predictions generated. `TEST_ONLY` mock models permitted for pipeline infrastructure tests.
- **Stage 8.1 Firewall**: Stage 8.1 champion files remain 100% frozen.
