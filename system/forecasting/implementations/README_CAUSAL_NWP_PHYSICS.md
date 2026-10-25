# Research-Only Causal NWP + Physics Solar Forecaster

## Overview

The `CausalNwpPhysicsForecastEngine` (`system/forecasting/implementations/causal_nwp_physics.py`) is an isolated research-only forecasting engine developed for closed-loop benchmark design in the POLARIS research harness.

It provides a 100% causal solar irradiance and generation forecast across a 24-hour horizon ($t+1 \dots t+24$) by coupling causal numerical weather prediction (NWP) cloud trajectories with deterministic clear-sky radiation physics.

---

## Governance & Compliance Disclaimers

> [!WARNING]
> **RESEARCH BASELINE ONLY — NOT AUTHORIZED FOR PRODUCTION**
> 1. **Research Assumption Only**: This module implements a baseline physical attenuation assumption for causal benchmark exploration. It is **NOT** physically validated against empirical pyranometer observations.
> 2. **No Empirical Parameter Tuning**: No parameter tuning, regression, or fitting has been performed. The historical Stage 4 empirical attenuation coefficient ($k_h \approx 0.50$) is **NOT** used.
> 3. **Stage 8.1 Untouched**: This implementation does **NOT** modify, replace, or alter frozen Stage 8.1 models, artifacts, hashes, or evaluation datasets.
> 4. **Production Governance Preserved**: Production forecasting engines and routers remain completely untouched.

---

## Formulation

### 1. Astronomical Clear-Sky Model
Using `pvlib.location.Location` configured for the Nuolja research station ($68.362074^\circ\text{N}$, $18.738752^\circ\text{E}$, elevation $702.0\text{ m}$, UTC timezone), the engine computes:
- Deterministic solar position (elevation angle $\theta_{\text{elev}}$ in degrees).
- Clear-sky global horizontal irradiance ($GHI_{\text{cs}}$ in $\text{W/m}^2$) via the Ineichen clear-sky radiation model.

### 2. Night-Time Physical Zeroing
Polar night and diurnal night hours are strictly enforced:
$$\text{if } \theta_{\text{elev}} \le 0.0^\circ \quad\text{or}\quad GHI_{\text{cs}} \le 0.0\text{ W/m}^2 \implies \text{forecast\_GHI} = 0.0\text{ W/m}^2$$

### 3. Clear-Sky Attenuation
For daytime steps ($\theta_{\text{elev}} > 0.0^\circ$ and $GHI_{\text{cs}} > 0.0\text{ W/m}^2$):
$$\text{cloud\_fraction} = \frac{\text{fc\_cloud\_cover}}{100.0}$$
$$\text{forecast\_GHI} = \max\left(0.0, \, GHI_{\text{cs}} \times (1.0 - \text{cloud\_fraction})\right)$$

### 4. Authorized D3 Engineering PV Transformation
Following the authorized POLARIS D3 governance decision:
$$\text{raw\_power} = \text{forecast\_GHI} \times 300\text{ m}^2 \times 0.20 \times 0.85 = \text{forecast\_GHI} \times 51.0$$
$$\text{solar\_generation} = \min(\text{raw\_power}, \, 60000.0\text{ W})$$

### 5. D1/D2 Degenerate Interval Representation
In conformance with POLARIS governance decisions D1 and D2:
$$\text{lower} = \text{point} = \text{upper}$$
for both `solar_irradiance` and `solar_generation`.

---

## Causal Firewall & Fail-Closed Validations

The engine enforces strict causal boundary conditions:

| Check | Condition | Failure Mode |
|---|---|---|
| **Causal Firewall** | Ground-truth observations or actual $SW_{\text{IN}}$ detected in `runtime_context` (e.g. `actual_SW_IN`, `ground_truth`, `future_actuals`) | `PermissionError` |
| **Missing MEPS** | Missing `fc_cloud_cover` / `meps_cloud_cover` trajectory in `runtime_context` | `ValueError` |
| **Horizon Check** | Trajectory length $\ne 24$ | `ValueError` |
| **Bounds Validation** | Cloud cover $< 0.0$ or $> 100.0$ (or fraction $< 0.0$ or $> 1.0$) | `ValueError` |
| **NaN / Inf Check** | Trajectory contains `NaN` or `Inf` values | `ValueError` |
| **Timestamp Alignment** | Target timestamps in `runtime_context` do not match expected $t+1 \dots t+24$ UTC | `ValueError` |

---

## Usage Example

```python
from pathlib import Path
from system.schemas.station_state import StationState
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine

# Initialize engine
engine = CausalNwpPhysicsForecastEngine()

# Current station state at forecast origin t0
station_state = StationState(
    timestamp="2024-06-20T23:00:00Z",
    battery_soc_pct=75.0,
    battery_energy_wh=15000.0,
    diesel_running=False,
    diesel_hours_running=0.0,
    last_observed_solar_irradiance=0.0,
    last_observed_demand=12000.0,
    last_observed_wind_generation=5000.0
)

# MEPS 18Z cloud trajectory (24 hourly steps for t+1 ... t+24)
runtime_context = {
    "fc_cloud_cover": [20.0, 15.0, 10.0, ..., 35.0]  # 24 steps
}

# Generate compliant ForecastBundle
bundle = engine.predict(station_state, runtime_context)
```

---

## Test Suite

The test suite in `system/tests/test_causal_nwp_physics.py` covers 13 test cases:
- **Test A**: 24-hour output shape.
- **Test B**: Timestamp alignment ($t+1 \dots t+24$ strictly monotonic UTC).
- **Test C**: Night-time zeroing during polar night and diurnal night.
- **Test D**: Zero cloud cover ($cf = 0$) matches clear-sky irradiance.
- **Test E**: 100% cloud cover ($cf = 1$) produces zero irradiance.
- **Test F**: Negative cloud cover fails closed (`ValueError`).
- **Test G**: Cloud cover $> 100\%$ fails closed (`ValueError`).
- **Test H**: NaN / Inf values fail closed (`ValueError`).
- **Test I**: Missing MEPS forecast or horizon $\ne 24$ fails closed (`ValueError`).
- **Test J**: Causal firewall blocks actual $SW_{\text{IN}}$ / ground-truth (`PermissionError`).
- **Test K**: Deterministic repeatable execution.
- **Test L**: `ForecastBundle` v1.0 schema compliance and JSON roundtrip.
- **Smoke Test**: Real-data verification on 2024 MEPS weather forecast dataset.
