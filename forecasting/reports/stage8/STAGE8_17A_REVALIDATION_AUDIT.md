# STAGE8.17A Revalidation Audit

## Forensic Audit Summary
- **Historical Reported Metric:** MAE 35.241085 W/m², nMAE 27.3337%, RMSE 63.290812 W/m², Bias +1.810421 W/m²
- **Current Executable Baseline (Stage8.1, 37 features):** MAE 36.188657 W/m², nMAE 28.0688%, RMSE 64.219495 W/m²
- **Delta:** +0.947572 W/m² MAE

## Root Cause Analysis
Historical Stage8.17A reported metrics relied on a 40-feature set incorporating AROME wind disagreement (700 hPa) and LWP disagreement. However, neither the 40-feature extraction code nor the raw AROME netCDF files nor the 4152-row prediction artifact were preserved in the repository.

Executing the surviving pipeline yields the 37-feature Stage8.1 baseline (36.188657 W/m² MAE).

## Provenance Conclusion
- **STAGE8.17A STATUS:** `STAGE8.17A = NOT RECONSTRUCTABLE`
- **Classification:** Historical reported numbers (35.241085 MAE) remain UNVERIFIED REFERENCE ONLY. They cannot be used as an authoritative benchmark without verified input lineage and prediction tables.
