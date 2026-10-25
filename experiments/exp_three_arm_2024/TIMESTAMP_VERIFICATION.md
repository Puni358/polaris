# Timestamp and Solar-Geometry Verification (summary)

The full report is copied verbatim at `reports/D7_VERIFICATION_REPORT.md`. Its §5 proposal is marked superseded in place by D7a. The original check scripts and their output are under `reports/source_prep/d7/`.

**Review outcome (M9, 2026-10-11): ACCEPTED by delegated technical authority.** D7 is RESOLVED BY DELEGATED TECHNICAL AUTHORITY: fixed UTC+1, no global conversion, narrow pvlib-input correction in A-Fix and C only (see DECISIONS_LOG ledger after M9). Earlier text: "Review outcome: PENDING (project lead)."

## Verified convention

- All 2024 inputs are labelled in **fixed UTC+1 (Etc/GMT-1), with no DST**.
- SITES 10-minute values are **period-ending**. The hourly file maps mean(HH:00..HH:50) → HH:00.
- Weather file: forecast_start is 00:00 label time, and timestamp = forecast_start + (horizon_hour − 1) h.
- Simulation: t0 = forecast_start − 1 h; realized step k = forecast_start + k h, which is also the first planner target at step k.
- True UTC of a label = label − 1 h.

## Evidence

**Documentary**
- SITES header `TIME ZONE: UTC+1`.
- `audit_clean_nwp_windows.py:16,33` requests `timezone=Etc/GMT-1`.
- `compute_clearsky.py:18,45` localizes to Etc/GMT-1.

**Data (D7 scripts, non-evaluation months only, 180 days)**

| Test | Labels as UTC | Labels as UTC+1 |
|---|---|---|
| Median sun elevation at first light (≥ 10 W/m²) | +5.69° | **+1.38°** |
| Median sun elevation at last light | −2.85° | **+1.83°** |
| Daylight midpoint (observed 11.67) vs expected solar noon | 10.75 | **11.75** |

**Integrity**
- 0 duplicates and 0 gaps in the raw and hourly files.
- 24 h on both DST days (2024-03-31, 2024-10-27).
- Weather file: 0 duplicate (origin, horizon) pairs, 24 rows per origin.

## Agreement between the two reserve-elevation methods: backed by test output

| Claim | Before this review | Now |
|---|---|---|
| The winner's reserve (precomputed decomposition CSV) and the new runner's reserve (`SolarElevationProvider(None)`, pvlib Etc/GMT-1) agree | 0.008°, a D7 claim that compared an independent NOAA calculation with the decomposition | **Max \|Δ\| = 0.000000°, mean 0.000000°, n = 8,784**: actual pvlib 0.16.1 through the unmodified adapter vs the 2024 decomposition (`tests/test_input_integrity_2024.py::test_reserve_provider_matches_2024_decomposition`, passed; output in `reports/PREP_CHECKS_OUTPUT.txt`) |

The 0.008° figure is the NOAA-vs-pvlib algorithm difference. It does not describe the two runtime methods.

**Tolerance 0.05°, justification:** the defect being guarded against is a 1-hour shift, which moves the sun by several degrees at these latitudes (up to 5.5° in the decomposition comparison). 0.05° is about 12 s of solar motion. That is more than 100× smaller than the defect, yet loose enough to absorb pvlib-version rounding if the device's pvlib changes. The device venv also has pvlib 0.16.1, the version tested here.

## Forecaster defect and its handling

- `causal_nwp_physics.py:55` sets `NUOLJA_TZ = "UTC"`.
- `:302-303` treats a naive timestamp as UTC; the runner's `…Z` strings are label clock values tagged UTC.
- `:334-336` calls pvlib on those values.
- Result: the forecaster's sun is 1 h off. Handling follows D7a: Arm A keeps the defect; A-Fix corrects it through `scripts/solar_convention.py`. No source timestamp is converted, and the reserve's time handling is unchanged.

## Automated fail-closed checks

`scripts/timestamp_guards.py` `run_all_guards()` checks:
- data hashes;
- the SITES UTC+1 header;
- hourly regularity and DST-day length;
- the weather-file identities and 2024-only rows;
- hourly linkage;
- that decomposition geometry matches UTC+1 and not UTC.

`scripts/solar_convention.py` refuses double wrapping and refuses use if the forecaster's Location tz is no longer `"UTC"`. Test results: `reports/FINAL_READINESS_REVIEW.md` §5.
