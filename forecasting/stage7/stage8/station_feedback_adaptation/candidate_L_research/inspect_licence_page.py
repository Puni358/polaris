#!/usr/bin/env python3
import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

url = "https://data.fieldsites.se/licence_accept?ids=%5B%22CWT5DHNcPD00c8IWgAZtcmrtthZkZOGqkAtBDaaN9ZA%22%5D"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, context=ctx) as resp:
    html = resp.read().decode("utf-8")
    print("Length:", len(html))
    # Print all script tags or form tags
    for m in re.finditer(r'<(script|form|a|button|input)[^>]*>', html, re.IGNORECASE):
        print(m.group(0))
