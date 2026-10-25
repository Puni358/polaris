# POLARIS STAGE 8.0 — MEPS MODEL-LEVEL FEASIBILITY & CAUSALITY REPORT

## Executive Summary
This report documents the rigorous data-engineering, archive-verification, causality, and novelty audit conducted under Stage 8.0 for the POLARIS benchmark at SITES Nuolja (68.362°N, 18.739°E).

## Key Verification Results
1. **Archive Verification:** 347/347 D-1 18Z forecast origins verified for `meps_det_sfc` and `meps_det_pl`.
2. **Model-Level Archive Claim:** **DISPROVED FOR 18Z**. The 2024 `meps25epsarchive` does NOT contain 18Z `meps_det_ml` runs (0/347). Only 00Z runs exist (347/347).
3. **Causality Audit:** Surface and pressure-level variables pass 100% causal check at D-1 18Z ($t_{\text{ref}} < t_0$). Model-level variables fail 18Z causality due to missing files.
4. **Cloud Base / Top Altitude:** Available in 100% of origins in `meps_det_sfc`. Requires fill-value masking ($9.96921 \times 10^{36}$).
5. **700 hPa Steering Wind:** Available in 100% of origins in `meps_det_pl`. Clean physical vectors representing free-atmosphere cloud advection.

## Governance & Champion Status
- **Official Operational Champion:** **STAGE 7.5 TERRAIN/HORIZON MODEL** (Held-out ODD MAE: **36.613571 W/m²**, nMAE: **28.3983%**).
- **Forecasting Experiment:** **NOT RUN**.
- **CV / Model Training:** **NOT RUN**.
- **ODD Target Access:** **NO**.
