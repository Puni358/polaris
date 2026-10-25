#!/usr/bin/env python3
import pandas as pd
from datetime import timedelta
import time

print("1. Loading midnight snapshot matrix and clear-sky boundaries...")
daily_df = pd.read_parquet("forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet")
daily_df['forecast_start'] = pd.to_datetime(daily_df['forecast_start'], utc=True)

cs_df = pd.read_csv("data/POLARIS_v0_1_clearsky_decomposition.csv")
cs_df['TIMESTAMP'] = pd.to_datetime(cs_df['TIMESTAMP'], utc=True)
cs_df.set_index('TIMESTAMP', inplace=True)

expanded_rows = []
origins = sorted(daily_df['forecast_start'].drop_duplicates().tolist())
start_time = time.time()
print(f"2. Expanding {len(origins)} daily origins into 8,328 rolling hourly origins...")

for midnight_orig in origins:
    base_forecast = daily_df[daily_df['forecast_start'] == midnight_orig].sort_values('horizon_hour').reset_index(drop=True)
    if len(base_forecast) != 24:
        continue
        
    for hour_offset in range(24):
        current_origin = midnight_orig + timedelta(hours=hour_offset)
        rolling_horizon = []
        
        for h in range(24):
            target_time = current_origin + timedelta(hours=h)
            hours_from_midnight = hour_offset + h
            
            if hours_from_midnight < 24:
                # Use real ML prediction
                row_data = base_forecast.iloc[hours_from_midnight].copy()
                row_data['forecast_start'] = current_origin
                row_data['horizon_hour'] = h + 1
                rolling_horizon.append(row_data)
            else:
                # Cross-day padding using C.2 logic
                synthetic_row = base_forecast.iloc[23].copy()
                synthetic_row['forecast_start'] = current_origin
                synthetic_row['horizon_hour'] = h + 1
                try:
                    synthetic_row['clearsky_ghi'] = cs_df.loc[target_time, 'clearsky_ghi']
                    synthetic_row['solar_elevation'] = max(0.0, 90.0 - synthetic_row['solar_zenith'])
                except KeyError:
                    pass
                rolling_horizon.append(synthetic_row)
                
        expanded_rows.extend(rolling_horizon)

print("3. Saving contiguous hourly matrix...")
hourly_df = pd.DataFrame(expanded_rows)
out_path = "scratch/hourly_rolling_candidate_matrix.parquet"
hourly_df.to_parquet(out_path, index=False)
print(f"SUCCESS: Generated {len(hourly_df):,} rows in {time.time() - start_time:.1f} seconds.")
print(f"File saved to: {out_path}")
