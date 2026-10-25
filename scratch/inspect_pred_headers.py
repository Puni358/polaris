import os
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

pred_files = [
    os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"),
    os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_multivariate_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/stage4/stage4_results/ensemble_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/stage3/stage3c_full_nwp_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv"),
    os.path.join(WORKSPACE, "forecasting/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv"),
    os.path.join(WORKSPACE, "forecasting/stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv"),
]

for p in pred_files:
    if os.path.exists(p):
        df = pd.read_csv(p)
        print("==================================================")
        print("FILE:", os.path.basename(p))
        print("SHAPE:", df.shape)
        print("COLUMNS:", df.columns.tolist()[:10])
        print(df.head(2))
    else:
        print("NOT FOUND:", p)
