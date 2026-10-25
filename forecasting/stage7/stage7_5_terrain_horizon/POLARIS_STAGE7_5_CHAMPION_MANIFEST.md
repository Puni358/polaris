# POLARIS STAGE 7.5 CHAMPION MANIFEST

**Status:** `FROZEN_OFFICIAL_OPERATIONAL_CHAMPION`  
**Stage:** Stage 7.5 Terrain / Horizon Radiative Geometry  
**Previous Champion:** Stage 6.6 LWP/IWP Model ($37.005888\text{ W/m}^2$ ODD MAE)  
**Date Frozen:** September 12, 2026  

---

## 1. Operational Champion Summary

The **Stage 7.5 Terrain Model** is the official operational champion for surface shortwave radiation forecasting in POLARIS. It augments the frozen 31-feature Stage 6.6 LWP/IWP model with four pre-specified Copernicus DEM 30m terrain/horizon features:
1. `terrain_horizon_elevation_deg`
2. `terrain_elevation_margin_deg`
3. `terrain_solar_obstruction_flag`
4. `clearsky_ghi_terrain_adjusted`

Total Feature Count: **35 Features**.

Model Architecture: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`

---

## 2. Authoritative Held-Out ODD Benchmark Performance

- **Held-Out Test Set**: 173 ODD origins ($4,152$ forecast hours, $2,883$ daytime hours, $1,269$ night hours)
- **Daytime MAE**: **$36.613571\text{ W/m}^2$** (down from $37.005888\text{ W/m}^2$, $\Delta\text{MAE} = -0.392318\text{ W/m}^2$)
- **Daytime nMAE**: **$28.3983\%$** (down from $28.7026\%$, $\Delta\text{nMAE} = -0.3043\text{ pp}$)
- **Daytime RMSE**: **$65.347064\text{ W/m}^2$** (down from $65.671702\text{ W/m}^2$, $\Delta\text{RMSE} = -0.324638\text{ W/m}^2$)
- **Daytime Bias**: **$+1.307778\text{ W/m}^2$**
- **Night MAE**: **$0.000000\text{ W/m}^2$**

---

## 3. Paired Origin-Level Bootstrap (10,000 Resamples)

- **Mean $\Delta\text{MAE}$**: $-0.397063\text{ W/m}^2$
- **95% Confidence Interval**: $[-0.791521, +0.001941]\text{ W/m}^2$
- **Fraction of Bootstrap Samples with $\Delta\text{MAE} < 0$**: $97.43\%$

### Official Scientific Interpretation
> "Stage 7.5 achieved a lower held-out ODD error than Stage 6.6, improving nMAE from 28.70% to 28.40%. The improvement is directionally consistent, but the paired bootstrap confidence interval narrowly includes zero, so the gain should be described as an observed held-out improvement rather than statistically significant."

---

## 4. Physical Novelty & Governance

- **Physical Mechanism**: Incorporates static 360-degree local terrain horizon geometry derived from Copernicus DEM 30m out to $25\text{ km}$ radius around Mt. Nuolja (max horizon angle $+29.80^\circ$ at azimuth $252^\circ$). Corrects false direct clear-sky irradiance predictions during low-angle solar elevation transitions.
- **Deterministic Feature**: `clearsky_ghi_terrain_adjusted` is a deterministic geometric transformation of existing clear-sky GHI, not an independent observational source.
- **Governance Locks**: Zero tuning on ODD, zero feature selection on ODD, zero hyperparameter adjustments on ODD, zero Stage 4 refitting.
