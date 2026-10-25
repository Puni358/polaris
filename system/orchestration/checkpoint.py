import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import os, json, hashlib
from pathlib import Path
from typing import Dict, Any, Optional

CHECKPOINT_SCHEMA_VERSION = 1

class CheckpointManager:
    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def create_checkpoint(
        checkpoint_dir: Path,
        run_id: str,
        cell_id: str,
        worker_id: str,
        cycle_index: int,
        timestamp: str,
        station_state_dict: dict,
        cumulative_fuel_l: float,
        cumulative_diesel_energy_kwh: float,
        cumulative_battery_throughput_kwh: float,
        integrity_counters: dict,
        protected_hashes: dict,
        fixture_hash: str,
        previous_checkpoint_hash: str = "GENESIS"
    ) -> Path:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        filename = f"checkpoint_{cycle_index:06d}.json"
        filepath = checkpoint_dir / filename
        
        body = {
            "schema_version": CHECKPOINT_SCHEMA_VERSION,
            "run_id": run_id,
            "cell_id": cell_id,
            "worker_id": worker_id,
            "cycle_index": cycle_index,
            "timestamp": timestamp,
            "station_state": station_state_dict,
            "cumulative_fuel_l": round(cumulative_fuel_l, 4),
            "cumulative_diesel_energy_kwh": round(cumulative_diesel_energy_kwh, 4),
            "cumulative_battery_throughput_kwh": round(cumulative_battery_throughput_kwh, 4),
            "integrity_counters": integrity_counters,
            "protected_hashes": protected_hashes,
            "fixture_hash": fixture_hash,
            "previous_checkpoint_hash": previous_checkpoint_hash
        }
        
        # Self-compute payload hash
        payload_str = json.dumps(body, sort_keys=True)
        body["current_checkpoint_hash"] = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(body, f, indent=2)
            
        return filepath

    @staticmethod
    def verify_and_load(
        filepath: Path,
        expected_run_id: str,
        expected_cell_id: str,
        expected_protected_hashes: Optional[dict] = None
    ) -> dict:
        if not filepath.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {filepath}")
            
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if data.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
            raise ValueError(f"Checkpoint schema version mismatch in {filepath}")
            
        if data.get("run_id") != expected_run_id:
            raise ValueError(f"Checkpoint run_id mismatch: expected {expected_run_id}, got {data.get('run_id')}")
            
        if data.get("cell_id") != expected_cell_id:
            raise ValueError(f"Checkpoint cell_id mismatch: expected {expected_cell_id}, got {data.get('cell_id')}")
            
        # Verify hash self-consistency
        saved_hash = data.get("current_checkpoint_hash")
        data_copy = dict(data)
        data_copy.pop("current_checkpoint_hash", None)
        recalculated = hashlib.sha256(json.dumps(data_copy, sort_keys=True).encode("utf-8")).hexdigest()
        
        if saved_hash != recalculated:
            raise ValueError(f"Checkpoint hash corrupted in {filepath}!")
            
        if expected_protected_hashes:
            for k, v in expected_protected_hashes.items():
                if data.get("protected_hashes", {}).get(k) != v:
                    raise ValueError(f"Protected component hash changed in checkpoint {filepath} for {k}")
                    
        return data
