"""
Unit and integration tests for POLARIS Model Reproducibility & Governance Framework.
Verifies the 20-point governance rule, 11 user amendments, dataset pre-flight checks,
state machine transitions, process-isolated replay runner, and EMS promotion firewall.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path

import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from system.governance import (
    PolarisModelGovernanceManager,
    ModelGovernanceError,
    ModelTrainingStatus,
    assert_governance_reproducible
)


@pytest.fixture
def temp_workspace():
    """Creates a temporary workspace directory for governance tests."""
    temp_dir = Path(tempfile.mkdtemp(prefix="polaris_test_gov_"))
    
    # Create sample dataset CSV for pre-flight testing
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = data_dir / "sample_dataset.csv"
    
    np.random.seed(42)
    n_samples = 100
    df_sample = pd.DataFrame({
        "timestamp": [f"2024-01-01T{h:02d}:00:00Z" for h in range(n_samples)],
        "feat_1": np.random.randn(n_samples),
        "feat_2": np.random.randn(n_samples),
        "actual_SW_IN": np.random.uniform(0, 800, n_samples)
    })
    df_sample.to_csv(sample_csv, index=False)
    
    yield temp_dir, sample_csv
    
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_end_to_end_governance_flow(temp_workspace):
    temp_dir, sample_csv = temp_workspace
    
    branch_id = "POLARIS_SOLAR_FORECAST_BRANCH_01"
    model_id = "test_ridge_solar_v1"
    model_type = "RidgeRegression"
    feature_names = ["feat_1", "feat_2"]
    
    # 1. Run model training within governance manager
    with PolarisModelGovernanceManager(
        branch_id=branch_id,
        model_id=model_id,
        model_type=model_type,
        base_dir=temp_dir,
        num_workers=8,
        worker_reason="Standard 8-worker parallel allocation"
    ) as gov:
        # Pre-flight dataset check
        preflight_info = gov.dataset_preflight_check(
            dataset_path=sample_csv,
            expected_rows=100,
            expected_cols=4,
            feature_order=feature_names,
            target_col="actual_SW_IN"
        )
        assert preflight_info["preflight_status"] == "PASS"
        
        # Record hyperparams & seeds
        hyperparams = {"alpha": 1.0, "solver": "auto"}
        seeds = {"random": 42, "numpy": 42}
        gov.record_hyperparameters_and_seeds(hyperparams, seeds)
        
        # Record feature contract & splits
        gov.record_feature_contract(feature_names, target_col="actual_SW_IN")
        gov.record_splits(
            train_range=("2024-01-01T00:00:00Z", "2024-01-01T10:00:00Z"),
            val_range=("2024-01-01T11:00:00Z", "2024-01-01T15:00:00Z"),
            test_range=("2024-01-01T16:00:00Z", "2024-01-01T23:00:00Z")
        )
        
        # Train model
        df = pd.read_csv(sample_csv)
        X = df[feature_names].values
        y = df["actual_SW_IN"].values
        
        model = Ridge(alpha=1.0, random_state=42)
        model.fit(X, y)
        preds = model.predict(X)
        
        # Save model, predictions, metrics
        gov.save_model(model, "fitted_model.joblib")
        assert gov.status == ModelTrainingStatus.SERIALIZATION_VERIFIED
        
        df_preds = pd.DataFrame({
            "forecast_origin": df["timestamp"].tolist(),
            "target_timestamp": df["timestamp"].tolist(),
            "horizon_hour": [1] * len(df),
            "predicted_SW_IN": preds,
            "actual_SW_IN": y
        })
        gov.save_predictions(df_preds)
        gov.save_metrics({"mae": 12.34, "rmse": 18.56})
        
        # Process-isolated replay verification
        replay_res = gov.execute_independent_replay(
            test_data_path=sample_csv,
            atol=1e-5,
            rtol=1e-5
        )
        assert replay_res["success"] is True
        assert gov.status == ModelTrainingStatus.REPRODUCIBLE

    # 2. Verify files and manifests in run directory
    run_dir = gov.run_dir
    assert (run_dir / "model" / "fitted_model.joblib").exists()
    assert (run_dir / "model" / "model.sha256").exists()
    assert (run_dir / "manifests" / "MODEL_MANIFEST.json").exists()
    assert (run_dir / "data" / "DATA_MANIFEST.json").exists()
    assert (run_dir / "features" / "FEATURE_MANIFEST.json").exists()
    assert (run_dir / "environment" / "ENVIRONMENT.json").exists()
    assert (run_dir / "predictions" / "predictions.json").exists()
    assert (run_dir / "predictions" / "predictions.sha256").exists()
    assert (run_dir / "replay" / "REPLAY_REPORT.json").exists()
    assert (run_dir / "REPRODUCTION_INSTRUCTIONS.md").exists()

    # 3. Assert EMS promotion check
    assert assert_governance_reproducible(run_dir) is True


def test_preflight_check_failure_aborts_run(temp_workspace):
    temp_dir, sample_csv = temp_workspace
    
    with pytest.raises(ModelGovernanceError, match="Pre-flight row count mismatch"):
        with PolarisModelGovernanceManager(
            branch_id="POLARIS_SOLAR_FORECAST_BRANCH_01",
            model_id="test_fail",
            model_type="Ridge",
            base_dir=temp_dir
        ) as gov:
            gov.dataset_preflight_check(
                dataset_path=sample_csv,
                expected_rows=9999,  # Mismatch (real count is 100)
                target_col="actual_SW_IN"
            )

    assert gov.status == ModelTrainingStatus.NOT_REPRODUCIBLE


def test_replay_prediction_mismatch_fails_governance(temp_workspace):
    temp_dir, sample_csv = temp_workspace
    
    with pytest.raises(ModelGovernanceError, match="Replay prediction length mismatch|Replay tolerance exceeded"):
        with PolarisModelGovernanceManager(
            branch_id="POLARIS_SOLAR_FORECAST_BRANCH_01",
            model_id="test_replay_fail",
            model_type="Ridge",
            base_dir=temp_dir
        ) as gov:
            gov.record_feature_contract(["feat_1", "feat_2"])
            df = pd.read_csv(sample_csv)
            X = df[["feat_1", "feat_2"]].values
            y = df["actual_SW_IN"].values
            
            model = Ridge().fit(X, y)
            gov.save_model(model, "fitted_model.joblib")
            
            # Save corrupted predictions
            df_preds = pd.DataFrame({
                "forecast_origin": df["timestamp"].tolist(),
                "target_timestamp": df["timestamp"].tolist(),
                "horizon_hour": [1] * len(df),
                "predicted_SW_IN": y + 999.0  # Corrupted predictions
            })
            gov.save_predictions(df_preds)
            
            # Replay will fail because loaded model predict(X) != y + 999.0
            gov.execute_independent_replay(test_data_path=sample_csv, atol=1e-5)

    assert gov.status == ModelTrainingStatus.NOT_REPRODUCIBLE


def test_ems_promotion_blocked_on_non_reproducible_model(temp_workspace):
    temp_dir, sample_csv = temp_workspace
    
    # Create fake directory with NOT_REPRODUCIBLE status
    run_dir = temp_dir / "artifacts" / "model_runs" / "RUN_FAKE_01"
    manifests_dir = run_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    
    status_data = {"MODEL_TRAINING_STATUS": "NOT_REPRODUCIBLE"}
    with open(manifests_dir / "GOVERNANCE_STATUS.json", "w") as f:
        json.dump(status_data, f)
        
    with pytest.raises(ModelGovernanceError, match="is NOT_REPRODUCIBLE"):
        assert_governance_reproducible(run_dir)
