import os
import pandas as pd
import numpy as np
import torch
from chronos import Chronos2Pipeline

# ============================================================
# POLARIS — STAGE 3: Chronos-2 + Future NWP Forecast Experiments
# ============================================================

NWP_PATH = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2024.csv"
DECOMP_PATH = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv"
BASELINE_PRED_PATH = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_347window_chronos2_raw_baseline.csv"
STAGE3_DIR = "/home/punith-bs/01polaris (Copy)/forecasting/stage3"

os.makedirs(STAGE3_DIR, exist_ok=True)

# Locked 347-window control baseline metrics
BASELINE_MAE = 38.479261899615754
BASELINE_RMSE = 81.50280145233156
BASELINE_DAY_MAE = 55.339616054091544
BASELINE_DAY_RMSE = 97.93006424364027

def calculate_regime_metrics(pred_col, df):
    actual = df["actual_SW_IN"].values
    pred = df[pred_col].values

    def get_stats(mask):
        if np.sum(mask) == 0:
            return np.nan, np.nan, 0
        err = pred[mask] - actual[mask]
        mae = np.mean(np.abs(err))
        rmse = np.sqrt(np.mean(err ** 2))
        return mae, rmse, int(np.sum(mask))

    regimes = {
        "Overall": actual >= 0.0,
        "Daytime (actual > 0)": actual > 0.0,
        "Night / Near-Zero (actual == 0)": actual <= 0.0,
        "Low Solar (0 < actual <= 100)": (actual > 0.0) & (actual <= 100.0),
        "Moderate Solar (100 < actual <= 300)": (actual > 100.0) & (actual <= 300.0),
        "High Solar (actual > 300)": actual > 300.0,
    }

    rows = []
    for r_name, mask in regimes.items():
        m, r, n = get_stats(mask)
        rows.append({"Regime": r_name, "Hours": n, "MAE": m, "RMSE": r})
    return pd.DataFrame(rows)

def calculate_horizon_metrics(pred_col, df):
    rows = []
    for h in range(1, 25):
        h_df = df[df["horizon_hour"] == h]
        act_all = h_df["actual_SW_IN"].values
        pred_all = h_df[pred_col].values

        mae_all = np.mean(np.abs(pred_all - act_all))
        rmse_all = np.sqrt(np.mean((pred_all - act_all) ** 2))

        day_mask = act_all > 0
        if np.sum(day_mask) > 0:
            mae_day = np.mean(np.abs(pred_all[day_mask] - act_all[day_mask]))
            rmse_day = np.sqrt(np.mean((pred_all[day_mask] - act_all[day_mask]) ** 2))
        else:
            mae_day, rmse_day = np.nan, np.nan

        rows.append({
            "horizon_hour": h,
            "n_overall": len(h_df),
            "n_daytime": int(np.sum(day_mask)),
            "mae_overall": mae_all,
            "rmse_overall": rmse_all,
            "mae_daytime": mae_day,
            "rmse_daytime": rmse_day
        })
    return pd.DataFrame(rows)

def main():
    print("=" * 85)
    print("POLARIS — STAGE 3: Chronos-2 + Future NWP Forecast Experiments")
    print("=" * 85)

    nwp_df = pd.read_csv(NWP_PATH)
    decomp_df = pd.read_csv(DECOMP_PATH)

    nwp_df["timestamp_dt"] = pd.to_datetime(nwp_df["timestamp"])
    nwp_df["forecast_start_dt"] = pd.to_datetime(nwp_df["forecast_start"])
    decomp_df["timestamp_dt"] = pd.to_datetime(decomp_df["TIMESTAMP"])

    origins = sorted(nwp_df["forecast_start_dt"].unique())
    assert len(origins) == 347, f"Expected 347 origins, got {len(origins)}"

    # Reindex NWP variables for past lookup
    nwp_vars = ["fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"]
    full_idx = pd.date_range("2024-01-01 00:00:00", "2024-12-31 23:00:00", freq="1h")
    nwp_ts_lookup = nwp_df.groupby("timestamp_dt")[nwp_vars].mean().reindex(full_idx).bfill().ffill()

    decomp_df = decomp_df.set_index("timestamp_dt").sort_index()

    print("Loading Chronos-2 pipeline...")
    pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
    quantiles = np.asarray(pipeline.quantiles)
    median_idx = int(np.argmin(np.abs(quantiles - 0.5)))

    # Define Experiment Configs
    experiments = [
        ("3A", "stage3a_solar_geometry", ["solar_elevation", "solar_zenith", "clearsky_ghi"]),
        ("3B", "stage3b_cloud_nwp", ["solar_elevation", "solar_zenith", "clearsky_ghi", "fc_cloud_cover"]),
        ("3C", "stage3c_full_nwp", ["solar_elevation", "solar_zenith", "clearsky_ghi"] + nwp_vars),
    ]

    summary_rows = []

    for exp_id, exp_prefix, cov_keys in experiments:
        print(f"\nRunning Experiment {exp_id} ({exp_prefix}) with covariates: {cov_keys}...")
        
        results = []
        for i, orig in enumerate(origins):
            ctx_start = orig - pd.Timedelta(hours=24)
            ctx_end = orig - pd.Timedelta(hours=1)
            fut_start = orig
            fut_end = orig + pd.Timedelta(hours=23)

            ctx_decomp = decomp_df.loc[ctx_start:ctx_end]
            fut_decomp = decomp_df.loc[fut_start:fut_end]
            ctx_nwp = nwp_ts_lookup.loc[ctx_start:ctx_end]
            fut_nwp = nwp_df[nwp_df["forecast_start_dt"] == orig].set_index("timestamp_dt").loc[fut_start:fut_end]

            target = ctx_decomp["actual_SW_IN"].to_numpy(dtype=np.float32)

            past_covs = {}
            fut_covs = {}

            for k in cov_keys:
                if k in ctx_decomp.columns:
                    past_covs[k] = ctx_decomp[k].to_numpy(dtype=np.float32)
                    fut_covs[k] = fut_decomp[k].to_numpy(dtype=np.float32)
                else:
                    past_covs[k] = ctx_nwp[k].to_numpy(dtype=np.float32)
                    fut_covs[k] = fut_nwp[k].to_numpy(dtype=np.float32)

            input_item = {
                "target": target,
                "past_covariates": past_covs,
                "future_covariates": fut_covs,
            }

            preds = pipeline.predict([input_item], prediction_length=24, context_length=24)
            pred_median = preds[0][0, median_idx].numpy()

            for h in range(24):
                results.append({
                    "forecast_start": orig,
                    "horizon_hour": h + 1,
                    "timestamp": fut_decomp.index[h],
                    "actual_SW_IN": fut_decomp["actual_SW_IN"].iloc[h],
                    f"pred_{exp_prefix}": float(pred_median[h])
                })

        pred_df = pd.DataFrame(results)
        pred_col = f"pred_{exp_prefix}"

        # Validations
        assert len(pred_df) == 8328, f"Expected 8328 rows, got {len(pred_df)}"
        assert pred_df["forecast_start"].nunique() == 347, f"Expected 347 origins, got {pred_df['forecast_start'].nunique()}"
        assert pred_df[pred_col].isna().sum() == 0, "NaN predictions found!"
        assert not np.isinf(pred_df[pred_col]).any(), "Inf predictions found!"

        # Save predictions CSV
        pred_csv = os.path.join(STAGE3_DIR, f"{exp_prefix}_predictions.csv")
        pred_df.to_csv(pred_csv, index=False)
        print(f"Saved: {pred_csv}")

        # Metrics by regime
        reg_df = calculate_regime_metrics(pred_col, pred_df)
        reg_csv = os.path.join(STAGE3_DIR, f"{exp_prefix}_metrics.csv")
        reg_df.to_csv(reg_csv, index=False)
        print(f"Saved: {reg_csv}")

        # Metrics by horizon
        hor_df = calculate_horizon_metrics(pred_col, pred_df)
        hor_csv = os.path.join(STAGE3_DIR, f"{exp_prefix}_horizon.csv")
        hor_df.to_csv(hor_csv, index=False)
        print(f"Saved: {hor_csv}")

        # Overall summary row
        mae_overall = reg_df.loc[reg_df["Regime"] == "Overall", "MAE"].values[0]
        rmse_overall = reg_df.loc[reg_df["Regime"] == "Overall", "RMSE"].values[0]
        mae_day = reg_df.loc[reg_df["Regime"] == "Daytime (actual > 0)", "MAE"].values[0]
        rmse_day = reg_df.loc[reg_df["Regime"] == "Daytime (actual > 0)", "RMSE"].values[0]

        mae_imp = BASELINE_MAE - mae_overall
        mae_imp_pct = 100.0 * mae_imp / BASELINE_MAE
        rmse_imp = BASELINE_RMSE - rmse_overall
        rmse_imp_pct = 100.0 * rmse_imp / BASELINE_RMSE
        day_mae_imp = BASELINE_DAY_MAE - mae_day
        day_mae_imp_pct = 100.0 * day_mae_imp / BASELINE_DAY_MAE
        day_rmse_imp = BASELINE_DAY_RMSE - rmse_day
        day_rmse_imp_pct = 100.0 * day_rmse_imp / BASELINE_DAY_RMSE

        summary_rows.append({
            "Model": f"Chronos-2 + Exp {exp_id}",
            "Features": ", ".join(cov_keys),
            "MAE": mae_overall,
            "RMSE": rmse_overall,
            "Daytime_MAE": mae_day,
            "Daytime_RMSE": rmse_day,
            "MAE_improvement": mae_imp,
            "MAE_improvement_pct": mae_imp_pct,
            "RMSE_improvement": rmse_imp,
            "RMSE_improvement_pct": rmse_imp_pct,
            "Daytime_MAE_improvement": day_mae_imp,
            "Daytime_MAE_improvement_pct": day_mae_imp_pct,
            "Daytime_RMSE_improvement": day_rmse_imp,
            "Daytime_RMSE_improvement_pct": day_rmse_imp_pct
        })

    comp_df = pd.DataFrame(summary_rows)
    comp_csv = os.path.join(STAGE3_DIR, "stage3_model_comparison.csv")
    comp_df.to_csv(comp_csv, index=False)
    print(f"\nSaved final comparison table: {comp_csv}")

    print("\n" + "=" * 90)
    print("STAGE 3 SUMMARY MODEL COMPARISON (VS 347-WINDOW CONTROL BASELINE)")
    print("=" * 90)
    print(f"Control Baseline (Raw SW_IN): MAE = {BASELINE_MAE:.3f}, RMSE = {BASELINE_RMSE:.3f}, Day MAE = {BASELINE_DAY_MAE:.3f}, Day RMSE = {BASELINE_DAY_RMSE:.3f}")
    print("-" * 90)
    for _, r in comp_df.iterrows():
        print(f"{r['Model']:<22} | MAE: {r['MAE']:<6.3f} ({r['MAE_improvement_pct']:+6.2f}%) | Day MAE: {r['Daytime_MAE']:<6.3f} ({r['Daytime_MAE_improvement_pct']:+6.2f}%) | Day RMSE: {r['Daytime_RMSE']:<6.3f} ({r['Daytime_RMSE_improvement_pct']:+6.2f}%)")

if __name__ == "__main__":
    main()
