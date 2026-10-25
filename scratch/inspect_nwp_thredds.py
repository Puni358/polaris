import urllib.request
import re
import xarray as xr
import numpy as np

nuolja_lat = 68.362074
nuolja_lon = 18.738752

print("=== INSPECTING AROME-ARCTIC CATALOG ===")
arome_catalog_url = "https://thredds.met.no/thredds/catalog/aromearcticarchive/2024/01/14/catalog.html"
req = urllib.request.Request(arome_catalog_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')
    files = re.findall(r'href=[\'"]([^\'"]*arome_arctic[^\'"]*\.nc)[\'"]', html)
    print("Found AROME files on 2024-01-14:", len(files))
    for f in set(files):
        print(" -", f)

print("\n=== INSPECTING MEPS CATALOG ===")
meps_catalog_url = "https://thredds.met.no/thredds/catalog/meps25epsarchive/2024/01/14/catalog.html"
req = urllib.request.Request(meps_catalog_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')
    files = re.findall(r'href=[\'"]([^\'"]*meps[^\'"]*\.ncml)[\'"]', html)
    print("Found MEPS files on 2024-01-14:", len(files))
    for f in set(files):
        print(" -", f)
