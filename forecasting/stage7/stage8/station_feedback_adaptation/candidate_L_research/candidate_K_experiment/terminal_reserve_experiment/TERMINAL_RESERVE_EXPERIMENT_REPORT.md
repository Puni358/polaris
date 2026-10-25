# Uncertainty-Aware Terminal Reserve Experiment — Mechanism A (CONDITIONAL GO)

**RESEARCH-ONLY. The 2x2 EMS factorial was NOT run. No production, Stage 8.1, F, K, or
immutable artifact was modified. Nothing promoted.**

## What was executed

Stage 1 only (`fit_and_gates.py`), per
`UNCERTAINTY_AWARE_TERMINAL_RESERVE_RESEARCH_DESIGN.md`'s conditional-go requirements:

1. Verified hashes of all frozen fitting/EMS-side inputs (all MATCH).
2. Fit Mechanism A's margin lookup table (`disagreement_fold` decile × terminal-reserve
   lookahead window) strictly on `TRAIN_2020_2021` + `VALIDATION_2022` rows of
   `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` joined to
   `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`. **Disclosed deviation**: fit as
   decile × lookahead-window-membership rather than decile × individual horizon-hour,
   because individual horizons beyond hour-ahead 19 have only 1 daytime sample each in
   TRAIN+VAL at this Arctic site (see `FIT_ARTIFACT.json["methodological_deviation"]`).
3. Ran the **degeneracy gate**: the new formula (`compute_terminal_target_wh_v2`,
   `mode='legacy'`) vs. the imported, unmodified `compute_terminal_target_wh` from
   `run_research_simulation.py`, across all 347 2024 origins × {F, K} = 694 (origin, arm)
   pairs. **Result: PASS** — max abs diff `0.000e+00` Wh, tolerance `1e-6` Wh.
4. Ran the **leakage gate**: confirmed the fitting function reads only the two frozen
   2020-2023 files, never opens the 2024 matrix, and used only `TRAIN_2020_2021` +
   `VALIDATION_2022` rows (0 `BLIND_TEST_2023` rows, 0 2024 rows). **Result: PASS**.
5. Discovered, while inspecting the fit artifact (not something either gate above checks
   for), a **blocking data-validity problem** — see below. The 2x2 EMS factorial was
   **stopped before it was run**, per instruction ("If any gate fails, STOP before the
   factorial EMS experiment").

## Blocking finding: SIGNAL VALIDITY GATE — FAIL

`disagreement_fold` — the exact signal Mechanism A was scoped to ("disagreement_fold decile
× horizon") — is **identically `0.0` for every daytime row in the entire frozen
`CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`**: not just the
`TRAIN_2020_2021`/`VALIDATION_2022` fitting population (12,206 daytime rows, 462 of them in
the terminal-reserve lookahead window), but, checked for disclosure only and never used in
fitting, `BLIND_TEST_2023` as well (5,187 rows, all exactly `0.0`). The computed decile
edges collapsed to eleven identical `0.0` boundaries; no non-degenerate stratification is
possible from this signal in this dataset. Full detail, including the exact counts and the
2024-side contrast, is in `LEAKAGE_DEGENERACY_AUDIT.md`.

For disclosure/contrast only (not used in fitting, not a substitution): `disagreement_fold`
in the 2024 application-side matrix is **not** degenerate (mean 44.05, std 71.99, range
[0.00003, 459.29] across 8,328 rows) — the signal exists and varies meaningfully in 2024; it
was simply never populated with real variance in this particular frozen 2020-2023
feature-matrix build. `ctx_std_3h` (named only for Mechanism B, not authorized for use here)
has some variance in TRAIN+VAL — noted only for transparency, not substituted or used.

Running the factorial despite this would have meant either silently substituting a
different signal or running a single degenerate bin while calling it "uncertainty-aware" —
both unauthorized, undisclosed deviations from the committed Mechanism A design. Per
instruction ("Do not invent or silently choose governance values"), this is reported back
for a decision rather than resolved unilaterally.

## What this means for the open research question

The research question from `UNCERTAINTY_AWARE_TERMINAL_RESERVE_RESEARCH_DESIGN.md` —
"can an uncertainty-aware terminal reserve recover the EMS reliability K loses under the
fixed-margin formula" — **remains untested**. This is not a negative result for Mechanism A;
it is a data-availability blocker discovered before any EMS outcome was measured. Plausible
paths forward (decision needed, not taken here): (a) investigate why `disagreement_fold`
was never populated with variance in the 2020-2023 feature-matrix build and, if it can be
legitimately recomputed from already-frozen upstream NWP/physical-model outputs without
re-deriving F or K, regenerate it there; (b) seek explicit authorization to use a different
already-existing signal (e.g. `ctx_std_3h`) for an explicitly-relabeled mechanism, not
Mechanism A as specified; (c) re-scope the experiment to the 2024 matrix's own internal
train/apply split instead of 2020-2023 (a materially different, not-yet-designed
experiment, since the current design's leakage control relies on the 2020-2023
`TRAIN`/`VALIDATION`/`BLIND_TEST` split structure that the 2024 matrix does not have).

## Files

- `fit_and_gates.py` — the Stage 1 script (fitting, degeneracy gate, leakage gate)
- `FIT_ARTIFACT.json` — fitted margin table, sample sizes, disclosed methodological deviation
- `GATE_RESULTS.json` — degeneracy + leakage gate results (machine-readable)
- `LEAKAGE_DEGENERACY_AUDIT.md` — full gate audit, including the signal-validity finding
- `TERMINAL_RESERVE_EXPERIMENT_MANIFEST.json` — hashes of all inputs and new outputs
- `TERMINAL_RESERVE_EXPERIMENT_REPORT.md` — this report

No origin-level or aggregate EMS results exist for this experiment — the factorial was not
run.

---

DEGENERACY GATE: **PASS** (max abs diff 0.000e+00 Wh vs. tolerance 1e-6 Wh, n=694 origin-arm pairs)

LEAKAGE GATE: **PASS** (fit used only TRAIN_2020_2021 + VALIDATION_2022; 0 BLIND_TEST_2023 rows; 0 2024 rows)

MECHANISM A RESULT: **NOT TESTED** — blocked before the factorial by a newly-discovered SIGNAL VALIDITY GATE FAIL: `disagreement_fold` is identically 0.0 across the entire frozen 2020-2023 matrix, so no decile stratification (the core of Mechanism A) is possible from this signal in this dataset.

EMS RESULT: **NOT RUN** — the 2x2 factorial (F/K × existing/uncertainty-aware reserve) was never executed; no unmet-load, reliability, diesel, curtailment, EFC, or terminal-SOC numbers exist for this experiment.

GOVERNANCE STATUS: No governance value was invented or silently chosen. The quantile sweep (`Q_SWEEP = [0.75, 0.90, 0.95]`) and `MIN_CELL_N = 15` are recorded in `FIT_ARTIFACT.json`, explicitly labeled RESEARCH-ONLY, and were never exercised against real stratified data because stratification itself failed. All frozen inputs verified by hash; no production, Stage 8.1, F, K, or immutable artifact touched.

PROMOTION STATUS: Nothing promoted. Candidate K remains research-only. This experiment neither supports nor refutes promoting K — it did not reach the point of producing an EMS result.
