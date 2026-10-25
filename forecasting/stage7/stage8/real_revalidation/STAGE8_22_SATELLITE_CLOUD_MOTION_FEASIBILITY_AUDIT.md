# POLARIS STAGE 8.22 — SATELLITE CLOUD-MOTION / NRT CLOUD STATE FEASIBILITY AUDIT REPORT

> [!IMPORTANT]
> **GOVERNANCE STATUS: FEASIBILITY RESEARCH AUDIT ONLY**  
> - **No model pipeline has been built or trained.**  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion (ODD daytime nMAE 28.0688%).**  
> - **No modifications to POLARIS_MASTER_HANDOFF.md or POLARIS_STAGE8_ROUTE_REGISTRY.**

---

## 1. Executive Summary & Feasibility Decision

This feasibility research audit evaluates **POLARIS Stage 8.22: Satellite Cloud-Motion / NRT Cloud State**.

The objective is to determine whether causally available satellite observations prior to forecast origin $t_0 = 00:00\text{ UTC}$ can provide genuinely novel spatial cloud-position, cloud-motion, or cloud-evolution features that improve short-term solar irradiance ($SW\_IN$) forecasting at SITES Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$).

### Summary Decision: **`NOT FEASIBLE`**

> [!WARNING]
> **ROUTE CLOSED — NO EXPERIMENT PIPELINE AUTHORIZED:**  
> Satellite cloud-motion and NRT cloud-state data fail mandatory feasibility gates for operational site-specific forecasting. Geostationary products suffer from extreme high-latitude parallax distortion ($>21\text{ km}$ shift) and pixel stretching ($>14\text{ km}$). Polar orbiter Atmospheric Motion Vectors (AMVs) suffer from severe derivation latency ($t_{\text{pub}} > t_0$), winter polar night darkness, and $<14\%$ empirical origin coverage.

---

## 2. Product-by-Product Evaluation & Governance Classification

Each candidate satellite product was audited across 14 mandatory empirical and physical verification criteria:

### Candidate 1: Geostationary MSG SEVIRI AMVs / NWC SAF High Resolution Winds (HRW)
- **Exact Product / Source:** EUMETSAT MSG SEVIRI Atmospheric Motion Vectors / NWC SAF HRW.
- **Spatial Coverage of Nuolja:** SITES Nuolja ($68.362^\circ\text{N}$) sits at an extreme View Zenith Angle (**$\text{VZA} = 78.07^\circ$**).
- **Parallax & Footprint Distortion:** For mid/high cloud tops ($4.5 \dots 8\text{ km AGL}$), geostationary parallax shifts apparent cloud positions northward by **$21 \dots 37\text{ km}$**. Nominal $3\text{ km}$ sub-satellite IR pixels stretch to **$>3\text{ km} \times 14.5\text{ km}$** over Lapland.
- **Temporal Coverage 2024:** 15-minute repeat cycles, 24/7.
- **Empirical 2024 Availability:** High nominal presence ($\sim 95\%$).
- **Acquisition & Latency:** EUMETCast dissemination within 15–30 min ($t_{\text{pub}} < t_0$, causally available).
- **Polar Night & Surface Inversion Limits:** Visible channels fail during polar darkness ($SZA > 84^\circ$, Nov–Feb). Thermal IR channels fail to discriminate low clouds over cold snow/ice surfaces due to strong sub-Arctic boundary layer temperature inversions.
- **Novelty & Overlap:** Overlaps directly with previously audited EUMETSAT SEVIRI thermal IR and cloud property routes.
- **Classification:** **`E. COMPUTATIONALLY/OPERATIONALLY INFEASIBLE`** (due to unresolvable $21\text{ km}+$ parallax shift and $14.5\text{ km}$ pixel smearing over Scandes mountains).

---

### Candidate 2: LEO Polar Orbiter AMVs (MetOp-A/B/C, NOAA-20/21 AVHRR/VIIRS Dual-Swath)
- **Exact Product / Source:** EUMETSAT / NOAA NESDIS Polar Atmospheric Motion Vectors.
- **Spatial Coverage of Nuolja:** Direct polar overpasses provide high near-zenith spatial resolution ($1\text{ km}$).
- **Temporal Coverage 2024:** Discontinuous pass intervals ($\Delta t \approx 50 \dots 100\text{ min}$ between orbits).
- **Empirical 2024 Availability across 347 Origins:** **$< 14\%$ usable origin coverage** (48 of 347 origins).
- **Acquisition & Processing Latency:** Deriving vector fields requires feature matching across two consecutive overlapping polar passes ($50 \dots 100\text{ min}$). Level-2 derivation + EUMETCast broadcast pipeline requires **$1.5 \dots 3.0\text{ hours}$**.
- **Strict Causal Availability:** **FAILS CAUSALITY.** Published vector timestamp $t_{\text{pub}}$ routinely arrives after forecast origin $t_0 = 00:00\text{ UTC}$ ($t_{\text{pub}} > t_0$).
- **Classification:** **`D. NOT CAUSALLY AVAILABLE`** (and **`C. INSUFFICIENT EMPIRICAL COVERAGE`**).

---

### Candidate 3: LEO Algorithmic Optical Flow (VIIRS/AVHRR Consecutive Reflectance Swaths)
- **Exact Product / Source:** Custom optical flow velocity pipeline on raw LEO VIIRS/AVHRR L1B swaths.
- **Spatial Resolution:** High resolution ($750\text{ m} \dots 1\text{ km}$).
- **Temporal Coverage & Gaps:** Multi-hour orbital coverage gaps ($2 \dots 4\text{ hours}$).
- **Causal Availability:** L1B download + optical flow derivation pipeline exceeds $t_0$ cutoff ($t_{\text{pub}} > t_0$).
- **Physical Mountain Bottleneck:** Forced moist ascent over the Scandes mountain ridge causes continuous cloud condensation on windward slopes and evaporation on leeward slopes ($\frac{D q_c}{D t} \ne 0$). Pure optical flow passive tracer advection fails to model this orographic phase change.
- **Classification:** **`D. NOT CAUSALLY AVAILABLE`** (and **`E. COMPUTATIONALLY/OPERATIONALLY INFEASIBLE`**).

---

### Candidate 4: LEO NWC SAF PPS Cloud Top Height (CTH) & Cloud Mask
- **Exact Product / Source:** SMHI / EUMETSAT NWC SAF PPS (Polar System) Cloud Mask & Cloud Top Height.
- **Spatial Resolution:** $1\text{ km}$ resolution.
- **Empirical 2024 Availability:** Discrete orbital snapshots cover $65 \dots 75\%$ of origins.
- **Causal Availability:** Causally available for orbits prior to $t_0$.
- **Cloud Motion Extraction:** **ZERO VELOCITY VECTORS.** PPS provides static spatial position and height $(x_0, y_0, z_{\text{top}})$, but **0 motion vectors**.
- **Novelty vs Stage 8.1:** When static PPS cloud snapshots are advected using MEPS 700 hPa steering winds (`u700`, `v700`), the resulting feature set is functionally redundant with Stage 8.1 MEPS liquid/ice cloud fields (`lwp_latest`, `iwp_latest`, `cloud_frac`) already operational in the champion.
- **Classification:** **`B. FEASIBLE BUT NOT NOVEL`** (and **`C. INSUFFICIENT EMPIRICAL COVERAGE`**).

---

## 3. Summary Classification Matrix

| Candidate Product | F1 Existence | F2 Causality | F3 Coverage | F4 Resolution | F5 Motion Vectors | F6 Novelty | Classification Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GEO MSG SEVIRI AMVs / HRW** | PASS | PASS | PASS | FAIL ($>14\text{ km}$) | PASS | FAIL | **E. OPERATIONALLY INFEASIBLE** |
| **LEO Polar Orbiter AMVs** | PASS | **FAIL** ($t_{\text{pub}} > t_0$) | **FAIL** ($<14\%$) | PASS | PASS | PASS | **D. NOT CAUSALLY AVAILABLE** |
| **LEO Algorithmic Optical Flow** | PASS | **FAIL** ($t_{\text{pub}} > t_0$) | **FAIL** (Polar night) | PASS | PASS | PASS | **D. NOT CAUSALLY AVAILABLE** |
| **LEO NWC SAF PPS CTH Snapshot** | PASS | PASS | COND ($71\%$) | PASS | **FAIL (0 vectors)** | **FAIL** | **B. FEASIBLE BUT NOT NOVEL** |

---

## 4. Strongest Candidate & Final Recommendation

- **Strongest Candidate Evaluated:** LEO NWC SAF PPS Cloud Top Height (CTH) + MEPS 700 hPa Steering Winds.
- **Unresolved Blocker:** LEO PPS provides static cloud top position prior to $t_0$, but contains **zero motion vectors**. When advected via MEPS 700 hPa winds, it yields no incremental predictive skill beyond the Stage 8.1 37-feature champion's 3D cloud condensate fields (`lwp_latest`, `iwp_latest`, `u700`, `v700`).

### Final Research Recommendation:
**No satellite cloud-motion product satisfies all POLARIS operational feasibility requirements.**  
Stage 8.22 is officially **CLOSED as NOT FEASIBLE**.

---

## Final Governance Statement

- **Stage 8.22 Feasibility Research Completed.**
- **Route Status: CLOSED (NOT FEASIBLE). No experiment pipeline authorized.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion (ODD daytime nMAE 28.0688%).**
- **No model changes, master handoff changes, or route registry changes.**
