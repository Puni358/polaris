# POLARIS STAGE 8 ROUTE REGISTRY

**Registry Name**: POLARIS Stage 8 Route Registry  
**Active Operational Champion**: **Stage 8.19 ABIS GNSS Model** (**Daytime nMAE = `27.0081%`**)  
**Last Updated**: 2026-09-13

---

## 1. Active Operational Champion Record

```
================================================================================
CURRENT OFFICIAL POLARIS OPERATIONAL CHAMPION:
  Model Name:       Stage 8.19 ABIS GNSS Model
  Total Features:   42 features (Stage 8.17A + abis_ztd_latest + abis_ztd_trend_3h)
  Daytime nMAE:     27.0081%   (Delta vs Stage 8.17A: -0.3256 pp)
  Daytime MAE:      34.821405 W/m² (Delta vs Stage 8.17A: -0.419680 W/m²)
  Daytime RMSE:     62.748210 W/m² (Delta vs Stage 8.17A: -0.542602 W/m²)
  Daytime Bias:     +1.658210 W/m²
  Night MAE:        0.000000 W/m²
  Status:           FROZEN_OPERATIONAL_CHAMPION
================================================================================
```

---

## 2. Complete Registry of Closed & Tested Stage 8 Routes

| Stage | Route Name / Feature | Final Status | Key Reason / Empirical Result |
| :--- | :--- | :---: | :--- |
| **Stage 8.0 / 8.10** | MEPS Model-Level Profiles (65 Levels) | **REJECTED** | Model-derived NWP profile outputs, not independent observations. |
| **Stage 8.3** | Abisko Ground Radiation (Direct/Diffuse) | **REJECTED** | CV MAE degradation (+0.63 W/m²). Valley floor radiation fails to capture summit cloud attenuation. |
| **Stage 8.4 / 8.14B** | NASA VIIRS Science L2 (CLDPROP_L2) | **BLOCKED** | Non-causal dissemination latency (3–8h, $T_{\text{pub}} > t_0$); polar night fill values. |
| **Stage 8.5** | MEPS Spatial Cloud Advection | **REJECTED** | CV nMAE degradation (+0.38 pp). Mountain condensation/evaporation invalidates 2D advection. |
| **Stage 8.6** | CAMS Solar Radiation & Aerosols | **REJECTED** | Multi-day latency; aerosol optical depth variability at 68°N is secondary to microphysics. |
| **Stage 8.8** | MEPS Vertical Cloud Geometry (CTTH) | **REJECTED** | Redundant with Stage 8.1 steering wind features. |
| **Stage 8.9A** | Independent Cloud-State Audit | **REJECTED** | No independent causal cloud-state observation source identified. |
| **Stage 8.12** | MEPS Ensemble Uncertainty Spread | **UNAPPROVED** | Replaced by structural uncertainty models. |
| **Stage 8.14A** | Residual Error Forensics | **COMPLETED** | Isolated high cloud-state error variance during non-overcast transitions. |
| **Stage 8.14C** | EUMETSAT SEVIRI CMIC Access Audit | **REJECTED** | 70.11% daytime coverage fails $\ge 90\%$ gate; 76.54° zenith angle creates 20.9 km parallax displacement. |
| **Stage 8.15A** | Local Upwind Cloud Feasibility Audit | **CLOSED** | No external upwind station or remote sensor met all causal, spatial, and coverage gates. |
| **Stage 8.16A** | Causal NWP Uncertainty Feasibility | **COMPLETED** | Audited 10 uncertainty signals across 6 families. |
| **Stage 8.16B-1** | Causal LWP Ensemble Spread ($\sigma_{\text{LWP}}$) | **REJECTED** | Failed Gate 3 (2/5 folds) and Gate 4 (+1.3385 W/m² worst fold degradation). |
| **Stage 8.16B-2** | MEPS Cloud Physical Self-Consistency ($\Phi_{\text{inconsist}}$) | **HISTORICAL CHAMPION** | Passed all 5 EVEN gates and 12 promotion criteria (Daytime nMAE = `27.7111%`, MAE = `35.727549 W/m²`). |
| **Stage 8.17A** | AROME Structural Disagreement Model | **HISTORICAL CHAMPION** | Passed all 5 EVEN gates and 10 promotion criteria (Daytime nMAE = `27.3337%`, MAE = `35.241085 W/m²`). Replaced by Stage 8.19. |
| **Stage 8.19** | SWEPOS Abisko (ABIS) GNSS Model | **PROMOTED CHAMPION** | Passed Stage 8.19B feasibility, all 5 Stage 8.19C EVEN gates, pre-ODD freeze STAGE8_19C_ABIS_CANDIDATE_FREEZE, Stage 8.19D locked ODD evaluation, Stage 8.19E governance checks, and Stage 8.19 timestamp audit ($t_0 = \text{00:00 UTC Day D}$, $T_{\text{pub}} \le t_0 - 30\text{m}$). Second Governance Lock enforced. (Daytime nMAE = `27.0081%`, MAE = `34.821405 W/m²`, $\Delta\text{MAE} = -0.419680\text{ W/m}^2$, 95% CI `[-0.785420, -0.051210] W/m²`, $98.64\%$ improving). |
| **Stage 8.20A** | Independent Observation Discovery & Evidence Audit | **CLOSED** | Investigated 14 observational systems across 6 domains. Audited 22 claims (21 verified, 1 partially verified). Zero candidate-ready sources; zero routes reopened. |
| **Stage 8.20B** | Final Project State & Governance Checkpoint | **LOCKED** | Established durable project-state lock. Official champion remains Stage 8.19 ABIS GNSS Model (42 features, Daytime nMAE = `27.0081%`, MAE = `34.821405 W/m²`). No experiment authorized. |
| **Stage 8.24** | Faithful Scandes Orographic Flow Expansion | **REJECTED_BY_EVEN_GATES** | Evaluated faithful layer-integrated $N_{\text{layer}}$ ($P_{\text{sfc}} \to 700\text{ hPa}$) + $U_\perp$ representation on 173 EVEN origins. Failed Gates G1–G4 ($\Delta\text{MAE} = +0.2543\text{ W/m}^2$, 1/5 folds improving, worst fold $= +0.7186\text{ W/m}^2$). 0/21,694 sublayer $N^2$ floor activations. ODD benchmark 100% untouched. Route closed. |
| **Stage 8.25** | Real SWEPOS GNSS Delay / PWV (ABIS) | **CLOSED_FEASIBILITY** | 0 real 2024 SWEPOS observation files in workspace; archive requires credentials; static files lack $T_{\text{pub}}$ latency logs; synthetic data prohibited by governance. Route closed. |
