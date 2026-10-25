#!/usr/bin/env python3
import urllib.request
import http.cookiejar
import ssl
import re
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "Mozilla/5.0")]

obj_id = "dz6gxxf__nEtEkqEvxtdAhkv"
meta_url = f"https://meta.fieldsites.se/objects/{obj_id}"
resp1 = opener.open(meta_url)
html1 = resp1.read().decode("utf-8")

m = re.search(r"https://data\.fieldsites\.se/licence_accept\?ids=[^\s\"\'<>]+", html1)
lic_url = m.group(0).replace("&amp;", "&")
opener.open(lic_url).read()

dl_url = f"https://data.fieldsites.se/objects/{obj_id}"
resp3 = opener.open(dl_url)

target_path = "data/raw_historical_sites_download/SITES_MET_ANS_NMS_20190619-20191231_L2_SH.csv"
with open(target_path, "wb") as f:
    f.write(resp3.read())

print("Downloaded 2019 raw file size:", os.path.getsize(target_path), "bytes")
