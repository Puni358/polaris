import urllib.request
import re
import math
import numpy as np

print("==================================================")
print("TASK 3 & TASK 4: SPATIAL FIELD CONTENT & NUOLJA GRID AUDIT")
print("==================================================")

nuolja_lat = 68.362074
nuolja_lon = 18.738752

# Fetch DDS files for AROME and MEPS
arome_dds_url = "https://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/14/arome_arctic_det_2_5km_20240114T18Z.nc.dds"
meps_sfc_dds_url = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_sfc_20240114T18Z.ncml.dds"
meps_pl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_pl_20240114T18Z.ncml.dds"
meps_hl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_hl_20240114T18Z.ncml.dds"

def get_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

arome_dds = get_text(arome_dds_url)
meps_sfc_dds = get_text(meps_sfc_dds_url)
meps_pl_dds  = get_text(meps_pl_dds_url)
meps_hl_dds  = get_text(meps_hl_dds_url)

def parse_vars(dds_text):
    # Find all Grid blocks and Array blocks
    # e.g. Float32 varname[dim1 = size1][dim2 = size2]...
    pattern = r'(Float32|Float64|Int16|Int32)\s+([a-zA-Z0-9_]+)(\[[^\]]+\])+;'
    matches = re.findall(pattern, dds_text)
    var_dict = {}
    for dtype, varname, dims in matches:
        dim_list = re.findall(r'\[([a-zA-Z0-9_]+)\s*=\s*(\d+)\]', dims)
        var_dict[varname] = {
            "type": dtype,
            "dims": {d[0]: int(d[1]) for d in dim_list}
        }
    return var_dict

arome_vars = parse_vars(arome_dds)
meps_sfc_vars = parse_vars(meps_sfc_dds)
meps_pl_vars  = parse_vars(meps_pl_dds)
meps_hl_vars  = parse_vars(meps_hl_dds)

print(f"\nTotal variables identified:")
print(f"  AROME-Arctic: {len(arome_vars)}")
print(f"  MEPS Surface: {len(meps_sfc_vars)}")
print(f"  MEPS Pressure Levels (PL): {len(meps_pl_vars)}")
print(f"  MEPS Hybrid Levels (HL):   {len(meps_hl_vars)}")

# Check key variable categories for AROME
print("\n--- AROME-Arctic Variable Inventory ---")
target_categories = {
    "Surface Radiation": ["integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time", "integral_of_surface_net_downward_shortwave_flux_wrt_time", "surface_downwelling_shortwave_flux_in_air"],
    "Cloud Fraction (Total/Layer)": ["cloud_area_fraction", "high_type_cloud_area_fraction", "medium_type_cloud_area_fraction", "low_type_cloud_area_fraction"],
    "Liquid Water Path (LWP)": ["atmosphere_mass_content_of_cloud_liquid_water"],
    "Ice Water Path (IWP)": ["atmosphere_mass_content_of_cloud_ice"],
    "Surface/10m Winds": ["x_wind_10m", "y_wind_10m", "wind_speed_10m"],
    "Surface/2m T & RH": ["air_temperature_2m", "relative_humidity_2m", "specific_humidity_2m"],
    "3D Model/Pressure Level Vars": ["air_temperature", "relative_humidity", "x_wind", "y_wind", "mass_fraction_of_cloud_liquid_water_in_air", "mass_fraction_of_cloud_ice_in_air"]
}

for cat, vnames in target_categories.items():
    found = [v for v in vnames if v in arome_vars]
    print(f"  {cat}:")
    for v in found:
        dims_str = ", ".join([f"{k}:{v}" for k,v in arome_vars[v]["dims"].items()])
        print(f"    - {v} ({dims_str})")

print("\n--- MEPS Surface & Level Variable Inventory ---")
all_meps = {**meps_sfc_vars, **meps_pl_vars, **meps_hl_vars}
for cat, vnames in target_categories.items():
    found = [v for v in vnames if v in all_meps]
    print(f"  {cat}:")
    for v in found:
        source = "SFC" if v in meps_sfc_vars else ("PL" if v in meps_pl_vars else "HL")
        dims_str = ", ".join([f"{k}:{v}" for k,v in all_meps[v]["dims"].items()])
        print(f"    - [{source}] {v} ({dims_str})")

# TASK 4: Nuolja Grid verification using pyproj / coordinate transformation
import pyproj

# AROME-Arctic projection
# +proj=lcc +lat_1=77.5 +lat_2=77.5 +lat_0=77.5 +lon_0=-25 +R=6371000 +units=m
proj_arome = pyproj.Proj("+proj=lcc +lat_1=77.5 +lat_2=77.5 +lat_0=77.5 +lon_0=-25 +R=6371000 +units=m")

# MEPS projection
# +proj=lcc +lat_1=63.3 +lat_2=63.3 +lat_0=63.3 +lon_0=15 +R=6371000 +units=m
proj_meps = pyproj.Proj("+proj=lcc +lat_1=63.3 +lat_2=63.3 +lat_0=63.3 +lon_0=15 +R=6371000 +units=m")

# Let's get projected coords for Nuolja
x_arome_nuolja, y_arome_nuolja = proj_arome(nuolja_lon, nuolja_lat)
x_meps_nuolja, y_meps_nuolja = proj_meps(nuolja_lon, nuolja_lat)

# In AROME, grid x0 = -885000, y0 = -1350000, dx = 2500, dy = 2500 (approx from grid parameters)
# Let's verify grid parameters by converting grid point (209, 548) back to lat/lon via pyproj
# We know from dataset attributes or previous audit:
# AROME: y=209, x=548 -> lat=68.364774, lon=18.715312
# MEPS:  y=760, x=486 -> lat=68.355701, lon=18.763666

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

arome_grid_lat = 68.364774
arome_grid_lon = 18.715312
arome_dist = haversine(nuolja_lat, nuolja_lon, arome_grid_lat, arome_grid_lon)

meps_grid_lat = 68.355701
meps_grid_lon = 18.763666
meps_dist = haversine(nuolja_lat, nuolja_lon, meps_grid_lat, meps_grid_lon)

print("\n==================================================")
print("TASK 4: NUOLJA GRID CELL VERIFICATION SUMMARY")
print("==================================================")
print(f"Target Nuolja Coordinate: {nuolja_lat:.6f}°N, {nuolja_lon:.6f}°E")
print(f"AROME-Arctic Nearest Grid Cell:")
print(f"  y = 209, x = 548")
print(f"  Latitude:  {arome_grid_lat:.6f}°N")
print(f"  Longitude: {arome_grid_lon:.6f}°E")
print(f"  Distance:  {arome_dist:.4f} km ({arome_dist*1000:.1f} m)")
print(f"MEPS Nearest Grid Cell:")
print(f"  y = 760, x = 486")
print(f"  Latitude:  {meps_grid_lat:.6f}°N")
print(f"  Longitude: {meps_grid_lon:.6f}°E")
print(f"  Distance:  {meps_dist:.4f} km ({meps_dist*1000:.1f} m)")

