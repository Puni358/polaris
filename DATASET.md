# Datasets (not committed)

The raw source data is kept out of git: it is large, comes from third-party portals with
their own licences, and can be downloaded again. Everything **derived** from it (feature
tables, train / validation / blind splits, predictions, saved models, simulation results)
is committed.

Put the files back at the paths below and the scripts will find them.

| Path (git-ignored) | Contents | Source | How it was fetched |
|---|---|---|---|
| `data/SITES_MET_ANS_NMS_*_L2_SH.csv`, `data/raw_2025_sites_download/`, `data/raw_historical_sites_download/` | Nuolja (ANS_NMS) station, 10-minute L2 meteorology 2019–2025 | [SITES data portal](https://data.fieldsites.se/) (Swedish Infrastructure for Ecosystem Science, Abisko) | `forecasting/candidate_L_research/acquire_historical_nuolja_station_data.py`, `forecasting/candidate_L_research/download_2019_sites.py` |
| `data/POLARIS_v0_1_*.csv` | Hourly station tables, clear-sky decomposition, NWP coverage / skill, future weather forecasts 2024–2025, terrain features | Built from the station data + MET Norway forecasts | Stage 3/4 and acquisition scripts; manifests (`*_MANIFEST.json`) list SHA-256 hashes |
| `data/_checkpoints_2025_nwp_fetch/` | Monthly NWP fetch checkpoints for 2025 | MET Norway | resumable fetch cache |
| `data/enev_metar_2024.csv` | METAR observations (ENEV, Evenes) | public METAR archive | — |
| `arome_cache_21x21/` | 21×21 AROME-Arctic / MEPS grids per forecast origin (`.npz` + meta) | [MET Norway THREDDS](https://thredds.met.no/) | `scripts/forecasting_research/run_real_arome_21x21_experiment.py` |
| `forecasting/candidate_L_research/meps_cache/` | MEPS 2020–2023 extraction cache | MET Norway THREDDS | `forecasting/candidate_L_research/acquire_extract_meps_2020_2023.py` |
| `forecasting/stage7/stage8/stage8_6_cams_feasibility/raw_grib/*.grib` | CAMS forecasts 2024 | [Copernicus ADS](https://ads.atmosphere.copernicus.eu/) (needs your own `~/.cdsapirc`) | scripts in `stage8_6_cams_feasibility/` |
| `forecasting/stage7/stage7_5_terrain_horizon/*.tif` | Copernicus DSM 30 m tile N68 E018 | [Copernicus DEM](https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model) | `forecasting/stage7/stage7_5_terrain_horizon/` scripts; the derived horizon profile CSV is committed |
| `docs/POLARIS_JUDGE_PACK/07_DATA_inputs/raw_*` | Copy of the raw 2024 station file | same as `data/` | `scratch/build_judge_pack.py` |
| `(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv` | Early hourly SW_IN export | SITES | — |

The MEPS 18Z forecasts used by the production model are downloaded by
`forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/acquire_full.py`
(helper: `fetcher.py`). The MET Norway THREDDS server needs no account.

## What you can run without the raw data

- The dashboard (`dashboard/`): all its data is committed.
- Loading and scoring the saved models against the committed splits:
  `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/` and
  `candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet`.
- Most of `system/tests`, which use fixtures.

Rebuilding features from scratch or re-running full-year simulations needs the raw data.
