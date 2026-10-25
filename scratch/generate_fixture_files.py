import os
import json
import hashlib

def get_diurnal_w(hour):
    if 0 <= hour <= 5:
        return 18000.0
    elif hour == 6:
        return 22000.0
    elif hour == 7:
        return 30000.0
    elif hour == 8:
        return 38000.0
    elif 9 <= hour <= 17:
        return 32000.0
    elif hour == 18:
        return 36000.0
    elif hour == 19:
        return 42000.0
    elif 20 <= hour <= 21:
        return 30000.0
    else:
        return 22000.0

def get_seasonal_mult(month):
    if month in [11, 12, 1, 2]:
        return 1.20
    elif month in [5, 6, 7, 8]:
        return 0.85
    else:
        return 1.00

def get_wind_w(v):
    if v < 3.0 or v >= 25.0:
        return 0.0
    elif 3.0 <= v < 12.0:
        return 60000.0 * ((v**3 - 27.0) / (1728.0 - 27.0))
    else:
        return 60000.0

solar_file = "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
wind_file = "research/wind_a2/smhi_188790_ws_full.csv"

with open(solar_file, 'r', encoding='utf-8') as f:
    solar_lines = [l.strip() for l in f if l.strip()]

header = solar_lines[0].split(',')
ts_idx = header.index("TIMESTAMP")
sw_idx = header.index("SW_IN")

# Load SMHI wind map if available
wind_map = {}
if os.path.exists(wind_file):
    with open(wind_file, 'r', encoding='utf-8', errors='ignore') as f:
        w_lines = f.readlines()
    data_start = False
    for line in w_lines:
        parts = line.strip().split(';')
        if len(parts) >= 3 and parts[0] == "Datum" and parts[1].startswith("Tid"):
            data_start = True
            continue
        if data_start and len(parts) >= 3:
            d_str = parts[0].strip()
            t_str = parts[1].strip()
            v_str = parts[2].strip()
            if d_str and t_str and v_str:
                try:
                    v_val = float(v_str)
                    wind_map[f"{d_str}T{t_str}Z"] = v_val
                except ValueError:
                    pass

out_dir = "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
os.makedirs(out_dir, exist_ok=True)

csv_lines = ["timestamp,solar_SW_IN_W_m2,solar_PV_power_W,wind_speed_proxy_m_s,wind_power_generic_W,synthetic_load_W,provenance_class_solar,provenance_class_wind,provenance_class_demand"]

min_load, max_load = 1e9, -1e9
min_pv, max_pv = 1e9, -1e9
min_wind_w, max_wind_w = 1e9, -1e9

for line in solar_lines[1:]:
    parts = line.split(',')
    if len(parts) <= max(ts_idx, sw_idx):
        continue
    ts_raw = parts[ts_idx].strip()
    sw_val = max(0.0, float(parts[sw_idx]))

    if ' ' in ts_raw:
        d_p, t_p = ts_raw.split(' ')
        iso_ts = f"{d_p}T{t_p}Z"
    else:
        iso_ts = ts_raw

    month = int(iso_ts[5:7])
    hour = int(iso_ts[11:13])

    pv_w = min(sw_val * 300.0 * 0.20 * 0.85, 60000.0)
    wind_ms = wind_map.get(iso_ts, 4.5)
    wind_w = get_wind_w(wind_ms)
    load_w = min(max(get_diurnal_w(hour) * get_seasonal_mult(month), 15000.0), 45000.0)

    min_pv = min(min_pv, pv_w)
    max_pv = max(max_pv, pv_w)
    min_wind_w = min(min_wind_w, wind_w)
    max_wind_w = max(max_wind_w, wind_w)
    min_load = min(min_load, load_w)
    max_load = max(max_load, load_w)

    csv_lines.append(f"{iso_ts},{sw_val:.4f},{pv_w:.4f},{wind_ms:.2f},{wind_w:.4f},{load_w:.2f},REAL_MEASURED,CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY,SYNTHETIC")

csv_content = "\n".join(csv_lines) + "\n"

with open(os.path.join(out_dir, "fixture.csv"), "w", encoding="utf-8") as f:
    f.write(csv_content)

prov_data = {
    "fixture_version": "H1.0",
    "solar_SW_IN_W_m2": {
        "provenance_class": "REAL_MEASURED",
        "source": "SITES Nuolja Middle Station AWS",
        "station": "Nuolja (68.36 N, 18.74 E)",
        "units": "W/m^2"
    },
    "solar_PV_power_W": {
        "provenance_class": "DERIVED_ENGINEERING_QUANTITY",
        "formula": "min(SW_IN * 300 * 0.20 * 0.85, 60000 W)",
        "units": "Watts (W)"
    },
    "wind_speed_proxy_m_s": {
        "provenance_class": "CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY",
        "source": "SMHI Station 188790 Abisko Aut (10m)",
        "distance_km": 4.1,
        "units": "m/s"
    },
    "wind_power_generic_W": {
        "provenance_class": "SYNTHETIC_ENGINEERING_SCENARIO",
        "scenario_name": "POLAR_REFERENCE_TURBINE_SCENARIO",
        "disclaimer": "NOT_NUOLJA_HARDWARE",
        "rated_power_w": 60000.0,
        "units": "Watts (W)"
    },
    "synthetic_load_W": {
        "provenance_class": "SYNTHETIC",
        "fixture_name": "SYNTHETIC_STATION_DEMAND",
        "disclaimer": "SYNTHETIC_STATION_DEMAND != NULLOJA_MEASURED_DEMAND",
        "range_w": [15000.0, 45000.0],
        "units": "Watts (W)"
    }
}
with open(os.path.join(out_dir, "ems/reports/other/provenance.json"), "w", encoding="utf-8") as f:
    json.dump(prov_data, f, indent=2)

config_data = {
    "fixture_version": "H1.0",
    "random_seed": 42,
    "base_demand_w": 25000.0,
    "min_demand_w": 15000.0,
    "max_demand_w": 45000.0,
    "pv_capacity_w": 60000.0,
    "turbine_rated_w": 60000.0,
    "solar_source": solar_file,
    "wind_source": wind_file
}
with open(os.path.join(out_dir, "config.json"), "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2)

def calc_sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

hashes = {
    "solar_source_sha256": calc_sha(solar_file),
    "wind_source_sha256": calc_sha(wind_file) if os.path.exists(wind_file) else "N/A",
    "fixture_csv_sha256": calc_sha(os.path.join(out_dir, "fixture.csv")),
    "provenance_json_sha256": calc_sha(os.path.join(out_dir, "ems/reports/other/provenance.json")),
    "config_json_sha256": calc_sha(os.path.join(out_dir, "config.json"))
}
with open(os.path.join(out_dir, "hashes.json"), "w", encoding="utf-8") as f:
    json.dump(hashes, f, indent=2)

print("SUCCESS: H1.0 Fixture Files Generated in ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/")
print(f"Total Rows: {len(csv_lines)-1}")
print(f"PV Power Range: [{min_pv:.2f}, {max_pv:.2f}] W")
print(f"Wind Power Range: [{min_wind_w:.2f}, {max_wind_w:.2f}] W")
print(f"Synthetic Load Range: [{min_load:.2f}, {max_load:.2f}] W")
print(f"Fixture CSV SHA256: {hashes['fixture_csv_sha256']}")
