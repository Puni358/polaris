import os
import json
import urllib.request
import numpy as np
import pandas as pd

BASE_DIR = "/home/punith-bs/01polaris (Copy)"
OUT_DIR = os.path.join(BASE_DIR, "forecasting/stage5", "stage5_4_spatial_nwp")
os.makedirs(OUT_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(OUT_DIR, "spatial_nwp_features_2024.csv")

NUOLJA_LAT = 68.362074
NUOLJA_LON = 18.738752
TIMEZONE = "Etc/GMT-1"

# Probes around Nuolja (~2.5 km spatial offset at native grid scale)
PROBES = {
    "center": (NUOLJA_LAT, NUOLJA_LON),
    "north": (round(NUOLJA_LAT + 0.0225, 6), NUOLJA_LON),
    "south": (round(NUOLJA_LAT - 0.0225, 6), NUOLJA_LON),
    "east": (NUOLJA_LAT, round(NUOLJA_LON + 0.06, 6)),
    "west": (NUOLJA_LAT, round(NUOLJA_LON - 0.06, 6)),
}

MONTHS = [
    ("2024-01-01", "2024-01-31"),
    ("2024-02-01", "2024-02-29"),
    ("2024-03-01", "2024-03-31"),
    ("2024-04-01", "2024-04-30"),
    ("2024-05-01", "2024-05-31"),
    ("2024-06-01", "2024-06-30"),
    ("2024-07-01", "2024-07-31"),
    ("2024-08-01", "2024-08-31"),
    ("2024-09-01", "2024-09-30"),
    ("2024-10-01", "2024-10-31"),
    ("2024-11-01", "2024-11-30"),
    ("2024-12-01", "2024-12-31"),
]

def fetch_probe_month(lat, lon, start_d, end_d):
    url = (
        f"https://previous-runs-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_d}&end_date={end_d}"
        f"&hourly=cloud_cover_previous_day1,wind_speed_10m_previous_day1,wind_direction_10m_previous_day1"
        f"&models=metno_seamless"
        f"&cell_selection=nearest"
        f"&timezone={TIMEZONE}"
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get("hourly", {})

def main():
    print("=" * 80)
    print("POLARIS Stage 5.4 — Extracting 2024 Spatial NWP Features")
    print("=" * 80)

    all_probe_data = {p_name: [] for p_name in PROBES}

    for start_d, end_d in MONTHS:
        print(f"Fetching {start_d} to {end_d}...")
        for p_name, (lat, lon) in PROBES.items():
            h_data = fetch_probe_month(lat, lon, start_d, end_d)
            times = h_data.get("time", [])
            clouds = h_data.get("cloud_cover_previous_day1", [])
            ws = h_data.get("wind_speed_10m_previous_day1", [])
            wd = h_data.get("wind_direction_10m_previous_day1", [])

            df_p = pd.DataFrame({
                "timestamp": pd.to_datetime(times),
                f"cloud_{p_name}": clouds,
                f"ws_{p_name}": ws,
                f"wd_{p_name}": wd
            })
            all_probe_data[p_name].append(df_p)

    # Merge probe data
    merged_df = None
    for p_name in PROBES:
        df_concat = pd.concat(all_probe_data[p_name], ignore_index=True)
        if merged_df is None:
            merged_df = df_concat
        else:
            merged_df = merged_df.merge(df_concat, on="timestamp", how="left")

    print(f"\nMerged probe data shape: {merged_df.shape}")

    # Feature Engineering
    # 1. Convert cloud cover to fractions
    for p_name in PROBES:
        merged_df[f"cloud_frac_{p_name}"] = merged_df[f"cloud_{p_name}"] / 100.0

    # 2. Wind Vector Components at Center Probe (Nuolja)
    # Meteorological convention: direction wind is blowing FROM
    # U = -ws * sin(rad), V = -ws * cos(rad)
    rad_center = np.radians(merged_df["wd_center"])
    ws_center = merged_df["ws_center"]

    merged_df["U_10m"] = -ws_center * np.sin(rad_center)
    merged_df["V_10m"] = -ws_center * np.cos(rad_center)

    # 3. Spatial Cloud Gradients
    merged_df["DeltaC_EW"] = merged_df["cloud_frac_east"] - merged_df["cloud_frac_west"]
    merged_df["DeltaC_NS"] = merged_df["cloud_frac_north"] - merged_df["cloud_frac_south"]

    # 4. Wind-Aligned Cloud Advection Proxies
    merged_df["u_advection"] = merged_df["U_10m"] * merged_df["DeltaC_EW"]
    merged_df["v_advection"] = merged_df["V_10m"] * merged_df["DeltaC_NS"]
    merged_df["advection_proxy"] = merged_df["u_advection"] + merged_df["v_advection"]

    # 5. Upwind Cloud Fraction
    # If U > 0 (wind blowing to East, coming from West), upwind is West.
    # If U < 0 (wind blowing to West, coming from East), upwind is East.
    # If V > 0 (wind blowing to North, coming from South), upwind is South.
    # If V < 0 (wind blowing to South, coming from North), upwind is North.
    cloud_upwind = []
    cloud_downwind = []

    for idx, row in merged_df.iterrows():
        u = row["U_10m"]
        v = row["V_10m"]
        c_n, c_s, c_e, c_w = row["cloud_frac_north"], row["cloud_frac_south"], row["cloud_frac_east"], row["cloud_frac_west"]

        if pd.isna(u) or pd.isna(v):
            cloud_upwind.append(np.nan)
            cloud_downwind.append(np.nan)
            continue

        # Quadrant selector
        if abs(u) >= abs(v):
            if u > 0: # Wind coming from West
                up, down = c_w, c_e
            else: # Wind coming from East
                up, down = c_e, c_w
        else:
            if v > 0: # Wind coming from South
                up, down = c_s, c_n
            else: # Wind coming from North
                up, down = c_n, c_s

        cloud_upwind.append(up)
        cloud_downwind.append(down)

    merged_df["cloud_frac_upwind"] = cloud_upwind
    merged_df["cloud_frac_downwind"] = cloud_downwind
    merged_df["upwind_downwind_contrast"] = merged_df["cloud_frac_upwind"] - merged_df["cloud_frac_downwind"]

    # Save to CSV
    merged_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved spatial features dataset to: {OUTPUT_CSV}")
    print("Columns:", list(merged_df.columns))

if __name__ == "__main__":
    main()
