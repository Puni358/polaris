# R2 Manifest — Solar-Forecast Ablation

**Status**: `FROZEN`. R2 is a **SOLAR-FORECAST ABLATION of R1**, not a new experiment design
and not a full renewable-forecast experiment. It reuses R1's frozen terminal-reserve
assumptions, scenario, simulator, MILP, and evaluation window unchanged. The only thing R2
adds relative to R1 is an explicit, full-window (not sampled) verification that wind and
demand are bit-identical between arms, plus its own independently-hashed run artifacts.

**Role**: Frozen by `SIMULATED_STATION_MANAGER` (role-played research stand-in; no real
organizational authority — see Governance Disclaimer in `RESEARCH_EXCEPTION_DECISION_RECORD.md`).
**No new SIMULATED_RESEARCH_ASSUMPTION was introduced for R2.** Every assumption below is
inherited from R1, unchanged.

---

## 1. What R2 changes relative to R1: nothing in the assumptions, only verification + fresh artifacts

- **Terminal-reserve formula, floor, look-ahead, margin, enforcement**: identical to R1 —
  see `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` §1. Reused by import
  (`from run_research_simulation import compute_terminal_target_wh, TERMINAL_FLOOR_WH,
  LOOKAHEAD_WINDOW_HOURS, UNCERTAINTY_MARGIN`), not re-implemented, so it cannot drift.
- **Initial `StationState`, scenario, fixture, simulator, MILP (GAP19HighsNativeOptimizer /
  OptionDFallbackSolver), config YAMLs**: identical to R1 — see
  `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` §2.
- **Evaluation window**: identical to R1 — the same 347 daily origins,
  2024-01-20 through 2024-12-31, from the same frozen matrix.
- **Baseline arm**: `LocalBaselineForecastEngine`, exact same R1 code path and instance
  construction.
- **Stage 8.1 arm**: `Stage81CorrectedForecastEngine`, exact same frozen model artifact and
  hash as R1.
- **Only solar forecast differs between arms** — explicitly verified below (§2), not merely
  assumed.

## 2. Identical-input verification (new for R2 — full window, not sampled)

`verify_r2_identical_wind_demand.py` (SHA-256 `35196dbadb815e826905e716d0fb8cff841c4a209444f73ed819c166ec5b8778`)
calls both engines' `predict()` (read-only, no optimizer/simulator) at **all 347** evaluation
origins and compares `bundle.wind_generation.point` and `bundle.demand.point` for exact
equality. Result: `R2_IDENTICAL_INPUT_VERIFICATION.json` —
**`"all_identical": true`, 347/347 origins checked, 0 mismatches.** This is a hard
precondition: if it had failed, R2 would not proceed (per instruction, and consistent with
the Governance Disclaimer's "STOP rather than silently changing anything").

## 3. Frozen artifact hashes (all inherited from R1, re-verified at R2 run time)

| Artifact | SHA-256 |
|---|---|
| Stage 8.1 feature matrix (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`) | `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43` |
| Frozen Stage 8.1 model artifact | `FROZEN_MODEL_SHA256` as hard-coded/checked in `s81_corrected_solar.py` (same value R1 used) |
| `run_research_simulation.py` (frozen formula, imported not copied) | `d68b343d60f67a2fc8143316278371342d3933f70d0e26d40f3c1c732d843bd1` |
| `RESEARCH_EXCEPTION_DECISION_RECORD.md` | `d8356282ca1550c255bf5d3f9e35c7256d322513da9824c990c9f3d1cc9fc26b` |
| `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` (R1, referenced not modified) | `ebc7180f25eace76d69111688d6872793d286390b5bfd66a2ea49baafce6de2e` |
| `run_full_experiment.py` (R1 run script, reused as R2's run script — same code, re-verified) | `8afaf9ee7862c4586c586d14debb418d78f655362d1d729407300595fce118d5` |
| `verify_r2_identical_wind_demand.py` (new for R2) | `35196dbadb815e826905e716d0fb8cff841c4a209444f73ed819c166ec5b8778` |
| Config YAMLs (`battery`/`diesel`/`loads`/`solar_pv`/`station`/`optimizer`.yaml) | identical to R1 — see `FROZEN_RESEARCH_EXPERIMENT_MANIFEST.md` §2 |

Because every one of these is bit-identical to R1, **R2's full-window run is the same
deterministic computation as R1's**, now additionally gated by the full-window
identical-input check in §2 and recorded under its own R2-labeled artifact names for
independent traceability.

## 4. Timestamp / provenance

- **Frozen**: 2026-10-03 (this session), as R2.
- **Verification run**: completed before this manifest was finalized — §2 result already
  confirmed PASS.

## 5. Declared scope limitation (unchanged from R1, restated per instruction)

This is a **solar-forecast ablation only**. Wind and demand are deliberately held identical
(both baseline-persistence) between arms — this experiment does not evaluate, validate, or
substitute any wind forecast (none exists that is authorized — see
`R2_AUDIT_AND_STOP_REPORT.md` Q2). It is not a full renewable-forecast experiment and must
not be reported or cited as one.
