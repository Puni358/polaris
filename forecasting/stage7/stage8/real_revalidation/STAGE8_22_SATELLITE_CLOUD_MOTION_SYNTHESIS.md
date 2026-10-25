# STAGE 8.22 — SATELLITE CLOUD-MOTION FEASIBILITY SYNTHESIS

**Stage:** POLARIS Stage 8.22 — Satellite Cloud-Motion / Position Feasibility  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation $675\text{ m a.s.l.}$)  
**Forecast Lead Times:** $H1 \dots H24$ Surface Shortwave Irradiance ($SW_{IN}$)  
**Date:** September 13, 2026  
**Final Feasibility Decision:** **`NOT FEASIBLE`**  
**Active Operational Champion:** **`UNCHANGED — STAGE 8.1 37-FEATURE HGB CHAMPION`**  

---

## 1. Executive Feasibility Synthesis

This document synthesizes the independent findings from the AI assistant and GPT research briefs ([`STAGE8_22_SATELLITE_CLOUD_MOTION_BRIEF.md`](file:///home/punith-bs/01polaris%20(Copy)/stage7/stage8/real_revalidation/STAGE8_22_SATELLITE_CLOUD_MOTION_BRIEF.md) and [`STAGE8_22_SATELLITE_CLOUD_MOTION_GPT_BRIEF.md`](file:///home/punith-bs/01polaris%20(Copy)/stage7/stage8/real_revalidation/STAGE8_22_SATELLITE_CLOUD_MOTION_GPT_BRIEF.md)) regarding the feasibility of satellite cloud-motion, cloud-position, and NRT cloud-state data for SITES Nuolja in 2024.

The core research question evaluated is:
> *"What historically accessible satellite/NRT cloud-motion or cloud-position information could have been available causally before the locked POLARIS forecast origin $t_0$ for SITES Nuolja in 2024, and does any source provide genuinely new spatial cloud-evolution information?"*

**Synthesis Finding:** Both independent briefs arrive at an unanimous conclusion: **Satellite-derived cloud-motion data is NOT FEASIBLE for operational solar forecasting at SITES Nuolja.**

---

## 2. Candidate Evaluation Matrix Across Feasibility Gates (F1 – F8)

| Candidate Source | F1 Existence | F2 Causality | F3 2024 Coverage | F4 Spatial Rep. | F5 Temporal | F6 Novelty | F7 Archive | F8 Usability | Overall Gate Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GEO MSG SEVIRI AMVs / NWC SAF HRW** | **PASS** | **COND** | **COND** | **FAIL** (VZA $76.5^\circ$, Parallax $25\text{ km}$, Pixel $>6 \times 11\text{ km}$) | **FAIL** | **PASS** | **PASS** | **FAIL** | **NOT FEASIBLE** |
| **LEO MetOp / VIIRS Polar Orbit AMVs** | **PASS** | **FAIL** ($t_{\text{pub}} > t_0$) | **FAIL** ($<14\%$ origin coverage) | **PASS** | **FAIL** (2–4 h gaps) | **PASS** | **PASS** | **FAIL** | **NOT FEASIBLE** |
| **LEO Algorithmic Optical Flow (VIIRS/AVHRR)** | **PASS** | **FAIL** ($t_{\text{pub}} > t_0$) | **FAIL** (Polar night darkness, non-uniform $\Delta t$) | **COND** | **FAIL** | **PASS** | **PASS** | **FAIL** (Orographic non-stationarity) | **NOT FEASIBLE** |
| **LEO NWC SAF PPS Cloud Mask & CTH** | **PASS** | **COND** | **COND** (65–75% origins) | **PASS** ($1\text{ km}$) | **FAIL** (Static snapshot, zero velocity) | **PASS** | **PASS** | **FAIL** | **NOT FEASIBLE** |

---

## 3. Detailed Breakdown of Feasibility Gates

### F1 — PRODUCT EXISTENCE: PASS
Real satellite products exist in historical archives (EUMETSAT Data Centre, NOAA CLASS, NASA LAADS DAAC, SMHI NWC SAF PPS archives) providing cloud mask, cloud top height, and atmospheric motion vectors.

### F2 — CAUSAL AVAILABILITY: FAIL / CONDITIONAL
- **GEO Products:** Disseminated via EUMETCast within 15–30 min. Causally available before $t_0$, but severely distorted spatially.
- **LEO Dual-Swath AMVs:** Deriving vector fields requires tracking features across two overlapping polar passes ($\Delta t \approx 50 \dots 100\text{ min}$). Level-2 extraction and EUMETCast dissemination latency requires $1.5 \dots 3.0\text{ hours}$. Publication timestamp $t_{\text{pub}}$ is routinely after forecast origin $t_0 = 00:00\text{ UTC}$ ($t_{\text{pub}} > t_0$), violating strict causal availability.

### F3 — EMPIRICAL 2024 COVERAGE: FAIL / CONDITIONAL
- **LEO Polar Overlaps:** Swath matching over Lapland yields valid AMVs for $< 14\%$ of 2024 benchmark origins (48 / 347 origins).
- **Polar Night Missingness:** Visible band cloud motion retrievals fail completely during sub-Arctic polar darkness (November–February, $SZA > 84^\circ$).

### F4 — SPATIAL REPRESENTATIVENESS: FAIL
- **GEO Parallax Distortion:** SITES Nuolja ($68.36^\circ\text{N}$) sits at extreme high latitudes where geostationary View Zenith Angle (VZA) exceeds $76.5^\circ$. High cloud tops ($7 \dots 9\text{ km AGL}$) are shifted northward by $20 \dots 28\text{ km}$ relative to ground coordinates.
- **Pixel Footprint Degradation:** $3\text{ km}$ sub-satellite pixels stretch to $> 6\text{ km} \times 11\text{ km}$ over Lapland, blurring localized mountain cloud structures.

### F5 — TEMPORAL USEFULNESS: FAIL
- Discrete polar orbiter passes leave large temporal gaps ($2 \dots 4\text{ hours}$ between passes).
- Static LEO cloud snapshots (NWC SAF PPS) provide initial cloud position at $t \le t_0$, but contain **zero motion vectors**, rendering them incapable of driving advection forecasts over $H1 \dots H24$.

### F6 — INFORMATION NOVELTY: PASS
Directly observed cloud positions and motion vectors represent a conceptual **NEW INFORMATION AXIS** (observed physical cloud kinematics vs numerical MEPS forecast fields). However, novelty alone does not overcome physical and operational failure.

### F7 — HISTORICAL ACCESS: PASS
2024 data products can be retrieved from EUMETSAT and SMHI archives.

### F8 — OPERATIONAL INTERPRETATION & PHYSICAL MOUNTAIN BOTTLENECK: FAIL
- **Orographic Non-Stationarity:** Translation-based cloud advection assumes clouds behave as conservative passive tracers ($\frac{D q_c}{D t} = 0$). Over the Scandes mountain ridge near Nuolja, forced moist ascent continuously generates new cloud cover on windward slopes, while lee-side subsidence evaporates clouds on leeward slopes.
- Pure optical flow or translational velocity vectors fail to capture this localized phase change dynamics.

---

## 4. Strongest Candidate & Unresolved Evidence

- **Strongest Candidate:** LEO NWC SAF PPS Cloud Top Height (CTH) + 700 hPa MEPS Steering Winds.
- **Unresolved Blocker:** LEO PPS provides a static $1\text{ km}$ cloud top snapshot prior to $t_0$, but contains **zero motion velocity vectors**. When advected using MEPS winds, it becomes functionally redundant with existing MEPS LWP/IWP and cloud fraction fields already included in the Stage 8.1 37-feature champion (`lwp_latest`, `iwp_latest`, `u700`, `v700`).

---

## 5. Final Feasibility Decision & Governance Statement

### FINAL DECISION: **`NOT FEASIBLE`**

> [!WARNING]
> **REJECTED FOR EXPERIMENT DESIGN:**
> Satellite cloud-motion and NRT cloud-state data fail mandatory feasibility gates F2 (Causal Availability), F3 (Empirical Coverage), F4 (Spatial Representativeness), F5 (Temporal Usefulness), and F8 (Operational Usability).
>
> **Do NOT build an experiment pipeline. Do NOT extract full satellite datasets.**

### Governance Firewall Compliance Statement

1. **Experiment Code Executed:** `NONE` (Zero model training, zero cross-validation).
2. **ODD Target Access:** `NONE` (Zero ODD targets read or evaluated).
3. **Operational Champion:** `UNCHANGED` (Stage 8.1 37-feature HGB champion preserved, Daytime nMAE = $28.0688\%$).
4. **Governance Files:** `POLARIS_MASTER_HANDOFF.md` and `POLARIS_STAGE8_ROUTE_REGISTRY` remain untouched.
