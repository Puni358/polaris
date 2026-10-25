import os
import json
import hashlib
import pandas as pd
import numpy as np
import pvlib

# ============================================================
# POLARIS — CORRECTED 2024 terrain features (for the corrected
# Stage 8.1 retraining only; does NOT touch the historical 2024
# artifact forecasting/stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv).
#
# Same documented formula as the 2025 build
# (forecasting/stage7/stage7_5_terrain_horizon/build_terrain_features_2025.py):
# fixes the azimuth off-by-one-row bug found and quantified in the
# historical 2024 artifact (99.8% of hours shifted, mean 2.69 deg,
# max 10.27 deg; 234 daytime hours with a flipped
# terrain_solar_obstruction_flag, mean ~167 W/m2 swing in
# clearsky_ghi_terrain_adjusted when flipped).
#
# Reuses, UNMODIFIED: the local DEM-derived static horizon profile
# (year-independent geometric property).
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"

BASE = "/home/punith-bs/01polaris (Copy)"
CLEARSKY_2024 = f"{BASE}/data/POLARIS_v0_1_clearsky_decomposition.csv"
HORIZON_PROFILE = f"{BASE}/forecasting/stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv"
OUTPUT_CSV = f"{BASE}/forecasting/stage7/stage8/stage8_1_corrected_2025/nuolja_terrain_features_2024_CORRECTED.csv"
MANIFEST_FILE = f"{BASE}/forecasting/stage7/stage8/stage8_1_corrected_2025/nuolja_terrain_features_2024_CORRECTED_MANIFEST.json"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_csv(df, path):
    tmp = path + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def main():
    print("=" * 75)
    print("CORRECTED 2024 terrain / horizon radiative-geometry features")
    print("=" * 75)

    horizon_hash = sha256_of(HORIZON_PROFILE)
    cs_hash = sha256_of(CLEARSKY_2024)
    print(f"Clear-sky 2024 input hash:  {cs_hash}")
    print(f"Horizon profile hash (reused, unmodified): {horizon_hash}")

    cs = pd.read_csv(CLEARSKY_2024)
    cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
    assert len(cs) == 8784, f"Expected 8784 rows (2024, leap year), got {len(cs)}"

    location = pvlib.location.Location(latitude=LATITUDE, longitude=LONGITUDE, tz=TIMEZONE,
                                        name="SITES Nuolja Middle Station")
    times_localized = pd.DatetimeIndex(cs["TIMESTAMP"]).tz_localize(TIMEZONE)
    solpos = location.get_solarposition(times_localized)

    max_elev_diff = np.max(np.abs(solpos["elevation"].values - cs["solar_elevation"].values))
    print(f"Cross-check vs verified 2024 clearsky decomposition elevation: max abs diff = {max_elev_diff:.2e}")
    assert max_elev_diff < 1e-9

    solar_elevation = solpos["elevation"].values
    solar_azimuth = solpos["azimuth"].values
    clearsky_ghi = cs["clearsky_ghi"].values

    hp = pd.read_csv(HORIZON_PROFILE)
    assert len(hp) == 360
    horizon_lookup = hp.set_index("azimuth_deg")["horizon_elevation_angle_deg"].to_dict()

    az_rounded = np.round(solar_azimuth).astype(int) % 360
    terrain_horizon_elevation_deg = np.array([horizon_lookup[a] for a in az_rounded])
    terrain_elevation_margin_deg = solar_elevation - terrain_horizon_elevation_deg
    terrain_solar_obstruction_flag = (
        (solar_elevation > 0) & (solar_elevation <= terrain_horizon_elevation_deg)
    ).astype(int)
    clearsky_ghi_terrain_adjusted = clearsky_ghi * (1 - terrain_solar_obstruction_flag)

    out = pd.DataFrame({
        "TIMESTAMP": cs["TIMESTAMP"].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "solar_elevation": solar_elevation,
        "solar_azimuth": solar_azimuth,
        "clearsky_ghi": clearsky_ghi,
        "terrain_horizon_elevation_deg": terrain_horizon_elevation_deg,
        "terrain_elevation_margin_deg": terrain_elevation_margin_deg,
        "terrain_solar_obstruction_flag": terrain_solar_obstruction_flag,
        "clearsky_ghi_terrain_adjusted": clearsky_ghi_terrain_adjusted,
    })

    assert len(out) == 8784
    assert out.isna().sum().sum() == 0

    atomic_write_csv(out, OUTPUT_CSV)
    out_hash = sha256_of(OUTPUT_CSV)
    print(f"Output SHA256: {out_hash}")
    print(f"Output path:   {OUTPUT_CSV}")

    # Compare against the historical (buggy) 2024 artifact, read-only
    hist_path = f"{BASE}/forecasting/stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv"
    hist_hash = sha256_of(hist_path)
    hist = pd.read_csv(hist_path)
    diff_horizon = hist["terrain_horizon_elevation_deg"].values - terrain_horizon_elevation_deg
    flag_mismatch = (hist["terrain_solar_obstruction_flag"].values != terrain_solar_obstruction_flag)

    manifest = {
        "output_file": OUTPUT_CSV,
        "sha256": out_hash,
        "row_count": int(len(out)),
        "columns": list(out.columns),
        "input_hashes": {"clearsky_decomposition_2024": cs_hash, "horizon_profile": horizon_hash},
        "historical_2024_artifact_untouched": {"path": hist_path, "sha256": hist_hash},
        "quantified_difference_vs_historical_2024_artifact": {
            "terrain_horizon_elevation_deg_mean_abs_diff_deg": float(np.mean(np.abs(diff_horizon))),
            "terrain_horizon_elevation_deg_max_abs_diff_deg": float(np.max(np.abs(diff_horizon))),
            "pct_hours_with_any_diff": float(np.mean(np.abs(diff_horizon) > 0.01) * 100),
            "obstruction_flag_mismatches": int(flag_mismatch.sum()),
            "obstruction_flag_mismatches_pct": float(flag_mismatch.mean() * 100),
        },
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to: {MANIFEST_FILE}")
    print("Done!")


if __name__ == "__main__":
    main()
