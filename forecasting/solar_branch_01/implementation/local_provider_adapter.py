"""
Local Data Provider -> Branch 01 Feature Adapter
Bridges LocalDataProvider runtime state/history into the frozen Branch 01
18-element feature contract defined by FeatureMatrixBuilder.ORDERED_FEATURE_NAMES,
without altering feature definitions, retraining, or touching the frozen model
artifact.

Resolves the clear-sky source mismatch identified during the Branch 01
production-readiness audit: campaign scripts (run_polaris_branch01_v2_campaign.py
and related) compute an ad hoc sinusoidal 'clearsky_ghi' approximation at
runtime, but the frozen Candidate A HGB model (POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1)
was trained against the physical clear-sky reference series loaded by
DataLoader.load_clearsky_2024() (forecasting/clear_sky/nuolja_clearsky_2024.csv, SHA-256
181d27b19f25ae23a3394ff8f5cafcb20bc14c29f26da1db726e1b1bc1778846, as recorded in
forecasting/reports/solar_branch01/POLARIS_SOLAR_FORECAST_BRANCH_01_MODEL_FREEZE_MANIFEST.json). This adapter uses
that same canonical source, not the ad hoc approximation.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from system.data.provider import LocalDataProvider
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.data_loader import DataLoader
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder
from forecasting.solar_branch_01.implementation.timestamp_normalizer import TimestampNormalizer


class LocalProviderBranch01Adapter:
    """
    Builds the frozen Branch 01 18-element feature vector from a
    LocalDataProvider's causal runtime state, using the canonical physical
    clear-sky reference series the model was trained on.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path("/home/punith-bs/01polaris (Copy)")
        self._clearsky_lookup = self._build_canonical_clearsky_lookup()

    def _build_canonical_clearsky_lookup(self) -> pd.DataFrame:
        """
        Load the canonical physical clear-sky series via the same DataLoader
        used by Branch 01 training, and re-key it on the ISO-8601 'Z' string
        format ClearSkyFeatureBuilder matches against. No values are altered;
        only the timestamp representation is normalized for lookup.
        """
        raw = DataLoader(self.base_dir).load_clearsky_2024()
        ts_strings = [TimestampNormalizer.to_iso8601_utc(ts.to_pydatetime()) for ts in raw["timestamp"]]
        return pd.DataFrame({
            "timestamp": ts_strings,
            "clearsky_sw_in": raw["clearsky_sw_in"].astype(float).values,
        })

    def build_feature_vector(self, provider: LocalDataProvider, current_index: int) -> np.ndarray:
        """
        Build the 18-element Branch 01 feature vector for the forecast origin
        at `current_index`, using only data causally observable at that index.

        LocalDataProvider.get_runtime_state() already slices history as
        self.timesteps[:current_index + 1] -- it structurally cannot see
        rows beyond current_index, so this adapter never receives future
        observations to leak.
        """
        state = provider.get_runtime_state(current_index)
        history = state["history"]

        if len(history) == 0:
            raise ModelGovernanceError("Fail-closed: empty history from LocalDataProvider.")

        sw_in_series = pd.Series([float(h["actual_SW_IN"]) for h in history])
        timestamps = pd.Series([h["timestamp"] for h in history])
        origin_idx = len(history) - 1

        if timestamps.iloc[origin_idx] != state["origin_timestamp"]:
            raise ModelGovernanceError(
                "Fail-closed: origin timestamp / history misalignment between "
                "LocalDataProvider.get_runtime_state() fields."
            )

        return FeatureMatrixBuilder.build_feature_vector(
            sw_in_series, timestamps, origin_idx, self._clearsky_lookup
        )

    def build_runtime_context_entry(self, provider: LocalDataProvider, current_index: int) -> Dict[str, Any]:
        """Produce the 'feature_vector' runtime_context entry Branch01ForecastEngine.predict() expects."""
        vec = self.build_feature_vector(provider, current_index)
        return {"feature_vector": vec.tolist()}


def predict_with_fallback(
    branch01_engine: Any,
    baseline_engine: Any,
    adapter: LocalProviderBranch01Adapter,
    provider: LocalDataProvider,
    current_index: int,
    station_state: Any,
    runtime_context: Dict[str, Any],
) -> Tuple[Any, str]:
    """
    Attempt a Branch 01 Candidate A forecast via the adapter; fall back to
    LocalBaselineForecastEngine if feature construction or inference fails
    closed (insufficient history, missing clear-sky coverage, governance
    check failure, etc). Returns (ForecastBundle, source_label).

    This never retries with substituted/synthetic features in place of the
    Branch 01 contract -- on failure it defers entirely to the independent,
    already-validated baseline engine rather than guessing at missing inputs.
    """
    try:
        ctx = dict(runtime_context)
        ctx.update(adapter.build_runtime_context_entry(provider, current_index))
        bundle = branch01_engine.predict(station_state, ctx)
        return bundle, "branch01_candidate_a_hgb"
    except ModelGovernanceError:
        bundle = baseline_engine.predict(station_state, runtime_context)
        return bundle, "local_baseline_fallback"
