# POLARIS STAGE 8 — OPUS PHASE 2: SMHI WEATHER RADAR INVESTIGATION

> [!IMPORTANT]
> **STATUS: INVESTIGATION COMPLETE — CLASS C/D CANDIDATE**
> Radar composite has 2024 data but faces severe physical limitations for SW_IN forecasting at Nuolja.

---

## 1. SMHI Radar API — Verified Product Structure

**Source:** Direct API queries to `https://opendata-download-radar.smhi.se/api/version/latest.json`
**Query date:** 2026-09-13

### Radar Areas Available
The SMHI radar open-data API exposes 13 areas:
`angelholm`, `atvidaberg`, `balsta`, `hemse`, `hudiksvall`, `karlskrona`, `kiruna`, `leksand`, `lulea`, `ornskoldsvik`, `ostersund`, `sweden`, `vara`

### Sweden-Wide Composite ("comp")

| Property | Verified Value | Source |
| :--- | :--- | :--- |
| Product key | `comp` | API: `.../area/sweden/product/comp.json` |
| Oldest data | 2008-10-01 (PNG format) | API `firstFiles` field |
| Current data | 2026-09-12 12:45 (H5 format) | API `firstFiles` field |
| 2024 archive | **CONFIRMED COMPLETE** — every day of Jan 2024 present, every month expected | API: `.../product/comp/2024/01` |
| Temporal cadence | **5-minute intervals** (00:00, 00:05, 00:10, ...) | File listing for 2024-01-15 |
| Publication latency | **~1 minute** (valid "2024-01-15 00:00" → updated "2024-01-15T00:01:05Z") | API timestamp comparison |
| File formats | PNG, TIF (GeoTIFF), H5 (HDF5 — only recent data) | API format keys |
| Coverage | Sweden-wide | Product name "sweden/comp" |

### Kiruna Individual Radar

| Property | Verified Value | Source |
| :--- | :--- | :--- |
| Product key | `qcvol` (quality-controlled volume) | API: `.../area/kiruna.json` |
| Current status | **ACTIVE** — updated 2026-09-13T12:49:49Z | API |
| 2024/01 archive | **EMPTY — 0 days** | API: `.../kiruna/product/qcvol/2024/01` returns `{"days":[]}` |
| 2024/06 archive | **EMPTY — 0 days** | API: `.../kiruna/product/qcvol/2024/06` returns `{"days":[]}` |
| **CONCLUSION** | **CLOSED — No 2024 historical data available** | |

### Luleå Individual Radar

| Property | Verified Value | Source |
| :--- | :--- | :--- |
| Product key | `qcvol` | API: `.../area/lulea.json` |
| Current status | **ACTIVE** — updated 2026-09-13T12:49:44Z | API |
| 2024/01 archive | **EMPTY — 0 days** | API: `.../lulea/product/qcvol/2024/01` returns `{"days":[]}` |
| **CONCLUSION** | **CLOSED — No 2024 historical data available** | |

---

## 2. Sweden Composite — Verified Characteristics

### What the composite product IS:
- A **2D precipitation radar reflectivity/rate composite** covering all of Sweden
- Updated every 5 minutes with ~1-minute publication latency
- Complete 2024 historical archive available via public API
- Available as GeoTIFF (TIF) and PNG images (older data), HDF5 for recent data

### What the composite product measures:
- **Radar reflectivity / precipitation rate** — this is a measure of **hydrometeor (rain/snow/ice) intensity**
- It does NOT directly measure clouds, cloud optical depth, or cloud radiative properties
- Weather radar operates at C-band (~5.6 GHz) which detects rain-sized droplets and ice crystals
- It primarily senses **precipitating hydrometeors**, not cloud droplets or cloud radiative state

---

## 3. Physical Analysis: Radar vs. SW_IN Relevance

### Critical Physical Distinction

| Property | Weather Radar | Cloud Optical Depth (SW_IN driver) |
| :--- | :--- | :--- |
| What it senses | Precipitating hydrometeors (>100μm) | All cloud droplets (1-20μm) |
| Physical process | Rayleigh/Mie backscatter at C-band | Solar radiation extinction |
| Sensitivity threshold | ~0.1 mm/h precipitation rate | Even thin cirrus affects SW_IN |
| Cloud type coverage | Only precipitating clouds | ALL clouds |
| Arctic relevance | Many overcast non-precipitating days | These non-precipitating clouds dominate SW_IN errors |

### Why Radar Information Has LIMITED SW_IN Relevance

1. **Most SW_IN-affecting clouds don't precipitate**: At Nuolja (68.35°N), many overcast days feature stratus or stratocumulus with optical depths >5 that dramatically reduce SW_IN, but produce little/no precipitation detectable by radar.

2. **Radar ≠ Cloud optical information**: A radar-clear sky can still have 8/8 cloud cover. A radar-active sky always has clouds, but the radar tells you about precipitation intensity, not cloud transmittance.

3. **Information content is asymmetric**:
   - Radar echo PRESENT → definitely cloudy + precipitating (optically thick) → some information
   - Radar echo ABSENT → could be clear OR could have extensive non-precipitating cloud cover → low information

4. **At Nuolja, the hard SW_IN cases are precisely the non-precipitating overcast periods** where radar adds no information beyond what MEPS cloud fraction already provides.

---

## 4. Spatial Coverage at Nuolja

### Nuolja Location
- Latitude: 68.35°N
- Longitude: 18.82°E
- Elevation: ~553 m (station), surrounding peaks to ~1100 m (Nuolja peak)

### Nearest SMHI Radars (ESTIMATE)
| Radar | Approximate Distance | Status |
| :--- | :--- | :--- |
| Kiruna | ~83 km (ESTIMATE from prior research) | Active but no 2024 data for individual product |
| Luleå | ~250 km (ESTIMATE) | Active but no 2024 data for individual product |

### Sweden Composite Coverage at 68.35°N
- The composite covers "Sweden-wide" but the **quality of radar composite data at Nuolja depends on which radars contribute**
- Kiruna radar (~83 km) is within C-band range (~250 km max, typically useful within ~150 km)
- At 83 km range: beam height at 0.5° elevation is approximately 1.5-2 km AGL — this means the radar sees above-ground level precipitation, not surface-level
- **Terrain blockage**: Nuolja is in mountainous terrain (Scandes). The Kiruna radar to the east must look OVER mountain ridges toward Abisko/Nuolja. Significant terrain blockage is EXPECTED but not verified.
- The composite may show "no data" or "ground clutter" at Nuolja if beam blockage is severe

### CRITICAL UNCERTAINTY: Whether the composite actually contains usable reflectivity data at the Nuolja grid pixel

This CANNOT be determined from the API metadata alone. It requires downloading a sample GeoTIFF file and examining the pixel value at 68.35°N, 18.82°E.

---

## 5. Causal Availability Assessment

| Criterion | Assessment | Confidence |
| :--- | :--- | :--- |
| Historical 2024 data exists | **YES** — complete archive confirmed | VERIFIED |
| 5-minute cadence | **YES** | VERIFIED |
| ~1 minute publication latency | **YES** — causal at t0 | VERIFIED |
| Available at every t0 | **LIKELY** — 288 files/day, every day | HIGH |
| Spatial coverage at Nuolja | **UNKNOWN** — terrain blockage concern | UNKNOWN |
| Physical relevance to SW_IN | **WEAK** — hydrometeors ≠ cloud optics | ASSESSED |
| Independence from Stage 8.1 | **PARTIAL** — radar is independent observation, but limited info content | ASSESSED |
| Information value vs. MEPS cloud_cover | **PROBABLY MARGINAL** — MEPS already has cloud fraction from assimilation (which includes radar) | INFERENCE |

---

## 6. The Assimilation Redundancy Problem

**CRITICAL CONSIDERATION**: MEPS/HARMONIE-AROME assimilates radar reflectivity data in its data assimilation system. This means that the radar information is ALREADY partially incorporated into the MEPS cloud and precipitation forecasts that Stage 8.1 uses.

The composite radar at t0 provides the raw observation, while MEPS provides the model's interpretation of that (and other) observations. The incremental value of adding raw radar on top of MEPS is:
1. **Timing precision**: Radar is 5-min real-time; MEPS forecast has temporal displacement errors
2. **Precipitation state at t0**: Binary "is it precipitating now?" — but this is a t0-only feature, not a forecast

However, the MEPS forecast itself already contains precipitation fields.

---

## 7. Final Classification

### Sweden Composite Radar: CLASS C — WEAK NOVELTY / MARGINAL INFORMATION VALUE

**Rationale:**
1. ✅ 2024 data exists and is complete
2. ✅ Causal availability is confirmed (~1 min latency)
3. ✅ Temporal resolution is excellent (5 min)
4. ❌ Physical measurement (hydrometeor reflectivity) is NOT the information gap identified in Stage 8.1
5. ❌ Information is partially redundant with MEPS (which assimilates radar)
6. ❓ Spatial coverage at Nuolja is UNKNOWN (terrain blockage risk)
7. ❌ The key SW_IN error mode (non-precipitating cloud timing/optical depth) is precisely what radar CANNOT observe
8. ❌ Radar echo is a weak/asymmetric proxy for cloud optical state

### Kiruna Individual Radar: CLASS D — OPERATIONALLY INFEASIBLE
- No 2024 historical archive in the public API
- CLOSED

### Luleå Individual Radar: CLASS D — OPERATIONALLY INFEASIBLE
- No 2024 historical archive in the public API
- Too far from Nuolja (~250 km)
- CLOSED

---

## 8. Remaining Questions

1. Does the Sweden composite GeoTIFF actually contain non-null radar data at the Nuolja pixel (68.35°N, 18.82°E)?
2. What fraction of 2024 daytime hours show radar echo at Nuolja?
3. Is there any residual information in "precipitation at t0" beyond what MEPS fc_cloud_cover already provides?

### Recommendation
The radar composite route does NOT merit a formal feasibility audit for POLARIS Stage 8 because:
- The physical quantity measured (hydrometeor reflectivity) is the WRONG information gap
- Stage 8.1's limitation is cloud optical depth information, not precipitation detection
- The data is partially assimilated into MEPS already
- A supervised experiment would likely show marginal or zero improvement

However, if all other routes close, a quick feasibility check (download one GeoTIFF, check pixel coverage) could be attempted with minimal cost.

---

*Investigation completed 2026-09-13. No experiments performed. No ODD access.*
