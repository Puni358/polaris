# PHASE 10 — CANDIDATE A FINAL RESULTS / CLOSURE

**Date:** 2026-09-14  
**Status:** `REJECTED_BY_EVEN_GATES`  
**Experiment validity:** `VALID`

## Candidate A

Frozen architecture:

```text
Input [batch, 24, 39]
→ Dense 39→32 ReLU
→ Dropout 0.2
→ Bidirectional GRU, hidden=16 per direction, return_sequences=True
→ Dropout 0.2
→ Dense 32→1 linear
```

Standard PyTorch `torch.nn.GRU` parameter count: **6,113**.

No proxy was used. The sequence structure `[origin, 24, 39]` was preserved.

## Protocol

- 173 EVEN origins only
- 5-fold GroupKFold by origin
- Nested deterministic inner 80/20 validation by origin
- Inner seed formula: `42 + fold_idx`
- StandardScaler fit on inner-training origins only
- ODD completely firewalled and not accessed

## Valid EVEN-OOF results

| Fold | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) |
|---:|---:|---:|---:|
| 1 | 53.0343 | 122.1581 | -45.9053 |
| 2 | 46.8871 | 111.8654 | -37.1397 |
| 3 | 45.4633 | 108.1309 | -38.7683 |
| 4 | 69.3759 | 151.2010 | -60.8768 |
| 5 | 59.3008 | 135.4479 | -51.0647 |
| **Aggregate** | **54.7022** | **126.5499** | — |

All five folds show strong negative bias.

The Phase 10 reconstructed EVEN HGB control is approximately **26.47 W/m² MAE**, so Candidate A is substantially worse.

## Gate verdict

- **G1:** FAIL — no MAE improvement
- **G2:** FAIL — 0/5 folds improved
- **G3:** FAIL — large fold degradations
- **G4:** FAIL — MAE/RMSE worse than control
- **G5:** PASS — causal/protocol compliance
- **G6:** Not needed to establish rejection; the candidate decisively fails G1–G4

### Final verdict

**CANDIDATE A — REJECTED BY EVEN GATES.**

This is a **valid rejection**, unlike the earlier invalid Candidate A attempt, which used a flattened sklearn MLP instead of the specified GRU.

## Repeat-prevention lock

Do **not** repeat this same Candidate A Bi-GRU experiment.

Do **not** create A.1/A.2 rescue variants or tune this architecture unless Phase 10 is explicitly reopened with a new preregistered architecture.

Do **not** evaluate Candidate A on ODD.

The protected Stage 8.1 HGB champion remains unchanged.

## Phase 10 state

Candidate B: rejected.  
Candidate A: valid experiment, rejected.  
ODD: locked.  
Protected champion: Stage 8.1 37-feature HGB.

The next work should move to the **next preregistered architecture**, not repeat Candidate A.
