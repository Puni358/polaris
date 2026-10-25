"""
POLARIS H1.0 Hybrid Fixture Canonical Generator & Determinism Verification Script
"""

import os
import sys
import json
import math
import hashlib

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_string_sha256(data_str):
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

def get_diurnal_w(hour):
    if 0 <= hour <= 5:
        return 18000.0
    elif hour == 6:
        return 22000.0
    elif hour == 7:
        return 30000.0
    elif hour == 8:
        return 38000.0  # Morning Peak
    elif 9 <= hour <= 17:
        return 32000.0  # Day Sustained
    elif hour == 18:
        return 36000.0
    elif hour == 19:
        return 42000.0  # Evening Peak
    elif 20 <= hour <= 21:
        return 30000.0
    else:
        return 22000.0

def get_seasonal_multiplier(month):
    if month in [11, 12, 1, 2]:
        return 1.20
    elif month in [5, 6, 7, 8]:
        return 0.85
    else:
        return 1.00

def get_wind_power(v):
    if v < 3.0 or v >= 25.0:
        return 0.0
    elif 3.0 <= v < 12.0:
        return 60000.0 * ((v**3 - 3.0**3) / (12.0**3 - 3.0**3))
    else:
        return 60000.0

def generate_h10_fixture_content():
    solar_file = "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
    wind_file = "research/wind_a2/smhi_188790_ws_full.csv"

    # Read solar file lines
    with open(solar_file, 'r', encoding='utf-8') as f:
        solar_lines = [l.strip() for l in f if l.strip()]

    header = solar_lines[0].split(',')
    ts_idx = header.index("TIMESTAMP")
    sw_idx = header.index("SW_IN")

    # Read SMHI wind data lookup map if available
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
                        iso_k = f"{d_str}T{t_str}Z"
                        wind_map[iso_k] = v_val
                    except ValueError:
                        pass

    default_wind_ms = 4.5  # Standard regional proxy fallback

    csv_rows = []
    csv_rows.append("timestamp,solar_SW_IN_W_m2,solar_PV_power_W,wind_speed_proxy_m_s,wind_power_generic_W,synthetic_load_W,provenance_class_solar,provenance_class_wind,provenance_class_demand")

    rows_data = []
    for line in solar_lines[1:]:
        parts = line.split(',')
        if len(parts) <= max(ts_idx, sw_idx):
            continue
        ts_raw = parts[ts_idx].strip()
        sw_val = max(0.0, float(parts[sw_idx]))

        if ' ' in ts_raw:
            d_part, t_part = ts_raw.split(' ')
            iso_ts = f"{d_part}T{t_part}Z"
        else:
            iso_ts = ts_raw

        month = int(iso_ts[5:7])
        hour = int(iso_ts[11:13])

        # Solar PV (D3)
        p_raw = sw_val * 300.0 * 0.20 * 0.85
        p_solar = min(p_raw, 60000.0)

        # Wind
        wind_ms = wind_map.get(iso_ts, default_wind_ms)
        p_wind = get_wind_power(wind_ms)

        # Synthetic Demand
        diurnal_w = get_diurnal_w(hour)
        season_mult = get_seasonal_multiplier(month)
        p_load = min(max(diurnal_w * season_mult, 15000.0), 45000.0)

        row_str = f"{iso_ts},{sw_val:.4f},{p_solar:.4f},{wind_ms:.2f},{p_wind:.4f},{p_load:.2f},REAL_MEASURED,CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY,SYNTHETIC"
        csv_rows.append(row_str)
        rows_data.append({
            "ts": iso_ts,
            "sw_in": sw_val,
            "p_solar": p_solar,
            "wind_ms": wind_ms,
            "p_wind": p_wind,
            "p_load": p_load
        })

    fixture_csv_str = "\n".join(csv_rows) + "\n"

    prov_json_data = {
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
    prov_json_str = json.dumps(prov_json_data, indent=2) + "\n"

    config_json_data = {
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
    config_json_str = json.dumps(config_json_data, indent=2) + "\n"

    return fixture_csv_str, prov_json_str, config_json_str, rows_data

if __name__ == "__main__":
    out_dir = "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
    os.makedirs(out_dir, exist_ok=True)

    csv_a, prov_a, cfg_a, rows_data = generate_h10_fixture_content()

    csv_path = os.path.join(out_dir, "fixture.csv")
    prov_path = os.path.join(out_dir, "ems/reports/other/provenance.json")
    cfg_path = os.path.join(out_dir, "config.json")
    hash_path = os.path.join(out_dir, "hashes.json")

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_a)
    with open(prov_path, "w", encoding="utf-8") as f:
        f.write(prov_a)
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(cfg_a)

    csv_sha_a = compute_sha256(csv_path)
    prov_sha_a = compute_sha256(prov_path)
    cfg_sha_a = compute_sha256(cfg_path)
    solar_sha = compute_sha256("data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv")
    wind_sha = compute_sha256("research/wind_a2/smhi_188790_ws_full.csv")

    hashes_data = {
        "solar_source_sha256": solar_sha,
        "wind_source_sha256": wind_sha,
        "fixture_csv_sha256": csv_sha_a,
        "provenance_json_sha256": prov_sha_a,
        "config_json_sha256": cfg_sha_a
    }
    with open(hash_path, "w", encoding="utf-8") as f:
        json.dump(hashes_data, f, indent=2)

    # RUN B Determinism Check
    csv_b, prov_b, cfg_b, _ = generate_h10_fixture_content()
    csv_sha_b = compute_string_sha256(csv_b)
    prov_sha_b = compute_string_sha256(prov_b)
    cfg_sha_b = compute_string_sha256(cfg_b)

    determinism_pass = (csv_sha_a == csv_sha_b) and (prov_sha_a == prov_sha_b) and (cfg_sha_a == cfg_sha_b)

    print("==================================================")
    print("H1.0 FIXTURE GENERATION AND DETERMINISM AUDIT")
    print("==================================================")
    print(f"Fixture CSV Rows: {len(rows_data)}")
    print(f"RUN A fixture.csv SHA-256: {csv_sha_a}")
    print(f"RUN B fixture.csv SHA-256: {csv_sha_b}")
    print(f"Determinism Test (RUN A == RUN B): {'PASS' if determinism_pass else 'FAIL'}")
    print(f"Solar Source SHA-256: {solar_sha}")
    print(f"Wind Source SHA-256: {wind_sha}")
