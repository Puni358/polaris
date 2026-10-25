#!/usr/bin/env python3
"""
STAGE 8.6A — CAMS SMOKE TEST FILE INSPECTION SCRIPT
===================================================
Inspects ONLY the single GRIB file:
  forecasting/stage7/stage8/stage8_6_cams_feasibility/CAMS_SMOKE_TEST_20240101_12Z_L12.grib

Strict Governance:
- NO 347-origin extraction
- NO model training
- NO EVEN CV
- NO ODD target access
- NO tuning
- NO modification of docs/decision_registers/POLARIS_MASTER_HANDOFF.md
- NO declaration of CAMS utility/rejection
- NO Stage 8.6B start
"""

import os
import sys
import json
import eccodes
import cfgrib
import xarray as xr
import numpy as np
from pathlib import Path

FILE_PATH = Path("/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_6_cams_feasibility/CAMS_SMOKE_TEST_20240101_12Z_L12.grib")

# Station Coordinates: SITES Nuolja
NUOLJA_LAT = 68.362074
NUOLJA_LON = 18.738752

def inspect_grib_messages(file_path):
    assert file_path.exists(), f"File not found: {file_path}"
    
    file_size_bytes = file_path.stat().st_size
    print(f"File Path: {file_path}")
    print(f"File Size: {file_size_bytes} bytes ({file_size_bytes / 1024:.2f} KB)")
    
    messages = []
    with open(file_path, "rb") as f:
        msg_idx = 0
        while True:
            gid = eccodes.codes_grib_new_from_file(f)
            if gid is None:
                break
            msg_idx += 1
            
            # Extract key metadata fields
            keys_to_extract = [
                "name", "shortName", "paramId", "units", "cfName", "cfVarName",
                "discipline", "parameterCategory", "parameterNumber",
                "dataDate", "dataTime", "stepRange", "startStep", "endStep", "stepUnits",
                "validityDate", "validityTime", "gridType",
                "Ni", "Nj", "numberOfPoints", "missingValue", "bitmapPresent",
                "latitudeOfFirstGridPointInDegrees", "latitudeOfLastGridPointInDegrees",
                "longitudeOfFirstGridPointInDegrees", "longitudeOfLastGridPointInDegrees",
                "iDirectionIncrementInDegrees", "jDirectionIncrementInDegrees"
            ]
            
            meta = {"message_index": msg_idx}
            for k in keys_to_extract:
                try:
                    if eccodes.codes_is_defined(gid, k):
                        val = eccodes.codes_get(gid, k)
                        meta[k] = val
                    else:
                        meta[k] = None
                except Exception as e:
                    meta[k] = f"EXCP: {e}"
                    
            # Get values array and lat/lon coordinates
            try:
                values = eccodes.codes_get_values(gid)
                lats = eccodes.codes_get_array(gid, "latitudes")
                lons = eccodes.codes_get_array(gid, "longitudes")
                
                meta["values_count"] = len(values)
                meta["min_val"] = float(np.nanmin(values))
                meta["max_val"] = float(np.nanmax(values))
                meta["mean_val"] = float(np.nanmean(values))
                meta["median_val"] = float(np.median(values))
                meta["std_val"] = float(np.nanstd(values))
                
                # Check for missing values / NaNs
                missing_val = meta.get("missingValue", 9999.0)
                n_missing = int(np.sum((values == missing_val) | np.isnan(values)))
                meta["missing_count"] = n_missing
                
                # Distance to Nuolja
                dists = np.sqrt(((lats - NUOLJA_LAT) * 111.0)**2 + 
                                ((lons - NUOLJA_LON) * 111.0 * np.cos(np.radians(NUOLJA_LAT)))**2)
                nearest_idx = int(np.argmin(dists))
                meta["nearest_lat"] = float(lats[nearest_idx])
                meta["nearest_lon"] = float(lons[nearest_idx])
                meta["nearest_dist_km"] = float(dists[nearest_idx])
                meta["nearest_value"] = float(values[nearest_idx])
                
            except Exception as e:
                meta["values_error"] = str(e)
                
            eccodes.codes_release(gid)
            messages.append(meta)
            
    return messages

def main():
    print("=== INSPECTING CAMS SMOKE TEST GRIB FILE ===")
    messages = inspect_grib_messages(FILE_PATH)
    
    print(f"\nTotal GRIB Messages Found: {len(messages)}")
    print("=" * 60)
    
    for msg in messages:
        print(f"\n--- Message #{msg['message_index']} ---")
        for k, v in msg.items():
            print(f"  {k:35s}: {v}")
            
    # Also attempt loading with cfgrib / xarray to verify high-level reader compatibility
    print("\n" + "=" * 60)
    print("Testing xarray / cfgrib high-level dataset loading...")
    try:
        ds_list = cfgrib.open_datasets(FILE_PATH)
        print(f"cfgrib successfully opened {len(ds_list)} dataset(s):")
        for i, ds in enumerate(ds_list, 1):
            print(f"\nDataset #{i}:")
            print(ds)
            print("\nData variables:")
            for varname in ds.data_vars:
                da = ds[varname]
                print(f"  Variable: {varname}")
                print(f"    Long name: {da.attrs.get('long_name', 'N/A')}")
                print(f"    Units    : {da.attrs.get('units', 'N/A')}")
                print(f"    Shape    : {da.shape}")
                print(f"    Min/Max  : {float(da.min()):.6f} / {float(da.max()):.6f}")
    except Exception as e:
        print(f"cfgrib loading error: {e}")

if __name__ == "__main__":
    main()
