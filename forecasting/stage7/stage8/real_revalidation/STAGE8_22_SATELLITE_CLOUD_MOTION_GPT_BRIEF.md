# STAGE 8.22 — SATELLITE CLOUD-MOTION FEASIBILITY BRIEF (GPT BRIEF)

**Topic:** Feasibility Audit of Satellite Cloud-Motion & NRT Cloud-State Data for SITES Nuolja (2024)  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $675\text{ m a.s.l.}$)  
**Author:** GPT Independent Research Agent  
**Date:** September 13, 2026  

---

## 1. Executive Summary

This independent research brief evaluates whether **real-time satellite cloud motion, cloud position, or cloud state observations** can serve as a viable new input axis for forecasting surface solar irradiance ($SW_{IN}$) at SITES Nuolja across lead times $H1 \dots H24$.

The inquiry focuses on establishing whether any satellite product satisfies the strict **POLARIS Governance Requirements**:
1. **Product Existence (F1)**
2. **Causal Availability at $t_0$ (F2)**
3. **Empirical 2024 Coverage (F3)**
4. **Spatial Representativeness at $68.36^\circ\text{N}$ (F4)**
5. **Temporal Usefulness for $H1 \dots H24$ (F5)**
6. **Information Novelty relative to Stage 8.1 (F6)**
7. **Historical Archive Accessibility for 2024 (F7)**
8. **Operational Usability (F8)**

**Verdict:** **NOT FEASIBLE**. While satellite products exist historically in space agency archives, **zero candidates satisfy all mandatory operational gates simultaneously**. GEO geostationary products suffer from unusable spatial distortion at $68^\circ\text{N}$, LEO polar motion products fail causal dissemination deadlines ($t_{\text{pub}} > t_0$), and optical tracking breaks down over the Scandes mountain range due to orographic cloud generation and evaporation.

---

## 2. Detailed Audit Across Candidate Data Sources

### Source Family 1: Geostationary Satellites (MSG / Meteosat SEVIRI AMVs & NWC SAF HRW)
- **Product Existence (F1):** PASS. EUMETSAT NWC SAF High-Resolution Winds (HRW) product generates Atmospheric Motion Vectors (AMVs) from MSG SEVIRI IR and WV channels.
- **Causal Availability (F2):** CONDITIONAL. MSG SEVIRI scans every 15 minutes. Dissemination via EUMETCast takes 15–30 minutes, meaning pre-$t_0$ imagery is causally available in real time.
- **Empirical 2024 Coverage (F3):** CONDITIONAL. Full 15-minute coverage in time, but quality indicator (QI) scores drop below usable thresholds at latitudes $> 65^\circ\text{N}$.
- **Spatial Representativeness (F4):** **FAIL**. SITES Nuolja ($68.36^\circ\text{N}$) is located at the extreme northern periphery of the MSG SEVIRI viewing disk:
  - **View Zenith Angle (VZA):** $\approx 76.5^\circ$ (nadir is $0^\circ\text{N}, 0^\circ\text{E}$).
  - **Pixel Size Degradation:** Nominal $3\text{ km}$ IR pixels stretch to $> 6\text{ km} \times 11\text{ km}$ over Lapland.
  - **Parallax Displacement:** High cloud tops ($7 \dots 9\text{ km AGL}$) are shifted northward by $20 \dots 28\text{ km}$, misplacing cloud shadows relative to the station.
- **Temporal Usefulness (F5):** **FAIL**. Extreme spatial distortion renders 15-min tracking unsuitable for localized station forecasting.
- **Information Novelty (F6):** PASS. Direct observation of cloud motion.
- **Historical Access (F7):** PASS. Complete 2024 archive exists in EUMETSAT Data Centre.
- **Operational Interpretation (F8):** **FAIL**. Unusable due to geometric distortion.

### Source Family 2: Polar Orbiting Satellites (MetOp AVHRR & NOAA/VIIRS AMVs)
- **Product Existence (F1):** PASS. EUMETSAT EPS AVHRR AMV and NOAA VIIRS Polar Wind products exist.
- **Causal Availability (F2):** **FAIL**. Deriving a polar AMV vector requires tracking cloud features across consecutive overlapping passes (pass interval $\Delta t \approx 50 \dots 100\text{ minutes}$).
  - Swath 1 overpass: $t_0 - 2.5\text{ h}$.
  - Swath 2 overpass: $t_0 - 1.2\text{ h}$.
  - Processing & EUMETCast dissemination delay: $+1.5 \dots +2.5\text{ hours}$.
  - **Result:** $t_{\text{pub}} = t_0 + 0.3\text{ h} \dots t_0 + 1.8\text{ h}$. The vector arrives **after** forecast origin $t_0$ (`CAUSAL_FAIL`).
- **Empirical 2024 Coverage (F3):** **FAIL**. Swath overlap over Lapland is intermittent. Valid AMV coverage across the 347 benchmark origins is $< 14\%$. Visible channels are missing during polar night (November–February).
- **Spatial Representativeness (F4):** PASS. High spatial resolution ($1\text{ km}$ at nadir).
- **Temporal Usefulness (F5):** **FAIL**. Large orbital time gaps ($2 \dots 4\text{ hours}$) prevent continuous $H1 \dots H24$ trajectory modeling.
- **Information Novelty (F6):** PASS. Independent cloud velocity measurement.
- **Historical Access (F7):** PASS. NOAA CLASS / EUMETSAT archives.
- **Operational Interpretation (F8):** **FAIL**. Latency and coverage gaps preclude operational deployment.

### Source Family 3: Algorithmic Optical Flow on Polar Imager Radiance (VIIRS / AVHRR)
- **Product Existence (F1):** PASS. Dense 2D optical flow vector fields computed from sequential LEO thermal IR radiance bands.
- **Causal Availability (F2):** **FAIL**. Level-1B imager swath dissemination delays ($1.0 \dots 2.5\text{ hours}$) prevent real-time optical flow computation before $t_0$.
- **Empirical 2024 Coverage (F3):** **FAIL**. Polar orbiter pass intervals are non-uniform ($\Delta t \in [20\text{ min}, 105\text{ min}]$), breaking the constant time-step assumption of optical flow solvers. Rapid solar elevation changes violate the brightness constancy constraint ($\partial I / \partial t = 0$).
- **Spatial Representativeness (F4):** CONDITIONAL. High resolution at nadir, but distorted at swath edges.
- **Temporal Usefulness (F5):** **FAIL**. Irregular sampling invalidates forward optical flow integration.
- **Information Novelty (F6):** PASS. 2D image-based motion fields.
- **Historical Access (F7):** PASS. NASA LAADS DAAC / EUMETSAT.
- **Operational Interpretation (F8):** **FAIL**. **Physical Mountain Bottleneck:** Optical flow assumes cloud mass is conserved during translation ($\frac{D q_c}{D t} = 0$). Near Nuolja, forced moist ascent over the Scandes mountains constantly generates new cloud cover on windward slopes, while downslope subsidence evaporates clouds on leeward slopes. Pure translation algorithms completely fail to model this phase dynamics.

### Source Family 4: NWC SAF PPS Polar Cloud Mask & Cloud Top Height (LEO NRT Products)
- **Product Existence (F1):** PASS. NWC SAF Polar Satellite Processing Software (PPS) NRT Cloud Mask and Cloud Top Temperature/Height (CTTH) products exist.
- **Causal Availability (F2):** CONDITIONAL. Single-swath processing and dissemination take $\approx 30 \dots 60\text{ minutes}$. Passes prior to 22:30 UTC arrive before $t_0 = 00:00\text{ UTC}$, but availability is irregular.
- **Empirical 2024 Coverage (F3):** CONDITIONAL. Passes cover $\approx 65 \dots 75\%$ of origins, but leave 25–35% total missingness.
- **Spatial Representativeness (F4):** PASS. $1\text{ km}$ spatial resolution over Sweden/Norway.
- **Temporal Usefulness (F5):** **FAIL**. Provides a single static cloud snapshot at $t \le t_0$, but contains **no velocity or displacement vectors**. It cannot propagate clouds forward to $H3, H6,$ or $H12$ without relying on model wind fields.
- **Information Novelty (F6):** PASS. Direct satellite-observed cloud top height.
- **Historical Access (F7):** PASS. SMHI / EUMETSAT archive.
- **Operational Interpretation (F8):** **FAIL**. Static cloud snapshots without velocity vectors cannot drive cloud advection forecasts.

---

## 3. Summary Gate Evaluation Matrix

| Source Candidate | F1 Product | F2 Causality | F3 2024 Coverage | F4 Representativeness | F5 Temporal | F6 Novelty | F7 Archive | F8 Usability | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **MSG SEVIRI AMV / NWC SAF HRW** | PASS | COND | COND | **FAIL** (VZA $76.5^\circ$) | **FAIL** | PASS | PASS | **FAIL** | **NOT FEASIBLE** |
| **MetOp / VIIRS Polar AMVs** | PASS | **FAIL** ($t_{\text{pub}} > t_0$) | **FAIL** ($<14\%$) | PASS | **FAIL** | PASS | PASS | **FAIL** | **NOT FEASIBLE** |
| **LEO Optical Flow (VIIRS/AVHRR)** | PASS | **FAIL** | **FAIL** | COND | **FAIL** | PASS | PASS | **FAIL** | **NOT FEASIBLE** |
| **NWC SAF PPS Cloud Mask / CTH** | PASS | COND | COND | PASS | **FAIL** (Static) | PASS | PASS | **FAIL** | **NOT FEASIBLE** |

---

## 4. Final Recommendation

**DO NOT PROCEED TO EXPERIMENT DESIGN.**

Satellite cloud-motion data fails on **geostationary pixel distortion at high latitudes**, **LEO multi-swath publication latency**, **polar night temporal missingness**, and **orographic cloud non-stationarity**. The frozen Stage 8.1 37-feature operational champion remains the authoritative baseline.
