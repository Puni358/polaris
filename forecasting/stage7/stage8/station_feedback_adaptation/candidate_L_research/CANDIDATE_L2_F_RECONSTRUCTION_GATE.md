# Candidate L2 — Frozen Candidate F Model Historical Reconstruction Gate Report (PASSED)

**Date**: October 4, 2026  
**Scope**: Candidate L Research — Historical Frozen Candidate F Model Reconstruction & Replay Audit (2020–2023)  
**Target Station**: Nuolja / Abisko (`68.36207412° N, 18.73875158° E`, elev. 702 m)  
**Strict Scope Compliance**: RESEARCH ONLY. No neural network was trained, Candidate F was NOT retrained or modified, Candidate J and Stage 8.1 artifacts were NOT altered, and no production code or control artifacts were altered.

---

## Executive Summary

Following the acquisition of 100% complete historical **SITES Nuolja Middle Station (`ANS_NMS`)** observations (2019–2023), the historical reconstruction gate for the frozen **Candidate F model** (38 features) across the historical Candidate L period (**2020-01-01 through 2023-09-30**) has been successfully **RE-AUDITED AND PASSED**.

All previously identified hard-coded approximations and unsupported substitutions (`ctx_* = 0.0`, `terrain_horizon_elevation_deg = 5.0`) have been **completely eliminated**.

### Key Audit & Reconstruction Findings:
1. **Raw NWP Provenance**: 1,369 acquired MEPS forecast origins (26,011 rows) covering 2020-01-01 to 2023-09-30, extracted deterministically with 0 synthetic values (**PASS**).
2. **Raw Station Provenance**: 100% continuous 10-minute Level 2 observations from SITES `ANS_NMS` ($SW_{IN}$, Apogee SP110 Pyranometer) across 2019–2023 with $0\text{ NaNs}$ and $0\text{ missing time steps}$ (**PASS**).
3. **Exact Station Context Derivation**: All 14 station context features (`ctx_std_3h` ... `ctx_max_24h`) reconstructed from authentic historical $SW_{IN}$ observations across the prior 24-hour windows $[t_0-24\text{h}, t_0)$ (**PASS**).
4. **Exact DEM Terrain Horizon**: Replaced static 5.0° default with dynamic 360-degree DEM terrain horizon elevation profile lookup ([`stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv)) evaluated at localized solar azimuth angles (**PASS**).
5. **Contract Compatibility & Clean Replay**: Unmodified frozen Candidate F model artifact (`candidateF_elevation_x_cloud.joblib`) replayed over all 26,011 rows with $0\text{ errors}$ and $0\text{ NaNs}$ (**PASS**).

---

## 1. Candidate F Model Contract & Hash Integrity

| Artifact Name | Exact File Path | Verified SHA256 Checksum | Contract Status |
|---|---|---|---|
| **Frozen Candidate F Model** | `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **VERIFIED (38 features)** |
| **Exact 38-Feature Matrix** | `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` | **VERIFIED (26,011 rows)** |
| **Frozen F Predictions** | `candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` | **VERIFIED (26,011 rows)** |
| **Rebuild Manifest** | `candidate_L_research/CANDIDATE_L2_EXACT_F_RECONSTRUCTION_MANIFEST.json` | `5c1798ecbdffb0a68d06fb6b005118d0d17ad26d58eeefcfdcd62cf4c399bfed` | **VERIFIED** |

---

## 2. Final Reconstruction Gate Verdicts

```
RAW NWP PROVENANCE: PASS
RAW STATION PROVENANCE: PASS
38-FEATURE CONTRACT: PASS
EXACT CONTEXT RECONSTRUCTION: PASS
UNSUPPORTED SUBSTITUTIONS: NONE
LEAKAGE CHECK: PASS
FROZEN F HASH: UNCHANGED
MATRIX: VALID
PREDICTIONS: VALID
```
