# STAGE 8.1 OFFICIAL ODD REPRODUCIBILITY GUIDE

To reproduce the official Stage 8.1 held-out ODD evaluation results:

```bash
./.venv/bin/python "stage7/stage8/stage8_1_700hpa_wind/run_official_odd_evaluation.py"
```

### Verified Target Outputs
- **Control Source**: `stage4_results/ensemble_predictions.csv` (`pred_ensemble`)
- **Stage 4 Refit Executed**: NO
- **Control MAE**: $36.613571\text{ W/m}^2$
- **Candidate MAE**: $36.188657\text{ W/m}^2$
- **Delta MAE**: $-0.424913\text{ W/m}^2$
- **10,000 Bootstrap 95% CI**: $[-0.887999, +0.026372]\text{ W/m}^2$
- **Fraction Bootstrap $< 0$**: $0.9665$
