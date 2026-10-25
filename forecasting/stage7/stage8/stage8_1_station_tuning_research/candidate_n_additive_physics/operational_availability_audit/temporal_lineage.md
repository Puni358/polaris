# POLARIS Candidate N6 — Source-to-Feature Temporal Lineage & Timestamp Rules

**Document Version:** 1.0.0  
**Status:** READ-ONLY OPERATIONAL CAUSALITY AUDIT ARTIFACT  
**Governing Status:** winner: null (Strictly Non-Production)  
**Date:** 2026-10-17  

---

## 1. Architectural Overview & Temporal Horizon Semantics

The POLARIS Candidate N6 model operates on a strictly defined **24-hour ahead receding-horizon schedule** for microgrid energy management and battery reserve allocation.

### 1.1 The Operational Cutoff Timestamp ($t_0$)
- **Nominal Dispatch Origin ($t_0$):** $00:00:00\text{ UTC}$ of operational day $T$ (`forecast_start`).
- **Decision Cutoff Constraint:** Every input observation, NWP forecast field, and intermediate baseline prediction required by the 36-feature vector must be physically and cryptographically available on the inference host prior to $t_0 = 00:00:00\text{ UTC}$.
- **Target Horizons ($h = 1, 2, \dots, 24$):**
  $$\text{Valid Timestamp } t_v(h) = t_0 + (h - 1) \text{ hours}$$
  Specifically:
  - Horizon $h=1 \implies t_v = 00:00\text{ UTC}$ (immediate hour)
  - Horizon $h=2 \implies t_v = 01:00\text{ UTC}$
  - $\dots$
  - Horizon $h=24 \implies t_v = 23:00\text{ UTC}$ (closing hour of Day $T$).

This explicit index-to-valid-time mapping ($t_v = t_0 + (h - 1)$) was formally certified in `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v2.md` and independently audited across all 17,064 rows in `CANDIDATE_F_SUCCESSOR_DATASET_V2_INDEPENDENT_AUDIT.md`.

---

## 2. Temporal Lineage Across the Four Source Classes

The 36 features of Candidate N6 originate from four distinct physical and computational pipelines:

```
+-------------------------------------------------------------------------------------------------+
|                                    OPERATIONAL CUTOFF t0                                        |
|                                       00:00:00 UTC                                              |
+-------------------------------------------------------------------------------------------------+
        |                               |                                |               |
        v                               v                                v               v
[Class 1: Astronomical]      [Class 2: Telemetry]             [Class 3: NWP 18Z]     [Class 4: Baseline]
Ephemeris & Topography       Nuolja SITES [t0-24, t0)         MET Norway meps_det_pl  Stage 4 Clean
Deterministic / Static       Zero Future Contamination        Nominal Init D-1 18Z    Chronos-2 + Ineichen
Features: 1-5, 24-27         Features: 10-23                  Features: 6-9, 28-33,36 Features: 34-35
(9 PASS)                     (14 UNPROVEN - unlogged live)    (11 UNPROVEN - latency) (2 UNPROVEN)
```

---

### Class 1: Astronomical Ephemeris & Static Topography (9 Features) — VERDICT: PASS

These features depend solely on fixed site coordinates (Nuolja Middle Station: $68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, elevation 385 m a.s.l.), orbital mechanics, and static digital elevation models (DEM).

1. **`month` (Feature 1):** $\text{month}(t_v) \in \{1, \dots, 12\}$. Known a priori.
2. **`hour` (Feature 2):** $\text{hour}(t_v) \in \{0, \dots, 23\}$. Known a priori.
3. **`solar_elevation` (Feature 3):** Computed via the Solar Position Algorithm (SPA / pvlib). Deterministically calculated for coordinate $(\phi, \lambda)$ at valid time $t_v$.
4. **`solar_zenith` (Feature 4):** $\theta_z = 90^\circ - \alpha_{\text{elev}}$.
5. **`clearsky_ghi` (Feature 5):** Modeled global horizontal irradiance under aerosol-free and cloud-free conditions via the Ineichen-Perez model parameterized with climatological Linke turbidity $T_L(m)$:
   $$GHI_{\text{cs}} = f(\alpha_{\text{elev}}, T_L, \text{altitude})$$
6. **`terrain_horizon_elevation_deg` (Feature 24):** Derived from the Lantmäteriet 50 m Digital Elevation Model. Ray-tracing from the Nuolja pyranometer coordinates across 360 azimuth angles yields the local horizon elevation profile $\theta_{\text{horizon}}(\psi_{\text{az}})$. Evaluated at the solar azimuth $\psi_{\text{az}}(t_v)$.
7. **`terrain_elevation_margin_deg` (Feature 25):** 
   $$\Delta \theta = \alpha_{\text{elev}}(t_v) - \theta_{\text{horizon}}(\psi_{\text{az}}(t_v))$$
8. **`terrain_solar_obstruction_flag` (Feature 26):**
   $$\mathbf{1}_{\{\Delta \theta \le 0^\circ\}}$$
9. **`clearsky_ghi_terrain_adjusted` (Feature 27):** If obstructed ($\Delta \theta \le 0$), direct beam radiation $DNI \cdot \sin(\alpha) = 0$, preserving only terrain-scattered diffuse irradiance:
   $$GHI_{\text{cs, terrain}} = \begin{cases} GHI_{\text{cs}} & \text{if unshaded} \\ DHI_{\text{cs}} & \text{if shaded} \end{cases}$$

**Temporal Lineage Rule:** Deterministic forward calculation. Available infinitely prior to $t_0$. Zero temporal leakage.

---

### Class 2: Station Telemetry Context Metrics (14 Features) — VERDICT: UNPROVEN

All 14 context features (`ctx_*`) characterize the historical short-term optical state of the local atmosphere over the immediate station pyranometer.

- **Temporal Observation Window:** Strictly backward-looking:
  $$[t_0 - 24\text{ h}, t_0) = [D-1\ 00:00\text{ UTC}, D\ 00:00\text{ UTC})$$
- **Mathematical Lineage:**
  - `ctx_std_3h`: $\sigma(SW_{\text{in}}[t_0 - 3\text{h} : t_0])$
  - `ctx_std_6h`: $\sigma(SW_{\text{in}}[t_0 - 6\text{h} : t_0])$
  - `ctx_std_12h`: $\sigma(SW_{\text{in}}[t_0 - 12\text{h} : t_0])$
  - `ctx_std_24h`: $\sigma(SW_{\text{in}}[t_0 - 24\text{h} : t_0])$
  - `ctx_abs_change_1h`: $|SW_{\text{in}}(t_0 - 1\text{h}) - SW_{\text{in}}(t_0 - 2\text{h})|$
  - `ctx_abs_change_3h`: $|SW_{\text{in}}(t_0 - 1\text{h}) - SW_{\text{in}}(t_0 - 4\text{h})|$
  - `ctx_abs_change_6h`: $|SW_{\text{in}}(t_0 - 1\text{h}) - SW_{\text{in}}(t_0 - 7\text{h})|$
  - `ctx_max_diff_6h`: $\max_{k} |SW_{\text{in}}(t_0 - k\text{h}) - SW_{\text{in}}(t_0 - (k+1)\text{h})|$ for $k \in \{1..5\}$
  - `ctx_mean_diff_6h`: $\frac{1}{5} \sum_{k=1}^5 |SW_{\text{in}}(t_0 - k\text{h}) - SW_{\text{in}}(t_0 - (k+1)\text{h})|$
  - `ctx_slope_6h`: Ordinary least squares linear trend of $SW_{\text{in}}$ over the trailing 6 hours.
  - `ctx_kt_std_6h`: $\sigma(k_t[t_0 - 6\text{h} : t_0])$ where $k_t = \min(1.5, \max(0, SW_{\text{in}} / GHI_{\text{cs}}))$
  - `ctx_last_obs`: Last recorded station measurement $SW_{\text{in}}(t_0 - 1\text{h})$
  - `ctx_mean_24h`: $\mu(SW_{\text{in}}[t_0 - 24\text{h} : t_0])$
  - `ctx_max_24h`: $\max(SW_{\text{in}}[t_0 - 24\text{h} : t_0])$

**Temporal Causality Analysis:**
- *Causal Window Integrity:* No target values from $t \ge t_0$ enter any formula. Zero label leakage.
- *Operational Ingestion Bottleneck:* In the research repository, these values were derived from **retrospective annual Level 2 files** (`SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`) downloaded months after the calendar year closed. The repository contains **no real-time telemetry streaming daemon, log, or timestamped buffer** demonstrating that live 10-minute pyranometer readings were ingested into POLARIS at $t_0 - 5\text{ min}$.
- *Verdict:* Causally valid by mathematical definition, but **UNPROVEN** as an operational real-time feed.

---

### Class 3: MEPS NWP 18Z Cycles & Upper-Atmospheric Microphysics (11 Features) — VERDICT: UNPROVEN

Candidate N6 avoids the fatal zero-lead leakage of Candidate F by shifting exclusively to the **prior-day 18:00 UTC MEPS forecast cycle** ($D-1\ 18\text{Z}$).

#### 3.1 Prior-Day 18Z Initialization & Source Lead Mapping
- **NWP Model:** MetCoOp Ensemble Prediction System (MEPS), deterministic run (`meps_det_pl`).
- **Initialization Time ($t_{\text{init}}$):** Day $D-1$ at $18:00:00\text{ UTC}$ ($t_0 - 6\text{ hours}$).
- **Target Valid Time:** $t_v(h) = t_0 + (h - 1)\text{ hours}$.
- **Source Lead Time Calculation:**
  $$\text{lead}(h) = t_v(h) - t_{\text{init}} = (t_0 + (h - 1)) - (t_0 - 6) = 5 + h\text{ hours}$$
- **Coverage Range:**
  For horizons $h \in [1, 24]$, required source leads span **lead 6 through lead 29**.
  Since MEPS trajectories extend to lead 66, all 24 horizons are covered within the single 18Z run.

#### 3.2 Individual Features
- **`fc_cloud_cover` (Feature 6):** Total cloud cover (0–100%) from Open-Meteo `previous_day1` seamless extraction.
- **`fc_temperature_2m` (Feature 7):** Surface temperature.
- **`fc_relative_humidity_2m` (Feature 8):** Surface relative humidity.
- **`cloud_frac` (Feature 9):** Normalized cloud area fraction:
  $$\text{cloud}\_\text{frac} = \frac{\text{fc}\_\text{cloud}\_\text{cover}}{100.0}$$
- **`u700`, `v700` (Features 28, 29):** Zonal and meridional winds at $700\text{ hPa}$ (pressure level index 8 of 13) extracted from `meps_det_pl_{YYYYMMDD}T18Z.ncml` via OPeNDAP:
  $$\text{lead} \in [7, 30] \implies \text{leads 6 to 24 populated; horizons 20..24 are NaN due to lead-19 convention}.$$
- **`lwp_18z_fc`, `iwp_18z_fc` (Features 30, 31):** Cloud liquid water path and ice water path at $700\text{ hPa}$ ($[\text{g/m}^2]$), mapped via `cache_lead6_v2` ($h=1$) and `cache_full_acquisition` ($h=2..24$).
- **Interactions (Features 32, 33, 36):**
  - `lwp_x_cloud_18z` = $\text{lwp}\_\text{18z}\_\text{fc} \times \text{cloud}\_\text{frac}$
  - `elevation_x_cloud_frac` = $\text{solar}\_\text{elevation} \times \text{cloud}\_\text{frac}$
  - `elevation_x_transition_cloud` = $\text{solar}\_\text{elevation} \times \mathbf{1}_{\{0.2 \le \text{cloud}\_\text{frac} < 0.6\}}$

#### 3.3 Latency & Publication Gap (The Critical 18Z Blocker)
- Nominal MEPS run initialization: $18:00\text{ UTC}$.
- Provider operational benchmark (MetCoOp, 2024): General forecast dissemination requires approximately **135 minutes (2h15m)** after analysis, yielding nominal availability around **20:15 UTC** ($3\text{h}45\text{m}$ ahead of the $00:00\text{ UTC}$ cutoff).
- **The Operational Evidentiary Gap:**
  - Neither MET Norway's THREDDS server nor the POLARIS repository preserves contemporaneous HTTP headers (`Last-Modified`, `Date`) or download access logs recording the exact minute when `meps_det_pl` NetCDF files became readable during 2024 or 2025.
  - Pressure-level products (`pl`) are computationally heavy and may experience publishing delays exceeding the surface tier.
  - MET Norway historical incident records (e.g. 2020-01-13) confirm operational delays frequently stall dissemination for hours.
- *Verdict:* **UNPROVEN**. While temporally plausible with a positive 3.75-hour nominal margin, timely operational availability cannot be proven without contemporaneous ingestion logs.

---

### Class 4: Stage 4 Clean Baseline Conditioning (2 Features) — VERDICT: UNPROVEN

1. **`pred_stage4_clean` (Feature 34):**
   $$pred_{\text{stage4, clean}}(h) = \max\left(0.0,\ w_h \cdot pred_{\text{stage3b, cloud, nwp}}(h) + (1.0 - w_h) \cdot phys_{\text{pred, clean}}(h)\right)$$
   where:
   $$phys_{\text{pred, clean}}(h) = \max\left(0.0,\ GHI_{\text{cs}}(h) \cdot (1.0 - k_h \cdot \text{cloud}\_\text{frac}(h))\right)$$
   - $(w_h, k_h)$ are frozen parameters strictly fitted on 2024-EVEN (`stage4/stage4_results/ensemble_parameters.json`, SHA-256 `26cfbd19...`).
   - Zero 2025 target contamination occurs.
2. **`clean_attenuation` (Feature 35):**
   $$clean_{\text{attenuation}}(h) = GHI_{\text{cs}}(h) - pred_{\text{stage4, clean}}(h)$$

**Temporal Causality Analysis:**
- *Chronos-2 Dependency:* `pred_stage3b_cloud_nwp` requires zero-shot / fine-tuned Chronos-2 transformer inference conditioning on prior weather and GHI history up to $t_0$.
- *Operational Gap:* Stage 3b was executed as an offline batch computation. No operational deployment logs exist recording the inference execution time of Chronos-2 before $00:00\text{ UTC}$.
- *Verdict:* **UNPROVEN** (inherits the unproven operational latency of Stage 3b Chronos-2 and MEPS 18Z `cloud_frac`).

---

## 3. Strict Prohibitions & Anti-Leakage Invariants

1. **No Target Leakage:** Columns `actual_SW_IN`, `actual_ghi`, and `residual_target` are strictly excluded from the inference matrix.
2. **No Future Horizon Cross-Talk:** Each row $h$ is evaluated strictly at valid time $t_v(h)$. No centered rolling windows, backward fills, or smoothing across horizon steps are permitted.
3. **Fail-Closed Policy:** Missing or late features must raise `InputValidationError` and reject dispatch rather than substituting zeros or synthetic interpolations.
