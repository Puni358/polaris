#!/usr/bin/env python3
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://data.fieldsites.se/licence_accept?ids=%5B%22CWT5DHNcPD00c8IWgAZtcmrtthZkZOGqkAtBDaaN9ZA%22%5D"
}

url = "https://data.fieldsites.se/licence_accept?ids=%5B%22CWT5DHNcPD00c8IWgAZtcmrt%22%5D"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        print("Status:", resp.status)
        print("Final URL:", resp.geturl())
        print("Content-Type:", resp.headers.get("Content-Type"))
        content = resp.read()
        print("Content length:", len(content))
        print("First 200 bytes:", content[:200])
except Exception as e:
        print("Error:", e)
