# POLARIS — FINAL RESEARCH AUDIT

## Purpose

Single handover record of the POLARIS/SIH solar-irradiance forecasting
research. Upload this file to another AI and ask it to audit the work,
find weaknesses, challenge conclusions, or identify genuinely new room
for improvement.

> This is a consolidated audit of the project checkpoints. Where later
> forensic work corrected an earlier interpretation, the later
> interpretation is used.

# 1. Locked benchmark

**Site:** SITES Nuolja, ~68.36°N, 18.74°E  
**Target:** 2024 hourly reconstructed SITES `SW_IN` (W/m²), derived from
10-minute station observations. The hourly target represents the
preceding 60-minute period.  
**Task:** previous 24 hourly observations → next 24 hourly SW_IN values,
H1–H24.  
**Origins:** 347 clean origins; 8,328 forecast hours.  
**Split:** even-indexed origins = development/training; odd-indexed
origins = sealed ODD.  
**t0:** 00:00 UTC; H1=00:00 UTC, H24=23:00 UTC. Station timezone
Europe/Stockholm.

Night forecasts are causally forced to zero using solar elevation \<=0
or clear-sky GHI ==0; future actuals are never used.

NWP values require both issuance \<=t0 and valid time inside the
forecast horizon. No future-NWP ffill/bfill.

**Primary metric:** daytime nMAE = daytime MAE / mean daytime actual
×100%. MAPE is not used.

## Promotion gates

- G1: aggregated ΔMAE \<= -0.50 W/m²
- G2: \>=4/5 folds improved
- G3: maximum fold degradation \<= +0.50 W/m²
- G4: nMAE \<= control AND RMSE \<= control
- G5: causal availability/parser compliance
- G6: exact control reproduction / frozen-control verification

ODD firewall is absolute.

# 2. Official champion

## Stage8.1 — 37-feature HGB + 700 hPa wind steering

**Official reproducible ODD champion**

- daytime MAE: **36.188657 W/m²**
- daytime nMAE: **28.0688%**
- RMSE: **64.219495 W/m²**
- bias: **+1.439399 W/m²**
- night MAE: **0**
- ODD rows: 4,152
- daytime rows: 1,939

Prediction artifact:
`stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv`

SHA256:
`213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`

**Status: PROTECTED CHAMPION.**

# 3. Baselines and model routes

| Experiment                                            | Result / status                                  |
|-------------------------------------------------------|--------------------------------------------------|
| Seasonal Naive                                        | 42.76% nMAE                                      |
| Persistence                                           | 95.99%                                           |
| Chronos-2 zero-shot univariate                        | 41.91%                                           |
| Chronos-2 + historical weather                        | 42.14%                                           |
| TimesFM 3.0                                           | 66.87%                                           |
| Moirai 2.0 R-small                                    | 82.69%                                           |
| Direct raw-kt Chronos                                 | 50.32%; unconstrained future-kt route prohibited |
| Stage3B Chronos + solar geometry + future total cloud | 41.06%; best pure-neural route                   |

## Stage4 physics ensemble

Horizon-Adaptive Cloud-Damped Clear-Sky Ensemble: - ODD MAE 43.4508 -
nMAE 33.70% - RMSE 74.8530 - bias -1.9716 - night MAE .3242

Stage4.1 isotonic: 45.22 / 35.07%, rejected.  
Stage4.2 affine: 44.08 / 34.19%, rejected.  
Stage4.3 dynamic-state blend: no robust improvement.  
Stage4.4 hard-weather audit: \>150 W/m² errors were 210 hours per split,
~35.8% of total absolute error.  
Stage4.5 residual ACF: lag1 +.6665, lag2 +.4041, lag3 +.2513, lag24
+.0352; no operational gain.  
Stage4.6 causal residual audit: no leakage, no robust improvement.

## Stage5 residual correction

Stage5.1 amplitude/volatility calibration: degraded.

Stage5.2 Architecture A GBDT residual corrector: - ODD MAE 39.0848 -
nMAE 30.32% - RMSE 68.9935 - bias +1.9347 - EVEN 5-fold: Stage4 40.7822
→ candidate 39.4236, Δ=-1.3587 - top features: `ctx_std_6h`,
`clearsky_ghi`, `cloud_frac`, `pred_stage4_fold`, `ctx_slope_6h`

Stage5.3/5.4 supported an **information-bottleneck hypothesis** related
to spatial/temporal cloud representation. Do not call this a proven
irreducible ceiling.

# 4. Stage6 information routes

**MEPS ensemble spread:** 30 members, 249,840 tuples. `meps_std_SW_IN`
vs absolute residual Spearman +.7685, but direct GBDT integration ΔMAE
+.0457. Rejected.

**Satellite thermal IR:** MET Norway archive; VIIRS M15/M16 and
AVHRR4/5. 347/347 origins, 334 valid obs. EVEN 39.4525 vs 39.4236,
Δ+.0290. Rejected.

**Deterministic MEPS revisions:** 4 latest eligible pre-t0 runs, 8
features, 1,388 files, 69,400 tuples. EVEN 39.1579 vs 39.4236, Δ-.2657,
but only 3/5 folds improved and one degraded beyond limit. Rejected.

**Snow/cloud:** Δ+.3033. Rejected.

**LWP/IWP:** pressure levels 50–1000 hPa; surface-aware hydrostatic
integration, exact surface truncation, below-ground exclusion. Features
`lwp_latest`, `iwp_latest`, `lwp_x_cloud`. 347×24, no missing. EVEN
38.2806 vs 39.4236, Δ=-1.1430; passed gates. Frozen ODD: MAE 37.005888,
nMAE 28.7026%, RMSE 65.671702, bias +1.144965. Later forensic audit
showed these were per-horizon valid values, not a simple t0 snapshot, so
the “novel route” interpretation must be treated cautiously.

# 5. Stage7

**Native MEPS radiation:** verified, no diffuse field; integration
worsened. Rejected.

**kt reformulation:** raw MAE 36.3828, but nMAE 40.46 vs control 40.39.
Rejected.

**Vertical cloud structure:** no improvement. Rejected.

**Terrain/horizon:** Copernicus DEM GLO-30; 360°, 1° azimuth, 25 km
rays, Earth curvature. Max horizon +29.80° WSW, min -1.80°, mean
+9.5954°, median +4.0660°. SVF 0.942228; terrain factor .057772.
Corrected ODD MAE 36.613571, nMAE 28.3983%, RMSE 65.347064, bias
+1.307778. Bootstrap mean Δ=-.397063, CI \[-.791521,+.001941\], 97.43%
negative. Became intermediate champion before Stage8.1.

# 6. Stage8 feature-space research

**8.1 700 hPa U/V steering:** became official champion.

**8.2 observability audit:** corrected claims around VIIRS/NWC; Abisko
dataset/direct-diffuse variables verified.

**8.3 Abisko direct/diffuse:** control 35.069059, candidate 35.696286,
Δ+.627227; nMAE +1.0033pp; 1/5 improved. Rejected.

**8.4 VIIRS feasibility:** SNPP 90/347, NOAA20 135/347, NOAA21 0/347,
union 225/347=64.84%; causal acquisition 346/347; quality-valid 346/347;
optical COT/CER 225/347. Standard science L2 had ~3–13h publication
latency, so operational causal availability was 0/347. Conditional only.

**8.5 MEPS spatial cloud summaries:** causal D-1 18Z, 14 scalar spatial
features. Strict control 35.270823, candidate 35.085741, Δ-.185082, but
nMAE +.3772pp and 2/5 improved. Rejected. Important: scalar summaries
discarded topology.

**8.6 CAMS AOD/TCWV:** causal D-1 12Z, 347/347 and 8,328 tuples. EVEN
37.620054 → 37.867306, Δ+.247252; 3/5 improved. Rejected.

**8.7 DNI proxy:** 49.445841 vs 37.620054, Δ+11.825787, 0/5 improved.
Rejected.

**8.8 cloud base/top:** 35.270823 → 35.417182, Δ+.14636, 2/5 improved.
Rejected.

**8.9A cloud-state/motion feasibility:** closed.

**8.10A true MEPS model-level condensate:** D-1 18Z archive 0/347; D-1
00Z 347/347 but longer lead; D-0 00Z post-t0 by ~3.25h.
Conditional/timing-limited.

**8.11A LWP/IWP forensic audit:** confirmed Stage6.6 was per-horizon
valid information, not t0 snapshot.

**8.17A real AROME revalidation:** 347×24 real tuples. Nearest Nuolja
AROME y209,x548, ~1.007 km. Real LWP from
`mass_fraction_of_cloud_condensed_water_in_air_pl`, surface-aware
integration. Dataset SHA
`db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a96195995948ceec298`.

40-feature candidate: Stage8.1 37 + LWP/IWP + terrain + wind +
`wind_disagreement_700` + `LWP_disagreement`.

EVEN control 44.718895 → candidate 44.553480, Δ-.165414, all 5 gates.  
ODD control 36.211027 → candidate 36.426418; nMAE 28.0861→28.2532%; RMSE
64.230507→64.611649; bias +.994557→+.537993. Bootstrap mean +.177449, CI
\[-.1127,+.4749\], only 11.81% improving. **Rejected.**

**8.19 ABIS ZTD/GNSS:** synthetic invalid route. Closed.

**8.21A 3D cloud–solar slant path:** EVEN Δ-.0285, 2/5 improved.
Rejected.

**8.22 satellite motion:** closed.

**8.23 local surface state:** all candidates failed.

**8.24 faithful orographic flow:** worse; EVEN-only and not comparable
to ODD. Rejected.

**8.25 real SWEPOS GNSS:** unavailable. Closed.

**Phase8:** feature-space research complete/closed.

# 7. Phase9 error forensics

After normalizing origin keys and timestamp parsing:

- foundation-model data had 365 full-year origins, but matched-173
  diagnostics were used for ODD comparison.
- H12 was worst: MAE 64.837218, RMSE 101.007472, bias -14.747066.
- H9–H12 produced 52.0% of absolute error while representing 37.4% of
  daytime observations.
- worst 10% origins = 32.1% of H9–H12 error; worst 5% = 17.8%.
- 59% of origins underestimated H9–H12; 41% overestimated; median origin
  bias -1.6.
- H9–H12 seasonal MAE/bias: April 64.9/-41.3; May 106.3/-43.4; June
  124.1/+13.5; July 92.9/-9.2; August 75.3/-.1; September 76.9/+3.3.
  Nov–Feb \<25.
- realised future irradiance volatility correlated with H9–H12 MAE at
  r≈+.726 (diagnostic only).
- top 10% errors = 46.6% of total absolute error, concentrated H9–H15
  Apr–Sep.
- HGB37 won every horizon except H1/H23/H24 in matched ODD ranking.
- no exploitable error diversity in the existing model inventory.

Phase9 candidates: - calendar: rejected - cross-model disagreement:
\|HGB–dynamic hybrid\| vs absolute error r=.41; signed Pearson -.12;
Spearman -.07; diagnostic only - NWP cloud volatility: ΔMAE -.29, 3/5
improved; failed G1/G2; closed

`PHASE9_NO_ROBUST_IMPROVEMENT_FOUND`

# 8. Phase10 architecture research

Architecture audit found 347×24 matrix, 173 EVEN/174 ODD, 14 static
context features constant across horizons, and HGB has no temporal
coupling/shared multi-task structure.

**Candidate B — shared small MLP + horizon embedding** - reconstructed
EVEN control MAE 26.3668, RMSE 55.2513, bias -.1291, nMAE 20.4507 -
candidate MAE 26.0112, RMSE 54.2820, bias -2.7713, nMAE 20.1750 - ΔMAE
-.3556 - fold deltas: -2.0731,+1.2593,+.1486,-1.2084,+.0839 - 2/5
improved, max degradation +1.2593 - G1/G2/G3 failed; rejected

**Candidate A — BiGRU** - \[B,24,39\] → Dense39→32 → BiGRU16/dir →
Dense - 6,113 parameters - Adam 1e-3, wd 1e-4, MAE, batch8, max300,
patience20, seed42, GroupKFold5 by origin, train-fold-only scaling -
EVEN OOF MAE 54.7022, RMSE 126.5499 - fold MAEs
53.0343,46.8871,45.4633,69.3759,59.3008 - 0/5 improved; rejected

**Candidate C — disagreement-gated residual MLP** - frozen Stage4
anchor; 39 standardized features - Dense39→16, gate + magnitude heads,
674 parameters - candidate MAE 27.0940 vs paired control 26.4522;
Δ+.6418 - RMSE 56.1025 vs 55.2715 - bias -.6006 vs +.124 - 1/5 improved;
max degradation +2.1096 - G1–G4 failed; G6 unverified; ODD untouched -
rejected

**Phase10 closed.**

# 9. Spatial/AROME research

AROME-Arctic: MET Norway THREDDS, ~2.5 km, 739×949, 00/06/12/18 cycles,
standard +66h, off cycles +36h. Surface fields include
total/high/medium/low cloud, LWP, IWP, SW, 10m U/V, 2m T/RH, surface
pressure; 13 pressure levels and 65 hybrid levels.

For t0=00Z, D-1 18Z is causally eligible, published ~20:15–20:45,
roughly 3.25–3.75h before t0.

### Initial spatial sweep

Invalid: synthetic sin/cos/ramp inputs, unused anchor, missing
xarray/netCDF4/cfgrib. Excluded from scientific conclusions.

### Real 21×21 control

Reproducible HGB control: - total MAE 25.639318 - total RMSE 54.369219 -
total bias -5.043934 - proper daytime MAE 47.451469 - proper daytime
nMAE 36.8045% - proper daytime RMSE 74.376601 - daytime bias -8.863007 -
night MAE .672516 - 173 EVEN origins, 4,152 predictions, no
duplicates/NaNs

Prediction SHA:
`b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`

Control script SHA:
`dfa69828303342d65c38f10ef890b6328541eca343cfd9d689033430e45a72a7`

Freeze JSON SHA:
`a3c56ed184874e284e3b1d934c38317bfad6b41207e737779b0978074f502b06`

**Important:** 19.8865% from total MAE/daytime normalizer is NOT
official nMAE. Do not compare it to 28.07%.

### Real 21×21 spatial candidate

Candidate total MAE 31.3268 vs control 25.6393, Δ+5.6875.

Proper daytime: - MAE 58.107798 - nMAE 45.0698% - RMSE 85.2543 - bias
-5.1555

Fold daytime deltas: +21.822,+12.369,+9.769,+1.101,+8.190; 0/5 improved.

Valid EVEN experiment, rejected; ODD sealed.

### Spatial information audit

Real AROME spatial information is substantial: - SW spatial std mean
17.65 W/m² - SW range mean 65.57 - SW gradient ~13.38 W/m²/cell -
directional asymmetry ~1.04–1.84 - adjacent-horizon SW correlations
\>.79 - 10m wind \>.92 - apparent cloud translation ~1.96 km/h - LWP
apparent translation ~4.48 km/h

Absolute-error associations: - SW range ρ=.653 - SW std .6281 - SW
gradient .6242 - SW mean .6238 - SW center .5949 - 10m wind gradient
-.2526 - cloud gradient .1873 - cloud std .1771 - cloud center -.0634

Conclusion: **strong spatial information exists**, but association does
not imply forecasting gain.

### Topology-preserving CNN

Input \[B,24,11,21,21\]. No pooling. Center, 3×3 and 7×7 branches;
GRU64→32; context38→32; head; 48,273 parameters.

Synthetic north-vs-south sanity: - old pooled difference 0 - new
architecture .689553

Real candidate: - daytime MAE 63.286275 vs control 47.451469,
Δ+15.834806 - nMAE 49.0864% vs 36.8045% - RMSE 92.363659 vs 74.376601 -
bias -8.6352 vs -8.8630 - fold deltas
+15.92,+17.55,+22.15,+12.39,+11.09 - 0/5 improved

**Rejected.** Raw topology preservation alone was not enough.

### 3×3 local-spatial preregistered model

Input 3×3×11 + 38 tabular + horizon embedding; 15,633 params.

Candidate: - daytime MAE 50.471940 vs control 47.451469, Δ+3.020471 -
nMAE 39.1473 vs 36.8045 (+2.3428pp) - RMSE 78.0695 vs 74.3766 - bias
-8.460 vs -8.863 - fold deltas -.1447,+5.1428,+6.2674,+4.3883,-.5914 -
2/5 improved

**Rejected; route CLOSED.**

Registry SHA:
`7d2114c13eb9c95d7b1eaa6d02dcc2cbedc9cb21482d2ba841b102ec463c130b`

# 10. Cloud motion / trajectory diagnostics

### Simple causal cloud-advection diagnostic

- valid cloud motion 3005/4152 = 72.4%
- mean apparent displacement 1.63 km/h
- 10m wind 16.40 km/h; angular disagreement 79.3°
- 700hPa wind 40.67 km/h; disagreement 79.1°

Upstream cloud vs absolute error: - H1–H3 ρ=-.3024, p=.0034 - H4–H6
ρ=-.344, p=5.7e-7 - H7–H12 ρ=-.1593, p=7.5e-6 - H13–H18 ρ=-.0535,
p=.128 - H19–H24 ρ=+.0249, p=.653

Random-direction ρ=-.1077; real 700hPa upstream ρ=-.1075.

**Classification: C — WEAK / INCONCLUSIVE.**

### Trajectory consistency

Persistence NCC .5206, MAE .1050.  
Estimated translation NCC .5058, MAE .1128.  
10m wind NCC .4259.  
700hPa NCC .2818, MAE .1844.  
Random displacement NCC .1449, MAE .2220.

677 cloud blobs: - reached station 240 (35.45%) - dissipated 255
(37.67%) - missed 182 (26.88%)

Translation error vs SW error ρ=.1434; persistence .1503.

Conclusion: rigid translation does not beat persistence; cloud fields
form, dissipate and deform.

# 11. Causal state-aliasing audit

Question: how much do future SW_IN trajectories diverge for nearly
identical causal states?

173 EVEN origins, 4,152 rows, ODD sealed, no training/new data/new
features.

32D state from H1 of existing 37-feature matrix; observation context +
solar/season + causal NWP/cloud/microphysics/terrain/wind. Model outputs
and future prediction outputs excluded.

k=5 nearest-neighbour trajectory RMSE: **75.10 W/m²** vs random
**~144.37**, ratio .5202.

Horizon-wise NN mean absolute divergence peaked at: - H11: **127.16
W/m²** - H12: 123.82 - H10: 108.65 - H13: 106.04

Conditional IQR peaked ~122–125 W/m² around H11–H12.

Forecast error association: - Pearson r=.6606, p=4.8e-21 - Spearman
ρ=.7496, p=1.41e-29 - N=157 usable origins

High-solar analysis was corrected to use **peak trajectory clear-sky
GHI**, not t0 GHI (t0 was midnight). Top quartile \>=644 W/m², 40
origins; NN trajectory RMSE 145.68. Month-matched null was nearly
identical at H11.

**Classification: C — WEAK / INCONCLUSIVE STATE-ALIASING.**

Caveats: - verify H1 row is fully causal - distance may be dominated by
solar/season features - month-matched null weakens the apparent
advantage - high-solar sample is small - divergence is not proof of
causality

# 12. Corrected local-spatial state audit

Earlier audit had methodological overclaims. Corrected v2 used nested
OLS incremental R².

Classification: **B — PARTIAL / HORIZON-CONDITIONAL INFORMATION.**

Grouped incremental R² from local spatial layers:

- H1–H3: L2 +.0037, L3 +.0022, L4 +.0012, L5 +.0012
- H4–H6: L2 +.0106, L3 +.0014, L4 +.0019, L5 +.0002
- H7–H12: L2 +.0059, L3 +.0011, L4 +.0004, L5 +.0010
- H13–H18: L2 +.0135, L3 +.0009, L4 +.0006, L5 +.0001
- H19–H24: L2 +.0140, L3 +.0025, L4 +.0016, L5 +.0002

FDR-supported individual horizons:
H2,H5,H6,H8,H10,H13,H17,H19,H20,H22,H23.

Borderline: H9,H15,H18,H21.

Real 3×3 cloud vs random patch: ρ=.1895 vs .1749; difference .0146, CI
\[-.0388,+.0644\] — inconclusive.

Conclusion: local spatial information is real but modest and
horizon-dependent.

# 13. State-to-trajectory dynamics audit

Final diagnosis: **C — WEAK / INCONCLUSIVE transition-dynamics
limitation.**

173 EVEN origins; 147 usable daytime trajectories; 26 had no daylight
and were excluded only from transmission diagnostics.

Major-transition origins: - +22.8 W/m² higher total daytime MAE than
no-transition origins - bootstrap CI +12.1 to +32.7

Major-transition MAE: - pre-event 43.3 - during 47.9 - post-event 64.3

H7–H12 association: - Spearman ρ=.460 - FDR q=.00125

Simple event detector did not establish reliable timing-error causality.

**Sequence-model route CLOSED.**

Governance: ODD NO; training NO; new features NO; new data NO; champion
unchanged.

# 14. Literature-supported interpretation

Literature reviewed included work showing that cloud growth/dissipation,
formation/evolution and regime-dependent cloud motion matter for
intraday solar forecasting (e.g. Carpentieri et al. 2023/2024, Roy et
al. 2022, cloud-track/advection and regime-dependent forecasting
studies).

The literature supports: - cloud evolution matters - rigid advection is
limited - trajectory uncertainty is meaningful - spatial/cloud
information can help

It does NOT prove: - a POLARIS irreducible error floor - that a
particular CNN/GRU/Transformer will improve POLARIS - that spatial NWP
automatically beats point features - that transitions are the sole cause
of H7–H12 error

# 15. What the entire experiment history tells us

1.  Generic foundation models are weaker than domain-specific supervised
    models.
2.  Many additional scalar weather variables are redundant or unhelpful.
3.  Strong error diagnostics do not guarantee point-forecast
    improvement.
4.  Satellite information can be unusable because of causal publication
    latency.
5.  Real AROME spatial structure exists.
6.  Scalar spatial summaries discard topology.
7.  Topology-preserving CNNs nevertheless failed badly.
8.  Rigid cloud advection does not beat persistence.
9.  BiGRU/MLP architecture changes did not rescue performance.
10. Future cloud evolution appears important, especially H7–H15, but the
    causal mechanism remains unproven.
11. State aliasing is plausible but weak/inconclusive.
12. Therefore, more arbitrary feature/model sweeps are not justified.

# 16. Important corrections / anti-mistakes

- **Never** compare total-MAE/daytime-normalizer percentages with
  official daytime nMAE.
- EVEN is for development; ODD is locked evaluation.
- EVEN-only results are not ODD evidence.
- Synthetic spatial runs are invalid evidence.
- Availability is not causal availability.
- Statistical association is not forecasting gain.
- Do not call the current error an “irreducible ceiling.”
- Do not reopen closed routes without a genuinely new
  hypothesis/information source.
- Never use future actuals for night masking or any causal feature.
- Never silently mix different frozen controls (e.g. 35.069059,
  37.620054, 38.280605, 44.718895); state exactly which development
  protocol produced a number.

# 17. Final route status

| Route                                      | Status                                          |
|--------------------------------------------|-------------------------------------------------|
| Stage8.1 37-feature HGB + 700hPa wind      | **OFFICIAL CHAMPION**                           |
| Stage4 ensemble/calibration                | Rejected                                        |
| Stage5 residual correction                 | Superseded                                      |
| MEPS spread                                | Rejected                                        |
| Thermal satellite                          | Rejected                                        |
| NWP revisions                              | Rejected                                        |
| LWP/IWP                                    | Frozen historical route; later forensic overlap |
| Native radiation / kt / vertical cloud     | Rejected                                        |
| Terrain/horizon                            | Strong intermediate route                       |
| Abisko direct/diffuse                      | Rejected                                        |
| VIIRS                                      | Conditional, not operationally causal           |
| MEPS spatial summaries                     | Rejected                                        |
| CAMS AOD/TCWV                              | Rejected                                        |
| DNI / cloud geometry                       | Rejected                                        |
| Real AROME point candidate                 | ODD rejected                                    |
| 3D slant path                              | Rejected                                        |
| Local surface / GNSS / orographic flow     | Rejected/closed                                 |
| Phase8                                     | **CLOSED**                                      |
| Phase9                                     | **CLOSED**                                      |
| Shared MLP                                 | Rejected                                        |
| BiGRU                                      | Rejected                                        |
| Disagreement-gated MLP                     | Rejected                                        |
| Phase10                                    | **CLOSED**                                      |
| Raw spatial CNN                            | Rejected                                        |
| Local 3×3 model                            | Rejected / closed                               |
| Cloud advection                            | Weak/inconclusive; closed                       |
| State aliasing                             | Weak/inconclusive                               |
| Trajectory dynamics                        | Weak/inconclusive                               |
| Forecast uncertainty + energy optimization | **Recommended next strategic direction**        |

# 18. Recommended next move

Do **not** immediately train another Transformer/GRU/CNN.

Keep the official champion and investigate whether the
difficult-transition signal should become an **uncertainty/risk signal
for energy optimization**.

Potential system-level actions: - preserve extra battery reserve when
irradiance confidence is low - avoid optimistic solar assumptions -
schedule diesel backup conservatively - defer flexible loads under high
forecast-risk conditions - use robust/risk-aware optimization

This does not require pretending that the forecaster can perfectly
predict cloud evolution.

A future forecasting experiment should only reopen when it introduces
genuinely new information or a genuinely new representation, with: -
pre-registered hypothesis - causal data audit - frozen champion
reproduction - G1–G6 gates - no ODD access before promotion

# 19. Known important artifact hashes

Official ODD prediction:
`213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`

AROME dataset:
`db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a96195995948ceec298`

Spatial control prediction:
`b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`

Spatial control script:
`dfa69828303342d65c38f10ef890b6328541eca343cfd9d689033430e45a72a7`

Spatial freeze JSON:
`a3c56ed184874e284e3b1d934c38317bfad6b41207e737779b0978074f502b06`

Topology-preserving freeze JSON:
`363aaab5635b6e67437ddd592bfeb280bedd15b4cfde61bf86bf1def6c629335`

Topology-preserving script:
`b425cfaa59155b0c65f3d4ec13769de61826b584ea59b10866a58ac87c9eecd4`

Trajectory-consistency JSON:
`4453cc46430811ac6d60f65fb70445a23f83b7e0a4f856f6453e9fc403d3bee9`

Local-spatial v2 MD:
`fca953f9bc036d557f6565ebd6db11cf9e07930c7cb184615fa6b8d46ab689e2`

Local-spatial v2 JSON:
`7ddb4855e533a445c3bdb1ad911d4284451384cc71ee101e768671d4760631fb`

Local-spatial registry:
`7d2114c13eb9c95d7b1eaa6d02dcc2cbedc9cb21482d2ba841b102ec463c130b`

State-to-trajectory dynamics MD:
`5e400ff85ee09ba530124b2e239fe6902c69d893e63a7db09d468f60dc9649df`

State-to-trajectory dynamics JSON:
`7034aa67f82743d07c0d56f105bcea719e8d754f20f469314c22ec80e147b1ec`

# 20. Prompt for the next AI

> You are auditing POLARIS using this document as the complete research
> record. Be hostile but fair. Reconstruct the benchmark, causal rules,
> EVEN/ODD governance, official champion, every major experiment and its
> rejection reason. Identify internal inconsistencies, possible leakage,
> invalid comparisons, premature route closures and unsupported claims.
> Challenge the information-bottleneck hypothesis. Do not recommend
> generic model swaps unless they add a genuinely new mechanism or
> information source. Search current literature when useful, especially
> polar/high-latitude solar forecasting, cloud evolution, spatial NWP,
> satellite nowcasting, uncertainty-aware forecasting and energy
> optimization. For every proposed new experiment give: hypothesis,
> mechanism, causal data source, exact representation, model, split,
> metrics, G1–G6 gates, failure condition, and why it is genuinely
> different from prior failed routes. Finally answer: (A) what was done
> right, (B) what was wrong, (C) what remains unexplored, (D) the single
> highest-value next experiment, and (E) whether forecasting research
> should stop while uncertainty-aware energy optimization becomes the
> focus.

# FINAL BOTTOM LINE

The project did not establish that 28.07% nMAE is a hard physical limit.

It did establish that the strongest current point forecast is the
Stage8.1 37-feature HGB + 700hPa wind model, and that a large number of
additional features, spatial representations and architecture changes
failed robust promotion.

The best-supported working hypothesis is:

**POLARIS is likely limited by the information and representation
available at t0 about future cloud evolution, rather than by a simple
lack of model capacity.**

That hypothesis remains falsifiable.

**Forecasting research status: CLOSED pending genuinely new information
or a scientifically distinct hypothesis.**

**Recommended system-level direction: uncertainty-aware energy
management built around forecast difficulty, especially cloud-transition
regimes.**
