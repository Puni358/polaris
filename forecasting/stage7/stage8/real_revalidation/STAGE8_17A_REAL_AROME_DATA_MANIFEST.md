# POLARIS — Stage 8.17A Real AROME-Arctic 2024 Data Acquisition & Integration Manifest

**Timestamp:** 2026-09-13T14:28:18Z  
**Target Location:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**AROME Grid Cell:** `y = 209, x = 548` ($68.364774^\circ\text{N}, 18.715312^\circ\text{E}$, dist = $1.007\text{ km}$)  
**Final Status:** `AROME_REAL_DATA_READY = TRUE`

---

## 1. Executive Summary

Following the OPeNDAP `.ascii` point-subset feasibility confirmation, a comprehensive **Variable Semantics & LWP Construction Audit** was performed. Upon successful verification of liquid water path semantics and surface-aware pressure integration, bulk extraction of real historical **AROME-Arctic 2024** forecast data was executed across all **347 locked benchmark origins**.

- **Total Forecast Tuples Extracted:** 8,328 (347 origins $\times$ 24 horizon lead hours $H1 \dots H24$)
- **Data Coverage:** **100% (8,328 / 8,328)**
- **Synthetic / Missing / Substituted Values:** **0**
- **Causality Audit:** **100% PASS** ($t_{\text{init}} = \text{D-1 18:00 UTC}$, $t_0 = \text{D 00:00 UTC}$, $H = +6\text{h}$)
- **Canonical Dataset SHA256:** `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`

---

## 2. AROME Variable Semantics & LWP Integration Audit

### A. U700 & V700 Semantics Audit
- **U-Wind Variable:** `x_wind_pl` (pressure level index 8 = $700.0\text{ hPa}$, m/s)
- **V-Wind Variable:** `y_wind_pl` (pressure level index 8 = $700.0\text{ hPa}$, m/s)
- **Coordinate Order:** `[time][pressure][y][x]`
- **Audit Status:** **VERIFIED & PASSED**

### B. LWP Semantics & CF/GRIB Audit
- **Cloud Water Variable:** `mass_fraction_of_cloud_condensed_water_in_air_pl` ($q_l$)
- **CF Standard Name:** `mass_fraction_of_cloud_condensed_water_in_air`
- **Units:** $\text{kg/kg}$ (specific cloud liquid water mass fraction)
- **Phase Composition:** **Liquid Water Only** (Cloud ice is stored separately in `mass_fraction_of_cloud_ice_in_air_pl`).
- **Hydrostatic Integration Formula:**
  $$\text{LWP} = \int_{0}^{P_{\text{surface}}} q_l \frac{dp}{g} \quad \left[\text{kg/m}^2\right], \quad \text{LWP}_{g/m^2} = \text{LWP}_{\text{kg/m}^2} \times 1000$$
  where $g = 9.80665\text{ m/s}^2$.

### C. Surface-Aware Integration Truncation
- **Surface Air Pressure Variable:** `surface_air_pressure` ($P_{\text{surface}}$, Pa)
- **Nuolja Surface Pressure:** $\sim 90,860.61\text{ Pa}$ ($908.61\text{ hPa}$)
- **Pressure Level Breakdown (13 levels):**
  - **Included (Above Surface):** $50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850\text{ hPa}$
  - **Truncated Layer:** $850.0\text{ hPa} \to 908.61\text{ hPa}$ ($\text{effective } dp = 5,860.61\text{ Pa}$)
  - **Excluded (Below Surface):** $925.0\text{ hPa}$ and $1000.0\text{ hPa}$ ($\text{effective } dp = 0\text{ Pa}$)
- **Audit Status:** **VERIFIED & PASSED**

---

## 3. Representative Numerical Integration Check (2024-01-19 18Z, $H+20$)

| Layer | $p_{\text{top}}$ (hPa) | $p_{\text{bot}}$ (hPa) | Effective $dp$ (Pa) | Mean $q_l$ (kg/kg) | Layer LWP ($\text{g/m}^2$) | Integration Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0–6** | $50.0$ | $400.0$ | $35,000.0$ | $0.000000$ | $0.000000$ | Included ($q_l = 0$) |
| **6** | $400.0$ | $500.0$ | $10,000.0$ | $0.000000$ | $0.000000$ | Included ($q_l = 0$) |
| **7** | $500.0$ | $700.0$ | $20,000.0$ | $1.054 \times 10^{-6}$ | **2.150086** | Included |
| **8** | $700.0$ | $800.0$ | $10,000.0$ | $1.054 \times 10^{-6}$ | **1.075043** | Included |
| **9** | $800.0$ | $850.0$ | $5,000.0$ | $0.000000$ | $0.000000$ | Included ($q_l = 0$) |
| **10** | $850.0$ | $908.61$ | $5,860.61$ | $0.000000$ | $0.000000$ | **Truncated at $P_{\text{surface}}$** |
| **11** | $925.0$ | $1000.0$ | $0.00$ | $0.000000$ | $0.000000$ | **Excluded (Below Ground)** |
| **TOTAL** | $-$ | $-$ | $-$ | $-$ | **$3.225129\text{ g/m}^2$** | **Physically Plausible & Exact** |

---

## 4. Bulk Real Extraction Results across 347 Origins

```
======================================================================
BULK REAL AROME POINT EXTRACTION AUDIT
======================================================================
Total Target Benchmark Origins : 347
Successfully Extracted Origins : 347 / 347 (100.0%)
Failed Origins                 : 0
Forecast Horizons per Origin   : 24 (H1 to H24)
Total Forecast Tuples          : 8,328
Usable Tuples                  : 8,328
Coverage Ratio                 : 1.000000 (100.0%)
Synthetic / Missing / Padded   : 0
Causal Pass Count              : 8,328 / 8,328 (100.0%)
Extraction Elapsed Time        : 431.67 seconds (~7.2 minutes)
======================================================================
```

---

## 5. Artifact Provenance & SHA256 Checksums

| Artifact File | Description | Size | SHA256 Checksum |
| :--- | :--- | :---: | :--- |
| [`arome_arctic_347_origins_real_subset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/arome_arctic_347_origins_real_subset.csv) | Canonical 8,328-tuple real AROME dataset | $1.03\text{ MB}$ | `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298` |
| [`arome_arctic_nuolja_20240119T18Z_real_subset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/arome_arctic_nuolja_20240119T18Z_real_subset.csv) | Single origin test extraction CSV | $3.16\text{ KB}$ | `fdb42f63ebc37223774eba65c21dd0b9cef837ac16217b385eef8ff413a73d94` |
| [`STAGE8_17A_REAL_AROME_DATA_MANIFEST.json`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_17A_REAL_AROME_DATA_MANIFEST.json) | Structured JSON data manifest | $2.85\text{ KB}$ | $-$ |
| [`STAGE8_17A_REAL_AROME_DATA_MANIFEST.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_17A_REAL_AROME_DATA_MANIFEST.md) | Formatted Markdown data manifest | $4.20\text{ KB}$ | $-$ |

---

## 6. Final Protocol Compliance & Governance

- **Model Execution / Training / Evaluation:** **NONE** (0 models trained, 0 predictions evaluated).
- **Synthetic Data Usage:** **NONE** (100% real historical AROME-Arctic data).
- **Master Handoff & Route Registry:** **UNTOUCHED** (`POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY.*` remain unmodified).
- **Final Status:** **`AROME_REAL_DATA_READY = TRUE`**

```
STOP — REAL AROME DATA EXTRACTION & MANIFEST COMPLETE.
```
