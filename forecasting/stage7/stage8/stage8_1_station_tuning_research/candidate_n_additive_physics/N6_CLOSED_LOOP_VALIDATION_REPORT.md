# POLARIS — Multi-Hour Candidate N6 Closed-Loop Validation Report

## 1. Executive Summary
- **Overall Status**: `PASS`
- **Continuous Duration Completed**: 24/24 hours (continuous 24-step simulation)
- **Governance State**: `winner: null` (strictly preserved, non-production)
- **Production Default**: `system.forecasting.implementations.baseline.LocalBaselineForecastEngine` (unchanged)
- **Operational Reality**: Real-time arrival of 18Z MEPS pressure levels remains unproven; all results are strictly offline simulation evidence.

---

## 2. Test Configuration & Provenance
- **Simulation Fixture**: `POLARIS_HYBRID_FIXTURE_H1_0` (8,784 records, canonical 2024 hourly dataset, SITES Nuolja real solar)
- **Origin Timestamp**: `2024-06-01T00:00:00Z` (Fixture Index 3,648)
- **Horizon**: 24 hourly timesteps ($h = 1 \dots 24$)
- **Forecaster Under Test**: `N6SolarForecastEngine` ([`system/forecasting/implementations/n6_solar.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/forecasting/implementations/n6_solar.py))
- **Model Bundle**: Frozen 40-member ensemble ([`candidate_n6_model.joblib`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib))
- **Uncertainty Engine**: L2 Split-Conformal 90% Lower Bound ($\hat{Q}_{\text{norm}} = 1.8590$) & Forward 6-Hour Rolling Shortfall Reserve Multiplier ($Q_{90,W} = 1.5702$)
- **Optimizer**: `GAP19HighsNativeOptimizer` (HiGHS Lexicographic Multi-Objective MILP)
- **Simulator**: `DigitalTwinSimulator` ([`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py))

---

## 3. Step-by-Step Verification Results
All 24 timesteps satisfied all physical, statistical, and operational constraints without exception:

| Verification Check | Required Boundary | Observed Status | Details |
| :--- | :--- | :--- | :--- |
| **Finite & Bounded Forecasts** | $0 \le GHI \le 1200\text{ W/m}^2$, $P_{\text{PV}} \le 60\text{ kW}$ | **PASS** | Min $0.0\text{ W/m}^2$, Max $768.42\text{ W/m}^2$; no NaN/Inf |
| **Strict Night Zeroing** | $GHI = 0.0$ when $\text{elev} \le 0^\circ$ or $GHI_{\text{cs}} \le 0$ | **PASS** | Exact $0.0000$ across all night hours |
| **Lower Bound Monotonicity** | $0 \le GHI_{\text{lower}} \le GHI_{\text{pred}}$ | **PASS** | Satisfied for all 24 horizons |
| **Dynamic EBR Trajectory** | Units Wh, 6h lookahead, $\ge 15{,}000\text{ Wh}$ | **PASS** | Dynamic range $[15{,}000.0\text{ Wh}, 50{,}885.0\text{ Wh}]$ |
| **Physical Battery SOC Extrema** | $20.0\% \le \text{SOC} \le 95.0\%$ | **PASS** | Range $[44.13\%, 95.00\%]$; Final SOC: $95.00\%$ |
| **Diesel Fuel Consumption** | Fuel remaining $\ge 0.0\text{ L}$, monotonic drop | **PASS** | Initial $500.0\text{ L} \to$ Final $470.945\text{ L}$ ($29.055\text{ L}$ consumed) |
| **GAP19 Solver Status** | Status == `OPTIMAL`, no infeasibilities | **PASS** | Solved optimally in $31.0554$ objective value |
| **Critical-Load Unmet Energy** | Zero unmet critical load | **PASS** | $0.0\text{ Wh}$ critical load deficit |

---

## 4. Controlled Comparison vs Baseline

A strictly controlled run was executed over the identical 24-hour fixture window starting from the identical initial station state:

| Metric | Candidate N6 + Conformal EBR | Baseline Forecaster + Default EBR | Delta | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Router Route** | `NORMAL` | `NORMAL` | Same | Both routed to GAP19 |
| **GAP19 Status** | `OPTIMAL` | `OPTIMAL` | Same | Both solved cleanly |
| **EBR Target Range** | $[15{,}000\text{ Wh}, 50{,}885\text{ Wh}]$ | $[15{,}000\text{ Wh}, 32{,}400\text{ Wh}]$ | $+18{,}485\text{ Wh}$ peak reserve | N6 inflates reserves during high forward uncertainty |
| **Battery SOC Extrema** | $[44.13\%, 95.00\%]$ | $[57.83\%, 95.00\%]$ | $-13.70\%$ min SOC | Deeper battery utilization |
| **Final Battery SOC** | $95.00\%$ | $95.00\%$ | $0.0\%$ | Both achieve full reserve replenishment |
| **Diesel Fuel Consumed**| $29.055\text{ L}$ | $27.742\text{ L}$ | $+1.313\text{ L}$ | Higher reserve buffer maintenance |
| **Critical Unmet Load** | $0.0\text{ Wh}$ | $0.0\text{ Wh}$ | $0.0\text{ Wh}$ | Zero critical shedding across both runs |

*Note*: Candidate N6 consumes slightly more fuel ($+1.31\text{ L}$) because the L2 split-conformal mechanism dynamically raises the forward battery reserve ceiling ($EBR_{\max} = 50.88\text{ kWh}$ vs $32.40\text{ kWh}$) to safeguard the microgrid against forward epistemic shortfall risk.

---

## 5. Protected Assets Cryptographic Integrity Status

All 4 protected governance assets were cryptographically verified via SHA-256 before simulation execution:

1. `candidate_n6_model.joblib`: `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` (**MATCH**)
2. `candidate_n1_model.joblib`: `7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7` (**MATCH**)
3. `CANDIDATE_N_MANIFEST.json`: `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` (**MATCH**)
4. `ensemble_parameters.json`: `26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0` (**MATCH**)

---

## 6. Documented Limitations & Operational Boundaries
- **`u700`/`v700` Upper Wind Gap**: NaN values at horizons 20–24 remain an immutable characteristic of the archived MEPS 18Z pressure level products. Handled gracefully by the HistGradientBoosting trees without synthetic imputation.
- **Operational Availability Gate**: The real-time arrival of 18Z MEPS pressure levels prior to the operational dispatch cutoff (00:00 UTC) remains **unproven** historically.
- **Governance**: `winner: null` preserved. No model winner declared or promoted to production.
