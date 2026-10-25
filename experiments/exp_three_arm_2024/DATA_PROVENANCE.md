# Data Provenance

Hashes are SHA-256 of the copies staged from `/home/punith-bs/01polaris (Copy)/data/` during this session. They match the hashes recorded in the earlier audit and D7 report. The fail-closed guard (`scripts/timestamp_guards.py`) re-checks them on the device before any run.

## 1. Source and derived files

| File | SHA-256 | Role | Coverage |
|---|---|---|---|
| `data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv` | `f3fe7cf2fff45f21feeceb850e63299a919da658d1474851b1cf611a35e43473` | Raw observations (immutable source) | 2024-01-01 00:00 … 2024-12-31 23:50, 10-min, 52,704 rows |
| `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` | `80b721a16a79dab828eb1aa02755d22c34acc35b5f48ad0d1beb5b9ab237052d` | Hourly aggregate of the above | 8,784 rows, 2024 only |
| `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16` | Forecast cloud cover plus benchmark actual_SW_IN, per origin | 8,328 rows, 347 origins, 2024-01-20 … 2024-12-31, 2024 only |
| `data/POLARIS_v0_1_clearsky_decomposition.csv` | `596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a` | Clear-sky GHI and solar elevation (UTC+1); used here only as a geometry reference in checks | 8,784 rows, 2024 only |
| `data/POLARIS_v0_1_nwp_coverage_pass_fail.csv` | `997fa46be5e492f8519d0ba90dea157e8e94db503e9535d04cdfed1d2632fa33` | Coverage audit output (context only, not an input) | — |

**Derived inputs:** no derived data file is written. At run time the code reads the weather file and selects rows in memory:
- `run_three_arm_2024.evaluation_origins` keeps the 123 evaluation origins;
- `calibrate_arm_c.select_calibration_rows` keeps the 222 calibration origins and fails closed on any evaluation-window or buffer origin, or any target hour inside the evaluation window.

Both call `assert_no_protected_dates()` first and abort on any non-2024 row. The source file already contains only 2024 rows (verified earlier: `weather_years: [2024]`). Preflight verifies the SHA-256 of every input before anything else runs. The calibration artifact records the weather-file hash it was built from, and the runner refuses an artifact whose recorded hash differs.

## 2. Creation procedure (from code, statically read)

1. **SITES raw:** downloaded from data.fieldsites.se (file header `FILE RETRIVED FROM`). Station: **Nuolja Middle Station** (Abisko), lat 68.36207412, lon 18.73875158, 702 m. The header says `TIME ZONE: UTC+1`. Each value covers the 10-minute period ending at its timestamp.
2. **Hourly file:** mean of raw labels HH:00..HH:50, written to label HH:00. Reproduced exactly (max |Δ| 3e-11 W/m²). The alternative grouping is off by up to 429 W/m².
3. **Weather file:** `clear_sky/audit_clean_nwp_windows.py` (`c8f1a220…ad21`) calls the Open-Meteo previous-runs API with `models=metno_seamless`, `*_previous_day1` variables and `timezone=Etc/GMT-1` (lines 16, 25-33). It merges on timestamp with the SITES hourly benchmark (line 78) and keeps only windows with complete 24 h coverage. `actual_SW_IN` equals the hourly SITES value at the same label (max |Δ| 3e-7, 0 unmatched).
4. **Decomposition:** `clear_sky/compute_clearsky.py` (`3a649a6f…c145`), pvlib with `tz_localize("Etc/GMT-1")` (lines 18, 45).

## 3. Exclusions and isolation

- **Evaluation:** origins 2024-05-01 … 2024-08-31 (123).
- **Arm C calibration:** origins ≤ 2024-04-29 or ≥ 2024-09-02 (222 origins present in the weather file).
- **Buffer origins excluded from both:** 2024-04-30 and 2024-09-01, both present in the file.
- **Protected and never read:** every 2025 file. In particular the 2025 decomposition CSV that the old runner loads (`planner_cf_campaign_runner.py:214`), the 2025 weather file, and the quarantined May–Aug 2025 window with its boundary dates.
- **Known limitation:** the Open-Meteo grid point is about 12 km from the station in mountainous terrain (`POLARIS_MASTER_HANDOFF.md` §37). It is a forecast source, not station truth.
- **Dataset identity:** the researchdata.se record cited in M3 (`sites-0nkkishnbw6pls70hlhoqgcw`) describes **Latnjajaure**, a different station. It is **not** used as evidence for this file. The evidence is the Nuolja file's own header.

## 4. Data-use rights

| Source | Evidence | Status |
|---|---|---|
| SITES Nuolja 2024 (data.fieldsites.se) | Raw file header, line 12: "SITES data is licensed under a Creative Commons Attribution 4.0 international license". Line 13 requires citing SITES and acknowledging POLARIN. File SHA-256 `f3fe7cf2…e43473` | **CC BY 4.0, documented in the source file.** Attribution obligations: cite SITES and acknowledge POLARIN in any output that uses the data |
| Open-Meteo previous-runs API data (`models=metno_seamless`; MET Norway source), in the weather file | The download script (`clear_sky/audit_clean_nwp_windows.py`) records the API call but no licence. No archived licence page, terms snapshot or licence statement for the exact data, model and retrieval date was found in the repository or the project files. An earlier session read the current generic website licence page (2026-10-11). That is a statement about the service today, not evidence for these data, and it is not used | **UNVERIFIED** |
| The weather file (SITES and Open-Meteo combined) | Inherits both of the above | **UNVERIFIED** (Open-Meteo part) |

D11 stays PENDING. Preflight refuses calibration and execution until D11 is APPROVED, which requires the project lead to confirm the Open-Meteo licence from identified evidence: an archived licence or terms page covering the retrieval date and the `metno_seamless` model, or equivalent. The authorization sheet's "data-use rights confirmed" box stays unticked.

### Update 2026-10-11 (M9)

The table above is the state through M8 and is kept. Current state:
- **D11 (internal research use): APPROVED BY EXISTING AUTHORITY.** M9: "The project lead states that they have the necessary data rights." Documentary evidence and gaps: `reports/evidence/D11_DATA_RIGHTS_EVIDENCE_2026-10-11.md` (product: Open-Meteo Previous Runs API, `metno_seamless`; current terms: free API non-commercial only, data CC BY 4.0; no archived terms; download date not established, device file mtime 2026-09-09T15:47:45Z is only the latest possible date).
- **D11-PUB (publication, redistribution, competition demonstration): BLOCKED — EVIDENCE REQUIRED.**
- **Attribution in every output:** Open-Meteo (CC BY 4.0), MET Norway as model source, SITES (cite) and POLARIN (acknowledge).
- The authorization sheet's "data-use rights confirmed" box is still for the project lead to tick.
