"""
Source Validator Module
Fail-closed validator for dataset source integrity, paths, schemas, and SHA-256 hashes.
"""

from pathlib import Path
from typing import List, Optional, Union
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.hash_generator import HashGenerator


class SourceValidator:
    """Validates raw source datasets against strict governance contracts."""

    @staticmethod
    def validate_csv_source(
        filepath: Union[str, Path],
        expected_columns: List[str],
        expected_sha256: Optional[str] = None,
        min_rows: int = 1
    ) -> pd.DataFrame:
        """
        Validate CSV file existence, non-emptiness, column schema, and optional SHA-256 hash.
        Fails closed on any discrepancy.
        """
        path = Path(filepath)
        if not path.exists():
            raise ModelGovernanceError(f"Fail-closed: Source CSV does not exist at {path}")

        if expected_sha256:
            actual_hash = HashGenerator.compute_file_sha256(path)
            if actual_hash.lower() != expected_sha256.lower():
                raise ModelGovernanceError(
                    f"Fail-closed: SHA-256 hash mismatch for {path.name}. "
                    f"Expected {expected_sha256}, got {actual_hash}"
                )

        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Unparseable CSV at {path}: {str(e)}")

        if len(df) < min_rows:
            raise ModelGovernanceError(
                f"Fail-closed: Insufficient rows in {path.name}. Got {len(df)}, min expected {min_rows}"
            )

        cols_lower = {c.lower(): c for c in df.columns}
        missing_cols = [c for c in expected_columns if c not in df.columns and c.lower() not in cols_lower]
        if missing_cols:
            raise ModelGovernanceError(
                f"Fail-closed: Schema mismatch in {path.name}. Missing required columns: {missing_cols}"
            )

        return df
