#!/usr/bin/env python3
import urllib.request
import http.cookiejar
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")]

def download_object(obj_id):
    meta_url = f"https://meta.fieldsites.se/objects/{obj_id}"
    print(f"1. Fetching meta page: {meta_url}")
    resp1 = opener.open(meta_url)
    html1 = resp1.read().decode("utf-8")
    
    m = re.search(r"https://data\.fieldsites\.se/licence_accept\?ids=[^\s\"\'<>]+", html1)
    if not m:
        print("No licence URL found.")
        return
    lic_url = m.group(0).replace("&amp;", "&")
    print(f"2. Fetching licence URL to set cookie: {lic_url}")
    resp2 = opener.open(lic_url)
    resp2.read()
    
    print(f"Cookies after licence accept: {list(cj)}")
    
    dl_url = f"https://data.fieldsites.se/objects/{obj_id}"
    print(f"3. Requesting object download: {dl_url}")
    resp3 = opener.open(dl_url)
    print("Response status:", resp3.status)
    print("Content-Type:", resp3.headers.get("Content-Type"))
    print("Content-Disposition:", resp3.headers.get("Content-Disposition"))
    data = resp3.read()
    print(f"Downloaded byte size: {len(data)}")
    print("First 200 bytes:\n", data[:200])

download_object("CWT5DHNcPD00c8IWgAZtcmrt")
