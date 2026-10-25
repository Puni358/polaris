import os
import pandas as pd
import numpy as np

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

c_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"))
cm_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_multivariate_predictions.csv"))
t_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"))
m_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"))
p_df = pd.read_csv(os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"))

# Filter to daytime (actual_SW_IN > 0)
mask = c_df['actual_SW_IN'] > 0.0

actual = c_df.loc[mask, 'actual_SW_IN'].values
c_pred = c_df.loc[mask, 'chronos2'].values
cm_pred = cm_df.loc[mask, 'chronos2_multivariate'].values
t_pred = t_df.loc[mask, 'timesfm3'].values
m_pred = m_df.loc[mask, 'moirai2'].values
p_pred = p_df.loc[mask, 'kt_persistence_24h'].values

c_err = c_pred - actual
cm_err = cm_pred - actual
t_err = t_pred - actual
m_err = m_pred - actual
p_err = p_pred - actual

models = {
    'Chronos2_Raw': (c_pred, c_err),
    'Chronos2_Multivariate': (cm_pred, cm_err),
    'TimesFM3': (t_pred, t_err),
    'Moirai2': (m_pred, m_err),
    'Kt_Persistence': (p_pred, p_err)
}

keys = list(models.keys())
corr_matrix = np.zeros((len(keys), len(keys)))
err_corr_matrix = np.zeros((len(keys), len(keys)))
abs_err_corr_matrix = np.zeros((len(keys), len(keys)))

for i, k1 in enumerate(keys):
    for j, k2 in enumerate(keys):
        p1, e1 = models[k1]
        p2, e2 = models[k2]
        corr_matrix[i, j] = np.corrcoef(p1, p2)[0, 1]
        err_corr_matrix[i, j] = np.corrcoef(e1, e2)[0, 1]
        abs_err_corr_matrix[i, j] = np.corrcoef(np.abs(e1), np.abs(e2))[0, 1]

print("=== PREDICTION CORRELATION MATRIX ===")
print(pd.DataFrame(corr_matrix, index=keys, columns=keys).to_string())

print("\n=== SIGNED ERROR CORRELATION MATRIX ===")
print(pd.DataFrame(err_corr_matrix, index=keys, columns=keys).to_string())

print("\n=== ABSOLUTE ERROR CORRELATION MATRIX ===")
print(pd.DataFrame(abs_err_corr_matrix, index=keys, columns=keys).to_string())
