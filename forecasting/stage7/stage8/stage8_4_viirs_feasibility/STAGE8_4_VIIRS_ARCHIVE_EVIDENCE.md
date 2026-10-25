# STAGE 8.4 — VIIRS ARCHIVE EVIDENCE DOCUMENT

**Project:** POLARIS  
**Dataset:** NASA LAADS DAAC / Earthdata CMR API  
**Query Bounding Box:** 17.7388, 67.8621, 19.7388, 68.8621  

## Verified Collections
1. `CLDPROP_L2_VIIRS_SNPP`: VIIRS/SNPP Cloud Properties 6-min L2 Swath 750 m
2. `CLDPROP_L2_VIIRS_NOAA20`: VIIRS/NOAA20 Cloud Properties L2 6-Min Swath 750 m
3. `CLDMSK_L2_VIIRS_NOAA21`: VIIRS/NOAA21 Cloud Mask 6-Min L2 Swath 750 m

## Key Findings
- **Physical Overpass Coverage:** 100% (347/347 origins have VIIRS overpass within 3 hours prior to t0).
- **Sunlight / Optical Validity:** Optical properties (COT, CER) return fill values (-9999) during Arctic polar night (Nov 25 – Jan 15).
- **Operational Latency:** `Updated` metadata fields verify standard science L2 files are published 3 to 13 hours post-acquisition.
