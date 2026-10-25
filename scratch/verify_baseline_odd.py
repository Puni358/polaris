import os
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

odd_pred_path = os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv")
odd_df = pd.read_csv(odd_pred_path)
print("ODD predictions shape:", odd_df.shape)
print("ODD columns:", odd_df.columns.tolist())
print("Unique origins in ODD predictions:", odd_df['origin_id'].nunique())
print("Horizon range in ODD:", odd_df['horizon'].min(), "to", odd_df['horizon'].max())
daytime_odd = odd_df[odd_df['daytime_flag'] == True]
print("Daytime ODD rows:", len(daytime_odd))
print("Night ODD rows:", len(odd_df[odd_df['daytime_flag'] == False]))
mae_day = (daytime_odd['y_true'] - daytime_odd['y_pred']).abs().mean()
mean_y_true = daytime_odd['y_true'].mean()
nmae_day = (mae_day / mean_y_true) * 100
rmse_day = (((daytime_odd['y_true'] - daytime_odd['y_pred'])**2).mean())**0.5
bias_day = (daytime_odd['y_pred'] - daytime_odd['y_true']).mean()
print(f"Recomputed ODD Daytime MAE: {mae_day:.6f} W/m2")
print(f"Recomputed ODD Daytime Mean Y True: {mean_y_true:.6f} W/m2")
print(f"Recomputed ODD Daytime nMAE: {nmae_day:.6f}%")
print(f"Recomputed ODD Daytime RMSE: {rmse_day:.6f} W/m2")
print(f"Recomputed ODD Daytime Bias: {bias_day:.6f} W/m2")
