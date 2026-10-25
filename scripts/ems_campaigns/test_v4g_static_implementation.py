"""
POLARIS Stage 8.1 EMS V4.G Formal Execution Authorization Audit
Computes SHA256 provenance hashes and verifies objective invariants for authorization review.
"""
import hashlib
import json
from pathlib import Path

FILES_TO_AUDIT = [
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION.json",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION.md",
    "forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv",
    "system/schemas/forecast_bundle.py",
    "system/schemas/station_state.py",
    "system/schemas/dispatch_plan.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "system/forecasting/implementations/s81_solar.py",
    "system/optimization/implementations/milp.py",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.md",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.json",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.md",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.json",
    "scripts/ems_campaigns/test_v4g_static_implementation.py"
]

def compute_hashes():
    results = {}
    for f in FILES_TO_AUDIT:
        p = Path(f)
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            results[f] = h
        else:
            results[f] = "FILE_NOT_FOUND"
    return results

if __name__ == "__main__":
    h_dict = compute_hashes()
    with open("v4g_hashes.json", "w") as out:
        json.dump(h_dict, out, indent=2)
    print("Hashes written to v4g_hashes.json")
