# POLARIS Stage 7.2 Reproducibility Notes

## Environment & Dependencies
- **Python**: 3.12+ (in virtual environment `.venv`)
- **Core Packages**: `numpy`, `pandas`, `scikit-learn`, `requests`
- **Execution Script**: `python3 stage7/stage7_2_meps_native_radiation/run_stage7_2.py`

## Locked Benchmark Protocol Execution
1. **Control Reproduction (E0)**:
   - Evaluated Stage 6.6 31-feature model on EVEN CV.
   - Target: residual modeling relative to Stage 4 fold prediction (`y_true - pred_stage4_fold`).
   - Hyperparameters: `HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`.
   - Verified reproduction of control MAE = 38.2806 W/m².

2. **Feature Extraction**:
   - Source: MET Norway MEPS 2.5km Deterministic Surface Archive (`meps25epsarchive` on `thredds.met.no`).
   - Selected Run: Previous-day 18:00 UTC run (`meps_det_sfc_YYYYMMDD_18Z.ncml`).
   - Causal Rule: `forecast_reference_time < t0` strictly satisfied for 100% of 347 clean origins.
   - Target Grid Point: $y=760, x=486$ ($68.355701^\circ\text{N}, 18.763666^\circ\text{E}$).

3. **CV Splits**:
   - EVEN CV: 174 EVEN clean benchmark origins divided into 6 equal blocks of 29 origins.
   - 5 forward-chaining folds: Fold 1 (29 train / 29 val), Fold 2 (58 train / 29 val), Fold 3 (87 train / 29 val), Fold 4 (116 train / 29 val), Fold 5 (145 train / 29 val).

4. **ODD Test Set Security**:
   - The 173 ODD test origins were **never loaded, read, evaluated, or predicted**.
