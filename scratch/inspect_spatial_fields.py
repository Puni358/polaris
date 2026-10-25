import urllib.request
import re
import math
import numpy as np

nuolja_lat = 68.362074
nuolja_lon = 18.738752

print("==================================================")
print("TASK 3 & 4: SPATIAL FIELD CONTENT & NUOLJA GRID AUDIT")
print("==================================================")

# Fetch AROME-Arctic DDS and DAS
arome_dds_url = "https://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/14/arome_arctic_det_2_5km_20240114T18Z.nc.dds"
arome_das_url = "https://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/14/arome_arctic_det_2_5km_20240114T18Z.nc.das"

req = urllib.request.Request(arome_dds_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    arome_dds = resp.read().decode('utf-8')

req = urllib.request.Request(arome_das_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    arome_das = resp.read().decode('utf-8')

# Fetch MEPS SFC, PL, HL DDS
meps_sfc_dds_url = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_sfc_20240114T18Z.ncml.dds"
meps_pl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_pl_20240114T18Z.ncml.dds"
meps_hl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_hl_20240114T18Z.ncml.dds"

req = urllib.request.Request(meps_sfc_dds_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    meps_sfc_dds = resp.read().decode('utf-8')

req = urllib.request.Request(meps_pl_dds_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    meps_pl_dds = resp.read().decode('utf-8')

req = urllib.request.Request(meps_hl_dds_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    meps_hl_dds = resp.read().decode('utf-8')

print("\n--- AROME-Arctic Grid & Variable Summary ---")
# Extract dimensions
dims = re.findall(r'(\w+)\[\1 = (\d+)\]', arome_dds)
for dim_name, dim_size in dims:
    if dim_name in ['x', 'y', 'time', 'pressure', 'hybrid']:
        print(f"  Dimension {dim_name}: {dim_size}")

print("\n--- MEPS Grid & Variable Summary ---")
meps_dims = re.findall(r'(\w+)\[\1 = (\d+)\]', meps_sfc_dds)
for dim_name, dim_size in meps_dims:
    if dim_name in ['x', 'y', 'time', 'pressure', 'hybrid']:
        print(f"  SFC Dimension {dim_name}: {dim_size}")

# Now query Nuolja coordinate grid points via OPeNDAP ASCII slice around Nuolja!
# Nuolja is at approx y=209, x=548 for AROME, y=760, x=486 for MEPS
# Let's query AROME lat/lon slice y=205:215, x=545:555
arome_grid_ascii_url = "https://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/14/arome_arctic_det_2_5km_20240114T18Z.nc.ascii?latitude[205:1:215][545:1:555],longitude[205:1:215][545:1:555]"
req = urllib.request.Request(arome_grid_ascii_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    arome_grid_ascii = resp.read().decode('utf-8')

print("\nFetched AROME grid slice around Nuolja successfully.")

# Parse AROME grid slice and find exact minimum distance
def parse_ascii_2d(text, varname):
    # locate varname
    section = text.split(f"{varname}[")[1].split("---------------------------------------------")[1]
    # parse numbers
    vals = [float(x) for x in re.findall(r'[-+]?\d*\.\d+', section)]
    # shape 11x11
    arr = np.array(vals).reshape((11, 11))
    return arr

arome_lats = parse_ascii_2d(arome_grid_ascii, "latitude")
arome_lons = parse_ascii_2d(arome_grid_ascii, "longitude")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

min_d = 999999
best_y, best_x = -1, -1
best_lat, best_lon = 0, 0

for j in range(11):
    for i in range(11):
        lat = arome_lats[j, i]
        lon = arome_lons[j, i]
        d = haversine(nuolja_lat, nuolja_lon, lat, lon)
        if d < min_d:
            min_d = d
            best_y = 205 + j
            best_x = 545 + i
            best_lat = lat
            best_lon = lon

print(f"AROME Nearest Nuolja cell: y={best_y}, x={best_x}, lat={best_lat:.6f}°N, lon={best_lon:.6f}°E, dist={min_d:.4f} km")

# Query MEPS grid slice y=755:765, x=480:490
meps_grid_ascii_url = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_sfc_20240114T18Z.ncml.ascii?latitude[755:1:765][480:1:490],longitude[755:1:765][480:1:490]"
req = urllib.request.Request(meps_grid_ascii_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    meps_grid_ascii = resp.read().decode('utf-8')

meps_lats = parse_ascii_2d(meps_grid_ascii, "latitude")
meps_lons = parse_ascii_2d(meps_grid_ascii, "longitude")

min_d_meps = 999999
best_y_meps, best_x_meps = -1, -1
best_lat_meps, best_lon_meps = 0, 0

for j in range(11):
    for i in range(11):
        lat = meps_lats[j, i]
        lon = meps_lons[j, i]
        d = haversine(nuolja_lat, nuolja_lon, lat, lon)
        if d < min_d_meps:
            min_d_meps = d
            best_y_meps = 755 + j
            best_x_meps = 480 + i
            best_lat_meps = lat
            best_lon_meps = lon

print(f"MEPS Nearest Nuolja cell: y={best_y_meps}, x={best_x_meps}, lat={best_lat_meps:.6f}°N, lon={best_lon_meps:.6f}°E, dist={min_d_meps:.4f} km")

