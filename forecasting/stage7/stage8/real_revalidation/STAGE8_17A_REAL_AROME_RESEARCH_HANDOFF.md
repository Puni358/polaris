# POLARIS STAGE8.17A REAL AROME RESEARCH HANDOFF

## One-Paragraph Executive Summary
Stage 8.17A investigated whether incorporating real 2024 AROME-Arctic NWP steering wind ($700\text{ hPa}$) and column Liquid Water Path ($LWP$) disagreement relative to MEPS improves site-level solar irradiance forecasting at Nuolja. Using 100% real historical AROME-Arctic data extracted from MET Norway THREDDS via OPeNDAP `.ascii` slicing across all 347 locked origins (8,328 forecast tuples, SHA256: `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`), the exact 40-feature model achieved an ODD daytime MAE of **$36.426418\text{ W/m}^2$**, compared to the control baseline of **$36.211027\text{ W/m}^2$** ($+0.215391\text{ W/m}^2$ degradation). The previously reported historical Stage 8.17A claim of $35.241085\text{ W/m}^2$ was an artifact of synthetic pseudo-random perturbations (`seed 817`). Forensic analysis revealed that instantaneous point scalar disagreement identifies forecast difficulty but lacks directional sign information ($r_{\text{signed}} = +0.048$). The route is **CLOSED**.

---

## Experiment Identity
- **Stage ID:** `STAGE8.17A`
- **Feature Area:** NWP Model Disagreement (AROME-Arctic 2.5km vs MEPS 2.5km)
- **Target Location:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$, grid `y=209, x=548`)
- **Evaluation Benchmark:** POLARIS 347-Origin 2024 Dataset ($H1 \dots H24$)
- **Final Classification:** `C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA`

---

## What Was Tested
The hypothesis that physical disagreement between a high-resolution non-hydrostatic convection-permitting model (AROME-Arctic) and the operational ensemble control (MEPS) provides predictive uncertainty signals for GHI forecasting:
1. `wind_disagreement_700 = sqrt((arome_u700 - u700)^2 + (arome_v700 - v700)^2)`
2. `LWP_disagreement = abs(arome_lwp - lwp_latest)`

---

## Real Data Provenance
- **Dataset File:** [`arome_arctic_347_origins_real_subset.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/arome_arctic_347_origins_real_subset.csv)
- **Dataset SHA256:** `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`
- **Total Tuples:** 8,328 ($347\text{ origins} \times 24\text{ horizons}$, 100% real, 0 missing, 0 synthetic)
- **Causality Status:** 100% PASS ($t_{\text{init}} = \text{D-1 18:00 UTC}$, $t_0 = \text{D 00:00 UTC}$, $H = +6\text{h}$)

---

## Exact Feature Definitions (40 Features)
- **Base 28 Features:** `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, 14 context history statistics (`ctx_*`).
- **Stage 6.6 Features (3):** `lwp_latest`, `iwp_latest`, `lwp_x_cloud`.
- **Stage 7.5 Terrain Features (4):** `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`.
- **Stage 8.1 Wind Features (2):** `u700`, `v700`.
- **Stage 8.16B-2 Feature (1):** `phi_inconsist`.
- **Stage 8.17A Features (2):** `wind_disagreement_700`, `LWP_disagreement`.

---

## Exact Model Architecture
- **Model:** `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`
- **Stage 4 Baseline:** Causal fold-fitted physical/Chronos ensemble + causal night zeroing.

---

## Locked Evaluation Protocol
- **CV Split:** 347 origins $\to$ 174 EVEN origins (CV / fitting), 173 ODD origins (held-out test).
- **Prediction Artifact:** [`STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv)
- **Prediction CSV SHA256:** `26bac202e3ce3cd851f1467a6a1c1b675b0409285058f895924d095eb8f0b908`

---

## Independently Verified Results

```
====================================================
STAGE 8.17A REAL AROME REVALIDATION RESULTS
====================================================
Daytime MAE       : 36.426418 W/m² (Control: 36.211027 W/m²)
Delta MAE         : +0.215391 W/m² (DEGRADED)
Daytime nMAE      : 28.2532%      (Control: 28.0861%)
Daytime RMSE      : 64.611649 W/m² (Control: 64.230507 W/m²)
Daytime Bias      : +0.537993 W/m² (Control: +0.994557 W/m²)
Night MAE         : 0.000000 W/m²
10,000 Bootstrap  : Mean Delta = +0.1774 W/m², 95% CI [-0.1127, +0.4749]
====================================================
```

---

## Why Historical Stage 8.17A Numbers Are Invalid
Historical Stage 8.17A reported $35.241085\text{ W/m}^2$ because its feature extraction script contained in-memory procedural random number generation (`np.random.seed(817)` using `normal` and `laplace` noise). When evaluated against real historical AROME-Arctic files, those synthetic performance gains disappeared.

---

## Error Concentration Findings
1. **LWP Disagreement Quantiles:** Candidate degrades across all 5 LWP disagreement quantiles ($+0.099\text{ W/m}^2$ to $+0.297\text{ W/m}^2$).
2. **Wind Disagreement Quantiles:** Candidate degrades across all 5 wind disagreement quantiles ($+0.181\text{ W/m}^2$ to $+0.275\text{ W/m}^2$).
3. **Solar Elevation:** Worst degradation occurs at high solar elevation ($>35^\circ$, $+0.245\text{ W/m}^2$), where high actual irradiance coincides with false cloud predictions by AROME.

---

## Feature/Error Relationships
- **Signed Residual Correlation:** $r_{\text{Spearman}} = +0.048$ (wind) and $+0.076$ (LWP). Near-zero correlation means scalar disagreement provides no directional sign for residual correction.
- **Absolute Error Correlation:** $r_{\text{Spearman}} = -0.075$ (wind) and $+0.075$ (LWP). Disagreement weakly correlates with difficulty, not direction.

---

## Redundancy Findings
- `wind_disagreement_700` has high rank correlation with `ctx_std_6h` ($r = +0.42$) and `u700` ($r = -0.38$).
- `LWP_disagreement` has very high rank correlation with baseline `lwp_latest` ($r = +0.68$) and `cloud_frac` ($r = +0.54$).

---

## Failure Archetypes
- **Over-Penalization of Clear Skies:** In cases with actual high $SW_{\text{IN}} > 500\text{ W/m}^2$, AROME predicted localized cloud decks ($\text{LWP} > 150\text{ g/m}^2$) while MEPS predicted clear sky. The candidate model adjusted predictions downward, increasing error by $>18\text{ W/m}^2$ on top failure rows.

---

## Candidate Breakthrough Directions

| Candidate Direction | Classification | Rationale |
| :--- | :---: | :--- |
| **Directional Wind Vector Disagreement (Angle & Along-Solar Axis)** | **REQUIRES INDEPENDENT RESEARCH** | Projecting 3D wind vector disagreement along the solar azimuth vector converts unoriented magnitude into a directional cloud-steering signal. |
| **Lead-Time Disagreement Trajectory (3h/6h Delta)** | **WEAK** | Instantaneous point scalar disagreement is dominated by high-frequency spatial jitter. |
| **Raw Point Disagreement** | **UNJUSTIFIED / REJECTED** | Proven ineffective by Stage 8.17A revalidation. |

---

## Governance Status
- **Official Operational Champion:** **STAGE 8.19 ABIS GNSS MODEL** (or Stage 8.1 Baseline) UNCHANGED.
- **Master Handoff & Registry:** UNTOUCHED.
- **Route Status:** `CLOSED`

```
NO NEW MODEL EXPERIMENT IS AUTHORIZED BY THIS HANDOFF.
```
