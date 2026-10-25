# PHASE10_CANDIDATE_C_DESIGN_CHECKPOINT

**Status:** DESIGN_FROZEN_PENDING_TRAINING
**Candidate C has NOT been trained. No training has occurred. No ODD access has occurred.**
**Date:** September 2026
**ODD Firewall:** INTACT — ODD not accessed at any point during this design phase
**Protected Champion:** Stage 8.1 37-feature HGB — NOT MODIFIED, NOT REPLACED

---

## 0. Provenance / Audit Completeness Notice (read first)

This audit was performed against the files available in this session:
`POLARIS_COMPLETE_EXPERIMENT_HISTORY.md`,
`PHASE9_MASTER_CLOSURE_CHECKPOINT.json`, and the Phase 10 Candidate A design
checkpoints. **This session has no filesystem access to the local POLARIS
environment (`~/01polaris (Copy)`)** — only uploaded files were inspected.

Two important gaps were found and are disclosed here rather than papered
over:

- **Stage 5.2 ("Architecture A — GBDT residual corrector")** does not appear
  in any uploaded document. Its description in this checkpoint is taken
  **entirely from the user's characterization in the Candidate C request
  message**, not from an independently verified design doc or source file.
- **Phase 10 Candidate B** exists only as two one-line mentions inside the
  Candidate A checkpoint ("symmetric multi-task embedding (permutation
  invariant)"). No Candidate B design checkpoint has been uploaded to this
  session.
- **"Stage 4: Horizon-Adaptive Cloud-Damped Clear-Sky Ensemble"** does not
  appear under that exact name. The closest matches in the uploaded history
  are Stage 4.1 ("Cloud Regime Affine: GBDT + Affine Residual") and Stage 4.3
  ("Ensemble Hybrid: Dynamic Ridge Blend", historical champion), documented
  only as one-line summary-table entries with MAE/feature-count, no design
  checkpoint or implementation file.

If a more rigorous, independently-verified audit of Stage 4 and Stage 5.2 is
required before training, the corresponding design checkpoints / scripts
should be uploaded and this document revised accordingly. Everything below
was still designed conservatively around the information available,
including the user's own description of Stage 5.2, which is treated as
reliable for the purpose of avoiding duplication.

---

## 1. Forensic Audit Summary

| # | Approach | Source | Mechanism | Target | Correction | Status |
|---|---|---|---|---|---|---|
| 1 | Stage 4 (4.1 / 4.3) | History table only, no design doc | Cloud-regime affine adjustment (4.1); dynamic Ridge blend of Stage 3B/3C/affine (4.3) | Absolute SW_IN via blended predictions | Linear blend / affine, not a learned nonlinear residual net | Superseded pre-dates current EVEN/ODD 173/174 gate protocol |
| 2 | Stage 5.2 | **User-supplied description only** — no doc found | Presumed: 2nd-stage GBDT regresses `(actual − first_stage_pred)`, added back to frozen anchor | Residual | Additive, tree-based, row-independent | Referenced only as "the pattern to avoid duplicating" |
| 3 | Phase 9 Candidate 2 | `PHASE9_MASTER_CLOSURE_CHECKPOINT.json` | Tested `disagreement_fold` as a standalone correlate of error | N/A (correlation study, no trained corrector) | **None built** | `REAL_BUT_PARTIAL_NOT_STANDALONE`; explicit note that a directional correction paired with disagreement "has not been designed or tested" |
| 4 | Candidate B | Two one-line mentions only, no design doc | Presumed: shared trunk + horizon embedding, joint multi-horizon regression | Absolute SW_IN, jointly | None — single-stage, no anchor/residual decomposition | Result unknown to this session |
| 5 | Candidate A | Full design checkpoints (original + 6,113-param corrected) | Bidirectional GRU over 24-horizon sequence | Absolute SW_IN per horizon | None — single-stage sequence regression | Design frozen at 6,113 params; **not yet trained** |

---

## 2. Duplication Risks Identified

- A plain "predict residual, add back" architecture is Stage 5.2 by the
  user's own description — the explicit pattern to avoid.
- A second tabular GBDT on the same 39 features would also duplicate Stage
  5.2 regardless of framing.
- Using `disagreement_fold` as a plain input feature to a tabular/NN model
  would re-tread Phase 9 Candidate 2's already-explored, only-partially-
  useful territory (magnitude-informative, direction-uninformative alone).
- A joint end-to-end multi-horizon regressor with no anchor/residual
  decomposition collapses into Candidate B.
- Any model coupling information across horizons (recurrent or attention
  over the 24-step sequence) collapses into Candidate A.

**The one identified, on-record, genuinely untested gap:** Phase 9
Candidate 2 explicitly logged that pairing `disagreement_fold` with a
learned **directional** correction had not been designed or tested. No
audited approach (Stage 4, Stage 5.2 as described, Phase 9 C2, Candidate A,
or Candidate B as described) does this.

---

## 3. Candidate C: Disagreement-Gated Residual MLP

### 3.1 Core idea

A frozen physical anchor plus a small MLP that outputs a residual
**magnitude** and a **gate** from a shared hidden layer. The applied
correction is `gate x magnitude`, so the network can learn to suppress the
correction toward zero when models agree and let it through when they
disagree — directly instantiating the untested "directional correction
paired with disagreement" hypothesis from Phase 9 Candidate 2's closure
notes.

### 3.2 Exact architecture

```
Anchor (frozen, raw W/m^2):  pred_stage4_fold  (existing feature, unmodified)

Input:                        39 standardized features  [batch, 39] (row-wise, no sequence)

Shared trunk:
  Dense(39 -> 16), ReLU
  Dropout(0.2)

Magnitude head:  Dense(16 -> 1), linear         -> m(x)
Gate head:       Dense(16 -> 1), Sigmoid         -> g(x) in [0,1]

Correction:      g(x) * m(x)
Final output:    y_hat = anchor + correction
```

### 3.3 First-stage status

**Frozen.** `pred_stage4_fold` is read directly from the existing 39-feature
matrix (an upstream, already-computed prediction). It is not retrained, not
fine-tuned, and no gradient flows into producing it. It is used twice: once
in raw W/m^2 form as the additive anchor, and once (its standardized copy)
as one of the 39 inputs to the shared trunk — no new feature is created.

### 3.4 Parameter count

| Layer | Calculation | Count |
|---|---|---|
| Shared Dense (39->16) | 39x16 + 16 | 640 |
| Magnitude head (16->1) | 16x1 + 1 | 17 |
| Gate head (16->1) | 16x1 + 1 | 17 |
| **TOTAL** | | **674** |

Verification method: same as Candidate A — direct instantiation in PyTorch
(`nn.Linear` x3) and `sum(p.numel() for p in model.parameters())`, to be
confirmed at implementation time before training (not yet run).

### 3.5 Loss, optimizer, regularization

- Loss: MAE between `y_hat` and `actual_SW_IN` (row-wise; mathematically
  equivalent to MAE on the residual since the anchor is a fixed per-row
  offset).
- Optimizer: Adam, lr=1e-3, betas=(0.9, 0.999), eps=1e-7 — reused from the
  already-locked Candidate A hyperparameters, not newly tuned.
- Weight decay: 1e-4.
- Regularization: Dropout 0.2 after the shared hidden layer.
- No hyperparameter sweep performed or planned.

### 3.6 Batch construction

8 origins per batch (192 rows). Rows are processed independently by the
model (no cross-horizon coupling exists in this architecture) — batching is
origin-grouped only to keep the protocol consistent and comparable with
Candidates A and B, and to avoid any accidental origin leakage across
batches during a single epoch.

### 3.7 Epochs / early stopping

max_epochs = 300, patience = 20 — reused locked values, unchanged from
Candidate A.

### 3.8 Preprocessing / scaling

StandardScaler fit on inner-training-fold origins only, applied to
train/val/test. The anchor (`pred_stage4_fold`) is additionally kept in its
**raw, unstandardized** form for the final additive step; the standardized
copy still appears as one of the 39 network inputs.

### 3.9 Fold protocol

5-fold GroupKFold by origin_id, EVEN only (173 origins), identical to
Candidate A.

### 3.10 Inner validation protocol

Nested 80/20 split by origin within each outer training fold. Deterministic,
same formula as the corrected Candidate A checkpoint:

```
seed = INNER_SPLIT_BASE_SEED + fold_idx
INNER_SPLIT_BASE_SEED = 42
fold_idx in 1..5
```

Internal validation origins are always a subset of that fold's training
pool, never the test fold; test-fold origins are never used for early
stopping.

### 3.11 Random seeds

Model initialization and dropout: `torch.manual_seed(42 + fold_idx)` per
outer fold, recorded per fold at training time (not yet run).

### 3.12 Causal justification

Candidate C introduces **zero new features or data sources**. Every input
(the 39 features, including `pred_stage4_fold` and `disagreement_fold`) was
already causally verified as available at t0 in the Candidate A design
checkpoint's Section 4 causality audit. No new causal risk is introduced.

---

## 4. Why Candidate C Is Distinct

- **From Stage 5.2 (as described):** neural (small MLP), not GBDT; imposes
  an explicit multiplicative gate structure (`g(x) * m(x)`) that a generic
  tree-based residual regressor would not necessarily reproduce, and is
  purpose-built around the disagreement-direction question rather than a
  generic tabular residual fit.
- **From Phase 9 Candidate 2:** Candidate 2 only measured a correlation and
  explicitly did not build a directional corrector. Candidate C *is* that
  untested directional correction, operationalized as a learned gate rather
  than a raw feature.
- **From Candidate B (as described):** Candidate B is single-stage,
  symmetric across horizons, and predicts the absolute target directly with
  no frozen anchor or residual decomposition. Candidate C is explicitly
  anchor + gated-residual, row-wise, asymmetric by design (gate output is
  intentionally unconstrained per-row, not shared/embedded across horizons).
- **From Candidate A:** Candidate A models cross-horizon temporal dependency
  via a bidirectional GRU; Candidate C has no sequence coupling at all — it
  is deliberately row-independent, and its distinguishing structure is the
  anchor/gate/residual decomposition, not temporal modeling.
- **Worth testing despite A and B:** A and B both compete on the same axis —
  a single learned function predicting the absolute target end-to-end.
  Candidate C never attempts that axis. It tests a structurally different,
  previously-flagged-but-unbuilt hypothesis (gated residual correction
  anchored to an existing physical prediction). Its outcome is informative
  independent of how A or B perform.

---

## 5. Locked Protocol (unchanged, inherited from prior phases)

- 347 total origins; 173 EVEN (development); 174 ODD (firewalled test).
- EVEN-only candidate development.
- 5-fold GroupKFold by origin.
- Nested inner 80/20 validation, deterministic, recorded per fold.
- ODD firewall intact — no access planned or performed.
- G1–G6 unchanged (see Candidate A checkpoint for full text); control
  baseline unchanged (reconstructed EVEN HGB: MAE 26.3668 W/m^2, nMAE
  20.4507%, RMSE 55.2513 W/m^2).
- No feature additions. No arbitrary hyperparameter sweeps.
- No ODD evaluation unless all EVEN gates pass for Candidate C.
- Official Stage 8.1 champion remains protected and unmodified.

---

## 6. DO NOT REPEAT

| Pattern | Where it was already tried | Why Candidate C avoids it |
|---|---|---|
| Second-stage GBDT residual regression on full tabular feature set | Stage 5.2 (per user description) | Candidate C uses a small MLP with an explicit gated-magnitude structure, not a tree ensemble |
| Disagreement as a raw/plain input feature with no directional mechanism | Phase 9 Candidate 2 | Candidate C routes disagreement-relevant information through a dedicated sigmoid gate that scales a learned correction |
| Single-stage symmetric multi-horizon joint regression | Candidate B (as described) | Candidate C is explicitly two-stage: frozen anchor + gated residual |
| Sequence/temporal coupling across the 24 horizons | Candidate A | Candidate C is strictly row-wise, no recurrence or attention over horizons |
| Linear/affine blend of upstream predictions | Stage 4.1 / 4.3 | Candidate C's correction is a learned nonlinear (ReLU + sigmoid gate) function, not a linear blend |

---

## 7. Status

- Design: **FROZEN**
- Parameter count: **674** (to be confirmed by direct PyTorch instantiation
  at implementation time, not yet run)
- Training: **NOT PERFORMED**
- ODD: **NOT ACCESSED**
- Next step: **AWAITING EXPLICIT USER AUTHORIZATION TO IMPLEMENT AND TRAIN**

No training will proceed until explicit authorization is given for this
exact frozen configuration.
