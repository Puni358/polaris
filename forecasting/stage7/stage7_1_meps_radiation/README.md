# POLARIS Stage 7.1 — MEPS Native Surface Shortwave Radiation Verification

## Objective
This directory contains the authoritative, empirical data and causality verification for **Stage 7.1: MEPS Native Surface Shortwave Radiation Diagnostics**.

Before building feature extractors or conducting experiments, Stage 7.1 establishes whether the exact MEPS radiation-scheme variables exist in the 2024 MEPS archive, determines their exact NetCDF metadata and accumulation semantics, audits their causality across all 347 clean POLARIS origins, and investigates discrepancies with multi-LLM research reports.

## Locked Benchmark Protocol Rules Enforced
- **Zero Model Training**: No model (HistGradientBoosting or otherwise) trained.
- **Zero CV**: No cross-validation executed.
- **Zero ODD Access**: The 173 ODD benchmark test origins were **never loaded, read, or evaluated**.
- **Champion Frozen**: The Stage 6.6 LWP/IWP champion (ODD daytime nMAE = 28.7026%, MAE = 37.0059 W/m²) remains completely unmodified.

## Key Findings & Recommendation
- **Gate Recommendation**: **GO**
- **Verified Variables**: `surface_downwelling_shortwave_flux_in_air` (Instantaneous W/m²) and `integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time` (Accumulated W s/m²) are fully verified, grid-aligned, and 100% causally eligible across all 347 benchmark origins.
- **Accumulation Semantics**: `integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time` accumulates continuously from forecast reference time ($H=0$). Converting to hourly mean flux ($W/m^2$) for lead hour $H_k$ requires:
  $$\text{Hourly SW\_IN}(H_k) = \frac{\text{acc}(H_k) - \text{acc}(H_{k-1})}{3600}$$
- **Gemini Report Discrepancy**: Gemini claimed MEPS provides a diffuse shortwave component (`surface_diffuse_downwelling_shortwave_flux_in_air`). Our forensic audit of the 2024 MEPS surface archive proves **this variable does NOT exist**.
- **Novelty**: Confirmed 100% NEW relative to the frozen Stage 6.6 31-feature manifest (Stage 6.6 used 3D cloud liquid/ice microphysics, not surface radiation scheme outputs).

## Artifact Directory Inventory
- `README.md`: Overview and usage instructions.
- `meps_radiation_variable_inventory.json`: Full JSON inventory of candidate variables and exact NetCDF metadata.
- `meps_radiation_variable_inventory.csv`: Tabular CSV inventory of candidate variables.
- `meps_radiation_causality_audit.csv`: Origin-by-origin causality audit across all 347 clean benchmark origins.
- `meps_radiation_verification_report.md`: Detailed scientific report with empirical evidence, accumulation derivations, and multi-seasonal data tables.
- `run_stage7_1_verification.py`: Self-contained reproducibility script to repeat the data inventory and causality audit.

## Reproducibility
To repeat the verification audit, execute:
```bash
python3 stage7/stage7_1_meps_radiation/run_stage7_1_verification.py
```
