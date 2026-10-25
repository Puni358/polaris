# Frozen Research Experiment Manifest — R1

**Status**: `FROZEN` — `SIMULATED_RESEARCH_ASSUMPTION` policy, **NOT station-approved policy**,
**NOT governance-authorized**. Frozen for exactly one experiment run (this manifest's
provenance block, below). Any change to any field requires a new manifest (R2+), not an
edit of this one.

**Role**: Frozen by `SIMULATED_STATION_MANAGER` (role-played research stand-in; no real
organizational authority — see Governance Disclaimer in `RESEARCH_EXCEPTION_DECISION_RECORD.md`).

---

## 1. Terminal reserve policy (R1, frozen)

| Parameter | Frozen value | Label |
|---|---|---|
| Formula | `terminal_target_wh = 40,000 + max(0, Σ_{k=19..24}(crit_demand[k] − renewable_avail[k])·1h) × 1.10`, computed from that cycle's own 24h `ForecastBundle` (last 6 of 24 horizon hours; no data beyond the horizon, no hindsight) | `SIMULATED_RESEARCH_ASSUMPTION` |
| Floor | 40,000 Wh (= 20% × 200,000 Wh technical minimum SOC) | floor value itself `CURRENT_IMPLEMENTATION_FACT` (battery.yaml); its *use as the terminal floor* is `SIMULATED_RESEARCH_ASSUMPTION` |
| Look-ahead | 6 hours | `GOVERNANCE_AUTHORIZED` ($T_{\text{REQUIRED}}=6\text{h}$, the one `ESTABLISHED` numeric value in this governance space) |
| Uncertainty margin | +10%, multiplicative on the energy deficit | `SIMULATED_RESEARCH_ASSUMPTION` (value borrowed from pre-existing unauthorized register entry NC-07) |
| Enforcement | Secondary lexicographic $J_2$ objective, not a hard constraint | `GOVERNANCE_AUTHORIZED` (policy structure decided in prior turn) |
| Recalculation | Every cycle, from that cycle's own fresh forecast | `SIMULATED_RESEARCH_ASSUMPTION` |

Full rationale/evidence for each row: `RESEARCH_EXCEPTION_DECISION_RECORD.md` (this directory).
**No field in this table changes in this revision** — reproduced here only for a
self-contained manifest.

## 2. Baseline vs. Stage 8.1 configuration (identical for both arms except forecast engine)

- **Scenario / fixture**: `H10RuntimeAdapter` over `POLARIS_HYBRID_FIXTURE_H1_0` (real H1.0
  fixture, 8,784 hourly rows, SITES Nuolja REAL_MEASURED solar) — identical for both arms.
- **Initial `StationState`** (identical for both arms, every cycle): `battery_soc_pct=80.0`,
  `battery_energy_wh=160000.0`, `diesel_running=True`, `diesel_hours_running=2.0`,
  `diesel_fuel_remaining_liters=500.0`; environmental observation fields taken from the
  fixture at that cycle's index. (Fixed "warmed-up" state, reused unchanged from the
  previously-proven smoke-test pattern — not re-derived per cycle.)
- **Router**: `EMSControlRouter` (unmodified).
- **Optimizer**: `GAP19HighsNativeOptimizer` (NORMAL route, unmodified) /
  `OptionDFallbackSolver` (EMERGENCY route, unmodified) — route determined by the router per
  cycle, identically for both arms' own forecast.
- **Simulator**: `DigitalTwinSimulator` (unmodified), stepped once per cycle (first planned
  hour only — see §5 limitations).
- **Config YAMLs** (unmodified production files, identical for both arms):

  | File | SHA-256 |
  |---|---|
  | `system/config/battery.yaml` | `eb06f81d8b11364e254cbcd5c37a4769874f8703e9e86e3b067b60d8858da216` |
  | `system/config/diesel.yaml` | `421120967328e18366daf41b682fc9f1cbe91b0f9ebe2133b83290bb9e294ac3` |
  | `system/config/loads.yaml` | `eacb84d1c25f8768de0ee0cf8fdb286d4dbc9254824d7c17aea738cbe9774467` |
  | `system/config/solar_pv.yaml` | `611521090b7d551614c23d91fc190320a42bccee667929618d40bab987262e5e` |
  | `system/config/station.yaml` | `e021368133587b5752b9471722d7997d1cd2aa2d674697a47b1b2f5b06052e42` |
  | `system/config/optimizer.yaml` | `bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8` |

- **Only difference between arms**: the forecast engine —
  `baseline` = `LocalBaselineForecastEngine` (synthetic persistence/diurnal, `PROTOTYPE_UNVALIDATED`);
  `stage8_1_corrected` = `Stage81CorrectedForecastEngine` (frozen model, see §3). Both engines
  fall back to the SAME `LocalBaselineForecastEngine` instance for wind/demand channels
  (`s81_corrected_solar.py` internal design — only the solar irradiance channel differs
  between arms).

## 3. Frozen Stage 8.1 model / artifact

- **Model artifact**: `stage7/stage8/stage8_1_corrected_2025/model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib`
  — SHA-256 `FROZEN_MODEL_SHA256` as hard-coded and hash-checked in
  `system/forecasting/implementations/s81_corrected_solar.py` (verified again at the start
  of every run of `run_research_simulation.py`/`run_full_experiment.py`; run aborts on mismatch).
- **Feature matrix**: `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`
  — SHA-256 `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` (verified at
  start of every run).
- **Established evaluation window**: the full set of daily origins present in that frozen,
  hash-verified matrix — **347 daily origins, 2024-01-20T00:00:00Z through
  2024-12-31T00:00:00Z** (not every calendar day in that span has a row; only the matrix's own
  347 origins are used — no gap is filled or interpolated). This is the only evaluation
  window actually defined by existing frozen evidence; no separate "established evaluation
  window" document exists elsewhere in the repository, so the frozen matrix's own full
  coverage is used as-is, without curation or selection.

## 4. Frozen research script

| File | SHA-256 |
|---|---|
| `run_research_simulation.py` (defines the frozen formula/constants, reused by import, not copied) | `d68b343d60f67a2fc8143316278371342d3933f70d0e26d40f3c1c732d843bd1` |
| `RESEARCH_EXCEPTION_DECISION_RECORD.md` (assumption rationale, frozen) | `d8356282ca1550c255bf5d3f9e35c7256d322513da9824c990c9f3d1cc9fc26b` |

The full-window experiment (`run_full_experiment.py`, written after this manifest) imports
`compute_terminal_target_wh`, `TERMINAL_FLOOR_WH`, `LOOKAHEAD_WINDOW_HOURS`,
`UNCERTAINTY_MARGIN` directly from `run_research_simulation.py` rather than
re-implementing them, so the frozen formula cannot drift between the two scripts.

## 5. Timestamp / provenance

- **Frozen**: 2026-10-03 (this session).
- **Prior smoke test** (5 origins, 10 cycles, both arms `OPTIMAL`): see
  `RESEARCH_SIMULATION_RESULTS.md` in this directory — already executed, results already
  recorded, assumptions unchanged since.
- **Repository state**: `system/` is untracked in git in this working tree (no commit hash
  available for production code); the config/script/model/matrix SHA-256 values above are
  the reproducibility anchor instead.

## 6. Known limitations (declared up front, not discovered after the fact)

- Each of the 347 cycles is an **independent single-step closed-loop evaluation** (fresh
  `ForecastBundle` → router → optimizer → one `simulator.step` call), not a continuous
  347-day trajectory. The Stage 8.1 corrected feature matrix only has one row-set per
  calendar day (daily origins), so there is no hour-by-hour frozen Stage 8.1 forecast to
  thread a continuous state through; threading state through un-forecasted hours would
  require fabricating data, which is excluded by design.
- Only the plan's first hour (`t=0`) is actually executed by `DigitalTwinSimulator.step`
  per cycle; the remaining 23 hours of each 24h `DispatchPlan` are the optimizer's *plan*,
  not a realized outcome. Metrics are reported in two explicit tiers (realized t0 vs.
  planned 24h horizon) — never blended — per `run_full_experiment.py` and the results
  report.
- This manifest and the resulting comparison are RESEARCH-SIMULATION ONLY. They do not
  authorize, approve, or recommend any terminal-reserve value, formula, or forecast engine
  for production use.
