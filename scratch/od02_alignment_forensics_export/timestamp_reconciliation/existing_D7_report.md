# D7: Timestamp Convention and Solar-Geometry Verification

**Status:** verification done, read-only, 2024 data only. Review outcome: **pending project lead**. Nothing was executed except the read-only check scripts in this folder. No repository file was changed. The experiment is still not authorized.

## 1. Verdict

All 2024 data labels are **fixed-offset UTC+1 (Etc/GMT-1), with no DST**. The SITES 10-minute values are **period-ending**. This rests on documentary evidence, and the station's own irradiance data independently agrees with it (§4).

The winner's solar forecaster `causal_nwp_physics.py` reads these UTC+1 labels **as UTC**. Its sun position is therefore computed one hour off: the forecast clear-sky curve sits about 1 h early in label time. Every other component that computes solar geometry (`compute_clearsky.py`, the EBR adapter's pvlib fallback) uses UTC+1 correctly. Within a single run, the EBR reserve and the PV forecast therefore disagree about where the sun is.

I did not measure how much this costs in diesel. That would need a simulation, which is out of scope.

## 2. Provenance and documentary evidence

| Item | Evidence |
|---|---|
| SITES raw file | `data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`, SHA-256 `f3fe7cf2fff45f21feeceb850e63299a919da658d1474851b1cf611a35e43473`. Header: `TIME ZONE: UTC+1`, `TIME RESOLUTION: 10 minutes`, "each timestamp represents the 10 minute period leading up to the stated timestamp". Station: Nuolja Middle Station, lat 68.36207412, lon 18.73875158. CC-BY 4.0 |
| Hourly file | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv`, `80b721a16a79dab828eb1aa02755d22c34acc35b5f48ad0d1beb5b9ab237052d`. Label HH:00 = mean of raw labels HH:00..HH:50, reproduced to 3e-11 W/m². The alternative (HH-1:10..HH:00) is off by up to 429 W/m² |
| Weather file | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv`, `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16`. Built by `clear_sky/audit_clean_nwp_windows.py` (`c8f1a220…50ad21`) from the Open-Meteo previous-runs API, `metno_seamless`, `*_previous_day1`, with `&timezone=Etc/GMT-1` (lines 16 and 33), then merged on the label with the SITES benchmark. `actual_SW_IN` matches the hourly file at the same label to 3e-7 W/m², with 0 unmatched rows |
| Clear-sky decomposition | `data/POLARIS_v0_1_clearsky_decomposition.csv`, `596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a`. Built by `clear_sky/compute_clearsky.py` (`3a649a6f…c145`), `TIMEZONE = "Etc/GMT-1"`, `tz_localize` at line 45. Its `solar_elevation` matches an independent NOAA calculation at UTC+1 to 0.008° and misses UTC by up to 5.5° |
| Forecaster | `system/forecasting/implementations/causal_nwp_physics.py` (`14e72d8a…b710`): `NUOLJA_TZ = "UTC"` (line 55); naive timestamps get `tzinfo=timezone.utc` (lines 302-303); pvlib is called on those (lines 334-336). Its docstring also says "MEPS 18Z", which does not match the Open-Meteo source actually used |
| EBR adapter | `stage4_low_sun_adapter.py` (`3427da6a…95d0`): the pvlib fallback uses `Etc/GMT-1` (consistent) |

**Flag:** the dataset record you linked (researchdata.se `sites-0nkkishnbw6pls70hlhoqgcw`) is for **Latnjajaure**. The file actually used is from **Nuolja Middle Station**. The file's own header is the evidence I relied on. The preregistration should cite the Nuolja record instead.

## 3. Alignment, gaps, duplicates and DST

| Check | Result |
|---|---|
| Raw SITES | 52,704 rows covering 2024-01-01 00:00 to 2024-12-31 23:50; every step is 10 min; 0 duplicates; 0 missing; 0 NaN SW_IN |
| DST days (03-31, 10-27) | 144 rows each and 0 duplicates, so the file has no DST shift (consistent with a fixed offset) |
| Hourly file | 8,784 rows; 0 duplicates; 0 missing |
| Weather file | Only 2024 rows. Every forecast_start is at 00:00. timestamp = forecast_start + (horizon_hour − 1) h for every row. 0 duplicate (origin, horizon) pairs; timestamps are unique |
| t0 convention | t0 = forecast_start − 1 h. The realized step k is at forecast_start + k, which is also the first planner target at step k. Consistent. (Lookahead L1 in the horizon tail is a separate issue, handled by PROPOSED_PATCH.diff) |
| Forecast valid time | Open-Meteo hourly values were requested in UTC+1, the same label basis as SITES. I found no documentation of whether cloud cover is instantaneous or a preceding-hour mean for `metno_seamless` previous-runs data. **Open question**, not assumed |

## 4. Solar geometry versus the data

Tests used only months outside the evaluation window: 2024-04-29 to 2024-09-02 was excluded, leaving 180 days. Sun positions came from an independent NOAA algorithm at the station coordinates, evaluated at the centre of each 10-minute period.

| Test | Labels read as UTC | Labels read as UTC+1 |
|---|---|---|
| Median sun elevation at first light (SW_IN ≥ 10 W/m²) | 5.69° | 1.38° |
| Median sun elevation at last light | **−2.85°** (light measured after sunset) | 1.83° |
| Midpoint between first and last light, compared with solar noon | Solar noon would be 10.75; the observed midpoint is 11.67 | Solar noon would be **11.75**; the observed midpoint is 11.67 |
| Best correlation lag, scanned from −120 to +120 min | — | Best at +40 min (r 0.8927, vs 0.8821 at 0 and 0.8879 at +60). The peak is broad and the slope's terrain affects it, so this test is weak |

UTC+1 makes dawn and dusk symmetric and puts the midday midpoint within about 5 minutes of solar noon. UTC requires 10 W/m² to be measured with the sun 2.85° below the horizon. The data independently confirm the documentary convention. My earlier "centroid at 11.04" result was skewed by the terrain and is superseded by these tests.

## 5. Proposed correction (for review only, not applied)

> **Superseded 2026-10-11:** the timestamp-conversion approach below would also shift the baseline wind and demand forecasts and double-convert the reserve's elevation. It is withdrawn. See `../PROTOCOL_ADDENDUM_D7a.md` §2 for the adopted Location-wrapper mechanism. The "about 4k solves" figure is corrected there to 2,952.

There should be no relabelling of any file and no blanket shift. Original timestamps stay as they are. The proposed in-memory conversion is: the new experiment runner converts each label to UTC with `to_utc()` (Etc/GMT-1 → UTC) and passes `…Z` strings to `causal_nwp_physics` as both `station_state.timestamp` and `runtime_context["timestamps"]`. It then maps the 24 outputs back to the original labels. The forecaster file stays byte-identical (`14e72d8a…`). The guard `check_forecaster_input_is_utc` fails closed if a naive label reaches it.

**Decision needed (D7a):** this changes what Arm A means.
- **A-as-is:** keep the 1 h error, so Arm A reproduces the winner exactly. The correction would become a separate sub-arm.
- **A-corrected:** apply the conversion in every arm that uses the forecaster. This is cleaner, but Arm A would no longer be a pure reproduction.
- **Recommended:** run A-as-is plus an A-corrected sub-arm. That keeps the reproduction and isolates the effect of the fix. This adds roughly 4k MILP solves to the resource line on the authorization sheet.

## 6. Automated fail-closed checks

`PROPOSED_timestamp_guards.py` in this folder targets `experiments/exp_three_arm_2024/timestamp_guards.py`. It is not applied and not run. `run_all_guards()` checks:
- hashes of all four data files;
- the SITES `TIME ZONE: UTC+1` header line;
- regular hourly coverage, including 24 h on both DST days;
- the weather file is 2024-only, has 00:00 origins, the lead/horizon identity holds, there are 24 rows per origin and no duplicates;
- hourly linkage;
- the decomposition's geometry matches UTC+1 and not UTC.

Any failure raises an error, and the run stays FAILED. Per D7 step 6, these checks still need your review, and then a passing run, before any solve.

## 7. Preregistration entry (to copy into PREREGISTRATION.md once approved)

```
D7 TIMESTAMP CONVENTION — verified 2026-10-11, review: PENDING
Convention: all 2024 inputs labelled fixed UTC+1 (Etc/GMT-1), no DST. SITES 10-min = period-ending.
Hourly = mean(HH:00..HH:50) -> HH:00. Weather: timestamp = forecast_start + (horizon_hour-1) h, forecast_start 00:00.
Simulation: t0 = forecast_start - 1 h; realized step k = forecast_start + k h.
Solar geometry evaluated at label - 1 h (UTC).
Evidence: SITES header "TIME ZONE: UTC+1"; audit_clean_nwp_windows.py:16,33 (timezone=Etc/GMT-1);
compute_clearsky.py:18,45; decomposition elevation matches UTC+1 to 0.008 deg (vs 5.5 deg for UTC);
non-eval-month data: first/last light at +1.4/+1.8 deg (UTC+1) vs +5.7/-2.9 deg (UTC); midpoint 11.67 vs noon 11.75.
Known defect: causal_nwp_physics.py:55,302-303,334-336 treats labels as UTC (1 h geometry error). Handling: D7a.
Open: Open-Meteo cloud_cover instant vs hour-mean semantics undocumented.
Data SHA-256: SITES raw f3fe7cf2fff45f21feeceb850e63299a919da658d1474851b1cf611a35e43473
  hourly 80b721a16a79dab828eb1aa02755d22c34acc35b5f48ad0d1beb5b9ab237052d
  weather 8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16
  decomposition 596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a
Code SHA-256: causal_nwp_physics 14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710
  compute_clearsky 3a649a6ff9f227b5a1819f6cf577d896c6bc1488274a86ccdaaafc29a109c145
  audit_clean_nwp_windows c8f1a2204af1703296e32658e5d8890e2bd7f876d554a2b1a5ee46f1bc50ad21
  stage4_low_sun_adapter 3427da6a7b1d7763f8fa655e541cd2a344aeefdd33379137c6311501799395d0
Check scripts: d7_checks.py f65aa905d00b2418e762fa9337b2fc7174ca6b88157a336e6d6d90ef8951d2ca
  d7_extra.py 334c9cd51bf7da23f62eea111b731a1a27974e2a1d537ed9ef25a4fc014e71d1
  d7_geom.py 82e15cf9abd4b2fe6781d2a14f16c138ce494e8e66be25b4d4cb033b7b3b7d6e
  output d7_out.txt 669cf79d17a6ff3cb7ec41b1c2f75e674054fe765a9929fec00c39e51adabbd9
Review outcome: ______  Reviewer: ______  Date (UTC): ______
```

## 8. What was and was not touched

- **Read:** the SITES 2024 raw file, the hourly 2024 file, the weather 2024 file and the decomposition file (each contains 2024 only; date coverage was checked from the timestamp column before loading), plus the code files above.
- **Not read:** no 2025 file and no file from a `stage4_*_2025` result folder.
- **Not run:** no simulation, training, replay or patch.
- **Not changed:** no repository file. All outputs are new files under `/mnt/project-files/polaris/three_arm_prep/d7/`.
