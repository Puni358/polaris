# POLARIS vs Reactive Hybrid Baseline Benchmark Reproducibility Report

## 1. Reproducibility Audit Summary

A post-benchmark repeat-run verification was executed for both **Controller A (POLARIS Closed-Loop MPC)** and **Controller B (Reactive Hybrid Baseline)** across the full 8,784-hour annual trajectory.

```yaml
BENCHMARK_ID: polaris_vs_reactive_hybrid_1year_20260930
HORIZON_HOURS: 8784
REPRODUCIBILITY_RUN_COUNT: 2
POLARIS_REPRODUCIBILITY: PASS (100% Exact Bit-for-Bit Match)
REACTIVE_BASELINE_REPRODUCIBILITY: PASS (100% Exact Bit-for-Bit Match)
SOLVER_DETERMINISM: 100% (Scipy HiGHS C++ MILP Engine)
VERDICT: 100% DETERMINISTICALLY REPRODUCIBLE
```

---

## 2. Repeat-Run Comparison Metrics

| Controller | Initial Run Diesel Fuel (L) | Repeat Run Diesel Fuel (L) | Fuel Difference (L) | Initial Run Diesel Energy (kWh) | Repeat Run Diesel Energy (kWh) | Reproducibility Status |
| :--- | ---: | ---: | ---: | ---: | ---: | :---: |
| **POLARIS (Closed-Loop MPC)** | 93,465.6264 | 93,465.6264 | 0.0000 | 210,502.5055 | 210,502.5055 | **EXACT_MATCH** |
| **Reactive Hybrid Baseline** | 77,022.5981 | 77,022.5981 | 0.0000 | 165,770.3923 | 165,770.3923 | **EXACT_MATCH** |

---

## 3. Determinism Verification by Stage

1. **Input Data Stream**: `LocalDataProvider` reads static deterministic JSON arrays. Re-reading produces identical arrays across all 8,784 hours.
2. **Forecast Engine**: `LocalBaselineForecastEngine` computes deterministic mathematical functions (`math.sin`, `math.cos`) based on ISO timestamps. Zero random perturbations applied.
3. **MILP Solver**: Scipy HiGHS C++ solver operates with fixed tolerance `1e-5` and deterministic presolve routines. Zero stochastic seed dependence.
4. **Digital Twin Simulator**: `DigitalTwinSimulator` updates battery SOC and diesel fuel linearly.
5. **Reactive Controller**: `ReactiveHybridBaseline` applies pure deterministic conditional logic.

---

## 4. Final Reproducibility Gate Declaration

```yaml
REPRODUCIBILITY:
  POLARIS: PASS
  REACTIVE_BASELINE: PASS
```
