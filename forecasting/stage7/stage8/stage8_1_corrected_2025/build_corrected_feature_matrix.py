#!/usr/bin/env python3
"""
POLARIS — CORRECTED Stage 8.1 feature matrix builder (2024 + 2025).

Exact replica of the data-loading / merge / derived-column / context-
feature logic in
forecasting/stage7/stage8/stage8_1_700hpa_wind/save_stage8_1_model_artifact.py
(2024, LOCKED) -- same files, same merges, same 28-base / 31-stage66 /
35-stage75 / 37-candidate feature contracts, same context-feature
formulas -- EXCEPT the terrain (4 features) and u700/v700 (2 features)
inputs are swapped for the corrected versions built in this
investigation:
  - forecasting/stage7/stage8/stage8_1_corrected_2025/nuolja_terrain_features_2024_CORRECTED.csv
  - forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_wind700_features_2024_CORRECTED.csv
  - forecasting/stage7/stage7_5_terrain_horizon/nuolja_terrain_features_2025.csv (already correct)
  - forecasting/stage7/stage8/stage8_1_700hpa_wind_2025/stage8_1_wind700_features_2025.csv (already correct)

The other 31 features are read from the SAME historical 2024 files
this script has always used (SITES, clearsky, NWP, Stage4, LWP/IWP)
for the 2024 side, and from the equivalent verified 2025 artifacts
for the 2025 side. Nothing historical is modified; this script only
reads those files and writes new ones under stage8_1_corrected_2025/.

Produces, for each year: a full 37-feature matrix CSV (plus origin_id,
forecast_start, horizon_hour, timestamp, actual_SW_IN, split,
is_daytime, is_night_causal -- same metadata columns as
stage8_1_full_37_feature_matrix_2024.csv) with an EVEN/ODD split
column, atomically written, hashed.
"""

import os
import json
import hashlib
import pandas as pd
import numpy as np

BASE = "/home/punith-bs/01polaris (Copy)"
OUT_DIR = f"{BASE}/forecasting/stage7/stage8/stage8_1_corrected_2025"


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


CONFIGS = {
    2024: dict(
        sites_path=f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv",
        sites_sw_in_col="SW_IN",
        clearsky_path=f"{BASE}/data/POLARIS_v0_1_clearsky_decomposition.csv",
        nwp_path=f"{BASE}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv",
        stage4_preds_path=f"{BASE}/forecasting/stage4/stage4_results/ensemble_predictions.csv",
        stage4_params_path=f"{BASE}/forecasting/stage4/stage4_results/ensemble_parameters.json",
        stage66_feat_path=f"{BASE}/forecasting/stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv",
        terrain_feat_path=f"{OUT_DIR}/nuolja_terrain_features_2024_CORRECTED.csv",
        wind_feat_path=f"{OUT_DIR}/stage8_1_wind700_features_2024_CORRECTED.csv",
        output_csv=f"{OUT_DIR}/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv",
    ),
    2025: dict(
        sites_path=f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv",
        sites_sw_in_col="SW_IN",
        clearsky_path=f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv",
        nwp_path=f"{BASE}/data/POLARIS_v0_1_future_weather_forecasts_2025.csv",
        stage4_preds_path=f"{BASE}/forecasting/stage4/stage4_results_2025/ensemble_predictions.csv",
        stage4_params_path=f"{BASE}/forecasting/stage4/stage4_results_2025/ensemble_parameters.json",
        stage66_feat_path=f"{BASE}/forecasting/stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv",
        terrain_feat_path=f"{BASE}/data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv",
        wind_feat_path=f"{BASE}/forecasting/stage7/stage8/stage8_1_700hpa_wind_2025/stage8_1_wind700_features_2025.csv",
        output_csv=f"{OUT_DIR}/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv",
    ),
}


def build(year):
    cfg = CONFIGS[year]
    print("=" * 80)
    print(f"Building CORRECTED Stage 8.1 feature matrix — {year}")
    print("=" * 80)

    input_hashes = {k: sha256_of(v) for k, v in cfg.items() if k.endswith("_path")}
    for k, v in input_hashes.items():
        print(f"  {k}: {v}")

    s4_preds = pd.read_csv(cfg["stage4_preds_path"])
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"], utc=True)
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"], utc=True)

    df_nwp = pd.read_csv(cfg["nwp_path"])
    df_nwp["timestamp"] = pd.to_datetime(df_nwp["timestamp"], utc=True)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)

    df_sites = pd.read_csv(cfg["sites_path"])
    df_sites["timestamp"] = pd.to_datetime(df_sites["TIMESTAMP"], utc=True)

    df_cs = pd.read_csv(cfg["clearsky_path"])
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)

    df_66 = pd.read_csv(cfg["stage66_feat_path"])
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)

    df_75 = pd.read_csv(cfg["terrain_feat_path"])
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)

    df_wind = pd.read_csv(cfg["wind_feat_path"])
    df_wind["forecast_start"] = pd.to_datetime(df_wind["forecast_start"], utc=True)
    df_wind["valid_time"] = pd.to_datetime(df_wind["valid_time"], utc=True)

    df = s4_preds.copy()
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0

    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]
    df = df.merge(df_cs[cs_cols], on="timestamp", how="left")

    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]

    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
                    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    df = df.merge(df_75[terrain_cols], on="timestamp", how="left")

    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df = df.merge(df_wind[wind_cols], on=["forecast_start", "horizon_hour"], how="left")

    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["is_daytime"] = df["actual_SW_IN"] > 0
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)

    with open(cfg["stage4_params_path"]) as f:
        ensemble_params_full = json.load(f)

    phys_preds_full = []
    for idx, row in df.iterrows():
        h = str(int(row["horizon_hour"]))
        p = ensemble_params_full[h]
        k_h = p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        phys_preds_full.append(phys)

    df["phys_pred_fold"] = phys_preds_full
    df["pred_stage4_fold"] = df["pred_ensemble"]
    df["disagreement_fold"] = (df["pred_stage3b_cloud_nwp"] - df["phys_pred_fold"]).abs()

    base_28_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]

    sw_in_col = cfg["sites_sw_in_col"]
    all_origins = sorted(df["forecast_start"].unique())
    ctx_feature_rows = []
    for origin_ts in all_origins:
        context_start = origin_ts - pd.Timedelta(hours=24)
        ctx_sites = df_sites[(df_sites["timestamp"] >= context_start) & (df_sites["timestamp"] < origin_ts)].sort_values("timestamp")

        if len(ctx_sites) < 24:
            ctx_feature_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue

        sw_vals = ctx_sites[sw_in_col].values
        s3, s6, s12, s24 = sw_vals[-3:], sw_vals[-6:], sw_vals[-12:], sw_vals[-24:]

        std_3h = np.std(s3) if len(s3) > 1 else 0.0
        std_6h = np.std(s6) if len(s6) > 1 else 0.0
        std_12h = np.std(s12) if len(s12) > 1 else 0.0
        std_24h = np.std(s24) if len(s24) > 1 else 0.0

        abs_chg_1h = abs(sw_vals[-1] - sw_vals[-2]) if len(sw_vals) >= 2 else 0.0
        abs_chg_3h = abs(sw_vals[-1] - sw_vals[-4]) if len(sw_vals) >= 4 else 0.0
        abs_chg_6h = abs(sw_vals[-1] - sw_vals[-7]) if len(sw_vals) >= 7 else 0.0

        diffs_6h = np.abs(np.diff(s6)) if len(s6) > 1 else [0.0]
        max_diff_6h = np.max(diffs_6h)
        mean_diff_6h = np.mean(diffs_6h)
        slope_6h = np.polyfit(np.arange(len(s6)), s6, 1)[0] if len(s6) >= 3 else 0.0

        ctx_cs = df_cs[(df_cs["timestamp"] >= context_start) & (df_cs["timestamp"] < origin_ts)].sort_values("timestamp")
        if len(ctx_cs) == len(ctx_sites):
            cs_ghi_vals = ctx_cs["clearsky_ghi"].values
            valid_cs = cs_ghi_vals > 10.0
            kt_vals = np.zeros_like(sw_vals)
            kt_vals[valid_cs] = np.clip(sw_vals[valid_cs] / cs_ghi_vals[valid_cs], 0.0, 1.5)
            kt_std_6h = np.std(kt_vals[-6:]) if len(kt_vals) >= 6 else 0.0
        else:
            kt_std_6h = 0.0

        ctx_feature_rows.append({
            "forecast_start": origin_ts,
            "ctx_std_3h": std_3h, "ctx_std_6h": std_6h, "ctx_std_12h": std_12h, "ctx_std_24h": std_24h,
            "ctx_abs_change_1h": abs_chg_1h, "ctx_abs_change_3h": abs_chg_3h, "ctx_abs_change_6h": abs_chg_6h,
            "ctx_max_diff_6h": max_diff_6h, "ctx_mean_diff_6h": mean_diff_6h, "ctx_slope_6h": slope_6h,
            "ctx_kt_std_6h": kt_std_6h, "ctx_last_obs": sw_vals[-1],
            "ctx_mean_24h": np.mean(s24), "ctx_max_24h": np.max(s24)
        })

    ctx_df = pd.DataFrame(ctx_feature_rows)
    df = df.merge(ctx_df, on="forecast_start", how="left")

    stage66_31_features = base_28_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    stage75_35_features = stage66_31_features + ["terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
                                                   "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    candidate_37_features = stage75_35_features + ["u700", "v700"]

    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    odd_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 1]
    df["split"] = np.where(df["forecast_start"].isin(even_origins), "EVEN", "ODD")

    out_cols = ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "split",
                "is_daytime", "is_night_causal"] + candidate_37_features
    # horizon_hour appears once in candidate_37_features and once as metadata in the
    # original 37-feature-matrix CSV's header (kept for parity: it's a duplicate col
    # name in the original stage8_1_full_37_feature_matrix_2024.csv too).
    out_df = df[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "split",
                 "is_daytime", "is_night_causal"]].copy()
    out_df["origin_id"] = out_df["forecast_start"].astype(str)
    for c in candidate_37_features:
        out_df[c] = df[c]

    print(f"\nRows: {len(out_df)}  Origins: {out_df['forecast_start'].nunique()}  "
          f"EVEN: {len(even_origins)}  ODD: {len(odd_origins)}")
    print(f"NaN counts in candidate_37_features:\n{out_df[candidate_37_features].isna().sum()[out_df[candidate_37_features].isna().sum() > 0]}")

    atomic_write_csv(out_df, cfg["output_csv"])
    out_hash = sha256_of(cfg["output_csv"])
    print(f"\nOutput SHA256: {out_hash}")
    print(f"Output path:   {cfg['output_csv']}")

    manifest = {
        "output_file": cfg["output_csv"],
        "sha256": out_hash,
        "row_count": int(len(out_df)),
        "unique_origins": int(out_df["forecast_start"].nunique()),
        "even_origins": len(even_origins),
        "odd_origins": len(odd_origins),
        "candidate_37_features": candidate_37_features,
        "stage75_35_features": stage75_35_features,
        "input_hashes": input_hashes,
        "corrected_feature_families": ["terrain (4)", "u700/v700 (2)"],
        "unchanged_feature_count": 31,
    }
    with open(cfg["output_csv"].replace(".csv", "_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    return out_df, candidate_37_features, stage75_35_features, even_origins, odd_origins


if __name__ == "__main__":
    import sys
    years = [int(y) for y in sys.argv[1:]] if len(sys.argv) > 1 else [2024, 2025]
    for y in years:
        build(y)
        print()
