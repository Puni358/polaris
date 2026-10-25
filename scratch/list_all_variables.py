import urllib.request
import re

arome_dds_url = "https://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/14/arome_arctic_det_2_5km_20240114T18Z.nc.dds"
meps_sfc_dds_url = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_sfc_20240114T18Z.ncml.dds"
meps_pl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_pl_20240114T18Z.ncml.dds"
meps_hl_dds_url  = "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/14/meps_det_hl_20240114T18Z.ncml.dds"

def get_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

def parse_vars_full(dds_text):
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

arome_vars = parse_vars_full(get_text(arome_dds_url))
meps_sfc = parse_vars_full(get_text(meps_sfc_dds_url))
meps_pl  = parse_vars_full(get_text(meps_pl_dds_url))
meps_hl  = parse_vars_full(get_text(meps_hl_dds_url))

print("=== AROME-ARCTIC VARIABLES SEARCH ===")
keywords = ["cloud", "water", "ice", "liquid", "wind", "temp", "humidity", "flux", "shortwave", "radiation", "atmosphere"]
for k, v in arome_vars.items():
    if any(kw in k.lower() for kw in keywords):
        dims_str = ", ".join([f"{dim}:{sz}" for dim, sz in v['dims'].items()])
        print(f"  AROME: {k} -> {dims_str}")

print("\n=== MEPS SURFACE VARIABLES SEARCH ===")
for k, v in meps_sfc.items():
    if any(kw in k.lower() for kw in keywords):
        dims_str = ", ".join([f"{dim}:{sz}" for dim, sz in v['dims'].items()])
        print(f"  MEPS SFC: {k} -> {dims_str}")

print("\n=== MEPS PRESSURE LEVEL (PL) VARIABLES SEARCH ===")
for k, v in meps_pl.items():
    dims_str = ", ".join([f"{dim}:{sz}" for dim, sz in v['dims'].items()])
    print(f"  MEPS PL: {k} -> {dims_str}")

print("\n=== MEPS HYBRID LEVEL (HL) VARIABLES SEARCH ===")
for k, v in meps_hl.items():
    dims_str = ", ".join([f"{dim}:{sz}" for dim, sz in v['dims'].items()])
    print(f"  MEPS HL: {k} -> {dims_str}")

