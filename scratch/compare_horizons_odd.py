import os
import pandas as pd
import numpy as np

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

# Load prediction files
hgb_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"))
arome_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv"))

# Merge on origin_id / origin_t0 and horizon
arome_df['origin_id'] = arome_df['origin_t0'].astype(str).str.extract(r'(\d+)').astype(int) if 'origin_id' not in arome_df.columns else arome_df['origin_id']
# Let's inspect unique origin timestamps in ODD
print("HGB ODD rows:", len(hgb_df), "Daytime rows:", len(hgb_df[hgb_df['daytime_flag'] == True]))
print("AROME ODD rows:", len(arome_df), "Daytime rows:", len(arome_df[arome_df['daytime_flag'] == True]))

# Calculate per-horizon MAE for HGB vs Real AROME on ODD
hgb_day = hgb_df[hgb_df['daytime_flag'] == True]
arome_day = arome_df[arome_df['daytime_flag'] == True]

hgb_horz = hgb_day.groupby('horizon').apply(lambda g: pd.Series({
    'hgb_mae': np.mean(np.abs(g['y_true'] - g['y_pred'])),
    'hgb_rmse': np.sqrt(np.mean((g['y_true'] - g['y_pred'])**2)),
    'hgb_bias': np.mean(g['y_pred'] - g['y_true']),
    'mean_y': np.mean(g['y_true']),
    'n_obs': len(g)
})).reset_index()

arome_horz = arome_day.groupby('horizon_h').apply(lambda g: pd.Series({
    'arome_mae': np.mean(np.abs(g['actual_sw_in'] - g['candidate_prediction'])),
    'arome_rmse': np.sqrt(np.mean((g['actual_sw_in'] - g['candidate_prediction'])**2)),
    'arome_bias': np.mean(g['candidate_prediction'] - g['actual_sw_in']),
})).reset_index()

comp = pd.merge(hgb_horz, arome_horz, left_on='horizon', right_on='horizon_h')
comp['delta_mae'] = comp['arome_mae'] - comp['hgb_mae']
comp['hgb_nmae'] = (comp['hgb_mae'] / comp['mean_y']) * 100
comp['arome_nmae'] = (comp['arome_mae'] / comp['mean_y']) * 100
comp['delta_nmae'] = comp['arome_nmae'] - comp['hgb_nmae']

print("\n=== H1-H24 HORIZON COMPARISON: STAGE 8.1 HGB vs STAGE 8.17A REAL AROME (ODD) ===")
print(comp[['horizon', 'n_obs', 'mean_y', 'hgb_mae', 'arome_mae', 'delta_mae', 'hgb_nmae', 'arome_nmae', 'delta_nmae']].to_string())
