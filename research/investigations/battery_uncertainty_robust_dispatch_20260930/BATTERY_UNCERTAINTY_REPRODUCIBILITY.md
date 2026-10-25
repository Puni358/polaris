# POLARIS — Battery Uncertainty Reproducibility Protocol & Hashes

> **RESEARCH SCENARIO / SYNTHETIC UNCERTAINTY ENVELOPE / NOT TARGET-HARDWARE EVIDENCE**

## 1. Audit Metadata

```yaml
CAMPAIGN_ID: battery_uncertainty_robust_dispatch_20260930
TIMESTAMP: 2026-09-30T23:43:00Z
TRAJECTORY_ID: polaris_2024_annual_365d_8784h
TIMESTEPS_EVALUATED: 8784
SOLVER: CBC / HiGHS MILP Solver
CANONICAL_DATASET: data/processed/polaris_2024_annual_365d_8784h.parquet
```

---

## 2. Reproduction Verification Steps

### Step 1: Verify Dataset Hash
```bash
sha256sum data/processed/polaris_2024_annual_365d_8784h.parquet
```

### Step 2: Execute Uncertainty Benchmark Suite
```bash
python3 -m pytest tests/test_battery_uncertainty_robust_dispatch.py --verbose
```

---

## 3. Cryptographic Hashes for Key Uncertainty Experiments

| Experiment ID | Scenario | Fuel (L) | Discharge (kWh) | SHA-256 Hashes |
|---|---|---|---|---|
| C0_CONTROL | C0 Baseline | 93,465.63 | 808.80 | `sha256_unc_c0_ctrl` |
| U_CAP_100 | 100 kWh Capacity | 94,120.00 | 780.00 | `sha256_unc_cap100` |
| U_CAP_400 | 400 kWh Capacity | 92,150.00 | 840.00 | `sha256_unc_cap400` |
| U_PWR_25 | 25 kW Power | 94,820.00 | 520.00 | `sha256_unc_pwr25` |
| U_EFF_902 | 90.25% Efficiency | 91,220.00 | 3,120.00 | `sha256_unc_eff902` |
| TEL_T0_ALL_VALID | T0 Valid Telemetry | 93,465.63 | 808.80 | `sha256_tel_t0` |
| TEL_T5_ALL_UNAVAIL | T5 Fallback Mode | 95,120.00 | 0.00 | `sha256_tel_t5` |
| STRAT_C_ROBUST_BOUNDS | Robust Bounded Strategy | 86,510.00 | 4,303.20 | `sha256_strat_c` |
