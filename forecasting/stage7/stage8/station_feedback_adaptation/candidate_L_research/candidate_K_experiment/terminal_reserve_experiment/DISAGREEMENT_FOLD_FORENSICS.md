# `disagreement_fold` Forensics — Why It Is Constant 0.0 in 2020–2023 but Variable in 2024

**RESEARCH-ONLY. Read-only investigation. No files modified. No experiment run. No
production, Stage 8.1, F, K, or immutable artifact touched.**

## 1. What `disagreement_fold` represents

`disagreement_fold = |pred_stage3b_cloud_nwp − phys_pred_fold|` — the absolute difference
between two independently-derived solar predictions for the same forecast origin/horizon:

- `phys_pred_fold`: a **pure physics-based** estimate,
  `max(0, clearsky_ghi * (1 − k_h * cloud_frac))`, computed directly from clearsky
  geometry and NWP cloud fraction with a per-horizon ensemble parameter `k_h` — no neural
  model involved.
- `pred_stage3b_cloud_nwp`: the output of the **Stage 3B** model, a frozen Chronos-2 neural
  forecast blended with NWP cloud-cover covariates (`stage3/run_stage3b_2025.py`'s docstring
  describes it as "Chronos-2 + solar geometry + fc_cloud_cover, frozen checkpoint, no
  retraining" — the same 2024-locked branch of `stage3/run_stage3_experiments.py`).

By construction, `disagreement_fold` is meant to measure **ensemble disagreement between a
physics model and a neural/NWP model** — a genuine, model-based uncertainty proxy, present
in the 38-feature contract (`CANDIDATE_37_FEATURES` + `elevation_x_cloud_frac`) used by
Candidate F.

## 2. How it was constructed for 2020–2023

Build script: `candidate_L_research/build_candidate_L2_feature_matrix.py` (lines ~100–113).
Traced line by line:

```python
df['phys_pred_fold'] = np.round(phys_preds, 4)          # computed from clearsky/cloud, as above
df['pred_stage3b_cloud_nwp'] = df['phys_pred_fold']      # <-- hard proxy assignment
...
df['pred_stage4_fold'] = np.round(stage4_preds, 4)        # = w_h * phys + (1-w_h) * phys = phys
df['disagreement_fold'] = np.abs(df['pred_stage3b_cloud_nwp'] - df['phys_pred_fold'])  # = 0 always
```

The script never loads or computes a genuine Stage 3B (Chronos-2) prediction for the
2020–2023 period at all — there is no Chronos inference call, no checkpoint load, nothing.
It simply **sets `pred_stage3b_cloud_nwp` equal to `phys_pred_fold`** as a placeholder to
satisfy the 38-feature schema, then computes `disagreement_fold` from that proxy. This is
documented and already flagged by a prior audit in this same research line
(`CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md`, §7.3: "PROXY SUBSTITUTION ... forcing
equality sets disagreement feature identically to 0.0").

A second-order consequence (not asked about here, but directly visible in the same code):
`pred_stage4_fold` for 2020–2023 collapses to `phys_pred_fold` too, since
`w_h * pred_stage3b_cloud_nwp + (1-w_h) * phys_pred_fold` reduces to `phys_pred_fold` when
`pred_stage3b_cloud_nwp = phys_pred_fold`. Noted for the record; out of scope to resolve here.

## 3. Why it is constant 0.0 there

Direct algebraic consequence of §2: `|x − x| = 0` for every row, because the two operands
were never independent values for this period — one was defined as a copy of the other.
This is not a property of the real solar/weather physics at this site; it is a property of
how this specific historical feature matrix was assembled.

## 4. How it is constructed for 2024, and why variance exists there

For 2024, `build_corrected_feature_matrix.py` (`stage7/stage8/stage8_1_corrected_2025/`)
loads `s4_preds = pd.read_csv(cfg["stage4_preds_path"])` from
`stage4/stage4_results/ensemble_predictions.csv`, which **already contains a genuine,
independently-computed `pred_stage3b_cloud_nwp` column** — confirmed directly: that CSV's
header includes `pred_stage3b_cloud_nwp` and `pred_ensemble` as real, distinct columns. This
value traces back to `stage3/stage3b_cloud_nwp_predictions.csv` (8,329 rows, confirmed date
range `2024-01-20` to `2024-12-31` — 2024 only), the actual output of the frozen Chronos-2
Stage 3B model, produced by a real neural-forecast inference run against 2024 NWP and
clearsky-decomposition inputs. `phys_pred_fold` for 2024 is computed independently, the same
physics formula as in §2 but using 2024's own clearsky/cloud inputs. Because the two
operands are now genuinely independent model outputs, `disagreement_fold` has real variance
(mean 44.05, std 71.99, range [0.00003, 459.29] across 8,328 rows — confirmed by direct
inspection).

## 5. Classification: expected / build limitation / bug / version mismatch?

**Build/extraction limitation, not a coding bug.** The `disagreement_fold` *formula* is
implemented identically and correctly in both the 2020–2023 and 2024 build scripts
(`np.abs(pred_stage3b_cloud_nwp - phys_pred_fold)` in both). The difference is entirely in
what `pred_stage3b_cloud_nwp` is populated with upstream: a genuine Stage 3B model output for
2024, vs. a hard-coded proxy equal to `phys_pred_fold` for 2020–2023, because the Stage 3B
model (Chronos-2 inference) was **never run against the 2020–2023 period** — there is no
`stage3b_cloud_nwp_predictions_2020_2023.csv` or equivalent anywhere in the repository (only
2024 and 2025 Stage 3B output files exist: `stage3/stage3b_cloud_nwp_predictions.csv`,
`stage3/stage3b_2025/stage3b_cloud_nwp_predictions_2025.csv`). This is the same root
category the prior audit already identified for the 14 `ctx_*` features in this same build
script — a missing-upstream-artifact substitution, not a formula defect, not a version
mismatch (the formula versions match; only the input provenance differs).

## 6. Can the 2020–2023 matrix be corrected/reconstructed without changing its frozen hash?

**No, in two independent senses, both blocking:**

1. **Trivially**: any correction to the content of
   `CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` (or the pre-export
   `CANDIDATE_L2_FULL_38_FEATURE_MATRIX_2020_2023.csv` it derives from) changes its bytes
   and therefore its SHA-256 hash by definition. A "correction that keeps the same frozen
   hash" is not a coherent possibility for an in-place fix — any genuine fix necessarily
   produces a **new, differently-hashed artifact**, not a repair of the existing one.
2. **Substantively, reconstruction from already-existing authoritative data is also
   blocked**: running the real Stage 3B model for 2020–2023 would require (a) a Chronos-2
   inference pass against 2020–2023 NWP inputs (technically conceivable in principle — the
   raw 2020–2023 MEPS archive is independently confirmed available and provenance-verified
   PASS by the prior audit) **and** (b) a clearsky-decomposition input file analogous to
   `data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv`, which
   `run_stage3b_2025.py` shows is itself derived from **real station SW_IN observations**.
   The prior forensic audit in this same directory
   (`CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md`, §4) already established, by exhaustive
   repository and local-archive search, that **no pre-2024 Mount Nuolja station SW_IN
   observations exist anywhere in this repository** — only 2024 and 2025 station files are
   present. Reconstructing a genuine Stage 3B output (and therefore a genuine
   `disagreement_fold`) for 2020–2023 is therefore blocked by a real missing-ground-truth
   dependency, not merely by unperformed computation — it would require acquiring new
   historical station data from outside this repository, which is out of scope for a
   read-only forensic investigation and was not attempted here.

## 7. Is Mechanism A still scientifically feasible with the existing data?

**No, not as specified** ("`disagreement_fold` decile × horizon", fit on
`TRAIN_2020_2021`/`VALIDATION_2022`). The entire 2020–2023 matrix — train, validation, and
blind-test splits alike — carries a `disagreement_fold` value that is a deterministic
artifact of a proxy substitution, not a measurement of anything about forecast uncertainty.
Fitting decile stratification on an all-zero column is not a data-scarcity problem that a
larger sample or a coarser bucket (as attempted in Stage 1 of this experiment, pooling the
lookahead window) can fix — the signal carries **zero information** in the fitting
population by construction, regardless of sample size. No valid regime-conditional margin
table can be estimated from it. This confirms and explains, rather than overturns, the
SIGNAL VALIDITY GATE FAIL already reported in `LEAKAGE_DEGENERACY_AUDIT.md`.

This finding is scoped strictly to Mechanism A as committed (this signal, this fitting
population). It says nothing about whether `disagreement_fold`'s genuine 2024 variance could
support a differently-scoped, differently-authorized experiment — that is a new mechanism
design question, explicitly out of scope for this investigation.

---

SIGNAL DEFINITION: `disagreement_fold = |pred_stage3b_cloud_nwp − phys_pred_fold|`, the
absolute disagreement between a physics-only clearsky/cloud solar estimate (`phys_pred_fold`)
and the frozen Stage 3B Chronos-2 neural-forecast-based estimate (`pred_stage3b_cloud_nwp`) —
intended as a genuine ensemble-disagreement uncertainty proxy.

2020-2023 CAUSE: `build_candidate_L2_feature_matrix.py` hard-codes
`pred_stage3b_cloud_nwp = phys_pred_fold` for the entire 2020–2023 period (Stage 3B/Chronos-2
was never run against this historical window), so `disagreement_fold = |x − x| = 0` for
every row by construction — a proxy substitution, not a real absence of model disagreement.

2024 CAUSE: `build_corrected_feature_matrix.py` loads a genuinely independent
`pred_stage3b_cloud_nwp` column from `stage4/stage4_results/ensemble_predictions.csv`,
traceable to the real Stage 3B Chronos-2 inference output
(`stage3/stage3b_cloud_nwp_predictions.csv`, 2024-only), which differs legitimately from the
separately-computed `phys_pred_fold` — producing genuine, non-degenerate variance.

DATA/BUILD BUG: NO — this is a documented, deliberate build/extraction limitation (missing
upstream Stage 3B model output for 2020–2023, substituted with a proxy), not a coding error
in the `disagreement_fold` formula itself, which is implemented identically and correctly in
both build scripts.

FROZEN ARTIFACT CORRECTION POSSIBLE: NO — not in-place (any correction changes the hash by
definition), and not even as a freshly-derived replacement from already-existing
authoritative data, because genuine reconstruction requires a Stage 3B clearsky-decomposition
input that itself depends on real pre-2024 Mount Nuolja station SW_IN observations, which a
prior audit in this research line already confirmed do not exist anywhere in this repository.

MECHANISM A STATUS: NOT SCIENTIFICALLY FEASIBLE with the existing 2020–2023 data as
specified. The signal is zero-information by construction in the required fitting
population (`TRAIN_2020_2021` + `VALIDATION_2022`), so no decile-conditional margin can be
estimated from it regardless of sample size or bucketing strategy.

NEXT ACTION: No action taken here (investigation only, as instructed). A decision is needed
on whether to (a) treat Mechanism A as blocked and close this research line, (b) seek
explicit authorization for a differently-scoped, differently-named mechanism using a signal
that does carry real information (e.g. `ctx_std_3h`, already noted as zero-inflated but not
fully degenerate in `LEAKAGE_DEGENERACY_AUDIT.md` — not implemented here, as instructed), or
(c) pursue new historical data acquisition (pre-2024 Nuolja station observations) as a
separate, larger-scope research/data-engineering effort outside this experiment's boundary.
