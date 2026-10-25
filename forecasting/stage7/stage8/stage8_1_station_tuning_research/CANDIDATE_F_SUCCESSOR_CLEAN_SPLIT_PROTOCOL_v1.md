# Candidate F Successor — Clean Data & Training Protocol (v1, SPECIFICATION ONLY, NOT IMPLEMENTED)

**Date:** 2026-10-12. **Status: DRAFT PROTOCOL — no data has been partitioned under this protocol, no ensemble parameter has been fit, no model has been trained.** This document is a companion to `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md`. Neither modifies, overwrites, or supersedes the existing Candidate F contract, model, or the two existing audit documents in this folder.

## 1. Provenance trace (reused from existing, already-verified audits — not re-derived here)

| Component | Provenance | Status |
|---|---|---|
| Candidate F GBDT weights | `phase2_candidateF_additive_feature.py:143`, trained on 2024-EVEN only | `TRAINING_INTEGRITY_VERIFIED` (per `TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md` §D) |
| `k_h`/`w_h`, 2024 (`stage4/stage4_results/ensemble_parameters.json`) | Fit on 2024-EVEN `actual_SW_IN` only (`run_stage4_pipeline.py:156-160,271-285`) | `TRAINING_INTEGRITY_VERIFIED` relative to the 2024-EVEN/ODD split |
| `k_h`/`w_h`, 2025 (`stage4/stage4_results_2025/ensemble_parameters.json`) | Fit on **2025-EVEN realized `actual_SW_IN`** (`run_stage4_pipeline_2025.py:200-203,304,317-341,347-348`) | **`TRAINING_CONTAMINATION_VERIFIED`** — this is the finding this protocol exists to remediate |
| `lwp_latest`/`iwp_latest`/`lwp_x_cloud` | Same-day 00Z `meps_det_pl` run (`run_stage6_6.py:214,223-230`) | `UNAVAILABLE_AT_CUTOFF_VERIFIED` (per the same audit, §I) — this protocol assumes these are replaced per the companion feature contract, not reused |

## 2. Mandatory remediation: the 2025 ensemble-parameter contamination

**This protocol does not permit reusing `stage4/stage4_results_2025/ensemble_parameters.json` or any feature derived from it (`pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, for 2025 rows) as a clean blind-evaluation input, under any circumstance.**

Two remediation options are specified (neither implemented here):

- **Option A — reuse-forward:** apply the existing, already-clean 2024-fit `k_h`/`w_h` (`stage4/stage4_results/ensemble_parameters.json`) to 2025 rows directly, without any 2025-specific re-fitting. This is the simpler, more conservative option, since it introduces no new fitting step and no new data-acquisition requirement.
- **Option B — re-fit-on-permitted-data:** re-fit `k_h`/`w_h` for 2025 using only data available before the 2025 evaluation period begins (i.e., 2024 data, under the same methodology as `run_stage4_pipeline_2025.py` but with its `even_origins`/`train_mask` restricted to pre-2025 origins). This requires new code and a new, separately-hashed parameter artifact — not performed here.

**This protocol recommends Option A as the minimal-change path**, since it requires no new fitting run and no new data acquisition, and because Option B would itself need its own reproducibility/hash controls before being trusted — but it does not implement either option. **Until one of these is actually executed, no 2025 evaluation under this protocol may proceed**, per this protocol's own gate (§5).

## 3. Partition definition

Reusing the existing origin-count convention (not inventing a new one):

| Partition | Origins | Rows | Source |
|---|---|---|---|
| **Train** | 2024-EVEN origins (per the existing `even_origins = origins[::2]`-style split already used by `phase2_candidateF_additive_feature.py` and `run_stage4_pipeline.py`) | Half of 347 2024 origins (exact count not re-derived in this protocol; read directly from `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`'s existing EVEN/ODD split column at implementation time) | `stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` (347 origins, 8,328 rows total, confirmed by direct count this session) |
| **Validation** | 2024-ODD origins | The remaining half of 347 | Same file |
| **Blind** | All 2025 origins, used whole (no internal EVEN/ODD split, per the existing Candidate F methodology stated in `CANDIDATE_F_REPORT.md:8-15`) | 364 origins, 8,736 rows (confirmed by direct count this session) | `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` |

**Origin-grouping rule:** all 24 horizon rows of a given `forecast_start` origin stay together in the same partition — no origin may contribute rows to more than one partition. This is already the existing matrices' own structure (one row per `(forecast_start, horizon_hour)` pair, 24 per origin); this protocol requires that any new 18Z-sourced feature column be joined onto these existing rows **by the same `(forecast_start, horizon_hour)` key**, never by a separate re-indexing that could misalign origins.

**No new partition boundary is introduced by the 18Z feature replacement** — the replacement changes two columns' *values*, not the row/origin structure, so the existing EVEN/ODD/blind boundaries are reused unchanged.

## 4. Fitting-window rules

- Any learned parameter (GBDT weights, `k_h`/`w_h`, or any future addition) **must be fit using Train-partition rows only**.
- Validation-partition rows may be used only for the decisions the existing methodology already permits (reporting held-out MAE/RMSE/bias; the existing bootstrap CI procedure) — never for additional fitting, feature selection, or hyperparameter tuning beyond what `phase2_candidateF_additive_feature.py` already fixed (architecture and hyperparameters are **frozen**, inherited unchanged from the existing Candidate F report, not re-tuned by this protocol).
- Blind-partition rows (2025) **must not** be read, inspected, or used for any fitting, tuning, or feature-construction decision before the final evaluation. This includes the ensemble-parameter remediation in §2 — whichever option is chosen, it must use only pre-2025 data, never 2025 `actual_SW_IN`.

## 5. Stop conditions (this protocol's own gate — not yet cleared)

This protocol explicitly **stops** rather than proceeding if any of the following are not yet true. **As of this document's creation, none of the following has been done:**

1. The 2025 ensemble-parameter remediation (§2, Option A or B) has not been executed.
2. The 18Z feature contract (`CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md`) has not been implemented in code — no fetcher exists, no new feature matrix exists.
3. No row-selection/split-manifest file exists yet reflecting this protocol (it would be a straightforward derivation from the existing matrices' own origin lists, but has not been generated).
4. No new model has been trained.

**Given 1–4, this protocol cannot currently support a defensible clean evaluation, and none is authorized or implied by this document.** This is a design specification only.

## 6. What would unblock Phase 3/4 (training/evaluation) — not performed here

1. Implement the §2 remediation (Option A recommended) and produce a new, hashed parameter artifact (or confirm reuse of the existing 2024-fit file with its existing hash, under Option A).
2. Implement the feature contract: write a new, isolated fetcher (per `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md` §8) and run it against the ≈347 2024 + ≈364 2025 origins to build new `lwp_18z_fc`/`iwp_18z_fc`/`lwp_x_cloud_18z` columns, merged onto the existing matrices by `(forecast_start, horizon_hour)`.
3. Generate and hash a split-manifest file recording the exact origin lists per partition.
4. Train a new model (same frozen architecture/hyperparameters as Candidate F) on the Train partition only, hash the resulting artifact, and record the training command/environment.
5. Only then: freeze the evaluation code/metrics/acceptance criteria, hash them, and run the blind evaluation exactly once.

None of steps 1–5 were performed in this session. Step 2 in particular requires roughly 700 new external network requests against MET Norway's live THREDDS archive — a large-scale data-acquisition operation this protocol does not undertake without separate, explicit authorization to do so.
