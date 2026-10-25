# PHASE10_CANDIDATE_A_DESIGN_CHECKPOINT — CORRECTED (6,113 parameters)

**Status:** DESIGN FROZEN — PARAMETER COUNT CORRECTED — AWAITING TRAINING AUTHORIZATION
**Supersedes:** `updatePHASE10_CANDIDATE_A_DESIGN_CHECKPOINT.md` (which stated 6,049 params)
**Date:** September 2026
**ODD Firewall:** INTACT — no ODD data accessed or referenced
**Protected Champion:** Stage 8.1 37-feature HGB — NOT MODIFIED, NOT REPLACED

---

## 1. What changed, and what did not

**The architecture is unchanged.** Every layer, dimension, activation, dropout
rate, and hyperparameter in the frozen design remains exactly as specified in
`updatePHASE10_CANDIDATE_A_DESIGN_CHECKPOINT.md` Section 3.1:

```
Input:              [batch, 24, 39]
Dense1:              39 -> 32, ReLU, Dropout 0.2
Bidirectional GRU:   32 -> 16 per direction, return_sequences=True, Dropout 0.2
Dense_out:           32 -> 1, Linear
Loss:                MAE over 24 horizons
```

**Only the expected total-parameter figure is corrected**, from 6,049 to
**6,113**, because the original figure was a hand-arithmetic error, not a
property of the actual architecture. This was discovered by implementing the
model in real `torch.nn.GRU(bidirectional=True)` and calling
`sum(p.numel() for p in model.parameters())`, rather than by changing any
layer shape or hyperparameter.

---

## 2. Root cause of the 6,049 -> 6,113 discrepancy

The original design checkpoint (Section 3.2) computed the GRU parameter count
by hand using:

```
2 x [3 gates x ((32+16)x16 + 16)] = 2 x 2,352 = 4,704
```

This formula assumes **one tied bias vector per gate** — i.e. that the
combined-input-and-hidden-state weight matrix has a single `+16` bias term
per gate. That is a valid way to implement a GRU cell, but it is **not** how
the standard `torch.nn.GRU` module (in PyTorch, and the equivalent in
TensorFlow/Keras when `use_bias=True` with default settings — note Keras
GRU also has an optional `reset_after` bias variant) parameterizes the cell.
Standard `nn.GRU` stores **two separate bias vectors per gate**:
`bias_ih` (applied to the input-to-hidden transform) and `bias_hh` (applied
to the hidden-to-hidden transform). This is standard practice (it allows
weight-normalization / cuDNN-fused kernels to treat the two transforms
independently) and is not something AI assistant introduced — it is the default,
unmodified behavior of `torch.nn.GRU(bias=True)`, which is the default.

For hidden_size=16, input_size=32, per direction:

| Term | Tied-bias formula (original doc) | Real `nn.GRU` |
|---|---|---|
| weight_ih (3 gates x 16 x 32) | 1,536 | 1,536 |
| weight_hh (3 gates x 16 x 16) | 768 | 768 |
| bias (per gate) | 16 x 3 = 48 (**one** bias vector) | 48 (`bias_ih`) **+** 48 (`bias_hh`) = 96 |
| **Total per direction** | 2,352 | 2,400 |
| **Bidirectional (x2)** | **4,704** | **4,800** |

Separately, the original doc's output Dense layer (32 -> 1) was stated as
"32x1 (weights) + 1 (bias) = **65**" (Section 3.2 table, and
`dense_output_weights: 64` in the JSON checkpoint). The correct arithmetic
for a 32-in, 1-out linear layer is `32*1 + 1 = 33`, not 65. This second error
was independent of the GRU bias issue and appears to have been a simple
transcription/arithmetic slip in the original hand calculation.

### Corrected total

| Layer | Params |
|---|---|
| Dense1 (39 -> 32) | 1,280 |
| Bidirectional GRU (32 -> 16x2, real `nn.GRU` bias convention) | 4,800 |
| Dense_out (32 -> 1) | 33 |
| **TOTAL** | **6,113** |

---

## 3. Verification method

The corrected figure was obtained two ways, which agree:

1. **Hand arithmetic** using the standard `nn.GRU` bias convention (table
   above): 1,280 + 4,800 + 33 = 6,113.
2. **Direct instantiation** of the frozen architecture as
   `nn.Linear(39,32)` + `nn.GRU(32,16,bidirectional=True,batch_first=True)`
   + `nn.Linear(32,1)`, summing `p.numel()` over all named parameters. This
   is implemented in `phase10_candidate_a_train.py`, function
   `count_parameters()`, and is printed/asserted in the audit step before any
   training occurs.

No layer shape, activation, dropout rate, or hyperparameter was changed to
reach this number. It is the actual, real parameter count of the exact
frozen architecture under a standard, unmodified `nn.GRU` implementation.

---

## 4. Updated gate/checkpoint fields

Wherever `updatePHASE10_CANDIDATE_A_DESIGN_CHECKPOINT.md` /
`updatePHASE10_CANDIDATE_A_DESIGN_CHECKPOINT.json` state:

```
total_parameters: 6049
```

that field is corrected to:

```
total_parameters: 6113
correction_note: "6,049 was a manual arithmetic error (tied-bias GRU
  assumption + output-layer miscount). Real torch.nn.GRU gives 6,113.
  Architecture unchanged."
```

All other frozen fields (feature inventory, 39 inputs, 14 static + 25
horizon-varying, causality verification, training procedure, gate
requirements G1-G6, control baseline) are unchanged and remain as specified
in the original design checkpoint.

---

## 5. Reproducibility of the nested inner 80/20 validation split

Per explicit instruction, the inner train/validation split (used only for
early stopping, never for test-fold evaluation) is deterministic and is now
explicitly recorded:

- **Seed formula:** `seed = INNER_SPLIT_BASE_SEED + fold_idx`, with
  `INNER_SPLIT_BASE_SEED = 42` and `fold_idx` running 1..5 (one seed per
  outer GroupKFold fold).
- **Selection procedure:** `np.random.RandomState(seed).choice(n_train_origins,
  n_val, replace=False)` over the index array of that outer fold's training
  origins (the origins remaining after the outer test-fold origins are
  removed). `n_val = max(1, round(0.2 * n_train_origins))`.
- **What is recorded:** for every outer fold, the script now writes the
  exact `inner_split_seed`, the resulting `train_inner_origins` list, and
  `val_inner_origins` list into both the console audit output and the
  results checkpoint JSON (`PHASE10_CANDIDATE_A_RESULTS_REAL.json`), so the
  exact split used for early stopping in any given run can be reconstructed
  or audited later without re-running training.
- **Guarantee unchanged:** internal validation origins are always a subset
  of that fold's training-origin pool and never include that fold's test
  origins; test-fold origins are never used for early-stopping decisions.

---

## 6. Status

- Architecture: **FROZEN, unchanged**
- Expected parameter count: **6,113 (corrected)**
- Inner-split reproducibility: **deterministic, seed formula recorded**
- Training: **NOT YET RUN** — awaiting explicit authorization to execute
  `phase10_candidate_a_train.py --train` in the local POLARIS environment
- ODD: **firewalled, untouched**

No further design changes are pending. This checkpoint corrects a reporting
error only.
