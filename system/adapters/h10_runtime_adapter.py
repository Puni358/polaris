"""
POLARIS H1.0 Hybrid Runtime Integration Adapter (Version 1.0.0)

Provides narrow, contract-preserving static ingestion of canonical H1.0 hybrid input fixture data
(POLARIS_HYBRID_FIXTURE_H1_0) into existing frozen POLARIS runtime interfaces.

STRICT CONSTRAINTS:
- Preserves ForecastBundle, StationState, and DispatchPlan schemas without modification.
- Preserves physical units (W/m^2, W, m/s).
- Preserves timestamps and 1h monotonicity.
- Preserves explicit provenance metadata externally and within bundle.metadata.
- ZERO MILP solves or simulator steps executed within this adapter.
"""

import os
import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.interface.base import ForecastEngine


class H10RuntimeAdapter:
    """
    Static Integration Adapter for canonical H1.0 Hybrid Input Fixture.
    """

    def __init__(self, fixture_dir: str = "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"):
        self.fixture_dir = Path(fixture_dir)
        self.fixture_csv_path = self.fixture_dir / "fixture.csv"
        self.provenance_json_path = self.fixture_dir / "ems/reports/other/provenance.json"
        self.config_json_path = self.fixture_dir / "config.json"
        self.hashes_json_path = self.fixture_dir / "hashes.json"

        if not self.fixture_csv_path.exists():
            raise FileNotFoundError(f"Canonical H1.0 fixture CSV not found at {self.fixture_csv_path}")

        self.rows: List[Dict[str, Any]] = []
        self.provenance: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        self.hashes: Dict[str, Any] = {}

        self._load_and_validate()

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def _load_and_validate(self):
        # 1. Check file hashes if hashes.json exists
        if self.hashes_json_path.exists():
            with open(self.hashes_json_path, "r", encoding="utf-8") as f:
                self.hashes = json.load(f)

            csv_hash = self.compute_sha256(self.fixture_csv_path)
            expected_csv_hash = self.hashes.get("fixture_csv_sha256")
            if expected_csv_hash and csv_hash != expected_csv_hash:
                raise ValueError(f"H1.0 fixture.csv hash mismatch! Calculated: {csv_hash}, Expected: {expected_csv_hash}")

        # 2. Load provenance and config
        if self.provenance_json_path.exists():
            with open(self.provenance_json_path, "r", encoding="utf-8") as f:
                self.provenance = json.load(f)

        if self.config_json_path.exists():
            with open(self.config_json_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

        # 3. Load fixture rows
        with open(self.fixture_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected_fields = [
                "timestamp",
                "solar_SW_IN_W_m2",
                "solar_PV_power_W",
                "wind_speed_proxy_m_s",
                "wind_power_generic_W",
                "synthetic_load_W",
                "provenance_class_solar",
                "provenance_class_wind",
                "provenance_class_demand"
            ]
            for fn in expected_fields:
                if fn not in reader.fieldnames:
                    raise ValueError(f"H1.0 fixture missing required column: '{fn}'")

            for row in reader:
                self.rows.append({
                    "timestamp": row["timestamp"],
                    "solar_SW_IN_W_m2": float(row["solar_SW_IN_W_m2"]),
                    "solar_PV_power_W": float(row["solar_PV_power_W"]),
                    "wind_speed_proxy_m_s": float(row["wind_speed_proxy_m_s"]),
                    "wind_power_generic_W": float(row["wind_power_generic_W"]),
                    "synthetic_load_W": float(row["synthetic_load_W"]),
                    "provenance_class_solar": row["provenance_class_solar"],
                    "provenance_class_wind": row["provenance_class_wind"],
                    "provenance_class_demand": row["provenance_class_demand"]
                })

        if len(self.rows) != 8784:
            raise ValueError(f"H1.0 fixture row count mismatch: expected 8,784, got {len(self.rows)}")

    @property
    def total_records(self) -> int:
        return len(self.rows)

    def get_station_state(self, index: int, battery_soc_pct: float = 50.0, battery_capacity_wh: float = 200000.0) -> StationState:
        """
        Constructs frozen StationState object for timestep index t0 from H1.0 fixture.
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Index {index} out of bounds for H1.0 fixture records (0..{len(self.rows)-1})")

        rec = self.rows[index]
        return StationState(
            timestamp=rec["timestamp"],
            battery_soc_pct=battery_soc_pct,
            battery_energy_wh=battery_capacity_wh * (battery_soc_pct / 100.0),
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=rec["solar_SW_IN_W_m2"],
            last_observed_demand=rec["synthetic_load_W"],
            last_observed_wind_generation=rec["wind_power_generic_W"]
        )

    def get_runtime_context(self, index: int) -> Dict[str, Any]:
        """
        Constructs observable runtime_context for ForecastEngine prediction at timestep index t0.
        Strictly excludes future actual observations beyond index.
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Index {index} out of bounds for H1.0 fixture records")

        rec = self.rows[index]
        history = self.rows[:index + 1]

        return {
            "origin_timestamp": rec["timestamp"],
            "current_index": index,
            "last_observed_solar_irradiance": rec["solar_SW_IN_W_m2"],
            "last_observed_demand": rec["synthetic_load_W"],
            "last_observed_wind_generation": rec["wind_power_generic_W"],
            "last_observed_wind_speed": rec["wind_speed_proxy_m_s"],
            "h10_provenance": self.provenance,
            "h10_record": rec
        }

    def get_future_ground_truth(self, index: int, horizon_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Returns hidden future actual observations for simulation/evaluation ONLY.
        Must NEVER be passed to ForecastEngine or EnergyOptimizer during optimization.
        """
        start = index + 1
        end = min(start + horizon_hours, len(self.rows))
        future_steps = []

        for i in range(start, end):
            rec = self.rows[i]
            future_steps.append({
                "timestep_index": i,
                "timestamp": rec["timestamp"],
                "actual_SW_IN": rec["solar_SW_IN_W_m2"],
                "actual_solar_PV_power": rec["solar_PV_power_W"],
                "actual_wind_speed_proxy": rec["wind_speed_proxy_m_s"],
                "actual_wind_generation": rec["wind_power_generic_W"],
                "actual_demand": rec["synthetic_load_W"]
            })

        while len(future_steps) < horizon_hours:
            last_step = future_steps[-1] if future_steps else self.rows[-1]
            pad_idx = len(future_steps) + 1
            future_steps.append({
                "timestep_index": index + pad_idx,
                "timestamp": f"padded_{pad_idx}",
                "actual_SW_IN": last_step.get("actual_SW_IN", last_step.get("solar_SW_IN_W_m2", 0.0)),
                "actual_solar_PV_power": last_step.get("actual_solar_PV_power", last_step.get("solar_PV_power_W", 0.0)),
                "actual_wind_speed_proxy": last_step.get("actual_wind_speed_proxy", last_step.get("wind_speed_proxy_m_s", 0.0)),
                "actual_wind_generation": last_step.get("actual_wind_generation", last_step.get("wind_power_generic_W", 0.0)),
                "actual_demand": last_step.get("actual_demand", last_step.get("synthetic_load_W", 0.0))
            })

        return future_steps

    def export_scenario_format(self) -> Dict[str, Any]:
        """
        Exports H1.0 fixture as a POLARIS scenario dictionary for compatibility with LocalDataProvider.
        """
        scenario_timesteps = []
        for idx, rec in enumerate(self.rows):
            scenario_timesteps.append({
                "timestep_index": idx,
                "timestamp": rec["timestamp"],
                "actual_SW_IN": rec["solar_SW_IN_W_m2"],
                "clearsky_ghi": rec["solar_SW_IN_W_m2"] / 0.75 if rec["solar_SW_IN_W_m2"] > 0 else 0.0,
                "actual_wind_generation": rec["wind_power_generic_W"],
                "actual_demand": rec["synthetic_load_W"],
                "actual_wind_speed_proxy": rec["wind_speed_proxy_m_s"],
                "actual_solar_PV_power": rec["solar_PV_power_W"],
                "provenance_class_solar": rec["provenance_class_solar"],
                "provenance_class_wind": rec["provenance_class_wind"],
                "provenance_class_demand": rec["provenance_class_demand"]
            })

        return {
            "scenario_id": "polaris_h10_hybrid_fixture",
            "version": "H1.0",
            "description": "Canonical H1.0 Hybrid Fixture Scenario (SITES Nuolja Solar + SMHI 188790 Wind Proxy + H1.0 Synthetic Demand)",
            "provenance_manifest": self.provenance,
            "timesteps": scenario_timesteps
        }
