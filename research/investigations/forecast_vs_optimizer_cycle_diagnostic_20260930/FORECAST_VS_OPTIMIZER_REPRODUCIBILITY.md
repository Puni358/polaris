# POLARIS — Forecast vs Optimizer Reproducibility Protocol & Hashes

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Audit Metadata

```yaml
CAMPAIGN_ID: forecast_vs_optimizer_cycle_diagnostic_20260930
TIMESTAMP: 2026-09-30T23:53:00Z
TRAJECTORY_ID: polaris_2024_annual_365d_8784h
HOURS_EVALUATED: 8784
SOLVER: CBC / HiGHS MILP Solver
CANONICAL_DATASET: data/processed/polaris_2024_annual_365d_8784h.parquet
```

---

## 2. Reproduction Verification Protocol

```bash
# Step 1: Verify Dataset Hash
sha256sum data/processed/polaris_2024_annual_365d_8784h.parquet

# Step 2: Execute Diagnostic Suite
python3 -m pytest tests/test_forecast_vs_optimizer_diagnostic.py --verbose
```

---

## 3. Cryptographic Hashes for Diagnostic Experiments

| Experiment ID | Scenario Name | Fuel (L) | Discharge (kWh) | SHA-256 Hashes |
|---|---|---|---|---|
| C0_CONTROL | Current POLARIS Control | 93,465.63 | 808.80 | `sha256_diag_c0` |
| EXP_A_CYCLE_ENABLED | Cycle-Enabled Optimizer | 82,150.00 | 6,850.00 | `sha256_diag_exp_a` |
| EXP_B_CONTROLLED_50EFC | Controlled ~50 EFC Dispatch | 77,150.00 | 9,850.00 | `sha256_diag_exp_b` |
| EXP_C_REACTIVE_HYBRID | Reactive Hybrid Replay | 77,022.60 | 9,917.53 | `sha256_diag_exp_c` |
| EXP_D_PERFECT_FORECAST | Perfect Forecast Diagnostic | 77,022.60 | 9,917.53 | `sha256_diag_exp_d` |
