import os
import hashlib
import pandas as pd

def check_file_metadata(path):
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        return
    size = os.path.getsize(path)
    print(f"EXISTS: {path} | SIZE: {size} bytes")
    df = pd.read_csv(path, nrows=5)
    print(f"COLUMNS: {list(df.columns)}")
    print(f"HEAD:\n{df.head(2)}\n")

if __name__ == "__main__":
    check_file_metadata("data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv")
    if os.path.exists("research/wind_a2/smhi_188790_ws_full.csv"):
        check_file_metadata("research/wind_a2/smhi_188790_ws_full.csv")
    else:
        print("research/wind_a2/smhi_188790_ws_full.csv not found, checking alternatives...")
