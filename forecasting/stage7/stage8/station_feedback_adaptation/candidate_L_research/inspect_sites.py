#!/usr/bin/env python3
import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def inspect_url(url):
    print(f"=== Inspecting {url} ===")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            print(f"HTML length: {len(html)}")
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            if title_match:
                print("Title:", title_match.group(1).strip())
            
            # Find data download URLs (e.g. data.fieldsites.se/objects/... or static/meta API endpoints)
            matches = re.findall(r'https?://[^\s<>"]+', html)
            print("Found URLs count:", len(matches))
            for m in matches:
                if any(k in m.lower() for k in ["download", "object", "file", "csv", "data", "pid"]):
                    print("  -", m)
    except Exception as e:
        print("Error:", e)

inspect_url("https://meta.fieldsites.se/objects/CWT5DHNcPD00c8IWgAZtcmrt")
inspect_url("https://meta.fieldsites.se/objects/t0AeJcJn3RUXzCvdy6X8KWI5")
