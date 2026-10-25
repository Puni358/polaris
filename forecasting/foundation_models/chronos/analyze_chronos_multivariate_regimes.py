import pandas as pd
import numpy as np

path = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv"
uni_path = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

df = pd.read_csv(path)
uni = pd.read_csv(uni_path)

def regime(x):
    if x <= 0:
        return "Night / near-zero"
    elif x <= 100:
        return "Low solar"
    elif x <= 400:
        return "Moderate solar"
    else:
        return "High solar"

df["regime"] = df["actual_SW_IN"].apply(regime)
uni["regime"] = uni["actual_SW_IN"].apply(regime)

rows = []

for r in ["Night / near-zero", "Low solar", "Moderate solar", "High solar"]:
    d = df[df["regime"] == r]
    u = uni[uni["regime"] == r]

    y = d["actual_SW_IN"].to_numpy()
    multi = d["chronos2_multivariate"].to_numpy()
    naive = d["seasonal_naive_24h"].to_numpy()
    uni_pred = u["chronos2"].to_numpy()

    def score(actual, pred):
        e = pred - actual
        return np.mean(np.abs(e)), np.sqrt(np.mean(e**2))

    m_mae, m_rmse = score(y, multi)
    n_mae, n_rmse = score(y, naive)
    u_mae, u_rmse = score(y, uni_pred)

    rows.append({
        "regime": r,
        "observations": len(d),
        "percentage": len(d) / len(df) * 100,
        "multivariate_MAE": m_mae,
        "multivariate_RMSE": m_rmse,
        "univariate_MAE": u_mae,
        "univariate_RMSE": u_rmse,
        "seasonal_naive_MAE": n_mae,
        "seasonal_naive_RMSE": n_rmse,
        "multi_vs_univariate_MAE_pct": (1 - m_mae/u_mae) * 100,
        "multi_vs_univariate_RMSE_pct": (1 - m_rmse/u_rmse) * 100,
        "multi_vs_naive_MAE_pct": (1 - m_mae/n_mae) * 100,
        "multi_vs_naive_RMSE_pct": (1 - m_rmse/n_rmse) * 100,
    })

result = pd.DataFrame(rows)

out = "/home/punith-bs/01polaris/chronos/POLARIS_v0_1_chronos2_multivariate_solar_regime_analysis.csv"
result.to_csv(out, index=False)

print("=" * 110)
print("CHRONOS-2 MULTIVARIATE — SOLAR REGIME ANALYSIS")
print("=" * 110)

print(result.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

print("\n" + "=" * 110)
print("SUMMARY")
print("=" * 110)

wins_mae = (result["multivariate_MAE"] < result["univariate_MAE"]).sum()
wins_rmse = (result["multivariate_RMSE"] < result["univariate_RMSE"]).sum()

print(f"Multivariate beats Univariate — MAE:  {wins_mae}/4 regimes")
print(f"Multivariate beats Univariate — RMSE: {wins_rmse}/4 regimes")

print(f"\nSaved: {out}")
