#!/usr/bin/env python3
import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

meta_url = "https://meta.fieldsites.se/objects/CWT5DHNcPD00c8IWgAZtcmrt"
req = urllib.request.Request(meta_url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode("utf-8")
    
m = re.search(r"https://data\.fieldsites\.se/licence_accept\?ids=[^\s\"\'<>]+", html)
lic_url = m.group(0).replace("&amp;", "&")
req2 = urllib.request.Request(lic_url, headers=headers)
with urllib.request.urlopen(req2, context=ctx) as resp2:
    lic_html = resp2.read().decode("utf-8")
    for line in lic_html.splitlines():
        if any(k in line.lower() for k in ["form", "action", "submit", "accept", "download", "post", "href"]):
            print(line.strip())
