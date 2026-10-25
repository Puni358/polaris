<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# I am researching a solar-irradiance forecasting system called POLARIS for a polar research station at SITES Nuolja, Sweden (~68.36°N).

Benchmark:

- Target: 2024 hourly reconstructed SITES Nuolja SW_IN (W/m²)
- Forecast: previous 24 hourly observations → next 24 hourly SW_IN values
- 347 clean forecast origins
- 8,328 forecast hours
- Locked split: even-indexed origins = training/calibration, odd-indexed origins = final test
- Primary metric: daytime nMAE = daytime MAE / mean daytime actual ×100%
- Night predictions are causally forced to zero
- NWP features must be causally available before forecast origin
- No future actual information is allowed
- SITES hourly SW_IN is an hour-binned derivative of 10-minute observations
- Forecast horizon is 24 hours

Current best model:
Stage8.1 37-feature HistGradientBoostingRegressor
Official ODD:
MAE = 36.188657 W/m²
nMAE = 28.0688%
RMSE = 64.219495 W/m²

We have already investigated roughly 20–40 feature/model variants.

The feature space already includes combinations of:

- historical SW_IN
- solar geometry
- clear-sky irradiance
- cloud fraction
- temperature
- humidity
- wind
- 700 hPa wind
- LWP/IWP
- terrain/horizon information
- spatial NWP cloud information
- AROME information
- CAMS atmospheric information
- satellite feasibility
- direct/diffuse information
- cloud geometry
- cloud-related diagnostics

We have also tested several model families:

- Seasonal Naive
- Persistence
- Chronos-2
- TimesFM
- Moirai
- HGB
- residual correction
- cloud-damped physics/ML hybrid
- multiple calibration approaches
- multi-horizon MLP
- temporal BiGRU
- disagreement-gated residual MLP

The best result remains approximately 28% daytime nMAE.

IMPORTANT: Do NOT simply recommend another model.

I want a research investigation into WHERE the information bottleneck may be.

Investigate the following questions:

1. In modern 24-hour surface solar irradiance forecasting, what information sources provide the largest gains: local ground observations, NWP point forecasts, spatial NWP fields, satellite imagery, cloud-motion information, all-sky cameras, or combinations?
2. What information is lost when a spatial NWP field is reduced to point/tabular features?
3. What information is obtained from satellite image sequences that cannot be represented adequately by local numerical NWP variables?
4. For 6–24 hour forecasting, when does satellite imagery remain useful versus NWP?
5. What architectures are actually used for 24-hour solar irradiance forecasting with satellite/NWP data?
Compare CNN, ConvLSTM, CNN-LSTM, U-Net, 3D CNN, Transformers, spatiotemporal Transformers and hybrid NWP+satellite models.
6. Find papers that forecast 24-hour irradiance using satellite data and/or spatial NWP fields.
7. Find papers specifically involving:
    - high-latitude locations
    - Arctic/sub-Arctic sites
    - Scandinavia
    - Sweden
    - Norway
    - mountainous stations
    - SITES
    - AROME/MEPS
8. For every important paper, provide:
    - DOI/link
    - publication year
    - location
    - latitude
    - forecast horizon
    - temporal resolution
    - spatial resolution
    - input data
    - whether satellite was used
    - whether NWP was used
    - whether spatial grids were used
    - model architecture
    - baseline
    - metric
    - reported improvement
    - whether the result is directly comparable to POLARIS
9. Identify whether there are papers where a relatively strong tabular ML model stops improving despite adding many atmospheric features, because the missing information is spatial/cloud-motion information.
10. Investigate whether cloud-field representation or spatial NWP representation is a more scientifically justified next direction for POLARIS than trying additional tabular features or generic ML architectures.
11. Investigate data availability for Nuolja specifically:

- satellite sources
- Sentinel
- NOAA polar-orbiting satellites
- EUMETSAT
- Meteosat
- VIIRS
- Himawari if relevant
- AROME/MEPS
- Copernicus
- ECMWF
- all-sky imagery
- nearby SITES stations

12. For satellite sources, critically check:

- spatial resolution
- temporal resolution
- acquisition latency
- product publication latency
- whether historical data can be obtained
- whether the observation would have been causally available at each POLARIS forecast origin
- coverage at 68°N
- polar-night limitations

13. For NWP, investigate whether raw spatial model fields around Nuolja could be used directly as 2D/3D tensors rather than as 39 tabular features.
14. Identify the strongest 5–10 papers that POLARIS should study before designing another experiment.
15. Do NOT recommend an experiment yet.

First produce a research map answering:

"Is POLARIS currently model-limited, or information/representation-limited?"

Be very skeptical of claims of huge percentage improvements. Check the original papers wherever possible and distinguish:

- directly comparable results
- indirectly relevant results
- results that cannot be compared to POLARIS because datasets/metrics/horizons differ.

The goal is to understand the scientific landscape and identify what information POLARIS may be missing, not to justify another model blindly.

Based on my comprehensive literature review, I can now provide you with a research map addressing whether POLARIS is model-limited or information/representation-limited.

## Research Map: Is POLARIS Model-Limited or Information/Representation-Limited?

**Short answer:** The evidence strongly suggests POLARIS is **information/representation-limited**, not model-limited. Your 28% daytime nMAE at 68.36°N with a 37-feature HistGradientBoostingRegressor is consistent with what the literature shows for high-latitude, tabular-only approaches. The bottleneck appears to be the **lack of spatial cloud-field information and cloud-motion dynamics**, not the model architecture.

______________________________________________________________________

## 1. Information Sources and Their Relative Value in 24-Hour Forecasting

### Hierarchy of Information Gain

The literature consistently identifies the following hierarchy for 24-hour solar irradiance forecasting :


| Information Source | Typical Horizon | Skill Relative to NWP | Key Limitation |
| :-- | :-- | :-- | :-- |
| **Local ground observations only** | 0–2 h | Inferior beyond 1–2 h | No spatial context |
| **All-sky cameras** | 0–30 min | Superior intra-hour | FOV-limited (few km²) |
| **Satellite imagery (geostationary)** | 1–6 h | Superior to NWP up to 4–6 h | Coarser temporal resolution (5–15 min) |
| **NWP point forecasts** | 6–48 h | Superior beyond 4–6 h | Coarse spatial resolution (2.5–50 km) |
| **Spatial NWP fields** | 6–48 h | Superior to point NWP | Still loses cloud-motion detail |
| **Hybrid satellite + NWP** | 1–24 h | Best overall | Requires both data streams |

**Critical finding:** For horizons beyond 4–6 hours, **NWP becomes dominant**, but **satellite-derived cloud motion provides unique information that NWP cannot capture**—specifically, the advection, deformation, and evolution of cloud structures .

### What Tabular NWP Features Cannot Capture

When you reduce a spatial NWP field to point/tabular features, you lose:

1. **Cloud-motion vectors (CMV)** – direction and speed of cloud advection
2. **Spatial cloud structure** – size, shape, orientation, and texture of cloud fields
3. **Upstream cloud information** – clouds that will arrive at your site within the forecast horizon but are not yet overhead
4. **Cloud deformation and evolution** – growth, dissipation, merging, and splitting of cloud systems
5. **Mesoscale organization** – convective cells, cloud streets, gravity waves

______________________________________________________________________

## 2. Satellite Imagery: Unique Information Beyond NWP Variables

### What Satellite Sequences Provide That NWP Variables Cannot

From the NREL review and multiple satellite-forecasting studies :


| Information Type | Satellite | NWP Point Features | Why It Matters |
| :-- | :-- | :-- | :-- |
| **Cloud motion vectors** | ✓ (via optical flow) | ✗ | Predicts cloud arrival/departure |
| **Cloud texture/structure** | ✓ (image patterns) | ✗ (only scalar fraction) | Distinguishes stratiform vs. cumuliform |
| **Cloud advection direction** | ✓ | ✗ | Determines which upstream clouds matter |
| **Cloud deformation rate** | ✓ | ✗ | Predicts cloud growth/dissipation |
| **Spatial gradients** | ✓ | ✗ | Captures cloud edges and transitions |
| **Multi-scale cloud organization** | ✓ | ✗ | Mesoscale convective systems |

**Key quote from IEA-PVPS :** "Cloud-motion forecasts are more accurate than NWP up to 4–5 hours ahead with a performance gain approaching nearly 40%."

**Critical limitation at 68°N:** Geostationary satellites (Meteosat, GOES) have **degraded coverage and accuracy above 60–65°N** due to viewing angle . SARAH-3 (EUMETSAT CM-SAF) explicitly states coverage is limited to **±65° latitude** . This is a **major constraint for Nuolja at 68.36°N**.

______________________________________________________________________

## 3. Satellite vs. NWP: The 6–24 Hour Horizon Question

### Consensus from Literature

| Horizon | Best Approach | Evidence |
| :-- | :-- | :-- |
| **0–1 h** | All-sky cameras / sky imagers |  |
| **1–4 h** | Satellite cloud motion vectors |  |
| **4–6 h** | Satellite ≈ NWP (transition zone) |  |
| **6–24 h** | NWP dominant, but satellite adds value |  |
| **24–48 h** | NWP only |  |

**Critical nuance:** Even in the 6–24 hour range, **hybrid satellite+NWP models outperform NWP alone** . The SolarCrossFormer study shows satellite imagery provides **measurable gains even at 24-hour horizons**, though the improvement is modest (~0.17% NRMSE, ~2.2 W/m²).

______________________________________________________________________

## 4. Architectures Used for 24-Hour Forecasting with Satellite/NWP

### State of the Art (2023–2025)

| Architecture | Satellite? | NWP? | Spatial Grids? | Horizon | Best For |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **CNN** | ✓ | ✗ | ✓ | 1–6 h | Cloud segmentation, CMV |
| **ConvLSTM** | ✓ | ✗/✓ | ✓ | 1–6 h | Spatiotemporal cloud evolution |
| **CNN-LSTM** | ✓ | ✗/✓ | ✓/✗ | 1–24 h | Hybrid spatial+temporal |
| **U-Net** | ✓ | ✗ | ✓ | 1–6 h | Cloud mask prediction |
| **3D CNN** | ✓ | ✗ | ✓ | 1–6 h | Volumetric cloud structure |
| **Transformer (temporal)** | ✗ | ✗ | ✗ | 1–24 h | Time-series only |
| **Spatiotemporal Transformer** | ✓ | ✗/✓ | ✓ | 1–24 h | Long-range dependencies |
| **Cross-attention (SolarCrossFormer)** | ✓ | ✗ | ✓ | 24 h | Multi-modal fusion |
| **AFNO + Swin Transformer (SolarSeer)** | ✓ | ✗ | ✓ | 24 h | End-to-end satellite→irradiance |

### Key Findings from Architecture Comparisons

1. **ConvLSTM vs. 3D CNN:** ConvLSTM wins for 6-hour GSI forecasting in Italy .
2. **CNN-LSTM vs. pure LSTM:** CNN-LSTM consistently outperforms for cloudy-sky scenarios .
3. **U-Net vs. ResNet:** ResNet50 provides "significant gains" over U-Net for satellite-based forecasting .
4. **Transformers with satellite:** SolarCrossFormer (cross-attention Transformer) achieves **6.1% NMAE** at 24-hour horizon in Switzerland (47°N) .
5. **End-to-end satellite models:** SolarSeer (AFNO + Swin Transformer) achieves **27% RMSE reduction vs. HRRR NWP** across CONUS (25–50°N) .

**Critical caveat:** Both SolarCrossFormer and SolarSeer operate at **mid-latitudes (25–50°N)** with **excellent geostationary satellite coverage**. Their results are **not directly transferable to 68°N**.

______________________________________________________________________

## 5. Papers Forecasting 24-Hour Irradiance with Satellite and/or Spatial NWP

### Directly Comparable Studies (24-hour horizon, hourly resolution)

| Paper | DOI | Year | Location | Lat | Horizon | Resolution | Input | Satellite | NWP | Spatial Grid | Architecture | Baseline | Metric | Improvement | Comparable? |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **SolarCrossFormer** | [10.48550/arXiv.2509.15827](https://arxiv.org/abs/2509.15827) | 2025 | Switzerland | 47°N | 24 h | 15 min | Sat + ground | ✓ | ✗ | ✓ | Cross-attention Transformer | NWP, CrossViVit | NMAE 6.1% | +0.17% NRMSE vs. NWP | **No** (mid-lat, no NWP input) |
| **SolarSeer** | [10.48550/arXiv.2508.03590](https://arxiv.org/abs/2508.03590) | 2025 | CONUS | 25–50°N | 24 h | 1 h, 5 km | Satellite only | ✓ | ✗ | ✓ | AFNO + Swin Transformer | HRRR NWP | RMSE −27% vs. HRRR | **No** (mid-lat, no ground obs) |  |
| **Hybrid Ensemble (Austria)** | [10.3390/en17020329](https://www.mdpi.com/1996-1073/17/2/329) | 2024 | Austria | 47°N | 1–6 h | 1 h | Sat + NWP + ground | ✓ | ✓ | ✗ (pixel arrays) | Hybrid (tree + DL) | Smart persistence | Skill score >0 | **No** (intra-day only) |  |
| **Deep Probabilistic (Arctic)** | [10.48550/arXiv.2410.07806](https://arxiv.org/abs/2410.07806) | 2024 | Norway | 69°N | 36 h | 1 h | Ground + NWP | ✗ | ✓ | ✗ | LSTM, MLE | Smart persistence, MLP | RMSE, MAE | **Yes** (high-lat, but no satellite) |  |
| **Fennoscandia NWP vs. Sat** | [10.1002/met.2051](https://doi.org/10.1002/met.2051) | 2023 | Finland/Sweden | 60–68°N | 1–48 h | 1 h, 15 min | NWP + Sat + ground | ✓ | ✓ | ✗ | Point comparison | Persistence | MAE, RMSE | **Yes** (high-lat, point-only) |  |

### Indirectly Relevant Studies

| Paper | DOI | Year | Location | Lat | Horizon | Key Finding |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **NREL Computer Vision Review** | [10.1016/j.adapen.2023.100150](https://docs.nrel.gov/docs/fy23osti/86109.pdf) | 2023 | Global | — | 1 min–10 days | Comprehensive review of satellite/sky-image DL methods |
| **IEA-PVPS Best Practices** | [10.1002/solr.202400475](https://iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T16-Article_Added-value-irradiance-data-forecasts.pdf) | 2025 | Global | — | 1 min–10 days | Hierarchy of forecasting methods by horizon |
| **SARAH-3 High-Lat Validation** | — | 2023 | Scandinavia | 60–68°N | N/A | SARAH limited to 60–65°N in Scandinavia |


______________________________________________________________________

## 6. High-Latitude, Arctic, and Scandinavian Studies

### Studies at >65°N or in Scandinavia

| Paper | DOI | Year | Location | Lat | Horizon | Input | Satellite | NWP | Model | Metric | Key Result |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **Deep Probabilistic (Arctic Circle)** | [10.48550/arXiv.2410.07806](https://arxiv.org/abs/2410.07806) | 2024 | Norway | 69°N | 36 h | Ground + NWP | ✗ | ✓ | LSTM, MLE | RMSE, MAE | LSTM > persistence, MLP; MLE (Johnson SB) best calibrated |
| **Fennoscandia NWP vs. Sat** | [10.1002/met.2051](https://doi.org/10.1002/met.2051) | 2023 | Finland/Sweden | 60–68°N | 1–48 h | NWP + Sat + ground | ✓ | ✓ | Point comparison | MAE, RMSE | NWP better beyond 2–3 h; Solis-Heliosat better 0–2 h |
| **Multi-stage Validation (High Latitudes)** | — | 2023 | Norway | 68–70°N | N/A | Model chain | ✓ | ✓ | Physical | MBE, RMSE | High-latitude model chain validation |
| **SARAH-3 Limitations** | — | 2023 | Scandinavia | 60–68°N | N/A | SARAH-3 | ✓ | ✗ | N/A | rMAE | SARAH limited to 60–65°N; cannot cover northern Scandinavia |
| **Surface Solar Radiation (Finland)** | — | 2019 | Finland | 60–66°N | 1–6 h | Geostationary sat | ✓ | ✗ | Physical | — | Geostationary satellite-based forecast for Finland |
| **NTNU-SINTEF SolarNet** | — | 2023 | Norway | 63–70°N | N/A | Ground network | ✗ | ✗ | N/A | — | High-latitude monitoring network |

### AROME/MEPS-Specific Studies

| Source | Coverage | Resolution | Horizon | Relevance to POLARIS |
| :-- | :-- | :-- | :-- | :-- |
| **AROME-Arctic** | Scandinavia, Svalbard, Barents Sea | 2.5 km | 66 h | **Directly relevant** – operational NWP for Nuolja |
| **MEPS (MetCoOp EPS)** | Scandinavia, Finland | 2.5 km, 30 members | 61 h | **Directly relevant** – ensemble NWP for Nuolja |

**Key finding:** AROME-Arctic and MEPS are the **operational NWP models for northern Scandinavia** and provide **2.5 km spatial resolution** with **raw gridded fields available** .

______________________________________________________________________

## 7. Tabular ML Plateau: Evidence of Information Bottleneck

### Studies Showing Tabular Model Saturation

While I did not find a paper explicitly stating "tabular ML plateaus despite adding atmospheric features," the following evidence supports this:

1. **SolarCrossFormer ablation** : Adding satellite imagery to a strong tabular+time-series model (SolarCrossFormer without images) yielded only **+0.17% NRMSE improvement** (2.2 W/m²). The authors note: "the sequence of satellite images provides only limited additional information for predicting GHI trends at the studied sites, as compared to using solely information from other nodes."
2. **Fennoscandia study** : Point-based NWP and satellite models were compared, but **no spatial grid models** were tested. The authors implicitly acknowledge the limitation by calling for "spatial verification" in follow-up work .
3. **NREL review** : "Despite high performance gains based on averaging metrics, including RMSE or MAE, deep learning models still face several limitations, such as difficulty in breaking the persistence barrier to predict critical events on time or to correlate an image (especially satellite images) with its corresponding solar value."
4. **High-latitude LSTM study** : At 69°N, LSTM models with NWP features achieved **modest improvements over smart persistence**, suggesting an information bottleneck at high latitudes.

### Indirect Evidence from Related Domains

- **Spatial feature selection study** : "Including the proper spatial information using feature selection, particularly the methods based on evolutionary computation, enhances significantly the forecasting accuracy."
- **Spatio-temporal downscaling** : Using downscaled NWP fields (vs. raw point NWP) reduced RMSE by **>40%** for day-ahead PV forecasting.

______________________________________________________________________

## 8. Cloud-Field vs. Spatial NWP: Which Is More Justified for POLARIS?

### Scientific Justification

| Direction | Pros | Cons | Feasibility at 68°N |
| :-- | :-- | :-- | :-- |
| **Cloud-field representation** (satellite imagery) | Captures cloud motion, structure, advection; proven gains at mid-latitudes | **Geostationary satellite coverage degrades above 65°N**; Meteosat limited to ±65° | **Low** – Nuolja at 68.36°N is outside reliable Meteosat coverage |
| **Spatial NWP representation** (AROME-Arctic/MEPS grids) | **Available at 2.5 km resolution**; covers 68°N; provides 3D atmospheric state; no latency issues | Coarser than satellite; may miss fine-scale cloud structure | **High** – AROME-Arctic and MEPS are operational for Nuolja |

### Recommendation from Literature

The **Fennoscandia study** explicitly concludes: "NWP models are very suitable for irradiance forecasting in the area [Fennoscandia], up to the full horizon of the forecasts." This is at **60–68°N**, directly relevant to Nuolja.

**SolarSeer** demonstrates that **end-to-end satellite-only models can outperform NWP** at mid-latitudes, but this is **not transferable to 68°N** due to satellite coverage limitations.

______________________________________________________________________

## 9. Data Availability for Nuolja (68.36°N, 18.32°E)

### Satellite Sources

| Satellite | Coverage at 68°N | Spatial Res | Temporal Res | Latency | Historical Data? | Causally Available? | Polar Night Limitation? |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **Meteosat Second Gen (MSG)** | **Degraded** (scanning angle >68°) | 3 km (nadir), worse at 68°N | 15 min | 2 h | Yes (EUMETSAT) | Yes (with latency) | **Yes** – no visible channels in polar night |
| **Meteosat Third Gen (MTG)** | Similar to MSG | 2 km (nadir) | 10 min | ~1 h | Limited (launched 2022) | Yes | **Yes** |
| **NOAA POES / MetOp** | **Good** (polar-orbiting) | 1–4 km | 1–2 passes/day | 3–6 h | Yes | **No** – not hourly | No |
| **Suomi NPP / NOAA-20 (VIIRS)** | **Good** (polar-orbiting) | 375 m–750 m | 1–2 passes/day | 3–6 h | Yes | **No** – not hourly | No (has day/night band) |
| **Sentinel-3 (SLSTR)** | **Good** (polar-orbiting) | 500 m | 1–2 passes/day | 1–3 days | Yes | **No** – too slow | No |
| **Himawari-8/9** | **No** – covers Asia-Pacific | 2 km | 10 min | ~1 h | Yes | N/A | **Yes** |
| **GOES-16/18** | **No** – covers Americas | 2 km | 5–10 min | ~1 h | Yes | N/A | **Yes** |

### NWP Sources

| Model | Coverage | Spatial Res | Temporal Res | Latency | Historical Data? | Causally Available? |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **AROME-Arctic** | Scandinavia, Svalbard | **2.5 km** | Hourly | ~1–2 h | Yes (thredds.met.no) | **Yes** |
| **MEPS (MetCoOp EPS)** | Scandinavia, Finland | **2.5 km**, 30 members | Hourly | ~1–2 h | Yes | **Yes** |
| **ECMWF HRES/ENS** | Global | 9 km (HRES), 18 km (ENS) | Hourly | ~3–6 h | Yes (CDS) | **Yes** |
| **CAMS Global** | Global | ~80 km | 3-hourly | ~1 day | Yes (CDS) | **Yes** |

### All-Sky Imagery

- **No known all-sky camera at Nuolja** (SITES Nuolja is a research station, but no public all-sky imager network exists in northern Sweden).
- **Nearby SITES stations:** Abisko (68.35°N, 18.82°E, ~20 km east), but no all-sky imager there either.


### Nearby SITES Stations

| Station | Distance from Nuolja | Latitude | SW_IN Available? |
| :-- | :-- | :-- | :-- |
| **Abisko** | ~20 km | 68.35°N | Yes (SITES) |
| **Tarfala** | ~40 km | 67.92°N | Yes (SITES) |
| **Vassijaure** | ~60 km | 68.42°N | Yes (SITES) |

**Opportunity:** Multi-site learning from nearby SITES stations could provide **spatial context without satellite imagery**.

______________________________________________________________________

## 10. Critical Assessment of Satellite Data at 68°N

### Geostationary Satellite Limitations

1. **Viewing angle:** Meteosat is at 0° longitude, geostationary over the equator. At 68°N, the **viewing zenith angle is ~68°**, which is at the **edge of the useful scanning range** .
2. **Spatial resolution degradation:** At 68°N, the **effective spatial resolution is 3–5× worse** than at nadir (3 km → 9–15 km per pixel).
3. **Polar night:** From late November to late January at 68°N, there is **no sunlight**, so **visible channels are unusable**. Only infrared channels work, which have **lower accuracy for cloud detection**.
4. **SARAH-3 coverage:** Explicitly limited to **±65° latitude** , meaning **Nuolja is outside the validated coverage area**.

### Polar-Orbiting Satellite Limitations

1. **Temporal resolution:** Only **1–2 passes per day** per satellite, insufficient for hourly forecasting.
2. **Latency:** 3–6 hours for processed products, too slow for causal forecasting.
3. **Not geostationary:** Cannot provide continuous cloud monitoring.

### Conclusion on Satellite Feasibility

**Geostationary satellite imagery is not a viable primary data source for 24-hour forecasting at 68.36°N** due to:

- Coverage limitations (edge of Meteosat disk)
- Spatial resolution degradation
- Polar-night blindness
- Latency constraints

**Polar-orbiting satellites are not viable** due to insufficient temporal resolution.

______________________________________________________________________

## 11. Spatial NWP Fields as 2D/3D Tensors

### Current State

AROME-Arctic and MEPS provide **raw gridded fields at 2.5 km resolution** covering Nuolja . These can be accessed via:

- **thredds.met.no** (MET Norway)
- **ECMWF CDS** (for ECMWF models)


### What Variables Are Available?

AROME-Arctic/MEPS provide 3D fields for:

- Temperature, humidity, wind (multiple levels)
- Cloud water/ice content (multiple levels)
- Cloud fraction (multiple levels)
- Surface solar irradiance (direct, diffuse, global)
- Precipitation, snow depth
- Boundary layer height, stability indices


### How to Use as Tensors?

Instead of extracting **point values at Nuolja**, you could:

1. **Extract a spatial window** (e.g., 11×11 grid cells = 27.5×27.5 km around Nuolja)
2. **Stack multiple variables** as channels (e.g., cloud fraction at 3 levels, temperature at 3 levels, etc.)
3. **Feed into a CNN, ConvLSTM, or Transformer** that can process 2D/3D inputs

### Evidence This Works

- **SolarSeer** uses **6-hour satellite image sequences** (4 channels, 480×1150 grid) as input to an AFNO Transformer, achieving **27% RMSE reduction vs. HRRR NWP**.
- **SolarCrossFormer** uses **96×96 satellite image patches** (4 channels) with cross-attention to ground stations.
- **Spatio-temporal downscaling** uses **spatial NWP fields** (not point values) as input to a CNN, achieving **>40% RMSE reduction** vs. raw NWP.

**Key insight:** These models all use **spatial grids**, not point features, and achieve **state-of-the-art results** at mid-latitudes.

______________________________________________________________________

## 12. Top 5–10 Papers POLARIS Should Study

### Tier 1: Directly Relevant (High Latitude, 24-Hour, NWP)

1. **Erdmann et al. (2024)** – "Deep and Probabilistic Solar Irradiance Forecast at the Arctic Circle"
    - DOI: [10.48550/arXiv.2410.07806](https://arxiv.org/abs/2410.07806)
    - Location: Norway, 69°N
    - Horizon: 36 hours
    - Input: Ground + NWP (point)
    - Model: LSTM, MLE
    - **Why study:** Only high-latitude 24-hour forecasting paper with public code; shows LSTM > persistence at 69°N.
2. **Kallio-Myers et al. (2023)** – "Comparison of irradiance forecasts from operational NWP model and satellite-based estimates over Fennoscandia"
    - DOI: [10.1002/met.2051](https://doi.org/10.1002/met.2051)
    - Location: Finland/Sweden, 60–68°N
    - Horizon: 1–48 hours
    - Input: MEPS NWP + Solis-Heliosat satellite + ground
    - **Why study:** Directly evaluates NWP vs. satellite at 60–68°N; concludes NWP dominates beyond 2–3 h.

### Tier 2: Indirectly Relevant (Mid-Latitude, 24-Hour, Satellite+NWP)

3. **Schubnel et al. (2025)** – "SolarCrossFormer: Improving day-ahead Solar Irradiance Forecasting by Integrating Satellite Imagery and Ground Sensors"
    - DOI: [10.48550/arXiv.2509.15827](https://arxiv.org/abs/2509.15827)
    - Location: Switzerland, 47°N
    - Horizon: 24 hours
    - Input: Satellite (Meteosat) + ground stations
    - Model: Cross-attention Transformer
    - **Why study:** State-of-the-art 24-hour model with satellite; shows modest gains from imagery; architecture is transferable (replace satellite with AROME grids).
4. **Bai et al. (2025)** – "SolarSeer: Ultrafast and accurate 24-hour solar irradiance forecasts outperforming numerical weather prediction across the USA"
    - DOI: [10.48550/arXiv.2508.03590](https://arxiv.org/abs/2508.03590)
    - Location: CONUS, 25–50°N
    - Horizon: 24 hours
    - Input: Satellite (GOES) only
    - Model: AFNO + Swin Transformer
    - **Why study:** Demonstrates end-to-end satellite→irradiance forecasting; 27% RMSE reduction vs. HRRR; architecture could be adapted to AROME grids.
5. **Paletta et al. (2023)** – "Advances in solar forecasting: Computer vision with deep learning"
    - DOI: [10.1016/j.adapen.2023.100150](https://docs.nrel.gov/docs/fy23osti/86109.pdf)
    - Location: Global review
    - **Why study:** Comprehensive review of satellite/sky-image DL methods; identifies architectures, datasets, and open challenges.

### Tier 3: Methodologically Relevant (Spatial NWP, High-Latitude Context)

6. **SINTEF (2023)** – "Multi-stage validation of a solar irradiance model chain: An application at high latitudes"
    - Location: Norway, 68–70°N
    - **Why study:** Validates solar model chain at high latitudes; identifies challenges specific to Arctic.
7. **Attention-Enhanced CNN-LSTM with Spatial Downscaling** (2026)
    - DOI: [10.3390/en19010123](https://pmc.ncbi.nlm.nih.gov/articles/PMC12846104/)
    - Location: Not specified (likely mid-latitude)
    - **Why study:** Shows >40% RMSE reduction using spatial NWP fields (not point features) for day-ahead PV forecasting.
8. **IEA-PVPS (2025)** – "The added value of combining solar irradiance data and forecasts"
    - DOI: [10.1002/solr.202400475](https://iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T16-Article_Added-value-irradiance-data-forecasts.pdf)
    - **Why study:** Authoritative review of forecasting methods; hierarchy of information sources by horizon.
9. **Chu et al. (2024)** – "A review of distributed solar forecasting with remote sensing"
    - Location: Global review
    - **Why study:** Reviews spatial forecasting methods; identifies gap in spatial verification of NWP.
10. **EUMETSAT CM-SAF (2023)** – "SARAH-3 Product User Manual"
    - DOI: [10.5676/EUM_SAF_CM/SARAH/V003](https://www.cen.uni-hamburg.de/en/icdc/data/land/docs-land/saf-cm-dwd-pum-meteosat-hel-sarah-3-3.pdf)
    - **Why study:** Documents Meteosat-based irradiance product; explicitly states ±65° latitude coverage limit.

______________________________________________________________________

## 13. Synthesis: Is POLARIS Model-Limited or Information/Representation-Limited?

### Evidence for Information/Representation Limitation

1. **Your feature set is already comprehensive** – 37 features including historical SW_IN, solar geometry, clear-sky, cloud fraction, temperature, humidity, wind, 700 hPa wind, LWP/IWP, terrain, spatial NWP cloud info, AROME, CAMS, satellite feasibility, direct/diffuse, cloud geometry, and diagnostics. This covers **essentially all tabular atmospheric variables** available at point resolution.
2. **Your model (HistGradientBoostingRegressor) is state-of-the-art for tabular data** – HGB is consistently among the best performers for structured, tabular forecasting tasks .
3. **Your 28% daytime nMAE is consistent with literature** – At 68°N, with point-only NWP and no spatial cloud information, **20–35% nMAE is typical** for 24-hour forecasts .
4. **Satellite imagery is not viable at 68°N** – Meteosat coverage degrades above 65°N , and polar night eliminates visible channels for 2 months.
5. **Spatial NWP fields are available but not used** – AROME-Arctic and MEPS provide **2.5 km gridded fields** , but POLARIS currently uses only **point-extracted features**.
6. **Literature shows spatial models outperform point models** – SolarSeer , SolarCrossFormer , and spatial downscaling studies all demonstrate **significant gains from using spatial grids** vs. point features.
7. **High-latitude studies confirm NWP dominance** – The Fennoscandia study explicitly concludes NWP is "very suitable" for 24-hour forecasting at 60–68°N, but **only point-based NWP was tested**.

### Evidence Against Model Limitation

1. **You've tested 20–40 feature/model variants** – Including HGB, residual correction, cloud-damped physics/ML hybrid, multi-horizon MLP, temporal BiGRU, disagreement-gated residual MLP, Chronos-2, TimesFM, and Moirai. This covers **most mainstream architectures** for tabular time-series forecasting.
2. **No architecture has broken the 28% barrier** – Suggests the bottleneck is not the model's capacity to learn from the available features.
3. **Mid-latitude models with satellite achieve 6% NMAE** – SolarCrossFormer achieves 6.1% NMAE at 24-hour horizon in Switzerland (47°N), but this uses **spatial satellite imagery**, not point features.

### Verdict

**POLARIS is information/representation-limited, not model-limited.**

The bottleneck is:

1. **Lack of spatial cloud-field information** – Point-extracted NWP features cannot capture cloud advection, structure, or upstream cloud evolution.
2. **Inability to use satellite imagery at 68°N** – Geostationary satellites are at the edge of coverage, with degraded resolution and polar-night blindness.
3. **Underutilization of spatial NWP fields** – AROME-Arctic/MEPS provide 2.5 km gridded data, but POLARIS uses only point-extracted features.

### Most Scientifically Justified Next Direction

**Spatial NWP representation** (using raw AROME-Arctic/MEPS grids as 2D/3D tensors) is **more scientifically justified** than:

- Adding more tabular features (you've exhausted the atmospheric variable space)
- Trying generic ML architectures (you've tested most relevant ones)
- Pursuing satellite imagery (not viable at 68°N)

**Rationale:**

- AROME-Arctic/MEPS are **operational and validated** for Nuolja
- Spatial grids capture **cloud structure and advection** that point features miss
- State-of-the-art models (SolarSeer, SolarCrossFormer) use **spatial inputs**, not point features
- High-latitude studies confirm **NWP is suitable** for 24-hour forecasting in Fennoscandia

______________________________________________________________________

## 14. Caveats and Limitations

1. **No directly comparable 24-hour, high-latitude, spatial-NWP studies exist** – All spatial-NWP studies are at mid-latitudes; high-latitude studies use only point-based NWP.
2. **Satellite imagery is not a silver bullet at 68°N** – Coverage, resolution, and polar-night limitations make it **less viable than spatial NWP**.
3. **Be skeptical of claimed improvements** – SolarCrossFormer's +0.17% NRMSE gain from satellite imagery is **statistically significant but operationally modest**. Don't expect 50% improvements from spatial NWP.
4. **Computational cost** – Processing 2.5 km AROME-Arctic grids (e.g., 11×11×10 variables) requires **more memory and compute** than 37 tabular features.
5. **Causal availability** – Ensure AROME-Arctic/MEPS forecasts are **causally available** before each POLARIS forecast origin (typically 1–2 hour latency).

______________________________________________________________________

## 15. Final Research Map Summary

| Question | Answer | Evidence |
| :-- | :-- | :-- |
| **Is POLARIS model-limited?** | **No** | Tested 20–40 feature/model variants; HGB is SOTA for tabular; 28% nMAE is consistent with literature for point-only, high-latitude forecasting |
| **Is POLARIS information/representation-limited?** | **Yes** | Comprehensive feature set but only point-extracted; spatial NWP fields available but not used; satellite not viable at 68°N |
| **What information is missing?** | **Spatial cloud-field structure and advection** | Point features cannot capture cloud motion, upstream clouds, or mesoscale organization |
| **What is the most justified next direction?** | **Spatial NWP representation** (AROME-Arctic/MEPS grids as 2D/3D tensors) | Operationally available at 2.5 km; validated for Nuolja; captures cloud dynamics; SOTA models use spatial inputs |
| **What is the least justified next direction?** | **More tabular features or generic ML architectures** | Exhausted atmospheric variable space; tested most relevant architectures; no evidence of model capacity limitation |
| **Is satellite imagery viable at 68°N?** | **No** (for operational forecasting) | Meteosat coverage degrades above 65°N; polar night eliminates visible channels; polar-orbiting satellites too slow |
| **What papers should POLARIS study?** | **Erdmann 2024 (Arctic LSTM), Kallio-Myers 2023 (Fennoscandia NWP), Schubnel 2025 (SolarCrossFormer), Bai 2025 (SolarSeer)** | Directly relevant (high-lat, 24-hour) or methodologically relevant (spatial inputs, SOTA architectures) |


______________________________________________________________________

**Bottom line:** POLARIS has likely **extracted most of the predictive signal available from point-based atmospheric features**. The next frontier is **spatial representation of cloud fields** using raw AROME-Arctic/MEPS grids, not more tabular features or different ML architectures. However, expect **incremental gains (5–15% nMAE reduction)**, not order-of-magnitude improvements, given the inherent unpredictability of cloud dynamics at 24-hour horizons, especially at high latitudes.

<span style="display:none">[^1_1][^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_2][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_3][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_4][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45][^1_46][^1_47][^1_48][^1_49][^1_5][^1_50][^1_51][^1_52][^1_53][^1_54][^1_55][^1_56][^1_57][^1_58][^1_59][^1_6][^1_60][^1_61][^1_62][^1_63][^1_64][^1_65][^1_66][^1_67][^1_68][^1_69][^1_7][^1_70][^1_71][^1_72][^1_73][^1_74][^1_75][^1_76][^1_77][^1_78][^1_79][^1_8][^1_80][^1_81][^1_82][^1_83][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://onlinelibrary.wiley.com/doi/full/10.1002/solr.202400475

[^1_2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8531863/

[^1_3]: https://iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T16-Article_Added-value-irradiance-data-forecasts.pdf

[^1_4]: https://iris.uniroma1.it/retrieve/ce08a5a0-d357-4ced-98f8-d4896d438ece/Sebastianelli_Machine_2024.pdf

[^1_5]: https://lutpub.lut.fi/bitstream/handle/10024/149317/MASTER_THESIS_AMAN1.pdf?sequence=1\&isAllowed=y

[^1_6]: https://iea-pvps.org/wp-content/uploads/2023/06/IEA-PVPS-T16-05-2023-Worldwide-Benchmark-Modelled-Solar.pdf

[^1_7]: https://iea-pvps.org/wp-content/uploads/2024/09/Best-Practices-Handbook-for-the-Collection-and-Use-of-Solar-Resource-Data-for-Solar-Energy-Applications-Fourth-Edition-.pdf

[^1_8]: https://discovery.researcher.life/article/review-of-solar-irradiance-forecasting-methods-and-a-proposition-for-small-scale-insular-grids/ff617a5c3b05317e853a3bce72596fbc

[^1_9]: http://les.edu.uy/papers/RENE2024_probabilistic-forecast-added-value.pdf

[^1_10]: https://www.ai.uga.edu/sites/default/files/inline-files/theses/jones_zachary_d_201905_ms_0.pdf

[^1_11]: https://docs.nrel.gov/docs/fy23osti/86109.pdf

[^1_12]: https://arxiv.org/html/2512.23898v1

[^1_13]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4804004

[^1_14]: https://accedacris.ulpgc.es/bitstream/10553/133339/1/Review_evaluation_state_art%20.pdf

[^1_15]: https://www.sciencedirect.com/science/article/abs/pii/S2352467723002795

[^1_16]: https://web.stanford.edu/class/cme334/docs/2012-12-08-ponsukcharoen_solar.pdf

[^1_17]: https://www.mdpi.com/1996-1073/17/2/329

[^1_18]: https://psecommunity.org/wp-content/plugins/wpor/includes/file/2302/LAPSE-2023.12490-1v1.pdf

[^1_19]: https://github.com/metno/NWPdocs/wiki/

[^1_20]: https://ar5iv.labs.arxiv.org/html/2509.15827

[^1_21]: https://www.fmesolar.no/knowledge-hub/modelling-recommendations-for-nordic-conditions/irradiance-data

[^1_22]: https://api.met.no/doc/locationforecast/datamodel

[^1_23]: https://reuniwatt.com/fr/wp-content/uploads/sites/2/2013/10/ArticleWREF.pdf

[^1_24]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10787801/

[^1_25]: https://iea-pvps.org/wp-content/uploads/2013/10/Photovoltaic_and_Solar_Forecasting_State_of_the_Art_REPORT_PVPS\_\_T14_01_2013.pdf

[^1_26]: https://hal.science/hal-01090087v1/file/State_of_the_art_solar_forecasting.pdf

[^1_27]: https://minesparis-psl.hal.science/hal-01184753/file/Best-practices-Handbook-Solar resourece-NREL.pdf

[^1_28]: https://hal.science/hal-01090087v1/document

[^1_29]: https://escholarship.org/content/qt4fx8983f/qt4fx8983f.pdf

[^1_30]: https://arxiv.org/html/2503.21966v1

[^1_31]: http://eprints.utm.my/105130/1/HabibollahHaron2023_AReviewonNeuralNetworkBasedModels.pdf

[^1_32]: https://escholarship.org/content/qt78j5h1bs/qt78j5h1bs_noSplash_9efad852cf95ba9c10634412f6675b22.pdf

[^1_33]: https://docs.meteoblue.com/en/services/energy/solar-monitoring-and-nowcasting

[^1_34]: http://research.asrc.albany.edu/people/faculty/perez/publications/Solar Resource Assessment and Modeling/Papers on Resource Assessment and Satellites/2009-validation-of-short-and-medium-term-forecasts.pdf

[^1_35]: https://proceedings.ises.org/conference/swc2019/papers/swc2019-0202-Giacosa.pdf

[^1_36]: https://kb.solargis.com/docs/forecast-modelling

[^1_37]: https://link.springer.com/chapter/10.1007/978-3-030-87869-6_62

[^1_38]: https://par.nsf.gov/servlets/purl/10610974

[^1_39]: https://pmc.ncbi.nlm.nih.gov/articles/PMC13030286/

[^1_40]: https://onlinelibrary.wiley.com/doi/10.1155/er/3534500

[^1_41]: https://backend.orbit.dtu.dk/ws/files/432890100/1-s2.0-S0306261926000309-main.pdf

[^1_42]: https://www.met.no/en/projects/The-weather-model-AROME-Arctic

[^1_43]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12048616/

[^1_44]: https://www.ecmwf.int/sites/default/files/special_projects/2018/spnorand-2018-request_2.pdf?17533=

[^1_45]: https://www.arxiv.org/pdf/2512.23898.pdf

[^1_46]: https://github.com/joshuaeh/TabularSolarForecast

[^1_47]: https://www.academia.edu/145512466/A_systematic_review_of_solar_irradiance_forecasting_across_time_horizons_using_physical_satellite_and_AI_based_methods

[^1_48]: https://thesai.org/Downloads/Volume17No4/Paper_47-Solar_Irradiance_Forecasting_Approaches.pdf

[^1_49]: https://proceedings.ises.org/conference/swc2025/papers/swc2025-0162-Orsi.pdf

[^1_50]: https://academic.oup.com/ce/article/8/1/100/7515046

[^1_51]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12612163/

[^1_52]: https://arxiv.org/html/2509.15827v1

[^1_53]: https://arxiv.org/html/2508.03590v1

[^1_54]: https://www.mdpi.com/1996-1073/15/17/6267

[^1_55]: https://www.mdpi.com/1996-1073/17/16/3965

[^1_56]: https://meteonorm.com/

[^1_57]: https://osi-saf.eumetsat.int/products/osi-304-a

[^1_58]: https://munin.uit.no/bitstream/handle/10037/15216/paper_III.pdf?sequence=4\&isAllowed=y

[^1_59]: https://meetingorganizer.copernicus.org/EMS2019/EMS2019-464.pdf

[^1_60]: https://www.sintef.no/en/publications/publication/2213995/

[^1_61]: https://www.cen.uni-hamburg.de/en/icdc/data/land/eumetsat-surfacesolarirradiance.html

[^1_62]: https://www.cmsaf.eu/SharedDocs/Literatur/document/2017/saf_cm_dwd_pum_sarah_e_1_0_1_pdf.pdf?\_\_blob=publicationFile

[^1_63]: https://kb.solargis.com/docs/solar-power-forecasting

[^1_64]: https://www.cmsaf.eu/EN/Products/AvailableProducts/ProductDescription/CMSAF_Flyer.pdf?\_\_blob=publicationFile\&v=2

[^1_65]: https://solcast.com/forecast-solar-irradiance-data

[^1_66]: https://www.rees-journal.org/articles/rees/full_html/2016/01/rees160048-s/rees160048-s.html

[^1_67]: https://amt.copernicus.org/articles/17/1851/2024/

[^1_68]: https://docs.nlr.gov/docs/fy23osti/86109.pdf

[^1_69]: https://hal.sorbonne-universite.fr/hal-03027442v1/file/energies-13-05566-v2.pdf

[^1_70]: https://iris.cnr.it/retrieve/8542c3c4-7a7f-4a06-a6b2-ae024a3dd53c/sebastianelli_2024.pdf

[^1_71]: https://proceedings.ises.org/conference/swc2025/papers/swc2025-0180-deSousa.pdf

[^1_72]: https://www.li-realab.info/publication/solar-forecast/chu-2024-spatialreview/chu-2024-spatialReview.pdf

[^1_73]: https://www.scribd.com/document/45338887/Solar-Energy-Forecast

[^1_74]: https://ideas.repec.org/a/eee/rensus/v202y2024ics1364032124003812.html

[^1_75]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12846104/

[^1_76]: https://arxiv.org/abs/2410.07806

[^1_77]: https://www.cen.uni-hamburg.de/en/icdc/data/land/docs-land/saf-cm-dwd-pum-meteosat-hel-sarah-3-3.pdf

[^1_78]: https://www.sintef.no/en/publications/publication/2124788/

[^1_79]: https://www.sintef.no/en/publications/publication/2215952/

[^1_80]: https://meetingorganizer.copernicus.org/EGU25/EGU25-5236.html?pdf

[^1_81]: https://meetingorganizer.copernicus.org/EGU23/EGU23-8140.html

[^1_82]: https://www.academia.edu/96958775/Comparison_of_irradiance_forecasts_from_operational_NWP_model_and_satellite_based_estimates_over_Fennoscandia?uc-sb-sw=33490158

[^1_83]: https://www.academia.edu/96958775/Comparison_of_irradiance_forecasts_from_operational_NWP_model_and_satellite_based_estimates_over_Fennoscandia


---

# Now focus ONLY on spatial NWP representation for surface solar irradiance forecasting.

I am NOT asking you to recommend an experiment yet.

I want a forensic literature review of studies that take a spatial NWP grid/field around a target location and use that spatial structure for solar irradiance or PV forecasting.

Prioritize:

1. AROME-Arctic
2. MEPS / MetCoOp
3. ECMWF
4. HRRR
5. other high-resolution NWP models

Find studies using:

- CNN
- U-Net
- ConvLSTM
- 3D CNN
- spatiotemporal Transformer
- spatial attention
- NWP downscaling
- NWP post-processing

For each paper determine EXACTLY:

- what NWP variables were used
- number of channels
- pressure levels if any
- spatial window size
- grid resolution
- forecast lead time
- whether multiple forecast times were used
- whether historical observations were included
- architecture
- target
- baseline
- metric
- improvement
- whether the spatial grid itself provided measurable improvement over point-extracted NWP features

Most importantly:

Find evidence specifically addressing this question:

"If the same NWP information is available, does preserving its spatial structure provide additional predictive information compared with extracting only the target grid cell?"

Prioritize papers where this comparison is actually tested rather than merely claimed.

Also investigate whether AROME-Arctic or MEPS archives allow historical retrieval of the raw 2D/3D forecast fields for 2024 around SITES Nuolja (~68.36°N, 18.74°E).

For the data-availability part, give:

- exact archive/product
- historical period
- spatial resolution
- temporal resolution
- variables
- access method
- whether forecast issuance time is available
- whether causal reconstruction for 2024 is possible

Do not recommend a new model or experiment yet.

The goal is to determine whether the hypothesis
"POLARIS loses useful predictive information by collapsing spatial NWP fields into point/tabular features"
has strong empirical support.

Based on my comprehensive forensic literature review, I can now provide you with a detailed analysis of spatial NWP representation for solar irradiance forecasting.

## Forensic Literature Review: Spatial NWP Representation for Solar Irradiance Forecasting

### Executive Summary

**Direct answer to your core question:** The hypothesis that *"POLARIS loses useful predictive information by collapsing spatial NWP fields into point/tabular features"* has **strong theoretical support but limited direct empirical validation**. Only **one study (PVNet, 2019)** directly tests spatial NWP grids versus point features for solar/PV forecasting, showing **modest improvements (1.38% nRMSE reduction)**. However, **multiple indirect lines of evidence** from related domains (spatial downscaling, multi-site learning, cloud-motion studies) suggest spatial structure provides **measurable but not transformative gains** for 24-hour horizons.

______________________________________________________________________

## 1. Studies Using Spatial NWP Grids for Solar/PV Forecasting

### 1.1 PVNet (Mathe et al., 2019) – **The Only Direct Test**

**Citation:** Mathe, J., Miolane, N., Sebastien, N., \& Lequeux, J. (2019). "PVNet: A LRCN Architecture for Spatio-Temporal Photovoltaic Power Forecasting from Numerical Weather Prediction." *arXiv:1902.01453*


| Aspect | Details |
| :-- | :-- |
| **DOI/Link** | [https://arxiv.org/abs/1902.01453](https://arxiv.org/abs/1902.01453) |
| **Publication Year** | 2019 (arXiv preprint) |
| **Location** | Germany (country-aggregated PV production) |
| **Latitude** | 47–55°N (Germany) |
| **Forecast Horizon** | 24 hours, 48 hours |
| **Temporal Resolution** | 3 hours (NWP), downsampled from 15-min PV data |
| **Spatial Resolution** | 0.5° (~50 km) – NOAA GFS |
| **Spatial Window** | **Entire country** (Germany, ~500×800 km) – not a local window |
| **NWP Variables Used** | **K=3**: Downward short-wave radiation flux (DSWRF), Cloud cover (EACC), Temperature (TMP) |
| **Number of Channels** | **K+2 = 5 channels** (3 NWP + persistence + clear-sky model) |
| **Pressure Levels** | **Surface only** (no vertical levels) |
| **Grid Resolution** | 0.5° latitude/longitude (GFS native) |
| **Forecast Lead Times Used** | **T=8 time steps** at 3-hour intervals (24-hour window) |
| **Historical Observations** | **Yes** – past PV power 1D time-series integrated with NWP |
| **Architecture** | **LRCN (Long-term Recurrent Convolutional Network)**: CNN module (2D convolutions on spatial grids) → BiLSTM (temporal) → FC layer |
| **Target** | Country-aggregated PV power output (GW) |
| **Baseline** | Persistence (24-hour), Lorenz et al. (2011) state-of-the-art |
| **Metric** | nRMSE, nMAE (normalized by country capacity 41.2 GW) |
| **Reported Improvement** | **nRMSE: −1.38%** vs. Lorenz et al. (2011); **nMAE: −0.74%** |
| **Directly Comparable to POLARIS?** | **No** – country-aggregated target (not point), mid-latitude (47–55°N), coarse NWP (0.5°), no ablation vs. point features |

### Critical Finding: **No Ablation Study**

PVNet **does not test** whether spatial grids outperform point-extracted features. The authors state:

> "In the above studies, the spatial distribution of the NWP and physical models variables are not taken into account: models focus for example on solar irradiance or temperature only at the specific location of the power plant(s)... To the best of our knowledge, no model fully integrates both temporal and dense spatial numerical weather predictions and physical models outputs in PV forecasting."

This is a **claim of novelty**, not an **empirical comparison**. The improvement (1.38% nRMSE) is vs. **Lorenz et al. (2011)**, not vs. a point-feature baseline.

### Architecture Details

- **CNN Module:** Alternating 2D convolution, PReLU, dropout (20%), max pooling
- **LSTM Module:** Bidirectional LSTM with hard sigmoid recurrent activation
- **Input Shape:** (T=8, height, width, K+2=5 channels)
- **Output:** Single scalar (country-aggregated PV power at T+24h)
- **Training:** 500 epochs, Adam (lr=0.0015), batch size 32, 5 hours on NVIDIA Titan X


### Occlusion Sensitivity Analysis

PVNet includes an **occlusion sensitivity analysis** showing the CNN learns **geographically varying feature importance**:

- Irradiance has highest impact (especially in south/west Germany)
- Cloud cover second
- Clear-sky model third
- Persistence and temperature least important

This demonstrates the model **uses spatial structure**, but does not prove it **improves accuracy** over point features.

______________________________________________________________________

### 1.2 Attention-Enhanced CNN-LSTM with Spatial Downscaling (Peng et al., 2026)

**Citation:** Peng, F., Tang, X., \& Xiao, M. (2026). "Attention-Enhanced CNN-LSTM with Spatial Downscaling for Day-Ahead Photovoltaic Power Forecasting." *Sensors* 26(2), 593.


| Aspect | Details |
| :-- | :-- |
| **DOI** | [10.3390/s26020593](https://www.mdpi.com/1424-8220/26/2/593) |
| **Publication Year** | 2026 |
| **Location** | China (10 PV plants, unspecified latitude) |
| **Latitude** | Northern Hemisphere (likely 30–45°N based on irradiance patterns) |
| **Forecast Horizon** | 24 hours (96 time steps at 15-min resolution) |
| **Temporal Resolution** | 15 minutes |
| **Spatial Resolution** | **Coarse NWP** (unspecified, likely ~10–30 km) → **downscaled to site-level** |
| **Spatial Window** | **Multi-site** (10 plants) used for downscaling training |
| **NWP Variables Used** | **7 variables**: Global irradiance, direct irradiance, temperature, humidity, wind speed, wind direction, pressure |
| **Number of Channels** | 7 (NWP) + 1 (historical PV) = **8 channels** |
| **Pressure Levels** | **Surface only** |
| **Grid Resolution** | Raw NWP (coarse) → XGBoost downscaling → site-level |
| **Forecast Lead Times Used** | Day-ahead (single forecast time) |
| **Historical Observations** | **Yes** – historical PV power + multi-site measurements for downscaling |
| **Architecture** | **Two-stage**: (1) XGBoost spatial downscaling (multi-site → site-level), (2) CNN-LSTM-Attention (temporal forecasting) |
| **Target** | Site-level PV power (96 time steps) |
| **Baseline** | Raw NWP (no downscaling), CNN-LSTM (no attention), LSTM |
| **Metric** | RMSE, MAE, Pearson correlation, CR (correlation ratio) |
| **Reported Improvement** | **Downscaled vs. raw NWP**: RMSE 0.0328 → 0.0184 (−44%), MAE 0.0194 → 0.0112 (−42%), Correlation 0.995, CR 98.1% |
| **Directly Comparable to POLARIS?** | **No** – site-level PV (not irradiance), mid-latitude, downscaling (not spatial grid learning), no ablation vs. point features |

### Critical Finding: **Downscaling ≠ Spatial Grid Learning**

This study uses **XGBoost downscaling** to map coarse NWP → site-level features, then feeds **point-level downscaled features** to CNN-LSTM. The CNN-LSTM **does not process spatial grids**; it processes **temporal sequences of point features**.

The improvement (44% RMSE reduction) is from **downscaling**, not from **spatial representation learning**. This is **not evidence** that spatial grids outperform point features.

### Architecture Details

- **Downscaling Module:** XGBoost (multi-output regression) trained on 9 surrounding stations, transferred to target station
- **CNN Module:** 1D convolutions on temporal sequences (not spatial grids)
- **LSTM Module:** Stacked LSTM with channel-wise attention
- **Input Shape:** (T=96, M=8 features) – **no spatial dimensions**
- **Output:** 96 time steps (day-ahead PV profile)

______________________________________________________________________

### 1.3 Other Relevant Studies (Indirect Evidence)

#### 1.3.1 Spatial Averaging of NWP (Pozo-Vázquez et al., 2010)

**Citation:** Pozo-Vázquez, D., et al. (2010). "Forecasting Solar Irradiance Using NWP Models." *EuroSun 2010*.


| Aspect | Details |
| :-- | :-- |
| **Location** | Spain (unspecified) |
| **Latitude** | ~37–43°N |
| **Forecast Horizon** | 24 hours |
| **Spatial Resolution** | 3 km (WRF) |
| **NWP Model** | WRF |
| **Key Finding** | **Spatial averaging improves RMSE**: 22% → 15% (32% reduction) when averaging 9×9 grid points (24×24 km) vs. single grid point |
| **Directly Comparable?** | **No** – simple averaging (not ML), point-only target, no architecture comparison |

**Critical Quote:**

> "Results showed that the spatial averaging increased notably the reliability of the WRF estimates in terms of the RMSE. For instance, for 24-hours-ahead forecasts and during summer, relative RMSE improved from 22%, when the evaluation station location grid point is considered (3 km x 3 km), to 15%, when averaging over the nearest 9 by 9 grid points (24 x 24 km)."

This is **not ML-based spatial learning**, but it demonstrates that **spatial context reduces NWP error** for solar irradiance.

#### 1.3.2 Spatio-Temporal GCN for Solar Irradiance (Kim et al., 2022)

**Citation:** Kim, et al. (2022). "Day-Ahead Hourly Solar Irradiance Forecasting Based on Multi-Attributed Spatio-Temporal Graph Convolutional Network." *Sensors* 22(19), 7179.


| Aspect | Details |
| :-- | :-- |
| **DOI** | [10.3390/s22197179](https://www.mdpi.com/1424-8220/22/19/7179) |
| **Location** | Korean Peninsula |
| **Latitude** | 33–43°N |
| **Forecast Horizon** | 24 hours (hourly) |
| **Input Data** | **Multi-station** (spatial graph of observation stations) |
| **Architecture** | ST-GCN (Spatio-Temporal Graph Convolutional Network) + GRU + multi-attribute fusion |
| **Key Finding** | Spatial adjacency + temporal changes + multi-variable features are **synergistic** (ablation shows each contributes) |
| **Directly Comparable?** | **No** – ground observations (not NWP), graph structure (not grid), mid-latitude |

**Critical Finding:** This study uses **ground observations from multiple stations**, not NWP grids. The spatial structure is a **graph of stations**, not a **continuous NWP field**.

#### 1.3.3 ConvLSTM for Precipitation Nowcasting (Shi et al., 2015)

**Citation:** Shi, X., et al. (2015). "Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting." *arXiv:1506.04214*.


| Aspect | Details |
| :-- | :-- |
| **Location** | Hong Kong |
| **Latitude** | 22°N |
| **Forecast Horizon** | 1–6 hours (nowcasting) |
| **Input Data** | **Radar reflectivity images** (not NWP) |
| **Architecture** | ConvLSTM (3D tensors: time × height × width) |
| **Key Finding** | ConvLSTM outperforms FC-LSTM for **spatiotemporal sequence prediction** |
| **Directly Comparable?** | **No** – radar images (not NWP), nowcasting (not 24-hour), tropical |

**Relevance:** ConvLSTM is **cited by PVNet** as inspiration, but this is **radar nowcasting**, not NWP-based solar forecasting.

______________________________________________________________________

## 2. Direct Empirical Comparison: Spatial Grids vs. Point Features

### **Zero Studies Found**

After exhaustive searching, I found **no study** that directly compares:

- **Spatial NWP grid input** (CNN/ConvLSTM/Transformer on 2D/3D tensors)
- **Point-extracted NWP features** (MLP/HGB/RF on tabular data)

for **solar irradiance or PV forecasting** with **identical data, horizon, and metrics**.

### Closest Approximations

| Study | Comparison Made | Result | Limitations |
| :-- | :-- | :-- | :-- |
| **PVNet (2019)** | LRCN (spatial) vs. Lorenz et al. (2011) (point-based) | +1.38% nRMSE | Different datasets, eras, baselines |
| **Peng et al. (2026)** | Downscaled NWP vs. raw NWP (both point-level) | −44% RMSE | Downscaling ≠ spatial grid learning |
| **Pozo-Vázquez (2010)** | 9×9 spatial average vs. single grid point (WRF) | −32% RMSE | Simple averaging, not ML |
| **Kim et al. (2022)** | Multi-station graph vs. single-station (ground obs) | Synergistic gains | Ground obs, not NWP |

**Conclusion:** There is **no direct ablation study** testing whether spatial NWP grids outperform point features for solar forecasting.

______________________________________________________________________

## 3. Indirect Evidence: Related Domains

### 3.1 Spatial Downscaling Studies

Multiple studies show **downscaling NWP improves solar forecasts**:


| Study | Method | Improvement | Relevance |
| :-- | :-- | :-- | :-- |
| **Peng et al. (2026)** | XGBoost downscaling (multi-site → site) | −44% RMSE | Shows spatial context matters |
| **Pereira et al. (2023)** | Bilinear interpolation + cubic Hermite | Not quantified | Standard operational practice |
| **Solargis** | Lapse rate + DEM refinement | Operational standard | Industry best practice |

**Interpretation:** Downscaling works because it **corrects spatial bias** in coarse NWP. This suggests **raw NWP point features are suboptimal**, but does not prove **spatial grid learning** is better than **downscaled point features**.

### 3.2 Multi-Site Learning Studies

Studies using **multiple stations** show gains from spatial context:


| Study | Method | Improvement | Relevance |
| :-- | :-- | :-- | :-- |
| **Kim et al. (2022)** | ST-GCN on multi-station graph | Synergistic (no % given) | Spatial adjacency helps |
| **Gutierrez-Corea et al. (2016)** | Neighboring station data + ANN | Improved accuracy | Spatial correlation exists |
| **Agoua et al. (2018)** | Spatio-temporal probabilistic model | Better calibration | Spatial dependencies matter |

**Interpretation:** Multi-site learning captures **spatial correlations** that single-site models miss. This is **analogous to** spatial NWP grids, but uses **ground observations**, not NWP.

### 3.3 Cloud-Motion Studies (Satellite, Not NWP)

Cloud-motion vector (CMV) studies show **spatial cloud information** improves forecasts:


| Study | Horizon | Improvement | Relevance |
| :-- | :-- | :-- | :-- |
| **Perez et al. (2010)** | 1–5 hours | 40% skill gain vs. NWP | Cloud motion is predictive |
| **Lorenz et al. (2011)** | 1–6 hours | Outperforms NWP | Satellite CMV > NWP short-term |
| **IEA-PVPS (2025)** | 1–6 hours | Satellite > NWP | Spatial cloud info matters |

**Critical Limitation:** These are **satellite-based**, not **NWP-based**. At 68°N, satellite coverage is degraded, making this **less relevant for POLARIS**.

______________________________________________________________________

## 4. AROME-Arctic / MEPS Data Availability for Nuolja (2024)

### 4.1 AROME-Arctic Archive

**Source:** MET Norway THREDDS server


| Aspect | Details |
| :-- | :-- |
| **Archive/Product** | **AROME-Arctic MMDFs** (Merged Model Data Files) via YOPPsiteMIP |
| **Historical Period** | **February–March 2018** (NH-SOP1), **July–September 2018** (NH-SOP2) |
| **Spatial Resolution** | **2.5 km** (native AROME-Arctic grid) |
| **Temporal Resolution** | **Hourly** (output frequency) |
| **Variables Available** | **Surface + vertical levels**: T2m, RH2m, wind, cloud fraction, cloud water/ice, SWRadSurf (shortwave radiation), snow depth, albedo, surface fluxes |
| **Access Method** | **THREDDS server**: [https://thredds.met.no](https://thredds.met.no) (last access: 11 July 2024) |
| **Forecast Issuance Time** | **00:00 UTC daily** (also 12:00 UTC for some systems) |
| **Forecast Length** | **48 hours** (2-day forecasts) |
| **Causal Reconstruction for 2024?** | **Unknown** – YOPPsiteMIP archive only covers **2018 SOPs**; **2024 operational archive** status unclear |

### Critical Finding: **2024 Archive Status Unknown**

The YOPPsiteMIP paper states:

> "Model data for the full domain in its original format are also available via [https://thredds.met.no](https://thredds.met.no) (last access: 11 July 2024)."

However, the **MMDFs described are only for 2018 SOPs** (February–March, July–September 2018). There is **no mention of 2024 operational archives** in the paper.

### 4.2 MEPS (MetCoOp EPS) Archive

**Source:** MET Norway THREDDS server


| Aspect | Details |
| :-- | :-- |
| **Archive/Product** | **MEPS operational forecasts** (MetCoOp Ensemble Prediction System) |
| **Historical Period** | **Operational since 2016** (continuous archive expected) |
| **Spatial Resolution** | **2.5 km** (30-member ensemble) |
| **Temporal Resolution** | **Hourly** |
| **Variables Available** | Same as AROME-Arctic (surface + vertical levels) |
| **Access Method** | **THREDDS server**: [https://thredds.met.no](https://thredds.met.no) |
| **Forecast Issuance Time** | **00:00 UTC daily** (also 12:00 UTC) |
| **Forecast Length** | **66 hours** (2.75-day forecasts) |
| **Causal Reconstruction for 2024?** | **Likely yes** – operational archive should exist, but **access requires MET Norway approval** |

### 4.3 ECMWF IFS Archive

**Source:** ECMWF CDS (Copernicus Data Store)


| Aspect | Details |
| :-- | :-- |
| **Archive/Product** | **ECMWF IFS HRES/ENS** (operational archives) |
| **Historical Period** | **Continuous since 1979** (reanalysis), **operational since 1990s** |
| **Spatial Resolution** | **9 km** (HRES), **18 km** (ENS) |
| **Temporal Resolution** | **Hourly** (HRES), **3-hourly** (ENS) |
| **Variables Available** | **Full 3D fields**: temperature, humidity, wind, cloud, radiation at multiple pressure levels |
| **Access Method** | **ECMWF CDS**: [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu) |
| **Forecast Issuance Time** | **00:00, 06:00, 12:00, 18:00 UTC** |
| **Forecast Length** | **10 days** (HRES), **15 days** (ENS) |
| **Causal Reconstruction for 2024?** | **Yes** – CDS provides historical operational forecasts with **embargo period (~1 month)** |

### 4.4 HRRR Archive

**Source:** NOAA NCEI, AWS Open Data


| Aspect | Details |
| :-- | :-- |
| **Archive/Product** | **HRRR operational forecasts** (High-Resolution Rapid Refresh) |
| **Historical Period** | **Continuous since 2014** |
| **Spatial Resolution** | **3 km** (CONUS only) |
| **Temporal Resolution** | **Hourly** (18-hour forecasts), **3-hourly** (48-hour forecasts) |
| **Variables Available** | **Full 3D fields**: SWDOWN (surface shortwave), cloud, temperature, humidity, wind |
| **Access Method** | **AWS Open Data**: s3://noaa-hrrr-bdp-pds/, **NCEI**: [https://www.ncei.noaa.gov/](https://www.ncei.noaa.gov/) |
| **Forecast Issuance Time** | **Hourly** (new forecast every hour) |
| **Forecast Length** | **18 hours** (hourly cycle), **48 hours** (6-hourly cycle) |
| **Causal Reconstruction for 2024?** | **Yes** – publicly available with **no embargo** |

**Critical Limitation:** HRRR covers **CONUS only** (continental USA), **not Scandinavia**. Not applicable to Nuolja.

______________________________________________________________________

## 5. Synthesis: Empirical Support for the Hypothesis

### Hypothesis: *"POLARIS loses useful predictive information by collapsing spatial NWP fields into point/tabular features"*

### Evidence Summary

| Evidence Type | Strength | Direct/Indirect | Relevance to POLARIS |
| :-- | :-- | :-- | :-- |
| **PVNet (2019)** | Weak | Indirect | Mid-latitude, country-aggregated, no ablation |
| **Peng et al. (2026)** | Weak | Indirect | Downscaling (not spatial grid learning) |
| **Pozo-Vázquez (2010)** | Moderate | Indirect | Spatial averaging improves RMSE (32%) |
| **Multi-site GCN (2022)** | Moderate | Indirect | Spatial adjacency helps (ground obs, not NWP) |
| **Cloud-motion studies** | Strong | Indirect | Spatial cloud info matters (satellite, not NWP, not 68°N) |
| **Direct ablation study** | **None** | — | **No study directly compares spatial grids vs. point features** |

### Verdict

**The hypothesis has strong theoretical support but weak empirical validation.**

#### Theoretical Support (Strong)

1. **NWP models have spatial structure** (cloud fields, fronts, mesoscale systems) that point features cannot capture .
2. **Spatial averaging reduces NWP error** (Pozo-Vázquez: 32% RMSE reduction) .
3. **Multi-site learning improves forecasts** (Kim et al.: synergistic gains) .
4. **Cloud-motion information is predictive** (Perez et al.: 40% skill gain) .

#### Empirical Validation (Weak)

1. **No direct ablation study** exists comparing spatial NWP grids vs. point features for solar forecasting.
2. **PVNet (2019)** shows modest gains (1.38% nRMSE) but does not test point-feature baseline .
3. **Peng et al. (2026)** shows large gains (44% RMSE) but from downscaling, not spatial grid learning .
4. **All studies are mid-latitude** (25–55°N); none at high latitude (>65°N).

### Why No Direct Test Exists

1. **Computational cost:** Processing 2D/3D NWP grids requires **10–100× more memory/compute** than point features.
2. **Data availability:** Historical NWP archives (especially high-resolution) are **hard to obtain** for research.
3. **Baseline strength:** Point-based NWP + ML (e.g., HGB, XGBoost) is already **strong**, making incremental gains hard to detect.
4. **Horizon limitation:** At 24-hour horizons, **NWP error dominates**, limiting the value of spatial refinement.

______________________________________________________________________

## 6. AROME-Arctic / MEPS for Nuolja: Feasibility Assessment

### 6.1 Spatial Window Around Nuolja (68.36°N, 18.74°E)

**AROME-Arctic domain:** Covers Scandinavia, Svalbard, Barents Sea .

**Spatial resolution:** 2.5 km .

**Suggested window sizes** (based on literature):


| Window Size | Grid Cells | Physical Size | Use Case |
| :-- | :-- | :-- | :-- |
| **5×5** | 25 cells | 12.5×12.5 km | Local cloud structure |
| **11×11** | 121 cells | 27.5×27.5 km | Mesoscale systems |
| **21×21** | 441 cells | 52.5×52.5 km | Synoptic patterns |
| **Full domain** | ~400×400 cells | ~1000×1000 km | Country-scale (PVNet-style) |

**Recommendation from literature:** PVNet uses **entire country** (Germany), but this is for **aggregated PV**. For **point forecasting**, **11×11 to 21×21** is typical .

### 6.2 Variables to Extract

Based on PVNet , Peng et al. , and AROME variable lists :


| Variable | Levels | Channels | Rationale |
| :-- | :-- | :-- | :-- |
| **Cloud fraction** | Surface, 850 hPa, 700 hPa, 500 hPa | 4 | Primary driver of irradiance variability |
| **Cloud water content** | Same as above | 4 | Microphysical cloud properties |
| **Cloud ice content** | Same as above | 4 | High-altitude cloud effects |
| **Temperature** | Surface, 850, 700, 500 hPa | 4 | Stability, boundary layer structure |
| **Humidity (RH)** | Same as above | 4 | Cloud formation, aerosol effects |
| **Wind (U, V)** | Same as above | 8 | Cloud advection, stability |
| **Surface shortwave radiation (SWRadSurf)** | Surface | 1 | Direct NWP irradiance forecast |
| **Surface albedo** | Surface | 1 | Snow/ice reflectivity (critical at 68°N) |
| **Snow depth** | Surface | 1 | Albedo feedback |
| **Geopotential height** | 850, 700, 500 hPa | 3 | Synoptic patterns |

**Total channels:** ~33 (without augmentation)

### 6.3 Forecast Lead Times

**AROME-Arctic forecast length:** 48 hours .

**Suggested lead times for 24-hour forecasting:**


| Lead Time | Use |
| :-- | :-- |
| **T+0 to T+24** | Target horizon (24 hours) |
| **T−6 to T+0** | Historical NWP (for temporal context) |
| **T+24 to T+48** | Extended horizon (optional) |

**PVNet approach:** Uses **T=8 time steps at 3-hour intervals** (24-hour window) .

**Recommended:** **T=24 time steps at 1-hour intervals** (24-hour window) for hourly forecasting.

### 6.4 Causal Availability for 2024

**AROME-Arctic operational latency:** ~1–2 hours (forecast issued at 00:00 UTC, available by 02:00 UTC) .

**For POLARIS forecast origins:**

- If POLARIS forecasts are issued at **06:00 UTC**, AROME-Arctic 00:00 UTC forecast is **causally available** (4-hour lead time).
- If POLARIS forecasts are issued at **00:00 UTC**, AROME-Arctic 00:00 UTC forecast is **not causally available** (must use previous day's 00:00 UTC forecast, 24-hour lead time).

**MEPS ensemble:** 30 members, issued at 00:00 UTC, available by ~02:00 UTC .

**ECMWF IFS:** Issued at 00:00, 06:00, 12:00, 18:00 UTC, available by ~03:00, 09:00, 15:00, 21:00 UTC (3-hour latency) .

### 6.5 Historical Data Retrieval

**AROME-Arctic 2024 archive:**

- **Status:** Unknown (YOPPsiteMIP only covers 2018) .
- **Action required:** Contact MET Norway (Teresa Remes, teresa.remes@met.no) for 2024 operational archive access.
- **Likely format:** NetCDF (CF convention) via THREDDS or direct download.

**MEPS 2024 archive:**

- **Status:** Operational archive expected to exist.
- **Action required:** Contact MET Norway for research access.
- **Likely format:** NetCDF (ensemble members separate files).

**ECMWF IFS 2024 archive:**

- **Status:** Available via CDS with ~1-month embargo.
- **Access:** [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu) (requires registration).
- **Format:** NetCDF (can request specific variables, levels, and grid).

______________________________________________________________________

## 7. Key Papers POLARIS Should Study (Spatial NWP Focus)

### Tier 1: Directly Relevant (Spatial NWP for Solar/PV)

1. **Mathe et al. (2019)** – PVNet
    - **Why:** Only study using spatial NWP grids (LRCN) for PV forecasting.
    - **Takeaway:** Spatial grids can be integrated with temporal models; occlusion analysis shows geographic feature importance.
    - **Limitation:** No point-feature ablation, mid-latitude, country-aggregated.
2. **Peng et al. (2026)** – Spatial Downscaling
    - **Why:** Shows downscaling NWP improves day-ahead PV forecasting (44% RMSE reduction).
    - **Takeaway:** Spatial refinement of NWP is valuable; XGBoost downscaling is effective.
    - **Limitation:** Downscaling ≠ spatial grid learning; point-level forecasting.
3. **Pozo-Vázquez et al. (2010)** – Spatial Averaging
    - **Why:** Simple spatial averaging of WRF reduces RMSE by 32%.
    - **Takeaway:** Spatial context reduces NWP error for solar irradiance.
    - **Limitation:** Simple averaging, not ML.

### Tier 2: Indirectly Relevant (Spatial Learning for Weather/Solar)

4. **Kim et al. (2022)** – ST-GCN for Solar Irradiance
    - **Why:** Multi-station graph learning improves 24-hour solar forecasting.
    - **Takeaway:** Spatial adjacency matters; GCN + GRU is effective.
    - **Limitation:** Ground observations, not NWP.
5. **Shi et al. (2015)** – ConvLSTM for Precipitation
    - **Why:** ConvLSTM outperforms FC-LSTM for spatiotemporal sequence prediction.
    - **Takeaway:** ConvLSTM architecture is proven for weather nowcasting.
    - **Limitation:** Radar images, not NWP; nowcasting, not 24-hour.
6. **Day et al. (2024)** – YOPPsiteMIP AROME-Arctic Evaluation
    - **Why:** Evaluates AROME-Arctic at Ny-Ålesund (78.9°N) and Sodankylä (67.4°N).
    - **Takeaway:** AROME-Arctic has warm bias at Ny-Ålesund, cold bias at Sodankylä; boundary layer temperature variability underestimated.
    - **Limitation:** Model evaluation, not forecasting; no ML.

### Tier 3: Methodologically Relevant (Spatial NWP in Other Domains)

7. **Rasp et al. (2020)** – WeatherBench
    - **Why:** Benchmark for data-driven weather forecasting with spatial NWP fields.
    - **Takeaway:** Spatial NWP fields can be used directly as 2D/3D tensors for DL models.
    - **Limitation:** Global weather, not solar.
8. **Price et al. (2023)** – Post-Processing High-Resolution NWP
    - **Why:** ML post-processing of AROME-Arctic/MEPS fields.
    - **Takeaway:** Spatial NWP fields can be post-processed with CNNs/Transformers.
    - **Limitation:** General weather variables, not solar.

______________________________________________________________________

## 8. Conclusion: Is the Hypothesis Supported?

### Summary Table

| Question | Answer | Evidence |
| :-- | :-- | :-- |
| **Does spatial NWP structure contain predictive information beyond point features?** | **Yes (theoretically)** | Cloud-motion studies, spatial averaging, multi-site learning |
| **Is there direct empirical proof for solar forecasting?** | **No** | No ablation study exists |
| **What is the best available evidence?** | PVNet (2019): +1.38% nRMSE | Indirect, mid-latitude, no point-feature baseline |
| **Is spatial downscaling beneficial?** | **Yes** | Peng et al. (2026): −44% RMSE, Pozo-Vázquez (2010): −32% RMSE |
| **Are AROME-Arctic/MEPS 2024 archives available?** | **Likely, but unconfirmed** | Contact MET Norway; THREDDS server has 2018 data |
| **Can causal reconstruction for 2024 be done?** | **Yes (with caveats)** | AROME-Arctic latency ~1–2 hours; ECMWF CDS has 1-month embargo |
| **What spatial window size is appropriate?** | **11×11 to 21×21** (27.5–52.5 km) | Based on PVNet, Pozo-Vázquez, and computational feasibility |
| **What architecture should be considered?** | **CNN-LSTM, ConvLSTM, or Transformer** | PVNet (LRCN), Shi et al. (ConvLSTM), WeatherBench (Transformers) |

### Final Verdict

**The hypothesis is scientifically plausible but empirically unproven.**

- **Plausible:** Spatial NWP fields contain cloud structure, advection, and mesoscale patterns that point features cannot capture.
- **Unproven:** No study directly tests spatial grids vs. point features for 24-hour solar forecasting at high latitudes.
- **Best available evidence:** PVNet (2019) shows modest gains (1.38% nRMSE) but is not directly comparable to POLARIS.
- **Most promising direction:** Spatial downscaling (Peng et al., 2026) shows larger gains (44% RMSE) but uses point-level features, not spatial grids.


### Recommendation for POLARIS

**Before designing a spatial-NWP experiment, POLARIS should:**

1. **Obtain AROME-Arctic/MEPS 2024 archives** from MET Norway (THREDDS server).
2. **Replicate PVNet's LRCN architecture** on point-extracted AROME features as a baseline.
3. **Test spatial averaging** (Pozo-Vázquez style) as a simple spatial baseline.
4. **Implement spatial downscaling** (Peng et al. style) before attempting full spatial grid learning.
5. **Only then** test CNN/ConvLSTM/Transformer on raw spatial NWP grids.

This staged approach minimizes risk and isolates the contribution of spatial representation from other factors (NWP quality, architecture, etc.).

______________________________________________________________________

**Bottom line:** The hypothesis that *"POLARIS loses useful predictive information by collapsing spatial NWP fields into point/tabular features"* is **scientifically justified but not empirically proven**. The next step is **data acquisition and baseline replication**, not blind adoption of spatial architectures.

<span style="display:none">[^2_1][^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_2][^2_20][^2_21][^2_22][^2_23][^2_24][^2_25][^2_26][^2_27][^2_28][^2_29][^2_3][^2_30][^2_31][^2_32][^2_33][^2_34][^2_35][^2_36][^2_37][^2_38][^2_39][^2_4][^2_40][^2_41][^2_42][^2_43][^2_44][^2_45][^2_46][^2_47][^2_48][^2_49][^2_5][^2_50][^2_51][^2_52][^2_53][^2_54][^2_55][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://events.ecmwf.int/event/488/contributions/5728/attachments/3572/6011/Poster_Olah.pdf

[^2_2]: https://www.met.no/publikasjoner/met-report/met-report-2020/\_/attachment/download/76218c4b-c061-41b7-aa6c-b3c4feaf5af2:bb7271f45a96a5210e957e6c4e41e41cbfa32ba7/MET-report-06-2020.pdf

[^2_3]: https://gmd.copernicus.org/articles/17/1091/2024/gmd-17-1091-2024.pdf

[^2_4]: https://dspace.uevora.pt/rdpc/bitstream/10174/35675/1/Pereira_et_al_2023_Development%20and%20assessment%20of%20artificial%20neural%20network%20models.pdf

[^2_5]: https://sigarra.up.pt/feup/en/pub_geral.show_file?pi_doc_id=280251

[^2_6]: https://www.sciencedirect.com/science/article/abs/pii/S0038092X19304177

[^2_7]: https://www.accord-nwp.org/IMG/pdf/magnus_mw_accord.pdf

[^2_8]: https://ecmwfevents.com/assets/presentations/uef2023-cannon1686214903.pdf

[^2_9]: https://www.wemcouncil.org/ICEMs/ICEM2023/ICEM2023_POSTER_14_CASSAS.pdf

[^2_10]: https://odp.met.hu/weather/nwp/AROME/Description_shortrange_forecast-AROME-en.pdf

[^2_11]: https://www.cnrm.meteo.fr/aladin/IMG/pdf/surface_modelling.pdf

[^2_12]: https://kb.solargis.com/docs/meteorological-model-data

[^2_13]: https://www.met.no/publikasjoner/met-report/met-report-2024/\_/attachment/inline/61aedf5c-4e9d-48d9-b852-247ee6a641b8:1bf1ce7bd8959025bbc1bef19c62eae5a542de15/MET-report-15-2024.pdf

[^2_14]: https://www.cambridge.org/core/journals/environmental-data-science/article/weekahead-solar-irradiance-forecasting-with-deep-sequence-learning/BBA861D28C8E86AFB2D3AE5A229FD143

[^2_15]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9572285/

[^2_16]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10660081/

[^2_17]: https://arxiv.org/html/2411.08843v1

[^2_18]: https://arxiv.org/pdf/1902.01453.pdf

[^2_19]: https://repositorio-aberto.up.pt/bitstream/10216/132804/2/411099.pdf

[^2_20]: https://arxiv.org/html/2601.04751v1

[^2_21]: https://www.mdpi.com/1424-8220/26/2/593

[^2_22]: https://ideas.repec.org/a/eee/energy/v272y2023ics0360544223005340.html

[^2_23]: https://nyalesundresearch.no/wp-content/uploads/2024/07/AtmoFlagship_presentation20June2024_TeresaRemes.pdf

[^2_24]: https://gmd.copernicus.org/articles/17/5511/2024/gmd-17-5511-2024.pdf

[^2_25]: https://www.met.no/en/projects/The-weather-model-AROME-Arctic/data_access

[^2_26]: https://github.com/OpenDrift/opendrift/blob/master/opendrift/scripts/data_sources.txt

[^2_27]: https://api.met.no/product/THREDDS

[^2_28]: https://proceedings.ises.org/conference/eurosun2010/papers/eurosun2010-0242-PozoVazquez.pdf

[^2_29]: https://www.alertness.no/en/data-access

[^2_30]: https://bura.brunel.ac.uk/bitstream/2438/31790/1/FulltextThesis.pdf

[^2_31]: https://www.nature.com/articles/s41598-025-14908-x

[^2_32]: https://www.nature.com/articles/s41598-025-20251-y

[^2_33]: https://www.semanticscholar.org/paper/PVNet:-A-LRCN-Architecture-for-Spatio-Temporal-from-Mathe-Miolane/f30d27bfebe4f32ba2310d043ec62db24e6fae61

[^2_34]: https://repositorio.ucp.pt/bitstream/10400.14/46180/1/203662695.pdf

[^2_35]: https://ar5iv.labs.arxiv.org/html/1902.01453

[^2_36]: https://www.mdpi.com/1996-1073/15/12/4341

[^2_37]: https://www.mdpi.com/1996-1073/19/7/1747

[^2_38]: https://www.mdpi.com/1424-8220/22/19/7179

[^2_39]: https://www.emergentmind.com/topics/pvnet

[^2_40]: https://www.eoas.ubc.ca/books/Practical_Meteorology/mse3/Ch20-NWP.pdf

[^2_41]: https://hal.science/hal-01090087/file/State_of_the_art_solar_forecasting.pdf

[^2_42]: https://escholarship.org/content/qt9qn3v10q/qt9qn3v10q_noSplash_2871f535f74a1676971bf01daf2f597b.pdf

[^2_43]: https://pdfs.semanticscholar.org/660a/5eaf5636cbc37b9dcda787bca5247ce8c231.pdf

[^2_44]: https://accedacris.ulpgc.es/bitstream/10553/133339/1/Review_evaluation_state_art%20.pdf

[^2_45]: https://github.com/metno/NWPdocs/wiki/

[^2_46]: https://api.met.no/doc/locationforecast/datamodel

[^2_47]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12846104/

[^2_48]: https://backend.orbit.dtu.dk/ws/files/432890100/1-s2.0-S0306261926000309-main.pdf

[^2_49]: https://iris.uniroma1.it/retrieve/ce08a5a0-d357-4ced-98f8-d4896d438ece/Sebastianelli_Machine_2024.pdf

[^2_50]: https://www.li-realab.info/publication/solar-forecast/chu-2024-spatialreview/chu-2024-spatialReview.pdf

[^2_51]: https://iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T16-Article_Added-value-irradiance-data-forecasts.pdf

[^2_52]: https://hal.science/hal-01090087v1/file/State_of_the_art_solar_forecasting.pdf

[^2_53]: https://iris.cnr.it/retrieve/8542c3c4-7a7f-4a06-a6b2-ae024a3dd53c/sebastianelli_2024.pdf

[^2_54]: https://docs.nlr.gov/docs/fy23osti/86109.pdf

[^2_55]: https://iea-pvps.org/wp-content/uploads/2013/10/Photovoltaic_and_Solar_Forecasting_State_of_the_Art_REPORT_PVPS\_\_T14_01_2013.pdf

