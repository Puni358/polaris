# POLARIS — Forecast-driven energy management for an Arctic off-grid microgrid

POLARIS is a research and operational workspace for a solar + wind + battery + diesel
microgrid at the Mount Nuolja automatic weather station (Abisko, Sweden). It has two halves:

1. **Solar forecaster** – predicts the next 24 h of solar irradiance at the station.
   The production model is **Candidate N6** (25-seed additive-residual HGB ensemble +
   15-seed clearness-index specialist, 36 causal features, 18Z MET Norway MEPS inputs).
2. **Energy optimizer (GAP19)** – a HiGHS MILP that plans battery and diesel use each hour
   over a 24 h receding horizon, with a forecast-driven battery safety reserve.

Full-year simulation (8,328 h, identical demand/wind for every run):

| Run | Diesel (L) | Generator hours | Unmet load |
|---|---:|---:|---:|
| Basic reactive controller (no forecast) | 38,405 | 3,928 | 0 kWh |
| **POLARIS — forecast + smart cushion** | **26,942** | **1,270** | **0 kWh** |
| Forecast, no safety cushion | 27,038 | 1,288 | 2.5 kWh |

Source: [`dashboard/public/data/matched/aggregates.json`](dashboard/public/data/matched/aggregates.json).

---

## Where to start

| You want… | Open |
|---|---|
| Every model trained, its scripts, results, and **why it was kept or discarded** | [`MODEL_REGISTRY.md`](MODEL_REGISTRY.md) |
| The datasets (not in git) and how to get them | [`DATASET.md`](DATASET.md) |
| The whole project in plain language, plus the 3-minute presentation map | [`docs/POLARIS_EXPLAINED_LIKE_IM_5/00_START_HERE.md`](docs/POLARIS_EXPLAINED_LIKE_IM_5/00_START_HERE.md) |
| A curated, readable walk-through with plain file names | [`docs/POLARIS_JUDGE_PACK/00_START_HERE_where_to_find_everything.md`](docs/POLARIS_JUDGE_PACK/00_START_HERE_where_to_find_everything.md) |
| The full forecasting research write-up | [`docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/ALL_FORECASTERS_COMPARED_compendium.md`](docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/ALL_FORECASTERS_COMPARED_compendium.md) |
| Every design / governance decision | [`docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md`](docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md) |
| System architecture | [`docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md`](docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md) |

## Repository layout

```
polaris/
├── README.md, MODEL_REGISTRY.md, DATASET.md   ← start here
├── system/          Operational EMS code: N6 forecaster engine, GAP19 optimizer, schemas, config, tests
├── dashboard/       The local web app (React + Vite) and its pre-computed simulation data
├── polaris-ui/      Earlier UI prototype
├── forecasting/     All solar/wind forecasting research
│   ├── stage3/ … stage7/       Research stages (physics baselines → Stage 4 ensemble → NWP, microphysics, terrain)
│   │   └── stage7/stage8/stage8_1_station_tuning_research/   Candidates A–N, L2 uncertainty, saved models (N6 lives here)
│   ├── foundation_models/      TimesFM, Chronos-2 (+ LoRA adapters), Moirai, their plots and results
│   ├── n6/                     N6 readiness reports and remediation history
│   ├── candidate_L_research/   2020–2023 historical replay (link into stage7/stage8)
│   ├── clear_sky/, spatial_arome_research/, CANDIDATE2_FORECAST_CONTENT_ABLATION/, solar_branch_01/
│   ├── wind/reports/           Wind forecaster reports
│   └── reports/                Forecasting audit reports, grouped: stage8, solar_branch01, candidates, uncertainty, …
├── ems/             Energy-management (optimizer / controller) work
│   ├── gap19/                  GAP19 optimizer audits, tests and research branches
│   ├── gates/, hd_decisions/, ecd/, option_d/, specification/, fixtures/, other/
│   ├── campaigns/              Simulation campaigns: 168 h pilots, OFAT sweep, Branch-01, 365-day runs
│   └── reports/                EMS reports, grouped: stage81_ems_runs, hybrid_h1_fixture, rt01_runtime_fixes, …
├── experiments/     Pre-registered EMS experiments (diesel reduction, Stage 4 consistency, L2 risk)
├── research/        Focused diagnostics (wind, reserve margin, investigations)
├── scratch/         Full-year simulation runners that produce the dashboard data
├── scripts/         Helper scripts: ems_campaigns/, forecasting_research/, governance/ (+ step-10 runners)
├── artifacts/       Branch-01 model runs
├── docs/            Plain-language explainer, judge pack, presentation, decision registers,
│                    architecture, external research PDFs, launch video, UI reports
├── tests/, tools/
└── requirements.txt, requirements-full.txt
```

Paths inside scripts were updated for this layout. Many older scripts still hard-code
the original machine path `/home/punith-bs/01polaris (Copy)`; on another machine, edit
that `BASE` / `ROOT` line to your clone's location (or create a symlink at that path).

---

## Run the dashboard locally

The dashboard is a static React app. All simulation results it shows are already
committed under `dashboard/public/data/`, so no Python or dataset is needed to view it.

Works on Windows, macOS and Linux. You only need **Node.js 18 or newer**
(Node 20 LTS recommended, from <https://nodejs.org>). Check with `node --version`.

```bash
git clone --depth 1 https://github.com/Puni358/polaris.git
cd polaris/dashboard
npm ci
npm run dev
```

Open <http://localhost:5173>. The server listens on all interfaces (`--host`), so other
devices on your network can open `http://<your-ip>:5173`.

- `--depth 1` skips the git history and makes the ~1.4 GB clone faster; drop it if you want the history.
- `npm ci` installs the exact versions in `package-lock.json`. Use `npm install` only if `npm ci` complains.
- Port already in use? Run `npm run dev -- --port 5174`.
- `Cannot find module @rollup/rollup-…` after copying `node_modules` between machines: delete `node_modules` and run `npm ci` again.

Production build:

```bash
npm run build
npm run preview
```

The older prototype UI runs the same way from `polaris-ui/` (`npm install && npm run dev`, port 5173 by default, so stop the dashboard first).

## Set up Python (models, simulations, tests)

Python **3.12** is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-full.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

`requirements.txt` is a minimal plotting set; `requirements-full.txt` is the full pinned
environment (scikit-learn, highspy, pvlib, xarray, cfgrib, netCDF4, pytest, …).

The foundation-model benchmarks each use their own environment because of conflicting
torch / CUDA pins:

```bash
cd chronos && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ../moirai && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### Run the tests

```bash
source .venv/bin/activate
pytest system/tests tests
```

Most optimizer and forecaster-engine tests use committed fixtures and saved models. Tests that rebuild features from raw station or MEPS data need the datasets in [`DATASET.md`](DATASET.md).

### Use the production forecaster and optimizer

- Saved N6 model: `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` (a copy is in `docs/POLARIS_JUDGE_PACK/08_FORECASTER_frozen_models/`), with SHA-256 fingerprints in `CANDIDATE_N_MANIFEST.json`.
- Runtime engine: `system/forecasting/implementations/n6_solar.py`
- Optimizer: `system/optimization/implementations/gap19_highs_native.py`, configured by `system/config/*.yaml`
- One live forecast → optimize cycle: `forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/demonstrate_live_operational_execution.py`

### Regenerate the dashboard data

The full-year runs that fill `dashboard/public/data/` are in `scratch/` (they need the datasets):

```bash
python scratch/run_reactive_matched.py              # basic controller baseline
python scratch/run_scenario2_full_trace.py          # POLARIS with full decision trace
python scratch/run_continuous_ui_rhc_scenario3.py   # fixed big cushion
python scratch/run_continuous_ui_rhc_scenario4.py   # no safety cushion
python scratch/whatif_decisions.py                  # "what if" counterfactuals
python scratch/build_matched_aggregates.py          # year totals for the Proof page
python scratch/build_featured_days.py               # highlighted days
```

---

## What is not in this repository

- **Raw datasets** (SITES station files, MET Norway MEPS / AROME downloads, CAMS GRIB, Copernicus DEM). See [`DATASET.md`](DATASET.md).
- Virtual environments, `node_modules/`, build output (`dist/`), and rendered video frames. Recreate them with the steps above.

Derived feature tables, train/validation/blind splits, model predictions, saved models and all results **are** committed.
