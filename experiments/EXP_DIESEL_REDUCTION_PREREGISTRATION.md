# Pre-Registration & Experiment Audit: Closed-Loop Diesel Reduction

**Experiment Identifier**: `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`  
**Governance Status**: `PRE_REGISTERED_AMENDED_READY_FOR_EXECUTION`  
**Execution Gate**: `HOLD — DESIGN AND AUDIT ONLY. DO NOT EXECUTE AUTOMATICALLY.`  
**Date**: October 4, 2026 (Amended with Governance-Supported Worker Rule)  
**Artifact Directory**: `experiments/`  

---

## 1. Executive Summary & Audit Disposition

A comprehensive feasibility, architectural, and causal-provenance audit has been conducted across the forecasting, optimization, and realization layers of the POLARIS microgrid EMS:
- **Causal NWP + Physics Forecaster**: Implemented and verified against 13/13 unit tests.
- **Research Realization Executor**: Implemented with exact busbar/load conservation and verified against 15/15 unit tests.
- **Hourly Closed-Loop Receding-Horizon Runner**: Implemented and verified against 15/15 unit tests.
- **Canonical Critical Demand Governance Adapter**: Implemented and verified against 4/4 micro-tests and 24-step closed-loop smoke test.
- **Combined Regression Test Status**: **52 / 52 PASSED**.

This document pre-registers the empirical research design for evaluating whether adding causally available numerical weather prediction (NWP) solar forecasts reduces diesel consumption relative to a causal no-weather-information baseline under true receding-horizon closed-loop control.

---

## 2. Research Questions & Hypotheses

### Primary Research Question
> Does adding causally available MEPS NWP cloud information to the solar forecast reduce realized diesel consumption relative to a causal no-weather-information baseline under identical closed-loop conditions?

- **Null Hypothesis ($H_0$)**: The median paired difference in diesel fuel consumption between the Causal No-Weather-Information Baseline (Arm A) and the Causal NWP Forecaster (Arm B) is non-positive:
  $$\Delta_{\text{fuel}} = \text{Fuel}_{\text{Baseline}} - \text{Fuel}_{\text{Candidate}} \le 0\text{ Liters}$$
- **Alternative Hypothesis ($H_1$)**: The Causal NWP forecaster produces a statistically significant reduction in realized diesel fuel consumption:
  $$\Delta_{\text{fuel}} = \text{Fuel}_{\text{Baseline}} - \text{Fuel}_{\text{Candidate}} > 0\text{ Liters}$$

### Secondary Research Questions
1. **Diesel Engine Operating Hours**: Does causal solar information reduce cumulative diesel engine runtime hours?
2. **Generator Startups**: Does causal solar lookahead prevent short-cycling and reduce diesel startup/ignition events?
3. **Microgrid Reliability & Unmet Demand**: Does causal NWP improve or maintain zero unmet critical load ($J_1 = 0$)?
4. **Renewable Curtailment**: Does causal solar forecasting reduce solar/wind curtailment by scheduling battery charging ahead of solar peaks?
5. **Battery Health & Cycling**: What is the impact on equivalent full cycles (EFC), cumulative battery throughput (Wh), and minimum observed SoC?
6. **Physical Safety Invariants**: Are battery SoC bounds $[20\%, 95\%]$ strictly respected with zero hardware violations?
7. **Upper Bound / Information Ceiling**: How close does the Causal NWP candidate come to the theoretical performance of the noncausal perfect-foresight diagnostic?

---

## 3. Experiment Arms

The experiment evaluates three strictly defined, parallel arms under identical closed-loop conditions:

```
                          ┌──────────────────────────┐
                          │  StationState at hour t  │
                          └─────────────┬────────────┘
                                        │
           ┌────────────────────────────┼───────────────────────────┐
           ▼                            ▼                           ▼
    [ ARM A: BASELINE ]          [ ARM B: CANDIDATE ]        [ ARM C: DIAGNOSTIC ]
    Causal No-Weather-           Causal MEPS 18Z +           NONCAUSAL PERFECT-
    Information Baseline         PVLIB Clear-Sky Physics     FORESIGHT DIAGNOSTIC
           │                            │                           │
           └────────────────────────────┼───────────────────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │  Critical Demand Adapter │
                          │  min(11.6kW, demand[t])  │
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │    GAP19 MILP Solver     │
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │  Execute Timestep 0 Only │
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │ Realization Executor (t) │
                          │ (Actual Solar/Wind/Load) │
                          └─────────────┬────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │ StationState at hour t+1 │
                          └──────────────────────────┘
```

### Arm A: Causal No-Weather-Information Baseline
- **Designation**: Control Baseline.
- **Forecast Engine**: `LocalBaselineForecastEngine` (`system/forecasting/implementations/baseline.py`).
- **Solar Information**: Fixed diurnal sinusoidal clear-sky persistence curve ($SW_{\text{IN}}$ sine wave between 04:00 and 20:00). Zero weather forecast information; zero live sensor observations.
- **Wind Information**: Local baseline persistence model.
- **Demand Information**: Local baseline persistence model.
- **Causality**: 100% causal; relies strictly on static diurnal curve and current state.

### Arm B: Candidate (Causal NWP + Physics)
- **Designation**: Active Research Candidate.
- **Forecast Engine**: `CausalNwpPhysicsForecastEngine` (`system/forecasting/implementations/causal_nwp_physics.py`).
- **Solar Information**: MET Norway MEPS 18Z causal cloud cover forecast trajectory ($fc\_cloud\_cover$) + PVLIB Ineichen clear-sky astronomical radiation model for Nuolja ($68.362^\circ\text{N}, 18.739^\circ\text{E}$).
  $$\text{forecast\_GHI} = \max\left(0.0, \, GHI_{\text{cs}} \times (1.0 - \text{fc\_cloud\_cover} / 100.0)\right)$$
- **Wind Information**: Local baseline persistence model (**100% identical to Arm A**).
- **Demand Information**: Local baseline persistence model (**100% identical to Arm A**).
- **Causality**: 100% causal; MEPS 18Z run is initialized on D-1 at 18:00 UTC, disseminated by ~20:30 UTC, $>2.5\text{h}$ before 23:00 UTC daily microgrid issuance.

### Arm C: NONCAUSAL PERFECT-FORESIGHT DIAGNOSTIC
- **Designation**: Noncausal Diagnostic Benchmark Ceiling.
- **Forecast Engine**: `NoncausalPerfectForesightForecastEngine`.
- **Solar Information**: Ground-truth future SITES $SW_{\text{IN}}$ realization over the 24-hour horizon ($SW_{\text{IN}} \times 51.0\text{ W}$, clipped at $60\text{ kW}$).
- **Wind Information**: Local baseline persistence model (**100% identical to Arm A & B**).
- **Demand Information**: Local baseline persistence model (**100% identical to Arm A & B**).
- **Causality**: **STRICTLY NONCAUSAL DIAGNOSTIC ONLY**. Explicitly firewalled from operational claims; used solely as an upper-bound information ceiling.

---

## 4. Controlled Comparison Audit (Isolating the Solar Channel)

To ensure scientific validity, all factors other than the solar forecast information are strictly held constant across all three arms:

| Experimental Dimension | Controlled Specification | Cross-Arm Invariance |
|---|---|:---:|
| **Initial State ($t_0$)** | $\text{SoC} = 50.0\%$, $E = 100,000\text{ Wh}$, Diesel OFF, Fuel $100.0\text{ L}$ | **IDENTICAL** |
| **Realized Solar** | Ground-truth pyranometer observations from SITES Nuolja | **IDENTICAL** |
| **Realized Wind** | Benchmark realized wind series from 2024 dataset | **IDENTICAL** |
| **Realized Demand** | Benchmark realized demand series ($10000\text{ W} - 18000\text{ W}$) | **IDENTICAL** |
| **Wind Forecast** | Baseline persistence wind forecast trajectory | **IDENTICAL** |
| **Demand Forecast** | Baseline persistence demand forecast trajectory | **IDENTICAL** |
| **Critical Load Rule** | $\min(11600.0\text{ W}, \, d_{\text{total}}[t])$ (canonical worker rule) | **IDENTICAL** |
| **Terminal Target Energy** | $100,000\text{ Wh}$ (`SIMULATED_RESEARCH_ASSUMPTION — NOT PRODUCTION GOVERNANCE`) | **IDENTICAL** |
| **Optimization Solver** | GAP19 HiGHS Native Lexicographic MILP ($J_1 \to J_2 \to J_3 \to J_4$) | **IDENTICAL** |
| **Policy Router** | `EMSControlRouter` wrapping `EmergencyConditionDetector` | **IDENTICAL** |
| **Realization Executor** | `ResearchRealizationExecutor` enforcing busbar energy balance | **IDENTICAL** |
| **Simulation Timestep** | Exactly $1.0\text{ hour}$ ($\Delta t = 1.0\text{ h}$) | **IDENTICAL** |
| **Closed-Loop Protocol** | Hourly replanning, execute step 0, discard steps $1 \dots 23$ | **IDENTICAL** |

---

## 5. Critical Load Governance & Canonical Worker Adaptation Rule

### Governed Critical Load Ceiling
- **Authority**: Canonical configuration file [system/config/loads.yaml:3-5](file:///home/punith-bs/01polaris%20(Copy)/system/config/loads.yaml#L3-L5).
- **Governed Baseline Power**: `critical_load.baseline_power_w = 11600.0` ($11.6\text{ kW}$).
- **Governed Unmet Penalty**: `critical_load.unmet_penalty_per_wh = 10.0` ($\$10,000/\text{kWh}$).
- **Nominal Ceiling Definition**: $11,600.0\text{ W}$ represents the governed nominal critical-load ceiling, **NOT a mandatory minimum total demand floor**.

### Canonical POLARIS Worker Interface Rule
In microgrid busbar physics, critical demand cannot physically exceed total electrical demand ($d_{\text{crit}}[t] \le d_{\text{total}}[t]$).
In accordance with canonical POLARIS production architecture established in:
- `system/orchestration/worker.py:241-244` (Cell B production orchestration path)
- `system/tests/test_demand_critical_config_path.py` (regression specification)

For every hourly optimization step, the critical demand vector supplied to GAP19 is governed by the frozen rule:
$$\text{critical\_demand}[t] = \min\left(\text{critical\_load.baseline\_power\_w}, \, \text{forecasted\_total\_demand}[t]\right)$$
where:
$$\text{critical\_load.baseline\_power\_w} = 11600.0\text{ W}$$

- When forecasted total demand $\ge 11,600\text{ W}$: critical demand is capped at $11,600\text{ W}$ (the remainder is treated as non-critical load).
- When forecasted total demand $< 11,600\text{ W}$: critical demand is clipped to total demand ($100\%$ of load is protected as critical; zero non-critical load).

### Research-Only Critical Demand Adapter
To reproduce this pre-existing canonical worker interface rule without modifying production GAP19:
- **Module**: `system/research/research_critical_demand_adapter.py`
- **Class**: `AdaptedClosedLoopRunner(ClosedLoopCausalNwpRunner)`
- **SHA-256**: `c9aab75bfebf7fc24454ae959173a7892139b70eedafd8680a6c0ea6a3cef640`
- **Scope**: Explicitly designated as **RESEARCH-ONLY**.
- **Cross-Arm Invariance**: Applied 100% identically across Arms A, B, and C. Because all three arms share identical demand forecasts (`LocalBaselineForecastEngine`), the adapted critical demand vector is bit-for-bit identical across all arms at every timestep.

### Governance Evidence Base
- **Canonical Worker Logic**: `system/orchestration/worker.py:244` explicitly uses `[min(critical_load_baseline_w, d) for d in bundle.demand.point]`.
- **Regression Tests**: `system/tests/test_demand_critical_config_path.py` verifies unmodified GAP19 accepts this clipped vector and rejects unclipped vectors.
- **Micro-Tests (Cases A, B, C, D)**: $4/4\text{ PASS}$ ($15\text{ kW} \to 11.6\text{ kW}$, $11.325\text{ kW} \to 11.325\text{ kW}$, $10\text{ kW} \to 10\text{ kW}$, $20\text{ kW} \to 11.6\text{ kW}$).
- **Origin 1 Closed-Loop Smoke**: $24/24\text{ steps PASS}$ (`AdaptedClosedLoopRunner` executes 24 hours of 2024-05-01 to completion).
- **Combined Regression Suite**: $52/52\text{ PASS}$ across all research and integration tests.
- **Production Integrity**: `gap19_highs_native.py`, `router.py`, `loads.yaml`, `simulator.py`, and `s81_solar.py` remain 100% unmodified.

---

## 6. Causal Forecast Lineage & Availability Tightening

A continuous sequence of hourly timestamps does NOT constitute proof of causal forecast availability. Each forecast input must have an unbroken, verified causal chain:

$$\text{Forecast Issuance Time} \longrightarrow \text{NWP Model Initialization} \longrightarrow \text{Dissemination Availability} \longrightarrow \text{Target Forecast Hours}$$

### Proven MEPS 18Z Causal Lineage
In the 2024 dataset (`data/POLARIS_v0_1_future_weather_forecasts_2024.csv`):
- **Forecast Issuance Time**: $23:00\text{ UTC}$ ($00:00\text{ CET}$) on calendar day $D-1$.
- **MEPS Model Run**: $18:00\text{ UTC}$ run of day $D-1$ (`metno_seamless _previous_day1`).
- **Dissemination Availability**: MET Norway completes MEPS 18Z data dissemination between $20:15$ and $20:30\text{ UTC}$. At $23:00\text{ UTC}$, this dataset is fully available with $>2.5\text{ hours}$ of causal margin.
- **Target Hours ($t+1 \dots t+24$)**: Day $D$ $00:00\text{ UTC}$ through $23:00\text{ UTC}$ (forecast lead times $+6\text{h}$ to $+29\text{h}$ relative to $18\text{Z}$ initialization). Native MEPS runs extend to $+66\text{h}$, well beyond $+29\text{h}$.

### Intraday Rolling vs. Daily Forward Steps Audit
- **Intraday MEPS Availability in Archive**:
  The 2024 weather archive contains exactly 347 daily forecast initializations (`forecast_start = YYYY-MM-DD 00:00:00`), each covering exactly 24 horizon hours. It does NOT contain archived intraday $00\text{Z}$, $06\text{Z}$, or $12\text{Z}$ runs.
- **Causality Risk of Intraday Multi-Day Stitching**:
  If an intraday reoptimization at hour $h > 0$ on day $D$ (e.g., $08:00\text{ UTC}$) queries a fixed 24h lookahead spanning into day $D+1$, those $D+1$ target hours in the archive originate from day $D$'s $18\text{Z}$ run. At $08:00\text{ UTC}$ on day $D$, the $18\text{Z}$ run has **not yet occurred**; using it would constitute an operational data leak of $10\text{ hours}$ into the future.
- **Causal Constraint & Rejection Rule**:
  **Any target hour that lacks proven causal availability at the exact simulation time of optimization is STRICTLY REJECTED.**
  Therefore, the pre-registered primary experiment evaluates daily 24-hour cycles: each origin is initialized at $23:00\text{ UTC}$ ($00:00\text{ CET}$), executing 24 receding-horizon steps across Day $D$ where every target hour has proven causal lineage from the $D-1$ 18Z run.

---

## 7. Common Evaluation Window & Origin Selection Rule

### High-Solar Evaluation Window
- **Season**: Arctic Summer Solar Active Season (May 1, 2024 – August 31, 2024).
- **Total Duration**: 123 consecutive days (2,952 hours).
- **Window Rationale**: Nuolja ($68.36^\circ\text{N}$) experiences Arctic polar night from late November to mid-January, and minimal solar irradiance in early spring/late autumn ($GHI < 10\text{ W/m}^2$). The May–August window isolates the period where solar forecast accuracy has meaningful microgrid operational impact.
- **Origin Selection Rule**: All 123 daily origins ($23:00\text{ UTC}$ day prior / $00:00\text{ CET}$) within this window are evaluated contiguously. No cherry-picking, post-hoc filtering, or data trimming is permitted.

---

## 8. Metrics & Statistical Testing Plan

### Metrics Register
| Metric | Category | Unit | Target / Best Direction |
|---|---|:---:|:---:|
| **Total Diesel Fuel Consumed** | Primary | Liters (L) | Minimization ($\downarrow$) |
| **Diesel Operating Hours** | Secondary | Hours (h) | Minimization ($\downarrow$) |
| **Diesel Startup Count** | Secondary | Count | Minimization ($\downarrow$) |
| **Unmet Critical Load** | Secondary | Watt-hours (Wh) | Zero ($= 0.0$) |
| **Microgrid Reliability** | Secondary | Percent (%) | $100.0\%$ |
| **Renewable Curtailment** | Secondary | Watt-hours (Wh) | Minimization ($\downarrow$) |
| **Battery Throughput** | Secondary | Watt-hours (Wh) | Informational |
| **Equivalent Full Cycles (EFC)** | Secondary | Cycles | Informational |
| **Minimum Battery SoC** | Secondary | Percent (%) | $\ge 20.0\%$ |
| **SoC Floor Violations** | Secondary | Count | Strictly $0$ |
| **Optimizer Infeasibilities** | Secondary | Count | Strictly $0$ |

### Statistical Analysis Protocol
1. **Paired Difference**: For each daily origin $i \in \{1 \dots 123\}$:
   $$\Delta_{\text{fuel}, i} = \text{Fuel}_{\text{Baseline}, i} - \text{Fuel}_{\text{Candidate}, i}$$
2. **Wilcoxon Signed-Rank Test**: Nonparametric paired two-sided and one-sided tests evaluated at $\alpha = 0.05$.
3. **Bootstrap Confidence Intervals**: 10,000 bias-corrected and accelerated (BCa) bootstrap resamples (fixed random seed = 42) computing 95% confidence intervals on both mean and median fuel savings.
4. **Win / Loss / Tie Counts**: Explicitly reporting the number of origins where Candidate uses less fuel ($\Delta > 0.01\text{ L}$), more fuel ($\Delta < -0.01\text{ L}$), or equivalent fuel ($|\Delta| \le 0.01\text{ L}$).

---

## 9. Neutral Reliability Constraint (Research Gate)

To be declared an operationally viable diesel-reduction strategy, Arm B (Candidate) must satisfy:
1. **Fuel Savings**: Statistically significant fuel reduction ($\Delta_{\text{fuel}} > 0$, $p < 0.05$).
2. **Reliability Preservation**: Zero additional unmet critical load compared to Baseline:
   $$\text{Unmet}_{\text{Candidate}} \le \text{Unmet}_{\text{Baseline}}$$
3. **Physical Safety**: Zero battery SoC floor violations ($\text{SoC} \ge 20.0\%$).
4. **Solver Robustness**: Zero GAP19 optimization failures (`status == OPTIMAL` at every hour).

---

## 10. Cryptographic Provenance & Hash Register

All software components, models, and datasets are frozen with SHA-256 hashes:

| File / Component | Path | SHA-256 Hash |
|---|---|---|
| **2024 Weather Dataset** | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16` |
| **Candidate Forecaster** | `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` |
| **Control Forecaster** | `system/forecasting/implementations/baseline.py` | `905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993` |
| **GAP19 Optimizer** | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| **Policy Router** | `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` |
| **Realization Executor** | `system/simulation/research_realization_executor.py` | `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` |
| **Closed-Loop Runner** | `system/research/closed_loop_causal_nwp_runner.py` | `62cb1607a8dfa63edd804142f167916c1cc11bef30d49ae380d236efad03daa4` |
| **Critical Demand Adapter** | `system/research/research_critical_demand_adapter.py` | `c9aab75bfebf7fc24454ae959173a7892139b70eedafd8680a6c0ea6a3cef640` |
| **Battery Config** | `system/config/battery.yaml` | `eb06f81d8b11364e254cbcd5c37a4769874f8703e9e86e3b067b60d8858da216` |
| **Diesel Config** | `system/config/diesel.yaml` | `421120967328e18366daf41b682fc9f1cbe91b0f9ebe2133b83290bb9e294ac3` |
| **Solar PV Config** | `system/config/solar_pv.yaml` | `611521090b7d551614c23d91fc190320a42bccee667929618d40bab987262e5e` |
| **Loads Config** | `system/config/loads.yaml` | `eacb84d1c25f8768de0ee0cf8fdb286d4dbc9254824d7c17aea738cbe9774467` |
| **Optimizer Config** | `system/config/optimizer.yaml` | `bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8` |
| **Experiment Manifest** | `experiments/EXP_DIESEL_REDUCTION_MANIFEST.json` | `71413cb81fe7a6f208c5b976af6f227707c9f51a38dbf37a80ef912b73e98cd7` |

---

## 11. Final Preregistration Audit Disposition

All pre-execution gates, governance validations, causal lineages, and critical load parameterizations have been verified:
1. Primary question is strictly aligned to evaluating the value of adding causal MEPS NWP cloud forecasts vs. a causal no-weather-information baseline.
2. Arm A is designated as "Causal No-Weather-Information Baseline".
3. Arm C is strictly designated as "NONCAUSAL PERFECT-FORESIGHT DIAGNOSTIC".
4. Governed critical load nominal ceiling of $11,600\text{ W}$ (`system/config/loads.yaml`) is preserved and adapted via the canonical worker clipping rule:
   $$\text{critical\_demand}[t] = \min(11600.0, \, \text{forecasted\_total\_demand}[t])$$
   in exact accordance with `system/orchestration/worker.py:244`.
5. Research adapter `system/research/research_critical_demand_adapter.py` is hashed and frozen.
6. Causal lineage from MEPS 18Z initialization $\to$ dissemination $\to$ issuance $\to$ target hours is strictly proven.
7. `terminal_target_wh = 100,000 Wh` is explicitly declared as `SIMULATED_RESEARCH_ASSUMPTION — NOT PRODUCTION GOVERNANCE`.
8. Production files (`simulator.py`, `router.py`, `gap19_highs_native.py`, `s81_solar.py`, and YAML configs) remain 100% untouched.

**PREREGISTRATION STATUS: READY (AMENDMENT RATIFIED)**
