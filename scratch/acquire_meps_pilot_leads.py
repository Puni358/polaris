#!/usr/bin/env python3
"""
POLARIS — Stage 1 Causal MEPS Lead Acquisition (June 1–8, 2024 Pilot)
File: scratch/acquire_meps_pilot_leads.py

Acquires ONLY the missing lead slices (leads 31..52) for the 7 approved 18Z cycles
from MET Norway THREDDS OPeNDAP archive:
  - Variables: LWP, IWP, u700, v700, pressure, time, forecast_reference_time
  - Location: Nuolja Middle Station (y=760, x=486, level 8 ~ 700 hPa)
  - Output directory: scratch/meps_pilot_leads/

Strict Governance:
  - ZERO model inference, optimizer execution, or simulations.
  - Fail-closed validation on all downloaded payloads.
  - Cryptographic verification and retrieval manifest generated.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = REPO_ROOT / "scratch/meps_pilot_leads"

# Target Coordinates & Indices
NUOLJA_Y = 760
NUOLJA_X = 486
P700_IDX = 8
LEAD_START = 31
LEAD_END = 52
EXPECTED_COUNT = LEAD_END - LEAD_START + 1  # 22 leads

ARCHIVE_BASE = "https://thredds.met.no/thredds/dodsC/meps25epsarchive"
USER_AGENT = "POLARIS-Stage1-Pilot-Acquisition/1.0 (research, authorized pilot)"

# Approved 7 cycles (18Z of D-1 for June 1..7)
TARGET_CYCLES = [
    datetime(2024, 5, 31, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 1, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 2, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 3, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 4, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 5, 18, 0, tzinfo=timezone.utc),
    datetime(2024, 6, 6, 18, 0, tzinfo=timezone.utc),
]

VAR_LWP = "mass_fraction_of_cloud_condensed_water_in_air_pl"
VAR_IWP = "mass_fraction_of_cloud_ice_in_air_pl"
VAR_U = "x_wind_pl"
VAR_V = "y_wind_pl"


def compute_sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_ascii_series(ascii_text: str, var_name: str, expected_count: int) -> Optional[np.ndarray]:
    """Parses OPeNDAP ASCII numerical response for a specific variable."""
    if not ascii_text or var_name not in ascii_text:
        return None

    # Handle inline scalar (e.g. forecast_reference_time)
    if expected_count == 1:
        for raw_line in ascii_text.splitlines():
            line_str = raw_line.strip()
            if line_str.startswith(var_name + ",") or line_str.startswith(var_name + " ,"):
                remainder = line_str[len(var_name):].lstrip()
                if remainder.startswith(","):
                    remainder = remainder[1:].strip()
                try:
                    return np.array([float(remainder)], dtype=float)
                except ValueError:
                    pass

    try:
        lines = ascii_text.splitlines()
        values: List[float] = []
        in_var = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith(var_name + "[") or line_str.startswith(var_name + "."):
                in_var = True
                continue
            if in_var:
                if line_str.startswith("Dataset") or (line_str and line_str[0].isalpha() and "[" in line_str):
                    in_var = False
                    continue
                for p in line_str.split(","):
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    if "[" in p_clean:
                        p_clean = p_clean.split("]")[-1].strip()
                    try:
                        values.append(float(p_clean))
                    except ValueError:
                        pass
        if len(values) >= expected_count:
            return np.array(values[:expected_count], dtype=float)
        return None
    except Exception:
        return None


def build_request_url(run_init: datetime) -> Tuple[str, str]:
    y = run_init.strftime("%Y")
    m = run_init.strftime("%m")
    d = run_init.strftime("%d")
    tag = run_init.strftime("%Y%m%dT%HZ")
    base_url = f"{ARCHIVE_BASE}/{y}/{m}/{d}/meps_det_pl_{tag}.ncml.ascii"

    query_parts = [
        f"{VAR_LWP}[{LEAD_START}:1:{LEAD_END}][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]",
        f"{VAR_IWP}[{LEAD_START}:1:{LEAD_END}][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]",
        f"{VAR_U}[{LEAD_START}:1:{LEAD_END}][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]",
        f"{VAR_V}[{LEAD_START}:1:{LEAD_END}][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]",
        f"pressure[{P700_IDX}:1:{P700_IDX}]",
        f"time[{LEAD_START}:1:{LEAD_END}]",
        "forecast_reference_time"
    ]
    raw_query = ",".join(query_parts)
    encoded_query = urllib.parse.quote(raw_query, safe="=:,")
    return f"{base_url}?{encoded_query}", base_url


def acquire_cycle(run_init: datetime) -> Dict[str, Any]:
    url, base_url = build_request_url(run_init)
    tag = run_init.strftime("%Y%m%dT%HZ")
    print(f"\n[ACQUIRE] Querying MEPS cycle {tag} (leads {LEAD_START}..{LEAD_END})...")
    print(f"  URL: {url}")

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as resp:
        body_bytes = resp.read()
    t_elapsed = time.perf_counter() - t0
    print(f"  [OK] Received {len(body_bytes):,} bytes in {t_elapsed:.2f}s")

    raw_text = body_bytes.decode("utf-8", errors="replace")
    raw_sha = compute_sha256_bytes(body_bytes)

    # Save raw ascii
    ascii_file = OUT_DIR / f"meps_{tag}_leads_{LEAD_START}_{LEAD_END}.ascii"
    ascii_file.write_bytes(body_bytes)

    # 1. Parse forecast_reference_time
    frt = parse_ascii_series(raw_text, "forecast_reference_time", 1)
    if frt is None:
        raise ValueError(f"forecast_reference_time missing in response for {tag}")
    frt_dt = datetime.fromtimestamp(float(frt[0]), tz=timezone.utc)
    if frt_dt != run_init:
        raise ValueError(f"FRT mismatch: got {frt_dt.isoformat()}, expected {run_init.isoformat()}")

    # 2. Parse time array
    time_arr = parse_ascii_series(raw_text, "time", EXPECTED_COUNT)
    if time_arr is None or len(time_arr) != EXPECTED_COUNT:
        raise ValueError(f"time array length mismatch for {tag}: got {len(time_arr) if time_arr is not None else 0}")

    valid_times_utc = []
    lead_hours = []
    for idx, epoch_sec in enumerate(time_arr):
        v_dt = datetime.fromtimestamp(float(epoch_sec), tz=timezone.utc)
        expected_lead = LEAD_START + idx
        expected_v_dt = run_init + timedelta(hours=expected_lead)
        if v_dt != expected_v_dt:
            raise ValueError(f"Timestamp step mismatch at index {idx}: {v_dt} != {expected_v_dt}")
        valid_times_utc.append(v_dt.isoformat())
        lead_hours.append(expected_lead)

    # 3. Parse pressure
    pressure = parse_ascii_series(raw_text, "pressure", 1)
    if pressure is None:
        raise ValueError(f"pressure missing for {tag}")
    p_hpa = float(pressure[0]) / 100.0 if float(pressure[0]) > 1000.0 else float(pressure[0])
    if not (650.0 <= p_hpa <= 750.0):
        raise ValueError(f"Unexpected level 8 pressure: {p_hpa} hPa (expected ~700 hPa)")

    # 4. Parse physical variables
    lwp_raw = parse_ascii_series(raw_text, VAR_LWP, EXPECTED_COUNT)
    iwp_raw = parse_ascii_series(raw_text, VAR_IWP, EXPECTED_COUNT)
    u_raw = parse_ascii_series(raw_text, VAR_U, EXPECTED_COUNT)
    v_raw = parse_ascii_series(raw_text, VAR_V, EXPECTED_COUNT)

    for name, arr in [("LWP", lwp_raw), ("IWP", iwp_raw), ("u700", u_raw), ("v700", v_raw)]:
        if arr is None or len(arr) != EXPECTED_COUNT:
            raise ValueError(f"Variable {name} length mismatch: got {len(arr) if arr is not None else 0}")
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"Variable {name} contains non-finite values!")

    if np.any(lwp_raw < 0.0) or np.any(iwp_raw < 0.0):
        raise ValueError("Negative cloud water/ice path detected!")

    parsed_record = {
        "run_init_utc": run_init.isoformat(),
        "tag": tag,
        "base_url": base_url,
        "query_url": url,
        "retrieval_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(t_elapsed, 3),
        "raw_ascii_file": ascii_file.name,
        "raw_ascii_size_bytes": len(body_bytes),
        "raw_ascii_sha256": raw_sha,
        "pressure_hpa": round(p_hpa, 2),
        "leads_acquired": lead_hours,
        "valid_times_utc": valid_times_utc,
        "data": {
            "lead_hours": lead_hours,
            "valid_times_utc": valid_times_utc,
            "lwp_mass_fraction": [float(x) for x in lwp_raw],
            "iwp_mass_fraction": [float(x) for x in iwp_raw],
            "u700": [float(x) for x in u_raw],
            "v700": [float(x) for x in v_raw],
        }
    }

    json_file = OUT_DIR / f"meps_{tag}_leads_{LEAD_START}_{LEAD_END}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(parsed_record, f, indent=2)

    parsed_record["json_file"] = json_file.name
    parsed_record["json_size_bytes"] = json_file.stat().st_size
    parsed_record["json_sha256"] = compute_sha256_file(json_file)

    print(f"  [SAVED] {ascii_file.name} (SHA: {raw_sha[:16]}...)")
    print(f"  [SAVED] {json_file.name} (SHA: {parsed_record['json_sha256'][:16]}...)")
    print(f"  [VALIDATED] All 22 leads (31..52) strictly valid, finite, and physically aligned.")

    return parsed_record


def main():
    print("=" * 80)
    print("POLARIS — STAGE 1 CAUSAL MEPS LEAD ACQUISITION (JUNE 1–8, 2024 PILOT)")
    print("=" * 80)
    print(f"Target directory: {OUT_DIR}")
    print(f"Requested leads: {LEAD_START}..{LEAD_END} ({EXPECTED_COUNT} leads per cycle)")
    print(f"Target cycles: {len(TARGET_CYCLES)} cycles")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for cycle_dt in TARGET_CYCLES:
        rec = acquire_cycle(cycle_dt)
        records.append(rec)

    # Build comprehensive manifest
    manifest = {
        "stage": "STAGE_1_CAUSAL_MEPS_ACQUISITION",
        "timestamp_completed_utc": datetime.now(timezone.utc).isoformat(),
        "cycles_attempted": len(TARGET_CYCLES),
        "cycles_successful": len(records),
        "cycles_failed": 0,
        "leads_acquired_per_cycle": EXPECTED_COUNT,
        "lead_range": [LEAD_START, LEAD_END],
        "variables": [VAR_LWP, VAR_IWP, VAR_U, VAR_V],
        "location": {"name": "Nuolja Middle Station", "y": NUOLJA_Y, "x": NUOLJA_X, "pressure_level_idx": P700_IDX},
        "records": records
    }

    manifest_path = OUT_DIR / "STAGE1_ACQUISITION_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 80)
    print("STAGE 1 ACQUISITION COMPLETE!")
    print(f"Manifest written to: {manifest_path}")
    print(f"Manifest SHA-256: {compute_sha256_file(manifest_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
