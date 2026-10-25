import xarray as xr
import numpy as np
import pandas as pd

nuolja_lat = 68.362074
nuolja_lon = 18.738752

dates = ["20240114", "20240414", "20240714", "20241014"]

def haversine_np(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367.0 * c
    return km

print("==================================================")
print("INSPECTING AROME-ARCTIC ARCHIVE METADATA")
print("==================================================")

for date_str in dates:
    yyyy = date_str[:4]
    mm = date_str[4:6]
    dd = date_str[6:8]
    url = f"https://thredds.met.no/thredds/dodsC/aromearcticarchive/{yyyy}/{mm}/{dd}/arome_arctic_det_2_5km_{date_str}T18Z.nc"
    print(f"\n--- AROME-Arctic {date_str}T18Z ---")
    print("URL:", url)
    try:
        ds = xr.open_dataset(url, engine="netcdf4")
        print("Dimensions:", dict(ds.sizes))
        
        # Check time variable
        time_var = ds["time"].values
        print(f"Time steps count: {len(time_var)}")
        print(f"First valid time: {pd.to_datetime(time_var[0])}")
        print(f"Last valid time:  {pd.to_datetime(time_var[-1])}")
        
        # Target day is next day (e.g. 2024-01-15 00:00 to 23:00)
        target_day_str = pd.to_datetime(time_var[0]).strftime("%Y-%m-%d") # approx
        # Check forecast leads for H1 (00:00 UTC Day D) to H24 (23:00 UTC Day D)
        init_time = pd.Timestamp(f"{yyyy}-{mm}-{dd} 18:00:00")
        valid_times = [pd.to_datetime(t) for t in time_var]
        
        # Calculate lead hours
        leads = [(vt - init_time).total_seconds() / 3600.0 for vt in valid_times]
        print(f"Lead hours sample: min={min(leads)}, max={max(leads)}")
        
        # Check Nuolja grid cell
        lats = ds["latitude"].values
        lons = ds["longitude"].values
        dist = haversine_np(nuolja_lat, nuolja_lon, lats, lons)
        min_idx = np.unravel_index(np.argmin(dist), dist.shape)
        min_dist = dist[min_idx]
        grid_lat = lats[min_idx]
        grid_lon = lons[min_idx]
        print(f"Nuolja nearest grid: y={min_idx[0]}, x={min_idx[1]}, lat={grid_lat:.6f}, lon={grid_lon:.6f}, dist={min_dist:.4f} km")
        
        # Close dataset
        ds.close()
    except Exception as e:
        print("Error opening AROME dataset:", e)
