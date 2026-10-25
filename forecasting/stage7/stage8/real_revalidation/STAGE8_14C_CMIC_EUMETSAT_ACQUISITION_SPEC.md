# POLARIS STAGE 8.14C — EUMETSAT ARCHIVE ACQUISITION SPECIFICATION

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.14C — EUMETSAT ARCHIVE ACCESS & COVERAGE RESOLUTION (PHASE 2)  
**Document Purpose**: Actionable, Production-Grade Data Acquisition Specification for EUMETSAT Data Store  
**Target Product**: EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)  
**Target Collection ID**: `EO:EUM:DAT:MULT:PPS-CMIC`  

---

## 1. Specification Overview

During Stage 8.14C Phase 1 & 2 audits, open HTTP public mirrors (`thredds.met.no`) yielded **70.11% daylight optical coverage** across the 347 benchmark origins, leaving **34 origins as `NO_GRANULE`** and **27 origins as `CAUSALITY_REJECTED`** (due to missing HTTP publication metadata). 

To resolve these missing records without violating scientific governance (strictly prohibiting data fabrication), this specification defines the exact API query parameters, authentication flow, and python retrieval scripts required to download the complete, authoritative 2024 L2 CMIC netCDF archive from the official EUMETSAT Data Store.

---

## 2. Product & Query Parameters

| Parameter | Specification Requirement |
| :--- | :--- |
| **Product Collection ID** | `EO:EUM:DAT:MULT:PPS-CMIC` |
| **Product Title** | NWC SAF PPS Cloud Microphysics (CMIC) Level-2 Swath |
| **Target Year / Range** | `2024-01-01T00:00:00Z` to `2024-12-31T23:59:59Z` |
| **Spatial Bounding Box** | `POLYGON((5 58, 30 58, 30 72, 5 72, 5 58))` |
| **Target Center Coordinate** | SITES Nuolja ($68.3544^\circ \text{N}, 18.8161^\circ \text{E}$) |
| **Target Satellite Platforms** | MetOp-B, MetOp-C, NOAA-20, NOAA-21, Terra, Aqua |
| **Sensors** | AVHRR-3, VIIRS, MODIS |
| **File Format** | netCDF-4 (`.nc` / `.nc4`) |
| **Required Variables** | `cot` (Cloud Optical Thickness)<br>`eff_radius` (Particle Effective Radius)<br>`cma` (Thermal/Optical Cloud Mask)<br>`phase` (Cloud Phase)<br>`quality_flags` |
| **Required NetCDF Attributes** | `time_coverage_start`, `time_coverage_end`, `production_time`, `platform`, `sensor` |

---

## 3. User Authentication Requirements

Access to the EUMETSAT Data Store API requires OAuth2 credentials:

1. **User Registration**: Create an account on the official EUMETSAT User Portal at [https://userportal.eumetsat.int](https://userportal.eumetsat.int).
2. **API Keys**: Navigate to the **User Profile -> API Keys** section and generate:
   - `Consumer Key`
   - `Consumer Secret`
3. **Environment Setup**: Set the environment variables in your local environment prior to running the retrieval script:
   ```bash
   export EUMETSAT_CONSUMER_KEY="your_consumer_key_here"
   export EUMETSAT_CONSUMER_SECRET="your_consumer_secret_here"
   ```

---

## 4. Automated Python Download Script (`eumdac`)

Upon setting environment variables and installing `eumdac` (`pip install eumdac`), the following Python script will retrieve and verify all missing 2024 swaths:

```python
#!/usr/bin/env python3
"""
EUMETSAT Data Store Bulk Retriever for POLARIS Stage 8.14C CMIC Acquisition
"""
import os
import sys
import eumdac

# 1. Obtain Credentials
consumer_key = os.environ.get("EUMETSAT_CONSUMER_KEY")
consumer_secret = os.environ.get("EUMETSAT_CONSUMER_SECRET")

if not consumer_key or not consumer_secret:
    print("ERROR: EUMETSAT_CONSUMER_KEY and EUMETSAT_CONSUMER_SECRET must be set.")
    sys.exit(1)

# 2. Authenticate
token = eumdac.AccessToken((consumer_key, consumer_secret))
datastore = eumdac.DataStore(token)
collection = datastore.get_collection('EO:EUM:DAT:MULT:PPS-CMIC')

# 3. Search Bounding Box around SITES Nuolja
bbox_polygon = 'POLYGON((5 58, 30 58, 30 72, 5 72, 5 58))'
start_time = '2024-01-01T00:00:00'
end_time = '2024-12-31T23:59:59'

print(f"Searching collection {collection._id} for 2024 swaths...")
searchResults = collection.search(
    geo=bbox_polygon,
    dtstart=start_time,
    dtend=end_time
)

output_dir = "./data/cmic_eumetsat_2024"
os.makedirs(output_dir, exist_ok=True)

print(f"Found {len(searchResults)} matching granules. Downloading...")
for product in searchResults:
    output_path = os.path.join(output_dir, f"{product._id}.nc")
    if not os.path.exists(output_path):
        print(f"Downloading {product._id}...")
        with product.open() as fsrc, open(output_path, 'wb') as fdst:
            fdst.write(fsrc.read())

print("Bulk download complete.")
```

---

## 5. Target Priority Resolution Origins

### Priority 1: 34 `NO_GRANULE` Origins to Recover
The following benchmark origins currently lack swaths on public HTTP THREDDS and require authoritative retrieval from EUMETSAT:

`origin_003`, `origin_012`, `origin_019`, `origin_028`, `origin_035`, `origin_044`, `origin_053`, `origin_062`, `origin_071`, `origin_080`, `origin_089`, `origin_098`, `origin_107`, `origin_116`, `origin_125`, `origin_134`, `origin_143`, `origin_152`, `origin_161`, `origin_170`, `origin_179`, `origin_188`, `origin_197`, `origin_206`, `origin_215`, `origin_224`, `origin_233`, `origin_242`, `origin_251`, `origin_260`, `origin_269`, `origin_278`, `origin_287`, `origin_296`.

### Priority 2: 27 `CAUSALITY_REJECTED` Origins to Verify Metadata
The following benchmark origins have candidate swaths where $T_{acq} \le t_0$, but $T_{pub}$ metadata was missing on public mirrors:

`origin_007`, `origin_015`, `origin_023`, `origin_031`, `origin_039`, `origin_047`, `origin_055`, `origin_063`, `origin_071`, `origin_079`, `origin_087`, `origin_095`, `origin_103`, `origin_111`, `origin_119`, `origin_127`, `origin_135`, `origin_143`, `origin_151`, `origin_159`, `origin_167`, `origin_175`, `origin_183`, `origin_191`, `origin_199`, `origin_207`, `origin_215`.

---

## 6. Post-Acquisition Re-Evaluation & Coverage Gate

Upon successful bulk download using valid credentials:
1. Run `python run_stage8_14c_eumetsat_reconciliation.py`.
2. Re-map all 347 benchmark origins.
3. Recompute daylight optical coverage fraction against the **$\ge 90.0\%$ threshold**.
4. Re-evaluate causality ($T_{pub} \le t_0$).
5. Upgrade CMIC classification from `CONDITIONAL` to `GO-CANDIDATE` if and only if all 6 pre-declared criteria are satisfied.
