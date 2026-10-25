# PHASE 10 — CANDIDATE B FINAL REJECTION CHECKPOINT

**Date:** 2026-09-14  
**Status:** `REJECTED_BY_EVEN_GATES`  
**Experiment validity:** `VALID`

## Architecture

Shared MLP with learned 24-horizon embedding, jointly trained across all horizons of each origin using the frozen 39-feature input space.

## EVEN-only results

| Metric | Control | Candidate B |
|---|---:|---:|
| MAE | 26.3668 | **26.0112 W/m²** |
| RMSE | 55.2513 | **54.2820 W/m²** |
| nMAE | 20.4507% | **20.1750%** |

Aggregate ΔMAE = **−0.3556 W/m²**.

| Fold | Control MAE | Candidate B MAE | ΔMAE | Improved |
|---:|---:|---:|---:|:---:|
| 0 | 29.1137 | 27.0406 | −2.0731 | Yes |
| 1 | 22.8351 | 24.0944 | +1.2593 | No |
| 2 | 25.5086 | 25.6572 | +0.1486 | No |
| 3 | 30.0997 | 28.8913 | −1.2084 | Yes |
| 4 | 24.3254 | 24.4093 | +0.0839 | No |

Improved folds: **2/5**. Maximum degradation: **+1.2593 W/m²**.

## Locked gate verdict

- G1: **FAIL** — ΔMAE −0.3556 does not reach −0.50 W/m².
- G2: **FAIL** — only 2/5 folds improved.
- G3: **FAIL** — +1.2593 W/m² exceeds +0.50 W/m².
- G4: **PASS** — candidate nMAE and RMSE are lower.
- G5: **PASS** — causal / ODD firewall compliant.
- G6: **HONESTLY APPROXIMATE** — reconstructed control, not exact original Stage 8.1 code.

### Final verdict

**CANDIDATE B — REJECTED BY EVEN GATES.**

No B1/B2/B3 rescue variants are permitted. Candidate B is closed.

ODD was not evaluated. The Stage 8.1 37-feature HGB champion remains protected.

## Repeat-prevention lock

This checkpoint exists so Candidate B is not accidentally repeated in a later chat.

Do not repeat the same architecture, hyperparameters, or evaluation as a new experiment.

Do not reopen feature research because of this result.

## Next

Proceed to **Candidate C** only after a new architecture design-freeze/audit. Candidate C must be a genuinely distinct hypothesis, not a B rescue variant.
