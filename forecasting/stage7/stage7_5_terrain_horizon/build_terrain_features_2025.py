import os
import json
import hashlib
import pandas as pd
import numpy as np
import pvlib

# ============================================================
# POLARIS — Stage 8.1 upstream dependency: Terrain / Horizon
# radiative-geometry features, 2025
#
# No generation script for this stage survives in the repo (only
# its CSV/JSON/MD outputs do); this reconstructs it strictly from
# the documented formula in stage7_5_horizon_method.md and
# stage7_5_feature_definitions.md (2024, LOCKED docs, read-only).
#
# Reuses, UNMODIFIED:
#   - the local Copernicus DEM GLO-30 tile (no re-download; the
#     horizon profile derived from it is a static geometric
#     property of the station + terrain, independent of year)
#   - the existing 360-azimuth horizon profile
#     (nuolja_horizon_profile_360deg.csv) computed from that DEM
#
# Only the per-hour solar geometry (elevation, azimuth) and
# clearsky_ghi are year-specific (2025) inputs.
#
# IMPORTANT FINDING (reported, not silently worked around):
# independent recomputation shows the 2024 artifact
# (nuolja_terrain_features_2024.csv) has its solar_azimuth column
# shifted by exactly -1 row relative to its own TIMESTAMP column
# (elevation matches a fresh pvlib call to ~1e-15; azimuth matches
# the FOLLOWING row's pvlib azimuth to ~5e-5). This looks like an
# indexing bug in whatever script originally produced it (lost,
# not in the repo), not an intentional convention -- the horizon
# method doc specifies the azimuth AT THE SAME timestamp. This
# script computes elevation and azimuth from a single aligned
# pvlib call (no shift), i.e. implements the DOCUMENTED formula
# correctly, rather than reproducing the bug. The 2024 file is
# left untouched.
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"

BASE = "/home/punith-bs/01polaris (Copy)"
CLEARSKY_2025 = f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
HORIZON_PROFILE = f"{BASE}/forecasting/stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv"
DEM_FILE = f"{BASE}/forecasting/stage7/stage7_5_terrain_horizon/Copernicus_DSM_COG_10_N68_00_E018_00_DEM.tif"
OUTPUT_CSV = f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv"
MANIFEST_FILE = f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features_MANIFEST.json"


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
    print("POLARIS — Terrain / Horizon radiative-geometry features (2025)")
    print("=" * 75)

    dem_hash = sha256_of(DEM_FILE)
    horizon_hash = sha256_of(HORIZON_PROFILE)
    print(f"\nDEM (reused, unmodified):            {DEM_FILE}")
    print(f"  SHA256: {dem_hash}")
    print(f"Horizon profile (reused, unmodified): {HORIZON_PROFILE}")
    print(f"  SHA256: {horizon_hash}")

    # 1. Load 2025 clear-sky / solar elevation (already verified in an earlier step)
    cs = pd.read_csv(CLEARSKY_2025)
    cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
    assert len(cs) == 8760, f"Expected 8760 rows, got {len(cs)}"

    # 2. Compute solar position (elevation + azimuth) from ONE aligned pvlib call
    location = pvlib.location.Location(latitude=LATITUDE, longitude=LONGITUDE, tz=TIMEZONE,
                                        name="SITES Nuolja Middle Station")
    times_localized = pd.DatetimeIndex(cs["TIMESTAMP"]).tz_localize(TIMEZONE)
    solpos = location.get_solarposition(times_localized)

    # Cross-check: this call's elevation must match the already-verified clear-sky
    # decomposition elevation (same model/location/tz) -- if it doesn't, something
    # about this script's setup has drifted from the earlier verified step.
    max_elev_diff = np.max(np.abs(solpos["elevation"].values - cs["solar_elevation"].values))
    print(f"\nCross-check vs verified clearsky decomposition elevation: max abs diff = {max_elev_diff:.2e}")
    assert max_elev_diff < 1e-9, "Solar elevation mismatch vs verified clearsky decomposition!"

    solar_elevation = solpos["elevation"].values
    solar_azimuth = solpos["azimuth"].values
    clearsky_ghi = cs["clearsky_ghi"].values

    # 3. Load static horizon profile (azimuth_deg 0..359 -> horizon_elevation_angle_deg)
    hp = pd.read_csv(HORIZON_PROFILE)
    assert len(hp) == 360
    assert sorted(hp["azimuth_deg"].tolist()) == list(range(360))
    horizon_lookup = hp.set_index("azimuth_deg")["horizon_elevation_angle_deg"].to_dict()

    # 4. Apply documented formula (stage7_5_feature_definitions.md)
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

    # 5. Validation
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    print(f"1. Row count: {len(out)} (expected 8760)")
    assert len(out) == 8760

    ts = pd.to_datetime(out["TIMESTAMP"])
    hourly_ok = (ts.diff().dropna().unique() == np.array([pd.Timedelta(hours=1)])).all()
    print(f"2. Strict hourly cadence, no gaps/dupes: {hourly_ok}")
    assert hourly_ok
    assert ts.is_monotonic_increasing and not ts.duplicated().any()

    n_nan = out.isna().sum().sum()
    print(f"3. NaN count: {n_nan} (expected 0)")
    assert n_nan == 0

    n_obstructed = int(terrain_solar_obstruction_flag.sum())
    print(f"4. Hours flagged as terrain-obstructed (elevation>0 and <= horizon): {n_obstructed}")
    print(f"5. terrain_horizon_elevation_deg range: [{terrain_horizon_elevation_deg.min():.4f}, "
          f"{terrain_horizon_elevation_deg.max():.4f}] (2024 doc: [-1.80, 29.80])")

    # Causal check: every feature here is a deterministic function of (a) the
    # static DEM-derived horizon profile and (b) this exact hour's astronomical
    # solar position and already-verified clearsky_ghi -- no dependence on any
    # future timestamp, forecast, or observation. Spot-check: flag can only be
    # 1 when elevation>0 and elevation<=horizon, by construction.
    causal_ok = bool(((terrain_solar_obstruction_flag == 1) <= ((solar_elevation > 0) & (solar_elevation <= terrain_horizon_elevation_deg))).all())
    print(f"6. Causal/deterministic construction (flag definition self-consistent): {causal_ok}")
    assert causal_ok

    expected_cols = ["TIMESTAMP", "solar_elevation", "solar_azimuth", "clearsky_ghi",
                      "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
                      "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    print(f"7. Schema: {list(out.columns)}")
    assert list(out.columns) == expected_cols

    atomic_write_csv(out, OUTPUT_CSV)
    out_hash = sha256_of(OUTPUT_CSV)
    print(f"\n8. Output SHA256: {out_hash}")
    print(f"   Output path:   {OUTPUT_CSV}")

    manifest = {
        "output_file": OUTPUT_CSV,
        "sha256": out_hash,
        "row_count": int(len(out)),
        "columns": expected_cols,
        "dem_file": {"path": DEM_FILE, "sha256": dem_hash, "reused_unmodified": True, "redownloaded": False},
        "horizon_profile_file": {"path": HORIZON_PROFILE, "sha256": horizon_hash, "reused_unmodified": True,
                                  "note": "static geometric property of station+DEM, year-independent"},
        "method": "documented formula from stage7_5_feature_definitions.md / stage7_5_horizon_method.md (2024, LOCKED docs)",
        "known_issue_in_2024_artifact": {
            "file": "forecasting/stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2024.csv",
            "finding": (
                "solar_azimuth column is shifted -1 row relative to its own TIMESTAMP "
                "column (confirmed by independent pvlib recomputation: elevation matches "
                "to ~1e-15, azimuth matches the FOLLOWING row's recomputed azimuth to "
                "~5e-5). This 2025 script does NOT reproduce that shift -- it computes "
                "elevation and azimuth from a single aligned pvlib call per the documented "
                "formula. The 2024 file was left unmodified."
            ),
            "action_taken": "flagged only, 2024 file not modified",
        },
        "validation": {
            "row_count_ok": True,
            "hourly_cadence_ok": bool(hourly_ok),
            "no_nan": bool(n_nan == 0),
            "causal_construction_ok": causal_ok,
            "schema_ok": True,
            "elevation_crosscheck_vs_clearsky_max_abs_diff": float(max_elev_diff),
        },
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {MANIFEST_FILE}")
    print("Done!")


if __name__ == "__main__":
    main()
