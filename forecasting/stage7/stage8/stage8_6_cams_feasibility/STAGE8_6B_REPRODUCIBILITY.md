# Stage 8.6B Reproducibility Statement

* **Script:** `run_stage8_6b_experiment.py`
* **Execution Timestamp:** 2026-09-12T15:57:20.151871+00:00
* **Control Model:** Stage 8.1 Champion (37 features: Base 28 + LWP/IWP + Terrain + U700 + V700)
* **Candidate Model:** Stage 8.6B CAMS (39 features: 37 + AOD550 + TCWV)
* **Origins Evaluated:** 174 EVEN origins (Forward-Chaining 5-Fold CV)
* **ODD Evaluation:** **UNTOUCHED (0 ODD reads / metrics / predictions)**
* **Random Seed:** 42 (`HistGradientBoostingRegressor`)
* **Control MAE Reproduction:** 37.620054 W/m² (Expected: 37.620054 W/m², Error: 0.000000 W/m²)
