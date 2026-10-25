import os
import json
import glob
import numpy as np
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"
BENCHMARK_PATH = os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv")
benchmark_df = pd.read_csv(BENCHMARK_PATH)
print("Benchmark shape:", benchmark_df.shape)
print("Columns:", benchmark_df.columns.tolist())
print("Unique origins:", benchmark_df['origin_id'].nunique())
origins = sorted(benchmark_df['origin_id'].unique())
even_origins = [o for o in origins if o % 2 == 0]
odd_origins = [o for o in origins if o % 2 != 0]
print(f"Total origins: {len(origins)}, EVEN: {len(even_origins)}, ODD: {len(odd_origins)}")

# Daytime count in benchmark ODD vs EVEN
daytime_bm = benchmark_df[benchmark_df['solar_elevation'] > 0]
print(f"Total daytime rows in benchmark: {len(daytime_bm)}")
print(f"EVEN daytime rows: {len(daytime_bm[daytime_bm['origin_id'].isin(even_origins)])}")
print(f"ODD daytime rows: {len(daytime_bm[daytime_bm['origin_id'].isin(odd_origins)])}")
mean_daytime_actual = daytime_bm['actual_SW_IN'].mean()
mean_odd_daytime_actual = daytime_bm[daytime_bm['origin_id'].isin(odd_origins)]['actual_SW_IN'].mean()
print(f"Mean daytime actual (all): {mean_daytime_actual:.4f} W/m2")
print(f"Mean daytime actual (ODD): {mean_odd_daytime_actual:.4f} W/m2")
