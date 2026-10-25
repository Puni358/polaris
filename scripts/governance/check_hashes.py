import hashlib
from pathlib import Path

files = [
    "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv",
    "forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv",
    "system/forecasting/implementations/s81_solar.py",
    "system/forecasting/implementations/baseline.py",
    "system/optimization/implementations/milp.py",
    "system/schemas/forecast_bundle.py",
    "system/schemas/station_state.py",
    "system/schemas/dispatch_plan.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.md",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.md",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_AUTHORIZATION.md",
    "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_RESOURCE_CONFIGURATION_CORRECTION.md"
]

base = Path(".")
for f in files:
    p = base / f
    if p.exists():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f'"{f}": "{h}",')
    else:
        print(f'"{f}": "MISSING",')
