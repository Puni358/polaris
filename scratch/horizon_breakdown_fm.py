import os
import pandas as pd
import numpy as np

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

hgb_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"))
chronos_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"))
timesfm_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"))
moirai_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"))

# Build H1-H24 summary for Chronos2, TimesFM3, Moirai2, Kt_Persistence vs HGB
# We need to filter daytime where actual_SW_IN > 0
for df in [chronos_df, timesfm_df, moirai_df]:
    df['daytime_flag'] = df['actual_SW_IN'] > 0.0

def get_horizon_stats(df, pred_col, name):
    day = df[df['daytime_flag'] == True]
    res = day.groupby('horizon_hour').apply(lambda g: pd.Series({
        f'{name}_mae': np.mean(np.abs(g['actual_SW_IN'] - g[pred_col])),
        f'{name}_rmse': np.sqrt(np.mean((g['actual_SW_IN'] - g[pred_col])**2)),
        f'{name}_bias': np.mean(g[pred_col] - g['actual_SW_IN'])
    })).reset_index()
    return res

c_stats = get_horizon_stats(chronos_df, 'chronos2', 'chronos2')
t_stats = get_horizon_stats(timesfm_df, 'timesfm3', 'timesfm3')
m_stats = get_horizon_stats(moirai_df, 'moirai2', 'moirai2')

merged = pd.merge(c_stats, t_stats, on='horizon_hour')
merged = pd.merge(merged, m_stats, on='horizon_hour')

print("=== HORIZON ERROR BREAKDOWN: CHRONOS-2 vs TIMESFM-3 vs MOIRAI-2 (347 origins) ===")
print(merged.to_string())
