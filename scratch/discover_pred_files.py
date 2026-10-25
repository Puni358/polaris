import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime

WORKSPACE = "/home/punith-bs/01polaris (Copy)"
BRAIN_DIR = "/home/punith-bs/.gemini/antigravity/brain/78d43461-fb6a-495e-9d93-9d263bdcf970"
SCRATCH_DIR = os.path.join(WORKSPACE, "scratch")
os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

# 1. Discover prediction files
print("Scanning for prediction files...")
pred_files = []
for root, dirs, files in os.walk(WORKSPACE):
    if '.venv' in root or '__pycache__' in root or 'forecasting/foundation_models/chronos/.venv' in root or 'forecasting/foundation_models/moirai/.venv' in root:
        continue
    for f in files:
        if f.endswith('.csv') and ('pred' in f.lower() or 'baseline' in f.lower() or 'chronos' in f.lower() or 'timesfm' in f.lower() or 'moirai' in f.lower()):
            path = os.path.join(root, f)
            pred_files.append((f, path, os.path.getsize(path)))

for f, p, s in pred_files:
    print(f"File: {f} ({s} bytes) -> {p}")
