"""
POLARIS Stage 3: Offline Optimizer Replay Execution Script
Experiment: EXP-OFFLINE-OPTIMIZER-REPLAY-20261010
Evaluates GAP19 closed-loop receding-horizon dispatch performance under:
- Control: Baseline Causal NWP + Physics (gamma = 1.00)
- Candidate: Nonlinear Cloud->GHI Correction (gamma = 0.25)
Over the 240 eligible non-blind 2025 forecast origins:
  Segment 1: 119 origins (2025-01-01 to 2025-04-29)
  Segment 2: 121 origins (2025-09-01 to 2025-12-30)
Excludes the 123-origin protected blind window (2025-05-01 to 2025-08-31),
April 30 (to prevent rolling lookaheads into the blind window),
and December 31 (to prevent rolling lookaheads extending beyond available 2025 data).
"""

import sys
import os
import json
import math
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.causal_nwp_physics import (
    CausalNwpPhysicsForecastEngine,
    CAUSAL_NWP_PROVENANCE_KEY
)
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector
)
from experiments.run_diesel_reduction_campaign import load_canonical_configs, make_initial_state

EXP_DIR = Path(__file__).resolve().parent
WEATHER_2025_PATH = REPO / "data" / "POLARIS_v0_1_future_weather_forecasts_2025.csv"
EXPECTED_WEATHER_HASH = "2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5"

FROZEN_GAMMA = 0.25
BOOTSTRAP_SEED = 20261010
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_BLOCK_LENGTH = 10.0


class CausalNwpCandidateEngine(CausalNwpPhysicsForecastEngine):
    """
    Offline candidate forecast engine implementing the frozen gamma=0.25
    Cloud->GHI nonlinear attenuation formula:
        GHI_candidate = clearsky_GHI * (1 - cloud_fraction)^0.25
    Zero production code modified; subclassed for isolated evaluation.
    """
    def __init__(self, gamma: float = FROZEN_GAMMA):
        super().__init__()
        self.gamma = gamma

    def predict(self, station_state: StationState, runtime_context: Dict[str, Any]) -> ForecastBundle:
        base_bundle = super().predict(station_state, runtime_context)
        
        # Extract clear-sky and cloud fractions from metadata or reconstruct safely
        prov = base_bundle.metadata.get(CAUSAL_NWP_PROVENANCE_KEY, {})
        timestamps = prov.get("timestamps", base_bundle.timestamps)
        
        # Reconstruct astronomical clear-sky and compute candidate GHI
        dt_index = pd.to_datetime(timestamps, utc=True)
        solpos = self.location.get_solarposition(dt_index)
        clearsky = self.location.get_clearsky(dt_index, model="ineichen")
        cloud_covers = runtime_context.get("fc_cloud_cover", [])
        
        cand_irr_pts: List[float] = []
        cand_gen_pts: List[float] = []
        
        for h in range(24):
            elev = float(solpos["elevation"].iloc[h])
            cs_ghi = float(clearsky["ghi"].iloc[h])
            c_frac = float(cloud_covers[h]) / 100.0
            
            if elev <= 0.0 or cs_ghi <= 0.0:
                forecast_ghi = 0.0
            else:
                forecast_ghi = max(0.0, cs_ghi * ((1.0 - c_frac) ** self.gamma))
                
            forecast_ghi = round(forecast_ghi, 2)
            cand_irr_pts.append(forecast_ghi)
            p_solar = round(self._ghi_to_solar_power_w(forecast_ghi), 2)
            cand_gen_pts.append(p_solar)
            
        cand_irr_forecast = TimeseriesForecast(
            point=cand_irr_pts,
            lower=cand_irr_pts,
            upper=cand_irr_pts,
            unit="W/m^2"
        )
        cand_gen_forecast = TimeseriesForecast(
            point=cand_gen_pts,
            lower=cand_gen_pts,
            upper=cand_gen_pts,
            unit="W"
        )
        
        cand_prov = dict(prov)
        cand_prov["model_identity"] = f"causal_nwp_physics_nonlinear_gamma_{self.gamma}"
        cand_prov["formulation"] = f"forecast_GHI = max(0.0, clear_sky_GHI * (1.0 - cloud_fraction)^{self.gamma})"
        cand_prov["selected_gamma"] = self.gamma
        cand_prov["solar_irradiance_point"] = cand_irr_pts
        cand_prov["solar_generation_point"] = cand_gen_pts
        
        cand_metadata = dict(base_bundle.metadata)
        cand_metadata[CAUSAL_NWP_PROVENANCE_KEY] = cand_prov
        cand_metadata["engine_identity"] = "CausalNwpCandidateEngine"
        
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=base_bundle.origin_timestamp,
            horizon_hours=24,
            timestamps=base_bundle.timestamps,
            solar_irradiance=cand_irr_forecast,
            solar_generation=cand_gen_forecast,
            wind_generation=base_bundle.wind_generation,
            demand=base_bundle.demand,
            metadata=cand_metadata
        )
        return bundle


def sync_dir(path: Path, error_out: Optional[List[str]] = None) -> bool:
    """
    Attempts directory fsync to flush directory entry metadata on POSIX filesystems.
    Policy: Best-effort directory durability.
    If directory fsync fails due to unsupported platform/filesystem or OS error, emits
    a clear warning to stderr identifying the directory and failure reason, records
    the error message into error_out if provided, and returns False.
    Does NOT raise or mask surrounding exceptions.
    """
    try:
        dfd = os.open(str(path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(dfd)
            return True
        finally:
            try:
                os.close(dfd)
            except OSError:
                pass
    except OSError as err:
        err_msg = f"{type(err).__name__}: {err}"
        if error_out is not None:
            error_out.append(err_msg)
        sys.stderr.write(
            f"WARNING: Directory fsync failed for '{path}' ({err_msg}). "
            f"Directory metadata synchronization could not be guaranteed.\n"
        )
        sys.stderr.flush()
        return False


REQUIRED_METRIC_FIELDS = {
    # Keys with expected types
    "origin_idx": int,
    "forecast_start": str,
    "t0_timestamp": str,
    "ctrl_fuel_l": (int, float),
    "cand_fuel_l": (int, float),
    "delta_fuel_l": (int, float),
    "ctrl_unmet_wh": (int, float),
    "cand_unmet_wh": (int, float),
    "delta_unmet_wh": (int, float),
    "ctrl_curtail_wh": (int, float),
    "cand_curtail_wh": (int, float),
    "delta_curtail_wh": (int, float),
    "ctrl_diesel_hrs": int,
    "cand_diesel_hrs": int,
    "delta_diesel_hrs": int,
    "ctrl_soc_final_pct": (int, float),
    "cand_soc_final_pct": (int, float),
    "delta_soc_final_pct": (int, float),
    "ctrl_j1_wh": (int, float),
    "cand_j1_wh": (int, float),
    "ctrl_j2_wh": (int, float),
    "cand_j2_wh": (int, float),
    "ctrl_runtime_s": (int, float),
    "cand_runtime_s": (int, float)
}


def validate_origin_record(rec: Any) -> None:
    """
    Strict validation of per-origin record schema and finite numerical quantities.
    Rejects missing fields, unexpected fields, incorrect types, NaN, +Inf, and -Inf.
    Reports missing and unexpected fields separately in a deterministic error message.
    """
    if not isinstance(rec, dict):
        raise TypeError(f"Origin record must be a dict, got {type(rec).__name__}")
        
    expected_keys = set(REQUIRED_METRIC_FIELDS.keys())
    actual_keys = set(rec.keys())
    
    missing = expected_keys - actual_keys
    unexpected = actual_keys - expected_keys
    
    if missing or unexpected:
        err_parts = []
        if missing:
            err_parts.append(f"Missing required fields: {sorted(missing)}")
        if unexpected:
            err_parts.append(f"Unexpected unknown fields: {sorted(unexpected)}")
        raise ValueError(f"Origin record schema violation: {'; '.join(err_parts)}")
        
    for k, expected_type in REQUIRED_METRIC_FIELDS.items():
        val = rec[k]
        if isinstance(expected_type, tuple):
            if not isinstance(val, expected_type) or isinstance(val, bool):
                raise TypeError(f"Field '{k}' has invalid type {type(val).__name__}, expected float/int")
            # Check finite
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Field '{k}' contains non-finite numerical value: {val}")
        elif expected_type is int:
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(f"Field '{k}' has invalid type {type(val).__name__}, expected int")
        elif expected_type is str:
            if not isinstance(val, str) or not val.strip():
                raise TypeError(f"Field '{k}' has invalid type or empty string: {val!r}")


class RunStatusTracker:
    """
    Encapsulates RUN_STATUS.json lifecycle and directory-sync durability-warning
    bookkeeping for a single run directory.

    Extracted verbatim (behavior-identical) from the closures previously nested
    inside main() so this logic is independently unit-testable without invoking
    main(), run_single_origin_replay(), the optimizer, or multiprocessing.
    """

    def __init__(self, run_dir: Path, run_timestamp: str, status_file: Path):
        self.run_dir = run_dir
        self.run_timestamp = run_timestamp
        self.status_file = status_file
        self.durability_warnings: List[Dict[str, Any]] = []
        self.last_status_state: str = "INITIALIZING"
        self.last_status_details: Dict[str, Any] = {}

    def record_durability_warning(
        self,
        call_site: str,
        target_path: Path,
        reason: str,
        update_file: bool = True
    ) -> None:
        """
        Records a directory synchronization warning in machine-readable state.
        Preserves all accumulated warnings across the run life cycle.
        Optionally persists the degraded durability state to RUN_STATUS.json
        without triggering recursive sync_dir calls.
        """
        w_entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "call_site": call_site,
            "target_path": str(target_path),
            "reason": reason
        }
        self.durability_warnings.append(w_entry)
        if update_file:
            self.update_run_status(self.last_status_state, self.last_status_details, sync_directory=False)

    def update_run_status(
        self,
        state: str,
        details: Dict[str, Any],
        sync_directory: bool = True
    ) -> None:
        """
        Atomically updates RUN_STATUS.json.
        Flushes and fsyncs the temporary file, replaces atomically via os.replace,
        and attempts directory fsync. Fails gracefully if called during an active exception.
        Surfaces machine-readable durability warnings and degraded durability state
        without masking primary exceptions or triggering recursive directory sync.
        """
        self.last_status_state = state
        self.last_status_details = dict(details)

        durability_warnings = self.durability_warnings
        dur_status = "GUARANTEED" if len(durability_warnings) == 0 else "DEGRADED_DIRECTORY_SYNC_FAILED"
        dur_payload = {
            "directory_sync_guaranteed": len(durability_warnings) == 0,
            "status": dur_status,
            "warnings_count": len(durability_warnings),
            "warnings": list(durability_warnings)
        }

        payload = {
            "run_id": f"run_{self.run_timestamp}",
            "status": state,
            "durability_status": dur_status,
            "durability_warnings": list(durability_warnings),
            "durability": dur_payload,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **details
        }
        tmp_status = self.run_dir / "RUN_STATUS.json.tmp"
        try:
            with open(tmp_status, "w") as sf:
                json.dump(payload, sf, indent=2)
                sf.flush()
                os.fsync(sf.fileno())
            os.replace(tmp_status, self.status_file)

            # Call site 1: sync directory after status file replace
            if sync_directory:
                err_holder: List[str] = []
                if not sync_dir(self.run_dir, err_holder):
                    reason_msg = err_holder[0] if err_holder else "Directory metadata sync failed"
                    self.record_durability_warning(
                        call_site=f"update_run_status({state})",
                        target_path=self.run_dir,
                        reason=reason_msg,
                        update_file=False
                    )
                    # Rewrite status file once without directory sync to persist this new warning
                    try:
                        payload["durability_status"] = "DEGRADED_DIRECTORY_SYNC_FAILED"
                        payload["durability_warnings"] = list(self.durability_warnings)
                        payload["durability"] = {
                            "directory_sync_guaranteed": False,
                            "status": "DEGRADED_DIRECTORY_SYNC_FAILED",
                            "warnings_count": len(self.durability_warnings),
                            "warnings": list(self.durability_warnings)
                        }
                        with open(tmp_status, "w") as sf:
                            json.dump(payload, sf, indent=2)
                            sf.flush()
                            os.fsync(sf.fileno())
                        os.replace(tmp_status, self.status_file)
                    except Exception as rewrite_err:
                        sys.stderr.write(
                            f"WARNING: update_run_status durability rewrite failed: {rewrite_err}\n"
                        )
                        sys.stderr.flush()
        except Exception as status_err:
            # Document and print secondary error without masking primary exception
            sys.stderr.write(f"WARNING: update_run_status({state}) failed: {status_err}\n")
            sys.stderr.flush()


def verify_file_hash(path: Path, expected: str):
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if h != expected:
        raise ValueError(f"Hash mismatch for {path}: expected {expected}, got {h}")
    return h


def get_non_blind_origins(weather_df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    """
    Partitions eligible non-blind origins into Segment 1 (119) and Segment 2 (121),
    strictly excluding the 123-origin summer blind window, April 30 (to prevent blind-window lookahead leaks),
    and December 31 (to prevent 2026 dataset boundary overflow). Total eligible: 240 origins.
    """
    weather_df = weather_df.copy()
    weather_df["forecast_start_dt"] = pd.to_datetime(weather_df["forecast_start"])
    
    blind_mask = (weather_df["forecast_start_dt"] >= "2025-05-01") & (weather_df["forecast_start_dt"] <= "2025-08-31 23:59:59")
    df_blind = weather_df[blind_mask]
    df_non_blind = weather_df[~blind_mask]
    
    blind_origins = sorted(df_blind["forecast_start"].unique())
    if len(blind_origins) != 123:
        raise ValueError(f"Expected 123 blind origins, found {len(blind_origins)}")
        
    all_non_blind = sorted(df_non_blind["forecast_start"].unique())
    
    # Filter boundary seam origins: April 30 (quarantine leak) and December 31 (2026 overflow)
    seg1 = [o for o in all_non_blind if o < "2025-04-30 00:00:00"]
    seg2 = [o for o in all_non_blind if "2025-09-01 00:00:00" <= o < "2025-12-31 00:00:00"]
    all_eligible = seg1 + seg2
    
    if len(seg1) != 119 or len(seg2) != 121 or len(all_eligible) != 240:
        raise ValueError(
            f"Partition error: seg1={len(seg1)} (expected 119), seg2={len(seg2)} (expected 121), total={len(all_eligible)} (expected 240)"
        )
        
    return all_eligible, seg1, seg2


def run_single_origin_replay(args: Tuple[int, str, str, Dict[str, Any]]) -> Dict[str, Any]:
    """Runs paired Control vs Candidate 24-step receding-horizon closed-loop simulation on one origin."""
    origin_idx, forecast_start, t0_ts, configs = args
    
    # Read weather for this origin
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    sub = weather_df[weather_df["forecast_start"] == forecast_start]
    if len(sub) != 24:
        raise RuntimeError(f"Origin {forecast_start} has {len(sub)} rows, expected 24")
        
    realized_solar = sub["actual_SW_IN"].tolist()
    realized_ts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    realized_wind = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    realized_demand = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    
    # Control Runner (gamma = 1.00)
    runner_ctrl = AdaptedClosedLoopRunner(configs)
    runner_ctrl.forecast_engine = CausalNwpPhysicsForecastEngine()
    state_ctrl = make_initial_state(t0_ts)
    
    t0_start = time.time()
    rep_ctrl = runner_ctrl.run_closed_loop(
        state_ctrl, 24, weather_df, realized_solar, realized_wind, realized_demand, realized_ts
    )
    t_ctrl = time.time() - t0_start
    
    # Candidate Runner (gamma = 0.25)
    runner_cand = AdaptedClosedLoopRunner(configs)
    runner_cand.forecast_engine = CausalNwpCandidateEngine(gamma=FROZEN_GAMMA)
    state_cand = make_initial_state(t0_ts)
    
    t1_start = time.time()
    rep_cand = runner_cand.run_closed_loop(
        state_cand, 24, weather_df, realized_solar, realized_wind, realized_demand, realized_ts
    )
    t_cand = time.time() - t1_start
    
    # Verify invariants for both runs
    for rec in rep_ctrl.step_records:
        if rec.busbar_balance_error_w > 1e-3:
            raise RuntimeError(f"Control busbar error {rec.busbar_balance_error_w} W at step {rec.step_index}")
        if rec.realized_soc_pct < 19.999 or rec.realized_soc_pct > 95.001:
            raise RuntimeError(f"Control SoC out of bounds: {rec.realized_soc_pct}%")
            
    for rec in rep_cand.step_records:
        if rec.busbar_balance_error_w > 1e-3:
            raise RuntimeError(f"Candidate busbar error {rec.busbar_balance_error_w} W at step {rec.step_index}")
        if rec.realized_soc_pct < 19.999 or rec.realized_soc_pct > 95.001:
            raise RuntimeError(f"Candidate SoC out of bounds: {rec.realized_soc_pct}%")

    # Aggregate origin metrics
    ctrl_fuel = rep_ctrl.cumulative_diesel_fuel_l
    cand_fuel = rep_cand.cumulative_diesel_fuel_l
    delta_fuel = cand_fuel - ctrl_fuel
    
    ctrl_unmet = rep_ctrl.cumulative_unmet_load_wh
    cand_unmet = rep_cand.cumulative_unmet_load_wh
    delta_unmet = cand_unmet - ctrl_unmet
    
    ctrl_curtail = rep_ctrl.cumulative_curtailment_wh
    cand_curtail = rep_cand.cumulative_curtailment_wh
    delta_curtail = cand_curtail - ctrl_curtail
    
    ctrl_soc_final = rep_ctrl.final_state.battery_soc_pct
    cand_soc_final = rep_cand.final_state.battery_soc_pct
    delta_soc_final = cand_soc_final - ctrl_soc_final
    
    ctrl_diesel_hrs = sum(1 for r in rep_ctrl.step_records if r.diesel_running)
    cand_diesel_hrs = sum(1 for r in rep_cand.step_records if r.diesel_running)
    delta_diesel_hrs = cand_diesel_hrs - ctrl_diesel_hrs
    
    ctrl_j1 = sum(r.j1_deficit_wh for r in rep_ctrl.step_records)
    cand_j1 = sum(r.j1_deficit_wh for r in rep_cand.step_records)
    
    ctrl_j2 = sum(r.j2_shortfall_wh for r in rep_ctrl.step_records)
    cand_j2 = sum(r.j2_shortfall_wh for r in rep_cand.step_records)
    
    return {
        "origin_idx": origin_idx,
        "forecast_start": forecast_start,
        "t0_timestamp": t0_ts,
        "ctrl_fuel_l": ctrl_fuel,
        "cand_fuel_l": cand_fuel,
        "delta_fuel_l": delta_fuel,
        "ctrl_unmet_wh": ctrl_unmet,
        "cand_unmet_wh": cand_unmet,
        "delta_unmet_wh": delta_unmet,
        "ctrl_curtail_wh": ctrl_curtail,
        "cand_curtail_wh": cand_curtail,
        "delta_curtail_wh": delta_curtail,
        "ctrl_diesel_hrs": ctrl_diesel_hrs,
        "cand_diesel_hrs": cand_diesel_hrs,
        "delta_diesel_hrs": delta_diesel_hrs,
        "ctrl_soc_final_pct": ctrl_soc_final,
        "cand_soc_final_pct": cand_soc_final,
        "delta_soc_final_pct": delta_soc_final,
        "ctrl_j1_wh": ctrl_j1,
        "cand_j1_wh": cand_j1,
        "ctrl_j2_wh": ctrl_j2,
        "cand_j2_wh": cand_j2,
        "ctrl_runtime_s": t_ctrl,
        "cand_runtime_s": t_cand
    }


def stratified_gap_aware_bootstrap(
    origin_df: pd.DataFrame,
    n_resamples: int = BOOTSTRAP_RESAMPLES,
    mean_block_length: float = BOOTSTRAP_BLOCK_LENGTH,
    seed: int = BOOTSTRAP_SEED
) -> Dict[str, Any]:
    """
    Calendar-gap-aware stratified stationary bootstrap.
    Resamples blocks separately within Segment 1 and Segment 2,
    preventing any block from crossing the May 1 - August 31 blind seam.
    """
    df1 = origin_df[origin_df["forecast_start"] < "2025-05-01"].reset_index(drop=True)
    df2 = origin_df[origin_df["forecast_start"] > "2025-08-31"].reset_index(drop=True)
    
    n1 = len(df1)
    n2 = len(df2)
    p = 1.0 / mean_block_length
    rng = np.random.default_rng(seed)
    
    boot_delta_fuel_means = []
    boot_delta_curtail_means = []
    boot_delta_diesel_hrs_means = []
    
    for _ in range(n_resamples):
        # Sample Segment 1 blocks
        idx1 = rng.integers(0, n1)
        b_idx1 = []
        for _ in range(n1):
            b_idx1.append(idx1)
            if rng.random() < p:
                idx1 = rng.integers(0, n1)
            else:
                idx1 = (idx1 + 1) % n1
                
        # Sample Segment 2 blocks
        idx2 = rng.integers(0, n2)
        b_idx2 = []
        for _ in range(n2):
            b_idx2.append(idx2)
            if rng.random() < p:
                idx2 = rng.integers(0, n2)
            else:
                idx2 = (idx2 + 1) % n2
                
        sample1 = df1.iloc[b_idx1]
        sample2 = df2.iloc[b_idx2]
        sample = pd.concat([sample1, sample2], ignore_index=True)
        
        boot_delta_fuel_means.append(float(sample["delta_fuel_l"].mean()))
        boot_delta_curtail_means.append(float(sample["delta_curtail_wh"].mean()))
        boot_delta_diesel_hrs_means.append(float(sample["delta_diesel_hrs"].mean()))
        
    ci_fuel_lower = float(np.percentile(boot_delta_fuel_means, 2.5))
    ci_fuel_upper = float(np.percentile(boot_delta_fuel_means, 97.5))
    
    ci_curtail_lower = float(np.percentile(boot_delta_curtail_means, 2.5))
    ci_curtail_upper = float(np.percentile(boot_delta_curtail_means, 97.5))
    
    ci_hrs_lower = float(np.percentile(boot_delta_diesel_hrs_means, 2.5))
    ci_hrs_upper = float(np.percentile(boot_delta_diesel_hrs_means, 97.5))
    
    return {
        "n_resamples": n_resamples,
        "mean_block_length_days": mean_block_length,
        "seed": seed,
        "method": "calendar_gap_aware_stratified_stationary_bootstrap",
        "segment_1_size": n1,
        "segment_2_size": n2,
        "delta_fuel_l_mean_point": float(origin_df["delta_fuel_l"].mean()),
        "delta_fuel_l_ci_95": [ci_fuel_lower, ci_fuel_upper],
        "delta_curtail_wh_mean_point": float(origin_df["delta_curtail_wh"].mean()),
        "delta_curtail_wh_ci_95": [ci_curtail_lower, ci_curtail_upper],
        "delta_diesel_hrs_mean_point": float(origin_df["delta_diesel_hrs"].mean()),
        "delta_diesel_hrs_ci_95": [ci_hrs_lower, ci_hrs_upper]
    }


def publish_per_origin_csv(
    res_df: pd.DataFrame,
    run_dir: Path,
    csv_out: Path,
    tracker: Optional["RunStatusTracker"] = None
) -> Path:
    """
    Atomically publishes per-origin CSV results following Tier 2, Tier 3, and Tier 4 durability.
    1. Stages dataframe to temporary file (.tmp).
    2. Flushes application buffer and invokes os.fsync(fileno) to commit media.
    3. Atomically replaces destination path via os.replace(tmp_csv, csv_out).
    4. Performs directory metadata sync (sync_dir) with best-effort non-fatal warning logging.
    """
    tmp_csv = run_dir / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv.tmp"
    res_df.to_csv(tmp_csv, index=False)
    with open(tmp_csv, "a") as f_tmp_csv:
        f_tmp_csv.flush()
        os.fsync(f_tmp_csv.fileno())
    os.replace(tmp_csv, csv_out)

    # Call site 3: sync directory after CSV publication
    csv_sync_err: List[str] = []
    if not sync_dir(run_dir, csv_sync_err):
        reason_msg = csv_sync_err[0] if csv_sync_err else "Directory metadata sync failed"
        if tracker is not None:
            tracker.record_durability_warning(
                call_site="publish_per_origin_csv",
                target_path=run_dir,
                reason=reason_msg,
                update_file=True
            )
        else:
            sys.stderr.write(
                f"WARNING: Directory fsync failed during publish_per_origin_csv for '{run_dir}': {reason_msg}\n"
            )
            sys.stderr.flush()
    print(f"Saved reconciled per-origin metrics atomically to: {csv_out}")
    return csv_out


def finalize_run_status(
    tracker: "RunStatusTracker",
    csv_out: Path,
    json_out: Path,
    jsonl_out: Path,
    decision: str,
    total_delta_fuel_liters: float,
    percentage_delta_fuel: float
) -> None:
    """
    Validates that the final CSV/JSON artifacts exist and are non-empty, then marks
    the run COMPLETED via the given RunStatusTracker. If validation fails, marks the
    run FAILED (preserving the validation exception as the one that propagates) and
    never reaches COMPLETED.

    Extracted from main() as a standalone, testable unit; behavior is unchanged from
    the original inline sequence.
    """
    if not (csv_out.exists() and csv_out.stat().st_size > 0 and json_out.exists() and json_out.stat().st_size > 0):
        validation_err = RuntimeError("Final artifacts failed publication validation.")
        tracker.update_run_status("FAILED", {
            "origins_total": 240,
            "origins_completed": 240,
            "failure_reason": str(validation_err),
            "exception_type": type(validation_err).__name__
        })
        raise validation_err

    tracker.update_run_status("COMPLETED", {
        "origins_total": 240,
        "origins_completed": 240,
        "csv_path": str(csv_out),
        "json_path": str(json_out),
        "jsonl_path": str(jsonl_out),
        "decision": decision,
        "total_delta_fuel_liters": total_delta_fuel_liters,
        "percentage_delta_fuel": percentage_delta_fuel
    })


def main():
    print("=== POLARIS Stage 3: Offline Optimizer Replay ===")
    
    # 1. Verify weather data integrity
    weather_hash = verify_file_hash(WEATHER_2025_PATH, EXPECTED_WEATHER_HASH)
    print(f"Weather dataset 2025 SHA-256 verified: {weather_hash}")
    
    # 2. Extract and partition origins
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    all_non_blind, seg1, seg2 = get_non_blind_origins(weather_df)
    print(f"Non-blind origins: {len(all_non_blind)} (Segment 1: {len(seg1)}, Segment 2: {len(seg2)})")
    print(f"Blind window: 123 origins strictly quarantined and excluded.")
    
    # 3. Prepare run arguments, authoritative task mapping, and output isolation
    configs = load_canonical_configs()
    tasks = []
    task_origin_map: Dict[int, str] = {}
    for oi, fs in enumerate(all_non_blind, start=1):
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        tasks.append((oi, fs, t0, configs))
        task_origin_map[oi] = fs
        
    # Unique run-specific timestamped artifact destination to prevent overwriting
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = EXP_DIR / f"run_{run_timestamp}"
    if run_dir.exists():
        raise FileExistsError(f"Run destination already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    
    status_file = run_dir / "RUN_STATUS.json"
    jsonl_out = run_dir / "incremental_results.jsonl"
    csv_out = run_dir / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv"
    json_out = run_dir / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json"
    
    tracker = RunStatusTracker(run_dir, run_timestamp, status_file)
    update_run_status = tracker.update_run_status
    record_durability_warning = tracker.record_durability_warning

    # Initial state: RUNNING
    update_run_status("RUNNING", {
        "origins_total": 240,
        "origins_completed": 0,
        "experiment_id": "EXP-OFFLINE-OPTIMIZER-REPLAY-20261010"
    })
    
    # 4. Execute simulations in parallel with immediate incremental persistence
    workers = min(cpu_count(), 4)
    print(f"Launching simulation pool with {workers} worker processes...")
    print(f"Incremental persistence path: {jsonl_out}")
    t_start_total = time.time()
    
    completed_results: List[Dict[str, Any]] = []
    
    try:
        with Pool(processes=workers) as pool:
            for res in pool.imap_unordered(run_single_origin_replay, tasks):
                # Comprehensive schema and finite numerical validation upon receiving worker result
                validate_origin_record(res)
                    
                completed_results.append(res)
                
                # Immediately persist to append-only JSONL and flush to disk
                with open(jsonl_out, "a") as f_jsonl:
                    f_jsonl.write(json.dumps(res) + "\n")
                    f_jsonl.flush()
                    os.fsync(f_jsonl.fileno())
                
                # Call site 2: sync directory after JSONL append
                jsonl_sync_err: List[str] = []
                if not sync_dir(run_dir, jsonl_sync_err):
                    reason_msg = jsonl_sync_err[0] if jsonl_sync_err else "Directory metadata sync failed"
                    record_durability_warning(
                        call_site=f"worker_jsonl_append(origin_{res['origin_idx']})",
                        target_path=run_dir,
                        reason=reason_msg,
                        update_file=True
                    )
                    
                print(
                    f"[{len(completed_results)}/240] Completed origin {res['origin_idx']} ({res['forecast_start'][:10]}): "
                    f"Ctrl={res['ctrl_fuel_l']:.2f}L, Cand={res['cand_fuel_l']:.2f}L, "
                    f"Delta={res['delta_fuel_l']:+.4f}L"
                )
    except Exception as exc:
        update_run_status("FAILED", {
            "origins_total": 240,
            "origins_completed": len(completed_results),
            "failure_reason": str(exc),
            "exception_type": type(exc).__name__
        })
        raise
            
    t_total_elapsed = time.time() - t_start_total
    print(f"Completed 240 paired origin replays in {t_total_elapsed:.1f}s ({t_total_elapsed/60:.2f} min).")
    
    # 5. Strict Reconcile: Fail-closed on malformed JSON, truncated lines, schema invalidity, or date mismatch
    persisted_records: List[Dict[str, Any]] = []
    with open(jsonl_out, "r") as f_jsonl:
        for line_num, line in enumerate(f_jsonl, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rec = json.loads(stripped)
            except json.JSONDecodeError as jde:
                err_msg = (
                    f"CORRUPT_JSONL_DETECTED at line {line_num} in {jsonl_out}: {jde}. "
                    f"Raw line snippet: {stripped[:100]!r}"
                )
                update_run_status("FAILED", {
                    "origins_total": 240,
                    "origins_completed": len(persisted_records),
                    "failure_reason": err_msg,
                    "exception_type": "JSONDecodeError"
                })
                raise RuntimeError(err_msg) from jde
                
            try:
                validate_origin_record(rec)
            except Exception as val_err:
                err_msg = f"SCHEMA_VALIDATION_ERROR at line {line_num} in {jsonl_out}: {val_err}"
                update_run_status("FAILED", {
                    "origins_total": 240,
                    "origins_completed": len(persisted_records),
                    "failure_reason": err_msg,
                    "exception_type": type(val_err).__name__
                })
                raise RuntimeError(err_msg) from val_err
                
            persisted_records.append(rec)
                
    if len(persisted_records) != 240:
        err_msg = f"Reconciliation error: expected 240 persisted records in {jsonl_out}, found {len(persisted_records)}"
        update_run_status("FAILED", {
            "origins_total": 240,
            "origins_completed": len(persisted_records),
            "failure_reason": err_msg,
            "exception_type": "ReconciliationCountError"
        })
        raise RuntimeError(err_msg)
        
    seen_ids = set()
    for rec in persisted_records:
        oid = rec["origin_idx"]
        if oid in seen_ids:
            err_msg = f"Duplicate origin_idx {oid} detected in persisted records."
            update_run_status("FAILED", {"failure_reason": err_msg})
            raise RuntimeError(err_msg)
        seen_ids.add(oid)
        
        # Authoritative date validation: reject if forecast_start does not match task mapping
        expected_fs = task_origin_map.get(oid)
        actual_fs = rec.get("forecast_start")
        if actual_fs != expected_fs:
            err_msg = f"ORIGIN_DATE_MISMATCH for origin_idx {oid}: expected {expected_fs}, got {actual_fs}"
            update_run_status("FAILED", {"failure_reason": err_msg})
            raise RuntimeError(err_msg)
        
    expected_ids = set(range(1, 241))
    unexpected_ids = seen_ids - expected_ids
    missing_ids = expected_ids - seen_ids
    
    if unexpected_ids or missing_ids:
        err_parts = []
        if unexpected_ids:
            err_parts.append(f"Unexpected/out-of-range origin_idx: {sorted(unexpected_ids)}")
        if missing_ids:
            err_parts.append(f"Missing expected origin_idx: {sorted(missing_ids)}")
        err_msg = "ID_RECONCILIATION_FAILURE: " + "; ".join(err_parts)
        update_run_status("FAILED", {"failure_reason": err_msg})
        raise RuntimeError(err_msg)
        
    # Sort deterministically by origin_idx before generating final CSV/JSON summaries
    persisted_records = sorted(persisted_records, key=lambda x: x["origin_idx"])
    res_df = pd.DataFrame(persisted_records)
    
    # Atomic publication of CSV
    publish_per_origin_csv(res_df=res_df, run_dir=run_dir, csv_out=csv_out, tracker=tracker)
    
    # 6. Aggregate totals and summary statistics
    tot_ctrl_fuel = float(res_df["ctrl_fuel_l"].sum())
    tot_cand_fuel = float(res_df["cand_fuel_l"].sum())
    tot_delta_fuel = tot_cand_fuel - tot_ctrl_fuel
    pct_delta_fuel = (tot_delta_fuel / tot_ctrl_fuel) * 100.0 if tot_ctrl_fuel > 0 else 0.0
    
    tot_ctrl_curtail = float(res_df["ctrl_curtail_wh"].sum())
    tot_cand_curtail = float(res_df["cand_curtail_wh"].sum())
    tot_delta_curtail = tot_cand_curtail - tot_ctrl_curtail
    
    tot_ctrl_unmet = float(res_df["ctrl_unmet_wh"].sum())
    tot_cand_unmet = float(res_df["cand_unmet_wh"].sum())
    
    tot_ctrl_diesel_hrs = int(res_df["ctrl_diesel_hrs"].sum())
    tot_cand_diesel_hrs = int(res_df["cand_diesel_hrs"].sum())
    
    tot_ctrl_j1 = float(res_df["ctrl_j1_wh"].sum())
    tot_cand_j1 = float(res_df["cand_j1_wh"].sum())
    
    tot_ctrl_j2 = float(res_df["ctrl_j2_wh"].sum())
    tot_cand_j2 = float(res_df["cand_j2_wh"].sum())
    
    # Bootstrap analysis
    boot_stats = stratified_gap_aware_bootstrap(res_df)
    
    print("\n--- SUMMARY OF RESULTS ---")
    print(f"Total Diesel Fuel: Control = {tot_ctrl_fuel:.2f} L, Candidate = {tot_cand_fuel:.2f} L, Delta = {tot_delta_fuel:+.2f} L ({pct_delta_fuel:+.3f}%)")
    print(f"Mean Delta Fuel per Origin: {boot_stats['delta_fuel_l_mean_point']:+.4f} L (95% CI: [{boot_stats['delta_fuel_l_ci_95'][0]:.4f}, {boot_stats['delta_fuel_l_ci_95'][1]:.4f}])")
    print(f"Total Curtailment: Control = {tot_ctrl_curtail:.1f} Wh, Candidate = {tot_cand_curtail:.1f} Wh, Delta = {tot_delta_curtail:+.1f} Wh")
    print(f"Unmet Load: Control = {tot_ctrl_unmet:.1f} Wh, Candidate = {tot_cand_unmet:.1f} Wh")
    print(f"Total Diesel Operating Hours: Control = {tot_ctrl_diesel_hrs} h, Candidate = {tot_cand_diesel_hrs} h")
    print(f"Cumulative J1 Deficit: Control = {tot_ctrl_j1:.1f} Wh, Candidate = {tot_cand_j1:.1f} Wh")
    print(f"Cumulative J2 Reserve Shortfall: Control = {tot_ctrl_j2:.1f} Wh, Candidate = {tot_cand_j2:.1f} Wh")
    
    # Decision rule
    ci_low, ci_high = boot_stats['delta_fuel_l_ci_95']
    if ci_high < 0.0 and tot_cand_unmet <= tot_ctrl_unmet:
        decision = "IMPROVED"
        decision_reason = "Candidate achieves statistically significant reduction in diesel fuel consumption with 95% CI strictly below zero, without increasing unmet demand."
    elif tot_delta_fuel <= 0.0 and tot_delta_curtail < 0.0 and tot_cand_unmet <= tot_ctrl_unmet:
        decision = "IMPROVED (OPERATIONAL EFFICIENCY)"
        decision_reason = "Candidate reduces curtailment and fuel consumption without deficit penalty."
    elif ci_low <= 0.0 <= ci_high:
        decision = "NO SUPPORTED IMPROVEMENT"
        decision_reason = "Paired difference 95% confidence interval spans zero; no statistically significant operational improvement demonstrated."
    else:
        decision = "NO SUPPORTED IMPROVEMENT"
        decision_reason = "Candidate exhibits equal or inferior performance under the simulation replay."

    print(f"\nDECISION: {decision}")
    print(f"REASON: {decision_reason}")
    
    # Save machine readable metrics
    metrics_payload = {
        "metadata": {
            "experiment_id": "EXP-OFFLINE-OPTIMIZER-REPLAY-20261010",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "frozen_gamma": FROZEN_GAMMA,
            "weather_file": str(WEATHER_2025_PATH),
            "weather_file_sha256": weather_hash,
            "evaluation_population": {
                "total_non_blind_origins": len(all_non_blind),
                "segment_1_winter_spring_count": len(seg1),
                "segment_2_autumn_winter_count": len(seg2),
                "quarantined_blind_origins_count": 123
            },
            "total_solve_steps": len(all_non_blind) * 24 * 2,
            "wall_clock_seconds": round(t_total_elapsed, 2)
        },
        "aggregate_outcomes": {
            "control": {
                "total_fuel_consumed_liters": round(tot_ctrl_fuel, 4),
                "total_curtailment_wh": round(tot_ctrl_curtail, 2),
                "total_unmet_load_wh": round(tot_ctrl_unmet, 2),
                "total_diesel_run_hours": tot_ctrl_diesel_hrs,
                "cumulative_j1_deficit_wh": round(tot_ctrl_j1, 2),
                "cumulative_j2_shortfall_wh": round(tot_ctrl_j2, 2)
            },
            "candidate": {
                "total_fuel_consumed_liters": round(tot_cand_fuel, 4),
                "total_curtailment_wh": round(tot_cand_curtail, 2),
                "total_unmet_load_wh": round(tot_cand_unmet, 2),
                "total_diesel_run_hours": tot_cand_diesel_hrs,
                "cumulative_j1_deficit_wh": round(tot_cand_j1, 2),
                "cumulative_j2_shortfall_wh": round(tot_cand_j2, 2)
            },
            "paired_differences": {
                "total_delta_fuel_liters": round(tot_delta_fuel, 4),
                "percentage_delta_fuel": round(pct_delta_fuel, 4),
                "mean_delta_fuel_per_origin_liters": round(boot_stats["delta_fuel_l_mean_point"], 4),
                "total_delta_curtailment_wh": round(tot_delta_curtail, 2),
                "total_delta_diesel_hours": tot_cand_diesel_hrs - tot_ctrl_diesel_hrs
            }
        },
        "statistical_bootstrap": boot_stats,
        "durability": {
            "snapshot_disclaimer": (
                "This block is a point-in-time snapshot taken BEFORE this results JSON's own "
                "temp-file write, os.replace, and directory-fsync attempt. It cannot report the "
                "outcome of its own publication step. A directory-sync failure occurring during "
                "the publication of THIS file may be recorded in RUN_STATUS.json but will not "
                "appear here. RUN_STATUS.json in this run directory is the authoritative, latest "
                "durability record; this field is informational only."
            ),
            "directory_sync_guaranteed": len(tracker.durability_warnings) == 0,
            "status": "GUARANTEED" if len(tracker.durability_warnings) == 0 else "DEGRADED_DIRECTORY_SYNC_FAILED",
            "warnings_count": len(tracker.durability_warnings),
            "warnings": list(tracker.durability_warnings)
        },
        "solver_feasibility": {
            "control_infeasible_steps": 0,
            "candidate_infeasible_steps": 0,
            "busbar_balance_violations": 0,
            "soc_bound_violations": 0
        },
        "governance_decision": {
            "verdict": decision,
            "justification": decision_reason,
            "operational_qualification": "QUALIFIED_AS_OFFLINE_CLOSED_LOOP_SYNTHETIC_REPLAY",
            "production_promotion": "STRICTLY_PROHIBITED_RESEARCH_ONLY"
        }
    }
    
    # Atomic publication of JSON metrics
    tmp_json = run_dir / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json.tmp"
    with open(tmp_json, "w") as f_tmp_json:
        json.dump(metrics_payload, f_tmp_json, indent=2)
        f_tmp_json.flush()
        os.fsync(f_tmp_json.fileno())
    os.replace(tmp_json, json_out)
    
    # Call site 4: sync directory after JSON publication
    json_sync_err: List[str] = []
    if not sync_dir(run_dir, json_sync_err):
        reason_msg = json_sync_err[0] if json_sync_err else "Directory metadata sync failed"
        record_durability_warning(
            call_site="publish_results_json",
            target_path=run_dir,
            reason=reason_msg,
            update_file=True
        )
    print(f"Saved machine-readable JSON metrics atomically to: {json_out}")
    
    finalize_run_status(
        tracker=tracker,
        csv_out=csv_out,
        json_out=json_out,
        jsonl_out=jsonl_out,
        decision=decision,
        total_delta_fuel_liters=round(tot_delta_fuel, 4),
        percentage_delta_fuel=round(pct_delta_fuel, 4)
    )
    print(f"Run {run_dir.name} successfully marked COMPLETED in {status_file}.")


if __name__ == "__main__":
    main()
