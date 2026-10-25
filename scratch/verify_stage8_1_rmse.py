import pandas as pd
import numpy as np

df = pd.read_csv("/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv")

# Daytime mask (is_daytime == True)
df_day = df[df["is_daytime"]].copy()

# Daytime metrics for Stage 8.1 candidate
actual_day = df_day["actual_SW_IN"].values
pred_day = df_day["pred_stage8_1_candidate"].values

mae_day = np.mean(np.abs(actual_day - pred_day))
mean_actual_day = np.mean(actual_day)
nmae_day = (mae_day / mean_actual_day) * 100.0
rmse_day = np.sqrt(np.mean((actual_day - pred_day)**2))
bias_day = np.mean(pred_day - actual_day)

# All-hours metrics for Stage 8.1 candidate (4,152 rows)
actual_all = df["actual_SW_IN"].values
pred_all = df["pred_stage8_1_candidate"].values

mae_all = np.mean(np.abs(actual_all - pred_all))
mean_actual_all = np.mean(actual_all)
nmae_all = (mae_all / mean_actual_all) * 100.0
rmse_all = np.sqrt(np.mean((actual_all - pred_all)**2))
bias_all = np.mean(pred_all - actual_all)

# Control (Stage 7.5) metrics
pred_ctrl_day = df_day["pred_stage7_5_control"].values
mae_ctrl_day = np.mean(np.abs(actual_day - pred_ctrl_day))
nmae_ctrl_day = (mae_ctrl_day / mean_actual_day) * 100.0
rmse_ctrl_day = np.sqrt(np.mean((actual_day - pred_ctrl_day)**2))

pred_ctrl_all = df["pred_stage7_5_control"].values
rmse_ctrl_all = np.sqrt(np.mean((actual_all - pred_ctrl_all)**2))

results = {
    "daytime_rows": len(df_day),
    "all_rows": len(df),
    "mean_actual_daytime": float(mean_actual_day),
    "mean_actual_all": float(mean_actual_all),
    "stage8_1_daytime_mae": float(mae_day),
    "stage8_1_daytime_nmae": float(nmae_day),
    "stage8_1_daytime_rmse": float(rmse_day),
    "stage8_1_daytime_bias": float(bias_day),
    "stage8_1_all_hours_rmse": float(rmse_all),
    "stage8_1_all_hours_mae": float(mae_all),
    "stage7_5_daytime_mae": float(mae_ctrl_day),
    "stage7_5_daytime_nmae": float(nmae_ctrl_day),
    "stage7_5_daytime_rmse": float(rmse_ctrl_day),
    "stage7_5_all_hours_rmse": float(rmse_ctrl_all),
}

print(json_str := pd.Series(results).to_json(indent=2))

with open("/home/punith-bs/01polaris (Copy)/scratch/stage8_1_rmse_verification.json", "w") as f:
    f.write(json_str)
