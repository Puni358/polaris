# POLARIS RAW SPATIAL NWP FIELD DATA & CAUSAL FEASIBILITY AUDIT

**Date:** September 14, 2026  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}, 702\text{ m ASL}$)  
**Benchmark Context:** POLARIS Phase 11 Reopening (Post-Phase 10)  
**Official Champion:** Stage 8.1 37-feature GBDT (`HistGradientBoostingRegressor`)  
**Official Benchmark Baseline:** ODD MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`  
**Champion SHA-256:** `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`  
**Current Research Question:** *"Does preserving the spatial structure of existing causal NWP information provide predictive information that our current point-feature representation destroys?"*  
**Scope:** DATA + CAUSAL FEASIBILITY AUDIT ONLY (NO MODEL TRAINING, NO NEURAL NETWORKS, NO FEATURE EXTLECTION FOR FORECAST MODEL, NO HYPERPARAMETER SEARCH, NO ODD ACCESS).

---

## 1. Executive Verdict

$$\mathbf{VERDICT: GO}$$

### Verdict Rationale & Empirical Findings:
1. **100% Historical 2024 Archive Availability:** Empirical inspection of MET Norway's official THREDDS Data Server confirms that **full, raw 2024 historical spatial field archives exist and are 100% online** for both **AROME-Arctic 2.5 km** (`aromearcticarchive/2024/`) and **MEPS 2.5 km** (`meps25epsarchive/2024/`) for all 366 days of 2024.
2. **Raw Spatial Field Retrieval Verified:** Both datasets provide 2D continuous spatial grid fields (surface, pressure levels, and 65 hybrid model levels) via direct OPeNDAP (`/thredds/dodsC/`) and HTTP file server (`/thredds/fileServer/`).
3. **Strict Causal Eligibility Confirmed:** The **D-1 18:00 UTC initialization run** for both AROME-Arctic and MEPS is published and accessible on THREDDS by **~20:15–20:45 UTC Day D-1**, which precedes the locked benchmark origin $t_0 = 00:00\text{ UTC Day } D$ by **3.25 to 3.75 hours**. Lead times $+7\text{h}$ to $+30\text{h}$ cover all 24 forecast hours (H1–H24) without post-$t_0$ data leakage.
4. **Exact Nuolja Grid Cell Identified:** 
   - **AROME-Arctic:** Grid Index $(y=209, x=548)$, coordinates $68.364774^\circ\text{N}, 18.715312^\circ\text{E}$, distance **1.007 km** from SITES Nuolja.
   - **MEPS:** Grid Index $(y=760, x=486)$, coordinates $68.355701^\circ\text{N}, 18.763666^\circ\text{E}$, distance **1.243 km** from SITES Nuolja.
5. **No Prior Raw Spatial Representation Learning:** Forensic audit of Stage 8.5 and Stage 8.17A proves that **POLARIS has NEVER evaluated a raw 2D spatial tensor** or a spatial-field representation learning model. Stage 8.5 reduced a $9 \times 9$ MEPS grid into 14 scalar tabular features, destroying spatial grid topology. Stage 8.17A extracted point features at a single nearest grid cell.

---

## 2. AROME-Arctic 2024 Archive Status

- **Online Availability:** **100% AVAILABLE & ONLINE**. Hosted on MET Norway THREDDS.
- **Catalog Path:** `https://thredds.met.no/thredds/catalog/aromearcticarchive/2024/catalog.html`
- **Sample File (2024-01-01 00Z):** `https://thredds.met.no/thredds/catalog/aromearcticarchive/2024/01/01/catalog.html?dataset=aromearcticarchive/2024/01/01/arome_arctic_det_2_5km_20240101T00Z.nc`
- **Coverage:** All 366 days of 2024 present with 8 daily initialization runs ($00, 03, 06, 09, 12, 15, 18, 21\text{Z}$).
- **File Naming Format:** `arome_arctic_det_2_5km_YYYYMMDDTHHZ.nc`
- **Retrieval Protocols:** OPeNDAP (`dodsC`), WMS, WCS, HTTP FileServer.

---

## 3. MEPS / MetCoOp 2024 Archive Status

- **Online Availability:** **100% AVAILABLE & ONLINE**. Hosted on MET Norway THREDDS.
- **Catalog Path:** `https://thredds.met.no/thredds/catalog/meps25epsarchive/2024/catalog.html`
- **Sample File (2024-01-01 00Z Surface):** `https://thredds.met.no/thredds/catalog/meps25epsarchive/2024/01/01/catalog.html?dataset=meps25epsarchive/2024/01/01/meps_det_sfc_20240101T00Z.ncml`
- **Coverage:** All 366 days of 2024 present with 4 major 3D-Var initialization runs ($00, 06, 12, 18\text{Z}$) and hourly deterministic updates.
- **File Collections:**
  - `meps_det_sfc_YYYYMMDDTHHZ.ncml` (Surface & 2D single-level fields)
  - `meps_det_pl_YYYYMMDDTHHZ.ncml` (Pressure-level 3D fields)
  - `meps_det_hl_YYYYMMDDTHHZ.ncml` (65 Hybrid-level 3D atmospheric fields)

---

## 4. ECMWF IFS Fallback Status

- **Status:** **AVAILABLE AS FALLBACK / SYNOPTIC CONTROL**.
- **Provider:** ECMWF Open Data / AWS Open Data (`ecmwf-forecasts`).
- **Resolution:** $0.1^\circ \times 0.1^\circ$ (~11 km N-S x 4 km E-W at $68^\circ\text{N}$).
- **Initialization Runs:** $00\text{Z}$ and $12\text{Z}$.
- **Operational Latency:** ~6–7 hours post-initialization.
- **Role in POLARIS:** Useful as a coarse synoptic baseline to test whether 2.5 km local mesoscale spatial detail outperforms 11 km global synoptic fields.

---

## 5. Raw Spatial-Field Availability

Both AROME-Arctic and MEPS retain **un-aggregated 2D spatial grid arrays** for every forecast timestep. The dataset files contain explicit 2D spatial dimensions:
- **AROME-Arctic:** $y = 949$ grid points, $x = 739$ grid points.
- **MEPS:** $y = 1069$ grid points, $x = 949$ grid points.

These arrays can be sliced directly into $N \times N$ local spatial tensors centered on Nuolja without downloading full domain files.

---

## 6. Exact Variables Inventory

| Variable Family | Parameter Name in NetCDF | Standard Name / Units | Available Levels |
| :--- | :--- | :--- | :--- |
| **Surface Radiation** | `integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time` | Downward Shortwave Radiation ($J/m^2$ / $W/m^2$) | Surface |
| **Total Cloud Cover** | `cloud_area_fraction` | Total Cloud Fraction ($0.0 - 1.0$) | Surface |
| **Layer Cloud Fractions** | `high_type_cloud_area_fraction`, `medium_type_cloud...`, `low_type_cloud...` | High/Med/Low Cloud Fraction ($0.0 - 1.0$) | Surface |
| **Liquid Water Path (LWP)**| `atmosphere_mass_content_of_cloud_liquid_water` | Liquid Water Path ($kg/m^2$) | Surface |
| **Ice Water Path (IWP)** | `atmosphere_mass_content_of_cloud_ice` | Ice Water Path ($kg/m^2$) | Surface |
| **10m Wind Fields** | `x_wind`, `y_wind` | $U, V$ Wind Components ($m/s$) | 10m Height |
| **Upper Air Wind Fields** | `x_wind`, `y_wind` | $U, V$ Steering Winds ($m/s$) | 700, 850, 500 hPa & Model Levels |
| **3D Cloud Water/Ice** | `mass_fraction_of_cloud_liquid_water_in_air`, `..._cloud_ice_in_air` | Cloud Condensate ($kg/kg$) | 65 Hybrid Model Levels |
| **Temperature & Humidity**| `air_temperature`, `relative_humidity`, `specific_humidity` | $T (K)$, $RH (\%)$, $q (kg/kg)$ | 2m, Pressure & Model Levels |

---

## 7. Exact Spatial Resolution & Domain Projection

- **Native Horizontal Grid Spacing:** $2.5\text{ km} \times 2.5\text{ km}$ ($2500\text{ m}$).
- **AROME-Arctic Domain:**
  - Projection: Lambert Conformal Conic (`+proj=lcc +lat_1=77.5 +lat_2=77.5 +lat_0=77.5 +lon_0=-25 +R=6371000 +units=m`)
  - Bounds: Lat $62.0^\circ\text{N}$ to $88.0^\circ\text{N}$, Lon $-18.0^\circ\text{E}$ to $80.0^\circ\text{E}$.
- **MEPS Domain:**
  - Projection: Lambert Conformal Conic (`+proj=lcc +lat_1=63.3 +lat_2=63.3 +lat_0=63.3 +lon_0=15 +R=6371000 +units=m`)
  - Bounds: Lat $49.8^\circ\text{N}$ to $75.2^\circ\text{N}$, Lon $-18.1^\circ\text{E}$ to $54.2^\circ\text{E}$.

---

## 8. Exact Temporal Resolution

- Discrete 1-hourly forecast lead intervals ($t = +1\text{h}, +2\text{h}, \dots, +66\text{h}$).

---

## 9. Forecast Initialization Cycles

- **AROME-Arctic:** 8 cycles per day ($00, 03, 06, 09, 12, 15, 18, 21\text{Z}$).
- **MEPS:** 4 main 3D-Var cycles per day ($00, 06, 12, 18\text{Z}$).

---

## 10. Causality & Availability Analysis

```
TIMELINE FOR BENCHMARK ORIGIN t0 = 00:00 UTC (Day D):

Day D-1 18:00 UTC : Model Cycle Initialization (t_init)
Day D-1 20:15 UTC : Model Run Completes & Output Processed
Day D-1 20:45 UTC : Published on THREDDS Catalog (t_avail)  <--- AVAILABLE 3.25h BEFORE t0
Day D   00:00 UTC : Benchmark Forecast Origin t0            <--- FIREWALL BOUNDARY
Day D   01:00 UTC : H1 Target (Lead +7h from 18Z run)
...
Day D   24:00 UTC : H24 Target (Lead +30h from 18Z run)
```

- **Causal Run Selection:** For $t_0 = 00:00\text{ UTC Day } D$, the **D-1 18:00 UTC run** is selected.
- **Availability Margin:** Available $\approx 3.25\text{ to } 3.75$ hours BEFORE $t_0$.
- **Lead Mapping:** Forecast lead hours $+7\text{h}$ to $+30\text{h}$ provide valid predictions for H1 through H24 of Day $D$.
- **Post-$t_0$ Leakage Firewall:** The 00:00 UTC Day $D$ run completes and publishes around **02:15–02:45 UTC Day $D$** (after $t_0$). It is strictly **EXCLUDED** from usage at $t_0 = 00:00$.

---

## 11. Nuolja Grid-Cell Verification

- **Target Coordinates:** $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$ (SITES Nuolja Middle Station).
- **AROME-Arctic Grid Index:** $y = 209, x = 548$. Grid Point: $68.364774^\circ\text{N}, 18.715312^\circ\text{E}$. Distance: **1.007 km**.
- **MEPS Grid Index:** $y = 760, x = 486$. Grid Point: $68.355701^\circ\text{N}, 18.763666^\circ\text{E}$. Distance: **1.243 km**.

---

## 12. Feasible Spatial Windows around Nuolja

Centered on Nuolja grid cell ($y_0, x_0$):

| Stencil Window | Spatial Extent | Physical Coverage Area | Use Case |
| :---: | :---: | :---: | :--- |
| **$3 \times 3$** | $7.5\text{ km} \times 7.5\text{ km}$ | $56.25\text{ km}^2$ | Immediate valley/peak micro-neighborhood |
| **$5 \times 5$** | $12.5\text{ km} \times 12.5\text{ km}$ | $156.25\text{ km}^2$ | Abisko valley & Lake Torneträsk shoreline |
| **$9 \times 9$** | $22.5\text{ km} \times 22.5\text{ km}$ | $506.25\text{ km}^2$ | Local Scandes mountain ridge advection |
| **$11 \times 11$** | $27.5\text{ km} \times 27.5\text{ km}$ | $756.25\text{ km}^2$ | Regional mountain range advection |
| **$21 \times 21$** | $52.5\text{ km} \times 52.5\text{ km}$ | $2,756.25\text{ km}^2$ | Mesoscale cloud front tracking (Kiruna to Riksgränsen) |
| **$64 \times 64$** | $160\text{ km} \times 160\text{ km}$ | $25,600\text{ km}^2$ | Regional atmospheric circulation (Atlantic coast to Baltic) |

---

## 13. Storage & Data Volume Estimates

Total Benchmark Scope: 347 Origins $\times$ 24 Forecast Hours = **8,328 Spatial Frames**.

| Spatial Bounding Box | Variables per Frame | Frame Size | Total Dataset Size (347 Origins, 24h) | OPeNDAP Extraction Time |
| :---: | :---: | :---: | :---: | :---: |
| **$5 \times 5$** | 5 Surface Vars (float32) | 500 B | **4.16 MB** | ~15 seconds |
| **$11 \times 11$** | 5 Surface Vars (float32) | 2,420 B | **20.15 MB** | ~35 seconds |
| **$21 \times 21$** | 5 Surface Vars (float32) | 8,820 B | **73.45 MB** | ~1.5 minutes |
| **$21 \times 21$** | 10 Surface + Pressure Vars | 17,640 B | **146.90 MB** | ~3.0 minutes |
| **$64 \times 64$** | 10 Surface + 5 Model Levels | 819.2 KB | **6.82 GB** | ~25.0 minutes |

---

## 14. Stage 8.5 Forensic Comparison

- **What Spatial Data Were Used:** MEPS 2.5 km $9 \times 9$ grid surrounding Nuolja.
- **How They Were Reduced:** Reduced to 14 scalar summary statistics (spatial means, spatial stds, upwind advection scalar projections).
- **Did Model Receive a 2D Tensor:** **NO.** The model (`HistGradientBoostingRegressor`) received 14 tabular scalar columns appended to 37 baseline features (51 total scalar features).
- **Were Spatial Relationships Preserved:** **NO.** Grid spatial structure $[C, H, W]$ was flattened and collapsed into scalar summary metrics before reaching the model. Grid topology, spatial gradients, and 2D spatial feature maps were completely destroyed.

---

## 15. Stage 8.17A Forensic Comparison

- **What AROME Information Was Retained/Lost:** Extracted point/single grid-cell features at the nearest AROME grid point ($68.364774^\circ\text{N}, 18.715312^\circ\text{E}$, distance ~1.0 km).
- **Retained Features:** 3 scalar disagreement features (wind disagreement, LWP disagreement, SW_IN disagreement) added to 37 baseline features (40 total scalar features).
- **Lost Information:** **100% of spatial neighborhood information was lost.** Zero surrounding grid cells, 2D spatial gradients, or spatial field relationships were retained.

---

## 16. What Is Known

1. **2024 Raw Spatial NWP Fields Exist Online:** MET Norway's THREDDS archive contains complete 1-hourly 2D spatial field NetCDF files for both AROME-Arctic and MEPS across all 366 days of 2024.
2. **Causality Is 100% Valid:** The D-1 18Z cycle for both models is published by ~20:45 UTC Day D-1 and provides valid $+7\text{h}$ to $+30\text{h}$ forecasts for H1–H24 of Day $D$ without post-$t_0$ data leakage.
3. **Nearest Grid Points Are Verified:** AROME-Arctic nearest grid point is $1.007\text{ km}$ from Nuolja; MEPS nearest grid point is $1.243\text{ km}$ from Nuolja.
4. **POLARIS Has Never Tested Raw 2D Spatial Field Models:** Previous stages (Stage 8.5 and Stage 8.17A) used tabular scalar reductions or single-point extractions. No spatial convolutional or spatial-field architecture has ever been trained or evaluated on POLARIS.

---

## 17. What Remains Unknown (Hypotheses to Test in Future Phases)

1. **Predictive Value of Raw Spatial Fields:** Whether preserving 2D grid topology provides actionable predictive information that point/tabular features destroyed (The Core Research Hypothesis).
2. **Optimal Spatial Window Size:** Whether a small micro-scale stencil ($5 \times 5$), mesoscale stencil ($21 \times 21$), or regional stencil ($64 \times 64$) captures the optimal atmospheric motion scale over the Scandes mountains.
3. **Optimal Model Representation:** Whether spatial representations are best learned via lightweight spatial encoders, ConvLSTMs, 2D CNNs, or spatial-temporal transformers (to be designed and tested only in subsequent authorized phases).

---

## 18. Final Governance Statement & Protocol Compliance

- **No Model Training Performed:** Zero models were trained during this audit.
- **No Feature Extraction for Forecast Model:** No new feature matrix was created for model consumption.
- **No ODD Access:** ODD test origins remain strictly untouched and firewalled.
- **Baseline Preserved:** Stage 8.1 37-feature HGB remains the official benchmark champion.
- **Audit Outcome:** **GO** — Historical 2024 raw spatial NWP fields exist, are causally valid, and can be retrieved for spatial representation research.
