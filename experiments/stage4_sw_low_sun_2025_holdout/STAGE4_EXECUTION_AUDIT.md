# POLARIS Stage 4: Execution & Governance Audit (2025 Holdout)

**Experiment:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`  
**Execution Timestamp:** 2026-10-05T20:02:12Z to 2026-10-05T21:02:53Z (elapsed: 3,640.85 s)  
**Execution Environment:** Linux, Python 3.12.3, HiGHS 1.8.0, SciPy 1.14.1, NumPy 1.26.4, Pandas 2.2.2, PVLib 0.16.1

---

## 1. Cryptographic Startup Hash Guards (All 15 Verified)

| Component | Path | Expected Hash | Actual Hash | Match |
|---|---|---|---|---|
| GAP19 Solver | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | **YES** |
| Dispatch Plan Schema | `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` | **YES** |
| Causal NWP Forecaster | `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | **YES** |
| S/SW Adapter (2024) | `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` | **YES** |
| S/SW Preregistration MD | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md` | `1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5` | `1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5` | **YES** |
| S/SW Preregistration JSON | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json` | `3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4` | `3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4` | **YES** |
| Numerical Addendum MD | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md` | `228474e1100d4ce4a1c1470198125d699ddd3d9c0bf1f91678f4373f8e1d0054` | `228474e1100d4ce4a1c1470198125d699ddd3d9c0bf1f91678f4373f8e1d0054` | **YES** |
| Numerical Addendum JSON | `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.json` | `94c6f623a35628bd5f4efab40557c8fa99395fdf81b4c6c665ab0af968d7bfdd` | `94c6f623a35628bd5f4efab40557c8fa99395fdf81b4c6c665ab0af968d7bfdd` | **YES** |
| Solar Elevation Module | `clear_sky/compute_clearsky_2025.py` | `3ac68ee705e9a9ec68044687c5df79100082d9ab172d09baac70dde6be00ed54` | `3ac68ee705e9a9ec68044687c5df79100082d9ab172d09baac70dde6be00ed54` | **YES** |
| 2025 NWP Forecast File | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` | `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5` | `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5` | **YES** |
| 2025 NWP Manifest | `data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json` | `534ed055d632950c474e4a38ff11b4b31f16955e6dff5968b7acabd31edf14cf` | `534ed055d632950c474e4a38ff11b4b31f16955e6dff5968b7acabd31edf14cf` | **YES** |
| Stage 4 Preregistration MD | `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md` | `9cb2d5459894be8add07a3bd01595f40ab2485c2a18510765c4d8f0264fe4e46` | `9cb2d5459894be8add07a3bd01595f40ab2485c2a18510765c4d8f0264fe4e46` | **YES** |
| Stage 4 Preregistration JSON | `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json` | `9a16ccc8c28267331da2816fe0c7c04aeb9afd6f963e49673eb6c3872d892623` | `9a16ccc8c28267331da2816fe0c7c04aeb9afd6f963e49673eb6c3872d892623` | **YES** |
| Holdout Governance MD | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md` | `22e67a16a90ef90fa88b248614a83d853511a33619548272535e05615314d7a7` | `22e67a16a90ef90fa88b248614a83d853511a33619548272535e05615314d7a7` | **YES** |
| Holdout Governance JSON | `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json` | `f96fd97c812f44e88455c966c500a3874a99f07b8ae94744759d0fac6b461bf7` | `f96fd97c812f44e88455c966c500a3874a99f07b8ae94744759d0fac6b461bf7` | **YES** |

---

## 2. Population and Execution Statistics

- **Origins Expected:** 123
- **Origins Executed:** 123
- **Origins Excluded:** 0
- **Arm Hours Per Arm:** 2,952
- **Total Arm Hours (5 arms):** 14,760
- **Execution Failures:** 0
- **Optimizer Infeasibilities:** 0
- **Simultaneous Charge/Discharge Violations > tau (0.055 W):** 0
- **Max Busbar Balance Error:** $\le 10^{-3}\text{ W}$ across all 14,760 hours
- **Deterministic Random Seed:** 42 (`numpy.random.default_rng(42)`)

---

## 3. Operational Telemetry Summary

| Arm | Total Fuel (L) | Served Load (MWh) | Unmet Load (MWh) | Curtailment (MWh) | Diesel On Hours | Startups | Battery Throughput (MWh) | EFC | Route Mode (Step 0) |
|---|---|---|---|---|---|---|---|---|---|
| **Control_Frozen_B** | 6117.97 | 37.52 | 5.56 | 6.55 | 589 | 108 | 31.60 | 79.00 | EMERGENCY 123 / NORMAL 0 |
| **Candidate_S** | 4648.33 | 37.66 | 5.42 | 9.94 | 446 | 101 | 37.59 | 93.97 | EMERGENCY 123 / NORMAL 0 |
| **Candidate_SW** | 3885.02 | 37.08 | 6.00 | 9.79 | 368 | 83 | 37.75 | 94.38 | EMERGENCY 123 / NORMAL 0 |
| **Candidate_SL** | 5334.13 | 37.94 | 5.14 | 10.35 | 506 | 114 | 34.62 | 86.54 | EMERGENCY 123 / NORMAL 0 |
| **Candidate_SWL** | 5221.32 | 37.99 | 5.08 | 10.40 | 496 | 109 | 35.79 | 89.48 | EMERGENCY 123 / NORMAL 0 |

---

## 4. Leakage and Firewall Audit
- **Causal Firewall Check:** 0 violations. No actual SW_IN, future observations, or ground-truth values were exposed to the optimizer.
- **Ephemeris Causality:** Solar elevation $e_k$ is computed strictly from deterministic timestamp geometry and fixed coordinates (latitude 68.362074°N, longitude 18.738752°E, Etc/GMT-1).
- **Production Boundary:** Production files (`gap19_highs_native.py`, `dispatch_plan.py`, `causal_nwp_physics.py`) remain completely untouched and identical to frozen hashes.
