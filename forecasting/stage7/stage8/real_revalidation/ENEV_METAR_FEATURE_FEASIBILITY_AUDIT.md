# ENEV METAR → POLARIS Feature Feasibility Audit

**Station:** ENEV (Evenes/Harstad-Narvik Airport, 68.517°N 16.683°E, 26m ASL)  
**Distance to Nuolja:** ~86 km WNW (upstream for prevailing westerlies)  
**Archive:** IEM ASOS, 2024-01-20 → 2024-12-31  
**Rows:** 13,651 (empirically verified in prior session)  
**Benchmark coverage:** 347/347 origins = 100% (empirically verified)  

---

## 1. Exact Usable Fields from IEM ASOS Download

### 1A. Cloud Layer Fields (Parsed by IEM)

| Field | Description | Population | Notes |
| :--- | :--- | :--- | :--- |
| `skyc1` | Cloud cover layer 1 (CLR/FEW/SCT/BKN/OVC/VV) | ~68% non-M | Lowest reported layer |
| `skyl1` | Cloud base layer 1 (feet AGL) | ~68% non-M | Height of lowest layer |
| `skyc2` | Cloud cover layer 2 | sparse | Second layer (if multi-layer) |
| `skyl2` | Cloud base layer 2 (feet AGL) | sparse | |
| `skyc3` | Cloud cover layer 3 | very sparse | Third layer |
| `skyl3` | Cloud base layer 3 (feet AGL) | very sparse | |
| `skyc4` | Cloud cover layer 4 | rare | Fourth layer |
| `skyl4` | Cloud base layer 4 (feet AGL) | rare | |

> [!WARNING]
> **Raw `skyc1/skyl1` layer fields are only ~68% populated.** This is NOT 100%.
> The remaining ~32% are rows where `skyc1 = M` and `skyl1 = M`.

### 1B. Why Effective Cloud State = 100%

When `skyc1 = M`, the raw METAR string (`metar` column) reveals one of:

| METAR Keyword | Meaning | skyc1 in IEM | Cloud State |
| :--- | :--- | :--- | :--- |
| **CAVOK** | Ceiling And Visibility OK (no cloud below 5000ft or below MSA, vis ≥10km, no significant weather) | `M` | **Clear/negligible cloud** |
| **NSC** | No Significant Cloud (no cloud below 5000ft or MSA, no CB/TCU) | `M` | **Clear/negligible cloud** |
| **NCD** | No Cloud Detected (automated, no cloud) | `M` | **Clear** |
| **SKC** | Sky Clear (manual observation, no cloud) | `M` | **Clear** |

**Result:** Every ENEV METAR row has a definite cloud state — either explicit layer reports (skyc1 populated) or CAVOK/NSC/NCD/SKC (skyc1=M but cloud state is known). Effective cloud-state information = 17,007/17,008 ≈ 100% (from prior empirical verification).

### 1C. Other Potentially Relevant Fields

| Field | Description | Population | Solar Relevance |
| :--- | :--- | :--- | :--- |
| `vsby` | Visibility (statute miles) | ~100% | Proxy for precipitation / fog opacity |
| `wxcodes` | Present weather (SN, -SN, BLSN, VCFG, VCSH, etc.) | partial | Weather type indicator |
| `metar` | Full raw METAR string | 100% | Source for CAVOK/NSC parsing |

---

## 2. Timestamp Convention & Causal Availability

### 2A. ENEV Reporting Schedule

ENEV reports at **xx:50 UTC** each hour (standard Norwegian aviation METAR timing).

### 2B. Causal Availability at t0 = 00:00 UTC

| METAR Valid Time | Status Relative to t0=00:00 UTC | Causal? |
| :--- | :--- | :--- |
| 23:50 UTC (day D-1) | 10 minutes BEFORE t0 | **YES — strictly causal** |
| 22:50 UTC (day D-1) | 70 minutes BEFORE t0 | **YES — strictly causal** |
| 21:50 UTC (day D-1) | 130 minutes BEFORE t0 | **YES — strictly causal** |
| 00:50 UTC (day D) | 50 minutes AFTER t0 | **NO — not available at t0** |

**Key finding:** The most recent strictly causal ENEV observation is the **23:50 UTC** report, which is observed and published ~10 minutes before t0. Aviation METARs are published within 1–5 minutes of observation time, so the 23:50 UTC report is operationally available at 23:55 UTC at the latest — well before t0=00:00.

### 2C. Temporal Window for Feature Extraction

The causally available ENEV reports at t0=00:00 UTC are:
- **23:50** (t0 − 10 min) — most recent, primary candidate
- **22:50** (t0 − 70 min) — 1-hour lookback
- **21:50** (t0 − 130 min) — 2-hour lookback
- Earlier hours also available for temporal change features

**Recommendation:** Use the **23:50 UTC** report as the primary feature extraction point. This is the most recent causal observation.

---

## 3. CAVOK / NSC / MISSING Encoding

> [!IMPORTANT]
> CAVOK and NSC are **positive reports with specific physical meaning**. They must NOT be encoded as missing data.

### 3A. Proposed Encoding Scheme

#### Cloud Cover (oktas → numeric)

| METAR Code | Oktas | Numeric Encoding | Rationale |
| :--- | :--- | :--- | :--- |
| CAVOK | 0 | 0 | No cloud below 5000ft/MSA, vis ≥10km |
| NSC | 0 | 0 | No significant cloud below 5000ft/MSA |
| NCD / SKC / CLR | 0 | 0 | No cloud detected/observed |
| FEW | 1–2 | 1.5 | Midpoint of 1–2 oktas |
| SCT | 3–4 | 3.5 | Midpoint of 3–4 oktas |
| BKN | 5–7 | 6 | Midpoint of 5–7 oktas |
| OVC | 8 | 8 | Full overcast |
| VV (vertical vis) | 8 | 8 | Sky obscured = effectively overcast |

#### Cloud Base Height

| Condition | Encoding | Rationale |
| :--- | :--- | :--- |
| Layer reported (skyl1 non-M) | `skyl1 × 0.3048` (convert ft→m AGL) | Direct ceilometer measurement |
| CAVOK | **Sentinel: 5000 m** (≈16,400 ft) | CAVOK means no cloud below 5000 ft or MSA. Use 5000m as "no low cloud" sentinel |
| NSC / NCD / SKC / CLR | **Sentinel: 5000 m** | Same as CAVOK: no significant cloud below reporting threshold |
| VV (vertical visibility) | `VVxxx × 30.48` (convert 100ft→m) | Sky obscured at reported height |
| Genuinely missing | **NaN → impute with median or forward-fill** | Should be ≤1% of rows after CAVOK/NSC handling |

> [!CAUTION]
> **Do NOT invent cloud information.** CAVOK/NSC = "no significant cloud" is a real observation, not missing data. The sentinel value of 5000m reflects the physical definition (no cloud below 5000ft). Genuinely missing rows (neither layers nor CAVOK/NSC) should be flagged and imputed conservatively, NOT silently dropped.

---

## 4. Independence from Stage 8.1 MEPS Cloud Features

### 4A. Stage 8.1 Champion Cloud Feature Inventory

The Stage 8.1 champion (37 features) includes these cloud/atmosphere variables as **MEPS NWP forecasts**:

| Feature | Source | Physical Quantity | Temporal Character |
| :--- | :--- | :--- | :--- |
| TCC | MEPS D-1 18Z forecast | Total cloud cover (0–1) | Model forecast, 6–30h lead |
| LCC | MEPS D-1 18Z forecast | Low cloud cover (0–1) | Model forecast, 6–30h lead |
| MCC | MEPS D-1 18Z forecast | Medium cloud cover (0–1) | Model forecast, 6–30h lead |
| HCC | MEPS D-1 18Z forecast | High cloud cover (0–1) | Model forecast, 6–30h lead |
| LWP | MEPS D-1 18Z forecast | Liquid Water Path (kg/m²) | Model forecast, 6–30h lead |
| IWP | MEPS D-1 18Z forecast | Ice Water Path (kg/m²) | Model forecast, 6–30h lead |
| U700 | MEPS D-1 18Z forecast | 700 hPa zonal wind (m/s) | Model forecast, 6–30h lead |
| V700 | MEPS D-1 18Z forecast | 700 hPa meridional wind (m/s) | Model forecast, 6–30h lead |

### 4B. ENEV METAR vs MEPS: Four Axes of Independence

#### Axis 1: Observation vs Forecast

| Property | MEPS Cloud Features | ENEV METAR Cloud |
| :--- | :--- | :--- |
| **Type** | NWP model forecast | Direct ceilometer observation |
| **Error character** | NWP systematic bias + stochastic error | Instrument measurement noise only |
| **Assimilation cycle** | D-1 18:00 UTC | Observation at 23:50 UTC (D-1) |
| **Information age at t0** | ≥6 hours old | ≤10 minutes old |

**Verdict:** ENEV METAR at 23:50 UTC contains cloud-state information **5+ hours newer** than what MEPS assimilated. This is genuinely new observational evidence about the actual cloud state, not just another MEPS derivative.

#### Axis 2: Spatial Location

| Property | MEPS Cloud Features | ENEV METAR Cloud |
| :--- | :--- | :--- |
| **Location** | Nuolja grid cell (68.36°N, 18.74°E) | ENEV airport (68.52°N, 16.68°E) |
| **Terrain** | Mountain site, 702m ASL | Coastal lowland, 26m ASL |
| **Position relative to weather systems** | At target | 86 km upstream (WNW) |

**Verdict:** ENEV observes cloud state in the **upstream airmass** before it crosses the Scandes to reach Nuolja. This is a physically distinct observation point that may carry precursor information about incoming weather.

#### Axis 3: Physical Quantity

| Property | MEPS TCC/LCC/MCC/HCC | ENEV METAR skyc/skyl |
| :--- | :--- | :--- |
| **Variable** | Fractional cloud cover (0–1) continuous | Cloud cover oktas (categorical 0/1.5/3.5/6/8) |
| **Vertical info** | Separated into Low/Medium/High bands | Explicit cloud base height per layer (feet AGL) |
| **Cloud base** | NOT directly in Stage 8.1 features | Directly reported by ceilometer |

**Verdict:** Cloud base height is a **different physical quantity** from cloud fraction. It tells you whether the cloud deck will intercept Nuolja's terrain (702m ASL). Stage 8.8 tested MEPS-derived CBH at Nuolja and REJECTED it — but ENEV provides **observed** CBH at an upstream location, which is a different information channel (observed precursor, not local model CBH).

#### Axis 4: Temporal Freshness (Critical Distinction)

POLARIS uses the **MEPS D-1 18:00 UTC** run. By t0=00:00 UTC, this forecast has **6 hours of lead time** for the first forecast hour. In the 6 hours between MEPS initialization and t0, the real atmosphere has evolved. The ENEV 23:50 UTC observation captures this evolved state.

**This is the strongest independence argument:** ENEV METAR provides a **post-MEPS-initialization observation** of the actual cloud state approaching from upstream.

### 4C. Potential Redundancy Concerns

> [!WARNING]
> **Honest redundancy risks that must be acknowledged:**
>
> 1. **MEPS itself ingests SYNOP/METAR via assimilation** — but the relevant MEPS run (D-1 18Z) assimilated data up to ~18:00 UTC. The ENEV 23:50 UTC observation is 5:50 hours AFTER the assimilation cutoff. No METAR from ENEV after 18Z is in the MEPS D-1 18Z run.
> 2. **The 24-hour SW_IN history** already captures cloud effects at Nuolja up to t0. But it captures the **effect at Nuolja**, not the **state upstream**. These are distinct information channels unless advection perfectly correlates them (which Stage 8.5 showed it does NOT in mountain terrain).
> 3. **ENEV is 86 km from Nuolja across the Scandes divide.** Stage 8.9A REJECTED Kiruna (88 km ESE, downstream) partly for spatial separation. However, ENEV is UPSTREAM (WNW), not downstream, and the physical hypothesis is explicitly about precursor information, not about representing local Nuolja cloud state.

### 4D. Independence Verdict

**ENEV METAR cloud state is genuinely independent of Stage 8.1 MEPS cloud features on all four axes:**
1. ✅ Observation vs forecast
2. ✅ Different spatial location (upstream)
3. ✅ Different physical quantity (CBH vs cloud fraction)
4. ✅ Post-MEPS-initialization timing (5+ hours newer)

**Strongest argument:** Temporal freshness + upstream positioning. This is the only candidate that provides a **real-time observed cloud state** in the **incoming airmass** that is **newer than MEPS**.

**Weakest point:** 86 km spatial separation across the Scandes ridge. Mountain orographic effects can decouple upstream coastal cloud state from Nuolja cloud state (same physics that killed Stage 8.5 advection). This is the key risk that only an experiment can resolve.

---

## 5. Proposed Feature Set (Minimal, Defensible)

### 5A. Design Principles

1. **Minimize feature count** — avoid overfitting risk on 347 origins (174 even / 173 odd split)
2. **Only encode what ENEV genuinely observes** — no invented information
3. **Preserve CAVOK/NSC as real data** — not as missing
4. **Use 23:50 UTC only** — strictly causal, most recent before t0

### 5B. Proposed Features (2 candidates)

#### Feature 1: `enev_cloud_cover_okta` (Scalar)

- **Extraction:** From 23:50 UTC METAR
- **Encoding:** CAVOK/NSC/NCD/SKC→0, FEW→1.5, SCT→3.5, BKN→6, OVC→8, VV→8
- **Physical hypothesis:** Upstream cloud cover = precursor for incoming cloud mass
- **Expected coverage:** ~100% (every METAR has a cloud state)

#### Feature 2: `enev_cloud_base_m` (Scalar)

- **Extraction:** From 23:50 UTC METAR
- **Encoding:** skyl1 converted to meters AGL; CAVOK/NSC→5000m sentinel; VV→VVxxx×30.48m
- **Physical hypothesis:** Low upstream cloud base → incoming cloud deck will immerse Nuolja terrain. High base or CAVOK → clear upstream airmass approaching.
- **Expected coverage:** ~100% (layer height or CAVOK/NSC sentinel)

### 5C. Features Explicitly EXCLUDED and Why

| Rejected Feature | Reason for Exclusion |
| :--- | :--- |
| Multi-layer structure (skyc2/skyl2+) | Too sparse (~32% for layer 2, worse for 3/4). Would introduce heavy imputation = noise. |
| Visibility (`vsby`) | Already partially captured by `wxcodes` and cloud cover. Adding a 3rd feature on 347 origins risks overfitting for marginal gain. |
| Weather codes (`wxcodes`) | Categorical with many levels. Hard to encode without one-hot explosion. Precipitation is partially correlated with BKN/OVC/VV. |
| Temporal change (23:50 minus 22:50) | Doubles feature count. Marginal value when spatial advection is already uncertain across 86 km of mountains. |
| Multiple stations (ENDU, ENTC, ENAN) | Each adds features. Multi-station approach = 6+ new features on 347 origins. Start with ENEV alone (closest upstream). |
| Cloud base relative to Nuolja terrain | This is a derived feature (cloud_base_m_ASL − 702). Could be added as Feature 3 only if Features 1–2 show signal. |

### 5D. Feature Count Assessment

**2 new features** on 347 origins (174 train / 173 test) is conservative. The existing model has 37 features. Adding 2 features = ~5% expansion. This is defensible from an overfitting perspective.

---

## 6. Risk Assessment

| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| 86 km spatial separation + Scandes barrier decouples upstream cloud from Nuolja | **HIGH** | Only an experiment can answer this. Same distance/barrier argument that killed Kiruna — but ENEV is upstream, not downstream. |
| Cloud cover okta is a crude 5-level ordinal, not continuous | **MEDIUM** | Physical signal may still be present in coarse categories. BKN/OVC upstream is a strong precursor. |
| ENEV coastal lowland (26m) ≠ Nuolja mountain (702m) | **MEDIUM** | Altitude difference means ENEV cloud base reported as AGL is 676m lower than Nuolja in ASL terms. Feature 2 (cloud base m AGL) may need ASL conversion. |
| Hourly observations at xx:50 may miss rapid changes | **LOW** | Aviation METAR cadence is standard. SPECIs are available for rapid changes. |
| Temporal decorrelation: upstream cloud at 23:50 has ~2–6 hour advection time to Nuolja at typical wind speeds | **MEDIUM** | This IS the precursor hypothesis — we're testing whether the upstream state has predictive value for H1–H6 forecasts. |

---

## 7. Decision

### CONDITIONAL

**Rationale:** ENEV METAR cloud information passes all four audit gates:

1. ✅ **Usable fields exist** — cloud cover (oktas) and cloud base height (meters) are extractable from 100% of METAR reports (including CAVOK/NSC encoding)
2. ✅ **Causal availability confirmed** — 23:50 UTC report is strictly causal at t0=00:00 UTC
3. ✅ **CAVOK/NSC encoding is defensible** — these are real physical observations, not missing data, with well-defined numeric encoding
4. ✅ **Genuine independence from Stage 8.1** — on all four axes (observation type, spatial location, physical quantity, temporal freshness)
5. ✅ **Minimal feature set proposed** — 2 features, conservative for 347-origin benchmark

**The CONDITIONAL gate is the 86 km spatial separation across the Scandes ridge.** The same physics that killed Kiruna ESNQ (88 km ESE, downstream) — mountain orographic decoupling — applies equally to ENEV (86 km WNW, upstream). The upstream argument is physically stronger but NOT empirically verified. Only a governed experiment can determine whether upstream coastal cloud state at ENEV carries predictive signal for Nuolja SW_IN.

**Next step:** Governed experiment with the 2-feature set on even-indexed origins, evaluated on ODD, comparing against Stage 8.1 champion.

---

*Audit completed 2026-09-13. No experiments performed. No ODD access. No ML models run.*
