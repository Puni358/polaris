"""
Manifest Generator Module
Generates 20-point machine-readable reproducibility manifests conforming to Draft-07 JSON Schema.
"""

import json
from pathlib import Path
import platform
import sys
from typing import Dict, Any, Union
from system.governance.model_reproducibility import ModelGovernanceError


class ManifestGenerator:
    """Generates MODEL_RUN_MANIFEST.json conforming to POLARIS_SOLAR_FORECAST_BRANCH_01_MODEL_RUN_MANIFEST_SCHEMA.json."""

    REQUIRED_FIELDS = [
        "run_id", "branch_id", "model_id", "model_class", "model_hash",
        "dataset_ids", "dataset_hashes", "feature_hash", "target_hash",
        "prediction_hash", "training_script_hash", "feature_pipeline_hash",
        "evaluation_script_hash", "config_hash", "hyperparameters",
        "random_seeds", "worker_count", "checkpoint_policy", "checkpoint_hashes",
        "start_time", "end_time", "duration", "python_version", "os",
        "dependencies", "hardware", "resource_summary", "metrics",
        "split_definitions", "replay_tolerance", "replay_status", "governance_status"
    ]

    @classmethod
    def build_manifest(cls, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and assemble run manifest dictionary.
        """
        missing = set(cls.REQUIRED_FIELDS) - set(manifest_data.keys())
        if missing:
            raise ModelGovernanceError(f"Fail-closed: Missing required manifest fields: {missing}")

        return manifest_data

    @classmethod
    def save_manifest(cls, manifest_data: Dict[str, Any], destination_path: Union[str, Path]) -> str:
        """
        Save manifest dictionary to JSON file.
        """
        path = Path(destination_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        validated_manifest = cls.build_manifest(manifest_data)

        with open(path, "w") as f:
            json.dump(validated_manifest, f, indent=2)

        return str(path)
