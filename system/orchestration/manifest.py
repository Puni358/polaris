import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import os, json, hashlib, platform, sys
from pathlib import Path
from datetime import datetime, timezone

PROTECTED_FILES = [
    "system/optimization/implementations/gap19_highs_native.py",
    "system/optimization/implementations/option_d.py",
    "system/control/ecd.py",
    "system/control/router.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py"
]

def hash_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class RunManifest:
    @staticmethod
    def generate_manifest(
        run_id: str,
        system_dir: Path,
        scenario_file: str = "h10_scenario_temp.json",
        requested_workers: int = 8,
        selected_workers: int = 8,
        checkpoint_interval: int = 500,
        authorized: bool = False
    ) -> dict:
        scenarios_dir = system_dir / "data" / "scenarios"
        scenario_path = scenarios_dir / scenario_file
        
        protected_hashes = {}
        for pf in PROTECTED_FILES:
            full_p = system_dir.parent / pf if not (system_dir / pf).exists() else system_dir / pf
            if full_p.exists():
                protected_hashes[pf] = hash_file(str(full_p))
            elif Path(pf).exists():
                protected_hashes[pf] = hash_file(pf)
                
        fixture_hash = hash_file(str(scenario_path)) if scenario_path.exists() else "UNAVAILABLE"
        
        manifest = {
            "schema_version": "1.0.0",
            "run_id": run_id,
            "created_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "human_execution_authorization": "GRANTED" if authorized else "NOT_GRANTED",
            "time_domain": "Full-calendar-year 2024 / 8,784 hourly cycles",
            "start_timestamp": "2024-01-01T00:00:00Z",
            "end_timestamp": "2024-12-31T23:00:00Z",
            "timezone": "UTC",
            "total_cycles": 8784,
            "fuel_scenario": "SCENARIO_FUEL_1_INFINITE_CUMULATIVE",
            "comparison_matrix": {
                "cell_a2": "Reactive Hybrid Baseline (No Forecast, No MILP, 8-rule Reactive Dispatch)",
                "cell_b": "Complete POLARIS Closed-Loop System (Option B Native HiGHS MILP / Router)"
            },
            "gate02_compliance": "OPTION_C_COMPULSORY_CRITICAL_LOAD",
            "requested_workers": requested_workers,
            "selected_workers": selected_workers,
            "checkpoint_interval": checkpoint_interval,
            "environment": {
                "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
                "python_version": sys.version.split()[0],
                "executable": sys.executable
            },
            "protected_source_hashes": protected_hashes,
            "fixture_hash": fixture_hash
        }
        return manifest
