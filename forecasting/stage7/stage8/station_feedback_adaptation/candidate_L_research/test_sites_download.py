#!/usr/bin/env python3
import urllib.request
import ssl
import hashlib
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

url_2020 = 'https://data.fieldsites.se/objects?ids=%5B%22CWT5DHNcPD00c8IWgAZtcmrt%22%5D'
req = urllib.request.Request(url_2020, headers=headers)

out_dir = "data/raw_historical_sites_download"
os.makedirs(out_dir, exist_ok=True)
test_path = os.path.join(out_dir, "test_2020.csv")

with urllib.request.urlopen(req, context=ctx) as resp, open(test_path, "wb") as f:
    chunk = resp.read(65536)
    f.write(chunk)
    print("Read first 64KB. Header preview:\n")
    print(chunk.decode("utf-8", errors="ignore")[:1000])

if os.path.exists(test_path):
    os.remove(test_path)
