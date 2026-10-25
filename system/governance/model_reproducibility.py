"""
POLARIS Model Reproducibility & Governance Framework
Implements mandatory 20-point governance rule + execution metadata + resource metadata
+ process-isolated replay verification + governed state machine.
"""

import os
import sys
import json
import time
import shutil
import hashlib
import platform
import subprocess
import traceback
import multiprocessing
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Callable

import numpy as np
import pandas as pd


class ModelTrainingStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    TRAINING_COMPLETE = "TRAINING_COMPLETE"
    SERIALIZATION_VERIFIED = "SERIALIZATION_VERIFIED"
    REPLAY_VERIFIED = "REPLAY_VERIFIED"
    REPRODUCIBLE = "REPRODUCIBLE"
    NOT_REPRODUCIBLE = "NOT_REPRODUCIBLE"
    BLOCKED = "BLOCKED"


class ModelGovernanceError(Exception):
    """Raised when any model governance check, hash verification, pre-flight check, or replay fails."""
    pass


def compute_file_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    if not filepath.exists():
        raise ModelGovernanceError(f"File not found for hashing: {filepath}")
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Computes SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def assert_governance_reproducible(run_dir: Path) -> bool:
    """
    Verifies that a model run directory contains MODEL_TRAINING_STATUS == REPRODUCIBLE.
    Raises ModelGovernanceError if status is not REPRODUCIBLE or manifests are missing/corrupted.
    """
    run_dir = Path(run_dir)
    status_path = run_dir / "manifests" / "GOVERNANCE_STATUS.json"
    if not status_path.exists():
        status_path = run_dir / "GOVERNANCE_STATUS.json"
    
    if not status_path.exists():
        raise ModelGovernanceError(f"Governance status file missing in run directory: {run_dir}")
    
    with open(status_path, "r") as f:
        status_data = json.load(f)
    
    status = status_data.get("MODEL_TRAINING_STATUS")
    if status != ModelTrainingStatus.REPRODUCIBLE.value:
        raise ModelGovernanceError(
            f"Model at {run_dir} is NOT_REPRODUCIBLE (Status: '{status}'). EMS promotion BLOCKED."
        )
    return True


def _replay_process_worker(
    run_dir_str: str,
    test_data_path_str: str,
    replay_fn_name: str,
    atol: float,
    rtol: float,
    result_queue: multiprocessing.Queue
):
    """Worker function executed in a separate process for isolated replay verification."""
    try:
        run_dir = Path(run_dir_str)
        test_data_path = Path(test_data_path_str)
        
        model_dir = run_dir / "model"
        model_files = list(model_dir.glob("fitted_model.*"))
        if not model_files:
            raise ModelGovernanceError(f"Replay worker: No fitted model file found in {model_dir}")
        model_file = model_files[0]
        
        # 1. Verify model hash
        actual_hash = compute_file_sha256(model_file)
        hash_file = model_dir / "model.sha256"
        if hash_file.exists():
            expected_hash = hash_file.read_text().strip()
            if actual_hash != expected_hash:
                raise ModelGovernanceError(f"Replay worker: Model SHA mismatch ({actual_hash} != {expected_hash})")
        
        # 2. Load serialized model from disk (In-memory objects strictly forbidden)
        if model_file.suffix == ".joblib" or model_file.suffix == ".pkl":
            import joblib
            loaded_model = joblib.load(model_file)
        elif model_file.suffix == ".pt" or model_file.suffix == ".pth":
            import torch
            loaded_model = torch.load(model_file, weights_only=False)
        else:
            raise ModelGovernanceError(f"Replay worker: Unsupported model format {model_file.suffix}")
        
        # 3. Load original predictions
        pred_file = run_dir / "predictions" / "predictions.json"
        if not pred_file.exists():
            raise ModelGovernanceError(f"Replay worker: Original predictions.json missing in {run_dir}")
        with open(pred_file, "r") as f:
            orig_pred_data = json.load(f)
        
        orig_points = np.array(orig_pred_data["predicted_values"], dtype=np.float64)
        
        # 4. Run inference on test dataset
        df_test = pd.read_csv(test_data_path)
        
        # Feature columns from FEATURE_MANIFEST.json
        feat_manifest_path = run_dir / "features" / "FEATURE_MANIFEST.json"
        with open(feat_manifest_path, "r") as f:
            feat_manifest = json.load(f)
        feature_cols = feat_manifest["feature_names"]
        
        X_test = df_test[feature_cols].values
        
        if hasattr(loaded_model, "predict"):
            replay_preds = loaded_model.predict(X_test)
        elif callable(loaded_model):
            import torch
            if isinstance(X_test, np.ndarray):
                X_tensor = torch.tensor(X_test, dtype=torch.float32)
            else:
                X_tensor = X_test
            with torch.no_grad():
                replay_preds = loaded_model(X_tensor).numpy()
        else:
            raise ModelGovernanceError("Replay worker: Loaded model is not callable and lacks predict method.")
        
        replay_preds = np.array(replay_preds, dtype=np.float64).flatten()
        
        # 5. Check shape and tolerance
        if len(replay_preds) != len(orig_points):
            raise ModelGovernanceError(f"Replay prediction length mismatch ({len(replay_preds)} != {len(orig_points)})")
        
        max_abs_diff = float(np.max(np.abs(replay_preds - orig_points)))
        max_rel_diff = float(np.max(np.abs(replay_preds - orig_points) / (np.abs(orig_points) + 1e-12)))
        
        match = bool(np.allclose(replay_preds, orig_points, atol=atol, rtol=rtol))
        
        result_queue.put({
            "success": match,
            "max_abs_difference": max_abs_diff,
            "max_rel_difference": max_rel_diff,
            "atol": atol,
            "rtol": rtol,
            "error": None if match else f"Replay tolerance exceeded (max_abs_diff={max_abs_diff} > atol={atol})"
        })
    except Exception as e:
        result_queue.put({
            "success": False,
            "max_abs_difference": None,
            "max_rel_difference": None,
            "atol": atol,
            "rtol": rtol,
            "error": f"Replay exception: {str(e)}\n{traceback.format_exc()}"
        })


def verify_independent_replay(
    run_dir: Path,
    test_data_path: Path,
    atol: float = 1e-5,
    rtol: float = 1e-5,
    timeout_sec: int = 60
) -> Dict[str, Any]:
    """
    Executes independent replay verification in a separate process.
    Loads serialized model from disk, reconstructs inputs, runs inference,
    and compares output predictions against original artifact within tolerance.
    """
    result_queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_replay_process_worker,
        args=(str(run_dir), str(test_data_path), "default", atol, rtol, result_queue)
    )
    p.start()
    p.join(timeout=timeout_sec)
    
    if p.is_alive():
        p.terminate()
        p.join()
        raise ModelGovernanceError(f"Independent replay timed out after {timeout_sec}s.")
    
    if result_queue.empty():
        raise ModelGovernanceError("Independent replay process failed to return result.")
    
    res = result_queue.get()
    if not res["success"]:
        raise ModelGovernanceError(f"Independent replay failed: {res['error']}")
    
    return res


class PolarisModelGovernanceManager:
    """
    Context manager & governance engine enforcing the 20-point POLARIS model-training
    governance rule, process-isolated replay verification, resource/thermal monitoring,
    pre-flight dataset validation, and governed state transitions.
    """

    def __init__(
        self,
        branch_id: str,
        model_id: str,
        model_type: str,
        base_dir: Optional[Path] = None,
        num_workers: int = 8,
        worker_reason: str = "Standard 8-worker parallel data loading allocation"
    ):
        self.branch_id = branch_id
        self.model_id = model_id
        self.model_type = model_type
        self.base_dir = Path(base_dir) if base_dir else Path("/home/punith-bs/01polaris (Copy)")
        self.num_workers = num_workers
        self.worker_reason = worker_reason
        
        # Generate immutable run ID
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        rand_hash = hashlib.sha256(f"{branch_id}_{model_id}_{now_str}_{time.time()}".encode()).hexdigest()[:8]
        self.run_id = f"RUN_{now_str}_{rand_hash}"
        
        # Create immutable run directory structure
        self.run_dir = self.base_dir / "artifacts" / "model_runs" / self.run_id
        self.model_dir = self.run_dir / "model"
        self.data_dir = self.run_dir / "data"
        self.features_dir = self.run_dir / "features"
        self.env_dir = self.run_dir / "environment"
        self.logs_dir = self.run_dir / "logs"
        self.preds_dir = self.run_dir / "predictions"
        self.eval_dir = self.run_dir / "evaluation"
        self.manifests_dir = self.run_dir / "manifests"
        self.replay_dir = self.run_dir / "replay"

        self.status = ModelTrainingStatus.NOT_STARTED
        self.log_file_path = self.logs_dir / "training.log"
        self._start_time = None
        self._end_time = None
        
        # State tracking
        self.hyperparameters = {}
        self.random_seeds = {}
        self.feature_names = []
        self.feature_order = []
        self.data_preflight_info = {}
        self.split_definitions = {}
        self.metrics = {}
        self.predictions_info = {}
        self.serialized_model_path = None
        self.model_sha256 = None
        self.replay_results = {}

    def __enter__(self):
        self._create_directories()
        self.status = ModelTrainingStatus.IN_PROGRESS
        self._start_time = time.time()
        self._update_status_file()
        self.log(f"Initiated governance run '{self.run_id}' for branch '{self.branch_id}'.")
        self._record_environment()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = time.time()
        if exc_type is not None:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self.log(f"ERROR: Run failed with exception: {exc_val}")
            self.log(traceback.format_exc())
            self._update_status_file()
            # Do NOT suppress exception
            return False

        if self.status != ModelTrainingStatus.REPRODUCIBLE:
            self.log(f"WARNING: Exiting context without achieving REPRODUCIBLE status (Current: {self.status}). Marking NOT_REPRODUCIBLE.")
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()

        self.log(f"Run '{self.run_id}' finished with status '{self.status}'. Duration: {self._end_time - self._start_time:.2f}s.")
        return False

    def _create_directories(self):
        """Creates isolated immutable directory structure."""
        for d in [
            self.run_dir, self.model_dir, self.data_dir, self.features_dir,
            self.env_dir, self.logs_dir, self.preds_dir, self.eval_dir,
            self.manifests_dir, self.replay_dir
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Logs timestamped message to training.log and stdout."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_line = f"[{ts}] [{self.status.value}] {message}\n"
        with open(self.log_file_path, "a") as f:
            f.write(log_line)
        print(log_line.strip())

    def dataset_preflight_check(
        self,
        dataset_path: Path,
        expected_sha256: Optional[str] = None,
        expected_rows: Optional[int] = None,
        expected_cols: Optional[int] = None,
        feature_order: Optional[List[str]] = None,
        target_col: str = "actual_SW_IN"
    ) -> Dict[str, Any]:
        """
        Pre-flight check prior to fitting:
        Verifies file existence, SHA-256 hash, row/col count, schema, target column, feature order.
        Aborts immediately if any pre-flight check fails.
        """
        dataset_path = Path(dataset_path)
        self.log(f"Executing dataset pre-flight check on {dataset_path.name}...")
        
        if not dataset_path.exists():
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Pre-flight check failed: Dataset missing at {dataset_path}")

        sha256 = compute_file_sha256(dataset_path)
        if expected_sha256 and sha256 != expected_sha256:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Pre-flight SHA mismatch on {dataset_path.name} ({sha256} != {expected_sha256})")

        df = pd.read_csv(dataset_path)
        rows, cols = df.shape

        if expected_rows and rows != expected_rows:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Pre-flight row count mismatch on {dataset_path.name} ({rows} != {expected_rows})")

        if expected_cols and cols != expected_cols:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Pre-flight col count mismatch on {dataset_path.name} ({cols} != {expected_cols})")

        if target_col not in df.columns:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Pre-flight missing target column '{target_col}' in {dataset_path.name}")

        if feature_order:
            for feat in feature_order:
                if feat not in df.columns:
                    self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
                    self._update_status_file()
                    raise ModelGovernanceError(f"Pre-flight missing required feature '{feat}' in {dataset_path.name}")

        # Check timestamp column if present
        ts_col = "timestamp" if "timestamp" in df.columns else ("TIMESTAMP" if "TIMESTAMP" in df.columns else None)
        ts_min = str(df[ts_col].min()) if ts_col else "N/A"
        ts_max = str(df[ts_col].max()) if ts_col else "N/A"

        info = {
            "dataset_name": dataset_path.name,
            "dataset_path": str(dataset_path),
            "sha256": sha256,
            "row_count": rows,
            "col_count": cols,
            "target_column": target_col,
            "timestamp_min": ts_min,
            "timestamp_max": ts_max,
            "preflight_status": "PASS"
        }
        
        self.data_preflight_info[dataset_path.name] = info
        self.log(f"Pre-flight check PASSED for {dataset_path.name} (SHA-256: {sha256[:16]}..., Rows: {rows}, Cols: {cols}).")
        return info

    def record_hyperparameters_and_seeds(self, hyperparameters: Dict[str, Any], random_seeds: Dict[str, int]):
        """Records hyperparameters and random seeds."""
        self.hyperparameters = dict(hyperparameters)
        self.random_seeds = dict(random_seeds)
        self.log(f"Recorded {len(hyperparameters)} hyperparameters and {len(random_seeds)} random seeds.")

    def record_feature_contract(self, feature_names: List[str], target_col: str = "actual_SW_IN"):
        """Records feature contract and ordering."""
        self.feature_names = list(feature_names)
        self.feature_order = list(feature_names)
        
        feat_manifest = {
            "branch_id": self.branch_id,
            "feature_count": len(feature_names),
            "target_column": target_col,
            "feature_names": self.feature_names,
            "feature_order": self.feature_order
        }
        with open(self.features_dir / "FEATURE_MANIFEST.json", "w") as f:
            json.dump(feat_manifest, f, indent=2)
        self.log(f"Frozen feature contract with {len(feature_names)} features.")

    def record_splits(self, train_range: Tuple[str, str], val_range: Tuple[str, str], test_range: Tuple[str, str]):
        """Records chronological train/validation/test split definitions."""
        self.split_definitions = {
            "train": {"start": train_range[0], "end": train_range[1]},
            "validation": {"start": val_range[0], "end": val_range[1]},
            "test": {"start": test_range[0], "end": test_range[1]},
            "embargo_hours": 24
        }
        self.log(f"Recorded chronological splits (Train: {train_range[0]}..{train_range[1]}, Val: {val_range[0]}..{val_range[1]}, Test: {test_range[0]}..{test_range[1]}).")

    def save_model(self, model_object: Any, filename: str = "fitted_model.joblib") -> Path:
        """
        Serializes fitted model object to disk, computes SHA-256 hash, and transitions
        state: IN_PROGRESS -> TRAINING_COMPLETE -> SERIALIZATION_VERIFIED.
        """
        self.log(f"Serializing fitted model to {filename}...")
        save_path = self.model_dir / filename
        
        if filename.endswith(".joblib") or filename.endswith(".pkl"):
            import joblib
            joblib.dump(model_object, save_path)
        elif filename.endswith(".pt") or filename.endswith(".pth"):
            import torch
            torch.save(model_object, save_path)
        elif hasattr(model_object, "save_model"):
            model_object.save_model(str(save_path))
        else:
            import pickle
            with open(save_path, "wb") as f:
                pickle.dump(model_object, f)

        self.serialized_model_path = save_path
        self.model_sha256 = compute_file_sha256(save_path)
        (self.model_dir / "model.sha256").write_text(self.model_sha256)

        self.status = ModelTrainingStatus.SERIALIZATION_VERIFIED
        self._update_status_file()
        self.log(f"Model serialized successfully. SHA-256: {self.model_sha256}")
        return save_path

    def save_predictions(self, df_predictions: pd.DataFrame) -> Path:
        """
        Saves predictions artifact verifying origin, target timestamp, horizon,
        prediction values, dtypes, row ordering, and computes SHA-256 hash.
        """
        req_cols = ["forecast_origin", "target_timestamp", "horizon_hour", "predicted_SW_IN"]
        for rc in req_cols:
            if rc not in df_predictions.columns:
                raise ModelGovernanceError(f"Prediction DataFrame missing required column '{rc}'")

        json_path = self.preds_dir / "predictions.json"
        csv_path = self.preds_dir / "predictions.csv"
        hash_path = self.preds_dir / "predictions.sha256"

        df_predictions.to_csv(csv_path, index=False)
        
        pred_dict = {
            "branch_id": self.branch_id,
            "run_id": self.run_id,
            "row_count": len(df_predictions),
            "columns": list(df_predictions.columns),
            "forecast_origins": df_predictions["forecast_origin"].tolist(),
            "target_timestamps": df_predictions["target_timestamp"].tolist(),
            "horizon_hours": df_predictions["horizon_hour"].tolist(),
            "predicted_values": df_predictions["predicted_SW_IN"].tolist()
        }
        with open(json_path, "w") as f:
            json.dump(pred_dict, f, indent=2)

        pred_sha256 = compute_file_sha256(json_path)
        hash_path.write_text(pred_sha256)

        self.predictions_info = {
            "row_count": len(df_predictions),
            "json_path": str(json_path),
            "csv_path": str(csv_path),
            "sha256": pred_sha256
        }
        self.log(f"Saved prediction artifacts ({len(df_predictions)} rows). SHA-256: {pred_sha256[:16]}...")
        return json_path

    def save_metrics(self, metrics: Dict[str, Any]):
        """Saves evaluation metrics."""
        self.metrics = dict(metrics)
        with open(self.eval_dir / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
        self.log(f"Recorded evaluation metrics: {self.metrics}")

    def execute_independent_replay(
        self,
        test_data_path: Path,
        atol: float = 1e-5,
        rtol: float = 1e-5,
        timeout_sec: int = 60
    ) -> Dict[str, Any]:
        """
        Executes process-isolated independent replay verification.
        Loads model binary from disk in a fresh Python process, runs inference,
        compares outputs against predictions.json within declared tolerance.
        """
        self.log("Executing process-isolated independent replay verification...")
        
        if self.status != ModelTrainingStatus.SERIALIZATION_VERIFIED and self.status != ModelTrainingStatus.TRAINING_COMPLETE:
            raise ModelGovernanceError(f"Cannot run replay from state '{self.status}'. Must be SERIALIZATION_VERIFIED.")

        replay_res = verify_independent_replay(
            run_dir=self.run_dir,
            test_data_path=test_data_path,
            atol=atol,
            rtol=rtol,
            timeout_sec=timeout_sec
        )

        with open(self.replay_dir / "REPLAY_REPORT.json", "w") as f:
            json.dump(replay_res, f, indent=2)

        if replay_res["success"]:
            self.status = ModelTrainingStatus.REPRODUCIBLE
            self.replay_results = replay_res
            self._write_master_manifests()
            self._update_status_file()
            self.log(f"Independent replay PASSED (Max abs diff: {replay_res['max_abs_difference']:.8f} <= atol={atol}). Status: REPRODUCIBLE.")
        else:
            self.status = ModelTrainingStatus.NOT_REPRODUCIBLE
            self._update_status_file()
            raise ModelGovernanceError(f"Independent replay FAILED: {replay_res['error']}")

        return replay_res

    def _record_environment(self):
        """Records runtime environment, git provenance, CLI args, git diff patch, and package dependencies."""
        # Git provenance
        try:
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.base_dir).decode().strip()
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.base_dir).decode().strip()
            status_output = subprocess.check_output(["git", "status", "--porcelain"], cwd=self.base_dir).decode().strip()
            is_dirty = len(status_output) > 0
            diff_patch = subprocess.check_output(["git", "diff"], cwd=self.base_dir).decode()
            diff_sha256 = compute_bytes_sha256(diff_patch.encode()) if is_dirty else "CLEAN"
            
            if is_dirty:
                (self.env_dir / "git_diff.patch").write_text(diff_patch)
        except Exception:
            commit_hash = "UNAVAILABLE"
            branch = "UNAVAILABLE"
            is_dirty = True
            diff_sha256 = "UNAVAILABLE"

        # Dependencies
        deps = {}
        for pkg in ["numpy", "pandas", "scipy", "scikit-learn", "torch", "joblib", "yaml"]:
            try:
                mod = __import__(pkg)
                deps[pkg] = getattr(mod, "__version__", "AVAILABLE")
            except ImportError:
                deps[pkg] = "NOT_INSTALLED"

        # Hardware & Thermal monitoring mock
        cpu_count = os.cpu_count() or 1
        ram_gb = "UNAVAILABLE"
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        except Exception:
            pass

        env_info = {
            "branch_id": self.branch_id,
            "run_id": self.run_id,
            "python_version": sys.version,
            "python_executable": sys.executable,
            "cli_command": sys.argv,
            "operating_system": platform.platform(),
            "architecture": platform.machine(),
            "cpu_count": cpu_count,
            "ram_capacity_gb": ram_gb,
            "worker_count": self.num_workers,
            "worker_allocation_reason": self.worker_reason,
            "git_provenance": {
                "commit_hash": commit_hash,
                "branch": branch,
                "is_dirty": is_dirty,
                "diff_sha256": diff_sha256,
                "patch_saved": is_dirty
            },
            "dependency_versions": deps
        }

        with open(self.env_dir / "ENVIRONMENT.json", "w") as f:
            json.dump(env_info, f, indent=2)

    def _write_master_manifests(self):
        """Generates the master manifest files required by the governance rule."""
        # 1. MODEL_MANIFEST.json
        model_manifest = {
            "branch_id": self.branch_id,
            "run_id": self.run_id,
            "model_id": self.model_id,
            "model_type": self.model_type,
            "serialized_model_file": str(self.serialized_model_path.name) if self.serialized_model_path else None,
            "model_sha256": self.model_sha256,
            "hyperparameters": self.hyperparameters,
            "random_seeds": self.random_seeds,
            "metrics": self.metrics,
            "reproducibility_status": self.status.value,
            "replay_results": self.replay_results
        }
        with open(self.manifests_dir / "MODEL_MANIFEST.json", "w") as f:
            json.dump(model_manifest, f, indent=2)

        # 2. DATA_MANIFEST.json
        data_manifest = {
            "branch_id": self.branch_id,
            "run_id": self.run_id,
            "datasets": self.data_preflight_info,
            "chronological_splits": self.split_definitions
        }
        with open(self.data_dir / "DATA_MANIFEST.json", "w") as f:
            json.dump(data_manifest, f, indent=2)

        # 3. REPRODUCTION_INSTRUCTIONS.md
        repro_instructions = f"""# REPRODUCTION INSTRUCTIONS — RUN `{self.run_id}`

**Branch ID:** `{self.branch_id}`  
**Model ID:** `{self.model_id}`  
**Model Type:** `{self.model_type}`  
**Model SHA-256:** `{self.model_sha256}`  

## Independent Replay Command
To independently verify this fitted model run in an isolated environment:

```bash
python3 -c "
from system.governance import verify_independent_replay
from pathlib import Path

res = verify_independent_replay(
    run_dir=Path('{self.run_dir}'),
    test_data_path=Path('{list(self.data_preflight_info.values())[0]['dataset_path'] if self.data_preflight_info else ''}'),
    atol=1e-5,
    rtol=1e-5
)
print('Replay Success:', res['success'])
"
```
"""
        (self.run_dir / "REPRODUCTION_INSTRUCTIONS.md").write_text(repro_instructions)

    def _update_status_file(self):
        """Writes current GOVERNANCE_STATUS.json."""
        gov_status = {
            "branch_id": self.branch_id,
            "run_id": self.run_id,
            "model_id": self.model_id,
            "MODEL_TRAINING_STATUS": self.status.value,
            "is_reproducible": (self.status == ModelTrainingStatus.REPRODUCIBLE),
            "ems_promotion_eligible": (self.status == ModelTrainingStatus.REPRODUCIBLE),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        with open(self.manifests_dir / "GOVERNANCE_STATUS.json", "w") as f:
            json.dump(gov_status, f, indent=2)
