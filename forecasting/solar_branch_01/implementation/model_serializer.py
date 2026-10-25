"""
Model Serializer Module
Handles deterministic serialization and byte-level SHA-256 calculation for fitted model artifacts.
"""

from pathlib import Path
from typing import Union
import joblib
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.hash_generator import HashGenerator
from forecasting.solar_branch_01.implementation.model_interface import GenericModelInterface


class ModelSerializer:
    """Serializes model objects to disk and calculates authoritative SHA-256 hashes."""

    @staticmethod
    def save_model(model: GenericModelInterface, destination_path: Union[str, Path]) -> str:
        """
        Serialize model object to destination_path and return SHA-256 hash digest.
        """
        path = Path(destination_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        model.save(path)

        if not path.exists():
            raise ModelGovernanceError(f"Fail-closed: Model serialization failed for path {path}")

        sha256_hash = HashGenerator.compute_file_sha256(path)
        return sha256_hash

    @staticmethod
    def load_model(model_class: type, source_path: Union[str, Path], expected_sha256: str = None) -> GenericModelInterface:
        """
        Load serialized model object after verifying byte-level SHA-256 hash.
        """
        path = Path(source_path)
        if not path.exists():
            raise ModelGovernanceError(f"Fail-closed: Model artifact missing at {path}")

        if expected_sha256:
            actual_sha = HashGenerator.compute_file_sha256(path)
            if actual_sha.lower() != expected_sha256.lower():
                raise ModelGovernanceError(
                    f"Fail-closed: Model artifact SHA-256 hash mismatch. "
                    f"Expected {expected_sha256}, got {actual_sha}"
                )

        model = model_class()
        model.load(path)
        return model
