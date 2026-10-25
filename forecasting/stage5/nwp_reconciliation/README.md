# POLARIS Stage 5 — NWP Data Reconciliation

This directory contains the artifacts and empirical results from the Stage 5 Local NWP Data Reconciliation.

## Directory Artifacts

- `reconciliation_results.csv`: Hourly comparative analysis between existing benchmark CSV (`POLARIS_v0_1_future_weather_forecasts_2024.csv`), live `metno_seamless`, and live `metno_nordic`.
- `wind_direction_check.csv`: 2024 full-year audit of 10m wind direction (`wind_direction_10m_previous_day1`), checking non-null rates, range, and semantics.
- `spatial_probe_results.csv`: Spatial grid probe around Nuolja Middle Station evaluating coordinate resolution, elevation variation, and cell selection modes (`default` vs `nearest`).
- `issuance_semantics_notes.md`: Detailed scientific analysis of `_previous_day1` forecast issuance semantics, causal guarantees, and API metadata limits.
- `final_summary.txt`: 10-section summary report and final recommendation.
- `final_evidence_gate.md`: Final evidence gate defining established facts, unresolved aspects, testable hypothesis, and Stage 5.4 clearance.

## Key Conclusions

1. **Exact Reproduction:** Live Open-Meteo `metno_seamless` perfectly reproduces the POLARIS benchmark NWP dataset.
2. **Seamless vs Nordic Equivalence:** `metno_seamless` and `metno_nordic` produce 100% identical outputs at Nuolja coordinates.
3. **Wind Direction Quality:** 10m wind direction (`wind_direction_10m_previous_day1`) is valid for 8,337 / 8,784 hours in 2024 (94.91% availability), matching 100% of available wind speed hours.
4. **Spatial Resolution:** Spatial variations become apparent at approximately the native model-grid scale (~2.5 km); coordinate separation alone does not prove independent grid-cell identity.
5. **Issuance Semantics:** The selected previous-day forecast is causally available before t0; exact model-run reference timestamps are not exposed through the Open-Meteo point API.
6. **Evidence Gate:** **GO — Stage 5.4 spatial-NWP experiment is scientifically justified.**
