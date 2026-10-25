"""
Data Loader Module
Deterministic data loader for Nuolja 2024 SITES observations, Clear-Sky series, and AROME 21x21 cache.
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.source_validator import SourceValidator
from forecasting.solar_branch_01.implementation.timestamp_normalizer import TimestampNormalizer


class DataLoader:
    """Loads and validates all governed input series for Branch 01."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def load_sites_nuolja_2024(self) -> pd.DataFrame:
        """Load and normalize hourly Nuolja 2024 solar irradiance (SW_IN) observations."""
        sites_path = self.base_dir / "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
        expected_cols = ["timestamp", "SW_IN"]
        df = SourceValidator.validate_csv_source(sites_path, expected_cols, min_rows=8700)
        df = df.rename(columns={col: "timestamp" for col in df.columns if col.lower() == "timestamp"})
        df["timestamp"] = TimestampNormalizer.normalize_series(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def load_clearsky_2024(self) -> pd.DataFrame:
        """Load and normalize hourly Nuolja 2024 physical clear-sky reference series."""
        clearsky_path = self.base_dir / "forecasting/clear_sky/nuolja_clearsky_2024.csv"
        if not clearsky_path.exists():
            # Fallback for fixture testing if path is relative
            clearsky_path = self.base_dir / "data/clearsky_2024.csv"
        expected_cols = ["timestamp", "clearsky_sw_in"]
        df = SourceValidator.validate_csv_source(clearsky_path, expected_cols, min_rows=8700)
        df["timestamp"] = TimestampNormalizer.normalize_series(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df
