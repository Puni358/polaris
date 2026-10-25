# Leakage + Degeneracy Audit — Uncertainty-Aware Terminal Reserve (Mechanism A)

RESEARCH-ONLY. Both gates must PASS before the 2x2 EMS factorial is run.

## Degeneracy gate

New formula (`compute_terminal_target_wh_v2`, mode='legacy') was compared against the imported, unmodified `compute_terminal_target_wh` from `run_research_simulation.py` for all 694 (origin, arm) pairs across the 347 2024 origins x {F, K}.

- Max abs diff: **0.000e+00 Wh**
- Tolerance: 1e-06 Wh
- **Result: PASS**

## Leakage gate

- Fitting function reads ONLY: `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`, `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`
- Fitting function has no reference to the 2024 matrix path anywhere in its code.
- Splits used in fit: `['TRAIN_2020_2021', 'VALIDATION_2022']`
- `BLIND_TEST_2023` rows in fit set: 0
- 2024 rows in fit set: 0
- **Result: PASS**

## Fit input hashes

- `matrix_38_feature_2020_2023`: `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde`
- `historical_residual_dataset_2020_2023`: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`

## SIGNAL VALIDITY GATE — FAIL (blocking; discovered after the two gates above passed)

Both the degeneracy gate and the leakage gate passed cleanly. However, inspecting the
fitted artifact (`FIT_ARTIFACT.json`) surfaced a prerequisite problem that neither gate
checks for: **`disagreement_fold` — the exact signal Mechanism A was instructed to use
("disagreement_fold decile x horizon") — is identically `0.0` for every single daytime row
in the ENTIRE frozen `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv`**, not just in the
`TRAIN_2020_2021`/`VALIDATION_2022` fitting population but also in `BLIND_TEST_2023`
(verified directly, for disclosure only — `BLIND_TEST_2023` was never used in fitting).
Confirmed by direct inspection:

```
TRAIN_2020_2021 + VALIDATION_2022, all 12,206 daytime rows: disagreement_fold == 0.0 for 100.0% of rows
TRAIN_2020_2021 + VALIDATION_2022, 462 lookahead-window (hour-ahead 19-24) daytime rows: disagreement_fold == 0.0 for 100.0% of rows
BLIND_TEST_2023, all 5,187 rows: disagreement_fold == 0.0 for 100.0% of rows
```

Consequently the computed decile edges collapsed to `[0.0, 0.0, ..., 0.0]` (11 identical
edges), `pd.cut` could not form any non-degenerate bins, and `per_decile_n` is empty — there
is **no decile stratification at all**, only a single degenerate pooled value. Running the
2x2 factorial as-is would silently test nothing but a flat additive constant dressed up as
"uncertainty-aware," which is not Mechanism A as specified and would misrepresent the
experiment.

**For contrast (disclosure only, not used anywhere in fitting):** `disagreement_fold` in the
2024 application-side matrix (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`) is
**not** degenerate — mean 44.05, std 71.99, range [0.00003, 459.29] across 8,328 rows. The
signal exists and varies meaningfully in 2024; it simply was never populated with real
variance in the 2020-2023 feature-matrix build used for fitting. (`ctx_std_3h`, the
alternate signal named for Mechanism B in the research design doc — not authorized for use
here — has some variance in TRAIN+VAL, 50th percentile 0.0 but mean 0.58/max 10.39/std 1.56,
i.e. zero-inflated but not fully degenerate; noted only for transparency, not substituted.)

**Result: FAIL.** Per the explicit instruction "do not invent or silently choose governance
values" and "if any gate fails, STOP before the factorial EMS experiment," the 2x2 EMS
factorial was **NOT run**. Substituting a different signal, or proceeding with a degenerate
single-bin "stratification," would both be an unauthorized, undisclosed deviation from the
committed Mechanism A specification. This is reported back for a decision rather than
silently resolved.
