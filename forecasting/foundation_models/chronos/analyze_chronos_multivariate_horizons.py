import pandas as pd
import numpy as np

path = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv"
uni_path = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

df = pd.read_csv(path)
uni = pd.read_csv(uni_path)

rows = []

for h in range(1, 25):
    d = df[df["horizon_hour"] == h]
    u = uni[uni["horizon_hour"] == h]

    actual = d["actual_SW_IN"].to_numpy()
    multi = d["chronos2_multivariate"].to_numpy()
    naive = d["seasonal_naive_24h"].to_numpy()
    uni_pred = u["chronos2"].to_numpy()

    def score(y, p):
        e = p - y
        return np.mean(np.abs(e)), np.sqrt(np.mean(e**2))

    m_mae, m_rmse = score(actual, multi)
    n_mae, n_rmse = score(actual, naive)
    u_mae, u_rmse = score(actual, uni_pred)

    rows.append({
        "horizon_hour": h,
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

out = "/home/punith-bs/01polaris/chronos/POLARIS_v0_1_chronos2_multivariate_horizon_analysis.csv"
result.to_csv(out, index=False)

print("=" * 90)
print("CHRONOS-2 MULTIVARIATE — HORIZON ANALYSIS")
print("=" * 90)

print(result.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)

mae_wins = (result["multivariate_MAE"] < result["univariate_MAE"]).sum()
rmse_wins = (result["multivariate_RMSE"] < result["univariate_RMSE"]).sum()

print(f"Multivariate beats Univariate — MAE:  {mae_wins}/24 horizons")
print(f"Multivariate beats Univariate — RMSE: {rmse_wins}/24 horizons")

best_mae = result.loc[result["multi_vs_univariate_MAE_pct"].idxmax()]
best_rmse = result.loc[result["multi_vs_univariate_RMSE_pct"].idxmax()]

print(
    f"\nBest MAE improvement: H{int(best_mae.horizon_hour)} "
    f"({best_mae.multi_vs_univariate_MAE_pct:+.2f}%)"
)

print(
    f"Best RMSE improvement: H{int(best_rmse.horizon_hour)} "
    f"({best_rmse.multi_vs_univariate_RMSE_pct:+.2f}%)"
)

print(f"\nSaved: {out}")
