# POLARIS Stage 7.4 Feasibility Report: MEPS Vertical Cloud Structure Data & Causality Verification

## 1. Executive Summary
* **Recommendation**: **GO** (Stage 7.4 Data & Causality Verification PASSED).
* **Scope**: Data and causality verification ONLY. Zero forecasting experiments, zero model fitting, zero EVEN CV, zero hyperparameter tuning, zero ODD access.
* **Official Champion**: **Stage 6.6 LWP/IWP Model remains frozen and active** ($37.005888	ext{ W/m}^2$ ODD MAE).
* **Key Finding**: MEPS 13-level pressure archive contains complete, causally eligible 3D cloud water, ice, and cloud fraction profiles. The candidate vertical features exhibit genuine non-redundancy with Stage 6.6 scalar LWP/IWP ($ho pprox 0.36 \dots 0.58$), confirming that Stage 7.4 introduces new atmospheric structure.

---

## 2. Scientific Hypothesis
Stage 6.6 incorporates column-integrated scalar LWP, IWP, and total cloud fraction. Stage 7.4 tests whether the **vertical distribution** of cloud liquid, ice, and cloud fraction provides additional physical signal. Two atmospheric columns can have identical total LWP and cloud fraction, but completely different vertical profiles (e.g. low stratus vs high cirrostratus), resulting in different shortwave scattering and surface irradiance responses.

---

## 3. Exact MEPS Archive Source
* Archive: MET Norway MEPS 2.5km Deterministic Collection (`meps25epsarchive` on `thredds.met.no`).
* Primary Files: `meps_det_pl_YYYYMMDDTHHZ.ncml` (3D pressure levels) and `meps_det_sfc_YYYYMMDDTHHZ.ncml` (surface pressure).

---

## 4. Variable Inventory
Verified directly from 2024 archive headers:
* `mass_fraction_of_cloud_condensed_water_in_air_pl` ($q_l$, $	ext{kg/kg}$)
* `mass_fraction_of_cloud_ice_in_air_pl` ($q_i$, $	ext{kg/kg}$)
* `cloud_area_fraction_pl` ($	ext{CF}_k$, $0..1$)
* `mass_fraction_of_snow_in_air_pl` ($q_s$, $	ext{kg/kg}$)
* `mass_fraction_of_rain_in_air_pl` ($q_r$, $	ext{kg/kg}$)
* `air_temperature_pl` ($T_k$, $	ext{K}$)
* `specific_humidity_pl` ($q_v$, $	ext{kg/kg}$)

---

## 5. Pressure-Level Inventory
13 hydrostatic isobaric levels: `[50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000] hPa`. Ordering: Top of atmosphere ($50	ext{ hPa}$) to surface ($1000	ext{ hPa}$).

---

## 6. Nuolja Grid Verification
Grid point $y=760, x=486$ ($68.355701^\circ	ext{N}, 18.763666^\circ	ext{E}$), located $1.24	ext{ km}$ from the Nuolja station target ($68.362074^\circ	ext{N}, 18.738752^\circ	ext{E}$).

---

## 7. Causal Availability Audit
Previous-day 18:00 UTC run selected ($t_{	ext{ref}} = 	ext{D-1 18:00 UTC} < t_0$). 100.0% pass rate across all 347 clean benchmark origins. Zero future observations used.

---

## 8. Timestamp & Horizon Alignment
Forecast lead hours $H1 \dots H24$ map 1:1 onto `time[1..24]` of the MEPS run, matching target hourly timestamps exactly.

---

## 9. Surface-Aware Integration Method
Approximated 13-level vertical integration truncated strictly at model surface pressure ($p_{	ext{sfc}} pprox 938.5 \dots 954.0	ext{ hPa}$) with linear boundary interpolation at $p_{	ext{sfc}}$, zeroing out subterranean $1000	ext{ hPa}$ mass.

---

## 10. Proposed Vertical Feature Candidate Set (8 Features)
1. `f_lwp_low`: Lower atmosphere LWP fraction ($p > 800	ext{ hPa}$)
2. `f_lwp_mid`: Mid-level atmosphere LWP fraction ($500 \le p \le 800	ext{ hPa}$)
3. `f_lwp_high`: Upper atmosphere LWP fraction ($p < 500	ext{ hPa}$)
4. `p_centroid_lwp`: Liquid water mass-weighted pressure centroid ($	ext{hPa}$)
5. `p_centroid_iwp`: Ice water mass-weighted pressure centroid ($	ext{hPa}$)
6. `dp_ice_liquid_centroid`: Liquid-ice vertical separation distance ($	ext{hPa}$)
7. `cloud_frac_mid`: Mid-level cloud area fraction ($500 \le p \le 800	ext{ hPa}$)
8. `cloud_frac_high`: High-level cloud area fraction ($p < 500	ext{ hPa}$)

---

## 11. Physical Interpretation
* `f_lwp_low` vs `f_lwp_high` distinguishes thick boundary layer clouds from elevated cirrus.
* `p_centroid_lwp` captures cloud base/top height in pressure space.
* `dp_ice_liquid_centroid` measures mixed-phase Arctic cloud stratification.

---

## 12. Novelty Relative to Stage 6.6
Spearman rank correlation analysis demonstrates genuine non-redundancy:
* `f_lwp_low` vs total LWP: $ho = 0.581$ (42% unshared rank variance)
* `f_lwp_high` vs total LWP: $ho = 0.525$ (72% unshared rank variance)
* `p_centroid_lwp` vs total LWP: $ho = -0.521$
* `cloud_frac_high` vs total cloud fraction: $ho = 0.363$ (87% unshared rank variance)

---

## 13. Missing / Invalid Data Audit
* Missing values: 0
* Physical validity: $0 \le 	ext{LWP} \le 3000	ext{ g/m}^2$, $0 \le 	ext{cloud\_frac} \le 1.0$, $800 \le p_{	ext{sfc}} \le 1050	ext{ hPa}$. 100% clean.

---

## 14. Computational Feasibility
* Origins: 347 origins $	imes$ 24 hours $= 8,328$ rows.
* Architecture: Resumable multi-threaded extraction with persistent JSON checkpointing.
* Estimated Extraction Time: $pprox 12 \dots 18$ minutes over 4 worker threads.

---

## 15. Risks and Limitations
* Discrete 13-level vertical resolution is an approximation of continuous atmospheric profiles.
* Extraction requires network calls to MET Norway THREDDS; handled via rate-limiting retries and persistent checkpointing.

---

## 16. GO / NO-GO Decision
**GO** — MEPS vertical cloud structure is verified as available, causally clean, complete, and non-redundant with Stage 6.6 scalars.

---

## 17. Recommendation for Stage 7.4 Experiment
Proceed to Stage 7.4 forecasting experiment ONLY after explicit authorization. Maintain Stage 6.6 as frozen operational champion and ODD as 100% locked.
