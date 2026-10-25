# POLARIS Stage 8.0 — Free-Atmosphere Steering Wind Audit

## 1. Physical Rationale & Distinction from Stage 5.4
- **Stage 5.4 Experiment (Failed):** Tested 10m surface winds ($U_{10}, V_{10}$). Surface winds over mountain terrain (Nuolja, 675m) are heavily distorted by steep local topography, boundary-layer turbulence, and valley channelling.
- **700 hPa Free-Atmosphere Steering Wind ($U_{700}, V_{700}$):** 700 hPa pressure level (~3,000 m a.s.l.) sits cleanly above mountain boundary-layer friction. It represents synoptic cloud steering flow that transports cloud decks over Torneträsk valley.

## 2. Availability & Technical Feasibility
- **Product:** `meps_det_pl_YYYYMMDDTHHZ.ncml` (Pressure levels).
- **18Z Causal Availability:** **347 / 347 (100.0%)** origins available at D-1 18Z.
- **Data Quality:** Clean floats in m/s, zero fill values, zero NaNs.
- **Extraction Speed:** Instantaneous via OpenDAP slice.

## 3. Candidate Features Proposed
1. $U_{700}$: 700 hPa Eastward wind component (m/s)
2. $V_{700}$: 700 hPa Northward wind component (m/s)
3. $\text{WS}_{700} = \sqrt{U_{700}^2 + V_{700}^2}$: 700 hPa Steering wind speed (m/s)
4. $\text{WD}_{700} = \text{atan2}(-U_{700}, -V_{700})$: 700 hPa Steering wind direction (degrees)
