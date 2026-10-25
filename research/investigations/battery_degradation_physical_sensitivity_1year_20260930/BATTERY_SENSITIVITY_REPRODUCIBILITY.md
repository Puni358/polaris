# Battery Sensitivity Reproducibility & Verification Log

```yaml
STUDY_ID: battery_degradation_physical_sensitivity_1year_20260930
DETERMINISTIC_REPRODUCIBILITY: PASS
REPEAT_RUNS_EXECUTED: 2
```

## 1. C0 Control Baseline Verification

Before launching parameter sweeps, the C0 control baseline (`deg_penalty_per_wh = 0.00005`, `eta_rt = 0.8464`) was executed across two independent runs on `polaris_2024_annual_365d_8784h`.

| Metric | Target C0 Benchmark | Run 1 | Run 2 | Difference | Status |
| :--- | ---: | ---: | ---: | ---: | :---: |
| **Fuel (L)** | 93,465.63 | 93,465.63 | 93,465.63 | 0.00 | **EXACT MATCH** |
| **Diesel Energy (kWh)** | 210,502.51 | 210,502.51 | 210,502.51 | 0.00 | **EXACT MATCH** |
| **Renewable Curtailment (kWh)** | 66,192.50 | 66,192.50 | 66,192.50 | 0.00 | **EXACT MATCH** |
| **Battery Discharge (kWh)** | 808.80 | 808.80 | 808.80 | 0.00 | **EXACT MATCH** |
| **Battery Cycles** | 4.04 | 4.04 | 4.04 | 0.00 | **EXACT MATCH** |
| **Unmet Load (kWh)** | 0.00 | 0.00 | 0.00 | 0.00 | **EXACT MATCH** |

## 2. Deterministic Sweep Repeatability Check

Every tested parameter point (P0–P9, E0–E3) was executed twice to ensure complete numerical determinism.

- **P0–P9 Sweep**: 100% exact numerical agreement across all metrics between Run 1 and Run 2.
- **E0–E3 Sweep**: 100% exact numerical agreement across all metrics between Run 1 and Run 2.
- **Safety Screening**: Zero unmet load, zero constraint violations across all configurations.

```text
DETERMINISTIC_REPRODUCIBILITY = PASS
```
