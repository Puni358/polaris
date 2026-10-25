# Stage 7.3 Reproducibility Notes

To reproduce the exact numerical results of POLARIS Stage 7.3 Clear-Sky Index ($k_t$) Target Reformulation:

## Environment & Requirements
* Environment: Python 3.10+ with standard scientific stack (`numpy`, `pandas`, `scikit-learn`).
* Execution Binary: `./.venv/bin/python3`

## Single-Command Reproduction
Execute the automated Stage 7.3 pipeline runner:

```bash
./.venv/bin/python3 stage7/stage7_3_kt_reformulation/run_stage7_3.py
```

## Key Expected Outputs & Verification Metrics
1. **Control Reproduction (E0)**:
   - EVEN CV MAE: `38.2806 W/m²`
   - EVEN CV nMAE: `40.39%`
   - EVEN CV RMSE: `60.7509 W/m²`
2. **Candidate E1 Results**:
   - EVEN CV MAE: `36.3828 W/m²`
   - EVEN CV nMAE: `40.46%`
   - EVEN CV RMSE: `58.8212 W/m²`
   - Folds Improved: `3 / 5` (Folds 1, 2, 4)
   - Folds Degraded: `2 / 5` (Fold 3: +1.7020 W/m², Fold 5: +0.2633 W/m²)
3. **Decision File**:
   - File: `stage7/stage7_3_kt_reformulation/stage7_3_decision.json`
   - Final Decision: `"STAGE 7.3 = NO IMPROVEMENT"`
   - ODD Accessed: `false`
