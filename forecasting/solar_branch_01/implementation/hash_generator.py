"""
Hash Generator Module
Centralized byte-level SHA-256 calculation utilities.
"""

import hashlib
from pathlib import Path
from typing import Union
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError


class HashGenerator:
    """Provides deterministic SHA-256 hashing for files, DataFrames, and byte payloads."""

    @staticmethod
    def compute_file_sha256(filepath: Union[str, Path]) -> str:
        """Compute SHA-256 hex digest of a local file."""
        path = Path(filepath)
        if not path.exists():
            raise ModelGovernanceError(f"Cannot compute hash: file does not exist at {filepath}")
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def compute_bytes_sha256(data: bytes) -> str:
        """Compute SHA-256 hex digest of in-memory bytes."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_dataframe_sha256(df: pd.DataFrame) -> str:
        """Compute deterministic SHA-256 hash of a pandas DataFrame."""
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return hashlib.sha256(csv_bytes).hexdigest()
