# POLARIS STAGE 7.4 REPRODUCIBILITY & AUDIT MANIFEST

**Stage:** Stage 7.4  
**Date:** 2026-09-12  
**Status:** REJECTED  

## Reproducibility Protocol

To reproduce the Stage 7.4 extraction, pre-CV audit, control validation, and candidate evaluation:

```bash
# Run full execution script
./.venv/bin/python3 stage7/stage7_4_vertical_cloud/run_stage7_4.py --workers 16
```

## Key Verification Checkpoints

1. **Data Source**: MEPS deterministic pressure-level collection on THREDDS (`thredds.met.no`).
2. **Origins**: 347 clean benchmark origins (174 EVEN, 173 ODD).
3. **Surface-Aware Integration**: Pressure integration truncated at surface pressure $p_{\text{sfc}}$ with linear boundary interpolation.
4. **Control Baseline (E0)**:
   - MAE: $38.2806\text{ W/m}^2$
   - nMAE: $40.39\%$
   - RMSE: $60.7509\text{ W/m}^2$
5. **Candidate E1**:
   - MAE: $38.2869\text{ W/m}^2$
   - nMAE: $40.65\%$
   - RMSE: $61.2295\text{ W/m}^2$
   - Gates: 0/5 passed -> **REJECTED**.
6. **ODD Test Set**: 100% UNTOUCHED & LOCKED (`odd_accessed: false`).
