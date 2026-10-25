# STAGE 8.22 — SATELLITE CLOUD-MOTION FEASIBILITY BRIEF (AI BRIEF)

**Topic:** Causal Satellite Cloud-Motion / Cloud-Position / NRT Cloud-State Data for SITES Nuolja (2024)  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $675\text{ m a.s.l.}$)  
**Forecast Context:** POLARIS $H1 \dots H24$ Surface Shortwave Irradiance ($SW_{IN}$) Forecasting  
**Author:** AI assistant Scientific Research Agent  
**Date:** September 13, 2026  

---

## 1. Executive Summary

This brief evaluates the feasibility of incorporating **observed NRT satellite cloud-motion, cloud-position, and cloud-state data** to improve $H1 \dots H24$ shortwave irradiance forecasts at SITES Nuolja. The core scientific question is whether an independently observed cloud-motion or cloud-position sequence prior to forecast origin $t_0$ can causally inform cloud advection over the Scandes mountains and beat the frozen Stage 8.1 37-feature operational champion ($U_{700}, V_{700}$ steering wind model).

**Main Finding:** Satellite-derived cloud-motion products (AMVs, optical flow) and high-latitude NRT cloud masks are **NOT FEASIBLE** for operational forecasting at SITES Nuolja due to a combination of **severe geostationary distortion at $68.36^\circ\text{N}$**, **LEO multi-swath dissemination latencies exceeding $t_0$**, **polar night missingness**, and **orographic cloud non-stationarity** over mountain terrain.

---

## 2. Technical Evaluation of Candidate Sources

### Candidate 1: GEO Geostationary Atmospheric Motion Vectors (MSG SEVIRI AMV / NWC SAF HRW)
- **Product Existence (F1):** PASS. EUMETSAT NWC SAF High-Resolution Winds (HRW) and MSG SEVIRI AMVs exist.
- **Causal Availability (F2):** CONDITIONAL. MSG 15-minute image files are disseminated via EUMETCast with 15–30 min latency.
- **Empirical 2024 Coverage (F3):** CONDITIONAL. Continuous 15-min cadence, but quality flags drop sharply above $65^\circ\text{N}$.
- **Spatial Representativeness (F4):** **FAIL**. Nuolja sits at $68.36^\circ\text{N}$. The MSG satellite sub-satellite point is $0^\circ\text{N}, 0^\circ\text{E}$, yielding an extreme view zenith angle (VZA) $\approx 76.5^\circ$. This creates:
  1. **Severe Parallax Shift:** Cloud tops at $6 \dots 8\text{ km AGL}$ are geometrically displaced to the north by $15 \dots 25\text{ km}$ relative to their true ground position.
  2. **Pixel Footprint Distortion:** Standard $3\text{ km}$ sub-satellite IR pixels expand to $> 6\text{ km} \times 11\text{ km}$ over Lapland, blurring localized mountain cloud features.
- **Temporal Usefulness (F5):** CONDITIONAL. High 15-min temporal resolution is offset by spatial blur and parallax errors.
- **Information Novelty (F6):** PASS. Provides direct observed cloud motion vectors.
- **Historical Access (F7):** PASS. Available via EUMETSAT Data Centre.
- **Operational Interpretation (F8):** **FAIL**. High-latitude geometric distortion invalidates site-specific tracking over Nuolja.

### Candidate 2: LEO Polar Satellite AMVs (MetOp AVHRR / NOAA-20/21 VIIRS AMVs)
- **Product Existence (F1):** PASS. EUMETSAT Polar System (EPS) and NOAA NESP polar AMV products exist.
- **Causal Availability (F2):** **FAIL**. Generating a polar AMV requires feature tracking between two consecutive overlapping polar orbiter swaths (pass interval $\Delta t \approx 50 \dots 100\text{ min}$). Level-2 AMV derivation and EUMETCast dissemination latency requires $1.5 \dots 3.0\text{ hours}$. For $t_0 = 00:00\text{ UTC}$, the latest pre-$t_0$ dual-swath AMV vector is routinely published after $t_0$ ($t_{\text{pub}} > t_0$).
- **Empirical 2024 Coverage (F3):** **FAIL**. Swath overlap occurs intermittently over Scandinavia. Usable origin coverage is $< 14\%$ (48 / 347 origins). Visible-channel tracking fails completely during sub-Arctic polar night (November–February).
- **Spatial Representativeness (F4):** PASS. High spatial resolution ($1\text{ km}$ at nadir).
- **Temporal Usefulness (F5):** **FAIL**. Discrete 50–100 min orbit passes leave 2–4 hour coverage gaps.
- **Information Novelty (F6):** PASS. Direct observed cloud motion.
- **Historical Access (F7):** PASS. Retrievable from EUMETSAT Data Centre / NOAA CLASS.
- **Operational Interpretation (F8):** **FAIL**. Publication latency exceeds $t_0$ and temporal coverage is severely fragmented.

### Candidate 3: Image-Based Optical Flow on Sequential LEO Satellite Imagery (VIIRS / AVHRR)
- **Product Existence (F1):** PASS. Custom optical flow algorithms (Farneback, TV-L1) applied to sequential LEO channels.
- **Causal Availability (F2):** **FAIL**. Raw LEO Level-1B imagery dissemination latencies ($1.0 \dots 2.5\text{ hours}$) prevent real-time optical flow computation before $t_0$.
- **Empirical 2024 Coverage (F3):** **FAIL**. Non-uniform orbit time intervals ($\Delta t \in [20\text{ min}, 105\text{ min}]$) violate equal-time-step differential optical flow assumptions. Rapid solar zenith angle shifts alter cloud illumination, violating the optical flow brightness constancy assumption ($\partial I / \partial t = 0$).
- **Spatial Representativeness (F4):** CONDITIONAL. High resolution at nadir, but distorted at swath edges.
- **Temporal Usefulness (F5):** **FAIL**. Irregular sampling invalidates motion extrapolation beyond $H1$.
- **Information Novelty (F6):** PASS. 2D image motion.
- **Historical Access (F7):** PASS. Available via LAADS DAAC / EUMETSAT.
- **Operational Interpretation (F8):** **FAIL**. Physical mountain obstacle: cloud advection assumes conservative tracer behavior ($\frac{D q_c}{D t} = 0$). Over the Scandes ridge, clouds continuously condense on windward slopes and evaporate on leeward slopes (orographic non-stationarity). Optical flow translation fails to capture phase changes.

### Candidate 4: NWC SAF PPS / EUMETSAT NRT Cloud Mask & Cloud Top Height (LEO Snapshots)
- **Product Existence (F1):** PASS. NWC SAF Polar Satellite Processing Software (PPS) Cloud Mask (CMA) & CT/CTH products exist.
- **Causal Availability (F2):** CONDITIONAL. Single-swath NRT processing delay is $\approx 30 \dots 60\text{ min}$. Overpasses occurring before 22:30 UTC arrive before $t_0 = 00:00\text{ UTC}$, but coverage is intermittent.
- **Empirical 2024 Coverage (F3):** CONDITIONAL. Single-pass coverage exists for $\approx 60 \dots 75\%$ of 2024 benchmark origins.
- **Spatial Representativeness (F4):** PASS. $1\text{ km}$ spatial resolution over Northern Scandinavia.
- **Temporal Usefulness (F5):** **FAIL**. Provides a static cloud snapshot at $t \le t_0$, but contains **zero motion velocity vectors**. Without velocity vectors, it cannot predict cloud position at $H3, H6,$ or $H12$ without relying back on MEPS wind fields.
- **Information Novelty (F6):** PASS. Direct observed cloud top height and cloud mask.
- **Historical Access (F7):** PASS. Archive accessible via SMHI / EUMETSAT.
- **Operational Interpretation (F8):** **FAIL**. Static initial snapshot lacks cloud velocity information and does not provide a functional advection mechanism.

---

## 3. Synthesis & Rejection Justification

```
+-----------------------------------------------------------------------------------+
|                        PHYSICAL & OPERATIONAL BOTTLENECKS                         |
+-----------------------------------------------------------------------------------+
|  1. GEO Parallax & Pixel Blur: SEVIRI VZA ~ 76.5 deg at 68.36 N distorts cloud    |
|     positions by 15-25 km and expands pixel size to > 6x11 km.                    |
|  2. LEO Latency & Gaps: Polar dual-swath AMVs take > 1.5-3.0 h to publish (t_pub > |
|     t_0), leaving severe 2-4 h temporal gaps between passes.                      |
|  3. Polar Night Darkness: Sub-Arctic winter darkness (Nov-Feb) eliminates visible  |
|     channel retrievals and optical flow tracking.                                 |
|  4. Orographic Non-Stationarity: Scandes mountain uplift continuously generates    |
|     windward clouds and dissipates leeward clouds, breaking passive advection.    |
+-----------------------------------------------------------------------------------+
```

**Conclusion:** Observed satellite cloud motion does not satisfy the operational requirements of causal availability, temporal continuity, and physical validity in complex mountain terrain.
