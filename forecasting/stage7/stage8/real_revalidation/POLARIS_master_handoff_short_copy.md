# POLARIS — Complete Project Handoff / Master Context

**Project:** POLARIS
**Full name:** AI-Powered Predictive Energy Management for Polar Research Stations
**Competition:** Smart India Hackathon 2026
**Problem Statement ID:** SIH26061
**Problem Statement:** AI-Driven Smart Energy Management System for Polar Research Stations
**Organization:** Ministry of Earth Sciences (MoES)
**Department:** National Centre for Polar and Ocean Research (NCPOR)
**Category:** Software
**Theme:** Clean & Green Technology
**Date compiled:** 2026-09-09

---

## Table of Contents

1. [Original SIH Problem](#1-original-sih-problem)
2. [Original POLARIS Concept](#2-original-polaris-concept)
3. [Research Findings](#3-original-research-findings)
4. [Novelty Caution](#4-important-novelty-caution)
5. [Data Problem](#5-major-data-problem)
6. [SITES Dataset](#6-the-sites-dataset-discovery)
7. [Timestamp Convention (LOCKED)](#7-critical-timestamp-discovery)
8. [Clean Hourly Dataset](#8-clean-hourly-dataset)
9. [Full Multivariate Dataset](#9-full-multivariate-dataset)
10. [Forecasting Protocol (LOCKED)](#10-locked-forecasting-problem)
11. [Baselines](#11-baselines)
12. [Foundation Model Benchmark](#12-foundation-model-benchmark)
13. [Chronos-2 Setup](#13-chronos-2-univariate)
14. [Chronos-2 Results (Champion)](#14-chronos-2-univariate-results)
15. [Chronos Solar-Regime Analysis](#15-chronos-2-solar-regime-analysis)
16. [Chronos Horizon Analysis](#16-chronos-2-horizon-analysis)
17. [TimesFM 3.0](#17-timesfm-30)
18. [TimesFM Results](#18-timesfm-results)
19. [Moirai 2.0](#19-moirai-20-r-small)
20. [Moirai Results](#20-moirai-results)
21. [Leaderboard](#21-final-foundation-model-leaderboard)
22. [Representative Chronos Behavior](#22-representative-chronos-behavior)
23. [Chronos Multivariate Experiment](#23-chronos-multivariate-experiment)
24. [Multivariate Results](#24-chronos-multivariate-results)
25. [Multivariate Horizon Results](#25-multivariate-horizon-results)
26. [Multivariate Solar Regimes](#26-multivariate-solar-regimes)
27. [LoRA Setup](#27-chronos-2-adaptation--lora)
28. [LoRA Pilot](#28-lora-pilot)
29. [LoRA Experiment A — 500 Steps](#29-lora-experiment-a--500-steps)
30. [LoRA Experiment A — 1000 Steps](#30-lora-experiment-a--1000-steps)
31. [LoRA Experiment B](#31-lora-experiment-b)
32. [LoRA Experiment C](#32-lora-experiment-c)
33. [Final LoRA Conclusion](#33-final-lora-conclusion)
34. [Core Hypothesis](#34-current-core-hypothesis)
35. [Past vs Future Covariates](#35-important-distinction-past-vs-future-covariates)
36. [Data-Leakage Rule](#36-critical-data-leakage-rule)
37. [Open-Meteo Issue](#37-open-meteo-issue)
38. [Ground Truth Lock](#38-ground-truth-must-remain-sites)
39. [Next Data-Research Questions](#39-next-data-research-question)
40. [Forecast-Origin Rule](#40-important-forecast-origin-rule)
41. [Next Experiment](#41-current-next-experiment)
42. [Future Experiment Order](#42-future-experiment-order)
43. [Forecast Solar as Separate Experiment](#43-forecasted-solar-radiation-is-a-separate-experiment)
44. [Solar/Time Features](#44-solartime-features)
45. [Potential Final Architecture](#45-potential-final-forecasting-architecture)
46. [EMS — Not Yet Built](#46-energy-management-side--not-yet-built)
47. [Original Prototype Direction](#47-original-prototype-direction)
48. [Safety/Reliability Principles](#48-important-sih-safety--reliability-principles)
49. [Computer Environment](#49-current-computer-environment)
50. [Working Preferences](#50-important-user-working-preferences)
51. [AI Models Available](#51-ai-models-available-to-the-user)
52. [Files & Artifacts](#52-files--artifacts-currently-available)
53. [Current Status](#53-current-status--one-screen-version)
54. [Scientific Conclusion](#54-current-scientific-conclusion)
55. [Next Big Research Question](#55-the-next-big-research-question)
56. [Next Action Phases (A–E)](#56-next-action--do-not-skip-this-order)
57. [Project Philosophy](#57-very-important-philosophy-for-the-rest-of-the-project)
58. [Ultimate POLARIS Goal](#58-ultimate-polaris-goal)

---

## 1. Original SIH Problem

The SIH problem asks for an intelligent energy-management system for polar research stations using AI for:

- Electrical load forecasting
- Renewable-energy forecasting/integration
- Fuel optimization
- Energy management under extreme polar conditions
- Reliable energy supply

The original research was deliberately instructed **not to assume that "AI + solar + battery" is automatically the right solution**. The goal was to investigate the real energy problem, existing polar-station systems, research gaps, data availability, novelty, technical feasibility, and then determine the best architecture.

The project is ultimately intended to address Indian Antarctic research stations, especially **Maitri and Bharati**, while being conceptually scalable to other remote/off-grid polar stations.

---

## 2. Original POLARIS Concept

The original proposed system is an AI-driven Energy Management System (AI-EMS):

```
Station sensors / weather / energy data
                ↓
        AI Forecasting Layer
                ↓
       Load + renewable forecast
                ↓
        Optimization Engine
                ↓
 Generator scheduling
 Battery charge/discharge
 Renewable utilization
 Load prioritization
 Fuel minimization
                ↓
          Energy Management
                ↓
       Station energy system
```

Potential additional components: dashboard, alerts, manual override, what-if simulation, historical analytics, digital twin, fuel/resupply intelligence, explainable AI, critical-load prioritization.

The original prototype proposal explicitly included a simulated polar station/digital twin, synthetic load profiles, generator models, battery models, AI forecasting, MILP optimization, and a dashboard.

---

## 3. Original Research Findings

### Polar energy problem

Polar research stations are generally isolated and require reliable electricity and heating.

Major problems:
- Diesel dependence
- Expensive fuel logistics
- Fuel-spill/environmental risk
- Renewable intermittency
- Extreme seasonal changes
- Polar night
- Heating demand
- Limited maintenance access
- Generator inefficiency
- Lack of advanced predictive energy management

### Existing systems

Existing polar stations already use: diesel generators, wind, solar, batteries, hybrid microgrids, PLC/SCADA, rule-based energy management, automated load prioritization.

Examples investigated: Princess Elisabeth, Mawson, Scott Base, Ross Island, other Antarctic/Arctic systems.

> [!IMPORTANT]
> Existing smart systems already automate substantial portions of energy management, so **POLARIS must not claim that automation itself is novel**.

The proposed research gap is centered around integrating: **forecasting + weather awareness + optimization + polar-specific constraints + predictive rather than purely reactive control**.

---

## 4. Important Novelty Caution

> [!CAUTION]
> Do **NOT** claim: "Nobody has ever used AI for energy management." That is too broad and scientifically unsafe.

AI/ML-based EMS research already exists in non-polar environments.

The defensible differentiation is:

> **AI-driven predictive energy management specifically adapted to polar/off-grid research-station conditions, integrating forecasting, uncertainty, fuel-aware optimization, critical-load prioritization, and polar-specific constraints.**

---

## 5. Major Data Problem

> [!IMPORTANT]
> There is **no convenient public dataset** containing complete real polar-station microgrid data (station electrical load, generator output, fuel consumption, battery SOC, PV generation, wind generation) for Maitri/Bharati in a clean ML-ready format.

Therefore the prototype architecture uses:
- Real weather data
- Public climate data
- Synthetic station loads
- Digital-twin simulation
- Modeled renewable generation

We do NOT pretend synthetic station data is real station data.

---

## 6. The SITES Dataset Discovery

**SITES — Swedish Infrastructure for Ecosystem Science**

Location: **Nuolja Middle Station, Abisko Scientific Research Station, Sweden**

Not Antarctic, but a genuine polar/mountain research station with high-quality observations suitable for developing/testing the forecasting component.

Dataset: `SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`

- 2024 station measurements at **10-minute resolution**
- Quality controlled (gaps not filled)

Variables:

| Variable | Description |
|----------|-------------|
| `TIMESTAMP` | Observation timestamp |
| `TA` | Air temperature |
| `TA_STD` | Air temperature standard deviation |
| `RH` | Relative humidity |
| `SW_IN` | Incoming shortwave radiation |
| `TS_-0.01m` | Soil temperature at ~-0.01 m |
| `TS_STD` | Soil temperature standard deviation |
| `PRECIP` | Precipitation |
| `D_SNOW` | Snow depth |

---

## 7. Critical Timestamp Discovery

> [!WARNING]
> This convention is **LOCKED**. Do not change it casually.

SITES states timestamps represent the 10-minute period leading up to the timestamp. The correct hourly aggregation convention found empirically:

```
HH:00, HH:10, HH:20, HH:30, HH:40, HH:50
→ average → HH:00 hourly value
```

Reconstruction reproduces existing hourly SW_IN:

| Metric | Value |
|--------|-------|
| MAE | ≈ 1.49 × 10⁻⁷ W/m² |
| RMSE | ≈ 2.23 × 10⁻⁷ W/m² |
| Max error | ≈ 3.33 × 10⁻⁷ W/m² |

All 8,784 hourly values match within `1e-6`.

---

## 8. Clean Hourly Dataset

**Path:** [POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv](file:///home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv)

| Property | Value |
|----------|-------|
| Shape | 8784 rows × 6 columns |
| Range | 2024-01-01 00:00 → 2024-12-31 23:00 |
| Missing | None |

Columns: `TIMESTAMP, TA, RH, SW_IN, TS_-0.01m, PRECIP`

Aggregation: TA→mean, RH→mean, SW_IN→mean, TS→mean, PRECIP→sum

Excluded: `D_SNOW, TA_STD, TS_STD`

---

## 9. Full Multivariate Dataset

**Path:** [POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv](file:///home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv)

| Property | Value |
|----------|-------|
| Shape | 8784 × 9 |
| Missing | D_SNOW: 133 hours (1.51%) |

Not the main forecasting dataset (the 5-variable version is cleaner).

---

## 10. Locked Forecasting Problem

> [!WARNING]
> This is a **locked scientific protocol**. All models must use exactly the same forecast windows.

| Parameter | Value |
|-----------|-------|
| Target | `SW_IN` |
| Forecast horizon | 24 hours |
| Context | Previous 24 hours |
| Evaluation | 365 non-overlapping daily windows |
| Total forecast hours | 365 × 24 = 8,760 |
| Daytime definition | `actual_SW_IN > 0` |
| Probabilistic point forecast | Median / 0.5 quantile |

---

## 11. Baselines

**Benchmark:** [POLARIS_v0_1_fixed_24h_benchmark.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv)

Shape: 8760 × 6 | Windows: 365 | First: 2024-01-02 | Last: 2024-12-31

### Seasonal Naive (tomorrow = same hour yesterday)

| Metric | Value |
|--------|-------|
| MAE | 37.186 |
| RMSE | 85.127 |
| Day MAE | 55.099 |
| Day RMSE | 103.622 |

### Persistence (future = latest observed)

| Metric | Value |
|--------|-------|
| MAE | 83.489 |
| RMSE | 169.374 |
| Day MAE | 123.708 |
| Day RMSE | 206.173 |

---

## 12. Foundation Model Benchmark

Three pretrained time-series foundation models evaluated: Chronos-2, TimesFM 3.0, Moirai 2.0 R-Small.

---

## 13. Chronos-2 Univariate

| Property | Value |
|----------|-------|
| Environment | `~/01polaris/chronos/.venv` |
| Version | chronos-forecasting 2.3.1 |
| Model | amazon/chronos-2 |
| PyTorch | 2.14.0+cu130 |
| CUDA | False (CPU-only, intentional) |
| Model size | ~478 MB |

---

## 14. Chronos-2 Univariate Results

**Predictions:** [POLARIS_v0_1_chronos2_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv)

| Metric | Chronos-2 | vs Seasonal Naive |
|--------|-----------|-------------------|
| MAE | 36.593 | +1.59% |
| RMSE | 79.468 | +6.65% |
| Day MAE | 54.009 | +1.98% |
| Day RMSE | 96.731 | +6.65% |

**🏆 Current champion.**

---

## 15. Chronos-2 Solar-Regime Analysis

| Regime | Definition | Chronos MAE | Naive MAE | Winner |
|--------|-----------|-------------|-----------|--------|
| Night | actual ≤ 0 | 0.441 | ~0 | Naive |
| Low | 0 < actual ≤ 100 | 20.276 | 20.660 | Chronos |
| Moderate | 100 < actual ≤ 400 | 91.880 | 100.733 | **Chronos** |
| High | actual > 400 | 161.685 | 145.889 | **Naive** |

> [!IMPORTANT]
> **Major clue:** The main weakness isn't nighttime — it's **high-solar / strongly varying daytime conditions**.

---

## 16. Chronos-2 Horizon Analysis

- MAE: Chronos wins **10/24** horizons
- RMSE: Chronos wins **17/24** horizons
- Strongest: ~H6–H15
- Weakest: ~H23–H24

The model captures the general daily solar shape but smooths amplitude and struggles with abrupt changes.

---

## 17. TimesFM 3.0

| Property | Value |
|----------|-------|
| Environment | `~/01polaris/timesfm/.venv` |
| Model | google/timesfm-3.0-pytorch |
| Parameters | 0.3B |
| Weights | ~1.32 GB |
| License | Non-commercial/research |

Architecture: Stacked Mixing Transformer, Variate Attention, CPM Iterative RevIN, patch length 32, 20 layers, dimension 1280, 16 heads, quantile outputs.

---

## 18. TimesFM Results

**Predictions:** [POLARIS_v0_1_timesfm3_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv)

| Metric | Value |
|--------|-------|
| MAE | 58.254 |
| RMSE | 123.322 |
| Day MAE | 86.172 |
| Day RMSE | 150.111 |

Substantially worse than Chronos-2. Severely compresses moderate/high solar amplitudes. Retained as benchmark, **not the model to build upon**.

---

## 19. Moirai 2.0 R-Small

| Property | Value |
|----------|-------|
| Model | Salesforce/moirai-2.0-R-small |
| Parameters | 11.4M |
| Size | 45.6 MB F32 |
| License | CC-BY-NC-4.0 |

Architecture: patch size 16, max seq 512, 6 layers, d_model 384, 4 predict tokens, quantiles 0.1–0.9.

---

## 20. Moirai Results

**Predictions:** [POLARIS_v0_1_moirai2_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv)

| Metric | Value |
|--------|-------|
| MAE | 72.264 |
| RMSE | 147.849 |
| Day MAE | 106.565 |
| Day RMSE | 179.958 |

Worst of the three. Strong amplitude compression / underprediction during moderate and high solar periods.

---

## 21. Final Foundation-Model Leaderboard

| Rank | Model | MAE | RMSE | Day MAE | Day RMSE |
|------|-------|-----|------|---------|----------|
| 🏆 1 | **Chronos-2** | 36.593 | 79.468 | 54.009 | 96.731 |
| 2 | Seasonal Naive | 37.186 | 85.127 | 55.099 | 103.622 |
| 3 | TimesFM 3.0 | 58.254 | 123.322 | 86.172 | 150.111 |
| 4 | Moirai 2.0 | 72.264 | 147.849 | 106.565 | 179.958 |

---

## 22. Representative Chronos Behavior

| Date | Actual Peak | Chronos | Naive | Note |
|------|------------|---------|-------|------|
| 2024-04-27 | ~746 | ~497 | ~590 | Underprediction, but lower MAE than naive |
| 2024-05-10 | ~715 | ~302 | — | Very large amplitude underprediction |
| 2024-06-18 | ~145 | ~513 | — | Huge overprediction (expected stronger regime) |
| 2024-06-22 | ~693 | ~238 | — | Strong underprediction |
| 2024-06-23 | ~562 | ~611 | — | Good prediction |

> **Key insight:** The model understands the recurring solar cycle but cannot reliably infer tomorrow's atmospheric/cloud-driven deviation.

---

## 23. Chronos Multivariate Experiment

Question: Can historical station weather improve Chronos?

Input: Past 24h of `SW_IN, TA, RH, TS_-0.01m, PRECIP`
Target: Future `SW_IN`

These are **past covariates**, not future covariates.

---

## 24. Chronos Multivariate Results

**Predictions:** [POLARIS_v0_1_chronos2_multivariate_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv)

| Metric | Multivariate | Univariate |
|--------|-------------|------------|
| MAE | 36.918 | 36.593 |
| RMSE | 79.676 | 79.468 |
| Day MAE | 54.300 | 54.009 |
| Day RMSE | 96.978 | 96.731 |

> [!IMPORTANT]
> Multivariate was **slightly worse**. Adding past TA/RH/soil temperature/precipitation alone does not solve the main solar forecasting problem.

---

## 25. Multivariate Horizon Results

- MAE wins: 9/24
- RMSE wins: 11/24
- Best MAE improvement: H5 ≈ +4.48%
- Best RMSE improvement: H21 ≈ +4.16%
- No consistent systematic improvement.

---

## 26. Multivariate Solar Regimes

| Regime | Result vs Univariate |
|--------|---------------------|
| Night | Worse |
| Low | Slightly better (MAE +0.9%, RMSE +2.9%) |
| Moderate | Slightly worse |
| High | Slightly worse |

> Historical weather covariates are not providing enough information to solve the high-solar problem.

---

## 27. Chronos-2 Adaptation / LoRA

Official support: `finetune_mode="full"` and `finetune_mode="lora"`

| Parameter | Value |
|-----------|-------|
| r | 8 |
| alpha | 16 |
| Target modules | self_attention.{q,v,k,o}, output_patch_embedding.output_layer |
| LoRA LR | 1e-5 |
| Full LR | 1e-6 |
| PEFT version | 0.20.0 |

---

## 28. LoRA Pilot

10-step pilot succeeded. Train: Jan–Sep, Validation: October, Target: SW_IN, Covariates: TA/RH/TS/PRECIP, Context: 24h, Horizon: 24h, Batch: 1.

---

## 29. LoRA Experiment A — 500 Steps

Train: Jan 1 → Sep 30 | Validation: October | Test: November + December

| Metric | LoRA 500 | Zero-shot | Naive |
|--------|----------|-----------|-------|
| MAE | 0.748 | 0.777 | 0.798 |
| RMSE | 3.133 | 3.278 | 3.763 |
| Day MAE | 2.189 | 2.289 | 2.445 |
| Day RMSE | 5.480 | 5.735 | 6.586 |

LoRA appeared to improve, **BUT** this test period was mostly low-solar winter/autumn conditions.

---

## 30. LoRA Experiment A — 1000 Steps

Same split:

| Metric | LoRA 1000 | LoRA 500 |
|--------|-----------|----------|
| MAE | 0.748 | 0.748 |
| RMSE | 3.141 | 3.133 |

500 steps was better on most metrics. **No meaningful improvement from more steps.**

---

## 31. LoRA Experiment B

Train: Jan → Jul | Validation: August | Test: Sep → Dec | 500 steps

| Metric | LoRA | Zero-shot | Naive |
|--------|------|-----------|-------|
| MAE | 13.235 | **13.043** | 13.526 |
| RMSE | 41.247 | **41.193** | 43.325 |

**LoRA was slightly worse than zero-shot.**

---

## 32. LoRA Experiment C

Train: Jan → Jun | Validation: Jul → Aug | Test: Sep → Dec | 500 steps

| Metric | LoRA | Zero-shot |
|--------|------|-----------|
| MAE | 13.252 | **13.043** |
| RMSE | 41.197 | **41.193** |

Again zero-shot wins.

---

## 33. Final LoRA Conclusion

| Experiment | Result |
|-----------|--------|
| A (low-solar test) | LoRA wins |
| B (broad seasonal test) | LoRA loses |
| C (broad seasonal test) | LoRA loses |

> [!IMPORTANT]
> **LoRA adaptation is not currently a reliable general improvement over zero-shot Chronos-2.** Do not continue with 1500/2000 steps unless new evidence justifies it. This is a valid scientific result.

---

## 34. Current Core Hypothesis

> [!IMPORTANT]
> **The biggest limitation is not Chronos-2's model capacity. The bigger problem is missing information about future atmospheric conditions.**

The model sees past 24h of `SW_IN, TA, RH, TS, PRECIP` and tries to predict next 24h `SW_IN`.

But tomorrow's solar radiation depends heavily on: **cloud cover, weather evolution, atmospheric conditions** — which are not contained in past observations.

This explains why:
- Daily solar timing is captured ✅
- Low/moderate solar is handled reasonably ✅
- High-solar/amplitude-changing conditions remain difficult ❌

---

## 35. Important Distinction: Past vs Future Covariates

### Already tested (past covariates)
```
PAST: SW_IN, TA, RH, TS, PRECIP → Chronos → future SW_IN
```

### NOT yet tested (future covariates)
```
PAST: SW_IN, TA, RH, TS, PRECIP
  + FUTURE WEATHER FORECAST: cloud cover, temperature, humidity, precipitation, wind
    → Chronos-2 → future SW_IN
```

**This is the next major experiment.**

---

## 36. Critical Data-Leakage Rule

> [!CAUTION]
> We cannot give the model actual future weather observations. That would be future leakage. We need a weather forecast that was **genuinely available at the forecast origin**.

---

## 37. Open-Meteo Issue

Open-Meteo was considered as a future-weather source with historical forecast/reforecast products.

**Problem:** The Open-Meteo point/grid is approximately **12 km away** from the SITES target.

Concerns:
- Nuolja is mountainous
- Arctic weather varies significantly spatially
- Cloud fields can be highly local
- Station-specific irradiance is the actual target

> **DO NOT blindly use Open-Meteo data as if it were Nuolja station weather.**

Open-Meteo remains a candidate **forecast source**, not ground truth.

---

## 38. Ground Truth Must Remain SITES

> [!WARNING]
> This is **locked**: SITES Nuolja station → actual SW_IN → ground truth. Any external weather source can only be forecast input/covariate, never ground truth replacement.

---

## 39. Next Data-Research Questions

Before using any weather forecast data, determine:

1. What is the highest-resolution forecast source covering Nuolja?
2. What is its exact spatial grid/location?
3. How far is it from Nuolja?
4. Does it have historical forecast runs for 2024?
5. What forecast initialization times are available?
6. Does it contain cloud cover?
7. Does it contain temperature/humidity/wind/precipitation?
8. Can we reconstruct one fixed-origin 24h forecast for every POLARIS window?
9. Was the forecast genuinely available at the forecast origin?
10. What spatial mismatch does it introduce?

---

## 40. Important Forecast-Origin Rule

For each POLARIS window:
```
             SAME ORIGIN
                 │
                 ▼
        Weather forecast run
                 │
        ┌────────┴────────┐
        ▼                 ▼
     Hour 1             Hour 24
```

Do NOT accidentally use different weather-model runs for different future hours.

---

## 41. Current Next Experiment

### Chronos-2 + future weather covariates

```
        PAST SITES              FUTURE WEATHER FORECAST
  ┌──────────────────┐    ┌──────────────────────────────┐
  │ SW_IN            │    │ cloud cover                  │
  │ TA               │    │ temperature                  │
  │ RH               │    │ humidity                     │
  │ TS               │    │ precipitation                │
  │ PRECIP           │    │ wind                         │
  └────────┬─────────┘    └──────────────┬───────────────┘
           │                             │
           └──────────┬──────────────────┘
                      ▼
                 Chronos-2
                      ▼
               NEXT 24h SW_IN
```

This directly attacks the identified information bottleneck.

---

## 42. Future Experiment Order

```
Zero-shot Chronos-2 🏆
        ↓
Future-weather data research
        ↓
Chronos-2 + future weather forecasts
        ↓
Evaluate improvement
        ↓
  YES → investigate more useful covariates → possibly forecasted GHI benchmark
  NO  → investigate model formulation
        ↓
Best forecasting model
        ↓
Energy optimization
```

---

## 43. Forecasted Solar Radiation Is a Separate Experiment

External weather forecasts may provide GHI/DNI/direct/diffuse radiation.

Do NOT immediately use forecast GHI as the main model input. That's a different scientific question.

Test order:
1. Future atmospheric variables → predict SW_IN
2. Forecast GHI → predict/calibrate SITES SW_IN
3. Potentially combine

---

## 44. Solar/Time Features

Deterministic features known at forecast time (not leakage):

- Hour, day of year, month
- Solar elevation, zenith, sunrise/sunset, daylight indicator
- Cyclic encodings: sin/cos(2π × hour/24), sin/cos(2π × day/365)

Hypothesis: The model should not have to rediscover astronomical solar geometry from 24 hours of historical irradiance.

---

## 45. Potential Final Forecasting Architecture

```
        SITES observations
               │
        Historical state
               │
   ┌───────────┼──────────────┐
   ▼           ▼              ▼
SW_IN       Weather      Solar geometry
history     history       + timestamp
   │           │              │
   └───────────┼──────────────┘
               │
               + Future weather forecast
               │
               ▼
         Forecast model → 24h SW_IN forecast
               ↓
         Renewable-energy forecast
               ↓
         Optimization engine
               ↓
   ┌───────────┼──────────────┐
   ▼           ▼              ▼
Battery     Diesel      Flexible loads
   │           │              │
   └───────────┼──────────────┘
               ▼
         AI-EMS decision
```

**Planned architecture, not yet implemented.**

---

## 46. Energy Management Side — Not Yet Built

Not yet completed:
- Real load forecasting
- Generator scheduling
- Battery optimization
- MILP optimization
- Digital twin
- Fuel optimization
- Critical-load control
- Dashboard
- What-if simulator
- Final EMS

> Do not claim these components are already implemented.

---

## 47. Original Prototype Direction

### Simulated station
Based on Maitri/Bharati characteristics, literature-based loads, generator models, battery model, renewable generation, weather.

### AI forecasting
Considered: XGBoost, LSTM, hybrid models with 24h forecasting.

### Optimization
Potentially: MILP, Pyomo, PuLP, OR-Tools.

### Dashboard
Potentially: Streamlit, React, FastAPI/Flask.

### Deployment
Prototype: software simulation. Real: edge computer, industrial sensors, generator controllers, battery inverter, SCADA integration, manual fallback.

> [!CAUTION]
> The project must **never claim that the student prototype is ready to directly control an Antarctic research station**.

---

## 48. Important SIH Safety / Reliability Principles

```
AI recommendation → constraints/safety layer → optimization → operator approval/automated control
```

Must always include:
- Manual override
- Fallback control
- Safety margins
- Critical-load protection
- Generator backup
- Communication-failure resilience
- Local/offline operation

AI should not become a single point of failure.

---

## 49. Current Computer Environment

| Property | Value |
|----------|-------|
| OS | Ubuntu |
| RAM | 8 GB |
| Storage | ~390 GB free |
| PyTorch | CPU-only |
| CUDA | False |
| NVIDIA driver | Not installed (intentional) |

Project directories: `~/01polaris/chronos`, `~/01polaris/timesfm`, `~/01polaris/moirai`, `~/01polaris/data`

---

## 50. Important User Working Preferences

- Give exact terminal commands
- Don't randomly install packages
- Only install when the need is clear
- Keep chats/workflows clean
- Prefer controlled experiments
- Preserve existing benchmark protocol
- Don't change dataset or evaluation rules casually
- Verify data alignment before model experiments
- Do not fabricate results
- Do not force a model to win
- If an approach doesn't work, document it and move on
- Use AI resources strategically, not for the sake of using them

---

## 51. AI Models Available to the User

| Model | Strategic Use |
|-------|--------------|
| AI assistant Opus | Deep research, architecture, methodology, reasoning, gap analysis |
| AI assistant Sonnet | Implementation, coding, debugging, practical analysis |
| Gemini Pro | Second opinions, research, papers, architecture comparison |
| Gemini Flash | Fast analysis, repetitive checks, quick review, data inspection |
| GPT-OSS 120B | Alternative reasoning perspective |

---

## 52. Files & Artifacts Currently Available

### Core Data
| File | Path |
|------|------|
| SITES raw | [SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv](file:///home/punith-bs/01polaris/data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv) |
| 5-var hourly | [POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv](file:///home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv) |
| Multivariate hourly | [POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv](file:///home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv) |

### Benchmarks & Baselines
| File | Path |
|------|------|
| Benchmark | [POLARIS_v0_1_fixed_24h_benchmark.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv) |
| Baseline metrics | [POLARIS_v0_1_fixed_24h_baseline_metrics.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_baseline_metrics.csv) |
| Horizon metrics | [POLARIS_v0_1_fixed_24h_horizon_metrics.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_horizon_metrics.csv) |

### Model Predictions
| Model | Path |
|-------|------|
| Chronos-2 | [POLARIS_v0_1_chronos2_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv) |
| Chronos-2 multivariate | [POLARIS_v0_1_chronos2_multivariate_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv) |
| TimesFM 3.0 | [POLARIS_v0_1_timesfm3_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv) |
| Moirai 2.0 | [POLARIS_v0_1_moirai2_predictions.csv](file:///home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv) |

### Analysis & Comparison
| Directory | Path |
|-----------|------|
| Final comparison | [final_model_comparison/](file:///home/punith-bs/01polaris/final_model_comparison) |
| Chronos scripts & analysis | [chronos/](file:///home/punith-bs/01polaris/chronos) |

### LoRA Checkpoints
- [polaris_lora_pilot](file:///home/punith-bs/01polaris/chronos/polaris_lora_pilot)
- [polaris_lora_500](file:///home/punith-bs/01polaris/chronos/polaris_lora_500)
- [polaris_lora_1000](file:///home/punith-bs/01polaris/chronos/polaris_lora_1000)
- [polaris_lora_expB_500](file:///home/punith-bs/01polaris/chronos/polaris_lora_expB_500)
- [polaris_lora_expC_500](file:///home/punith-bs/01polaris/chronos/polaris_lora_expC_500)

---

## 53. Current Status — One Screen Version

```
POLARIS
│
├── SIH problem research                 ✅
├── Polar energy research               ✅
├── Existing EMS research               ✅
├── Novelty/research-gap analysis       ✅
│
├── Real station dataset                ✅  (SITES Nuolja)
├── Timestamp reconstruction            ✅  (LOCKED)
├── Hourly station dataset              ✅
├── Fixed benchmark                     ✅  (LOCKED)
├── Seasonal naive baseline             ✅
├── Persistence baseline                ✅
│
├── Chronos-2 univariate                ✅ 🏆
├── TimesFM 3.0                         ✅
├── Moirai 2.0                          ✅
│
├── Chronos multivariate past weather   ✅  (no improvement)
├── Chronos solar-regime analysis       ✅
├── Chronos horizon analysis            ✅
│
├── LoRA 500                            ✅  (not reliably better)
├── LoRA 1000                           ✅  (not reliably better)
├── LoRA Exp B                          ✅  (zero-shot wins)
├── LoRA Exp C                          ✅  (zero-shot wins)
│
├── Future-weather covariates           ⏳ NEXT
├── Solar geometry features             ⏳
├── Future-weather + Chronos            ⏳
├── Dedicated forecasting model         ⏳
├── Load forecasting                    ⏳
├── Digital twin                        ⏳
├── MILP optimization                   ⏳
├── Battery scheduling                  ⏳
├── Fuel optimization                   ⏳
├── Dashboard                           ⏳
└── Full AI-EMS                         ⏳
```

---

## 54. Current Scientific Conclusion

> **Zero-shot Chronos-2 is the strongest evaluated forecasting foundation model for the current SITES Nuolja 24-hour SW_IN benchmark.**

- Adding historical meteorological covariates did **not** meaningfully improve it.
- LoRA adaptation produced a modest improvement on one low-solar holdout but failed to consistently generalize.
- More LoRA training is **not currently justified**.

The major unresolved issue:

> **How to provide legitimate information about future atmospheric conditions without introducing spatial mismatch or future-data leakage.**

---

## 55. The Next Big Research Question

> **Can historically valid future weather forecasts, especially cloud/atmospheric information, significantly improve 24-hour station-specific SW_IN forecasting when evaluated against real SITES Nuolja observations?**

---

## 56. Next Action — Do Not Skip This Order

### Phase A — Forecast-source research
Find the best geographically appropriate forecast source.
Priority: station/local → high-res regional → global NWP → Open-Meteo/grid

### Phase B — Validate spatial alignment
For every candidate: forecast grid distance from Nuolja, terrain differences, resolution.

### Phase C — Validate temporal causality
For every forecast: initialization time, what was available, 24h forecast, compare with SITES.

### Phase D — Validate usefulness
Before Chronos: does forecast cloud cover correlate with actual SITES SW_IN variability?

### Phase E — Chronos future-covariate experiment
Past SITES + future weather forecast → Chronos-2 → SITES SW_IN. Compare against frozen baselines.

---

## 57. Very Important Philosophy for the Rest of the Project

Do **not** optimize the benchmark artificially. Do not:
- Change forecast windows because a model performs poorly
- Use actual future weather
- Use data unavailable at forecast time
- Select only good dates
- Tune repeatedly on the final test set
- Claim synthetic data is real
- Claim nearby gridded weather is station weather
- Claim AI novelty without checking literature
- Claim fuel savings before running actual optimization simulation

Every improvement must survive: **same data, same windows, same horizon, same metrics, same ground truth**.

---

## 58. Ultimate POLARIS Goal

```
                  POLAR STATION
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Weather         Loads        Generation
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Forecasting AI
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           Load      Solar      Wind
          forecast  forecast  forecast
             │         │         │
             └─────────┼─────────┘
                       ▼
              Uncertainty-aware optimization
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Battery       Diesel      Flexible
       dispatch     scheduling     loads
          │            │            │
          └────────────┼────────────┘
                       ▼
                AI ENERGY EMS
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Reliability    Fuel       Renewable
                      use         utilization
                       │
                       ▼
                 Operator UI
```

> **Reliable polar-station energy management with lower fuel dependence, better renewable utilization, proactive shortage prevention, and protection of critical loads.**

---

## 🔥 THE SINGLE MOST IMPORTANT THING FOR THE NEXT AI

> **Do not restart the project from "which forecasting model should we try?"**
>
> We already benchmarked Seasonal Naive, Chronos-2, TimesFM 3.0 and Moirai 2.0. Chronos-2 is the current champion.
>
> We already tested Chronos-2 with historical SITES weather covariates and LoRA adaptation. Neither produced a robust improvement.
>
> The current hypothesis is that the main bottleneck is **missing future atmospheric information**, especially cloud/weather evolution.
>
> The next task is therefore **not more LoRA training**. The next task is to find a scientifically valid, geographically appropriate historical weather-forecast source for Nuolja, verify forecast-origin causality and spatial mismatch, and then test Chronos-2 with genuine future covariates.
>
> **SITES Nuolja SW_IN remains the ground truth. The 365 × 24 benchmark is locked. No future leakage. No changing the evaluation to make a model look better.**

---

*Compiled: 2026-09-09 | Verified against filesystem*
