import csv
import json
from pathlib import Path

v4g_csv = Path("ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv")
v3_csv = Path("ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv")

with open(v4g_csv, "r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    v4g_fields = r.fieldnames
    v4g_first = next(r)

print(f"V4G Raw CSV Fields ({len(v4g_fields)}): {v4g_fields}")

with open(v3_csv, "r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    v3_fields = r.fieldnames
    v3_first = next(r)

print(f"V3 Raw CSV Fields ({len(v3_fields)}): {v3_fields}")
